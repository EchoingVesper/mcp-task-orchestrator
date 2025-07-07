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

from config import get_config
from .orchestrator.task_orchestration_service import TaskOrchestrator
from .orchestrator.orchestration_state_manager import StateManager
from .orchestrator.specialist_management_service import SpecialistManager
from .orchestrator.artifacts import ArtifactManager
from .db.auto_migration import execute_startup_migration
from .reboot.reboot_tools import REBOOT_TOOLS, REBOOT_TOOL_HANDLERS
from .reboot.reboot_integration import initialize_reboot_system

# DI imports for modern architecture
from .infrastructure.di import (
    ServiceContainer, get_container, set_container, 
    get_service, ServiceResolutionError
)
from .infrastructure.di.service_configuration import (
    configure_all_services, get_default_config
)
from .domain.services import OrchestrationCoordinator

# Configure logging with custom handler to separate INFO from ERROR
import sys

# Initialize configuration system
try:
    config = get_config()
    log_level = config.logging.level.value
except Exception as e:
    # Fallback to environment variable for backwards compatibility
    log_level = os.environ.get("MCP_TASK_ORCHESTRATOR_LOG_LEVEL", "INFO")
    print(f"Warning: Could not load configuration, using fallback: {e}")

# Create a custom logging configuration that sends INFO to stdout and WARN+ to stderr
class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno <= logging.INFO

class WarnFilter(logging.Filter):
    def filter(self, record):
        return record.levelno > logging.INFO

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, log_level))

# Remove default handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Stdout handler for INFO and below
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.addFilter(InfoFilter())
stdout_handler.setFormatter(formatter)
root_logger.addHandler(stdout_handler)

# Stderr handler for WARN and above
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.addFilter(WarnFilter())
stderr_handler.setFormatter(formatter)
root_logger.addHandler(stderr_handler)

logger = logging.getLogger("mcp_task_orchestrator")

# Initialize the MCP server
app = Server("task-orchestrator")

# Global instances - initialized on demand to prevent startup conflicts
_state_manager: Optional[StateManager] = None
_specialist_manager: Optional[SpecialistManager] = None
_orchestrator: Optional[TaskOrchestrator] = None

# DI container management
_use_dependency_injection = False
_di_container: Optional[ServiceContainer] = None
_di_coordinator: Optional[OrchestrationCoordinator] = None


def initialize_database_with_migration(base_dir: str = None, db_path: str = None) -> bool:
    """
    Initialize database with automatic migration support.
    
    This function is called before StateManager initialization to ensure
    the database schema is up to date before any operations begin.
    
    Args:
        base_dir: Base directory for the database (optional)
        db_path: Specific database path (optional)
        
    Returns:
        True if database initialization succeeded, False otherwise
    """
    try:
        # Determine database path using configuration system
        if db_path is None:
            try:
                config = get_config()
                # Try to get from configuration first
                if hasattr(config.paths, 'workspace_dir') and config.paths.workspace_dir:
                    base_dir = config.paths.workspace_dir
                elif hasattr(config.paths, 'data_dir') and config.paths.data_dir:
                    base_dir = config.paths.data_dir
                else:
                    # Fallback to environment variables for backwards compatibility
                    db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
                    if not db_path:
                        if base_dir is None:
                            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
                            if not base_dir:
                                base_dir = os.getcwd()
            except Exception:
                # Fallback to environment variables for backwards compatibility
                db_path = os.environ.get("MCP_TASK_ORCHESTRATOR_DB_PATH")
                if not db_path:
                    if base_dir is None:
                        base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
                        if not base_dir:
                            base_dir = os.getcwd()
            
            if not db_path:
                db_path = os.path.join(base_dir, ".task_orchestrator", "task_orchestrator.db")
        
        # Ensure database directory exists
        from pathlib import Path
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct database URL
        database_url = f"sqlite:///{db_path}"
        
        # Execute migration
        logger.info(f"Checking database schema: {database_url}")
        result = execute_startup_migration(database_url)
        
        if result.success:
            if result.migration_needed:
                logger.info(f"Database migration completed: {result.operations_executed} operations in {result.execution_time_ms}ms")
                
                if result.backup_created and result.backup_info:
                    logger.info(f"Backup created: {result.backup_info.backup_id}")
            else:
                logger.info("Database schema is up to date")
            
            return True
        else:
            logger.error(f"Database migration failed: {result.error_message}")
            if result.warnings:
                for warning in result.warnings:
                    logger.warning(f"Migration warning: {warning}")
            return False
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def enable_dependency_injection(config: Optional[Dict[str, Any]] = None):
    """
    Enable dependency injection for the server.
    
    Args:
        config: Optional configuration for services
    """
    global _use_dependency_injection, _di_container, _di_coordinator
    
    try:
        # Get configuration
        if config is None:
            try:
                config = get_config()
                config = config.__dict__ if hasattr(config, '__dict__') else get_default_config()
            except Exception:
                config = get_default_config()
        
        # Create and configure container
        _di_container = ServiceContainer()
        configure_all_services(_di_container, config)
        
        # Set as global container
        set_container(_di_container)
        
        # Get coordinator
        _di_coordinator = _di_container.get_service(OrchestrationCoordinator)
        
        # Enable DI mode
        _use_dependency_injection = True
        
        logger.info("Dependency injection enabled successfully")
        
    except Exception as e:
        logger.error(f"Failed to enable dependency injection: {e}")
        logger.info("Falling back to legacy singleton mode")
        _use_dependency_injection = False


