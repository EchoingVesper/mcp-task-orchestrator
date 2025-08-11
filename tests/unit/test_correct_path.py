#!/usr/bin/env python3
"""Test with the correct database path used by the StateManager."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def test_correct_database_path():
    """Test the performance fix with the correct database path."""
    print("Testing with correct database path...")
    
    try:
        # Use the correct database path that StateManager uses
        correct_db_path = r"E:\My Work\Programming\MCP Task Orchestrator\.task_orchestrator\task_orchestrator.db"
        print(f"Database path: {correct_db_path}")
        
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Initialize with the correct database path
        db_url = f"sqlite:///{correct_db_path}"
        persistence = DatabasePersistenceManager(
            base_dir=r"E:\My Work\Programming\MCP Task Orchestrator",
            db_url=db_url
        )
        print("DatabasePersistenceManager initialized with correct path")
        
        # Check database contents
        with persistence.session_scope() as session:
            from mcp_task_orchestrator.db.models import TaskBreakdownModel, SubTaskModel
            
            task_count = session.query(TaskBreakdownModel).count()
            subtask_count = session.query(SubTaskModel).count()
            
            print(f"TaskBreakdownModel count: {task_count}")
            print(f"SubTaskModel count: {subtask_count}")
            
            if subtask_count > 0:
                # Test with existing data
                sample_subtask = session.query(SubTaskModel).first()
                
                print(f"Testing lookup for task ID: {sample_subtask.task_id}")
                print(f"Expected parent ID: {sample_subtask.task_id}")
                
                # Test the new direct lookup method
                start_time = time.time()
                result = persistence.get_parent_task_id(sample_subtask.task_id)
                elapsed = time.time() - start_time
                
                print(f"Direct lookup completed in {elapsed:.4f}s")
                print(f"Result: {result}")
                
                if result == sample_subtask.task_id:
                    print("SUCCESS: Direct lookup works correctly!")
                    return True
                else:
                    print("FAILURE: Lookup returned wrong result")
                    return False
            else:
                print("Database is empty - creating test data to verify the fix works...")
                
                # The database exists but is empty, which means the original prompt's 
                # statement about having 26 task breakdowns and 82 subtasks refers to
                # a different state. Let's verify our implementation works by creating
                # a simple test case.
                
                # Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
                from datetime import datetime
                
                # Create a test task breakdown
                test_breakdown = Task(
                    parent_task_id="test_parent_123",
                    description="Test task for performance verification",
                    complexity=ComplexityLevel.MODERATE,
                    context="Testing the performance fix",
                    created_at=datetime.now(),
                    subtasks=[
                        Task(
                            task_id="test_subtask_456",
                            title="Test Subtask",
                            description="A test subtask for performance testing",
                            specialist_type=SpecialistType.RESEARCH_ANALYST,
                            dependencies=[],
                            estimated_effort="1-2 hours",
                            status=TaskStatus.PENDING,
                            results=None,
                            artifacts=[],
                            created_at=datetime.now(),
                            completed_at=None
                        )
                    ]
                )
                
                # Save the test data
                persistence.save_task_breakdown(test_breakdown)
                print("Created test data")
                
                # Now test the lookup
                start_time = time.time()
                result = persistence.get_parent_task_id("test_subtask_456")
                elapsed = time.time() - start_time
                
                print(f"Direct lookup completed in {elapsed:.4f}s")
                print(f"Expected: test_parent_123")
                print(f"Got: {result}")
                
                if result == "test_parent_123" and elapsed < 0.1:
                    print("SUCCESS: Performance fix verified with test data!")
                    print(f"Performance: {elapsed:.4f}s < 0.1s target")
                    return True
                else:
                    print("FAILURE: Performance fix not working as expected")
                    return False
                
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_correct_database_path()
    print("PASSED" if success else "FAILED")
