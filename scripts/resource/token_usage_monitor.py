#!/usr/bin/env python3
"""
Token Usage Monitor

Monitors Claude token usage during documentation modernization operations to prevent
context limit issues and optimize resource utilization.

Key Features:
- Real-time token usage tracking
- Context limit monitoring and warnings
- Automatic agent suspension before limits
- Token usage analytics and reporting
- Integration with Agent Recovery Manager
- Historical usage pattern analysis
"""

import json
import os
import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
from collections import deque, defaultdict

try:
    from mcp_task_orchestrator.orchestrator.orchestration_state_manager import OrchestrationStateManager
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    logging.warning("Orchestrator not available - running in standalone mode")


class TokenLimit(Enum):
    """Token limit thresholds"""
    CLAUDE_3_SONNET = 200000
    CLAUDE_3_OPUS = 200000
    CLAUDE_3_HAIKU = 200000
    DEFAULT = 100000


class UsageLevel(Enum):
    """Token usage levels"""
    LOW = "low"          # < 50% of limit
    MODERATE = "moderate" # 50-75% of limit  
    HIGH = "high"        # 75-90% of limit
    CRITICAL = "critical" # 90-95% of limit
    DANGER = "danger"    # > 95% of limit


@dataclass
class TokenUsageSnapshot:
    """Snapshot of token usage at a point in time"""
    timestamp: str
    agent_id: str
    task_id: Optional[str]
    file_path: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    context_tokens: int
    percentage_used: float
    usage_level: UsageLevel
    model: str = "unknown"
    operation: str = "unknown"


@dataclass
class TokenUsageSession:
    """Token usage for an entire session"""
    session_id: str
    agent_id: str
    start_time: str
    end_time: Optional[str] = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_context_tokens: int = 0
    peak_context_usage: int = 0
    files_processed: int = 0
    operations_count: int = 0
    average_tokens_per_file: float = 0.0
    efficiency_rating: str = "unknown"


@dataclass
class TokenUsageAlert:
    """Alert for token usage thresholds"""
    alert_id: str
    timestamp: str
    agent_id: str
    alert_type: str
    usage_level: UsageLevel
    current_usage: int
    limit: int
    percentage_used: float
    message: str
    action_required: bool
    auto_action_taken: Optional[str] = None


