#!/usr/bin/env python3
"""Test StateManager with correct database path."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time

async def test_state_manager_with_correct_db():
    """Test StateManager with correct database configuration."""
    print("Testing StateManager with correct database...")
    
    try:
        # Set environment variables to point to the correct database
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        base_dir = r"E:\My Work\Programming\MCP Task Orchestrator"
        
        os.environ["MCP_TASK_ORCHESTRATOR_DB_PATH"] = db_path
        os.environ["MCP_TASK_ORCHESTRATOR_BASE_DIR"] = base_dir
        
        from .orchestrator.orchestration_state_manager import StateManager
        
        # Initialize StateManager with explicit paths
        state_manager = StateManager(db_path=db_path, base_dir=base_dir)
        print("StateManager initialized with correct database")
        
        # Test getting tasks
        start_time = time.time()
        tasks = await asyncio.wait_for(state_manager.get_all_tasks(), timeout=5.0)
        elapsed = time.time() - start_time
        print(f"Retrieved {len(tasks)} tasks in {elapsed:.2f}s")
        
        if tasks:
            # Test getting a specific task
            start_time = time.time()
            task = await asyncio.wait_for(
                state_manager.get_subtask(tasks[0].task_id), 
                timeout=5.0
            )
            elapsed = time.time() - start_time
            print(f"Retrieved specific task in {elapsed:.2f}s")
            
            if task:
                # Test updating a task - this should now be fast
                start_time = time.time()
                await asyncio.wait_for(
                    state_manager.update_subtask(task), 
                    timeout=5.0
                )
                elapsed = time.time() - start_time
                print(f"Updated task in {elapsed:.2f}s")
                
                if elapsed < 2.0:
                    print("SUCCESS: update_subtask completed quickly!")
                    return True
                else:
                    print(f"WARNING: update_subtask took {elapsed:.2f}s")
                    return False
            else:
                print("Could not retrieve specific task")
                return False
        else:
            print("No tasks found")
            return False
            
    except asyncio.TimeoutError:
        print("FAILURE: Operations timed out")
        return False
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_state_manager_with_correct_db())
    print("PASSED" if success else "FAILED")
