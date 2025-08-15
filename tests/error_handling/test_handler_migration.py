"""
Test Suite for Handler Migration System.

Tests the gradual migration from dictionary-based to Pydantic DTO-based handlers,
including feature flags, backward compatibility, and migration management.
"""

import pytest
import os
from unittest.mock import patch, Mock, AsyncMock
from typing import Dict, Any

# Import migration components
# from mcp_task_orchestrator.infrastructure.mcp.handlers.migration_config import  # TODO: Complete this import
# from mcp_task_orchestrator.infrastructure.mcp.tool_router import  # TODO: Complete this import


class TestHandlerMigrationManager:
    """Test suite for HandlerMigrationManager."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Clear environment variables
        env_vars_to_clear = [
            "MCP_USE_PYDANTIC_HANDLERS",
            "MCP_USE_PYDANTIC_CREATE_TASK",
            "MCP_USE_PYDANTIC_UPDATE_TASK",
            "MCP_USE_PYDANTIC_DELETE_TASK",
            "MCP_USE_PYDANTIC_CANCEL_TASK",
            "MCP_USE_PYDANTIC_QUERY_TASKS",
            "MCP_USE_PYDANTIC_EXECUTE_TASK",
            "MCP_USE_PYDANTIC_COMPLETE_TASK"
        ]
        
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
    
    def test_default_configuration(self):
        """Test default migration manager configuration."""
        manager = HandlerMigrationManager()
        
        # By default, all handlers should use old implementations
        for tool_name, config in manager.handler_configs.items():
            assert config.use_new == False
    
    def test_global_flag_enables_all(self):
        """Test that global flag enables all new handlers."""
        with patch.dict(os.environ, {"MCP_USE_PYDANTIC_HANDLERS": "true"}):
            manager = HandlerMigrationManager()
            
            # All handlers should use new implementations
            for tool_name, config in manager.handler_configs.items():
                assert config.use_new == True
    
    def test_individual_flags(self):
        """Test individual handler flags."""
        with patch.dict(os.environ, {
            "MCP_USE_PYDANTIC_CREATE_TASK": "true",
            "MCP_USE_PYDANTIC_QUERY_TASKS": "true"
        }):
            manager = HandlerMigrationManager()
            
            # Only specific handlers should use new implementations
            assert manager.handler_configs["orchestrator_plan_task"].use_new == True
            assert manager.handler_configs["orchestrator_create_generic_task"].use_new == True
            assert manager.handler_configs["orchestrator_query_tasks"].use_new == True
            
            # Others should remain old
            assert manager.handler_configs["orchestrator_update_task"].use_new == False
            assert manager.handler_configs["orchestrator_delete_task"].use_new == False
    
    def test_get_handler_old_implementation(self):
        """Test getting old handler implementation."""
        manager = HandlerMigrationManager()
        
        handler = manager.get_handler("orchestrator_plan_task")
        
        # Should return old handler
        assert handler.__name__ == "handle_create_generic_task"
    
    def test_get_handler_new_implementation(self):
        """Test getting new handler implementation."""
        manager = HandlerMigrationManager()
        manager.enable_handler("orchestrator_plan_task")
        
        handler = manager.get_handler("orchestrator_plan_task")
        
        # Should return new handler
        assert handler.__name__ == "handle_create_task_v2"
    
    def test_get_handler_unknown_tool(self):
        """Test getting handler for unknown tool."""
        manager = HandlerMigrationManager()
        
        with pytest.raises(ValueError, match="Unknown tool"):
            manager.get_handler("unknown_tool")
    
    def test_enable_disable_handlers(self):
        """Test enabling and disabling individual handlers."""
        manager = HandlerMigrationManager()
        
        # Initially disabled
        assert manager.handler_configs["orchestrator_plan_task"].use_new == False
        
        # Enable
        manager.enable_handler("orchestrator_plan_task")
        assert manager.handler_configs["orchestrator_plan_task"].use_new == True
        
        # Disable
        manager.disable_handler("orchestrator_plan_task")
        assert manager.handler_configs["orchestrator_plan_task"].use_new == False
    
    def test_enable_disable_all_handlers(self):
        """Test enabling and disabling all handlers."""
        manager = HandlerMigrationManager()
        
        # Enable all
        manager.enable_all_handlers()
        for config in manager.handler_configs.values():
            assert config.use_new == True
        
        # Disable all
        manager.disable_all_handlers()
        for config in manager.handler_configs.values():
            assert config.use_new == False
    
    def test_migration_status(self):
        """Test getting migration status."""
        manager = HandlerMigrationManager()
        manager.enable_handler("orchestrator_plan_task")
        
        status = manager.get_migration_status()
        
        assert isinstance(status, dict)
        assert "orchestrator_plan_task" in status
        assert status["orchestrator_plan_task"]["using_new_handler"] == True
        assert "description" in status["orchestrator_plan_task"]
        assert "old_handler" in status["orchestrator_plan_task"]
        assert "new_handler" in status["orchestrator_plan_task"]


class TestGlobalMigrationFunctions:
    """Test global migration management functions."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Clear environment variables
        for var in os.environ:
            if var.startswith("MCP_USE_PYDANTIC"):
                del os.environ[var]
    
    def test_get_migration_manager_singleton(self):
        """Test that get_migration_manager returns singleton."""
        manager1 = get_migration_manager()
        manager2 = get_migration_manager()
        
        assert manager1 is manager2
    
    def test_get_handler_for_tool(self):
        """Test get_handler_for_tool function."""
        # Default should return old handler
        handler = get_handler_for_tool("orchestrator_plan_task")
        assert handler.__name__ == "handle_create_generic_task"
        
        # Enable new handler
        manager = get_migration_manager()
        manager.enable_handler("orchestrator_plan_task")
        
        handler = get_handler_for_tool("orchestrator_plan_task")
        assert handler.__name__ == "handle_create_task_v2"
    
    def test_get_migration_status_global(self):
        """Test global get_migration_status function."""
        status = get_migration_status()
        
        assert isinstance(status, dict)
        assert len(status) > 0
        assert "orchestrator_plan_task" in status


