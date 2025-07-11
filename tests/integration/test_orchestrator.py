#!/usr/bin/env python3
"""
Improved test script for the MCP Task Orchestrator.

This script tests the task orchestrator functionality with proper error handling
and timeout management.
"""

import asyncio
import json
import uuid
import logging
import sys
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_orchestrator")

# Import after configuring logging
from mcp_task_orchestrator.orchestrator.models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
)
from mcp_task_orchestrator.persistence import PersistenceManager
from mcp_task_orchestrator.orchestrator.state import StateManager
from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator

async def cleanup_stale_locks():
    """Clean up any stale lock files."""
    persistence = PersistenceManager()
    locks_dir = persistence.persistence_dir / persistence.LOCKS_DIR
    
    if not locks_dir.exists():
        logger.warning(f"Locks directory not found: {locks_dir}")
        return
    
    logger.info(f"Checking for stale locks in {locks_dir}")
    count = 0
    for lock_file in locks_dir.glob("*.lock"):
        try:
            # Check if the lock file is stale (older than 1 minute)
            if time.time() - lock_file.stat().st_mtime > 60:
                lock_file.unlink()
                count += 1
                logger.info(f"Removed stale lock file: {lock_file.name}")
        except Exception as e:
            logger.warning(f"Failed to check/remove lock file {lock_file}: {str(e)}")
    
    logger.info(f"Removed {count} stale lock files")

