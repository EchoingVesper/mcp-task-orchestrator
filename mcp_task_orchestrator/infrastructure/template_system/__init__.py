"""
JSON5 Template System Infrastructure

This module provides the infrastructure layer for the JSON5-based template system,
implementing parsing, validation, storage, and parameter substitution with security controls.
"""

__version__ = "1.0.0"

from .json5_parser import JSON5Parser, JSON5ValidationError
from .template_engine import TemplateEngine, TemplateValidationError, ParameterSubstitutionError
from .storage_manager import TemplateStorageManager, TemplateStorageError
from .security_validator import TemplateSecurityValidator, SecurityValidationError

__all__ = [
    "JSON5Parser",
    "JSON5ValidationError", 
    "TemplateEngine",
    "TemplateValidationError",
    "ParameterSubstitutionError",
    "TemplateStorageManager",
    "TemplateStorageError",
    "TemplateSecurityValidator",
    "SecurityValidationError"
]