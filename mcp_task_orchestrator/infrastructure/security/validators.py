"""
Input Validation Framework for MCP Task Orchestrator

Implements comprehensive input validation with XSS prevention, injection protection,
and parameter sanitization. Follows security-first design principles.
"""

import logging
import re
import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urlparse
import uuid

# Configure security logging
security_logger = logging.getLogger("mcp_task_orchestrator.security.validation")


class XSSValidator:
    """
    Prevents Cross-Site Scripting (XSS) attacks through input validation.
    
    Detects and blocks dangerous patterns that could be used for script injection,
    HTML injection, and other client-side attack vectors.
    """
    
    # Dangerous patterns that indicate potential XSS attempts
    DANGEROUS_PATTERNS = [
        # Script tags and variations
        r'<script[^>]*>.*?</script>',
        r'<script[^>]*>',
        r'</script>',
        r'javascript:',
        r'vbscript:',
        r'data:text/html',
        
        # Event handlers
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'onfocus\s*=',
        r'onblur\s*=',
        r'onchange\s*=',
        r'onsubmit\s*=',
        
        # HTML tags that can execute scripts
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<form[^>]*>',
        r'<meta[^>]*>',
        r'<link[^>]*>',
        
        # CSS injection patterns
        r'expression\s*\(',
        r'@import',
        r'behavior\s*:',
        
        # Common payload patterns
        r'alert\s*\(',
        r'confirm\s*\(',
        r'prompt\s*\(',
        r'eval\s*\(',
        r'Function\s*\(',
        r'setTimeout\s*\(',
        r'setInterval\s*\(',
        
        # Data URI schemes
        r'data:[^;]*;base64',
        
        # Special characters used in attacks
        r'&#x[0-9a-fA-F]+;',  # Hex encoded
        r'&#[0-9]+;',          # Decimal encoded
    ]
    
    def __init__(self):
        """Initialize XSS validator with compiled patterns."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL) 
            for pattern in self.DANGEROUS_PATTERNS
        ]
    
    def validate_input(self, value: str, field_name: str = "input") -> str:
        """
        Validate input for XSS patterns and return sanitized value.
        
        Args:
            value: Input string to validate
            field_name: Name of the field for logging
            
        Returns:
            str: Sanitized input value
            
        Raises:
            ValidationError: If dangerous patterns are detected
        """
        if not isinstance(value, str):
            return str(value)
        
        original_value = value
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(value):
                security_logger.warning(
                    f"XSS attempt detected in field '{field_name}': pattern matched"
                )
                raise ValidationError(
                    f"Potentially malicious content detected in {field_name}",
                    error_code="XSS_DETECTED"
                )
        
        # HTML entity encode as additional protection
        sanitized_value = html.escape(value, quote=True)
        
        # Log if sanitization changed the input
        if sanitized_value != original_value:
            security_logger.info(
                f"Input sanitized in field '{field_name}': HTML entities encoded"
            )
        
        return sanitized_value
    
    def is_safe_html(self, value: str) -> bool:
        """
        Check if HTML content is safe (no script execution).
        
        Args:
            value: HTML content to check
            
        Returns:
            bool: True if content appears safe
        """
        try:
            self.validate_input(value, "html_content")
            return True
        except ValidationError:
            return False


class PathValidator:
    """
    Prevents path traversal attacks and validates file system paths.
    
    Ensures that file operations remain within allowed directories
    and prevents directory traversal attacks via malicious paths.
    """
    
    # Dangerous path patterns
    DANGEROUS_PATH_PATTERNS = [
        r'\.\.',           # Parent directory traversal
        r'~/',             # Home directory access
        r'/etc/',          # System configuration access
        r'/usr/',          # System binaries access
        r'/var/',          # System variables access (except allowed)
        r'/root/',         # Root user directory
        r'\\',             # Windows path separators (normalize)
        r'\x00',           # Null byte injection
        r'\.\.\\',         # Windows parent traversal
        r'\.\./',          # Unix parent traversal
    ]
    
    def __init__(self):
        """Initialize path validator with compiled patterns."""
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.DANGEROUS_PATH_PATTERNS
        ]
    
    def validate_file_path(self, path: str, base_dir: Union[str, Path], 
                          field_name: str = "path") -> Path:
        """
        Validate file path and ensure it stays within base directory.
        
        Args:
            path: File path to validate
            base_dir: Base directory to restrict access to
            field_name: Name of the field for logging
            
        Returns:
            Path: Validated and resolved path
            
        Raises:
            ValidationError: If path is dangerous or outside base directory
        """
        if not isinstance(path, (str, Path)):
            raise ValidationError(f"Invalid path type in {field_name}")
        
        path_str = str(path)
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(path_str):
                security_logger.warning(
                    f"Path traversal attempt detected in field '{field_name}': {path_str}"
                )
                raise ValidationError(
                    f"Potentially dangerous path detected in {field_name}",
                    error_code="PATH_TRAVERSAL_DETECTED"
                )
        
        # Normalize and resolve paths
        base_path = Path(base_dir).resolve()
        try:
            target_path = (base_path / path).resolve()
        except Exception as e:
            security_logger.warning(f"Path resolution failed for {path_str}: {str(e)}")
            raise ValidationError(f"Invalid path format in {field_name}")
        
        # Ensure target path is within base directory
        try:
            target_path.relative_to(base_path)
        except ValueError:
            security_logger.warning(
                f"Path traversal attempt: {path_str} resolves outside base directory"
            )
            raise ValidationError(
                f"Path {field_name} is outside allowed directory",
                error_code="PATH_OUTSIDE_BASE"
            )
        
        return target_path
    
    def validate_directory_name(self, name: str, field_name: str = "directory") -> str:
        """
        Validate directory name for safety.
        
        Args:
            name: Directory name to validate
            field_name: Name of the field for logging
            
        Returns:
            str: Validated directory name
        """
        if not name or not isinstance(name, str):
            raise ValidationError(f"Invalid directory name in {field_name}")
        
        # Check for dangerous characters
        dangerous_chars = ['/', '\\', '..', '~', '\x00', '*', '?', '<', '>', '|', ':']
        if any(char in name for char in dangerous_chars):
            security_logger.warning(
                f"Dangerous characters in directory name '{field_name}': {name}"
            )
            raise ValidationError(f"Invalid characters in directory name {field_name}")
        
        # Length validation
        if len(name) > 255:
            raise ValidationError(f"Directory name {field_name} too long")
        
        return name


class ParameterValidator:
    """
    Validates parameters and prevents injection attacks.
    
    Provides comprehensive parameter validation including type checking,
    length limits, format validation, and injection prevention.
    """
    
    def __init__(self):
        """Initialize parameter validator."""
        self.xss_validator = XSSValidator()
        self.path_validator = PathValidator()
    
    def validate_string(self, value: Any, field_name: str, 
                       min_length: int = 0, max_length: int = 10000,
                       allow_empty: bool = True) -> str:
        """
        Validate string parameter with length and content checks.
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed
            
        Returns:
            str: Validated string
        """
        if value is None:
            if allow_empty:
                return ""
            else:
                raise ValidationError(f"Field {field_name} cannot be empty")
        
        if not isinstance(value, str):
            value = str(value)
        
        # Length validation
        if len(value) < min_length:
            raise ValidationError(
                f"Field {field_name} too short (minimum {min_length} characters)"
            )
        
        if len(value) > max_length:
            security_logger.warning(
                f"Field {field_name} exceeds maximum length: {len(value)} > {max_length}"
            )
            raise ValidationError(
                f"Field {field_name} too long (maximum {max_length} characters)"
            )
        
        # XSS validation
        validated_value = self.xss_validator.validate_input(value, field_name)
        
        return validated_value
    
    def validate_identifier(self, value: Any, field_name: str) -> str:
        """
        Validate identifier (task_id, session_id, etc.) for safety.
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            
        Returns:
            str: Validated identifier
        """
        if not value:
            raise ValidationError(f"Field {field_name} cannot be empty")
        
        value_str = str(value)
        
        # Check format (alphanumeric, hyphens, underscores only)
        if not re.match(r'^[a-zA-Z0-9_-]+$', value_str):
            security_logger.warning(
                f"Invalid identifier format in field '{field_name}': {value_str}"
            )
            raise ValidationError(
                f"Field {field_name} contains invalid characters"
            )
        
        # Length validation
        if len(value_str) > 100:
            raise ValidationError(f"Identifier {field_name} too long")
        
        return value_str
    
    def validate_uuid(self, value: Any, field_name: str) -> str:
        """
        Validate UUID format.
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            
        Returns:
            str: Validated UUID string
        """
        if not value:
            raise ValidationError(f"Field {field_name} cannot be empty")
        
        value_str = str(value)
        
        try:
            # This will raise ValueError if not a valid UUID
            uuid_obj = uuid.UUID(value_str)
            return str(uuid_obj)
        except ValueError:
            security_logger.warning(
                f"Invalid UUID format in field '{field_name}': {value_str}"
            )
            raise ValidationError(f"Field {field_name} is not a valid UUID")
    
    def validate_integer(self, value: Any, field_name: str,
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None) -> int:
        """
        Validate integer parameter with range checks.
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            int: Validated integer
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Field {field_name} must be an integer")
        
        if min_value is not None and int_value < min_value:
            raise ValidationError(
                f"Field {field_name} below minimum value ({min_value})"
            )
        
        if max_value is not None and int_value > max_value:
            raise ValidationError(
                f"Field {field_name} above maximum value ({max_value})"
            )
        
        return int_value
    
    def validate_json_safe(self, value: Any, field_name: str) -> Any:
        """
        Validate that value is JSON-safe (no function objects, etc.).
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            
        Returns:
            JSON-safe value
        """
        try:
            import json
            # This will raise an exception if not JSON serializable
            json.dumps(value)
            return value
        except (TypeError, ValueError) as e:
            security_logger.warning(
                f"Non-JSON-safe value in field '{field_name}': {str(e)}"
            )
            raise ValidationError(f"Field {field_name} contains non-serializable data")


class ValidationError(Exception):
    """Custom exception for validation failures."""
    
    def __init__(self, message: str, error_code: str = "VALIDATION_FAILED"):
        """Initialize validation error."""
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now(timezone.utc).isoformat()


# Global validator instances for easy import
xss_validator = XSSValidator()
path_validator = PathValidator()
parameter_validator = ParameterValidator()

# Convenience functions for common operations
def validate_string_input(value: str, field_name: str = "input", 
                         max_length: int = 1000) -> str:
    """Validate string input - convenience function."""
    return parameter_validator.validate_string(value, field_name, max_length=max_length)

def validate_file_path(path: str, base_dir: Union[str, Path], 
                      field_name: str = "path") -> Path:
    """Validate file path - convenience function."""
    return path_validator.validate_file_path(path, base_dir, field_name)

def validate_task_id(task_id: str) -> str:
    """Validate task ID - convenience function."""
    return parameter_validator.validate_identifier(task_id, "task_id")

def is_safe_input(value: str) -> bool:
    """Check if input is safe - convenience function."""
    try:
        xss_validator.validate_input(value)
        return True
    except ValidationError:
        return False