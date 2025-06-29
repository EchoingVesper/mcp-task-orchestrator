"""
Progress Tracking Service - Handles task progress monitoring and status updates.

This service is responsible for tracking task completion, managing task states,
and providing progress insights for orchestration decisions.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json

from ..repositories import TaskRepository, StateRepository
from ...orchestrator.models import TaskStatus


class ProgressTrackingService:
    """
    Service for tracking task progress and managing status updates.
    
    This service encapsulates the logic for progress monitoring,
    status transitions, and completion tracking.
    """
    
    def __init__(self,
                 task_repository: TaskRepository,
                 state_repository: StateRepository):
        """
        Initialize the progress tracking service.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
        """
        self.task_repo = task_repository
        self.state_repo = state_repository
    
    async def get_status(self, 
                        session_id: Optional[str] = None,
                        include_completed: bool = False) -> Dict[str, Any]:
        """
        Get current status of tasks.
        
        Args:
            session_id: Optional session to filter by
            include_completed: Whether to include completed tasks
            
        Returns:
            Status dictionary with task breakdowns and progress
        """
        # Get all tasks for session
        all_tasks = self.task_repo.list_tasks(session_id=session_id)
        
        # Filter out completed if requested
        if not include_completed:
            all_tasks = [
                t for t in all_tasks 
                if t['status'] not in ('completed', 'failed', 'cancelled')
            ]
        
        # Group by parent
        tasks_by_parent = {}
        root_tasks = []
        
        for task in all_tasks:
            parent_id = task.get('parent_task_id')
            if parent_id:
                if parent_id not in tasks_by_parent:
                    tasks_by_parent[parent_id] = []
                tasks_by_parent[parent_id].append(task)
            else:
                root_tasks.append(task)
        
        # Build status for each root task
        status = {
            'session_id': session_id,
            'tasks': [],
            'summary': {
                'total': len(all_tasks),
                'pending': sum(1 for t in all_tasks if t['status'] == 'pending'),
                'in_progress': sum(1 for t in all_tasks if t['status'] == 'in_progress'),
                'completed': sum(1 for t in all_tasks if t['status'] == 'completed'),
                'failed': sum(1 for t in all_tasks if t['status'] == 'failed'),
                'blocked': 0  # Will calculate below
            }
        }
        
        # Process each root task
        for root_task in root_tasks:
            task_status = await self._build_task_status(
                root_task, 
                tasks_by_parent,
                include_completed
            )
            status['tasks'].append(task_status)
        
        # Calculate blocked tasks
        blocked_count = await self._count_blocked_tasks(all_tasks)
        status['summary']['blocked'] = blocked_count
        
        # Add progress percentage
        if status['summary']['total'] > 0:
            completed_count = status['summary']['completed'] + status['summary']['failed']
            status['summary']['progress_percentage'] = round(
                (completed_count / status['summary']['total']) * 100, 1
            )
        else:
            status['summary']['progress_percentage'] = 0
        
        return status
    
    async def complete_task(self,
                          task_id: str,
                          results: str,
                          artifacts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Mark a task as completed with results.
        
        Args:
            task_id: Task to complete
            results: Task results/output
            artifacts: Optional artifacts to attach
            
        Returns:
            Completion details including next recommendations
        """
        # Get task
        task = self.task_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Check if already completed
        if task['status'] in ('completed', 'failed', 'cancelled'):
            raise ValueError(f"Task already in terminal state: {task['status']}")
        
        # Check if subtasks are completed
        subtasks = self.task_repo.get_subtasks(task_id)
        incomplete_subtasks = [
            st for st in subtasks
            if st['status'] not in ('completed', 'failed', 'cancelled')
        ]
        
        if incomplete_subtasks:
            raise ValueError(
                f"Cannot complete task with {len(incomplete_subtasks)} incomplete subtasks"
            )
        
        # Update task status
        self.task_repo.update_task_status(task_id, 'completed')
        
        # Add result artifact
        self.task_repo.add_task_artifact(task_id, {
            'type': 'result',
            'name': 'completion_result',
            'content': results
        })
        
        # Add any additional artifacts
        if artifacts:
            for artifact in artifacts:
                self.task_repo.add_task_artifact(task_id, artifact)
        
        # Record completion event
        self.state_repo.record_event(
            task.get('session_id'),
            'task_completed',
            {
                'task_id': task_id,
                'title': task.get('title'),
                'duration': self._calculate_duration(task)
            }
        )
        
        # Check parent task progress
        parent_progress = await self._check_parent_task_progress(task_id)
        
        # Get next recommended task
        next_task = await self._get_next_recommended_task(task_id)
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'parent_progress': parent_progress,
            'next_recommendation': next_task
        }
    
    async def update_task_progress(self,
                                 task_id: str,
                                 progress_data: Dict[str, Any]) -> bool:
        """
        Update progress information for a task.
        
        Args:
            task_id: Task to update
            progress_data: Progress information (percentage, notes, etc.)
            
        Returns:
            True if successful
        """
        task = self.task_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update metadata with progress
        metadata = task.get('metadata', {})
        metadata['progress'] = progress_data
        metadata['last_progress_update'] = datetime.utcnow().isoformat()
        
        # Update status to in_progress if still pending
        if task['status'] == 'pending' and progress_data.get('percentage', 0) > 0:
            self.task_repo.update_task_status(task_id, 'in_progress')
        
        # Update task metadata
        return self.task_repo.update_task(task_id, {'metadata': metadata})
    
    async def _build_task_status(self,
                               task: Dict[str, Any],
                               tasks_by_parent: Dict[str, List[Dict]],
                               include_completed: bool) -> Dict[str, Any]:
        """Build status information for a task and its subtasks."""
        subtasks = tasks_by_parent.get(task['id'], [])
        
        # Filter completed subtasks if needed
        if not include_completed:
            subtasks = [
                st for st in subtasks
                if st['status'] not in ('completed', 'failed', 'cancelled')
            ]
        
        # Build subtask statuses recursively
        subtask_statuses = []
        for subtask in subtasks:
            subtask_status = await self._build_task_status(
                subtask,
                tasks_by_parent,
                include_completed
            )
            subtask_statuses.append(subtask_status)
        
        # Check if blocked
        is_blocked = await self._is_task_blocked(task)
        
        return {
            'id': task['id'],
            'title': task.get('title', 'Untitled'),
            'status': task['status'],
            'is_blocked': is_blocked,
            'metadata': task.get('metadata', {}),
            'subtasks': subtask_statuses,
            'progress': self._calculate_task_progress(task, subtasks)
        }
    
    async def _check_parent_task_progress(self, completed_task_id: str) -> Dict[str, Any]:
        """Check if parent task can be progressed after subtask completion."""
        task = self.task_repo.get_task(completed_task_id)
        if not task or not task.get('parent_task_id'):
            return {'has_parent': False}
        
        parent_id = task['parent_task_id']
        parent_task = self.task_repo.get_task(parent_id)
        if not parent_task:
            return {'has_parent': False}
        
        # Get all sibling tasks
        siblings = self.task_repo.get_subtasks(parent_id)
        
        # Check completion status
        completed_count = sum(
            1 for s in siblings 
            if s['status'] in ('completed', 'failed', 'cancelled')
        )
        
        all_completed = all(
            s['status'] in ('completed', 'failed', 'cancelled')
            for s in siblings
        )
        
        # Check if parent can be marked ready
        parent_ready = (
            all_completed and 
            parent_task['status'] not in ('completed', 'failed', 'cancelled')
        )
        
        return {
            'has_parent': True,
            'parent_id': parent_id,
            'parent_title': parent_task.get('title', 'Untitled'),
            'parent_status': parent_task['status'],
            'siblings_total': len(siblings),
            'siblings_completed': completed_count,
            'all_subtasks_complete': all_completed,
            'parent_ready_for_completion': parent_ready
        }
    
    async def _get_next_recommended_task(self, completed_task_id: str) -> Optional[Dict[str, Any]]:
        """Get recommendation for next task to work on."""
        task = self.task_repo.get_task(completed_task_id)
        if not task:
            return None
        
        session_id = task.get('session_id')
        if not session_id:
            return None
        
        # Get all pending/in_progress tasks
        all_tasks = self.task_repo.list_tasks(session_id=session_id)
        
        actionable_tasks = []
        for t in all_tasks:
            if t['status'] in ('pending', 'in_progress'):
                # Check if blocked
                if not await self._is_task_blocked(t):
                    # For in_progress tasks, check if they have incomplete subtasks
                    if t['status'] == 'in_progress':
                        subtasks = self.task_repo.get_subtasks(t['id'])
                        has_incomplete = any(
                            st['status'] not in ('completed', 'failed', 'cancelled')
                            for st in subtasks
                        )
                        if has_incomplete:
                            continue
                    
                    actionable_tasks.append(t)
        
        if not actionable_tasks:
            return None
        
        # Prioritize tasks
        # 1. Tasks with same parent (siblings)
        # 2. Tasks at same level
        # 3. Any other tasks
        
        parent_id = task.get('parent_task_id')
        
        # Find siblings
        if parent_id:
            siblings = [
                t for t in actionable_tasks 
                if t.get('parent_task_id') == parent_id
            ]
            if siblings:
                return self._format_task_recommendation(siblings[0])
        
        # Find tasks at same level
        same_level = [
            t for t in actionable_tasks
            if bool(t.get('parent_task_id')) == bool(parent_id)
        ]
        if same_level:
            return self._format_task_recommendation(same_level[0])
        
        # Return any actionable task
        return self._format_task_recommendation(actionable_tasks[0])
    
    async def _is_task_blocked(self, task: Dict[str, Any]) -> bool:
        """Check if a task is blocked by dependencies."""
        dependencies = self.task_repo.get_task_dependencies(task['id'])
        
        for dep_id in dependencies:
            dep_task = self.task_repo.get_task(dep_id)
            if dep_task and dep_task['status'] not in ('completed', 'failed', 'cancelled'):
                return True
        
        return False
    
    async def _count_blocked_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        """Count how many tasks are blocked."""
        blocked_count = 0
        
        for task in tasks:
            if task['status'] in ('pending', 'in_progress'):
                if await self._is_task_blocked(task):
                    blocked_count += 1
        
        return blocked_count
    
    def _calculate_task_progress(self, 
                               task: Dict[str, Any], 
                               subtasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate progress percentage for a task."""
        # If no subtasks, use status-based progress
        if not subtasks:
            status_progress = {
                'pending': 0,
                'in_progress': 50,
                'completed': 100,
                'failed': 100,
                'cancelled': 100
            }
            percentage = status_progress.get(task['status'], 0)
            
            # Check for custom progress in metadata
            custom_progress = task.get('metadata', {}).get('progress', {})
            if 'percentage' in custom_progress:
                percentage = custom_progress['percentage']
        else:
            # Calculate based on subtask completion
            total = len(subtasks)
            completed = sum(
                1 for st in subtasks
                if st['status'] in ('completed', 'failed', 'cancelled')
            )
            percentage = round((completed / total) * 100, 1) if total > 0 else 0
        
        return {
            'percentage': percentage,
            'subtasks_total': len(subtasks),
            'subtasks_completed': sum(
                1 for st in subtasks
                if st['status'] in ('completed', 'failed', 'cancelled')
            )
        }
    
    def _calculate_duration(self, task: Dict[str, Any]) -> Optional[float]:
        """Calculate task duration in seconds."""
        created_at = task.get('created_at')
        completed_at = task.get('completed_at')
        
        if created_at and completed_at:
            try:
                start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                return (end - start).total_seconds()
            except:
                return None
        
        return None
    
    def _format_task_recommendation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Format task for recommendation."""
        return {
            'task_id': task['id'],
            'title': task.get('title', 'Untitled'),
            'status': task['status'],
            'specialist': task.get('metadata', {}).get('specialist', 'unknown'),
            'parent_id': task.get('parent_task_id'),
            'reason': 'Next actionable task in workflow'
        }