def disable_dependency_injection():
    """Disable dependency injection and fall back to legacy mode."""
    global _use_dependency_injection, _di_container, _di_coordinator
    
    if _di_container:
        _di_container.dispose()
        _di_container = None
    
    _di_coordinator = None
    _use_dependency_injection = False
    
    logger.info("Dependency injection disabled, using legacy mode")


def get_state_manager() -> StateManager:
    """Get or create the StateManager singleton instance."""
    global _state_manager
    if _state_manager is None:
        # Get base directory for persistence using configuration system
        try:
            config = get_config()
            if hasattr(config.paths, 'workspace_dir') and config.paths.workspace_dir:
                base_dir = config.paths.workspace_dir
            elif hasattr(config.paths, 'data_dir') and config.paths.data_dir:
                base_dir = config.paths.data_dir
            else:
                # Fallback to environment variables for backwards compatibility
                base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
                if not base_dir:
                    base_dir = os.getcwd()
        except Exception:
            # Fallback to environment variables for backwards compatibility
            base_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_BASE_DIR")
            if not base_dir:
                base_dir = os.getcwd()
        
        # Initialize database with migration check before StateManager creation
        migration_success = initialize_database_with_migration(base_dir=base_dir)
        if not migration_success:
            logger.warning("Database migration failed - StateManager may encounter schema issues")
            # Continue with StateManager creation as it may still work with existing schema
        
        _state_manager = StateManager(base_dir=base_dir)
        logger.info(f"Initialized StateManager with persistence in {base_dir}/.task_orchestrator")
    
    return _state_manager


def get_specialist_manager(project_dir: str = None) -> SpecialistManager:
    """Get or create the SpecialistManager singleton instance."""
    global _specialist_manager
    if _specialist_manager is None:
        _specialist_manager = SpecialistManager(project_dir=project_dir)
        logger.info("Initialized SpecialistManager")
    
    return _specialist_manager


def get_orchestrator(project_dir: str = None) -> TaskOrchestrator:
    """Get or create the TaskOrchestrator singleton instance."""
    global _orchestrator
    if _orchestrator is None:
        state_mgr = get_state_manager()
        specialist_mgr = get_specialist_manager(project_dir=project_dir)
        _orchestrator = TaskOrchestrator(state_mgr, specialist_mgr, project_dir=project_dir)
        logger.info("Initialized TaskOrchestrator")
    
    return _orchestrator


def get_orchestration_coordinator() -> OrchestrationCoordinator:
    """
    Get the orchestration coordinator (DI mode only).
    
    Returns:
        OrchestrationCoordinator instance
        
    Raises:
        RuntimeError: If dependency injection is not enabled
    """
    if not _use_dependency_injection or _di_coordinator is None:
        raise RuntimeError("Dependency injection must be enabled to use OrchestrationCoordinator")
    
    return _di_coordinator


