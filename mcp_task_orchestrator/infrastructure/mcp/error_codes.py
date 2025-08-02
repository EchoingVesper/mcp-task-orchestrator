# MCP Error Codes
"""
MCP JSON-RPC Error Code Implementation

This module provides MCP-compliant JSON-RPC error codes and utilities for proper
error handling in the MCP Task Orchestrator. It integrates with the existing
error sanitization framework to provide secure, standardized error responses.

References:
- JSON-RPC 2.0 Specification: https://www.jsonrpc.org/specification
- MCP Protocol Documentation: https://modelcontextprotocol.io/docs/specification
"""

from enum import Enum
from typing import Dict, Any, Optional, Union
from datetime import datetime
import uuid

from ..security.error_sanitization import ErrorCategory


class MCPErrorCode(Enum):
    """
    MCP JSON-RPC Error Codes.
    
    Standard JSON-RPC error codes plus MCP-specific server errors.
    """
    # JSON-RPC 2.0 Standard Error Codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600  
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # MCP Server Error Range (-32000 to -32099)
    TASK_NOT_FOUND = -32000
    PERMISSION_DENIED = -32001
    VALIDATION_FAILED = -32002
    AUTHENTICATION_REQUIRED = -32003
    RESOURCE_EXHAUSTED = -32004
    DATABASE_ERROR = -32005
    ORCHESTRATION_ERROR = -32006
    SECURITY_VIOLATION = -32007
    CONFIGURATION_ERROR = -32008
    SPECIALIST_ERROR = -32009
    TIMEOUT_ERROR = -32010
    DEPENDENCY_ERROR = -32011
    WORKSPACE_ERROR = -32012
    
    @property
    def message(self) -> str:
        """Get standard message for error code."""
        return ERROR_CODE_MESSAGES.get(self, "Unknown error")
    
    @property
    def is_client_error(self) -> bool:
        """Check if this is a client-side error (4xx equivalent)."""
        return self.value in {
            self.PARSE_ERROR.value,
            self.INVALID_REQUEST.value,
            self.METHOD_NOT_FOUND.value,
            self.INVALID_PARAMS.value,
            self.VALIDATION_FAILED.value,
            self.AUTHENTICATION_REQUIRED.value,
            self.PERMISSION_DENIED.value
        }
    
    @property
    def is_server_error(self) -> bool:
        """Check if this is a server-side error (5xx equivalent)."""
        return not self.is_client_error


# Standard error messages for each code
ERROR_CODE_MESSAGES: Dict[MCPErrorCode, str] = {
    MCPErrorCode.PARSE_ERROR: "Parse error",
    MCPErrorCode.INVALID_REQUEST: "Invalid Request", 
    MCPErrorCode.METHOD_NOT_FOUND: "Method not found",
    MCPErrorCode.INVALID_PARAMS: "Invalid params",
    MCPErrorCode.INTERNAL_ERROR: "Internal error",
    MCPErrorCode.TASK_NOT_FOUND: "Task not found",
    MCPErrorCode.PERMISSION_DENIED: "Permission denied",
    MCPErrorCode.VALIDATION_FAILED: "Validation failed",
    MCPErrorCode.AUTHENTICATION_REQUIRED: "Authentication required",
    MCPErrorCode.RESOURCE_EXHAUSTED: "Resource exhausted",
    MCPErrorCode.DATABASE_ERROR: "Database error",
    MCPErrorCode.ORCHESTRATION_ERROR: "Orchestration error",
    MCPErrorCode.SECURITY_VIOLATION: "Security violation",
    MCPErrorCode.CONFIGURATION_ERROR: "Configuration error",
    MCPErrorCode.SPECIALIST_ERROR: "Specialist error",
    MCPErrorCode.TIMEOUT_ERROR: "Request timeout",
    MCPErrorCode.DEPENDENCY_ERROR: "Dependency error",
    MCPErrorCode.WORKSPACE_ERROR: "Workspace error",
}


