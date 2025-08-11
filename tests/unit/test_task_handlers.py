"""
Unit tests for task handlers (execute_task and complete_task).

Tests the new MCP handlers that replaced the legacy subtask handlers.
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from mcp import types

# Import the handlers to test
# from mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers import  # TODO: Complete this import


class TestHandleExecuteTask:
    """Test cases for handle_execute_task handler."""
    
    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test that execute_task returns specialist context successfully."""
        # Test input
        args = {"task_id": "valid-task-id"}
        
        # Call the handler
        result = await handle_execute_task(args)
        
        # Verify response structure
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        
        # Parse the JSON response
        response = json.loads(result[0].text)
        
        # Verify response content
        assert response["status"] == "ready_for_execution"
        assert response["task_id"] == "valid-task-id"
        assert "specialist_context" in response
        assert "specialist_prompts" in response
        assert "execution_instructions" in response
        assert "dependencies_completed" in response
        assert "next_steps" in response
    
    @pytest.mark.asyncio
    async def test_execute_task_missing_id(self):
        """Test that execute_task fails without task_id."""
        # Test input with missing task_id
        args = {}
        
        # Call the handler
        result = await handle_execute_task(args)
        
        # Verify error response
        assert isinstance(result, list)
        assert len(result) == 1
        
        response = json.loads(result[0].text)
        assert "error" in response
        assert "task_id" in response["error"]
        assert response["required"] == ["task_id"]
    
    @pytest.mark.asyncio
    async def test_execute_task_invalid_id(self):
        """Test execute_task with invalid task_id format."""
        # Test input with invalid task_id
        args = {"task_id": ""}
        
        # Call the handler
        result = await handle_execute_task(args)
        
        # Should still attempt to process but may fail in use case
        assert isinstance(result, list)
        assert len(result) == 1
        
        response = json.loads(result[0].text)
        # Could be success with mock or error depending on implementation
        assert "status" in response or "error" in response


class TestHandleCompleteTask:
    """Test cases for handle_complete_task handler."""
    
    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test that complete_task stores artifacts successfully."""
        # Test input with all required fields
        args = {
            "task_id": "valid-task-id",
            "summary": "Task completed successfully",
            "detailed_work": "Detailed implementation work was completed...",
            "next_action": "complete",
            "artifact_type": "code"
        }
        
        # Call the handler
        result = await handle_complete_task(args)
        
        # Verify response structure
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        
        # Parse the JSON response
        response = json.loads(result[0].text)
        
        # Verify response content
        assert response["status"] == "success"
        assert response["task_id"] == "valid-task-id"
        assert response["summary"] == "Task completed successfully"
        assert "artifact_count" in response
        assert "artifact_references" in response
        assert response["next_action"] == "complete"
        assert "completion_time" in response
        assert "next_steps" in response
    
    @pytest.mark.asyncio
    async def test_complete_task_missing_required_fields(self):
        """Test that complete_task fails with missing required fields."""
        # Test cases with missing required fields
        test_cases = [
            # Missing task_id
            {
                "summary": "Test summary",
                "detailed_work": "Test work",
                "next_action": "complete"
            },
            # Missing summary
            {
                "task_id": "test-id",
                "detailed_work": "Test work", 
                "next_action": "complete"
            },
            # Missing detailed_work
            {
                "task_id": "test-id",
                "summary": "Test summary",
                "next_action": "complete"
            },
            # Missing next_action
            {
                "task_id": "test-id",
                "summary": "Test summary",
                "detailed_work": "Test work"
            }
        ]
        
        for args in test_cases:
            # Call the handler
            result = await handle_complete_task(args)
            
            # Verify error response
            assert isinstance(result, list)
            assert len(result) == 1
            
            response = json.loads(result[0].text)
            assert "error" in response
            assert "Missing required fields" in response["error"] or "Missing required field" in response["error"]
    
    @pytest.mark.asyncio
    async def test_complete_task_invalid_next_action(self):
        """Test complete_task with invalid next_action value."""
        # Test input with invalid next_action
        args = {
            "task_id": "valid-task-id",
            "summary": "Task completed",
            "detailed_work": "Work details",
            "next_action": "invalid_action"  # Invalid value
        }
        
        # Call the handler
        result = await handle_complete_task(args)
        
        # Should return error for invalid next_action
        assert isinstance(result, list)
        assert len(result) == 1
        
        response = json.loads(result[0].text)
        # Should have error about invalid next_action
        assert "error" in response
    
    @pytest.mark.asyncio 
    async def test_complete_task_with_optional_fields(self):
        """Test complete_task with optional fields included."""
        # Test input with optional fields
        args = {
            "task_id": "valid-task-id",
            "summary": "Task completed with artifacts",
            "detailed_work": "Comprehensive work output with code and documentation",
            "next_action": "complete",
            "artifact_type": "documentation",
            "file_paths": ["/path/to/file1.py", "/path/to/file2.md"],
            "legacy_artifacts": ["artifact1", "artifact2"]
        }
        
        # Call the handler
        result = await handle_complete_task(args)
        
        # Verify successful response
        assert isinstance(result, list)
        assert len(result) == 1
        
        response = json.loads(result[0].text)
        assert response["status"] == "success"
        assert response["task_id"] == "valid-task-id"
        assert "artifact_count" in response
        assert "completion_time" in response


class TestHandlerIntegration:
    """Integration tests for task handlers working together."""
    
    @pytest.mark.asyncio
    async def test_execute_then_complete_workflow(self):
        """Test the workflow of executing then completing a task."""
        task_id = "workflow-test-task"
        
        # Step 1: Execute the task
        execute_args = {"task_id": task_id}
        execute_result = await handle_execute_task(execute_args)
        
        execute_response = json.loads(execute_result[0].text)
        assert execute_response["status"] == "ready_for_execution"
        assert execute_response["task_id"] == task_id
        
        # Step 2: Complete the task
        complete_args = {
            "task_id": task_id,
            "summary": "Workflow test completed",
            "detailed_work": "Both execute and complete handlers work correctly",
            "next_action": "complete"
        }
        complete_result = await handle_complete_task(complete_args)
        
        complete_response = json.loads(complete_result[0].text)
        assert complete_response["status"] == "success"
        assert complete_response["task_id"] == task_id
        assert complete_response["next_action"] == "complete"
    
    @pytest.mark.asyncio
    async def test_handlers_error_format_consistency(self):
        """Test that both handlers return consistent error formats."""
        # Test execute_task error
        execute_result = await handle_execute_task({})
        execute_response = json.loads(execute_result[0].text)
        
        # Test complete_task error  
        complete_result = await handle_complete_task({})
        complete_response = json.loads(complete_result[0].text)
        
        # Both should have consistent error structure
        assert "error" in execute_response
        assert "error" in complete_response
        assert "required" in execute_response or "received" in execute_response
        assert "required" in complete_response or "received" in complete_response


if __name__ == "__main__":
    # Run tests if called directly
    import subprocess
    import sys
    
    # Run with pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    sys.exit(result.returncode)