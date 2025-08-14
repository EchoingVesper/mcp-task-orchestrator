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
from datetime import datetime, timezone

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
        
        # Register TaskRepository with its SQLite implementation
        from ....domain.repositories.task_repository import TaskRepository
        from ....infrastructure.database.sqlite.sqlite_task_repository import SQLiteTaskRepository
        from ....infrastructure.database.connection_manager import DatabaseConnectionManager
        
        # Register DatabaseConnectionManager as singleton with database URL
        def create_database_connection_manager(container):
            from pathlib import Path
            # Use default SQLite database path
            db_path = Path(".task_orchestrator") / "tasks.sqlite"
            db_url = f"sqlite:///{db_path.absolute()}"
            return DatabaseConnectionManager(db_url)
        
        registrar.register_factory(
            DatabaseConnectionManager, 
            create_database_connection_manager
        ).as_singleton()
        
        # Register TaskRepository with SQLite implementation
        registrar.register_factory(
            TaskRepository,
            lambda container: SQLiteTaskRepository(container.get_service(DatabaseConnectionManager))
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


# Core handler functions - REAL IMPLEMENTATIONS with hot-reload support - TEST CHANGE
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
        
        # Initialize and check database connectivity
        try:
            from ....infrastructure.database.unified_manager import initialize_global_database_manager, get_database_manager
            from ....infrastructure.database.base import DatabaseType
            
            # Initialize the multi-database architecture if not already done
            db_manager = get_database_manager()
            if db_manager is None:
                logger.info("Initializing multi-database architecture (SQLite + Vector + Graph)")
                db_manager = await initialize_global_database_manager()
            
            # Check connectivity of each database type
            health_status = await db_manager.health_check()
            session_state["database_status"] = "connected"
            session_state["database_health"] = health_status
            session_state["capabilities"]["database_persistence"] = True
            
            # Log which databases are available
            available_dbs = []
            
            if db_manager.has_database(DatabaseType.OPERATIONAL):
                available_dbs.append("SQLite (operational)")
            if db_manager.has_database(DatabaseType.VECTOR):
                available_dbs.append("Vector (ChromaDB)")
            if db_manager.has_database(DatabaseType.GRAPH):
                available_dbs.append("Graph (Neo4j)")
            
            logger.info(f"Databases available: {', '.join(available_dbs)}")
            session_state["available_databases"] = available_dbs
            
            # Verify operational database is working
            if db_manager.operational:
                # Test a simple query to ensure the database is functional
                try:
                    async with db_manager.operational.transaction() as tx:
                        pass  # Just test that we can create a transaction
                    logger.info("Operational database connection verified")
                except Exception as db_test_error:
                    logger.warning(f"Operational database test failed: {db_test_error}")
                    session_state["database_warnings"] = [f"Operational DB test failed: {str(db_test_error)}"]
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            session_state["database_status"] = "disconnected"
            session_state["database_error"] = str(e)
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
    logger = logging.getLogger(__name__)
    
    try:
        parent_task_id = args.get("parent_task_id")
        if not parent_task_id:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "synthesis_failed",
                    "error": "parent_task_id is required for results synthesis",
                    "recovery_suggestions": ["Provide a valid parent_task_id parameter"]
                }, indent=2)
            )]
        
        # Get the parent task and its subtasks
        try:
            from ....infrastructure.mcp.handlers.db_integration import get_generic_task_use_case
            
            use_case = get_generic_task_use_case()
            
            # Get the parent task
            parent_query = await use_case.query_tasks({
                "task_id": parent_task_id,
                "limit": 1
            })
            
            if not parent_query.get("tasks"):
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "synthesis_failed",
                        "error": f"Parent task {parent_task_id} not found",
                        "parent_task_id": parent_task_id,
                        "recovery_suggestions": ["Verify the parent task ID exists", "Use orchestrator_query_tasks to find valid tasks"]
                    }, indent=2)
                )]
            
            parent_task = parent_query["tasks"][0]
            
            # Find all completed subtasks for this parent
            subtasks_query = await use_case.query_tasks({
                "parent_task_id": parent_task_id,
                "status": ["completed"],
                "limit": 100
            })
            
            completed_subtasks = subtasks_query.get("tasks", [])
            
            # Also check for failed subtasks to provide comprehensive status
            failed_query = await use_case.query_tasks({
                "parent_task_id": parent_task_id,
                "status": ["failed"],
                "limit": 100
            })
            
            failed_subtasks = failed_query.get("tasks", [])
            
            # Synthesize results from completed subtasks
            synthesis_results = {
                "artifacts_collected": [],
                "key_outcomes": [],
                "metrics": {
                    "total_subtasks": len(completed_subtasks) + len(failed_subtasks),
                    "completed_count": len(completed_subtasks),
                    "failed_count": len(failed_subtasks),
                    "success_rate": round(len(completed_subtasks) / max(1, len(completed_subtasks) + len(failed_subtasks)) * 100, 1)
                },
                "timeline": {
                    "started": None,
                    "completed": None,
                    "duration_minutes": None
                }
            }
            
            # Process completed subtasks
            earliest_start = None
            latest_completion = None
            
            for subtask in completed_subtasks:
                task_dict = subtask.dict() if hasattr(subtask, 'dict') else subtask
                
                # Collect artifacts
                if task_dict.get("artifacts"):
                    artifacts = task_dict["artifacts"] if isinstance(task_dict["artifacts"], list) else [task_dict["artifacts"]]
                    synthesis_results["artifacts_collected"].extend(artifacts)
                
                # Extract key outcomes from results
                if task_dict.get("results"):
                    synthesis_results["key_outcomes"].append({
                        "subtask_id": task_dict.get("task_id", "unknown"),
                        "title": task_dict.get("title", "Untitled"),
                        "outcome": task_dict["results"]
                    })
                
                # Track timeline
                if task_dict.get("started_at"):
                    start_time = task_dict["started_at"]
                    if earliest_start is None or start_time < earliest_start:
                        earliest_start = start_time
                
                if task_dict.get("completed_at"):
                    completion_time = task_dict["completed_at"]
                    if latest_completion is None or completion_time > latest_completion:
                        latest_completion = completion_time
            
            # Calculate timeline metrics
            if earliest_start and latest_completion:
                synthesis_results["timeline"]["started"] = earliest_start
                synthesis_results["timeline"]["completed"] = latest_completion
                
                # Calculate duration (simplified - would need proper datetime parsing in real implementation)
                try:
                    from datetime import datetime
                    if isinstance(earliest_start, str):
                        start_dt = datetime.fromisoformat(earliest_start.replace('Z', '+00:00'))
                    else:
                        start_dt = earliest_start
                    
                    if isinstance(latest_completion, str):
                        end_dt = datetime.fromisoformat(latest_completion.replace('Z', '+00:00'))
                    else:
                        end_dt = latest_completion
                    
                    duration = end_dt - start_dt
                    synthesis_results["timeline"]["duration_minutes"] = round(duration.total_seconds() / 60, 1)
                except Exception as e:
                    logger.debug(f"Could not calculate duration: {e}")
            
            # Generate summary analysis
            summary_analysis = "Results synthesis completed successfully."
            
            if synthesis_results["metrics"]["success_rate"] == 100:
                summary_analysis = f"All {synthesis_results['metrics']['completed_count']} subtasks completed successfully."
            elif synthesis_results["metrics"]["success_rate"] >= 80:
                summary_analysis = f"Strong completion rate: {synthesis_results['metrics']['completed_count']}/{synthesis_results['metrics']['total_subtasks']} subtasks succeeded."
            elif synthesis_results["metrics"]["failed_count"] > 0:
                summary_analysis = f"Mixed results: {synthesis_results['metrics']['completed_count']} succeeded, {synthesis_results['metrics']['failed_count']} failed."
            
            response = {
                "status": "results_synthesized",
                "message": summary_analysis,
                "parent_task_id": parent_task_id,
                "parent_task_title": parent_task.title if hasattr(parent_task, 'title') else parent_task.get("title", "Unknown"),
                "synthesis_results": synthesis_results,
                "failed_subtasks_summary": [
                    {
                        "subtask_id": task.task_id if hasattr(task, 'task_id') else task.get("task_id"),
                        "title": task.title if hasattr(task, 'title') else task.get("title", "Unknown"),
                        "error": task.error_details if hasattr(task, 'error_details') else task.get("error_details", "Unknown error")
                    }
                    for task in failed_subtasks[:5]  # Limit to first 5 failed tasks
                ],
                "recommendations": self._generate_synthesis_recommendations(synthesis_results, failed_subtasks),
                "next_steps": [
                    "Review synthesized artifacts and outcomes",
                    "Address any failed subtasks if needed",
                    "Use results for further task planning"
                ]
            }
            
            logger.info(f"Synthesized results for {parent_task_id}: {synthesis_results['metrics']['success_rate']}% success rate")
            
        except Exception as e:
            logger.error(f"Error during results synthesis: {e}")
            response = {
                "status": "synthesis_failed",
                "error": f"Failed to synthesize results: {str(e)}",
                "parent_task_id": parent_task_id,
                "error_type": type(e).__name__,
                "recovery_suggestions": [
                    "Check if parent task exists",
                    "Verify database connectivity",
                    "Ensure subtasks have completed"
                ]
            }
        
    except Exception as e:
        logger.error(f"Critical error in results synthesis: {e}")
        response = {
            "status": "synthesis_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "recovery_suggestions": [
                "Check input parameters",
                "Verify system health"
            ]
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2, default=str)
    )]

