"""
Unit tests for the database-backed persistence implementation.

This module contains tests for the DatabasePersistenceManager class to ensure
it correctly stores and retrieves task data.
"""

import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager


class TestDatabasePersistenceManager(unittest.TestCase):
    """Test case for the DatabasePersistenceManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for the test
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = self.temp_dir.name
        
        # Create a temporary database URL
        self.db_url = f"sqlite:///{self.base_dir}/test.db"
        
        # Create a persistence manager
        self.persistence = DatabasePersistenceManager(self.base_dir, self.db_url)
    
    def tearDown(self):
        """Clean up the test environment."""
        # Close the database connection
        self.persistence.engine.dispose()
        
        # Remove any file handlers to close log files
        import logging
        for handler in logging.getLogger("mcp_task_orchestrator.db.persistence").handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
        
        # Remove the temporary directory with error handling
        try:
            self.temp_dir.cleanup()
        except PermissionError as e:
            import os
            import time
            print(f"Warning: Could not clean up temporary directory due to permission error: {e}")
            # Wait a moment and try again
            time.sleep(1)
            try:
                self.temp_dir.cleanup()
            except Exception as e2:
                print(f"Failed to clean up temporary directory after retry: {e2}")
                # Just continue - the OS will clean up temp files eventually
    
    def test_save_and_load_task_breakdown(self):
        """Test saving and loading a task breakdown."""
        # Create a task breakdown
        breakdown = self._create_test_task_breakdown()
        
        # Save the task breakdown
        self.persistence.save_task_breakdown(breakdown)
        
        # Load the task breakdown
        loaded_breakdown = self.persistence.load_task_breakdown(breakdown.parent_task_id)
        
        # Check that the loaded breakdown matches the original
        self.assertIsNotNone(loaded_breakdown)
        self.assertEqual(loaded_breakdown.parent_task_id, breakdown.parent_task_id)
        self.assertEqual(loaded_breakdown.description, breakdown.description)
        self.assertEqual(loaded_breakdown.complexity, breakdown.complexity)
        self.assertEqual(loaded_breakdown.context, breakdown.context)
        
        # Check that the subtasks match
        self.assertEqual(len(loaded_breakdown.subtasks), len(breakdown.subtasks))
        for i, subtask in enumerate(breakdown.subtasks):
            loaded_subtask = loaded_breakdown.subtasks[i]
            self.assertEqual(loaded_subtask.task_id, subtask.task_id)
            self.assertEqual(loaded_subtask.title, subtask.title)
            self.assertEqual(loaded_subtask.description, subtask.description)
            self.assertEqual(loaded_subtask.specialist_type, subtask.specialist_type)
            self.assertEqual(loaded_subtask.dependencies, subtask.dependencies)
            self.assertEqual(loaded_subtask.estimated_effort, subtask.estimated_effort)
            self.assertEqual(loaded_subtask.status, subtask.status)
            self.assertEqual(loaded_subtask.results, subtask.results)
            self.assertEqual(loaded_subtask.artifacts, subtask.artifacts)
    
    def test_update_subtask(self):
        """Test updating a subtask."""
        # Create a task breakdown
        breakdown = self._create_test_task_breakdown()
        
        # Save the task breakdown
        self.persistence.save_task_breakdown(breakdown)
        
        # Update a subtask
        subtask = breakdown.subtasks[0]
        subtask.title = "Updated Title"
        subtask.description = "Updated Description"
        subtask.status = TaskStatus.COMPLETED
        subtask.results = "Completed successfully"
        subtask.artifacts = ["artifact1.txt", "artifact2.txt"]
        subtask.completed_at = datetime.now()
        
        # Save the updated subtask
        self.persistence.update_subtask(subtask, breakdown.parent_task_id)
        
        # Load the task breakdown
        loaded_breakdown = self.persistence.load_task_breakdown(breakdown.parent_task_id)
        
        # Check that the subtask was updated
        loaded_subtask = next(st for st in loaded_breakdown.subtasks if st.task_id == subtask.task_id)
        self.assertEqual(loaded_subtask.title, subtask.title)
        self.assertEqual(loaded_subtask.description, subtask.description)
        self.assertEqual(loaded_subtask.status, subtask.status)
        self.assertEqual(loaded_subtask.results, subtask.results)
        self.assertEqual(loaded_subtask.artifacts, subtask.artifacts)
        self.assertIsNotNone(loaded_subtask.completed_at)
    
    def test_get_all_active_tasks(self):
        """Test getting all active tasks."""
        # Create and save multiple task breakdowns
        breakdown1 = self._create_test_task_breakdown("task1")
        breakdown2 = self._create_test_task_breakdown("task2")
        
        self.persistence.save_task_breakdown(breakdown1)
        self.persistence.save_task_breakdown(breakdown2)
        
        # Get all active tasks
        active_tasks = self.persistence.get_all_active_tasks()
        
        # Check that both tasks are in the list
        self.assertEqual(len(active_tasks), 2)
        self.assertIn(breakdown1.parent_task_id, active_tasks)
        self.assertIn(breakdown2.parent_task_id, active_tasks)
    
    def _create_test_task_breakdown(self, task_id_prefix="test"):
        """Create a test task breakdown."""
        # Create subtasks
        subtasks = [
            SubTask(
                task_id=f"{task_id_prefix}_subtask1",
                title="Subtask 1",
                description="Description for subtask 1",
                specialist_type=SpecialistType.ARCHITECT,
                dependencies=[],
                estimated_effort="1 hour",
                status=TaskStatus.PENDING
            ),
            SubTask(
                task_id=f"{task_id_prefix}_subtask2",
                title="Subtask 2",
                description="Description for subtask 2",
                specialist_type=SpecialistType.IMPLEMENTER,
                dependencies=[f"{task_id_prefix}_subtask1"],
                estimated_effort="2 hours",
                status=TaskStatus.PENDING
            )
        ]
        
        # Create task breakdown
        return TaskBreakdown(
            parent_task_id=f"{task_id_prefix}_parent",
            description="Test task breakdown",
            complexity=ComplexityLevel.MODERATE,
            subtasks=subtasks,
            context="Test context"
        )


if __name__ == "__main__":
    unittest.main()
