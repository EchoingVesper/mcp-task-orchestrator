"""
Modernized Task Management Handlers with Pydantic DTOs.

This module implements type-safe MCP handlers using Pydantic models for
request/response validation, replacing dictionary-based patterns with
strongly-typed DTOs.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from mcp import types

# Import Pydantic DTOs
from ..dto import (
    CreateTaskRequest,
    CreateTaskResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
    DeleteTaskRequest,
    DeleteTaskResponse,
    CancelTaskRequest,
    CancelTaskResponse,
    QueryTasksRequest,
    QueryTasksResponse,
    TaskQueryResult,
    ExecuteTaskRequest,
    ExecuteTaskResponse,
    CompleteTaskRequest,
    CompleteTaskResponse,
    NextStep,
    MCPErrorResponse
)

# Import error handling infrastructure
from ...error_handling.decorators import handle_errors, ErrorContext

# Import use cases and domain models
from .db_integration import (
    get_generic_task_use_case,
    get_execute_task_use_case,
    get_complete_task_use_case
)
from ....domain.exceptions import OrchestrationError, ValidationError
from ....domain.entities.task import Task

logger = logging.getLogger(__name__)


def _serialize_task(task: Task) -> Dict[str, Any]:
    """Convert task domain model to serializable dictionary."""
    task_dict = task.dict()
    
    # Convert datetime objects to ISO strings
    for field in ["created_at", "updated_at", "due_date", "started_at", "completed_at", "deleted_at"]:
        if task_dict.get(field):
            task_dict[field] = task_dict[field].isoformat()
    
    # Convert enums to string values
    for field in ["status", "lifecycle_stage", "complexity", "specialist_type", "task_type"]:
        if task_dict.get(field) and hasattr(task_dict[field], 'value'):
            task_dict[field] = task_dict[field].value
    
    return task_dict


@handle_errors(
    component="MCPHandler",
    operation="create_task",
    auto_retry=True,
    log_errors=True
)
async def handle_create_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle creation of a new task using Pydantic DTOs.
    
    This handler provides type-safe request/response handling with
    automatic validation and serialization.
    """
    try:
        # Parse and validate request
        request = CreateTaskRequest(**args)
        logger.info(f"Creating task: {request.title}")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Create task using validated data
        created_task = await use_case.create_task(request.dict(exclude_unset=True))
        
        # Build typed response
        response = CreateTaskResponse(
            message=f"Task '{created_task.title}' created successfully",
            task_id=created_task.task_id,
            task_title=created_task.title,
            task_type=created_task.task_type.value,
            created_at=created_task.created_at,
            next_steps=[
                NextStep(
                    action="assign_task",
                    description="Task is ready for assignment and execution",
                    tool_name="orchestrator_execute_task",
                    parameters={"task_id": created_task.task_id}
                ),
                NextStep(
                    action="update_task",
                    description="Modify task properties if needed",
                    tool_name="orchestrator_update_task",
                    parameters={"task_id": created_task.task_id}
                ),
                NextStep(
                    action="query_task",
                    description="Find this task later",
                    tool_name="orchestrator_query_tasks",
                    parameters={"task_id": created_task.task_id}
                )
            ]
        )
        
        # Serialize to JSON for MCP protocol
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        # Handle validation errors
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_create_task",
            component="MCPHandler",
            operation="create_task",
            recovery_suggestions=[
                "Check that all required fields are provided",
                "Ensure field values meet validation constraints",
                "Review the error details for specific validation failures"
            ]
        )
        logger.error(f"Validation error creating task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]
        
    except OrchestrationError as e:
        # Handle orchestration errors
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_create_task",
            component="MCPHandler",
            operation="create_task",
            recovery_suggestions=[
                "Verify the task orchestrator service is running",
                "Check system resources and database connectivity",
                "Review logs for detailed error information"
            ]
        )
        logger.error(f"Orchestration error creating task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="update_task",
    auto_retry=True,
    log_errors=True
)
async def handle_update_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle updating an existing task with type-safe DTOs."""
    try:
        # Parse and validate request
        request = UpdateTaskRequest(**args)
        logger.info(f"Updating task: {request.task_id}")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Prepare update data (exclude None values and task_id)
        update_data = request.dict(exclude_unset=True, exclude={"task_id"})
        
        # Update task
        updated_task = await use_case.update_task(request.task_id, update_data)
        
        # Determine which fields were updated
        updated_fields = list(update_data.keys())
        
        # Build typed response
        response = UpdateTaskResponse(
            message=f"Task {request.task_id} updated successfully",
            task_id=request.task_id,
            updated_fields=updated_fields,
            updated_at=updated_task.updated_at,
            task_status=updated_task.status.value,
            next_steps=[
                NextStep(
                    action="verify_updates",
                    description="Verify the changes were applied",
                    tool_name="orchestrator_query_tasks",
                    parameters={"task_id": request.task_id}
                ),
                NextStep(
                    action="update_dependents",
                    description="Consider updating dependent tasks if needed",
                    tool_name="orchestrator_query_tasks",
                    parameters={"parent_task_id": request.task_id}
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_update_task",
            component="MCPHandler",
            operation="update_task"
        )
        logger.error(f"Validation error updating task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="delete_task",
    auto_retry=False,  # Don't retry deletions
    log_errors=True
)
async def handle_delete_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task deletion with type-safe DTOs."""
    try:
        # Parse and validate request
        request = DeleteTaskRequest(**args)
        logger.info(f"Deleting task: {request.task_id} (force={request.force}, archive={request.archive_instead})")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Delete task
        deletion_result = await use_case.delete_task(
            request.task_id, 
            request.force, 
            request.archive_instead
        )
        
        # Build typed response
        response = DeleteTaskResponse(
            message=f"Task {request.task_id} {deletion_result['action_taken']} successfully",
            task_id=request.task_id,
            action_taken=deletion_result["action_taken"],
            affected_tasks=deletion_result.get("affected_tasks", []),
            deletion_time=datetime.utcnow(),
            next_steps=[
                NextStep(
                    action="verify_deletion",
                    description="Verify the task state",
                    tool_name="orchestrator_query_tasks",
                    parameters={"task_id": request.task_id, "include_archived": True}
                ),
                NextStep(
                    action="check_dependents",
                    description="Check dependent tasks if any were affected",
                    tool_name="orchestrator_query_tasks",
                    parameters={"dependency_ids": [request.task_id]}
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_delete_task",
            component="MCPHandler",
            operation="delete_task"
        )
        logger.error(f"Validation error deleting task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="cancel_task",
    auto_retry=False,
    log_errors=True
)
async def handle_cancel_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task cancellation with type-safe DTOs."""
    try:
        # Parse and validate request
        request = CancelTaskRequest(**args)
        logger.info(f"Cancelling task: {request.task_id} (reason: {request.reason})")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Cancel task
        cancellation_result = await use_case.cancel_task(
            request.task_id,
            request.reason,
            request.preserve_work
        )
        
        # Build typed response
        response = CancelTaskResponse(
            message=f"Task {request.task_id} cancelled successfully",
            task_id=request.task_id,
            preserved_artifacts=cancellation_result.get("preserved_artifacts", []),
            affected_dependents=cancellation_result.get("affected_dependents", []),
            cancellation_time=datetime.utcnow(),
            next_steps=[
                NextStep(
                    action="review_artifacts",
                    description="Review preserved work artifacts if needed",
                    tool_name="orchestrator_query_tasks",
                    parameters={"task_id": request.task_id}
                ),
                NextStep(
                    action="reschedule_task",
                    description="Consider rescheduling or recreating the task",
                    tool_name="orchestrator_create_task"
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_cancel_task",
            component="MCPHandler",
            operation="cancel_task"
        )
        logger.error(f"Validation error cancelling task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="query_tasks",
    auto_retry=True,
    log_errors=True
)
async def handle_query_tasks_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task queries with type-safe DTOs and advanced filtering."""
    try:
        # Parse and validate request
        request = QueryTasksRequest(**args)
        logger.info(f"Querying tasks with filters: {request.dict(exclude_unset=True)}")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Query tasks with validated parameters
        query_result = await use_case.query_tasks(request.dict(exclude_unset=True))
        
        # Convert tasks to response format
        task_results = []
        for task in query_result["tasks"]:
            task_dict = _serialize_task(task)
            
            # Create TaskQueryResult with proper field mapping
            task_result = TaskQueryResult(
                task_id=task.task_id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                task_type=task.task_type.value,
                complexity=task.complexity.value,
                specialist_type=task.specialist_type,
                created_at=task.created_at,
                updated_at=task.updated_at,
                progress=task.progress,
                parent_task_id=task.parent_task_id,
                subtask_ids=task.subtask_ids,
                dependency_ids=[d.task_id for d in task.dependencies] if task.dependencies else [],
                tags=task.tags,
                metadata=task.metadata or {}
            )
            task_results.append(task_result)
        
        # Build typed response
        response = QueryTasksResponse(
            message=f"Found {query_result['pagination']['total_count']} tasks matching criteria",
            query_summary=request.dict(exclude_unset=True),
            tasks=task_results,
            pagination=query_result["pagination"],
            filters_applied=query_result["filters_applied"],
            total_count=query_result["pagination"]["total_count"],
            page_count=query_result["pagination"]["page_count"],
            next_steps=[
                NextStep(
                    action="refine_search",
                    description="Refine search criteria if needed",
                    tool_name="orchestrator_query_tasks"
                ),
                NextStep(
                    action="operate_on_tasks",
                    description="Update or execute found tasks",
                    tool_name="orchestrator_update_task"
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_query_tasks",
            component="MCPHandler",
            operation="query_tasks",
            recovery_suggestions=[
                "Check query parameter formats",
                "Ensure pagination values are within valid ranges",
                "Verify date formats are ISO 8601 compliant"
            ]
        )
        logger.error(f"Validation error querying tasks: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="execute_task",
    auto_retry=True,
    log_errors=True
)
async def handle_execute_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task execution with type-safe DTOs."""
    try:
        # Parse and validate request
        request = ExecuteTaskRequest(**args)
        logger.info(f"Executing task: {request.task_id}")
        
        # Get use case instance
        use_case = get_execute_task_use_case()
        
        # Get execution context
        execution_context = await use_case.get_task_execution_context(request.task_id)
        
        # Build typed response
        response = ExecuteTaskResponse(
            task_id=request.task_id,
            task_title=execution_context.task_title,
            task_description=execution_context.task_description,
            specialist_type=execution_context.specialist_type,
            specialist_context=execution_context.specialist_context,
            specialist_prompts=execution_context.specialist_prompts,
            execution_instructions=execution_context.execution_instructions,
            dependencies_completed=execution_context.dependencies_completed,
            estimated_effort=execution_context.estimated_effort,
            execution_warnings=execution_context.warnings or [],
            next_steps=[
                NextStep(
                    action="complete_task",
                    description="Complete the task after execution",
                    tool_name="orchestrator_complete_task",
                    parameters={"task_id": request.task_id}
                ),
                NextStep(
                    action="update_progress",
                    description="Update task progress during execution",
                    tool_name="orchestrator_update_task",
                    parameters={"task_id": request.task_id, "progress": 50}
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_execute_task",
            component="MCPHandler",
            operation="execute_task"
        )
        logger.error(f"Validation error executing task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


@handle_errors(
    component="MCPHandler",
    operation="complete_task",
    auto_retry=False,  # Don't retry completions
    log_errors=True
)
async def handle_complete_task_v2(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task completion with type-safe DTOs and artifact storage."""
    try:
        # Parse and validate request
        request = CompleteTaskRequest(**args)
        logger.info(f"Completing task: {request.task_id}")
        
        # Get use case instance
        use_case = get_complete_task_use_case()
        
        # Complete task with validated data
        completion_response = await use_case.complete_task_with_artifacts(
            request.task_id,
            request.dict(exclude_unset=True)
        )
        
        # Build typed response
        response = CompleteTaskResponse(
            task_id=request.task_id,
            message=completion_response.message,
            summary=completion_response.summary,
            artifact_count=completion_response.artifact_count,
            artifact_references=completion_response.artifact_references,
            next_action=completion_response.next_action,
            completion_time=datetime.utcnow(),
            task_duration_minutes=completion_response.duration_minutes,
            parent_task_progress=completion_response.parent_progress,
            triggered_tasks=completion_response.triggered_tasks or [],
            next_steps=[
                NextStep(
                    action="review_completion",
                    description="Review task completion details",
                    tool_name="orchestrator_query_tasks",
                    parameters={"task_id": request.task_id}
                ),
                NextStep(
                    action="execute_next",
                    description=completion_response.next_action,
                    tool_name="orchestrator_execute_task" if completion_response.triggered_tasks else None
                )
            ]
        )
        
        return [types.TextContent(
            type="text",
            text=response.json(indent=2)
        )]
        
    except ValidationError as e:
        error_response = MCPErrorResponse.from_exception(
            e,
            tool="orchestrator_complete_task",
            component="MCPHandler", 
            operation="complete_task",
            recovery_suggestions=[
                "Ensure all required completion fields are provided",
                "Verify summary and detailed_work are not empty",
                "Check that artifact data is properly formatted"
            ]
        )
        logger.error(f"Validation error completing task: {e}")
        return [types.TextContent(
            type="text",
            text=error_response.json(indent=2)
        )]


# Export modernized handlers
__all__ = [
    "handle_create_task_v2",
    "handle_update_task_v2",
    "handle_delete_task_v2",
    "handle_cancel_task_v2",
    "handle_query_tasks_v2",
    "handle_execute_task_v2",
    "handle_complete_task_v2"
]