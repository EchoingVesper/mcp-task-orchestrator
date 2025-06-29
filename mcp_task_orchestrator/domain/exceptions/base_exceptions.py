"""
Base exception classes for the MCP Task Orchestrator.

This module provides the foundation exception hierarchy that all other
exceptions inherit from, including error severity levels and recovery strategies.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import time


class ErrorSeverity(Enum):
    """Error severity levels for categorizing exceptions."""
    LOW = "low"           # Minor issues, system continues normally
    MEDIUM = "medium"     # Significant issues, some functionality affected
    HIGH = "high"         # Major issues, core functionality affected
    CRITICAL = "critical" # System-threatening issues, immediate attention required


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""
    NONE = "none"         # No recovery possible, manual intervention required
    RETRY = "retry"       # Can be retried after a delay
    FALLBACK = "fallback" # Can use alternative approach
    RESTART = "restart"   # Component restart required
    RESET = "reset"       # State reset required


class BaseOrchestrationError(Exception):
    """
    Base exception for all MCP Task Orchestrator errors.
    
    Provides comprehensive error information including severity,
    recovery strategies, and contextual details.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.NONE,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.severity = severity
        self.recovery_strategy = recovery_strategy
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = time.time()
        self.error_id = self._generate_error_id()
    
    def _generate_error_id(self) -> str:
        """Generate a unique error ID for tracking."""
        import uuid
        return f"ERR-{int(self.timestamp)}-{str(uuid.uuid4())[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "details": self.details,
            "severity": self.severity.value,
            "recovery_strategy": self.recovery_strategy.value,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp,
            "exception_type": self.__class__.__name__
        }
    
    def is_retryable(self) -> bool:
        """Check if this error can be retried."""
        return self.recovery_strategy in [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK]
    
    def is_critical(self) -> bool:
        """Check if this error is critical."""
        return self.severity == ErrorSeverity.CRITICAL
    
    def __str__(self) -> str:
        """String representation with error ID and severity."""
        return f"[{self.error_id}] {self.severity.value.upper()}: {self.message}"


class ConfigurationError(BaseOrchestrationError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, config_key: str, issue: str, config_value: Optional[Any] = None):
        super().__init__(
            f"Configuration error for '{config_key}': {issue}",
            details={
                "config_key": config_key,
                "config_value": config_value,
                "issue": issue
            },
            severity=ErrorSeverity.HIGH,
            recovery_strategy=RecoveryStrategy.RESTART,
            error_code="CONFIG_INVALID"
        )
        self.config_key = config_key
        self.config_value = config_value
        self.issue = issue


class InfrastructureError(BaseOrchestrationError):
    """Raised when infrastructure components fail."""
    
    def __init__(self, component: str, failure_reason: str, 
                 is_recoverable: bool = False):
        recovery = RecoveryStrategy.RETRY if is_recoverable else RecoveryStrategy.RESTART
        severity = ErrorSeverity.HIGH if not is_recoverable else ErrorSeverity.MEDIUM
        
        super().__init__(
            f"Infrastructure failure in {component}: {failure_reason}",
            details={
                "component": component,
                "failure_reason": failure_reason,
                "is_recoverable": is_recoverable
            },
            severity=severity,
            recovery_strategy=recovery,
            error_code="INFRA_FAILURE"
        )
        self.component = component
        self.failure_reason = failure_reason
        self.is_recoverable = is_recoverable


class ValidationError(BaseOrchestrationError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: Any, validation_rules: List[str]):
        super().__init__(
            f"Validation failed for field '{field}': {', '.join(validation_rules)}",
            details={
                "field": field,
                "value": str(value),
                "validation_rules": validation_rules
            },
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.NONE,
            error_code="VALIDATION_FAILED"
        )
        self.field = field
        self.value = value
        self.validation_rules = validation_rules


class ExternalServiceError(BaseOrchestrationError):
    """Raised when external service calls fail."""
    
    def __init__(self, service_name: str, operation: str, error_details: str,
                 status_code: Optional[int] = None, retry_after: Optional[int] = None):
        recovery = RecoveryStrategy.RETRY if retry_after else RecoveryStrategy.FALLBACK
        
        super().__init__(
            f"External service '{service_name}' failed for operation '{operation}': {error_details}",
            details={
                "service_name": service_name,
                "operation": operation,
                "error_details": error_details,
                "status_code": status_code,
                "retry_after": retry_after
            },
            severity=ErrorSeverity.MEDIUM,
            recovery_strategy=recovery,
            error_code="EXTERNAL_SERVICE_FAILED"
        )
        self.service_name = service_name
        self.operation = operation
        self.status_code = status_code
        self.retry_after = retry_after


class SecurityError(BaseOrchestrationError):
    """Raised when security violations occur."""
    
    def __init__(self, violation_type: str, details: str, 
                 resource: Optional[str] = None, user: Optional[str] = None):
        super().__init__(
            f"Security violation ({violation_type}): {details}",
            details={
                "violation_type": violation_type,
                "resource": resource,
                "user": user,
                "security_details": details
            },
            severity=ErrorSeverity.CRITICAL,
            recovery_strategy=RecoveryStrategy.NONE,
            error_code="SECURITY_VIOLATION"
        )
        self.violation_type = violation_type
        self.resource = resource
        self.user = user


class PerformanceError(BaseOrchestrationError):
    """Raised when performance thresholds are exceeded."""
    
    def __init__(self, metric: str, threshold: float, actual: float, operation: str):
        super().__init__(
            f"Performance threshold exceeded for {metric} in operation '{operation}': {actual} > {threshold}",
            details={
                "metric": metric,
                "threshold": threshold,
                "actual": actual,
                "operation": operation,
                "performance_ratio": actual / threshold
            },
            severity=ErrorSeverity.HIGH if actual > threshold * 2 else ErrorSeverity.MEDIUM,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            error_code="PERFORMANCE_THRESHOLD_EXCEEDED"
        )
        self.metric = metric
        self.threshold = threshold
        self.actual = actual
        self.operation = operation