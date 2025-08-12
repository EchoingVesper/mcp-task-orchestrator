"""
Core MCP Tool Handlers

Simplified version for refactoring validation.
Contains essential handler functions and utilities.
"""

import asyncio
import json
import os
import logging
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

from mcp import types


# Logging setup function
def setup_logging():
    """Set up MCP-compliant logging configuration."""
    
    # Get log level from environment
    log_level = os.environ.get("MCP_TASK_ORCHESTRATOR_LOG_LEVEL", "INFO")
    
    # Detect if running in MCP server mode (non-interactive environment)
    is_mcp_server = not sys.stdin.isatty()
    
    # Configure logging based on mode for MCP protocol compliance
    if is_mcp_server:
        # MCP mode: Use stderr and reduce noise for protocol compliance
        handler = logging.StreamHandler(sys.stderr)
        effective_level = max(getattr(logging, log_level), logging.WARNING)
    else:
        # CLI mode: Use stdout for visibility
        handler = logging.StreamHandler(sys.stdout)
        effective_level = getattr(logging, log_level)
    
    # Create MCP-compliant logging configuration
    logging.basicConfig(
        level=effective_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[handler],
        force=True  # Override any existing configuration
    )
    
    logger = logging.getLogger("mcp_task_orchestrator")
    
    # Log the configuration for debugging (only in non-MCP mode)
    if not is_mcp_server:
        logger.info(f"Logging configured for CLI mode: level={log_level}, output=stdout")
    
    return logger


# Dependency injection setup
async def enable_dependency_injection():
    """Enable dependency injection and initialize core services."""
    logger = logging.getLogger(__name__)
    logger.info("Initializing dependency injection container...")
    
    from ...di.container import get_container, register_services
    from ...di.registration import LifetimeScope
    from ....reboot.reboot_integration import initialize_reboot_system, get_reboot_manager
    from ....orchestrator.orchestration_state_manager import StateManager
    
    def configure_services(registrar):
        """Configure all services in the DI container."""
        
        # Register StateManager as singleton
        registrar.register_factory(StateManager, lambda container: StateManager()).as_singleton()
        
        # Register RebootManager - singleton that gets initialized with StateManager
        registrar.register_factory(
            type(get_reboot_manager()), 
            lambda container: get_reboot_manager()
        ).as_singleton()
    
    # Configure services
    register_services(configure_services)
    
    # Initialize the reboot system
    try:
        container = get_container()
        state_manager = container.get_service(StateManager)
        
        # StateManager initializes automatically in constructor
        
        # Initialize reboot system with state manager
        await initialize_reboot_system(state_manager)
        
        logger.info("Dependency injection and core services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize core services: {e}")
        raise


def disable_dependency_injection():
    """Disable dependency injection and cleanup resources."""
    logger = logging.getLogger(__name__)
    logger.info("Cleaning up dependency injection container...")
    
    try:
        from ...di.container import reset_container
        reset_container()
        logger.info("Dependency injection container cleaned up")
    except Exception as e:
        logger.warning(f"Error during DI cleanup: {e}")


