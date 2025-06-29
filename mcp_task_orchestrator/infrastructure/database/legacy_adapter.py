"""
Legacy Adapter for gradual migration to repository pattern.

This module provides adapters that allow the existing code to gradually
migrate from direct database access to using the repository pattern.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ...domain.repositories import TaskRepository, StateRepository, SpecialistRepository
from ...orchestrator.generic_models import GenericTask, TaskStatus
from .repository_factory import RepositoryFactory

logger = logging.getLogger(__name__)


class LegacyDatabaseAdapter:
    """
    Adapter that provides a bridge between the old database access patterns
    and the new repository-based architecture.
    """
    
    def __init__(self, repository_factory: RepositoryFactory):
        """
        Initialize the adapter with repository factory.
        
        Args:
            repository_factory: Factory for creating repository instances
        """
        self.repository_factory = repository_factory
        self._task_repo = None
        self._state_repo = None
        self._specialist_repo = None
    
    @property
    def task_repository(self) -> TaskRepository:
        """Get or create task repository."""
        if self._task_repo is None:
            self._task_repo = self.repository_factory.create_task_repository()
        return self._task_repo
    
    @property
    def state_repository(self) -> StateRepository:
        """Get or create state repository."""
        if self._state_repo is None:
            self._state_repo = self.repository_factory.create_state_repository()
        return self._state_repo
    
    @property
    def specialist_repository(self) -> SpecialistRepository:
        """Get or create specialist repository."""
        if self._specialist_repo is None:
            self._specialist_repo = self.repository_factory.create_specialist_repository()
        return self._specialist_repo
    
    # ============================================
    # Task Operations (async -> sync adapter)
    # ============================================
    
    async def create_task_async(self, task: GenericTask) -> GenericTask:
        """
        Async wrapper for creating a task (maintains compatibility).
        
        Args:
            task: GenericTask object
            
        Returns:
            Created task with ID
        """
        # Convert GenericTask to dict for repository
        task_data = {
            'id': task.id,
            'session_id': task.session_id,
            'parent_task_id': task.parent_id,
            'type': task.type.value if hasattr(task.type, 'value') else str(task.type),
            'status': task.status.value if hasattr(task.status, 'value') else str(task.status),
            'title': task.title,
            'description': task.description,
            'metadata': task.metadata or {}
        }
        
        # Create task synchronously (repositories are sync)
        task_id = await asyncio.to_thread(
            self.task_repository.create_task, 
            task_data
        )
        
        task.id = task_id
        return task
    
    async def get_task_async(self, task_id: str) -> Optional[GenericTask]:
        """
        Async wrapper for getting a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            GenericTask object or None
        """
        task_data = await asyncio.to_thread(
            self.task_repository.get_task,
            task_id
        )
        
        if task_data:
            # Convert dict back to GenericTask
            # (simplified - real implementation would handle all fields)
            task = GenericTask(
                id=task_data['id'],
                session_id=task_data['session_id'],
                parent_id=task_data.get('parent_task_id'),
                title=task_data.get('title', ''),
                description=task_data.get('description', ''),
                type=task_data.get('type', 'generic'),
                status=TaskStatus(task_data.get('status', 'pending')),
                metadata=task_data.get('metadata', {})
            )
            return task
        return None
    
    async def update_task_status_async(self, task_id: str, status: TaskStatus) -> bool:
        """
        Async wrapper for updating task status.
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            True if successful
        """
        status_value = status.value if hasattr(status, 'value') else str(status)
        return await asyncio.to_thread(
            self.task_repository.update_task_status,
            task_id,
            status_value
        )
    
    async def get_subtasks_async(self, parent_task_id: str) -> List[GenericTask]:
        """
        Async wrapper for getting subtasks.
        
        Args:
            parent_task_id: Parent task ID
            
        Returns:
            List of GenericTask objects
        """
        task_datas = await asyncio.to_thread(
            self.task_repository.get_subtasks,
            parent_task_id
        )
        
        tasks = []
        for task_data in task_datas:
            task = GenericTask(
                id=task_data['id'],
                session_id=task_data['session_id'],
                parent_id=task_data.get('parent_task_id'),
                title=task_data.get('title', ''),
                description=task_data.get('description', ''),
                type=task_data.get('type', 'generic'),
                status=TaskStatus(task_data.get('status', 'pending')),
                metadata=task_data.get('metadata', {})
            )
            tasks.append(task)
        
        return tasks
    
    # ============================================
    # State Operations
    # ============================================
    
    async def save_session_async(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Async wrapper for saving session."""
        return await asyncio.to_thread(
            self.state_repository.save_session,
            session_id,
            session_data
        )
    
    async def get_session_async(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Async wrapper for getting session."""
        return await asyncio.to_thread(
            self.state_repository.get_session,
            session_id
        )
    
    async def save_context_async(self, session_id: str, context_key: str,
                                context_data: Dict[str, Any]) -> bool:
        """Async wrapper for saving context."""
        return await asyncio.to_thread(
            self.state_repository.save_context,
            session_id,
            context_key,
            context_data
        )
    
    # ============================================
    # Cleanup Operations
    # ============================================
    
    def close(self):
        """Clean up resources."""
        # Repositories don't need explicit cleanup in this implementation
        # but this method is here for compatibility
        pass


def create_legacy_adapter(config: Dict[str, Any]) -> LegacyDatabaseAdapter:
    """
    Create a legacy adapter from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured LegacyDatabaseAdapter instance
    """
    from .repository_factory import create_repository_factory
    
    factory = create_repository_factory(config)
    return LegacyDatabaseAdapter(factory)