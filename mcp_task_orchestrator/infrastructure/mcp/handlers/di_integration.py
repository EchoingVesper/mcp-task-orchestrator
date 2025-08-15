"""
Clean Architecture DI Container Integration for MCP Handlers

This module provides use case factories that integrate with the
Clean Architecture dependency injection container system.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from ....domain.repositories.task_repository import TaskRepository
from ....domain.entities.task import Task, TaskType, TaskStatus
from ....domain.value_objects.complexity_level import ComplexityLevel
from ....domain.value_objects.specialist_type import SpecialistType
from ....domain.exceptions import OrchestrationError
from ....infrastructure.di import get_container

logger = logging.getLogger(__name__)


class CleanArchTaskUseCase:
    """Clean Architecture task use case using DI container."""
    
    def __init__(self):
        """Initialize with DI container."""
        self.container = get_container()
        self.task_repository = self.container.get_service(TaskRepository)
    
    async def create_task(self, task_data: Dict[str, Any]) -> Any:
        """Create a task using Clean Architecture."""
        try:
            # Generate task ID
            from uuid import uuid4
            task_id = f"task_{str(uuid4()).replace('-', '')[:8]}"
            
            # Convert data to Clean Architecture format
            clean_task_data = {
                "id": task_id,
                "session_id": task_data.get("session_id"),
                "parent_task_id": task_data.get("parent_task_id"),
                "type": task_data.get("task_type", "standard"),
                "status": "pending",
                "title": task_data.get("title", "Untitled Task"),
                "description": task_data.get("description", ""),
                "metadata": json.dumps({
                    "complexity": task_data.get("complexity", "moderate"),
                    "specialist_type": task_data.get("specialist_type", "generic"),
                    "estimated_effort": task_data.get("estimated_effort"),
                    "due_date": task_data.get("due_date"),
                    "dependencies": task_data.get("dependencies", []),
                    "context": task_data.get("context", {})
                }),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "completed_at": None
            }
            
            # Store in repository
            result_id = self.task_repository.create_task(clean_task_data)
            
            logger.info(f"Successfully created task {result_id} via Clean Architecture")
            
            # Return simple dict - no MockTask objects needed
            return {
                "task_id": result_id,
                "title": task_data.get("title", ""),
                "description": task_data.get("description", ""),
                "status": "pending",
                "task_type": task_data.get("task_type", "standard"),
                "complexity": task_data.get("complexity", "moderate"),
                "specialist_type": task_data.get("specialist_type", "generic"),
                "created_at": clean_task_data["created_at"],
                "message": f"Task created successfully with ID: {result_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to create task via Clean Architecture: {str(e)}")
            raise OrchestrationError(f"Task creation failed: {str(e)}")
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task using Clean Architecture."""
        try:
            # Get existing task
            existing_task = self.task_repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Update fields
            updates = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if "title" in update_data:
                updates["title"] = update_data["title"]
            if "description" in update_data:
                updates["description"] = update_data["description"]
            if "status" in update_data:
                updates["status"] = update_data["status"]
            
            # Handle metadata updates
            if any(key in update_data for key in ["complexity", "specialist_type", "context"]):
                existing_metadata = json.loads(existing_task.get("metadata", "{}"))
                if "complexity" in update_data:
                    existing_metadata["complexity"] = update_data["complexity"]
                if "specialist_type" in update_data:
                    existing_metadata["specialist_type"] = update_data["specialist_type"]
                if "context" in update_data:
                    existing_metadata["context"] = update_data["context"]
                updates["metadata"] = json.dumps(existing_metadata)
            
            # Update in repository
            success = self.task_repository.update_task(task_id, updates)
            if not success:
                raise OrchestrationError(f"Failed to update task {task_id}")
            
            # Return updated task
            updated_task = self.task_repository.get_task(task_id)
            return self._format_task_response(updated_task)
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task update failed: {str(e)}")
    
    async def query_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query tasks using Clean Architecture."""
        try:
            # Apply filters
            filters = filters or {}
            tasks = await self.task_repository.query_tasks(filters)
            
            return [self._format_task_response(task) for task in tasks]
            
        except Exception as e:
            logger.error(f"Failed to query tasks: {str(e)}")
            raise OrchestrationError(f"Task query failed: {str(e)}")
    
    async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
        """Delete a task with dependency checking and archive logic."""
        try:
            # Check if task exists
            existing_task = self.task_repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Find tasks that depend on this task (if not forcing deletion)
            if not force:
                dependent_tasks = await self._find_dependent_tasks(task_id)
                if dependent_tasks:
                    dependent_ids = [task["id"] for task in dependent_tasks]
                    raise OrchestrationError(
                        f"Cannot delete task {task_id}: {len(dependent_tasks)} dependent tasks found: {dependent_ids}. "
                        f"Use force=True to delete anyway."
                    )
            
            action_taken = "archived" if archive_instead else "deleted"
            
            if archive_instead:
                # Archive the task by updating status and adding archived timestamp
                archive_updates = {
                    "status": "archived",
                    "updated_at": datetime.utcnow().isoformat(),
                    "archived_at": datetime.utcnow().isoformat()
                }
                success = self.task_repository.update_task(task_id, archive_updates)
                if not success:
                    raise OrchestrationError(f"Failed to archive task {task_id}")
            else:
                # Actually delete the task
                success = self.task_repository.delete_task(task_id)
                if not success:
                    raise OrchestrationError(f"Failed to delete task {task_id}")
            
            logger.info(f"Task {task_id} {action_taken} successfully")
            
            return {
                "task_id": task_id,
                "action_taken": action_taken,
                "success": True,
                "message": f"Task {task_id} {action_taken} successfully",
                "forced": force,
                "archive_instead": archive_instead,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task deletion failed: {str(e)}")
    
    async def cancel_task(self, task_id: str, reason: str = "", preserve_work: bool = True) -> Dict[str, Any]:
        """Cancel a task with state management and artifact preservation."""
        try:
            # Check if task exists
            existing_task = self.task_repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            current_status = existing_task.get("status", "")
            
            # Check if task is cancellable
            if current_status in ["completed", "cancelled", "archived"]:
                raise OrchestrationError(
                    f"Cannot cancel task {task_id}: task is already {current_status}"
                )
            
            # Preserve work artifacts if requested
            artifacts_preserved = 0
            if preserve_work:
                try:
                    # Get existing artifacts
                    artifacts = self.task_repository.get_task_artifacts(task_id)
                    artifacts_preserved = len(artifacts)
                    
                    # Add cancellation artifact with reason
                    cancellation_artifact = {
                        "type": "cancellation_record",
                        "reason": reason or "No reason provided",
                        "preserved_work_count": artifacts_preserved,
                        "cancelled_at": datetime.utcnow().isoformat(),
                        "original_status": current_status
                    }
                    self.task_repository.add_task_artifact(task_id, cancellation_artifact)
                    
                except Exception as artifact_error:
                    logger.warning(f"Failed to preserve artifacts for task {task_id}: {artifact_error}")
            
            # Update task status to cancelled
            cancellation_updates = {
                "status": "cancelled",
                "updated_at": datetime.utcnow().isoformat(),
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
            # Add cancellation reason to metadata
            existing_metadata = json.loads(existing_task.get("metadata", "{}"))
            existing_metadata["cancellation"] = {
                "reason": reason or "No reason provided",
                "cancelled_at": datetime.utcnow().isoformat(),
                "original_status": current_status,
                "work_preserved": preserve_work,
                "artifacts_preserved": artifacts_preserved
            }
            cancellation_updates["metadata"] = json.dumps(existing_metadata)
            
            success = self.task_repository.update_task(task_id, cancellation_updates)
            if not success:
                raise OrchestrationError(f"Failed to cancel task {task_id}")
            
            # Update dependent tasks (mark them as ready if this was a blocking dependency)
            await self._update_dependent_tasks_on_cancellation(task_id)
            
            logger.info(f"Task {task_id} cancelled successfully. Reason: {reason}")
            
            return {
                "task_id": task_id,
                "status": "cancelled",
                "success": True,
                "message": f"Task {task_id} cancelled successfully",
                "reason": reason or "No reason provided",
                "original_status": current_status,
                "work_preserved": preserve_work,
                "artifacts_preserved": artifacts_preserved,
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task cancellation failed: {str(e)}")
    
    async def _find_dependent_tasks(self, task_id: str) -> List[Dict[str, Any]]:
        """Find tasks that depend on the given task."""
        try:
            # Query all tasks to check their dependencies
            # This is a simplified implementation - in a full system you'd have a proper dependency table
            all_tasks = await self.task_repository.query_tasks({})
            dependent_tasks = []
            
            for task in all_tasks:
                # Check if this task has the target task as a dependency
                task_deps = self.task_repository.get_task_dependencies(task["id"])
                if task_id in task_deps:
                    dependent_tasks.append(task)
            
            return dependent_tasks
            
        except Exception as e:
            logger.warning(f"Failed to find dependent tasks for {task_id}: {e}")
            return []
    
    async def _update_dependent_tasks_on_cancellation(self, cancelled_task_id: str):
        """Update tasks that depended on the cancelled task."""
        try:
            dependent_tasks = await self._find_dependent_tasks(cancelled_task_id)
            
            for task in dependent_tasks:
                # For now, just add a note about the cancelled dependency
                # In a full implementation, you might update dependency status or make the task ready
                existing_metadata = json.loads(task.get("metadata", "{}"))
                
                if "dependency_issues" not in existing_metadata:
                    existing_metadata["dependency_issues"] = []
                
                existing_metadata["dependency_issues"].append({
                    "cancelled_dependency": cancelled_task_id,
                    "noted_at": datetime.utcnow().isoformat(),
                    "impact": "dependency_cancelled"
                })
                
                update_data = {
                    "metadata": json.dumps(existing_metadata),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                self.task_repository.update_task(task["id"], update_data)
                logger.info(f"Updated task {task['id']} due to cancelled dependency {cancelled_task_id}")
                
        except Exception as e:
            logger.warning(f"Failed to update dependent tasks for cancelled task {cancelled_task_id}: {e}")

    def _format_task_response(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format task data for response."""
        # Handle metadata that could be either a string or dict
        metadata_raw = task_data.get("metadata", {})
        if isinstance(metadata_raw, str):
            metadata = json.loads(metadata_raw) if metadata_raw else {}
        else:
            metadata = metadata_raw if metadata_raw else {}
        return {
            "task_id": task_data["id"],
            "title": task_data["title"],
            "description": task_data["description"],
            "status": task_data["status"],
            "complexity": metadata.get("complexity", "moderate"),
            "specialist_type": metadata.get("specialist_type", "generic"),
            "task_type": task_data["type"],
            "created_at": task_data["created_at"],
            "updated_at": task_data["updated_at"],
            "completed_at": task_data.get("completed_at"),
            "metadata": metadata.get("context", {})
        }


