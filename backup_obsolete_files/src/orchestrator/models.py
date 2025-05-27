"""
Data models for the Task Orchestrator.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class SpecialistType(str, Enum):
    """Available specialist types."""
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    DEBUGGER = "debugger"
    DOCUMENTER = "documenter"
    REVIEWER = "reviewer"
    RESEARCHER = "researcher"


class ComplexityLevel(str, Enum):
    """Task complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class SubTask(BaseModel):
    """Represents a single subtask within a larger orchestrated task."""
    task_id: str = Field(..., description="Unique identifier for this subtask")
    title: str = Field(..., description="Human-readable title for the subtask")
    description: str = Field(..., description="Detailed description of what needs to be done")
    specialist_type: SpecialistType = Field(..., description="Type of specialist needed")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this depends on")
    estimated_effort: str = Field(..., description="Estimated time/effort required")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    results: Optional[str] = Field(None, description="Results when completed")
    artifacts: List[str] = Field(default_factory=list, description="Created artifacts/files")
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class TaskBreakdown(BaseModel):
    """Represents the breakdown of a complex task into subtasks."""
    parent_task_id: str = Field(..., description="ID of the parent task")
    description: str = Field(..., description="Original task description")
    complexity: ComplexityLevel = Field(..., description="Assessed complexity level")
    subtasks: List[SubTask] = Field(..., description="List of subtasks")
    created_at: datetime = Field(default_factory=datetime.now)
    context: Optional[str] = Field(None, description="Additional context provided")


class TaskResult(BaseModel):
    """Represents the result of completing a task or subtask."""
    task_id: str
    results: str
    artifacts: List[str]
    next_action: str
    timestamp: datetime = Field(default_factory=datetime.now)
