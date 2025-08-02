"""
Generic Task Management Handlers

Handlers for the 5 critical Generic Task Model MCP tools that enable
flexible task creation, modification, deletion, cancellation, and querying.

These handlers implement the foundation for the v2.0.0 Generic Task Model system
with proper MCP JSON-RPC error code compliance.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from mcp import types

# Import the Generic Task models
from ....domain.entities.task import (
    Task, TaskType, TaskStatus, LifecycleStage,
    TaskDependency, DependencyType
)

# Import value objects from domain layer
from ....domain.value_objects.complexity_level import ComplexityLevel
from ....domain.value_objects.specialist_type import SpecialistType

# Import use cases and database integration
from .db_integration import (
    get_generic_task_use_case, 
    get_execute_task_use_case,
    get_complete_task_use_case
)
from ....domain.exceptions import OrchestrationError

# Import MCP error handling system
from ..error_handling import (
    mcp_error_handler, 
    mcp_validation_handler,
    format_mcp_success_response
)

logger = logging.getLogger(__name__)


@mcp_validation_handler(["title", "description"])
@mcp_error_handler(tool_name="orchestrator_create_generic_task", require_auth=True)
async def handle_create_generic_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle creation of a new generic task using Clean Architecture."""
    logger.info(f"Creating generic task: {args.get('title', 'Unknown')}")
    
    # Get use case instance
    use_case = get_generic_task_use_case()
    
    # Create task using use case
    created_task = await use_case.create_task(args)
    
    # Convert task to dict for response
    task_dict = created_task.dict()
    
    # Convert datetime objects to ISO strings for JSON serialization
    for field in ["created_at", "updated_at", "due_date", "started_at", "completed_at", "deleted_at"]:
        if task_dict.get(field):
            task_dict[field] = task_dict[field].isoformat()
    
    # Convert enums to string values
    for field in ["status", "lifecycle_stage", "complexity", "specialist_type", "task_type"]:
        if task_dict.get(field) and hasattr(task_dict[field], 'value'):
            task_dict[field] = task_dict[field].value
    
    # Format success response
    response_data = {
        "task": task_dict,
        "next_steps": [
            "Task is ready for assignment and execution",
            "Use orchestrator_update_task to modify properties",
            "Use orchestrator_query_tasks to find this task later"
        ]
    }
    
    return format_mcp_success_response(
        data=response_data,
        message=f"Generic task '{created_task.title}' created successfully"
    )


@mcp_validation_handler(["task_id"])
@mcp_error_handler(tool_name="orchestrator_update_task", require_auth=True)
async def handle_update_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle updating an existing generic task with validation and lifecycle management."""
    task_id = args.get("task_id")
    logger.info(f"Updating generic task: {task_id}")
    
    # Get use case instance
    use_case = get_generic_task_use_case()
    
    # Create update data from args (excluding task_id)
    update_data = {k: v for k, v in args.items() if k != "task_id"}
    
    # Update task using use case
    updated_task = await use_case.update_task(task_id, update_data)
    
    # Convert task to dict for response
    task_dict = updated_task.dict()
    
    # Convert datetime objects to ISO strings for JSON serialization
    for field in ["created_at", "updated_at", "due_date", "started_at", "completed_at", "deleted_at"]:
        if task_dict.get(field):
            task_dict[field] = task_dict[field].isoformat()
    
    # Convert enums to string values
    for field in ["status", "lifecycle_stage", "complexity", "specialist_type", "task_type"]:
        if task_dict.get(field) and hasattr(task_dict[field], 'value'):
            task_dict[field] = task_dict[field].value
    
    # Format success response
    response_data = {
        "task_id": task_id,
        "updated_task": task_dict,
        "next_steps": [
            "Task has been updated in the database",
            "Use orchestrator_query_tasks to verify changes",
            "Consider updating dependent tasks if needed"
        ]
    }
    
    return format_mcp_success_response(
        data=response_data,
        message=f"Task {task_id} updated successfully"
    )


@mcp_validation_handler(["task_id"])
@mcp_error_handler(tool_name="orchestrator_delete_task", require_auth=True)
async def handle_delete_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle deletion of a generic task with dependency checking and safe removal."""
    task_id = args.get("task_id")
    force = args.get("force", False)
    archive_instead = args.get("archive_instead", True)
    
    logger.info(f"Deleting generic task: {task_id} (force={force}, archive={archive_instead})")
    
    # Get use case instance
    use_case = get_generic_task_use_case()
    
    # Delete task using use case
    deletion_result = await use_case.delete_task(task_id, force, archive_instead)
    
    logger.info(f"Task {task_id} deletion completed: {deletion_result['action_taken']}")
    
    # Format success response
    response_data = {
        "task_id": task_id,
        "action_taken": deletion_result["action_taken"],
        "deletion_result": deletion_result,
        "next_steps": [
            "Task has been processed according to the deletion policy",
            "Check dependent tasks if any were affected",
            "Use orchestrator_query_tasks to verify the task state"
        ]
    }
    
    return format_mcp_success_response(
        data=response_data,
        message=f"Task {task_id} {deletion_result['action_taken']} successfully"
    )


