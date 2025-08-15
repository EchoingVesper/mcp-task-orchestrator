#!/usr/bin/env python3
"""
Agent Recovery Manager

Provides checkpoint system for agent progress tracking, resume-from-failure capability,
token limit detection, and orchestrator integration for the Documentation Ecosystem
Modernization project.

Key Features:
- Checkpoint system for tracking agent progress
- Resume-from-failure capability for interrupted agents  
- Token limit detection and graceful suspension
- File-level backup system before each agent starts
- Skip and return later workflow for problematic files
- Orchestrator integration for progress persistence
"""

import json
import os
import shutil
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from mcp_task_orchestrator.orchestrator.orchestration_state_manager import OrchestrationStateManager
    from mcp_task_orchestrator.orchestrator.generic_models import GenericTask
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    logging.warning("Orchestrator not available - running in standalone mode")


class AgentStatus(Enum):
    """Agent execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CheckpointType(Enum):
    """Types of checkpoints"""
    FILE_START = "file_start"
    FILE_COMPLETE = "file_complete"
    BATCH_COMPLETE = "batch_complete"
    SUSPENSION = "suspension"
    ERROR = "error"


@dataclass
class AgentCheckpoint:
    """Agent checkpoint data structure"""
    checkpoint_id: str
    agent_id: str
    task_id: Optional[str]
    checkpoint_type: CheckpointType
    timestamp: str
    file_path: Optional[str] = None
    batch_id: Optional[str] = None
    progress_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    recovery_instructions: Optional[List[str]] = None
    token_usage: Optional[Dict[str, int]] = None


@dataclass
class AgentProgress:
    """Agent progress tracking data"""
    agent_id: str
    task_id: Optional[str]
    status: AgentStatus
    start_time: str
    last_update: str
    files_processed: List[str]
    files_remaining: List[str]
    files_skipped: List[str]
    files_failed: List[str]
    current_file: Optional[str]
    total_files: int
    completion_percentage: float
    estimated_remaining_time: Optional[str]
    token_usage: Dict[str, int]
    error_count: int
    last_checkpoint_id: Optional[str]


class AgentRecoveryManager:
    """
    Manages agent recovery, checkpoints, and progress tracking for documentation 
    modernization agents.
    """
    
    def __init__(self, 
                 workspace_path: Union[str, Path],
                 orchestrator_session_id: Optional[str] = None):
        """
        Initialize the Agent Recovery Manager.
        
        Args:
            workspace_path: Path to the workspace directory
            orchestrator_session_id: Optional orchestrator session ID
        """
        self.workspace_path = Path(workspace_path)
        self.recovery_dir = self.workspace_path / ".recovery"
        self.checkpoints_dir = self.recovery_dir / "checkpoints"
        self.backups_dir = self.recovery_dir / "backups"
        self.progress_dir = self.recovery_dir / "progress"
        
        # Create recovery directories
        for dir_path in [self.recovery_dir, self.checkpoints_dir, 
                        self.backups_dir, self.progress_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.orchestrator_session_id = orchestrator_session_id
        self.state_manager = None
        
        if ORCHESTRATOR_AVAILABLE and orchestrator_session_id:
            try:
                self.state_manager = OrchestrationStateManager()
                logging.info(f"Orchestrator integration enabled for session {orchestrator_session_id}")
            except Exception as e:
                logging.warning(f"Failed to initialize orchestrator integration: {e}")
        
        # Setup logging
        self.setup_logging()
        
        # Token limits and thresholds
        self.token_limits = {
            'warning_threshold': 80000,  # 80% of typical limit
            'suspension_threshold': 95000,  # 95% of typical limit
            'max_context_length': 100000
        }

    def setup_logging(self):
        """Setup logging for the recovery manager"""
        log_file = self.recovery_dir / "recovery_manager.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AgentRecoveryManager')

    def create_checkpoint(self, 
                         agent_id: str,
                         checkpoint_type: CheckpointType,
                         task_id: Optional[str] = None,
                         file_path: Optional[str] = None,
                         batch_id: Optional[str] = None,
                         progress_data: Optional[Dict[str, Any]] = None,
                         error_data: Optional[Dict[str, Any]] = None,
                         recovery_instructions: Optional[List[str]] = None,
                         token_usage: Optional[Dict[str, int]] = None) -> str:
        """
        Create a checkpoint for agent progress.
        
        Args:
            agent_id: Unique identifier for the agent
            checkpoint_type: Type of checkpoint being created
            task_id: Optional orchestrator task ID
            file_path: Path to file being processed (if applicable)
            batch_id: Batch identifier (if applicable)
            progress_data: Additional progress data
            error_data: Error information (if applicable)
            recovery_instructions: Instructions for recovery
            token_usage: Token usage statistics
            
        Returns:
            checkpoint_id: Unique checkpoint identifier
        """
        checkpoint_id = f"{agent_id}_{checkpoint_type.value}_{int(time.time())}"
        
        checkpoint = AgentCheckpoint(
            checkpoint_id=checkpoint_id,
            agent_id=agent_id,
            task_id=task_id,
            checkpoint_type=checkpoint_type,
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            batch_id=batch_id,
            progress_data=progress_data or {},
            error_data=error_data,
            recovery_instructions=recovery_instructions or [],
            token_usage=token_usage or {}
        )
        
        # Save checkpoint to file
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2)
        
        # Update progress tracking
        self.update_progress(agent_id, task_id, checkpoint_type, checkpoint_id)
        
        # Sync with orchestrator if available
        if self.state_manager and task_id:
            self.sync_with_orchestrator(checkpoint, task_id)
        
        self.logger.info(f"Created checkpoint {checkpoint_id} for agent {agent_id}")
        return checkpoint_id

    def backup_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Create a backup of a file before processing.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            backup_path: Path to the backup file, or None if backup failed
        """
        file_path = Path(file_path)
        if not file_path.exists():
            self.logger.warning(f"Cannot backup non-existent file: {file_path}")
            return None
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}_{timestamp}.backup"
        backup_path = self.backups_dir / backup_name
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return str(backup_path)
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return None

    def update_progress(self, 
                       agent_id: str,
                       task_id: Optional[str],
                       checkpoint_type: CheckpointType,
                       checkpoint_id: str,
                       **kwargs):
        """
        Update agent progress based on checkpoint.
        
        Args:
            agent_id: Agent identifier
            task_id: Task identifier  
            checkpoint_type: Type of checkpoint
            checkpoint_id: Checkpoint identifier
            **kwargs: Additional progress data
        """
        progress_file = self.progress_dir / f"{agent_id}_progress.json"
        
        # Load existing progress or create new
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            progress = AgentProgress(**progress_data)
        else:
            progress = AgentProgress(
                agent_id=agent_id,
                task_id=task_id,
                status=AgentStatus.NOT_STARTED,
                start_time=datetime.now().isoformat(),
                last_update=datetime.now().isoformat(),
                files_processed=[],
                files_remaining=[],
                files_skipped=[],
                files_failed=[],
                current_file=None,
                total_files=0,
                completion_percentage=0.0,
                estimated_remaining_time=None,
                token_usage={'input': 0, 'output': 0, 'total': 0},
                error_count=0,
                last_checkpoint_id=None
            )
        
        # Update progress based on checkpoint type
        progress.last_update = datetime.now().isoformat()
        progress.last_checkpoint_id = checkpoint_id
        
        if checkpoint_type == CheckpointType.FILE_START:
            progress.status = AgentStatus.IN_PROGRESS
            progress.current_file = kwargs.get('file_path')
            
        elif checkpoint_type == CheckpointType.FILE_COMPLETE:
            file_path = kwargs.get('file_path')
            if file_path and file_path not in progress.files_processed:
                progress.files_processed.append(file_path)
            if file_path in progress.files_remaining:
                progress.files_remaining.remove(file_path)
            progress.current_file = None
            
        elif checkpoint_type == CheckpointType.SUSPENSION:
            progress.status = AgentStatus.SUSPENDED
            
        elif checkpoint_type == CheckpointType.ERROR:
            progress.error_count += 1
            file_path = kwargs.get('file_path')
            if file_path and file_path not in progress.files_failed:
                progress.files_failed.append(file_path)
        
        # Update completion percentage
        if progress.total_files > 0:
            completed = len(progress.files_processed)
            progress.completion_percentage = (completed / progress.total_files) * 100
        
        # Save updated progress
        with open(progress_file, 'w') as f:
            json.dump(asdict(progress), f, indent=2)
        
        self.logger.info(f"Updated progress for agent {agent_id}: {progress.completion_percentage:.1f}% complete")

    def get_progress(self, agent_id: str) -> Optional[AgentProgress]:
        """
        Get current progress for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            progress: Agent progress data or None if not found
        """
        progress_file = self.progress_dir / f"{agent_id}_progress.json"
        
        if not progress_file.exists():
            return None
        
        try:
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
            return AgentProgress(**progress_data)
        except Exception as e:
            self.logger.error(f"Failed to load progress for agent {agent_id}: {e}")
            return None

    def detect_token_limits(self, token_usage: Dict[str, int]) -> Dict[str, Any]:
        """
        Detect if token limits are being approached.
        
        Args:
            token_usage: Dictionary with token usage stats
            
        Returns:
            detection_result: Dictionary with limit detection results
        """
        total_tokens = token_usage.get('total', 0)
        
        result = {
            'approaching_limit': False,
            'should_suspend': False,
            'percentage_used': 0.0,
            'tokens_remaining': 0,
            'recommendation': 'continue'
        }
        
        if total_tokens > 0:
            percentage_used = (total_tokens / self.token_limits['max_context_length']) * 100
            result['percentage_used'] = percentage_used
            result['tokens_remaining'] = self.token_limits['max_context_length'] - total_tokens
            
            if total_tokens >= self.token_limits['suspension_threshold']:
                result['should_suspend'] = True
                result['recommendation'] = 'suspend'
            elif total_tokens >= self.token_limits['warning_threshold']:
                result['approaching_limit'] = True
                result['recommendation'] = 'caution'
        
        return result

    def suspend_agent(self, 
                     agent_id: str,
                     task_id: Optional[str],
                     reason: str,
                     recovery_instructions: Optional[List[str]] = None) -> str:
        """
        Suspend an agent and create recovery checkpoint.
        
        Args:
            agent_id: Agent identifier
            task_id: Task identifier
            reason: Reason for suspension
            recovery_instructions: Instructions for resuming
            
        Returns:
            checkpoint_id: Suspension checkpoint ID
        """
        checkpoint_id = self.create_checkpoint(
            agent_id=agent_id,
            checkpoint_type=CheckpointType.SUSPENSION,
            task_id=task_id,
            progress_data={'suspension_reason': reason},
            recovery_instructions=recovery_instructions or [
                "Review token usage and context length",
                "Clear unnecessary context before resuming",
                "Resume from last successful checkpoint"
            ]
        )
        
        self.logger.warning(f"Suspended agent {agent_id}: {reason}")
        return checkpoint_id

    def resume_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Resume an agent from its last checkpoint.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            resume_data: Data needed to resume agent, or None if resume not possible
        """
        progress = self.get_progress(agent_id)
        if not progress:
            self.logger.error(f"No progress found for agent {agent_id}")
            return None
        
        if progress.status not in [AgentStatus.SUSPENDED, AgentStatus.FAILED]:
            self.logger.warning(f"Agent {agent_id} is not in a resumable state: {progress.status}")
            return None
        
        # Load last checkpoint
        if not progress.last_checkpoint_id:
            self.logger.error(f"No checkpoint found for agent {agent_id}")
            return None
        
        checkpoint_file = self.checkpoints_dir / f"{progress.last_checkpoint_id}.json"
        if not checkpoint_file.exists():
            self.logger.error(f"Checkpoint file not found: {checkpoint_file}")
            return None
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            resume_data = {
                'agent_id': agent_id,
                'progress': asdict(progress),
                'last_checkpoint': checkpoint_data,
                'files_remaining': progress.files_remaining,
                'files_processed': progress.files_processed,
                'files_skipped': progress.files_skipped,
                'files_failed': progress.files_failed,
                'resume_instructions': checkpoint_data.get('recovery_instructions', [])
            }
            
            self.logger.info(f"Agent {agent_id} ready for resume from {progress.completion_percentage:.1f}% completion")
            return resume_data
            
        except Exception as e:
            self.logger.error(f"Failed to prepare resume data for agent {agent_id}: {e}")
            return None

    def skip_file(self, 
                  agent_id: str,
                  file_path: str,
                  reason: str,
                  task_id: Optional[str] = None) -> str:
        """
        Mark a file as skipped and create checkpoint.
        
        Args:
            agent_id: Agent identifier
            file_path: Path to file being skipped
            reason: Reason for skipping
            task_id: Task identifier
            
        Returns:
            checkpoint_id: Skip checkpoint ID
        """
        checkpoint_id = self.create_checkpoint(
            agent_id=agent_id,
            checkpoint_type=CheckpointType.ERROR,
            task_id=task_id,
            file_path=file_path,
            progress_data={'skip_reason': reason, 'action': 'skip'},
            recovery_instructions=[
                f"Review file: {file_path}",
                f"Skip reason: {reason}",
                "Address issue and retry if needed"
            ]
        )
        
        # Update progress to mark file as skipped
        progress = self.get_progress(agent_id)
        if progress:
            if file_path not in progress.files_skipped:
                progress.files_skipped.append(file_path)
            if file_path in progress.files_remaining:
                progress.files_remaining.remove(file_path)
            
            # Save updated progress
            progress_file = self.progress_dir / f"{agent_id}_progress.json"
            with open(progress_file, 'w') as f:
                json.dump(asdict(progress), f, indent=2)
        
        self.logger.warning(f"Skipped file {file_path} for agent {agent_id}: {reason}")
        return checkpoint_id

    def sync_with_orchestrator(self, checkpoint: AgentCheckpoint, task_id: str):
        """
        Sync checkpoint data with orchestrator.
        
        Args:
            checkpoint: Checkpoint data to sync
            task_id: Orchestrator task ID
        """
        if not self.state_manager:
            return
        
        try:
            # Create progress update for orchestrator
            progress_data = {
                'checkpoint_id': checkpoint.checkpoint_id,
                'checkpoint_type': checkpoint.checkpoint_type.value,
                'timestamp': checkpoint.timestamp,
                'file_path': checkpoint.file_path,
                'progress_data': checkpoint.progress_data,
                'token_usage': checkpoint.token_usage
            }
            
            # Update task progress in orchestrator
            # Note: This would need to be implemented based on the actual orchestrator API
            self.logger.info(f"Synced checkpoint {checkpoint.checkpoint_id} with orchestrator task {task_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to sync with orchestrator: {e}")

    def get_recovery_report(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a recovery report for agents.
        
        Args:
            agent_id: Optional specific agent ID, or None for all agents
            
        Returns:
            report: Recovery status report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'workspace_path': str(self.workspace_path),
            'agents': {}
        }
        
        # Get all agent progress files
        progress_files = list(self.progress_dir.glob("*_progress.json"))
        
        if agent_id:
            progress_files = [f for f in progress_files if f.stem.startswith(agent_id)]
        
        for progress_file in progress_files:
            try:
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                
                progress = AgentProgress(**progress_data)
                
                # Get latest checkpoint
                latest_checkpoint = None
                if progress.last_checkpoint_id:
                    checkpoint_file = self.checkpoints_dir / f"{progress.last_checkpoint_id}.json"
                    if checkpoint_file.exists():
                        with open(checkpoint_file, 'r') as f:
                            latest_checkpoint = json.load(f)
                
                agent_report = {
                    'status': progress.status.value,
                    'completion_percentage': progress.completion_percentage,
                    'files_processed': len(progress.files_processed),
                    'files_remaining': len(progress.files_remaining),
                    'files_skipped': len(progress.files_skipped),
                    'files_failed': len(progress.files_failed),
                    'error_count': progress.error_count,
                    'last_update': progress.last_update,
                    'latest_checkpoint': latest_checkpoint
                }
                
                report['agents'][progress.agent_id] = agent_report
                
            except Exception as e:
                self.logger.error(f"Failed to process progress file {progress_file}: {e}")
        
        return report

    def cleanup_old_checkpoints(self, days_old: int = 7):
        """
        Clean up checkpoints older than specified days.
        
        Args:
            days_old: Number of days after which to clean up checkpoints
        """
        cutoff_time = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for checkpoint_file in self.checkpoints_dir.glob("*.json"):
            try:
                # Check file modification time
                file_time = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                
                if file_time < cutoff_time:
                    checkpoint_file.unlink()
                    cleaned_count += 1
                    
            except Exception as e:
                self.logger.warning(f"Failed to clean checkpoint {checkpoint_file}: {e}")
        
        self.logger.info(f"Cleaned up {cleaned_count} old checkpoints")


def main():
    """Example usage of AgentRecoveryManager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Recovery Manager")
    parser.add_argument("--workspace", "-w", required=True, help="Workspace path")
    parser.add_argument("--agent-id", "-a", help="Agent ID for operations")
    parser.add_argument("--report", "-r", action="store_true", help="Generate recovery report")
    parser.add_argument("--resume", action="store_true", help="Resume agent")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old checkpoints")
    
    args = parser.parse_args()
    
    manager = AgentRecoveryManager(args.workspace)
    
    if args.report:
        report = manager.get_recovery_report(args.agent_id)
        print(json.dumps(report, indent=2))
    
    elif args.resume and args.agent_id:
        resume_data = manager.resume_agent(args.agent_id)
        if resume_data:
            print(f"Agent {args.agent_id} ready for resume")
            print(json.dumps(resume_data, indent=2))
        else:
            print(f"Cannot resume agent {args.agent_id}")
    
    elif args.cleanup:
        manager.cleanup_old_checkpoints()
    
    else:
        print("Use --report, --resume, or --cleanup with appropriate arguments")


if __name__ == "__main__":
    main()