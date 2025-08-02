"""
Template Engine for JSON5 Task Templates

Provides parameter substitution, template inheritance, composition, and validation
with comprehensive security controls.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Set, Union
from dataclasses import dataclass
from pathlib import Path
import copy

from .json5_parser import JSON5Parser, JSON5ValidationError
from .security_validator import TemplateSecurityValidator, SecurityValidationError

logger = logging.getLogger(__name__)


class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass


class ParameterSubstitutionError(Exception):
    """Raised when parameter substitution fails."""
    pass


@dataclass
class TemplateParameter:
    """Definition of a template parameter."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation_pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None


@dataclass
class TemplateMetadata:
    """Metadata for a template."""
    name: str
    version: str
    description: str
    author: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    extends: Optional[str] = None  # Parent template ID
    requires: Optional[List[str]] = None  # Required template dependencies


class TemplateEngine:
    """
    JSON5 Template Engine with parameter substitution and inheritance.
    
    Features:
    - Parameter substitution with {{parameter}} syntax
    - Template inheritance and composition
    - Security validation
    - Type checking and validation
    - Circular dependency detection
    """
    
    def __init__(self, template_dir: Optional[Path] = None, security_validator: Optional[TemplateSecurityValidator] = None):
        self.template_dir = template_dir or Path.cwd() / ".task_orchestrator" / "templates"
        self.json5_parser = JSON5Parser()
        self.security_validator = security_validator or TemplateSecurityValidator()
        self._template_cache: Dict[str, Dict[str, Any]] = {}
        self._inheritance_chain: Set[str] = set()
        
    def load_template(self, template_id: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load a template by ID from storage.
        
        Args:
            template_id: Unique template identifier
            use_cache: Whether to use cached templates
            
        Returns:
            Template dictionary
            
        Raises:
            TemplateValidationError: If template cannot be loaded or is invalid
        """
        if use_cache and template_id in self._template_cache:
            return copy.deepcopy(self._template_cache[template_id])
            
        template_file = self.template_dir / f"{template_id}.json5"
        
        if not template_file.exists():
            raise TemplateValidationError(f"Template not found: {template_id}")
            
        try:
            template_data = self.json5_parser.parse_file(template_file)
            
            # Validate template structure
            self._validate_template_structure(template_data)
            
            # Security validation
            self.security_validator.validate_template(template_data)
            
            # Cache the template
            if use_cache:
                self._template_cache[template_id] = copy.deepcopy(template_data)
                
            return template_data
            
        except JSON5ValidationError as e:
            raise TemplateValidationError(f"Failed to parse template {template_id}: {e}")
        except SecurityValidationError as e:
            raise TemplateValidationError(f"Security validation failed for template {template_id}: {e}")
    
    def instantiate_template(self, template_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a template instance with parameter substitution.
        
        Args:
            template_id: Template to instantiate
            parameters: Parameter values for substitution
            
        Returns:
            Instantiated template with parameters substituted
            
        Raises:
            TemplateValidationError: If template is invalid
            ParameterSubstitutionError: If parameter substitution fails
        """
        # Reset inheritance chain tracking
        self._inheritance_chain.clear()
        
        # Load and resolve template (including inheritance)
        template = self._resolve_template_inheritance(template_id)
        
        # Extract parameter definitions
        param_definitions = self._extract_parameter_definitions(template)
        
        # Validate provided parameters
        validated_params = self._validate_parameters(param_definitions, parameters)
        
        # Perform parameter substitution
        instantiated = self._substitute_parameters(template, validated_params)
        
        # Final validation of instantiated template
        self._validate_instantiated_template(instantiated)
        
        return instantiated
    
    def validate_template_syntax(self, template_data: Dict[str, Any]) -> List[str]:
        """
        Validate template syntax and structure.
        
        Args:
            template_data: Template to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            self._validate_template_structure(template_data)
        except TemplateValidationError as e:
            errors.append(str(e))
            
        try:
            self.security_validator.validate_template(template_data)
        except SecurityValidationError as e:
            errors.append(f"Security validation: {e}")
            
        return errors
    
    def get_template_parameters(self, template_id: str) -> List[TemplateParameter]:
        """
        Get parameter definitions for a template.
        
        Args:
            template_id: Template to analyze
            
        Returns:
            List of parameter definitions
        """
        template = self.load_template(template_id)
        return self._extract_parameter_definitions(template)
    
    def _resolve_template_inheritance(self, template_id: str) -> Dict[str, Any]:
        """Resolve template inheritance chain."""
        if template_id in self._inheritance_chain:
            raise TemplateValidationError(f"Circular inheritance detected: {template_id}")
            
        self._inheritance_chain.add(template_id)
        
        template = self.load_template(template_id)
        metadata = template.get('metadata', {})
        
        # Check if template extends another template
        extends = metadata.get('extends')
        if extends:
            # Load parent template
            parent_template = self._resolve_template_inheritance(extends)
            
            # Merge parent with child (child overrides parent)
            merged_template = self._merge_templates(parent_template, template)
            return merged_template
        
        return template
    
    def _merge_templates(self, parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """Merge child template with parent template."""
        merged = copy.deepcopy(parent)
        
        # Merge sections
        for section in ['metadata', 'parameters', 'tasks', 'variables']:
            if section in child:
                if section in merged:
                    if isinstance(merged[section], dict) and isinstance(child[section], dict):
                        merged[section].update(child[section])
                    elif isinstance(merged[section], list) and isinstance(child[section], list):
                        merged[section].extend(child[section])
                    else:
                        merged[section] = child[section]
                else:
                    merged[section] = child[section]
        
        return merged
    
    def _validate_template_structure(self, template: Dict[str, Any]) -> None:
        """Validate basic template structure."""
        required_sections = ['metadata', 'tasks']
        
        for section in required_sections:
            if section not in template:
                raise TemplateValidationError(f"Missing required section: {section}")
        
        # Validate metadata
        metadata = template['metadata']
        required_metadata = ['name', 'version', 'description']
        
        for field in required_metadata:
            if field not in metadata:
                raise TemplateValidationError(f"Missing required metadata field: {field}")
        
        # Validate tasks section
        tasks = template['tasks']
        if not isinstance(tasks, dict):
            raise TemplateValidationError("Tasks section must be a dictionary")
        
        if not tasks:
            raise TemplateValidationError("Tasks section cannot be empty")
    
    def _extract_parameter_definitions(self, template: Dict[str, Any]) -> List[TemplateParameter]:
        """Extract parameter definitions from template."""
        parameters = []
        param_section = template.get('parameters', {})
        
        for param_name, param_def in param_section.items():
            if isinstance(param_def, dict):
                parameters.append(TemplateParameter(
                    name=param_name,
                    type=param_def.get('type', 'string'),
                    description=param_def.get('description', ''),
                    required=param_def.get('required', True),
                    default=param_def.get('default'),
                    validation_pattern=param_def.get('pattern'),
                    allowed_values=param_def.get('allowed_values'),
                    min_length=param_def.get('min_length'),
                    max_length=param_def.get('max_length'),
                    min_value=param_def.get('min_value'),
                    max_value=param_def.get('max_value')
                ))
        
        return parameters
    
    def _validate_parameters(self, param_definitions: List[TemplateParameter], 
                           provided_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provided parameters against definitions."""
        validated = {}
        
        # Check required parameters
        for param_def in param_definitions:
            param_name = param_def.name
            
            if param_def.required and param_name not in provided_params:
                if param_def.default is not None:
                    validated[param_name] = param_def.default
                else:
                    raise ParameterSubstitutionError(f"Required parameter missing: {param_name}")
            elif param_name in provided_params:
                value = provided_params[param_name]
                validated[param_name] = self._validate_parameter_value(param_def, value)
        
        # Check for extra parameters
        extra_params = set(provided_params.keys()) - {p.name for p in param_definitions}
        if extra_params:
            logger.warning(f"Extra parameters provided: {extra_params}")
        
        return validated
    
    def _validate_parameter_value(self, param_def: TemplateParameter, value: Any) -> Any:
        """Validate a single parameter value."""
        # Type checking
        if param_def.type == 'string' and not isinstance(value, str):
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be a string")
        elif param_def.type == 'number' and not isinstance(value, (int, float)):
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be a number")
        elif param_def.type == 'boolean' and not isinstance(value, bool):
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be a boolean")
        elif param_def.type == 'array' and not isinstance(value, list):
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be an array")
        elif param_def.type == 'object' and not isinstance(value, dict):
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be an object")
        
        # String validations
        if isinstance(value, str):
            if param_def.min_length is not None and len(value) < param_def.min_length:
                raise ParameterSubstitutionError(f"Parameter {param_def.name} too short (min: {param_def.min_length})")
            if param_def.max_length is not None and len(value) > param_def.max_length:
                raise ParameterSubstitutionError(f"Parameter {param_def.name} too long (max: {param_def.max_length})")
            if param_def.validation_pattern:
                if not re.match(param_def.validation_pattern, value):
                    raise ParameterSubstitutionError(f"Parameter {param_def.name} doesn't match pattern")
        
        # Number validations
        if isinstance(value, (int, float)):
            if param_def.min_value is not None and value < param_def.min_value:
                raise ParameterSubstitutionError(f"Parameter {param_def.name} too small (min: {param_def.min_value})")
            if param_def.max_value is not None and value > param_def.max_value:
                raise ParameterSubstitutionError(f"Parameter {param_def.name} too large (max: {param_def.max_value})")
        
        # Allowed values validation
        if param_def.allowed_values is not None and value not in param_def.allowed_values:
            raise ParameterSubstitutionError(f"Parameter {param_def.name} must be one of: {param_def.allowed_values}")
        
        return value
    
    def _substitute_parameters(self, template: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform parameter substitution throughout the template."""
        def substitute_recursive(obj: Any) -> Any:
            if isinstance(obj, str):
                return self._substitute_string(obj, parameters)
            elif isinstance(obj, dict):
                return {key: substitute_recursive(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [substitute_recursive(item) for item in obj]
            else:
                return obj
        
        return substitute_recursive(template)
    
    def _substitute_string(self, text: str, parameters: Dict[str, Any]) -> str:
        """Substitute parameters in a string using {{parameter}} syntax."""
        def replace_param(match):
            param_name = match.group(1)
            if param_name in parameters:
                value = parameters[param_name]
                return str(value) if value is not None else ''
            else:
                # Leave unmatched parameters as-is with warning
                logger.warning(f"Unmatched parameter in substitution: {param_name}")
                return match.group(0)
        
        # Replace {{parameter}} patterns
        return re.sub(r'\{\{(\w+)\}\}', replace_param, text)
    
    def _validate_instantiated_template(self, template: Dict[str, Any]) -> None:
        """Validate the instantiated template for consistency."""
        # Check that no parameter placeholders remain
        def check_placeholders(obj: Any, path: str = ""):
            if isinstance(obj, str):
                if '{{' in obj and '}}' in obj:
                    remaining = re.findall(r'\{\{(\w+)\}\}', obj)
                    if remaining:
                        raise ParameterSubstitutionError(f"Unresolved parameters at {path}: {remaining}")
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_placeholders(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_placeholders(item, f"{path}[{i}]")
        
        check_placeholders(template)
        
        # Additional semantic validation could go here
        # (e.g., checking task dependencies, resource requirements, etc.)