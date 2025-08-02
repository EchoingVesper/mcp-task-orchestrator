# MCP Error Handling
"""
MCP Error Handling Utilities

This module provides decorators, utilities, and integrations for handling errors
in MCP tool handlers while maintaining security and compliance with JSON-RPC 2.0.

Key Features:
- MCP error handler decorator for consistent error responses
- Integration with existing error sanitization framework
- Secure error response formatting that prevents information disclosure
- JSON-RPC 2.0 compliant error responses
- Comprehensive logging and audit trail
"""

import json
import logging
from functools import wraps
from typing import List, Dict, Any, Callable, Optional, Union
from datetime import datetime

from mcp import types

from .error_codes import (
    MCPErrorCode,
    MCPErrorResponse,
    create_mcp_error_response,
    create_validation_error,
    create_not_found_error,
    create_authentication_error,
    create_permission_error
)
from ..security.error_sanitization import sanitize_error, SafeErrorResponse
from ..security.error_sanitization import ErrorCategory
from ..security.audit_logger import SecurityAuditLogger


logger = logging.getLogger(__name__)
security_audit = SecurityAuditLogger()


def mcp_error_handler(
    tool_name: Optional[str] = None,
    require_auth: bool = False,
    log_errors: bool = True
) -> Callable:
    """
    Decorator for consistent MCP error handling in tool handlers.
    
    This decorator:
    1. Catches all exceptions from the wrapped handler
    2. Applies security sanitization to prevent information disclosure
    3. Converts errors to MCP JSON-RPC compliant responses
    4. Logs security events and errors for audit trail
    5. Provides consistent error formatting across all tools
    
    Args:
        tool_name: Name of the tool (auto-detected if not provided)
        require_auth: Whether this tool requires authentication
        log_errors: Whether to log errors (default: True)
        
    Returns:
        Decorated function with MCP error handling
        
    Example:
        @mcp_error_handler(tool_name="create_task", require_auth=True)
        async def handle_create_task(args: Dict[str, Any]) -> List[types.TextContent]:
            # Handler implementation
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> List[types.TextContent]:
            # Extract handler context for error reporting
            handler_name = tool_name or func.__name__
            start_time = datetime.utcnow()
            
            try:
                # Log tool invocation for audit trail
                if log_errors:
                    logger.info(f"MCP tool invoked: {handler_name}")
                    
                # Execute the actual handler
                result = await func(*args, **kwargs)
                
                # Log successful completion
                duration = (datetime.utcnow() - start_time).total_seconds()
                if log_errors:
                    logger.debug(f"MCP tool completed: {handler_name} ({duration:.3f}s)")
                
                return result
                
            except Exception as e:
                # Calculate error duration for monitoring
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Extract context from handler arguments
                context = {
                    "handler": handler_name,
                    "duration_seconds": duration,
                    "requires_auth": require_auth,
                    "args_count": len(args) if args else 0,
                    "kwargs_keys": list(kwargs.keys()) if kwargs else [],
                    "timestamp": start_time.isoformat()
                }
                
                # Add sanitized argument information for debugging
                if args and len(args) > 0 and isinstance(args[0], dict):
                    # First argument is typically the tool arguments
                    tool_args = args[0]
                    context["tool_args_keys"] = list(tool_args.keys())
                    # Add safe argument info (no sensitive values)
                    context["has_title"] = "title" in tool_args
                    context["has_description"] = "description" in tool_args
                
                # Security audit logging
                if log_errors:
                    security_audit.log_error_event(
                        error_type=type(e).__name__,
                        context=handler_name,
                        severity="HIGH" if require_auth else "MEDIUM",
                        details=f"MCP tool error in {handler_name}: {str(e)[:200]}"
                    )
                
                # Create secure MCP error response
                try:
                    # First apply security sanitization
                    sanitized = sanitize_error(e, context)
                    
                    # Convert to MCP-compliant error response
                    mcp_response = create_mcp_error_response(
                        exception=e,
                        context={
                            **context,
                            "sanitized_category": sanitized.category.value,
                            "sanitized_message": sanitized.message,
                            "suggestions": sanitized.suggestions
                        }
                    )
                    
                    # Log the error with correlation ID
                    if log_errors:
                        logger.error(
                            f"MCP tool error in {handler_name} "
                            f"[{mcp_response.error_id}]: {sanitized.message}"
                        )
                    
                    # Return MCP-compliant error response
                    return [types.TextContent(
                        type="text", 
                        text=mcp_response.to_json()
                    )]
                    
                except Exception as formatting_error:
                    # Last resort error handling if response formatting fails
                    logger.critical(
                        f"Error formatting failed in {handler_name}: {formatting_error}"
                    )
                    
                    # Create minimal safe error response
                    fallback_response = MCPErrorResponse(
                        code=MCPErrorCode.INTERNAL_ERROR,
                        message="Internal error occurred",
                        data={"handler": handler_name}
                    )
                    
                    return [types.TextContent(
                        type="text",
                        text=fallback_response.to_json()
                    )]
        
        return wrapper
    return decorator


def mcp_validation_handler(required_fields: List[str]) -> Callable:
    """
    Decorator for validating required fields with MCP-compliant error responses.
    
    Args:
        required_fields: List of required field names
        
    Returns:
        Decorator that validates fields before handler execution
        
    Example:
        @mcp_validation_handler(["title", "description"])
        @mcp_error_handler("create_task")
        async def handle_create_task(args: Dict[str, Any]) -> List[types.TextContent]:
            # Fields are guaranteed to be present
            pass
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> List[types.TextContent]:
            # Extract tool arguments 
            # Handle both direct dict argument and wrapped in args
            if args and isinstance(args[0], dict):
                tool_args = args[0]
            elif kwargs and isinstance(kwargs, dict):
                tool_args = kwargs
            else:
                # Fallback - empty dict will trigger validation error
                tool_args = {}
            
            # Validate required fields
            missing_fields = []
            invalid_fields = []
            
            for field in required_fields:
                if field not in tool_args:
                    missing_fields.append(field)
                elif not tool_args[field] or (isinstance(tool_args[field], str) and not tool_args[field].strip()):
                    invalid_fields.append(field)
            
            # Return validation error if fields are missing or invalid
            if missing_fields or invalid_fields:
                error_details = []
                if missing_fields:
                    error_details.append(f"Missing required fields: {', '.join(missing_fields)}")
                if invalid_fields:
                    error_details.append(f"Empty or invalid fields: {', '.join(invalid_fields)}")
                
                validation_error = create_validation_error(
                    field=missing_fields[0] if missing_fields else invalid_fields[0],
                    value=None,
                    message="; ".join(error_details)
                )
                
                return [types.TextContent(
                    type="text",
                    text=validation_error.to_json()
                )]
            
            # All validations passed, execute handler
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def format_mcp_success_response(
    data: Dict[str, Any],
    message: str = "Operation completed successfully"
) -> List[types.TextContent]:
    """
    Format successful MCP response with consistent structure.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Formatted MCP success response
    """
    response = {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


def format_mcp_error_response(
    error: Union[Exception, str],
    context: Optional[Dict[str, Any]] = None,
    error_code: Optional[MCPErrorCode] = None
) -> List[types.TextContent]:
    """
    Format MCP error response for manual error handling.
    
    Args:
        error: Exception or error message
        context: Additional context
        error_code: Specific MCP error code
        
    Returns:
        Formatted MCP error response
    """
    if isinstance(error, str):
        # Create exception from string message
        error = ValueError(error)
    
    # Create MCP error response
    if error_code:
        mcp_response = MCPErrorResponse(
            code=error_code,
            message=str(error),
            data=context or {}
        )
    else:
        mcp_response = create_mcp_error_response(error, context)
    
    return [types.TextContent(
        type="text",
        text=mcp_response.to_json()
    )]


def handle_authentication_error(
    reason: str = "Authentication required"
) -> List[types.TextContent]:
    """
    Create authentication error response.
    
    Args:
        reason: Authentication failure reason
        
    Returns:
        MCP authentication error response
    """
    auth_error = create_authentication_error(reason)
    return [types.TextContent(
        type="text",
        text=auth_error.to_json()
    )]


def handle_permission_error(
    action: str,
    resource: str = ""
) -> List[types.TextContent]:
    """
    Create permission denied error response.
    
    Args:
        action: Action that was denied
        resource: Resource the action was attempted on
        
    Returns:
        MCP permission error response
    """
    perm_error = create_permission_error(action, resource)
    return [types.TextContent(
        type="text",
        text=perm_error.to_json()
    )]


def handle_not_found_error(
    resource_type: str,
    resource_id: str
) -> List[types.TextContent]:
    """
    Create not found error response.
    
    Args:
        resource_type: Type of resource (e.g., 'task', 'specialist')  
        resource_id: ID of the resource that wasn't found
        
    Returns:
        MCP not found error response
    """
    not_found_error = create_not_found_error(resource_type, resource_id)
    return [types.TextContent(
        type="text",
        text=not_found_error.to_json()
    )]


class MCPErrorContext:
    """
    Context manager for capturing additional error information.
    
    Example:
        async def my_handler(args):
            with MCPErrorContext(tool="create_task", user_id="123") as ctx:
                # Handler logic
                ctx.add_context("operation", "task_creation")
                result = create_task(args)
                return format_mcp_success_response(result)
    """
    
    def __init__(self, **initial_context):
        self.context = initial_context
        self.start_time = datetime.utcnow()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            # Add timing information to context
            self.context["duration_seconds"] = (
                datetime.utcnow() - self.start_time
            ).total_seconds()
    
    def add_context(self, key: str, value: Any) -> None:
        """Add context information for error reporting."""
        self.context[key] = value
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context dictionary."""
        return self.context.copy()


# Utility functions for common MCP operations
def validate_task_id(task_id: Any) -> str:
    """
    Validate and normalize task ID.
    
    Args:
        task_id: Task ID to validate
        
    Returns:
        Validated task ID string
        
    Raises:
        ValueError: If task ID is invalid
    """
    if not task_id:
        raise ValueError("Task ID is required")
    
    task_id_str = str(task_id).strip()
    if not task_id_str:
        raise ValueError("Task ID cannot be empty")
    
    # Basic format validation (UUIDs, numeric IDs, etc.)
    if len(task_id_str) > 100:
        raise ValueError("Task ID too long (max 100 characters)")
    
    return task_id_str


def validate_tool_arguments(
    args: Dict[str, Any], 
    required: List[str],
    optional: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate and sanitize tool arguments.
    
    Args:
        args: Tool arguments to validate
        required: Required field names
        optional: Optional field names
        
    Returns:
        Validated and sanitized arguments
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be a dictionary")
    
    # Check required fields
    missing = [field for field in required if field not in args]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    
    # Check for unknown fields (if optional list provided)
    if optional is not None:
        allowed = set(required) | set(optional)
        unknown = set(args.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields: {', '.join(unknown)}")
    
    # Sanitize string fields
    sanitized = {}
    for key, value in args.items():
        if isinstance(value, str):
            # Basic string sanitization
            sanitized[key] = value.strip()
        else:
            sanitized[key] = value
    
    return sanitized