"""
Async Task Repository interface.

This module defines the contract for async task persistence operations that 
infrastructure implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class AsyncTaskRepository(ABC):
    """Abstract interface for async task persistence operations."""
    
    @abstractmethod
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create a new task asynchronously.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            The ID of the created task
        """
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a task by ID asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            Task data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_tasks(self, 
                        session_id: Optional[str] = None,
                        parent_task_id: Optional[str] = None,
                        status: Optional[str] = None,
                        limit: Optional[int] = None,
                        offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering asynchronously.
        
        Args:
            session_id: Filter by session ID
            parent_task_id: Filter by parent task ID
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of task dictionaries
        """
        pass
    
    @abstractmethod
    async def query_tasks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query tasks with advanced filtering and pagination asynchronously.
        
        Args:
            filters: Dictionary containing query filters such as:
                - status: Task status filter
                - task_type: Task type filter
                - complexity: Complexity level filter
                - specialist_type: Specialist type filter
                - created_after: Created after date filter
                - created_before: Created before date filter
                - updated_after: Updated after date filter
                - updated_before: Updated before date filter
                - parent_task_id: Parent task ID filter
                - tags: Tags filter (list)
                - search_query: Text search in title/description
                - page: Page number for pagination (default: 1)
                - page_size: Page size for pagination (default: 20, max: 100)
                - sort_by: Sort field (default: 'created_at')
                - sort_order: Sort order 'asc' or 'desc' (default: 'desc')
                - include_archived: Include archived tasks (default: False)
                - include_subtasks: Include subtasks (default: True)
                - dependency_ids: Filter by dependency IDs
            
        Returns:
            Dictionary containing:
                - tasks: List of matching task objects
                - pagination: Pagination information (total_count, page, page_size, page_count)
                - filters_applied: Filters that were applied
        """
        pass
    
    @abstractmethod
    async def get_subtasks(self, parent_task_id: str) -> List[Dict[str, Any]]:
        """
        Get all subtasks of a parent task asynchronously.
        
        Args:
            parent_task_id: The ID of the parent task
            
        Returns:
            List of subtask dictionaries
        """
        pass
    
    @abstractmethod
    async def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            status: The new status
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def add_task_artifact(self, task_id: str, artifact: Dict[str, Any]) -> bool:
        """
        Add an artifact to a task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            artifact: Artifact data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all artifacts for a task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            List of artifact dictionaries
        """
        pass
    
    @abstractmethod
    async def search_tasks(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search tasks by text query asynchronously.
        
        Args:
            query: Search query string
            fields: List of fields to search in (default: all text fields)
            
        Returns:
            List of matching task dictionaries
        """
        pass
    
    @abstractmethod
    async def get_task_dependencies(self, task_id: str) -> List[str]:
        """
        Get task IDs that this task depends on asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            List of dependency task IDs
        """
        pass
    
    @abstractmethod
    async def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """
        Add a dependency between tasks asynchronously.
        
        Args:
            task_id: The task that depends on another
            dependency_id: The task being depended on
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup_old_tasks(self, older_than: datetime, 
                              exclude_sessions: Optional[List[str]] = None) -> int:
        """
        Clean up tasks older than a specified date asynchronously.
        
        Args:
            older_than: Delete tasks created before this date
            exclude_sessions: Session IDs to exclude from cleanup
            
        Returns:
            Number of tasks deleted
        """
        pass
    
    @abstractmethod
    async def get_task_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics about tasks asynchronously.
        
        Args:
            session_id: Optional session ID to filter metrics
            
        Returns:
            Dictionary containing metrics like counts by status, avg duration, etc.
        """
        pass

    @abstractmethod
    async def get_task_hierarchy(self, root_task_id: str) -> List[Dict[str, Any]]:
        """
        Get task hierarchy starting from a root task asynchronously.
        
        Args:
            root_task_id: The ID of the root task
            
        Returns:
            List of task dictionaries in hierarchical order
        """
        pass

    @abstractmethod
    async def add_artifact(self, task_id: str, artifact_data: Dict[str, Any]) -> str:
        """
        Add an artifact to a task asynchronously.
        
        Args:
            task_id: The unique identifier of the task
            artifact_data: Artifact data dictionary
            
        Returns:
            The ID of the created artifact
        """
        pass

    @abstractmethod
    async def add_dependency(self, task_id: str, dependency_id: str) -> bool:
        """
        Add a dependency between tasks asynchronously.
        
        Args:
            task_id: The task that depends on another
            dependency_id: The task being depended on
            
        Returns:
            True if successful, False otherwise
        """
        pass