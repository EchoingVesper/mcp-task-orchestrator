
# Security Patterns

**Purpose**: Essential security patterns for MCP Task Orchestrator development, focusing on input validation, secure error handling, authentication patterns, and security-first design principles.

#
# Core Security Principles

#
## Security-First Design Philosophy

- **Defense in Depth**: Multiple layers of security controls

- **Principle of Least Privilege**: Grant minimum necessary permissions

- **Fail Securely**: Failures should default to secure state

- **Input Validation**: Validate all inputs at system boundaries

- **Information Disclosure Prevention**: Never leak sensitive information in errors

- **Secure Defaults**: System should be secure by default

#
# Input Validation Patterns

#
## Pattern: Pydantic Schema Validation

```python

# PATTERN: Comprehensive input validation with Pydantic v2

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, Literal
import re

class TaskCreationRequest(BaseModel):
    """Secure task creation request with comprehensive validation."""
    
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Task title (1-255 characters)"
    )
    
    description: str = Field(
        ..., 
        min_length=1,
        max_length=2000,
        description="Task description (1-2000 characters)"
    )
    
    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Task priority level"
    )
    
    due_date: Optional[str] = Field(
        None,
        regex=r"^\d{4}-\d{2}-\d{2}$",
        description="Due date in YYYY-MM-DD format"
    )
    
    tags: List[str] = Field(
        default=[],
        max_items=10,
        description="Task tags (max 10)"
    )
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title for security issues."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        
        
# SECURITY: Basic XSS prevention
        dangerous_patterns = [
            '<script', '</script>', '<iframe', 'javascript:', 'data:', 'vbscript:',
            'onload=', 'onerror=', 'onclick=', '<object', '<embed'
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError('Title contains potentially dangerous content')
        
        
# SECURITY: Prevent path traversal
        if '../' in v or '..\\' in v:
            raise ValueError('Title contains invalid path characters')
        
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description for security and content."""
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        
        
# SECURITY: Length check to prevent DoS
        if len(v.strip()) > 2000:
            raise ValueError('Description too long')
        
        
# SECURITY: Basic content validation
        if v.count('\n') > 100:  
# Prevent excessive newlines
            raise ValueError('Description has too many line breaks')
        
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags for security."""
        if not isinstance(v, list):
            raise ValueError('Tags must be a list')
        
        validated_tags = []
        for tag in v:
            if not isinstance(tag, str):
                raise ValueError('All tags must be strings')
            
            tag = tag.strip()
            if not tag:
                continue  
# Skip empty tags
            
            
# SECURITY: Tag length and character validation
            if len(tag) > 50:
                raise ValueError('Tag too long (max 50 characters)')
            
            
# SECURITY: Only allow alphanumeric, dash, underscore
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
                raise ValueError('Tag contains invalid characters')
            
            validated_tags.append(tag)
        
        return validated_tags
    
    @root_validator
    def validate_combination(cls, values):
        """Validate field combinations."""
        title = values.get('title', '')
        description = values.get('description', '')
        
        
# SECURITY: Ensure title and description aren't identical (potential spam)
        if title and description and title.strip() == description.strip():
            raise ValueError('Title and description cannot be identical')
        
        return values

    class Config:
        
# SECURITY: Strict validation mode
        extra = 'forbid'  
# Reject unknown fields
        str_strip_whitespace = True  
# Auto-strip whitespace
        validate_assignment = True  
# Validate on assignment

```text

#
## Pattern: File Path Validation

