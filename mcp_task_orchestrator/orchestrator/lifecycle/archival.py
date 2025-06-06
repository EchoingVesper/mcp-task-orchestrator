"""
Task Archival Operations Module

This module handles the archival of completed and stale tasks, including 
artifact preservation, retention management, and cleanup operations.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from ...db.persistence import DatabasePersistenceManager
from ...db.models import SubTaskModel, TaskArchiveModel, TaskLifecycleModel
from ..artifacts import ArtifactManager
from .base import TaskLifecycleState, LifecycleConfig

logger = logging.getLogger("mcp_task_orchestrator.lifecycle.archival")


class TaskArchivalManager:
    """Handles archival operations for tasks and their artifacts."""
    
    def __init__(self, state_manager: DatabasePersistenceManager, 
                 artifact_manager: ArtifactManager, config: LifecycleConfig):
        self.state_manager = state_manager
        self.artifact_manager = artifact_manager
        self.config = config
        self.logger = logger
        
        # Archive retention configuration (days)
        self.archive_retention_config = {
            "stale_timeout": 30,        # Stale tasks kept for 30 days
            "completed_normal": 90,     # Normal completed tasks for 90 days
            "completed_critical": 180,  # Critical tasks for 180 days
            "orphaned": 7,              # Orphaned tasks for 7 days
            "abandoned": 14,            # Abandoned workflows for 14 days
            "user_requested": 365       # User requested archives for 1 year
        }
    
    async def archive_task(self, task_id: str, archive_reason: str = "stale_timeout",
                          preserve_artifacts: bool = True, 
                          task_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Archive a single task with its artifacts.
        
        Args:
            task_id: ID of task to archive
            archive_reason: Reason for archival
            preserve_artifacts: Whether to preserve task artifacts
            task_info: Optional additional task information
            
        Returns:
            Archive operation result
        """
        try:
            with self.state_manager.session_scope() as session:
                # Get the task
                task = session.query(SubTaskModel).filter_by(task_id=task_id).first()
                
                if not task:
                    return {
                        "status": "failed",
                        "task_id": task_id,
                        "error": "Task not found"
                    }
                
                # Preserve artifacts if requested
                artifacts_preserved = False
                artifact_references = []
                
                if preserve_artifacts:
                    archive_artifact = await self._create_archive_artifact(task, archive_reason)
                    if archive_artifact:
                        artifacts_preserved = True
                        artifact_references.append(archive_artifact["artifact_id"])
                
                # Create comprehensive archive data
                archive_data = {
                    "task_details": {
                        "task_id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "specialist_type": task.specialist_type,
                        "status": task.status,
                        "parent_task_id": task.parent_task_id,
                        "dependencies": task.dependencies,
                        "results": task.results,
                        "summary": task.summary
                    },
                    "timeline": {
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "archived_at": datetime.utcnow().isoformat()
                    },
                    "archive_metadata": {
                        "reason": archive_reason,
                        "stale_reasons": task_info.get("stale_reasons", []) if task_info else [],
                        "recommended_action": task_info.get("recommended_action", "unknown") if task_info else "unknown"
                    }
                }
                
                # Determine retention period based on archive reason
                retention_days = self.archive_retention_config.get(archive_reason, 30)
                expires_at = datetime.utcnow() + timedelta(days=retention_days)
                
                # Create archive record
                archive_record = TaskArchiveModel(
                    original_task_id=task.task_id,
                    parent_task_id=task.parent_task_id,
                    archive_reason=archive_reason,
                    archived_data=archive_data,
                    artifacts_preserved=artifacts_preserved,
                    artifact_references=artifact_references,
                    expires_at=expires_at
                )
                
                session.add(archive_record)
                
                # Record lifecycle transition
                lifecycle_record = TaskLifecycleModel(
                    task_id=task.task_id,
                    lifecycle_stage=TaskLifecycleState.ARCHIVED.value,
                    previous_stage=task.status,
                    transition_reason=f"Archived: {archive_reason}",
                    automated_transition=True,
                    transition_metadata={
                        "archive_reason": archive_reason,
                        "retention_days": retention_days,
                        "artifacts_preserved": artifacts_preserved
                    }
                )
                
                session.add(lifecycle_record)
                
                # Remove the task from active tasks
                session.delete(task)
                
                session.commit()
                
                self.logger.info(f"Successfully archived task {task_id}")
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "archive_reason": archive_reason,
                    "artifacts_preserved": artifacts_preserved,
                    "retention_days": retention_days,
                    "expires_at": expires_at.isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error archiving task {task_id}: {str(e)}")
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _create_archive_artifact(self, task: SubTaskModel, archive_reason: str) -> Optional[Dict[str, Any]]:
        """Create an archive artifact preserving task details."""
        try:
            archive_content = f"""# Archived Task: {task.title}

## Task Information
- **Task ID**: {task.task_id}
- **Specialist Type**: {task.specialist_type}
- **Status**: {task.status}
- **Parent Task ID**: {task.parent_task_id}

## Archive Details
- **Archive Reason**: {archive_reason}
- **Archived At**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Original Created**: {task.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if task.created_at else 'Unknown'}

## Task Description
{task.description}

## Dependencies
{json.dumps(task.dependencies, indent=2) if task.dependencies else 'None'}

## Results
{task.results if task.results else 'No results recorded'}

## Summary
{task.summary if task.summary else 'No summary available'}

---
*This task was automatically archived by the Task Lifecycle Manager*
"""
            
            # Create artifact through artifact manager
            artifact_result = await self.artifact_manager.create_artifact(
                task_id=task.task_id,
                artifact_type="archive_record",
                content=archive_content,
                metadata={
                    "archive_reason": archive_reason,
                    "original_specialist": task.specialist_type,
                    "archive_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            if artifact_result and artifact_result.get("success"):
                return {
                    "artifact_id": artifact_result["artifact_id"],
                    "file_path": artifact_result.get("file_path"),
                    "content_length": len(archive_content)
                }
            
        except Exception as e:
            self.logger.warning(f"Failed to create archive artifact for task {task.task_id}: {e}")
        
        return None
    
    async def bulk_archive_tasks(self, task_ids: List[str], archive_reason: str = "bulk_cleanup",
                                preserve_artifacts: bool = False) -> Dict[str, Any]:
        """Archive multiple tasks in a batch operation."""
        results = {
            "total_tasks": len(task_ids),
            "successful_archives": 0,
            "failed_archives": 0,
            "errors": [],
            "archived_task_ids": []
        }
        
        for task_id in task_ids:
            try:
                archive_result = await self.archive_task(
                    task_id, archive_reason, preserve_artifacts
                )
                
                if archive_result["status"] == "success":
                    results["successful_archives"] += 1
                    results["archived_task_ids"].append(task_id)
                else:
                    results["failed_archives"] += 1
                    results["errors"].append({
                        "task_id": task_id,
                        "error": archive_result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["failed_archives"] += 1
                results["errors"].append({
                    "task_id": task_id,
                    "error": str(e)
                })
        
        self.logger.info(
            f"Bulk archive completed: {results['successful_archives']} successful, "
            f"{results['failed_archives']} failed"
        )
        
        return results
    
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up archives that have exceeded their retention period."""
        results = {
            "expired_archives_found": 0,
            "archives_cleaned": 0,
            "cleanup_errors": 0,
            "freed_space_mb": 0
        }
        
        try:
            with self.state_manager.session_scope() as session:
                # Find expired archives
                current_time = datetime.utcnow()
                expired_archives = session.query(TaskArchiveModel).filter(
                    TaskArchiveModel.expires_at < current_time
                ).all()
                
                results["expired_archives_found"] = len(expired_archives)
                
                for archive in expired_archives:
                    try:
                        # Clean up associated artifacts if any
                        if archive.artifact_references:
                            for artifact_id in archive.artifact_references:
                                await self.artifact_manager.delete_artifact(artifact_id)
                        
                        # Delete the archive record
                        session.delete(archive)
                        results["archives_cleaned"] += 1
                        
                    except Exception as e:
                        results["cleanup_errors"] += 1
                        self.logger.warning(f"Error cleaning archive {archive.archive_id}: {e}")
                
                session.commit()
                
        except Exception as e:
            self.logger.error(f"Error during archive cleanup: {e}")
            results["cleanup_errors"] += 1
        
        return results