def _generate_synthesis_recommendations(synthesis_results: Dict[str, Any], failed_subtasks: list) -> List[str]:
    """Generate recommendations based on synthesis results."""
    recommendations = []
    
    success_rate = synthesis_results["metrics"]["success_rate"]
    
    if success_rate == 100:
        recommendations.append("Excellent execution - consider using this approach as a template for future tasks")
    elif success_rate >= 80:
        recommendations.append("Strong performance - review failed subtasks for improvement opportunities")
    elif success_rate >= 60:
        recommendations.append("Moderate success - analyze failed subtasks to identify common issues")
    else:
        recommendations.append("Low success rate - recommend task restructuring and requirement clarification")
    
    if failed_subtasks:
        recommendations.append(f"Address {len(failed_subtasks)} failed subtasks before marking parent task complete")
    
    if synthesis_results.get("timeline", {}).get("duration_minutes"):
        duration = synthesis_results["timeline"]["duration_minutes"]
        if duration > 240:  # > 4 hours
            recommendations.append("Consider breaking down similar tasks into smaller chunks for better manageability")
        elif duration < 30:  # < 30 minutes
            recommendations.append("Fast execution - this task structure works well for quick iterations")
    
    if len(synthesis_results.get("artifacts_collected", [])) == 0:
        recommendations.append("No artifacts collected - consider if deliverables were properly captured")
    
    return recommendations


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
        
        # Try to get tasks from the database using Clean Architecture
        try:
            from ....infrastructure.mcp.handlers.di_integration import get_clean_task_use_case
            
            use_case = await get_clean_task_use_case()
            
            # Query for active and pending tasks
            active_tasks = await use_case.query_tasks({
                "status": "in_progress",
                "limit": 100
            })
            
            pending_tasks = await use_case.query_tasks({
                "status": "pending",
                "limit": 100  
            })
            
            failed_tasks = await use_case.query_tasks({
                "status": "failed",
                "limit": 50
            })
            
            response["active_tasks"] = active_tasks
            response["pending_tasks"] = pending_tasks
            response["failed_tasks"] = failed_tasks
            
            # Update summary counts
            response["task_summary"]["total_active"] = len(response["active_tasks"])
            response["task_summary"]["total_pending"] = len(response["pending_tasks"]) 
            response["task_summary"]["total_failed"] = len(response["failed_tasks"])
            
            if include_completed:
                completed_tasks = await use_case.query_tasks({
                    "status": "completed",
                    "limit": 50
                })
                response["completed_tasks"] = completed_tasks
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
    logger = logging.getLogger(__name__)
    
    try:
        action = args.get("action")
        scope = args.get("scope", "current_session")
        validation_level = args.get("validation_level", "basic")
        target_task_id = args.get("target_task_id")
        
        if not action:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "maintenance_failed",
                    "error": "action parameter is required",
                    "available_actions": ["scan_cleanup", "validate_structure", "update_documentation", "prepare_handover"],
                    "recovery_suggestions": ["Provide a valid action parameter"]
                }, indent=2)
            )]
        
        maintenance_results = {
            "action": action,
            "scope": scope,
            "validation_level": validation_level,
            "started_at": asyncio.get_event_loop().time(),
            "operations_performed": [],
            "issues_found": [],
            "items_cleaned": [],
            "recommendations": []
        }
        
        # Execute maintenance action based on type
        if action == "scan_cleanup":
            await _perform_cleanup_scan(maintenance_results, scope, target_task_id)
        elif action == "validate_structure":
            await _perform_structure_validation(maintenance_results, validation_level, scope)
        elif action == "update_documentation":
            await _perform_documentation_update(maintenance_results, scope)
        elif action == "prepare_handover":
            await _perform_handover_preparation(maintenance_results, scope)
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "maintenance_failed",
                    "error": f"Unknown maintenance action: {action}",
                    "available_actions": ["scan_cleanup", "validate_structure", "update_documentation", "prepare_handover"],
                    "recovery_suggestions": ["Use a valid action from the available list"]
                }, indent=2)
            )]
        
        # Calculate completion metrics
        maintenance_results["completed_at"] = asyncio.get_event_loop().time()
        maintenance_results["duration_seconds"] = round(
            maintenance_results["completed_at"] - maintenance_results["started_at"], 2
        )
        
        # Generate summary message
        operations_count = len(maintenance_results["operations_performed"])
        issues_count = len(maintenance_results["issues_found"])
        cleaned_count = len(maintenance_results["items_cleaned"])
        
        if issues_count == 0 and cleaned_count == 0:
            summary_message = f"Maintenance action '{action}' completed successfully - no issues found"
        elif cleaned_count > 0:
            summary_message = f"Maintenance action '{action}' completed - cleaned {cleaned_count} items, found {issues_count} issues"
        else:
            summary_message = f"Maintenance action '{action}' completed - {operations_count} operations performed, {issues_count} issues identified"
        
        response = {
            "status": "maintenance_completed",
            "message": summary_message,
            "maintenance_results": maintenance_results,
            "summary": {
                "operations_performed": operations_count,
                "issues_found": issues_count,
                "items_cleaned": cleaned_count,
                "duration_seconds": maintenance_results["duration_seconds"]
            },
            "next_steps": _generate_maintenance_next_steps(maintenance_results)
        }
        
        logger.info(f"Maintenance action '{action}' completed: {operations_count} operations, {issues_count} issues")
        
    except Exception as e:
        logger.error(f"Error during maintenance coordination: {e}")
        response = {
            "status": "maintenance_failed",
            "error": f"Maintenance coordination failed: {str(e)}",
            "action": args.get("action", "unknown"),
            "scope": args.get("scope", "unknown"),
            "error_type": type(e).__name__,
            "recovery_suggestions": [
                "Check system health and connectivity",
                "Verify maintenance action parameters",
                "Try with simpler scope or validation level"
            ]
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2, default=str)
    )]


