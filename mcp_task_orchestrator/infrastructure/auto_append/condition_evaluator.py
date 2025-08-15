"""
Condition Evaluator for Auto-Append Rules

Implements rule-based conditional logic for automatic task creation.
Supports complex conditions, boolean logic, and safe evaluation.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from .event_system import TaskEvent, EventType

logger = logging.getLogger(__name__)


class ConditionType(Enum):
    """Types of conditions that can be evaluated."""
    TASK_STATUS = "task_status"
    TASK_TYPE = "task_type" 
    SPECIALIST_TYPE = "specialist_type"
    COMPLEXITY = "complexity"
    EVENT_TYPE = "event_type"
    TASK_PROPERTY = "task_property"
    EVENT_DATA = "event_data"
    TIME_BASED = "time_based"
    CUSTOM = "custom"


class Operator(Enum):
    """Comparison operators for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES_REGEX = "matches_regex"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


class LogicalOperator(Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class Condition:
    """Represents a single condition in a rule."""
    condition_type: ConditionType
    field: str  # Field to check (e.g., "status", "type", "event_data.error_count")
    operator: Operator
    value: Any  # Expected value
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert condition to dictionary."""
        return {
            "condition_type": self.condition_type.value,
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Condition':
        """Create condition from dictionary."""
        return cls(
            condition_type=ConditionType(data["condition_type"]),
            field=data["field"],
            operator=Operator(data["operator"]),
            value=data["value"],
            description=data.get("description")
        )


@dataclass
class LogicalExpression:
    """Represents a logical expression combining multiple conditions."""
    operator: LogicalOperator
    conditions: List[Union[Condition, 'LogicalExpression']]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert expression to dictionary."""
        return {
            "operator": self.operator.value,
            "conditions": [
                c.to_dict() if isinstance(c, Condition) else c.to_dict()
                for c in self.conditions
            ],
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogicalExpression':
        """Create expression from dictionary."""
        conditions = []
        for cond_data in data["conditions"]:
            if "operator" in cond_data and "conditions" in cond_data:
                # Nested logical expression
                conditions.append(cls.from_dict(cond_data))
            else:
                # Simple condition
                conditions.append(Condition.from_dict(cond_data))
        
        return cls(
            operator=LogicalOperator(data["operator"]),
            conditions=conditions,
            description=data.get("description")
        )


class ConditionEvaluator:
    """
    Evaluates conditions against task events and data.
    
    Provides safe evaluation of complex conditional logic
    with security controls and performance limits.
    """
    
    def __init__(self):
        # Security limits
        self.max_evaluation_depth = 20
        self.max_conditions_per_rule = 50
        self.max_regex_length = 1000
        self.evaluation_timeout_seconds = 5.0
        
        # Compiled regex cache
        self._regex_cache: Dict[str, re.Pattern] = {}
        self._cache_size_limit = 100
    
    def evaluate_condition(self, condition: Condition, 
                          event: TaskEvent,
                          task_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Evaluate a single condition against event and task data.
        
        Args:
            condition: Condition to evaluate
            event: Task event context
            task_data: Additional task data (optional)
            
        Returns:
            True if condition is met, False otherwise
        """
        try:
            # Get the actual value to compare against
            actual_value = self._extract_value(condition, event, task_data)
            expected_value = condition.value
            
            # Perform comparison based on operator
            return self._compare_values(actual_value, expected_value, condition.operator)
            
        except Exception as e:
            logger.warning(f"Error evaluating condition {condition.field}: {e}")
            return False
    
    def evaluate_expression(self, expression: LogicalExpression,
                           event: TaskEvent,
                           task_data: Optional[Dict[str, Any]] = None,
                           depth: int = 0) -> bool:
        """
        Evaluate a logical expression recursively.
        
        Args:
            expression: Logical expression to evaluate
            event: Task event context
            task_data: Additional task data (optional)
            depth: Current recursion depth
            
        Returns:
            True if expression evaluates to true, False otherwise
        """
        # Security check: prevent deep recursion
        if depth > self.max_evaluation_depth:
            logger.error(f"Evaluation depth limit exceeded: {depth}")
            return False
        
        # Security check: limit number of conditions
        if len(expression.conditions) > self.max_conditions_per_rule:
            logger.error(f"Too many conditions: {len(expression.conditions)}")
            return False
        
        try:
            if expression.operator == LogicalOperator.AND:
                return all(self._evaluate_item(item, event, task_data, depth + 1) 
                          for item in expression.conditions)
            
            elif expression.operator == LogicalOperator.OR:
                return any(self._evaluate_item(item, event, task_data, depth + 1)
                          for item in expression.conditions)
            
            elif expression.operator == LogicalOperator.NOT:
                if len(expression.conditions) != 1:
                    logger.error("NOT operator requires exactly one condition")
                    return False
                return not self._evaluate_item(expression.conditions[0], event, task_data, depth + 1)
            
            else:
                logger.error(f"Unknown logical operator: {expression.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating logical expression: {e}")
            return False
    
    def _evaluate_item(self, item: Union[Condition, LogicalExpression],
                      event: TaskEvent,
                      task_data: Optional[Dict[str, Any]],
                      depth: int) -> bool:
        """Evaluate a single item (condition or expression)."""
        if isinstance(item, Condition):
            return self.evaluate_condition(item, event, task_data)
        elif isinstance(item, LogicalExpression):
            return self.evaluate_expression(item, event, task_data, depth)
        else:
            logger.error(f"Unknown item type: {type(item)}")
            return False
    
    def _extract_value(self, condition: Condition,
                      event: TaskEvent,
                      task_data: Optional[Dict[str, Any]]) -> Any:
        """Extract the actual value from event/task data based on condition field."""
        field = condition.field
        
        # Handle nested field access (e.g., "event_data.error_count")
        if '.' in field:
            parts = field.split('.')
            root_field = parts[0]
            nested_path = parts[1:]
        else:
            root_field = field
            nested_path = []
        
        # Get root value based on condition type
        if condition.condition_type == ConditionType.EVENT_TYPE:
            root_value = event.event_type.value
        elif condition.condition_type == ConditionType.EVENT_DATA:
            root_value = event.event_data
        elif condition.condition_type == ConditionType.TASK_PROPERTY:
            if task_data is None:
                logger.warning("Task data not available for task property condition")
                return None
            root_value = task_data
        else:
            # Default: try event data first, then task data
            if root_field in event.event_data:
                root_value = event.event_data[root_field]
            elif task_data and root_field in task_data:
                root_value = task_data[root_field]
            else:
                logger.debug(f"Field {root_field} not found in event or task data")
                return None
        
        # Navigate nested path
        current_value = root_value
        for part in nested_path:
            if isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]
            else:
                logger.debug(f"Nested field {part} not found")
                return None
        
        return current_value
    
    def _compare_values(self, actual: Any, expected: Any, operator: Operator) -> bool:
        """Compare two values using the specified operator."""
        try:
            if operator == Operator.EQUALS:
                return actual == expected
            
            elif operator == Operator.NOT_EQUALS:
                return actual != expected
            
            elif operator == Operator.CONTAINS:
                return self._safe_contains(actual, expected)
            
            elif operator == Operator.NOT_CONTAINS:
                return not self._safe_contains(actual, expected)
            
            elif operator == Operator.STARTS_WITH:
                return isinstance(actual, str) and actual.startswith(str(expected))
            
            elif operator == Operator.ENDS_WITH:
                return isinstance(actual, str) and actual.endswith(str(expected))
            
            elif operator == Operator.MATCHES_REGEX:
                return self._safe_regex_match(actual, expected)
            
            elif operator == Operator.GREATER_THAN:
                return self._safe_numeric_compare(actual, expected, lambda a, e: a > e)
            
            elif operator == Operator.LESS_THAN:
                return self._safe_numeric_compare(actual, expected, lambda a, e: a < e)
            
            elif operator == Operator.GREATER_EQUAL:
                return self._safe_numeric_compare(actual, expected, lambda a, e: a >= e)
            
            elif operator == Operator.LESS_EQUAL:
                return self._safe_numeric_compare(actual, expected, lambda a, e: a <= e)
            
            elif operator == Operator.IN_LIST:
                return isinstance(expected, list) and actual in expected
            
            elif operator == Operator.NOT_IN_LIST:
                return isinstance(expected, list) and actual not in expected
            
            else:
                logger.error(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            logger.warning(f"Error comparing values with {operator}: {e}")
            return False
    
    def _safe_contains(self, actual: Any, expected: Any) -> bool:
        """Safely check if actual contains expected."""
        if isinstance(actual, str):
            return str(expected) in actual
        elif isinstance(actual, (list, tuple, set)):
            return expected in actual
        elif isinstance(actual, dict):
            return expected in actual.values()
        else:
            return False
    
    def _safe_regex_match(self, actual: Any, pattern: str) -> bool:
        """Safely perform regex matching with security controls."""
        if not isinstance(actual, str):
            return False
        
        # Security check: limit regex pattern length
        if len(pattern) > self.max_regex_length:
            logger.error(f"Regex pattern too long: {len(pattern)}")
            return False
        
        try:
            # Use cache to avoid recompiling patterns
            if pattern not in self._regex_cache:
                if len(self._regex_cache) >= self._cache_size_limit:
                    # Clear oldest entries
                    self._regex_cache.clear()
                
                # Compile with timeout protection
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
                self._regex_cache[pattern] = compiled_pattern
            
            regex = self._regex_cache[pattern]
            return bool(regex.search(actual))
            
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
            return False
    
    def _safe_numeric_compare(self, actual: Any, expected: Any, compare_func) -> bool:
        """Safely perform numeric comparison."""
        try:
            actual_num = float(actual) if actual is not None else 0
            expected_num = float(expected) if expected is not None else 0
            return compare_func(actual_num, expected_num)
        except (ValueError, TypeError):
            return False
    
    def validate_condition(self, condition: Condition) -> List[str]:
        """
        Validate a condition for security and correctness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check field name for suspicious patterns
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', condition.field):
            errors.append(f"Invalid field name: {condition.field}")
        
        # Check for dangerous field access
        dangerous_fields = ['__', 'eval', 'exec', 'import']
        if any(dangerous in condition.field.lower() for dangerous in dangerous_fields):
            errors.append(f"Dangerous field access detected: {condition.field}")
        
        # Validate regex patterns
        if condition.operator == Operator.MATCHES_REGEX:
            if not isinstance(condition.value, str):
                errors.append("Regex pattern must be a string")
            elif len(condition.value) > self.max_regex_length:
                errors.append(f"Regex pattern too long: {len(condition.value)}")
            else:
                try:
                    re.compile(condition.value)
                except re.error as e:
                    errors.append(f"Invalid regex pattern: {e}")
        
        return errors
    
    def validate_expression(self, expression: LogicalExpression, depth: int = 0) -> List[str]:
        """
        Validate a logical expression for security and correctness.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check recursion depth
        if depth > self.max_evaluation_depth:
            errors.append(f"Expression too deeply nested: {depth}")
            return errors
        
        # Check number of conditions
        if len(expression.conditions) > self.max_conditions_per_rule:
            errors.append(f"Too many conditions: {len(expression.conditions)}")
            return errors
        
        # Validate NOT operator has exactly one condition
        if expression.operator == LogicalOperator.NOT and len(expression.conditions) != 1:
            errors.append("NOT operator requires exactly one condition")
        
        # Validate nested conditions and expressions
        for item in expression.conditions:
            if isinstance(item, Condition):
                errors.extend(self.validate_condition(item))
            elif isinstance(item, LogicalExpression):
                errors.extend(self.validate_expression(item, depth + 1))
            else:
                errors.append(f"Invalid item type: {type(item)}")
        
        return errors