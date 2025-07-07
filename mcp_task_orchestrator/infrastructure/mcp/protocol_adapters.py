"""
MCP protocol adapters for converting between MCP and domain objects.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

from mcp import types

from ...domain import (
    TaskPriority, TaskComplexity, OrchestrationError
)
from ...application.dto import (
    TaskPlanRequest, TaskExecutionRequest, ProgressStatusRequest
)


@dataclass
class MCPRequestAdapter:
    """
    Adapts MCP protocol requests to application DTOs.
    
    This adapter converts raw MCP tool arguments into
    properly typed application request objects.
    """
    
    @staticmethod
    def to_task_plan_request(args: Dict[str, Any]) -> TaskPlanRequest:
        """Convert MCP arguments to TaskPlanRequest."""
        return TaskPlanRequest(
            description=args.get('description', ''),
            complexity_level=args.get('complexity_level', 'moderate'),
            subtasks_json=args.get('subtasks_json'),
            context=args.get('context'),
            metadata=args.get('metadata', {})
        )
    
    @staticmethod
    def to_task_execution_request(args: Dict[str, Any]) -> TaskExecutionRequest:
        """Convert MCP arguments to TaskExecutionRequest."""
        return TaskExecutionRequest(
            task_id=args.get('task_id', ''),
            force=args.get('force', False),
            timeout=args.get('timeout'),
            context_override=args.get('context_override'),
            metadata=args.get('metadata', {})
        )
    
    @staticmethod
    def to_progress_status_request(args: Dict[str, Any]) -> ProgressStatusRequest:
        """Convert MCP arguments to ProgressStatusRequest."""
        return ProgressStatusRequest(
            session_id=args.get('session_id'),
            task_id=args.get('task_id'),
            include_completed=args.get('include_completed', False),
            include_subtasks=args.get('include_subtasks', True),
            include_metrics=args.get('include_metrics', True)
        )
    
    @staticmethod
    def validate_args(args: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """
        Validate that required fields are present.
        
        Returns error message if validation fails, None if valid.
        """
        missing = [field for field in required_fields if field not in args or not args[field]]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None


@dataclass
class MCPResponseAdapter:
    """
    Adapts application responses to MCP protocol format.
    
    This adapter converts application DTOs and domain objects
    into MCP TextContent responses.
    """
    
    @staticmethod
    def success_response(data: Dict[str, Any]) -> List[types.TextContent]:
        """Create a successful MCP response."""
        return [types.TextContent(
            type="text",
            text=json.dumps(data, indent=2, default=str)
        )]
    
    @staticmethod
    def error_response(error: Exception) -> List[types.TextContent]:
        """Create an error MCP response."""
        if isinstance(error, OrchestrationError):
            error_data = {
                "error": error.message,
                "type": error.__class__.__name__,
                "details": error.details
            }
        else:
            error_data = {
                "error": str(error),
                "type": error.__class__.__name__
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]
    
    @staticmethod
    def task_plan_response(response) -> List[types.TextContent]:
        """Convert TaskPlanResponse to MCP format."""
        data = {
            "task_created": response.success,
            "parent_task_id": response.parent_task_id,
            "description": response.description,
            "complexity": response.complexity,
            "subtasks": response.subtasks,
            "execution_order": response.execution_order,
            "estimated_duration_minutes": response.estimated_duration,
            "next_steps": "Use orchestrator_execute_subtask to start working on individual subtasks"
        }
        
        if response.error:
            data["error"] = response.error
        
        return MCPResponseAdapter.success_response(data)
    
    @staticmethod
    def task_execution_response(response) -> List[types.TextContent]:
        """Convert TaskExecutionResponse to MCP format."""
        data = {
            "execution_completed": response.success,
            "task_id": response.task_id,
            "status": response.status,
            "started_at": response.started_at.isoformat() if response.started_at else None,
            "completed_at": response.completed_at.isoformat() if response.completed_at else None,
            "result": response.result,
            "artifacts": response.artifacts,
            "metrics": response.metrics
        }
        
        if response.error:
            data["error"] = response.error
        
        return MCPResponseAdapter.success_response(data)
    
    @staticmethod
    def progress_status_response(response) -> List[types.TextContent]:
        """Convert ProgressStatusResponse to MCP format."""
        data = {
            "overall_status": response.overall_status,
            "metrics": response.metrics
        }
        
        if response.session_info:
            data["session"] = response.session_info
        
        if response.task_info:
            data["task"] = response.task_info
        
        if response.sessions:
            data["sessions"] = response.sessions
        
        if response.active_tasks:
            data["active_tasks"] = response.active_tasks
        
        if response.pending_tasks:
            data["pending_tasks"] = response.pending_tasks
        
        if response.completed_tasks:
            data["completed_tasks"] = response.completed_tasks
        
        if response.failed_tasks:
            data["failed_tasks"] = response.failed_tasks
        
        if response.subtasks:
            data["subtasks"] = response.subtasks
        
        return MCPResponseAdapter.success_response(data)


@dataclass
class MCPErrorAdapter:
    """
    Adapts errors to MCP-friendly format with helpful context.
    """
    
    @staticmethod
    def validation_error(message: str, suggestions: List[str] = None) -> List[types.TextContent]:
        """Create validation error response."""
        error_data = {
            "error": message,
            "type": "ValidationError",
            "suggestions": suggestions or ["Check the input parameters", "Refer to tool documentation"]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]
    
    @staticmethod
    def timeout_error(task_id: str, timeout_seconds: int) -> List[types.TextContent]:
        """Create timeout error response."""
        error_data = {
            "error": f"Operation timed out after {timeout_seconds} seconds",
            "type": "TimeoutError",
            "task_id": task_id,
            "recovery_suggestions": [
                "Check task status with orchestrator_get_status",
                "The task may still be processing",
                "Consider increasing timeout value"
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]
    
    @staticmethod
    def not_found_error(resource_type: str, resource_id: str) -> List[types.TextContent]:
        """Create not found error response."""
        error_data = {
            "error": f"{resource_type} not found: {resource_id}",
            "type": "NotFoundError",
            "resource_type": resource_type,
            "resource_id": resource_id,
            "suggestions": [
                f"Check if the {resource_type.lower()} ID is correct",
                "Use orchestrator_get_status to list available resources"
            ]
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_data, indent=2)
        )]