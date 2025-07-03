"""
Generic Task Management Handlers

Handlers for the 5 critical Generic Task Model MCP tools that enable
flexible task creation, modification, deletion, cancellation, and querying.

These handlers implement the foundation for the v2.0.0 Generic Task Model system.
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

# Import use case and database integration
from .db_integration import get_generic_task_use_case
from ....domain.exceptions import OrchestrationError

logger = logging.getLogger(__name__)


async def handle_create_generic_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle creation of a new generic task using Clean Architecture."""
    try:
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
        
        response = {
            "status": "success",
            "message": f"Generic task '{created_task.title}' created successfully",
            "task": task_dict,
            "next_steps": [
                "Task is ready for assignment and execution",
                "Use orchestrator_update_task to modify properties",
                "Use orchestrator_query_tasks to find this task later"
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except OrchestrationError as e:
        error_response = {
            "error": "Task creation failed",
            "details": str(e),
            "tool": "orchestrator_create_generic_task"
        }
        logger.error(f"Orchestration error creating task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
        
    except Exception as e:
        error_response = {
            "error": "Internal error",
            "details": str(e),
            "tool": "orchestrator_create_generic_task"
        }
        logger.error(f"Unexpected error creating generic task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_update_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle updating an existing generic task with validation and lifecycle management."""
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
        
        response = {
            "status": "success",
            "message": f"Task {task_id} updated successfully",
            "task_id": task_id,
            "updated_task": task_dict,
            "next_steps": [
                "Task has been updated in the database",
                "Use orchestrator_query_tasks to verify changes",
                "Consider updating dependent tasks if needed"
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except OrchestrationError as e:
        error_response = {
            "error": "Task update failed",
            "details": str(e),
            "tool": "orchestrator_update_task"
        }
        logger.error(f"Orchestration error updating task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
        
    except Exception as e:
        error_response = {
            "error": "Update execution error",
            "details": str(e),
            "tool": "orchestrator_update_task"
        }
        logger.error(f"Error updating task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_delete_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle deletion of a generic task with dependency checking and safe removal."""
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
        
        force = args.get("force", False)
        archive_instead = args.get("archive_instead", True)
        
        logger.info(f"Deleting generic task: {task_id} (force={force}, archive={archive_instead})")
        
        # Get use case instance
        use_case = get_generic_task_use_case()
        
        # Delete task using use case
        deletion_result = await use_case.delete_task(task_id, force, archive_instead)
        
        response = {
            "status": "success",
            "message": f"Task {task_id} {deletion_result['action_taken']} successfully",
            "task_id": task_id,
            "action_taken": deletion_result["action_taken"],
            "deletion_result": deletion_result,
            "next_steps": [
                "Task has been processed according to the deletion policy",
                "Check dependent tasks if any were affected",
                "Use orchestrator_query_tasks to verify the task state"
            ]
        }
        
        logger.info(f"Task {task_id} deletion completed: {deletion_result['action_taken']}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except OrchestrationError as e:
        error_response = {
            "error": "Task deletion failed",
            "details": str(e),
            "tool": "orchestrator_delete_task"
        }
        logger.error(f"Orchestration error deleting task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
        
    except Exception as e:
        error_response = {
            "error": "Deletion execution error",
            "details": str(e),
            "tool": "orchestrator_delete_task"
        }
        logger.error(f"Error deleting task: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


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