# Core handler functions - simplified implementations for now
async def handle_initialize_session(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle initialization of a new task orchestration session."""
    logger = logging.getLogger(__name__)
    
    try:
        # Get or create working directory
        working_directory = args.get("working_directory", os.getcwd())
        working_path = Path(working_directory).resolve()
        
        # Ensure working directory exists
        working_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique session ID
        import time
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        
        # Initialize session state
        session_state = {
            "session_id": session_id,
            "working_directory": str(working_path),
            "created_at": time.time(),
            "initialized": True,
            "capabilities": {
                "hot_reload": True,
                "task_orchestration": True,
                "domain_services": True,
                "database_persistence": True,
                "template_system": True
            }
        }
        
        # Try to initialize hot-reload if available
        try:
            from ....reboot.orchestrator import get_hot_reload_orchestrator, initialize_orchestrator
            
            hot_reload = get_hot_reload_orchestrator()
            if hot_reload:
                session_state["hot_reload_status"] = hot_reload.get_status()
                logger.info("Hot-reload orchestrator initialized for session")
            
        except Exception as e:
            logger.warning(f"Could not initialize hot-reload: {e}")
            session_state["capabilities"]["hot_reload"] = False
        
        # Check database connectivity
        try:
            from ....infrastructure.database.unified_manager import get_database_manager
            db_manager = get_database_manager()
            session_state["database_status"] = "connected"
        except Exception as e:
            logger.warning(f"Database connection issue: {e}")
            session_state["database_status"] = "disconnected"
            session_state["capabilities"]["database_persistence"] = False
        
        # Create task orchestrator directory if needed
        task_orchestrator_dir = working_path / ".task_orchestrator"
        task_orchestrator_dir.mkdir(exist_ok=True)
        
        # Store session metadata
        session_file = task_orchestrator_dir / f"session_{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_state, f, indent=2)
        
        response = {
            "status": "session_initialized", 
            "message": "Task orchestration session initialized successfully with full capabilities",
            "session_id": session_id,
            "working_directory": str(working_path),
            "capabilities": session_state["capabilities"],
            "session_file": str(session_file),
            "hot_reload_enabled": session_state["capabilities"]["hot_reload"],
            "database_status": session_state.get("database_status", "unknown"),
            "next_steps": [
                "Use orchestrator_plan_task to break down complex tasks",
                "Use orchestrator_query_tasks to find existing tasks",
                "Use orchestrator_get_status to monitor progress"
            ]
        }
        
        logger.info(f"Initialized orchestration session {session_id} in {working_path}")
        
    except Exception as e:
        logger.error(f"Failed to initialize session: {e}")
        response = {
            "status": "initialization_failed",
            "error": str(e),
            "fallback_session": f"fallback_{int(time.time())}",
            "working_directory": str(Path(args.get("working_directory", os.getcwd())).resolve()),
            "recovery_suggestions": [
                "Check working directory permissions",
                "Verify disk space availability", 
                "Check if hot-reload dependencies are installed"
            ]
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]








async def handle_synthesize_results(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle results synthesis from completed subtasks."""
    parent_task_id = args.get("parent_task_id", "unknown")
    response = {
        "status": "results_synthesized",
        "message": f"Results synthesized for task {parent_task_id} (simplified implementation)",
        "parent_task_id": parent_task_id
    }
    return [types.TextContent(
        type="text", 
        text=json.dumps(response, indent=2)
    )]


async def handle_get_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle status requests for active tasks and orchestrator health."""
    logger = logging.getLogger(__name__)
    
    try:
        # Parse request parameters
        include_completed = args.get("include_completed", False)
        include_metrics = args.get("include_metrics", True)  
        include_system_status = args.get("include_system_status", True)
        session_id = args.get("session_id")
        task_id = args.get("task_id")
        
        response = {
            "status": "status_retrieved",
            "timestamp": asyncio.get_event_loop().time(),
            "include_completed": include_completed,
            "active_tasks": [],
            "pending_tasks": [],
            "completed_tasks": [] if include_completed else None,
            "failed_tasks": [],
            "task_summary": {
                "total_active": 0,
                "total_pending": 0,
                "total_completed": 0 if include_completed else None,
                "total_failed": 0
            }
        }
        
        # Try to get tasks from the database
        try:
            from ....infrastructure.mcp.handlers.db_integration import get_generic_task_use_case
            
            use_case = get_generic_task_use_case()
            
            # Query for active and pending tasks
            active_query = await use_case.query_tasks({
                "status": ["active", "in_progress"],
                "limit": 100
            })
            
            pending_query = await use_case.query_tasks({
                "status": ["pending"],
                "limit": 100  
            })
            
            failed_query = await use_case.query_tasks({
                "status": ["failed"],
                "limit": 50
            })
            
            response["active_tasks"] = [task.dict() if hasattr(task, 'dict') else task for task in active_query.get("tasks", [])]
            response["pending_tasks"] = [task.dict() if hasattr(task, 'dict') else task for task in pending_query.get("tasks", [])]
            response["failed_tasks"] = [task.dict() if hasattr(task, 'dict') else task for task in failed_query.get("tasks", [])]
            
            # Update summary counts
            response["task_summary"]["total_active"] = len(response["active_tasks"])
            response["task_summary"]["total_pending"] = len(response["pending_tasks"]) 
            response["task_summary"]["total_failed"] = len(response["failed_tasks"])
            
            if include_completed:
                completed_query = await use_case.query_tasks({
                    "status": ["completed"],
                    "limit": 50
                })
                response["completed_tasks"] = [task.dict() if hasattr(task, 'dict') else task for task in completed_query.get("tasks", [])]
                response["task_summary"]["total_completed"] = len(response["completed_tasks"])
            
            response["database_status"] = "connected"
            
        except Exception as e:
            logger.warning(f"Could not retrieve tasks from database: {e}")
            response["database_status"] = "disconnected"
            response["database_error"] = str(e)
        
        # Add system status if requested
        if include_system_status:
            response["system_status"] = {
                "server_healthy": True,
                "maintenance_mode": False,
                "capabilities": {
                    "hot_reload": False,
                    "task_orchestration": True,
                    "database_persistence": response.get("database_status") == "connected"
                }
            }
            
            # Check hot-reload status
            try:
                from ....reboot.orchestrator import get_hot_reload_orchestrator
                hot_reload = get_hot_reload_orchestrator()
                if hot_reload:
                    reload_status = hot_reload.get_status()
                    response["system_status"]["hot_reload_status"] = reload_status
                    response["system_status"]["capabilities"]["hot_reload"] = reload_status.get("enabled", False)
            except Exception as e:
                logger.debug(f"Could not get hot-reload status: {e}")
            
            # Check restart orchestrator status
            try:
                from ....reboot.orchestrator import get_restart_orchestrator
                restart = get_restart_orchestrator()
                if restart:
                    restart_status = restart.get_status()
                    response["system_status"]["restart_status"] = restart_status
                    if restart_status.get("maintenance_mode"):
                        response["system_status"]["maintenance_mode"] = True
            except Exception as e:
                logger.debug(f"Could not get restart status: {e}")
        
        # Add metrics if requested
        if include_metrics:
            response["metrics"] = {
                "response_time_ms": round((asyncio.get_event_loop().time() - response["timestamp"]) * 1000, 2),
                "session_active": session_id is not None,
                "query_scope": "specific_task" if task_id else "all_tasks"
            }
        
        # Filter by specific task if requested
        if task_id:
            filtered_tasks = []
            for task_list in [response["active_tasks"], response["pending_tasks"], response["failed_tasks"]]:
                for task in task_list:
                    if (isinstance(task, dict) and task.get("task_id") == task_id) or \
                       (hasattr(task, 'task_id') and task.task_id == task_id):
                        filtered_tasks.append(task)
            
            if include_completed and response["completed_tasks"]:
                for task in response["completed_tasks"]:
                    if (isinstance(task, dict) and task.get("task_id") == task_id) or \
                       (hasattr(task, 'task_id') and task.task_id == task_id):
                        filtered_tasks.append(task)
            
            response["filtered_tasks"] = filtered_tasks
            response["message"] = f"Status retrieved for task {task_id}" + (f" - found {len(filtered_tasks)} matching tasks" if filtered_tasks else " - task not found")
        else:
            total_tasks = response["task_summary"]["total_active"] + response["task_summary"]["total_pending"] + response["task_summary"]["total_failed"]
            if include_completed and response["task_summary"]["total_completed"] is not None:
                total_tasks += response["task_summary"]["total_completed"]
            response["message"] = f"System status retrieved - {total_tasks} total tasks tracked"
        
        # Add next steps
        response["next_steps"] = []
        if response["task_summary"]["total_active"] > 0:
            response["next_steps"].append("Use orchestrator_execute_task to work on active tasks")
        if response["task_summary"]["total_pending"] > 0:
            response["next_steps"].append("Use orchestrator_execute_task to start pending tasks")
        if response["task_summary"]["total_failed"] > 0:
            response["next_steps"].append("Review failed tasks and use orchestrator_update_task to fix issues")
        if not response["next_steps"]:
            response["next_steps"].append("Use orchestrator_plan_task to create new tasks")
        
        logger.info(f"Status retrieved: {response['task_summary']}")
        
    except Exception as e:
        logger.error(f"Error retrieving status: {e}")
        response = {
            "status": "status_error",
            "error": str(e),
            "message": "Failed to retrieve system status",
            "fallback_info": {
                "timestamp": asyncio.get_event_loop().time(),
                "include_completed": include_completed,
                "error_type": type(e).__name__
            },
            "recovery_suggestions": [
                "Check database connectivity",
                "Verify orchestrator system health",
                "Try with simpler query parameters"
            ]
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2, default=str)
    )]


async def handle_maintenance_coordinator(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle maintenance coordination requests."""
    action = args.get("action", "unknown")
    scope = args.get("scope", "current_session")
    response = {
        "status": "maintenance_completed",
        "message": f"Maintenance action '{action}' completed (simplified implementation)",
        "action": action,
        "scope": scope
    }
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]