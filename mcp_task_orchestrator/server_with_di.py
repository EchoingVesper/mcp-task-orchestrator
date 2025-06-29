"""
MCP Task Orchestrator Server with Dependency Injection.

This is a refactored version of the main server that uses dependency injection
instead of singleton patterns for better testability and modularity.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

from .infrastructure.di import (
    ServiceContainer, get_container, set_container, 
    get_service, register_services
)
from .infrastructure.di.service_configuration import (
    configure_all_services, get_default_config
)
from .domain.services import OrchestrationCoordinator
from .orchestrator.enhanced_core import get_orchestrator_handlers
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_task_orchestrator.server_di")


class DIEnabledMCPServer:
    """MCP Server with dependency injection support."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the DI-enabled MCP server.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or get_default_config()
        self.container: Optional[ServiceContainer] = None
        self.coordinator: Optional[OrchestrationCoordinator] = None
        self.server = Server("task-orchestrator")
        
        # Initialize DI container
        self._setup_dependency_injection()
        
        # Setup MCP handlers
        self._setup_handlers()
    
    def _setup_dependency_injection(self):
        """Setup the dependency injection container."""
        try:
            # Create and configure container
            self.container = ServiceContainer()
            configure_all_services(self.container, self.config)
            
            # Set as global container
            set_container(self.container)
            
            # Get coordinator
            self.coordinator = self.container.get_service(OrchestrationCoordinator)
            
            logger.info("Dependency injection container configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup dependency injection: {e}")
            raise
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        # List available tools
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available orchestration tools."""
            return [
                Tool(
                    name="orchestrator_initialize_session",
                    description="Initialize a new task orchestration session",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="orchestrator_plan_task",
                    description="Plan and break down a complex task into subtasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Main task description"
                            },
                            "complexity": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Task complexity level"
                            },
                            "subtasks": {
                                "type": "string",
                                "description": "JSON string containing subtask definitions"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context for the task"
                            }
                        },
                        "required": ["description", "complexity", "subtasks"]
                    }
                ),
                Tool(
                    name="orchestrator_get_specialist_context",
                    description="Get context for a specialist to work on a specific task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                Tool(
                    name="orchestrator_complete_subtask",
                    description="Complete a subtask with results and optional artifacts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to complete"
                            },
                            "results": {
                                "type": "string",
                                "description": "The results or output of the task"
                            },
                            "artifacts": {
                                "type": "array",
                                "description": "Optional artifacts (code, files, etc.)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "name": {"type": "string"},
                                        "content": {"type": "string"},
                                        "metadata": {"type": "object"}
                                    }
                                }
                            }
                        },
                        "required": ["task_id", "results"]
                    }
                ),
                Tool(
                    name="orchestrator_synthesize_results",
                    description="Synthesize results from completed subtasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "parent_task_id": {
                                "type": "string",
                                "description": "The parent task ID to synthesize results for"
                            }
                        },
                        "required": ["parent_task_id"]
                    }
                ),
                Tool(
                    name="orchestrator_get_status",
                    description="Get current status of all orchestrated tasks",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Optional session ID to filter by"
                            },
                            "include_completed": {
                                "type": "boolean",
                                "description": "Whether to include completed tasks"
                            }
                        },
                        "required": []
                    }
                )
            ]
        
        # Handle tool calls
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
            """Handle tool execution."""
            try:
                if not self.coordinator:
                    raise ValueError("Orchestration coordinator not initialized")
                
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {e}")]
        
        # List resources (if needed)
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available resources."""
            return []
        
        # Read resources (if needed)
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read a resource."""
            return "Resource reading not implemented"
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with the given arguments."""
        if name == "orchestrator_initialize_session":
            return await self.coordinator.initialize_session()
        
        elif name == "orchestrator_plan_task":
            return await self.coordinator.plan_task(
                description=arguments["description"],
                complexity=arguments["complexity"],
                subtasks_json=arguments["subtasks"],
                context=arguments.get("context", "")
            )
        
        elif name == "orchestrator_get_specialist_context":
            return await self.coordinator.get_specialist_context(
                task_id=arguments["task_id"]
            )
        
        elif name == "orchestrator_complete_subtask":
            return await self.coordinator.complete_subtask(
                task_id=arguments["task_id"],
                results=arguments["results"],
                artifacts=arguments.get("artifacts", [])
            )
        
        elif name == "orchestrator_synthesize_results":
            return await self.coordinator.synthesize_results(
                parent_task_id=arguments["parent_task_id"]
            )
        
        elif name == "orchestrator_get_status":
            return await self.coordinator.get_status(
                session_id=arguments.get("session_id"),
                include_completed=arguments.get("include_completed", False)
            )
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def run(self):
        """Run the MCP server."""
        logger.info("Starting MCP Task Orchestrator Server with Dependency Injection")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            # Cleanup
            if self.container:
                self.container.dispose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.container:
            self.container.dispose()


async def run_server_with_di(config: Optional[Dict[str, Any]] = None):
    """
    Run the MCP server with dependency injection.
    
    Args:
        config: Optional configuration
    """
    # Get configuration
    if config is None:
        try:
            config = get_config()
        except Exception:
            # Fall back to default config if unified config not available
            config = get_default_config()
    
    # Create and run server
    with DIEnabledMCPServer(config) as server:
        await server.run()


def main():
    """Main entry point."""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # Run server
        asyncio.run(run_server_with_di())
        
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()