async def handle_cancel_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle cancellation of an in-progress generic task with graceful state management."""
    try:
        # Extract required task_id
        task_id = args.get("task_id")
        if not task_id:
            error_response = {
                "error": "Missing required field: task_id",
                "required": ["task_id"],
                "received": list(args.keys())
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]
        
        reason = args.get("reason", "No reason provided")
        preserve_work = args.get("preserve_work", True)
        
        logger.info(f"Cancelling generic task: {task_id} (preserve_work={preserve_work})")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Cancel task using use case
        cancellation_result = await use_case.cancel_task(task_id, reason, preserve_work)
        
        response = {
            "status": "cancelled",
            "message": f"Task {task_id} cancelled successfully",
            "task_id": task_id,
            "cancellation_result": cancellation_result,
            "next_steps": [
                "Review preserved work artifacts if needed",
                "Check dependent tasks for new availability",
                "Consider rescheduling or recreating task if needed"
            ]
        }
        
        logger.info(f"Task {task_id} cancelled successfully. Reason: {reason}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except OrchestrationError as e:
        error_response = {
            "error": "Task cancellation failed",
            "details": str(e),
            "tool": "orchestrator_cancel_task"
        }
        logger.error(f"Orchestration error cancelling task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
        
    except Exception as e:
        error_response = {
            "error": "Cancellation execution error",
            "details": str(e),
            "tool": "orchestrator_cancel_task"
        }
        logger.error(f"Error cancelling task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_query_tasks(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle querying and filtering generic tasks with advanced search capabilities."""
    try:
        logger.info(f"Querying generic tasks with filters: {list(args.keys())}")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Query tasks using use case
        query_result = await use_case.query_tasks(args)
        
        # Convert task objects to dictionaries for JSON serialization
        tasks_dict = []
        for task in query_result["tasks"]:
            task_dict = task.dict()
            
            # Convert datetime objects to ISO strings
            for field in ["created_at", "updated_at", "due_date", "started_at", "completed_at", "deleted_at"]:
                if task_dict.get(field):
                    task_dict[field] = task_dict[field].isoformat()
            
            # Convert enums to string values
            for field in ["status", "lifecycle_stage", "complexity", "specialist_type", "task_type"]:
                if task_dict.get(field) and hasattr(task_dict[field], 'value'):
                    task_dict[field] = task_dict[field].value
            
            # Handle dependencies and children serialization
            if task_dict.get("dependencies"):
                for dep in task_dict["dependencies"]:
                    if hasattr(dep, 'dict'):
                        dep_dict = dep.dict() if hasattr(dep, 'dict') else dep
                        # Convert enum values in dependencies
                        for dep_field in ["dependency_type", "dependency_status"]:
                            if dep_dict.get(dep_field) and hasattr(dep_dict[dep_field], 'value'):
                                dep_dict[dep_field] = dep_dict[dep_field].value
            
            tasks_dict.append(task_dict)
        
        response = {
            "status": "success",
            "message": f"Found {query_result['pagination']['total_count']} tasks matching query criteria",
            "query_summary": {
                "filters_applied": query_result["filters_applied"],
                "pagination": query_result["pagination"]
            },
            "tasks": tasks_dict,
            "next_steps": [
                "Review the returned tasks",
                "Use orchestrator_update_task to modify any tasks as needed",
                "Use task_id values for further operations"
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except OrchestrationError as e:
        error_response = {
            "error": "Task query failed",
            "details": str(e),
            "tool": "orchestrator_query_tasks"
        }
        logger.error(f"Orchestration error querying tasks: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
        
    except Exception as e:
        error_response = {
            "error": "Query execution error",
            "details": str(e),
            "tool": "orchestrator_query_tasks"
        }
        logger.error(f"Error querying tasks: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_execute_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle executing a task by providing specialist context and instructions."""
    try:
        # Extract required task_id
        task_id = args.get("task_id")
        if not task_id:
            error_response = {
                "error": "Missing required field: task_id",
                "required": ["task_id"],
                "received": list(args.keys())
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]

        logger.info(f"Executing task: {task_id}")

        # Get use case instance
        use_case = get_execute_task_use_case()

        # Get execution context using use case
        execution_context = await use_case.get_task_execution_context(task_id)

        # Convert response to dict for serialization
        response = {
            "status": "ready_for_execution",
            "task_id": task_id,
            "task_title": execution_context.task_title,
            "task_description": execution_context.task_description,
            "specialist_type": execution_context.specialist_type,
            "specialist_context": execution_context.specialist_context,
            "specialist_prompts": execution_context.specialist_prompts,
            "execution_instructions": execution_context.execution_instructions,
            "dependencies_completed": execution_context.dependencies_completed,
            "estimated_effort": execution_context.estimated_effort,
            "next_steps": execution_context.next_steps
        }

        logger.info(f"Task {task_id} ready for execution")

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except OrchestrationError as e:
        error_response = {
            "error": "Task execution failed",
            "details": str(e),
            "tool": "orchestrator_execute_task"
        }
        logger.error(f"Orchestration error executing task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]

    except Exception as e:
        error_response = {
            "error": "Execution setup error",
            "details": str(e),
            "tool": "orchestrator_execute_task"
        }
        logger.error(f"Error setting up task execution: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_complete_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle completing a task with artifact storage to prevent context limit issues."""
    try:
        # Extract required fields
        task_id = args.get("task_id")
        if not task_id:
            error_response = {
                "error": "Missing required field: task_id",
                "required": ["task_id"],
                "received": list(args.keys())
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]

        # Validate required completion fields
        required_fields = ["summary", "detailed_work", "next_action"]
        missing_fields = [field for field in required_fields if not args.get(field)]
        if missing_fields:
            error_response = {
                "error": f"Missing required fields: {missing_fields}",
                "required": required_fields,
                "received": list(args.keys())
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]

        logger.info(f"Completing task: {task_id}")

        # Get use case instance
        use_case = get_complete_task_use_case()

        # Complete task using use case
        completion_response = await use_case.complete_task_with_artifacts(task_id, args)

        # Convert response to dict for serialization
        response = {
            "status": "success",
            "task_id": task_id,
            "message": completion_response.message,
            "summary": completion_response.summary,
            "artifact_count": completion_response.artifact_count,
            "artifact_references": completion_response.artifact_references,
            "next_action": completion_response.next_action,
            "completion_time": completion_response.completion_time,
            "next_steps": completion_response.next_steps
        }

        logger.info(f"Task {task_id} completed successfully")

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]

    except OrchestrationError as e:
        error_response = {
            "error": "Task completion failed",
            "details": str(e),
            "tool": "orchestrator_complete_task"
        }
        logger.error(f"Orchestration error completing task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]

    except Exception as e:
        error_response = {
            "error": "Completion execution error",
            "details": str(e),
            "tool": "orchestrator_complete_task"
        }
        logger.error(f"Error completing task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]