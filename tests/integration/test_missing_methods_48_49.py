"""
Test suite for GitHub Issues #48-49: Missing Methods Implementation

This test module validates the missing methods fixes in the missing-methods worktree:
- Issue #48: delete_task implementation 
- Issue #49: cancel_task implementation

Tests focus on:
1. Use case method existence and functionality
2. Repository implementation details
3. Error handling and edge cases
4. Integration with existing systems
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
from mcp_task_orchestrator.domain.repositories.task_repository import TaskRepository


class TestGitHubIssue48DeleteTaskImplementation:
    """
    Test Issue #48: Missing delete_task implementation.
    
    Validates the newly implemented delete_task method in TaskUseCase
    and ensures proper delegation to repository.
    """
    
    @pytest.mark.asyncio
    async def test_delete_task_method_exists_in_use_case(self):
        """Test that delete_task method exists in TaskUseCase."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Method should exist and be callable
        assert hasattr(use_case, 'delete_task')
        assert callable(getattr(use_case, 'delete_task'))
    
    @pytest.mark.asyncio
    async def test_delete_task_has_correct_signature(self):
        """Test delete_task has the expected method signature."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Should accept task_id, force, and archive_instead parameters
        import inspect
        sig = inspect.signature(use_case.delete_task)
        params = list(sig.parameters.keys())
        
        assert 'task_id' in params
        assert 'force' in params  
        assert 'archive_instead' in params
        
        # Check default values
        assert sig.parameters['force'].default is False
        assert sig.parameters['archive_instead'].default is True
    
    @pytest.mark.asyncio 
    async def test_delete_task_calls_repository_with_correct_params(self):
        """Test delete_task properly delegates to repository."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "test_task_123",
            "action": "archived"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call with default parameters
        result = await use_case.delete_task("test_task_123")
        
        # Verify repository method was called correctly
        mock_repo.delete_task.assert_called_once_with("test_task_123", False, True)
        
        # Verify result
        assert result["success"] is True
        assert result["task_id"] == "test_task_123"
    
    @pytest.mark.asyncio
    async def test_delete_task_with_force_option(self):
        """Test delete_task with force=True parameter."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "force_delete_task",
            "action": "deleted",
            "force_applied": True
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call with force=True
        result = await use_case.delete_task("force_delete_task", force=True, archive_instead=False)
        
        # Verify repository was called with force=True
        mock_repo.delete_task.assert_called_once_with("force_delete_task", True, False)
        
        # Verify result indicates force was applied
        assert result["action"] == "deleted"
        assert result.get("force_applied") is True
    
    @pytest.mark.asyncio
    async def test_delete_task_archive_mode(self):
        """Test delete_task with archive_instead=True (default behavior)."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "archive_task",
            "action": "archived",
            "archive_mode": True
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call with explicit archive_instead=True
        result = await use_case.delete_task("archive_task", archive_instead=True)
        
        # Verify repository was called with archive_instead=True
        mock_repo.delete_task.assert_called_once_with("archive_task", False, True)
        
        # Verify result indicates archival
        assert result["action"] == "archived"
        assert result.get("archive_mode") is True
    
    @pytest.mark.asyncio
    async def test_delete_task_error_handling(self):
        """Test delete_task handles repository errors properly."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.side_effect = Exception("Task not found")
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Should propagate repository exceptions
        with pytest.raises(Exception, match="Task not found"):
            await use_case.delete_task("nonexistent_task")
    
    @pytest.mark.asyncio
    async def test_delete_task_returns_dict(self):
        """Test delete_task returns dictionary response."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {
            "success": True,
            "task_id": "dict_test_task",
            "action": "archived",
            "dependent_tasks": ["dep1", "dep2"],
            "metadata": {"archive_timestamp": "2025-08-15T12:00:00"}
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.delete_task("dict_test_task")
        
        # Verify result is a dictionary
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["task_id"] == "dict_test_task"
        assert result["action"] == "archived"
        assert "dependent_tasks" in result
        assert "metadata" in result


