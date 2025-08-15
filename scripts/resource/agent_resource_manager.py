#!/usr/bin/env python3
"""
Agent Resource Manager

Manages concurrent agents and resource constraints during documentation
modernization operations to prevent system overload and optimize performance.

Key Features:
- Concurrent agent management with resource allocation
- System resource monitoring and throttling
- Load balancing across agents
- Resource constraint enforcement
- Performance optimization and tuning
- Integration with recovery and monitoring systems
"""

import json
import os
import psutil
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import queue
import subprocess
from collections import defaultdict, deque

try:
    from .token_usage_monitor import TokenUsageMonitor
    from .agent_recovery_manager import AgentRecoveryManager
    TOKEN_MONITOR_AVAILABLE = True
    RECOVERY_MANAGER_AVAILABLE = True
except ImportError:
    TOKEN_MONITOR_AVAILABLE = False
    RECOVERY_MANAGER_AVAILABLE = False
    logging.warning("Token monitor or recovery manager not available")


class ResourceType(Enum):
    """Types of resources to manage"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    TOKEN_CONTEXT = "token_context"
    FILE_HANDLES = "file_handles"


class AgentPriority(Enum):
    """Agent priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class ResourceLimits:
    """Resource limit configuration"""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    max_disk_usage_percent: float = 85.0
    max_concurrent_agents: int = 2
    max_files_per_agent: int = 10
    max_tokens_per_agent: int = 50000
    min_free_memory_mb: int = 1024
    throttle_on_high_load: bool = True
    auto_suspend_on_limits: bool = True


@dataclass
class AgentResource:
    """Resource allocation for an agent"""
    agent_id: str
    cpu_limit_percent: float
    memory_limit_mb: int
    token_allocation: int
    file_allocation: int
    priority: AgentPriority
    allocated_at: str
    last_activity: str
    resource_usage: Dict[str, float] = None
    
    def __post_init__(self):
        if self.resource_usage is None:
            self.resource_usage = {}


