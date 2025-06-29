"""
Task entity - Core business object representing a task in the orchestration system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
from enum import Enum


# Import these from value objects to avoid duplication
from ..value_objects.task_status import TaskStatus, TaskComplexity


@dataclass
class Task:
    """
    Core task entity representing a unit of work.
    
    This is a domain entity with business logic and identity.
    """
    task_id: str
    title: str
    description: str
    status: TaskStatus
    complexity: TaskComplexity
    specialist_type: str
    created_at: datetime
    updated_at: datetime
    parent_task_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    artifact_ids: List[str] = field(default_factory=list)
    
    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        specialist_type: str,
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        parent_task_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Task':
        """Factory method to create a new task."""
        now = datetime.utcnow()
        return cls(
            task_id=str(uuid4()),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            complexity=complexity,
            specialist_type=specialist_type,
            created_at=now,
            updated_at=now,
            parent_task_id=parent_task_id,
            dependencies=dependencies or [],
            metadata=metadata or {},
            context=context
        )
    
    def start(self) -> None:
        """Start the task execution."""
        if self.status != TaskStatus.PENDING:
            raise ValueError(f"Cannot start task in {self.status} status")
        
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
    
    def complete(self, result: str, artifact_ids: Optional[List[str]] = None) -> None:
        """Mark task as completed with result."""
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete task in {self.status} status")
        
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.artifact_ids = artifact_ids or []
        self.updated_at = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """Mark task as failed with error."""
        if self.status not in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            raise ValueError(f"Cannot fail task in {self.status} status")
        
        self.status = TaskStatus.FAILED
        self.error = error
        self.updated_at = datetime.utcnow()
    
    def block(self, reason: str) -> None:
        """Mark task as blocked."""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Cannot block completed task")
        
        self.status = TaskStatus.BLOCKED
        self.metadata['block_reason'] = reason
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the task."""
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Cannot cancel completed task")
        
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def is_ready(self, completed_task_ids: List[str]) -> bool:
        """Check if task is ready to execute based on dependencies."""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)
    
    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to this task."""
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.utcnow()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update task metadata."""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()


@dataclass
class Subtask:
    """Lightweight subtask representation within a breakdown."""
    task_id: str
    title: str
    description: str
    specialist_type: str
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None
    
    def to_task(self, parent_task_id: str, complexity: TaskComplexity) -> Task:
        """Convert subtask to full Task entity."""
        return Task.create(
            title=self.title,
            description=self.description,
            specialist_type=self.specialist_type,
            complexity=complexity,
            parent_task_id=parent_task_id,
            dependencies=self.dependencies,
            metadata={'estimated_effort': self.estimated_effort} if self.estimated_effort else {}
        )


@dataclass
class TaskBreakdown:
    """Represents a task breakdown plan."""
    parent_task_id: str
    description: str
    complexity: TaskComplexity
    subtasks: List[Subtask]
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def validate(self) -> List[str]:
        """Validate the task breakdown structure."""
        errors = []
        
        if not self.subtasks:
            errors.append("Task breakdown must have at least one subtask")
        
        # Check for circular dependencies
        task_ids = {st.task_id for st in self.subtasks}
        for subtask in self.subtasks:
            for dep in subtask.dependencies:
                if dep not in task_ids:
                    errors.append(f"Subtask {subtask.task_id} has unknown dependency: {dep}")
        
        return errors
    
    def get_execution_order(self) -> List[List[Subtask]]:
        """
        Get subtasks organized by execution order (levels).
        Returns a list of levels, where each level contains tasks that can run in parallel.
        """
        levels = []
        remaining = self.subtasks.copy()
        completed = set()
        
        while remaining:
            current_level = []
            
            for subtask in remaining[:]:
                if all(dep in completed for dep in subtask.dependencies):
                    current_level.append(subtask)
                    remaining.remove(subtask)
            
            if not current_level:
                # Circular dependency or invalid structure
                break
            
            levels.append(current_level)
            completed.update(st.task_id for st in current_level)
        
        return levels