"""
Optimized core orchestration logic for task management and specialist coordination.

This module provides an optimized TaskOrchestrator class that addresses timeout issues
by implementing more efficient transaction handling and error recovery.
"""

import os
import uuid
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from ..domain.entities.task import (
    Task, TaskType, TaskStatus, LifecycleStage
)
from ..domain.value_objects.specialist_type import SpecialistType
from ..domain.value_objects.complexity_level import ComplexityLevel
from .specialist_management_service import SpecialistManager
from .orchestration_state_manager import StateManager
from .role_loader import get_roles
from ..infrastructure.error_handling.decorators import handle_errors
from ..infrastructure.error_handling.retry_coordinator import ExponentialBackoffPolicy
from ..application.dto.error_responses import ErrorResponseBuilder


# Configure logging
logger = logging.getLogger("mcp_task_orchestrator.core")


class TaskOrchestrator:
    """Main orchestrator for managing complex tasks and specialist coordination.
    
    This optimized version addresses timeout issues by:
    - Using more efficient transaction handling
    - Implementing better error recovery
    - Adding retry mechanisms with exponential backoff
    - Increasing timeout thresholds where appropriate
    """
    
    def __init__(self, state_manager: StateManager, specialist_manager: SpecialistManager, project_dir: str = None):
        self.state = state_manager
        self.specialists = specialist_manager
        self.project_dir = project_dir or os.getcwd()
    
    async def initialize_session(self) -> Dict:
        """Initialize a new task orchestration session with guidance for the LLM."""
        
        # Load role definitions from project directory or default
        roles = get_roles(self.project_dir)
        
        # If task_orchestrator role is defined in the roles, use it
        if roles and 'task_orchestrator' in roles:
            task_orchestrator = roles['task_orchestrator']
            
            # Build response from role definition
            response = {
                "role": "Task Orchestrator",
                "capabilities": task_orchestrator.get('expertise', []),
                "instructions": "\n".join(task_orchestrator.get('approach', [])),
                "specialist_roles": task_orchestrator.get('specialist_roles', {})
            }
            
            return response
        
        # Fall back to default task orchestrator definition
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
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="plan_task"
    )
    async def _store_task_breakdown_with_timeout(self, main_task: Task) -> None:
        """Store task breakdown with timeout and error handling."""
        await asyncio.wait_for(
            self.state.store_task_breakdown(main_task),
            timeout=5  # 5s timeout for fast database operations
        )

    async def plan_task(self, description: str, complexity: str, subtasks_json: str, context: str = "") -> Task:
        """Create a task breakdown from LLM-provided subtasks."""
        
        # Generate unique task ID
        parent_task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Parse the subtasks JSON provided by the LLM
        try:
            subtasks_data = json.loads(subtasks_json)
            subtasks = []
            
            for i, st_data in enumerate(subtasks_data):
                # Create Task objects from the provided JSON
                task_id = st_data.get("task_id", f"{st_data['specialist_type']}_{uuid.uuid4().hex[:6]}")
                subtask = Task(
                    task_id=task_id,
                    parent_task_id=parent_task_id,
                    title=st_data["title"],
                    description=st_data["description"],
                    task_type=TaskType.STANDARD,
                    hierarchy_path=f"/{parent_task_id}/{task_id}",
                    hierarchy_level=1,
                    position_in_parent=i,
                    estimated_effort=st_data.get("estimated_effort", "Unknown"),
                    specialist_type=st_data["specialist_type"]
                )
                subtasks.append(subtask)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid subtasks JSON format: {str(e)}")
        
        # Create main task with child tasks
        complexity_level = ComplexityLevel(complexity)
        main_task = Task(
            task_id=parent_task_id,
            title=description[:100],  # First 100 chars as title
            description=description,
            task_type=TaskType.BREAKDOWN,
            complexity=complexity_level,
            hierarchy_path=f"/{parent_task_id}",
            children=subtasks,
            context={"original_context": context} if context else {}
        )
        
        # Store in state manager using error handling infrastructure
        await self._store_task_breakdown_with_timeout(main_task)
        
        return main_task
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="get_specialist_context"
    )
    async def _get_specialist_context_with_recovery(self, task_id: str) -> str:
        """Get specialist context with error handling and recovery."""
        # Retrieve task from state with timeout
        subtask = await asyncio.wait_for(
            self.state.get_subtask(task_id),
            timeout=5
        )
        
        if not subtask:
            raise ValueError(f"Task {task_id} not found")
        
        original_status = subtask.status
        
        try:
            # Mark task as active
            subtask.status = TaskStatus.ACTIVE
            await asyncio.wait_for(
                self.state.update_subtask(subtask),
                timeout=5
            )
            
            # Get specialist prompt and context
            specialist_context = await asyncio.wait_for(
                self.specialists.get_specialist_prompt(
                    subtask.specialist_type, subtask
                ),
                timeout=5
            )
            
            return specialist_context
        
        except Exception:
            # Revert task status on any error
            try:
                subtask.status = original_status
                await asyncio.wait_for(
                    self.state.update_subtask(subtask),
                    timeout=5
                )
            except Exception as revert_error:
                logger.error(f"Failed to revert task status: {str(revert_error)}")
            raise

    async def get_specialist_context(self, task_id: str) -> str:
        """Get specialist context and prompts for a specific subtask."""
        return await self._get_specialist_context_with_recovery(task_id)
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="complete_subtask_with_artifacts"
    )
    async def _complete_subtask_with_artifacts_core(self, task_id: str, summary: str, artifacts: List[str], artifact_info: Dict[str, Any]) -> Dict:
        """Core logic for completing subtask with artifacts."""
        # Retrieve task with timeout
        subtask = await asyncio.wait_for(
            self.state.get_subtask(task_id),
            timeout=5
        )
        
        if not subtask:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status and data with artifact information
        subtask.status = TaskStatus.COMPLETED
        subtask.results = summary
        subtask.artifacts = artifacts
        subtask.completed_at = datetime.utcnow()
        
        # Update the subtask
        await asyncio.wait_for(
            self.state.update_subtask(subtask),
            timeout=5
        )
        
        # Check if parent task can be progressed and get next recommended task
        parent_progress, next_task = await asyncio.gather(
            self._check_parent_task_progress(task_id),
            self._get_next_recommended_task(task_id)
        )
        
        return {
            "task_id": task_id,
            "status": "completed",
            "results_recorded": True,
            "parent_task_progress": parent_progress,
            "next_recommended_task": next_task,
            "artifact_integration": {
                "artifact_id": artifact_info.get("artifact_id"),
                "artifact_type": artifact_info.get("artifact_type"),
                "stored_successfully": True,
                "accessible_via": artifact_info.get("accessible_via")
            }
        }

    async def complete_subtask_with_artifacts(self, 
                                            task_id: str, 
                                            summary: str, 
                                            artifacts: List[str], 
                                            next_action: str,
                                            artifact_info: Dict[str, Any]) -> Dict:
        """Complete a subtask with enhanced artifact information.
        
        This method extends the standard complete_subtask to include artifact metadata
        and enhanced tracking for the new artifact system.
        
        Args:
            task_id: Task ID
            summary: Brief summary for database storage
            artifacts: List of artifact references (includes file paths)
            next_action: Next action to take
            artifact_info: Metadata about the created artifact
            
        Returns:
            Completion result dictionary with artifact information
        """
        # Ensure artifacts is properly formatted
        if artifacts is None:
            artifacts = []
        elif not isinstance(artifacts, list):
            artifacts = [artifacts] if artifacts else []
        
        try:
            return await self._complete_subtask_with_artifacts_core(task_id, summary, artifacts, artifact_info)
        except Exception as e:
            # Return error response using ErrorResponseBuilder
            error_response = ErrorResponseBuilder.subtask_error(task_id, e)
            # Add artifact-specific fields
            error_response_dict = error_response.dict()
            error_response_dict["artifact_integration"] = {
                "artifact_id": artifact_info.get("artifact_id"),
                "stored_successfully": True,
                "accessible_via": artifact_info.get("accessible_via"),
                "warning": "Task completion failed but artifact was stored"
            }
            return error_response_dict
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="complete_subtask"
    )
    async def _complete_subtask_core(self, task_id: str, results: str, artifacts: List[str]) -> Dict:
        """Core logic for completing a subtask."""
        # Retrieve task with timeout
        subtask = await asyncio.wait_for(
            self.state.get_subtask(task_id),
            timeout=5
        )
        
        if not subtask:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task status and data
        subtask.status = TaskStatus.COMPLETED
        subtask.results = results
        subtask.artifacts = artifacts
        subtask.completed_at = datetime.utcnow()
        
        # Update the subtask
        await asyncio.wait_for(
            self.state.update_subtask(subtask),
            timeout=5
        )
        
        # Check if parent task can be progressed and get next recommended task
        parent_progress, next_task = await asyncio.gather(
            self._check_parent_task_progress(task_id),
            self._get_next_recommended_task(task_id)
        )
        
        return {
            "task_id": task_id,
            "status": "completed",
            "results_recorded": True,
            "parent_task_progress": parent_progress,
            "next_recommended_task": next_task
        }

    async def complete_subtask(self, task_id: str, results: str, 
                             artifacts: List[str], next_action: str) -> Dict:
        """Mark a subtask as complete and record its results.
        
        This optimized version:
        - Uses error handling infrastructure with retry
        - Combines related operations to reduce lock acquisitions
        - Implements standardized error responses
        """
        
        # Ensure artifacts is properly formatted
        if artifacts is None:
            artifacts = []
        elif not isinstance(artifacts, list):
            artifacts = [artifacts] if artifacts else []
        
        try:
            return await self._complete_subtask_core(task_id, results, artifacts)
        except Exception as e:
            # Return error response using ErrorResponseBuilder
            return ErrorResponseBuilder.subtask_error(task_id, e).dict()
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="synthesize_results"
    )
    async def synthesize_results(self, parent_task_id: str) -> str:
        """Combine completed subtasks into a comprehensive final result."""
        
        # Get all subtasks for parent with timeout
        subtasks = await asyncio.wait_for(
            self.state.get_subtasks_for_parent(parent_task_id),
            timeout=5
        )
        
        completed_subtasks = [st for st in subtasks if st.status == TaskStatus.COMPLETED]
        
        # Generate synthesis using specialist manager
        synthesis = await asyncio.wait_for(
            self.specialists.synthesize_task_results(
                parent_task_id, completed_subtasks
            ),
            timeout=10
        )
        
        return synthesis
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=0.1, backoff_factor=1.5),
        component="TaskOrchestrator",
        operation="get_status"
    )
    async def _get_status_core(self, include_completed: bool = False) -> Dict:
        """Core logic for getting task status."""
        all_tasks = await asyncio.wait_for(
            self.state.get_all_tasks(),
            timeout=5
        )
        
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

    async def get_status(self, include_completed: bool = False) -> Dict:
        """Get current status of all tasks."""
        try:
            return await self._get_status_core(include_completed)
        except Exception as e:
            # Return error response using ErrorResponseBuilder
            return ErrorResponseBuilder.status_error(e).dict()
    
    async def _check_parent_task_progress(self, completed_task_id: str) -> Dict:
        """Check progress of parent task when a subtask completes."""
        try:
            # Get parent task ID with timeout protection
            parent_task_id = await asyncio.wait_for(
                self.state._get_parent_task_id(completed_task_id),
                timeout=3  # Quick timeout since DB operations are fast
            )
            if not parent_task_id:
                return {"progress": "unknown", "error": "Parent task not found"}
            
            # Get all subtasks for parent with timeout protection
            subtasks = await asyncio.wait_for(
                self.state.get_subtasks_for_parent(parent_task_id),
                timeout=3  # Quick timeout since DB operations are fast
            )
            total = len(subtasks)
            completed = len([st for st in subtasks if st.status == TaskStatus.COMPLETED])
            
            # Calculate progress percentage
            progress_pct = (completed / total) * 100 if total > 0 else 0
            
            return {
                "progress": "in_progress" if completed < total else "completed",
                "parent_task_id": parent_task_id,
                "completed_subtasks": completed,
                "total_subtasks": total,
                "progress_percentage": progress_pct
            }
        except asyncio.TimeoutError:
            logger.error(f"Timeout checking parent task progress for {completed_task_id}")
            return {"progress": "unknown", "error": "Operation timed out"}
        except Exception as e:
            logger.error(f"Error checking parent task progress: {str(e)}")
            return {"progress": "unknown", "error": str(e)}
    
    async def _get_next_recommended_task(self, completed_task_id: str) -> Optional[Dict]:
        """Get the next recommended task based on dependencies."""
        try:
            # Get parent task ID with timeout protection
            parent_task_id = await asyncio.wait_for(
                self.state._get_parent_task_id(completed_task_id),
                timeout=3  # Quick timeout since DB operations are fast
            )
            if not parent_task_id:
                return None
            
            # Get all subtasks for parent with timeout protection
            subtasks = await asyncio.wait_for(
                self.state.get_subtasks_for_parent(parent_task_id),
                timeout=3  # Quick timeout since DB operations are fast
            )
            
            # Find subtasks that depend on the completed task
            dependent_tasks = []
            for subtask in subtasks:
                if completed_task_id in subtask.dependencies:
                    dependent_tasks.append(subtask)
            
            # Check if all dependencies are met for each dependent task
            for task in dependent_tasks:
                all_deps_met = True
                for dep_id in task.dependencies:
                    dep_task = next((st for st in subtasks if st.task_id == dep_id), None)
                    if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                        all_deps_met = False
                        break
                
                if all_deps_met and task.status == TaskStatus.PENDING:
                    # Found a task with all dependencies met
                    return {
                        "task_id": task.task_id,
                        "title": task.title,
                        "specialist_type": task.specialist_type.value
                    }
            
            # If no dependent tasks are ready, find any pending task
            for task in subtasks:
                if task.status == TaskStatus.PENDING:
                    all_deps_met = True
                    for dep_id in task.dependencies:
                        dep_task = next((st for st in subtasks if st.task_id == dep_id), None)
                        if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                            all_deps_met = False
                            break
                    
                    if all_deps_met:
                        return {
                            "task_id": task.task_id,
                            "title": task.title,
                            "specialist_type": task.specialist_type.value
                        }
            
            return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout getting next recommended task for {completed_task_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting next recommended task: {str(e)}")
            return None
