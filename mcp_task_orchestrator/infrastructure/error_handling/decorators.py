"""
Error handling decorators and utilities for standardized error management.
"""

import asyncio
import functools
import logging
from typing import Dict, Optional, Any, Callable, Type, Union, List
from .handlers import ErrorHandlerRegistry
from .retry_coordinator import get_retry_coordinator, RetryPolicy
from .logging_handlers import get_error_logger
from .recovery_strategies import get_recovery_manager
from ...domain.exceptions import BaseOrchestrationError

logger = logging.getLogger(__name__)


def handle_errors(
    error_types: Optional[List[Type[Exception]]] = None,
    auto_retry: bool = False,
    retry_policy: Optional[RetryPolicy] = None,
    auto_recover: bool = False,
    log_errors: bool = True,
    context: Optional[Dict[str, Any]] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None
):
    """
    Decorator for standardized error handling.
    
    Args:
        error_types: List of exception types to handle (None = all)
        auto_retry: Whether to automatically retry on retryable errors
        retry_policy: Custom retry policy (uses default if None)
        auto_recover: Whether to attempt automatic recovery
        log_errors: Whether to log errors
        context: Additional context for error handling
        component: Component name for logging
        operation: Operation name for logging
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_context = {
                "component": component,
                "operation": operation or func.__name__,
                "function": func.__qualname__,
                **(context or {})
            }
            
            error_registry = ErrorHandlerRegistry()
            error_logger = get_error_logger() if log_errors else None
            
            try:
                if auto_retry:
                    # Use retry coordinator
                    retry_coordinator = get_retry_coordinator()
                    operation_id = f"{component or 'unknown'}.{func.__name__}"
                    
                    async def operation_func():
                        return await func(*args, **kwargs)
                    
                    result = await retry_coordinator.retry_async(
                        operation_func, operation_id, retry_policy, error_context
                    )
                    
                    if result.success:
                        return result.final_result
                    else:
                        # Handle the final error
                        if result.last_error:
                            await _handle_error(
                                result.last_error, error_context, error_types,
                                auto_recover, error_registry, error_logger
                            )
                        raise result.last_error
                else:
                    # Direct execution
                    return await func(*args, **kwargs)
            
            except Exception as error:
                await _handle_error(
                    error, error_context, error_types,
                    auto_recover, error_registry, error_logger
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_context = {
                "component": component,
                "operation": operation or func.__name__,
                "function": func.__qualname__,
                **(context or {})
            }
            
            error_registry = ErrorHandlerRegistry()
            error_logger = get_error_logger() if log_errors else None
            
            try:
                if auto_retry:
                    # Use retry coordinator
                    retry_coordinator = get_retry_coordinator()
                    operation_id = f"{component or 'unknown'}.{func.__name__}"
                    
                    def operation_func():
                        return func(*args, **kwargs)
                    
                    result = retry_coordinator.retry_sync(
                        operation_func, operation_id, retry_policy, error_context
                    )
                    
                    if result.success:
                        return result.final_result
                    else:
                        # Handle the final error
                        if result.last_error:
                            _handle_error_sync(
                                result.last_error, error_context, error_types,
                                auto_recover, error_registry, error_logger
                            )
                        raise result.last_error
                else:
                    # Direct execution
                    return func(*args, **kwargs)
            
            except Exception as error:
                _handle_error_sync(
                    error, error_context, error_types,
                    auto_recover, error_registry, error_logger
                )
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


async def _handle_error(
    error: Exception,
    context: Dict[str, Any],
    error_types: Optional[List[Type[Exception]]],
    auto_recover: bool,
    error_registry: ErrorHandlerRegistry,
    error_logger: Optional[Any]
):
    """Handle error asynchronously."""
    # Check if we should handle this error type
    if error_types and not any(isinstance(error, et) for et in error_types):
        return
    
    # Log the error
    if error_logger:
        error_logger.log_error(error, context)
    
    # Handle the error
    error_response = error_registry.handle_error(error, context)
    
    # Attempt recovery if enabled
    if auto_recover:
        recovery_manager = get_recovery_manager()
        recovery_result = await recovery_manager.attempt_recovery(error, context)
        
        if recovery_result and recovery_result.success:
            logger.info(f"Successfully recovered from {type(error).__name__}: {recovery_result.notes}")


def _handle_error_sync(
    error: Exception,
    context: Dict[str, Any],
    error_types: Optional[List[Type[Exception]]],
    auto_recover: bool,
    error_registry: ErrorHandlerRegistry,
    error_logger: Optional[Any]
):
    """Handle error synchronously."""
    # Check if we should handle this error type
    if error_types and not any(isinstance(error, et) for et in error_types):
        return
    
    # Log the error
    if error_logger:
        error_logger.log_error(error, context)
    
    # Handle the error
    error_response = error_registry.handle_error(error, context)
    
    # Note: Auto-recovery is async, so skip for sync functions
    if auto_recover:
        logger.warning("Auto-recovery not available for synchronous functions")


def with_error_context(component: str, operation: Optional[str] = None, **additional_context):
    """
    Decorator to add error context without full error handling.
    
    Useful for adding component/operation context to functions
    that will be called by other error-handled functions.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Add context to any BaseOrchestrationError that occurs
            try:
                return func(*args, **kwargs)
            except BaseOrchestrationError as error:
                # Update error context
                error.context.update({
                    "component": component,
                    "operation": operation or func.__name__,
                    **additional_context
                })
                raise
            except Exception:
                # Re-raise other exceptions unchanged
                raise
        
        return wrapper
    return decorator


