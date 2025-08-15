"""
Auto-Append Task Engine Module

Event-driven task creation system with conditional logic,
security controls, and comprehensive monitoring.
"""

from .event_system import (
    EventType, TaskEvent, EventListener, EventBus, TaskEventPublisher,
    get_event_bus, get_event_publisher
)

from .condition_evaluator import (
    ConditionType, Operator, LogicalOperator,
    Condition, LogicalExpression, ConditionEvaluator
)

from .auto_append_engine import (
    AutoAppendRuleStatus, TaskCreationMode, TaskDefinition,
    AutoAppendRule, AutoAppendEngine, get_auto_append_engine
)

from .security_controls import (
    SecurityLevel, ResourceType, ResourceLimit,
    SecurityValidator, ResourceMonitor, SecurityManager,
    get_security_manager
)

from .mcp_tools import get_auto_append_tools

__all__ = [
    # Event System
    'EventType', 'TaskEvent', 'EventListener', 'EventBus', 'TaskEventPublisher',
    'get_event_bus', 'get_event_publisher',
    
    # Condition Evaluator
    'ConditionType', 'Operator', 'LogicalOperator',
    'Condition', 'LogicalExpression', 'ConditionEvaluator',
    
    # Auto-Append Engine
    'AutoAppendRuleStatus', 'TaskCreationMode', 'TaskDefinition',
    'AutoAppendRule', 'AutoAppendEngine', 'get_auto_append_engine',
    
    # Security Controls
    'SecurityLevel', 'ResourceType', 'ResourceLimit',
    'SecurityValidator', 'ResourceMonitor', 'SecurityManager',
    'get_security_manager',
    
    # MCP Tools
    'get_auto_append_tools'
]