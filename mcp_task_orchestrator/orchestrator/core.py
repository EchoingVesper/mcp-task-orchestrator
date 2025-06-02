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

from .models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, 
    ComplexityLevel, TaskResult
)
from .specialists import SpecialistManager
from .state import StateManager
from .role_loader import get_roles


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
        
        # Store in state manager with optimized retry logic for fast database operations
        max_retries = 2  # Reduced from 3
        retry_delay = 0.1  # Reduced from 0.5s
        
        for attempt in range(max_retries):
            try:
                await asyncio.wait_for(
                    self.state.store_task_breakdown(breakdown),
                    timeout=5  # Reduced from 15s to 5s since DB operations are fast
                )
                break  # Success, exit the retry loop
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout storing task breakdown (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced multiplier from 2 to 1.5
                else:
                    # Last attempt, re-raise the exception
                    raise ValueError(f"Failed to store task breakdown after {max_retries} attempts: {str(e)}")
            except Exception as e:
                logger.error(f"Error storing task breakdown (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced multiplier from 2 to 1.5
                else:
                    # Last attempt, re-raise the exception
                    raise
        
        return breakdown
    
    async def get_specialist_context(self, task_id: str) -> str:
        """Get specialist context and prompts for a specific subtask."""
        
        # Optimized retry logic for fast database operations
        max_retries = 2  # Reduced from 3
        retry_delay = 0.1  # Reduced from 0.5s
        
        for attempt in range(max_retries):
            try:
                # Retrieve task from state with reduced timeout
                subtask = await asyncio.wait_for(
                    self.state.get_subtask(task_id),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                if not subtask:
                    raise ValueError(f"Task {task_id} not found")
                
                # Mark task as active
                subtask.status = TaskStatus.ACTIVE
                await asyncio.wait_for(
                    self.state.update_subtask(subtask),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                # Get specialist prompt and context with reduced timeout
                specialist_context = await asyncio.wait_for(
                    self.specialists.get_specialist_prompt(
                        subtask.specialist_type, subtask
                    ),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                return specialist_context
                
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout getting specialist context for task {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, revert task status if possible and raise exception
                    try:
                        subtask = await self.state.get_subtask(task_id)
                        if subtask and subtask.status == TaskStatus.ACTIVE:
                            subtask.status = TaskStatus.PENDING
                            await self.state.update_subtask(subtask)
                    except Exception as revert_error:
                        logger.error(f"Failed to revert task status: {str(revert_error)}")
                    
                    raise ValueError(f"Timeout getting specialist context for task {task_id} after {max_retries} attempts")
                
            except Exception as e:
                logger.error(f"Error getting specialist context for task {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, revert task status if possible and raise exception
                    try:
                        subtask = await self.state.get_subtask(task_id)
                        if subtask and subtask.status == TaskStatus.ACTIVE:
                            subtask.status = TaskStatus.PENDING
                            await self.state.update_subtask(subtask)
                    except Exception as revert_error:
                        logger.error(f"Failed to revert task status: {str(revert_error)}")
                    
                    raise
    
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
        
        # Use the standard completion method with optimized retry logic
        max_retries = 2
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                # Retrieve task with reduced timeout
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
                
                # Update the subtask with reduced timeout
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
                
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout completing subtask with artifacts {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5
                else:
                    return {
                        "task_id": task_id,
                        "status": "timeout",
                        "error": f"Operation timed out after {max_retries} attempts: {str(e)}",
                        "results_recorded": False,
                        "parent_task_progress": {"progress": "unknown", "error": f"Timeout: {str(e)}"},
                        "next_recommended_task": None,
                        "artifact_integration": {
                            "artifact_id": artifact_info.get("artifact_id"),
                            "stored_successfully": True,
                            "accessible_via": artifact_info.get("accessible_via"),
                            "warning": "Task completion timed out but artifact was stored"
                        }
                    }
                    
            except Exception as e:
                logger.error(f"Error completing subtask with artifacts {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5
                else:
                    return {
                        "task_id": task_id,
                        "status": "error",
                        "error": str(e),
                        "results_recorded": False,
                        "parent_task_progress": {"progress": "unknown", "error": str(e)},
                        "next_recommended_task": None,
                        "artifact_integration": {
                            "artifact_id": artifact_info.get("artifact_id"),
                            "stored_successfully": True,
                            "accessible_via": artifact_info.get("accessible_via"),
                            "warning": "Task completion failed but artifact was stored"
                        }
                    }
    
    async def complete_subtask(self, task_id: str, results: str, 
                             artifacts: List[str], next_action: str) -> Dict:
        """Mark a subtask as complete and record its results.
        
        This optimized version:
        - Uses a retry mechanism with exponential backoff
        - Combines related operations to reduce lock acquisitions
        - Implements better error handling and recovery
        """
        
        # Ensure artifacts is properly formatted
        if artifacts is None:
            artifacts = []
        elif not isinstance(artifacts, list):
            artifacts = [artifacts] if artifacts else []
        
        # Optimized retry logic - reduced timeouts since database operations are now fast
        max_retries = 2  # Reduced from 3 to 2
        retry_delay = 0.1  # Reduced from 0.5s to 0.1s
        
        for attempt in range(max_retries):
            try:
                # Retrieve task with reduced timeout (database operations are fast now)
                subtask = await asyncio.wait_for(
                    self.state.get_subtask(task_id),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                if not subtask:
                    raise ValueError(f"Task {task_id} not found")
                
                # Update task status and data
                subtask.status = TaskStatus.COMPLETED
                subtask.results = results
                subtask.artifacts = artifacts
                subtask.completed_at = datetime.utcnow()
                
                # Update the subtask with reduced timeout
                await asyncio.wait_for(
                    self.state.update_subtask(subtask),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                # Check if parent task can be progressed and get next recommended task
                # Combine these operations to reduce the number of lock acquisitions
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
                
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout completing subtask {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced exponential backoff multiplier from 2 to 1.5
                else:
                    # Last attempt, return a partial result to avoid hanging
                    return {
                        "task_id": task_id,
                        "status": "timeout",
                        "error": f"Operation timed out after {max_retries} attempts: {str(e)}",
                        "results_recorded": False,
                        "parent_task_progress": {"progress": "unknown", "error": f"Timeout: {str(e)}"},
                        "next_recommended_task": None
                    }
                    
            except Exception as e:
                logger.error(f"Error completing subtask {task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced exponential backoff multiplier from 2 to 1.5
                else:
                    # Last attempt, return a partial result to avoid hanging
                    return {
                        "task_id": task_id,
                        "status": "error",
                        "error": str(e),
                        "results_recorded": False,
                        "parent_task_progress": {"progress": "unknown", "error": str(e)},
                        "next_recommended_task": None
                    }
    
    async def synthesize_results(self, parent_task_id: str) -> str:
        """Combine completed subtasks into a comprehensive final result."""
        
        # Optimized retry logic for fast database operations
        max_retries = 2  # Reduced from 3
        retry_delay = 0.1  # Reduced from 0.5s
        
        for attempt in range(max_retries):
            try:
                # Get all subtasks for parent with reduced timeout
                subtasks = await asyncio.wait_for(
                    self.state.get_subtasks_for_parent(parent_task_id),
                    timeout=5  # Reduced from 15s to 5s
                )
                
                completed_subtasks = [st for st in subtasks if st.status == TaskStatus.COMPLETED]
                
                # Generate synthesis using specialist manager with reduced timeout
                synthesis = await asyncio.wait_for(
                    self.specialists.synthesize_task_results(
                        parent_task_id, completed_subtasks
                    ),
                    timeout=10  # Reduced from 20s to 10s
                )
                
                return synthesis
                
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout synthesizing results for task {parent_task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, raise exception
                    raise ValueError(f"Timeout synthesizing results for task {parent_task_id} after {max_retries} attempts")
                    
            except Exception as e:
                logger.error(f"Error synthesizing results for task {parent_task_id} (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, raise exception
                    raise
    
    async def get_status(self, include_completed: bool = False) -> Dict:
        """Get current status of all tasks."""
        
        # Optimized retry logic for fast database operations
        max_retries = 2  # Reduced from 3
        retry_delay = 0.1  # Reduced from 0.5s
        
        for attempt in range(max_retries):
            try:
                all_tasks = await asyncio.wait_for(
                    self.state.get_all_tasks(),
                    timeout=5  # Reduced from 15s to 5s
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
                
            except asyncio.TimeoutError as e:
                logger.error(f"Timeout getting status (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, return a partial result
                    return {
                        "error": f"Timeout getting status after {max_retries} attempts",
                        "active_tasks": 0,
                        "pending_tasks": 0,
                        "completed_tasks": 0,
                        "tasks": []
                    }
                    
            except Exception as e:
                logger.error(f"Error getting status (attempt {attempt+1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Reduced from 2 to 1.5
                else:
                    # Last attempt, return a partial result
                    return {
                        "error": str(e),
                        "active_tasks": 0,
                        "pending_tasks": 0,
                        "completed_tasks": 0,
                        "tasks": []
                    }
    
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
