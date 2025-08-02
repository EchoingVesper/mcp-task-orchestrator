"""
Error Sanitization Framework for MCP Task Orchestrator

Implements comprehensive error sanitization to prevent information disclosure
while maintaining helpful error messages for legitimate debugging and user feedback.

Enhanced with MCP JSON-RPC error code support for protocol compliance.
"""

import logging
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Type, Any, Optional, List, Tuple, Union
import re
import hashlib
import json

# Configure security logging
security_logger = logging.getLogger("mcp_task_orchestrator.security.error_sanitization")


class ErrorCategory(Enum):
    """Categories of errors for consistent handling and MCP error code mapping."""
    
    # Client-safe errors (can show details)
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND_ERROR = "not_found_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    
    # Internal errors (sanitize details)
    DATABASE_ERROR = "database_error"
    SYSTEM_ERROR = "system_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    
    # Critical errors (minimal disclosure)
    SECURITY_ERROR = "security_error"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    
    # MCP-specific error categories
    TIMEOUT_ERROR = "timeout_error"
    DEPENDENCY_ERROR = "dependency_error"
    WORKSPACE_ERROR = "workspace_error"


class SafeErrorResponse:
    """Represents a sanitized error response safe for client consumption."""
    
    def __init__(self, 
                 message: str,
                 error_code: str,
                 category: ErrorCategory,
                 error_id: str,
                 details: Optional[Dict[str, Any]] = None,
                 suggestions: Optional[List[str]] = None):
        """Initialize safe error response."""
        self.message = message
        self.error_code = error_code
        self.category = category
        self.error_id = error_id
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": True,
            "message": self.message,
            "error_code": self.error_code,
            "category": self.category.value,
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "details": self.details,
            "suggestions": self.suggestions
        }
    
    def to_mcp_error(self) -> Dict[str, Any]:
        """Convert to MCP JSON-RPC compliant error format."""
        # Import here to avoid circular imports
        try:
            from ..mcp.error_codes import ERROR_CATEGORY_TO_MCP_CODE, MCPErrorCode
            
            # Map category to MCP error code
            mcp_code = ERROR_CATEGORY_TO_MCP_CODE.get(
                self.category, 
                MCPErrorCode.INTERNAL_ERROR
            )
            
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": mcp_code.value,
                    "message": self.message,
                    "data": {
                        "error_id": self.error_id,
                        "category": self.category.value,
                        "timestamp": self.timestamp,
                        "details": self.details,
                        "suggestions": self.suggestions,
                        "error_type": mcp_code.name.lower()
                    }
                },
                "id": None
            }
            
        except ImportError:
            # Fallback to basic structure if MCP module not available
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,  # Internal error
                    "message": self.message,
                    "data": {
                        "error_id": self.error_id,
                        "category": self.category.value,
                        "timestamp": self.timestamp,
                        "details": self.details,
                        "suggestions": self.suggestions
                    }
                },
                "id": None
            }


