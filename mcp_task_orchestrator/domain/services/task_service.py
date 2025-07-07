"""
Task Service - Domain service for task operations.

This service implements business logic for task management using
repository interfaces, demonstrating clean architecture principles.
"""

from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ..repositories import TaskRepository, StateRepository


class TaskService:
    """
    Domain service for task operations.
    
    This service encapsulates business logic for task management,
    using repository interfaces for persistence.
    """
    
    def __init__(self, task_repository: TaskRepository, state_repository: StateRepository):
        """
        Initialize the task service.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
        """
        self.task_repository = task_repository
        self.state_repository = state_repository
    
    def create_task(self, 
                   session_id: str,
                   title: str,
                   description: Optional[str] = None,
                   parent_task_id: Optional[str] = None,
                   task_type: str = 'generic',
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new task with business logic validation.
        
        Args:
            session_id: Session this task belongs to
            title: Task title
            description: Task description
            parent_task_id: Parent task ID if this is a subtask
            task_type: Type of task
            metadata: Additional task metadata
            
        Returns:
            Created task ID
            
        Raises:
            ValueError: If validation fails
        """
        # Validate session exists
        session = self.state_repository.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Validate parent task if specified
        if parent_task_id:
            parent_task = self.task_repository.get_task(parent_task_id)
            if not parent_task:
                raise ValueError(f"Parent task {parent_task_id} not found")
            
            # Ensure parent task is from same session
            if parent_task.get('session_id') != session_id:
                raise ValueError("Parent task must be from same session")
        
        # Create task data
        task_data = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'parent_task_id': parent_task_id,
            'type': task_type,
            'status': 'pending',
            'title': title,
            'description': description,
            'metadata': metadata or {}
        }
        
        # Create task
        task_id = self.task_repository.create_task(task_data)
        
        # Record event
        self.state_repository.record_event(
            session_id,
            'task_created',
            {
                'task_id': task_id,
                'title': title,
                'parent_task_id': parent_task_id
            }
        )
        
        return task_id
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Complete a task with business logic.
        
        Args:
            task_id: Task to complete
            result: Task result/output
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If task cannot be completed
        """
        # Get task
        task = self.task_repository.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Check if already completed
        if task['status'] in ('completed', 'failed', 'cancelled'):
            raise ValueError(f"Task {task_id} already completed with status: {task['status']}")
        
        # Check if all subtasks are completed
        subtasks = self.task_repository.get_subtasks(task_id)
        incomplete_subtasks = [
            st for st in subtasks 
            if st['status'] not in ('completed', 'failed', 'cancelled')
        ]
        
        if incomplete_subtasks:
            raise ValueError(f"Cannot complete task with {len(incomplete_subtasks)} incomplete subtasks")
        
        # Update task status
        success = self.task_repository.update_task_status(task_id, 'completed')
        
        if success and result:
            # Add result as artifact
            self.task_repository.add_task_artifact(task_id, {
                'type': 'result',
                'name': 'task_result',
                'content': result
            })
        
        # Record event
        if success:
            self.state_repository.record_event(
                task['session_id'],
                'task_completed',
                {
                    'task_id': task_id,
                    'title': task.get('title')
                }
            )
        
        return success
    
    def get_task_hierarchy(self, task_id: str, include_completed: bool = True) -> Dict[str, Any]:
        """
        Get task with its full hierarchy.
        
        Args:
            task_id: Root task ID
            include_completed: Whether to include completed tasks
            
        Returns:
            Task hierarchy as nested dictionary
        """
        task = self.task_repository.get_task(task_id)
        if not task:
            return None
        
        # Get subtasks
        subtasks = self.task_repository.get_subtasks(task_id)
        
        # Filter if needed
        if not include_completed:
            subtasks = [
                st for st in subtasks 
                if st['status'] not in ('completed', 'failed', 'cancelled')
            ]
        
        # Recursively build hierarchy
        task['subtasks'] = []
        for subtask in subtasks:
            subtask_hierarchy = self.get_task_hierarchy(
                subtask['id'], 
                include_completed
            )
            if subtask_hierarchy:
                task['subtasks'].append(subtask_hierarchy)
        
        return task
    
    def get_next_actionable_task(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next task that can be worked on.
        
        This implements business logic to find tasks that:
        - Are pending or in_progress
        - Have no incomplete dependencies
        - Have no incomplete subtasks (for in_progress tasks)
        
        Args:
            session_id: Session ID
            
        Returns:
            Next actionable task or None
        """
        # Get all pending/in_progress tasks for session
        pending_tasks = self.task_repository.list_tasks(
            session_id=session_id,
            status='pending'
        )
        in_progress_tasks = self.task_repository.list_tasks(
            session_id=session_id,
            status='in_progress'
        )
        
        all_tasks = pending_tasks + in_progress_tasks
        
        for task in all_tasks:
            # Check dependencies
            dependencies = self.task_repository.get_task_dependencies(task['id'])
            has_incomplete_deps = False
            
            for dep_id in dependencies:
                dep_task = self.task_repository.get_task(dep_id)
                if dep_task and dep_task['status'] not in ('completed', 'failed', 'cancelled'):
                    has_incomplete_deps = True
                    break
            
            if has_incomplete_deps:
                continue
            
            # For in_progress tasks, check if they have incomplete subtasks
            if task['status'] == 'in_progress':
                subtasks = self.task_repository.get_subtasks(task['id'])
                has_incomplete_subtasks = any(
                    st['status'] not in ('completed', 'failed', 'cancelled')
                    for st in subtasks
                )
                
                if has_incomplete_subtasks:
                    continue
            
            # This task is actionable
            return task
        
        return None