```text
python

# PATTERN: Secure file path validation

from pathlib import Path
import os

class SecureFileValidator:
    """Validator for file paths with security checks."""
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_base_dirs: List[str]) -> Path:
        """Validate file path for security issues."""
        if not file_path:
            raise ValueError("File path cannot be empty")
        
        try:
            
# SECURITY: Resolve path to prevent traversal attacks
            resolved_path = Path(file_path).resolve()
            
            
# SECURITY: Check for path traversal attempts
            if '..' in file_path or '~' in file_path:
                raise ValueError("Path traversal not allowed")
            
            
# SECURITY: Ensure path is within allowed directories
            allowed = False
            for base_dir in allowed_base_dirs:
                base_path = Path(base_dir).resolve()
                try:
                    resolved_path.relative_to(base_path)
                    allowed = True
                    break
                except ValueError:
                    continue
            
            if not allowed:
                raise ValueError("File path not in allowed directories")
            
            
# SECURITY: Check file size limits (if file exists)
            if resolved_path.exists() and resolved_path.is_file():
                file_size = resolved_path.stat().st_size
                max_size = 10 * 1024 * 1024  
# 10MB limit
                if file_size > max_size:
                    raise ValueError("File too large")
            
            return resolved_path
            
        except OSError as e:
            raise ValueError(f"Invalid file path: {e}")

# USAGE: Validate file paths in handlers

async def handle_file_operation(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle file operations with path validation."""
    try:
        file_path = arguments.get('file_path')
        allowed_dirs = [os.getcwd(), '/tmp']  
# Define allowed directories
        
        validated_path = SecureFileValidator.validate_file_path(file_path, allowed_dirs)
        
        
# Proceed with file operation using validated path
        result = await process_file(validated_path)
        
        return [types.TextContent(type="text", text=json.dumps(result))]
        
    except ValueError as e:
        raise McpError(-32602, f"Invalid file path: {e}")

```text

#
# Authentication and Authorization Patterns

#
## Pattern: API Key Validation

```text
python

# PATTERN: Secure API key validation

import secrets
import hashlib
from typing import Optional

class APIKeyManager:
    """Manages API key validation and security."""
    
    def __init__(self):
        self._valid_keys: Dict[str, Dict[str, Any]] = {}
    
    def generate_api_key(self, user_id: str, permissions: List[str]) -> str:
        """Generate a secure API key."""
        
# SECURITY: Use cryptographically secure random generator
        raw_key = secrets.token_urlsafe(32)
        
        
# SECURITY: Store hash, not plaintext
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        self._valid_keys[key_hash] = {
            'user_id': user_id,
            'permissions': permissions,
            'created_at': datetime.utcnow(),
            'last_used': None
        }
        
        return raw_key
    
    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key and return user info."""
        if not api_key:
            return None
        
        
# SECURITY: Hash provided key for comparison
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        key_info = self._valid_keys.get(key_hash)
        if not key_info:
            return None
        
        
# SECURITY: Update last used timestamp
        key_info['last_used'] = datetime.utcnow()
        
        return key_info
    
    def check_permission(self, api_key: str, required_permission: str) -> bool:
        """Check if API key has required permission."""
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return False
        
        permissions = key_info.get('permissions', [])
        return required_permission in permissions or 'admin' in permissions

# PATTERN: MCP handler with authentication

async def authenticated_handler(
    handler_func: Callable, 
    required_permission: str
) -> Callable:
    """Decorator for authenticated MCP handlers."""
    
    async def wrapper(arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Wrapper with authentication check."""
        
        
# SECURITY: Extract API key from arguments
        api_key = arguments.get('api_key')
        if not api_key:
            raise McpError(-32602, "API key required")
        
        
# SECURITY: Validate API key and permissions
        api_manager = APIKeyManager()
        if not api_manager.check_permission(api_key, required_permission):
            raise McpError(-32603, "Access denied")
        
        
# SECURITY: Remove API key from arguments before processing
        clean_arguments = {k: v for k, v in arguments.items() if k != 'api_key'}
        
        return await handler_func(clean_arguments)
    
    return wrapper

```text

#
## Pattern: Role-Based Access Control

