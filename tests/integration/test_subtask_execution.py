#!/usr/bin/env python3
"""
Test script for the task orchestrator subtask execution.

This script creates a simple task and attempts to execute a subtask
to verify that the orchestrator_execute_subtask function works correctly.
"""

import asyncio
import json
import uuid
import logging
import sys
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Import after configuring logging
from mcp_task_orchestrator.orchestrator.models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
)
from mcp_task_orchestrator.persistence import PersistenceManager
from mcp_task_orchestrator.orchestrator.state import StateManager
from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator


async def test_subtask_execution():
    """Test the subtask execution mechanism."""
    print("\n=== Testing subtask execution mechanism ===\n")
    
    # Initialize managers
    base_dir = Path(__file__).parent
    persistence = PersistenceManager(base_dir)
    state_manager = StateManager(base_dir=base_dir)
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    # Create a test task
    parent_task_id = f"test_task_{uuid.uuid4().hex[:8]}"
    
    # Create subtasks
    subtasks = [
        SubTask(
            task_id=f"architect_{uuid.uuid4().hex[:6]}",
            title="Design Test Architecture",
            description="Design a simple test architecture",
            specialist_type=SpecialistType.ARCHITECT,
            dependencies=[],
            estimated_effort="10 minutes"
        ),
        SubTask(
            task_id=f"implementer_{uuid.uuid4().hex[:6]}",
            title="Implement Test Feature",
            description="Implement a simple test feature",
            specialist_type=SpecialistType.IMPLEMENTER,
            dependencies=[],
            estimated_effort="15 minutes"
        )
    ]
    
    # Create task breakdown
    breakdown = TaskBreakdown(
        parent_task_id=parent_task_id,
        description="Test task for subtask execution",
        complexity=ComplexityLevel.SIMPLE,
        subtasks=subtasks,
        context="Testing subtask execution"
    )
    
    # Save task breakdown
    print(f"Creating task {parent_task_id}...")
    await state_manager.store_task_breakdown(breakdown)
    
    # Verify that the task was saved
    active_tasks = persistence.get_all_active_tasks()
    print(f"Active tasks: {active_tasks}")
    
    if parent_task_id in active_tasks:
        print("✅ Task was successfully saved to persistent storage")
    else:
        print("❌ Task was not saved to persistent storage")
        return
    
    # Try to execute the first subtask
    subtask_id = subtasks[0].task_id
    print(f"\nExecuting subtask {subtask_id}...")
    
    try:
        # Set a timeout for the execution
        specialist_context = await asyncio.wait_for(
            orchestrator.get_specialist_context(subtask_id),
            timeout=10  # 10 seconds timeout
        )
        
        print("✅ Subtask execution successful")
        print(f"Specialist context length: {len(specialist_context)}")
        print(f"Context preview: {specialist_context[:100]}...")
        
        # Verify that the subtask status was updated
        subtask = await state_manager.get_subtask(subtask_id)
        print(f"Subtask status: {subtask.status}")
        
        if subtask.status == TaskStatus.ACTIVE:
            print("✅ Subtask status was correctly updated to ACTIVE")
        else:
            print(f"❌ Subtask status was not updated correctly: {subtask.status}")
        
        # Complete the subtask
        print("\nCompleting subtask...")
        completion_result = await asyncio.wait_for(
            orchestrator.complete_subtask(
                subtask_id,
                "Test results for subtask execution",
                ["test_artifact.md"],
                "continue"
            ),
            timeout=10  # 10 seconds timeout
        )
        
        print("✅ Subtask completion successful")
        print(f"Completion result: {json.dumps(completion_result, indent=2)}")
        
        # Verify that the subtask status was updated
        subtask = await state_manager.get_subtask(subtask_id)
        print(f"Subtask status after completion: {subtask.status}")
        
        if subtask.status == TaskStatus.COMPLETED:
            print("✅ Subtask status was correctly updated to COMPLETED")
        else:
            print(f"❌ Subtask status was not updated correctly: {subtask.status}")
        
    except asyncio.TimeoutError:
        print("❌ Subtask execution timed out")
        
        # Check if the subtask is locked
        lock_file = persistence.get_lock_file_path(f"task_{parent_task_id}")
        if lock_file.exists():
            print(f"⚠️ Lock file exists: {lock_file}")
            
            # Try to clean up the lock
            cleaned = persistence._check_and_cleanup_stale_lock(f"task_{parent_task_id}", force=True)
            print(f"Lock cleanup {'successful' if cleaned else 'failed'}")
        
    except Exception as e:
        print(f"❌ Error during subtask execution: {str(e)}")
    
    print("\nSubtask execution test completed.")

async def main():
    """Main entry point."""
    await test_subtask_execution()

if __name__ == "__main__":
    asyncio.run(main())
