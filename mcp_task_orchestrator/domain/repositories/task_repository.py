"""
Abstract Task Repository interface.

This module defines the contract for task persistence operations that 
infrastructure implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class TaskRepository(ABC):
    """Abstract interface for task persistence operations."""
    
    @abstractmethod
    def create_task(self, task_data: Dict[str, Any]) -> str:
        """
        Create a new task.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            The ID of the created task
        """
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a task by ID.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            Task data as a dictionary, or None if not found
        """
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: The unique identifier of the task
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_tasks(self, 
                   session_id: Optional[str] = None,
                   parent_task_id: Optional[str] = None,
                   status: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List tasks with optional filtering.
        
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
    def get_subtasks(self, parent_task_id: str) -> List[Dict[str, Any]]:
        """
        Get all subtasks of a parent task.
        
        Args:
            parent_task_id: The ID of the parent task
            
        Returns:
            List of subtask dictionaries
        """
        pass
    
    @abstractmethod
    def update_task_status(self, task_id: str, status: str) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_id: The unique identifier of the task
            status: The new status
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def add_task_artifact(self, task_id: str, artifact: Dict[str, Any]) -> bool:
        """
        Add an artifact to a task.
        
        Args:
            task_id: The unique identifier of the task
            artifact: Artifact data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all artifacts for a task.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            List of artifact dictionaries
        """
        pass
    
    @abstractmethod
    def search_tasks(self, query: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search tasks by text query.
        
        Args:
            query: Search query string
            fields: List of fields to search in (default: all text fields)
            
        Returns:
            List of matching task dictionaries
        """
        pass
    
    @abstractmethod
    def get_task_dependencies(self, task_id: str) -> List[str]:
        """
        Get task IDs that this task depends on.
        
        Args:
            task_id: The unique identifier of the task
            
        Returns:
            List of dependency task IDs
        """
        pass
    
    @abstractmethod
    def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """
        Add a dependency between tasks.
        
        Args:
            task_id: The task that depends on another
            dependency_id: The task being depended on
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup_old_tasks(self, older_than: datetime, 
                         exclude_sessions: Optional[List[str]] = None) -> int:
        """
        Clean up tasks older than a specified date.
        
        Args:
            older_than: Delete tasks created before this date
            exclude_sessions: Session IDs to exclude from cleanup
            
        Returns:
            Number of tasks deleted
        """
        pass
    
    @abstractmethod
    def get_task_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics about tasks.
        
        Args:
            session_id: Optional session ID to filter metrics
            
        Returns:
            Dictionary containing metrics like counts by status, avg duration, etc.
        """
        pass