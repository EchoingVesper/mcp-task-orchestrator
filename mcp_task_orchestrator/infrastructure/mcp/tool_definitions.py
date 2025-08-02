"""
MCP Tool Definitions for Task Orchestrator

This module contains all MCP tool definitions extracted from the main server file
for better organization and maintainability.
"""

from typing import List
from mcp import types

# Import reboot tools from existing system
from ...reboot.reboot_tools import REBOOT_TOOLS


def get_core_orchestration_tools() -> List[types.Tool]:
    """Get the core task orchestration tools."""
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
        )
    ]


def get_generic_task_tools() -> List[types.Tool]:
    """Get the generic task management tools."""
    return [
        types.Tool(
            name="orchestrator_plan_task",
            description="Create a new task with rich metadata and flexible structure",
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
                        "default": False
                    },
                    "archive_instead": {
                        "type": "boolean",
                        "description": "Archive task instead of permanent deletion",
                        "default": True
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
                        "default": True
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
                        "default": False
                    },
                    "include_artifacts": {
                        "type": "boolean",
                        "description": "Include task artifacts in results",
                        "default": False
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
            name="orchestrator_execute_task",
            description="Get specialist context and prompts for executing a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the task to execute"
                    }
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="orchestrator_complete_task",
            description="Mark a task as complete and store detailed work as artifacts to prevent context limit issues",
            inputSchema={
                "type": "object", 
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "ID of the completed task"
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
        )
    ]


def get_maintenance_tools() -> List[types.Tool]:
    """Get the maintenance and coordination tools."""
    return [
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
    ]


def get_all_tools() -> List[types.Tool]:
    """Get all available MCP tools for the Task Orchestrator."""
    tools = []
    
    # Add core orchestration tools
    tools.extend(get_core_orchestration_tools())
    
    # Add generic task management tools
    tools.extend(get_generic_task_tools())
    
    # Add maintenance tools
    tools.extend(get_maintenance_tools())
    
    # Add template system tools
    from ..template_system.mcp_tools import get_template_tools
    tools.extend(get_template_tools())
    
    # Add reboot tools from existing system
    tools.extend(REBOOT_TOOLS)
    
    return tools