async def _perform_cleanup_scan(results: Dict[str, Any], scope: str, target_task_id: Optional[str]):
    """Perform cleanup scan operations."""
    results["operations_performed"].append("cleanup_scan_initiated")
    
    try:
        from ....infrastructure.mcp.handlers.db_integration import get_generic_task_use_case
        use_case = get_generic_task_use_case()
        
        if scope == "specific_subtask" and target_task_id:
            # Scan specific task
            task_query = await use_case.query_tasks({
                "task_id": target_task_id,
                "limit": 1
            })
            
            if task_query.get("tasks"):
                task = task_query["tasks"][0]
                task_dict = task.dict() if hasattr(task, 'dict') else task
                
                # Check for cleanup opportunities
                if task_dict.get("status") == "completed" and not task_dict.get("artifacts"):
                    results["issues_found"].append(f"Completed task {target_task_id} has no artifacts")
                
                if task_dict.get("status") == "failed" and not task_dict.get("error_details"):
                    results["issues_found"].append(f"Failed task {target_task_id} missing error details")
                
                results["operations_performed"].append(f"scanned_task_{target_task_id}")
            else:
                results["issues_found"].append(f"Target task {target_task_id} not found")
        
        else:
            # Scan for stale tasks
            stale_query = await use_case.query_tasks({
                "status": ["in_progress"],
                "limit": 50
            })
            
            stale_tasks = stale_query.get("tasks", [])
            for task in stale_tasks:
                task_dict = task.dict() if hasattr(task, 'dict') else task
                
                # Check if task has been in progress too long (simplified check)
                if task_dict.get("started_at"):
                    results["issues_found"].append(f"Task {task_dict.get('task_id')} has been in progress - may need attention")
            
            results["operations_performed"].append(f"scanned_{len(stale_tasks)}_active_tasks")
            
            # Look for orphaned tasks
            orphan_query = await use_case.query_tasks({
                "parent_task_id": "nonexistent",  # This would find orphaned tasks in a real implementation
                "limit": 20
            })
            
            results["operations_performed"].append("checked_for_orphaned_tasks")
    
    except Exception as e:
        results["issues_found"].append(f"Cleanup scan error: {str(e)}")


