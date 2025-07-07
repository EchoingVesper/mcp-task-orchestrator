"""
MCP Tool Router with Migration Support

Handles routing of MCP tool calls to appropriate handler functions.
Supports gradual migration from dictionary-based to Pydantic DTO-based handlers.
"""

import logging
from typing import Dict, List, Any
from mcp import types

# Import reboot tool handlers
from ...reboot.reboot_tools import REBOOT_TOOL_HANDLERS

# Import migration manager
from .handlers.migration_config import get_handler_for_tool, get_migration_status

logger = logging.getLogger(__name__)


async def route_tool_call(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Route tool calls to appropriate handler functions with migration support.
    
    This router uses the migration manager to determine whether to use old
    dictionary-based handlers or new Pydantic DTO-based handlers based on
    environment configuration.
    
    Args:
        name: Tool name to route
        arguments: Tool arguments from MCP client
        
    Returns:
        List of TextContent responses
        
    Raises:
        ValueError: If tool name is not recognized
    """
    # Import core handlers (not migrated yet)
    from .handlers.core_handlers import (
        handle_initialize_session,
        handle_synthesize_results,
        handle_get_status,
        handle_maintenance_coordinator
    )
    
    # Log handler selection for debugging
    migration_status = get_migration_status()
    if name in migration_status:
        handler_info = migration_status[name]
        logger.debug(f"Tool {name}: using {'new' if handler_info['using_new_handler'] else 'old'} handler")
    
    # Core orchestration tools (not migrated yet)
    if name == "orchestrator_initialize_session":
        return await handle_initialize_session(arguments)
    elif name == "orchestrator_synthesize_results":
        return await handle_synthesize_results(arguments)
    elif name == "orchestrator_get_status":
        return await handle_get_status(arguments)
    elif name == "orchestrator_maintenance_coordinator":
        return await handle_maintenance_coordinator(arguments)
    
    # Task management tools (use migration manager)
    elif name in ["orchestrator_plan_task", "orchestrator_create_generic_task", 
                  "orchestrator_execute_task", "orchestrator_complete_task",
                  "orchestrator_update_task", "orchestrator_delete_task",
                  "orchestrator_cancel_task", "orchestrator_query_tasks"]:
        try:
            # Get appropriate handler from migration manager
            handler = get_handler_for_tool(name)
            return await handler(arguments)
        except Exception as e:
            logger.error(f"Error routing tool {name}: {e}")
            # Return error response
            error_response = {
                "status": "error",
                "error": f"Handler error: {str(e)}",
                "tool": name,
                "error_type": type(e).__name__
            }
            return [types.TextContent(
                type="text",
                text=str(error_response)
            )]
    
    # Reboot tools from existing system
    elif name in REBOOT_TOOL_HANDLERS:
        return await REBOOT_TOOL_HANDLERS[name](arguments)
    
    # Unknown tool
    else:
        raise ValueError(f"Unknown tool: {name}")


def get_handler_migration_info() -> Dict[str, Any]:
    """Get information about current handler migration status."""
    return {
        "migration_status": get_migration_status(),
        "description": "Handler migration status shows which tools are using new Pydantic handlers vs old dictionary handlers",
        "configuration": {
            "global_flag": "MCP_USE_PYDANTIC_HANDLERS",
            "individual_flags": [
                "MCP_USE_PYDANTIC_CREATE_TASK",
                "MCP_USE_PYDANTIC_UPDATE_TASK", 
                "MCP_USE_PYDANTIC_DELETE_TASK",
                "MCP_USE_PYDANTIC_CANCEL_TASK",
                "MCP_USE_PYDANTIC_QUERY_TASKS",
                "MCP_USE_PYDANTIC_EXECUTE_TASK",
                "MCP_USE_PYDANTIC_COMPLETE_TASK"
            ]
        }
    }