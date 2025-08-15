"""
Test suite for GitHub Issues #46, #47, #50: Compatibility Layer Implementation

This test module validates the compatibility layer fixes:
- Issue #46: MockTask JSON serialization (compatibility layer)
- Issue #47: update_task response formatting (compatibility layer)  
- Issue #50: query_tasks format mismatch (compatibility layer)

Tests focus on:
1. Response formatter functionality
2. JSON serialization validation
3. Compatibility layer bridging use case responses to MCP handler expectations
4. Error handling and edge cases
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

from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.response_formatter import ResponseFormatter
from mcp_task_orchestrator.infrastructure.mcp.handlers.compatibility.serialization import SerializationValidator
from mcp_task_orchestrator.application.usecases.manage_tasks import TaskUseCase
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
    
    def test_serialization_validator_handles_missing_fields(self):
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
    
    def test_update_response_with_empty_changes(self):
        """Test update response formatter handles empty changes list."""
        formatter = ResponseFormatter()
        
        task_data = {
            "id": "no_changes_task",
            "title": "Unchanged Task",
            "status": "pending"
        }
        
        result = formatter.format_update_response(task_data, [])
        
        assert result["success"] is True
        assert result["task_id"] == "no_changes_task"
        assert result["changes_applied"] == []
        assert "No changes applied" in result["message"] or "updated successfully" in result["message"]
    
    def test_update_response_with_timestamp_fields(self):
        """Test update response properly handles various timestamp fields."""
        formatter = ResponseFormatter()
        
        task_data = {
            "id": "timestamp_task",
            "title": "Timestamp Task",
            "created_at": "2025-08-15T10:00:00",
            "updated_at": "2025-08-15T12:00:00",
            "completed_at": None
        }
        
        result = formatter.format_update_response(task_data, ["title"])
        
        assert result["task_id"] == "timestamp_task"
        assert "updated_at" in result
        # Should handle null/None values gracefully
        json.dumps(result)


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
    
    def test_query_response_with_pagination_context(self):
        """Test query response includes pagination metadata."""
        formatter = ResponseFormatter()
        
        tasks_list = [{"id": f"task_{i}", "metadata": "{}"} for i in range(5)]
        
        pagination_context = {
            "page_count": 3,
            "current_page": 2,
            "page_size": 5,
            "has_more": True,
            "filters_applied": ["status:active", "type:implementation"],
            "metadata": {
                "total_matching": 15,
                "query_time_ms": 45
            }
        }
        
        result = formatter.format_query_response(tasks_list, pagination_context)
        
        # Verify pagination info
        assert result["total_count"] == 5  # Number of tasks in this page
        assert result["page_count"] == 3
        assert result["current_page"] == 2
        assert result["page_size"] == 5
        assert result["has_more"] is True
        assert result["filters_applied"] == ["status:active", "type:implementation"]
        assert result["query_metadata"]["total_matching"] == 15
        assert result["query_metadata"]["query_time_ms"] == 45


class TestCompatibilityLayerIntegration:
    """
    Integration tests for the compatibility layer components.
    """
    
    def test_response_formatter_handles_all_task_operations(self):
        """Test ResponseFormatter has methods for all task operations."""
        formatter = ResponseFormatter()
        
        # Should have formatters for all operations
        assert hasattr(formatter, 'format_task_dict')
        assert hasattr(formatter, 'format_create_response')
        assert hasattr(formatter, 'format_update_response')
        assert hasattr(formatter, 'format_query_response')
        assert hasattr(formatter, 'format_delete_response')
        assert hasattr(formatter, 'format_cancel_response')
    
    def test_serialization_validator_comprehensive_test(self):
        """Test SerializationValidator with complex mixed data."""
        validator = SerializationValidator()
        
        complex_data = {
            "string_field": "text",
            "int_field": 42,
            "float_field": 3.14,
            "bool_field": True,
            "none_field": None,
            "datetime_field": datetime(2025, 8, 15, 14, 30, 0),
            "nested_dict": {
                "inner_datetime": datetime(2025, 8, 15, 15, 0, 0),
                "inner_list": [1, "text", datetime(2025, 8, 15, 16, 0, 0)]
            },
            "list_field": [
                datetime(2025, 8, 15, 17, 0, 0),
                {"nested_datetime": datetime(2025, 8, 15, 18, 0, 0)}
            ]
        }
        
        result = validator.ensure_serializable(complex_data)
        
        # Should be fully JSON serializable
        json_str = json.dumps(result)
        parsed = json.loads(json_str)
        
        # Verify structure preserved
        assert parsed["string_field"] == "text"
        assert parsed["int_field"] == 42
        assert parsed["bool_field"] is True
        assert parsed["none_field"] is None
        
        # Verify datetime fields converted to strings
        assert isinstance(parsed["datetime_field"], str)
        assert isinstance(parsed["nested_dict"]["inner_datetime"], str)
        assert isinstance(parsed["list_field"][0], str)
        assert isinstance(parsed["list_field"][1]["nested_datetime"], str)
    
    def test_response_formatters_produce_consistent_structure(self):
        """Test all response formatters produce consistent base structure."""
        formatter = ResponseFormatter()
        
        base_task = {
            "id": "consistency_task",
            "title": "Consistency Test",
            "status": "pending",
            "metadata": "{}"
        }
        
        # Test all response types
        create_response = formatter.format_create_response(base_task)
        update_response = formatter.format_update_response(base_task, ["title"])
        query_response = formatter.format_query_response([base_task], {})
        delete_response = formatter.format_delete_response("consistency_task", "archived", {})
        cancel_response = formatter.format_cancel_response("consistency_task", {"reason": "test"})
        
        # All should have consistent base fields
        for response in [create_response, update_response, query_response, delete_response, cancel_response]:
            assert "success" in response
            assert "operation" in response
            assert "timestamp" in response
            # All should be JSON serializable
            json.dumps(response)


class TestCompatibilityLayerErrorHandling:
    """
    Test error handling and edge cases in compatibility layer.
    """
    
    def test_serialization_validator_handles_circular_references(self):
        """Test SerializationValidator handles potential circular references safely."""
        validator = SerializationValidator()
        
        # Create circular reference
        data = {"key": "value"}
        data["self"] = data
        
        # Should either handle gracefully or fail predictably
        try:
            result = validator.validate_json_serializable(data)
            # If it completes, verify basic structure
            assert "key" in result
        except RecursionError:
            # This is acceptable behavior for circular references
            pass
        except Exception as e:
            # Should not crash with other unexpected errors
            assert "recursion" in str(e).lower() or "circular" in str(e).lower()
    
    def test_response_formatter_handles_none_inputs(self):
        """Test ResponseFormatter handles None and missing inputs gracefully."""
        formatter = ResponseFormatter()
        
        # Test with None task data (should use defaults)
        result = formatter.format_task_dict({})
        assert result["task_id"] == ""
        assert result["title"] == ""
        assert result["status"] == "pending"
        
        # Test with None metadata
        result = formatter.format_task_dict({"id": "test", "metadata": None})
        assert result["task_id"] == "test"
        assert result["complexity"] == "moderate"  # Default
        
        # Should all be JSON serializable
        json.dumps(result)
    
    def test_timestamp_conversion_edge_cases(self):
        """Test timestamp conversion handles various formats."""
        validator = SerializationValidator()
        
        test_data = {
            "iso_string": "2025-08-15T12:00:00",
            "iso_with_z": "2025-08-15T12:00:00Z",
            "datetime_obj": datetime(2025, 8, 15, 12, 0, 0),
            "none_timestamp": None,
            "empty_string": "",
            "invalid_format": "not a timestamp"
        }
        
        result = validator.convert_timestamps(test_data)
        
        # Should handle all formats gracefully
        assert isinstance(result["iso_string"], str)
        assert isinstance(result["datetime_obj"], str)
        assert result["none_timestamp"] is None
        assert result["empty_string"] == ""
        # Invalid format should be preserved (validation is repository's responsibility)
        assert result["invalid_format"] == "not a timestamp"
        
        # Should be JSON serializable
        json.dumps(result)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])