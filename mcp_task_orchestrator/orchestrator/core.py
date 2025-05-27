"""
Core orchestration logic for task management and specialist coordination.
"""

import uuid
import json
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
    
    async def initialize_session(self) -> Dict:
        """Initialize a new task orchestration session with guidance for the LLM."""
        
        # Provide context and instructions to the LLM for effective task orchestration
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
    
    async def plan_task(self, description: str, complexity: str, subtasks_json: str, context: str = "") -> TaskBreakdown:
        """Create a task breakdown from LLM-provided subtasks."""
        
        # Generate unique task ID
        parent_task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Parse the subtasks JSON provided by the LLM
        try:
            subtasks_data = json.loads(subtasks_json)
            subtasks = []
            
            for st_data in subtasks_data:
                # Create SubTask objects from the provided JSON
                subtask = SubTask(
                    task_id=st_data.get("task_id", f"{st_data['specialist_type']}_{uuid.uuid4().hex[:6]}"),
                    title=st_data["title"],
                    description=st_data["description"],
                    specialist_type=SpecialistType(st_data["specialist_type"]),
                    dependencies=st_data.get("dependencies", []),
                    estimated_effort=st_data.get("estimated_effort", "Unknown")
                )
                subtasks.append(subtask)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid subtasks JSON format: {str(e)}")
        
        # Create task breakdown
        complexity_level = ComplexityLevel(complexity)
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
    
    # The _analyze_and_breakdown_task method and the template methods are no longer needed
    # as the LLM will now be responsible for task breakdown
    # We're removing:
    # - _analyze_and_breakdown_task
    # - _create_development_subtasks
    # - _create_analysis_subtasks
    # - _create_debugging_subtasks
    # - _create_generic_subtasks
    
    async def _check_parent_task_progress(self, completed_task_id: str) -> Dict:
        """Check progress of parent task when a subtask completes."""
        # This would check if all dependencies are met and suggest next steps
        return {"progress": "in_progress", "next_steps": "Continue with dependent tasks"}
    
    async def _get_next_recommended_task(self, completed_task_id: str) -> Optional[str]:
        """Get the next recommended task based on dependencies."""
        # This would analyze task dependencies and suggest the next logical task
        return None
