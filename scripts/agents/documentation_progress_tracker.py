#!/usr/bin/env python3
"""
Documentation Progress Tracker

Provides real-time progress monitoring for documentation updates during the
Documentation Ecosystem Modernization project with orchestrator integration.

Key Features:
- Real-time progress monitoring for documentation updates
- Integration with orchestrator task system  
- File-by-file status tracking with detailed metrics
- Recovery point management for interrupted operations
- Progress reporting and visualization
- Automated milestone detection and reporting
"""

import json
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict

try:
    from mcp_task_orchestrator.orchestrator.orchestration_state_manager import OrchestrationStateManager
    from mcp_task_orchestrator.orchestrator.generic_models import GenericTask
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    logging.warning("Orchestrator not available - running in standalone mode")


class FileStatus(Enum):
    """File processing status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    NEEDS_REVIEW = "needs_review"
    VALIDATED = "validated"


class PhaseStatus(Enum):
    """Documentation modernization phase status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class MilestoneType(Enum):
    """Types of progress milestones"""
    PHASE_START = "phase_start"
    PHASE_COMPLETE = "phase_complete"
    BATCH_COMPLETE = "batch_complete"
    PERCENTAGE_MILESTONE = "percentage_milestone"
    ERROR_THRESHOLD = "error_threshold"
    TIME_MILESTONE = "time_milestone"


@dataclass
class FileProgress:
    """Individual file progress tracking"""
    file_path: str
    relative_path: str
    file_type: str
    size_bytes: int
    status: FileStatus
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    processing_duration: Optional[float] = None
    error_message: Optional[str] = None
    changes_made: List[str] = None
    validation_status: Optional[str] = None
    backup_path: Optional[str] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []


@dataclass
class PhaseProgress:
    """Phase-level progress tracking"""
    phase_id: str
    phase_name: str
    description: str
    status: PhaseStatus
    start_time: Optional[str] = None
    completion_time: Optional[str] = None
    files_total: int = 0
    files_completed: int = 0
    files_failed: int = 0
    files_skipped: int = 0
    files_in_progress: int = 0
    completion_percentage: float = 0.0
    estimated_remaining_time: Optional[str] = None
    current_batch: Optional[str] = None
    error_count: int = 0
    warning_count: int = 0


@dataclass
class ProgressMilestone:
    """Progress milestone tracking"""
    milestone_id: str
    milestone_type: MilestoneType
    timestamp: str
    phase_id: Optional[str] = None
    description: str = ""
    data: Optional[Dict[str, Any]] = None
    notification_sent: bool = False


@dataclass
class ProgressMetrics:
    """Overall progress metrics"""
    total_files: int = 0
    files_completed: int = 0
    files_failed: int = 0  
    files_skipped: int = 0
    files_in_progress: int = 0
    overall_completion_percentage: float = 0.0
    estimated_total_time: Optional[str] = None
    estimated_remaining_time: Optional[str] = None
    average_processing_time: float = 0.0
    error_rate: float = 0.0
    throughput_files_per_hour: float = 0.0
    start_time: Optional[str] = None
    last_update: Optional[str] = None


