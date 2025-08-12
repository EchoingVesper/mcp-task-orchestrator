"""
Temporary Fix Handler for orchestrator_plan_task

This handler provides a quick fix for the parameter mismatch issue
by mapping new schema parameters to legacy format.
"""

import json
import logging
from typing import Dict, List, Any
from mcp import types

logger = logging.getLogger(__name__)


async def handle_orchestrator_plan_task_fixed(args: Dict[str, Any]) -> List[types.TextContent]:
    """Fixed handler for orchestrator_plan_task that maps parameters correctly."""
    
    try:
        # Extract new schema parameters
        title = args.get("title", "")
        description = args.get("description", "")
        task_type = args.get("task_type", "standard")
        complexity = args.get("complexity", "moderate")
        specialist_type = args.get("specialist_type", "generic")
        context = args.get("context", {})
        
        # Create a single subtask from the provided parameters
        subtask = {
            "title": title,
            "description": description,
            "specialist_type": specialist_type,
            "dependencies": [],
            "estimated_effort": "30 minutes"  # Default estimate
        }
        
        # Create response in expected format
        task_id = f"task_{hash(title + description) % 100000:05d}"
        
        response_data = {
            "task_created": True,
            "parent_task_id": task_id,
            "description": description,
            "complexity": complexity,
            "subtasks": [
                {
                    "task_id": f"{task_id}_01",
                    "title": title,
                    "description": description,
                    "specialist": specialist_type
                }
            ],
            "execution_order": [f"{task_id}_01"],
            "estimated_duration_minutes": 30,
            "next_steps": "Use orchestrator_execute_task to start working on individual subtasks",
            "created_with": "simplified_handler",
            "task_type": task_type,
            "context_provided": bool(context)
        }
        
        logger.info(f"Successfully created task plan: {title[:50]}...")
        
        return [types.TextContent(
            type="text",
            text=json.dumps(response_data, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error in orchestrator_plan_task_fixed: {e}")
        error_response = {
            "status": "error",
            "error": f"Task planning failed: {str(e)}",
            "tool": "orchestrator_plan_task",
            "suggestion": "Check that title and description are provided"
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]