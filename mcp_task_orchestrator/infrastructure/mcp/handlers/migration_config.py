"""
Handler Migration Configuration.

This module provides feature flags and configuration for gradually migrating
from dictionary-based handlers to Pydantic DTO-based handlers.
"""

import os
from typing import Dict, Callable, Any
from dataclasses import dataclass

# Import old handlers
from .task_handlers import (
    handle_create_generic_task,
    handle_update_task,
    handle_delete_task,
    handle_cancel_task,
    handle_query_tasks,
    handle_execute_task,
    handle_complete_task,
    handle_plan_task_legacy
)

# Fixed handler removed - routing directly to Clean Architecture handlers

# Import new Pydantic-based handlers
from .task_handlers_v2 import (
    handle_create_task_v2,
    handle_update_task_v2,
    handle_delete_task_v2,
    handle_cancel_task_v2,
    handle_query_tasks_v2,
    handle_execute_task_v2,
    handle_complete_task_v2
)


@dataclass
class HandlerConfig:
    """Configuration for a handler migration."""
    tool_name: str
    old_handler: Callable
    new_handler: Callable
    use_new: bool = False
    description: str = ""


class HandlerMigrationManager:
    """Manages the gradual migration from old to new handlers."""
    
    def __init__(self):
        # Check environment variable for enabling new handlers
        use_pydantic_handlers = os.getenv("MCP_USE_PYDANTIC_HANDLERS", "false").lower() == "true"
        
        # Define handler configurations
        self.handler_configs: Dict[str, HandlerConfig] = {
            # orchestrator_plan_task removed - routes directly to Clean Architecture handlers
            "orchestrator_create_generic_task": HandlerConfig(
                tool_name="orchestrator_create_generic_task",
                old_handler=handle_create_generic_task,
                new_handler=handle_create_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("CREATE_TASK"),
                description="Create a generic task"
            ),
            "orchestrator_update_task": HandlerConfig(
                tool_name="orchestrator_update_task",
                old_handler=handle_update_task,
                new_handler=handle_update_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("UPDATE_TASK"),
                description="Update an existing task"
            ),
            "orchestrator_delete_task": HandlerConfig(
                tool_name="orchestrator_delete_task",
                old_handler=handle_delete_task,
                new_handler=handle_delete_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("DELETE_TASK"),
                description="Delete a task"
            ),
            "orchestrator_cancel_task": HandlerConfig(
                tool_name="orchestrator_cancel_task",
                old_handler=handle_cancel_task,
                new_handler=handle_cancel_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("CANCEL_TASK"),
                description="Cancel an in-progress task"
            ),
            "orchestrator_query_tasks": HandlerConfig(
                tool_name="orchestrator_query_tasks",
                old_handler=handle_query_tasks,
                new_handler=handle_query_tasks_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("QUERY_TASKS"),
                description="Query and filter tasks"
            ),
            "orchestrator_execute_task": HandlerConfig(
                tool_name="orchestrator_execute_task",
                old_handler=handle_execute_task,
                new_handler=handle_execute_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("EXECUTE_TASK"),
                description="Execute a task"
            ),
            "orchestrator_complete_task": HandlerConfig(
                tool_name="orchestrator_complete_task",
                old_handler=handle_complete_task,
                new_handler=handle_complete_task_v2,
                use_new=use_pydantic_handlers or self._check_specific_flag("COMPLETE_TASK"),
                description="Complete a task"
            )
        }
    
    def _check_specific_flag(self, operation: str) -> bool:
        """Check for operation-specific feature flags."""
        env_var = f"MCP_USE_PYDANTIC_{operation}"
        return os.getenv(env_var, "false").lower() == "true"
    
    def get_handler(self, tool_name: str) -> Callable:
        """Get the appropriate handler based on migration configuration."""
        config = self.handler_configs.get(tool_name)
        if not config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Return new or old handler based on configuration
        if config.use_new:
            return config.new_handler
        else:
            return config.old_handler
    
    def get_migration_status(self) -> Dict[str, Dict[str, Any]]:
        """Get the current migration status for all handlers."""
        status = {}
        for tool_name, config in self.handler_configs.items():
            status[tool_name] = {
                "using_new_handler": config.use_new,
                "description": config.description,
                "old_handler": config.old_handler.__name__,
                "new_handler": config.new_handler.__name__
            }
        return status
    
    def enable_handler(self, tool_name: str) -> None:
        """Enable the new handler for a specific tool."""
        if tool_name in self.handler_configs:
            self.handler_configs[tool_name].use_new = True
    
    def disable_handler(self, tool_name: str) -> None:
        """Disable the new handler for a specific tool (revert to old)."""
        if tool_name in self.handler_configs:
            self.handler_configs[tool_name].use_new = False
    
    def enable_all_handlers(self) -> None:
        """Enable all new handlers."""
        for config in self.handler_configs.values():
            config.use_new = True
    
    def disable_all_handlers(self) -> None:
        """Disable all new handlers (revert to old)."""
        for config in self.handler_configs.values():
            config.use_new = False


# Global instance
_migration_manager = HandlerMigrationManager()


def get_migration_manager() -> HandlerMigrationManager:
    """Get the global handler migration manager."""
    return _migration_manager


# Convenience functions
def get_handler_for_tool(tool_name: str) -> Callable:
    """Get the appropriate handler for a tool based on migration settings."""
    return _migration_manager.get_handler(tool_name)


def get_migration_status() -> Dict[str, Dict[str, Any]]:
    """Get the current migration status."""
    return _migration_manager.get_migration_status()


# Environment variable documentation
"""
Migration Environment Variables:

Global Control:
- MCP_USE_PYDANTIC_HANDLERS=true  # Enable all new Pydantic handlers

Individual Control:
- MCP_USE_PYDANTIC_CREATE_TASK=true    # Enable new create task handler
- MCP_USE_PYDANTIC_UPDATE_TASK=true    # Enable new update task handler
- MCP_USE_PYDANTIC_DELETE_TASK=true    # Enable new delete task handler
- MCP_USE_PYDANTIC_CANCEL_TASK=true    # Enable new cancel task handler
- MCP_USE_PYDANTIC_QUERY_TASKS=true    # Enable new query tasks handler
- MCP_USE_PYDANTIC_EXECUTE_TASK=true   # Enable new execute task handler
- MCP_USE_PYDANTIC_COMPLETE_TASK=true  # Enable new complete task handler

Example usage:
# Enable only create and query handlers
export MCP_USE_PYDANTIC_CREATE_TASK=true
export MCP_USE_PYDANTIC_QUERY_TASKS=true

# Enable all handlers
export MCP_USE_PYDANTIC_HANDLERS=true
"""