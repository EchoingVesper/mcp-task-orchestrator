#!/usr/bin/env python3
"""Check the main database file for the existing data."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def check_main_database():
    """Check the main database file."""
    print("Checking main database file...")
    
    try:
        # Point to the root database file directly
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        print(f"Database path: {db_path}")
        
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Initialize with the correct database path
        db_url = f"sqlite:///{db_path}"
        # Use context manager for proper cleanup
        with DatabasePersistenceManager(db_url=db_url) as persistence:
            print("DatabasePersistenceManager initialized with main database")
            
            # Check active tasks
            active_tasks = persistence.get_all_active_tasks()
            print(f"Active tasks count: {len(active_tasks)}")
            
            # Check actual table counts
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
                        print(f"Sample subtask - ID: {sample_subtask.task_id}")
                        print(f"Sample parent ID: {sample_subtask.task_id}")
                        
                        # Test the new direct lookup method
                        start_time = time.time()
                        result = persistence.get_parent_task_id(sample_subtask.task_id)
                        elapsed = time.time() - start_time
                        
                        print(f"Direct lookup completed in {elapsed:.4f}s")
                        print(f"Expected: {sample_subtask.task_id}")
                        print(f"Got: {result}")
                        
                        if result == sample_subtask.task_id:
                            print("✅ SUCCESS: Direct lookup works correctly!")
                            print(f"✅ Performance: {elapsed:.4f}s")
                            return elapsed < 0.1  # Should be very fast
                        else:
                            print("❌ FAILURE: Lookup returned wrong result")
                            return False
                else:
                    print("No subtasks found in main database either")
                    return False
                
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Checking main database and testing performance fix...")
    success = check_main_database()
    print("PASSED" if success else "FAILED")