async def test_task_orchestrator():
    """Test the task orchestrator functionality."""
    logger.info("=== Testing Task Orchestrator ===")
    
    # Clean up stale locks first
    await cleanup_stale_locks()
    
    # Initialize managers
    base_dir = Path(__file__).parent
    persistence = PersistenceManager(base_dir)
    state_manager = StateManager(base_dir=base_dir)
    
    try:
        # Rest of the test logic will remain the same...
        # (I'll preserve the existing test logic and just add cleanup at the end)
        
        # Initialize orchestrator
        orchestrator = TaskOrchestrator(
            persistence=persistence,
            state_manager=state_manager,
            specialist_manager=SpecialistManager()
        )
        
        # Create a test task
        task_breakdown = TaskBreakdown(
            title="Test Task for Orchestrator",
            description="A test task to verify orchestrator functionality",
            complexity=ComplexityLevel.MODERATE,
            subtasks=[
                SubTask(
                    task_id="test_subtask_001",
                    title="Test Subtask",
                    description="A test subtask",
                    specialist_type=SpecialistType.IMPLEMENTER,
                    status=TaskStatus.PENDING
                )
            ]
        )
        
        # Test task planning
        logger.info("Testing plan_task...")
        parent_task_id = await orchestrator.plan_task(task_breakdown)
        logger.info(f"✅ Task planned successfully with ID: {parent_task_id}")
        
        # Test subtask execution
        subtask_id = task_breakdown.subtasks[0].task_id
        logger.info(f"Testing execute_subtask for {subtask_id}...")
        execution_context = await orchestrator.execute_subtask(subtask_id)
        logger.info("✅ Subtask execution context provided")
        logger.info(f"Context length: {len(execution_context)}")
        
        # Test subtask completion
        logger.info(f"Testing complete_subtask for {subtask_id}...")
        result = await orchestrator.complete_subtask(
            task_id=subtask_id,
            results="Test completion results",
            artifacts=["test_artifact.txt"],
            next_action="complete"
        )
        logger.info("✅ Subtask completed successfully")
        logger.info(f"Result status: {result.get('status')}")
        
        # Verify subtask status
        subtask = await state_manager.get_subtask(subtask_id)
        if subtask and subtask.status == TaskStatus.COMPLETED:
            logger.info("✅ Subtask status correctly updated to COMPLETED")
        else:
            logger.warning(f"⚠️ Unexpected subtask status: {subtask.status if subtask else 'None'}")
    
        # Test synthesize_results
        try:
            logger.info(f"Testing synthesize_results for task {parent_task_id}...")
            synthesis = await orchestrator.synthesize_results(parent_task_id)
            logger.info("✅ Results synthesized successfully")
            logger.info(f"Synthesis length: {len(synthesis)}")
        except Exception as e:
            logger.error(f"❌ Failed to synthesize results: {str(e)}")
            
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        raise
    finally:
        # Cleanup database connections
        try:
            if hasattr(persistence, 'dispose') and callable(getattr(persistence, 'dispose')):
                persistence.dispose()
                logger.info("✅ Persistence manager disposed")
            elif hasattr(persistence, 'engine') and persistence.engine is not None:
                persistence.engine.dispose()
                logger.info("✅ Persistence engine disposed manually")
        except Exception as e:
            logger.warning(f"⚠️ Error disposing persistence manager: {str(e)}")
    
    logger.info("=== Task Orchestrator Test Completed ===")
    specialist_manager = SpecialistManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    # Create a test task
    parent_task_id = f"test_task_{uuid.uuid4().hex[:8]}"
    logger.info(f"Creating test task: {parent_task_id}")
    
    # Create subtasks
    subtasks = [
        SubTask(
            task_id=f"architect_{uuid.uuid4().hex[:6]}",
            title="Design Test Architecture",
            description="Design a simple test architecture",
            specialist_type=SpecialistType.ARCHITECT,
            dependencies=[],
            estimated_effort="10 minutes"
        ),
        SubTask(
            task_id=f"implementer_{uuid.uuid4().hex[:6]}",
            title="Implement Test Feature",
            description="Implement a simple test feature",
            specialist_type=SpecialistType.IMPLEMENTER,
            dependencies=[],
            estimated_effort="15 minutes"
        )
    ]
    
    # Create task breakdown
    breakdown = TaskBreakdown(
        parent_task_id=parent_task_id,
        description="Test task for orchestrator",
        complexity=ComplexityLevel.SIMPLE,
        subtasks=subtasks,
        context="Testing orchestrator functionality"
    )
    
    # Save task breakdown
    try:
        logger.info("Storing task breakdown...")
        await state_manager.store_task_breakdown(breakdown)
        logger.info("✅ Task breakdown stored successfully")
    except Exception as e:
        logger.error(f"❌ Failed to store task breakdown: {str(e)}")
        return
    
    # Test initialize_session
    try:
        logger.info("Testing initialize_session...")
        session_info = await orchestrator.initialize_session()
        logger.info("✅ Session initialized successfully")
        logger.info(f"Session role: {session_info.get('role')}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize session: {str(e)}")
    
    # Test get_status
    try:
        logger.info("Testing get_status...")
        status = await orchestrator.get_status(include_completed=True)
        logger.info("✅ Status retrieved successfully")
        logger.info(f"Active tasks: {status.get('active_tasks')}")
        logger.info(f"Pending tasks: {status.get('pending_tasks')}")
        logger.info(f"Completed tasks: {status.get('completed_tasks')}")
    except Exception as e:
        logger.error(f"❌ Failed to get status: {str(e)}")
    
    # Test get_specialist_context
    subtask_id = subtasks[0].task_id
    try:
        logger.info(f"Testing get_specialist_context for subtask {subtask_id}...")
        specialist_context = await orchestrator.get_specialist_context(subtask_id)
        logger.info("✅ Specialist context retrieved successfully")
        logger.info(f"Context length: {len(specialist_context)}")
        
        # Verify subtask status
        subtask = await state_manager.get_subtask(subtask_id)
        if subtask and subtask.status == TaskStatus.ACTIVE:
            logger.info("✅ Subtask status correctly updated to ACTIVE")
        else:
            logger.warning(f"⚠️ Unexpected subtask status: {subtask.status if subtask else 'None'}")
    except Exception as e:
        logger.error(f"❌ Failed to get specialist context: {str(e)}")
    
    # Test complete_subtask
    try:
        logger.info(f"Testing complete_subtask for subtask {subtask_id}...")
        result = await orchestrator.complete_subtask(
            subtask_id,
            "Test results for orchestrator",
            ["test_artifact.md"],
            "continue"
        )
        logger.info("✅ Subtask completed successfully")
        logger.info(f"Result status: {result.get('status')}")
        
        # Verify subtask status
        subtask = await state_manager.get_subtask(subtask_id)
        if subtask and subtask.status == TaskStatus.COMPLETED:
            logger.info("✅ Subtask status correctly updated to COMPLETED")
        else:
            logger.warning(f"⚠️ Unexpected subtask status: {subtask.status if subtask else 'None'}")
    except Exception as e:
        logger.error(f"❌ Failed to complete subtask: {str(e)}")
    
    # Test synthesize_results
    try:
        logger.info(f"Testing synthesize_results for task {parent_task_id}...")
        synthesis = await orchestrator.synthesize_results(parent_task_id)
        logger.info("✅ Results synthesized successfully")
        logger.info(f"Synthesis length: {len(synthesis)}")
    except Exception as e:
        logger.error(f"❌ Failed to synthesize results: {str(e)}")
    
    # Cleanup database connections
    try:
        if hasattr(persistence, 'dispose') and callable(getattr(persistence, 'dispose')):
            persistence.dispose()
            logger.info("✅ Persistence manager disposed")
        elif hasattr(persistence, 'engine') and persistence.engine is not None:
            persistence.engine.dispose()
            logger.info("✅ Persistence engine disposed manually")
    except Exception as e:
        logger.warning(f"⚠️ Error disposing persistence manager: {str(e)}")
    
    logger.info("=== Task Orchestrator Test Completed ===")

async def main():
    """Main entry point."""
    try:
        await test_task_orchestrator()
    except Exception as e:
        logger.error(f"Unhandled exception in test: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