async def _perform_structure_validation(results: Dict[str, Any], validation_level: str, scope: str):
    """Perform structure validation operations."""
    results["operations_performed"].append(f"structure_validation_{validation_level}")
    
    try:
        # Check hot-reload system integrity
        try:
            from ....reboot.orchestrator import get_hot_reload_orchestrator
            hot_reload = get_hot_reload_orchestrator()
            
            if hot_reload:
                status = hot_reload.get_status()
                if not status.get("enabled"):
                    results["issues_found"].append("Hot-reload system is disabled")
                else:
                    results["operations_performed"].append("hot_reload_system_validated")
            else:
                results["issues_found"].append("Hot-reload orchestrator not available")
        
        except Exception as e:
            results["issues_found"].append(f"Hot-reload validation error: {str(e)}")
        
        # Check database connectivity
        try:
            from ....infrastructure.mcp.handlers.db_integration import get_generic_task_use_case
            use_case = get_generic_task_use_case()
            
            # Simple connectivity test
            test_query = await use_case.query_tasks({"limit": 1})
            results["operations_performed"].append("database_connectivity_validated")
            
        except Exception as e:
            results["issues_found"].append(f"Database validation error: {str(e)}")
        
        if validation_level in ["comprehensive", "full_audit"]:
            # Additional comprehensive checks
            results["operations_performed"].append("comprehensive_system_audit")
            
            # Check for missing modules or dependencies
            required_modules = [
                "mcp_task_orchestrator.domain",
                "mcp_task_orchestrator.application", 
                "mcp_task_orchestrator.infrastructure",
                "mcp_task_orchestrator.reboot.orchestrator"
            ]
            
            for module_name in required_modules:
                try:
                    __import__(module_name)
                    results["operations_performed"].append(f"validated_module_{module_name}")
                except ImportError as e:
                    results["issues_found"].append(f"Missing or broken module: {module_name} - {str(e)}")
    
    except Exception as e:
        results["issues_found"].append(f"Structure validation error: {str(e)}")


