#!/usr/bin/env python3
"""
Optimized MCP Task Orchestrator Server

A Model Context Protocol server that provides task orchestration capabilities
for AI assistants with improved synchronization, timeout handling, and error recovery.
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

from .orchestrator.core import TaskOrchestrator
from .orchestrator.state import StateManager
from .orchestrator.specialists import SpecialistManager

# Configure logging
log_level = os.environ.get("MCP_TASK_ORCHESTRATOR_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_task_orchestrator")

# Initialize the MCP server
app = Server("task-orchestrator")

# Global instances - initialized on demand to prevent startup conflicts
_state_manager: Optional[StateManager] = None
_specialist_manager: Optional[SpecialistManager] = None
_orchestrator: Optional[TaskOrchestrator] = None


def get_state_manager() -> StateManager:
    """Get or create the StateManager singleton instance."""
    global _state_manager
    if _state_manager is None:
        # Get base directory for persistence
        base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
        if not base_dir:
            base_dir = Path(__file__).parent.parent
        
        _state_manager = StateManager(base_dir=base_dir)
        logger.info(f"Initialized StateManager with persistence in {base_dir}/.task_orchestrator")
    
    return _state_manager


def get_specialist_manager() -> SpecialistManager:
    """Get or create the SpecialistManager singleton instance."""
    global _specialist_manager
    if _specialist_manager is None:
        _specialist_manager = SpecialistManager()
        logger.info("Initialized SpecialistManager")
    
    return _specialist_manager


def get_orchestrator() -> TaskOrchestrator:
    """Get or create the TaskOrchestrator singleton instance."""
    global _orchestrator
    if _orchestrator is None:
        state_mgr = get_state_manager()
        specialist_mgr = get_specialist_manager()
        _orchestrator = TaskOrchestrator(state_mgr, specialist_mgr)
        logger.info("Initialized TaskOrchestrator")
    
    return _orchestrator


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    return [
        types.Tool(
            name="orchestrator_initialize_session",
            description="Initialize a new task orchestration session with guidance for effective task breakdown",
            inputSchema={
                "type": "object",
                "properties": {}
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
                        "description": "JSON array of subtasks created by the LLM, each with title, description, specialist_type, and optional dependencies and estimated_effort"
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
                "required": ["description", "subtasks_json"]
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
    
    if name == "orchestrator_initialize_session":
        return await handle_initialize_session(arguments)
    elif name == "orchestrator_plan_task":
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


async def handle_initialize_session(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle initialization of a new task orchestration session.
    
    Checks for interrupted tasks and offers to resume them.
    """
    orchestrator = get_orchestrator()
    state_manager = get_state_manager()
    
    # Get orchestration guidance from the orchestrator
    session_context = await orchestrator.initialize_session()
    
    # Check for interrupted tasks
    active_tasks = await state_manager.get_all_tasks()
    active_parent_tasks = set()
    
    # Get unique parent task IDs
    for task in active_tasks:
        parent_id = await state_manager._get_parent_task_id_from_persistence(task.task_id)
        if parent_id:
            active_parent_tasks.add(parent_id)
    
    # Format the response for the LLM
    response = {
        "session_initialized": True,
        "orchestrator_context": session_context,
        "instructions": (
            "I'll help you break down complex tasks into manageable subtasks. "
            "Each subtask will be assigned to a specialist role with appropriate context and guidance."
        ),
        "active_tasks": [
            {
                "parent_task_id": parent_id,
                "subtasks": [
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "status": task.status.value
                    }
                    for task in active_tasks
                    if await state_manager._get_parent_task_id_from_persistence(task.task_id) == parent_id
                ]
            }
            for parent_id in active_parent_tasks
        ]
    }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_plan_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle task planning with LLM-provided subtasks."""
    orchestrator = get_orchestrator()
    
    description = args["description"]
    subtasks_json = args["subtasks_json"]
    complexity = args.get("complexity_level", "moderate")
    context = args.get("context", "")
    
    try:
        # Use a longer timeout for task planning
        breakdown = await asyncio.wait_for(
            orchestrator.plan_task(description, complexity, subtasks_json, context),
            timeout=30  # 30 seconds timeout
        )
        
        response = {
            "task_created": True,
            "parent_task_id": breakdown.parent_task_id,
            "description": breakdown.description,
            "complexity": breakdown.complexity.value,
            "subtasks": [
                {
                    "task_id": subtask.task_id,
                    "title": subtask.title,
                    "specialist_type": subtask.specialist_type.value,
                    "dependencies": subtask.dependencies
                }
                for subtask in breakdown.subtasks
            ],
            "next_steps": "Use orchestrator_execute_subtask to start working on individual subtasks"
        }
    except asyncio.TimeoutError:
        logger.error("Timeout while planning task")
        response = {
            "task_created": False,
            "error": "Operation timed out",
            "suggestions": "Try breaking the task into smaller pieces or reducing complexity"
        }
    except Exception as e:
        logger.error(f"Error planning task: {str(e)}")
        response = {
            "task_created": False,
            "error": str(e)
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_execute_subtask(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle subtask execution by providing specialist context."""
    orchestrator = get_orchestrator()
    task_id = args["task_id"]
    
    try:
        # Use a longer timeout for getting specialist context
        specialist_context = await asyncio.wait_for(
            orchestrator.get_specialist_context(task_id),
            timeout=20  # 20 seconds timeout
        )
        
        return [types.TextContent(
            type="text",
            text=specialist_context
        )]
    except asyncio.TimeoutError:
        logger.error(f"Timeout while getting specialist context for task {task_id}")
        error_response = {
            "error": "Operation timed out",
            "task_id": task_id,
            "suggestions": "Try again in a few moments or choose a different subtask"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error getting specialist context for task {task_id}: {str(e)}")
        error_response = {
            "error": str(e),
            "task_id": task_id
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_complete_subtask(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle subtask completion with improved timeout handling."""
    orchestrator = get_orchestrator()
    
    task_id = args["task_id"]
    results = args["results"]
    
    # Ensure artifacts is always a list
    artifacts = args.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = [artifacts] if artifacts else []
    
    next_action = args["next_action"]
    
    try:
        # Set a longer timeout for the operation
        completion_result = await asyncio.wait_for(
            orchestrator.complete_subtask(task_id, results, artifacts, next_action),
            timeout=30.0  # Increased from 10 to 30 seconds
        )
    except asyncio.TimeoutError:
        logger.error(f"Timeout while completing subtask {task_id}")
        # Provide more helpful error information
        completion_result = {
            "task_id": task_id,
            "status": "error",
            "error": "Operation timed out - the system is still processing your request",
            "results_recorded": False,
            "recovery_suggestions": [
                "Wait a few moments and check the task status",
                "The results may still be recorded asynchronously",
                "If the issue persists, try completing the task again"
            ]
        }
    except Exception as e:
        logger.error(f"Error completing subtask {task_id}: {str(e)}")
        completion_result = {
            "task_id": task_id,
            "status": "error",
            "error": str(e),
            "results_recorded": False
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(completion_result, indent=2)
    )]


async def handle_synthesize_results(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle result synthesis."""
    orchestrator = get_orchestrator()
    parent_task_id = args["parent_task_id"]
    
    try:
        # Use a longer timeout for synthesis
        synthesis = await asyncio.wait_for(
            orchestrator.synthesize_results(parent_task_id),
            timeout=30  # 30 seconds timeout
        )
        
        return [types.TextContent(
            type="text",
            text=synthesis
        )]
    except asyncio.TimeoutError:
        logger.error(f"Timeout while synthesizing results for task {parent_task_id}")
        error_response = {
            "error": "Operation timed out",
            "parent_task_id": parent_task_id,
            "suggestions": "Try again in a few moments or synthesize the results manually"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error synthesizing results for task {parent_task_id}: {str(e)}")
        error_response = {
            "error": str(e),
            "parent_task_id": parent_task_id
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_get_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle status requests."""
    orchestrator = get_orchestrator()
    include_completed = args.get("include_completed", False)
    
    try:
        # Use a longer timeout for getting status
        status = await asyncio.wait_for(
            orchestrator.get_status(include_completed),
            timeout=20  # 20 seconds timeout
        )
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    except asyncio.TimeoutError:
        logger.error("Timeout while getting status")
        error_response = {
            "error": "Operation timed out",
            "suggestions": "Try again in a few moments with fewer tasks (set include_completed=False)"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        error_response = {
            "error": str(e)
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def main():
    """Main entry point for the MCP server."""
    try:
        # Log server initialization
        logger.info("Starting MCP Task Orchestrator server...")
        
        # Use the original implementation pattern with async context manager
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream, 
                write_stream,
                app.create_initialization_options()
            )
        
        # This line will only be reached if the server exits normally
        logger.info("MCP Task Orchestrator server shutdown gracefully")
    except Exception as e:
        logger.error(f"Error in MCP Task Orchestrator server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
