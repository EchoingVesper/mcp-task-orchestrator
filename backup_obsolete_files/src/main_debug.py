#!/usr/bin/env python3
"""
MCP Task Orchestrator Server - Debug Version

Debug version with comprehensive error handling and logging to stderr.
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add proper error logging to stderr
def log_error(message: str, exception: Exception = None):
    """Log errors to stderr (not stdout to avoid interfering with MCP protocol)."""
    timestamp = asyncio.get_event_loop().time()
    error_msg = f"[ERROR {timestamp}] {message}"
    if exception:
        error_msg += f": {str(exception)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr, flush=True)

def log_info(message: str):
    """Log info messages to stderr."""
    timestamp = asyncio.get_event_loop().time()
    print(f"[INFO {timestamp}] {message}", file=sys.stderr, flush=True)

try:
    import mcp.types as types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    log_info("MCP imports successful")
except Exception as e:
    log_error("Failed to import MCP modules", e)
    sys.exit(1)

try:
    from orchestrator.core import TaskOrchestrator
    from orchestrator.models import TaskBreakdown, SubTask, TaskStatus
    from orchestrator.specialists import SpecialistManager
    from orchestrator.state_debug import StateManager
    log_info("Orchestrator imports successful")
except Exception as e:
    log_error("Failed to import orchestrator modules", e)
    sys.exit(1)

# Initialize the MCP server
try:
    app = Server("task-orchestrator")
    log_info("MCP Server created successfully")
except Exception as e:
    log_error("Failed to create MCP Server", e)
    sys.exit(1)

# Initialize core components with error handling
try:
    log_info("Initializing StateManager...")
    state_manager = StateManager()
    log_info("StateManager initialized successfully")
    
    log_info("Initializing SpecialistManager...")
    specialist_manager = SpecialistManager()
    log_info("SpecialistManager initialized successfully")
    
    log_info("Initializing TaskOrchestrator...")
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    log_info("TaskOrchestrator initialized successfully")
    
except Exception as e:
    log_error("Failed to initialize core components", e)
    sys.exit(1)


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    try:
        log_info("list_tools called")
        return [
            types.Tool(
                name="orchestrator_plan_task",
                description="Analyze a complex task and break it down into specialized subtasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "The complex task to be broken down"
                        },
                        "complexity_level": {
                            "type": "string", 
                            "enum": ["simple", "moderate", "complex", "very_complex"],
                            "description": "Estimated complexity of the task",
                            "default": "moderate"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context about the task (optional)"
                        }
                    },
                    "required": ["description"]
                }
            ),
            types.Tool(
                name="orchestrator_get_status",
                description="Get current status of all active tasks and their progress",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_completed": {
                            "type": "boolean",
                            "description": "Whether to include completed tasks in the status",
                            "default": False
                        }
                    }
                }
            )
        ]
    except Exception as e:
        log_error("Error in list_tools", e)
        raise


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from the LLM."""
    try:
        log_info(f"call_tool called with: {name}")
        
        if name == "orchestrator_plan_task":
            return await handle_plan_task(arguments)
        elif name == "orchestrator_get_status":
            return await handle_get_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        log_error(f"Error in call_tool {name}", e)
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def handle_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task planning and breakdown."""
    try:
        log_info("handle_plan_task called")
        description = args["description"]
        complexity = args.get("complexity_level", "moderate")
        context = args.get("context", "")
        
        breakdown = await orchestrator.plan_task(description, complexity, context)
        
        response = {
            "task_breakdown": {
                "parent_task_id": breakdown.parent_task_id,
                "total_subtasks": len(breakdown.subtasks),
                "estimated_complexity": breakdown.complexity,
                "subtasks": [
                    {
                        "task_id": subtask.task_id,
                        "title": subtask.title,
                        "specialist_type": subtask.specialist_type,
                        "description": subtask.description,
                        "dependencies": subtask.dependencies,
                        "estimated_effort": subtask.estimated_effort
                    }
                    for subtask in breakdown.subtasks
                ]
            },
            "instructions": (
                f"Task breakdown complete! {len(breakdown.subtasks)} subtasks identified. "
                f"Debug server working correctly!"
            )
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
    except Exception as e:
        log_error("Error in handle_plan_task", e)
        raise


async def handle_get_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle status requests."""
    try:
        log_info("handle_get_status called")
        include_completed = args.get("include_completed", False)
        
        status = await orchestrator.get_status(include_completed)
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    except Exception as e:
        log_error("Error in handle_get_status", e)
        raise


async def main():
    """Main entry point for the MCP server."""
    try:
        log_info("Starting MCP Task Orchestrator Debug Server...")
        log_info(f"Working directory: {Path.cwd()}")
        log_info(f"Script location: {Path(__file__).parent}")
        
        async with stdio_server() as (read_stream, write_stream):
            log_info("stdio_server created, starting app.run()")
            await app.run(
                read_stream, 
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        log_error("Error in main()", e)
        sys.exit(1)


if __name__ == "__main__":
    try:
        log_info("=== MCP Task Orchestrator Debug Server Starting ===")
        asyncio.run(main())
    except Exception as e:
        log_error("Fatal error in server startup", e)
        sys.exit(1)
