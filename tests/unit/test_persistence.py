#!/usr/bin/env python3
"""
Test script for the task persistence mechanism.

This script creates a simple task and verifies that it's properly persisted
to the .task_orchestrator directory.
"""

import asyncio
import json
import uuid
from pathlib import Path

# Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
from mcp_task_orchestrator.persistence import PersistenceManager
from .orchestrator.orchestration_state_manager import StateManager


async def test_persistence():
    """Test the persistence mechanism by creating and retrieving a task."""
    print("Testing task persistence mechanism...")
    
    # Initialize persistence manager
    base_dir = Path(__file__).parent
    persistence = PersistenceManager(base_dir)
    state_manager = StateManager(base_dir=base_dir)
    
    # Create a test task
    parent_task_id = f"test_task_{uuid.uuid4().hex[:8]}"
    
    # Create subtasks
    subtasks = [
        Task(
            task_id=f"architect_{uuid.uuid4().hex[:6]}",
            title="Design Persistence Architecture",
            description="Design the overall directory structure and file formats for persistence",
            specialist_type=SpecialistType.ARCHITECT,
            dependencies=[],
            estimated_effort="30 minutes"
        ),
        Task(
            task_id=f"implementer_{uuid.uuid4().hex[:6]}",
            title="Implement Persistence Manager",
            description="Create the PersistenceManager class for task state serialization",
            specialist_type=SpecialistType.IMPLEMENTER,
            dependencies=[],
            estimated_effort="1 hour"
        ),
        Task(
            task_id=f"tester_{uuid.uuid4().hex[:6]}",
            title="Test Persistence Mechanism",
            description="Create tests for the persistence mechanism",
            specialist_type=SpecialistType.TESTER,
            dependencies=[],
            estimated_effort="45 minutes"
        )
    ]
    
    # Create task breakdown
    breakdown = Task(
        parent_task_id=parent_task_id,
        description="Implement task persistence for MCP Task Orchestrator",
        complexity=ComplexityLevel.MODERATE,
        subtasks=subtasks,
        context="Testing the persistence mechanism"
    )
    
    # Save task breakdown
    print(f"Creating task {parent_task_id}...")
    persistence.save_task_breakdown(breakdown)
    
    # Verify that the task was saved
    active_tasks = persistence.get_all_active_tasks()
    print(f"Active tasks: {active_tasks}")
    
    if parent_task_id in active_tasks:
        print("✅ Task was successfully saved to persistent storage")
    else:
        print("❌ Task was not saved to persistent storage")
    
    # Load the task from persistent storage
    loaded_breakdown = persistence.load_task_breakdown(parent_task_id)
    
    if loaded_breakdown and loaded_breakdown.task_id == parent_task_id:
        print("✅ Task was successfully loaded from persistent storage")
        print(f"Task description: {loaded_breakdown.description}")
        print(f"Number of subtasks: {len(loaded_breakdown.children)}")
    else:
        print("❌ Task could not be loaded from persistent storage")
    
    # Update a subtask
    if loaded_breakdown:
        subtask = loaded_breakdown.children[0]
        subtask.status = TaskStatus.COMPLETED
        subtask.results = "Persistence architecture design completed"
        subtask.artifacts = ["docs/persistence.md"]
        
        print(f"Updating subtask {subtask.task_id}...")
        persistence.update_subtask(subtask, parent_task_id)
        
        # Verify the update
        updated_breakdown = persistence.load_task_breakdown(parent_task_id)
        updated_subtask = next((st for st in updated_breakdown.children if st.task_id == subtask.task_id), None)
        
        if updated_subtask and updated_subtask.status == TaskStatus.COMPLETED:
            print("✅ Subtask was successfully updated in persistent storage")
        else:
            print("❌ Subtask was not updated in persistent storage")
    
    # Archive the task
    print(f"Archiving task {parent_task_id}...")
    archived = persistence.archive_task(parent_task_id)
    
    if archived:
        print("✅ Task was successfully archived")
        
        # Verify that the task is no longer in active tasks
        active_tasks = persistence.get_all_active_tasks()
        archived_tasks = persistence.get_all_archived_tasks()
        
        if parent_task_id not in active_tasks and parent_task_id in archived_tasks:
            print("✅ Task was moved from active to archive")
        else:
            print("❌ Task archiving failed")
    else:
        print("❌ Task archiving failed")
    
    print("\nPersistence test completed.")
    
    # Clean up
    # Note: In a real test, you might want to clean up the test data
    # But for this demonstration, we'll leave it for inspection

async def main():
    """Main entry point."""
    await test_persistence()

if __name__ == "__main__":
    asyncio.run(main())
