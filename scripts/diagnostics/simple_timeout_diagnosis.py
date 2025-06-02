#!/usr/bin/env python3
"""
Simple timeout diagnosis script for complete_subtask operation.
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project to path
project_root = Path(r"E:\My Work\Programming\MCP Task Orchestrator")
sys.path.insert(0, str(project_root))

async def test_complete_subtask():
    print("Starting Complete Subtask Timeout Diagnosis")
    print("=" * 60)
    
    try:
        from mcp_task_orchestrator.orchestrator.state import StateManager
        from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator  
        from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
        
        print("Imports successful")
        
        # Initialize components
        state_manager = StateManager(base_dir=project_root)
        specialist_manager = SpecialistManager()
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        
        print("Components initialized")
        
        # Find a test task
        start = time.time()
        all_tasks = await state_manager.get_all_tasks()
        get_tasks_time = time.time() - start
        print(f"Got {len(all_tasks)} tasks in {get_tasks_time:.4f}s")
        
        if not all_tasks:
            print("No tasks found")
            return
            
        # Use first available task
        test_task = all_tasks[0]
        task_id = test_task.task_id
        print(f"Testing with task: {task_id}")
        
        # Test complete_subtask directly
        print("\nTesting complete_subtask operation:")
        
        start = time.time()
        try:
            result = await orchestrator.complete_subtask(
                task_id,
                "Test completion results", 
                ["test_artifact.py"],
                "continue"
            )
            complete_time = time.time() - start
            print(f"complete_subtask(): {complete_time:.4f}s")
            
            if complete_time > 30:
                print(f"TIMEOUT ISSUE: {complete_time:.4f}s > 30s")
            elif complete_time > 10:
                print(f"SLOW: {complete_time:.4f}s")
            else:
                print(f"OK: {complete_time:.4f}s")
                
        except Exception as e:
            complete_time = time.time() - start
            print(f"complete_subtask(): {complete_time:.4f}s - ERROR: {str(e)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_subtask())