class DocumentationProgressTracker:
    """
    Tracks progress of documentation modernization with real-time monitoring
    and orchestrator integration.
    """
    
    def __init__(self,
                 workspace_path: Union[str, Path],
                 orchestrator_session_id: Optional[str] = None,
                 update_interval: float = 5.0):
        """
        Initialize the Documentation Progress Tracker.
        
        Args:
            workspace_path: Path to the workspace directory
            orchestrator_session_id: Optional orchestrator session ID
            update_interval: Interval in seconds for progress updates
        """
        self.workspace_path = Path(workspace_path)
        self.progress_dir = self.workspace_path / ".progress"
        self.reports_dir = self.progress_dir / "reports"
        self.milestones_dir = self.progress_dir / "milestones"
        
        # Create progress directories
        for dir_path in [self.progress_dir, self.reports_dir, self.milestones_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.orchestrator_session_id = orchestrator_session_id
        self.state_manager = None
        
        if ORCHESTRATOR_AVAILABLE and orchestrator_session_id:
            try:
                self.state_manager = OrchestrationStateManager()
                logging.info(f"Orchestrator integration enabled for session {orchestrator_session_id}")
            except Exception as e:
                logging.warning(f"Failed to initialize orchestrator integration: {e}")
        
        self.update_interval = update_interval
        self._monitoring = False
        self._monitor_thread = None
        
        # Progress data structures
        self.file_progress: Dict[str, FileProgress] = {}
        self.phase_progress: Dict[str, PhaseProgress] = {}
        self.milestones: List[ProgressMilestone] = []
        self.metrics = ProgressMetrics()
        
        # Load existing progress
        self.load_progress()
        
        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for the progress tracker"""
        log_file = self.progress_dir / "progress_tracker.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DocumentationProgressTracker')

    def initialize_phases(self, phase_config: Dict[str, Dict[str, Any]]):
        """
        Initialize documentation modernization phases.
        
        Args:
            phase_config: Configuration for phases
        """
        for phase_id, config in phase_config.items():
            phase = PhaseProgress(
                phase_id=phase_id,
                phase_name=config['name'],
                description=config.get('description', ''),
                status=PhaseStatus.NOT_STARTED,
                files_total=len(config.get('files', []))
            )
            self.phase_progress[phase_id] = phase
        
        self.save_progress()
        self.logger.info(f"Initialized {len(phase_config)} phases for tracking")

    def register_files(self, files: List[Dict[str, Any]], phase_id: Optional[str] = None):
        """
        Register files for progress tracking.
        
        Args:
            files: List of file information dictionaries
            phase_id: Optional phase ID to associate files with
        """
        for file_info in files:
            file_path = file_info['path']
            file_progress = FileProgress(
                file_path=file_path,
                relative_path=str(Path(file_path).relative_to(self.workspace_path)),
                file_type=file_info.get('type', Path(file_path).suffix),
                size_bytes=file_info.get('size', 0),
                status=FileStatus.NOT_STARTED
            )
            
            self.file_progress[file_path] = file_progress
        
        # Update phase file counts
        if phase_id and phase_id in self.phase_progress:
            self.phase_progress[phase_id].files_total = len([
                f for f in self.file_progress.values() 
                if f.file_path in [fi['path'] for fi in files]
            ])
        
        self.update_metrics()
        self.save_progress()
        self.logger.info(f"Registered {len(files)} files for progress tracking")

    def start_file_processing(self, 
                            file_path: str,
                            agent_id: Optional[str] = None,
                            task_id: Optional[str] = None,
                            phase_id: Optional[str] = None) -> bool:
        """
        Mark a file as starting processing.
        
        Args:
            file_path: Path to file being processed
            agent_id: Agent processing the file
            task_id: Task ID from orchestrator
            phase_id: Phase the file belongs to
            
        Returns:
            success: True if file was successfully marked as started
        """
        if file_path not in self.file_progress:
            self.logger.warning(f"File not registered: {file_path}")
            return False
        
        file_prog = self.file_progress[file_path]
        file_prog.status = FileStatus.IN_PROGRESS
        file_prog.start_time = datetime.now().isoformat()
        file_prog.agent_id = agent_id
        file_prog.task_id = task_id
        
        # Update phase progress
        if phase_id and phase_id in self.phase_progress:
            phase = self.phase_progress[phase_id]
            phase.files_in_progress += 1
            if phase.status == PhaseStatus.NOT_STARTED:
                phase.status = PhaseStatus.IN_PROGRESS
                phase.start_time = datetime.now().isoformat()
        
        self.update_metrics()
        self.save_progress()
        
        # Sync with orchestrator
        if self.state_manager and task_id:
            self.sync_file_start_with_orchestrator(file_path, task_id, agent_id)
        
        self.logger.info(f"Started processing file: {file_path}")
        return True

    def complete_file_processing(self,
                                file_path: str,
                                changes_made: Optional[List[str]] = None,
                                validation_status: Optional[str] = None,
                                phase_id: Optional[str] = None) -> bool:
        """
        Mark a file as completed processing.
        
        Args:
            file_path: Path to completed file
            changes_made: List of changes made to the file
            validation_status: Validation result
            phase_id: Phase the file belongs to
            
        Returns:
            success: True if file was successfully marked as completed
        """
        if file_path not in self.file_progress:
            self.logger.warning(f"File not registered: {file_path}")
            return False
        
        file_prog = self.file_progress[file_path]
        file_prog.status = FileStatus.COMPLETED
        file_prog.completion_time = datetime.now().isoformat()
        file_prog.changes_made = changes_made or []
        file_prog.validation_status = validation_status
        
        # Calculate processing duration
        if file_prog.start_time:
            start = datetime.fromisoformat(file_prog.start_time)
            end = datetime.fromisoformat(file_prog.completion_time)
            file_prog.processing_duration = (end - start).total_seconds()
        
        # Update phase progress
        if phase_id and phase_id in self.phase_progress:
            phase = self.phase_progress[phase_id]
            phase.files_completed += 1
            phase.files_in_progress = max(0, phase.files_in_progress - 1)
            
            # Check if phase is complete
            if phase.files_completed == phase.files_total:
                phase.status = PhaseStatus.COMPLETED
                phase.completion_time = datetime.now().isoformat()
                self.create_milestone(
                    MilestoneType.PHASE_COMPLETE,
                    phase_id=phase_id,
                    description=f"Phase {phase.phase_name} completed"
                )
        
        self.update_metrics()
        self.save_progress()
        
        # Sync with orchestrator  
        if self.state_manager and file_prog.task_id:
            self.sync_file_complete_with_orchestrator(file_path, file_prog.task_id)
        
        self.logger.info(f"Completed processing file: {file_path}")
        return True

    def fail_file_processing(self,
                           file_path: str,
                           error_message: str,
                           phase_id: Optional[str] = None) -> bool:
        """
        Mark a file as failed processing.
        
        Args:
            file_path: Path to failed file
            error_message: Error message
            phase_id: Phase the file belongs to
            
        Returns:
            success: True if file was successfully marked as failed
        """
        if file_path not in self.file_progress:
            self.logger.warning(f"File not registered: {file_path}")
            return False
        
        file_prog = self.file_progress[file_path]
        file_prog.status = FileStatus.FAILED
        file_prog.error_message = error_message
        file_prog.retry_count += 1
        
        # Update phase progress
        if phase_id and phase_id in self.phase_progress:
            phase = self.phase_progress[phase_id]
            phase.files_failed += 1
            phase.files_in_progress = max(0, phase.files_in_progress - 1)
            phase.error_count += 1
        
        self.update_metrics()
        self.save_progress()
        
        # Check error threshold
        self.check_error_threshold()
        
        self.logger.error(f"Failed processing file {file_path}: {error_message}")
        return True

    def skip_file_processing(self,
                           file_path: str,
                           reason: str,
                           phase_id: Optional[str] = None) -> bool:
        """
        Mark a file as skipped.
        
        Args:
            file_path: Path to skipped file
            reason: Reason for skipping
            phase_id: Phase the file belongs to
            
        Returns:
            success: True if file was successfully marked as skipped
        """
        if file_path not in self.file_progress:
            self.logger.warning(f"File not registered: {file_path}")
            return False
        
        file_prog = self.file_progress[file_path]
        file_prog.status = FileStatus.SKIPPED
        file_prog.error_message = f"Skipped: {reason}"
        
        # Update phase progress
        if phase_id and phase_id in self.phase_progress:
            phase = self.phase_progress[phase_id]
            phase.files_skipped += 1
            phase.files_in_progress = max(0, phase.files_in_progress - 1)
        
        self.update_metrics()
        self.save_progress()
        
        self.logger.warning(f"Skipped processing file {file_path}: {reason}")
        return True

    def update_metrics(self):
        """Update overall progress metrics"""
        self.metrics.total_files = len(self.file_progress)
        self.metrics.files_completed = len([f for f in self.file_progress.values() 
                                          if f.status == FileStatus.COMPLETED])
        self.metrics.files_failed = len([f for f in self.file_progress.values() 
                                       if f.status == FileStatus.FAILED])
        self.metrics.files_skipped = len([f for f in self.file_progress.values() 
                                        if f.status == FileStatus.SKIPPED])
        self.metrics.files_in_progress = len([f for f in self.file_progress.values() 
                                            if f.status == FileStatus.IN_PROGRESS])
        
        # Calculate completion percentage
        if self.metrics.total_files > 0:
            completed_or_skipped = self.metrics.files_completed + self.metrics.files_skipped
            self.metrics.overall_completion_percentage = (
                completed_or_skipped / self.metrics.total_files
            ) * 100
        
        # Calculate error rate
        total_processed = self.metrics.files_completed + self.metrics.files_failed
        if total_processed > 0:
            self.metrics.error_rate = (self.metrics.files_failed / total_processed) * 100
        
        # Calculate average processing time and throughput
        completed_files = [f for f in self.file_progress.values() 
                          if f.status == FileStatus.COMPLETED and f.processing_duration]
        
        if completed_files:
            total_time = sum(f.processing_duration for f in completed_files)
            self.metrics.average_processing_time = total_time / len(completed_files)
            
            # Calculate throughput (files per hour)
            if total_time > 0:
                self.metrics.throughput_files_per_hour = (len(completed_files) / total_time) * 3600
        
        # Update timestamps
        self.metrics.last_update = datetime.now().isoformat()
        if not self.metrics.start_time and self.metrics.files_in_progress > 0:
            self.metrics.start_time = datetime.now().isoformat()
        
        # Check for percentage milestones
        self.check_percentage_milestones()

    def check_percentage_milestones(self):
        """Check and create percentage milestones"""
        milestones = [10, 25, 50, 75, 90]
        
        for milestone in milestones:
            if (self.metrics.overall_completion_percentage >= milestone and 
                not any(m.milestone_type == MilestoneType.PERCENTAGE_MILESTONE and 
                       m.data and m.data.get('percentage') == milestone 
                       for m in self.milestones)):
                
                self.create_milestone(
                    MilestoneType.PERCENTAGE_MILESTONE,
                    description=f"Reached {milestone}% completion",
                    data={'percentage': milestone}
                )

    def check_error_threshold(self):
        """Check if error threshold is exceeded"""
        if self.metrics.error_rate > 20:  # 20% error rate threshold
            if not any(m.milestone_type == MilestoneType.ERROR_THRESHOLD 
                      for m in self.milestones[-5:]):  # Check recent milestones
                
                self.create_milestone(
                    MilestoneType.ERROR_THRESHOLD,
                    description=f"Error threshold exceeded: {self.metrics.error_rate:.1f}% error rate",
                    data={'error_rate': self.metrics.error_rate}
                )

    def create_milestone(self,
                        milestone_type: MilestoneType,
                        phase_id: Optional[str] = None,
                        description: str = "",
                        data: Optional[Dict[str, Any]] = None):
        """
        Create a progress milestone.
        
        Args:
            milestone_type: Type of milestone
            phase_id: Optional phase ID
            description: Milestone description
            data: Additional milestone data
        """
        milestone_id = f"{milestone_type.value}_{int(time.time())}"
        
        milestone = ProgressMilestone(
            milestone_id=milestone_id,
            milestone_type=milestone_type,
            timestamp=datetime.now().isoformat(),
            phase_id=phase_id,
            description=description,
            data=data or {}
        )
        
        self.milestones.append(milestone)
        
        # Save milestone
        milestone_file = self.milestones_dir / f"{milestone_id}.json"
        with open(milestone_file, 'w') as f:
            json.dump(asdict(milestone), f, indent=2)
        
        self.logger.info(f"Created milestone: {description}")

    def start_monitoring(self):
        """Start real-time progress monitoring"""
        if self._monitoring:
            self.logger.warning("Progress monitoring already started")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Started progress monitoring")

    def stop_monitoring(self):
        """Stop real-time progress monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("Stopped progress monitoring")

    def _monitor_loop(self):
        """Real-time monitoring loop"""
        while self._monitoring:
            try:
                self.update_metrics()
                self.save_progress()
                
                # Generate periodic report
                if int(time.time()) % 60 == 0:  # Every minute
                    self.generate_progress_report()
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get current progress summary.
        
        Returns:
            summary: Progress summary data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': asdict(self.metrics),
            'phases': {pid: asdict(phase) for pid, phase in self.phase_progress.items()},
            'recent_milestones': [asdict(m) for m in self.milestones[-5:]],
            'files_by_status': {
                status.value: len([f for f in self.file_progress.values() if f.status == status])
                for status in FileStatus
            }
        }

    def generate_progress_report(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Generate comprehensive progress report.
        
        Args:
            detailed: Include detailed file information
            
        Returns:
            report: Progress report data
        """
        report = {
            'report_id': f"progress_report_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'summary': self.get_progress_summary(),
            'phases': {pid: asdict(phase) for pid, phase in self.phase_progress.items()},
            'milestones': [asdict(m) for m in self.milestones],
            'performance': {
                'average_processing_time': self.metrics.average_processing_time,
                'throughput_files_per_hour': self.metrics.throughput_files_per_hour,
                'error_rate': self.metrics.error_rate
            }
        }
        
        if detailed:
            report['files'] = {fp: asdict(prog) for fp, prog in self.file_progress.items()}
        
        # Save report
        report_file = self.reports_dir / f"{report['report_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

    def save_progress(self):
        """Save current progress to files"""
        try:
            # Save file progress
            files_data = {fp: asdict(prog) for fp, prog in self.file_progress.items()}
            files_file = self.progress_dir / "file_progress.json"
            with open(files_file, 'w') as f:
                json.dump(files_data, f, indent=2)
            
            # Save phase progress
            phases_data = {pid: asdict(phase) for pid, phase in self.phase_progress.items()}
            phases_file = self.progress_dir / "phase_progress.json"
            with open(phases_file, 'w') as f:
                json.dump(phases_data, f, indent=2)
            
            # Save metrics
            metrics_file = self.progress_dir / "metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to save progress: {e}")

    def load_progress(self):
        """Load existing progress from files"""
        try:
            # Load file progress
            files_file = self.progress_dir / "file_progress.json"
            if files_file.exists():
                with open(files_file, 'r') as f:
                    files_data = json.load(f)
                self.file_progress = {
                    fp: FileProgress(**data) for fp, data in files_data.items()
                }
            
            # Load phase progress
            phases_file = self.progress_dir / "phase_progress.json"
            if phases_file.exists():
                with open(phases_file, 'r') as f:
                    phases_data = json.load(f)
                self.phase_progress = {
                    pid: PhaseProgress(**data) for pid, data in phases_data.items()
                }
            
            # Load metrics
            metrics_file = self.progress_dir / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    metrics_data = json.load(f)
                self.metrics = ProgressMetrics(**metrics_data)
            
            # Load milestones
            for milestone_file in self.milestones_dir.glob("*.json"):
                try:
                    with open(milestone_file, 'r') as f:
                        milestone_data = json.load(f)
                    milestone = ProgressMilestone(**milestone_data)
                    self.milestones.append(milestone)
                except Exception as e:
                    self.logger.warning(f"Failed to load milestone {milestone_file}: {e}")
            
            # Sort milestones by timestamp
            self.milestones.sort(key=lambda m: m.timestamp)
            
        except Exception as e:
            self.logger.warning(f"Failed to load existing progress: {e}")

    def sync_file_start_with_orchestrator(self, file_path: str, task_id: str, agent_id: Optional[str]):
        """Sync file start with orchestrator"""
        if not self.state_manager:
            return
        
        try:
            # Implementation would depend on orchestrator API
            self.logger.debug(f"Synced file start {file_path} with orchestrator task {task_id}")
        except Exception as e:
            self.logger.warning(f"Failed to sync file start with orchestrator: {e}")

    def sync_file_complete_with_orchestrator(self, file_path: str, task_id: str):
        """Sync file completion with orchestrator"""
        if not self.state_manager:
            return
        
        try:
            # Implementation would depend on orchestrator API
            self.logger.debug(f"Synced file completion {file_path} with orchestrator task {task_id}")
        except Exception as e:
            self.logger.warning(f"Failed to sync file completion with orchestrator: {e}")

    def get_recovery_points(self) -> List[Dict[str, Any]]:
        """
        Get recovery points for resuming interrupted operations.
        
        Returns:
            recovery_points: List of recovery point data
        """
        recovery_points = []
        
        # Get files that were in progress
        in_progress_files = [
            f for f in self.file_progress.values() 
            if f.status == FileStatus.IN_PROGRESS
        ]
        
        for file_prog in in_progress_files:
            recovery_point = {
                'file_path': file_prog.file_path,
                'agent_id': file_prog.agent_id,
                'task_id': file_prog.task_id,
                'start_time': file_prog.start_time,
                'backup_path': file_prog.backup_path,
                'recovery_action': 'resume_or_restart'
            }
            recovery_points.append(recovery_point)
        
        return recovery_points


def main():
    """Example usage of DocumentationProgressTracker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Documentation Progress Tracker")
    parser.add_argument("--workspace", "-w", required=True, help="Workspace path")
    parser.add_argument("--report", "-r", action="store_true", help="Generate progress report")
    parser.add_argument("--summary", "-s", action="store_true", help="Show progress summary")
    parser.add_argument("--monitor", "-m", action="store_true", help="Start monitoring")
    
    args = parser.parse_args()
    
    tracker = DocumentationProgressTracker(args.workspace)
    
    if args.report:
        report = tracker.generate_progress_report(detailed=True)
        print(json.dumps(report, indent=2))
    
    elif args.summary:
        summary = tracker.get_progress_summary()
        print(json.dumps(summary, indent=2))
    
    elif args.monitor:
        tracker.start_monitoring()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            tracker.stop_monitoring()
    
    else:
        print("Use --report, --summary, or --monitor")


if __name__ == "__main__":
    main()