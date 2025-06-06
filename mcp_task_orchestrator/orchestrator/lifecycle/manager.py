"""
Task Lifecycle Manager

This module provides the main TaskLifecycleManager class that coordinates
all lifecycle operations including stale detection, archival, and cleanup.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from ...db.persistence import DatabasePersistenceManager
from ..artifacts import ArtifactManager
from .base import LifecycleConfig, TaskLifecycleState, StaleTaskReason
from .stale_detection import StaleTaskDetector
from .archival import TaskArchivalManager
from .cleanup import WorkspaceCleanupManager

logger = logging.getLogger("mcp_task_orchestrator.lifecycle.manager")


class TaskLifecycleManager:
    """Main manager for task lifecycle operations."""
    
    def __init__(self, state_manager: DatabasePersistenceManager, 
                 artifact_manager: ArtifactManager, config: Optional[LifecycleConfig] = None):
        """Initialize the TaskLifecycleManager.
        
        Args:
            state_manager: Database persistence manager
            artifact_manager: Artifact management instance
            config: Optional lifecycle configuration
        """
        self.state_manager = state_manager
        self.artifact_manager = artifact_manager
        self.config = config or LifecycleConfig()
        self.logger = logger
        
        # Initialize specialized managers
        self.stale_detector = StaleTaskDetector(state_manager, self.config)
        self.archival_manager = TaskArchivalManager(state_manager, artifact_manager, self.config)
        self.cleanup_manager = WorkspaceCleanupManager(state_manager, artifact_manager, self.config)
        
        # Tracking for maintenance operations
        self._maintenance_operations = {}
    
    async def detect_stale_tasks(self, comprehensive_scan: bool = False) -> List[Dict[str, Any]]:
        """Detect tasks that have become stale.
        
        Args:
            comprehensive_scan: Whether to perform comprehensive scanning
            
        Returns:
            List of stale task information
        """
        return await self.stale_detector.detect_stale_tasks(comprehensive_scan)
    
    async def archive_task(self, task_id: str, archive_reason: str = "stale_timeout",
                          preserve_artifacts: bool = True, 
                          task_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Archive a single task.
        
        Args:
            task_id: ID of task to archive
            archive_reason: Reason for archival
            preserve_artifacts: Whether to preserve task artifacts
            task_info: Optional additional task information
            
        Returns:
            Archive operation result
        """
        return await self.archival_manager.archive_task(
            task_id, archive_reason, preserve_artifacts, task_info
        )
    
    async def bulk_archive_tasks(self, task_ids: List[str], archive_reason: str = "bulk_cleanup",
                                preserve_artifacts: bool = False) -> Dict[str, Any]:
        """Archive multiple tasks in a batch operation.
        
        Args:
            task_ids: List of task IDs to archive
            archive_reason: Reason for archival
            preserve_artifacts: Whether to preserve artifacts
            
        Returns:
            Bulk archive operation results
        """
        return await self.archival_manager.bulk_archive_tasks(
            task_ids, archive_reason, preserve_artifacts
        )
    
    async def perform_workspace_cleanup(self, cleanup_type: str = "standard", 
                                       aggressive: bool = False) -> Dict[str, Any]:
        """Perform comprehensive workspace cleanup.
        
        Args:
            cleanup_type: Type of cleanup to perform
            aggressive: Whether to use aggressive cleanup strategies
            
        Returns:
            Cleanup operation results
        """
        return await self.cleanup_manager.perform_workspace_cleanup(cleanup_type, aggressive)
    
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up archives that have exceeded their retention period."""
        return await self.archival_manager.cleanup_expired_archives()
    
    async def comprehensive_maintenance(self, aggressive: bool = False) -> Dict[str, Any]:
        """Perform comprehensive maintenance operations.
        
        Args:
            aggressive: Whether to use aggressive maintenance strategies
            
        Returns:
            Comprehensive maintenance results
        """
        maintenance_id = f"maintenance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        results = {
            "maintenance_id": maintenance_id,
            "started_at": datetime.utcnow().isoformat(),
            "aggressive_mode": aggressive,
            "operations": [],
            "total_summary": {},
            "errors": []
        }
        
        try:
            self.logger.info(f"Starting comprehensive maintenance {maintenance_id}")
            
            # Step 1: Detect stale tasks
            self.logger.info("Detecting stale tasks...")
            stale_tasks = await self.detect_stale_tasks(comprehensive_scan=True)
            
            stale_operation = {
                "operation": "stale_detection",
                "tasks_found": len(stale_tasks),
                "critical_count": len([t for t in stale_tasks if t.get("max_severity") == "critical"]),
                "high_count": len([t for t in stale_tasks if t.get("max_severity") == "high"])
            }
            results["operations"].append(stale_operation)
            
            # Step 2: Archive eligible stale tasks
            if stale_tasks:
                self.logger.info(f"Archiving {len(stale_tasks)} stale tasks...")
                eligible_task_ids = [
                    task["task_id"] for task in stale_tasks 
                    if task.get("auto_cleanup_eligible", False) or aggressive
                ]
                
                if eligible_task_ids:
                    archive_results = await self.bulk_archive_tasks(
                        eligible_task_ids, "maintenance_cleanup", preserve_artifacts=not aggressive
                    )
                    results["operations"].append({
                        "operation": "stale_task_archival",
                        **archive_results
                    })
            
            # Step 3: Workspace cleanup
            self.logger.info("Performing workspace cleanup...")
            cleanup_results = await self.perform_workspace_cleanup("comprehensive", aggressive)
            results["operations"].append(cleanup_results)
            
            # Step 4: Clean up expired archives
            self.logger.info("Cleaning up expired archives...")
            archive_cleanup = await self.cleanup_expired_archives()
            results["operations"].append({
                "operation": "expired_archive_cleanup",
                **archive_cleanup
            })
            
            # Calculate total summary
            results["total_summary"] = {
                "total_tasks_processed": sum(
                    op.get("total_tasks", op.get("tasks_found", 0)) 
                    for op in results["operations"]
                ),
                "total_items_cleaned": sum(
                    op.get("items_cleaned", op.get("total_cleaned", 0)) 
                    for op in results["operations"]
                ),
                "total_space_freed_mb": sum(
                    op.get("space_freed_mb", op.get("workspace_freed_mb", 0)) 
                    for op in results["operations"]
                ),
                "operations_completed": len(results["operations"])
            }
            
            results["completed_at"] = datetime.utcnow().isoformat()
            results["status"] = "completed"
            
            self.logger.info(
                f"Maintenance {maintenance_id} completed: "
                f"{results['total_summary']['total_items_cleaned']} items cleaned, "
                f"{results['total_summary']['total_space_freed_mb']:.2f}MB freed"
            )
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["completed_at"] = datetime.utcnow().isoformat()
            results["errors"].append(str(e))
            
            self.logger.error(f"Maintenance {maintenance_id} failed: {e}")
        
        return results
    
    async def get_lifecycle_status(self) -> Dict[str, Any]:
        """Get current lifecycle management status and metrics."""
        try:
            # Get stale tasks without comprehensive scan for quick status
            stale_tasks = await self.detect_stale_tasks(comprehensive_scan=False)
            
            # Categorize by severity
            critical_tasks = [t for t in stale_tasks if t.get("max_severity") == "critical"]
            high_priority_tasks = [t for t in stale_tasks if t.get("max_severity") == "high"]
            medium_priority_tasks = [t for t in stale_tasks if t.get("max_severity") == "medium"]
            
            # Get archive statistics
            with self.state_manager.session_scope() as session:
                from ...db.models import TaskArchiveModel
                
                total_archives = session.query(TaskArchiveModel).count()
                
                # Count archives by reason
                archive_reasons = {}
                archives = session.query(TaskArchiveModel).all()
                for archive in archives:
                    reason = archive.archive_reason
                    archive_reasons[reason] = archive_reasons.get(reason, 0) + 1
            
            return {
                "status": "healthy",
                "stale_task_summary": {
                    "total_stale_tasks": len(stale_tasks),
                    "critical_priority": len(critical_tasks),
                    "high_priority": len(high_priority_tasks),
                    "medium_priority": len(medium_priority_tasks),
                    "auto_cleanup_eligible": len([
                        t for t in stale_tasks if t.get("auto_cleanup_eligible", False)
                    ])
                },
                "archive_summary": {
                    "total_archives": total_archives,
                    "archive_reasons": archive_reasons
                },
                "config": {
                    "stale_threshold_hours": self.config.stale_threshold_hours,
                    "archive_threshold_days": self.config.archive_threshold_days,
                    "cleanup_batch_size": self.config.cleanup_batch_size
                },
                "last_checked": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting lifecycle status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_checked": datetime.utcnow().isoformat()
            }
    
    async def schedule_maintenance(self, maintenance_type: str = "standard", 
                                 delay_hours: int = 0) -> Dict[str, Any]:
        """Schedule a maintenance operation for future execution.
        
        Args:
            maintenance_type: Type of maintenance to schedule
            delay_hours: Hours to delay before execution
            
        Returns:
            Scheduling result
        """
        scheduled_time = datetime.utcnow() + timedelta(hours=delay_hours)
        maintenance_id = f"scheduled_{maintenance_type}_{scheduled_time.strftime('%Y%m%d_%H%M%S')}"
        
        # Store scheduled maintenance (in a real implementation, this would use a proper scheduler)
        self._maintenance_operations[maintenance_id] = {
            "type": maintenance_type,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.utcnow()
        }
        
        self.logger.info(f"Scheduled maintenance {maintenance_id} for {scheduled_time}")
        
        return {
            "maintenance_id": maintenance_id,
            "scheduled_time": scheduled_time.isoformat(),
            "maintenance_type": maintenance_type,
            "status": "scheduled"
        }