"""
Structured error logging and metrics collection.
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from ...domain.exceptions import BaseOrchestrationError, ErrorSeverity

logger = logging.getLogger(__name__)


@dataclass
class ErrorEvent:
    """Structured error event for logging and metrics."""
    error_id: str
    timestamp: float
    error_type: str
    severity: str
    message: str
    details: Dict[str, Any]
    context: Dict[str, Any]
    recovery_strategy: Optional[str] = None
    component: Optional[str] = None
    operation: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class ErrorLogger:
    """Base error logger with structured logging capabilities."""
    
    def __init__(self, logger_name: str = "error_handler"):
        self.logger = logging.getLogger(logger_name)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with appropriate severity level."""
        context = context or {}
        
        if isinstance(error, BaseOrchestrationError):
            self._log_orchestration_error(error, context)
        else:
            self._log_generic_error(error, context)
    
    def _log_orchestration_error(self, error: BaseOrchestrationError, context: Dict[str, Any]):
        """Log orchestration-specific errors with full details."""
        error_data = error.to_dict()
        error_data.update(context)
        
        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"[{error.error_id}] {error.message}", extra=error_data)
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(f"[{error.error_id}] {error.message}", extra=error_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"[{error.error_id}] {error.message}", extra=error_data)
        else:
            self.logger.info(f"[{error.error_id}] {error.message}", extra=error_data)
    
    def _log_generic_error(self, error: Exception, context: Dict[str, Any]):
        """Log generic errors with basic information."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        
        self.logger.error(f"Unhandled error: {str(error)}", extra=error_data, exc_info=True)


class StructuredErrorLogger(ErrorLogger):
    """Enhanced error logger with structured event creation."""
    
    def __init__(self, logger_name: str = "structured_error_handler"):
        super().__init__(logger_name)
        self.event_handlers: List[callable] = []
    
    def add_event_handler(self, handler: callable):
        """Add a handler for error events."""
        self.event_handlers.append(handler)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error and create structured event."""
        context = context or {}
        
        # Create structured error event
        error_event = self._create_error_event(error, context)
        
        # Log the error
        super().log_error(error, context)
        
        # Notify event handlers
        for handler in self.event_handlers:
            try:
                handler(error_event)
            except Exception as handler_error:
                self.logger.error(f"Error event handler failed: {handler_error}")
    
    def _create_error_event(self, error: Exception, context: Dict[str, Any]) -> ErrorEvent:
        """Create a structured error event."""
        if isinstance(error, BaseOrchestrationError):
            return ErrorEvent(
                error_id=error.error_id,
                timestamp=error.timestamp,
                error_type=type(error).__name__,
                severity=error.severity.value,
                message=error.message,
                details=error.details,
                context=context,
                recovery_strategy=error.recovery_strategy.value,
                component=context.get('component'),
                operation=context.get('operation'),
                user_id=context.get('user_id')
            )
        else:
            import uuid
            return ErrorEvent(
                error_id=f"ERR-{int(time.time())}-{str(uuid.uuid4())[:8]}",
                timestamp=time.time(),
                error_type=type(error).__name__,
                severity="medium",
                message=str(error),
                details={"exception_info": str(error)},
                context=context,
                component=context.get('component'),
                operation=context.get('operation'),
                user_id=context.get('user_id')
            )


