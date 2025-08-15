"""
MCP Tool Handlers Package

Contains organized handler functions for different categories of MCP tools.
"""

# Re-export handler functions for easier importing
from .core_handlers import (
    handle_initialize_session,
    handle_synthesize_results,
    handle_get_status,
    handle_maintenance_coordinator
)

from .task_handlers import (
    handle_create_generic_task,
    handle_update_task,
    handle_delete_task,
    handle_cancel_task,
    handle_query_tasks,
    handle_execute_task,
    handle_complete_task
)

__all__ = [
    # Core handlers
    "handle_initialize_session",
    "handle_synthesize_results",
    "handle_get_status",
    "handle_maintenance_coordinator",
    
    # Task handlers
    "handle_create_generic_task",
    "handle_update_task",
    "handle_delete_task", 
    "handle_cancel_task",
    "handle_query_tasks",
    "handle_execute_task",
    "handle_complete_task"
]