class CleanArchExecuteTaskUseCase:
    """Execute task use case using Clean Architecture."""
    
    def __init__(self):
        self.container = get_container()
        self.task_repository = self.container.get_service(TaskRepository)
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a task and return specialist context."""
        try:
            task = self.task_repository.get_task(task_id)
            if not task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            metadata = json.loads(task.get("metadata", "{}"))
            specialist_type = metadata.get("specialist_type", "generic")
            context_data = metadata.get("context", {})
            
            # Generate specialist prompts based on type
            specialist_prompts = []
            if specialist_type == "devops":
                specialist_prompts.extend([
                    "Focus on infrastructure, CI/CD, and deployment concerns",
                    "Ensure system reliability and performance",
                    "Follow security best practices"
                ])
            elif specialist_type == "documenter":
                specialist_prompts.extend([
                    "Create clear, comprehensive documentation",
                    "Follow documentation standards and formatting",
                    "Consider your audience's needs"
                ])
            elif specialist_type == "architect":
                specialist_prompts.extend([
                    "Design for scalability and maintainability", 
                    "Consider system architecture and patterns",
                    "Document architectural decisions"
                ])
            elif specialist_type == "coder":
                specialist_prompts.extend([
                    "Write clean, well-tested code",
                    "Follow coding standards and best practices",
                    "Consider performance and security"
                ])
            else:
                specialist_prompts.append(f"Apply {specialist_type} specialist knowledge to this task")
            
            # Generate execution instructions
            execution_instructions = [
                f"Task: {task['title']}",
                f"Description: {task['description']}",
                f"Specialist Role: {specialist_type}",
                "",
                "Execute this task using your specialist expertise.",
                "Provide detailed work artifacts when completing the task.",
                "Use orchestrator_complete_task to store your results."
            ]
            
            # Return format expected by handler
            return {
                "task_id": task_id,
                "task_title": task.get('title', 'Untitled Task'),
                "task_description": task.get('description', ''),
                "specialist_type": specialist_type,
                "specialist_context": context_data,
                "specialist_prompts": specialist_prompts,
                "execution_instructions": execution_instructions,
                "dependencies_completed": True,  # Simplified for now
                "estimated_effort": metadata.get("estimated_effort", "Unknown"),
                "next_steps": [
                    "Review the task details and specialist context",
                    "Execute the task according to the instructions",
                    "Complete the task using orchestrator_complete_task"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to execute task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task execution failed: {str(e)}")


class CleanArchCompleteTaskUseCase:
    """Complete task use case using Clean Architecture."""
    
    def __init__(self):
        self.container = get_container()
        self.task_repository = self.container.get_service(TaskRepository)
    
    async def complete_task(self, task_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a task and store artifacts."""
        try:
            # Update task status to completed
            updates = {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = self.task_repository.update_task(task_id, updates)
            if not success:
                raise OrchestrationError(f"Failed to complete task {task_id}")
            
            # Store artifacts
            artifact_refs = []
            if "detailed_work" in completion_data:
                from .db_integration import ArtifactService
                artifact_service = ArtifactService()
                
                artifact_ref = await artifact_service.store_artifact(
                    task_id=task_id,
                    content=completion_data["detailed_work"],
                    artifact_type=completion_data.get("artifact_type", "general"),
                    metadata={
                        "summary": completion_data.get("summary", ""),
                        "next_action": completion_data.get("next_action", "complete")
                    }
                )
                artifact_refs.append({
                    "id": artifact_ref.artifact_id,
                    "type": artifact_ref.content_type,
                    "path": artifact_ref.path,
                    "size": artifact_ref.size
                })
            
            # Create response object that mimics the expected interface
            class CompletionResponse:
                def __init__(self, data):
                    self.message = data["message"]
                    self.summary = data["summary"]
                    self.artifact_count = data["artifact_count"]
                    self.artifact_references = data["artifact_references"]
                    self.next_action = data["next_action"]
                    self.completion_time = data["completion_time"]
                    self.next_steps = data.get("next_steps", [
                        "Task completed successfully",
                        "Artifacts have been stored for future reference",
                        "Check dependent tasks for new availability"
                    ])
            
            response_data = {
                "message": f"Task {task_id} completed successfully",
                "summary": completion_data.get("summary", "Task completed"),
                "artifact_count": len(artifact_refs),
                "artifact_references": artifact_refs,
                "next_action": completion_data.get("next_action", "complete"),
                "completion_time": updates["completed_at"]
            }
            
            return CompletionResponse(response_data)
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task completion failed: {str(e)}")


# Singleton instances
_task_use_case: Optional[CleanArchTaskUseCase] = None
_execute_use_case: Optional[CleanArchExecuteTaskUseCase] = None
_complete_use_case: Optional[CleanArchCompleteTaskUseCase] = None


async def get_clean_task_use_case() -> CleanArchTaskUseCase:
    """Get Clean Architecture task use case instance."""
    global _task_use_case
    if _task_use_case is None:
        # Ensure DI container is initialized
        from .core_handlers import enable_dependency_injection
        await enable_dependency_injection()
        _task_use_case = CleanArchTaskUseCase()
    return _task_use_case


async def get_clean_execute_use_case() -> CleanArchExecuteTaskUseCase:
    """Get Clean Architecture execute use case instance."""
    global _execute_use_case
    if _execute_use_case is None:
        # Ensure DI container is initialized
        from .core_handlers import enable_dependency_injection
        await enable_dependency_injection()
        _execute_use_case = CleanArchExecuteTaskUseCase()
    return _execute_use_case


async def get_clean_complete_use_case() -> CleanArchCompleteTaskUseCase:
    """Get Clean Architecture complete use case instance."""
    global _complete_use_case
    if _complete_use_case is None:
        # Ensure DI container is initialized
        from .core_handlers import enable_dependency_injection
        await enable_dependency_injection()
        _complete_use_case = CleanArchCompleteTaskUseCase()
    return _complete_use_case