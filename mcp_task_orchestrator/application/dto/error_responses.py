"""
Error response utilities for centralized error handling.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass


class TaskErrorResponse(BaseModel):
    """Standard error response for task operations."""
    task_id: str
    status: str = "error"
    error: str
    results_recorded: bool = False
    parent_task_progress: Dict[str, str] = Field(default_factory=dict)
    next_recommended_task: Optional[str] = None


class SubtaskErrorResponse(BaseModel):
    """Error response for subtask operations."""
    task_id: str
    status: str = "error"
    error: str
    artifacts_recorded: bool = False
    completion_status: Dict[str, Union[str, bool]] = Field(default_factory=dict)
    parent_task_info: Optional[Dict[str, Any]] = None


class StatusErrorResponse(BaseModel):
    """Error response for status operations."""
    error: str
    status: str = "error"
    active_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    completed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    session_info: Optional[Dict[str, Any]] = None


class SynthesisErrorResponse(BaseModel):
    """Error response for synthesis operations."""
    parent_task_id: str
    status: str = "error"
    error: str
    results_synthesized: bool = False
    subtask_count: int = 0
    completion_summary: Optional[str] = None


class ErrorResponseBuilder:
    """Builder class for creating standardized error responses."""
    
    @staticmethod
    def task_error(task_id: str, error: Exception, **kwargs) -> TaskErrorResponse:
        """Create a standardized task error response."""
        return TaskErrorResponse(
            task_id=task_id,
            error=str(error),
            parent_task_progress={"progress": "unknown", "error": str(error)},
            **kwargs
        )
    
    @staticmethod
    def subtask_error(task_id: str, error: Exception, **kwargs) -> SubtaskErrorResponse:
        """Create a standardized subtask error response."""
        return SubtaskErrorResponse(
            task_id=task_id,
            error=str(error),
            completion_status={"completed": False, "error": str(error)},
            **kwargs
        )
    
    @staticmethod
    def status_error(error: Exception, **kwargs) -> StatusErrorResponse:
        """Create a standardized status error response."""
        return StatusErrorResponse(
            error=str(error),
            session_info={"error": str(error), "status": "error"},
            **kwargs
        )
    
    @staticmethod
    def synthesis_error(parent_task_id: str, error: Exception, subtask_count: int = 0, **kwargs) -> SynthesisErrorResponse:
        """Create a standardized synthesis error response."""
        return SynthesisErrorResponse(
            parent_task_id=parent_task_id,
            error=str(error),
            subtask_count=subtask_count,
            completion_summary=f"Synthesis failed: {str(error)}",
            **kwargs
        )
    
    @staticmethod
    def generic_error(error: Exception, additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a generic error response dictionary."""
        response = {
            "status": "error",
            "error": str(error),
            "error_type": type(error).__name__
        }
        
        if additional_fields:
            response.update(additional_fields)
        
        return response


@dataclass
class ErrorContext:
    """Context information for error responses."""
    component: str
    operation: str
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class ErrorResponseFormatter:
    """Formats error responses with consistent structure and context."""
    
    @staticmethod
    def format_with_context(error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Format error response with context information."""
        base_response = ErrorResponseBuilder.generic_error(error)
        
        # Add context information
        base_response.update({
            "component": context.component,
            "operation": context.operation,
            "timestamp": "auto-generated",  # Will be replaced with actual timestamp
        })
        
        if context.task_id:
            base_response["task_id"] = context.task_id
        
        if context.session_id:
            base_response["session_id"] = context.session_id
        
        if context.additional_info:
            base_response.update(context.additional_info)
        
        return base_response
    
    @staticmethod
    def format_timeout_error(operation: str, task_id: Optional[str] = None, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Format timeout-specific error response."""
        return {
            "status": "error",
            "error": f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            "error_type": "TimeoutError",
            "task_id": task_id,
            "operation": operation,
            "timeout_seconds": timeout_seconds,
            "recommended_action": "retry_with_longer_timeout"
        }
    
    @staticmethod
    def format_retry_exhausted_error(operation: str, max_attempts: int, last_error: Exception) -> Dict[str, Any]:
        """Format retry exhausted error response."""
        return {
            "status": "error",
            "error": f"Operation '{operation}' failed after {max_attempts} attempts",
            "error_type": "RetryExhaustedError",
            "operation": operation,
            "max_attempts": max_attempts,
            "last_error": str(last_error),
            "last_error_type": type(last_error).__name__,
            "recommended_action": "investigate_root_cause"
        }