class ErrorSanitizer:
    """
    Comprehensive error sanitization system.
    
    Converts internal exceptions to safe, user-friendly error messages
    while logging full details internally for debugging and monitoring.
    """
    
    # Mapping of exception types to error categories and safe messages
    ERROR_MAPPINGS = {
        # Database-related exceptions
        'IntegrityError': (ErrorCategory.VALIDATION_ERROR, "Data validation failed", [
            "Check that all required fields are provided",
            "Ensure unique constraints are not violated"
        ]),
        'OperationalError': (ErrorCategory.DATABASE_ERROR, "Database operation failed", [
            "Please try again in a few moments",
            "Contact support if the problem persists"
        ]),
        'DatabaseError': (ErrorCategory.DATABASE_ERROR, "Database error occurred", [
            "Please try again later",
            "Check that the system is accessible"
        ]),
        
        # File system exceptions
        'FileNotFoundError': (ErrorCategory.NOT_FOUND_ERROR, "Requested resource not found", [
            "Check that the resource identifier is correct",
            "Ensure the resource has not been deleted"
        ]),
        'PermissionError': (ErrorCategory.AUTHORIZATION_ERROR, "Access denied", [
            "Check that you have permission to access this resource",
            "Contact an administrator if you need access"
        ]),
        'FileExistsError': (ErrorCategory.VALIDATION_ERROR, "Resource already exists", [
            "Use a different name or identifier",
            "Check if you meant to update an existing resource"
        ]),
        'IsADirectoryError': (ErrorCategory.VALIDATION_ERROR, "Invalid file operation", [
            "Check that the path points to a file, not a directory"
        ]),
        
        # Network and connection exceptions
        'ConnectionError': (ErrorCategory.NETWORK_ERROR, "Connection failed", [
            "Check your network connection",
            "Try again in a few moments"
        ]),
        'TimeoutError': (ErrorCategory.NETWORK_ERROR, "Operation timed out", [
            "The operation took too long to complete",
            "Try again with a simpler request"
        ]),
        
        # Validation and input exceptions
        'ValueError': (ErrorCategory.VALIDATION_ERROR, "Invalid input provided", [
            "Check that all input values are in the correct format",
            "Refer to the documentation for valid input examples"
        ]),
        'TypeError': (ErrorCategory.VALIDATION_ERROR, "Invalid data type", [
            "Check that the data types match the expected format",
            "Ensure all required fields are provided"
        ]),
        'KeyError': (ErrorCategory.VALIDATION_ERROR, "Missing required field", [
            "Check that all required fields are included",
            "Refer to the API documentation for required fields"
        ]),
        
        # Authentication and authorization
        'AuthenticationError': (ErrorCategory.AUTHENTICATION_ERROR, "Authentication failed", [
            "Check that your API key is valid and active",
            "Ensure you are using the correct authentication method"
        ]),
        'AuthorizationError': (ErrorCategory.AUTHORIZATION_ERROR, "Insufficient permissions", [
            "You don't have permission to perform this operation",
            "Contact an administrator to request access"
        ]),
        
        # Security-related exceptions
        'ValidationError': (ErrorCategory.SECURITY_ERROR, "Security validation failed", [
            "Input contains potentially dangerous content",
            "Please review your input and try again"
        ]),
        'SecurityError': (ErrorCategory.SECURITY_ERROR, "Security policy violation", [
            "This operation violates security policies",
            "Contact support if you believe this is an error"
        ]),
        
        # System and configuration errors
        'ImportError': (ErrorCategory.CONFIGURATION_ERROR, "System configuration error", [
            "A required component is not available",
            "Contact support for assistance"
        ]),
        'AttributeError': (ErrorCategory.CONFIGURATION_ERROR, "System configuration error", [
            "A system component is not properly configured",
            "Contact support for assistance"
        ]),
        'NotImplementedError': (ErrorCategory.SYSTEM_ERROR, "Feature not available", [
            "This feature is not yet implemented",
            "Check the documentation for alternative approaches"
        ]),
        
        # Generic fallbacks
        'Exception': (ErrorCategory.INTERNAL_SERVER_ERROR, "An unexpected error occurred", [
            "Please try again in a few moments",
            "Contact support if the problem persists"
        ])
    }
    
    # Patterns to remove from error messages (sensitive information)
    SENSITIVE_PATTERNS = [
        r'/[A-Za-z]:/[^/\s]*',           # Windows file paths
        r'/[a-zA-Z0-9_/.-]+',            # Unix file paths
        r'password["\']?\s*[:=]\s*["\']?[^\s"\']+',  # Passwords
        r'api_?key["\']?\s*[:=]\s*["\']?[^\s"\']+',  # API keys
        r'token["\']?\s*[:=]\s*["\']?[^\s"\']+',     # Tokens
        r'secret["\']?\s*[:=]\s*["\']?[^\s"\']+',    # Secrets
        r'host["\']?\s*[:=]\s*["\']?[^\s"\']+',      # Hostnames
        r'port["\']?\s*[:=]\s*["\']?\d+',            # Port numbers
        r'user[name]?["\']?\s*[:=]\s*["\']?[^\s"\']+', # Usernames
        r'0x[0-9a-fA-F]+',               # Memory addresses
        r'at 0x[0-9a-fA-F]+',            # Memory addresses in stack traces
        r'File "[^"]*"',                 # File references in stack traces
        r'line \d+',                     # Line numbers
        r'in [a-zA-Z_][a-zA-Z0-9_]*',    # Function names in stack traces
    ]
    
    def __init__(self):
        """Initialize error sanitizer."""
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.SENSITIVE_PATTERNS]
        self._error_counter = 0
    
    def sanitize_exception(self, 
                          exception: Exception,
                          context: Optional[Dict[str, Any]] = None,
                          user_id: Optional[str] = None,
                          operation: Optional[str] = None) -> SafeErrorResponse:
        """
        Sanitize an exception into a safe error response.
        
        Args:
            exception: The exception to sanitize
            context: Additional context about the error
            user_id: User ID associated with the error
            operation: Operation being performed when error occurred
            
        Returns:
            SafeErrorResponse: Sanitized error safe for client consumption
        """
        # Generate unique error ID for tracking
        error_id = self._generate_error_id(exception, context)
        
        # Get exception type name
        exception_type = type(exception).__name__
        
        # Find the most specific error mapping
        category, safe_message, suggestions = self._get_error_mapping(exception_type)
        
        # Sanitize the exception message
        sanitized_details = self._sanitize_error_message(str(exception))
        
        # Log full error details internally (with sensitive data)
        self._log_internal_error(exception, error_id, context, user_id, operation)
        
        # Create safe error response
        safe_response = SafeErrorResponse(
            message=safe_message,
            error_code=exception_type.upper(),
            category=category,
            error_id=error_id,
            details={"sanitized_message": sanitized_details} if sanitized_details else {},
            suggestions=suggestions
        )
        
        # Log sanitized error for monitoring
        security_logger.info(
            f"Error sanitized: error_id={error_id}, type={exception_type}, "
            f"category={category.value}, user_id={user_id}, operation={operation}"
        )
        
        return safe_response
    
    def _get_error_mapping(self, exception_type: str) -> Tuple[ErrorCategory, str, List[str]]:
        """Get error mapping for exception type."""
        # Try exact match first
        if exception_type in self.ERROR_MAPPINGS:
            return self.ERROR_MAPPINGS[exception_type]
        
        # Try parent class matches
        for mapped_type, mapping in self.ERROR_MAPPINGS.items():
            if mapped_type in exception_type or exception_type.endswith(mapped_type):
                return mapping
        
        # Fall back to generic error
        return self.ERROR_MAPPINGS['Exception']
    
    def _sanitize_error_message(self, message: str) -> str:
        """Remove sensitive information from error message."""
        sanitized = message
        
        # Remove sensitive patterns
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub('[REDACTED]', sanitized)
        
        # Truncate very long messages
        if len(sanitized) > 200:
            sanitized = sanitized[:197] + "..."
        
        return sanitized
    
    def _generate_error_id(self, exception: Exception, context: Optional[Dict[str, Any]]) -> str:
        """Generate unique error ID for tracking."""
        self._error_counter += 1
        
        # Create hash from exception details
        error_content = f"{type(exception).__name__}:{str(exception)}:{self._error_counter}"
        if context:
            error_content += f":{str(context)}"
        
        error_hash = hashlib.md5(error_content.encode()).hexdigest()[:8]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
        
        return f"ERR_{timestamp}_{error_hash}"
    
    def _log_internal_error(self, 
                           exception: Exception,
                           error_id: str,
                           context: Optional[Dict[str, Any]],
                           user_id: Optional[str],
                           operation: Optional[str]) -> None:
        """Log full error details internally for debugging."""
        # Log with full stack trace for debugging
        internal_logger = logging.getLogger("mcp_task_orchestrator.internal.errors")
        
        error_details = {
            "error_id": error_id,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "user_id": user_id,
            "operation": operation,
            "context": context,
            "stack_trace": traceback.format_exc()
        }
        
        internal_logger.error(f"Internal error details: {error_details}")


