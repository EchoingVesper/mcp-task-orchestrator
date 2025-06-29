"""
Domain-specific exceptions for orchestration errors.
"""

from typing import Optional, List, Dict, Any


class OrchestrationError(Exception):
    """Base exception for all orchestration domain errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class TaskNotFoundError(OrchestrationError):
    """Raised when a task cannot be found."""
    
    def __init__(self, task_id: str):
        super().__init__(
            f"Task not found: {task_id}",
            {"task_id": task_id}
        )
        self.task_id = task_id


class TaskStateError(OrchestrationError):
    """Raised when a task operation is invalid for its current state."""
    
    def __init__(self, task_id: str, current_state: str, operation: str):
        super().__init__(
            f"Task {task_id} in state '{current_state}' cannot perform operation '{operation}'",
            {
                "task_id": task_id,
                "current_state": current_state,
                "operation": operation
            }
        )
        self.task_id = task_id
        self.current_state = current_state
        self.operation = operation


class TaskDependencyError(OrchestrationError):
    """Raised when task dependencies are invalid or create cycles."""
    
    def __init__(self, message: str, task_id: str, dependencies: List[str]):
        super().__init__(
            message,
            {
                "task_id": task_id,
                "dependencies": dependencies
            }
        )
        self.task_id = task_id
        self.dependencies = dependencies


class TaskValidationError(OrchestrationError):
    """Raised when task data fails validation."""
    
    def __init__(self, message: str, validation_errors: List[str]):
        super().__init__(
            message,
            {"validation_errors": validation_errors}
        )
        self.validation_errors = validation_errors


class SessionNotFoundError(OrchestrationError):
    """Raised when an orchestration session cannot be found."""
    
    def __init__(self, session_id: str):
        super().__init__(
            f"Orchestration session not found: {session_id}",
            {"session_id": session_id}
        )
        self.session_id = session_id


class SessionStateError(OrchestrationError):
    """Raised when a session operation is invalid for its current state."""
    
    def __init__(self, session_id: str, current_state: str, operation: str):
        super().__init__(
            f"Session {session_id} in state '{current_state}' cannot perform operation '{operation}'",
            {
                "session_id": session_id,
                "current_state": current_state,
                "operation": operation
            }
        )
        self.session_id = session_id
        self.current_state = current_state
        self.operation = operation


class SpecialistNotFoundError(OrchestrationError):
    """Raised when a specialist cannot be found."""
    
    def __init__(self, specialist_type: str):
        super().__init__(
            f"Specialist not found: {specialist_type}",
            {"specialist_type": specialist_type}
        )
        self.specialist_type = specialist_type


class SpecialistAssignmentError(OrchestrationError):
    """Raised when a specialist cannot be assigned to a task."""
    
    def __init__(self, task_id: str, specialist_type: str, reason: str):
        super().__init__(
            f"Cannot assign specialist '{specialist_type}' to task {task_id}: {reason}",
            {
                "task_id": task_id,
                "specialist_type": specialist_type,
                "reason": reason
            }
        )
        self.task_id = task_id
        self.specialist_type = specialist_type
        self.reason = reason


class ArtifactError(OrchestrationError):
    """Base exception for artifact-related errors."""
    pass


class ArtifactNotFoundError(ArtifactError):
    """Raised when an artifact cannot be found."""
    
    def __init__(self, artifact_id: str):
        super().__init__(
            f"Artifact not found: {artifact_id}",
            {"artifact_id": artifact_id}
        )
        self.artifact_id = artifact_id


class WorkflowError(OrchestrationError):
    """Raised when workflow rules are violated."""
    
    def __init__(self, message: str, workflow_step: str):
        super().__init__(
            message,
            {"workflow_step": workflow_step}
        )
        self.workflow_step = workflow_step


class ConcurrencyError(OrchestrationError):
    """Raised when concurrent operations conflict."""
    
    def __init__(self, resource: str, operation: str):
        super().__init__(
            f"Concurrent operation conflict on resource '{resource}' for operation '{operation}'",
            {
                "resource": resource,
                "operation": operation
            }
        )
        self.resource = resource
        self.operation = operation


class ResourceExhaustedError(OrchestrationError):
    """Raised when system resources are exhausted."""
    
    def __init__(self, resource_type: str, limit: int, requested: int):
        super().__init__(
            f"Resource exhausted: {resource_type} (limit: {limit}, requested: {requested})",
            {
                "resource_type": resource_type,
                "limit": limit,
                "requested": requested
            }
        )
        self.resource_type = resource_type
        self.limit = limit
        self.requested = requested