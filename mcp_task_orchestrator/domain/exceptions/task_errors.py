"""
Task-specific exceptions for task lifecycle and execution errors.
"""

from typing import Optional, List, Dict, Any
from .orchestration_errors import OrchestrationError


class TaskError(OrchestrationError):
    """Base exception for all task-related errors."""
    pass


class TaskExecutionError(TaskError):
    """Raised when task execution fails."""
    
    def __init__(self, task_id: str, execution_error: str, 
                 exit_code: Optional[int] = None, stdout: Optional[str] = None, 
                 stderr: Optional[str] = None):
        super().__init__(
            f"Task execution failed for {task_id}: {execution_error}",
            {
                "task_id": task_id,
                "execution_error": execution_error,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            }
        )
        self.task_id = task_id
        self.execution_error = execution_error
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class TaskTimeoutError(TaskError):
    """Raised when a task times out."""
    
    def __init__(self, task_id: str, timeout_seconds: float, elapsed_seconds: float):
        super().__init__(
            f"Task {task_id} timed out after {elapsed_seconds:.2f}s (limit: {timeout_seconds}s)",
            {
                "task_id": task_id,
                "timeout_seconds": timeout_seconds,
                "elapsed_seconds": elapsed_seconds
            }
        )
        self.task_id = task_id
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds


class TaskCancellationError(TaskError):
    """Raised when task cancellation fails."""
    
    def __init__(self, task_id: str, cancellation_reason: str):
        super().__init__(
            f"Failed to cancel task {task_id}: {cancellation_reason}",
            {
                "task_id": task_id,
                "cancellation_reason": cancellation_reason
            }
        )
        self.task_id = task_id
        self.cancellation_reason = cancellation_reason


class TaskResourceError(TaskError):
    """Raised when task resources are insufficient or unavailable."""
    
    def __init__(self, task_id: str, resource_type: str, required: str, available: str):
        super().__init__(
            f"Insufficient {resource_type} for task {task_id}: required {required}, available {available}",
            {
                "task_id": task_id,
                "resource_type": resource_type,
                "required": required,
                "available": available
            }
        )
        self.task_id = task_id
        self.resource_type = resource_type
        self.required = required
        self.available = available


class TaskDeadlockError(TaskError):
    """Raised when tasks create a deadlock situation."""
    
    def __init__(self, task_ids: List[str], deadlock_chain: List[str]):
        super().__init__(
            f"Deadlock detected among tasks: {', '.join(task_ids)}",
            {
                "task_ids": task_ids,
                "deadlock_chain": deadlock_chain
            }
        )
        self.task_ids = task_ids
        self.deadlock_chain = deadlock_chain


class TaskCorruptionError(TaskError):
    """Raised when task data is corrupted or inconsistent."""
    
    def __init__(self, task_id: str, corruption_details: str):
        super().__init__(
            f"Task data corruption detected for {task_id}: {corruption_details}",
            {
                "task_id": task_id,
                "corruption_details": corruption_details
            }
        )
        self.task_id = task_id
        self.corruption_details = corruption_details


class TaskPriorityError(TaskError):
    """Raised when task priority configuration is invalid."""
    
    def __init__(self, task_id: str, priority_issue: str):
        super().__init__(
            f"Priority configuration error for task {task_id}: {priority_issue}",
            {
                "task_id": task_id,
                "priority_issue": priority_issue
            }
        )
        self.task_id = task_id
        self.priority_issue = priority_issue


class TaskBreakdownError(TaskError):
    """Raised when task breakdown or decomposition fails."""
    
    def __init__(self, task_id: str, breakdown_error: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Task breakdown failed for {task_id}: {breakdown_error}",
            {
                "task_id": task_id,
                "breakdown_error": breakdown_error,
                "context": context or {}
            }
        )
        self.task_id = task_id
        self.breakdown_error = breakdown_error
        self.context = context or {}


class TaskSynthesisError(TaskError):
    """Raised when task result synthesis fails."""
    
    def __init__(self, parent_task_id: str, subtask_ids: List[str], synthesis_error: str):
        super().__init__(
            f"Result synthesis failed for parent task {parent_task_id}: {synthesis_error}",
            {
                "parent_task_id": parent_task_id,
                "subtask_ids": subtask_ids,
                "synthesis_error": synthesis_error
            }
        )
        self.parent_task_id = parent_task_id
        self.subtask_ids = subtask_ids
        self.synthesis_error = synthesis_error