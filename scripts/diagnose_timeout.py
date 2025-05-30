#!/usr/bin/env python3
"""
Diagnostic script to identify and fix timeout issues in the MCP Task Orchestrator.

This script:
1. Analyzes the lock acquisition patterns
2. Tests subtask completion with instrumentation
3. Identifies bottlenecks in the process
4. Provides recommendations for fixes
"""

import os
import sys
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_task_orchestrator.orchestrator import TaskOrchestrator, StateManager, SpecialistManager
from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("timeout_diagnostics")

# Create a file handler
log_file = Path(__file__).parent / "timeout_diagnostics.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(file_handler)

class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    async def __aenter__(self):
        self.start_time = time.time()
        logger.info(f"Starting operation: {self.operation_name}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type:
            logger.error(f"Operation {self.operation_name} failed after {duration:.2f}s: {exc_val}")
        else:
            logger.info(f"Operation {self.operation_name} completed in {duration:.2f}s")


async def create_test_task() -> str:
    """Create a test task with subtasks for diagnostics."""
    logger.info("Creating test task")
    
    # Initialize components
    base_dir = Path(__file__).parent.parent
    state_manager = StateManager(base_dir=base_dir)
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    # Create a simple task breakdown
    description = "Test task for timeout diagnostics"
    complexity = "simple"
    subtasks_json = """[
        {
            "title": "Subtask 1",
            "description": "First test subtask",
            "specialist_type": "implementer",
            "dependencies": [],
            "estimated_effort": "small"
        },
        {
            "title": "Subtask 2",
            "description": "Second test subtask",
            "specialist_type": "debugger",
            "dependencies": [],
            "estimated_effort": "small"
        }
    ]"""
    
    async with TimingContext("plan_task"):
        breakdown = await orchestrator.plan_task(description, complexity, subtasks_json)
    
    logger.info(f"Created task with ID: {breakdown.parent_task_id}")
    logger.info(f"Subtask IDs: {[st.task_id for st in breakdown.subtasks]}")
    
    return breakdown.subtasks[0].task_id


async def test_complete_subtask(task_id: str, with_instrumentation: bool = False):
    """Test the complete_subtask function with timing instrumentation."""
    logger.info(f"Testing complete_subtask for task {task_id}")
    
    # Initialize components
    base_dir = Path(__file__).parent.parent
    state_manager = StateManager(base_dir=base_dir)
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    # Prepare test data
    results = "Test results for diagnostics"
    artifacts = ["test_artifact_1", "test_artifact_2"]
    next_action = "continue"
    
    if with_instrumentation:
        # Replace the original methods with instrumented versions
        original_get_subtask = state_manager.get_subtask
        original_update_subtask = state_manager.update_subtask
        
        async def instrumented_get_subtask(task_id: str, timeout: int = 10):
            async with TimingContext(f"get_subtask({task_id})"):
                return await original_get_subtask(task_id, timeout)
        
        async def instrumented_update_subtask(subtask):
            async with TimingContext(f"update_subtask({subtask.task_id})"):
                return await original_update_subtask(subtask)
        
        # Apply instrumentation
        state_manager.get_subtask = instrumented_get_subtask
        state_manager.update_subtask = instrumented_update_subtask
    
    # Test the complete_subtask function with timing
    try:
        async with TimingContext("complete_subtask"):
            result = await orchestrator.complete_subtask(task_id, results, artifacts, next_action)
        
        logger.info(f"Complete subtask result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in complete_subtask: {str(e)}")
        raise


async def analyze_lock_patterns():
    """Analyze lock acquisition patterns in the StateManager."""
    logger.info("Analyzing lock patterns")
    
    # Initialize components
    base_dir = Path(__file__).parent.parent
    state_manager = StateManager(base_dir=base_dir)
    
    # Count lock files
    locks_dir = Path(base_dir) / ".task_orchestrator" / "locks"
    lock_files = list(locks_dir.glob("*.lock"))
    logger.info(f"Found {len(lock_files)} lock files")
    
    # Check for stale locks
    stale_locks = 0
    for lock_file in lock_files:
        if time.time() - lock_file.stat().st_mtime > 300:  # 5 minutes
            stale_locks += 1
            logger.warning(f"Stale lock found: {lock_file}")
    
    logger.info(f"Found {stale_locks} stale locks out of {len(lock_files)}")
    
    # Test lock cleanup
    if stale_locks > 0:
        logger.info("Testing lock cleanup")
        from mcp_task_orchestrator.persistence import PersistenceManager
        persistence = PersistenceManager(base_dir=base_dir)
        cleaned = persistence.cleanup_stale_locks(max_age_seconds=300)
        logger.info(f"Cleaned up {cleaned} stale locks")


async def main():
    """Main diagnostic function."""
    logger.info("Starting timeout diagnostics")
    
    # Analyze lock patterns
    await analyze_lock_patterns()
    
    # Create a test task
    task_id = await create_test_task()
    
    # Test complete_subtask without instrumentation
    logger.info("Testing complete_subtask without instrumentation")
    try:
        await test_complete_subtask(task_id, with_instrumentation=False)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    
    # Create another test task
    task_id = await create_test_task()
    
    # Test complete_subtask with instrumentation
    logger.info("Testing complete_subtask with instrumentation")
    try:
        await test_complete_subtask(task_id, with_instrumentation=True)
    except Exception as e:
        logger.error(f"Test with instrumentation failed: {str(e)}")
    
    logger.info("Diagnostics completed")


if __name__ == "__main__":
    asyncio.run(main())