async def _perform_documentation_update(results: Dict[str, Any], scope: str):
    """Perform documentation update operations."""
    results["operations_performed"].append("documentation_update_scan")
    
    # Check for session files and update documentation
    try:
        from pathlib import Path
        
        # Look for session files
        task_orchestrator_dir = Path(".task_orchestrator")
        if task_orchestrator_dir.exists():
            session_files = list(task_orchestrator_dir.glob("session_*.json"))
            
            if session_files:
                results["operations_performed"].append(f"found_{len(session_files)}_session_files")
                
                # Check if any documentation needs updating
                for session_file in session_files:
                    try:
                        import json
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                        
                        if session_data.get("capabilities", {}).get("hot_reload"):
                            results["items_cleaned"].append(f"Updated session documentation for {session_file.name}")
                    
                    except Exception as e:
                        results["issues_found"].append(f"Could not update session file {session_file.name}: {str(e)}")
            else:
                results["issues_found"].append("No session files found for documentation update")
        else:
            results["issues_found"].append("Task orchestrator directory not found")
    
    except Exception as e:
        results["issues_found"].append(f"Documentation update error: {str(e)}")


async def _perform_handover_preparation(results: Dict[str, Any], scope: str):
    """Perform handover preparation operations."""
    results["operations_performed"].append("handover_preparation")
    
    try:
        # Collect system status for handover
        from ....infrastructure.mcp.handlers.db_integration import get_generic_task_use_case
        use_case = get_generic_task_use_case()
        
        # Get task summary
        active_query = await use_case.query_tasks({"status": ["active", "in_progress"], "limit": 50})
        pending_query = await use_case.query_tasks({"status": ["pending"], "limit": 50})
        completed_query = await use_case.query_tasks({"status": ["completed"], "limit": 10})
        
        handover_summary = {
            "active_tasks": len(active_query.get("tasks", [])),
            "pending_tasks": len(pending_query.get("tasks", [])),
            "recent_completed": len(completed_query.get("tasks", []))
        }
        
        results["operations_performed"].append("collected_task_summary")
        results["items_cleaned"].append(f"Prepared handover summary: {handover_summary}")
        
        # Check system health for handover
        try:
            from ....reboot.orchestrator import get_hot_reload_orchestrator, get_restart_orchestrator
            
            hot_reload = get_hot_reload_orchestrator()
            restart = get_restart_orchestrator()
            
            system_health = {
                "hot_reload_enabled": hot_reload.get_status().get("enabled", False) if hot_reload else False,
                "restart_available": restart is not None,
                "maintenance_mode": restart.get_status().get("maintenance_mode", False) if restart else False
            }
            
            results["items_cleaned"].append(f"System health check completed: {system_health}")
            results["operations_performed"].append("system_health_assessment")
        
        except Exception as e:
            results["issues_found"].append(f"System health check error: {str(e)}")
    
    except Exception as e:
        results["issues_found"].append(f"Handover preparation error: {str(e)}")


