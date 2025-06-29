"""
Error handlers for centralized error processing and response.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, Any, Callable
from ...domain.exceptions import (
    BaseOrchestrationError, ErrorSeverity, RecoveryStrategy,
    TaskError, SpecialistError, InfrastructureError
)

logger = logging.getLogger(__name__)


class ErrorHandler(ABC):
    """Abstract base class for error handlers."""
    
    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """Check if this handler can process the given error."""
        pass
    
    @abstractmethod
    def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle the error and return response information.
        
        Returns:
            Dictionary containing:
            - handled: bool
            - should_retry: bool
            - retry_after: Optional[int]
            - user_message: str
            - details: Dict[str, Any]
        """
        pass


class DefaultErrorHandler(ErrorHandler):
    """Default error handler for unhandled exceptions."""
    
    def can_handle(self, error: Exception) -> bool:
        """Default handler accepts any exception."""
        return True
    
    def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle unknown errors with basic logging and user-friendly message."""
        error_msg = str(error)
        
        # Log the error
        logger.error(f"Unhandled error: {error_msg}", exc_info=True)
        
        # Check if it's a BaseOrchestrationError for better handling
        if isinstance(error, BaseOrchestrationError):
            return {
                "handled": True,
                "should_retry": error.is_retryable(),
                "retry_after": 30 if error.is_retryable() else None,
                "user_message": error.message,
                "details": error.to_dict(),
                "severity": error.severity.value
            }
        
        # Generic error response
        return {
            "handled": True,
            "should_retry": False,
            "retry_after": None,
            "user_message": "An unexpected error occurred. Please try again later.",
            "details": {
                "error_type": type(error).__name__,
                "error_message": error_msg,
                "context": context or {}
            },
            "severity": "medium"
        }


class TaskErrorHandler(ErrorHandler):
    """Specialized handler for task-related errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """Handle task-specific errors."""
        return isinstance(error, TaskError)
    
    def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle task errors with specific recovery strategies."""
        task_error = error  # type: TaskError
        
        logger.warning(f"Task error in {context.get('task_id', 'unknown')}: {task_error}")
        
        # Determine retry strategy based on error type
        should_retry = True
        retry_after = 10
        user_message = "Task execution encountered an issue."
        
        if hasattr(task_error, 'task_id'):
            user_message = f"Task {task_error.task_id} encountered an issue."
        
        # Specific handling for different task error types
        if "timeout" in str(task_error).lower():
            retry_after = 60
            user_message += " The operation timed out and will be retried."
        elif "resource" in str(task_error).lower():
            should_retry = False
            user_message += " Insufficient resources available."
        elif "deadlock" in str(task_error).lower():
            retry_after = 30
            user_message += " A deadlock was detected and will be resolved."
        
        return {
            "handled": True,
            "should_retry": should_retry,
            "retry_after": retry_after,
            "user_message": user_message,
            "details": task_error.to_dict() if hasattr(task_error, 'to_dict') else {
                "error_type": type(task_error).__name__,
                "error_message": str(task_error)
            },
            "severity": "medium"
        }


class SpecialistErrorHandler(ErrorHandler):
    """Specialized handler for specialist-related errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """Handle specialist-specific errors."""
        return isinstance(error, SpecialistError)
    
    def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle specialist errors with role management considerations."""
        specialist_error = error  # type: SpecialistError
        
        logger.warning(f"Specialist error: {specialist_error}")
        
        should_retry = True
        retry_after = 15
        user_message = "Specialist assignment encountered an issue."
        
        # Specific handling for different specialist error types
        if "configuration" in str(specialist_error).lower():
            should_retry = False
            user_message = "Specialist configuration error. Please check role definitions."
        elif "overload" in str(specialist_error).lower():
            retry_after = 60
            user_message = "Specialist is currently overloaded. Retrying with different assignment."
        elif "capability" in str(specialist_error).lower():
            should_retry = False
            user_message = "Selected specialist lacks required capabilities for this task."
        
        return {
            "handled": True,
            "should_retry": should_retry,
            "retry_after": retry_after,
            "user_message": user_message,
            "details": specialist_error.to_dict() if hasattr(specialist_error, 'to_dict') else {
                "error_type": type(specialist_error).__name__,
                "error_message": str(specialist_error)
            },
            "severity": "medium"
        }


class InfrastructureErrorHandler(ErrorHandler):
    """Specialized handler for infrastructure-related errors."""
    
    def can_handle(self, error: Exception) -> bool:
        """Handle infrastructure-specific errors."""
        return isinstance(error, InfrastructureError)
    
    def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle infrastructure errors with system recovery strategies."""
        infra_error = error  # type: InfrastructureError
        
        logger.error(f"Infrastructure error: {infra_error}")
        
        should_retry = infra_error.is_recoverable if hasattr(infra_error, 'is_recoverable') else True
        retry_after = 30 if should_retry else None
        user_message = "System infrastructure issue detected."
        
        # Specific handling for different infrastructure components
        if "database" in str(infra_error).lower():
            retry_after = 60
            user_message = "Database connectivity issue. Attempting to reconnect."
        elif "network" in str(infra_error).lower():
            retry_after = 45
            user_message = "Network connectivity issue. Retrying connection."
        elif "storage" in str(infra_error).lower():
            should_retry = False
            user_message = "Storage system issue. Manual intervention may be required."
        
        return {
            "handled": True,
            "should_retry": should_retry,
            "retry_after": retry_after,
            "user_message": user_message,
            "details": infra_error.to_dict() if hasattr(infra_error, 'to_dict') else {
                "error_type": type(infra_error).__name__,
                "error_message": str(infra_error)
            },
            "severity": "high"
        }


class ErrorHandlerRegistry:
    """Registry for managing error handlers with priority-based selection."""
    
    def __init__(self):
        self.handlers: Dict[int, ErrorHandler] = {}
        self.default_handler = DefaultErrorHandler()
        
        # Register default handlers
        self.register_handler(TaskErrorHandler(), priority=100)
        self.register_handler(SpecialistErrorHandler(), priority=100)
        self.register_handler(InfrastructureErrorHandler(), priority=100)
    
    def register_handler(self, handler: ErrorHandler, priority: int = 50):
        """Register an error handler with specified priority."""
        self.handlers[priority] = handler
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error by finding the appropriate handler.
        
        Handlers are tried in order of priority (highest first).
        """
        # Sort handlers by priority (highest first)
        sorted_handlers = sorted(self.handlers.items(), key=lambda x: x[0], reverse=True)
        
        for priority, handler in sorted_handlers:
            if handler.can_handle(error):
                try:
                    return handler.handle(error, context)
                except Exception as handler_error:
                    logger.error(f"Error handler {handler.__class__.__name__} failed: {handler_error}")
                    continue
        
        # Fall back to default handler
        logger.warning(f"No specific handler found for {type(error).__name__}, using default handler")
        return self.default_handler.handle(error, context)
    
    def get_registered_handlers(self) -> Dict[int, str]:
        """Get information about registered handlers."""
        return {priority: handler.__class__.__name__ for priority, handler in self.handlers.items()}