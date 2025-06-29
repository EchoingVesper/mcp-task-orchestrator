"""
Execution result value objects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ExecutionStatus(str, Enum):
    """Status of an execution attempt."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    
    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self in (ExecutionStatus.SUCCESS, ExecutionStatus.PARTIAL)
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return True  # All execution statuses are terminal


@dataclass(frozen=True)
class ExecutionResult:
    """Value object representing the result of a task execution."""
    status: ExecutionStatus
    summary: str
    started_at: datetime
    completed_at: datetime
    output: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[str] = None
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.artifacts is None:
            object.__setattr__(self, 'artifacts', [])
        if self.metrics is None:
            object.__setattr__(self, 'metrics', {})
        
        if self.completed_at < self.started_at:
            raise ValueError("Completion time cannot be before start time")
        
        if self.status == ExecutionStatus.SUCCESS and self.error:
            raise ValueError("Successful execution should not have an error")
        
        if self.status == ExecutionStatus.FAILURE and not self.error:
            raise ValueError("Failed execution must have an error message")
    
    @property
    def duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()
    
    @property
    def duration_formatted(self) -> str:
        """Get formatted duration string."""
        seconds = self.duration_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def with_artifact(self, artifact_id: str) -> 'ExecutionResult':
        """Create new result with additional artifact."""
        new_artifacts = list(self.artifacts)
        new_artifacts.append(artifact_id)
        
        return ExecutionResult(
            status=self.status,
            summary=self.summary,
            started_at=self.started_at,
            completed_at=self.completed_at,
            output=self.output,
            error=self.error,
            artifacts=new_artifacts,
            metrics=self.metrics
        )
    
    def with_metric(self, key: str, value: Any) -> 'ExecutionResult':
        """Create new result with additional metric."""
        new_metrics = dict(self.metrics)
        new_metrics[key] = value
        
        return ExecutionResult(
            status=self.status,
            summary=self.summary,
            started_at=self.started_at,
            completed_at=self.completed_at,
            output=self.output,
            error=self.error,
            artifacts=self.artifacts,
            metrics=new_metrics
        )


@dataclass(frozen=True)
class ExecutionAttempt:
    """Value object representing a single execution attempt."""
    attempt_number: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: Optional[ExecutionStatus]
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.attempt_number < 1:
            raise ValueError("Attempt number must be positive")
        
        if self.completed_at and self.completed_at < self.started_at:
            raise ValueError("Completion time cannot be before start time")
        
        if self.status and not self.completed_at:
            raise ValueError("Completed attempt must have completion time")
    
    @property
    def is_complete(self) -> bool:
        """Check if attempt is complete."""
        return self.completed_at is not None and self.status is not None
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Get attempt duration in seconds."""
        if not self.completed_at:
            return None
        return (self.completed_at - self.started_at).total_seconds()