@dataclass
class SystemResourceSnapshot:
    """Snapshot of system resources"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_agents: int
    total_processes: int
    load_average: Optional[float] = None
    network_io: Optional[Dict[str, int]] = None


@dataclass
class AgentTask:
    """Task queued for agent execution"""
    task_id: str
    agent_id: str
    operation_type: str
    file_paths: List[str]
    estimated_tokens: int
    priority: AgentPriority
    created_at: str
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class AgentResourceManager:
    """
    Manages agent resources, concurrent execution, and system constraints
    for documentation modernization operations.
    """
    
    def __init__(self,
                 workspace_path: Union[str, Path],
                 resource_limits: Optional[ResourceLimits] = None,
                 monitoring_interval: float = 10.0):
        """
        Initialize Agent Resource Manager.
        
        Args:
            workspace_path: Path to workspace directory
            resource_limits: Resource limit configuration
            monitoring_interval: Resource monitoring interval in seconds
        """
        self.workspace_path = Path(workspace_path)
        self.resource_dir = self.workspace_path / ".resources"
        self.allocation_dir = self.resource_dir / "allocations"
        self.monitoring_dir = self.resource_dir / "monitoring"
        
        # Create resource directories
        for dir_path in [self.resource_dir, self.allocation_dir, self.monitoring_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Resource configuration
        self.limits = resource_limits or ResourceLimits()
        self.monitoring_interval = monitoring_interval
        
        # Agent management
        self.active_agents: Dict[str, AgentResource] = {}
        self.agent_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.completed_agents: Dict[str, AgentResource] = {}
        self.task_queue: Dict[str, AgentTask] = {}
        
        # Resource monitoring
        self.resource_history: deque = deque(maxlen=720)  # 2 hours at 10s intervals
        self.monitoring_active = False
        self.monitor_thread = None
        
        # System information
        self.system_info = self._get_system_info()
        
        # External integrations
        self.token_monitor = None
        self.recovery_manager = None
        
        if TOKEN_MONITOR_AVAILABLE:
            try:
                self.token_monitor = TokenUsageMonitor(workspace_path)
            except Exception:
                pass
        
        if RECOVERY_MANAGER_AVAILABLE:
            try:
                self.recovery_manager = AgentRecoveryManager(workspace_path)
            except Exception:
                pass
        
        # Load existing state
        self.load_resource_state()
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for resource manager"""
        log_file = self.resource_dir / "resource_manager.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AgentResourceManager')

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for resource planning"""
        try:
            system_info = {
                'cpu_count': psutil.cpu_count(),
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'platform': os.name,
                'python_version': os.sys.version
            }
            
            # Add disk information
            disk_usage = psutil.disk_usage(str(self.workspace_path))
            system_info.update({
                'disk_total_gb': disk_usage.total / (1024**3),
                'disk_free_gb': disk_usage.free / (1024**3)
            })
            
            return system_info
            
        except Exception as e:
            self.logger.warning(f"Failed to get system info: {e}")
            return {'error': str(e)}

    def request_agent_resources(self,
                              agent_id: str,
                              priority: AgentPriority = AgentPriority.NORMAL,
                              estimated_tokens: int = 10000,
                              file_count: int = 1) -> Optional[AgentResource]:
        """
        Request resources for an agent.
        
        Args:
            agent_id: Agent identifier
            priority: Agent priority level
            estimated_tokens: Estimated token usage
            file_count: Number of files to process
            
        Returns:
            resource: Allocated resources or None if unavailable
        """
        # Check if agent already has resources
        if agent_id in self.active_agents:
            self.logger.warning(f"Agent {agent_id} already has resources allocated")
            return self.active_agents[agent_id]
        
        # Check system capacity
        if not self._can_allocate_resources(estimated_tokens, file_count):
            self.logger.warning(f"Cannot allocate resources for agent {agent_id} - system at capacity")
            return None
        
        # Calculate resource allocation
        cpu_limit = self._calculate_cpu_allocation(priority)
        memory_limit = self._calculate_memory_allocation(priority, estimated_tokens)
        token_allocation = min(estimated_tokens, self.limits.max_tokens_per_agent)
        
        # Create resource allocation
        resource = AgentResource(
            agent_id=agent_id,
            cpu_limit_percent=cpu_limit,
            memory_limit_mb=memory_limit,
            token_allocation=token_allocation,
            file_allocation=min(file_count, self.limits.max_files_per_agent),
            priority=priority,
            allocated_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat()
        )
        
        self.active_agents[agent_id] = resource
        
        # Save allocation
        self._save_allocation(resource)
        
        # Initialize token monitoring if available
        if self.token_monitor:
            self.token_monitor.start_session(agent_id)
        
        self.logger.info(f"Allocated resources for agent {agent_id}: "
                        f"{cpu_limit:.1f}% CPU, {memory_limit}MB memory, {token_allocation} tokens")
        
        return resource

    def _can_allocate_resources(self, estimated_tokens: int, file_count: int) -> bool:
        """Check if resources can be allocated"""
        # Check concurrent agent limit
        if len(self.active_agents) >= self.limits.max_concurrent_agents:
            return False
        
        # Check current system resources
        current_snapshot = self._get_current_resource_snapshot()
        
        # CPU check
        if current_snapshot.cpu_percent > self.limits.max_cpu_percent:
            return False
        
        # Memory check  
        if current_snapshot.memory_percent > self.limits.max_memory_percent:
            return False
        
        # Disk check
        if current_snapshot.disk_percent > self.limits.max_disk_usage_percent:
            return False
        
        # Token allocation check
        total_allocated_tokens = sum(r.token_allocation for r in self.active_agents.values())
        if total_allocated_tokens + estimated_tokens > self.limits.max_tokens_per_agent * self.limits.max_concurrent_agents:
            return False
        
        return True

    def _calculate_cpu_allocation(self, priority: AgentPriority) -> float:
        """Calculate CPU allocation based on priority"""
        base_allocation = self.limits.max_cpu_percent / self.limits.max_concurrent_agents
        
        priority_multipliers = {
            AgentPriority.LOW: 0.7,
            AgentPriority.NORMAL: 1.0,
            AgentPriority.HIGH: 1.3,
            AgentPriority.CRITICAL: 1.5
        }
        
        return base_allocation * priority_multipliers.get(priority, 1.0)

    def _calculate_memory_allocation(self, priority: AgentPriority, estimated_tokens: int) -> int:
        """Calculate memory allocation based on priority and token usage"""
        # Base memory allocation (MB)
        base_memory = 512
        
        # Additional memory based on token estimation
        token_memory = (estimated_tokens / 1000) * 10  # ~10MB per 1K tokens
        
        # Priority multiplier
        priority_multipliers = {
            AgentPriority.LOW: 0.8,
            AgentPriority.NORMAL: 1.0,
            AgentPriority.HIGH: 1.2,
            AgentPriority.CRITICAL: 1.5
        }
        
        total_memory = (base_memory + token_memory) * priority_multipliers.get(priority, 1.0)
        
        return int(min(total_memory, 2048))  # Cap at 2GB per agent

    def release_agent_resources(self, agent_id: str) -> bool:
        """
        Release resources for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            success: True if resources were released
        """
        if agent_id not in self.active_agents:
            self.logger.warning(f"Agent {agent_id} has no resources to release")
            return False
        
        resource = self.active_agents[agent_id]
        
        # Move to completed
        self.completed_agents[agent_id] = resource
        del self.active_agents[agent_id]
        
        # End token monitoring session
        if self.token_monitor:
            self.token_monitor.end_session(agent_id)
        
        # Clean up allocation file
        allocation_file = self.allocation_dir / f"{agent_id}.json"
        if allocation_file.exists():
            allocation_file.unlink()
        
        self.logger.info(f"Released resources for agent {agent_id}")
        return True

    def update_agent_activity(self, agent_id: str, activity_data: Optional[Dict[str, Any]] = None):
        """
        Update agent activity and resource usage.
        
        Args:
            agent_id: Agent identifier  
            activity_data: Optional activity data
        """
        if agent_id not in self.active_agents:
            return
        
        resource = self.active_agents[agent_id]
        resource.last_activity = datetime.now().isoformat()
        
        if activity_data:
            resource.resource_usage.update(activity_data)
        
        # Update token usage if monitor available
        if self.token_monitor and activity_data:
            token_data = {
                'input_tokens': activity_data.get('input_tokens', 0),
                'output_tokens': activity_data.get('output_tokens', 0),
                'context_tokens': activity_data.get('context_tokens'),
                'file_path': activity_data.get('file_path'),
                'operation': activity_data.get('operation', 'update')
            }
            
            self.token_monitor.record_usage(agent_id, **token_data)

    def suspend_agent(self, agent_id: str, reason: str) -> bool:
        """
        Suspend an agent due to resource constraints.
        
        Args:
            agent_id: Agent identifier
            reason: Suspension reason
            
        Returns:
            success: True if agent was suspended
        """
        if agent_id not in self.active_agents:
            return False
        
        # Use recovery manager for suspension if available
        if self.recovery_manager:
            checkpoint_id = self.recovery_manager.suspend_agent(
                agent_id=agent_id,
                task_id=None,  # Would need to track task IDs
                reason=reason,
                recovery_instructions=[
                    "Wait for system resources to become available",
                    "Check resource constraints and adjust if needed",
                    "Resume when system load decreases"
                ]
            )
            self.logger.warning(f"Suspended agent {agent_id}: {reason} (checkpoint: {checkpoint_id})")
        else:
            self.logger.warning(f"Suspended agent {agent_id}: {reason}")
        
        return True

    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of agents and their resource usage.
        
        Args:
            agent_id: Optional specific agent ID
            
        Returns:
            status: Agent status information
        """
        current_snapshot = self._get_current_resource_snapshot()
        
        if agent_id:
            if agent_id in self.active_agents:
                resource = self.active_agents[agent_id]
                return {
                    'agent_id': agent_id,
                    'status': 'active',
                    'resource_allocation': asdict(resource),
                    'system_snapshot': asdict(current_snapshot)
                }
            else:
                return {
                    'agent_id': agent_id,
                    'status': 'not_found',
                    'system_snapshot': asdict(current_snapshot)
                }
        
        # Return all agents status
        return {
            'system_snapshot': asdict(current_snapshot),
            'active_agents': {
                aid: asdict(resource) for aid, resource in self.active_agents.items()
            },
            'resource_limits': asdict(self.limits),
            'system_info': self.system_info,
            'monitoring_active': self.monitoring_active
        }

    def _get_current_resource_snapshot(self) -> SystemResourceSnapshot:
        """Get current system resource snapshot"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage(str(self.workspace_path))
            disk_percent = (disk.used / disk.total) * 100
            
            # Process count
            active_agents = len(self.active_agents)
            total_processes = len(psutil.pids())
            
            # Load average (Unix systems)
            load_average = None
            try:
                if hasattr(os, 'getloadavg'):
                    load_average = os.getloadavg()[0]
            except (OSError, AttributeError):
                pass
            
            snapshot = SystemResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                active_agents=active_agents,
                total_processes=total_processes,
                load_average=load_average
            )
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to get resource snapshot: {e}")
            return SystemResourceSnapshot(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                active_agents=len(self.active_agents),
                total_processes=0
            )

    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring_active:
            self.logger.warning("Resource monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Started resource monitoring")

    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Stopped resource monitoring")

    def _monitoring_loop(self):
        """Resource monitoring loop"""
        while self.monitoring_active:
            try:
                # Get current resource snapshot
                snapshot = self._get_current_resource_snapshot()
                self.resource_history.append(snapshot)
                
                # Check for resource violations
                self._check_resource_violations(snapshot)
                
                # Clean up stale agents
                self._cleanup_stale_agents()
                
                # Save monitoring data periodically
                if len(self.resource_history) % 60 == 0:  # Every 10 minutes
                    self._save_monitoring_data()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in resource monitoring loop: {e}")
                time.sleep(self.monitoring_interval)

    def _check_resource_violations(self, snapshot: SystemResourceSnapshot):
        """Check for resource limit violations"""
        violations = []
        
        if snapshot.cpu_percent > self.limits.max_cpu_percent:
            violations.append(f"CPU usage {snapshot.cpu_percent:.1f}% exceeds limit {self.limits.max_cpu_percent}%")
        
        if snapshot.memory_percent > self.limits.max_memory_percent:
            violations.append(f"Memory usage {snapshot.memory_percent:.1f}% exceeds limit {self.limits.max_memory_percent}%")
        
        if snapshot.disk_percent > self.limits.max_disk_usage_percent:
            violations.append(f"Disk usage {snapshot.disk_percent:.1f}% exceeds limit {self.limits.max_disk_usage_percent}%")
        
        if violations:
            self.logger.warning(f"Resource violations detected: {'; '.join(violations)}")
            
            # Take action if auto-suspension enabled
            if self.limits.auto_suspend_on_limits and self.active_agents:
                # Suspend lowest priority agents
                agents_by_priority = sorted(
                    self.active_agents.items(),
                    key=lambda x: x[1].priority.value
                )
                
                for agent_id, resource in agents_by_priority:
                    self.suspend_agent(agent_id, f"Resource violation: {violations[0]}")
                    break  # Suspend one agent at a time

    def _cleanup_stale_agents(self):
        """Clean up agents that haven't been active recently"""
        current_time = datetime.now()
        stale_threshold = timedelta(hours=1)
        
        stale_agents = []
        for agent_id, resource in self.active_agents.items():
            last_activity = datetime.fromisoformat(resource.last_activity)
            if current_time - last_activity > stale_threshold:
                stale_agents.append(agent_id)
        
        for agent_id in stale_agents:
            self.logger.warning(f"Cleaning up stale agent: {agent_id}")
            self.release_agent_resources(agent_id)

    def generate_resource_report(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Generate comprehensive resource usage report.
        
        Args:
            hours_back: Hours of history to include
            
        Returns:
            report: Resource usage report
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter relevant snapshots
        relevant_snapshots = [
            s for s in self.resource_history 
            if datetime.fromisoformat(s.timestamp) >= cutoff_time
        ]
        
        if not relevant_snapshots:
            return {
                'report_id': f"resource_report_{int(time.time())}",
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours_back,
                'status': 'no_data'
            }
        
        # Calculate statistics
        cpu_values = [s.cpu_percent for s in relevant_snapshots]
        memory_values = [s.memory_percent for s in relevant_snapshots]
        disk_values = [s.disk_percent for s in relevant_snapshots]
        
        report = {
            'report_id': f"resource_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours_back,
            'system_info': self.system_info,
            'resource_limits': asdict(self.limits),
            'resource_statistics': {
                'cpu': {
                    'average': sum(cpu_values) / len(cpu_values),
                    'peak': max(cpu_values),
                    'minimum': min(cpu_values)
                },
                'memory': {
                    'average': sum(memory_values) / len(memory_values),
                    'peak': max(memory_values),
                    'minimum': min(memory_values)
                },
                'disk': {
                    'average': sum(disk_values) / len(disk_values),
                    'peak': max(disk_values),
                    'minimum': min(disk_values)
                }
            },
            'agent_statistics': {
                'total_agents_managed': len(self.active_agents) + len(self.completed_agents),
                'currently_active': len(self.active_agents),
                'completed': len(self.completed_agents)
            },
            'performance_metrics': self._calculate_performance_metrics(relevant_snapshots)
        }
        
        # Save report
        report_file = self.monitoring_dir / f"{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

    def _calculate_performance_metrics(self, snapshots: List[SystemResourceSnapshot]) -> Dict[str, Any]:
        """Calculate performance metrics from snapshots"""
        if not snapshots:
            return {}
        
        # Resource efficiency
        cpu_efficiency = 100 - (sum(s.cpu_percent for s in snapshots) / len(snapshots))
        memory_efficiency = 100 - (sum(s.memory_percent for s in snapshots) / len(snapshots))
        
        # Agent throughput
        agent_hours = sum(s.active_agents for s in snapshots) * (len(snapshots) * self.monitoring_interval / 3600)
        
        return {
            'resource_efficiency': {
                'cpu_efficiency_percent': cpu_efficiency,
                'memory_efficiency_percent': memory_efficiency
            },
            'throughput': {
                'total_agent_hours': agent_hours,
                'average_concurrent_agents': sum(s.active_agents for s in snapshots) / len(snapshots)
            },
            'stability': {
                'monitoring_uptime_percent': 100.0,  # Simplified
                'total_snapshots': len(snapshots)
            }
        }

    def _save_allocation(self, resource: AgentResource):
        """Save agent resource allocation to file"""
        allocation_file = self.allocation_dir / f"{resource.agent_id}.json"
        with open(allocation_file, 'w') as f:
            json.dump(asdict(resource), f, indent=2)

    def _save_monitoring_data(self):
        """Save resource monitoring data"""
        try:
            # Save recent snapshots
            recent_snapshots = list(self.resource_history)[-100:]  # Last 100 snapshots
            snapshots_data = [asdict(s) for s in recent_snapshots]
            
            monitoring_file = self.monitoring_dir / "recent_snapshots.json"
            with open(monitoring_file, 'w') as f:
                json.dump(snapshots_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save monitoring data: {e}")

    def save_resource_state(self):
        """Save current resource management state"""
        try:
            state_data = {
                'active_agents': {aid: asdict(resource) for aid, resource in self.active_agents.items()},
                'completed_agents': {aid: asdict(resource) for aid, resource in self.completed_agents.items()},
                'resource_limits': asdict(self.limits),
                'system_info': self.system_info
            }
            
            state_file = self.resource_dir / "resource_state.json"
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save resource state: {e}")

    def load_resource_state(self):
        """Load existing resource management state"""
        try:
            state_file = self.resource_dir / "resource_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                
                # Load completed agents only (active agents should be restarted)
                for aid, data in state_data.get('completed_agents', {}).items():
                    # Convert priority back to enum
                    data['priority'] = AgentPriority(data['priority'])
                    self.completed_agents[aid] = AgentResource(**data)
                
        except Exception as e:
            self.logger.warning(f"Failed to load resource state: {e}")


def main():
    """Example usage and CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Resource Manager")
    parser.add_argument("--workspace", "-w", required=True, help="Workspace path")
    parser.add_argument("--monitor", "-m", action="store_true", help="Start resource monitoring")
    parser.add_argument("--status", "-s", action="store_true", help="Show resource status")
    parser.add_argument("--report", "-r", action="store_true", help="Generate resource report")
    parser.add_argument("--agent-id", "-a", help="Agent ID for operations")
    
    args = parser.parse_args()
    
    manager = AgentResourceManager(args.workspace)
    
    if args.monitor:
        manager.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_monitoring()
    
    elif args.status:
        status = manager.get_agent_status(args.agent_id)
        print(json.dumps(status, indent=2))
    
    elif args.report:
        report = manager.generate_resource_report()
        print(json.dumps(report, indent=2))
    
    else:
        print("Use --monitor, --status, or --report")


if __name__ == "__main__":
    main()