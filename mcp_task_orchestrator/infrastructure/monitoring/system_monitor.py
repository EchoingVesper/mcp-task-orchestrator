"""
Comprehensive system monitoring and resource tracking.
"""

import asyncio
import logging
import psutil
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from .metrics import MetricsCollector, get_metrics_collector
from .health_checks import HealthChecker, HealthCheckResult

logger = logging.getLogger(__name__)


@dataclass
class SystemSnapshot:
    """Snapshot of system resource usage."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_sent_mb: float
    network_recv_mb: float
    process_count: int
    thread_count: int
    file_descriptors: int


@dataclass
class AlertRule:
    """Rule for triggering alerts based on metrics."""
    name: str
    metric_name: str
    threshold: float
    operator: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    duration_seconds: int  # How long condition must persist
    callback: Optional[Callable[[str, float, float], None]] = None
    enabled: bool = True


class SystemMonitor:
    """Comprehensive system monitoring with alerting."""
    
    def __init__(self, collection_interval: int = 30, metrics_collector: Optional[MetricsCollector] = None):
        self.collection_interval = collection_interval
        self.metrics_collector = metrics_collector or get_metrics_collector()
        self.health_checker: Optional[HealthChecker] = None
        self.alert_rules: List[AlertRule] = []
        self.alert_states: Dict[str, Dict[str, Any]] = {}
        
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._initial_network_stats = None
        
        # Setup default alert rules
        self._setup_default_alerts()
    
    def set_health_checker(self, health_checker: HealthChecker):
        """Set the health checker for comprehensive monitoring."""
        self.health_checker = health_checker
    
    def _setup_default_alerts(self):
        """Setup default system alert rules."""
        self.alert_rules.extend([
            AlertRule(
                name="high_cpu_usage",
                metric_name="system.cpu_percent",
                threshold=80.0,
                operator="gt",
                duration_seconds=300,  # 5 minutes
                callback=self._default_alert_callback
            ),
            AlertRule(
                name="high_memory_usage",
                metric_name="system.memory_percent",
                threshold=85.0,
                operator="gt",
                duration_seconds=180,  # 3 minutes
                callback=self._default_alert_callback
            ),
            AlertRule(
                name="low_disk_space",
                metric_name="system.disk_usage_percent",
                threshold=90.0,
                operator="gt",
                duration_seconds=60,  # 1 minute
                callback=self._default_alert_callback
            ),
            AlertRule(
                name="high_file_descriptors",
                metric_name="system.file_descriptors",
                threshold=500,
                operator="gt",
                duration_seconds=120,  # 2 minutes
                callback=self._default_alert_callback
            )
        ])
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self.alert_rules.append(rule)
    
    def remove_alert_rule(self, rule_name: str) -> bool:
        """Remove an alert rule by name."""
        initial_count = len(self.alert_rules)
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        return len(self.alert_rules) < initial_count
    
    def start_monitoring(self):
        """Start background system monitoring."""
        if self._monitoring:
            logger.warning("System monitoring already running")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info(f"System monitoring started with {self.collection_interval}s interval")
    
    def stop_monitoring(self):
        """Stop background system monitoring."""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                snapshot = self._collect_system_snapshot()
                self._record_system_metrics(snapshot)
                self._check_alert_rules()
                
                # Sleep until next collection
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Short delay before retry
    
    def _collect_system_snapshot(self) -> SystemSnapshot:
        """Collect current system resource usage."""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk usage
        disk = psutil.disk_usage('.')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024 ** 3)
        
        # Network usage
        network = psutil.net_io_counters()
        if self._initial_network_stats is None:
            self._initial_network_stats = network
        
        network_sent_mb = (network.bytes_sent - self._initial_network_stats.bytes_sent) / (1024 * 1024)
        network_recv_mb = (network.bytes_recv - self._initial_network_stats.bytes_recv) / (1024 * 1024)
        
        # Process information
        process = psutil.Process()
        process_count = len(psutil.pids())
        thread_count = process.num_threads()
        
        # File descriptors (Unix only)
        try:
            file_descriptors = process.num_fds()
        except (AttributeError, psutil.AccessDenied):
            file_descriptors = 0
        
        return SystemSnapshot(
            timestamp=datetime.utcnow(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            process_count=process_count,
            thread_count=thread_count,
            file_descriptors=file_descriptors
        )
    
    def _record_system_metrics(self, snapshot: SystemSnapshot):
        """Record system metrics."""
        self.metrics_collector.record_gauge("system.cpu_percent", snapshot.cpu_percent, unit="%")
        self.metrics_collector.record_gauge("system.memory_percent", snapshot.memory_percent, unit="%")
        self.metrics_collector.record_gauge("system.memory_available_mb", snapshot.memory_available_mb, unit="MB")
        self.metrics_collector.record_gauge("system.disk_usage_percent", snapshot.disk_usage_percent, unit="%")
        self.metrics_collector.record_gauge("system.disk_free_gb", snapshot.disk_free_gb, unit="GB")
        self.metrics_collector.record_gauge("system.network_sent_mb", snapshot.network_sent_mb, unit="MB")
        self.metrics_collector.record_gauge("system.network_recv_mb", snapshot.network_recv_mb, unit="MB")
        self.metrics_collector.record_gauge("system.process_count", snapshot.process_count, unit="count")
        self.metrics_collector.record_gauge("system.thread_count", snapshot.thread_count, unit="count")
        self.metrics_collector.record_gauge("system.file_descriptors", snapshot.file_descriptors, unit="count")
    
    def _check_alert_rules(self):
        """Check all alert rules against current metrics."""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Get current metric value
            metric_summary = self.metrics_collector.get_metric_summary(
                rule.metric_name, 
                timedelta(seconds=rule.duration_seconds)
            )
            
            if not metric_summary:
                continue
            
            current_value = metric_summary.avg
            
            # Check if threshold is exceeded
            threshold_exceeded = self._evaluate_threshold(current_value, rule.threshold, rule.operator)
            
            # Manage alert state
            if rule.name not in self.alert_states:
                self.alert_states[rule.name] = {
                    "active": False,
                    "triggered_at": None,
                    "last_check": datetime.utcnow()
                }
            
            alert_state = self.alert_states[rule.name]
            
            if threshold_exceeded and not alert_state["active"]:
                # Threshold exceeded, check duration
                if alert_state["triggered_at"] is None:
                    alert_state["triggered_at"] = datetime.utcnow()
                
                duration_exceeded = (datetime.utcnow() - alert_state["triggered_at"]).total_seconds() >= rule.duration_seconds
                
                if duration_exceeded:
                    # Trigger alert
                    alert_state["active"] = True
                    self._trigger_alert(rule, current_value)
            
            elif not threshold_exceeded:
                # Threshold not exceeded, reset state
                alert_state["triggered_at"] = None
                if alert_state["active"]:
                    alert_state["active"] = False
                    self._resolve_alert(rule, current_value)
            
            alert_state["last_check"] = datetime.utcnow()
    
    def _evaluate_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Evaluate if value meets threshold condition."""
        if operator == "gt":
            return value > threshold
        elif operator == "gte":
            return value >= threshold
        elif operator == "lt":
            return value < threshold
        elif operator == "lte":
            return value <= threshold
        elif operator == "eq":
            return value == threshold
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _trigger_alert(self, rule: AlertRule, current_value: float):
        """Trigger an alert."""
        logger.warning(f"ALERT TRIGGERED: {rule.name} - {rule.metric_name} = {current_value} {rule.operator} {rule.threshold}")
        
        if rule.callback:
            try:
                rule.callback(rule.name, current_value, rule.threshold)
            except Exception as e:
                logger.error(f"Alert callback failed for {rule.name}: {e}")
        
        # Record alert metric
        self.metrics_collector.increment_counter(f"alerts.triggered.{rule.name}")
    
    def _resolve_alert(self, rule: AlertRule, current_value: float):
        """Resolve an alert."""
        logger.info(f"ALERT RESOLVED: {rule.name} - {rule.metric_name} = {current_value}")
        self.metrics_collector.increment_counter(f"alerts.resolved.{rule.name}")
    
    def _default_alert_callback(self, alert_name: str, current_value: float, threshold: float):
        """Default alert callback that just logs."""
        logger.critical(f"System alert: {alert_name} - Current: {current_value}, Threshold: {threshold}")
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including health checks."""
        # Get current system snapshot
        snapshot = self._collect_system_snapshot()
        
        # Get health check results if available
        health_results = {}
        overall_healthy = True
        
        if self.health_checker:
            try:
                health_results = await self.health_checker.run_all_checks()
                overall_healthy = self.health_checker.get_overall_health(health_results)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                overall_healthy = False
        
        # Get metrics report
        metrics_report = self.metrics_collector.get_metrics_report()
        
        # Get active alerts
        active_alerts = [
            rule.name for rule in self.alert_rules 
            if self.alert_states.get(rule.name, {}).get("active", False)
        ]
        
        return {
            "overall_healthy": overall_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "system_snapshot": {
                "cpu_percent": snapshot.cpu_percent,
                "memory_percent": snapshot.memory_percent,
                "memory_available_mb": snapshot.memory_available_mb,
                "disk_usage_percent": snapshot.disk_usage_percent,
                "disk_free_gb": snapshot.disk_free_gb,
                "process_count": snapshot.process_count,
                "thread_count": snapshot.thread_count,
                "file_descriptors": snapshot.file_descriptors
            },
            "health_checks": {
                name: {
                    "healthy": result.healthy,
                    "message": result.message,
                    "duration_ms": result.duration_ms
                } for name, result in health_results.items()
            },
            "active_alerts": active_alerts,
            "alert_summary": {
                "total_rules": len(self.alert_rules),
                "active_count": len(active_alerts),
                "rules": [
                    {
                        "name": rule.name,
                        "metric": rule.metric_name,
                        "threshold": rule.threshold,
                        "operator": rule.operator,
                        "active": self.alert_states.get(rule.name, {}).get("active", False)
                    } for rule in self.alert_rules
                ]
            },
            "metrics_summary": metrics_report
        }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status."""
        return {
            "monitoring_active": self._monitoring,
            "collection_interval": self.collection_interval,
            "alert_rules_count": len(self.alert_rules),
            "active_alerts": len([
                rule for rule in self.alert_rules 
                if self.alert_states.get(rule.name, {}).get("active", False)
            ])
        }


# Global system monitor
_global_system_monitor: Optional[SystemMonitor] = None


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    global _global_system_monitor
    if _global_system_monitor is None:
        _global_system_monitor = SystemMonitor()
    return _global_system_monitor


def set_system_monitor(monitor: SystemMonitor):
    """Set the global system monitor instance."""
    global _global_system_monitor
    _global_system_monitor = monitor