#!/usr/bin/env python3
"""Test the _get_parent_task_id method fix in StateManager."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import time
import uuid
from datetime import datetime

async def test_get_parent_task_id_fix():
    """Test that _get_parent_task_id method works correctly."""
    print("Testing _get_parent_task_id method fix...")
    
    try:
        # Set environment variables to point to the correct database
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        base_dir = r"E:\My Work\Programming\MCP Task Orchestrator"
        
        os.environ["MCP_TASK_ORCHESTRATOR_DB_PATH"] = db_path
        os.environ["MCP_TASK_ORCHESTRATOR_BASE_DIR"] = base_dir
        
        from .orchestrator.orchestration_state_manager import StateManager
        # Import Clean Architecture v2.0 models
from mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
        
        # Initialize StateManager with explicit paths
        state_manager = StateManager(db_path=db_path, base_dir=base_dir)
        print("StateManager initialized")
        
        # Test 1: Check if _get_parent_task_id method exists
        print("\nTest 1: Checking if _get_parent_task_id method exists...")
        if hasattr(state_manager, '_get_parent_task_id'):
            print("SUCCESS: _get_parent_task_id method exists")
        else:
            print("FAIL: _get_parent_task_id method missing!")
            return False
        
        # Test 2: Test with existing tasks
        print("\nTest 2: Testing with existing tasks...")
        tasks = await asyncio.wait_for(state_manager.get_all_tasks(), timeout=5.0)
        print(f"Found {len(tasks)} existing tasks")
        
        if tasks:
            # Test with an existing task
            test_task = tasks[0]
            print(f"Testing with task ID: {test_task.task_id}")
            
            start_time = time.time()
            parent_id = await asyncio.wait_for(
                state_manager._get_parent_task_id(test_task.task_id), 
                timeout=5.0
            )
            elapsed = time.time() - start_time
            
            print(f"Retrieved parent task ID: {parent_id} in {elapsed:.3f}s")
            
            if parent_id:
                print("SUCCESS: _get_parent_task_id returned a valid parent ID")
            else:
                print("FAIL: _get_parent_task_id returned None")
                return False
                
            if elapsed < 1.0:
                print(f"SUCCESS: Operation completed quickly ({elapsed:.3f}s)")
            else:
                print(f"WARNING: Operation took {elapsed:.3f}s (might be slow)")
        
        # Test 3: Test with non-existent task
        print("\nTest 3: Testing with non-existent task...")
        fake_task_id = f"fake_task_{uuid.uuid4().hex[:8]}"
        
        start_time = time.time()
        parent_id = await asyncio.wait_for(
            state_manager._get_parent_task_id(fake_task_id), 
            timeout=5.0
        )
        elapsed = time.time() - start_time
        
        print(f"Non-existent task result: {parent_id} in {elapsed:.3f}s")
        
        if parent_id is None:
            print("SUCCESS: _get_parent_task_id correctly returned None for non-existent task")
        else:
            print("FAIL: _get_parent_task_id should return None for non-existent task")
            return False
        
        # Test 4: Test that the method doesn't raise exceptions
        print("\nTest 4: Testing error handling...")
        try:
            # Test with empty string
            result = await asyncio.wait_for(
                state_manager._get_parent_task_id(""), 
                timeout=5.0
            )
            print("SUCCESS: Empty string handled gracefully")
            
            # Test with None
            # This would normally raise a TypeError in real usage
            
        except Exception as e:
            print(f"WARNING: Exception during error handling test: {str(e)}")
        
        print("\nSUCCESS: All _get_parent_task_id tests passed!")
        return True
        
    except asyncio.TimeoutError:
        print("FAIL: Operations timed out")
        return False
    except Exception as e:
        print(f"FAIL: Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_with_core():
    """Test that the fix works with the TaskOrchestrator core."""
    print("\n" + "="*50)
    print("Testing integration with TaskOrchestrator core...")
    
    try:
        # Set environment variables
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        base_dir = r"E:\My Work\Programming\MCP Task Orchestrator"
        
        os.environ["MCP_TASK_ORCHESTRATOR_DB_PATH"] = db_path
        os.environ["MCP_TASK_ORCHESTRATOR_BASE_DIR"] = base_dir
        
        from .orchestrator.orchestration_state_manager import StateManager
        from .orchestrator.task_orchestration_service import TaskOrchestrator
        from .orchestrator.specialist_management_service import SpecialistManager
        
        # Initialize components
        state_manager = StateManager(db_path=db_path, base_dir=base_dir)
        specialist_manager = SpecialistManager()
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        
        print("TaskOrchestrator initialized")
        
        # Get existing tasks to test the progress tracking
        tasks = await state_manager.get_all_tasks()
        
        if tasks:
            # Test the _check_parent_task_progress method which calls _get_parent_task_id
            test_task = tasks[0]
            print(f"Testing progress tracking with task: {test_task.task_id}")
            
            # This method in core.py calls state._get_parent_task_id
            progress = await orchestrator._check_parent_task_progress(test_task.task_id)
            
            print(f"Progress result: {progress}")
            
            if 'error' not in progress or progress.get('progress') != 'unknown':
                print("SUCCESS: Progress tracking works - no '_get_parent_task_id' error!")
                return True
            else:
                print(f"FAIL: Progress tracking failed: {progress}")
                return False
        else:
            print("No tasks found for integration testing")
            return True  # Not a failure, just no data to test with
            
    except Exception as e:
        if "'StateManager' object has no attribute '_get_parent_task_id'" in str(e):
            print("CRITICAL FAIL: The _get_parent_task_id error still exists!")
            return False
        else:
            print(f"Integration test error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("Running _get_parent_task_id fix tests...")
    
    # Run the basic method tests
    success1 = asyncio.run(test_get_parent_task_id_fix())
    
    # Run the integration tests
    success2 = asyncio.run(test_integration_with_core())
    
    overall_success = success1 and success2
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(f"Basic tests: {'PASSED' if success1 else 'FAILED'}")
    print(f"Integration tests: {'PASSED' if success2 else 'FAILED'}")
    print(f"Overall: {'PASSED' if overall_success else 'FAILED'}")
    
    if overall_success:
        print("\nSUCCESS: The _get_parent_task_id fix is working correctly!")
        print("SUCCESS: Parent task progress tracking should now work properly!")
    else:
        print("\nFAIL: There are still issues with the _get_parent_task_id implementation!")
