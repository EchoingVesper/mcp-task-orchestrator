"""
Performance metrics collection and monitoring.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric measurement point."""
    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""
    name: str
    count: int
    sum: float
    min: float
    max: float
    avg: float
    recent_values: List[float]
    unit: Optional[str] = None
    
    @property
    def rate_per_second(self) -> float:
        """Calculate rate per second based on recent values."""
        if len(self.recent_values) < 2:
            return 0.0
        return len(self.recent_values) / 60.0  # Assuming 1-minute window


class MetricsCollector:
    """Collects and manages performance metrics."""
    
    def __init__(self, max_points_per_metric: int = 1000):
        self.max_points_per_metric = max_points_per_metric
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points_per_metric))
        self.lock = threading.RLock()
        self.start_time = datetime.utcnow()
    
    def record_value(self, name: str, value: Union[int, float], 
                    tags: Optional[Dict[str, str]] = None, unit: Optional[str] = None):
        """Record a metric value."""
        with self.lock:
            point = MetricPoint(
                name=name,
                value=float(value),
                timestamp=datetime.utcnow(),
                tags=tags or {},
                unit=unit
            )
            self.metrics[name].append(point)
    
    def increment_counter(self, name: str, value: int = 1, 
                         tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        self.record_value(name, value, tags, "count")
    
    def record_timing(self, name: str, duration_seconds: float, 
                     tags: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        self.record_value(name, duration_seconds, tags, "seconds")
    
    def record_gauge(self, name: str, value: Union[int, float], 
                    tags: Optional[Dict[str, str]] = None, unit: Optional[str] = None):
        """Record a gauge (instantaneous value) metric."""
        self.record_value(name, value, tags, unit)
    
    def get_metric_summary(self, name: str, 
                          time_window: Optional[timedelta] = None) -> Optional[MetricSummary]:
        """Get summary statistics for a metric."""
        with self.lock:
            if name not in self.metrics:
                return None
            
            points = list(self.metrics[name])
            if not points:
                return None
            
            # Filter by time window if specified
            if time_window:
                cutoff = datetime.utcnow() - time_window
                points = [p for p in points if p.timestamp >= cutoff]
            
            if not points:
                return None
            
            values = [p.value for p in points]
            
            return MetricSummary(
                name=name,
                count=len(values),
                sum=sum(values),
                min=min(values),
                max=max(values),
                avg=sum(values) / len(values),
                recent_values=values[-60:],  # Last 60 values for rate calculation
                unit=points[0].unit
            )
    
    def get_all_metrics(self, time_window: Optional[timedelta] = None) -> Dict[str, MetricSummary]:
        """Get summaries for all metrics."""
        with self.lock:
            summaries = {}
            for metric_name in self.metrics.keys():
                summary = self.get_metric_summary(metric_name, time_window)
                if summary:
                    summaries[metric_name] = summary
            return summaries
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """Get comprehensive metrics report."""
        uptime = datetime.utcnow() - self.start_time
        
        # Get metrics for different time windows
        last_minute = self.get_all_metrics(timedelta(minutes=1))
        last_hour = self.get_all_metrics(timedelta(hours=1))
        all_time = self.get_all_metrics()
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_metrics": len(self.metrics),
            "collection_start": self.start_time.isoformat(),
            "last_minute": {name: {
                "count": summary.count,
                "avg": summary.avg,
                "rate_per_second": summary.rate_per_second
            } for name, summary in last_minute.items()},
            "last_hour": {name: {
                "count": summary.count,
                "avg": summary.avg,
                "min": summary.min,
                "max": summary.max
            } for name, summary in last_hour.items()},
            "all_time": {name: {
                "count": summary.count,
                "avg": summary.avg,
                "min": summary.min,
                "max": summary.max,
                "total": summary.sum
            } for name, summary in all_time.items()}
        }


class PerformanceTracker:
    """Context manager for tracking operation performance."""
    
    def __init__(self, metrics_collector: MetricsCollector, operation_name: str, 
                 tags: Optional[Dict[str, str]] = None):
        self.metrics_collector = metrics_collector
        self.operation_name = operation_name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.metrics_collector.increment_counter(f"{self.operation_name}.started", tags=self.tags)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.metrics_collector.record_timing(f"{self.operation_name}.duration", duration, self.tags)
        
        if exc_type is None:
            self.metrics_collector.increment_counter(f"{self.operation_name}.success", tags=self.tags)
        else:
            self.metrics_collector.increment_counter(f"{self.operation_name}.error", tags=self.tags)
            self.metrics_collector.increment_counter(f"{self.operation_name}.error.{exc_type.__name__}", tags=self.tags)


def timed_operation(metrics_collector: MetricsCollector, operation_name: str, 
                   tags: Optional[Dict[str, str]] = None):
    """Decorator for tracking operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceTracker(metrics_collector, operation_name, tags):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Global metrics collector
_global_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    return _global_metrics_collector


def set_metrics_collector(collector: MetricsCollector):
    """Set the global metrics collector instance."""
    global _global_metrics_collector
    _global_metrics_collector = collector


# Convenience functions
def record_metric(name: str, value: Union[int, float], 
                 tags: Optional[Dict[str, str]] = None, unit: Optional[str] = None):
    """Record a metric value using the global collector."""
    get_metrics_collector().record_value(name, value, tags, unit)


def increment_counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Increment a counter using the global collector."""
    get_metrics_collector().increment_counter(name, value, tags)


def record_timing(name: str, duration_seconds: float, tags: Optional[Dict[str, str]] = None):
    """Record timing using the global collector."""
    get_metrics_collector().record_timing(name, duration_seconds, tags)


def track_performance(operation_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager for tracking performance using global collector."""
    return PerformanceTracker(get_metrics_collector(), operation_name, tags)