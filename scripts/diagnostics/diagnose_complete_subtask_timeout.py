#!/usr/bin/env python3
"""
Diagnostic script to investigate complete_subtask timeout issues.

This script measures the performance of each component in the complete_subtask
operation to identify exactly where the bottleneck is occurring.
"""

import asyncio
import time
import logging
from pathlib import Path

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.orchestrator.state import StateManager
from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
from mcp_task_orchestrator.orchestrator.models import TaskStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("timeout_diagnosis")

async def time_operation(name: str, coro, *args, **kwargs):
    """Time an async operation and log the results."""
    start_time = time.time()
    try:
        result = await coro(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"✅ {name}: {elapsed:.4f}s")
        return result, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ {name}: {elapsed:.4f}s - ERROR: {str(e)}")
        return None, elapsed

async def diagnose_complete_subtask_performance():
    """Diagnose performance issues in complete_subtask operation."""
    
    print("🔍 Starting Complete Subtask Timeout Diagnosis")
    print("=" * 60)
    
    # Initialize components
    base_dir = Path(__file__).parent
    state_manager = StateManager(base_dir=base_dir)
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    # Find a suitable test task
    all_tasks, _ = await time_operation(
        "Get all tasks", 
        state_manager.get_all_tasks
    )
    
    if not all_tasks:
        print("❌ No tasks found for testing")
        return
    
    # Find a pending task to test with
    test_task = None
    for task in all_tasks:
        if task.status == TaskStatus.PENDING:
            test_task = task
            break
    
    if not test_task:
        print("❌ No pending tasks found for testing")
        # Use the first available task anyway for testing
        test_task = all_tasks[0]
    
    task_id = test_task.task_id
    print(f"🎯 Testing with task: {task_id} ({test_task.title})")
    print()
    
    # Step 1: Test individual StateManager operations
    print("📊 Testing StateManager Operations:")
    print("-" * 40)
    
    subtask, _ = await time_operation(
        "get_subtask()", 
        state_manager.get_subtask, 
        task_id
    )
    
    if subtask:
        # Modify subtask for testing
        original_status = subtask.status
        original_results = subtask.results
        
        subtask.status = TaskStatus.COMPLETED
        subtask.results = "Test completion results"
        subtask.artifacts = ["test_artifact.py"]
        
        _, update_time = await time_operation(
            "update_subtask()", 
            state_manager.update_subtask, 
            subtask
        )
        
        # Test parent task lookup
        _, parent_lookup_time = await time_operation(
            "_get_parent_task_id()", 
            state_manager._get_parent_task_id, 
            task_id
        )
        
        # Test getting subtasks for parent
        parent_id = await state_manager._get_parent_task_id(task_id)
        if parent_id:
            _, parent_subtasks_time = await time_operation(
                "get_subtasks_for_parent()", 
                state_manager.get_subtasks_for_parent, 
                parent_id
            )
        else:
            parent_subtasks_time = 0
            print("⚠️  No parent task found for subtask")
        
        # Restore original state
        subtask.status = original_status
        subtask.results = original_results
        subtask.artifacts = []
        await state_manager.update_subtask(subtask)
    
    print()
    
    # Step 2: Test TaskOrchestrator helper methods
    print("🔧 Testing TaskOrchestrator Helper Methods:")
    print("-" * 40)
    
    _, parent_progress_time = await time_operation(
        "_check_parent_task_progress()", 
        orchestrator._check_parent_task_progress, 
        task_id
    )
    
    _, next_task_time = await time_operation(
        "_get_next_recommended_task()", 
        orchestrator._get_next_recommended_task, 
        task_id
    )
    
    print()
    
    # Step 3: Test parallel execution of helper methods
    print("⚡ Testing Parallel Helper Method Execution:")
    print("-" * 40)
    
    start_time = time.time()
    try:
        parent_progress, next_task = await asyncio.gather(
            orchestrator._check_parent_task_progress(task_id),
            orchestrator._get_next_recommended_task(task_id)
        )
        parallel_time = time.time() - start_time
        logger.info(f"✅ asyncio.gather() for helpers: {parallel_time:.4f}s")
    except Exception as e:
        parallel_time = time.time() - start_time
        logger.error(f"❌ asyncio.gather() for helpers: {parallel_time:.4f}s - ERROR: {str(e)}")
    
    print()
    
    # Step 4: Test full complete_subtask operation
    print("🎯 Testing Full complete_subtask Operation:")
    print("-" * 40)
    
    _, full_operation_time = await time_operation(
        "complete_subtask() - FULL", 
        orchestrator.complete_subtask, 
        task_id, 
        "Test completion results", 
        ["test_artifact.py"], 
        "continue"
    )
    
    print()
    
    # Summary and Analysis
    print("📋 PERFORMANCE ANALYSIS SUMMARY:")
    print("=" * 60)
    
    # Calculate total expected time
    individual_ops_time = (
        _.get('get_subtask', 0) if 'get_subtask' in locals() else 0 +
        update_time if 'update_time' in locals() else 0 +
        parent_lookup_time if 'parent_lookup_time' in locals() else 0 +
        parent_subtasks_time if 'parent_subtasks_time' in locals() else 0
    )
    
    print(f"Individual operations total time: ~{individual_ops_time:.4f}s")
    print(f"Helper methods parallel time:     {parallel_time:.4f}s")
    print(f"Full complete_subtask time:       {full_operation_time:.4f}s")
    
    # Identify bottlenecks
    if full_operation_time > 30:
        print("\n🚨 TIMEOUT CAUSE IDENTIFIED:")
        print(f"   complete_subtask() takes {full_operation_time:.4f}s > 30s timeout")
    elif full_operation_time > 10:
        print("\n⚠️  PERFORMANCE WARNING:")
        print(f"   complete_subtask() takes {full_operation_time:.4f}s - approaching timeout")
    else:
        print("\n✅ PERFORMANCE OK:")
        print(f"   complete_subtask() takes {full_operation_time:.4f}s - well within timeout")
    
    # Specific bottleneck analysis
    print("\n🔍 BOTTLENECK ANALYSIS:")
    
    bottlenecks = []
    if parent_lookup_time > 5:
        bottlenecks.append(f"Parent task lookup: {parent_lookup_time:.4f}s")
    if parent_subtasks_time > 5:
        bottlenecks.append(f"Get parent subtasks: {parent_subtasks_time:.4f}s")
    if update_time > 5:
        bottlenecks.append(f"Update subtask: {update_time:.4f}s")
    if parallel_time > 10:
        bottlenecks.append(f"Helper method execution: {parallel_time:.4f}s")
    
    if bottlenecks:
        print("   Identified bottlenecks:")
        for bottleneck in bottlenecks:
            print(f"   - {bottleneck}")
    else:
        print("   No obvious bottlenecks identified in individual operations")
        if full_operation_time > individual_ops_time + parallel_time + 5:
            print("   ⚠️  Significant overhead in orchestrator logic or retry mechanisms")
    
    print("\n📝 RECOMMENDATIONS:")
    
    if full_operation_time > 30:
        print("   1. Reduce MCP timeout or optimize complete_subtask logic")
        print("   2. Consider breaking operation into smaller, non-blocking steps")
        print("   3. Implement async progress reporting instead of waiting for completion")
    
    if parallel_time > individual_ops_time:
        print("   1. Consider sequential execution instead of parallel for helper methods")
        print("   2. Investigate potential lock contention in parallel operations")
    
    if any('ERROR' in str(locals().get(var, '')) for var in locals()):
        print("   1. Fix errors in individual operations before optimizing")
        print("   2. Investigate database connection or state management issues")
    
    print("\n✅ Diagnosis complete!")

async def main():
    """Main entry point."""
    try:
        await diagnose_complete_subtask_performance()
    except Exception as e:
        logger.error(f"Diagnosis failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
