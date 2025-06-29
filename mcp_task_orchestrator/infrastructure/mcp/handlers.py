"""
MCP tool and resource handlers.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging

from mcp import types

from ...application import (
    OrchestrateTaskUseCase,
    ManageSpecialistsUseCase,
    TrackProgressUseCase
)
from ...domain import OrchestrationError
from .protocol_adapters import (
    MCPRequestAdapter,
    MCPResponseAdapter,
    MCPErrorAdapter
)

logger = logging.getLogger(__name__)


@dataclass
class MCPToolHandler:
    """
    Handles MCP tool invocations by delegating to application use cases.
    
    This handler acts as the bridge between MCP protocol and
    the application layer, handling all protocol-specific concerns.
    """
    orchestrate_use_case: OrchestrateTaskUseCase
    specialist_use_case: ManageSpecialistsUseCase
    progress_use_case: TrackProgressUseCase
    
    async def handle_initialize_session(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_initialize_session tool."""
        try:
            # For session initialization, we'll use the progress use case
            # to check for any existing sessions
            request = MCPRequestAdapter.to_progress_status_request({})
            response = await self.progress_use_case.get_session_progress(request)
            
            # Format initialization response
            init_data = {
                "session_initialized": True,
                "working_directory": args.get("working_directory", "."),
                "orchestrator_context": {
                    "active_sessions": len(response.sessions or []),
                    "overall_status": response.overall_status
                },
                "instructions": (
                    "I'll help you break down complex tasks into manageable subtasks. "
                    "Each subtask will be assigned to a specialist role with appropriate context."
                ),
                "next_steps": "Use orchestrator_plan_task to create a task breakdown"
            }
            
            return MCPResponseAdapter.success_response(init_data)
            
        except Exception as e:
            logger.error(f"Error initializing session: {e}")
            return MCPResponseAdapter.error_response(e)
    
    async def handle_plan_task(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_plan_task tool."""
        try:
            # Validate required arguments
            error = MCPRequestAdapter.validate_args(args, ['description', 'subtasks_json'])
            if error:
                return MCPErrorAdapter.validation_error(error)
            
            # Convert to request DTO
            request = MCPRequestAdapter.to_task_plan_request(args)
            
            # Call use case with timeout
            response = await asyncio.wait_for(
                self.orchestrate_use_case.plan_task(request),
                timeout=30.0  # 30 second timeout
            )
            
            # Convert response
            return MCPResponseAdapter.task_plan_response(response)
            
        except asyncio.TimeoutError:
            logger.error("Timeout while planning task")
            return MCPErrorAdapter.timeout_error("planning", 30)
        except OrchestrationError as e:
            logger.error(f"Orchestration error: {e}")
            return MCPResponseAdapter.error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error planning task: {e}")
            return MCPResponseAdapter.error_response(e)
    
    async def handle_execute_subtask(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_execute_subtask tool."""
        try:
            # Validate required arguments
            error = MCPRequestAdapter.validate_args(args, ['task_id'])
            if error:
                return MCPErrorAdapter.validation_error(error)
            
            # For now, return specialist context
            # In a full implementation, this would trigger actual execution
            task_id = args['task_id']
            
            # Get specialist assignment
            # This is a simplified version - full implementation would
            # involve more complex execution logic
            execution_data = {
                "task_id": task_id,
                "status": "ready",
                "specialist_assigned": True,
                "context": {
                    "task_description": "Task execution context would be provided here",
                    "specialist_guidance": "Specialist-specific guidance",
                    "parent_context": "Context from parent task"
                },
                "next_action": "Execute the task according to the specialist guidance"
            }
            
            return MCPResponseAdapter.success_response(execution_data)
            
        except Exception as e:
            logger.error(f"Error executing subtask: {e}")
            return MCPResponseAdapter.error_response(e)
    
    async def handle_complete_subtask(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_complete_subtask tool."""
        try:
            # Validate required arguments
            error = MCPRequestAdapter.validate_args(args, ['task_id', 'summary', 'next_action'])
            if error:
                return MCPErrorAdapter.validation_error(error)
            
            # In a full implementation, this would update task status
            # and potentially trigger synthesis
            completion_data = {
                "task_id": args['task_id'],
                "status": "completed",
                "summary_recorded": True,
                "artifacts_created": bool(args.get('artifact_ids', [])),
                "next_action": args['next_action']
            }
            
            return MCPResponseAdapter.success_response(completion_data)
            
        except Exception as e:
            logger.error(f"Error completing subtask: {e}")
            return MCPResponseAdapter.error_response(e)
    
    async def handle_get_status(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_get_status tool."""
        try:
            # Convert to request DTO
            request = MCPRequestAdapter.to_progress_status_request(args)
            
            # Call use case
            response = await self.progress_use_case.get_session_progress(request)
            
            # Convert response
            return MCPResponseAdapter.progress_status_response(response)
            
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return MCPResponseAdapter.error_response(e)
    
    async def handle_synthesize_results(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle orchestrator_synthesize_results tool."""
        try:
            # Validate required arguments
            error = MCPRequestAdapter.validate_args(args, ['parent_task_id'])
            if error:
                return MCPErrorAdapter.validation_error(error)
            
            # In a full implementation, this would trigger result synthesis
            synthesis_data = {
                "parent_task_id": args['parent_task_id'],
                "synthesis_complete": True,
                "combined_results": "Combined results from all subtasks would appear here",
                "overall_status": "completed"
            }
            
            return MCPResponseAdapter.success_response(synthesis_data)
            
        except Exception as e:
            logger.error(f"Error synthesizing results: {e}")
            return MCPResponseAdapter.error_response(e)


@dataclass
class MCPResourceHandler:
    """
    Handles MCP resource requests (if needed in future).
    
    This handler would manage resources like task lists,
    specialist definitions, etc.
    """
    
    async def list_resources(self) -> List[types.Resource]:
        """List available resources."""
        # Placeholder for future resource support
        return []
    
    async def read_resource(self, uri: str) -> str:
        """Read a specific resource."""
        # Placeholder for future resource support
        raise NotImplementedError("Resource reading not yet implemented")