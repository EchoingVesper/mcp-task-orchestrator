"""
Test Suite for Pydantic MCP Handlers.

Tests the new type-safe MCP handlers with Pydantic DTOs,
error handling integration, and validation scenarios.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any
from datetime import datetime
from mcp import types

# Import new Pydantic handlers
# from mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2 import  # TODO: Complete this import

# Import DTOs for validation
# from mcp_task_orchestrator.infrastructure.mcp.dto import  # TODO: Complete this import

# Import domain models and exceptions
from mcp_task_orchestrator.domain.entities.task import Task, TaskType, TaskStatus
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.exceptions import ValidationError, OrchestrationError


class TestCreateTaskHandler:
    """Test suite for handle_create_task_v2."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """Test successful task creation."""
        # Mock the use case
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Create mock task
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
            
            # Test valid request
            args = {
                "title": "Test Task",
                "description": "Test Description",
                "task_type": "STANDARD",
                "complexity": "moderate",
                "specialist_type": "developer"
            }
            
            result = await handle_create_task_v2(args)
            
            # Verify response structure
            assert len(result) == 1
            assert isinstance(result[0], types.TextContent)
            
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"
            assert response_data["task_id"] == "test-123"
            assert response_data["task_title"] == "Test Task"
            assert "next_steps" in response_data
            
            # Verify use case was called with correct data
            mock_use_case.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self):
        """Test task creation with validation errors."""
        # Test missing required fields
        args = {
            "description": "Missing title"
            # title is required but missing
        }
        
        result = await handle_create_task_v2(args)
        
        # Verify error response
        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
        assert "validation" in response_data["error"]["error"].lower()
    
    @pytest.mark.asyncio
    async def test_create_task_invalid_complexity(self):
        """Test task creation with invalid complexity level."""
        args = {
            "title": "Test Task",
            "description": "Test Description",
            "complexity": "invalid_complexity"  # Invalid value
        }
        
        result = await handle_create_task_v2(args)
        
        # Verify validation error response
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_create_task_orchestration_error(self):
        """Test task creation with orchestration service error."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock orchestration error
            mock_use_case.create_task.side_effect = OrchestrationError(
                "Service unavailable", 
                error_code="SERVICE_ERROR"
            )
            
            args = {
                "title": "Test Task",
                "description": "Test Description"
            }
            
            result = await handle_create_task_v2(args)
            
            # Verify error response
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "error"
            assert response_data["tool"] == "orchestrator_create_task"
            assert "recovery_suggestions" in response_data


class TestUpdateTaskHandler:
    """Test suite for handle_update_task_v2."""
    
    @pytest.mark.asyncio
    async def test_update_task_success(self):
        """Test successful task update."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Create mock updated task
            mock_task = Task(
                task_id="test-123",
                title="Updated Task",
                description="Updated Description",
                task_type=TaskType.STANDARD,
                status=TaskStatus.IN_PROGRESS,
                complexity=ComplexityLevel.MODERATE,
                specialist_type="developer",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_use_case.update_task.return_value = mock_task
            
            args = {
                "task_id": "test-123",
                "title": "Updated Task",
                "status": "IN_PROGRESS"
            }
            
            result = await handle_update_task_v2(args)
            
            # Verify response
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"
            assert response_data["task_id"] == "test-123"
            assert "title" in response_data["updated_fields"]
            assert "status" in response_data["updated_fields"]
    
    @pytest.mark.asyncio
    async def test_update_task_missing_task_id(self):
        """Test update with missing task_id."""
        args = {
            "title": "Updated Task"
            # task_id is required but missing
        }
        
        result = await handle_update_task_v2(args)
        
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_update_task_invalid_status(self):
        """Test update with invalid status value."""
        args = {
            "task_id": "test-123",
            "status": "INVALID_STATUS"
        }
        
        result = await handle_update_task_v2(args)
        
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"


class TestQueryTasksHandler:
    """Test suite for handle_query_tasks_v2."""
    
    @pytest.mark.asyncio
    async def test_query_tasks_success(self):
        """Test successful task query."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Create mock task for query results
            mock_task = Task(
                task_id="test-123",
                title="Test Task",
                description="Test Description",
                task_type=TaskType.STANDARD,
                status=TaskStatus.COMPLETED,
                complexity=ComplexityLevel.MODERATE,
                specialist_type="developer",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                subtask_ids=[],
                dependencies=[],
                tags=["test"],
                metadata={"source": "test"}
            )
            
            mock_query_result = {
                "tasks": [mock_task],
                "pagination": {
                    "total_count": 1,
                    "page_count": 1,
                    "current_page": 1,
                    "page_size": 20
                },
                "filters_applied": ["status"]
            }
            mock_use_case.query_tasks.return_value = mock_query_result
            
            args = {
                "status": "COMPLETED",
                "page": 1,
                "page_size": 20
            }
            
            result = await handle_query_tasks_v2(args)
            
            # Verify response
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"
            assert response_data["total_count"] == 1
            assert len(response_data["tasks"]) == 1
            assert response_data["tasks"][0]["task_id"] == "test-123"
            assert response_data["tasks"][0]["status"] == "COMPLETED"
    
    @pytest.mark.asyncio
    async def test_query_tasks_invalid_pagination(self):
        """Test query with invalid pagination parameters."""
        args = {
            "page": 0,  # Invalid: must be >= 1
            "page_size": 200  # Invalid: must be <= 100
        }
        
        result = await handle_query_tasks_v2(args)
        
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_query_tasks_date_filters(self):
        """Test query with date-based filters."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            mock_query_result = {
                "tasks": [],
                "pagination": {"total_count": 0, "page_count": 0},
                "filters_applied": ["created_after"]
            }
            mock_use_case.query_tasks.return_value = mock_query_result
            
            args = {
                "created_after": "2024-01-01T00:00:00Z",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
            
            result = await handle_query_tasks_v2(args)
            
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"


class TestCompleteTaskHandler:
    """Test suite for handle_complete_task_v2."""
    
    @pytest.mark.asyncio
    async def test_complete_task_success(self):
        """Test successful task completion."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_complete_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock completion response
            mock_completion = Mock()
            mock_completion.message = "Task completed successfully"
            mock_completion.summary = "Work completed"
            mock_completion.artifact_count = 2
            mock_completion.artifact_references = ["artifact1", "artifact2"]
            mock_completion.next_action = "Review results"
            mock_completion.duration_minutes = 45.5
            mock_completion.parent_progress = {"progress": "50%"}
            mock_completion.triggered_tasks = []
            
            mock_use_case.complete_task_with_artifacts.return_value = mock_completion
            
            args = {
                "task_id": "test-123",
                "summary": "Task completed successfully",
                "detailed_work": "Detailed work description",
                "next_action": "Review and validate results",
                "artifacts": [{"type": "code", "content": "example code"}],
                "completion_quality": 0.95
            }
            
            result = await handle_complete_task_v2(args)
            
            # Verify response
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"
            assert response_data["task_id"] == "test-123"
            assert response_data["artifact_count"] == 2
            assert response_data["task_duration_minutes"] == 45.5
    
    @pytest.mark.asyncio
    async def test_complete_task_missing_required_fields(self):
        """Test completion with missing required fields."""
        args = {
            "task_id": "test-123",
            "summary": "Task completed"
            # Missing: detailed_work, next_action
        }
        
        result = await handle_complete_task_v2(args)
        
        response_data = json.loads(result[0].text)
        assert response_data["status"] == "error"
        assert "required" in response_data["error"]["error"].lower()


