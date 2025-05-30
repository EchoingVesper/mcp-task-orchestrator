#!/usr/bin/env python3
"""Check database contents and test the performance fix."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def check_database_contents():
    """Check what's in the database."""
    print("Checking database contents...")
    
    try:
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Initialize the persistence manager
        persistence = DatabasePersistenceManager()
        print("DatabasePersistenceManager initialized")
        
        # Check active tasks
        active_tasks = persistence.get_all_active_tasks()
        print(f"Active tasks: {active_tasks}")
        
        # If no active tasks, let's check the database file location
        print(f"Database path: {persistence.engine.url}")
        
        # Try to inspect the database directly
        with persistence.session_scope() as session:
            from mcp_task_orchestrator.db.models import TaskBreakdownModel, SubTaskModel
            
            task_count = session.query(TaskBreakdownModel).count()
            subtask_count = session.query(SubTaskModel).count()
            
            print(f"TaskBreakdownModel count: {task_count}")
            print(f"SubTaskModel count: {subtask_count}")
            
            if subtask_count > 0:
                # Get a sample subtask to test with
                sample_subtask = session.query(SubTaskModel).first()
                if sample_subtask:
                    print(f"Sample subtask - ID: {sample_subtask.task_id}, Parent: {sample_subtask.parent_task_id}")
                    
                    # Test the new direct lookup method
                    start_time = time.time()
                    result = persistence.get_parent_task_id(sample_subtask.task_id)
                    elapsed = time.time() - start_time
                    
                    print(f"Direct lookup completed in {elapsed:.4f}s")
                    print(f"Expected: {sample_subtask.parent_task_id}")
                    print(f"Got: {result}")
                    
                    if result == sample_subtask.parent_task_id:
                        print("✅ SUCCESS: Direct lookup works correctly!")
                        print(f"✅ Performance: {elapsed:.4f}s (should be < 0.1s)")
                        return True
                    else:
                        print("❌ FAILURE: Lookup returned wrong result")
                        return False
            else:
                print("No subtasks found in database")
                return False
                
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Checking database and testing performance fix...")
    success = check_database_contents()
    print("PASSED" if success else "FAILED")