class TestToolRouterIntegration:
    """Test integration with the tool router."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Clear environment variables
        for var in os.environ:
            if var.startswith("MCP_USE_PYDANTIC"):
                del os.environ[var]
    
    @pytest.mark.asyncio
    async def test_route_tool_call_old_handler(self):
        """Test tool routing to old handler."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock successful task creation
            mock_task = Mock()
            mock_task.task_id = "test-123"
            mock_task.title = "Test Task"
            mock_task.created_at = "2024-01-01T00:00:00"
            mock_task.dict.return_value = {
                "task_id": "test-123",
                "title": "Test Task",
                "created_at": "2024-01-01T00:00:00"
            }
            mock_use_case.create_task.return_value = mock_task
            
            args = {
                "title": "Test Task",
                "description": "Test Description"
            }
            
            result = await route_tool_call("orchestrator_plan_task", args)
            
            # Should route to old handler
            assert len(result) == 1
            mock_use_case.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_tool_call_new_handler(self):
        """Test tool routing to new handler."""
        # Enable new handler
        manager = get_migration_manager()
        manager.enable_handler("orchestrator_plan_task")
        
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock successful task creation
            from mcp_task_orchestrator.domain.entities.task import Task, TaskType, TaskStatus
            from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
            from datetime import datetime
            
            mock_task = Task(
                task_id="test-123",
                title="Test Task",
                description="Test Description",
                task_type=TaskType.STANDARD,
                status=TaskStatus.PLANNED,
                complexity=ComplexityLevel.MODERATE,
                specialist_type="developer",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_use_case.create_task.return_value = mock_task
            
            args = {
                "title": "Test Task",
                "description": "Test Description"
            }
            
            result = await route_tool_call("orchestrator_plan_task", args)
            
            # Should route to new handler and return JSON response
            assert len(result) == 1
            mock_use_case.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_route_tool_call_error_handling(self):
        """Test error handling in tool routing."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.migration_config.get_handler_for_tool') as mock_get_handler:
            # Mock handler that raises exception
            mock_handler = AsyncMock()
            mock_handler.side_effect = Exception("Handler error")
            mock_get_handler.return_value = mock_handler
            
            args = {"test": "data"}
            
            result = await route_tool_call("orchestrator_plan_task", args)
            
            # Should return error response instead of raising
            assert len(result) == 1
            assert "error" in result[0].text
    
    def test_get_handler_migration_info(self):
        """Test getting handler migration information."""
        info = get_handler_migration_info()
        
        assert isinstance(info, dict)
        assert "migration_status" in info
        assert "description" in info
        assert "configuration" in info
        assert "global_flag" in info["configuration"]
        assert "individual_flags" in info["configuration"]


class TestEnvironmentVariableHandling:
    """Test environment variable configuration handling."""
    
    def test_case_insensitive_flags(self):
        """Test that environment flags are case insensitive."""
        test_cases = ["true", "True", "TRUE", "TrUe"]
        
        for value in test_cases:
            with patch.dict(os.environ, {"MCP_USE_PYDANTIC_HANDLERS": value}):
                manager = HandlerMigrationManager()
                assert manager.handler_configs["orchestrator_plan_task"].use_new == True
    
    def test_false_values(self):
        """Test various false values for environment flags."""
        test_cases = ["false", "False", "FALSE", "0", "", "no", "off"]
        
        for value in test_cases:
            with patch.dict(os.environ, {"MCP_USE_PYDANTIC_HANDLERS": value}):
                manager = HandlerMigrationManager()
                assert manager.handler_configs["orchestrator_plan_task"].use_new == False
    
    def test_global_flag_overrides_individual(self):
        """Test that global flag overrides individual flags."""
        with patch.dict(os.environ, {
            "MCP_USE_PYDANTIC_HANDLERS": "true",
            "MCP_USE_PYDANTIC_CREATE_TASK": "false"  # Should be overridden
        }):
            manager = HandlerMigrationManager()
            
            # Global flag should override individual flag
            assert manager.handler_configs["orchestrator_plan_task"].use_new == True


class TestBackwardCompatibility:
    """Test backward compatibility during migration."""
    
    @pytest.mark.asyncio
    async def test_old_handler_still_works(self):
        """Test that old handlers continue to work during migration."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock task
            mock_task = Mock()
            mock_task.dict.return_value = {"task_id": "test-123"}
            mock_use_case.create_task.return_value = mock_task
            
            # Get old handler directly
            handler = get_handler_for_tool("orchestrator_plan_task")
            
            args = {"title": "Test", "description": "Test"}
            result = await handler(args)
            
            assert len(result) == 1
            mock_use_case.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_new_handler_with_old_args(self):
        """Test that new handlers can handle arguments from old format."""
        # Enable new handler
        manager = get_migration_manager()
        manager.enable_handler("orchestrator_plan_task")
        
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            from mcp_task_orchestrator.domain.entities.task import Task, TaskType, TaskStatus
            from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
            from datetime import datetime
            
            mock_task = Task(
                task_id="test-123",
                title="Test Task",
                description="Test Description",
                task_type=TaskType.STANDARD,
                status=TaskStatus.PLANNED,
                complexity=ComplexityLevel.MODERATE,
                specialist_type="developer",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_use_case.create_task.return_value = mock_task
            
            # Use old-style arguments that should still work
            args = {
                "title": "Test Task",
                "description": "Test Description",
                "complexity_level": "moderate",  # Old naming
                "subtasks_json": "[]",  # Old field
                "context": "test context"  # Old field
            }
            
            handler = get_handler_for_tool("orchestrator_plan_task")
            result = await handler(args)
            
            # Should work despite using old argument names
            assert len(result) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])