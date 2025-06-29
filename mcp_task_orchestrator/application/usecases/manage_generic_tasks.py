"""
Generic Task Management Use Cases

Clean Architecture use cases for managing Generic Tasks.
Implements the business logic for CRUD operations on Generic Tasks.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from ...domain.exceptions import OrchestrationError
from ...orchestrator.generic_models import (
    GenericTask, TaskType, TaskStatus, LifecycleStage,
    TaskDependency, DependencyType, DependencyStatus, TaskAttribute, AttributeType
)
from ...orchestrator.models import ComplexityLevel, SpecialistType
from ...db.generic_repository import GenericTaskRepository

logger = logging.getLogger(__name__)


class GenericTaskUseCase:
    """Use case for managing Generic Tasks with Clean Architecture patterns."""
    
    def __init__(self, repository: GenericTaskRepository):
        """
        Initialize the use case with a repository.
        
        Args:
            repository: Generic task repository for data operations
        """
        self.repository = repository
    
    async def create_task(self, task_data: Dict[str, Any]) -> GenericTask:
        """
        Create a new generic task.
        
        Args:
            task_data: Dictionary containing task creation data
            
        Returns:
            Created GenericTask instance
            
        Raises:
            OrchestrationError: If task creation fails
        """
        try:
            # Generate unique task ID
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            
            # Extract and validate required fields
            title = task_data.get("title")
            description = task_data.get("description")
            
            if not title or not description:
                raise OrchestrationError("Title and description are required")
            
            # Extract optional fields with defaults
            task_type = TaskType(task_data.get("task_type", "standard"))
            parent_task_id = task_data.get("parent_task_id")
            complexity = ComplexityLevel(task_data.get("complexity", "moderate"))
            specialist_type = None
            if task_data.get("specialist_type"):
                specialist_type = SpecialistType(task_data.get("specialist_type"))
            
            # Build hierarchy path
            hierarchy_path = f"/{task_id}"
            hierarchy_level = 0
            
            if parent_task_id:
                # Get parent task to build proper hierarchy
                parent_task = await self.repository.get_task(parent_task_id)
                if parent_task:
                    hierarchy_path = f"{parent_task.hierarchy_path}/{task_id}"
                    hierarchy_level = parent_task.hierarchy_level + 1
                else:
                    raise OrchestrationError(f"Parent task {parent_task_id} not found")
            
            # Parse due date if provided
            due_date = None
            if task_data.get("due_date"):
                try:
                    due_date = datetime.fromisoformat(task_data["due_date"].replace('Z', '+00:00'))
                except ValueError:
                    raise OrchestrationError("Invalid due_date format. Use ISO 8601 format.")
            
            # Create the GenericTask instance
            task_kwargs = {
                "task_id": task_id,
                "parent_task_id": parent_task_id,
                "title": title,
                "description": description,
                "task_type": task_type,
                "hierarchy_path": hierarchy_path,
                "hierarchy_level": hierarchy_level,
                "status": TaskStatus.PENDING,
                "lifecycle_stage": LifecycleStage.CREATED,
                "complexity": complexity,
                "specialist_type": specialist_type,
                "due_date": due_date,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Only add optional fields if provided (let Pydantic handle defaults)
            if task_data.get("estimated_effort") is not None:
                task_kwargs["estimated_effort"] = task_data["estimated_effort"]
            if task_data.get("context") is not None:
                task_kwargs["context"] = task_data["context"]
            if task_data.get("configuration") is not None:
                task_kwargs["configuration"] = task_data["configuration"]
            
            generic_task = GenericTask(**task_kwargs)
            
            # Add dependencies if provided
            dependencies = task_data.get("dependencies", [])
            for dep_task_id in dependencies:
                dependency = TaskDependency(
                    dependent_task_id=task_id,
                    prerequisite_task_id=dep_task_id,
                    dependency_type=DependencyType.COMPLETION,
                    is_mandatory=True
                )
                generic_task.dependencies.append(dependency)
            
            # Create task in database
            created_task = await self.repository.create_task(generic_task)
            
            logger.info(f"Generic task created successfully: {task_id}")
            return created_task
            
        except Exception as e:
            logger.error(f"Error creating generic task: {e}")
            raise OrchestrationError(f"Failed to create task: {str(e)}")
    
    async def query_tasks(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query tasks with advanced filtering and pagination.
        
        Args:
            filters: Dictionary containing query filters
            
        Returns:
            Dictionary with query results and metadata
        """
        try:
            # Extract and validate parameters
            status_filter = filters.get("status", [])
            task_type_filter = filters.get("task_type", [])
            specialist_type_filter = filters.get("specialist_type", [])
            parent_task_id = filters.get("parent_task_id")
            complexity_filter = filters.get("complexity", [])
            search_text = filters.get("search_text")
            
            # Date filtering
            created_after = None
            created_before = None
            
            if filters.get("created_after"):
                try:
                    created_after = datetime.fromisoformat(filters["created_after"].replace('Z', '+00:00'))
                except ValueError:
                    raise OrchestrationError("Invalid created_after date format")
            
            if filters.get("created_before"):
                try:
                    created_before = datetime.fromisoformat(filters["created_before"].replace('Z', '+00:00'))
                except ValueError:
                    raise OrchestrationError("Invalid created_before date format")
            
            # Pagination
            limit = min(filters.get("limit", 100), 1000)  # Cap at 1000
            offset = max(filters.get("offset", 0), 0)
            
            # Options
            include_children = filters.get("include_children", False)
            include_artifacts = filters.get("include_artifacts", False)
            
            # Build query filters
            query_filters = {}
            if status_filter:
                query_filters["status"] = status_filter
            if task_type_filter:
                query_filters["task_type"] = task_type_filter
            if specialist_type_filter:
                query_filters["specialist_type"] = specialist_type_filter
            if parent_task_id:
                query_filters["parent_task_id"] = parent_task_id
            if complexity_filter:
                query_filters["complexity"] = complexity_filter
            if search_text:
                query_filters["search_text"] = search_text
            if created_after:
                query_filters["created_after"] = created_after
            if created_before:
                query_filters["created_before"] = created_before
            
            # Query database
            tasks = await self.repository.query_tasks(
                query_filters, limit=limit, offset=offset
            )
            
            # For simplicity, return the count of returned tasks
            # TODO: Implement proper total count in repository layer
            total_count = len(tasks)
            
            return {
                "tasks": tasks,
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(tasks),
                    "limit": limit,
                    "offset": offset
                },
                "filters_applied": {
                    "status": status_filter if status_filter else "all",
                    "task_type": task_type_filter if task_type_filter else "all",
                    "specialist_type": specialist_type_filter if specialist_type_filter else "all",
                    "parent_task_id": parent_task_id,
                    "complexity": complexity_filter if complexity_filter else "all",
                    "search_text": search_text,
                    "created_after": filters.get("created_after"),
                    "created_before": filters.get("created_before")
                }
            }
            
        except Exception as e:
            logger.error(f"Error querying tasks: {e}")
            raise OrchestrationError(f"Failed to query tasks: {str(e)}")
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> GenericTask:
        """
        Update an existing task.
        
        Args:
            task_id: ID of task to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated GenericTask instance
        """
        try:
            # Get existing task
            existing_task = await self.repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Track what fields are being updated
            updated_fields = []
            
            # Update basic fields
            if "title" in update_data and update_data["title"]:
                existing_task.title = update_data["title"]
                updated_fields.append("title")
            
            if "description" in update_data and update_data["description"]:
                existing_task.description = update_data["description"]
                updated_fields.append("description")
            
            # Update status with lifecycle synchronization
            if "status" in update_data:
                new_status = TaskStatus(update_data["status"])
                if new_status != existing_task.status:
                    existing_task.status = new_status
                    updated_fields.append("status")
                    
                    # Update lifecycle stage based on status
                    lifecycle_mapping = {
                        TaskStatus.PENDING: LifecycleStage.CREATED,
                        TaskStatus.ACTIVE: LifecycleStage.ACTIVE,
                        TaskStatus.IN_PROGRESS: LifecycleStage.ACTIVE,
                        TaskStatus.BLOCKED: LifecycleStage.BLOCKED,
                        TaskStatus.COMPLETED: LifecycleStage.COMPLETED,
                        TaskStatus.FAILED: LifecycleStage.FAILED,
                        TaskStatus.CANCELLED: LifecycleStage.ARCHIVED,
                        TaskStatus.ARCHIVED: LifecycleStage.ARCHIVED
                    }
                    
                    if new_status in lifecycle_mapping:
                        existing_task.lifecycle_stage = lifecycle_mapping[new_status]
                        updated_fields.append("lifecycle_stage")
            
            # Update other fields
            if "specialist_type" in update_data:
                specialist_type_str = update_data["specialist_type"]
                if specialist_type_str:
                    existing_task.specialist_type = SpecialistType(specialist_type_str)
                else:
                    existing_task.specialist_type = None
                updated_fields.append("specialist_type")
            
            if "complexity" in update_data:
                existing_task.complexity = ComplexityLevel(update_data["complexity"])
                updated_fields.append("complexity")
            
            if "estimated_effort" in update_data:
                existing_task.estimated_effort = update_data["estimated_effort"]
                updated_fields.append("estimated_effort")
            
            if "due_date" in update_data:
                due_date_str = update_data["due_date"]
                if due_date_str:
                    try:
                        existing_task.due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    except ValueError:
                        raise OrchestrationError("Invalid due_date format")
                else:
                    existing_task.due_date = None
                updated_fields.append("due_date")
            
            if "context" in update_data:
                if isinstance(update_data["context"], dict):
                    existing_task.context = update_data["context"]
                    updated_fields.append("context")
                else:
                    raise OrchestrationError("Context must be a JSON object")
            
            # Set updated timestamp
            existing_task.updated_at = datetime.now()
            updated_fields.append("updated_at")
            
            # Update in database
            updated_task = await self.repository.update_task(existing_task)
            
            logger.info(f"Task {task_id} updated successfully. Fields: {', '.join(updated_fields)}")
            return updated_task
            
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            raise OrchestrationError(f"Failed to update task: {str(e)}")
    
    async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
        """
        Delete or archive a task.
        
        Args:
            task_id: ID of task to delete
            force: Whether to force deletion despite dependencies
            archive_instead: Whether to archive instead of delete
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Check task exists
            existing_task = await self.repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # TODO: Implement dependency checking when repository methods are available
            # For now, if archive_instead is True and not force, always archive
            if archive_instead and not force:
                # Archive the task
                existing_task.status = TaskStatus.ARCHIVED
                existing_task.lifecycle_stage = LifecycleStage.ARCHIVED
                existing_task.updated_at = datetime.now()
                
                await self.repository.update_task(existing_task)
                
                return {
                    "action_taken": "archived",
                    "task_id": task_id,
                    "reason": "Task archived as requested (dependency checking not yet implemented)"
                }
            
            # Delete the task
            await self.repository.delete_task(task_id)
            
            return {
                "action_taken": "deleted",
                "task_id": task_id,
                "message": "Task deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            raise OrchestrationError(f"Failed to delete task: {str(e)}")
    
    async def cancel_task(self, task_id: str, reason: str = "No reason provided", 
                         preserve_work: bool = True) -> Dict[str, Any]:
        """
        Cancel an in-progress task.
        
        Args:
            task_id: ID of task to cancel
            reason: Reason for cancellation
            preserve_work: Whether to preserve work artifacts
            
        Returns:
            Dictionary with cancellation results
        """
        try:
            # Get existing task
            existing_task = await self.repository.get_task(task_id)
            if not existing_task:
                raise OrchestrationError(f"Task {task_id} not found")
            
            # Check if task can be cancelled
            cancellable_statuses = [TaskStatus.PENDING, TaskStatus.ACTIVE, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED]
            if existing_task.status not in cancellable_statuses:
                raise OrchestrationError(
                    f"Task cannot be cancelled in status '{existing_task.status.value}'. "
                    f"Cancellable statuses: {[s.value for s in cancellable_statuses]}"
                )
            
            # Store previous state
            previous_status = existing_task.status
            
            # Update task status
            existing_task.status = TaskStatus.CANCELLED
            existing_task.lifecycle_stage = LifecycleStage.ARCHIVED
            existing_task.updated_at = datetime.now()
            
            # Add cancellation reason to context
            if not existing_task.context:
                existing_task.context = {}
            existing_task.context["cancellation_reason"] = reason
            existing_task.context["cancelled_at"] = datetime.now().isoformat()
            existing_task.context["work_preserved"] = preserve_work
            
            # Update in database
            await self.repository.update_task(existing_task)
            
            # TODO: Implement work preservation and dependency updates when repository methods are available
            
            return {
                "task_id": task_id,
                "previous_status": previous_status.value if hasattr(previous_status, 'value') else str(previous_status),
                "new_status": "cancelled",
                "reason": reason,
                "work_preserved": preserve_work,
                "message": "Task cancelled successfully"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            raise OrchestrationError(f"Failed to cancel task: {str(e)}")