# Map error categories to MCP error codes
ERROR_CATEGORY_TO_MCP_CODE: Dict[ErrorCategory, MCPErrorCode] = {
    ErrorCategory.VALIDATION_ERROR: MCPErrorCode.INVALID_PARAMS,
    ErrorCategory.AUTHENTICATION_ERROR: MCPErrorCode.AUTHENTICATION_REQUIRED,
    ErrorCategory.AUTHORIZATION_ERROR: MCPErrorCode.PERMISSION_DENIED,
    ErrorCategory.NOT_FOUND_ERROR: MCPErrorCode.TASK_NOT_FOUND,
    ErrorCategory.DATABASE_ERROR: MCPErrorCode.DATABASE_ERROR,
    ErrorCategory.SYSTEM_ERROR: MCPErrorCode.INTERNAL_ERROR,
    ErrorCategory.INTERNAL_SERVER_ERROR: MCPErrorCode.INTERNAL_ERROR,
    ErrorCategory.CONFIGURATION_ERROR: MCPErrorCode.CONFIGURATION_ERROR,
    ErrorCategory.SECURITY_ERROR: MCPErrorCode.SECURITY_VIOLATION,
    ErrorCategory.TIMEOUT_ERROR: MCPErrorCode.TIMEOUT_ERROR,
    ErrorCategory.DEPENDENCY_ERROR: MCPErrorCode.DEPENDENCY_ERROR,
    ErrorCategory.WORKSPACE_ERROR: MCPErrorCode.WORKSPACE_ERROR,
}

# Map exception types to MCP error codes  
EXCEPTION_TYPE_TO_MCP_CODE: Dict[str, MCPErrorCode] = {
    "ValidationError": MCPErrorCode.VALIDATION_FAILED,
    "ValueError": MCPErrorCode.INVALID_PARAMS,
    "KeyError": MCPErrorCode.INVALID_PARAMS,
    "TypeError": MCPErrorCode.INVALID_PARAMS,
    "FileNotFoundError": MCPErrorCode.TASK_NOT_FOUND,
    "PermissionError": MCPErrorCode.PERMISSION_DENIED,
    "TimeoutError": MCPErrorCode.TIMEOUT_ERROR,
    "ConnectionError": MCPErrorCode.DATABASE_ERROR,
    "AuthenticationError": MCPErrorCode.AUTHENTICATION_REQUIRED,
    "AuthorizationError": MCPErrorCode.PERMISSION_DENIED,
    "TaskError": MCPErrorCode.ORCHESTRATION_ERROR,
    "SpecialistError": MCPErrorCode.SPECIALIST_ERROR,
    "WorkspaceError": MCPErrorCode.WORKSPACE_ERROR,
    "SecurityError": MCPErrorCode.SECURITY_VIOLATION,
}