def suppress_errors(
    error_types: List[Type[Exception]],
    default_return: Any = None,
    log_suppressed: bool = True
):
    """
    Decorator to suppress specific error types and return default value.
    
    Args:
        error_types: List of exception types to suppress
        default_return: Value to return when error is suppressed
        log_suppressed: Whether to log suppressed errors
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                if any(isinstance(error, et) for et in error_types):
                    if log_suppressed:
                        logger.warning(f"Suppressed {type(error).__name__} in {func.__qualname__}: {error}")
                    return default_return
                else:
                    raise
        
        return wrapper
    return decorator


def raise_on_error_response(error_field: str = "error", success_field: str = "success"):
    """
    Decorator to raise exceptions based on response dictionaries.
    
    Useful for converting error responses to exceptions.
    
    Args:
        error_field: Field name containing error information
        success_field: Field name indicating success/failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Check if result indicates an error
            if isinstance(result, dict):
                if success_field in result and not result[success_field]:
                    error_info = result.get(error_field, "Unknown error")
                    raise BaseOrchestrationError(
                        message=str(error_info),
                        details=result,
                        error_code="RESPONSE_ERROR"
                    )
                elif error_field in result and result[error_field]:
                    error_info = result[error_field]
                    raise BaseOrchestrationError(
                        message=str(error_info),
                        details=result,
                        error_code="RESPONSE_ERROR"
                    )
            
            return result
        
        return wrapper
    return decorator


class ErrorContext:
    """Context manager for error handling with automatic cleanup."""
    
    def __init__(self, component: str, operation: str, **context):
        self.component = component
        self.operation = operation
        self.context = context
        self.error_logger = get_error_logger()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_context = {
                "component": self.component,
                "operation": self.operation,
                **self.context
            }
            self.error_logger.log_error(exc_val, error_context)
        
        # Don't suppress the exception
        return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_context = {
                "component": self.component,
                "operation": self.operation,
                **self.context
            }
            self.error_logger.log_error(exc_val, error_context)
        
        # Don't suppress the exception
        return False


def safe_call(func: Callable, *args, default=None, log_errors=True, **kwargs):
    """
    Safely call a function, returning default value on error.
    
    Args:
        func: Function to call
        *args: Positional arguments for function
        default: Default value to return on error
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result or default value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as error:
        if log_errors:
            logger.warning(f"Safe call to {func.__name__} failed: {error}")
        return default


async def safe_call_async(func: Callable, *args, default=None, log_errors=True, **kwargs):
    """
    Safely call an async function, returning default value on error.
    
    Args:
        func: Async function to call
        *args: Positional arguments for function
        default: Default value to return on error
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result or default value on error
    """
    try:
        return await func(*args, **kwargs)
    except Exception as error:
        if log_errors:
            logger.warning(f"Safe async call to {func.__name__} failed: {error}")
        return default


def validate_input(validation_func: Callable[[Any], bool], error_message: str = "Input validation failed"):
    """
    Decorator to validate function input using a validation function.
    
    Args:
        validation_func: Function that takes input and returns True if valid
        error_message: Error message for validation failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate all arguments
            for arg in args:
                if not validation_func(arg):
                    from ...domain.exceptions import ValidationError
                    raise ValidationError("argument", arg, [error_message])
            
            for key, value in kwargs.items():
                if not validation_func(value):
                    from ...domain.exceptions import ValidationError
                    raise ValidationError(key, value, [error_message])
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator