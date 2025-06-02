#!/usr/bin/env python3
"""Test the performance fix for get_parent_task_id lookup."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def test_direct_lookup():
    """Test the new direct parent task ID lookup method."""
    print("Testing direct parent task ID lookup...")
    
    try:
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Initialize the persistence manager
        persistence = DatabasePersistenceManager()
        print("DatabasePersistenceManager initialized")
        
        # Get all active tasks to find a test task ID
        active_tasks = persistence.get_all_active_tasks()
        print(f"Found {len(active_tasks)} active tasks")
        
        if active_tasks:
            # Get the first task breakdown to find a subtask ID to test with
            breakdown = persistence.load_task_breakdown(active_tasks[0])
            if breakdown and breakdown.subtasks:
                test_task_id = breakdown.subtasks[0].task_id
                expected_parent_id = breakdown.parent_task_id
                
                print(f"Testing lookup for task_id: {test_task_id}")
                print(f"Expected parent_task_id: {expected_parent_id}")
                
                # Test the new direct lookup method
                start_time = time.time()
                result = persistence.get_parent_task_id(test_task_id)
                elapsed = time.time() - start_time
                
                print(f"Direct lookup completed in {elapsed:.4f}s")
                print(f"Result: {result}")
                
                if result == expected_parent_id:
                    print("✅ SUCCESS: Direct lookup returned correct parent task ID")
                    print(f"✅ Performance: {elapsed:.4f}s (should be < 0.1s)")
                    return True
                else:
                    print(f"❌ FAILURE: Expected {expected_parent_id}, got {result}")
                    return False
            else:
                print("No subtasks found in first task breakdown")
                return False
        else:
            print("No active tasks found")
            return False
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing performance fix for parent task ID lookup...")
    success = test_direct_lookup()
    print("PASSED" if success else "FAILED")
