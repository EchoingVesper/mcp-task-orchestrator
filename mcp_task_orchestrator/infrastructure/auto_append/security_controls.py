"""
Security Controls for Auto-Append System

Implements comprehensive security controls and resource limits to prevent
malicious rule creation, resource exhaustion, and system abuse.
"""

import logging
import re
import hashlib
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

from .auto_append_engine import AutoAppendRule, TaskDefinition
from .condition_evaluator import LogicalExpression, Condition

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security level for rules and operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(Enum):
    """Types of resources to monitor and limit."""
    RULE_COUNT = "rule_count"
    EXECUTION_RATE = "execution_rate"
    TASK_CREATION_RATE = "task_creation_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"


@dataclass
class ResourceLimit:
    """Resource limit configuration."""
    resource_type: ResourceType
    max_value: float
    time_window_minutes: int = 60
    enforcement_level: SecurityLevel = SecurityLevel.MEDIUM
    description: str = ""


@dataclass
class SecurityEvent:
    """Security event for audit logging."""
    event_type: str
    severity: SecurityLevel
    timestamp: datetime
    source: str
    details: Dict[str, Any]
    action_taken: str = ""


class SecurityValidator:
    """
    Validates auto-append rules for security issues.
    
    Checks for:
    - Malicious conditions and patterns
    - Resource exhaustion potential
    - Infinite loop scenarios
    - Privilege escalation attempts
    """
    
    def __init__(self):
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            # Code injection patterns
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'getattr\s*\(',
            r'setattr\s*\(',
            
            # Command injection
            r'subprocess',
            r'os\.system',
            r'shell=True',
            
            # Path traversal
            r'\.\./.*',
            r'/etc/',
            r'/root/',
            
            # System access
            r'\/proc\/',
            r'\/dev\/',
            r'\/sys\/',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.dangerous_patterns]
        
        # Suspicious field names
        self.suspicious_fields = {
            'password', 'secret', 'token', 'key', 'credential',
            'admin', 'root', 'sudo', 'privilege', 'permission'
        }
        
        # Resource limits
        self.max_rule_complexity = 50  # Max conditions per rule
        self.max_nesting_depth = 10
        self.max_string_length = 10000
        self.max_template_parameters = 100
    
    def validate_rule(self, rule: AutoAppendRule) -> List[str]:
        """
        Validate an auto-append rule for security issues.
        
        Returns:
            List of security issues found (empty if secure)
        """
        issues = []
        
        # Validate rule metadata
        issues.extend(self._validate_rule_metadata(rule))
        
        # Validate conditions
        issues.extend(self._validate_conditions(rule.condition))
        
        # Validate task definition
        if rule.task_definition:
            issues.extend(self._validate_task_definition(rule.task_definition))
        
        # Validate template parameters
        if rule.template_parameters:
            issues.extend(self._validate_template_parameters(rule.template_parameters))
        
        # Check for potential infinite loops
        issues.extend(self._check_infinite_loop_potential(rule))
        
        # Check resource exhaustion potential
        issues.extend(self._check_resource_exhaustion(rule))
        
        return issues
    
    def _validate_rule_metadata(self, rule: AutoAppendRule) -> List[str]:
        """Validate rule metadata for security issues."""
        issues = []
        
        # Check rule name and description for dangerous patterns
        for field_name, field_value in [("name", rule.name), ("description", rule.description)]:
            if isinstance(field_value, str):
                for pattern in self.compiled_patterns:
                    if pattern.search(field_value):
                        issues.append(f"Dangerous pattern detected in {field_name}: {pattern.pattern}")
        
        # Check for suspicious rule names
        if any(word in rule.name.lower() for word in self.suspicious_fields):
            issues.append(f"Suspicious rule name: {rule.name}")
        
        # Validate rule limits
        if rule.max_executions and rule.max_executions > 10000:
            issues.append(f"Excessive max_executions: {rule.max_executions}")
        
        if rule.priority < 0 or rule.priority > 1000:
            issues.append(f"Invalid priority value: {rule.priority}")
        
        return issues
    
    def _validate_conditions(self, expression: LogicalExpression, depth: int = 0) -> List[str]:
        """Validate logical expression for security issues."""
        issues = []
        
        # Check nesting depth
        if depth > self.max_nesting_depth:
            issues.append(f"Condition nesting too deep: {depth}")
            return issues
        
        # Check condition count
        if len(expression.conditions) > self.max_rule_complexity:
            issues.append(f"Too many conditions: {len(expression.conditions)}")
        
        # Validate individual conditions
        for item in expression.conditions:
            if isinstance(item, Condition):
                issues.extend(self._validate_single_condition(item))
            elif isinstance(item, LogicalExpression):
                issues.extend(self._validate_conditions(item, depth + 1))
        
        return issues
    
    def _validate_single_condition(self, condition: Condition) -> List[str]:
        """Validate a single condition for security issues."""
        issues = []
        
        # Check field name for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(condition.field):
                issues.append(f"Dangerous pattern in condition field: {condition.field}")
        
        # Check for suspicious field access
        if any(word in condition.field.lower() for word in self.suspicious_fields):
            issues.append(f"Suspicious field access: {condition.field}")
        
        # Validate condition value
        if isinstance(condition.value, str):
            if len(condition.value) > self.max_string_length:
                issues.append(f"Condition value too long: {len(condition.value)}")
            
            for pattern in self.compiled_patterns:
                if pattern.search(condition.value):
                    issues.append(f"Dangerous pattern in condition value: {condition.value[:100]}")
        
        return issues
    
    def _validate_task_definition(self, task_def: TaskDefinition) -> List[str]:
        """Validate task definition for security issues."""
        issues = []
        
        # Check task metadata for dangerous patterns
        for field_name, field_value in [
            ("title", task_def.title),
            ("description", task_def.description)
        ]:
            if isinstance(field_value, str):
                for pattern in self.compiled_patterns:
                    if pattern.search(field_value):
                        issues.append(f"Dangerous pattern in task {field_name}: {pattern.pattern}")
        
        # Check metadata for suspicious content
        for key, value in task_def.metadata.items():
            if any(word in key.lower() for word in self.suspicious_fields):
                issues.append(f"Suspicious metadata key: {key}")
            
            if isinstance(value, str):
                for pattern in self.compiled_patterns:
                    if pattern.search(value):
                        issues.append(f"Dangerous pattern in metadata {key}: {pattern.pattern}")
        
        return issues
    
    def _validate_template_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate template parameters for security issues."""
        issues = []
        
        if len(parameters) > self.max_template_parameters:
            issues.append(f"Too many template parameters: {len(parameters)}")
        
        for key, value in parameters.items():
            # Check parameter names
            if any(word in key.lower() for word in self.suspicious_fields):
                issues.append(f"Suspicious parameter name: {key}")
            
            # Check parameter values
            if isinstance(value, str):
                if len(value) > self.max_string_length:
                    issues.append(f"Parameter value too long: {key}")
                
                for pattern in self.compiled_patterns:
                    if pattern.search(value):
                        issues.append(f"Dangerous pattern in parameter {key}: {pattern.pattern}")
        
        return issues
    
    def _check_infinite_loop_potential(self, rule: AutoAppendRule) -> List[str]:
        """Check if rule could cause infinite loops."""
        issues = []
        
        # Check if rule creates tasks that could trigger itself
        if rule.task_definition:
            # Check if task type matches rule's trigger conditions
            # This is a simplified check - could be more sophisticated
            pass
        
        # Check cooldown period
        if rule.cooldown_minutes < 1:
            issues.append("No cooldown period - potential for rapid execution loops")
        
        # Check execution limits
        if not rule.max_executions:
            issues.append("No execution limit - potential for infinite execution")
        
        return issues
    
    def _check_resource_exhaustion(self, rule: AutoAppendRule) -> List[str]:
        """Check if rule could cause resource exhaustion."""
        issues = []
        
        # Check execution frequency
        if rule.max_executions and rule.max_executions > 1000:
            issues.append(f"High execution limit may cause resource exhaustion: {rule.max_executions}")
        
        # Check condition complexity
        complexity = self._calculate_condition_complexity(rule.condition)
        if complexity > 100:
            issues.append(f"High condition complexity may impact performance: {complexity}")
        
        return issues
    
    def _calculate_condition_complexity(self, expression: LogicalExpression, depth: int = 0) -> int:
        """Calculate complexity score for conditions."""
        if depth > 10:  # Prevent infinite recursion
            return 1000  # High penalty for deep nesting
        
        complexity = len(expression.conditions)
        
        for item in expression.conditions:
            if isinstance(item, LogicalExpression):
                complexity += self._calculate_condition_complexity(item, depth + 1)
            else:
                complexity += 1
        
        return complexity


class ResourceMonitor:
    """
    Monitors resource usage and enforces limits.
    
    Tracks:
    - Number of active rules
    - Execution rates
    - Task creation rates
    - System resource usage
    """
    
    def __init__(self):
        self.limits: Dict[ResourceType, ResourceLimit] = {}
        self.usage_history: Dict[ResourceType, List[Dict[str, Any]]] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Set default limits
        self._set_default_limits()
    
    def _set_default_limits(self):
        """Set default resource limits."""
        self.limits.update({
            ResourceType.RULE_COUNT: ResourceLimit(
                resource_type=ResourceType.RULE_COUNT,
                max_value=1000,
                time_window_minutes=0,  # No time window for count limits
                enforcement_level=SecurityLevel.HIGH,
                description="Maximum number of auto-append rules"
            ),
            ResourceType.EXECUTION_RATE: ResourceLimit(
                resource_type=ResourceType.EXECUTION_RATE,
                max_value=100,
                time_window_minutes=1,
                enforcement_level=SecurityLevel.MEDIUM,
                description="Maximum rule executions per minute"
            ),
            ResourceType.TASK_CREATION_RATE: ResourceLimit(
                resource_type=ResourceType.TASK_CREATION_RATE,
                max_value=50,
                time_window_minutes=1,
                enforcement_level=SecurityLevel.HIGH,
                description="Maximum tasks created per minute"
            )
        })
    
    def set_limit(self, limit: ResourceLimit) -> None:
        """Set a resource limit."""
        self.limits[limit.resource_type] = limit
        logger.info(f"Set resource limit: {limit.resource_type.value} = {limit.max_value}")
    
    def check_limit(self, resource_type: ResourceType, current_value: float) -> bool:
        """
        Check if current value exceeds limit.
        
        Returns:
            True if within limit, False if exceeded
        """
        if resource_type not in self.limits:
            return True
        
        limit = self.limits[resource_type]
        
        if current_value > limit.max_value:
            self._record_security_event(
                event_type="resource_limit_exceeded",
                severity=limit.enforcement_level,
                details={
                    "resource_type": resource_type.value,
                    "current_value": current_value,
                    "limit": limit.max_value,
                    "description": limit.description
                },
                action_taken="blocked_operation"
            )
            return False
        
        return True
    
    def record_usage(self, resource_type: ResourceType, value: float) -> None:
        """Record resource usage for monitoring."""
        if resource_type not in self.usage_history:
            self.usage_history[resource_type] = []
        
        usage_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "value": value
        }
        
        self.usage_history[resource_type].append(usage_record)
        
        # Limit history size
        if len(self.usage_history[resource_type]) > 1000:
            self.usage_history[resource_type] = self.usage_history[resource_type][-500:]
    
    def get_usage_statistics(self, resource_type: ResourceType, 
                           hours: int = 24) -> Dict[str, Any]:
        """Get usage statistics for a resource type."""
        if resource_type not in self.usage_history:
            return {"error": "No usage data available"}
        
        # Filter recent data
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_data = [
            record for record in self.usage_history[resource_type]
            if datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00")) > cutoff
        ]
        
        if not recent_data:
            return {"error": "No recent usage data"}
        
        values = [record["value"] for record in recent_data]
        
        return {
            "resource_type": resource_type.value,
            "time_period_hours": hours,
            "total_records": len(recent_data),
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": sum(values) / len(values),
            "current_limit": self.limits.get(resource_type, {}).max_value
        }
    
    def _record_security_event(self, event_type: str, severity: SecurityLevel,
                              details: Dict[str, Any], action_taken: str = "") -> None:
        """Record a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            timestamp=datetime.now(timezone.utc),
            source="auto_append_security",
            details=details,
            action_taken=action_taken
        )
        
        self.security_events.append(event)
        
        # Limit event history
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-500:]
        
        logger.warning(f"Security event: {event_type} - {action_taken}")