```text
python

# PATTERN: Role-based access control system

from enum import Enum
from typing import Set

class Role(Enum):
    """System roles with hierarchical permissions."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    READONLY = "readonly"

class Permission(Enum):
    """System permissions."""
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    VIEW_TASK = "view_task"
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIG = "system_config"

class RoleManager:
    """Manages role-based permissions."""
    
    
# SECURITY: Define role hierarchy and permissions
    ROLE_PERMISSIONS = {
        Role.ADMIN: {
            Permission.CREATE_TASK, Permission.UPDATE_TASK, Permission.DELETE_TASK,
            Permission.VIEW_TASK, Permission.MANAGE_USERS, Permission.SYSTEM_CONFIG
        },
        Role.MANAGER: {
            Permission.CREATE_TASK, Permission.UPDATE_TASK, Permission.DELETE_TASK,
            Permission.VIEW_TASK
        },
        Role.USER: {
            Permission.CREATE_TASK, Permission.UPDATE_TASK, Permission.VIEW_TASK
        },
        Role.READONLY: {
            Permission.VIEW_TASK
        }
    }
    
    @classmethod
    def has_permission(cls, user_role: Role, required_permission: Permission) -> bool:
        """Check if role has required permission."""
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in role_permissions
    
    @classmethod
    def get_user_permissions(cls, user_role: Role) -> Set[Permission]:
        """Get all permissions for a role."""
        return cls.ROLE_PERMISSIONS.get(user_role, set())

# PATTERN: Authorization decorator

def requires_permission(permission: Permission):
    """Decorator to require specific permission for handler."""
    
    def decorator(handler_func):
        async def wrapper(arguments: Dict[str, Any]) -> List[types.TextContent]:
            
# SECURITY: Get user context (from session, API key, etc.)
            user_context = await get_user_context(arguments)
            
            if not user_context:
                raise McpError(-32603, "Authentication required")
            
            user_role = Role(user_context.get('role'))
            
            
# SECURITY: Check authorization
            if not RoleManager.has_permission(user_role, permission):
                raise McpError(-32603, f"Permission denied: {permission.value}")
            
            return await handler_func(arguments)
        
        return wrapper
    return decorator

# USAGE: Protect handlers with permissions

@requires_permission(Permission.CREATE_TASK)
async def handle_create_task(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Create task handler with permission check."""
    
# Handler implementation here
    pass

```text

#
# Secure Error Handling Patterns

#
## Pattern: Error Sanitization

```text
python

# PATTERN: Secure error handling that prevents information disclosure

import logging
from typing import Any, Dict

class SecurityError(Exception):
    """Security-related error."""
    pass

class ErrorSanitizer:
    """Sanitizes errors for client consumption."""
    
    
# SECURITY: Map internal errors to safe messages
    ERROR_MAPPINGS = {
        FileNotFoundError: "Resource not found",
        PermissionError: "Access denied",
        ValueError: "Invalid input provided",
        IntegrityError: "Data conflict occurred",
        ConnectionError: "Service temporarily unavailable",
        TimeoutError: "Operation timed out",
    }
    
    @classmethod
    def sanitize_error(cls, error: Exception, context: str = "") -> str:
        """Convert internal error to safe client message."""
        
        
# SECURITY: Log full error details internally
        logger.error(f"Error in {context}: {type(error).__name__}: {error}")
        
        
# SECURITY: Return sanitized message to client
        error_type = type(error)
        safe_message = cls.ERROR_MAPPINGS.get(error_type, "Internal error")
        
        
# SECURITY: Additional sanitization for specific cases
        if isinstance(error, ValueError):
            error_str = str(error).lower()
            if any(keyword in error_str for keyword in ['sql', 'database', 'connection']):
                safe_message = "Invalid request"
            elif 'path' in error_str or 'file' in error_str:
                safe_message = "Invalid resource path"
        
        return safe_message
    
    @classmethod
    def create_safe_response(cls, error: Exception, context: str = "") -> Dict[str, Any]:
        """Create safe error response for MCP."""
        safe_message = cls.sanitize_error(error, context)
        
        return {
            "success": False,
            "error": safe_message,
            "timestamp": datetime.utcnow().isoformat()
        }

# PATTERN: Secure MCP error handler

async def secure_mcp_handler(handler_func: Callable, tool_name: str):
    """Wrapper for secure MCP tool handling."""
    
    async def wrapper(arguments: Dict[str, Any]) -> List[types.TextContent]:
        try:
            
# SECURITY: Input validation first
            validated_args = await validate_mcp_input(arguments, tool_name)
            
            
# Execute handler with validated input
            result = await handler_func(validated_args)
            
            return result
            
        except SecurityError as e:
            
# SECURITY: Security errors are logged but not detailed to client
            logger.warning(f"Security violation in {tool_name}: {e}")
            raise McpError(-32603, "Security policy violation")
            
        except ValidationError as e:
            
# SECURITY: Validation errors are safe to return
            raise McpError(-32602, f"Invalid input: {e}")
            
        except Exception as e:
            
# SECURITY: All other errors are sanitized
            safe_response = ErrorSanitizer.create_safe_response(e, tool_name)
            raise McpError(-32603, safe_response["error"])
    
    return wrapper

```text

