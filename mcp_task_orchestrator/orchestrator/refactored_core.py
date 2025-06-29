"""
Refactored TaskOrchestrator using domain services.

This module shows how the monolithic TaskOrchestrator can be refactored
to use the new domain services, maintaining the same interface while
achieving better separation of concerns.
"""

import os
import logging
from typing import Dict, List, Optional, Any

from ..domain.services import OrchestrationCoordinator
from ..infrastructure.database.repository_factory import create_repository_factory
from .models import TaskBreakdown
from .state import StateManager
from .specialists import SpecialistManager

logger = logging.getLogger("mcp_task_orchestrator.refactored_core")


class RefactoredTaskOrchestrator:
    """
    Refactored TaskOrchestrator that uses domain services.
    
    This class maintains the same public interface as the original
    TaskOrchestrator but delegates to domain services for better
    separation of concerns and testability.
    """
    
    def __init__(self, 
                 state_manager: StateManager, 
                 specialist_manager: SpecialistManager, 
                 project_dir: str = None):
        """
        Initialize the refactored orchestrator.
        
        Args:
            state_manager: State manager (for compatibility)
            specialist_manager: Specialist manager (for compatibility)
            project_dir: Project directory
        """
        self.project_dir = project_dir or os.getcwd()
        
        # For backward compatibility
        self.state = state_manager
        self.specialists = specialist_manager
        
        # Create repository factory from configuration
        # In a real implementation, this would come from dependency injection
        config = {
            'database': {
                'url': 'sqlite:///.task_orchestrator/orchestrator.db',
                'timeout': 30.0
            }
        }
        
        self.repository_factory = create_repository_factory(config)
        
        # Create the orchestration coordinator with all services
        self.coordinator = OrchestrationCoordinator(
            self.repository_factory.create_task_repository(),
            self.repository_factory.create_state_repository(),
            self.repository_factory.create_specialist_repository(),
            self.project_dir
        )
    
    async def initialize_session(self) -> Dict:
        """Initialize a new task orchestration session."""
        return await self.coordinator.initialize_session()
    
    async def plan_task(self, 
                       description: str, 
                       complexity: str, 
                       subtasks_json: str, 
                       context: str = "") -> TaskBreakdown:
        """Create a task breakdown from LLM-provided subtasks."""
        return await self.coordinator.plan_task(
            description,
            complexity,
            subtasks_json,
            context
        )
    
    async def get_specialist_context(self, task_id: str) -> str:
        """Generate context for a specialist to work on a specific task."""
        return await self.coordinator.get_specialist_context(task_id)
    
    async def complete_subtask_with_artifacts(self,
                                            task_id: str,
                                            results: str,
                                            output_file: Optional[str] = None,
                                            output_content: Optional[str] = None,
                                            metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Complete a subtask with optional artifacts.
        
        This method maintains compatibility with the original interface
        while using the new service architecture.
        """
        # Build artifacts list
        artifacts = []
        
        if output_file and output_content:
            artifacts.append({
                'type': 'code',
                'name': output_file,
                'content': output_content,
                'metadata': metadata or {}
            })
        
        # Complete the task
        return await self.coordinator.complete_subtask(
            task_id,
            results,
            artifacts
        )
    
    async def complete_subtask(self, 
                             task_id: str, 
                             results: str,
                             specialist_type: Optional[str] = None) -> Dict:
        """Complete a subtask and update its status."""
        return await self.coordinator.complete_subtask(
            task_id,
            results
        )
    
    async def synthesize_results(self, parent_task_id: str) -> str:
        """Synthesize results from all subtasks into a comprehensive summary."""
        return await self.coordinator.synthesize_results(parent_task_id)
    
    async def get_status(self, include_completed: bool = False) -> Dict:
        """Get the current status of all tasks being orchestrated."""
        # Get session from state manager for compatibility
        session_id = None
        if hasattr(self.state, 'current_session_id'):
            session_id = self.state.current_session_id
        
        return await self.coordinator.get_status(
            session_id,
            include_completed
        )
    
    async def _check_parent_task_progress(self, completed_task_id: str) -> Dict:
        """
        Check if parent task can be progressed after subtask completion.
        
        This is now handled internally by the progress tracking service
        but we maintain the method for compatibility.
        """
        # This functionality is now part of complete_subtask response
        completion = await self.coordinator.tracking_service.complete_task(
            completed_task_id,
            "",  # Empty results as this is just checking
            []
        )
        return completion.get('parent_progress', {})
    
    async def _get_next_recommended_task(self, completed_task_id: str) -> Optional[Dict]:
        """
        Get recommendation for the next task to work on.
        
        This is now handled by the coordinator but we maintain
        the method for compatibility.
        """
        # Get session from completed task
        task = self.coordinator.task_repo.get_task(completed_task_id)
        if not task:
            return None
        
        session_id = task.get('session_id')
        if not session_id:
            return None
        
        return await self.coordinator.get_next_recommended_task(session_id)
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'repository_factory'):
            self.repository_factory.close()


def create_refactored_orchestrator(state_manager: StateManager,
                                 specialist_manager: SpecialistManager,
                                 project_dir: str = None) -> RefactoredTaskOrchestrator:
    """
    Factory function to create a refactored orchestrator.
    
    This can be used as a drop-in replacement for the original
    TaskOrchestrator constructor.
    
    Args:
        state_manager: State manager
        specialist_manager: Specialist manager
        project_dir: Project directory
        
    Returns:
        RefactoredTaskOrchestrator instance
    """
    return RefactoredTaskOrchestrator(
        state_manager,
        specialist_manager,
        project_dir
    )