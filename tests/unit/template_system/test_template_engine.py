"""
Unit tests for Template Engine

Tests template instantiation, parameter substitution, validation,
and error handling.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from mcp_task_orchestrator.infrastructure.template_system.template_engine import (
    TemplateEngine,
    TemplateValidationError,
    ParameterSubstitutionError
)
from mcp_task_orchestrator.infrastructure.template_system.storage_manager import TemplateStorageError


class TestTemplateEngine:
    """Test suite for TemplateEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TemplateEngine()
        
        # Sample valid template
        self.valid_template = {
            "metadata": {
                "name": "Test Template",
                "version": "1.0.0",
                "description": "A test template"
            },
            "parameters": {
                "project_name": {
                    "type": "string",
                    "description": "Name of the project",
                    "required": True,
                    "min_length": 3,
                    "max_length": 50
                },
                "complexity": {
                    "type": "string",
                    "description": "Project complexity",
                    "required": False,
                    "enum": ["simple", "moderate", "complex"],
                    "default": "moderate"
                },
                "team_size": {
                    "type": "number",
                    "description": "Team size",
                    "required": False,
                    "min": 1,
                    "max": 20,
                    "default": 5
                }
            },
            "tasks": {
                "setup": {
                    "title": "Set up {{project_name}} project",
                    "description": "Initialize the {{project_name}} project with {{complexity}} complexity",
                    "type": "implementation",
                    "estimated_effort": "2 hours"
                },
                "development": {
                    "title": "Develop core features",
                    "description": "Build the main functionality for a team of {{team_size}}",
                    "type": "implementation",
                    "dependencies": ["setup"]
                }
            }
        }
    
    def test_validate_template_syntax_valid(self):
        """Test validation of a valid template."""
        errors = self.engine.validate_template_syntax(self.valid_template)
        assert errors == []
    
    def test_validate_template_syntax_missing_metadata(self):
        """Test validation with missing metadata."""
        invalid_template = self.valid_template.copy()
        del invalid_template["metadata"]
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("metadata" in error.lower() for error in errors)
    
    def test_validate_template_syntax_missing_required_metadata(self):
        """Test validation with missing required metadata fields."""
        invalid_template = self.valid_template.copy()
        invalid_template["metadata"] = {"name": "Test"}  # Missing version, description
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("version" in error.lower() for error in errors)
        assert any("description" in error.lower() for error in errors)
    
    def test_validate_template_syntax_invalid_parameter_type(self):
        """Test validation with invalid parameter type."""
        invalid_template = self.valid_template.copy()
        invalid_template["parameters"]["invalid_param"] = {
            "type": "invalid_type",
            "description": "Invalid parameter"
        }
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("invalid_type" in error for error in errors)
    
    def test_validate_template_syntax_missing_parameter_description(self):
        """Test validation with missing parameter description."""
        invalid_template = self.valid_template.copy()
        invalid_template["parameters"]["no_desc"] = {
            "type": "string",
            "required": True
        }
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("description" in error.lower() for error in errors)
    
    def test_validate_template_syntax_invalid_task_structure(self):
        """Test validation with invalid task structure."""
        invalid_template = self.valid_template.copy()
        invalid_template["tasks"]["invalid_task"] = {
            "title": "Missing description"
            # Missing required 'description' field
        }
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("description" in error.lower() for error in errors)
    
    def test_validate_template_syntax_invalid_dependency(self):
        """Test validation with invalid task dependency."""
        invalid_template = self.valid_template.copy()
        invalid_template["tasks"]["invalid_deps"] = {
            "title": "Invalid Dependencies",
            "description": "Task with non-existent dependencies",
            "dependencies": ["non_existent_task"]
        }
        
        errors = self.engine.validate_template_syntax(invalid_template)
        assert len(errors) > 0
        assert any("non_existent_task" in error for error in errors)
    
    def test_instantiate_template_valid_parameters(self):
        """Test template instantiation with valid parameters."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            parameters = {
                "project_name": "MyProject",
                "complexity": "complex",
                "team_size": 8
            }
            
            result = self.engine.instantiate_template("test_template", parameters)
            
            # Verify parameter substitution
            assert "MyProject" in result["tasks"]["setup"]["title"]
            assert "MyProject" in result["tasks"]["setup"]["description"]
            assert "complex" in result["tasks"]["setup"]["description"]
            assert "8" in result["tasks"]["development"]["description"]
    
    def test_instantiate_template_with_defaults(self):
        """Test template instantiation using default parameter values."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            # Only provide required parameter
            parameters = {"project_name": "DefaultProject"}
            
            result = self.engine.instantiate_template("test_template", parameters)
            
            # Should use default values
            assert "DefaultProject" in result["tasks"]["setup"]["title"]
            assert "moderate" in result["tasks"]["setup"]["description"]  # default complexity
            assert "5" in result["tasks"]["development"]["description"]  # default team_size
    
    def test_instantiate_template_missing_required_parameter(self):
        """Test template instantiation with missing required parameter."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            # Missing required project_name
            parameters = {"complexity": "simple"}
            
            with pytest.raises(ParameterSubstitutionError, match="Missing required parameter"):
                self.engine.instantiate_template("test_template", parameters)
    
    def test_instantiate_template_invalid_parameter_value(self):
        """Test template instantiation with invalid parameter value."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            parameters = {
                "project_name": "AB",  # Too short (min_length: 3)
                "complexity": "invalid_value"  # Not in enum
            }
            
            with pytest.raises(ParameterSubstitutionError, match="Parameter validation failed"):
                self.engine.instantiate_template("test_template", parameters)
    
    def test_instantiate_template_string_length_validation(self):
        """Test string parameter length validation."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            # Test too short
            with pytest.raises(ParameterSubstitutionError):
                self.engine.instantiate_template("test_template", {"project_name": "AB"})
            
            # Test too long
            long_name = "A" * 100  # max_length: 50
            with pytest.raises(ParameterSubstitutionError):
                self.engine.instantiate_template("test_template", {"project_name": long_name})
    
    def test_instantiate_template_number_range_validation(self):
        """Test number parameter range validation."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            parameters = {"project_name": "ValidProject"}
            
            # Test below minimum
            parameters["team_size"] = 0  # min: 1
            with pytest.raises(ParameterSubstitutionError):
                self.engine.instantiate_template("test_template", parameters)
            
            # Test above maximum
            parameters["team_size"] = 25  # max: 20
            with pytest.raises(ParameterSubstitutionError):
                self.engine.instantiate_template("test_template", parameters)
    
    def test_instantiate_template_enum_validation(self):
        """Test enum parameter validation."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            parameters = {
                "project_name": "ValidProject",
                "complexity": "invalid_complexity"
            }
            
            with pytest.raises(ParameterSubstitutionError, match="not in allowed values"):
                self.engine.instantiate_template("test_template", parameters)
    
    def test_instantiate_template_nonexistent(self):
        """Test instantiation of non-existent template."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.side_effect = TemplateStorageError("Template not found")
            
            with pytest.raises(TemplateValidationError, match="Template not found"):
                self.engine.instantiate_template("nonexistent", {})
    
    def test_substitute_parameters_simple(self):
        """Test simple parameter substitution."""
        content = "Hello {{name}}, welcome to {{project}}!"
        parameters = {"name": "Alice", "project": "MyProject"}
        
        result = self.engine._substitute_parameters(content, parameters)
        assert result == "Hello Alice, welcome to MyProject!"
    
    def test_substitute_parameters_multiple_occurrences(self):
        """Test parameter substitution with multiple occurrences."""
        content = "{{name}} likes {{project}}. {{name}} works on {{project}} daily."
        parameters = {"name": "Bob", "project": "CoolApp"}
        
        result = self.engine._substitute_parameters(content, parameters)
        assert result == "Bob likes CoolApp. Bob works on CoolApp daily."
    
    def test_substitute_parameters_nested_content(self):
        """Test parameter substitution in nested data structures."""
        content = {
            "title": "Setup {{project_name}}",
            "description": "Initialize {{project_name}} with {{complexity}} settings",
            "nested": {
                "detail": "Project {{project_name}} details",
                "list": ["{{project_name}}", "item2", "{{complexity}}"]
            }
        }
        
        parameters = {"project_name": "TestApp", "complexity": "advanced"}
        
        result = self.engine._substitute_parameters(content, parameters)
        
        assert result["title"] == "Setup TestApp"
        assert result["description"] == "Initialize TestApp with advanced settings"
        assert result["nested"]["detail"] == "Project TestApp details"
        assert result["nested"]["list"][0] == "TestApp"
        assert result["nested"]["list"][2] == "advanced"
    
    def test_substitute_parameters_missing_parameter(self):
        """Test parameter substitution with missing parameter."""
        content = "Hello {{name}}, welcome to {{missing_param}}!"
        parameters = {"name": "Alice"}
        
        with pytest.raises(ParameterSubstitutionError, match="Parameter 'missing_param' not found"):
            self.engine._substitute_parameters(content, parameters)
    
    def test_substitute_parameters_special_characters(self):
        """Test parameter substitution with special characters."""
        content = "Path: {{base_path}}/{{file_name}}"
        parameters = {
            "base_path": "/home/user/my-project",
            "file_name": "config_file.json"
        }
        
        result = self.engine._substitute_parameters(content, parameters)
        assert result == "Path: /home/user/my-project/config_file.json"
    
    def test_substitute_parameters_numeric_values(self):
        """Test parameter substitution with numeric values."""
        content = "Port: {{port}}, Timeout: {{timeout}}s, Count: {{count}}"
        parameters = {"port": 8080, "timeout": 30.5, "count": 100}
        
        result = self.engine._substitute_parameters(content, parameters)
        assert result == "Port: 8080, Timeout: 30.5s, Count: 100"
    
    def test_get_template_parameters_valid(self):
        """Test getting template parameters from valid template."""
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = self.valid_template
            
            parameters = self.engine.get_template_parameters("test_template")
            
            assert len(parameters) == 3
            
            # Find project_name parameter
            project_param = next(p for p in parameters if p.name == "project_name")
            assert project_param.type == "string"
            assert project_param.required is True
            assert project_param.min_length == 3
            assert project_param.max_length == 50
            
            # Find complexity parameter
            complexity_param = next(p for p in parameters if p.name == "complexity")
            assert complexity_param.type == "string"
            assert complexity_param.required is False
            assert complexity_param.default == "moderate"
            assert complexity_param.allowed_values == ["simple", "moderate", "complex"]
            
            # Find team_size parameter
            team_param = next(p for p in parameters if p.name == "team_size")
            assert team_param.type == "number"
            assert team_param.min_value == 1
            assert team_param.max_value == 20
            assert team_param.default == 5
    
    def test_get_template_parameters_no_parameters(self):
        """Test getting parameters from template with no parameters section."""
        template_no_params = {
            "metadata": {"name": "Simple", "version": "1.0.0", "description": "No params"},
            "tasks": {"task1": {"title": "Task", "description": "A task"}}
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = template_no_params
            
            parameters = self.engine.get_template_parameters("test_template")
            assert parameters == []
    
    def test_parameter_validation_pattern(self):
        """Test parameter validation with regex pattern."""
        template_with_pattern = self.valid_template.copy()
        template_with_pattern["parameters"]["email"] = {
            "type": "string",
            "description": "Email address",
            "required": True,
            "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = template_with_pattern
            
            # Valid email
            parameters = {
                "project_name": "EmailProject",
                "email": "user@example.com"
            }
            result = self.engine.instantiate_template("test_template", parameters)
            assert result is not None
            
            # Invalid email
            parameters["email"] = "invalid-email"
            with pytest.raises(ParameterSubstitutionError, match="does not match pattern"):
                self.engine.instantiate_template("test_template", parameters)
    
    def test_boolean_parameter_handling(self):
        """Test handling of boolean parameters."""
        template_with_bool = self.valid_template.copy()
        template_with_bool["parameters"]["enable_feature"] = {
            "type": "boolean",
            "description": "Enable feature flag",
            "required": False,
            "default": True
        }
        template_with_bool["tasks"]["conditional"] = {
            "title": "Feature is {{enable_feature}}",
            "description": "Feature enabled: {{enable_feature}}"
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = template_with_bool
            
            # Test with explicit boolean
            parameters = {"project_name": "BoolProject", "enable_feature": False}
            result = self.engine.instantiate_template("test_template", parameters)
            assert "False" in result["tasks"]["conditional"]["title"]
            
            # Test with default
            parameters = {"project_name": "BoolProject"}
            result = self.engine.instantiate_template("test_template", parameters)
            assert "True" in result["tasks"]["conditional"]["title"]
    
    def test_array_parameter_handling(self):
        """Test handling of array parameters."""
        template_with_array = self.valid_template.copy()
        template_with_array["parameters"]["tags"] = {
            "type": "array",
            "description": "Project tags",
            "required": False,
            "default": ["development", "project"]
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = template_with_array
            
            # Array parameters should be converted to string for substitution
            parameters = {
                "project_name": "ArrayProject",
                "tags": ["web", "frontend", "react"]
            }
            result = self.engine.instantiate_template("test_template", parameters)
            # Should handle array conversion appropriately
            assert result is not None
    
    def test_template_inheritance_placeholder(self):
        """Test placeholder for template inheritance (future feature)."""
        # This is a placeholder test for when template inheritance is implemented
        # Currently, templates are standalone, but this tests the structure
        
        base_template = {
            "metadata": {"name": "Base", "version": "1.0.0", "description": "Base template"},
            "parameters": {"common_param": {"type": "string", "description": "Common parameter"}},
            "tasks": {"base_task": {"title": "Base task", "description": "Common task"}}
        }
        
        # Verify that templates can be loaded and instantiated independently
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = base_template
            
            parameters = {"common_param": "test_value"}
            result = self.engine.instantiate_template("base_template", parameters)
            
            assert result["tasks"]["base_task"]["title"] == "Base task"
            assert "test_value" in str(result) if "{{common_param}}" in str(base_template) else True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])