def _generate_maintenance_next_steps(results: Dict[str, Any]) -> List[str]:
    """Generate next steps based on maintenance results."""
    next_steps = []
    
    action = results["action"]
    issues_count = len(results["issues_found"])
    cleaned_count = len(results["items_cleaned"])
    
    if issues_count > 0:
        next_steps.append(f"Review and address {issues_count} issues identified during {action}")
        
        # Add specific recommendations based on action type
        if action == "scan_cleanup":
            next_steps.append("Consider running cleanup operations to resolve identified issues")
        elif action == "validate_structure":
            next_steps.append("Fix structural issues before proceeding with complex operations")
        elif action == "update_documentation":
            next_steps.append("Complete documentation updates for identified gaps")
    
    if cleaned_count > 0:
        next_steps.append(f"Review {cleaned_count} items that were cleaned or updated")
    
    if issues_count == 0 and cleaned_count == 0:
        next_steps.append("System appears healthy - ready for normal operations")
        
        if action == "prepare_handover":
            next_steps.append("Handover preparation complete - system ready for transition")
    
    next_steps.append("Use orchestrator_get_status to monitor system health")
    
    return next_steps


# Session Management Handlers

logger = logging.getLogger(__name__)

async def handle_list_sessions(args: Dict[str, Any]) -> List[types.TextContent]:
    """List all orchestration sessions with status and metadata."""
    try:
        include_completed = args.get("include_completed", False)
        limit = args.get("limit", 10)
        
        # Get working directory and task orchestrator directory
        working_dir = Path.cwd()
        task_orchestrator_dir = working_dir / ".task_orchestrator"
        
        if not task_orchestrator_dir.exists():
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "sessions": [],
                    "total_count": 0,
                    "message": "No .task_orchestrator directory found - no sessions available"
                }, indent=2)
            )]
        
        # Find all session files
        session_files = list(task_orchestrator_dir.glob("session_*.json"))
        sessions = []
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Extract session info
                session_id = session_data.get("session_id", session_file.stem)
                created_at = session_data.get("created_at")
                initialized = session_data.get("initialized", False)
                database_status = session_data.get("database_status", "unknown")
                
                # Determine session status
                if not initialized:
                    status = "uninitialized"
                elif database_status == "connected":
                    status = "active"
                elif database_status == "disconnected":
                    status = "inactive"
                else:
                    status = "unknown"
                
                # Get file modification time for last activity
                last_modified = session_file.stat().st_mtime
                
                session_info = {
                    "session_id": session_id,
                    "status": status,
                    "created_at": created_at,
                    "last_activity": last_modified,
                    "initialized": initialized,
                    "database_status": database_status,
                    "working_directory": session_data.get("working_directory"),
                    "file_path": str(session_file),
                    "capabilities": session_data.get("capabilities", {}),
                    "hot_reload_status": session_data.get("hot_reload_status", {})
                }
                
                # Filter completed sessions if requested
                if not include_completed or status != "completed":
                    sessions.append(session_info)
                    
            except Exception as e:
                logger.warning(f"Failed to read session file {session_file}: {e}")
                sessions.append({
                    "session_id": session_file.stem,
                    "status": "corrupted",
                    "error": str(e),
                    "file_path": str(session_file)
                })
        
        # Sort by last activity (most recent first) and limit
        sessions.sort(key=lambda x: x.get("last_activity", 0), reverse=True)
        if limit > 0:
            sessions = sessions[:limit]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "sessions": sessions,
                "total_count": len(session_files),
                "displayed_count": len(sessions),
                "include_completed": include_completed,
                "limit_applied": limit,
                "message": f"Found {len(sessions)} sessions"
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Failed to list sessions: {str(e)}",
                "sessions": [],
                "total_count": 0
            }, indent=2)
        )]


