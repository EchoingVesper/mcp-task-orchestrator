"""
MCP Server adapter that bridges MCP protocol with clean architecture.
"""

from typing import Dict, Any, List
import logging

from mcp import types
from mcp.server import Server

from ...application import (
    OrchestrateTaskUseCase,
    ManageSpecialistsUseCase,
    TrackProgressUseCase
)
# from .handlers import MCPToolHandler, MCPResourceHandler  # Temporarily commented out

logger = logging.getLogger(__name__)


class MCPServerAdapter:
    """
    Adapter that configures an MCP server with clean architecture handlers.
    
    This adapter isolates MCP protocol concerns from the application layer,
    allowing the business logic to remain independent of the protocol.
    """
    
    def __init__(
        self,
        orchestrate_use_case: OrchestrateTaskUseCase,
        specialist_use_case: ManageSpecialistsUseCase,
        progress_use_case: TrackProgressUseCase
    ):
        self.server = Server("task-orchestrator")
        self.tool_handler = MCPToolHandler(
            orchestrate_use_case=orchestrate_use_case,
            specialist_use_case=specialist_use_case,
            progress_use_case=progress_use_case
        )
        self.resource_handler = MCPResourceHandler()
        
        self._register_tools()
        self._register_handlers()
    
    def _register_tools(self):
        """Register all available tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            """List all available orchestration tools."""
            return [
                types.Tool(
                    name="orchestrator_initialize_session",
                    description="Initialize a new task orchestration session",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "working_directory": {
                                "type": "string",
                                "description": "Working directory for the session"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="orchestrator_plan_task",
                    description="Create a task breakdown from LLM-analyzed subtasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "The complex task to be broken down"
                            },
                            "subtasks_json": {
                                "type": "string",
                                "description": "JSON array of subtasks"
                            },
                            "complexity_level": {
                                "type": "string",
                                "enum": ["simple", "moderate", "complex", "highly_complex"],
                                "default": "moderate"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the task"
                            }
                        },
                        "required": ["description", "subtasks_json"]
                    }
                ),
                types.Tool(
                    name="orchestrator_execute_subtask",
                    description="Execute a specific subtask with specialist context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "ID of the subtask to execute"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="orchestrator_complete_subtask",
                    description="Mark a subtask as completed with results",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "ID of the completed subtask"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Summary of work completed"
                            },
                            "detailed_work": {
                                "type": "string",
                                "description": "Detailed description of work done"
                            },
                            "next_action": {
                                "type": "string",
                                "enum": ["continue", "needs_revision", "blocked", "complete"],
                                "description": "What should happen next"
                            },
                            "artifact_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of artifact IDs created"
                            }
                        },
                        "required": ["task_id", "summary", "next_action"]
                    }
                ),
                types.Tool(
                    name="orchestrator_get_status",
                    description="Get current status of tasks and progress",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_completed": {
                                "type": "boolean",
                                "description": "Whether to include completed tasks",
                                "default": False
                            },
                            "session_id": {
                                "type": "string",
                                "description": "Specific session to check"
                            },
                            "task_id": {
                                "type": "string",
                                "description": "Specific task to check"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="orchestrator_synthesize_results",
                    description="Combine completed subtasks into final result",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "parent_task_id": {
                                "type": "string",
                                "description": "ID of the parent task to synthesize"
                            }
                        },
                        "required": ["parent_task_id"]
                    }
                )
            ]
    
    def _register_handlers(self):
        """Register tool call handlers with the MCP server."""
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls from the LLM."""
            
            try:
                # Route to appropriate handler
                if name == "orchestrator_initialize_session":
                    return await self.tool_handler.handle_initialize_session(arguments)
                elif name == "orchestrator_plan_task":
                    return await self.tool_handler.handle_plan_task(arguments)
                elif name == "orchestrator_execute_subtask":
                    return await self.tool_handler.handle_execute_subtask(arguments)
                elif name == "orchestrator_complete_subtask":
                    return await self.tool_handler.handle_complete_subtask(arguments)
                elif name == "orchestrator_get_status":
                    return await self.tool_handler.handle_get_status(arguments)
                elif name == "orchestrator_synthesize_results":
                    return await self.tool_handler.handle_synthesize_results(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            
            except Exception as e:
                logger.error(f"Error handling tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )]
    
    def get_server(self) -> Server:
        """Get the configured MCP server instance."""
        return self.server