#!/usr/bin/env python3
"""
Performance Test for MCP Task Orchestrator
"""

import asyncio
import time
import sys
import os

# Add project path
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

async def test_orchestrator_performance():
    """Run performance tests."""
    print("MCP Task Orchestrator Performance Benchmark")
    print("=" * 50)
    
    results = {}
    
    try:
        # Test 1: StateManager Initialization
        print("Testing StateManager initialization...")
        start = time.time()
        
        from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager
        db_path = r"E:\My Work\Programming\MCP Task Orchestrator\task_orchestrator.db"
        state_manager = StateManager(db_path=db_path)
        
        init_time = time.time() - start
        results["state_manager_init"] = init_time
        print(f"StateManager init: {init_time:.4f}s")
        
        # Test 2: Get All Tasks
        print("Testing get_all_tasks...")
        start = time.time()
        
        tasks = await asyncio.wait_for(
            state_manager.get_all_tasks(), 
            timeout=10.0
        )
        
        get_tasks_time = time.time() - start
        results["get_all_tasks"] = get_tasks_time
        print(f"Get {len(tasks)} tasks: {get_tasks_time:.4f}s")
        
        if tasks:
            test_task = tasks[0]
            
            # Test 3: Direct Parent Lookup (our fix)
            print("Testing direct parent lookup...")
            start = time.time()
            
            parent_id = state_manager.persistence.get_parent_task_id(test_task.task_id)
            
            lookup_time = time.time() - start
            results["direct_parent_lookup"] = lookup_time
            print(f"Direct lookup: {lookup_time:.4f}s")
            
            # Test 4: Get Single Subtask
            print("Testing get_subtask...")
            start = time.time()
            
            retrieved_task = await asyncio.wait_for(
                state_manager.get_subtask(test_task.task_id),
                timeout=10.0
            )
            
            get_subtask_time = time.time() - start
            results["get_subtask"] = get_subtask_time
            print(f"Get subtask: {get_subtask_time:.4f}s")
            
            # Test 5: Update Subtask (the critical test)
            print("Testing update_subtask...")
            start = time.time()
            
            if retrieved_task:
                await asyncio.wait_for(
                    state_manager.update_subtask(retrieved_task),
                    timeout=10.0
                )
                
                update_time = time.time() - start
                results["update_subtask"] = update_time
                print(f"Update subtask: {update_time:.4f}s")
        
        # Generate report
        print("\nPerformance Report")
        print("=" * 50)
        
        slow_operations = []
        for op_name, duration in results.items():
            status = "PASS" if duration < 5.0 else "SLOW"
            if duration >= 5.0:
                slow_operations.append((op_name, duration))
            print(f"{status:6} {op_name:25} {duration:8.4f}s")
        
        print(f"\nTotal operations: {len(results)}")
        print(f"Slow operations: {len(slow_operations)}")
        
        if slow_operations:
            print("\nSLOW OPERATIONS:")
            for op_name, duration in slow_operations:
                print(f"   {op_name}: {duration:.4f}s")
        else:
            print("\nSUCCESS: All operations completed within 5-second threshold!")
        
        return results
        
    except asyncio.TimeoutError as e:
        print(f"TIMEOUT ERROR: {str(e)}")
        return results
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return results

if __name__ == "__main__":
    asyncio.run(test_orchestrator_performance())