class SecurityManager:
    """
    Main security manager for the auto-append system.
    
    Coordinates validation, monitoring, and enforcement.
    """
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.monitor = ResourceMonitor()
        self.enabled = True
        self.audit_mode = False  # If True, logs issues but doesn't block
    
    def validate_and_authorize_rule(self, rule: AutoAppendRule) -> Dict[str, Any]:
        """
        Validate and authorize a rule for creation/modification.
        
        Returns:
            Dictionary with validation results and authorization decision
        """
        if not self.enabled:
            return {"authorized": True, "issues": [], "warnings": []}
        
        # Validate security
        security_issues = self.validator.validate_rule(rule)
        
        # Check resource limits
        if not self.monitor.check_limit(ResourceType.RULE_COUNT, 1):
            security_issues.append("Rule count limit would be exceeded")
        
        # Determine authorization
        critical_issues = [issue for issue in security_issues if "critical" in issue.lower()]
        authorized = len(critical_issues) == 0 or self.audit_mode
        
        result = {
            "authorized": authorized,
            "issues": security_issues,
            "warnings": [],
            "audit_mode": self.audit_mode
        }
        
        if not authorized:
            self.monitor._record_security_event(
                event_type="rule_authorization_denied",
                severity=SecurityLevel.HIGH,
                details={
                    "rule_id": rule.rule_id,
                    "rule_name": rule.name,
                    "issues": security_issues
                },
                action_taken="blocked_rule_creation"
            )
        
        return result
    
    def check_execution_authorization(self, rule: AutoAppendRule) -> bool:
        """Check if rule execution is authorized."""
        if not self.enabled:
            return True
        
        # Check execution rate limits
        if not self.monitor.check_limit(ResourceType.EXECUTION_RATE, 1):
            return False
        
        # Check task creation rate limits
        if not self.monitor.check_limit(ResourceType.TASK_CREATION_RATE, 1):
            return False
        
        return True
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get overall security status."""
        return {
            "enabled": self.enabled,
            "audit_mode": self.audit_mode,
            "recent_events": self.monitor.security_events[-10:],
            "resource_limits": {
                rt.value: limit.max_value 
                for rt, limit in self.monitor.limits.items()
            },
            "statistics": {
                "total_security_events": len(self.monitor.security_events),
                "critical_events_last_24h": len([
                    e for e in self.monitor.security_events
                    if e.severity == SecurityLevel.CRITICAL and
                    e.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)
                ])
            }
        }


# Global security manager instance
_global_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global _global_security_manager
    if _global_security_manager is None:
        _global_security_manager = SecurityManager()
    return _global_security_manager