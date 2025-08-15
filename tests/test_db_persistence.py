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

# Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType, TaskArtifact, ArtifactType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
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
    
    def test_save_and_load_task(self):
        """Test saving and loading a hierarchical task structure."""
        # Create parent task with children
        parent_task, child_tasks = self._create_test_task_hierarchy()
        
        # Save the parent task
        self.persistence.save_task(parent_task)
        
        # Save child tasks
        for child in child_tasks:
            self.persistence.save_task(child)
        
        # Load the parent task
        loaded_task = self.persistence.load_task(parent_task.task_id)
        
        # Check that the loaded task matches the original
        self.assertIsNotNone(loaded_task)
        self.assertEqual(loaded_task.task_id, parent_task.task_id)
        self.assertEqual(loaded_task.title, parent_task.title)
        self.assertEqual(loaded_task.description, parent_task.description)
        self.assertEqual(loaded_task.complexity, parent_task.complexity)
        self.assertEqual(loaded_task.context, parent_task.context)
        
        # Load child tasks and verify hierarchy
        loaded_children = self.persistence.get_child_tasks(parent_task.task_id)
        self.assertEqual(len(loaded_children), len(child_tasks))
        for i, child_task in enumerate(child_tasks):
            loaded_child = next((c for c in loaded_children if c.task_id == child_task.task_id), None)
            self.assertIsNotNone(loaded_child)
            self.assertEqual(loaded_child.parent_task_id, child_task.parent_task_id)
            self.assertEqual(loaded_child.title, child_task.title)
            self.assertEqual(loaded_child.description, child_task.description)
            self.assertEqual(loaded_child.specialist_type, child_task.specialist_type)
            self.assertEqual(loaded_child.estimated_effort, child_task.estimated_effort)
            self.assertEqual(loaded_child.status, child_task.status)
            self.assertEqual(loaded_child.results, child_task.results)
    
    def test_update_task(self):
        """Test updating a task."""
        # Create hierarchical tasks
        parent_task, child_tasks = self._create_test_task_hierarchy()
        
        # Save tasks
        self.persistence.save_task(parent_task)
        for child in child_tasks:
            self.persistence.save_task(child)
        
        # Update a child task
        child_task = child_tasks[0]
        child_task.title = "Updated Title"
        child_task.description = "Updated Description"
        child_task.status = TaskStatus.COMPLETED
        child_task.results = "Completed successfully"
        child_task.completed_at = datetime.now()
        
        # Add artifacts to the task
        child_task.artifacts.append(TaskArtifact(
            artifact_id=f"{child_task.task_id}_artifact_1",
            task_id=child_task.task_id,
            artifact_type=ArtifactType.GENERAL,
            artifact_name="Test Artifact",
            content="Test artifact content"
        ))
        
        # Save the updated task
        self.persistence.update_task(child_task)
        
        # Load the updated task
        loaded_task = self.persistence.load_task(child_task.task_id)
        
        # Check that the task was updated
        self.assertEqual(loaded_task.title, child_task.title)
        self.assertEqual(loaded_task.description, child_task.description)
        self.assertEqual(loaded_task.status, child_task.status)
        self.assertEqual(loaded_task.results, child_task.results)
        self.assertIsNotNone(loaded_task.completed_at)
    
    def test_get_all_active_tasks(self):
        """Test getting all active tasks."""
        # Create and save multiple tasks
        task1 = self._create_test_task("task1")
        task2 = self._create_test_task("task2")
        
        self.persistence.save_task(task1)
        self.persistence.save_task(task2)
        
        # Get all active tasks
        active_tasks = self.persistence.get_all_active_tasks()
        
        # Check that both tasks are in the list
        self.assertEqual(len(active_tasks), 2)
        self.assertIn(task1.task_id, active_tasks)
        self.assertIn(task2.task_id, active_tasks)
    
    def _create_test_task_hierarchy(self, task_id_prefix="test"):
        """Create a test hierarchical task structure."""
        # Create parent task
        parent_task = Task(
            task_id=f"{task_id_prefix}_parent",
            title="Parent Task",
            description="Test parent task for hierarchy",
            task_type=TaskType.BREAKDOWN,
            hierarchy_path=f"/{task_id_prefix}_parent",
            hierarchy_level=0,
            complexity=ComplexityLevel.MODERATE,
            context={"test_context": "Test context data"},
            status=TaskStatus.ACTIVE
        )
        
        # Create child tasks
        child_tasks = [
            Task(
                task_id=f"{task_id_prefix}_subtask1",
                parent_task_id=parent_task.task_id,
                title="Subtask 1",
                description="Description for subtask 1",
                task_type=TaskType.STANDARD,
                hierarchy_path=f"/{task_id_prefix}_parent/{task_id_prefix}_subtask1",
                hierarchy_level=1,
                position_in_parent=0,
                specialist_type="architect",
                estimated_effort="1 hour",
                status=TaskStatus.PENDING
            ),
            Task(
                task_id=f"{task_id_prefix}_subtask2",
                parent_task_id=parent_task.task_id,
                title="Subtask 2",
                description="Description for subtask 2",
                task_type=TaskType.STANDARD,
                hierarchy_path=f"/{task_id_prefix}_parent/{task_id_prefix}_subtask2",
                hierarchy_level=1,
                position_in_parent=1,
                specialist_type="implementer",
                estimated_effort="2 hours",
                status=TaskStatus.PENDING
            )
        ]
        
        # Add dependencies
        child_tasks[1].add_dependency(child_tasks[0].task_id)
        
        return parent_task, child_tasks
    
    def _create_test_task(self, task_id_prefix="test"):
        """Create a single test task."""
        return Task(
            task_id=f"{task_id_prefix}_single",
            title=f"Test Task {task_id_prefix}",
            description=f"Test task description for {task_id_prefix}",
            task_type=TaskType.STANDARD,
            hierarchy_path=f"/{task_id_prefix}_single",
            hierarchy_level=0,
            complexity=ComplexityLevel.MODERATE,
            status=TaskStatus.ACTIVE
        )


if __name__ == "__main__":
    unittest.main()
