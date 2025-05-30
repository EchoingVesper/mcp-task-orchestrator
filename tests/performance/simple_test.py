#!/usr/bin/env python3
"""Simple test to verify the performance fix works."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import time

def simple_performance_test():
    """Simple test of the performance fix."""
    print("Testing performance fix...")
    
    try:
        # Use the correct database path
        correct_db_path = r"E:\My Work\Programming\MCP Task Orchestrator\.task_orchestrator\task_orchestrator.db"
        
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        from mcp_task_orchestrator.orchestrator.models import (
            TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
        )
        from datetime import datetime
        
        # Initialize persistence manager
        db_url = f"sqlite:///{correct_db_path}"
        persistence = DatabasePersistenceManager(
            base_dir=r"E:\My Work\Programming\MCP Task Orchestrator",
            db_url=db_url
        )
        
        # Create test data
        test_breakdown = TaskBreakdown(
            parent_task_id="test_parent_123",
            description="Test task for performance verification",
            complexity=ComplexityLevel.MODERATE,
            context="Testing the performance fix",
            created_at=datetime.now(),
            subtasks=[
                SubTask(
                    task_id="test_subtask_456",
                    title="Test Subtask",
                    description="A test subtask for performance testing",
                    specialist_type=SpecialistType.RESEARCHER,  # Using correct enum value
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
        
        # Save test data
        persistence.save_task_breakdown(test_breakdown)
        print("Created test data")
        
        # Test the performance fix - direct lookup
        start_time = time.time()
        result = persistence.get_parent_task_id("test_subtask_456")
        elapsed = time.time() - start_time
        
        print(f"Direct lookup time: {elapsed:.4f}s")
        print(f"Expected: test_parent_123")
        print(f"Got: {result}")
        
        success = (result == "test_parent_123" and elapsed < 0.1)
        
        if success:
            print("SUCCESS: Performance fix working correctly!")
            print(f"Performance target met: {elapsed:.4f}s < 0.1s")
        else:
            print("FAILURE: Performance fix not working")
            
        return success
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = simple_performance_test()
    print("PASSED" if success else "FAILED")