class MCPErrorResponse:
    """
    Structured MCP error response following JSON-RPC 2.0 specification.
    """
    
    def __init__(
        self,
        code: MCPErrorCode,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Any = None,
        error_id: Optional[str] = None
    ):
        self.code = code
        self.message = message
        self.data = data or {}
        self.request_id = request_id
        self.error_id = error_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP JSON-RPC compliant dictionary."""
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": self.code.value,
                "message": self.message,
                "data": {
                    **self.data,
                    "error_id": self.error_id,
                    "timestamp": self.timestamp,
                    "error_type": self.code.name.lower()
                }
            },
            "id": self.request_id
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)


def get_mcp_error_code(
    exception: Exception,
    category: Optional[ErrorCategory] = None
) -> MCPErrorCode:
    """
    Determine appropriate MCP error code for an exception.
    
    Args:
        exception: The exception that occurred
        category: Optional error category override
        
    Returns:
        Appropriate MCP error code
    """
    # Use category mapping first if provided
    if category and category in ERROR_CATEGORY_TO_MCP_CODE:
        return ERROR_CATEGORY_TO_MCP_CODE[category]
    
    # Try exception type mapping
    exception_name = type(exception).__name__
    if exception_name in EXCEPTION_TYPE_TO_MCP_CODE:
        return EXCEPTION_TYPE_TO_MCP_CODE[exception_name]
    
    # Check if it's a known orchestration exception
    if hasattr(exception, 'category') and exception.category in ERROR_CATEGORY_TO_MCP_CODE:
        return ERROR_CATEGORY_TO_MCP_CODE[exception.category]
    
    # Default to internal error for unknown exceptions
    return MCPErrorCode.INTERNAL_ERROR


def create_mcp_error_response(
    exception: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: Any = None,
    category: Optional[ErrorCategory] = None
) -> MCPErrorResponse:
    """
    Create MCP-compliant error response from exception.
    
    Args:
        exception: The exception that occurred
        context: Additional context for the error
        request_id: JSON-RPC request ID
        category: Optional error category override
        
    Returns:
        MCP error response object
    """
    # Determine error code
    mcp_code = get_mcp_error_code(exception, category)
    
    # Use standard message or exception message
    if hasattr(exception, 'message') and exception.message:
        message = exception.message
    else:
        message = mcp_code.message
    
    # Prepare error data
    error_data = {
        "exception_type": type(exception).__name__,
        **(context or {})
    }
    
    # Add additional data from orchestration exceptions
    if hasattr(exception, 'error_id'):
        error_data["orchestration_error_id"] = exception.error_id
    
    if hasattr(exception, 'severity'):
        error_data["severity"] = exception.severity.value
    
    if hasattr(exception, 'recovery_strategy'):
        error_data["recovery_strategy"] = exception.recovery_strategy.value
    
    return MCPErrorResponse(
        code=mcp_code,
        message=message,
        data=error_data,
        request_id=request_id
    )


def create_validation_error(
    field: str,
    value: Any,
    message: str,
    request_id: Any = None
) -> MCPErrorResponse:
    """
    Create validation error response.
    
    Args:
        field: Field that failed validation
        value: Invalid value (will be sanitized)
        message: Validation error message
        request_id: JSON-RPC request ID
        
    Returns:
        MCP validation error response
    """
    return MCPErrorResponse(
        code=MCPErrorCode.INVALID_PARAMS,
        message=f"Validation failed for field '{field}': {message}",
        data={
            "field": field,
            "validation_message": message,
            "validation_type": "field_validation"
        },
        request_id=request_id
    )


def create_not_found_error(
    resource_type: str,
    resource_id: str,
    request_id: Any = None
) -> MCPErrorResponse:
    """
    Create resource not found error response.
    
    Args:
        resource_type: Type of resource (e.g., 'task', 'specialist')
        resource_id: ID of the resource that wasn't found
        request_id: JSON-RPC request ID
        
    Returns:
        MCP not found error response
    """
    return MCPErrorResponse(
        code=MCPErrorCode.TASK_NOT_FOUND,
        message=f"{resource_type.title()} not found",
        data={
            "resource_type": resource_type,
            "resource_id": resource_id
        },
        request_id=request_id
    )


def create_authentication_error(
    reason: str = "Authentication required",
    request_id: Any = None
) -> MCPErrorResponse:
    """
    Create authentication error response.
    
    Args:
        reason: Reason for authentication failure
        request_id: JSON-RPC request ID
        
    Returns:
        MCP authentication error response
    """
    return MCPErrorResponse(
        code=MCPErrorCode.AUTHENTICATION_REQUIRED,
        message=reason,
        data={"auth_required": True},
        request_id=request_id
    )


def create_permission_error(
    action: str,
    resource: str = "",
    request_id: Any = None
) -> MCPErrorResponse:
    """
    Create permission denied error response.
    
    Args:
        action: Action that was denied
        resource: Resource the action was attempted on
        request_id: JSON-RPC request ID
        
    Returns:
        MCP permission error response
    """
    message = f"Permission denied for action '{action}'"
    if resource:
        message += f" on resource '{resource}'"
        
    return MCPErrorResponse(
        code=MCPErrorCode.PERMISSION_DENIED,
        message=message,
        data={
            "action": action,
            "resource": resource
        },
        request_id=request_id
    )