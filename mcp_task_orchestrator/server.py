#!/usr/bin/env python3
"""
MCP Task Orchestrator Server

A Model Context Protocol server that provides task orchestration capabilities
for AI assistants. This server allows complex tasks to be broken down into
specialized subtasks, each with appropriate context and prompts.
"""

import asyncio
import json
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .orchestrator import TaskOrchestrator, StateManager, SpecialistManager

# Configure logging
log_level = os.environ.get("MCP_TASK_ORCHESTRATOR_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_task_orchestrator")

# Initialize the MCP server
app = Server("task-orchestrator")

# Initialize core components
state_manager = StateManager()
specialist_manager = SpecialistManager()
orchestrator = TaskOrchestrator(state_manager, specialist_manager)


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    return [
        types.Tool(
            name="orchestrator_plan_task",
            description="Analyze a complex task and break it down into specialized subtasks",            inputSchema={
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
            name="orchestrator_execute_subtask",
            description="Get specialist context and prompts for executing a specific subtask",
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
            description="Mark a subtask as complete and record its results",
            inputSchema={
                "type": "object", 
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the completed subtask"
                    },
                    "results": {
                        "type": "string",
                        "description": "Summary of what was accomplished"
                    },                    "artifacts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of files, code, or other artifacts created"
                    },
                    "next_action": {
                        "type": "string",
                        "enum": ["continue", "needs_revision", "blocked", "complete"],
                        "description": "What should happen next"
                    }
                },
                "required": ["task_id", "results", "next_action"]
            }
        ),
        types.Tool(
            name="orchestrator_synthesize_results", 
            description="Combine completed subtasks into a final comprehensive result",
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


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls from the LLM."""
    
    if name == "orchestrator_plan_task":
        return await handle_plan_task(arguments)
    elif name == "orchestrator_execute_subtask":
        return await handle_execute_subtask(arguments)
    elif name == "orchestrator_complete_subtask":
        return await handle_complete_subtask(arguments)
    elif name == "orchestrator_synthesize_results":
        return await handle_synthesize_results(arguments)
    elif name == "orchestrator_get_status":
        return await handle_get_status(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task planning and breakdown."""
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
            f"Use 'orchestrator_execute_subtask' with each task_id to begin working on them. "
            f"Recommended order: {' → '.join([st.task_id for st in breakdown.subtasks])}"
        )
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_execute_subtask(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle subtask execution by providing specialist context."""
    task_id = args["task_id"]
    
    specialist_context = await orchestrator.get_specialist_context(task_id)
    
    return [types.TextContent(
        type="text", 
        text=specialist_context
    )]


async def handle_complete_subtask(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle subtask completion."""
    task_id = args["task_id"]
    results = args["results"]
    artifacts = args.get("artifacts", [])
    next_action = args["next_action"]
    
    completion_result = await orchestrator.complete_subtask(
        task_id, results, artifacts, next_action
    )
    
    return [types.TextContent(
        type="text",
        text=json.dumps(completion_result, indent=2)
    )]


async def handle_synthesize_results(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle result synthesis."""
    parent_task_id = args["parent_task_id"]
    
    synthesis = await orchestrator.synthesize_results(parent_task_id)
    
    return [types.TextContent(
        type="text",
        text=synthesis
    )]


async def handle_get_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle status requests."""
    include_completed = args.get("include_completed", False)
    
    status = await orchestrator.get_status(include_completed)
    
    return [types.TextContent(
        type="text",
        text=json.dumps(status, indent=2)
    )]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