def get_orchestrator_hybrid(project_dir: str = None):
    """
    Get orchestrator using DI if enabled, otherwise fall back to legacy.
    
    Args:
        project_dir: Project directory
        
    Returns:
        Either OrchestrationCoordinator (DI mode) or TaskOrchestrator (legacy mode)
    """
    if _use_dependency_injection and _di_coordinator is not None:
        return _di_coordinator
    else:
        return get_orchestrator(project_dir=project_dir)


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available orchestration tools."""
    return [
        types.Tool(
            name="orchestrator_initialize_session",
            description="Initialize a new task orchestration session with guidance for effective task breakdown",
            inputSchema={
                "type": "object",
                "properties": {
                    "working_directory": {
                        "type": "string",
                        "description": "Path where .task_orchestrator should be created. If not specified, uses current working directory."
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
            description="Mark a subtask as complete and store detailed work as artifacts to prevent context limit issues",
            inputSchema={
                "type": "object", 
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the completed subtask"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Brief summary of what was accomplished (for database/UI display)"
                    },
                    "detailed_work": {
                        "type": "string",
                        "description": "Full detailed work content to store as artifacts (code, documentation, analysis, etc.)"
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of original file paths being referenced or created (optional)"
                    },
                    "artifact_type": {
                        "type": "string",
                        "enum": ["code", "documentation", "analysis", "design", "test", "config", "general"],
                        "description": "Type of artifact being created",
                        "default": "general"
                    },
                    "next_action": {
                        "type": "string",
                        "enum": ["continue", "needs_revision", "blocked", "complete"],
                        "description": "What should happen next"
                    },
                    "legacy_artifacts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Legacy artifacts field for backward compatibility (optional)"
                    }
                },
                "required": ["task_id", "summary", "detailed_work", "next_action"]
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
        ),
        types.Tool(
            name="orchestrator_create_generic_task",
            description="Create a new generic task with rich metadata and flexible structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description"
                    },
                    "task_type": {
                        "type": "string",
                        "enum": ["standard", "breakdown", "milestone", "review", "approval", "research", "implementation", "testing", "documentation", "deployment", "custom"],
                        "description": "Type of task",
                        "default": "standard"
                    },
                    "parent_task_id": {
                        "type": "string",
                        "description": "Parent task ID for hierarchy (optional)"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["trivial", "simple", "moderate", "complex", "very_complex"],
                        "description": "Task complexity level",
                        "default": "moderate"
                    },
                    "specialist_type": {
                        "type": "string",
                        "enum": ["analyst", "coder", "tester", "documenter", "reviewer", "architect", "devops", "researcher", "coordinator", "generic"],
                        "description": "Specialist type for assignment (optional)"
                    },
                    "estimated_effort": {
                        "type": "string",
                        "description": "Estimated effort (e.g., '2 hours', '1 day') (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in ISO format (optional)"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context data (optional)"
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of prerequisite task IDs (optional)"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        types.Tool(
            name="orchestrator_update_task",
            description="Update an existing generic task's properties",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description (optional)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "active", "in_progress", "blocked", "completed", "failed", "cancelled", "archived"],
                        "description": "New task status (optional)"
                    },
                    "specialist_type": {
                        "type": "string",
                        "enum": ["analyst", "coder", "tester", "documenter", "reviewer", "architect", "devops", "researcher", "coordinator", "generic"],
                        "description": "New specialist assignment (optional)"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["trivial", "simple", "moderate", "complex", "very_complex"],
                        "description": "New complexity level (optional)"
                    },
                    "estimated_effort": {
                        "type": "string",
                        "description": "New estimated effort (optional)"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "New due date in ISO format (optional)"
                    },
                    "context": {
                        "type": "object",
                        "description": "Updated context data (optional)"
                    }
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="orchestrator_delete_task",
            description="Safely delete a generic task and handle its dependencies",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of task to delete"
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deletion even if task has dependents",
                        "default": false
                    },
                    "archive_instead": {
                        "type": "boolean",
                        "description": "Archive task instead of permanent deletion",
                        "default": true
                    }
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="orchestrator_cancel_task",
            description="Cancel an in-progress generic task gracefully",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of task to cancel"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for cancellation (optional)"
                    },
                    "preserve_work": {
                        "type": "boolean",
                        "description": "Whether to preserve work artifacts",
                        "default": true
                    }
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="orchestrator_query_tasks",
            description="Query and filter generic tasks with advanced search capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["pending", "active", "in_progress", "blocked", "completed", "failed", "cancelled", "archived"]
                        },
                        "description": "Filter by task status (optional)"
                    },
                    "task_type": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["standard", "breakdown", "milestone", "review", "approval", "research", "implementation", "testing", "documentation", "deployment", "custom"]
                        },
                        "description": "Filter by task type (optional)"
                    },
                    "specialist_type": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["analyst", "coder", "tester", "documenter", "reviewer", "architect", "devops", "researcher", "coordinator", "generic"]
                        },
                        "description": "Filter by specialist type (optional)"
                    },
                    "parent_task_id": {
                        "type": "string",
                        "description": "Filter by parent task (optional)"
                    },
                    "complexity": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["trivial", "simple", "moderate", "complex", "very_complex"]
                        },
                        "description": "Filter by complexity level (optional)"
                    },
                    "search_text": {
                        "type": "string",
                        "description": "Search in title and description (optional)"
                    },
                    "created_after": {
                        "type": "string",
                        "description": "Filter tasks created after this date (ISO format) (optional)"
                    },
                    "created_before": {
                        "type": "string",
                        "description": "Filter tasks created before this date (ISO format) (optional)"
                    },
                    "include_children": {
                        "type": "boolean",
                        "description": "Include child tasks in results",
                        "default": false
                    },
                    "include_artifacts": {
                        "type": "boolean",
                        "description": "Include task artifacts in results",
                        "default": false
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="orchestrator_maintenance_coordinator",
            description="Automated maintenance task coordination for task cleanup, validation, and handover preparation",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["scan_cleanup", "validate_structure", "update_documentation", "prepare_handover"],
                        "description": "Type of maintenance action to perform"
                    },
                    "scope": {
                        "type": "string", 
                        "enum": ["current_session", "full_project", "specific_subtask"],
                        "description": "Scope of the maintenance operation",
                        "default": "current_session"
                    },
                    "validation_level": {
                        "type": "string",
                        "enum": ["basic", "comprehensive", "full_audit"],
                        "description": "Level of validation to perform",
                        "default": "basic"
                    },
                    "target_task_id": {
                        "type": "string",
                        "description": "Specific task ID for maintenance (required when scope is 'specific_subtask')"
                    }
                },
                "required": ["action"]
            }
        )
    ] + REBOOT_TOOLS


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
    elif name == "orchestrator_maintenance_coordinator":
        return await handle_maintenance_coordinator(arguments)
    elif name in REBOOT_TOOL_HANDLERS:
        return await REBOOT_TOOL_HANDLERS[name](arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_initialize_session(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle initialization of a new task orchestration session.
    
    Checks for interrupted tasks and offers to resume them.
    """
    # Extract working_directory from args
    working_directory = args.get("working_directory")
    
    # If working_directory is provided, use it; otherwise fall back to project directory detection
    if working_directory:
        # Validate the directory exists
        if not os.path.isdir(working_directory):
            error_response = {
                "error": f"Working directory does not exist: {working_directory}",
                "suggestions": "Please provide a valid directory path or omit the parameter to use auto-detection"
            }
            return [types.TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]
        project_dir = working_directory
        logger.info(f"Using explicit working directory: {project_dir}")
    else:
        # Get project directory using our multi-strategy approach
        project_dir = get_project_directory(args)
    
    # Get orchestrator using hybrid approach (DI if enabled, otherwise legacy)
    orchestrator = get_orchestrator_hybrid(project_dir=project_dir)
    
    # Get orchestration guidance from the orchestrator
    session_context = await orchestrator.initialize_session()
    
    # Get state manager for checking interrupted tasks
    if _use_dependency_injection:
        # In DI mode, get state manager from container
        state_manager = get_service(StateRepository)
        # Convert state repository to legacy interface if needed
        active_tasks = await state_manager.get_all_tasks()
    else:
        # In legacy mode, use singleton
        state_manager = get_state_manager()
        active_tasks = await state_manager.get_all_tasks()
    
    active_parent_tasks = set()
    
    # Get unique parent task IDs
    for task in active_tasks:
        if hasattr(state_manager, '_get_parent_task_id'):
            parent_id = await state_manager._get_parent_task_id(task.task_id)
        else:
            # For DI mode, we'll need to adapt this logic
            parent_id = getattr(task, 'parent_task_id', None)
        if parent_id:
            active_parent_tasks.add(parent_id)
    
    # Format the response for the LLM
    response = {
        "session_initialized": True,
        "working_directory": project_dir,
        "orchestrator_path": os.path.join(project_dir, ".task_orchestrator"),
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
                    if await state_manager._get_parent_task_id(task.task_id) == parent_id
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
    orchestrator = get_orchestrator_hybrid()
    
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
    orchestrator = get_orchestrator_hybrid()
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
    """Handle subtask completion with artifact storage to prevent context limit issues."""
    orchestrator = get_orchestrator_hybrid()
    
    # Extract new parameters
    task_id = args["task_id"]
    summary = args["summary"]
    detailed_work = args["detailed_work"]
    file_paths = args.get("file_paths", [])
    artifact_type = args.get("artifact_type", "general")
    next_action = args["next_action"]
    
    # Legacy support for old format
    legacy_artifacts = args.get("legacy_artifacts", [])
    
    try:
        # Get project directory for artifact manager
        project_dir = get_project_directory(args)
        
        # Initialize artifact manager
        artifact_manager = ArtifactManager(base_dir=project_dir)
        
        # Store the detailed work as an artifact
        artifact_info = artifact_manager.store_artifact(
            task_id=task_id,
            summary=summary,
            detailed_work=detailed_work,
            file_paths=file_paths,
            artifact_type=artifact_type
        )
        
        # Create the artifacts list with the new artifact reference
        artifacts = [artifact_info["accessible_via"]]
        
        # Add legacy artifacts if provided (for backward compatibility)
        if legacy_artifacts:
            artifacts.extend(legacy_artifacts)
        
        # Complete the subtask using the enhanced orchestrator method
        completion_result = await asyncio.wait_for(
            orchestrator.complete_subtask_with_artifacts(
                task_id, summary, artifacts, next_action, artifact_info
            ),
            timeout=30.0
        )
        
        # Enhance the response with artifact information
        completion_result.update({
            "artifact_created": True,
            "artifact_info": {
                "artifact_id": artifact_info["artifact_id"],
                "summary": artifact_info["summary"],
                "artifact_type": artifact_info["artifact_type"],
                "accessible_via": artifact_info["accessible_via"],
                "detailed_work_stored": True
            },
            "context_saving": {
                "detailed_work_length": len(detailed_work),
                "stored_in_filesystem": True,
                "prevents_context_limit": True
            }
        })
        
        logger.info(f"Completed subtask {task_id} with artifact {artifact_info['artifact_id']}")
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout while completing subtask {task_id}")
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
        
        # Try to fallback to legacy method if artifact creation fails
        try:
            logger.info(f"Falling back to legacy completion method for task {task_id}")
            legacy_artifacts_list = legacy_artifacts if legacy_artifacts else [summary]
            
            completion_result = await asyncio.wait_for(
                orchestrator.complete_subtask(task_id, summary, legacy_artifacts_list, next_action),
                timeout=30.0
            )
            
            completion_result.update({
                "artifact_created": False,
                "fallback_used": True,
                "warning": f"Artifact creation failed: {str(e)}",
                "legacy_method_used": True
            })
            
        except Exception as fallback_error:
            logger.error(f"Both artifact and legacy methods failed for task {task_id}: {str(fallback_error)}")
            completion_result = {
                "task_id": task_id,
                "status": "error",
                "error": f"Primary error: {str(e)}, Fallback error: {str(fallback_error)}",
                "results_recorded": False
            }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(completion_result, indent=2)
    )]