class TestGitHubIssue49CancelTaskImplementation:
    """
    Test Issue #49: Missing cancel_task implementation.
    
    Validates the newly implemented cancel_task method in TaskUseCase
    and ensures proper state management and artifact preservation.
    """
    
    @pytest.mark.asyncio
    async def test_cancel_task_method_exists_in_use_case(self):
        """Test that cancel_task method exists in TaskUseCase."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Method should exist and be callable
        assert hasattr(use_case, 'cancel_task')
        assert callable(getattr(use_case, 'cancel_task'))
    
    @pytest.mark.asyncio
    async def test_cancel_task_has_correct_signature(self):
        """Test cancel_task has the expected method signature."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Should accept task_id, reason, and preserve_work parameters
        import inspect
        sig = inspect.signature(use_case.cancel_task)
        params = list(sig.parameters.keys())
        
        assert 'task_id' in params
        assert 'reason' in params
        assert 'preserve_work' in params
        
        # Check default value for preserve_work
        assert sig.parameters['preserve_work'].default is True
    
    @pytest.mark.asyncio
    async def test_cancel_task_calls_repository_with_correct_params(self):
        """Test cancel_task properly delegates to repository."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "test_cancel_task",
            "previous_status": "in_progress",
            "reason": "User requested cancellation",
            "work_preserved": True
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call with reason
        result = await use_case.cancel_task("test_cancel_task", "User requested cancellation")
        
        # Verify repository method was called correctly
        mock_repo.cancel_task.assert_called_once_with("test_cancel_task", "User requested cancellation", True)
        
        # Verify result
        assert result["success"] is True
        assert result["task_id"] == "test_cancel_task"
        assert result["reason"] == "User requested cancellation"
    
    @pytest.mark.asyncio
    async def test_cancel_task_preserve_work_default(self):
        """Test cancel_task preserves work by default."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "preserve_default_task",
            "work_preserved": True,
            "artifact_count": 3
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call without specifying preserve_work (should default to True)
        result = await use_case.cancel_task("preserve_default_task", "Test reason")
        
        # Verify repository was called with preserve_work=True
        mock_repo.cancel_task.assert_called_once_with("preserve_default_task", "Test reason", True)
        
        # Verify work was preserved
        assert result["work_preserved"] is True
    
    @pytest.mark.asyncio
    async def test_cancel_task_discard_work(self):
        """Test cancel_task with preserve_work=False."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "discard_work_task",
            "work_preserved": False,
            "artifact_count": 0,
            "discarded_artifacts": 5
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Call with preserve_work=False
        result = await use_case.cancel_task("discard_work_task", "Discard work", preserve_work=False)
        
        # Verify repository was called with preserve_work=False
        mock_repo.cancel_task.assert_called_once_with("discard_work_task", "Discard work", False)
        
        # Verify work was not preserved
        assert result["work_preserved"] is False
    
    @pytest.mark.asyncio
    async def test_cancel_task_with_complex_cancellation_data(self):
        """Test cancel_task returns complex cancellation metadata."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "complex_cancel_task",
            "previous_status": "in_progress",
            "reason": "Resource constraints",
            "work_preserved": True,
            "artifact_count": 7,
            "dependent_tasks_updated": ["task_1", "task_2", "task_3"],
            "cancelled_at": "2025-08-15T14:30:45",
            "cancellation_metadata": {
                "user_id": "user123",
                "session_id": "session456"
            }
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.cancel_task("complex_cancel_task", "Resource constraints")
        
        # Verify all cancellation data is returned
        assert result["success"] is True
        assert result["task_id"] == "complex_cancel_task"
        assert result["previous_status"] == "in_progress"
        assert result["reason"] == "Resource constraints"
        assert result["work_preserved"] is True
        assert result["artifact_count"] == 7
        assert result["dependent_tasks_updated"] == ["task_1", "task_2", "task_3"]
        assert "cancelled_at" in result
        assert "cancellation_metadata" in result
    
    @pytest.mark.asyncio
    async def test_cancel_task_error_handling(self):
        """Test cancel_task handles repository errors properly."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.side_effect = Exception("Cannot cancel completed task")
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Should propagate repository exceptions
        with pytest.raises(Exception, match="Cannot cancel completed task"):
            await use_case.cancel_task("completed_task", "Try to cancel")
    
    @pytest.mark.asyncio
    async def test_cancel_task_returns_dict(self):
        """Test cancel_task returns dictionary response."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.cancel_task.return_value = {
            "success": True,
            "task_id": "dict_cancel_task",
            "previous_status": "pending",
            "reason": "Test cancellation",
            "work_preserved": True
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.cancel_task("dict_cancel_task", "Test cancellation")
        
        # Verify result is a dictionary
        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["task_id"] == "dict_cancel_task"
        assert result["previous_status"] == "pending"
        assert result["reason"] == "Test cancellation"


