"""
Orchestration Coordinator - Composes domain services for task orchestration.

This coordinator provides the main interface for task orchestration by
composing the individual domain services into cohesive workflows.
"""

from typing import Dict, List, Optional, Any
import json
import logging

from .task_breakdown_service import TaskBreakdownService
from .specialist_assignment_service import SpecialistAssignmentService
from .progress_tracking_service import ProgressTrackingService
from .result_synthesis_service import ResultSynthesisService
from ..repositories import TaskRepository, StateRepository, SpecialistRepository
from ...orchestrator.models import TaskBreakdown, TaskStatus

logger = logging.getLogger(__name__)


class OrchestrationCoordinator:
    """
    Coordinator that composes domain services for task orchestration.
    
    This class provides a unified interface for orchestration operations
    while maintaining separation of concerns through service composition.
    """
    
    def __init__(self,
                 task_repository: TaskRepository,
                 state_repository: StateRepository,
                 specialist_repository: SpecialistRepository,
                 project_dir: Optional[str] = None):
        """
        Initialize the orchestration coordinator.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
            specialist_repository: Repository for specialist management
            project_dir: Optional project directory for configuration
        """
        # Initialize repositories
        self.task_repo = task_repository
        self.state_repo = state_repository
        self.specialist_repo = specialist_repository
        
        # Initialize services
        self.breakdown_service = TaskBreakdownService(
            task_repository,
            state_repository,
            specialist_repository
        )
        
        self.assignment_service = SpecialistAssignmentService(
            task_repository,
            state_repository,
            specialist_repository,
            project_dir
        )
        
        self.tracking_service = ProgressTrackingService(
            task_repository,
            state_repository
        )
        
        self.synthesis_service = ResultSynthesisService(
            task_repository,
            state_repository
        )
        
        self.project_dir = project_dir
    
    async def initialize_session(self) -> Dict[str, Any]:
        """
        Initialize a new orchestration session.
        
        Returns:
            Session initialization information
        """
        # This is similar to the original but delegates to services
        return {
            "role": "Task Orchestrator",
            "capabilities": [
                "Breaking down complex tasks into manageable subtasks",
                "Assigning appropriate specialist roles to each subtask",
                "Managing dependencies between subtasks",
                "Tracking progress and coordinating work"
            ],
            "instructions": (
                "As the Task Orchestrator, your role is to analyze complex tasks and break them down "
                "into a structured set of subtasks. For each task you receive:\n\n"
                "1. Carefully analyze the requirements and context\n"
                "2. Identify logical components that can be worked on independently\n"
                "3. Create a clear dependency structure between subtasks\n"
                "4. Assign appropriate specialist roles to each subtask\n"
                "5. Estimate effort required for each component\n\n"
                "When creating subtasks, ensure each has:\n"
                "- A clear, specific objective\n"
                "- Appropriate specialist assignment (architect, implementer, debugger, etc.)\n"
                "- Realistic effort estimation\n"
                "- Proper dependency relationships\n\n"
                "This structured approach ensures complex work is broken down methodically."
            ),
            "specialist_roles": {
                "architect": "System design and architecture planning",
                "implementer": "Writing code and implementing features",
                "debugger": "Fixing issues and optimizing performance",
                "documenter": "Creating documentation and guides",
                "reviewer": "Code review and quality assurance",
                "tester": "Testing and validation",
                "researcher": "Research and information gathering"
            }
        }
    
    async def plan_task(self,
                       description: str,
                       complexity: str,
                       subtasks_json: str,
                       context: str = "",
                       session_id: Optional[str] = None) -> TaskBreakdown:
        """
        Plan a complex task by breaking it down into subtasks.
        
        Args:
            description: Main task description
            complexity: Complexity level (low, medium, high)
            subtasks_json: JSON string with subtask definitions
            context: Additional context
            session_id: Optional session ID
            
        Returns:
            TaskBreakdown with planned subtasks
        """
        try:
            # Delegate to breakdown service
            breakdown = await self.breakdown_service.plan_task(
                description,
                complexity,
                subtasks_json,
                context,
                session_id
            )
            
            # Validate the breakdown
            errors = await self.breakdown_service.validate_breakdown(breakdown)
            if errors:
                logger.warning(f"Task breakdown validation errors: {errors}")
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error planning task: {e}")
            raise
    
    async def get_specialist_context(self, task_id: str) -> str:
        """
        Get context for a specialist to work on a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Context string for the specialist
        """
        try:
            # Ensure specialist is assigned
            task = self.task_repo.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            # Assign specialist if not already assigned
            if not task.get('metadata', {}).get('assigned_specialist_id'):
                await self.assignment_service.assign_specialist(task_id)
            
            # Get specialist context
            return await self.assignment_service.get_specialist_context(task_id)
            
        except Exception as e:
            logger.error(f"Error getting specialist context: {e}")
            raise
    
    async def complete_subtask(self,
                             task_id: str,
                             results: str,
                             artifacts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Complete a subtask with results.
        
        Args:
            task_id: Task to complete
            results: Task results
            artifacts: Optional artifacts
            
        Returns:
            Completion details
        """
        try:
            # Complete the task
            completion = await self.tracking_service.complete_task(
                task_id,
                results,
                artifacts
            )
            
            # Check if parent needs synthesis
            parent_progress = completion.get('parent_progress', {})
            if parent_progress.get('parent_ready_for_completion'):
                # Trigger synthesis for parent
                parent_id = parent_progress['parent_id']
                logger.info(f"Parent task {parent_id} ready for synthesis")
                
                # Add synthesis recommendation
                completion['synthesis_needed'] = {
                    'task_id': parent_id,
                    'reason': 'All subtasks completed'
                }
            
            return completion
            
        except Exception as e:
            logger.error(f"Error completing subtask: {e}")
            raise
    
    async def synthesize_results(self, parent_task_id: str) -> str:
        """
        Synthesize results from completed subtasks.
        
        Args:
            parent_task_id: Parent task ID
            
        Returns:
            Synthesized results
        """
        try:
            return await self.synthesis_service.synthesize_task_results(parent_task_id)
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            raise
    
    async def get_status(self,
                        session_id: Optional[str] = None,
                        include_completed: bool = False) -> Dict[str, Any]:
        """
        Get current orchestration status.
        
        Args:
            session_id: Optional session filter
            include_completed: Include completed tasks
            
        Returns:
            Status information
        """
        try:
            return await self.tracking_service.get_status(
                session_id,
                include_completed
            )
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            raise
    
    async def update_task_progress(self,
                                 task_id: str,
                                 progress_percentage: int,
                                 notes: Optional[str] = None) -> bool:
        """
        Update progress for a task.
        
        Args:
            task_id: Task to update
            progress_percentage: Progress percentage (0-100)
            notes: Optional progress notes
            
        Returns:
            True if successful
        """
        try:
            progress_data = {
                'percentage': max(0, min(100, progress_percentage))
            }
            
            if notes:
                progress_data['notes'] = notes
            
            return await self.tracking_service.update_task_progress(
                task_id,
                progress_data
            )
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            raise
    
    async def get_next_recommended_task(self, 
                                      session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get recommendation for next task to work on.
        
        Args:
            session_id: Session ID
            
        Returns:
            Task recommendation or None
        """
        try:
            # Get all tasks
            status = await self.tracking_service.get_status(
                session_id,
                include_completed=False
            )
            
            # Find actionable tasks
            for task_group in status.get('tasks', []):
                recommendation = self._find_actionable_task(task_group)
                if recommendation:
                    return recommendation
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting task recommendation: {e}")
            return None
    
    def _find_actionable_task(self, task_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Recursively find an actionable task.
        
        Args:
            task_info: Task information with subtasks
            
        Returns:
            Actionable task or None
        """
        # Check if this task is actionable
        if (task_info['status'] in ('pending', 'in_progress') and 
            not task_info.get('is_blocked', False)):
            
            # For in_progress tasks, check if they have incomplete subtasks
            if task_info['status'] == 'in_progress':
                if task_info.get('subtasks'):
                    # Look for actionable subtasks first
                    for subtask in task_info['subtasks']:
                        sub_recommendation = self._find_actionable_task(subtask)
                        if sub_recommendation:
                            return sub_recommendation
                else:
                    # No subtasks, this task is actionable
                    return {
                        'task_id': task_info['id'],
                        'title': task_info['title'],
                        'status': task_info['status'],
                        'reason': 'In progress task without subtasks'
                    }
            else:
                # Pending task without blockers
                return {
                    'task_id': task_info['id'],
                    'title': task_info['title'],
                    'status': task_info['status'],
                    'reason': 'Pending task ready to start'
                }
        
        # Check subtasks
        for subtask in task_info.get('subtasks', []):
            recommendation = self._find_actionable_task(subtask)
            if recommendation:
                return recommendation
        
        return None