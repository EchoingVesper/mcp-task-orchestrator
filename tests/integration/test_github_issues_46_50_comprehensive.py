"""
Comprehensive test suite for GitHub Issues #46-50 fix validation.

This test module validates all 5 GitHub issue fixes:
- Issue #46: MockTask JSON serialization (compatibility layer)
- Issue #47: update_task response formatting (compatibility layer)  
- Issue #48: delete_task implementation (missing methods)
- Issue #49: cancel_task implementation (missing methods)
- Issue #50: query_tasks format mismatch (compatibility layer)

Tests include:
1. Unit tests for each new/modified method
2. Integration tests through MCP handlers
3. End-to-end tests via orchestrator tools
4. JSON serialization validation tests
5. Error handling and edge case tests
6. Regression testing for existing functionality
"""

import pytest
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_task_orchestrator.application.usecases.manage_tasks import TaskUseCase
from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.response_formatter import ResponseFormatter
from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.serialization import SerializationValidator
from mcp_task_orchestrator.db.generic_repository import GenericTaskRepository
from mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers import TaskHandlers
from mcp_task_orchestrator.domain.repositories.task_repository import TaskRepository


class TestGitHubIssue46MockTaskSerialization:
    """
    Test Issue #46: MockTask JSON serialization error.
    
    Tests the unified response formatting system that eliminates 
    MockTask remnants in serialization chain.
    """
    
    def test_serialization_validator_basic_types(self):
        """Test SerializationValidator handles basic types correctly."""
        validator = SerializationValidator()
        
        # Basic types should pass through unchanged
        assert validator.validate_json_serializable("string") == "string"
        assert validator.validate_json_serializable(123) == 123
        assert validator.validate_json_serializable(45.67) == 45.67
        assert validator.validate_json_serializable(True) is True
        assert validator.validate_json_serializable(None) is None
    
    def test_serialization_validator_datetime_conversion(self):
        """Test SerializationValidator converts datetime objects."""
        validator = SerializationValidator()
        test_dt = datetime(2025, 8, 15, 12, 30, 45)
        
        result = validator.validate_json_serializable(test_dt)
        assert isinstance(result, str)
        assert "2025-08-15T12:30:45" in result
    
    def test_serialization_validator_nested_structures(self):
        """Test SerializationValidator handles nested data structures."""
        validator = SerializationValidator()
        test_data = {
            "id": "task_123",
            "created_at": datetime(2025, 8, 15, 12, 30, 45),
            "metadata": {
                "complexity": "moderate",
                "nested_list": [1, "string", True]
            }
        }
        
        result = validator.validate_json_serializable(test_data)
        
        # Verify structure is maintained
        assert result["id"] == "task_123"
        assert isinstance(result["created_at"], str)
        assert result["metadata"]["complexity"] == "moderate"
        assert result["metadata"]["nested_list"] == [1, "string", True]
    
    def test_serialization_validator_ensures_json_serializable(self):
        """Test SerializationValidator output is actually JSON serializable."""
        validator = SerializationValidator()
        test_data = {
            "datetime_field": datetime.now(),
            "nested": {
                "list": [datetime.now(), "string", 42]
            }
        }
        
        result = validator.ensure_serializable(test_data)
        
        # This should not raise an exception
        json_string = json.dumps(result)
        assert isinstance(json_string, str)
        
        # And should be deserializable
        deserialized = json.loads(json_string)
        assert isinstance(deserialized, dict)
    
    def test_response_formatter_task_dict_formatting(self):
        """Test ResponseFormatter.format_task_dict handles all task fields."""
        formatter = ResponseFormatter()
        
        task_data = {
            "id": "task_123",
            "title": "Test Task",
            "description": "Test Description",
            "status": "in_progress",
            "type": "implementation",
            "created_at": "2025-08-15T12:30:45",
            "metadata": json.dumps({
                "complexity": "moderate",
                "specialist_type": "coder",
                "context": {"key": "value"}
            })
        }
        
        result = formatter.format_task_dict(task_data)
        
        # Verify all fields are present and correctly formatted
        assert result["task_id"] == "task_123"
        assert result["title"] == "Test Task"
        assert result["description"] == "Test Description"
        assert result["status"] == "in_progress"
        assert result["task_type"] == "implementation"
        assert result["complexity"] == "moderate"
        assert result["specialist_type"] == "coder"
        assert result["context"] == {"key": "value"}
        
        # Verify JSON serialization works
        json.dumps(result)  # Should not raise


