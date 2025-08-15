"""
Standardized error handling patterns for compatibility layer.

Provides consistent error processing, logging, and response formatting
across all use case operations.
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional

from .....domain.exceptions import OrchestrationError

logger = logging.getLogger(__name__)


class TaskNotFoundError(OrchestrationError):
    """Task does not exist in the system."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")


class TaskStateError(OrchestrationError):
    """Task is not in the required state for the operation."""
    def __init__(self, task_id: str, current_state: str, required_states: List[str]):
        self.task_id = task_id
        self.current_state = current_state
        self.required_states = required_states
        super().__init__(
            f"Task {task_id} is in state '{current_state}', "
            f"but requires one of: {required_states}"
        )


class DependencyError(OrchestrationError):
    """Task has dependencies that prevent the operation."""
    def __init__(self, task_id: str, dependent_tasks: List[str]):
        self.task_id = task_id
        self.dependent_tasks = dependent_tasks
        super().__init__(
            f"Task {task_id} has {len(dependent_tasks)} dependent tasks: "
            f"{', '.join(dependent_tasks[:3])}{'...' if len(dependent_tasks) > 3 else ''}"
        )


class ValidationError(OrchestrationError):
    """Input validation failed."""
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for {field}: {reason}")


class SerializationError(OrchestrationError):
    """JSON serialization failed."""
    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Serialization failed for {operation}: {str(original_error)}")


class DatabaseError(OrchestrationError):
    """Database operation failed."""
    def __init__(self, operation: str, details: str = ""):
        self.operation = operation
        self.details = details
        super().__init__(f"Database operation '{operation}' failed: {details}")


class ErrorHandlingMixin:
    """Mixin providing standard error handling for use cases."""
    
    def handle_error(self, error: Exception, operation: str, context: Dict[str, Any] = None) -> None:
        """Standard error handling and logging."""
        context = context or {}
        
        # Create detailed error context
        error_context = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            **context
        }
        
        # Log error with context
        if isinstance(error, OrchestrationError):
            logger.warning(f"Domain error in {operation}: {error}", extra=error_context)
        else:
            logger.error(
                f"Unexpected error in {operation}: {error}",
                extra=error_context,
                exc_info=True
            )
        
        # Re-raise with context preservation
        if not isinstance(error, OrchestrationError):
            raise OrchestrationError(f"{operation} failed: {str(error)}") from error
        else:
            raise error
    
    def validate_task_exists(self, task_id: str, task_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate task exists and return validated data."""
        if not task_data:
            raise TaskNotFoundError(task_id)
        
        # Ensure required fields exist
        required_fields = ["id", "title", "status"]
        for field in required_fields:
            if field not in task_data:
                raise ValidationError(
                    field, 
                    None, 
                    f"Required field missing from task {task_id}"
                )
        
        return task_data
    
    def validate_task_state(self, task_id: str, current_status: str, required_statuses: List[str]) -> None:
        """Validate task is in required state."""
        if current_status not in required_statuses:
            raise TaskStateError(task_id, current_status, required_statuses)
    
    def validate_input(self, field_name: str, value: Any, validator_func) -> Any:
        """Validate input using provided validator function."""
        try:
            return validator_func(value)
        except Exception as e:
            raise ValidationError(field_name, value, str(e))


class ErrorResponseFormatter:
    """Formats error responses consistently across all use cases."""
    
    @staticmethod
    def format_error_response(error: Exception, operation: str) -> Dict[str, Any]:
        """Format any exception into standardized error response."""
        error_type = type(error).__name__
        timestamp = datetime.utcnow().isoformat()
        
        # Base error response structure
        response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": str(error),
                "operation": operation,
                "timestamp": timestamp
            }
        }
        
        # Add specific error details based on error type
        if isinstance(error, TaskNotFoundError):
            response["error"]["task_id"] = error.task_id
            response["error"]["code"] = "TASK_NOT_FOUND"
            
        elif isinstance(error, TaskStateError):
            response["error"]["task_id"] = error.task_id
            response["error"]["current_state"] = error.current_state
            response["error"]["required_states"] = error.required_states
            response["error"]["code"] = "INVALID_TASK_STATE"
            
        elif isinstance(error, DependencyError):
            response["error"]["task_id"] = error.task_id
            response["error"]["dependent_tasks"] = error.dependent_tasks
            response["error"]["code"] = "DEPENDENCY_CONFLICT"
            
        elif isinstance(error, ValidationError):
            response["error"]["field"] = error.field
            response["error"]["value"] = str(error.value)
            response["error"]["reason"] = error.reason
            response["error"]["code"] = "VALIDATION_FAILED"
            
        elif isinstance(error, SerializationError):
            response["error"]["operation"] = error.operation
            response["error"]["original_error"] = str(error.original_error)
            response["error"]["code"] = "SERIALIZATION_FAILED"
            
        elif isinstance(error, DatabaseError):
            response["error"]["operation"] = error.operation
            response["error"]["details"] = error.details
            response["error"]["code"] = "DATABASE_ERROR"
            
        else:
            # Generic error handling
            response["error"]["code"] = "UNKNOWN_ERROR"
            response["error"]["traceback"] = traceback.format_exc()
        
        return response