class TokenUsageMonitor:
    """
    Monitors token usage for Claude operations with real-time tracking,
    alerts, and automatic agent suspension capabilities.
    """
    
    def __init__(self,
                 workspace_path: Union[str, Path],
                 model_type: str = "claude-3-sonnet",
                 custom_limit: Optional[int] = None,
                 orchestrator_session_id: Optional[str] = None):
        """
        Initialize Token Usage Monitor.
        
        Args:
            workspace_path: Path to workspace directory
            model_type: Claude model type for token limits
            custom_limit: Custom token limit override
            orchestrator_session_id: Optional orchestrator session ID
        """
        self.workspace_path = Path(workspace_path)
        self.monitoring_dir = self.workspace_path / ".monitoring"
        self.usage_dir = self.monitoring_dir / "token_usage"
        self.alerts_dir = self.monitoring_dir / "alerts"
        self.reports_dir = self.monitoring_dir / "reports"
        
        # Create monitoring directories
        for dir_path in [self.monitoring_dir, self.usage_dir, self.alerts_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Determine token limits
        self.model_type = model_type
        self.token_limit = custom_limit or self._get_model_limit(model_type)
        
        # Usage thresholds
        self.thresholds = {
            UsageLevel.MODERATE: int(self.token_limit * 0.50),
            UsageLevel.HIGH: int(self.token_limit * 0.75),
            UsageLevel.CRITICAL: int(self.token_limit * 0.90),
            UsageLevel.DANGER: int(self.token_limit * 0.95)
        }
        
        # Monitoring state
        self.active_sessions: Dict[str, TokenUsageSession] = {}
        self.usage_history: deque = deque(maxlen=1000)  # Keep last 1000 snapshots
        self.alerts: List[TokenUsageAlert] = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Recovery integration
        self.recovery_manager = None
        
        self.orchestrator_session_id = orchestrator_session_id
        if ORCHESTRATOR_AVAILABLE and orchestrator_session_id:
            try:
                self.state_manager = OrchestrationStateManager()
            except Exception:
                self.state_manager = None
        else:
            self.state_manager = None
        
        # Load existing data
        self.load_monitoring_data()
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for token usage monitor"""
        log_file = self.monitoring_dir / "token_monitor.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('TokenUsageMonitor')

    def _get_model_limit(self, model_type: str) -> int:
        """Get token limit for Claude model type"""
        model_limits = {
            'claude-3-sonnet': TokenLimit.CLAUDE_3_SONNET.value,
            'claude-3-opus': TokenLimit.CLAUDE_3_OPUS.value,
            'claude-3-haiku': TokenLimit.CLAUDE_3_HAIKU.value,
            'claude-sonnet': TokenLimit.CLAUDE_3_SONNET.value,
            'claude-opus': TokenLimit.CLAUDE_3_OPUS.value,
            'claude-haiku': TokenLimit.CLAUDE_3_HAIKU.value
        }
        
        return model_limits.get(model_type.lower(), TokenLimit.DEFAULT.value)

    def start_session(self, agent_id: str, session_id: Optional[str] = None) -> str:
        """
        Start a new token usage monitoring session.
        
        Args:
            agent_id: Agent identifier
            session_id: Optional session identifier
            
        Returns:
            session_id: Session identifier
        """
        if not session_id:
            session_id = f"{agent_id}_{int(time.time())}"
        
        session = TokenUsageSession(
            session_id=session_id,
            agent_id=agent_id,
            start_time=datetime.now().isoformat()
        )
        
        self.active_sessions[session_id] = session
        self.logger.info(f"Started token usage session: {session_id} for agent: {agent_id}")
        
        return session_id

    def record_usage(self,
                    agent_id: str,
                    input_tokens: int,
                    output_tokens: int,
                    context_tokens: Optional[int] = None,
                    session_id: Optional[str] = None,
                    file_path: Optional[str] = None,
                    operation: str = "unknown",
                    task_id: Optional[str] = None) -> TokenUsageSnapshot:
        """
        Record token usage for an operation.
        
        Args:
            agent_id: Agent identifier
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
            context_tokens: Context tokens (if different from input)
            session_id: Session identifier
            file_path: File being processed
            operation: Operation type
            task_id: Task identifier
            
        Returns:
            snapshot: Token usage snapshot
        """
        # Calculate totals
        total_tokens = input_tokens + output_tokens
        if context_tokens is None:
            context_tokens = input_tokens
        
        # Determine usage level
        percentage_used = (context_tokens / self.token_limit) * 100
        usage_level = self._determine_usage_level(percentage_used)
        
        # Create snapshot
        snapshot = TokenUsageSnapshot(
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            task_id=task_id,
            file_path=file_path,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            context_tokens=context_tokens,
            percentage_used=percentage_used,
            usage_level=usage_level,
            model=self.model_type,
            operation=operation
        )
        
        # Add to history
        self.usage_history.append(snapshot)
        
        # Update session
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.total_input_tokens += input_tokens
            session.total_output_tokens += output_tokens
            session.total_context_tokens = max(session.total_context_tokens, context_tokens)
            session.peak_context_usage = max(session.peak_context_usage, context_tokens)
            session.operations_count += 1
            
            if file_path:
                session.files_processed += 1
                if session.files_processed > 0:
                    session.average_tokens_per_file = session.total_input_tokens / session.files_processed
        
        # Check for alerts
        self._check_usage_alerts(snapshot)
        
        # Save data
        self.save_monitoring_data()
        
        self.logger.info(f"Recorded usage: {total_tokens} tokens ({percentage_used:.1f}%) for {agent_id}")
        return snapshot

    def _determine_usage_level(self, percentage_used: float) -> UsageLevel:
        """Determine usage level based on percentage"""
        if percentage_used >= 95:
            return UsageLevel.DANGER
        elif percentage_used >= 90:
            return UsageLevel.CRITICAL
        elif percentage_used >= 75:
            return UsageLevel.HIGH
        elif percentage_used >= 50:
            return UsageLevel.MODERATE
        else:
            return UsageLevel.LOW

    def _check_usage_alerts(self, snapshot: TokenUsageSnapshot):
        """Check if usage triggers any alerts"""
        alert_conditions = [
            (UsageLevel.CRITICAL, "Critical token usage - consider agent suspension"),
            (UsageLevel.DANGER, "Dangerous token usage - automatic suspension recommended"),
            (UsageLevel.HIGH, "High token usage - monitor closely")
        ]
        
        for level, message in alert_conditions:
            if snapshot.usage_level == level:
                # Check if we already have a recent alert for this level
                recent_alerts = [a for a in self.alerts[-10:] 
                               if a.agent_id == snapshot.agent_id and 
                               a.usage_level == level]
                
                if not recent_alerts or self._should_create_new_alert(recent_alerts[-1], snapshot):
                    alert = self._create_alert(snapshot, level, message)
                    
                    # Take automatic action for danger level
                    if level == UsageLevel.DANGER:
                        self._handle_danger_level_usage(snapshot, alert)

    def _should_create_new_alert(self, last_alert: TokenUsageAlert, snapshot: TokenUsageSnapshot) -> bool:
        """Determine if a new alert should be created"""
        last_alert_time = datetime.fromisoformat(last_alert.timestamp)
        current_time = datetime.fromisoformat(snapshot.timestamp)
        
        # Create new alert if more than 5 minutes since last alert
        return (current_time - last_alert_time).total_seconds() > 300

    def _create_alert(self, 
                     snapshot: TokenUsageSnapshot, 
                     level: UsageLevel, 
                     message: str) -> TokenUsageAlert:
        """Create a token usage alert"""
        alert_id = f"{snapshot.agent_id}_{level.value}_{int(time.time())}"
        
        alert = TokenUsageAlert(
            alert_id=alert_id,
            timestamp=snapshot.timestamp,
            agent_id=snapshot.agent_id,
            alert_type="token_usage_threshold",
            usage_level=level,
            current_usage=snapshot.context_tokens,
            limit=self.token_limit,
            percentage_used=snapshot.percentage_used,
            message=message,
            action_required=(level in [UsageLevel.CRITICAL, UsageLevel.DANGER])
        )
        
        self.alerts.append(alert)
        
        # Save alert to file
        alert_file = self.alerts_dir / f"{alert_id}.json"
        with open(alert_file, 'w') as f:
            json.dump(asdict(alert), f, indent=2)
        
        self.logger.warning(f"Created alert {alert_id}: {message}")
        return alert

    def _handle_danger_level_usage(self, snapshot: TokenUsageSnapshot, alert: TokenUsageAlert):
        """Handle dangerous token usage levels"""
        try:
            # Import recovery manager if available
            if not self.recovery_manager:
                try:
                    from .agent_recovery_manager import AgentRecoveryManager
                    self.recovery_manager = AgentRecoveryManager(
                        self.workspace_path,
                        self.orchestrator_session_id
                    )
                except ImportError:
                    self.logger.warning("Agent Recovery Manager not available for automatic suspension")
                    return
            
            # Suspend agent
            suspension_reason = f"Token usage at {snapshot.percentage_used:.1f}% - approaching context limit"
            recovery_instructions = [
                "Review current context and clear unnecessary information",
                "Consider breaking large operations into smaller chunks",
                "Resume with reduced context length",
                f"Current usage: {snapshot.context_tokens}/{self.token_limit} tokens"
            ]
            
            checkpoint_id = self.recovery_manager.suspend_agent(
                agent_id=snapshot.agent_id,
                task_id=snapshot.task_id,
                reason=suspension_reason,
                recovery_instructions=recovery_instructions
            )
            
            alert.auto_action_taken = f"Agent suspended - checkpoint: {checkpoint_id}"
            self.logger.critical(f"Automatically suspended agent {snapshot.agent_id} due to token usage")
            
        except Exception as e:
            self.logger.error(f"Failed to automatically suspend agent: {e}")

    def end_session(self, session_id: str) -> Optional[TokenUsageSession]:
        """
        End a token usage monitoring session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            session: Completed session data or None if not found
        """
        if session_id not in self.active_sessions:
            self.logger.warning(f"Session not found: {session_id}")
            return None
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.now().isoformat()
        
        # Calculate efficiency rating
        session.efficiency_rating = self._calculate_efficiency_rating(session)
        
        # Move to completed sessions
        completed_session = session
        del self.active_sessions[session_id]
        
        # Save session report
        session_file = self.reports_dir / f"session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(asdict(completed_session), f, indent=2)
        
        self.logger.info(f"Ended session {session_id} - efficiency: {session.efficiency_rating}")
        return completed_session

    def _calculate_efficiency_rating(self, session: TokenUsageSession) -> str:
        """Calculate efficiency rating for a session"""
        if session.files_processed == 0:
            return "no_files_processed"
        
        # Calculate tokens per file
        tokens_per_file = session.total_input_tokens / session.files_processed
        
        # Define efficiency thresholds (tokens per file)
        if tokens_per_file < 5000:
            return "excellent"
        elif tokens_per_file < 10000:
            return "good"
        elif tokens_per_file < 20000:
            return "moderate"
        elif tokens_per_file < 30000:
            return "poor"
        else:
            return "inefficient"

    def get_current_usage(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current token usage status.
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            usage_status: Current usage information
        """
        # Get recent snapshots
        recent_snapshots = list(self.usage_history)
        if agent_id:
            recent_snapshots = [s for s in recent_snapshots if s.agent_id == agent_id]
        
        if not recent_snapshots:
            return {
                'agent_id': agent_id,
                'current_usage': 0,
                'percentage_used': 0.0,
                'usage_level': UsageLevel.LOW.value,
                'limit': self.token_limit,
                'status': 'no_usage_data'
            }
        
        # Get latest snapshot for each agent
        latest_by_agent = {}
        for snapshot in recent_snapshots:
            if (snapshot.agent_id not in latest_by_agent or 
                snapshot.timestamp > latest_by_agent[snapshot.agent_id].timestamp):
                latest_by_agent[snapshot.agent_id] = snapshot
        
        if agent_id:
            if agent_id in latest_by_agent:
                snapshot = latest_by_agent[agent_id]
                return {
                    'agent_id': agent_id,
                    'current_usage': snapshot.context_tokens,
                    'percentage_used': snapshot.percentage_used,
                    'usage_level': snapshot.usage_level.value,
                    'limit': self.token_limit,
                    'last_update': snapshot.timestamp,
                    'status': 'active'
                }
        
        # Return summary for all agents
        return {
            'agents': {
                aid: {
                    'current_usage': snapshot.context_tokens,
                    'percentage_used': snapshot.percentage_used,
                    'usage_level': snapshot.usage_level.value,
                    'last_update': snapshot.timestamp
                }
                for aid, snapshot in latest_by_agent.items()
            },
            'limit': self.token_limit,
            'status': 'monitoring'
        }

    def generate_usage_report(self, 
                            hours_back: int = 24,
                            agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive usage report.
        
        Args:
            hours_back: Hours of history to include
            agent_id: Optional agent ID to filter by
            
        Returns:
            report: Usage report data
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Filter relevant snapshots
        relevant_snapshots = [
            s for s in self.usage_history 
            if datetime.fromisoformat(s.timestamp) >= cutoff_time
        ]
        
        if agent_id:
            relevant_snapshots = [s for s in relevant_snapshots if s.agent_id == agent_id]
        
        if not relevant_snapshots:
            return {
                'report_id': f"usage_report_{int(time.time())}",
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours_back,
                'agent_id': agent_id,
                'status': 'no_data'
            }
        
        # Calculate statistics
        total_operations = len(relevant_snapshots)
        total_input_tokens = sum(s.input_tokens for s in relevant_snapshots)
        total_output_tokens = sum(s.output_tokens for s in relevant_snapshots)
        total_tokens = total_input_tokens + total_output_tokens
        
        # Peak usage
        peak_usage = max(s.context_tokens for s in relevant_snapshots)
        peak_percentage = (peak_usage / self.token_limit) * 100
        
        # Usage levels distribution
        usage_distribution = defaultdict(int)
        for snapshot in relevant_snapshots:
            usage_distribution[snapshot.usage_level.value] += 1
        
        # Agent statistics
        agent_stats = defaultdict(lambda: {
            'operations': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'peak_usage': 0,
            'files_processed': set()
        })
        
        for snapshot in relevant_snapshots:
            stats = agent_stats[snapshot.agent_id]
            stats['operations'] += 1
            stats['input_tokens'] += snapshot.input_tokens
            stats['output_tokens'] += snapshot.output_tokens
            stats['peak_usage'] = max(stats['peak_usage'], snapshot.context_tokens)
            if snapshot.file_path:
                stats['files_processed'].add(snapshot.file_path)
        
        # Convert sets to counts
        for stats in agent_stats.values():
            stats['files_processed'] = len(stats['files_processed'])
        
        # Recent alerts
        recent_alert_time = cutoff_time
        recent_alerts = [
            a for a in self.alerts 
            if datetime.fromisoformat(a.timestamp) >= recent_alert_time
        ]
        if agent_id:
            recent_alerts = [a for a in recent_alerts if a.agent_id == agent_id]
        
        report = {
            'report_id': f"usage_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'period_hours': hours_back,
            'agent_id': agent_id,
            'model_type': self.model_type,
            'token_limit': self.token_limit,
            'summary': {
                'total_operations': total_operations,
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'total_tokens': total_tokens,
                'peak_usage': peak_usage,
                'peak_percentage': peak_percentage,
                'average_tokens_per_operation': total_tokens / total_operations if total_operations > 0 else 0
            },
            'usage_distribution': dict(usage_distribution),
            'agent_statistics': {k: dict(v) for k, v in agent_stats.items()},
            'recent_alerts': [asdict(a) for a in recent_alerts],
            'efficiency_metrics': self._calculate_efficiency_metrics(relevant_snapshots)
        }
        
        # Save report
        report_file = self.reports_dir / f"{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

    def _calculate_efficiency_metrics(self, snapshots: List[TokenUsageSnapshot]) -> Dict[str, Any]:
        """Calculate efficiency metrics from snapshots"""
        if not snapshots:
            return {}
        
        # Tokens per file analysis
        file_operations = defaultdict(list)
        for snapshot in snapshots:
            if snapshot.file_path:
                file_operations[snapshot.file_path].append(snapshot)
        
        tokens_per_file = []
        for file_path, file_snapshots in file_operations.items():
            total_tokens = sum(s.total_tokens for s in file_snapshots)
            tokens_per_file.append(total_tokens)
        
        if tokens_per_file:
            efficiency_metrics = {
                'files_processed': len(tokens_per_file),
                'average_tokens_per_file': statistics.mean(tokens_per_file),
                'median_tokens_per_file': statistics.median(tokens_per_file),
                'max_tokens_per_file': max(tokens_per_file),
                'min_tokens_per_file': min(tokens_per_file)
            }
            
            if len(tokens_per_file) > 1:
                efficiency_metrics['stdev_tokens_per_file'] = statistics.stdev(tokens_per_file)
        else:
            efficiency_metrics = {
                'files_processed': 0,
                'note': 'No file-based operations recorded'
            }
        
        return efficiency_metrics

    def start_monitoring(self, interval: float = 30.0):
        """
        Start continuous monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Started token usage monitoring (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Stopped token usage monitoring")

    def _monitoring_loop(self, interval: float):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for stale sessions
                self._check_stale_sessions()
                
                # Save monitoring data periodically
                self.save_monitoring_data()
                
                # Generate periodic reports
                if int(time.time()) % 1800 == 0:  # Every 30 minutes
                    self.generate_usage_report(hours_back=1)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)

    def _check_stale_sessions(self):
        """Check for stale sessions that should be closed"""
        current_time = datetime.now()
        stale_threshold = timedelta(hours=2)
        
        stale_sessions = []
        for session_id, session in self.active_sessions.items():
            session_start = datetime.fromisoformat(session.start_time)
            if current_time - session_start > stale_threshold:
                stale_sessions.append(session_id)
        
        for session_id in stale_sessions:
            self.logger.warning(f"Closing stale session: {session_id}")
            self.end_session(session_id)

    def save_monitoring_data(self):
        """Save monitoring data to files"""
        try:
            # Save active sessions
            sessions_data = {sid: asdict(session) for sid, session in self.active_sessions.items()}
            sessions_file = self.usage_dir / "active_sessions.json"
            with open(sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
            
            # Save recent usage history
            recent_history = list(self.usage_history)[-100:]  # Keep last 100
            history_data = [asdict(snapshot) for snapshot in recent_history]
            history_file = self.usage_dir / "recent_usage.json"
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save monitoring data: {e}")

    def load_monitoring_data(self):
        """Load existing monitoring data"""
        try:
            # Load recent usage history
            history_file = self.usage_dir / "recent_usage.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                for snapshot_data in history_data:
                    # Convert usage_level back to enum
                    snapshot_data['usage_level'] = UsageLevel(snapshot_data['usage_level'])
                    snapshot = TokenUsageSnapshot(**snapshot_data)
                    self.usage_history.append(snapshot)
            
            # Load alerts
            for alert_file in self.alerts_dir.glob("*.json"):
                try:
                    with open(alert_file, 'r') as f:
                        alert_data = json.load(f)
                    # Convert usage_level back to enum
                    alert_data['usage_level'] = UsageLevel(alert_data['usage_level'])
                    alert = TokenUsageAlert(**alert_data)
                    self.alerts.append(alert)
                except Exception as e:
                    self.logger.warning(f"Failed to load alert {alert_file}: {e}")
            
            # Sort alerts by timestamp
            self.alerts.sort(key=lambda a: a.timestamp)
            
        except Exception as e:
            self.logger.warning(f"Failed to load monitoring data: {e}")


def main():
    """Example usage and CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Token Usage Monitor")
    parser.add_argument("--workspace", "-w", required=True, help="Workspace path")
    parser.add_argument("--model", "-m", default="claude-3-sonnet", help="Claude model type")
    parser.add_argument("--limit", "-l", type=int, help="Custom token limit")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring")
    parser.add_argument("--report", "-r", action="store_true", help="Generate usage report")
    parser.add_argument("--status", "-s", action="store_true", help="Show current status")
    parser.add_argument("--agent-id", "-a", help="Agent ID for operations")
    
    args = parser.parse_args()
    
    monitor = TokenUsageMonitor(args.workspace, args.model, args.limit)
    
    if args.monitor:
        monitor.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    
    elif args.report:
        report = monitor.generate_usage_report(agent_id=args.agent_id)
        print(json.dumps(report, indent=2))
    
    elif args.status:
        status = monitor.get_current_usage(args.agent_id)
        print(json.dumps(status, indent=2))
    
    else:
        print("Use --monitor, --report, or --status")


if __name__ == "__main__":
    main()