"""
Core orchestration logic for task management and specialist coordination.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, 
    ComplexityLevel, TaskResult
)
from .specialists import SpecialistManager
from .state import StateManager


class TaskOrchestrator:
    """Main orchestrator for managing complex tasks and specialist coordination."""
    
    def __init__(self, state_manager: StateManager, specialist_manager: SpecialistManager):
        self.state = state_manager
        self.specialists = specialist_manager
    
    async def plan_task(self, description: str, complexity: str, context: str = "") -> TaskBreakdown:
        """Analyze a task and break it down into specialized subtasks."""
        
        # Generate unique task ID
        parent_task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Analyze task and determine breakdown strategy
        complexity_level = ComplexityLevel(complexity)
        subtasks = await self._analyze_and_breakdown_task(
            description, complexity_level, context
        )
        
        # Create task breakdown
        breakdown = TaskBreakdown(
            parent_task_id=parent_task_id,
            description=description,
            complexity=complexity_level,
            subtasks=subtasks,
            context=context
        )
        
        # Store in state manager
        await self.state.store_task_breakdown(breakdown)
        
        return breakdown
    
    async def get_specialist_context(self, task_id: str) -> str:
        """Get specialist context and prompts for a specific subtask."""
        
        # Retrieve task from state
        subtask = await self.state.get_subtask(task_id)
        if not subtask:
            raise ValueError(f"Task {task_id} not found")
        
        # Mark task as active
        subtask.status = TaskStatus.ACTIVE
        await self.state.update_subtask(subtask)
        
        # Get specialist prompt and context - using the method that exists
        specialist_context = await self.specialists.get_specialist_prompt(
            subtask.specialist_type, subtask
        )
        
        return specialist_context
    
    async def complete_subtask(self, task_id: str, results: str, 
                             artifacts: List[str], next_action: str) -> Dict:
        """Mark a subtask as complete and record its results."""
        
        # Retrieve and update task
        subtask = await self.state.get_subtask(task_id)
        if not subtask:
            raise ValueError(f"Task {task_id} not found")
        
        subtask.status = TaskStatus.COMPLETED
        subtask.results = results
        subtask.artifacts = artifacts
        subtask.completed_at = datetime.utcnow()
        
        await self.state.update_subtask(subtask)
        
        # Check if parent task can be progressed
        parent_progress = await self._check_parent_task_progress(task_id)
        
        return {
            "task_id": task_id,
            "status": "completed",
            "results_recorded": True,
            "parent_task_progress": parent_progress,
            "next_recommended_task": await self._get_next_recommended_task(task_id)
        }
    
    async def synthesize_results(self, parent_task_id: str) -> str:
        """Combine completed subtasks into a comprehensive final result."""
        
        # Get all subtasks for parent
        subtasks = await self.state.get_subtasks_for_parent(parent_task_id)
        completed_subtasks = [st for st in subtasks if st.status == TaskStatus.COMPLETED]
        
        # Generate synthesis using specialist manager
        synthesis = await self.specialists.synthesize_task_results(
            parent_task_id, completed_subtasks
        )
        
        return synthesis
    
    async def get_status(self, include_completed: bool = False) -> Dict:
        """Get current status of all tasks."""
        
        all_tasks = await self.state.get_all_tasks()
        
        if not include_completed:
            all_tasks = [task for task in all_tasks 
                        if task.status != TaskStatus.COMPLETED]
        
        return {
            "active_tasks": len([t for t in all_tasks if t.status == TaskStatus.ACTIVE]),
            "pending_tasks": len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
            "completed_tasks": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "status": task.status.value,
                    "specialist_type": task.specialist_type.value,
                    "created_at": task.created_at.isoformat()
                }
                for task in all_tasks
            ]
        }
    
    async def _analyze_and_breakdown_task(self, description: str, 
                                        complexity: ComplexityLevel, 
                                        context: str) -> List[SubTask]:
        """Analyze a task description and break it into appropriate subtasks."""
        
        # Task analysis logic - this could be enhanced with LLM analysis
        # For now, implementing rule-based analysis
        
        subtasks = []
        
        # Common patterns for different types of tasks
        if any(word in description.lower() for word in ['build', 'create', 'develop', 'implement']):
            # Development task pattern
            if any(word in description.lower() for word in ['web', 'app', 'system', 'api']):
                subtasks.extend(self._create_development_subtasks(description))
        
        elif any(word in description.lower() for word in ['review', 'analyze', 'audit']):
            # Analysis task pattern  
            subtasks.extend(self._create_analysis_subtasks(description))
        
        elif any(word in description.lower() for word in ['debug', 'fix', 'troubleshoot']):
            # Debugging task pattern
            subtasks.extend(self._create_debugging_subtasks(description))
        
        else:
            # Generic task breakdown
            subtasks.extend(self._create_generic_subtasks(description))
        
        return subtasks
    
    def _create_development_subtasks(self, description: str) -> List[SubTask]:
        """Create subtasks for development projects."""
        base_id = uuid.uuid4().hex[:6]
        
        return [
            SubTask(
                task_id=f"arch_{base_id}",
                title="Architecture & Design",
                description=f"Design system architecture and technical approach for: {description}",
                specialist_type=SpecialistType.ARCHITECT,
                estimated_effort="30-60 minutes"
            ),
            SubTask(
                task_id=f"impl_{base_id}",
                title="Core Implementation", 
                description=f"Implement core functionality for: {description}",
                specialist_type=SpecialistType.IMPLEMENTER,
                dependencies=[f"arch_{base_id}"],
                estimated_effort="2-4 hours"
            ),
            SubTask(
                task_id=f"test_{base_id}",
                title="Testing & Debugging",
                description=f"Test implementation and debug issues for: {description}",
                specialist_type=SpecialistType.DEBUGGER,
                dependencies=[f"impl_{base_id}"],
                estimated_effort="1-2 hours"
            ),
            SubTask(
                task_id=f"docs_{base_id}",
                title="Documentation",
                description=f"Create documentation for: {description}",
                specialist_type=SpecialistType.DOCUMENTER,
                dependencies=[f"test_{base_id}"],
                estimated_effort="30-60 minutes"
            )
        ]
    
    def _create_analysis_subtasks(self, description: str) -> List[SubTask]:
        """Create subtasks for analysis/review tasks."""
        base_id = uuid.uuid4().hex[:6]
        
        return [
            SubTask(
                task_id=f"research_{base_id}",
                title="Research & Information Gathering",
                description=f"Gather information and context for: {description}",
                specialist_type=SpecialistType.RESEARCHER,
                estimated_effort="30-45 minutes"
            ),
            SubTask(
                task_id=f"review_{base_id}",
                title="Detailed Review",
                description=f"Perform detailed analysis of: {description}",
                specialist_type=SpecialistType.REVIEWER,
                dependencies=[f"research_{base_id}"],
                estimated_effort="1-2 hours"
            ),
            SubTask(
                task_id=f"report_{base_id}",
                title="Analysis Report",
                description=f"Document findings and recommendations for: {description}",
                specialist_type=SpecialistType.DOCUMENTER,
                dependencies=[f"review_{base_id}"],
                estimated_effort="30-45 minutes"
            )
        ]
    
    def _create_debugging_subtasks(self, description: str) -> List[SubTask]:
        """Create subtasks for debugging/troubleshooting."""
        base_id = uuid.uuid4().hex[:6]
        
        return [
            SubTask(
                task_id=f"diagnose_{base_id}",
                title="Problem Diagnosis",
                description=f"Diagnose the root cause of: {description}",
                specialist_type=SpecialistType.DEBUGGER,
                estimated_effort="45-90 minutes"
            ),
            SubTask(
                task_id=f"fix_{base_id}",
                title="Implement Fix",
                description=f"Implement solution for: {description}",
                specialist_type=SpecialistType.IMPLEMENTER,
                dependencies=[f"diagnose_{base_id}"],
                estimated_effort="1-3 hours"
            ),
            SubTask(
                task_id=f"verify_{base_id}",
                title="Verify Fix",
                description=f"Test and verify the fix for: {description}",
                specialist_type=SpecialistType.DEBUGGER,
                dependencies=[f"fix_{base_id}"],
                estimated_effort="30-60 minutes"
            )
        ]
    
    def _create_generic_subtasks(self, description: str) -> List[SubTask]:
        """Create generic subtasks for unclear task types."""
        base_id = uuid.uuid4().hex[:6]
        
        return [
            SubTask(
                task_id=f"research_{base_id}",
                title="Research & Planning",
                description=f"Research and plan approach for: {description}",
                specialist_type=SpecialistType.RESEARCHER,
                estimated_effort="30-45 minutes"
            ),
            SubTask(
                task_id=f"execute_{base_id}",
                title="Execute Task",
                description=f"Execute the main work for: {description}",
                specialist_type=SpecialistType.IMPLEMENTER,
                dependencies=[f"research_{base_id}"],
                estimated_effort="1-3 hours"
            ),
            SubTask(
                task_id=f"review_{base_id}",
                title="Review & Finalize",
                description=f"Review and finalize work for: {description}",
                specialist_type=SpecialistType.REVIEWER,
                dependencies=[f"execute_{base_id}"],
                estimated_effort="30-45 minutes"
            )
        ]
    
    async def _check_parent_task_progress(self, completed_task_id: str) -> Dict:
        """Check progress of parent task when a subtask completes."""
        # This would check if all dependencies are met and suggest next steps
        return {"progress": "in_progress", "next_steps": "Continue with dependent tasks"}
    
    async def _get_next_recommended_task(self, completed_task_id: str) -> Optional[str]:
        """Get the next recommended task based on dependencies."""
        # This would analyze task dependencies and suggest the next logical task
        return None