class TestErrorHandlingIntegration:
    """Test error handling integration across all handlers."""
    
    @pytest.mark.asyncio
    async def test_error_decorator_applied(self):
        """Test that @handle_errors decorator is applied to all handlers."""
        # This test verifies that error handling decorators are working
        
        # Test with a handler that should have error handling
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock unexpected exception
            mock_use_case.create_task.side_effect = Exception("Unexpected error")
            
            args = {
                "title": "Test Task",
                "description": "Test Description"
            }
            
            # Should not raise exception due to error handling
            result = await handle_create_task_v2(args)
            
            # Should return error response instead of raising
            response_data = json.loads(result[0].text)
            assert response_data["status"] == "error"
    
    @pytest.mark.asyncio
    async def test_error_response_format_consistency(self):
        """Test that all handlers return consistent error response formats."""
        handlers_and_args = [
            (handle_create_task_v2, {"invalid": "data"}),
            (handle_update_task_v2, {"invalid": "data"}),
            (handle_delete_task_v2, {"invalid": "data"}),
            (handle_cancel_task_v2, {"invalid": "data"}),
            (handle_query_tasks_v2, {"page": -1}),  # Invalid pagination
        ]
        
        for handler, args in handlers_and_args:
            result = await handler(args)
            response_data = json.loads(result[0].text)
            
            # Verify consistent error response structure
            assert "status" in response_data
            assert response_data["status"] == "error"
            assert "error" in response_data
            assert isinstance(response_data["error"], dict)
            assert "error" in response_data["error"]  # Error message
            assert "tool" in response_data
    
    @pytest.mark.asyncio
    async def test_logging_integration(self):
        """Test that errors are properly logged."""
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.logger') as mock_logger:
            # Test error logging
            args = {"invalid": "validation_data"}
            
            await handle_create_task_v2(args)
            
            # Verify error was logged
            mock_logger.error.assert_called()


class TestPerformanceAndValidation:
    """Performance and validation tests for Pydantic handlers."""
    
    @pytest.mark.asyncio
    async def test_validation_performance(self):
        """Test that Pydantic validation doesn't significantly impact performance."""
        import time
        
        # Create large valid request
        args = {
            "title": "Performance Test Task",
            "description": "A" * 1000,  # Large description
            "task_type": "STANDARD",
            "complexity": "moderate",
            "specialist_type": "developer",
            "metadata": {f"key_{i}": f"value_{i}" for i in range(100)},  # Large metadata
            "tags": [f"tag_{i}" for i in range(50)]  # Many tags
        }
        
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case'):
            start_time = time.time()
            
            # Run validation multiple times
            for _ in range(10):
                try:
                    await handle_create_task_v2(args)
                except:
                    pass  # Ignore actual execution errors, focus on validation time
            
            validation_time = time.time() - start_time
            
            # Validation should be fast (less than 1 second for 10 iterations)
            assert validation_time < 1.0, f"Validation too slow: {validation_time:.2f}s"
    
    def test_dto_serialization_performance(self):
        """Test that DTO serialization is performant."""
        from mcp_task_orchestrator.infrastructure.mcp.dto import CreateTaskResponse, NextStep
        import time
        
        # Create complex response
        response = CreateTaskResponse(
            message="Task created successfully",
            task_id="test-123",
            task_title="Test Task",
            task_type="STANDARD",
            created_at=datetime.utcnow(),
            next_steps=[
                NextStep(
                    action=f"action_{i}",
                    description=f"Description {i}",
                    tool_name=f"tool_{i}",
                    parameters={"param": f"value_{i}"}
                ) for i in range(20)
            ]
        )
        
        start_time = time.time()
        
        # Serialize multiple times
        for _ in range(100):
            json_str = response.json()
            assert len(json_str) > 0
        
        serialization_time = time.time() - start_time
        
        # Serialization should be fast
        assert serialization_time < 1.0, f"Serialization too slow: {serialization_time:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])