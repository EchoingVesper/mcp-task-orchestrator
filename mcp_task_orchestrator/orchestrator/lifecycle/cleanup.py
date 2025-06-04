"""
Cleanup Operations Module

This module handles various cleanup operations including workspace cleanup,
incomplete workflow resolution, and maintenance operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from ...db.persistence import DatabasePersistenceManager
from ...db.models import TaskBreakdownModel, SubTaskModel, MaintenanceOperationModel
from ..artifacts import ArtifactManager
from .base import LifecycleConfig, LifecycleOperation

logger = logging.getLogger("mcp_task_orchestrator.lifecycle.cleanup")


class WorkspaceCleanupManager:
    """Handles workspace cleanup and maintenance operations."""
    
    def __init__(self, state_manager: DatabasePersistenceManager, 
                 artifact_manager: ArtifactManager, config: LifecycleConfig):
        self.state_manager = state_manager
        self.artifact_manager = artifact_manager
        self.config = config
        self.logger = logger
    
    async def perform_workspace_cleanup(self, cleanup_type: str = "standard", 
                                       aggressive: bool = False) -> Dict[str, Any]:
        """Perform comprehensive workspace cleanup.
        
        Args:
            cleanup_type: Type of cleanup to perform
            aggressive: Whether to use aggressive cleanup strategies
            
        Returns:
            Cleanup operation results
        """
        cleanup_results = {
            "cleanup_type": cleanup_type,
            "aggressive_mode": aggressive,
            "operations": [],
            "total_cleaned": 0,
            "errors": [],
            "workspace_freed_mb": 0
        }
        
        try:
            # Clean up temporary files
            temp_cleanup = await self._cleanup_temporary_files()
            cleanup_results["operations"].append(temp_cleanup)
            
            # Clean up orphaned artifacts
            artifact_cleanup = await self._cleanup_orphaned_artifacts()
            cleanup_results["operations"].append(artifact_cleanup)
            
            # Resolve incomplete workflows
            workflow_cleanup = await self._cleanup_incomplete_workflows(aggressive)
            cleanup_results["operations"].append(workflow_cleanup)
            
            # Clean up stale maintenance operations
            maintenance_cleanup = await self._cleanup_stale_maintenance_operations()
            cleanup_results["operations"].append(maintenance_cleanup)
            
            # Calculate totals
            cleanup_results["total_cleaned"] = sum(
                op.get("items_cleaned", 0) for op in cleanup_results["operations"]
            )
            cleanup_results["workspace_freed_mb"] = sum(
                op.get("space_freed_mb", 0) for op in cleanup_results["operations"]
            )
            
            self.logger.info(
                f"Workspace cleanup completed: {cleanup_results['total_cleaned']} items cleaned, "
                f"{cleanup_results['workspace_freed_mb']:.2f}MB freed"
            )
            
        except Exception as e:
            self.logger.error(f"Error during workspace cleanup: {e}")
            cleanup_results["errors"].append(str(e))
        
        return cleanup_results
    
    async def _cleanup_temporary_files(self) -> Dict[str, Any]:
        """Clean up temporary files and directories."""
        result = {
            "operation": "temporary_file_cleanup",
            "items_cleaned": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        try:
            # Define temporary directories to clean
            temp_dirs = [
                Path(".task_orchestrator/temp"),
                Path(".task_orchestrator/staging"),
                Path("/tmp/mcp_orchestrator")
            ]
            
            total_freed = 0
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    freed_space = await self._clean_directory(temp_dir, max_age_hours=24)
                    total_freed += freed_space
                    result["items_cleaned"] += 1
            
            result["space_freed_mb"] = total_freed / (1024 * 1024)  # Convert to MB
            
        except Exception as e:
            result["errors"].append(str(e))
            self.logger.warning(f"Error cleaning temporary files: {e}")
        
        return result
    
    async def _cleanup_orphaned_artifacts(self) -> Dict[str, Any]:
        """Clean up artifacts that no longer have associated tasks."""
        result = {
            "operation": "orphaned_artifact_cleanup",
            "items_cleaned": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        try:
            # Get all artifacts and check if their tasks still exist
            orphaned_artifacts = await self.artifact_manager.find_orphaned_artifacts()
            
            for artifact_id in orphaned_artifacts:
                try:
                    delete_result = await self.artifact_manager.delete_artifact(artifact_id)
                    if delete_result.get("success"):
                        result["items_cleaned"] += 1
                        result["space_freed_mb"] += delete_result.get("size_mb", 0)
                except Exception as e:
                    result["errors"].append(f"Failed to delete artifact {artifact_id}: {e}")
            
        except Exception as e:
            result["errors"].append(str(e))
            self.logger.warning(f"Error cleaning orphaned artifacts: {e}")
        
        return result
    
    async def _cleanup_incomplete_workflows(self, aggressive: bool = False) -> Dict[str, Any]:
        """Clean up incomplete or stalled workflows."""
        result = {
            "operation": "incomplete_workflow_cleanup",
            "items_cleaned": 0,
            "workflows_resolved": 0,
            "errors": []
        }
        
        try:
            incomplete_workflows = await self._identify_incomplete_workflows()
            
            for workflow_info in incomplete_workflows:
                if workflow_info.get("should_cleanup", False) or aggressive:
                    try:
                        resolution_result = await self._resolve_incomplete_workflow(
                            workflow_info, aggressive
                        )
                        
                        if resolution_result.get("success"):
                            result["workflows_resolved"] += 1
                            result["items_cleaned"] += resolution_result.get("tasks_processed", 0)
                        else:
                            result["errors"].append(
                                f"Failed to resolve workflow {workflow_info['parent_task_id']}: "
                                f"{resolution_result.get('error', 'Unknown error')}"
                            )
                            
                    except Exception as e:
                        result["errors"].append(
                            f"Error resolving workflow {workflow_info['parent_task_id']}: {e}"
                        )
            
        except Exception as e:
            result["errors"].append(str(e))
            self.logger.warning(f"Error cleaning incomplete workflows: {e}")
        
        return result
    
    async def _cleanup_stale_maintenance_operations(self) -> Dict[str, Any]:
        """Clean up stale maintenance operations."""
        result = {
            "operation": "stale_maintenance_cleanup",
            "items_cleaned": 0,
            "errors": []
        }
        
        try:
            with self.state_manager.session_scope() as session:
                # Find old maintenance operations
                cutoff_time = datetime.utcnow() - timedelta(hours=72)  # 3 days old
                
                stale_operations = session.query(MaintenanceOperationModel).filter(
                    MaintenanceOperationModel.created_at < cutoff_time,
                    MaintenanceOperationModel.status.in_(['pending', 'running'])
                ).all()
                
                for operation in stale_operations:
                    try:
                        # Mark as failed and clean up
                        operation.status = 'failed'
                        operation.completed_at = datetime.utcnow()
                        operation.results = {"error": "Operation timed out during cleanup"}
                        
                        result["items_cleaned"] += 1
                        
                    except Exception as e:
                        result["errors"].append(
                            f"Failed to clean maintenance operation {operation.operation_id}: {e}"
                        )
                
                session.commit()
                
        except Exception as e:
            result["errors"].append(str(e))
            self.logger.warning(f"Error cleaning stale maintenance operations: {e}")
        
        return result
    
    async def _identify_incomplete_workflows(self) -> List[Dict[str, Any]]:
        """Identify workflows that are incomplete and may need cleanup."""
        incomplete_workflows = []
        
        try:
            with self.state_manager.session_scope() as session:
                # Get all parent tasks
                parent_tasks = session.query(TaskBreakdownModel).all()
                
                for parent_task in parent_tasks:
                    # Get all subtasks for this parent
                    subtasks = session.query(SubTaskModel).filter_by(
                        parent_task_id=parent_task.parent_task_id
                    ).all()
                    
                    if not subtasks:
                        continue
                    
                    # Analyze workflow completion
                    total_subtasks = len(subtasks)
                    completed_subtasks = sum(1 for t in subtasks if t.status == 'completed')
                    failed_subtasks = sum(1 for t in subtasks if t.status == 'failed')
                    active_subtasks = sum(1 for t in subtasks if t.status in ['active', 'pending'])
                    
                    completion_rate = completed_subtasks / total_subtasks
                    
                    # Calculate workflow age
                    oldest_task_age = max(
                        (datetime.utcnow() - t.created_at).total_seconds() / 3600
                        for t in subtasks
                    )
                    
                    # Determine if workflow should be cleaned up
                    should_cleanup = False
                    cleanup_reasons = []
                    
                    # Very old workflows with minimal progress
                    if oldest_task_age > 168 and completion_rate < 0.1:  # 1 week old, <10% complete
                        should_cleanup = True
                        cleanup_reasons.append("aged_with_minimal_progress")
                    
                    # Workflows with many failed tasks
                    if failed_subtasks > total_subtasks * 0.5:  # >50% failed
                        should_cleanup = True
                        cleanup_reasons.append("high_failure_rate")
                    
                    # Workflows with no active tasks and incomplete
                    if active_subtasks == 0 and completion_rate < 1.0 and oldest_task_age > 72:  # 3 days
                        should_cleanup = True
                        cleanup_reasons.append("stalled_workflow")
                    
                    if completion_rate < 1.0:  # Only include incomplete workflows
                        workflow_info = {
                            "parent_task_id": parent_task.parent_task_id,
                            "description": parent_task.description,
                            "total_subtasks": total_subtasks,
                            "completed_subtasks": completed_subtasks,
                            "failed_subtasks": failed_subtasks,
                            "active_subtasks": active_subtasks,
                            "completion_rate": completion_rate,
                            "oldest_task_age_hours": oldest_task_age,
                            "should_cleanup": should_cleanup,
                            "cleanup_reasons": cleanup_reasons,
                            "created_at": parent_task.created_at.isoformat()
                        }
                        incomplete_workflows.append(workflow_info)
            
            return incomplete_workflows
            
        except Exception as e:
            self.logger.error(f"Error identifying incomplete workflows: {str(e)}")
            return []
    
    async def _resolve_incomplete_workflow(self, workflow_info: Dict[str, Any], 
                                         aggressive: bool) -> Dict[str, Any]:
        """Resolve an incomplete workflow through archival or completion."""
        parent_task_id = workflow_info["parent_task_id"]
        
        try:
            with self.state_manager.session_scope() as session:
                # Get all subtasks in the workflow
                subtasks = session.query(SubTaskModel).filter_by(
                    parent_task_id=parent_task_id
                ).all()
                
                # Strategy depends on completion rate and cleanup reasons
                completion_rate = workflow_info["completion_rate"]
                cleanup_reasons = workflow_info["cleanup_reasons"]
                
                if completion_rate > 0.7 and aggressive:
                    # High completion rate - try to complete remaining tasks
                    result = await self._complete_remaining_workflow_tasks(subtasks, session)
                    action = "completed_workflow"
                else:
                    # Low completion rate or non-aggressive - archive the workflow
                    result = await self._archive_incomplete_workflow(subtasks, cleanup_reasons)
                    action = "archived_workflow"
                
                return {
                    "success": True,
                    "action": action,
                    "tasks_processed": len(subtasks),
                    "completion_rate": completion_rate,
                    "cleanup_reasons": cleanup_reasons
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "parent_task_id": parent_task_id
            }
    
    async def _complete_remaining_workflow_tasks(self, subtasks: List[SubTaskModel], 
                                               session) -> Dict[str, Any]:
        """Attempt to complete remaining tasks in a workflow."""
        completed_count = 0
        
        for task in subtasks:
            if task.status in ['pending', 'active']:
                try:
                    # Mark as completed with cleanup note
                    task.status = 'completed'
                    task.completed_at = datetime.utcnow()
                    task.results = "Auto-completed during workflow cleanup"
                    task.summary = "Task completed automatically to resolve incomplete workflow"
                    
                    completed_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to auto-complete task {task.task_id}: {e}")
        
        session.commit()
        
        return {
            "success": True,
            "completed_tasks": completed_count
        }
    
    async def _archive_incomplete_workflow(self, subtasks: List[SubTaskModel], 
                                         cleanup_reasons: List[str]) -> Dict[str, Any]:
        """Archive an incomplete workflow."""
        # This would use the archival module to archive all tasks
        # For now, just return a placeholder
        return {
            "success": True,
            "archived_tasks": len(subtasks),
            "cleanup_reasons": cleanup_reasons
        }
    
    async def _clean_directory(self, directory: Path, max_age_hours: int = 24) -> int:
        """Clean files in a directory older than max_age_hours."""
        total_size = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        total_size += file_size
                        
        except Exception as e:
            self.logger.warning(f"Error cleaning directory {directory}: {e}")
        
        return total_size