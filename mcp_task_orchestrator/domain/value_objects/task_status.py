"""
Task-related value objects.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TaskStatus(str, Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal status."""
        return self in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)
    
    def is_active(self) -> bool:
        """Check if this is an active status."""
        return self == TaskStatus.IN_PROGRESS
    
    def can_transition_to(self, new_status: 'TaskStatus') -> bool:
        """Check if transition to new status is valid."""
        transitions = {
            TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.BLOCKED},
            TaskStatus.IN_PROGRESS: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
            TaskStatus.BLOCKED: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
            TaskStatus.COMPLETED: set(),
            TaskStatus.FAILED: set(),
            TaskStatus.CANCELLED: set()
        }
        return new_status in transitions.get(self, set())


class TaskComplexity(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HIGHLY_COMPLEX = "highly_complex"
    
    @property
    def weight(self) -> int:
        """Get numeric weight for complexity."""
        weights = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 3,
            TaskComplexity.COMPLEX: 5,
            TaskComplexity.HIGHLY_COMPLEX: 8
        }
        return weights[self]
    
    @property
    def expected_duration_minutes(self) -> int:
        """Get expected duration in minutes."""
        durations = {
            TaskComplexity.SIMPLE: 15,
            TaskComplexity.MODERATE: 60,
            TaskComplexity.COMPLEX: 180,
            TaskComplexity.HIGHLY_COMPLEX: 480
        }
        return durations[self]


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    
    @property
    def weight(self) -> int:
        """Get numeric weight for priority."""
        weights = {
            TaskPriority.CRITICAL: 1000,
            TaskPriority.HIGH: 100,
            TaskPriority.MEDIUM: 10,
            TaskPriority.LOW: 1
        }
        return weights[self]
    
    def __lt__(self, other: 'TaskPriority') -> bool:
        """Compare priorities (higher weight = higher priority)."""
        if not isinstance(other, TaskPriority):
            return NotImplemented
        return self.weight < other.weight


@dataclass(frozen=True)
class TaskIdentifier:
    """Value object representing a task identifier."""
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Task identifier must be a non-empty string")
        if len(self.value) < 8:
            raise ValueError("Task identifier must be at least 8 characters")
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def short_id(self) -> str:
        """Get shortened version of ID for display."""
        return self.value[:8]