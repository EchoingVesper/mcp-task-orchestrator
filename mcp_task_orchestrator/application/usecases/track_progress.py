"""
Use case for tracking task progress.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ...domain import (
    TaskRepository,
    StateRepository,
    OrchestrationSession,
    Task,
    TaskStatus,
    TaskNotFoundError,
    SessionNotFoundError,
    OrchestrationError
)
from ..dto import ProgressStatusRequest, ProgressStatusResponse


@dataclass
class TrackProgressUseCase:
    """
    Application use case for tracking task and session progress.
    
    This use case provides progress monitoring and status updates.
    """
    task_repository: TaskRepository
    state_repository: StateRepository
    
    async def get_session_progress(self, request: ProgressStatusRequest) -> ProgressStatusResponse:
        """
        Get progress status for a session or specific tasks.
        
        Args:
            request: Progress status request
            
        Returns:
            ProgressStatusResponse with current status
            
        Raises:
            SessionNotFoundError: If session not found
            TaskNotFoundError: If specific task not found
        """
        try:
            if request.session_id:
                return await self._get_session_status(request.session_id, request.include_completed)
            elif request.task_id:
                return await self._get_task_status(request.task_id, request.include_subtasks)
            else:
                return await self._get_overall_status(request.include_completed)
                
        except (SessionNotFoundError, TaskNotFoundError):
            raise
        except Exception as e:
            raise OrchestrationError(
                f"Failed to get progress status: {str(e)}",
                {"request": request.__dict__}
            )
    
    async def _get_session_status(
        self, 
        session_id: str, 
        include_completed: bool
    ) -> ProgressStatusResponse:
        """Get status for a specific session."""
        session = await self.state_repository.get_session(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        
        # Get all tasks in session
        tasks = []
        for task_id in session.active_tasks + (session.completed_tasks if include_completed else []):
            task = await self.task_repository.get_task(task_id)
            if task:
                tasks.append(task)
        
        # Calculate metrics
        metrics = session.get_progress()
        
        return ProgressStatusResponse(
            session_info={
                'session_id': session.session_id,
                'name': session.name,
                'status': session.status.value,
                'created_at': session.created_at.isoformat(),
                'progress': metrics
            },
            active_tasks=self._format_tasks(
                [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
            ),
            pending_tasks=self._format_tasks(
                [t for t in tasks if t.status == TaskStatus.PENDING]
            ),
            completed_tasks=self._format_tasks(
                [t for t in tasks if t.status == TaskStatus.COMPLETED]
            ) if include_completed else [],
            failed_tasks=self._format_tasks(
                [t for t in tasks if t.status == TaskStatus.FAILED]
            ),
            metrics=metrics,
            overall_status=self._determine_overall_status(session, tasks)
        )
    
    async def _get_task_status(
        self,
        task_id: str,
        include_subtasks: bool
    ) -> ProgressStatusResponse:
        """Get status for a specific task."""
        task = await self.task_repository.get_task(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        subtasks = []
        if include_subtasks:
            subtasks = await self.task_repository.get_subtasks(task_id)
        
        # Format task info
        task_info = self._format_task(task)
        subtask_info = self._format_tasks(subtasks)
        
        # Calculate task-specific metrics
        metrics = {
            'subtask_count': len(subtasks),
            'completed_subtasks': len([t for t in subtasks if t.status == TaskStatus.COMPLETED]),
            'duration_seconds': (
                (task.updated_at - task.created_at).total_seconds()
                if task.status.is_terminal() else None
            )
        }
        
        return ProgressStatusResponse(
            task_info=task_info,
            subtasks=subtask_info,
            metrics=metrics,
            overall_status=task.status.value
        )
    
    async def _get_overall_status(self, include_completed: bool) -> ProgressStatusResponse:
        """Get overall system status."""
        # Get all active sessions
        sessions = await self.state_repository.list_active_sessions()
        
        # Aggregate metrics
        total_tasks = 0
        active_tasks = 0
        completed_tasks = 0
        failed_tasks = 0
        
        session_summaries = []
        for session in sessions:
            progress = session.get_progress()
            total_tasks += progress['total_tasks']
            active_tasks += progress['active_tasks']
            completed_tasks += progress['completed_tasks']
            failed_tasks += progress['failed_tasks']
            
            session_summaries.append({
                'session_id': session.session_id,
                'name': session.name,
                'status': session.status.value,
                'progress': progress
            })
        
        metrics = {
            'total_sessions': len(sessions),
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'overall_completion': (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )
        }
        
        return ProgressStatusResponse(
            sessions=session_summaries,
            metrics=metrics,
            overall_status="active" if active_tasks > 0 else "idle"
        )
    
    def _format_task(self, task: Task) -> Dict[str, Any]:
        """Format a task for response."""
        return {
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'status': task.status.value,
            'specialist_type': task.specialist_type,
            'created_at': task.created_at.isoformat(),
            'updated_at': task.updated_at.isoformat(),
            'parent_task_id': task.parent_task_id,
            'dependencies': task.dependencies,
            'result': task.result,
            'error': task.error
        }
    
    def _format_tasks(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Format multiple tasks for response."""
        return [self._format_task(task) for task in tasks]
    
    def _determine_overall_status(
        self,
        session: OrchestrationSession,
        tasks: List[Task]
    ) -> str:
        """Determine overall status based on session and tasks."""
        if session.status == SessionStatus.FAILED:
            return "failed"
        elif session.status == SessionStatus.COMPLETED:
            return "completed"
        elif any(t.status == TaskStatus.IN_PROGRESS for t in tasks):
            return "in_progress"
        elif all(t.status == TaskStatus.COMPLETED for t in tasks):
            return "ready_to_complete"
        elif any(t.status == TaskStatus.FAILED for t in tasks):
            return "has_failures"
        else:
            return "pending"