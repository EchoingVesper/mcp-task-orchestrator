"""
Task-related Data Transfer Objects.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TaskPlanRequest:
    """Request to plan a complex task."""
    description: str
    complexity_level: str = "moderate"
    subtasks_json: Optional[str] = None
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskPlanResponse:
    """Response from task planning."""
    success: bool
    parent_task_id: str
    description: str
    complexity: str
    subtasks: List[Dict[str, Any]]
    execution_order: List[List[str]]
    estimated_duration: int  # minutes
    error: Optional[str] = None


@dataclass
class TaskExecutionRequest:
    """Request to execute a task."""
    task_id: str
    force: bool = False
    timeout: Optional[int] = None  # seconds
    context_override: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecutionResponse:
    """Response from task execution."""
    success: bool
    task_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[str] = None
    error: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContextRequest:
    """Request to get execution context for a task."""
    task_id: str
    include_dependencies: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContextResponse:
    """Response with task execution context."""
    success: bool
    task_id: str
    task_title: str
    task_description: str
    specialist_type: str
    specialist_context: Dict[str, Any]
    specialist_prompts: List[str]
    execution_instructions: List[str]
    dependencies_completed: bool
    estimated_effort: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class TaskCompletionRequest:
    """Request to complete a task."""
    task_id: str
    summary: str
    detailed_work: str
    artifact_type: str = "general"
    file_paths: List[str] = field(default_factory=list)
    next_action: str = "complete"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskCompletionResponse:
    """Response from task completion."""
    success: bool
    task_id: str
    message: str
    summary: str
    artifact_count: int
    artifact_references: List[Dict[str, Any]]
    next_action: str
    next_steps: List[str]
    completion_time: str
    error: Optional[str] = None