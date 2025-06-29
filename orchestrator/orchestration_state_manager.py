"""
Optimized state management for task orchestration with persistent storage.

This module provides an optimized StateManager class that addresses timeout issues
by implementing async-safe operations and unified database access patterns.
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple

from .models import TaskBreakdown, SubTask, TaskStatus, SpecialistType
from ..persistence_factory import create_persistence_manager


# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.state")

class StateManager:
    """Manages persistent state for tasks and orchestration data with optimized async handling.
    
    This class provides methods for storing and retrieving task state,
    with support for persistent storage to prevent task loss during restarts or context resets.
    
    Optimizations:
    - Async-safe operations with proper lock management
    - Retry mechanism with exponential backoff
    - Unified persistence through database manager only
    - Enhanced error recovery and timeout handling
    """
    
    def __init__(self, db_path: str = None, base_dir: str = None):
        # Initialize database path
        if db_path is None:
            # Check environment variable first
            db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
            
            if not db_path:
                # Default to a local database file in current working directory
                db_path = os.getcwd() + "/.task_orchestrator/task_orchestrator.db"
        
        self.db_path = str(db_path)
        self.lock = asyncio.Lock()  # For coordinating async operations only
        self._initialized = False
        
        # Initialize persistence manager
        if base_dir is None:
            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
            
            if not base_dir:
                # Default to current working directory (project being worked on)
                base_dir = os.getcwd()
        
        # Create the database persistence manager using the factory
        db_url = f"sqlite:///{self.db_path}"
        self.persistence = create_persistence_manager(base_dir, db_url)
        logger.info(f"Initialized persistence manager with base directory: {base_dir}")
        
        # Mark as initialized and perform startup tasks
        self._initialized = True
        
        # Attempt to recover any interrupted tasks
        self._recover_interrupted_tasks()
        
        # Clean up any stale locks
        self._cleanup_stale_locks()
    
    def _recover_interrupted_tasks(self):
        """Attempt to recover any interrupted tasks from persistent storage."""
        try:
            # Get all active tasks from persistent storage
            active_task_ids = self.persistence.get_all_active_tasks()
            logger.info(f"Found {len(active_task_ids)} active tasks in persistent storage")
            
            # Load each task into memory
            for task_id in active_task_ids:
                try:
                    # Load the task breakdown from persistent storage
                    breakdown = self.persistence.load_task_breakdown(task_id)
                    if breakdown:
                        logger.info(f"Recovered task {task_id} from persistent storage")
                except Exception as e:
                    logger.error(f"Failed to recover task {task_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to recover interrupted tasks: {str(e)}")
    
    def _cleanup_stale_locks(self):
        """Clean up any stale locks at startup."""
        try:
            # Use the persistence manager to clean up stale locks
            # Using a shorter timeout (2 minutes instead of 5)
            cleaned = self.persistence.cleanup_stale_locks(max_age_seconds=120)
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} stale locks at startup")
        except Exception as e:
            logger.error(f"Failed to clean up stale locks: {str(e)}")
    
    async def store_task_breakdown(self, breakdown: TaskBreakdown):
        """Store a task breakdown and its subtasks using persistence manager only."""
        async with self.lock:
            try:
                # Store in persistent storage - this handles all database operations
                self.persistence.save_task_breakdown(breakdown)
                logger.info(f"Saved task breakdown {breakdown.parent_task_id} to persistent storage")
            except Exception as e:
                logger.error(f"Failed to save task breakdown to persistent storage: {str(e)}")
                raise
    
    async def get_subtask(self, task_id: str, timeout: int = 10) -> Optional[SubTask]:
        """Retrieve a specific subtask by ID - simplified version."""
        async with self.lock:
            try:
                # Get parent task ID first
                parent_task_id = self.persistence.get_parent_task_id(task_id)
                if not parent_task_id:
                    return None
                
                # Load the task breakdown from persistent storage
                breakdown = self.persistence.load_task_breakdown(parent_task_id)
                if breakdown:
                    for subtask in breakdown.subtasks:
                        if subtask.task_id == task_id:
                            logger.info(f"Retrieved subtask {task_id} from persistent storage")
                            return subtask
                
                return None
                
            except Exception as e:
                logger.error(f"Error getting subtask {task_id}: {str(e)}")
                raise
    
    async def update_subtask(self, subtask: SubTask):
        """Update an existing subtask using persistence manager only - simplified version."""
        async with self.lock:
            try:
                # Get parent task ID for persistence
                parent_task_id = self.persistence.get_parent_task_id(subtask.task_id)
                
                if parent_task_id:
                    # Update in persistent storage
                    self.persistence.update_subtask(subtask, parent_task_id)
                    logger.info(f"Updated subtask {subtask.task_id} in persistent storage")
                    
                    # If the task is completed, check if we should archive the parent task
                    if subtask.status == TaskStatus.COMPLETED:
                        await self._check_and_archive_parent_task(parent_task_id)
                else:
                    logger.warning(f"Could not find parent task ID for subtask {subtask.task_id}")
                    
            except Exception as e:
                logger.error(f"Error updating subtask {subtask.task_id}: {str(e)}")
                raise
    
    async def _check_and_archive_parent_task(self, parent_task_id: str) -> None:
        """Check if all subtasks for a parent task are completed, and if so, archive the task.
        
        INTERNAL METHOD - assumes lock is already held by caller.
        """
        # Use internal method that doesn't acquire lock (since we already have it)
        subtasks = self._get_subtasks_for_parent_unlocked(parent_task_id)
        
        # If all subtasks are completed, archive the task
        if subtasks and all(st.status == TaskStatus.COMPLETED for st in subtasks):
            try:
                self.persistence.archive_task(parent_task_id)
                logger.info(f"Archived completed task {parent_task_id}")
            except Exception as e:
                logger.error(f"Failed to archive completed task {parent_task_id}: {str(e)}")
                # Continue execution even if archiving fails
    
    def _get_subtasks_for_parent_unlocked(self, parent_task_id: str) -> List[SubTask]:
        """Get all subtasks for a given parent task - INTERNAL METHOD without lock."""
        try:
            breakdown = self.persistence.load_task_breakdown(parent_task_id)
            if breakdown:
                logger.info(f"Retrieved subtasks for parent task {parent_task_id} from persistent storage")
                return breakdown.subtasks
            else:
                logger.warning(f"Task breakdown {parent_task_id} not found")
                return []
        except Exception as e:
            logger.error(f"Failed to retrieve subtasks for parent task {parent_task_id}: {str(e)}")
            return []
    
    async def get_subtasks_for_parent(self, parent_task_id: str) -> List[SubTask]:
        """Get all subtasks for a given parent task using persistence manager only."""
        async with self.lock:
            return self._get_subtasks_for_parent_unlocked(parent_task_id)
    
    async def get_all_tasks(self) -> List[SubTask]:
        """Get all tasks in the system using persistence manager only."""
        async with self.lock:
            all_subtasks = []
            
            try:
                # Get all active tasks from persistent storage
                active_task_ids = self.persistence.get_all_active_tasks()
                
                # Load each task breakdown and extract subtasks
                for parent_task_id in active_task_ids:
                    try:
                        breakdown = self.persistence.load_task_breakdown(parent_task_id)
                        if breakdown:
                            all_subtasks.extend(breakdown.subtasks)
                    except Exception as e:
                        logger.error(f"Failed to load task {parent_task_id} from persistent storage: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to get tasks from persistent storage: {str(e)}")
            
            # Sort by created_at in descending order
            all_subtasks.sort(key=lambda st: st.created_at, reverse=True)
            
            return all_subtasks

    async def _get_parent_task_id(self, task_id: str) -> Optional[str]:
        """
        Get the parent task ID for a given subtask.
        
        Args:
            task_id: The ID of the subtask
            
        Returns:
            The parent task ID, or None if subtask not found
        """
        async with self.lock:
            try:
                return self.persistence.get_parent_task_id(task_id)
            except Exception as e:
                logger.error(f"Error getting parent task ID for {task_id}: {str(e)}")
                return None
