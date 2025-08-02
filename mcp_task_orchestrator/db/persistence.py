"""
Database Persistence Manager - Compatibility wrapper for GenericTaskRepository

This module provides a compatibility wrapper that bridges the old DatabasePersistenceManager
interface with the new GenericTaskRepository implementation.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from .repository.base import TaskRepository
from ..domain.entities.task import Task

logger = logging.getLogger(__name__)


class DatabasePersistenceManager:
    """
    Compatibility wrapper for the GenericTaskRepository.
    
    This class provides the same interface as the original DatabasePersistenceManager
    but delegates to the GenericTaskRepository for actual database operations.
    """
    
    def __init__(self, base_dir: Optional[str] = None, db_url: Optional[str] = None):
        """Initialize the database persistence manager."""
        self.base_dir = base_dir or str(Path.cwd())
        self.db_url = db_url or f"sqlite:///{self.base_dir}/.task_orchestrator/tasks.db"
        self._repository = TaskRepository(db_url=self.db_url)
        logger.info(f"DatabasePersistenceManager initialized with base_dir: {self.base_dir}")
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task."""
        return await self._repository.create_task(task_data)
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return await self._repository.get_task(task_id)
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update a task."""
        return await self._repository.update_task(task_id, updates)
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return await self._repository.delete_task(task_id)
    
    async def query_tasks(self, filters: Dict[str, Any]) -> List[Task]:
        """Query tasks with filters."""
        return await self._repository.query_tasks(filters)
    
    async def get_all_tasks(self) -> List[Task]:
        """Get all tasks."""
        return await self._repository.get_all_tasks()
    
    async def initialize_database(self) -> bool:
        """Initialize the database."""
        return await self._repository.initialize_database()
    
    async def get_all_active_tasks(self) -> List[str]:
        """Get all active task IDs from the database."""
        try:
            # Get all tasks that are not archived or cancelled
            filters = {
                "status": ["pending", "in_progress", "active", "planned", "executing"]
            }
            active_tasks = await self._repository.query_tasks(filters)
            
            # Extract task IDs
            task_ids = [task.task_id for task in active_tasks]
            logger.info(f"Retrieved {len(task_ids)} active task IDs")
            return task_ids
            
        except Exception as e:
            logger.error(f"Failed to get active tasks: {str(e)}")
            return []
    
    async def cleanup_stale_locks(self, max_age_seconds: int = 120) -> int:
        """Clean up stale database locks older than max_age_seconds."""
        try:
            # Delegate to repository if it has the method
            if hasattr(self._repository, 'cleanup_stale_locks'):
                cleaned_count = await self._repository.cleanup_stale_locks(max_age_seconds)
                logger.info(f"Cleaned up {cleaned_count} stale locks")
                return cleaned_count
            else:
                # Fallback implementation - this would typically interact with database lock tables
                logger.warning("Repository does not support stale lock cleanup, using fallback")
                # In a real implementation, this would clean up database locks/sessions
                # For now, return 0 to indicate no locks were cleaned
                return 0
                
        except Exception as e:
            logger.error(f"Failed to cleanup stale locks: {str(e)}")
            return 0

    async def save_task_breakdown(self, breakdown: Task) -> bool:
        """Save task breakdown data."""
        try:
            # Convert the Task object to dict for storage
            task_data = {
                "task_id": breakdown.task_id,
                "title": breakdown.title,
                "description": breakdown.description,
                "status": breakdown.status.value if hasattr(breakdown.status, 'value') else str(breakdown.status),
                "task_type": breakdown.task_type.value if hasattr(breakdown.task_type, 'value') else str(breakdown.task_type),
                "specialist_type": breakdown.specialist_type.value if hasattr(breakdown.specialist_type, 'value') else str(breakdown.specialist_type),
                "complexity": breakdown.complexity.value if hasattr(breakdown.complexity, 'value') else str(breakdown.complexity),
                "parent_task_id": breakdown.parent_task_id,
                "dependencies": breakdown.dependencies or [],
                "context": breakdown.context or {},
                "estimated_effort": breakdown.estimated_effort,
                "due_date": breakdown.due_date.isoformat() if breakdown.due_date else None,
                "created_at": breakdown.created_at.isoformat() if breakdown.created_at else None,
                "updated_at": breakdown.updated_at.isoformat() if breakdown.updated_at else None
            }
            
            # Check if task already exists and update, otherwise create
            existing_task = await self.get_task(breakdown.task_id)
            if existing_task:
                updated_task = await self.update_task(breakdown.task_id, task_data)
                return updated_task is not None
            else:
                created_task = await self.create_task(task_data)
                return created_task is not None
                
        except Exception as e:
            logger.error(f"Failed to save task breakdown: {str(e)}")
            return False

    async def close(self):
        """Close the database connection."""
        if hasattr(self._repository, 'close'):
            await self._repository.close()