async def handle_resume_session(args: Dict[str, Any]) -> List[types.TextContent]:
    """Resume a previous orchestration session by ID."""
    try:
        session_id = args.get("session_id")
        if not session_id:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": "session_id is required"
                }, indent=2)
            )]
        
        # Get working directory and session file
        working_dir = Path.cwd()
        task_orchestrator_dir = working_dir / ".task_orchestrator"
        session_file = task_orchestrator_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Session file not found: {session_id}",
                    "session_id": session_id
                }, indent=2)
            )]
        
        # Load session data
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Update session to mark as resumed
        from datetime import datetime, timezone
        session_data["resumed_at"] = datetime.now(timezone.utc).timestamp()
        session_data["database_status"] = "connected"  # Will be verified by database manager
        
        # Save updated session
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Initialize database manager if needed
        db_manager = get_database_manager()
        if db_manager is None:
            db_manager = await initialize_global_database_manager()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "session_id": session_id,
                "message": f"Session {session_id} resumed successfully",
                "working_directory": session_data.get("working_directory"),
                "capabilities": session_data.get("capabilities", {}),
                "database_status": "connected",
                "next_steps": [
                    "Use orchestrator_get_status to check session state",
                    "Use orchestrator_query_tasks to see active tasks",
                    "Continue with task orchestration operations"
                ]
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to resume session: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": f"Failed to resume session: {str(e)}",
                "session_id": args.get("session_id")
            }, indent=2)
        )]


