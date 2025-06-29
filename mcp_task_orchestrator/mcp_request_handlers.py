#!/usr/bin/env python3
"""
Enhanced MCP Server with hang detection and prevention.

This module provides improved versions of the MCP server handlers with
comprehensive hang detection, timeout management, and recovery mechanisms.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp import types

# Import the hang detection system
from ..monitoring.hang_detection import with_hang_detection, hang_protected_operation, get_hang_detection_statistics

logger = logging.getLogger("mcp_task_orchestrator.enhanced_server")


@with_hang_detection("complete_subtask_enhanced", timeout=45.0)
async def handle_complete_subtask_enhanced(args: Dict[str, Any], orchestrator) -> List[types.TextContent]:
    """Enhanced subtask completion handler with comprehensive hang detection."""
    
    task_id = args["task_id"]
    results = args["results"]
    artifacts = args.get("artifacts", [])
    next_action = args["next_action"]
    
    # Ensure artifacts is always a list
    if not isinstance(artifacts, list):
        artifacts = [artifacts] if artifacts else []
    
    logger.info(f"Starting enhanced complete_subtask for {task_id}")
    
    try:
        # Phase 1: Basic subtask update (10s timeout)
        async with hang_protected_operation("subtask_update", timeout=10.0):
            # Get subtask with reduced timeout
            subtask = await asyncio.wait_for(
                orchestrator.state.get_subtask(task_id),
                timeout=5.0
            )
            
            if not subtask:
                raise ValueError(f"Task {task_id} not found")
            
            # Update subtask status
            subtask.status = orchestrator.state.TaskStatus.COMPLETED
            subtask.results = results
            subtask.artifacts = artifacts
            subtask.completed_at = datetime.utcnow()
            
            await asyncio.wait_for(
                orchestrator.state.update_subtask(subtask),
                timeout=5.0
            )
            
        logger.info(f"Phase 1 completed for {task_id}")
        
        # Phase 2: Progress and recommendations (20s timeout)
        async with hang_protected_operation("progress_analysis", timeout=20.0):
            # Use asyncio.gather with overall timeout instead of individual timeouts
            try:
                parent_progress, next_task = await asyncio.wait_for(
                    asyncio.gather(
                        orchestrator._check_parent_task_progress(task_id),
                        orchestrator._get_next_recommended_task(task_id),
                        return_exceptions=True  # Don't fail if one operation fails
                    ),
                    timeout=15.0
                )
                
                # Handle partial failures gracefully
                if isinstance(parent_progress, Exception):
                    logger.warning(f"Failed to get parent progress: {str(parent_progress)}")
                    parent_progress = {"progress": "unknown", "error": "Progress check failed"}
                
                if isinstance(next_task, Exception):
                    logger.warning(f"Failed to get next task: {str(next_task)}")
                    next_task = None
                    
            except asyncio.TimeoutError:
                logger.warning(f"Progress analysis timed out for {task_id}")
                parent_progress = {"progress": "unknown", "error": "Analysis timeout"}
                next_task = None
        
        logger.info(f"Phase 2 completed for {task_id}")
        
        # Build response
        response = {
            "task_id": task_id,
            "status": "completed",
            "results_recorded": True,
            "parent_task_progress": parent_progress,
            "next_recommended_task": next_task,
            "processing_time": "normal",
            "hang_detection_active": True
        }
        
    except asyncio.TimeoutError as e:
        logger.error(f"Enhanced complete_subtask timed out for {task_id}: {str(e)}")
        response = {
            "task_id": task_id,
            "status": "timeout",
            "error": f"Operation timed out: {str(e)}",
            "results_recorded": False,
            "recovery_suggestions": [
                "The operation may still be processing in the background",
                "Check task status in a few moments",
                "If the issue persists, try completing the task again",
                "Consider breaking down the task into smaller components"
            ],
            "hang_detection_active": True
        }
    except Exception as e:
        logger.error(f"Enhanced complete_subtask failed for {task_id}: {str(e)}")
        response = {
            "task_id": task_id,
            "status": "error", 
            "error": str(e),
            "results_recorded": False,
            "hang_detection_active": True
        }
    
    return [types.TextContent(
        type="text",
        text=json.dumps(response, indent=2)
    )]


@with_hang_detection("execute_subtask_enhanced", timeout=25.0)
async def handle_execute_subtask_enhanced(args: Dict[str, Any], orchestrator) -> List[types.TextContent]:
    """Enhanced subtask execution handler with hang detection."""
    
    task_id = args["task_id"]
    logger.info(f"Starting enhanced execute_subtask for {task_id}")
    
    try:
        async with hang_protected_operation("get_specialist_context", timeout=20.0):
            specialist_context = await asyncio.wait_for(
                orchestrator.get_specialist_context(task_id),
                timeout=15.0
            )
        
        return [types.TextContent(
            type="text",
            text=specialist_context
        )]
        
    except asyncio.TimeoutError:
        logger.error(f"Enhanced execute_subtask timed out for {task_id}")
        error_response = {
            "error": "Operation timed out",
            "task_id": task_id,
            "suggestions": [
                "Try again in a few moments",
                "Check system load and database connectivity", 
                "Consider using a different subtask if available"
            ],
            "hang_detection_active": True
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    except Exception as e:
        logger.error(f"Enhanced execute_subtask failed for {task_id}: {str(e)}")
        error_response = {
            "error": str(e),
            "task_id": task_id,
            "hang_detection_active": True
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


async def handle_get_hang_statistics(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get hang detection and monitoring statistics."""
    try:
        stats = get_hang_detection_statistics()
        
        response = {
            "monitoring_status": "active" if stats.get('monitoring_active') else "inactive",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": _generate_recommendations(stats)
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Failed to get hang statistics: {str(e)}")
        error_response = {
            "error": f"Failed to retrieve statistics: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]


def _generate_recommendations(stats: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on hang detection statistics."""
    recommendations = []
    
    hang_detector_stats = stats.get('hang_detector', {})
    db_stats = stats.get('database_monitor', {})
    
    # Check for active hangs
    active_ops = hang_detector_stats.get('active_operations', 0)
    if active_ops > 5:
        recommendations.append(f"High number of active operations ({active_ops}) - consider reducing concurrent load")
    
    # Check for frequent hangs
    total_hangs = hang_detector_stats.get('total_hangs_detected', 0)
    if total_hangs > 10:
        recommendations.append(f"Frequent hangs detected ({total_hangs}) - investigate system performance")
    
    # Check database issues
    lock_timeouts = db_stats.get('total_lock_timeouts', 0)
    if lock_timeouts > 0:
        recommendations.append(f"Database lock timeouts detected ({lock_timeouts}) - check database performance")
    
    deadlocks = db_stats.get('total_deadlocks', 0)
    if deadlocks > 0:
        recommendations.append(f"Database deadlocks detected ({deadlocks}) - review transaction patterns")
    
    if not recommendations:
        recommendations.append("System is operating normally with no hanging issues detected")
    
    return recommendations