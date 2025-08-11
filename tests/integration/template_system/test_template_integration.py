"""
Integration tests for Template System

Tests the complete template workflow from storage to instantiation,
including MCP tool integration and end-to-end functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import asyncio

# from mcp_task_orchestrator.infrastructure.template_system.storage_manager import  # TODO: Complete this import
# from mcp_task_orchestrator.infrastructure.template_system.template_engine import  # TODO: Complete this import
# from mcp_task_orchestrator.infrastructure.template_system.template_installer import  # TODO: Complete this import
# from mcp_task_orchestrator.infrastructure.template_system.mcp_tools import  # TODO: Complete this import


class TestTemplateSystemIntegration:
    """Integration tests for the complete template system."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.storage_manager = TemplateStorageManager(workspace_dir=self.temp_dir)
        self.template_engine = TemplateEngine(storage_manager=self.storage_manager)
        self.installer = TemplateInstaller(storage_manager=self.storage_manager)
        
        # Sample template for testing
        self.sample_template = {
            "metadata": {
                "name": "Integration Test Template",
                "version": "1.0.0",
                "description": "Template for integration testing",
                "category": "testing",
                "tags": ["test", "integration"],
                "author": "Test Suite",
                "complexity": "simple",
                "estimated_duration": "30 minutes"
            },
            "parameters": {
                "project_name": {
                    "type": "string",
                    "description": "Name of the test project",
                    "required": True,
                    "min_length": 3,
                    "max_length": 50,
                    "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$"
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "Whether to include test files",
                    "required": False,
                    "default": True
                },
                "framework": {
                    "type": "string",
                    "description": "Testing framework to use",
                    "required": False,
                    "enum": ["pytest", "unittest", "nose2"],
                    "default": "pytest"
                },
                "complexity_level": {
                    "type": "number",
                    "description": "Complexity level (1-10)",
                    "required": False,
                    "min": 1,
                    "max": 10,
                    "default": 5
                }
            },
            "tasks": {
                "project_setup": {
                    "title": "Set up {{project_name}} project",
                    "description": "Initialize the {{project_name}} project structure",
                    "type": "implementation",
                    "specialist_type": "architect",
                    "complexity": "simple",
                    "estimated_effort": "15 minutes",
                    "dependencies": [],
                    "checklist": [
                        "Create project directory for {{project_name}}",
                        "Initialize version control",
                        "Set up basic project structure",
                        "Create README.md for {{project_name}}"
                    ]
                },
                "test_setup": {
                    "title": "Configure testing with {{framework}}",
                    "description": "Set up {{framework}} testing framework for {{project_name}}",
                    "type": "implementation",
                    "specialist_type": "tester",
                    "complexity": "simple",
                    "estimated_effort": "10 minutes",
                    "dependencies": ["project_setup"],
                    "checklist": [
                        "Install {{framework}} dependencies",
                        "Create test directory structure",
                        "Configure {{framework}} settings",
                        "Add sample test for {{project_name}}"
                    ],
                    "condition": "{{include_tests}}"
                },
                "complexity_review": {
                    "title": "Review complexity level {{complexity_level}}",
                    "description": "Review and validate the complexity level of {{complexity_level}} for {{project_name}}",
                    "type": "review",
                    "specialist_type": "reviewer",
                    "complexity": "moderate",
                    "estimated_effort": "5 minutes",
                    "dependencies": ["project_setup"],
                    "checklist": [
                        "Assess if complexity level {{complexity_level}} is appropriate",
                        "Document complexity justification for {{project_name}}",
                        "Recommend adjustments if needed"
                    ]
                }
            },
            "milestones": {
                "project_initialized": {
                    "title": "Project {{project_name}} Initialized",
                    "description": "Basic project structure is ready",
                    "required_tasks": ["project_setup"]
                },
                "testing_ready": {
                    "title": "Testing Infrastructure Ready",
                    "description": "{{framework}} testing is configured for {{project_name}}",
                    "required_tasks": ["project_setup", "test_setup"],
                    "condition": "{{include_tests}}"
                },
                "project_complete": {
                    "title": "{{project_name}} Setup Complete",
                    "description": "All setup tasks completed for {{project_name}}",
                    "required_tasks": ["project_setup", "test_setup", "complexity_review"]
                }
            }
        }
    
    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_template_lifecycle(self):
        """Test the complete template lifecycle: create, load, instantiate, delete."""
        template_id = "integration_test_template"
        
        # 1. Create template
        self.storage_manager.save_template(template_id, self.sample_template, "user")
        
        # 2. Verify template exists
        templates = self.storage_manager.list_templates("user")
        template_ids = [t["id"] for t in templates]
        assert template_id in template_ids
        
        # 3. Load template
        loaded_template = self.storage_manager.load_template(template_id, "user")
        assert loaded_template["metadata"]["name"] == "Integration Test Template"
        assert len(loaded_template["parameters"]) == 4
        assert len(loaded_template["tasks"]) == 3
        
        # 4. Instantiate template with parameters
        parameters = {
            "project_name": "MyTestProject",
            "include_tests": True,
            "framework": "pytest",
            "complexity_level": 7
        }
        
        instantiated = self.template_engine.instantiate_template(template_id, parameters)
        
        # Verify parameter substitution
        assert "MyTestProject" in instantiated["tasks"]["project_setup"]["title"]
        assert "MyTestProject" in instantiated["tasks"]["project_setup"]["description"]
        assert "pytest" in instantiated["tasks"]["test_setup"]["title"]
        assert "pytest" in instantiated["tasks"]["test_setup"]["description"]
        assert "7" in instantiated["tasks"]["complexity_review"]["title"]
        
        # Verify milestones were also substituted
        assert "MyTestProject" in instantiated["milestones"]["project_initialized"]["title"]
        assert "pytest" in instantiated["milestones"]["testing_ready"]["description"]
        
        # 5. Delete template
        self.storage_manager.delete_template(template_id, "user")
        
        # 6. Verify template is deleted
        with pytest.raises(TemplateStorageError):
            self.storage_manager.load_template(template_id, "user")
    
    def test_template_validation_integration(self):
        """Test template validation during the complete workflow."""
        # Test with invalid template
        invalid_template = {
            "metadata": {
                "name": "Invalid Template",
                "version": "1.0.0"
                # Missing required description
            },
            "parameters": {
                "param1": {
                    "type": "invalid_type",  # Invalid parameter type
                    "description": "Invalid parameter"
                }
            },
            "tasks": {
                "task1": {
                    "title": "Task without description"
                    # Missing required description
                }
            }
        }
        
        # Validation should fail during save
        with pytest.raises(Exception):  # Could be validation or security error
            self.storage_manager.save_template("invalid_template", invalid_template, "user")
    
    def test_parameter_validation_integration(self):
        """Test parameter validation during template instantiation."""
        template_id = "param_validation_test"
        self.storage_manager.save_template(template_id, self.sample_template, "user")
        
        # Test with invalid parameters
        invalid_parameters = [
            # Missing required parameter
            {"include_tests": True, "framework": "pytest"},
            
            # Invalid string length
            {"project_name": "AB", "include_tests": True},  # Too short
            
            # Invalid enum value
            {"project_name": "ValidProject", "framework": "invalid_framework"},
            
            # Invalid number range
            {"project_name": "ValidProject", "complexity_level": 15},  # Too high
            
            # Invalid pattern
            {"project_name": "123InvalidName", "include_tests": True},  # Starts with number
        ]
        
        for params in invalid_parameters:
            with pytest.raises(ParameterSubstitutionError):
                self.template_engine.instantiate_template(template_id, params)
    
    def test_template_categories_and_filtering(self):
        """Test template organization by categories."""
        # Create templates in different categories
        templates_data = [
            ("user_template_1", "user", {"metadata": {"name": "User Template 1", "version": "1.0.0", "description": "User template"}}),
            ("user_template_2", "user", {"metadata": {"name": "User Template 2", "version": "1.0.0", "description": "Another user template"}}),
            ("shared_template_1", "shared", {"metadata": {"name": "Shared Template 1", "version": "1.0.0", "description": "Shared template"}}),
        ]
        
        for template_id, category, template_data in templates_data:
            self.storage_manager.save_template(template_id, template_data, category)
        
        # Test category filtering
        user_templates = self.storage_manager.list_templates("user")
        shared_templates = self.storage_manager.list_templates("shared")
        all_templates = self.storage_manager.list_templates()
        
        user_ids = [t["id"] for t in user_templates]
        shared_ids = [t["id"] for t in shared_templates]
        all_ids = [t["id"] for t in all_templates]
        
        assert "user_template_1" in user_ids
        assert "user_template_2" in user_ids
        assert "shared_template_1" not in user_ids
        
        assert "shared_template_1" in shared_ids
        assert "user_template_1" not in shared_ids
        
        assert len(all_ids) >= 3
        assert "user_template_1" in all_ids
        assert "shared_template_1" in all_ids
    
    def test_template_installer_integration(self):
        """Test template installer with the complete system."""
        # Test installing a custom template
        template_content = json.dumps(self.sample_template, indent=2)
        
        result = asyncio.run(self.installer.install_custom_template(
            "installer_test_template",
            template_content,
            "user",
            overwrite=False
        ))
        
        assert result["status"] == "installed"
        
        # Verify template can be loaded
        loaded = self.storage_manager.load_template("installer_test_template", "user")
        assert loaded["metadata"]["name"] == "Integration Test Template"
        
        # Test installer status
        status = asyncio.run(self.installer.get_installation_status())
        assert status["status"] == "success"
        assert status["user_installed"] >= 1
    
    def test_workspace_isolation(self):
        """Test that templates are isolated per workspace."""
        # Create second workspace
        temp_dir_2 = Path(tempfile.mkdtemp())
        storage_manager_2 = TemplateStorageManager(workspace_dir=temp_dir_2)
        
        try:
            # Save template in first workspace
            self.storage_manager.save_template("isolated_template", self.sample_template, "user")
            
            # Verify it doesn't exist in second workspace
            templates_ws2 = storage_manager_2.list_templates("user")
            template_ids_ws2 = [t["id"] for t in templates_ws2]
            assert "isolated_template" not in template_ids_ws2
            
            # Save different template in second workspace
            modified_template = self.sample_template.copy()
            modified_template["metadata"]["name"] = "Workspace 2 Template"
            storage_manager_2.save_template("ws2_template", modified_template, "user")
            
            # Verify isolation
            templates_ws1 = self.storage_manager.list_templates("user")
            template_ids_ws1 = [t["id"] for t in templates_ws1]
            assert "ws2_template" not in template_ids_ws1
            assert "isolated_template" in template_ids_ws1
        
        finally:
            import shutil
            shutil.rmtree(temp_dir_2, ignore_errors=True)
    
    def test_concurrent_template_operations(self):
        """Test concurrent template operations."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_template(thread_id):
            try:
                template_id = f"concurrent_template_{thread_id}"
                modified_template = self.sample_template.copy()
                modified_template["metadata"]["name"] = f"Concurrent Template {thread_id}"
                
                self.storage_manager.save_template(template_id, modified_template, "user")
                
                # Verify creation
                loaded = self.storage_manager.load_template(template_id, "user")
                results.append((thread_id, loaded["metadata"]["name"]))
                
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_template, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"
        assert len(results) == 5
        
        # Verify all templates were created
        templates = self.storage_manager.list_templates("user")
        template_ids = [t["id"] for t in templates]
        
        for i in range(5):
            assert f"concurrent_template_{i}" in template_ids


class TestMCPToolsIntegration:
    """Integration tests for MCP tools with the template system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock storage manager to use temporary directory
        self.patcher = patch('mcp_task_orchestrator.infrastructure.template_system.mcp_tools.TemplateStorageManager')
        self.mock_storage_class = self.patcher.start()
        self.mock_storage = Mock()
        self.mock_storage_class.return_value = self.mock_storage
        
        self.sample_template_content = json.dumps({
            "metadata": {
                "name": "MCP Test Template",
                "version": "1.0.0",
                "description": "Template for MCP testing"
            },
            "parameters": {
                "test_param": {
                    "type": "string",
                    "description": "Test parameter",
                    "required": True
                }
            },
            "tasks": {
                "test_task": {
                    "title": "Test {{test_param}}",
                    "description": "A test task"
                }
            }
        })
    
    def teardown_method(self):
        """Clean up mocks."""
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_mcp_template_create(self):
        """Test MCP template creation tool."""
        args = {
            "template_id": "mcp_test_template",
            "template_content": self.sample_template_content,
            "category": "user",
            "overwrite": False
        }
        
        # Mock successful save
        self.mock_storage.save_template.return_value = None
        
        result = await handle_template_create(args)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert response["template_id"] == "mcp_test_template"
        assert response["category"] == "user"
        assert "next_steps" in response
    
    @pytest.mark.asyncio
    async def test_mcp_template_list(self):
        """Test MCP template listing tool."""
        # Mock template list
        mock_templates = [
            {"id": "template1", "category": "user", "name": "Template 1"},
            {"id": "template2", "category": "user", "name": "Template 2"}
        ]
        self.mock_storage.list_templates.return_value = mock_templates
        
        args = {"category": "user", "include_metadata": False}
        result = await handle_template_list(args)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert len(response["templates"]) == 2
        assert response["total_count"] == 2
        assert response["filtered_by_category"] == "user"
    
    @pytest.mark.asyncio
    async def test_mcp_template_load(self):
        """Test MCP template loading tool."""
        # Mock template data
        mock_template = {
            "metadata": {"name": "Test Template", "version": "1.0.0", "description": "Test"},
            "parameters": {"param1": {"type": "string", "description": "Parameter 1"}},
            "tasks": {"task1": {"title": "Task 1", "description": "First task"}}
        }
        mock_info = {
            "id": "test_template",
            "category": "user",
            "size": 1024,
            "modified": "2024-01-01T00:00:00"
        }
        
        self.mock_storage.load_template.return_value = mock_template
        self.mock_storage.get_template_info.return_value = mock_info
        
        args = {"template_id": "test_template", "category": "user"}
        result = await handle_template_load(args)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert response["template"]["metadata"]["name"] == "Test Template"
        assert response["info"]["id"] == "test_template"
    
    @pytest.mark.asyncio
    async def test_mcp_template_instantiate(self):
        """Test MCP template instantiation tool."""
        with patch('mcp_task_orchestrator.infrastructure.template_system.mcp_tools.TemplateEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            # Mock instantiated template
            mock_instantiated = {
                "metadata": {"name": "Test Template"},
                "tasks": {
                    "task1": {
                        "title": "Process TestValue",
                        "description": "A processed task"
                    }
                }
            }
            mock_engine.instantiate_template.return_value = mock_instantiated
            
            args = {
                "template_id": "test_template",
                "parameters": {"test_param": "TestValue"},
                "create_tasks": False
            }
            
            result = await handle_template_instantiate(args)
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["status"] == "success"
            assert response["instantiated_template"]["tasks"]["task1"]["title"] == "Process TestValue"
            assert response["parameters_used"]["test_param"] == "TestValue"
            assert response["tasks_created"] is False
    
    @pytest.mark.asyncio
    async def test_mcp_template_validate(self):
        """Test MCP template validation tool."""
        with patch('mcp_task_orchestrator.infrastructure.template_system.mcp_tools.TemplateEngine') as mock_engine_class:
            mock_engine = Mock()
            mock_engine_class.return_value = mock_engine
            
            # Mock successful validation
            mock_engine.validate_template_syntax.return_value = []
            
            args = {"template_content": self.sample_template_content}
            result = await handle_template_validate(args)
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["status"] == "valid"
            assert response["valid"] is True
            assert "template_info" in response
    
    @pytest.mark.asyncio
    async def test_mcp_template_delete(self):
        """Test MCP template deletion tool."""
        # Mock successful deletion
        self.mock_storage.delete_template.return_value = None
        
        args = {"template_id": "test_template", "category": "user"}
        result = await handle_template_delete(args)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert "test_template" in response["message"]
    
    @pytest.mark.asyncio
    async def test_mcp_template_install_default_library(self):
        """Test MCP default library installation tool."""
        with patch('mcp_task_orchestrator.infrastructure.template_system.mcp_tools.get_template_installer') as mock_installer_func:
            mock_installer = Mock()
            mock_installer_func.return_value = mock_installer
            
            # Mock successful installation
            mock_result = {
                "status": "success",
                "category": "all",
                "total_templates": 5,
                "installed": ["template1", "template2", "template3"],
                "failed": [],
                "skipped": ["template4", "template5"],
                "message": "Successfully installed 3 templates"
            }
            mock_installer.install_default_library = AsyncMock(return_value=mock_result)
            
            args = {"category": "all", "overwrite": False}
            result = await handle_template_install_default_library(args)
            
            assert len(result) == 1
            response = json.loads(result[0].text)
            assert response["status"] == "success"
            assert response["total_templates"] == 5
            assert len(response["installed"]) == 3
            assert len(response["skipped"]) == 2
    
    @pytest.mark.asyncio
    async def test_mcp_error_handling(self):
        """Test MCP tools error handling."""
        # Test with storage error
        self.mock_storage.save_template.side_effect = Exception("Storage error")
        
        args = {
            "template_id": "error_template",
            "template_content": self.sample_template_content,
            "category": "user"
        }
        
        result = await handle_template_create(args)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "error"
        assert "Storage error" in response["message"]


class TestTemplateSystemPerformance:
    """Performance tests for template system operations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.storage_manager = TemplateStorageManager(workspace_dir=self.temp_dir)
        self.template_engine = TemplateEngine(storage_manager=self.storage_manager)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_template_handling(self):
        """Test handling of large templates."""
        # Create a large template with many parameters and tasks
        large_template = {
            "metadata": {
                "name": "Large Template",
                "version": "1.0.0",
                "description": "A template with many parameters and tasks"
            },
            "parameters": {},
            "tasks": {}
        }
        
        # Add many parameters
        for i in range(100):
            large_template["parameters"][f"param_{i}"] = {
                "type": "string",
                "description": f"Parameter {i}",
                "required": False,
                "default": f"default_value_{i}"
            }
        
        # Add many tasks
        for i in range(100):
            large_template["tasks"][f"task_{i}"] = {
                "title": f"Task {i} with {{param_{i}}}",
                "description": f"Process parameter {{param_{i}}} in task {i}",
                "type": "implementation"
            }
        
        # Test saving large template
        template_id = "large_template"
        self.storage_manager.save_template(template_id, large_template, "user")
        
        # Test loading large template
        loaded = self.storage_manager.load_template(template_id, "user")
        assert len(loaded["parameters"]) == 100
        assert len(loaded["tasks"]) == 100
        
        # Test instantiating with many parameters
        parameters = {f"param_{i}": f"value_{i}" for i in range(100)}
        
        import time
        start_time = time.time()
        instantiated = self.template_engine.instantiate_template(template_id, parameters)
        end_time = time.time()
        
        # Should complete in reasonable time
        assert end_time - start_time < 5.0
        
        # Verify substitution worked
        assert "value_0" in instantiated["tasks"]["task_0"]["title"]
        assert "value_99" in instantiated["tasks"]["task_99"]["title"]
    
    def test_many_templates_performance(self):
        """Test performance with many templates."""
        # Create many small templates
        template_count = 50
        
        for i in range(template_count):
            template = {
                "metadata": {
                    "name": f"Template {i}",
                    "version": "1.0.0",
                    "description": f"Template number {i}"
                },
                "parameters": {
                    "param": {
                        "type": "string",
                        "description": "A parameter",
                        "required": True
                    }
                },
                "tasks": {
                    "task": {
                        "title": f"Task from template {i}",
                        "description": "A task with {{param}}"
                    }
                }
            }
            
            self.storage_manager.save_template(f"template_{i}", template, "user")
        
        # Test listing many templates
        import time
        start_time = time.time()
        templates = self.storage_manager.list_templates("user")
        end_time = time.time()
        
        # Should complete quickly
        assert end_time - start_time < 2.0
        assert len(templates) == template_count
        
        # Test loading templates sequentially
        start_time = time.time()
        for i in range(min(10, template_count)):  # Test first 10
            loaded = self.storage_manager.load_template(f"template_{i}", "user")
            assert loaded["metadata"]["name"] == f"Template {i}"
        end_time = time.time()
        
        # Should load 10 templates quickly
        assert end_time - start_time < 3.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])