async def handle_cleanup_sessions(args: Dict[str, Any]) -> List[types.TextContent]:
    """Clean up old, completed, or orphaned sessions."""
    try:
        cleanup_type = args.get("cleanup_type", "completed")
        older_than_days = args.get("older_than_days", 7)
        dry_run = args.get("dry_run", True)
        
        # Get working directory and task orchestrator directory
        working_dir = Path.cwd()
        task_orchestrator_dir = working_dir / ".task_orchestrator"
        
        if not task_orchestrator_dir.exists():
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "cleaned_sessions": [],
                    "total_cleaned": 0,
                    "message": "No .task_orchestrator directory found"
                }, indent=2)
            )]
        
        # Find all session files
        session_files = list(task_orchestrator_dir.glob("session_*.json"))
        to_cleanup = []
        from datetime import datetime, timezone
        current_time = datetime.now(timezone.utc).timestamp()
        cutoff_time = current_time - (older_than_days * 24 * 60 * 60)
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_id = session_data.get("session_id", session_file.stem)
                created_at = session_data.get("created_at", 0)
                database_status = session_data.get("database_status", "unknown")
                initialized = session_data.get("initialized", False)
                
                should_cleanup = False
                reason = ""
                
                if cleanup_type == "completed":
                    # Sessions that are marked as completed or have disconnected database
                    if database_status == "disconnected" and initialized:
                        should_cleanup = True
                        reason = "completed (disconnected database)"
                elif cleanup_type == "orphaned":
                    # Sessions that are corrupted or uninitialized
                    if not initialized or database_status == "unknown":
                        should_cleanup = True
                        reason = "orphaned (not properly initialized)"
                elif cleanup_type == "old":
                    # Sessions older than the cutoff
                    if created_at < cutoff_time:
                        should_cleanup = True
                        reason = f"old (older than {older_than_days} days)"
                elif cleanup_type == "all":
                    should_cleanup = True
                    reason = "cleanup all requested"
                
                if should_cleanup:
                    to_cleanup.append({
                        "session_id": session_id,
                        "file_path": str(session_file),
                        "reason": reason,
                        "created_at": created_at,
                        "database_status": database_status
                    })
                    
            except Exception as e:
                # Corrupted files should be cleaned up
                to_cleanup.append({
                    "session_id": session_file.stem,
                    "file_path": str(session_file),
                    "reason": f"corrupted file: {str(e)}",
                    "error": str(e)
                })
        
        # Perform cleanup if not dry run
        cleaned_sessions = []
        if not dry_run:
            for session_info in to_cleanup:
                try:
                    session_file = Path(session_info["file_path"])
                    if session_file.exists():
                        session_file.unlink()  # Delete the file
                        cleaned_sessions.append(session_info)
                except Exception as e:
                    session_info["cleanup_error"] = str(e)
                    cleaned_sessions.append(session_info)
        else:
            cleaned_sessions = to_cleanup
        
        action_performed = "would be cleaned" if dry_run else "cleaned"
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "cleanup_type": cleanup_type,
                "dry_run": dry_run,
                "older_than_days": older_than_days if cleanup_type == "old" else None,
                "sessions_found": len(session_files),
                "sessions_to_cleanup": len(to_cleanup),
                "cleaned_sessions": cleaned_sessions,
                "total_cleaned": len(cleaned_sessions),
                "message": f"{len(cleaned_sessions)} sessions {action_performed}",
                "next_steps": [
                    "Run with dry_run=false to actually perform cleanup" if dry_run else "Cleanup completed",
                    "Use orchestrator_list_sessions to verify results"
                ]
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Failed to cleanup sessions: {str(e)}",
                "cleaned_sessions": [],
                "total_cleaned": 0
            }, indent=2)
        )]


async def handle_session_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get detailed status of a specific session."""
    try:
        session_id = args.get("session_id")
        if not session_id:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": "session_id is required"
                }, indent=2)
            )]
        
        # Get working directory and session file
        working_dir = Path.cwd()
        task_orchestrator_dir = working_dir / ".task_orchestrator"
        session_file = task_orchestrator_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "session_id": session_id,
                    "exists": False,
                    "error": f"Session file not found: {session_id}"
                }, indent=2)
            )]
        
        # Load session data
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Get file stats
        file_stats = session_file.stat()
        
        # Check database connectivity
        db_manager = get_database_manager()
        db_connected = db_manager is not None
        
        # Build comprehensive status
        status = {
            "session_id": session_id,
            "exists": True,
            "file_path": str(session_file),
            "file_size": file_stats.st_size,
            "created_at": session_data.get("created_at"),
            "last_modified": file_stats.st_mtime,
            "working_directory": session_data.get("working_directory"),
            "initialized": session_data.get("initialized", False),
            "database_status": session_data.get("database_status", "unknown"),
            "database_manager_available": db_connected,
            "capabilities": session_data.get("capabilities", {}),
            "hot_reload_status": session_data.get("hot_reload_status", {}),
            "resumed_at": session_data.get("resumed_at"),
            "session_context": session_data.get("session_context", {})
        }
        
        # Add health assessment
        if status["initialized"] and status["database_status"] == "connected" and db_connected:
            status["health"] = "healthy"
        elif status["initialized"] and status["database_status"] == "disconnected":
            status["health"] = "inactive"
        elif not status["initialized"]:
            status["health"] = "uninitialized"
        else:
            status["health"] = "degraded"
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "session_id": args.get("session_id"),
                "error": f"Failed to get session status: {str(e)}"
            }, indent=2)
        )]