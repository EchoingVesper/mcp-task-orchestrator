#!/usr/bin/env python3
"""Quick test for the critical complete_subtask synchronization issue."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time

async def test_quick_operations():
    """Test key operations with shorter timeouts."""
    print("Testing key operations...")
    
    try:
        from mcp_task_orchestrator.orchestrator.state import StateManager
        
        # Test StateManager operations
        state_manager = StateManager()
        print("StateManager initialized")
        
        # Test getting tasks (should be fast)
        start_time = time.time()
        tasks = await asyncio.wait_for(state_manager.get_all_tasks(), timeout=5.0)
        elapsed = time.time() - start_time
        print(f"Retrieved {len(tasks)} tasks in {elapsed:.2f}s")
        
        if tasks:
            # Test getting a specific task (should be fast)
            start_time = time.time()
            task = await asyncio.wait_for(
                state_manager.get_subtask(tasks[0].task_id), 
                timeout=5.0
            )
            elapsed = time.time() - start_time
            print(f"Retrieved specific task in {elapsed:.2f}s")
            
            if task:
                # Test updating a task (this was part of the hanging issue)
                start_time = time.time()
                await asyncio.wait_for(
                    state_manager.update_subtask(task), 
                    timeout=10.0
                )
                elapsed = time.time() - start_time
                print(f"Updated task in {elapsed:.2f}s")
                
                print("SUCCESS: All database operations completed without hanging!")
                return True
            else:
                print("Could not retrieve specific task")
                return False
        else:
            print("No tasks found - basic operations work")
            return True
            
    except asyncio.TimeoutError:
        print("FAILURE: Operations timed out - synchronization issues remain")
        return False
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Quick synchronization test...")
    success = asyncio.run(test_quick_operations())
    print("PASSED" if success else "FAILED")
    sys.exit(0 if success else 1)
