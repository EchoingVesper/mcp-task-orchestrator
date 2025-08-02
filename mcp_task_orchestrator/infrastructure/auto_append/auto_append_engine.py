"""
Auto-Append Task Engine

Main engine that creates follow-up tasks automatically based on events
and configurable rules. Integrates with the event system and condition
evaluator to provide powerful workflow automation.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .event_system import EventListener, TaskEvent, EventType, get_event_bus
from .condition_evaluator import ConditionEvaluator, LogicalExpression, Condition
from ..template_system.template_engine import TemplateEngine
from ..template_system.storage_manager import TemplateStorageManager

logger = logging.getLogger(__name__)


class AutoAppendRuleStatus(Enum):
    """Status of an auto-append rule."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ERROR = "error"


class TaskCreationMode(Enum):
    """How new tasks should be created."""
    DIRECT = "direct"  # Create task directly in orchestrator
    TEMPLATE = "template"  # Use template to create task
    CLONE = "clone"  # Clone an existing task


@dataclass
class TaskDefinition:
    """Definition of a task to be created automatically."""
    title: str
    description: str
    task_type: str = "standard"
    specialist_type: str = "generic"
    complexity: str = "moderate"
    parent_task_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None
    due_date: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for task creation."""
        return {
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type,
            "specialist_type": self.specialist_type,
            "complexity": self.complexity,
            "parent_task_id": self.parent_task_id,
            "dependencies": self.dependencies,
            "estimated_effort": self.estimated_effort,
            "due_date": self.due_date,
            **self.metadata
        }


@dataclass
class AutoAppendRule:
    """Rule for automatically creating tasks based on events."""
    rule_id: str
    name: str
    description: str
    trigger_events: Set[EventType]
    condition: LogicalExpression
    creation_mode: TaskCreationMode
    task_definition: Optional[TaskDefinition] = None
    template_id: Optional[str] = None
    template_parameters: Dict[str, Any] = field(default_factory=dict)
    clone_task_id: Optional[str] = None
    status: AutoAppendRuleStatus = AutoAppendRuleStatus.ACTIVE
    priority: int = 100  # Lower numbers = higher priority
    max_executions: Optional[int] = None  # Limit total executions
    execution_count: int = 0
    cooldown_minutes: int = 0  # Minimum time between executions
    last_execution: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "trigger_events": [e.value for e in self.trigger_events],
            "condition": self.condition.to_dict(),
            "creation_mode": self.creation_mode.value,
            "task_definition": self.task_definition.to_dict() if self.task_definition else None,
            "template_id": self.template_id,
            "template_parameters": self.template_parameters,
            "clone_task_id": self.clone_task_id,
            "status": self.status.value,
            "priority": self.priority,
            "max_executions": self.max_executions,
            "execution_count": self.execution_count,
            "cooldown_minutes": self.cooldown_minutes,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }


class AutoAppendEngine(EventListener):
    """
    Main auto-append engine that listens for events and creates tasks.
    
    Features:
    - Rule-based task creation
    - Template integration
    - Security controls and resource limits
    - Execution monitoring and statistics
    """
    
    def __init__(self, 
                 condition_evaluator: Optional[ConditionEvaluator] = None,
                 template_engine: Optional[TemplateEngine] = None,
                 storage_manager: Optional[TemplateStorageManager] = None):
        self.condition_evaluator = condition_evaluator or ConditionEvaluator()
        self.template_engine = template_engine or TemplateEngine()
        self.storage_manager = storage_manager or TemplateStorageManager()
        
        # Rule storage
        self.rules: Dict[str, AutoAppendRule] = {}
        
        # Security and performance limits
        self.max_rules = 1000
        self.max_executions_per_minute = 100
        self.max_tasks_per_event = 10
        
        # Execution tracking
        self.execution_history: List[Dict[str, Any]] = []
        self.execution_stats: Dict[str, int] = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "skipped_executions": 0
        }
        
        # Rate limiting
        self._execution_timestamps: List[datetime] = []
        
        # Register with event bus
        get_event_bus().subscribe(self)
    
    def get_supported_events(self) -> Set[EventType]:
        """Return all event types that might trigger rules."""
        all_events = set()
        for rule in self.rules.values():
            all_events.update(rule.trigger_events)
        
        # If no rules, still listen to common events
        if not all_events:
            all_events = {
                EventType.TASK_COMPLETED,
                EventType.TASK_FAILED,
                EventType.TASK_CREATED,
                EventType.MILESTONE_REACHED
            }
        
        return all_events
    
    async def handle_event(self, event: TaskEvent) -> None:
        """Handle incoming events and execute matching rules."""
        logger.debug(f"Auto-append engine handling event: {event.event_type.value}")
        
        # Rate limiting check
        if not self._check_rate_limits():
            logger.warning("Auto-append engine rate limit exceeded")
            return
        
        # Find matching rules
        matching_rules = self._find_matching_rules(event)
        
        if not matching_rules:
            logger.debug(f"No matching rules for event {event.event_type.value}")
            return
        
        logger.info(f"Found {len(matching_rules)} matching rules for event {event.event_type.value}")
        
        # Execute rules in priority order (lower priority number = higher priority)
        matching_rules.sort(key=lambda r: (r.priority, r.created_at))
        
        tasks_created = 0
        for rule in matching_rules:
            if tasks_created >= self.max_tasks_per_event:
                logger.warning(f"Max tasks per event limit reached: {self.max_tasks_per_event}")
                break
            
            try:
                created = await self._execute_rule(rule, event)
                if created:
                    tasks_created += 1
            except Exception as e:
                logger.error(f"Error executing rule {rule.rule_id}: {e}")
                self._record_execution(rule, event, success=False, error=str(e))
    
    def _find_matching_rules(self, event: TaskEvent) -> List[AutoAppendRule]:
        """Find rules that match the given event."""
        matching_rules = []
        
        for rule in self.rules.values():
            # Skip inactive rules
            if rule.status != AutoAppendRuleStatus.ACTIVE:
                continue
            
            # Check if event type matches
            if event.event_type not in rule.trigger_events:
                continue
            
            # Check execution limits
            if rule.max_executions and rule.execution_count >= rule.max_executions:
                logger.debug(f"Rule {rule.rule_id} has reached execution limit")
                continue
            
            # Check cooldown
            if self._is_in_cooldown(rule):
                logger.debug(f"Rule {rule.rule_id} is in cooldown period")
                continue
            
            # Evaluate conditions
            try:
                if self.condition_evaluator.evaluate_expression(rule.condition, event):
                    matching_rules.append(rule)
                    logger.debug(f"Rule {rule.rule_id} conditions matched")
                else:
                    logger.debug(f"Rule {rule.rule_id} conditions not met")
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id} conditions: {e}")
        
        return matching_rules
    
    def _is_in_cooldown(self, rule: AutoAppendRule) -> bool:
        """Check if rule is in cooldown period."""
        if rule.cooldown_minutes <= 0 or not rule.last_execution:
            return False
        
        cooldown_end = rule.last_execution.replace(tzinfo=timezone.utc) + \
                      timezone.utc.localize(datetime.fromtimestamp(rule.cooldown_minutes * 60))
        
        return datetime.now(timezone.utc) < cooldown_end
    
    async def _execute_rule(self, rule: AutoAppendRule, event: TaskEvent) -> bool:
        """Execute a single rule to create a task."""
        logger.info(f"Executing rule {rule.rule_id}: {rule.name}")
        
        try:
            # Create task based on creation mode
            if rule.creation_mode == TaskCreationMode.DIRECT:
                task_data = await self._create_direct_task(rule, event)
            elif rule.creation_mode == TaskCreationMode.TEMPLATE:
                task_data = await self._create_template_task(rule, event)
            elif rule.creation_mode == TaskCreationMode.CLONE:
                task_data = await self._create_cloned_task(rule, event)
            else:
                raise ValueError(f"Unknown creation mode: {rule.creation_mode}")
            
            if task_data:
                # TODO: Integrate with actual task creation system
                logger.info(f"Would create task: {task_data.get('title', 'Untitled')}")
                
                # Update rule execution tracking
                rule.execution_count += 1
                rule.last_execution = datetime.now(timezone.utc)
                
                self._record_execution(rule, event, success=True, task_data=task_data)
                return True
            else:
                logger.warning(f"Rule {rule.rule_id} did not generate task data")
                self._record_execution(rule, event, success=False, error="No task data generated")
                return False
                
        except Exception as e:
            logger.error(f"Error executing rule {rule.rule_id}: {e}")
            self._record_execution(rule, event, success=False, error=str(e))
            return False
    
    async def _create_direct_task(self, rule: AutoAppendRule, event: TaskEvent) -> Optional[Dict[str, Any]]:
        """Create task directly from rule definition."""
        if not rule.task_definition:
            raise ValueError("Direct creation mode requires task_definition")
        
        # Apply parameter substitution to task definition
        task_data = rule.task_definition.to_dict()
        
        # Substitute event-based parameters
        substitutions = {
            "source_task_id": event.task_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            **event.event_data
        }
        
        task_data = self._apply_substitutions(task_data, substitutions)
        
        return task_data
    
    async def _create_template_task(self, rule: AutoAppendRule, event: TaskEvent) -> Optional[Dict[str, Any]]:
        """Create task using template system."""
        if not rule.template_id:
            raise ValueError("Template creation mode requires template_id")
        
        # Load template
        try:
            template_content = await self.storage_manager.load_template(rule.template_id)
            template = self.template_engine.parse_template(template_content)
        except Exception as e:
            raise ValueError(f"Failed to load template {rule.template_id}: {e}")
        
        # Prepare parameters
        parameters = {
            "source_task_id": event.task_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            **event.event_data,
            **rule.template_parameters
        }
        
        # Instantiate template
        try:
            instantiated = self.template_engine.instantiate_template(template, parameters)
            
            # Extract task definitions from instantiated template
            tasks = instantiated.get("tasks", {})
            if not tasks:
                raise ValueError("Template produced no tasks")
            
            # Return first task definition (or could return all)
            first_task = next(iter(tasks.values()))
            return first_task
            
        except Exception as e:
            raise ValueError(f"Failed to instantiate template: {e}")
    
    async def _create_cloned_task(self, rule: AutoAppendRule, event: TaskEvent) -> Optional[Dict[str, Any]]:
        """Create task by cloning an existing task."""
        if not rule.clone_task_id:
            raise ValueError("Clone creation mode requires clone_task_id")
        
        # TODO: Implement task cloning from orchestrator
        # For now, return a placeholder
        return {
            "title": f"Cloned from {rule.clone_task_id}",
            "description": f"Auto-generated task cloned from {rule.clone_task_id}",
            "task_type": "standard",
            "specialist_type": "generic"
        }
    
    def _apply_substitutions(self, data: Dict[str, Any], substitutions: Dict[str, Any]) -> Dict[str, Any]:
        """Apply parameter substitutions to task data."""
        # Simple string substitution for now
        import json
        
        # Convert to JSON string for substitution
        json_str = json.dumps(data)
        
        # Apply substitutions
        for key, value in substitutions.items():
            placeholder = f"{{{{{key}}}}}"
            json_str = json_str.replace(placeholder, str(value))
        
        # Convert back to dict
        return json.loads(json_str)
    
    def _check_rate_limits(self) -> bool:
        """Check if execution rate limits are exceeded."""
        now = datetime.now(timezone.utc)
        
        # Clean old timestamps (older than 1 minute)
        cutoff = now - timezone.utc.localize(datetime.fromtimestamp(60))
        self._execution_timestamps = [ts for ts in self._execution_timestamps if ts > cutoff]
        
        # Check rate limit
        if len(self._execution_timestamps) >= self.max_executions_per_minute:
            return False
        
        # Add current timestamp
        self._execution_timestamps.append(now)
        return True
    
    def _record_execution(self, rule: AutoAppendRule, event: TaskEvent, 
                         success: bool, task_data: Optional[Dict[str, Any]] = None,
                         error: Optional[str] = None) -> None:
        """Record rule execution for monitoring and statistics."""
        execution_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rule_id": rule.rule_id,
            "rule_name": rule.name,
            "event_type": event.event_type.value,
            "source_task_id": event.task_id,
            "success": success,
            "task_data": task_data,
            "error": error
        }
        
        self.execution_history.append(execution_record)
        
        # Limit history size
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
        
        # Update statistics
        self.execution_stats["total_executions"] += 1
        if success:
            self.execution_stats["successful_executions"] += 1
        else:
            self.execution_stats["failed_executions"] += 1
    
    # Rule management methods
    
    def add_rule(self, rule: AutoAppendRule) -> None:
        """Add a new auto-append rule."""
        if len(self.rules) >= self.max_rules:
            raise ValueError(f"Maximum number of rules reached: {self.max_rules}")
        
        # Validate rule
        validation_errors = self.condition_evaluator.validate_expression(rule.condition)
        if validation_errors:
            raise ValueError(f"Rule validation failed: {', '.join(validation_errors)}")
        
        self.rules[rule.rule_id] = rule
        logger.info(f"Added auto-append rule: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an auto-append rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed auto-append rule: {rule_id}")
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[AutoAppendRule]:
        """Get a rule by ID."""
        return self.rules.get(rule_id)
    
    def list_rules(self, status: Optional[AutoAppendRuleStatus] = None) -> List[AutoAppendRule]:
        """List all rules, optionally filtered by status."""
        if status:
            return [rule for rule in self.rules.values() if rule.status == status]
        return list(self.rules.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.status == AutoAppendRuleStatus.ACTIVE]),
            "execution_stats": self.execution_stats.copy(),
            "recent_executions": self.execution_history[-10:],
            "rate_limit_status": {
                "current_rate": len(self._execution_timestamps),
                "max_rate": self.max_executions_per_minute
            }
        }


# Global auto-append engine instance
_global_auto_append_engine: Optional[AutoAppendEngine] = None


def get_auto_append_engine() -> AutoAppendEngine:
    """Get the global auto-append engine instance."""
    global _global_auto_append_engine
    if _global_auto_append_engine is None:
        _global_auto_append_engine = AutoAppendEngine()
    return _global_auto_append_engine