class ErrorAggregator:
    """Aggregates error events for analysis and reporting."""
    
    def __init__(self, max_events: int = 1000):
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.severity_counts: Dict[str, int] = defaultdict(int)
        self.component_errors: Dict[str, int] = defaultdict(int)
    
    def add_event(self, event: ErrorEvent):
        """Add an error event to the aggregator."""
        self.events.append(event)
        self.error_counts[event.error_type] += 1
        self.severity_counts[event.severity] += 1
        
        if event.component:
            self.component_errors[event.component] += 1
    
    def get_error_summary(self, time_window: Optional[float] = None) -> Dict[str, Any]:
        """Get summary of errors within optional time window."""
        cutoff_time = time.time() - time_window if time_window else 0
        
        relevant_events = [
            event for event in self.events 
            if event.timestamp >= cutoff_time
        ]
        
        if not relevant_events:
            return {
                "total_errors": 0,
                "by_type": {},
                "by_severity": {},
                "by_component": {},
                "time_window": time_window
            }
        
        # Count events in time window
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        component_counts = defaultdict(int)
        
        for event in relevant_events:
            type_counts[event.error_type] += 1
            severity_counts[event.severity] += 1
            if event.component:
                component_counts[event.component] += 1
        
        return {
            "total_errors": len(relevant_events),
            "by_type": dict(type_counts),
            "by_severity": dict(severity_counts),
            "by_component": dict(component_counts),
            "time_window": time_window,
            "oldest_event": min(event.timestamp for event in relevant_events),
            "newest_event": max(event.timestamp for event in relevant_events)
        }
    
    def get_frequent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent error types."""
        sorted_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"error_type": error_type, "count": count}
            for error_type, count in sorted_errors
        ]
    
    def get_critical_errors(self, limit: int = 50) -> List[ErrorEvent]:
        """Get recent critical errors."""
        critical_events = [
            event for event in self.events
            if event.severity == "critical"
        ]
        
        # Sort by timestamp (newest first)
        critical_events.sort(key=lambda x: x.timestamp, reverse=True)
        return critical_events[:limit]


class ErrorMetrics:
    """Collects and provides error metrics for monitoring."""
    
    def __init__(self):
        self.aggregator = ErrorAggregator()
        self.start_time = time.time()
    
    def record_error(self, event: ErrorEvent):
        """Record an error event for metrics."""
        self.aggregator.add_event(event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive error metrics."""
        uptime = time.time() - self.start_time
        
        # Get summaries for different time windows
        last_hour = self.aggregator.get_error_summary(3600)  # 1 hour
        last_day = self.aggregator.get_error_summary(86400)  # 24 hours
        
        return {
            "uptime_seconds": uptime,
            "total_events": len(self.aggregator.events),
            "last_hour": last_hour,
            "last_day": last_day,
            "frequent_errors": self.aggregator.get_frequent_errors(),
            "critical_errors_count": len(self.aggregator.get_critical_errors()),
            "error_rate_per_hour": last_hour["total_errors"] if last_hour["total_errors"] > 0 else 0
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status based on error metrics."""
        metrics = self.get_metrics()
        
        # Determine health based on error rates and severity
        critical_count = metrics["critical_errors_count"]
        hourly_errors = metrics["last_hour"]["total_errors"]
        
        if critical_count > 0:
            status = "critical"
            message = f"{critical_count} critical errors detected"
        elif hourly_errors > 50:  # Arbitrary threshold
            status = "warning"
            message = f"High error rate: {hourly_errors} errors in last hour"
        elif hourly_errors > 0:
            status = "degraded"
            message = f"{hourly_errors} errors in last hour"
        else:
            status = "healthy"
            message = "No errors detected"
        
        return {
            "status": status,
            "message": message,
            "metrics": metrics
        }


# Global instances
_global_error_logger: Optional[StructuredErrorLogger] = None
_global_error_metrics: Optional[ErrorMetrics] = None


def get_error_logger() -> StructuredErrorLogger:
    """Get the global error logger instance."""
    global _global_error_logger
    if _global_error_logger is None:
        _global_error_logger = StructuredErrorLogger()
        
        # Connect to metrics
        metrics = get_error_metrics()
        _global_error_logger.add_event_handler(metrics.record_error)
    
    return _global_error_logger


def get_error_metrics() -> ErrorMetrics:
    """Get the global error metrics instance."""
    global _global_error_metrics
    if _global_error_metrics is None:
        _global_error_metrics = ErrorMetrics()
    
    return _global_error_metrics