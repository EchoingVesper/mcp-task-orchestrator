"""
MCP Tool Router

Handles routing of MCP tool calls to appropriate handler functions.
Extracted from main server.py for better organization.
"""

from typing import Dict, List, Any
from mcp import types

# Import reboot tool handlers
from ...reboot.reboot_tools import REBOOT_TOOL_HANDLERS


async def route_tool_call(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Route tool calls to appropriate handler functions.
    
    Args:
        name: Tool name to route
        arguments: Tool arguments from MCP client
        
    Returns:
        List of TextContent responses
        
    Raises:
        ValueError: If tool name is not recognized
    """
    # Import handlers (using relative imports to avoid circular dependencies)
    from .handlers.core_handlers import (
        handle_initialize_session,
        handle_plan_task,
        handle_execute_subtask,
        handle_complete_subtask,
        handle_synthesize_results,
        handle_get_status,
        handle_maintenance_coordinator
    )
    from .handlers.generic_task_handlers import (
        handle_create_generic_task,
        handle_update_task,
        handle_delete_task,
        handle_cancel_task,
        handle_query_tasks
    )
    
    # Core orchestration tools
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
    elif name == "orchestrator_maintenance_coordinator":
        return await handle_maintenance_coordinator(arguments)
    
    # Generic task management tools
    elif name == "orchestrator_create_generic_task":
        return await handle_create_generic_task(arguments)
    elif name == "orchestrator_update_task":
        return await handle_update_task(arguments)
    elif name == "orchestrator_delete_task":
        return await handle_delete_task(arguments)
    elif name == "orchestrator_cancel_task":
        return await handle_cancel_task(arguments)
    elif name == "orchestrator_query_tasks":
        return await handle_query_tasks(arguments)
    
    # Reboot tools from existing system
    elif name in REBOOT_TOOL_HANDLERS:
        return await REBOOT_TOOL_HANDLERS[name](arguments)
    
    # Unknown tool
    else:
        raise ValueError(f"Unknown tool: {name}")