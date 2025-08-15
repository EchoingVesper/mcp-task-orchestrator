"""
MCP Tools for Auto-Append System

Provides MCP tool interface for managing auto-append rules,
monitoring executions, and configuring security controls.
"""

import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from mcp import types

from .auto_append_engine import (
    AutoAppendEngine, AutoAppendRule, TaskDefinition, 
    AutoAppendRuleStatus, TaskCreationMode, get_auto_append_engine
)
from .condition_evaluator import (
    ConditionEvaluator, LogicalExpression, Condition,
    ConditionType, Operator, LogicalOperator
)
from .event_system import EventType
from .security_controls import get_security_manager

logger = logging.getLogger(__name__)


async def handle_auto_append_create_rule(args: Dict[str, Any]) -> List[types.TextContent]:
    """Create a new auto-append rule."""
    try:
        engine = get_auto_append_engine()
        security_manager = get_security_manager()
        
        # Parse required fields
        name = args.get("name")
        description = args.get("description")
        trigger_events = args.get("trigger_events", [])
        condition_data = args.get("condition")
        creation_mode = args.get("creation_mode", "direct")
        
        if not all([name, description, trigger_events, condition_data]):
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "Missing required fields: name, description, trigger_events, condition"
                }, indent=2)
            )]
        
        # Parse trigger events
        try:
            parsed_events = {EventType(event) for event in trigger_events}
        except ValueError as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Invalid trigger event: {e}"
                }, indent=2)
            )]
        
        # Parse condition
        try:
            condition = LogicalExpression.from_dict(condition_data)
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Invalid condition format: {e}"
                }, indent=2)
            )]
        
        # Parse creation mode
        try:
            mode = TaskCreationMode(creation_mode)
        except ValueError:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Invalid creation mode: {creation_mode}. Must be one of: direct, template, clone"
                }, indent=2)
            )]
        
        # Create rule
        rule = AutoAppendRule(
            rule_id=args.get("rule_id", str(uuid.uuid4())),
            name=name,
            description=description,
            trigger_events=parsed_events,
            condition=condition,
            creation_mode=mode,
            priority=args.get("priority", 100),
            max_executions=args.get("max_executions"),
            cooldown_minutes=args.get("cooldown_minutes", 0),
            created_by=args.get("created_by", "user")
        )
        
        # Handle creation mode specific data
        if mode == TaskCreationMode.DIRECT:
            task_def_data = args.get("task_definition")
            if not task_def_data:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": "Direct creation mode requires task_definition"
                    }, indent=2)
                )]
            
            rule.task_definition = TaskDefinition(
                title=task_def_data.get("title", "Auto-created Task"),
                description=task_def_data.get("description", ""),
                task_type=task_def_data.get("task_type", "standard"),
                specialist_type=task_def_data.get("specialist_type", "generic"),
                complexity=task_def_data.get("complexity", "moderate"),
                parent_task_id=task_def_data.get("parent_task_id"),
                dependencies=task_def_data.get("dependencies", []),
                estimated_effort=task_def_data.get("estimated_effort"),
                due_date=task_def_data.get("due_date"),
                metadata=task_def_data.get("metadata", {})
            )
        
        elif mode == TaskCreationMode.TEMPLATE:
            rule.template_id = args.get("template_id")
            rule.template_parameters = args.get("template_parameters", {})
            if not rule.template_id:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": "Template creation mode requires template_id"
                    }, indent=2)
                )]
        
        elif mode == TaskCreationMode.CLONE:
            rule.clone_task_id = args.get("clone_task_id")
            if not rule.clone_task_id:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": "Clone creation mode requires clone_task_id"
                    }, indent=2)
                )]
        
        # Security validation
        auth_result = security_manager.validate_and_authorize_rule(rule)
        if not auth_result["authorized"]:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "Security validation failed",
                    "issues": auth_result["issues"]
                }, indent=2)
            )]
        
        # Add rule to engine
        engine.add_rule(rule)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "message": f"Auto-append rule '{name}' created successfully",
                "rule_id": rule.rule_id,
                "security_warnings": auth_result.get("warnings", [])
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error creating auto-append rule: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


async def handle_auto_append_list_rules(args: Dict[str, Any]) -> List[types.TextContent]:
    """List auto-append rules with optional filtering."""
    try:
        engine = get_auto_append_engine()
        
        # Parse filters
        status_filter = args.get("status")
        if status_filter:
            try:
                status = AutoAppendRuleStatus(status_filter)
                rules = engine.list_rules(status)
            except ValueError:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "error": f"Invalid status filter: {status_filter}"
                    }, indent=2)
                )]
        else:
            rules = engine.list_rules()
        
        # Format rules for output
        rules_data = []
        for rule in rules:
            rule_info = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "status": rule.status.value,
                "trigger_events": [e.value for e in rule.trigger_events],
                "creation_mode": rule.creation_mode.value,
                "priority": rule.priority,
                "execution_count": rule.execution_count,
                "max_executions": rule.max_executions,
                "cooldown_minutes": rule.cooldown_minutes,
                "last_execution": rule.last_execution.isoformat() if rule.last_execution else None,
                "created_at": rule.created_at.isoformat(),
                "created_by": rule.created_by
            }
            rules_data.append(rule_info)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "total_rules": len(rules_data),
                "rules": rules_data
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error listing auto-append rules: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


