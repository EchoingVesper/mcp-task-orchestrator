"""
Security Validator for Template System

Provides comprehensive security validation for JSON5 templates to prevent
injection attacks, resource exhaustion, and other security vulnerabilities.
"""

import re
import logging
from typing import Dict, Any, List, Set, Optional, Union
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class SecurityValidationError(Exception):
    """Raised when security validation fails."""
    pass


class TemplateSecurityValidator:
    """
    Comprehensive security validator for JSON5 templates.
    
    Security checks include:
    - Command injection prevention
    - Path traversal prevention  
    - Resource limits enforcement
    - Dangerous pattern detection
    - Content sanitization
    """
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            # Command injection patterns
            r'[;&|`$(){}[\]<>]',  # Shell metacharacters
            r'eval\s*\(',          # eval function calls
            r'exec\s*\(',          # exec function calls
            r'system\s*\(',        # system function calls
            r'subprocess',         # subprocess imports
            r'os\.system',         # os.system calls
            r'__import__',         # dynamic imports
            
            # Path traversal patterns
            r'\.\./.*',            # Directory traversal
            r'/etc/',              # System directories
            r'/root/',             # Root directory
            r'~/',                 # Home directory expansion
            r'%[A-Z_]+%',          # Environment variables (Windows)
            r'\$[A-Z_]+',          # Environment variables (Unix)
            
            # Network/URL patterns
            r'https?://',          # HTTP URLs
            r'ftp://',             # FTP URLs
            r'file://',            # File URLs
            
            # Dangerous file extensions
            r'\.(?:exe|bat|cmd|ps1|sh|bash|zsh)$',  # Executable files
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns]
        
        # Security limits
        self.max_string_length = 10000
        self.max_array_size = 1000
        self.max_object_keys = 500
        self.max_nesting_depth = 20
        self.max_template_size = 100000  # 100KB
        
        # Allowed file extensions for templates
        self.allowed_extensions = {'.json5', '.json'}
        
    def validate_template(self, template: Dict[str, Any]) -> None:
        """
        Perform comprehensive security validation on a template.
        
        Args:
            template: Template dictionary to validate
            
        Raises:
            SecurityValidationError: If security validation fails
        """
        # Structure and size validation
        self._validate_structure_security(template)
        
        # Content security validation
        self._validate_content_security(template)
        
        # Template-specific security validation
        self._validate_template_security(template)
        
        logger.debug("Template passed security validation")
    
    def validate_file_path(self, file_path: Union[str, Path]) -> None:
        """
        Validate file path for security.
        
        Args:
            file_path: Path to validate
            
        Raises:
            SecurityValidationError: If path is unsafe
        """
        path = Path(file_path)
        
        # Check file extension
        if path.suffix not in self.allowed_extensions:
            raise SecurityValidationError(f"Disallowed file extension: {path.suffix}")
        
        # Check for path traversal
        try:
            resolved_path = path.resolve()
            # Ensure path doesn't escape expected directories
            if '..' in str(resolved_path):
                raise SecurityValidationError(f"Path traversal detected: {file_path}")
        except (OSError, ValueError) as e:
            raise SecurityValidationError(f"Invalid file path: {file_path} ({e})")
        
        # Check path components for dangerous patterns
        for part in path.parts:
            if self._contains_dangerous_patterns(part):
                raise SecurityValidationError(f"Dangerous pattern in path: {part}")
    
    def sanitize_string(self, value: str) -> str:
        """
        Sanitize string value for security.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        sanitized = value.replace('\x00', '')
        
        # Limit length
        if len(sanitized) > self.max_string_length:
            sanitized = sanitized[:self.max_string_length]
            logger.warning(f"String truncated to {self.max_string_length} characters")
        
        # In strict mode, remove dangerous patterns
        if self.strict_mode:
            for pattern in self.compiled_patterns:
                if pattern.search(sanitized):
                    sanitized = pattern.sub('', sanitized)
                    logger.warning("Removed dangerous pattern from string")
        
        return sanitized
    
    def validate_parameter_value(self, param_name: str, value: Any) -> None:
        """
        Validate parameter value for security.
        
        Args:
            param_name: Parameter name
            value: Parameter value
            
        Raises:
            SecurityValidationError: If parameter value is unsafe
        """
        # Check parameter name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param_name):
            raise SecurityValidationError(f"Invalid parameter name: {param_name}")
        
        # Validate value content
        if isinstance(value, str):
            if self._contains_dangerous_patterns(value):
                raise SecurityValidationError(f"Parameter {param_name} contains dangerous patterns")
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str) and self._contains_dangerous_patterns(item):
                    raise SecurityValidationError(f"Parameter {param_name} array contains dangerous patterns")
        elif isinstance(value, dict):
            for key, val in value.items():
                if isinstance(key, str) and self._contains_dangerous_patterns(key):
                    raise SecurityValidationError(f"Parameter {param_name} object key contains dangerous patterns")
                if isinstance(val, str) and self._contains_dangerous_patterns(val):
                    raise SecurityValidationError(f"Parameter {param_name} object value contains dangerous patterns")
    
    def generate_content_hash(self, template: Dict[str, Any]) -> str:
        """
        Generate secure hash of template content.
        
        Args:
            template: Template to hash
            
        Returns:
            SHA-256 hex digest of template content
        """
        # Convert template to deterministic string representation
        import json
        content_str = json.dumps(template, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA-256 hash
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def _validate_structure_security(self, data: Any, depth: int = 0) -> None:
        """Validate data structure for security limits."""
        if depth > self.max_nesting_depth:
            raise SecurityValidationError(f"Nesting depth exceeds limit: {self.max_nesting_depth}")
        
        if isinstance(data, dict):
            if len(data) > self.max_object_keys:
                raise SecurityValidationError(f"Object has too many keys: {len(data)} > {self.max_object_keys}")
            
            for key, value in data.items():
                if not isinstance(key, str):
                    raise SecurityValidationError(f"Object key must be string, got {type(key)}")
                
                if len(key) > 1000:
                    raise SecurityValidationError(f"Object key too long: {len(key)} characters")
                
                if self._contains_dangerous_patterns(key):
                    raise SecurityValidationError(f"Object key contains dangerous patterns: {key}")
                
                self._validate_structure_security(value, depth + 1)
        
        elif isinstance(data, list):
            if len(data) > self.max_array_size:
                raise SecurityValidationError(f"Array too large: {len(data)} > {self.max_array_size}")
            
            for item in data:
                self._validate_structure_security(item, depth + 1)
        
        elif isinstance(data, str):
            if len(data) > self.max_string_length:
                raise SecurityValidationError(f"String too long: {len(data)} > {self.max_string_length}")
    
    def _validate_content_security(self, data: Any) -> None:
        """Validate content for dangerous patterns."""
        if isinstance(data, str):
            if self._contains_dangerous_patterns(data):
                raise SecurityValidationError(f"Content contains dangerous patterns: {data[:100]}...")
        
        elif isinstance(data, dict):
            for key, value in data.items():
                if self._contains_dangerous_patterns(key):
                    raise SecurityValidationError(f"Dictionary key contains dangerous patterns: {key}")
                self._validate_content_security(value)
        
        elif isinstance(data, list):
            for item in data:
                self._validate_content_security(item)
    
    def _validate_template_security(self, template: Dict[str, Any]) -> None:
        """Validate template-specific security requirements."""
        # Check template size
        template_str = str(template)
        if len(template_str) > self.max_template_size:
            raise SecurityValidationError(f"Template too large: {len(template_str)} > {self.max_template_size}")
        
        # Validate metadata
        metadata = template.get('metadata', {})
        
        # Check for suspicious metadata
        suspicious_metadata = ['script', 'command', 'executable', 'shell']
        for key in metadata:
            if any(term in key.lower() for term in suspicious_metadata):
                raise SecurityValidationError(f"Suspicious metadata key: {key}")
        
        # Validate task definitions
        tasks = template.get('tasks', {})
        for task_id, task_def in tasks.items():
            self._validate_task_security(task_id, task_def)
        
        # Validate parameter definitions
        parameters = template.get('parameters', {})
        for param_name, param_def in parameters.items():
            self._validate_parameter_definition_security(param_name, param_def)
    
    def _validate_task_security(self, task_id: str, task_def: Dict[str, Any]) -> None:
        """Validate individual task definition for security."""
        # Check task ID
        if not re.match(r'^[a-zA-Z0-9_-]+$', task_id):
            raise SecurityValidationError(f"Invalid task ID: {task_id}")
        
        # Check for suspicious task properties
        suspicious_props = ['command', 'script', 'executable', 'shell']
        for prop in suspicious_props:
            if prop in task_def:
                raise SecurityValidationError(f"Suspicious task property: {prop}")
        
        # Validate task type
        task_type = task_def.get('type', 'standard')
        allowed_types = ['standard', 'breakdown', 'milestone', 'review', 'approval', 
                        'research', 'implementation', 'testing', 'documentation', 'deployment']
        if task_type not in allowed_types:
            raise SecurityValidationError(f"Invalid task type: {task_type}")
        
        # Validate specialist type
        specialist_type = task_def.get('specialist_type')
        if specialist_type:
            allowed_specialists = ['analyst', 'coder', 'tester', 'documenter', 'reviewer', 
                                 'architect', 'devops', 'researcher', 'coordinator', 'generic']
            if specialist_type not in allowed_specialists:
                raise SecurityValidationError(f"Invalid specialist type: {specialist_type}")
    
    def _validate_parameter_definition_security(self, param_name: str, param_def: Any) -> None:
        """Validate parameter definition for security."""
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param_name):
            raise SecurityValidationError(f"Invalid parameter name: {param_name}")
        
        if isinstance(param_def, dict):
            # Check parameter type
            param_type = param_def.get('type', 'string')
            allowed_types = ['string', 'number', 'boolean', 'array', 'object']
            if param_type not in allowed_types:
                raise SecurityValidationError(f"Invalid parameter type: {param_type}")
            
            # Check validation pattern
            pattern = param_def.get('pattern')
            if pattern:
                try:
                    re.compile(pattern)
                except re.error as e:
                    raise SecurityValidationError(f"Invalid regex pattern for parameter {param_name}: {e}")
                
                # Check for dangerous regex patterns
                dangerous_regex = [r'\.\*', r'\.\+', r'\{.*,.*\}']  # Potential ReDoS patterns
                for dangerous in dangerous_regex:
                    if re.search(dangerous, pattern):
                        logger.warning(f"Potentially dangerous regex pattern in parameter {param_name}: {pattern}")
    
    def _contains_dangerous_patterns(self, text: str) -> bool:
        """Check if text contains any dangerous patterns."""
        if not isinstance(text, str):
            return False
        
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        
        return False