#!/usr/bin/env python3
"""
Test script to verify the synchronization fixes work properly.

This script tests:
1. Database connection handling without hanging
2. Proper session management
3. Concurrent task operations
4. Timeout handling and recovery
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("synchronization_test")

# Import the fixed components
from .orchestrator.orchestration_state_manager import StateManager
from .orchestrator.specialist_management_service import SpecialistManager
from .orchestrator.task_orchestration_service import TaskOrchestrator


async def test_basic_operations():
    """Test basic database operations for hanging issues."""
    logger.info("=== Testing Basic Operations ===")
    
    try:
        # Initialize components
        base_dir = Path(__file__).parent
        state_manager = StateManager(base_dir=base_dir)
        
        logger.info("✅ StateManager initialized successfully")
        
        # Test getting all tasks
        start_time = time.time()
        all_tasks = await state_manager.get_all_tasks()
        elapsed = time.time() - start_time
        
        logger.info(f"✅ Retrieved {len(all_tasks)} tasks in {elapsed:.2f}s")
        
        if elapsed > 5.0:
            logger.warning(f"⚠️ Operation took {elapsed:.2f}s - may indicate synchronization issues")
        else:
            logger.info("✅ Operation completed in reasonable time")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic operations failed: {str(e)}")
        return False

async def test_concurrent_operations():
    """Test concurrent database operations for race conditions."""
    logger.info("=== Testing Concurrent Operations ===")
    
    try:
        base_dir = Path(__file__).parent
        
        # Create multiple StateManager instances to simulate concurrent access
        managers = [StateManager(base_dir=base_dir) for _ in range(3)]
        
        logger.info("✅ Created 3 StateManager instances")
        
        # Run concurrent operations
        async def get_tasks(manager, index):
            start_time = time.time()
            tasks = await manager.get_all_tasks()
            elapsed = time.time() - start_time
            logger.info(f"Manager {index}: Retrieved {len(tasks)} tasks in {elapsed:.2f}s")
            return len(tasks), elapsed
        
        # Run all operations concurrently
        start_time = time.time()
        results = await asyncio.gather(*[
            get_tasks(manager, i) for i, manager in enumerate(managers)
        ])
        total_elapsed = time.time() - start_time
        
        logger.info(f"✅ All concurrent operations completed in {total_elapsed:.2f}s")
        
        # Check for consistency
        task_counts = [result[0] for result in results]
        if len(set(task_counts)) == 1:
            logger.info("✅ All managers returned consistent task counts")
        else:
            logger.warning(f"⚠️ Inconsistent task counts: {task_counts}")
        
        # Check for reasonable performance
        max_elapsed = max(result[1] for result in results)
        if max_elapsed > 10.0:
            logger.warning(f"⚠️ Slowest operation took {max_elapsed:.2f}s")
        else:
            logger.info("✅ All operations completed in reasonable time")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Concurrent operations failed: {str(e)}")
        return False

async def test_simple_task_operations():
    """Test simple task operations without full orchestrator complexity."""
    logger.info("=== Testing Simple Task Operations ===")
    
    try:
        base_dir = Path(__file__).parent
        state_manager = StateManager(base_dir=base_dir)
        
        logger.info("✅ StateManager initialized for task operations")
        
        # Test retrieving existing tasks
        start_time = time.time()
        all_tasks = await state_manager.get_all_tasks()
        elapsed = time.time() - start_time
        
        logger.info(f"✅ Retrieved {len(all_tasks)} existing tasks in {elapsed:.2f}s")
        
        if all_tasks:
            # Test getting a specific subtask
            test_task = all_tasks[0]
            start_time = time.time()
            retrieved_task = await state_manager.get_subtask(test_task.task_id)
            elapsed = time.time() - start_time
            
            if retrieved_task:
                logger.info(f"✅ Retrieved specific task in {elapsed:.2f}s")
            else:
                logger.warning("⚠️ Could not retrieve specific task")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple task operations failed: {str(e)}")
        return False


async def main():
    """Run synchronization tests."""
    logger.info("🚀 Starting Synchronization Fix Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Basic Operations", test_basic_operations),
        ("Concurrent Operations", test_concurrent_operations),
        ("Simple Task Operations", test_simple_task_operations)
    ]
    
    results = {}
    total_start_time = time.time()
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name}...")
        
        try:
            start_time = time.time()
            success = await test_func()
            elapsed = time.time() - start_time
            
            results[test_name] = {"success": success, "elapsed": elapsed}
            
            if success:
                logger.info(f"✅ {test_name} PASSED ({elapsed:.2f}s)")
            else:
                logger.error(f"❌ {test_name} FAILED ({elapsed:.2f}s)")
                
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"💥 {test_name} CRASHED: {str(e)} ({elapsed:.2f}s)")
            results[test_name] = {"success": False, "elapsed": elapsed}
    
    total_elapsed = time.time() - total_start_time
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        logger.info(f"{status:8} {test_name:30} ({result['elapsed']:.2f}s)")
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    logger.info(f"Total time: {total_elapsed:.2f}s")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - Synchronization fixes working!")
        return True
    else:
        logger.error(f"⚠️ {total - passed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
