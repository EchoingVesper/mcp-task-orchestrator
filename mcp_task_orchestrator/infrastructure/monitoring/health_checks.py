"""
Health check infrastructure for monitoring system status.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import logging
import traceback

from ...domain import TaskRepository, StateRepository

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    healthy: bool
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    duration_ms: float


class HealthChecker:
    """
    Performs health checks on critical system components.
    
    This class provides both individual and comprehensive health checks
    for monitoring the orchestrator's operational status.
    """
    
    def __init__(
        self,
        task_repository: Optional[TaskRepository] = None,
        state_repository: Optional[StateRepository] = None
    ):
        self.task_repository = task_repository
        self.state_repository = state_repository
        self.check_registry = {}
        
        # Register default health checks
        self._register_default_checks()
    
    def _register_default_checks(self):
        """Register default health check functions."""
        self.check_registry = {
            "database_connectivity": self._check_database_connectivity,
            "task_repository": self._check_task_repository,
            "state_repository": self._check_state_repository,
            "memory_usage": self._check_memory_usage,
            "disk_space": self._check_disk_space
        }
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """
        Run all registered health checks.
        
        Returns:
            Dictionary mapping check names to results
        """
        results = {}
        
        for check_name, check_func in self.check_registry.items():
            try:
                result = await self._run_single_check(check_name, check_func)
                results[check_name] = result
            except Exception as e:
                logger.error(f"Health check {check_name} failed with exception: {e}")
                results[check_name] = HealthCheckResult(
                    name=check_name,
                    healthy=False,
                    message=f"Check failed with exception: {str(e)}",
                    details={"exception": str(e), "traceback": traceback.format_exc()},
                    timestamp=datetime.utcnow(),
                    duration_ms=0.0
                )
        
        return results
    
    async def run_check(self, check_name: str) -> Optional[HealthCheckResult]:
        """
        Run a specific health check.
        
        Args:
            check_name: Name of the check to run
            
        Returns:
            Health check result or None if check not found
        """
        if check_name not in self.check_registry:
            logger.warning(f"Unknown health check: {check_name}")
            return None
        
        check_func = self.check_registry[check_name]
        return await self._run_single_check(check_name, check_func)
    
    async def _run_single_check(self, name: str, check_func) -> HealthCheckResult:
        """Run a single health check function with timing."""
        start_time = datetime.utcnow()
        
        try:
            result = await check_func()
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            result.timestamp = start_time
            result.duration_ms = duration_ms
            
            return result
            
        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheckResult(
                name=name,
                healthy=False,
                message=f"Check failed: {str(e)}",
                details={"exception": str(e)},
                timestamp=start_time,
                duration_ms=duration_ms
            )
    
    async def _check_database_connectivity(self) -> HealthCheckResult:
        """Check basic database connectivity."""
        if not self.task_repository:
            return HealthCheckResult(
                name="database_connectivity",
                healthy=False,
                message="No task repository configured",
                details={}
            )
        
        try:
            # Try a simple operation
            tasks = await self.task_repository.list_all_tasks()
            
            return HealthCheckResult(
                name="database_connectivity",
                healthy=True,
                message="Database connection successful",
                details={"task_count": len(tasks)}
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="database_connectivity",
                healthy=False,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _check_task_repository(self) -> HealthCheckResult:
        """Check task repository functionality."""
        if not self.task_repository:
            return HealthCheckResult(
                name="task_repository",
                healthy=False,
                message="Task repository not available",
                details={}
            )
        
        try:
            # Test basic operations
            tasks = await self.task_repository.list_all_tasks()
            active_count = len([t for t in tasks if t.status.is_active()])
            
            return HealthCheckResult(
                name="task_repository",
                healthy=True,
                message="Task repository operational",
                details={
                    "total_tasks": len(tasks),
                    "active_tasks": active_count
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="task_repository",
                healthy=False,
                message=f"Task repository error: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _check_state_repository(self) -> HealthCheckResult:
        """Check state repository functionality."""
        if not self.state_repository:
            return HealthCheckResult(
                name="state_repository",
                healthy=False,
                message="State repository not available",
                details={}
            )
        
        try:
            # Test session listing
            sessions = await self.state_repository.list_active_sessions()
            
            return HealthCheckResult(
                name="state_repository",
                healthy=True,
                message="State repository operational",
                details={
                    "active_sessions": len(sessions)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="state_repository",
                healthy=False,
                message=f"State repository error: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _check_memory_usage(self) -> HealthCheckResult:
        """Check memory usage."""
        try:
            import psutil
            
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Consider unhealthy if using more than 80% of available memory
            healthy = memory_percent < 80.0
            
            return HealthCheckResult(
                name="memory_usage",
                healthy=healthy,
                message=f"Memory usage: {memory_percent:.1f}%",
                details={
                    "memory_percent": memory_percent,
                    "memory_rss_mb": memory_info.rss / (1024 * 1024),
                    "memory_vms_mb": memory_info.vms / (1024 * 1024)
                }
            )
            
        except ImportError:
            return HealthCheckResult(
                name="memory_usage",
                healthy=True,
                message="psutil not available, memory check skipped",
                details={}
            )
        except Exception as e:
            return HealthCheckResult(
                name="memory_usage",
                healthy=False,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    async def _check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        try:
            import shutil
            
            # Check current directory disk space
            usage = shutil.disk_usage(".")
            free_percent = (usage.free / usage.total) * 100
            
            # Consider unhealthy if less than 10% free space
            healthy = free_percent > 10.0
            
            return HealthCheckResult(
                name="disk_space",
                healthy=healthy,
                message=f"Free disk space: {free_percent:.1f}%",
                details={
                    "free_percent": free_percent,
                    "free_gb": usage.free / (1024**3),
                    "total_gb": usage.total / (1024**3)
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                healthy=False,
                message=f"Disk space check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def register_check(self, name: str, check_func):
        """Register a custom health check function."""
        self.check_registry[name] = check_func
    
    def get_overall_health(self, results: Dict[str, HealthCheckResult]) -> bool:
        """Determine overall system health from individual check results."""
        return all(result.healthy for result in results.values())