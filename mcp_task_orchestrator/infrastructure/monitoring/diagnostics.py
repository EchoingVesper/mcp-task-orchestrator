"""
Diagnostic tools and system analysis capabilities.
"""

import asyncio
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import json

from .health_checks import HealthChecker
from .system_monitor import SystemMonitor
from ...domain.exceptions import get_error_metrics

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""
    name: str
    category: str
    status: str  # 'pass', 'warning', 'error', 'info'
    message: str
    details: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime


@dataclass
class SystemInfo:
    """Comprehensive system information."""
    python_version: str
    platform: str
    working_directory: str
    process_id: int
    memory_usage_mb: float
    cpu_count: int
    disk_free_gb: float
    environment_vars: Dict[str, str]
    installed_packages: List[str]


class DiagnosticRunner:
    """Runs comprehensive system diagnostics."""
    
    def __init__(self, health_checker: Optional[HealthChecker] = None,
                 system_monitor: Optional[SystemMonitor] = None):
        self.health_checker = health_checker
        self.system_monitor = system_monitor
        self.diagnostic_functions: Dict[str, Callable] = {}
        
        # Register default diagnostics
        self._register_default_diagnostics()
    
    def _register_default_diagnostics(self):
        """Register default diagnostic functions."""
        self.diagnostic_functions.update({
            "system_info": self._diagnose_system_info,
            "database_integrity": self._diagnose_database_integrity,
            "file_permissions": self._diagnose_file_permissions,
            "configuration_validation": self._diagnose_configuration,
            "dependency_check": self._diagnose_dependencies,
            "error_analysis": self._diagnose_error_patterns,
            "performance_analysis": self._diagnose_performance,
            "resource_utilization": self._diagnose_resource_utilization
        })
    
    def register_diagnostic(self, name: str, diagnostic_func: Callable):
        """Register a custom diagnostic function."""
        self.diagnostic_functions[name] = diagnostic_func
    
    async def run_all_diagnostics(self) -> Dict[str, DiagnosticResult]:
        """Run all registered diagnostics."""
        results = {}
        
        for name, diagnostic_func in self.diagnostic_functions.items():
            try:
                result = await self._run_diagnostic(name, diagnostic_func)
                results[name] = result
            except Exception as e:
                logger.error(f"Diagnostic {name} failed: {e}")
                results[name] = DiagnosticResult(
                    name=name,
                    category="error",
                    status="error",
                    message=f"Diagnostic failed: {str(e)}",
                    details={"exception": str(e), "traceback": traceback.format_exc()},
                    recommendations=["Check logs for detailed error information"],
                    timestamp=datetime.utcnow()
                )
        
        return results
    
    async def run_diagnostic(self, name: str) -> Optional[DiagnosticResult]:
        """Run a specific diagnostic."""
        if name not in self.diagnostic_functions:
            return None
        
        diagnostic_func = self.diagnostic_functions[name]
        return await self._run_diagnostic(name, diagnostic_func)
    
    async def _run_diagnostic(self, name: str, diagnostic_func: Callable) -> DiagnosticResult:
        """Run a single diagnostic function."""
        if asyncio.iscoroutinefunction(diagnostic_func):
            return await diagnostic_func()
        else:
            return diagnostic_func()
    
    async def _diagnose_system_info(self) -> DiagnosticResult:
        """Diagnose basic system information."""
        try:
            import psutil
            import platform
            
            process = psutil.Process()
            memory_info = process.memory_info()
            
            system_info = SystemInfo(
                python_version=sys.version,
                platform=platform.platform(),
                working_directory=os.getcwd(),
                process_id=os.getpid(),
                memory_usage_mb=memory_info.rss / (1024 * 1024),
                cpu_count=psutil.cpu_count(),
                disk_free_gb=psutil.disk_usage('.').free / (1024**3),
                environment_vars={k: v for k, v in os.environ.items() if 'SECRET' not in k.upper()},
                installed_packages=[]
            )
            
            # Check for potential issues
            recommendations = []
            if system_info.memory_usage_mb > 500:
                recommendations.append("High memory usage detected, consider monitoring for leaks")
            if system_info.disk_free_gb < 1:
                recommendations.append("Low disk space, consider cleanup")
            
            status = "warning" if recommendations else "pass"
            
            return DiagnosticResult(
                name="system_info",
                category="system",
                status=status,
                message="System information collected",
                details=system_info.__dict__,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="system_info",
                category="system",
                status="error",
                message=f"Failed to collect system info: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check system configuration"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_database_integrity(self) -> DiagnosticResult:
        """Diagnose database integrity and connectivity."""
        try:
            # Check for SQLite database files
            db_files = list(Path('.').glob('**/*.db'))
            
            issues = []
            details = {"database_files": [str(f) for f in db_files]}
            
            for db_file in db_files:
                try:
                    # Test database connectivity
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    
                    # Check integrity
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    
                    if integrity_result != "ok":
                        issues.append(f"Database {db_file} has integrity issues: {integrity_result}")
                    
                    # Check for common issues
                    cursor.execute("PRAGMA foreign_key_check")
                    fk_violations = cursor.fetchall()
                    if fk_violations:
                        issues.append(f"Database {db_file} has foreign key violations")
                    
                    conn.close()
                    
                except Exception as e:
                    issues.append(f"Cannot access database {db_file}: {str(e)}")
            
            status = "error" if issues else "pass"
            message = f"Checked {len(db_files)} database files"
            
            return DiagnosticResult(
                name="database_integrity",
                category="database",
                status=status,
                message=message,
                details=details,
                recommendations=["Run database repair if issues found"] if issues else [],
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="database_integrity",
                category="database",
                status="error",
                message=f"Database diagnostic failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check database configuration"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_file_permissions(self) -> DiagnosticResult:
        """Diagnose file and directory permissions."""
        try:
            issues = []
            checked_paths = []
            
            # Check important directories
            important_dirs = ['.', '.task_orchestrator', 'logs', 'config']
            
            for dir_path in important_dirs:
                path = Path(dir_path)
                if path.exists():
                    checked_paths.append(str(path))
                    
                    # Check read/write permissions
                    if not os.access(path, os.R_OK):
                        issues.append(f"No read permission for {path}")
                    if not os.access(path, os.W_OK):
                        issues.append(f"No write permission for {path}")
                    
                    # Check for sensitive files with wrong permissions
                    if path.name == 'config' and os.access(path, os.R_OK | os.W_OK | os.X_OK):
                        config_files = list(path.glob('*.yaml')) + list(path.glob('*.json'))
                        for config_file in config_files:
                            if os.stat(config_file).st_mode & 0o077:  # World or group readable
                                issues.append(f"Config file {config_file} has overly permissive permissions")
            
            status = "warning" if issues else "pass"
            message = f"Checked permissions for {len(checked_paths)} paths"
            
            return DiagnosticResult(
                name="file_permissions",
                category="security",
                status=status,
                message=message,
                details={"checked_paths": checked_paths, "issues": issues},
                recommendations=["Fix file permissions"] if issues else [],
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="file_permissions",
                category="security",
                status="error",
                message=f"Permission check failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check file system access"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_configuration(self) -> DiagnosticResult:
        """Diagnose configuration validity."""
        try:
            issues = []
            config_files = []
            
            # Look for configuration files
            config_patterns = ['config/*.yaml', 'config/*.json', '*.toml', '*.cfg']
            
            for pattern in config_patterns:
                config_files.extend(Path('.').glob(pattern))
            
            for config_file in config_files:
                try:
                    if config_file.suffix in ['.yaml', '.yml']:
                        import yaml
                        with open(config_file) as f:
                            yaml.safe_load(f)
                    elif config_file.suffix == '.json':
                        with open(config_file) as f:
                            json.load(f)
                    elif config_file.suffix == '.toml':
                        import tomli
                        with open(config_file, 'rb') as f:
                            tomli.load(f)
                            
                except Exception as e:
                    issues.append(f"Invalid config file {config_file}: {str(e)}")
            
            status = "error" if issues else "pass"
            message = f"Validated {len(config_files)} configuration files"
            
            return DiagnosticResult(
                name="configuration_validation",
                category="configuration",
                status=status,
                message=message,
                details={"config_files": [str(f) for f in config_files], "issues": issues},
                recommendations=["Fix configuration file syntax"] if issues else [],
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="configuration_validation",
                category="configuration",
                status="error",
                message=f"Configuration diagnostic failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check configuration system"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_dependencies(self) -> DiagnosticResult:
        """Diagnose dependency availability and versions."""
        try:
            import pkg_resources
            
            # Core dependencies to check
            core_deps = ['asyncio', 'sqlite3', 'json', 'pathlib', 'typing']
            optional_deps = ['psutil', 'yaml', 'pydantic', 'mcp']
            
            missing_core = []
            missing_optional = []
            version_info = {}
            
            # Check core dependencies
            for dep in core_deps:
                try:
                    __import__(dep)
                except ImportError:
                    missing_core.append(dep)
            
            # Check optional dependencies
            for dep in optional_deps:
                try:
                    module = __import__(dep)
                    if hasattr(module, '__version__'):
                        version_info[dep] = module.__version__
                    else:
                        version_info[dep] = "unknown"
                except ImportError:
                    missing_optional.append(dep)
            
            issues = []
            if missing_core:
                issues.extend([f"Missing core dependency: {dep}" for dep in missing_core])
            
            status = "error" if missing_core else ("warning" if missing_optional else "pass")
            message = f"Checked dependencies - {len(version_info)} available"
            
            recommendations = []
            if missing_core:
                recommendations.append("Install missing core dependencies immediately")
            if missing_optional:
                recommendations.append("Consider installing optional dependencies for full functionality")
            
            return DiagnosticResult(
                name="dependency_check",
                category="dependencies",
                status=status,
                message=message,
                details={
                    "available": version_info,
                    "missing_core": missing_core,
                    "missing_optional": missing_optional
                },
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="dependency_check",
                category="dependencies",
                status="error",
                message=f"Dependency check failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check Python environment"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_error_patterns(self) -> DiagnosticResult:
        """Analyze error patterns and trends."""
        try:
            error_metrics = get_error_metrics()
            health_status = error_metrics.get_health_status()
            
            # Analyze error patterns
            metrics = health_status["metrics"]
            issues = []
            recommendations = []
            
            # Check error rates
            hourly_errors = metrics["last_hour"]["total_errors"]
            critical_errors = metrics["critical_errors_count"]
            
            if critical_errors > 0:
                issues.append(f"{critical_errors} critical errors detected")
                recommendations.append("Address critical errors immediately")
            
            if hourly_errors > 10:
                issues.append(f"High error rate: {hourly_errors} errors in last hour")
                recommendations.append("Investigate error causes")
            
            # Check frequent errors
            frequent_errors = metrics["frequent_errors"]
            if frequent_errors and frequent_errors[0]["count"] > 5:
                top_error = frequent_errors[0]
                issues.append(f"Frequent error pattern: {top_error['error_type']} ({top_error['count']} occurrences)")
                recommendations.append(f"Focus on resolving {top_error['error_type']} errors")
            
            status = health_status["status"]
            if status in ["critical", "warning"]:
                status = "error" if status == "critical" else "warning"
            else:
                status = "pass"
            
            return DiagnosticResult(
                name="error_analysis",
                category="errors",
                status=status,
                message=health_status["message"],
                details=metrics,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="error_analysis",
                category="errors",
                status="error",
                message=f"Error analysis failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check error tracking system"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_performance(self) -> DiagnosticResult:
        """Analyze system performance metrics."""
        try:
            if not self.system_monitor:
                return DiagnosticResult(
                    name="performance_analysis",
                    category="performance",
                    status="info",
                    message="System monitor not available",
                    details={},
                    recommendations=["Enable system monitoring for performance analysis"],
                    timestamp=datetime.utcnow()
                )
            
            status = await self.system_monitor.get_comprehensive_status()
            snapshot = status["system_snapshot"]
            
            issues = []
            recommendations = []
            
            # Analyze performance metrics
            if snapshot["cpu_percent"] > 80:
                issues.append(f"High CPU usage: {snapshot['cpu_percent']:.1f}%")
                recommendations.append("Investigate CPU-intensive processes")
            
            if snapshot["memory_percent"] > 85:
                issues.append(f"High memory usage: {snapshot['memory_percent']:.1f}%")
                recommendations.append("Check for memory leaks")
            
            if snapshot["disk_usage_percent"] > 90:
                issues.append(f"Low disk space: {snapshot['disk_usage_percent']:.1f}% used")
                recommendations.append("Clean up disk space")
            
            if snapshot["file_descriptors"] > 500:
                issues.append(f"High file descriptor count: {snapshot['file_descriptors']}")
                recommendations.append("Check for resource leaks")
            
            diagnostic_status = "error" if any("High" in issue for issue in issues) else ("warning" if issues else "pass")
            
            return DiagnosticResult(
                name="performance_analysis",
                category="performance",
                status=diagnostic_status,
                message=f"Performance analysis complete - {len(issues)} issues found",
                details=snapshot,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="performance_analysis",
                category="performance",
                status="error",
                message=f"Performance analysis failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check system monitoring setup"],
                timestamp=datetime.utcnow()
            )
    
    async def _diagnose_resource_utilization(self) -> DiagnosticResult:
        """Analyze resource utilization patterns."""
        try:
            if not self.system_monitor:
                return DiagnosticResult(
                    name="resource_utilization",
                    category="resources",
                    status="info",
                    message="System monitor not available for resource analysis",
                    details={},
                    recommendations=["Enable system monitoring"],
                    timestamp=datetime.utcnow()
                )
            
            # Get metrics summary
            metrics_report = self.system_monitor.metrics_collector.get_metrics_report()
            
            analysis = {}
            recommendations = []
            
            # Analyze resource trends
            if "all_time" in metrics_report:
                all_time_metrics = metrics_report["all_time"]
                
                # Check for resource growth patterns
                if "system.memory_percent" in all_time_metrics:
                    memory_stats = all_time_metrics["system.memory_percent"]
                    if memory_stats["max"] - memory_stats["min"] > 20:
                        recommendations.append("Memory usage varies significantly, check for leaks")
                
                if "system.file_descriptors" in all_time_metrics:
                    fd_stats = all_time_metrics["system.file_descriptors"]
                    if fd_stats["avg"] > 100:
                        recommendations.append("High average file descriptor usage")
            
            status = "warning" if recommendations else "pass"
            
            return DiagnosticResult(
                name="resource_utilization",
                category="resources",
                status=status,
                message="Resource utilization analysis complete",
                details=metrics_report,
                recommendations=recommendations,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return DiagnosticResult(
                name="resource_utilization",
                category="resources",
                status="error",
                message=f"Resource analysis failed: {str(e)}",
                details={"error": str(e)},
                recommendations=["Check resource monitoring"],
                timestamp=datetime.utcnow()
            )
    
    def generate_diagnostic_report(self, results: Dict[str, DiagnosticResult]) -> str:
        """Generate a comprehensive diagnostic report."""
        report_lines = [
            "# MCP Task Orchestrator - Diagnostic Report",
            f"Generated: {datetime.utcnow().isoformat()}",
            "",
            "## Summary",
            ""
        ]
        
        # Count by status
        status_counts = {"pass": 0, "warning": 0, "error": 0, "info": 0}
        for result in results.values():
            status_counts[result.status] += 1
        
        report_lines.extend([
            f"- ✅ Passed: {status_counts['pass']}",
            f"- ⚠️  Warnings: {status_counts['warning']}",
            f"- ❌ Errors: {status_counts['error']}",
            f"- ℹ️  Info: {status_counts['info']}",
            ""
        ])
        
        # Group by category
        categories = {}
        for result in results.values():
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Report by category
        for category, category_results in categories.items():
            report_lines.extend([
                f"## {category.title()} Diagnostics",
                ""
            ])
            
            for result in category_results:
                status_icon = {"pass": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}[result.status]
                report_lines.extend([
                    f"### {status_icon} {result.name}",
                    f"**Status**: {result.status.upper()}",
                    f"**Message**: {result.message}",
                    ""
                ])
                
                if result.recommendations:
                    report_lines.extend([
                        "**Recommendations**:",
                        ""
                    ])
                    for rec in result.recommendations:
                        report_lines.append(f"- {rec}")
                    report_lines.append("")
        
        return "\n".join(report_lines)