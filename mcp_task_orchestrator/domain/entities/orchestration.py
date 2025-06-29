"""
Orchestration entity - Represents an orchestration session and work items.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
from enum import Enum


class SessionStatus(str, Enum):
    """Orchestration session states."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkItemPriority(str, Enum):
    """Work item priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OrchestrationSession:
    """
    Represents an orchestration session managing multiple tasks.
    
    A session tracks the overall progress of a complex task breakdown.
    """
    session_id: str
    name: str
    description: str
    status: SessionStatus
    root_task_id: str
    project_directory: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    active_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        root_task_id: str,
        project_directory: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'OrchestrationSession':
        """Factory method to create a new orchestration session."""
        now = datetime.utcnow()
        return cls(
            session_id=str(uuid4()),
            name=name,
            description=description,
            status=SessionStatus.ACTIVE,
            root_task_id=root_task_id,
            project_directory=project_directory,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
    
    def add_active_task(self, task_id: str) -> None:
        """Add a task to active execution."""
        if task_id not in self.active_tasks:
            self.active_tasks.append(task_id)
            self.updated_at = datetime.utcnow()
    
    def complete_task(self, task_id: str) -> None:
        """Mark a task as completed."""
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
        if task_id not in self.completed_tasks:
            self.completed_tasks.append(task_id)
        self.updated_at = datetime.utcnow()
    
    def fail_task(self, task_id: str) -> None:
        """Mark a task as failed."""
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
        if task_id not in self.failed_tasks:
            self.failed_tasks.append(task_id)
        self.updated_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pause the orchestration session."""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError(f"Cannot pause session in {self.status} status")
        
        self.status = SessionStatus.PAUSED
        self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Resume a paused session."""
        if self.status != SessionStatus.PAUSED:
            raise ValueError(f"Cannot resume session in {self.status} status")
        
        self.status = SessionStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark session as completed."""
        if self.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise ValueError(f"Cannot complete session in {self.status} status")
        
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = self.completed_at
    
    def fail(self, reason: str) -> None:
        """Mark session as failed."""
        if self.status == SessionStatus.COMPLETED:
            raise ValueError("Cannot fail completed session")
        
        self.status = SessionStatus.FAILED
        self.metadata['failure_reason'] = reason
        self.updated_at = datetime.utcnow()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get session progress metrics."""
        total_tasks = len(self.active_tasks) + len(self.completed_tasks) + len(self.failed_tasks)
        
        return {
            'total_tasks': total_tasks,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'completion_percentage': (len(self.completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0,
            'success_rate': (len(self.completed_tasks) / (len(self.completed_tasks) + len(self.failed_tasks)) * 100) 
                           if (len(self.completed_tasks) + len(self.failed_tasks)) > 0 else 0
        }


@dataclass
class WorkItem:
    """
    Represents a unit of work within an orchestration session.
    
    Work items are queued tasks ready for execution.
    """
    item_id: str
    session_id: str
    task_id: str
    priority: WorkItemPriority
    specialist_type: str
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        session_id: str,
        task_id: str,
        specialist_type: str,
        priority: WorkItemPriority = WorkItemPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'WorkItem':
        """Factory method to create a new work item."""
        return cls(
            item_id=str(uuid4()),
            session_id=session_id,
            task_id=task_id,
            priority=priority,
            specialist_type=specialist_type,
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
    
    def schedule(self, scheduled_time: datetime) -> None:
        """Schedule the work item for execution."""
        self.scheduled_at = scheduled_time
    
    def start(self) -> None:
        """Mark work item as started."""
        self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark work item as completed."""
        self.completed_at = datetime.utcnow()
    
    def can_retry(self) -> bool:
        """Check if work item can be retried."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if work item has expired based on timeout."""
        if not self.started_at:
            return False
        
        elapsed = (datetime.utcnow() - self.started_at).total_seconds() / 60
        return elapsed > timeout_minutes