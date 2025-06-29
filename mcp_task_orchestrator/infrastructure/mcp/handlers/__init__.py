"""
MCP Tool Handlers Package

Contains organized handler functions for different categories of MCP tools.
"""

# Re-export handler functions for easier importing
from .core_handlers import (
    handle_initialize_session,
    handle_plan_task,
    handle_execute_subtask,
    handle_complete_subtask,
    handle_synthesize_results,
    handle_get_status,
    handle_maintenance_coordinator
)

from .generic_task_handlers import (
    handle_create_generic_task,
    handle_update_task,
    handle_delete_task,
    handle_cancel_task,
    handle_query_tasks
)

__all__ = [
    # Core handlers
    "handle_initialize_session",
    "handle_plan_task", 
    "handle_execute_subtask",
    "handle_complete_subtask",
    "handle_synthesize_results",
    "handle_get_status",
    "handle_maintenance_coordinator",
    
    # Generic task handlers
    "handle_create_generic_task",
    "handle_update_task",
    "handle_delete_task", 
    "handle_cancel_task",
    "handle_query_tasks"
]