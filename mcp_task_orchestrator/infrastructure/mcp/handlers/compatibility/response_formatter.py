"""
Unified response formatting for all use case methods.

Ensures consistent JSON-serializable dict structures across all operations,
eliminating the need for MockTaskResult and similar wrapper classes.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from .serialization import SerializationValidator

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Unified response formatting for all use case methods."""
    
    @staticmethod
    def format_task_dict(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format a single task dictionary to ensure JSON serialization."""
        # Start with base task data
        formatted_task = {
            "task_id": str(task_data.get("id", task_data.get("task_id", ""))),
            "title": str(task_data.get("title", "")),
            "description": str(task_data.get("description", "")),
            "status": str(task_data.get("status", "pending")),
            "task_type": str(task_data.get("type", task_data.get("task_type", "standard"))),
        }
        
        # Handle metadata - could be string (JSON) or dict
        metadata_raw = task_data.get("metadata", {})
        if isinstance(metadata_raw, str):
            try:
                metadata = json.loads(metadata_raw) if metadata_raw else {}
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in metadata for task {formatted_task['task_id']}")
                metadata = {}
        else:
            metadata = metadata_raw if metadata_raw else {}
        
        # Extract metadata fields with defaults
        formatted_task.update({
            "complexity": str(metadata.get("complexity", "moderate")),
            "specialist_type": str(metadata.get("specialist_type", "generic")),
            "estimated_effort": metadata.get("estimated_effort"),
            "context": metadata.get("context", {}),
            "dependencies": metadata.get("dependencies", [])
        })
        
        # Add timestamps
        timestamp_fields = ["created_at", "updated_at", "completed_at", "started_at", "deleted_at"]
        for field in timestamp_fields:
            if field in task_data:
                formatted_task[field] = task_data[field]
        
        # Handle special fields
        if "due_date" in task_data:
            formatted_task["due_date"] = task_data["due_date"]
        if "parent_task_id" in task_data:
            formatted_task["parent_task_id"] = task_data["parent_task_id"]
        if "session_id" in task_data:
            formatted_task["session_id"] = task_data["session_id"]
        
        # Ensure JSON serialization
        return SerializationValidator.ensure_serializable(formatted_task)
    
    @staticmethod
    def format_create_response(task_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for create_task operations."""
        formatted_task = ResponseFormatter.format_task_dict(task_dict)
        
        response = {
            "success": True,
            "task_id": formatted_task["task_id"],
            "title": formatted_task["title"],
            "description": formatted_task["description"],
            "status": formatted_task["status"],
            "task_type": formatted_task["task_type"],
            "complexity": formatted_task["complexity"],
            "specialist_type": formatted_task["specialist_type"],
            "created_at": formatted_task.get("created_at"),
            "message": f"Task created successfully with ID: {formatted_task['task_id']}",
            "operation": "create_task",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return SerializationValidator.ensure_serializable(response)
    
    @staticmethod
    def format_update_response(task_dict: Dict[str, Any], changes: List[str]) -> Dict[str, Any]:
        """Format response for update_task operations."""
        formatted_task = ResponseFormatter.format_task_dict(task_dict)
        
        response = {
            "success": True,
            "task_id": formatted_task["task_id"],
            "title": formatted_task["title"],
            "description": formatted_task["description"],
            "status": formatted_task["status"],
            "task_type": formatted_task["task_type"],
            "complexity": formatted_task["complexity"],
            "specialist_type": formatted_task["specialist_type"],
            "updated_at": formatted_task.get("updated_at"),
            "changes_applied": changes,
            "message": f"Task {formatted_task['task_id']} updated successfully",
            "operation": "update_task",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return SerializationValidator.ensure_serializable(response)
    
    @staticmethod
    def format_query_response(tasks: List[Dict[str, Any]], query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for query_tasks operations."""
        formatted_tasks = [ResponseFormatter.format_task_dict(task) for task in tasks]
        
        response = {
            "success": True,
            "tasks": formatted_tasks,
            "total_count": len(formatted_tasks),
            "page_count": query_context.get("page_count", 1),
            "current_page": query_context.get("current_page", 1),
            "page_size": query_context.get("page_size", len(formatted_tasks)),
            "has_more": query_context.get("has_more", False),
            "filters_applied": query_context.get("filters_applied", []),
            "query_metadata": query_context.get("metadata", {}),
            "message": f"Found {len(formatted_tasks)} tasks",
            "operation": "query_tasks",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return SerializationValidator.ensure_serializable(response)
    
    @staticmethod
    def format_delete_response(task_id: str, action: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for delete_task operations."""
        response = {
            "success": True,
            "task_id": str(task_id),
            "action": str(action),
            "force_applied": metadata.get("force_applied", False),
            "archive_mode": metadata.get("archive_mode", True),
            "dependent_tasks": metadata.get("dependent_tasks", []),
            "message": f"Task {task_id} {action} successfully",
            "operation": "delete_task",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return SerializationValidator.ensure_serializable(response)
    
    @staticmethod
    def format_cancel_response(task_id: str, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for cancel_task operations."""
        response = {
            "success": True,
            "task_id": str(task_id),
            "previous_status": str(cancellation_data.get("previous_status", "unknown")),
            "reason": str(cancellation_data.get("reason", "")),
            "work_preserved": cancellation_data.get("work_preserved", True),
            "artifact_count": cancellation_data.get("artifact_count", 0),
            "dependent_tasks_updated": cancellation_data.get("dependent_tasks_updated", []),
            "cancelled_at": cancellation_data.get("cancelled_at"),
            "message": f"Task {task_id} cancelled successfully",
            "operation": "cancel_task",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return SerializationValidator.ensure_serializable(response)
    
    @staticmethod
    def _convert_timestamp(timestamp_value: Any) -> Optional[str]:
        """Convert various timestamp formats to ISO string."""
        if timestamp_value is None:
            return None
        
        if isinstance(timestamp_value, datetime):
            return timestamp_value.isoformat()
        elif isinstance(timestamp_value, str):
            return timestamp_value
        else:
            # Try to convert to string
            return str(timestamp_value)
    
    @staticmethod
    def _extract_metadata_field(metadata: Dict[str, Any], field: str, default: Any = None) -> Any:
        """Safely extract field from metadata with fallback."""
        return metadata.get(field, default)