async def handle_synthesize_results(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle result synthesis."""
    orchestrator = get_orchestrator_hybrid()
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
    orchestrator = get_orchestrator_hybrid()
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


async def handle_maintenance_coordinator(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle maintenance coordination requests."""
    orchestrator = get_orchestrator_hybrid()
    state_manager = get_state_manager()
    
    action = args["action"]
    scope = args.get("scope", "current_session")
    validation_level = args.get("validation_level", "basic")
    target_task_id = args.get("target_task_id")
    
    try:
        # Import maintenance functionality
        from .orchestrator.maintenance import MaintenanceCoordinator
        
        # Validate that we have the correct types before proceeding
        if not hasattr(state_manager, 'persistence'):
            raise TypeError(f"StateManager object missing 'persistence' attribute. Got type: {type(state_manager)}")
        
        persistence_manager = state_manager.persistence
        if not hasattr(persistence_manager, 'session_scope'):
            raise TypeError(f"Persistence manager missing 'session_scope' method. Got type: {type(persistence_manager)}")
        
        # Initialize maintenance coordinator with the persistence manager
        maintenance = MaintenanceCoordinator(persistence_manager, orchestrator)
        
        # Execute the requested maintenance action
        if action == "scan_cleanup":
            result = await maintenance.scan_and_cleanup(scope, validation_level, target_task_id)
        elif action == "validate_structure":
            result = await maintenance.validate_structure(scope, validation_level, target_task_id)
        elif action == "update_documentation":
            result = await maintenance.update_documentation(scope, validation_level, target_task_id)
        elif action == "prepare_handover":
            result = await maintenance.prepare_handover(scope, validation_level, target_task_id)
        else:
            raise ValueError(f"Unknown maintenance action: {action}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except ImportError:
        # If maintenance module doesn't exist yet, return a placeholder response
        logger.warning("Maintenance coordinator module not yet implemented")
        placeholder_response = {
            "action": action,
            "scope": scope,
            "validation_level": validation_level,
            "status": "pending_implementation",
            "message": "Maintenance coordinator functionality is being implemented",
            "next_steps": [
                "Database schema extensions completed",
                "MCP tool interface ready",
                "Core maintenance logic implementation in progress"
            ]
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(placeholder_response, indent=2)
        )]
        
    except asyncio.TimeoutError:
        logger.error(f"Timeout while executing maintenance action: {action}")
        error_response = {
            "error": "Operation timed out",
            "action": action,
            "suggestions": "Try again with a smaller scope or basic validation level"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except TypeError as e:
        logger.error(f"Type error in maintenance coordinator: {str(e)}")
        error_response = {
            "error": f"Configuration error: {str(e)}",
            "error_type": "TypeError",
            "action": action,
            "scope": scope,
            "troubleshooting": "This indicates a mismatch between expected and actual object types. Server restart may be required."
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        logger.error(f"Error executing maintenance action {action}: {str(e)}")
        error_response = {
            "error": str(e),
            "error_type": type(e).__name__,
            "action": action,
            "scope": scope
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_create_generic_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle creation of a new generic task."""
    # TODO: Implement generic task creation using GenericTask models
    # This will integrate with the database persistence layer
    response = {
        "status": "pending_implementation",
        "message": "Generic task creation handler is being implemented",
        "tool": "orchestrator_create_generic_task",
        "received_args": args
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_update_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle updating an existing generic task."""
    # TODO: Implement generic task update using GenericTask models
    # This will integrate with the database persistence layer
    response = {
        "status": "pending_implementation", 
        "message": "Generic task update handler is being implemented",
        "tool": "orchestrator_update_task",
        "received_args": args
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_delete_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle deletion of a generic task."""
    # TODO: Implement generic task deletion with dependency handling
    # This will integrate with the database persistence layer
    response = {
        "status": "pending_implementation",
        "message": "Generic task deletion handler is being implemented", 
        "tool": "orchestrator_delete_task",
        "received_args": args
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_cancel_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle cancellation of an in-progress generic task."""
    # TODO: Implement generic task cancellation with graceful handling
    # This will integrate with the database persistence layer
    response = {
        "status": "pending_implementation",
        "message": "Generic task cancellation handler is being implemented",
        "tool": "orchestrator_cancel_task", 
        "received_args": args
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def handle_query_tasks(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle querying and filtering generic tasks."""
    # TODO: Implement generic task querying with advanced search capabilities
    # This will integrate with the database persistence layer
    response = {
        "status": "pending_implementation",
        "message": "Generic task querying handler is being implemented",
        "tool": "orchestrator_query_tasks",
        "received_args": args
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


async def main():
    """Async main entry point for the MCP server."""
    try:
        # Log server initialization
        logger.info("Starting MCP Task Orchestrator server...")
        
        # Check if DI should be enabled
        enable_di = os.environ.get("MCP_TASK_ORCHESTRATOR_USE_DI", "true").lower() in ("true", "1", "yes")
        
        if enable_di:
            # Try to enable dependency injection
            try:
                enable_dependency_injection()
                logger.info("Server running in dependency injection mode")
            except Exception as e:
                logger.warning(f"DI initialization failed, using legacy mode: {e}")
                disable_dependency_injection()
        else:
            logger.info("Dependency injection disabled by configuration, using legacy mode")
            disable_dependency_injection()
        
        # Initialize reboot system
        try:
            if _use_dependency_injection:
                # In DI mode, we might need to adapt this
                logger.info("Skipping reboot system in DI mode (needs adaptation)")
            else:
                state_manager = get_state_manager()
                await initialize_reboot_system(state_manager)
                logger.info("Reboot system initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize reboot system: {e}")
        
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
    finally:
        # Cleanup resources
        if _use_dependency_injection and _di_container:
            logger.info("Disposing DI container")
            _di_container.dispose()


def main_sync():
    """Synchronous wrapper for console script entry point."""
    asyncio.run(main())


def get_project_directory(args: Dict[str, Any]) -> str:
    """
    Extract project directory from request metadata or environment.
    
    This function tries multiple strategies to determine the project directory:
    1. From request metadata (VS Code/Cursor/Windsurf can provide this)
    2. From environment variables 
    3. From current working directory
    4. Fall back to a default location
    """
    # Strategy 1: Try to get project directory from request metadata
    # This is a custom extension to the MCP protocol that editors can provide
    metadata = args.get("_metadata", {})
    project_dir = metadata.get("project_directory")
    
    if project_dir and os.path.isdir(project_dir):
        logger.info(f"Using project directory from request metadata: {project_dir}")
        return project_dir
    
    # Strategy 2: Check configuration system and environment variables
    try:
        config = get_config()
        if hasattr(config.paths, 'workspace_dir') and config.paths.workspace_dir:
            if os.path.isdir(config.paths.workspace_dir):
                logger.info(f"Using project directory from configuration: {config.paths.workspace_dir}")
                return config.paths.workspace_dir
    except Exception:
        pass
    
    # Fallback to environment variables (useful for VS Code extensions)
    env_project_dir = os.environ.get("MCP_TASK_ORCHESTRATOR_PROJECT_DIR")
    if env_project_dir and os.path.isdir(env_project_dir):
        logger.info(f"Using project directory from environment: {env_project_dir}")
        return env_project_dir
    
    # Strategy 3: Check common editor environment variables
    # VS Code sets VSCODE_CWD, others might set similar variables
    editor_cwd = (
        os.environ.get("VSCODE_CWD") or
        os.environ.get("CURSOR_CWD") or
        os.environ.get("WINDSURF_CWD")
    )
    if editor_cwd and os.path.isdir(editor_cwd):
        logger.info(f"Using editor working directory: {editor_cwd}")
        return editor_cwd
    
    # Strategy 4: Use current working directory as fallback
    # This ensures artifacts are created where the orchestrator is being run from
    project_dir = os.getcwd()
    logger.info(f"Using current working directory as project directory: {project_dir}")
    return project_dir


if __name__ == "__main__":
    asyncio.run(main())