#
## Pattern: Audit Logging

```text
python

# PATTERN: Security audit logging

import logging
from typing import Optional, Dict, Any
from datetime import datetime

class SecurityAuditor:
    """Handles security audit logging."""
    
    def __init__(self):
        
# SECURITY: Separate logger for security events
        self.audit_logger = logging.getLogger('security_audit')
        
        
# SECURITY: Configure secure logging (file only, not console)
        if not self.audit_logger.handlers:
            handler = logging.FileHandler('security_audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
            self.audit_logger.setLevel(logging.INFO)
    
    def log_authentication_attempt(self, user_id: str, success: bool, 
                                 ip_address: Optional[str] = None):
        """Log authentication attempts."""
        status = "SUCCESS" if success else "FAILURE"
        self.audit_logger.info(
            f"AUTH_ATTEMPT - User: {user_id} - Status: {status} - IP: {ip_address}"
        )
    
    def log_permission_check(self, user_id: str, permission: str, granted: bool):
        """Log permission checks."""
        status = "GRANTED" if granted else "DENIED"
        self.audit_logger.info(
            f"PERMISSION_CHECK - User: {user_id} - Permission: {permission} - Status: {status}"
        )
    
    def log_data_access(self, user_id: str, resource: str, action: str):
        """Log data access events."""
        self.audit_logger.info(
            f"DATA_ACCESS - User: {user_id} - Resource: {resource} - Action: {action}"
        )
    
    def log_security_violation(self, user_id: str, violation_type: str, details: str):
        """Log security violations."""
        self.audit_logger.warning(
            f"SECURITY_VIOLATION - User: {user_id} - Type: {violation_type} - Details: {details}"
        )

# PATTERN: Audit logging decorator

def audit_access(resource: str, action: str):
    """Decorator to audit resource access."""
    
    def decorator(handler_func):
        async def wrapper(arguments: Dict[str, Any]) -> List[types.TextContent]:
            user_context = await get_user_context(arguments)
            user_id = user_context.get('user_id', 'unknown') if user_context else 'anonymous'
            
            auditor = SecurityAuditor()
            
            try:
                
# SECURITY: Log access attempt
                auditor.log_data_access(user_id, resource, action)
                
                result = await handler_func(arguments)
                
                return result
                
            except Exception as e:
                
# SECURITY: Log failed access
                auditor.log_security_violation(
                    user_id, 
                    "ACCESS_FAILURE", 
                    f"{action} on {resource} failed: {type(e).__name__}"
                )
                raise
        
        return wrapper
    return decorator

```text

#
# Data Protection Patterns

#
## Pattern: Sensitive Data Handling

