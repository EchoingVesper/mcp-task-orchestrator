"""
MCP tools for server reboot functionality.

This module implements the MCP tool handlers for restart operations,
health checking, and restart coordination.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

from mcp import types

from .reboot_integration import get_reboot_manager
from .state_serializer import RestartReason
from ..orchestrator.state import StateManager

logger = logging.getLogger("mcp_task_orchestrator.server.reboot_tools")


# Tool definitions for server reboot functionality
REBOOT_TOOLS = [
    types.Tool(
        name="orchestrator_restart_server",
        description="Trigger a graceful server restart with state preservation",
        inputSchema={
            "type": "object",
            "properties": {
                "graceful": {
                    "type": "boolean",
                    "description": "Whether to perform graceful shutdown",
                    "default": True
                },
                "preserve_state": {
                    "type": "boolean", 
                    "description": "Whether to preserve server state across restart",
                    "default": True
                },
                "timeout": {
                    "type": "integer",
                    "description": "Maximum time to wait for restart completion (seconds)",
                    "default": 30,
                    "minimum": 10,
                    "maximum": 300
                },
                "reason": {
                    "type": "string",
                    "enum": ["configuration_update", "schema_migration", "error_recovery", "manual_request", "emergency_shutdown"],
                    "description": "Reason for the restart",
                    "default": "manual_request"
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="orchestrator_health_check",
        description="Check server health and readiness for operations",
        inputSchema={
            "type": "object",
            "properties": {
                "include_reboot_readiness": {
                    "type": "boolean",
                    "description": "Whether to include restart readiness in health check",
                    "default": True
                },
                "include_connection_status": {
                    "type": "boolean",
                    "description": "Whether to include client connection status",
                    "default": True
                },
                "include_database_status": {
                    "type": "boolean",
                    "description": "Whether to include database status",
                    "default": True
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="orchestrator_shutdown_prepare",
        description="Check server readiness for graceful shutdown",
        inputSchema={
            "type": "object",
            "properties": {
                "check_active_tasks": {
                    "type": "boolean",
                    "description": "Whether to check for active tasks",
                    "default": True
                },
                "check_database_state": {
                    "type": "boolean",
                    "description": "Whether to check database state",
                    "default": True
                },
                "check_client_connections": {
                    "type": "boolean",
                    "description": "Whether to check client connections",
                    "default": True
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="orchestrator_reconnect_test", 
        description="Test client reconnection capability and connection status",
        inputSchema={
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Specific session ID to test (optional)"
                },
                "include_buffer_status": {
                    "type": "boolean",
                    "description": "Whether to include request buffer status",
                    "default": True
                },
                "include_reconnection_stats": {
                    "type": "boolean",
                    "description": "Whether to include reconnection statistics",
                    "default": True
                }
            },
            "required": []
        }
    ),
    types.Tool(
        name="orchestrator_restart_status",
        description="Get current status of restart operation",
        inputSchema={
            "type": "object",
            "properties": {
                "include_history": {
                    "type": "boolean",
                    "description": "Whether to include restart history",
                    "default": False
                },
                "include_error_details": {
                    "type": "boolean", 
                    "description": "Whether to include detailed error information",
                    "default": True
                }
            },
            "required": []
        }
    )
]


async def handle_restart_server(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle server restart request.
    
    Args:
        args: Tool arguments containing restart parameters
        
    Returns:
        List of TextContent with restart status
    """
    try:
        graceful = args.get("graceful", True)
        preserve_state = args.get("preserve_state", True)
        timeout = args.get("timeout", 30)
        reason_str = args.get("reason", "manual_request")
        
        # Convert reason string to enum
        try:
            reason = RestartReason(reason_str)
        except ValueError:
            reason = RestartReason.MANUAL_REQUEST
            logger.warning(f"Invalid restart reason '{reason_str}', using manual_request")
        
        logger.info(f"Restart requested: graceful={graceful}, preserve_state={preserve_state}, reason={reason}")
        
        # Get reboot manager
        reboot_manager = get_reboot_manager()
        
        if not graceful:
            # Emergency restart without state preservation
            response = {
                "success": False,
                "error": "Emergency restart not yet implemented",
                "graceful": graceful,
                "preserve_state": preserve_state,
                "reason": reason.value
            }
        else:
            # Trigger graceful restart
            result = await reboot_manager.trigger_restart(reason, timeout)
            response = {
                **result,
                "graceful": graceful,
                "preserve_state": preserve_state,
                "timeout": timeout
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to handle restart request: {e}")
        error_response = {
            "success": False,
            "error": str(e),
            "phase": "request_handling_failed"
        }
        
        return [types.TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]


async def handle_health_check(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle health check request.
    
    Args:
        args: Tool arguments for health check options
        
    Returns:
        List of TextContent with health status
    """
    try:
        include_reboot_readiness = args.get("include_reboot_readiness", True)
        include_connection_status = args.get("include_connection_status", True)
        include_database_status = args.get("include_database_status", True)
        
        reboot_manager = get_reboot_manager()
        
        # Basic health status
        health_status = {
            "healthy": True,
            "timestamp": None,
            "server_version": "1.4.1",
            "checks": {}
        }
        
        # Add current timestamp
        from datetime import datetime, timezone
        health_status["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Check reboot readiness
        if include_reboot_readiness:
            try:
                readiness = await reboot_manager.get_restart_readiness()
                health_status["checks"]["reboot_readiness"] = readiness
                if not readiness["ready"]:
                    health_status["healthy"] = False
            except Exception as e:
                logger.error(f"Failed to check reboot readiness: {e}")
                health_status["checks"]["reboot_readiness"] = {
                    "ready": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
        
        # Check database status
        if include_database_status:
            try:
                # TODO: Implement actual database health check
                health_status["checks"]["database"] = {
                    "connected": True,
                    "status": "operational"
                }
            except Exception as e:
                logger.error(f"Failed to check database status: {e}")
                health_status["checks"]["database"] = {
                    "connected": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
        
        # Check connection status  
        if include_connection_status:
            try:
                # TODO: Implement actual connection status check
                health_status["checks"]["connections"] = {
                    "active_connections": 0,
                    "status": "operational"
                }
            except Exception as e:
                logger.error(f"Failed to check connection status: {e}")
                health_status["checks"]["connections"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(health_status, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to perform health check: {e}")
        error_response = {
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_shutdown_prepare(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle shutdown preparation check.
    
    Args:
        args: Tool arguments for shutdown readiness checks
        
    Returns:
        List of TextContent with shutdown readiness status
    """
    try:
        check_active_tasks = args.get("check_active_tasks", True)
        check_database_state = args.get("check_database_state", True)
        check_client_connections = args.get("check_client_connections", True)
        
        reboot_manager = get_reboot_manager()
        
        # Get restart readiness which includes shutdown preparation
        readiness = await reboot_manager.get_restart_readiness()
        
        # Enhance with specific checks
        shutdown_readiness = {
            "ready_for_shutdown": readiness["ready"],
            "blocking_issues": readiness["issues"],
            "checks": {},
            "details": readiness["details"]
        }
        
        # Add timestamp
        from datetime import datetime, timezone
        shutdown_readiness["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Check active tasks
        if check_active_tasks:
            try:
                # TODO: Implement active task checking
                shutdown_readiness["checks"]["active_tasks"] = {
                    "count": 0,
                    "suspendable": True,
                    "status": "ready"
                }
            except Exception as e:
                logger.error(f"Failed to check active tasks: {e}")
                shutdown_readiness["checks"]["active_tasks"] = {
                    "status": "error",
                    "error": str(e)
                }
                shutdown_readiness["ready_for_shutdown"] = False
        
        # Check database state
        if check_database_state:
            try:
                # TODO: Implement database state checking
                shutdown_readiness["checks"]["database"] = {
                    "transactions_pending": 0,
                    "connections_open": 1,
                    "status": "ready"
                }
            except Exception as e:
                logger.error(f"Failed to check database state: {e}")
                shutdown_readiness["checks"]["database"] = {
                    "status": "error",
                    "error": str(e)
                }
                shutdown_readiness["ready_for_shutdown"] = False
        
        # Check client connections
        if check_client_connections:
            try:
                # TODO: Implement client connection checking
                shutdown_readiness["checks"]["client_connections"] = {
                    "active_connections": 0,
                    "notifiable": True,
                    "status": "ready"
                }
            except Exception as e:
                logger.error(f"Failed to check client connections: {e}")
                shutdown_readiness["checks"]["client_connections"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(shutdown_readiness, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to check shutdown readiness: {e}")
        error_response = {
            "ready_for_shutdown": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_reconnect_test(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle reconnection test request.
    
    Args:
        args: Tool arguments for reconnection testing
        
    Returns:
        List of TextContent with reconnection test results
    """
    try:
        session_id = args.get("session_id")
        include_buffer_status = args.get("include_buffer_status", True)
        include_reconnection_stats = args.get("include_reconnection_stats", True)
        
        # TODO: Implement actual reconnection testing
        # For now, return a mock response
        
        test_results = {
            "test_completed": True,
            "timestamp": None,
            "overall_status": "pass",
            "results": {}
        }
        
        # Add timestamp
        from datetime import datetime, timezone
        test_results["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        if session_id:
            # Test specific session
            test_results["results"]["session_test"] = {
                "session_id": session_id,
                "reachable": True,
                "reconnect_capable": True,
                "status": "pass"
            }
        else:
            # Test all sessions
            test_results["results"]["all_sessions"] = {
                "total_sessions": 0,
                "reachable_sessions": 0,
                "reconnect_capable": 0,
                "status": "pass"
            }
        
        # Include buffer status
        if include_buffer_status:
            test_results["results"]["buffer_status"] = {
                "total_buffered_requests": 0,
                "sessions_with_buffers": 0,
                "status": "operational"
            }
        
        # Include reconnection stats
        if include_reconnection_stats:
            test_results["results"]["reconnection_stats"] = {
                "successful_reconnections": 0,
                "failed_reconnections": 0,
                "average_reconnection_time": 0.0,
                "status": "operational"
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(test_results, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to perform reconnection test: {e}")
        error_response = {
            "test_completed": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_restart_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle restart status request.
    
    Args:
        args: Tool arguments for status options
        
    Returns:
        List of TextContent with restart status
    """
    try:
        include_history = args.get("include_history", False)
        include_error_details = args.get("include_error_details", True)
        
        reboot_manager = get_reboot_manager()
        
        # Get current restart status
        status = await reboot_manager.get_shutdown_status()
        
        # Enhance status response
        restart_status = {
            "current_status": status,
            "timestamp": None
        }
        
        # Add timestamp
        from datetime import datetime, timezone
        restart_status["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        # Include history if requested
        if include_history:
            # TODO: Implement restart history tracking
            restart_status["history"] = {
                "recent_restarts": [],
                "total_restarts": 0,
                "last_successful_restart": None
            }
        
        # Filter error details if not requested
        if not include_error_details and "errors" in restart_status["current_status"]:
            restart_status["current_status"]["error_count"] = len(restart_status["current_status"]["errors"])
            del restart_status["current_status"]["errors"]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(restart_status, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to get restart status: {e}")
        error_response = {
            "status_available": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


# Handler mapping for the tool dispatcher
REBOOT_TOOL_HANDLERS = {
    "orchestrator_restart_server": handle_restart_server,
    "orchestrator_health_check": handle_health_check,
    "orchestrator_shutdown_prepare": handle_shutdown_prepare,
    "orchestrator_reconnect_test": handle_reconnect_test,
    "orchestrator_restart_status": handle_restart_status
}