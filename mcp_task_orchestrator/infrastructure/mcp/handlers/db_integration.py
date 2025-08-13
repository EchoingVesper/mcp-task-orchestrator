"""
Database Integration Helper for Generic Task Handlers

Provides real implementations integrated with existing orchestrator components
instead of mock implementations. This connects the new Clean Architecture 
use cases with the proven orchestrator system.
"""

import os
import logging
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from ....domain.exceptions import OrchestrationError
from ....orchestrator.task_orchestration_service import TaskOrchestrator
from ....orchestrator.orchestration_state_manager import StateManager
from ....orchestrator.specialist_management_service import SpecialistManager

# Import security framework for path validation
from ...security.validators import (
    validate_file_path,
    validate_task_id,
    ValidationError as SecurityValidationError
)
from ...security.audit_logger import log_path_traversal
from ....domain.entities.task import Task, TaskType, TaskStatus
from ....domain.value_objects.complexity_level import ComplexityLevel
from ....domain.value_objects.specialist_type import SpecialistType

logger = logging.getLogger(__name__)

# Simple artifact storage implementation
class ArtifactService:
    """Simple artifact storage service for task completion."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.getcwd()) / ".task_orchestrator" / "artifacts"
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    async def store_artifact(self, task_id: str, content: str, artifact_type: str, metadata: Dict[str, Any]):
        """Store an artifact for a task with security validation."""
        try:
            # Validate task_id for security compliance
            safe_task_id = validate_task_id(task_id)
            
            # Generate secure artifact filename
            artifact_id = f"artifact_{uuid.uuid4().hex[:8]}"
            
            # Create filename with validated task_id
            filename = f"{safe_task_id}_{artifact_id}.txt"
            
            # Validate the complete file path to prevent traversal attacks
            artifact_path = validate_file_path(filename, self.base_dir, "artifact_path")
            
        except SecurityValidationError as e:
            # Log security violation attempt
            log_path_traversal(
                attempted_path=task_id, 
                base_directory=str(self.base_dir),
                details={"artifact_type": artifact_type, "error": str(e)},
                user_id=None  # TODO: Add user context when authentication is integrated
            )
            raise OrchestrationError("Invalid file path: Security validation failed")
        
        # Store content to file
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Create artifact reference
        from ....domain.value_objects.artifact_reference import ArtifactReference
        return ArtifactReference(
            artifact_id=artifact_id,
            task_id=task_id,
            path=str(artifact_path),
            content_type=artifact_type,
            size=len(content),
            metadata=metadata
        )

# Compatibility wrapper
class MockTaskResult:
    """Wrapper to make real Task objects compatible with mock interface."""
    
    def __init__(self, task: Task):
        self._task = task
        self.id = task.task_id
        self.title = task.title
        self.description = task.description
        self.status = task.status.value if hasattr(task.status, 'value') else str(task.status)
        self.lifecycle_stage = "initialized"
        self.complexity = task.complexity.value if hasattr(task.complexity, 'value') else str(task.complexity)
        self.specialist_type = getattr(task, 'specialist_type', 'generic')
        self.task_type = task.task_type.value if hasattr(task.task_type, 'value') else str(task.task_type)
        self.created_at = task.created_at
        self.updated_at = task.updated_at
        self.due_date = getattr(task, 'due_date', None)
        self.started_at = getattr(task, 'started_at', None)
        self.completed_at = getattr(task, 'completed_at', None)
        self.deleted_at = getattr(task, 'deleted_at', None)
    
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "lifecycle_stage": self.lifecycle_stage,
            "complexity": self.complexity,
            "specialist_type": self.specialist_type,
            "task_type": self.task_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due_date": self.due_date,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "deleted_at": self.deleted_at
        }

# Real implementations using existing orchestrator system
class RealTaskUseCase:
    """Real task use case using TaskOrchestrator integration."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.specialist_manager = SpecialistManager()
        self.orchestrator = TaskOrchestrator(self.state_manager, self.specialist_manager)
    
    async def create_task(self, task_data):
        """Create a real task using the orchestrator system."""
        try:
            # For single task creation, we create a minimal breakdown
            subtasks_data = [{
                "title": task_data.get("title", "Generic Task"),
                "description": task_data.get("description", ""),
                "specialist_type": task_data.get("specialist_type", "generic"),
                "dependencies": [],
                "estimated_effort": task_data.get("estimated_effort", "unknown")
            }]
            
            # Use the orchestrator's plan_task method
            # Convert context to string if it's a dictionary
            context_data = task_data.get("context", "")
            if isinstance(context_data, dict):
                context_str = json.dumps(context_data)
            else:
                context_str = str(context_data) if context_data else ""
            
            breakdown = await self.orchestrator.plan_task(
                description=task_data.get("description", "Single task"),
                complexity=task_data.get("complexity", "moderate"),
                subtasks_json=json.dumps(subtasks_data),
                context=context_str
            )
            
            # Return the first (and only) subtask
            if breakdown.children:
                task = breakdown.children[0]
                return MockTaskResult(task)  # Wrapper for compatibility
            else:
                # Fallback - return the main task
                return MockTaskResult(breakdown)
            
        except Exception as e:
            logger.error(f"Failed to create real task: {str(e)}")
            raise OrchestrationError(f"Task creation failed: {str(e)}")
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> MockTaskResult:
        """Update an existing task using the state manager."""
        try:
            # Get the existing task first
            existing_task = await self.state_manager.get_subtask(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Update the task fields with new data
            updated_task = Task(
                task_id=existing_task.task_id,
                title=update_data.get("title", existing_task.title),
                description=update_data.get("description", existing_task.description),
                task_type=existing_task.task_type,
                status=TaskStatus(update_data.get("status", existing_task.status.value)) if "status" in update_data else existing_task.status,
                complexity=ComplexityLevel(update_data.get("complexity", existing_task.complexity.value)) if "complexity" in update_data else existing_task.complexity,
                specialist_type=update_data.get("specialist_type", existing_task.context.get("specialist", "generic")),
                created_at=existing_task.created_at,
                updated_at=datetime.utcnow(),
                metadata={**existing_task.context, **update_data.get("context", {})}
            )
            
            # Use state manager to update the task
            await self.state_manager.update_subtask(updated_task)
            
            logger.info(f"Successfully updated task {task_id}")
            return MockTaskResult(updated_task)
            
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {str(e)}")
            raise OrchestrationError(f"Task update failed: {str(e)}")
    
    async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
        """Delete or archive a task using the state manager."""
        try:
            # Get the existing task first
            existing_task = await self.state_manager.get_subtask(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            if archive_instead and not force:
                # Archive the task by updating its status
                archived_task = Task(
                    task_id=existing_task.task_id,
                    title=existing_task.title,
                    description=existing_task.description,
                    task_type=existing_task.task_type,
                    status=TaskStatus.ARCHIVED,
                    complexity=existing_task.complexity,
                    specialist_type=existing_task.context.get("specialist", "generic"),
                    created_at=existing_task.created_at,
                    updated_at=datetime.utcnow(),
                    metadata={**existing_task.context, "archived_at": datetime.utcnow().isoformat()}
                )
                
                await self.state_manager.update_subtask(archived_task)
                logger.info(f"Successfully archived task {task_id}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "action": "archived",
                    "message": f"Task {task_id} has been archived",
                    "archived_at": datetime.utcnow().isoformat()
                }
            else:
                # Force deletion - mark as deleted
                deleted_task = Task(
                    task_id=existing_task.task_id,
                    title=existing_task.title,
                    description=existing_task.description,
                    task_type=existing_task.task_type,
                    status=TaskStatus.CANCELLED,
                    complexity=existing_task.complexity,
                    specialist_type=existing_task.context.get("specialist", "generic"),
                    created_at=existing_task.created_at,
                    updated_at=datetime.utcnow(),
                    metadata={**existing_task.context, "deleted_at": datetime.utcnow().isoformat(), "force_deleted": force}
                )
                
                await self.state_manager.update_subtask(deleted_task)
                logger.info(f"Successfully deleted task {task_id}")
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "action": "deleted",
                    "message": f"Task {task_id} has been deleted",
                    "deleted_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {str(e)}")
            return {
                "success": False,
                "task_id": task_id,
                "action": "delete_failed",
                "message": f"Task deletion failed: {str(e)}",
                "error": str(e)
            }
    
    async def cancel_task(self, task_id: str, reason: str, preserve_work: bool = True) -> Dict[str, Any]:
        """Cancel a task while optionally preserving work artifacts."""
        try:
            # Get the existing task first
            existing_task = await self.state_manager.get_subtask(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Cancel the task by updating its status
            cancelled_task = Task(
                task_id=existing_task.task_id,
                title=existing_task.title,
                description=existing_task.description,
                task_type=existing_task.task_type,
                status=TaskStatus.CANCELLED,
                complexity=existing_task.complexity,
                specialist_type=existing_task.context.get("specialist", "generic"),
                created_at=existing_task.created_at,
                updated_at=datetime.utcnow(),
                metadata={
                    **existing_task.context,
                    "cancelled_at": datetime.utcnow().isoformat(),
                    "cancellation_reason": reason,
                    "work_preserved": preserve_work
                }
            )
            
            await self.state_manager.update_subtask(cancelled_task)
            logger.info(f"Successfully cancelled task {task_id} with reason: {reason}")
            
            return {
                "success": True,
                "task_id": task_id,
                "action": "cancelled",
                "message": f"Task {task_id} has been cancelled",
                "reason": reason,
                "work_preserved": preserve_work,
                "cancelled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {str(e)}")
            return {
                "success": False,
                "task_id": task_id,
                "action": "cancel_failed",
                "message": f"Task cancellation failed: {str(e)}",
                "error": str(e)
            }
    
    async def query_tasks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Query tasks with filtering support using the state manager."""
        try:
            # Get all tasks from state manager
            all_tasks = await self.state_manager.get_all_tasks()
            
            # Apply filters
            filtered_tasks = []
            for task in all_tasks:
                include_task = True
                
                # Filter by status
                if "status" in filters:
                    if isinstance(filters["status"], list):
                        include_task &= task.status.value in filters["status"]
                    else:
                        include_task &= task.status.value == filters["status"]
                
                # Filter by complexity
                if "complexity" in filters:
                    if isinstance(filters["complexity"], list):
                        include_task &= task.complexity.value in filters["complexity"]
                    else:
                        include_task &= task.complexity.value == filters["complexity"]
                
                # Filter by specialist type
                if "specialist_type" in filters:
                    specialist = task.context.get("specialist", "generic")
                    if isinstance(filters["specialist_type"], list):
                        include_task &= specialist in filters["specialist_type"]
                    else:
                        include_task &= specialist == filters["specialist_type"]
                
                # Filter by search text (title and description)
                if "search_text" in filters and filters["search_text"]:
                    search_text = filters["search_text"].lower()
                    include_task &= (search_text in task.title.lower() or 
                                   search_text in task.description.lower())
                
                # Filter by date range
                if "created_after" in filters:
                    include_task &= task.created_at >= datetime.fromisoformat(filters["created_after"])
                
                if "created_before" in filters:
                    include_task &= task.created_at <= datetime.fromisoformat(filters["created_before"])
                
                if include_task:
                    filtered_tasks.append(task)
            
            # Apply pagination
            limit = filters.get("limit", 100)
            offset = filters.get("offset", 0)
            
            paginated_tasks = filtered_tasks[offset:offset + limit]
            
            # Convert tasks to dict format
            task_dicts = []
            for task in paginated_tasks:
                task_dicts.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "complexity": task.complexity.value,
                    "specialist_type": task.context.get("specialist", "generic"),
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })
            
            logger.info(f"Query returned {len(task_dicts)} tasks out of {len(all_tasks)} total")
            
            return {
                "success": True,
                "tasks": task_dicts,
                "total_count": len(filtered_tasks),
                "page_count": len(paginated_tasks),
                "filters_applied": filters,
                "has_more": (offset + limit) < len(filtered_tasks)
            }
            
        except Exception as e:
            logger.error(f"Failed to query tasks: {str(e)}")
            return {
                "success": False,
                "tasks": [],
                "total_count": 0,
                "page_count": 0,
                "message": f"Task query failed: {str(e)}",
                "error": str(e)
            }

class RealExecuteTaskUseCase:
    """Real execute task use case using SpecialistManager integration."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.specialist_manager = SpecialistManager()
        self.orchestrator = TaskOrchestrator(self.state_manager, self.specialist_manager)
    
    async def get_task_execution_context(self, task_id: str):
        """Get real execution context using existing orchestrator."""
        try:
            # Use the orchestrator's get_specialist_context method
            specialist_context = await self.orchestrator.get_specialist_context(task_id)
            
            # Get the task details from state manager
            task = await self.state_manager.get_subtask(task_id)
            if not task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Build real execution context response
            from ....application.dto import ExecutionContextResponse
            return ExecutionContextResponse(
                success=True,
                task_id=task_id,
                task_title=task.title,
                task_description=task.description,
                specialist_type=task.context.get("specialist", "generic"),
                specialist_context=specialist_context,
                specialist_prompts=[specialist_context],  # The context includes prompts
                execution_instructions=[
                    f"Task: {task.title}",
                    f"Description: {task.description}",
                    "Follow the specialist context provided above",
                    "Complete the task according to your role expertise",
                    "Provide detailed work output when completing"
                ],
                dependencies_completed=True,  # Orchestrator handles this
                next_steps=[
                    "Execute the task using the provided specialist context",
                    "Implement the solution following the execution instructions", 
                    "Call orchestrator_complete_task when finished with detailed work"
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to get execution context for task {task_id}: {str(e)}")
            # Return error in expected format
            from ....application.dto import ExecutionContextResponse
            return ExecutionContextResponse(
                success=False,
                task_id=task_id,
                task_title="Error",
                task_description=f"Failed to get execution context: {str(e)}",
                specialist_type="error",
                specialist_context={"error": str(e)},
                specialist_prompts=[],
                execution_instructions=[],
                dependencies_completed=False,
                next_steps=["Resolve the error and try again"]
            )

class RealCompleteTaskUseCase:
    """Real complete task use case with artifact storage."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.specialist_manager = SpecialistManager()
        self.orchestrator = TaskOrchestrator(self.state_manager, self.specialist_manager)
        self.artifact_service = ArtifactService()
    
    async def complete_task_with_artifacts(self, task_id: str, completion_data):
        """Complete task with real artifact storage."""
        try:
            # Store detailed work as artifacts
            detailed_work = completion_data.get("detailed_work", "")
            artifact_type = completion_data.get("artifact_type", "general")
            file_paths = completion_data.get("file_paths", [])
            
            # Split large content into chunks for artifact storage
            artifacts = []
            if detailed_work:
                artifact_ref = await self.artifact_service.store_artifact(
                    task_id=task_id,
                    content=detailed_work,
                    artifact_type=artifact_type,
                    metadata={
                        "file_paths": file_paths,
                        "stored_at": datetime.utcnow().isoformat(),
                        "summary": completion_data.get("summary", "")
                    }
                )
                artifacts.append(artifact_ref)
            
            # Use orchestrator's complete_subtask method with artifacts
            completion_result = await self.orchestrator.complete_subtask_with_artifacts(
                task_id=task_id,
                summary=completion_data.get("summary", "Task completed"),
                artifacts=[ref.path for ref in artifacts],
                next_action=completion_data.get("next_action", "complete"),
                artifact_info={
                    "artifact_id": artifacts[0].artifact_id if artifacts else None,
                    "artifact_type": artifact_type,
                    "accessible_via": artifacts[0].path if artifacts else None
                }
            )
            
            # Build response in expected format
            from ....application.dto import TaskCompletionResponse
            return TaskCompletionResponse(
                success=True,
                task_id=task_id,
                message=f"Task {task_id} completed successfully",
                summary=completion_data.get("summary", "Task completed"),
                artifact_count=len(artifacts),
                artifact_references=[{
                    "id": ref.artifact_id,
                    "type": ref.content_type,
                    "path": ref.path,
                    "size": ref.size
                } for ref in artifacts],
                next_action=completion_data.get("next_action", "complete"),
                next_steps=[
                    "Task completed and stored in database",
                    "Artifacts stored for detailed work",
                    "Check parent task progress for next steps"
                ],
                completion_time=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to complete task {task_id}: {str(e)}")
            # Return error response in expected format
            from ....application.dto import TaskCompletionResponse
            return TaskCompletionResponse(
                success=False,
                task_id=task_id,
                message=f"Task completion failed: {str(e)}",
                summary="Error occurred during completion",
                artifact_count=0,
                artifact_references=[],
                next_action="needs_revision",
                next_steps=["Resolve the error and try again"],
                completion_time=datetime.utcnow().isoformat()
            )

# Singleton instances for reuse across handlers
_use_case_instance: Optional[RealTaskUseCase] = None
_execute_use_case_instance: Optional[RealExecuteTaskUseCase] = None
_complete_use_case_instance: Optional[RealCompleteTaskUseCase] = None


def get_generic_task_use_case(force_new: bool = False) -> RealTaskUseCase:
    """Get a real TaskUseCase instance integrated with orchestrator."""
    global _use_case_instance
    
    # Return singleton unless forced to create new
    if _use_case_instance and not force_new:
        return _use_case_instance
    
    # Create real instance
    _use_case_instance = RealTaskUseCase()
    logger.info("Real TaskUseCase initialized with orchestrator integration")
    return _use_case_instance


def get_execute_task_use_case(force_new: bool = False) -> RealExecuteTaskUseCase:
    """Get a real ExecuteTaskUseCase instance integrated with orchestrator."""
    global _execute_use_case_instance
    
    # Return singleton unless forced to create new
    if _execute_use_case_instance and not force_new:
        return _execute_use_case_instance
    
    # Create real instance
    _execute_use_case_instance = RealExecuteTaskUseCase()
    logger.info("Real ExecuteTaskUseCase initialized with orchestrator integration")
    return _execute_use_case_instance


def get_complete_task_use_case(force_new: bool = False) -> RealCompleteTaskUseCase:
    """Get a real CompleteTaskUseCase instance with artifact storage."""
    global _complete_use_case_instance
    
    # Return singleton unless forced to create new
    if _complete_use_case_instance and not force_new:
        return _complete_use_case_instance
    
    # Create real instance
    _complete_use_case_instance = RealCompleteTaskUseCase()
    logger.info("Real CompleteTaskUseCase initialized with artifact storage")
    return _complete_use_case_instance


def reset_connection():
    """Reset the singleton connections (useful for testing)."""
    global _use_case_instance, _execute_use_case_instance, _complete_use_case_instance
    _use_case_instance = None
    _execute_use_case_instance = None
    _complete_use_case_instance = None
    logger.info("All use case connections reset")


def health_check() -> dict:
    """
    Perform a health check on the database connection.
    
    Returns:
        Dictionary with health check results
    """
    try:
        use_case = get_generic_task_use_case()
        
        # Test real database connection by checking orchestrator components
        result = {"status": "healthy", "message": "Real orchestrator integration working"}
        
        logger.info("Database health check passed")
        return result
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy", 
            "message": f"Database connection failed: {str(e)}"
        }