class TestMethodsIntegrationAndEdgeCases:
    """
    Test integration scenarios and edge cases for both new methods.
    """
    
    @pytest.mark.asyncio
    async def test_both_methods_available_in_same_use_case(self):
        """Test both delete_task and cancel_task are available in the same use case instance."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # Both methods should be available
        assert hasattr(use_case, 'delete_task')
        assert hasattr(use_case, 'cancel_task')
        assert callable(getattr(use_case, 'delete_task'))
        assert callable(getattr(use_case, 'cancel_task'))
    
    @pytest.mark.asyncio
    async def test_method_signatures_are_async(self):
        """Test both new methods are async."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        import inspect
        
        # Both methods should be coroutines
        assert inspect.iscoroutinefunction(use_case.delete_task)
        assert inspect.iscoroutinefunction(use_case.cancel_task)
    
    @pytest.mark.asyncio
    async def test_methods_work_with_empty_strings(self):
        """Test methods handle empty string parameters gracefully."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.delete_task.return_value = {"success": False, "error": "Invalid task ID"}
        mock_repo.cancel_task.return_value = {"success": False, "error": "Invalid task ID"}
        
        use_case = TaskUseCase(repository=mock_repo)
        
        # Test with empty task IDs
        delete_result = await use_case.delete_task("")
        cancel_result = await use_case.cancel_task("", "reason")
        
        # Should delegate to repository (which can handle validation)
        mock_repo.delete_task.assert_called_once_with("", False, True)
        mock_repo.cancel_task.assert_called_once_with("", "reason", True)
        
        # Repository can decide how to handle invalid inputs
        assert delete_result["success"] is False
        assert cancel_result["success"] is False
    
    @pytest.mark.asyncio
    async def test_methods_with_none_values(self):
        """Test methods handle None parameters appropriately."""
        mock_repo = AsyncMock(spec=TaskRepository)
        use_case = TaskUseCase(repository=mock_repo)
        
        # This should raise TypeError for required parameters
        with pytest.raises(TypeError):
            await use_case.delete_task(None)
            
        with pytest.raises(TypeError):
            await use_case.cancel_task(None, "reason")


class TestTaskUseCaseRegressionValidation:
    """
    Regression tests to ensure existing TaskUseCase functionality still works.
    """
    
    @pytest.mark.asyncio
    async def test_existing_create_task_still_works(self):
        """Test create_task method unchanged by new implementations."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.create_task_from_dict.return_value = {
            "id": "regression_create",
            "title": "Regression Test Task",
            "status": "pending"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.create_task({"title": "Regression Test Task"})
        
        # Should work as before
        assert result["id"] == "regression_create"
        assert result["title"] == "Regression Test Task"
        mock_repo.create_task_from_dict.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_existing_get_task_still_works(self):
        """Test get_task method unchanged by new implementations."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = {
            "id": "regression_get",
            "title": "Get Test Task",
            "status": "completed"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.get_task("regression_get")
        
        # Should work as before
        assert result["id"] == "regression_get"
        assert result["title"] == "Get Test Task"
        mock_repo.get_task.assert_called_once_with("regression_get")
    
    @pytest.mark.asyncio
    async def test_existing_update_task_still_works(self):
        """Test update_task method unchanged by new implementations."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.update_task.return_value = {
            "id": "regression_update",
            "title": "Updated Task",
            "status": "updated"
        }
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.update_task("regression_update", {"status": "updated"})
        
        # Should work as before
        assert result["id"] == "regression_update"
        assert result["status"] == "updated"
        mock_repo.update_task.assert_called_once_with("regression_update", {"status": "updated"})
    
    @pytest.mark.asyncio
    async def test_existing_query_tasks_still_works(self):
        """Test query_tasks method unchanged by new implementations."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.query_tasks.return_value = [
            {"id": "task1", "status": "pending"},
            {"id": "task2", "status": "completed"}
        ]
        
        use_case = TaskUseCase(repository=mock_repo)
        
        result = await use_case.query_tasks({"status": "pending"})
        
        # Should work as before
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repo.query_tasks.assert_called_once_with({"status": "pending"})


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])