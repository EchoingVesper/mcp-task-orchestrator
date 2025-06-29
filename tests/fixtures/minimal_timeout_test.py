#!/usr/bin/env python3
"""
Minimal test to isolate the exact timeout issue.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project to path
project_root = Path(r"E:\My Work\Programming\MCP Task Orchestrator")
sys.path.insert(0, str(project_root))

async def minimal_test():
    print("Testing minimal database operations...")
    
    from .orchestrator.orchestration_state_manager import StateManager
    from mcp_task_orchestrator.orchestrator.models import TaskStatus
    from datetime import datetime
    
    # Initialize StateManager
    state_manager = StateManager(base_dir=project_root)
    
    print("StateManager initialized")
    
    # Find a test task
    all_tasks = await state_manager.get_all_tasks()
    if not all_tasks:
        print("No tasks found")
        return
        
    test_task = all_tasks[0]
    task_id = test_task.task_id
    print(f"Using task: {task_id}")
    
    # Test just the core operations without helper methods
    print("\nTesting core operations individually:")
    
    # 1. Get subtask
    start = time.time()
    subtask = await state_manager.get_subtask(task_id)
    print(f"get_subtask: {time.time() - start:.4f}s")
    
    if not subtask:
        print("No subtask found")
        return
    
    # Store original values
    original_status = subtask.status
    original_results = subtask.results
    original_artifacts = subtask.artifacts
    
    # 2. Update subtask
    start = time.time()
    subtask.status = TaskStatus.COMPLETED
    subtask.results = "Test results"
    subtask.artifacts = ["test.py"]
    subtask.completed_at = datetime.utcnow()
    
    await state_manager.update_subtask(subtask)
    print(f"update_subtask: {time.time() - start:.4f}s")
    
    # 3. Test parent lookup
    start = time.time()
    parent_id = await state_manager._get_parent_task_id(task_id)
    print(f"_get_parent_task_id: {time.time() - start:.4f}s")
    
    # 4. Test get subtasks for parent
    if parent_id:
        start = time.time()
        parent_subtasks = await state_manager.get_subtasks_for_parent(parent_id)
        print(f"get_subtasks_for_parent: {time.time() - start:.4f}s")
    
    print(f"\nAll operations completed successfully")
    
    # Restore original state
    subtask.status = original_status
    subtask.results = original_results
    subtask.artifacts = original_artifacts
    subtask.completed_at = None
    await state_manager.update_subtask(subtask)
    print("Original state restored")

if __name__ == "__main__":
    asyncio.run(minimal_test())