async def handle_auto_append_get_rule(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get detailed information about a specific rule."""
    try:
        engine = get_auto_append_engine()
        
        rule_id = args.get("rule_id")
        if not rule_id:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "rule_id is required"
                }, indent=2)
            )]
        
        rule = engine.get_rule(rule_id)
        if not rule:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Rule not found: {rule_id}"
                }, indent=2)
            )]
        
        # Convert rule to detailed dict
        rule_data = rule.to_dict()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "rule": rule_data
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting auto-append rule: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


async def handle_auto_append_delete_rule(args: Dict[str, Any]) -> List[types.TextContent]:
    """Delete an auto-append rule."""
    try:
        engine = get_auto_append_engine()
        
        rule_id = args.get("rule_id")
        if not rule_id:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "rule_id is required"
                }, indent=2)
            )]
        
        success = engine.remove_rule(rule_id)
        if success:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "message": f"Rule {rule_id} deleted successfully"
                }, indent=2)
            )]
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Rule not found: {rule_id}"
                }, indent=2)
            )]
        
    except Exception as e:
        logger.error(f"Error deleting auto-append rule: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


async def handle_auto_append_get_statistics(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get auto-append engine statistics and monitoring data."""
    try:
        engine = get_auto_append_engine()
        security_manager = get_security_manager()
        
        # Get engine statistics
        engine_stats = engine.get_statistics()
        
        # Get security status
        security_status = security_manager.get_security_status()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "engine_statistics": engine_stats,
                "security_status": security_status
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting auto-append statistics: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


async def handle_auto_append_test_condition(args: Dict[str, Any]) -> List[types.TextContent]:
    """Test a condition against sample data."""
    try:
        evaluator = ConditionEvaluator()
        
        condition_data = args.get("condition")
        sample_event_data = args.get("sample_event", {})
        sample_task_data = args.get("sample_task", {})
        
        if not condition_data:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": "condition is required"
                }, indent=2)
            )]
        
        # Parse condition
        try:
            if "operator" in condition_data and "conditions" in condition_data:
                # Logical expression
                condition = LogicalExpression.from_dict(condition_data)
                # Create a mock event for testing
                from .event_system import TaskEvent, EventType
                mock_event = TaskEvent(
                    event_type=EventType(sample_event_data.get("event_type", "task_completed")),
                    task_id=sample_event_data.get("task_id", "test-task"),
                    event_data=sample_event_data.get("event_data", {})
                )
                result = evaluator.evaluate_expression(condition, mock_event, sample_task_data)
            else:
                # Single condition
                condition = Condition.from_dict(condition_data)
                mock_event = TaskEvent(
                    event_type=EventType(sample_event_data.get("event_type", "task_completed")),
                    task_id=sample_event_data.get("task_id", "test-task"),
                    event_data=sample_event_data.get("event_data", {})
                )
                result = evaluator.evaluate_condition(condition, mock_event, sample_task_data)
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error": f"Invalid condition format: {e}"
                }, indent=2)
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "evaluation_result": result,
                "sample_event": sample_event_data,
                "sample_task": sample_task_data
            }, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error testing condition: {e}")
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2)
        )]


def get_auto_append_tools() -> List[types.Tool]:
    """Get all auto-append MCP tools."""
    return [
        types.Tool(
            name="auto_append_create_rule",
            description="Create a new auto-append rule for automatic task creation",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Human-readable name for the rule"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what the rule does"
                    },
                    "trigger_events": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event types that trigger this rule (e.g., task_completed, task_failed)"
                    },
                    "condition": {
                        "type": "object",
                        "description": "Logical condition that must be met for rule to execute"
                    },
                    "creation_mode": {
                        "type": "string",
                        "enum": ["direct", "template", "clone"],
                        "description": "How to create the new task",
                        "default": "direct"
                    },
                    "task_definition": {
                        "type": "object",
                        "description": "Task definition for direct creation mode"
                    },
                    "template_id": {
                        "type": "string",
                        "description": "Template ID for template creation mode"
                    },
                    "template_parameters": {
                        "type": "object",
                        "description": "Parameters for template instantiation"
                    },
                    "clone_task_id": {
                        "type": "string",
                        "description": "Task ID to clone for clone creation mode"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Rule priority (lower = higher priority)",
                        "default": 100
                    },
                    "max_executions": {
                        "type": "integer",
                        "description": "Maximum number of times rule can execute"
                    },
                    "cooldown_minutes": {
                        "type": "integer",
                        "description": "Minimum minutes between rule executions",
                        "default": 0
                    },
                    "rule_id": {
                        "type": "string",
                        "description": "Optional custom rule ID (auto-generated if not provided)"
                    },
                    "created_by": {
                        "type": "string",
                        "description": "Who created this rule",
                        "default": "user"
                    }
                },
                "required": ["name", "description", "trigger_events", "condition"]
            }
        ),
        types.Tool(
            name="auto_append_list_rules",
            description="List auto-append rules with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive", "suspended", "error"],
                        "description": "Filter rules by status"
                    }
                }
            }
        ),
        types.Tool(
            name="auto_append_get_rule",
            description="Get detailed information about a specific auto-append rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the rule to retrieve"
                    }
                },
                "required": ["rule_id"]
            }
        ),
        types.Tool(
            name="auto_append_delete_rule",
            description="Delete an auto-append rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {
                        "type": "string",
                        "description": "ID of the rule to delete"
                    }
                },
                "required": ["rule_id"]
            }
        ),
        types.Tool(
            name="auto_append_get_statistics",
            description="Get auto-append engine statistics and monitoring data",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="auto_append_test_condition",
            description="Test a condition against sample event and task data",
            inputSchema={
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "object",
                        "description": "Condition or logical expression to test"
                    },
                    "sample_event": {
                        "type": "object",
                        "description": "Sample event data for testing"
                    },
                    "sample_task": {
                        "type": "object",
                        "description": "Sample task data for testing"
                    }
                },
                "required": ["condition"]
            }
        )
    ]