```text
python

# PATTERN: Secure handling of sensitive data

import hashlib
import secrets
from cryptography.fernet import Fernet
from typing import Optional

class DataProtector:
    """Handles encryption and protection of sensitive data."""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """Initialize with encryption key."""
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            
# SECURITY: Generate key if not provided (for testing only)
            self.cipher = Fernet(Fernet.generate_key())
    
    def hash_sensitive_data(self, data: str) -> str:
        """Create one-way hash of sensitive data."""
        
# SECURITY: Use strong hashing with salt
        salt = secrets.token_bytes(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', data.encode(), salt, 100000)
        return salt.hex() + hash_obj.hex()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def mask_sensitive_data(self, data: str, visible_chars: int = 4) -> str:
        """Mask sensitive data for logging/display."""
        if not data or len(data) <= visible_chars:
            return '*' * len(data) if data else ''
        
        return data[:visible_chars] + '*' * (len(data) - visible_chars)

# PATTERN: Secure data model with protection

class SecureTaskModel(BaseModel):
    """Task model with built-in data protection."""
    
    task_id: str
    title: str
    description: str
    sensitive_notes: Optional[str] = None  
# Will be encrypted
    
    class Config:
        
# SECURITY: Custom serialization for sensitive fields
        json_encoders = {
            str: lambda v: DataProtector().mask_sensitive_data(v) if 'sensitive' in str(v) else v
        }
    
    def encrypt_sensitive_fields(self, protector: DataProtector):
        """Encrypt sensitive fields before storage."""
        if self.sensitive_notes:
            self.sensitive_notes = protector.encrypt_data(self.sensitive_notes)
    
    def decrypt_sensitive_fields(self, protector: DataProtector):
        """Decrypt sensitive fields after retrieval."""
        if self.sensitive_notes:
            self.sensitive_notes = protector.decrypt_data(self.sensitive_notes)

```text

#
# Rate Limiting and DoS Protection

#
## Pattern: Rate Limiting

```text
python

# PATTERN: Rate limiting to prevent abuse

import time
from collections import defaultdict, deque
from typing import Dict, Tuple

class RateLimiter:
    """Implements token bucket rate limiting."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """Check if request is allowed.
        
        Returns:
            Tuple of (allowed, requests_remaining)
        """
        now = time.time()
        cutoff = now - self.time_window
        
        
# SECURITY: Clean old requests
        request_times = self.requests[identifier]
        while request_times and request_times[0] < cutoff:
            request_times.popleft()
        
        
# SECURITY: Check rate limit
        if len(request_times) >= self.max_requests:
            return False, 0
        
        
# SECURITY: Record new request
        request_times.append(now)
        remaining = self.max_requests - len(request_times)
        
        return True, remaining
    
    def get_reset_time(self, identifier: str) -> int:
        """Get time until rate limit resets."""
        request_times = self.requests[identifier]
        if not request_times:
            return 0
        
        oldest_request = request_times[0]
        reset_time = oldest_request + self.time_window
        return max(0, int(reset_time - time.time()))

# PATTERN: MCP handler with rate limiting

def rate_limited(max_requests: int = 100, time_window: int = 60):
    """Decorator for rate-limited MCP handlers."""
    limiter = RateLimiter(max_requests, time_window)
    
    def decorator(handler_func):
        async def wrapper(arguments: Dict[str, Any]) -> List[types.TextContent]:
            
# SECURITY: Identify client (use API key, IP, or user ID)
            client_id = await get_client_identifier(arguments)
            
            allowed, remaining = limiter.is_allowed(client_id)
            
            if not allowed:
                reset_time = limiter.get_reset_time(client_id)
                raise McpError(
                    -32603, 
                    f"Rate limit exceeded. Try again in {reset_time} seconds"
                )
            
            
# SECURITY: Add rate limit headers to response
            result = await handler_func(arguments)
            
            
# Note: MCP doesn't support headers, but we could include in response
            return result
        
        return wrapper
    return decorator

```text

#
# Security Testing Patterns

#
## Pattern: Security Test Suite