# Global error sanitizer instance
error_sanitizer = ErrorSanitizer()

# Convenience functions for common operations
def sanitize_error(exception: Exception, 
                  context: Optional[Dict[str, Any]] = None,
                  user_id: Optional[str] = None,
                  operation: Optional[str] = None) -> SafeErrorResponse:
    """Sanitize an exception - convenience function."""
    return error_sanitizer.sanitize_exception(exception, context, user_id, operation)

def safe_error_response(exception: Exception, 
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get safe error response as dictionary - convenience function."""
    return sanitize_error(exception, context).to_dict()

def mcp_error_response(exception: Exception,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get MCP-compliant error response - convenience function."""
    return sanitize_error(exception, context).to_mcp_error()

# Decorator for automatic error sanitization in MCP handlers
def sanitize_handler_errors(func):
    """
    Decorator to automatically sanitize errors in MCP handlers.
    
    Usage:
        @sanitize_handler_errors
        async def handle_create_task(args):
            # Handler implementation that might raise exceptions
            pass
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Extract context from handler
            operation = func.__name__
            context = {"args": str(args)[:200], "kwargs": list(kwargs.keys())}
            
            # Get user ID from auth metadata if available
            user_id = kwargs.get('_auth_metadata', {}).get('user_id')
            
            # Return sanitized error response
            safe_response = sanitize_error(e, context, user_id, operation)
            return safe_response.to_mcp_error()
    
    return wrapper