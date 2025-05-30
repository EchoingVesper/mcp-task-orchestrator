#!/usr/bin/env python3
"""Test the performance fix - simple version without unicode."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def test_performance_fix():
    """Test the performance improvement."""
    print("Testing performance fix...")
    
    try:
        # Point to the root database file directly
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Initialize with the correct database path
        db_url = f"sqlite:///{db_path}"
        persistence = DatabasePersistenceManager(db_url=db_url)
        
        # Check database contents
        with persistence.session_scope() as session:
            from mcp_task_orchestrator.db.models import SubTaskModel
            
            subtask_count = session.query(SubTaskModel).count()
            print(f"Found {subtask_count} subtasks in database")
            
            if subtask_count > 0:
                # Get a sample subtask to test with
                sample_subtask = session.query(SubTaskModel).first()
                
                print(f"Testing lookup for task ID: {sample_subtask.task_id}")
                print(f"Expected parent ID: {sample_subtask.parent_task_id}")
                
                # Test the new direct lookup method multiple times for accuracy
                times = []
                for i in range(5):
                    start_time = time.time()
                    result = persistence.get_parent_task_id(sample_subtask.task_id)
                    elapsed = time.time() - start_time
                    times.append(elapsed)
                
                avg_time = sum(times) / len(times)
                max_time = max(times)
                
                print(f"Average lookup time: {avg_time:.4f}s")
                print(f"Maximum lookup time: {max_time:.4f}s")
                print(f"Result: {result}")
                
                if result == sample_subtask.parent_task_id and avg_time < 0.1:
                    print("SUCCESS: Direct lookup works correctly and is fast!")
                    print(f"Performance target met: {avg_time:.4f}s < 0.1s")
                    return True
                else:
                    if result != sample_subtask.parent_task_id:
                        print("FAILURE: Lookup returned wrong result")
                    if avg_time >= 0.1:
                        print(f"FAILURE: Lookup too slow: {avg_time:.4f}s >= 0.1s")
                    return False
            else:
                print("No subtasks found")
                return False
                
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_performance_fix()
    print("PASSED" if success else "FAILED")
