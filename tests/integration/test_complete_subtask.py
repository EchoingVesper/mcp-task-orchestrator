#!/usr/bin/env python3
"""Test the orchestrator complete_subtask operation that was hanging."""

import sys
import os
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

import asyncio
import json
import time

async def test_complete_subtask_operation():
    """Test the specific operation that was causing hangs."""
    print("Testing complete_subtask operation...")
    
    try:
        from mcp_task_orchestrator.orchestrator.state import StateManager
        from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
        from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
        
        print("All imports successful")
        
        # Initialize components
        start_time = time.time()
        state_manager = StateManager()
        specialist_manager = SpecialistManager()
        orchestrator = TaskOrchestrator(state_manager, specialist_manager)
        elapsed = time.time() - start_time
        print(f"Components initialized in {elapsed:.2f}s")
        
        # Get existing tasks
        all_tasks = await state_manager.get_all_tasks()
        print(f"Found {len(all_tasks)} existing tasks")
        
        if all_tasks:
            # Test with an existing task
            test_task = all_tasks[0]
            print(f"Testing with task: {test_task.task_id}")
            
            # Test the complete_subtask operation with timeout
            start_time = time.time()
            try:
                completion_result = await asyncio.wait_for(
                    orchestrator.complete_subtask(
                        test_task.task_id,
                        "Synchronization test - verifying fixes work",
                        ["sync_test_result.txt"],
                        "continue"  # Use continue instead of complete to avoid side effects
                    ),
                    timeout=30.0  # 30 second timeout
                )
                elapsed = time.time() - start_time
                print(f"CRITICAL TEST PASSED: complete_subtask completed in {elapsed:.2f}s")
                print(f"Result: {completion_result}")
                return True
                
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                print(f"CRITICAL TEST FAILED: complete_subtask timed out after {elapsed:.2f}s")
                return False
                
        else:
            print("No existing tasks found - creating a simple test task")
            
            # Create a simple test task
            test_subtasks = [
                {
                    "title": "Synchronization Test Task",
                    "description": "Test task to verify synchronization fixes",
                    "specialist_type": "project_manager",
                    "dependencies": [],
                    "estimated_effort": "5 minutes"
                }
            ]
            
            # Test task planning first
            start_time = time.time()
            breakdown = await asyncio.wait_for(
                orchestrator.plan_task(
                    "Test synchronization fixes",
                    "simple",
                    json.dumps(test_subtasks),
                    "Testing context"
                ),
                timeout=30.0
            )
            elapsed = time.time() - start_time
            print(f"Task planning completed in {elapsed:.2f}s")
            
            if breakdown.subtasks:
                task_id = breakdown.subtasks[0].task_id
                print(f"Created test task: {task_id}")
                
                # Now test complete_subtask
                start_time = time.time()
                try:
                    completion_result = await asyncio.wait_for(
                        orchestrator.complete_subtask(
                            task_id,
                            "Test completed successfully - synchronization fixes verified",
                            ["test_output.txt"],
                            "complete"
                        ),
                        timeout=30.0
                    )
                    elapsed = time.time() - start_time
                    print(f"CRITICAL TEST PASSED: complete_subtask completed in {elapsed:.2f}s")
                    print(f"Result: {completion_result}")
                    return True
                    
                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time
                    print(f"CRITICAL TEST FAILED: complete_subtask timed out after {elapsed:.2f}s")
                    return False
            else:
                print("Failed to create test subtasks")
                return False
        
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting critical synchronization test (complete_subtask operation)...")
    
    success = asyncio.run(test_complete_subtask_operation())
    
    if success:
        print("SUCCESS: The hanging issue in complete_subtask has been FIXED!")
        print("The synchronization improvements are working correctly.")
    else:
        print("FAILURE: The complete_subtask operation is still hanging.")
        print("Additional synchronization work may be needed.")
        
    sys.exit(0 if success else 1)
