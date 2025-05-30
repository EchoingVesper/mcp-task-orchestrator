#!/usr/bin/env python3
"""
Test script for the database persistence implementation.

This script verifies that the database persistence manager can be initialized
and used to store and retrieve task data.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_db_persistence")

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import the necessary modules
from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel

def main():
    """Test the database persistence manager."""
    try:
        # Create a database persistence manager
        logger.info("Creating database persistence manager...")
        db_path = Path(__file__).parent / "test_persistence.db"
        db_url = f"sqlite:///{db_path}"
        persistence = DatabasePersistenceManager(base_dir=str(Path(__file__).parent), db_url=db_url)
        logger.info(f"Database persistence manager created with URL: {db_url}")
        
        # Create a test task breakdown
        logger.info("Creating test task breakdown...")
        breakdown = TaskBreakdown(
            parent_task_id="test_task_123",
            description="Test task for database persistence",
            complexity=ComplexityLevel.MODERATE,
            context="This is a test task to verify database persistence",
            subtasks=[
                SubTask(
                    task_id="subtask_1",
                    title="Test subtask 1",
                    description="This is test subtask 1",
                    specialist_type=SpecialistType.IMPLEMENTER,
                    dependencies=[],
                    estimated_effort="low",
                    status=TaskStatus.PENDING
                ),
                SubTask(
                    task_id="subtask_2",
                    title="Test subtask 2",
                    description="This is test subtask 2",
                    specialist_type=SpecialistType.DEBUGGER,
                    dependencies=["subtask_1"],
                    estimated_effort="medium",
                    status=TaskStatus.PENDING
                )
            ]
        )
        
        # Save the task breakdown
        logger.info("Saving task breakdown to database...")
        persistence.save_task_breakdown(breakdown)
        logger.info("Task breakdown saved successfully")
        
        # Load the task breakdown
        logger.info("Loading task breakdown from database...")
        loaded_breakdown = persistence.load_task_breakdown("test_task_123")
        
        if loaded_breakdown:
            logger.info("Task breakdown loaded successfully")
            logger.info(f"Parent task ID: {loaded_breakdown.parent_task_id}")
            logger.info(f"Description: {loaded_breakdown.description}")
            logger.info(f"Number of subtasks: {len(loaded_breakdown.subtasks)}")
            
            for subtask in loaded_breakdown.subtasks:
                logger.info(f"Subtask ID: {subtask.task_id}, Title: {subtask.title}, Status: {subtask.status}")
        else:
            logger.error("Failed to load task breakdown")
        
        logger.info("Database persistence test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error testing database persistence: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