```text
python

# PATTERN: Comprehensive security testing

import pytest
from unittest.mock import patch, AsyncMock

class SecurityTestSuite:
    """Security-focused test cases."""
    
    @pytest.mark.asyncio
    async def test_input_validation_xss_prevention(self):
        """Test XSS attack prevention."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>",
            "onload=alert('xss')",
            "<object data='javascript:alert(1)'></object>"
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(ValidationError):
                TaskCreationRequest(
                    title=malicious_input,
                    description="Valid description"
                )
    
    @pytest.mark.asyncio
    async def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "~/.ssh/id_rsa",
            "file://../../sensitive_file"
        ]
        
        for malicious_path in malicious_paths:
            with pytest.raises(ValueError):
                SecureFileValidator.validate_file_path(
                    malicious_path, 
                    ["/tmp", "/allowed"]
                )
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        limiter = RateLimiter(max_requests=3, time_window=60)
        client_id = "test_client"
        
        
# SECURITY: First 3 requests should be allowed
        for i in range(3):
            allowed, remaining = limiter.is_allowed(client_id)
            assert allowed is True
            assert remaining == 2 - i
        
        
# SECURITY: 4th request should be denied
        allowed, remaining = limiter.is_allowed(client_id)
        assert allowed is False
        assert remaining == 0
    
    @pytest.mark.asyncio
    async def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information."""
        with patch('handler_func') as mock_handler:
            
# SECURITY: Simulate database error with sensitive info
            mock_handler.side_effect = Exception("Database error: user 'admin' password 'secret123'")
            
            try:
                await secure_mcp_handler(mock_handler, "test_tool")({})
            except McpError as e:
                
# SECURITY: Ensure sensitive info is not in error message
                assert "password" not in e.message.lower()
                assert "secret123" not in e.message
                assert "admin" not in e.message
                assert e.message == "Internal error"  
# Generic message

```text

#
# Common Security Gotchas

#
## Input Validation Issues

```text
python

# ❌ WRONG: Insufficient input validation

def unsafe_handler(title: str):
    
# No validation - vulnerable to XSS, injection, etc.
    return f"<h1>{title}</h1>"

# ✅ CORRECT: Comprehensive validation

def safe_handler(title: str):
    
# Validate with Pydantic schema
    request = TaskCreationRequest(title=title, description="desc")
    
# HTML escape output if needed
    import html
    return f"<h1>{html.escape(request.title)}</h1>"

# ❌ WRONG: Trusting file paths

def unsafe_file_handler(file_path: str):
    with open(file_path, 'r') as f:  
# Vulnerable to path traversal
        return f.read()

# ✅ CORRECT: Validating file paths

def safe_file_handler(file_path: str):
    validated_path = SecureFileValidator.validate_file_path(
        file_path, ["/allowed/directory"]
    )
    with open(validated_path, 'r') as f:
        return f.read()

```text

#
## Error Handling Security Issues

```text
python

# ❌ WRONG: Leaking sensitive information in errors

try:
    result = database.execute("SELECT * FROM users WHERE password = ?", [password])
except Exception as e:
    raise Exception(f"Query failed: {e}")  
# Might leak query/password

# ✅ CORRECT: Sanitized error handling

try:
    result = database.execute("SELECT * FROM users WHERE password = ?", [password])
except Exception as e:
    logger.error(f"Database query failed: {e}")  
# Log internally
    raise McpError(-32603, "Authentication failed")  
# Generic client message
```text

#
# Best Practices Summary

1. **Input Validation**: Validate all inputs with Pydantic schemas including security checks

2. **Path Security**: Always validate file paths and prevent traversal attacks

3. **Error Handling**: Sanitize all error messages to prevent information disclosure

4. **Authentication**: Implement proper authentication and authorization patterns

5. **Rate Limiting**: Protect against DoS attacks with rate limiting

6. **Audit Logging**: Log all security-relevant events for monitoring

7. **Data Protection**: Encrypt sensitive data and use secure hashing

8. **Testing**: Include comprehensive security tests in your test suite

#
# Related Documentation

- [MCP Protocol Patterns](./mcp-protocol-patterns.md)

- [Database Integration Patterns](./database-integration-patterns.md)

- [Context Engineering Guide](./context-engineering-guide.md)

- [Validation Framework](../validation/validation-framework.md)
