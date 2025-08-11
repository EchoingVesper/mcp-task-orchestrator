#!/usr/bin/env python3
"""Test the persistence layer update directly."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def test_persistence_update_directly():
    """Test persistence.update_subtask directly."""
    print("Testing persistence update directly...")
    
    try:
        # Connect to the database that has 82 tasks
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        db_url = f"sqlite:///{db_path}"
        persistence = DatabasePersistenceManager(db_url=db_url)
        
        # Get a sample task to update
        with persistence.session_scope() as session:
            from mcp_task_orchestrator.db.models import SubTaskModel
            sample_db_task = session.query(SubTaskModel).first()
            
            if sample_db_task:
                print(f"Testing update for task: {sample_db_task.task_id}")
                print(f"Parent task: {sample_db_task.parent_task_id}")
                
                # Convert to domain model
                from mcp_task_orchestrator.orchestrator.models import SubTask, TaskStatus, SpecialistType
                from datetime import datetime
                
                domain_task = SubTask(
                    task_id=sample_db_task.task_id,
                    title=sample_db_task.title,
                    description=sample_db_task.description,
                    specialist_type=SpecialistType(sample_db_task.specialist_type),
                    dependencies=sample_db_task.dependencies or [],
                    estimated_effort=sample_db_task.estimated_effort,
                    status=TaskStatus(sample_db_task.status),
                    results=sample_db_task.results,
                    artifacts=sample_db_task.artifacts or [],
                    created_at=sample_db_task.created_at,
                    completed_at=sample_db_task.completed_at
                )
                
                # Test direct persistence update
                print("Testing persistence.update_subtask directly...")
                start_time = time.time()
                persistence.update_subtask(domain_task, sample_db_task.parent_task_id)
                elapsed = time.time() - start_time
                print(f"Persistence update completed in {elapsed:.3f}s")
                
                if elapsed < 2.0:
                    print("SUCCESS: Direct persistence update is fast!")
                    return True
                else:
                    print(f"ISSUE: Direct persistence update took {elapsed:.3f}s")
                    return False
            else:
                print("No tasks found in database")
                return False
                
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_persistence_update_directly()
    print("PASSED" if success else "FAILED")
