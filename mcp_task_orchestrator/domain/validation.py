"""
Domain-level validation functions.

Basic validation functions that belong in the domain layer to avoid 
circular dependencies with infrastructure.
"""

import re
from typing import Optional


class ValidationError(Exception):
    """Domain validation error."""
    pass


def validate_string_input(value: str, field_name: str = "input", 
                         max_length: int = 1000) -> str:
    """
    Basic string validation for domain entities.
    
    Args:
        value: String to validate
        field_name: Name of field for error messages
        max_length: Maximum allowed length
        
    Returns:
        Validated string
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds maximum length of {max_length}")
    
    # Basic sanitization - remove dangerous characters
    sanitized = re.sub(r'[<>&"]', '', value)
    return sanitized.strip()


def validate_task_id(task_id: str) -> str:
    """
    Validate task ID format.
    
    Args:
        task_id: Task identifier to validate
        
    Returns:
        Validated task ID
        
    Raises:
        ValidationError: If task ID format is invalid
    """
    if not isinstance(task_id, str):
        raise ValidationError("Task ID must be a string")
    
    if not task_id.strip():
        raise ValidationError("Task ID cannot be empty")
    
    # Basic UUID-like format check
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, task_id):
        raise ValidationError("Task ID contains invalid characters")
    
    if len(task_id) > 255:
        raise ValidationError("Task ID too long")
    
    return task_id.strip()