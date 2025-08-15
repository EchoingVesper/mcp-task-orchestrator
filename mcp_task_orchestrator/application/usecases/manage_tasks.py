"""
Use case for managing generic tasks.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Import domain repository interface instead of infrastructure implementation
from ...domain.repositories.task_repository import TaskRepository


@dataclass
class TaskUseCase:
    """
    Use case for managing generic tasks following Clean Architecture principles.
    
    This use case provides a clean interface to task management operations,
    using domain repository interfaces instead of direct infrastructure dependencies.
    """
    repository: TaskRepository
    
    async def create_task(self, task_data: Dict[str, Any]) -> Any:
        """Create a new task using the repository."""
        return await self.repository.create_task_from_dict(task_data)
    
    async def get_task(self, task_id: str) -> Any:
        """Get a task by ID."""
        return await self.repository.get_task(task_id)
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Any:
        """Update an existing task."""
        return await self.repository.update_task(task_id, update_data)
    
    async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
        """Delete a task."""
        return await self.repository.delete_task(task_id, force, archive_instead)
    
    async def cancel_task(self, task_id: str, reason: str, preserve_work: bool = True) -> Dict[str, Any]:
        """Cancel a task."""
        return await self.repository.cancel_task(task_id, reason, preserve_work)
    
    async def query_tasks(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query tasks with filters."""
        return await self.repository.query_tasks(filters)