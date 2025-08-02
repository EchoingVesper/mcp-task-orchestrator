"""
Security Infrastructure for MCP Task Orchestrator

Comprehensive security framework implementing authentication, authorization,
input validation, and audit logging with security-first design principles.

This module provides:
- API key management with secure hashing
- Role-Based Access Control (RBAC) with hierarchical permissions  
- Input validation with XSS and injection prevention
- Path traversal protection
- Comprehensive security audit logging
- Decorator-based security enforcement

Usage Examples:

Authentication:
    from mcp_task_orchestrator.infrastructure.security import (
        generate_api_key, validate_api_key, require_auth
    )
    
    # Generate API key
    api_key = generate_api_key("Development Key", expires_days=30)
    
    # Use authentication decorator
    @require_auth
    async def protected_handler(args):
        # Handler automatically requires valid API key
        pass

Authorization:
    from mcp_task_orchestrator.infrastructure.security import (
        require_permission, require_role, Permission, Role
    )
    
    # Require specific permission
    @require_permission(Permission.CREATE_TASK)
    async def create_task_handler(args):
        # Handler requires CREATE_TASK permission
        pass
    
    # Require minimum role level
    @require_role(Role.MANAGER)
    async def admin_handler(args):
        # Handler requires MANAGER role or higher
        pass

Input Validation:
    from mcp_task_orchestrator.infrastructure.security import (
        validate_string_input, validate_file_path, validate_task_id
    )
    
    # Validate user input
    safe_title = validate_string_input(user_input, "title", max_length=255)
    
    # Validate file paths
    safe_path = validate_file_path(file_path, base_directory, "file_path")

Security Logging:
    from mcp_task_orchestrator.infrastructure.security import (
        log_auth_success, log_xss_attempt, get_security_summary
    )
    
    # Log security events
    log_auth_success("user123", {"method": "api_key"})
    
    # Get security summary
    summary = get_security_summary(hours=24)
"""

# Authentication components
from .authentication import (
    APIKeyManager,
    AuthenticationValidator,
    AuthenticationError,
    api_key_manager,
    auth_validator,
    generate_api_key,
    validate_api_key,
    require_auth
)

# Authorization components
from .authorization import (
    Permission,
    Role,
    RoleManager,
    UserRoleManager,
    AuthorizationValidator,
    AuthorizationError,
    role_manager,
    user_role_manager,
    authz_validator,
    require_permission,
    require_role,
    has_permission
)

# Input validation components
from .validators import (
    XSSValidator,
    PathValidator,
    ParameterValidator,
    ValidationError,
    xss_validator,
    path_validator,
    parameter_validator,
    validate_string_input,
    validate_file_path,
    validate_task_id,
    is_safe_input
)

# Security audit logging components
from .audit_logger import (
    SecurityEventType,
    SecurityLevel,
    SecurityAuditLogger,
    security_audit_logger,
    log_auth_success,
    log_auth_failure,
    log_authz_failure,
    log_xss_attempt,
    log_path_traversal,
    get_security_summary
)

# Error sanitization components
from .error_sanitization import (
    ErrorCategory,
    SafeErrorResponse,
    ErrorSanitizer,
    error_sanitizer,
    sanitize_error,
    safe_error_response,
    mcp_error_response,
    sanitize_handler_errors
)

# Combined security decorator for MCP handlers
def secure_mcp_handler(permission: Permission):
    """
    Combined security decorator requiring both authentication and authorization.
    
    This decorator combines authentication and authorization checks into a single
    decorator for MCP handlers, providing comprehensive security enforcement.
    
    Args:
        permission: Required permission for the handler
        
    Usage:
        @secure_mcp_handler(Permission.CREATE_TASK)
        async def handle_create_task(args):
            # Handler requires valid API key AND CREATE_TASK permission
            pass
    """
    def decorator(func):
        # Apply authorization check first (includes authentication)
        func = require_permission(permission)(func)
        # Apply authentication check
        func = require_auth(func)
        return func
    return decorator

# Security initialization function
def initialize_security(api_key_storage_path: str = None,
                       audit_log_path: str = None,
                       enable_console_logging: bool = False) -> None:
    """
    Initialize security infrastructure with custom configuration.
    
    Args:
        api_key_storage_path: Custom path for API key storage
        audit_log_path: Custom path for security audit logs
        enable_console_logging: Whether to enable console security logging
    """
    global api_key_manager, security_audit_logger
    
    # Reinitialize API key manager with custom path
    if api_key_storage_path:
        api_key_manager = APIKeyManager(api_key_storage_path)
    
    # Reinitialize audit logger with custom configuration
    if audit_log_path or enable_console_logging:
        security_audit_logger = SecurityAuditLogger(
            log_file_path=audit_log_path,
            enable_console=enable_console_logging
        )

# Security status check function
def get_security_status() -> dict:
    """
    Get comprehensive security status and configuration.
    
    Returns:
        Dict with security infrastructure status and statistics
    """
    # Get API key statistics
    active_keys = api_key_manager.list_active_keys()
    
    # Get role configuration
    role_info = role_manager.get_role_hierarchy_info()
    
    # Get recent security events
    security_summary = get_security_summary(hours=24)
    
    return {
        "security_framework": {
            "authentication": "enabled",
            "authorization": "enabled", 
            "input_validation": "enabled",
            "audit_logging": "enabled"
        },
        "api_keys": {
            "active_count": len(active_keys),
            "total_usage": sum(key.get("usage_count", 0) for key in active_keys)
        },
        "roles": {
            "available_roles": list(role_info.keys()),
            "total_permissions": len(Permission),
            "role_hierarchy": role_info
        },
        "security_events": security_summary,
        "components": {
            "api_key_manager": type(api_key_manager).__name__,
            "role_manager": type(role_manager).__name__,
            "audit_logger": type(security_audit_logger).__name__
        }
    }

# Export all components for easy access
__all__ = [
    # Authentication
    'APIKeyManager', 'AuthenticationValidator', 'AuthenticationError',
    'api_key_manager', 'auth_validator', 'generate_api_key', 'validate_api_key', 'require_auth',
    
    # Authorization  
    'Permission', 'Role', 'RoleManager', 'UserRoleManager', 'AuthorizationValidator', 'AuthorizationError',
    'role_manager', 'user_role_manager', 'authz_validator', 'require_permission', 'require_role', 'has_permission',
    
    # Input Validation
    'XSSValidator', 'PathValidator', 'ParameterValidator', 'ValidationError',
    'xss_validator', 'path_validator', 'parameter_validator',
    'validate_string_input', 'validate_file_path', 'validate_task_id', 'is_safe_input',
    
    # Security Logging
    'SecurityEventType', 'SecurityLevel', 'SecurityAuditLogger', 'security_audit_logger',
    'log_auth_success', 'log_auth_failure', 'log_authz_failure', 'log_xss_attempt', 'log_path_traversal', 'get_security_summary',
    
    # Error Sanitization
    'ErrorCategory', 'SafeErrorResponse', 'ErrorSanitizer', 'error_sanitizer',
    'sanitize_error', 'safe_error_response', 'mcp_error_response', 'sanitize_handler_errors',
    
    # Combined Components
    'secure_mcp_handler', 'initialize_security', 'get_security_status'
]