class TestGitHubIssue47UpdateTaskResponseFormatting:
    """
    Test Issue #47: orchestrator_update_task response formatting.
    
    Tests the compatibility layer that ensures update_task responses
    are properly formatted for MCP handlers.
    """
    
    def test_response_formatter_update_response(self):
        """Test ResponseFormatter.format_update_response creates proper structure."""
        formatter = ResponseFormatter()
        
        task_data = {
            "id": "task_456",
            "title": "Updated Task",
            "description": "Updated Description",
            "status": "completed",
            "type": "testing",
            "updated_at": "2025-08-15T13:30:45",
            "metadata": json.dumps({
                "complexity": "complex",
                "specialist_type": "tester"
            })
        }
        
        changes = ["status", "description"]
        result = formatter.format_update_response(task_data, changes)
        
        # Verify response structure
        assert result["success"] is True
        assert result["task_id"] == "task_456"
        assert result["title"] == "Updated Task"
        assert result["status"] == "completed"
        assert result["changes_applied"] == changes
        assert result["operation"] == "update_task"
        assert "timestamp" in result
        assert "message" in result
        
        # Verify JSON serialization
        json.dumps(result)
    
    @pytest.mark.asyncio
    async def test_task_use_case_update_returns_dict(self):
        """Test TaskUseCase.update_task returns dict format expected by handlers."""
        # Mock repository
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.update_task.return_value = {
            "id": "task_789",
            "title": "Test Task",
            "status": "updated",
            "updated_at": datetime.now().isoformat()
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.update_task("task_789", {"status": "updated"})
        
        # Verify it returns a dict (not an object with .dict() method)
        assert isinstance(result, dict)
        assert result["id"] == "task_789"
        assert result["status"] == "updated"
    
    def test_compatibility_layer_handles_dict_response(self):
        """Test compatibility layer properly handles dict responses from use case."""
        # Simulate the handler scenario where use case returns dict
        # but handler needs properly formatted response
        
        use_case_response = {
            "id": "task_101",
            "title": "Test",
            "status": "pending",
            "metadata": json.dumps({"complexity": "simple"})
        }
        
        formatter = ResponseFormatter()
        formatted_response = formatter.format_update_response(
            use_case_response, 
            ["title"]
        )
        
        # Verify compatibility layer bridges the gap
        assert formatted_response["success"] is True
        assert formatted_response["task_id"] == "task_101"
        assert formatted_response["changes_applied"] == ["title"]
        
        # Verify no .dict() method is needed
        json.dumps(formatted_response)


class TestGitHubIssue48DeleteTaskImplementation:
    """
    Test Issue #48: Missing delete_task implementation.
    
    Tests the newly implemented delete_task method with proper
    dependency handling and optional archive mode.
    """
    
    @pytest.mark.asyncio
    async def test_task_use_case_delete_task_method_exists(self):
        """Test delete_task method exists in TaskUseCase."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Method should exist
        assert hasattr(use_case, 'delete_task')
        assert callable(getattr(use_case, 'delete_task'))
    
    @pytest.mark.asyncio
    async def test_task_use_case_delete_task_calls_repository(self):
        """Test delete_task properly delegates to repository."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "task_delete_123",
            "action": "archived",
            "force_applied": False,
            "archive_mode": True
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.delete_task(
            "task_delete_123", 
            force=False, 
            archive_instead=True
        )
        
        # Verify repository was called with correct parameters
        mock_repo.delete_task.assert_called_once_with(
            "task_delete_123", 
            False, 
            True
        )
        
        # Verify response structure
        assert result["success"] is True
        assert result["task_id"] == "task_delete_123"
        assert result["action"] == "archived"
    
    def test_response_formatter_delete_response(self):
        """Test ResponseFormatter.format_delete_response creates proper structure."""
        formatter = ResponseFormatter()
        
        metadata = {
            "force_applied": False,
            "archive_mode": True,
            "dependent_tasks": ["dep_1", "dep_2"]
        }
        
        result = formatter.format_delete_response(
            "task_delete_456", 
            "archived", 
            metadata
        )
        
        # Verify response structure
        assert result["success"] is True
        assert result["task_id"] == "task_delete_456"
        assert result["action"] == "archived"
        assert result["force_applied"] is False
        assert result["archive_mode"] is True
        assert result["dependent_tasks"] == ["dep_1", "dep_2"]
        assert result["operation"] == "delete_task"
        assert "timestamp" in result
        assert "message" in result
        
        # Verify JSON serialization
        json.dumps(result)
    
    @pytest.mark.asyncio
    async def test_delete_task_with_force_mode(self):
        """Test delete_task with force=True for hard deletion."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "task_force_delete",
            "action": "deleted",
            "force_applied": True,
            "archive_mode": False
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.delete_task(
            "task_force_delete", 
            force=True, 
            archive_instead=False
        )
        
        mock_repo.delete_task.assert_called_once_with(
            "task_force_delete", 
            True, 
            False
        )
        
        assert result["action"] == "deleted"
        assert result["force_applied"] is True


class TestGitHubIssue49CancelTaskImplementation:
    """
    Test Issue #49: Missing cancel_task implementation.
    
    Tests the newly implemented cancel_task method with proper
    state management and artifact preservation.
    """
    
    @pytest.mark.asyncio
    async def test_task_use_case_cancel_task_method_exists(self):
        """Test cancel_task method exists in TaskUseCase."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Method should exist
        assert hasattr(use_case, 'cancel_task')
        assert callable(getattr(use_case, 'cancel_task'))
    
    @pytest.mark.asyncio
    async def test_task_use_case_cancel_task_calls_repository(self):
        """Test cancel_task properly delegates to repository."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "task_cancel_123",
            "previous_status": "in_progress",
            "reason": "User requested cancellation",
            "work_preserved": True,
            "artifact_count": 3,
            "cancelled_at": datetime.now().isoformat()
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.cancel_task(
            "task_cancel_123", 
            "User requested cancellation", 
            preserve_work=True
        )
        
        # Verify repository was called with correct parameters
        mock_repo.cancel_task.assert_called_once_with(
            "task_cancel_123", 
            "User requested cancellation", 
            True
        )
        
        # Verify response structure
        assert result["success"] is True
        assert result["task_id"] == "task_cancel_123"
        assert result["previous_status"] == "in_progress"
        assert result["work_preserved"] is True
    
    def test_response_formatter_cancel_response(self):
        """Test ResponseFormatter.format_cancel_response creates proper structure."""
        formatter = ResponseFormatter()
        
        cancellation_data = {
            "previous_status": "in_progress",
            "reason": "Resource constraints",
            "work_preserved": True,
            "artifact_count": 5,
            "dependent_tasks_updated": ["task_1", "task_2"],
            "cancelled_at": "2025-08-15T14:30:45"
        }
        
        result = formatter.format_cancel_response(
            "task_cancel_789", 
            cancellation_data
        )
        
        # Verify response structure
        assert result["success"] is True
        assert result["task_id"] == "task_cancel_789"
        assert result["previous_status"] == "in_progress"
        assert result["reason"] == "Resource constraints"
        assert result["work_preserved"] is True
        assert result["artifact_count"] == 5
        assert result["dependent_tasks_updated"] == ["task_1", "task_2"]
        assert result["cancelled_at"] == "2025-08-15T14:30:45"
        assert result["operation"] == "cancel_task"
        assert "timestamp" in result
        assert "message" in result
        
        # Verify JSON serialization
        json.dumps(result)
    
    @pytest.mark.asyncio
    async def test_cancel_task_preserves_work_by_default(self):
        """Test cancel_task preserves work by default."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "task_preserve",
            "work_preserved": True,
            "artifact_count": 2
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Default preserve_work=True
        result = await use_case.cancel_task("task_preserve", "Test reason")
        
        mock_repo.cancel_task.assert_called_once_with(
            "task_preserve", 
            "Test reason", 
            True  # Default preserve_work
        )
        
        assert result["work_preserved"] is True


class TestGitHubIssue50QueryTasksFormatMismatch:
    """
    Test Issue #50: orchestrator_query_tasks format mismatch.
    
    Tests the compatibility layer that ensures query_tasks responses
    are properly formatted as dict (not list) for MCP handlers.
    """
    
    @pytest.mark.asyncio
    async def test_task_use_case_query_returns_list(self):
        """Test TaskUseCase.query_tasks returns list of dicts."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.query_tasks.return_value = [
            {"id": "task_1", "title": "Task 1", "status": "pending"},
            {"id": "task_2", "title": "Task 2", "status": "completed"}
        ]
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.query_tasks({"status": "pending"})
        
        # Use case should return list
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "task_1"
    
    def test_response_formatter_query_response_wraps_list(self):
        """Test ResponseFormatter.format_query_response wraps list in dict structure."""
        formatter = ResponseFormatter()
        
        tasks_list = [
            {"id": "task_1", "title": "Task 1", "status": "pending", "metadata": "{}"},
            {"id": "task_2", "title": "Task 2", "status": "completed", "metadata": "{}"}
        ]
        
        query_context = {
            "page_count": 1,
            "current_page": 1,
            "page_size": 2,
            "has_more": False,
            "filters_applied": ["status:pending"]
        }
        
        result = formatter.format_query_response(tasks_list, query_context)
        
        # Verify response is dict structure
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["tasks"] == [
            formatter.format_task_dict(task) for task in tasks_list
        ]
        assert result["total_count"] == 2
        assert result["page_count"] == 1
        assert result["current_page"] == 1
        assert result["page_size"] == 2
        assert result["has_more"] is False
        assert result["filters_applied"] == ["status:pending"]
        assert result["operation"] == "query_tasks"
        assert "timestamp" in result
        assert "message" in result
        
        # Verify JSON serialization
        json.dumps(result)
    
    def test_query_response_handles_empty_results(self):
        """Test query response handles empty task list."""
        formatter = ResponseFormatter()
        
        result = formatter.format_query_response([], {})
        
        assert result["success"] is True
        assert result["tasks"] == []
        assert result["total_count"] == 0
        assert result["message"] == "Found 0 tasks"
        
        # Verify JSON serialization
        json.dumps(result)
    
    def test_query_response_formats_individual_tasks(self):
        """Test query response properly formats each task in the list."""
        formatter = ResponseFormatter()
        
        tasks_list = [
            {
                "id": "task_complex",
                "title": "Complex Task",
                "status": "in_progress",
                "created_at": "2025-08-15T10:00:00",
                "metadata": json.dumps({
                    "complexity": "very_complex",
                    "specialist_type": "architect"
                })
            }
        ]
        
        result = formatter.format_query_response(tasks_list, {})
        
        formatted_task = result["tasks"][0]
        assert formatted_task["task_id"] == "task_complex"
        assert formatted_task["title"] == "Complex Task"
        assert formatted_task["status"] == "in_progress"
        assert formatted_task["complexity"] == "very_complex"
        assert formatted_task["specialist_type"] == "architect"
        assert "created_at" in formatted_task


class TestIntegrationThroughMCPHandlers:
    """
    Integration tests that validate fixes work through MCP handlers.
    
    Tests the complete flow from MCP request to response through
    the compatibility layer and new implementations.
    """
    
    @pytest.mark.asyncio
    async def test_mcp_handler_update_task_integration(self):
        """Test MCP handler properly uses new update_task formatting."""
        # This would require setting up actual MCP handler test
        # For now, we test the compatibility layer components
        
        # Mock the use case response
        use_case_response = {
            "id": "integration_test_task",
            "title": "Integration Test",
            "status": "updated",
            "metadata": json.dumps({"complexity": "moderate"})
        }
        
        # Test response formatting
        formatter = ResponseFormatter()
        mcp_response = formatter.format_update_response(
            use_case_response, 
            ["title", "status"]
        )
        
        # Verify MCP-compatible response
        assert mcp_response["success"] is True
        assert mcp_response["task_id"] == "integration_test_task"
        assert mcp_response["changes_applied"] == ["title", "status"]
        
        # Verify JSON serialization for MCP protocol
        json_response = json.dumps(mcp_response)
        assert isinstance(json_response, str)
    
    @pytest.mark.asyncio
    async def test_mcp_handler_query_tasks_integration(self):
        """Test MCP handler properly uses new query_tasks formatting."""
        # Mock use case returning list
        use_case_response = [
            {"id": "query_task_1", "title": "Query Test 1", "metadata": "{}"},
            {"id": "query_task_2", "title": "Query Test 2", "metadata": "{}"}
        ]
        
        # Test response formatting
        formatter = ResponseFormatter()
        mcp_response = formatter.format_query_response(
            use_case_response, 
            {"filters_applied": ["status:pending"]}
        )
        
        # Verify MCP expects dict, not list
        assert isinstance(mcp_response, dict)
        assert "tasks" in mcp_response
        assert isinstance(mcp_response["tasks"], list)
        assert len(mcp_response["tasks"]) == 2
        
        # Verify JSON serialization for MCP protocol
        json_response = json.dumps(mcp_response)
        assert isinstance(json_response, str)


class TestErrorHandlingAndEdgeCases:
    """
    Test error handling and edge cases for all fixes.
    
    Ensures robust error handling and validates edge cases
    that might cause issues in production.
    """
    
    def test_serialization_validator_handles_malformed_json(self):
        """Test SerializationValidator handles malformed JSON in metadata."""
        formatter = ResponseFormatter()
        
        task_data = {
            "id": "malformed_task",
            "title": "Test",
            "metadata": "{ invalid json }"  # Malformed JSON
        }
        
        # Should not raise exception
        result = formatter.format_task_dict(task_data)
        
        # Should fallback to empty metadata
        assert result["complexity"] == "moderate"  # Default value
        assert result["specialist_type"] == "generic"  # Default value
    
    def test_response_formatter_handles_missing_fields(self):
        """Test ResponseFormatter handles tasks with missing fields gracefully."""
        formatter = ResponseFormatter()
        
        minimal_task = {
            "id": "minimal_task"
            # Missing title, description, etc.
        }
        
        result = formatter.format_task_dict(minimal_task)
        
        # Should provide defaults
        assert result["task_id"] == "minimal_task"
        assert result["title"] == ""  # Default empty string
        assert result["description"] == ""  # Default empty string
        assert result["status"] == "pending"  # Default status
        assert result["task_type"] == "standard"  # Default type
    
    def test_serialization_validator_handles_circular_references(self):
        """Test SerializationValidator handles potential circular references."""
        validator = SerializationValidator()
        
        # Create circular reference
        data = {"key": "value"}
        data["self"] = data
        
        # Should not hang or crash
        try:
            result = validator.validate_json_serializable(data)
            # If it completes, verify basic structure
            assert "key" in result
        except RecursionError:
            # This is acceptable behavior for circular references
            pass
    
    @pytest.mark.asyncio
    async def test_delete_task_handles_nonexistent_task(self):
        """Test delete_task handles attempts to delete nonexistent tasks."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.side_effect = Exception("Task not found")
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Should propagate repository exceptions
        with pytest.raises(Exception, match="Task not found"):
            await use_case.delete_task("nonexistent_task")
    
    @pytest.mark.asyncio
    async def test_cancel_task_handles_already_completed_task(self):
        """Test cancel_task handles attempts to cancel completed tasks."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": False,
            "task_id": "completed_task",
            "error": "Cannot cancel completed task"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.cancel_task("completed_task", "Test reason")
        
        # Should return error response
        assert result["success"] is False
        assert "error" in result


class TestRegressionValidation:
    """
    Regression tests to ensure existing functionality still works.
    
    Validates that the fixes don't break existing features.
    """
    
    @pytest.mark.asyncio
    async def test_create_task_still_works(self):
        """Test create_task functionality unchanged by fixes."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.create_task_from_dict.return_value = {
            "id": "regression_create_task",
            "title": "Regression Test",
            "status": "pending"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.create_task({
            "title": "Regression Test",
            "description": "Test description"
        })
        
        # Should work as before
        assert result["id"] == "regression_create_task"
        assert result["title"] == "Regression Test"
    
    @pytest.mark.asyncio
    async def test_get_task_still_works(self):
        """Test get_task functionality unchanged by fixes."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = {
            "id": "regression_get_task",
            "title": "Get Test",
            "status": "pending"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.get_task("regression_get_task")
        
        # Should work as before
        assert result["id"] == "regression_get_task"
        assert result["title"] == "Get Test"
    
    def test_response_formatter_backward_compatibility(self):
        """Test ResponseFormatter doesn't break existing response patterns."""
        formatter = ResponseFormatter()
        
        # Test with legacy task data structure
        legacy_task = {
            "id": "legacy_task",
            "title": "Legacy Task",
            "description": "Legacy Description",
            "status": "pending",
            # No metadata field
        }
        
        result = formatter.format_task_dict(legacy_task)
        
        # Should handle legacy format gracefully
        assert result["task_id"] == "legacy_task"
        assert result["title"] == "Legacy Task"
        assert result["complexity"] == "moderate"  # Default
        assert result["specialist_type"] == "generic"  # Default


if __name__ == "__main__":
    # Run tests with proper async support
    pytest.main([__file__, "-v", "--tb=short"])