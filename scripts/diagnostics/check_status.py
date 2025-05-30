#!/usr/bin/env python3
"""Check the status of the task being updated."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time

async def check_task_status():
    """Check what status the test task has."""
    print("Checking task status...")
    
    try:
        from mcp_task_orchestrator.orchestrator.state import StateManager
        
        state_manager = StateManager()
        
        # Get the first task
        tasks = await state_manager.get_all_tasks()
        if tasks:
            first_task = tasks[0]
            print(f"First task ID: {first_task.task_id}")
            print(f"First task status: {first_task.status}")
            print(f"First task title: {first_task.title}")
            
            # Check if it's completed (which would trigger the archive check)
            from mcp_task_orchestrator.orchestrator.models import TaskStatus
            
            if first_task.status == TaskStatus.COMPLETED:
                print("Task is COMPLETED - this triggers the expensive archive check!")
                print("This is likely causing the timeout.")
                
                # Test the archive check directly
                print("Testing archive check...")
                start_time = time.time()
                await state_manager._check_and_archive_parent_task("task_fa5563f1")
                elapsed = time.time() - start_time
                print(f"Archive check took {elapsed:.3f}s")
                
            else:
                print("Task is not completed, so archive check wouldn't be triggered")
                print("The timeout must be from another source")
                
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(check_task_status())
    print("PASSED" if success else "FAILED")
