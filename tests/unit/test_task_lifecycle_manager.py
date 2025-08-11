"""
Comprehensive test suite for the TaskLifecycleManager component.

Tests stale task detection with different specialist thresholds,
task archival functionality, and cleanup recommendations.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from pathlib import Path

# from mcp_task_orchestrator.orchestrator.task_lifecycle import  # TODO: Complete this import
# Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
# from mcp_task_orchestrator.db.models import  # TODO: Complete this import


class TestTaskLifecycleManager:
    """Test suite for TaskLifecycleManager functionality."""
    
    @pytest.fixture
    def mock_state_manager(self):
        """Create a mock state manager."""
        manager = Mock()
        manager.get_all_task_breakdowns = AsyncMock(return_value=[])
        manager.get_subtasks_by_parent_id = AsyncMock(return_value=[])
        manager.create_task_lifecycle = AsyncMock()
        manager.update_task_lifecycle = AsyncMock()
        manager.create_stale_task_tracking = AsyncMock()
        manager.create_task_archive = AsyncMock()
        manager.get_task_by_id = AsyncMock()
        manager.update_task_status = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_artifact_manager(self):
        """Create a mock artifact manager."""
        manager = Mock()
        manager.store_artifact = AsyncMock()
        manager.get_artifact_content = AsyncMock()
        manager.archive_artifacts = AsyncMock()
        manager.cleanup_artifacts = AsyncMock()
        return manager
    
    @pytest.fixture
    async def lifecycle_manager(self, mock_state_manager, mock_artifact_manager):
        """Create a TaskLifecycleManager instance."""
        return TaskLifecycleManager(mock_state_manager, mock_artifact_manager)
    
    # Test stale task detection
    @pytest.mark.asyncio
    async def test_detect_stale_tasks_basic(self, lifecycle_manager, mock_state_manager):
        """Test basic stale task detection."""
        # Setup mock tasks with different ages
        mock_tasks = [
            {
                "id": "task1",
                "status": TaskStatus.IN_PROGRESS.value,
                "specialist_type": SpecialistType.RESEARCHER.value,
                "created_at": datetime.utcnow() - timedelta(hours=15),  # Exceeds researcher threshold
                "updated_at": datetime.utcnow() - timedelta(hours=13),
                "progress_percentage": 5
            },
            {
                "id": "task2",
                "status": TaskStatus.IN_PROGRESS.value,
                "specialist_type": SpecialistType.IMPLEMENTER.value,
                "created_at": datetime.utcnow() - timedelta(hours=30),  # Within implementer threshold
                "updated_at": datetime.utcnow() - timedelta(hours=2),
                "progress_percentage": 60
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Execute stale detection
        stale_tasks = await lifecycle_manager.detect_stale_tasks(comprehensive_scan=False)
        
        # Verify results
        assert len(stale_tasks) == 1
        assert stale_tasks[0]["task_id"] == "task1"
        assert stale_tasks[0]["reason"] == StaleTaskReason.INACTIVITY_TIMEOUT.value
        assert "recommended_action" in stale_tasks[0]
    
    @pytest.mark.asyncio
    async def test_detect_stale_tasks_specialist_thresholds(self, lifecycle_manager, mock_state_manager):
        """Test stale detection with different specialist thresholds."""
        # Create tasks for each specialist type
        specialist_tasks = []
        for spec_type in SpecialistType:
            threshold = lifecycle_manager.stale_detection_config["specialist_thresholds"].get(
                spec_type.value.lower(),
                lifecycle_manager.stale_detection_config["default_threshold_hours"]
            )
            
            # Create one stale and one active task per specialist
            specialist_tasks.extend([
                {
                    "id": f"{spec_type.value}_stale",
                    "status": TaskStatus.IN_PROGRESS.value,
                    "specialist_type": spec_type.value,
                    "created_at": datetime.utcnow() - timedelta(hours=threshold + 5),
                    "updated_at": datetime.utcnow() - timedelta(hours=threshold + 1),
                    "progress_percentage": 5
                },
                {
                    "id": f"{spec_type.value}_active",
                    "status": TaskStatus.IN_PROGRESS.value,
                    "specialist_type": spec_type.value,
                    "created_at": datetime.utcnow() - timedelta(hours=threshold - 5),
                    "updated_at": datetime.utcnow() - timedelta(minutes=30),
                    "progress_percentage": 50
                }
            ])
        
        mock_state_manager.get_all_task_breakdowns.return_value = specialist_tasks
        
        # Execute detection
        stale_tasks = await lifecycle_manager.detect_stale_tasks(comprehensive_scan=False)
        
        # Verify each specialist type has one stale task
        stale_task_ids = [task["task_id"] for task in stale_tasks]
        for spec_type in SpecialistType:
            assert f"{spec_type.value}_stale" in stale_task_ids
            assert f"{spec_type.value}_active" not in stale_task_ids
    
    @pytest.mark.asyncio
    async def test_detect_stale_tasks_comprehensive(self, lifecycle_manager, mock_state_manager):
        """Test comprehensive stale detection with advanced heuristics."""
        # Setup complex scenarios
        mock_tasks = [
            # Abandoned workflow
            {
                "id": "abandoned1",
                "status": TaskStatus.IN_PROGRESS.value,
                "created_at": datetime.utcnow() - timedelta(days=10),
                "updated_at": datetime.utcnow() - timedelta(days=8),
                "parent_id": None,
                "subtask_ids": ["sub1", "sub2"],
                "progress_percentage": 20
            },
            # Orphaned task
            {
                "id": "orphan1",
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.utcnow() - timedelta(days=3),
                "updated_at": datetime.utcnow() - timedelta(days=3),
                "parent_id": "non_existent_parent",
                "progress_percentage": 0
            },
            # Task with failed dependencies
            {
                "id": "blocked1",
                "status": TaskStatus.PENDING.value,
                "created_at": datetime.utcnow() - timedelta(days=2),
                "updated_at": datetime.utcnow() - timedelta(days=2),
                "dependencies": ["failed_task1"],
                "progress_percentage": 0
            }
        ]
        
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        mock_state_manager.get_task_by_id.return_value = None  # Parent doesn't exist
        
        # Execute comprehensive detection
        stale_tasks = await lifecycle_manager.detect_stale_tasks(comprehensive_scan=True)
        
        # Verify different stale reasons were detected
        reasons = {task["reason"] for task in stale_tasks}
        assert StaleTaskReason.ABANDONED_WORKFLOW.value in reasons
        assert StaleTaskReason.ORPHANED_TASK.value in reasons
        assert StaleTaskReason.DEPENDENCY_FAILURE.value in reasons
    
    # Test task archival
    @pytest.mark.asyncio
    async def test_archive_task_basic(self, lifecycle_manager, mock_state_manager, mock_artifact_manager):
        """Test basic task archival."""
        task_id = "task_to_archive"
        
        # Setup mock task data
        mock_task = {
            "id": task_id,
            "status": TaskStatus.COMPLETED.value,
            "title": "Completed task",
            "description": "Task description",
            "artifacts": ["artifact1", "artifact2"],
            "created_at": datetime.utcnow() - timedelta(days=30),
            "completed_at": datetime.utcnow() - timedelta(days=1)
        }
        mock_state_manager.get_task_by_id.return_value = mock_task
        
        # Mock artifact content
        mock_artifact_manager.get_artifact_content.side_effect = [
            "Artifact 1 content",
            "Artifact 2 content"
        ]
        
        # Execute archival
        archive_result = await lifecycle_manager.archive_task(
            task_id,
            reason=StaleTaskReason.USER_ABANDONED,
            preserve_artifacts=True
        )
        
        # Verify archival
        assert archive_result["success"] is True
        assert archive_result["archived_task_id"] == task_id
        assert "archive_id" in archive_result
        
        # Verify archive was created with artifacts
        mock_state_manager.create_task_archive.assert_called_once()
        archive_call = mock_state_manager.create_task_archive.call_args[0][0]
        assert archive_call["task_id"] == task_id
        assert len(archive_call["archived_artifacts"]) == 2
        assert archive_call["archive_reason"] == StaleTaskReason.USER_ABANDONED.value
    
    @pytest.mark.asyncio
    async def test_archive_task_with_subtasks(self, lifecycle_manager, mock_state_manager, mock_artifact_manager):
        """Test archival of task with subtasks."""
        parent_id = "parent_task"
        
        # Setup parent and subtasks
        mock_parent = {
            "id": parent_id,
            "status": TaskStatus.COMPLETED.value,
            "subtask_ids": ["sub1", "sub2"]
        }
        mock_subtasks = [
            {
                "id": "sub1",
                "parent_id": parent_id,
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["sub1_artifact"]
            },
            {
                "id": "sub2",
                "parent_id": parent_id,
                "status": TaskStatus.COMPLETED.value,
                "artifacts": ["sub2_artifact"]
            }
        ]
        
        mock_state_manager.get_task_by_id.return_value = mock_parent
        mock_state_manager.get_subtasks_by_parent_id.return_value = mock_subtasks
        mock_artifact_manager.get_artifact_content.return_value = "Artifact content"
        
        # Execute archival with subtasks
        archive_result = await lifecycle_manager.archive_task(
            parent_id,
            include_subtasks=True,
            preserve_artifacts=True
        )
        
        # Verify all tasks were archived
        assert archive_result["success"] is True
        assert archive_result["archived_count"] == 3  # Parent + 2 subtasks
        assert len(archive_result["archived_task_ids"]) == 3
    
    @pytest.mark.asyncio
    async def test_archive_task_cleanup_artifacts(self, lifecycle_manager, mock_state_manager, mock_artifact_manager):
        """Test task archival with artifact cleanup."""
        task_id = "task_with_cleanup"
        
        # Setup mock task
        mock_task = {
            "id": task_id,
            "status": TaskStatus.COMPLETED.value,
            "artifacts": ["artifact1", "artifact2"]
        }
        mock_state_manager.get_task_by_id.return_value = mock_task
        
        # Execute archival without preserving artifacts
        archive_result = await lifecycle_manager.archive_task(
            task_id,
            preserve_artifacts=False
        )
        
        # Verify artifacts were cleaned up
        assert archive_result["success"] is True
        mock_artifact_manager.cleanup_artifacts.assert_called_with(["artifact1", "artifact2"])
    
    # Test cleanup recommendations
    @pytest.mark.asyncio
    async def test_generate_cleanup_recommendations(self, lifecycle_manager, mock_state_manager):
        """Test generation of cleanup recommendations."""
        # Setup various task scenarios
        mock_tasks = [
            # Old completed task
            {
                "id": "old_completed",
                "status": TaskStatus.COMPLETED.value,
                "created_at": datetime.utcnow() - timedelta(days=120),
                "completed_at": datetime.utcnow() - timedelta(days=100)
            },
            # Stale in-progress task
            {
                "id": "stale_progress",
                "status": TaskStatus.IN_PROGRESS.value,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow() - timedelta(days=25),
                "progress_percentage": 10
            },
            # Failed task
            {
                "id": "failed_task",
                "status": TaskStatus.FAILED.value,
                "created_at": datetime.utcnow() - timedelta(days=45),
                "failed_at": datetime.utcnow() - timedelta(days=44)
            }
        ]
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Generate recommendations
        recommendations = await lifecycle_manager.generate_cleanup_recommendations()
        
        # Verify recommendations
        assert len(recommendations) > 0
        
        # Check for different types of recommendations
        recommendation_types = {rec["type"] for rec in recommendations}
        assert "archive_old_completed" in recommendation_types
        assert "review_stale_tasks" in recommendation_types
        assert "cleanup_failed_tasks" in recommendation_types
        
        # Verify task-specific recommendations
        task_ids_in_recommendations = set()
        for rec in recommendations:
            if "task_ids" in rec:
                task_ids_in_recommendations.update(rec["task_ids"])
        
        assert "old_completed" in task_ids_in_recommendations
        assert "stale_progress" in task_ids_in_recommendations
        assert "failed_task" in task_ids_in_recommendations
    
    @pytest.mark.asyncio
    async def test_cleanup_recommendations_with_retention_policies(self, lifecycle_manager, mock_state_manager):
        """Test cleanup recommendations respect retention policies."""
        # Create tasks at various ages relative to retention policies
        mock_tasks = []
        
        # Task just under retention period - should not be recommended
        mock_tasks.append({
            "id": "recent_completed",
            "status": TaskStatus.COMPLETED.value,
            "created_at": datetime.utcnow() - timedelta(days=80),
            "completed_at": datetime.utcnow() - timedelta(days=80)
        })
        
        # Task over retention period - should be recommended
        mock_tasks.append({
            "id": "old_completed",
            "status": TaskStatus.COMPLETED.value,
            "created_at": datetime.utcnow() - timedelta(days=100),
            "completed_at": datetime.utcnow() - timedelta(days=100)
        })
        
        mock_state_manager.get_all_task_breakdowns.return_value = mock_tasks
        
        # Generate recommendations
        recommendations = await lifecycle_manager.generate_cleanup_recommendations()
        
        # Verify retention policies are respected
        archive_recommendations = [
            rec for rec in recommendations 
            if rec["type"] == "archive_old_completed"
        ]
        
        assert len(archive_recommendations) > 0
        archived_task_ids = archive_recommendations[0]["task_ids"]
        assert "old_completed" in archived_task_ids
        assert "recent_completed" not in archived_task_ids
    
    # Test error handling
    @pytest.mark.asyncio
    async def test_archive_task_not_found(self, lifecycle_manager, mock_state_manager):
        """Test archival of non-existent task."""
        mock_state_manager.get_task_by_id.return_value = None
        
        # Attempt to archive non-existent task
        archive_result = await lifecycle_manager.archive_task("non_existent_task")
        
        # Verify graceful failure
        assert archive_result["success"] is False
        assert "not found" in archive_result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_detect_stale_tasks_database_error(self, lifecycle_manager, mock_state_manager):
        """Test stale detection with database error."""
        mock_state_manager.get_all_task_breakdowns.side_effect = Exception("Database error")
        
        # Execute detection
        stale_tasks = await lifecycle_manager.detect_stale_tasks()
        
        # Verify error was handled
        assert isinstance(stale_tasks, list)
        assert len(stale_tasks) == 0  # Returns empty list on error
    
    # Test lifecycle state transitions
    @pytest.mark.asyncio
    async def test_transition_task_lifecycle_state(self, lifecycle_manager, mock_state_manager):
        """Test task lifecycle state transitions."""
        task_id = "task_lifecycle"
        
        # Setup mock task
        mock_task = {
            "id": task_id,
            "status": TaskStatus.IN_PROGRESS.value,
            "lifecycle_state": TaskLifecycleState.ACTIVE.value
        }
        mock_state_manager.get_task_by_id.return_value = mock_task
        
        # Test valid transition
        result = await lifecycle_manager.transition_lifecycle_state(
            task_id,
            TaskLifecycleState.COMPLETED
        )
        
        assert result["success"] is True
        assert result["new_state"] == TaskLifecycleState.COMPLETED.value
        mock_state_manager.update_task_lifecycle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_archival(self, lifecycle_manager, mock_state_manager, mock_artifact_manager):
        """Test bulk archival of multiple tasks."""
        task_ids = ["task1", "task2", "task3", "task4", "task5"]
        
        # Setup mock tasks
        for task_id in task_ids:
            mock_state_manager.get_task_by_id.side_effect = [
                {"id": tid, "status": TaskStatus.COMPLETED.value, "artifacts": []}
                for tid in task_ids
            ]
        
        # Execute bulk archival
        bulk_result = await lifecycle_manager.bulk_archive_tasks(
            task_ids,
            reason=StaleTaskReason.INACTIVITY_TIMEOUT
        )
        
        # Verify results
        assert bulk_result["total_tasks"] == 5
        assert bulk_result["successfully_archived"] == 5
        assert bulk_result["failed_archives"] == 0
        assert len(bulk_result["archive_ids"]) == 5