"""
Comprehensive test suite for the MaintenanceCoordinator component.

Tests all maintenance actions including scan_cleanup, validate_structure,
update_documentation, and prepare_handover with different scopes and validation levels.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path

from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator
from mcp_task_orchestrator.orchestrator.models import TaskStatus, SpecialistType
from mcp_task_orchestrator.db.models import (
    TaskBreakdownModel, SubTaskModel, MaintenanceOperationModel,
    TaskLifecycleModel, StaleTaskTrackingModel, TaskArchiveModel
)


class TestMaintenanceCoordinator:
    """Test suite for MaintenanceCoordinator functionality."""
    
    @pytest.fixture
    def mock_state_manager(self):
        """Create a mock state manager."""
        manager = Mock()
        manager.get_all_task_breakdowns = AsyncMock(return_value=[])
        manager.get_subtasks_by_parent_id = AsyncMock(return_value=[])
        manager.create_maintenance_operation = AsyncMock()
        manager.update_maintenance_operation = AsyncMock()
        manager.create_task_lifecycle = AsyncMock()
        manager.create_stale_task_tracking = AsyncMock()
        manager.get_active_tasks = AsyncMock(return_value=[])
        return manager
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator."""
        orchestrator = Mock()
        orchestrator.state_manager = Mock()
        orchestrator.artifact_manager = Mock()
        return orchestrator
    
    @pytest.fixture
    async def maintenance_coordinator(self, mock_state_manager, mock_orchestrator):
        """Create a MaintenanceCoordinator instance."""
        return MaintenanceCoordinator(mock_state_manager, mock_orchestrator)
    
    # Test scan_cleanup action
    @pytest.mark.asyncio
    async def test_scan_cleanup_current_session_basic(self, maintenance_coordinator, mock_state_manager):
        """Test basic scan and cleanup for current session scope."""
        # Setup mock data
        mock_tasks = [
            {
                "id": "task1",
                "status": TaskStatus.IN_PROGRESS.value,
                "created_at": datetime.utcnow() - timedelta(hours=2),
                "updated_at": datetime.utcnow() - timedelta(hours=1)
            }
        ]
        mock_state_manager.get_active_tasks.return_value = mock_tasks
        
        # Execute scan and cleanup
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify results
        assert result["scope"] == "current_session"
        assert result["validation_level"] == "basic"
        assert "operation_id" in result
        assert "scan_results" in result
        assert "cleanup_actions" in result
        assert "recommendations" in result
        
        # Verify maintenance operation was recorded
        mock_state_manager.create_maintenance_operation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_scan_cleanup_full_project_comprehensive(self, maintenance_coordinator, mock_state_manager):
        """Test comprehensive scan and cleanup for full project scope."""
        # Setup complex mock data with various task states
        mock_tasks = [
            {
                "id": "task1",
                "status": TaskStatus.COMPLETED.value,
                "created_at": datetime.utcnow() - timedelta(days=90),
                "updated_at": datetime.utcnow() - timedelta(days=90)
            },
            {
                "id": "task2",
                "status": TaskStatus.IN_PROGRESS.value,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=25)
            },
            {
                "id": "task3",
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.utcnow() - timedelta(days=7),
                "updated_at": datetime.utcnow() - timedelta(days=7)
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Execute scan and cleanup
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="full_project",
            validation_level="comprehensive"
        )
        
        # Verify comprehensive validation was performed
        assert result["validation_level"] == "comprehensive"
        assert len(result["cleanup_actions"]) > 0
        assert any("archive" in action.get("type", "") for action in result["cleanup_actions"])
    
    @pytest.mark.asyncio
    async def test_scan_cleanup_specific_subtask(self, maintenance_coordinator, mock_state_manager):
        """Test scan and cleanup for specific subtask scope."""
        target_task_id = "specific_task_123"
        
        # Setup mock subtask data
        mock_subtasks = [
            {
                "id": "subtask1",
                "parent_id": target_task_id,
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["artifact1", "artifact2"]
            }
        ]
        mock_state_manager.get_subtasks_by_parent_id.return_value = mock_subtasks
        
        # Execute scan and cleanup
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="specific_subtask",
            validation_level="basic",
            target_task_id=target_task_id
        )
        
        # Verify target task was processed
        assert result["scope"] == "specific_subtask"
        mock_state_manager.get_subtasks_by_parent_id.assert_called_with(target_task_id)
    
    @pytest.mark.asyncio
    async def test_scan_cleanup_invalid_scope(self, maintenance_coordinator):
        """Test scan and cleanup with invalid scope."""
        with pytest.raises(ValueError, match="Invalid scope"):
            await maintenance_coordinator.scan_and_cleanup(scope="invalid_scope")
    
    @pytest.mark.asyncio
    async def test_scan_cleanup_missing_target_task_id(self, maintenance_coordinator):
        """Test scan and cleanup with specific_subtask scope but missing target_task_id."""
        with pytest.raises(ValueError, match="target_task_id required"):
            await maintenance_coordinator.scan_and_cleanup(scope="specific_subtask")
    
    # Test validate_structure action
    @pytest.mark.asyncio
    async def test_validate_structure_basic(self, maintenance_coordinator, mock_state_manager):
        """Test basic structure validation."""
        # Setup mock task hierarchy
        mock_parent_task = {
            "id": "parent1",
            "status": TaskStatus.IN_PROGRESS.value,
            "subtask_ids": ["sub1", "sub2"]
        }
        mock_subtasks = [
            {"id": "sub1", "parent_id": "parent1", "status": TaskStatus.COMPLETED.value},
            {"id": "sub2", "parent_id": "parent1", "status": TaskStatus.IN_PROGRESS.value}
        ]
        
        mock_state_manager.get_all_task_breakdowns.return_value = [mock_parent_task]
        mock_state_manager.get_subtasks_by_parent_id.return_value = mock_subtasks
        
        # Execute validation
        result = await maintenance_coordinator.validate_structure(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify validation results
        assert "validation_results" in result
        assert "structure_issues" in result
        assert "integrity_checks" in result
        assert result["validation_results"]["valid_structure"] is True
    
    @pytest.mark.asyncio
    async def test_validate_structure_full_audit(self, maintenance_coordinator, mock_state_manager):
        """Test full audit structure validation."""
        # Setup complex mock data with potential issues
        mock_tasks = [
            {
                "id": "orphan1",
                "parent_id": "missing_parent",
                "status": TaskStatus.PENDING.value
            },
            {
                "id": "parent1",
                "subtask_ids": ["sub1", "missing_sub"],
                "status": TaskStatus.IN_PROGRESS.value
            }
        ]
        
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        mock_state_manager.get_subtasks_by_parent_id.return_value = []
        
        # Execute full audit
        result = await maintenance_coordinator.validate_structure(
            scope="full_project",
            validation_level="full_audit"
        )
        
        # Verify issues were detected
        assert len(result["structure_issues"]) > 0
        assert any("orphan" in issue.get("type", "") for issue in result["structure_issues"])
        assert any("missing" in issue.get("type", "") for issue in result["structure_issues"])
    
    # Test update_documentation action
    @pytest.mark.asyncio
    async def test_update_documentation_basic(self, maintenance_coordinator, mock_state_manager):
        """Test basic documentation update."""
        # Setup mock task with artifacts
        mock_tasks = [
            {
                "id": "task1",
                "title": "Implement feature X",
                "description": "Feature implementation",
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["code_artifact1", "doc_artifact1"]
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Execute documentation update
        result = await maintenance_coordinator.update_documentation(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify documentation was generated
        assert "documentation_updates" in result
        assert len(result["documentation_updates"]) > 0
        assert "generated_docs" in result
    
    @pytest.mark.asyncio
    async def test_update_documentation_comprehensive(self, maintenance_coordinator, mock_state_manager):
        """Test comprehensive documentation update with cross-references."""
        # Setup mock data with multiple related tasks
        mock_tasks = [
            {
                "id": "task1",
                "title": "Design API",
                "status": TaskStatus.COMPLETED.value,
                "related_tasks": ["task2", "task3"]
            },
            {
                "id": "task2",
                "title": "Implement API",
                "status": TaskStatus.IN_PROGRESS.value,
                "dependencies": ["task1"]
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Execute comprehensive documentation
        result = await maintenance_coordinator.update_documentation(
            scope="full_project",
            validation_level="comprehensive"
        )
        
        # Verify cross-references were created
        assert "cross_references" in result
        assert len(result["cross_references"]) > 0
    
    # Test prepare_handover action
    @pytest.mark.asyncio
    async def test_prepare_handover_basic(self, maintenance_coordinator, mock_state_manager, mock_orchestrator):
        """Test basic handover preparation."""
        # Setup mock session data
        mock_tasks = [
            {
                "id": "task1",
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["artifact1"],
                "completion_summary": "Task completed successfully"
            },
            {
                "id": "task2",
                "status": TaskStatus.IN_PROGRESS.value,
                "progress_percentage": 75
            }
        ]
        mock_state_manager.get_active_tasks.return_value = mock_tasks
        
        # Execute handover preparation
        result = await maintenance_coordinator.prepare_handover(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify handover package was created
        assert "handover_package" in result
        assert "session_summary" in result["handover_package"]
        assert "completed_tasks" in result["handover_package"]
        assert "in_progress_tasks" in result["handover_package"]
        assert "next_steps" in result["handover_package"]
    
    @pytest.mark.asyncio
    async def test_prepare_handover_comprehensive(self, maintenance_coordinator, mock_state_manager):
        """Test comprehensive handover with full context preservation."""
        # Setup complex mock data
        mock_tasks = [
            {
                "id": "task1",
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["artifact1", "artifact2"],
                "decisions": [
                    {"decision": "Use REST API", "rationale": "Better compatibility"}
                ],
                "learnings": ["API rate limiting needs consideration"]
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Mock artifact content
        mock_orchestrator.artifact_manager.get_artifact_content = AsyncMock(
            return_value="Detailed implementation code..."
        )
        
        # Execute comprehensive handover
        result = await maintenance_coordinator.prepare_handover(
            scope="full_project",
            validation_level="comprehensive"
        )
        
        # Verify comprehensive data was included
        assert "decisions_log" in result["handover_package"]
        assert "learnings_summary" in result["handover_package"]
        assert "artifact_contents" in result["handover_package"]
    
    # Test error handling
    @pytest.mark.asyncio
    async def test_scan_cleanup_database_error(self, maintenance_coordinator, mock_state_manager):
        """Test error handling when database operations fail."""
        # Simulate database error
        mock_state_manager.get_active_tasks.side_effect = Exception("Database connection failed")
        
        # Execute and expect graceful handling
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify error was handled
        assert "error" in result
        assert "Database connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_concurrent_maintenance_operations(self, maintenance_coordinator, mock_state_manager):
        """Test handling of concurrent maintenance operations."""
        # Simulate existing maintenance operation in progress
        mock_state_manager.get_active_maintenance_operations = AsyncMock(
            return_value=[{"id": "op1", "action": "scan_cleanup", "status": "in_progress"}]
        )
        
        # Try to start another operation
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="current_session",
            validation_level="basic"
        )
        
        # Verify concurrent operation was handled appropriately
        assert "queued" in result or "deferred" in result
    
    # Test edge cases
    @pytest.mark.asyncio
    async def test_empty_project_maintenance(self, maintenance_coordinator, mock_state_manager):
        """Test maintenance operations on empty project."""
        # No tasks in the system
        mock_state_manager.get_all_task_breakdowns.return_value = []
        mock_state_manager.get_active_tasks.return_value = []
        
        # Execute all maintenance actions
        scan_result = await maintenance_coordinator.scan_and_cleanup("current_session", "basic")
        validate_result = await maintenance_coordinator.validate_structure("current_session", "basic")
        doc_result = await maintenance_coordinator.update_documentation("current_session", "basic")
        handover_result = await maintenance_coordinator.prepare_handover("current_session", "basic")
        
        # Verify all operations handle empty state gracefully
        assert scan_result["scan_results"]["task_count"] == 0
        assert validate_result["validation_results"]["valid_structure"] is True
        assert len(doc_result["documentation_updates"]) == 0
        assert handover_result["handover_package"]["completed_tasks"] == []
    
    @pytest.mark.asyncio
    async def test_large_scale_cleanup(self, maintenance_coordinator, mock_state_manager):
        """Test cleanup with large number of tasks exceeding batch size."""
        # Create more tasks than default batch size
        large_task_list = [
            {
                "id": f"task{i}",
                "status": TaskStatus.COMPLETED.value,
                "created_at": datetime.utcnow() - timedelta(days=100),
                "updated_at": datetime.utcnow() - timedelta(days=100)
            }
            for i in range(100)
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = large_task_list
        
        # Execute cleanup
        result = await maintenance_coordinator.scan_and_cleanup(
            scope="full_project",
            validation_level="basic"
        )
        
        # Verify batching was used
        assert len(result["cleanup_actions"]) > 0
        assert any("batch" in action.get("details", "") for action in result["cleanup_actions"])