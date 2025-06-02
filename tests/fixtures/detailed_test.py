#!/usr/bin/env python3
"""Detailed test to pinpoint where the timeout occurs."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time

async def detailed_timeout_test():
    """Detailed test to see where the timeout occurs."""
    print("Running detailed timeout analysis...")
    
    try:
        from mcp_task_orchestrator.orchestrator.state import StateManager
        
        # Initialize StateManager (using default paths)
        print("1. Initializing StateManager...")
        state_manager = StateManager()
        print("   StateManager initialized successfully")
        
        # Test getting all tasks
        print("2. Getting all tasks...")
        start_time = time.time()
        tasks = await asyncio.wait_for(state_manager.get_all_tasks(), timeout=10.0)
        elapsed = time.time() - start_time
        print(f"   Retrieved {len(tasks)} tasks in {elapsed:.3f}s")
        
        if not tasks:
            print("   No tasks found - cannot proceed with update test")
            return False
            
        # Test getting a specific task
        print("3. Getting specific task...")
        start_time = time.time()
        task = await asyncio.wait_for(state_manager.get_subtask(tasks[0].task_id), timeout=10.0)
        elapsed = time.time() - start_time
        print(f"   Retrieved task in {elapsed:.3f}s")
        
        if not task:
            print("   Could not retrieve specific task")
            return False
            
        # Test the critical _get_parent_task_id_from_persistence method directly
        print("4. Testing parent task ID lookup directly...")
        start_time = time.time()
        parent_id = await state_manager._get_parent_task_id_from_persistence(task.task_id)
        elapsed = time.time() - start_time
        print(f"   Parent ID lookup completed in {elapsed:.3f}s")
        print(f"   Result: {parent_id}")
        
        # Test update_subtask (this is where the timeout likely occurs)
        print("5. Testing update_subtask...")
        start_time = time.time()
        try:
            await asyncio.wait_for(state_manager.update_subtask(task), timeout=10.0)
            elapsed = time.time() - start_time
            print(f"   Update completed in {elapsed:.3f}s")
            return True
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"   Update timed out after {elapsed:.3f}s")
            return False
            
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(detailed_timeout_test())
    print("PASSED" if success else "FAILED")
