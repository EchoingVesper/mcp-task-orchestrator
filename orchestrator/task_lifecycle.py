"""
Task Lifecycle Management for the MCP Task Orchestrator.

This module provides advanced task lifecycle management including intelligent stale task
detection, comprehensive archival operations, and workspace cleanup mechanisms.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from pathlib import Path
from enum import Enum

from ..db.persistence import DatabasePersistenceManager
from ..db.models import (
    TaskBreakdownModel, SubTaskModel, MaintenanceOperationModel,
    TaskArchiveModel, StaleTaskTrackingModel, TaskLifecycleModel
)
from .models import TaskStatus, SpecialistType
from .artifacts import ArtifactManager

logger = logging.getLogger("mcp_task_orchestrator.lifecycle")


class TaskLifecycleState(Enum):
    """Enumeration of task lifecycle states."""
    CREATED = "created"
    ACTIVE = "active"
    COMPLETED = "completed"
    STALE = "stale"
    ARCHIVED = "archived"
    FAILED = "failed"


class StaleTaskReason(Enum):
    """Enumeration of reasons why a task might be considered stale."""
    INACTIVITY_TIMEOUT = "inactivity_timeout"
    ABANDONED_WORKFLOW = "abandoned_workflow"
    ORPHANED_TASK = "orphaned_task"
    DEPENDENCY_FAILURE = "dependency_failure"
    SPECIALIST_UNAVAILABLE = "specialist_unavailable"
    USER_ABANDONED = "user_abandoned"


class TaskLifecycleManager:
    """Manages task lifecycle transitions and cleanup operations."""
    
    def __init__(self, state_manager: DatabasePersistenceManager, artifact_manager: ArtifactManager):
        """Initialize the task lifecycle manager.
        
        Args:
            state_manager: Database persistence manager
            artifact_manager: Artifact manager for preserving task outputs
        """
        self.state_manager = state_manager
        self.artifact_manager = artifact_manager
        self.logger = logger
        
        # Configuration for stale task detection
        self.stale_detection_config = {
            "default_threshold_hours": 24,
            "specialist_thresholds": {
                "researcher": 12,  # Research tasks should complete faster
                "documenter": 8,   # Documentation tasks are usually quicker
                "reviewer": 6,     # Review tasks should be timely
                "tester": 16,      # Testing might take longer
                "implementer": 48, # Implementation can be complex
                "architect": 72,   # Architecture decisions need time
                "debugger": 24     # Debugging varies but should have progress
            },
            "workflow_abandonment_threshold_hours": 168,  # 1 week for entire workflows
            "minimum_progress_threshold": 0.1  # 10% progress expected within threshold
        }
        
        # Archive retention policies
        self.archive_retention_config = {
            "completed_tasks": 90,      # 90 days for completed tasks
            "stale_tasks": 30,          # 30 days for stale tasks  
            "failed_tasks": 60,         # 60 days for failed tasks
            "orphaned_tasks": 7,        # 7 days for orphaned tasks
            "user_abandoned": 14        # 14 days for user-abandoned tasks
        }
        
        self.logger.info("Initialized TaskLifecycleManager")
    
    async def detect_stale_tasks(self, comprehensive_scan: bool = False) -> List[Dict[str, Any]]:
        """Detect tasks that may be stale based on various criteria.
        
        Args:
            comprehensive_scan: Whether to perform a comprehensive scan with advanced heuristics
            
        Returns:
            List of stale task information with reasons and recommended actions
        """
        self.logger.info(f"Starting stale task detection (comprehensive={comprehensive_scan})")
        
        stale_tasks = []
        
        try:
            with self.state_manager.session_scope() as session:
                # Get all active and pending tasks
                active_tasks = session.query(SubTaskModel).filter(
                    SubTaskModel.status.in_(['active', 'pending'])
                ).all()
                
                current_time = datetime.utcnow()
                
                for task in active_tasks:
                    stale_reasons = []
                    task_age_hours = (current_time - task.created_at).total_seconds() / 3600
                    
                    # Check inactivity timeout based on specialist type
                    specialist_threshold = self.stale_detection_config["specialist_thresholds"].get(
                        task.specialist_type, 
                        self.stale_detection_config["default_threshold_hours"]
                    )
                    
                    if task_age_hours > specialist_threshold:
                        stale_reasons.append({
                            "reason": StaleTaskReason.INACTIVITY_TIMEOUT.value,
                            "details": f"Task exceeded {specialist_threshold}h threshold for {task.specialist_type}",
                            "severity": "high" if task_age_hours > specialist_threshold * 2 else "medium"
                        })
                    
                    # Check for orphaned tasks (missing parent)
                    parent_exists = session.query(TaskBreakdownModel).filter_by(
                        parent_task_id=task.parent_task_id
                    ).first()
                    
                    if not parent_exists:
                        stale_reasons.append({
                            "reason": StaleTaskReason.ORPHANED_TASK.value,
                            "details": f"Parent task {task.parent_task_id} no longer exists",
                            "severity": "critical"
                        })
                    
                    # Comprehensive scan additional checks
                    if comprehensive_scan:
                        # Check for workflow abandonment
                        workflow_stale_reasons = await self._check_workflow_abandonment(session, task)
                        stale_reasons.extend(workflow_stale_reasons)
                        
                        # Check for dependency failures
                        dependency_stale_reasons = await self._check_dependency_failures(session, task)
                        stale_reasons.extend(dependency_stale_reasons)
                    
                    # If any stale reasons found, add to results
                    if stale_reasons:
                        stale_task_info = {
                            "task_id": task.task_id,
                            "title": task.title,
                            "specialist_type": task.specialist_type,
                            "status": task.status,
                            "parent_task_id": task.parent_task_id,
                            "created_at": task.created_at.isoformat(),
                            "age_hours": task_age_hours,
                            "stale_reasons": stale_reasons,
                            "max_severity": max(r["severity"] for r in stale_reasons),
                            "recommended_action": self._determine_recommended_action(stale_reasons),
                            "auto_cleanup_eligible": self._is_auto_cleanup_eligible(stale_reasons)
                        }
                        stale_tasks.append(stale_task_info)
                
                self.logger.info(f"Detected {len(stale_tasks)} stale tasks")
                return stale_tasks
                
        except Exception as e:
            self.logger.error(f"Error detecting stale tasks: {str(e)}")
            raise
    
    async def _check_workflow_abandonment(self, session, task: SubTaskModel) -> List[Dict[str, Any]]:
        """Check if a task is part of an abandoned workflow.
        
        Args:
            session: Database session
            task: Task to check
            
        Returns:
            List of stale reasons related to workflow abandonment
        """
        reasons = []
        
        try:
            # Get all tasks in the same workflow
            workflow_tasks = session.query(SubTaskModel).filter_by(
                parent_task_id=task.parent_task_id
            ).all()
            
            if not workflow_tasks:
                return reasons
            
            # Calculate workflow metrics
            total_tasks = len(workflow_tasks)
            completed_tasks = sum(1 for t in workflow_tasks if t.status == 'completed')
            active_tasks = sum(1 for t in workflow_tasks if t.status in ['active', 'pending'])
            
            workflow_age_hours = max(
                (datetime.utcnow() - t.created_at).total_seconds() / 3600 
                for t in workflow_tasks
            )
            
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            # Check for workflow abandonment indicators
            if (workflow_age_hours > self.stale_detection_config["workflow_abandonment_threshold_hours"] 
                and completion_rate < self.stale_detection_config["minimum_progress_threshold"]):
                
                reasons.append({
                    "reason": StaleTaskReason.ABANDONED_WORKFLOW.value,
                    "details": f"Workflow {task.parent_task_id} has {completion_rate:.1%} completion after {workflow_age_hours:.1f}h",
                    "severity": "high"
                })
            
            # Check for stalled workflows (some progress but no recent activity)
            if completion_rate > 0.1 and active_tasks > 0:
                latest_activity = max(
                    t.completed_at or t.created_at for t in workflow_tasks 
                    if t.completed_at or t.created_at
                )
                hours_since_activity = (datetime.utcnow() - latest_activity).total_seconds() / 3600
                
                if hours_since_activity > self.stale_detection_config["default_threshold_hours"] * 2:
                    reasons.append({
                        "reason": StaleTaskReason.ABANDONED_WORKFLOW.value,
                        "details": f"No workflow activity for {hours_since_activity:.1f}h despite {completion_rate:.1%} completion",
                        "severity": "medium"
                    })
            
            return reasons
            
        except Exception as e:
            self.logger.error(f"Error checking workflow abandonment for task {task.task_id}: {str(e)}")
            return []
    
    async def _check_dependency_failures(self, session, task: SubTaskModel) -> List[Dict[str, Any]]:
        """Check if a task has failed dependencies that make it stale.
        
        Args:
            session: Database session
            task: Task to check
            
        Returns:
            List of stale reasons related to dependency failures
        """
        reasons = []
        
        try:
            if not task.dependencies:
                return reasons
            
            # Check each dependency
            for dep_id in task.dependencies:
                dep_task = session.query(SubTaskModel).filter_by(task_id=dep_id).first()
                
                if not dep_task:
                    reasons.append({
                        "reason": StaleTaskReason.DEPENDENCY_FAILURE.value,
                        "details": f"Dependency task {dep_id} no longer exists",
                        "severity": "high"
                    })
                elif dep_task.status == 'failed':
                    reasons.append({
                        "reason": StaleTaskReason.DEPENDENCY_FAILURE.value,
                        "details": f"Dependency task {dep_id} has failed",
                        "severity": "critical"
                    })
                elif dep_task.status in ['active', 'pending']:
                    dep_age_hours = (datetime.utcnow() - dep_task.created_at).total_seconds() / 3600
                    dep_threshold = self.stale_detection_config["specialist_thresholds"].get(
                        dep_task.specialist_type,
                        self.stale_detection_config["default_threshold_hours"]
                    )
                    
                    if dep_age_hours > dep_threshold * 1.5:  # Dependencies get extra time
                        reasons.append({
                            "reason": StaleTaskReason.DEPENDENCY_FAILURE.value,
                            "details": f"Dependency task {dep_id} appears stale ({dep_age_hours:.1f}h old)",
                            "severity": "medium"
                        })
            
            return reasons
            
        except Exception as e:
            self.logger.error(f"Error checking dependency failures for task {task.task_id}: {str(e)}")
            return []
    
    def _determine_recommended_action(self, stale_reasons: List[Dict[str, Any]]) -> str:
        """Determine the recommended action based on stale reasons.
        
        Args:
            stale_reasons: List of reasons why the task is stale
            
        Returns:
            Recommended action string
        """
        severities = [r["severity"] for r in stale_reasons]
        reason_types = [r["reason"] for r in stale_reasons]
        
        # Critical issues require immediate action
        if "critical" in severities:
            if StaleTaskReason.ORPHANED_TASK.value in reason_types:
                return "remove_orphaned_task"
            elif StaleTaskReason.DEPENDENCY_FAILURE.value in reason_types:
                return "resolve_dependencies_or_archive"
            else:
                return "immediate_review_required"
        
        # High severity issues
        elif "high" in severities:
            if StaleTaskReason.ABANDONED_WORKFLOW.value in reason_types:
                return "archive_workflow"
            elif StaleTaskReason.INACTIVITY_TIMEOUT.value in reason_types:
                return "archive_stale_task"
            else:
                return "manual_review_recommended"
        
        # Medium severity issues
        else:
            return "monitor_and_notify"
    
    def _is_auto_cleanup_eligible(self, stale_reasons: List[Dict[str, Any]]) -> bool:
        """Determine if a task is eligible for automatic cleanup.
        
        Args:
            stale_reasons: List of reasons why the task is stale
            
        Returns:
            True if the task can be automatically cleaned up
        """
        reason_types = [r["reason"] for r in stale_reasons]
        severities = [r["severity"] for r in stale_reasons]
        
        # Only auto-cleanup for specific scenarios
        auto_cleanup_reasons = {
            StaleTaskReason.ORPHANED_TASK.value,
            StaleTaskReason.INACTIVITY_TIMEOUT.value
        }
        
        # Don't auto-cleanup critical dependency failures - need manual review
        if StaleTaskReason.DEPENDENCY_FAILURE.value in reason_types and "critical" in severities:
            return False
        
        # Auto-cleanup if any eligible reason exists
        return any(reason in auto_cleanup_reasons for reason in reason_types)
    
    async def archive_task(self, task_info: Dict[str, Any], archive_reason: str) -> Dict[str, Any]:
        """Archive a task with comprehensive data preservation.
        
        Args:
            task_info: Information about the task to archive
            archive_reason: Reason for archival
            
        Returns:
            Archive operation result
        """
        task_id = task_info["task_id"]
        self.logger.info(f"Archiving task {task_id} with reason: {archive_reason}")
        
        try:
            with self.state_manager.session_scope() as session:
                # Get the full task information
                task = session.query(SubTaskModel).filter_by(task_id=task_id).first()
                
                if not task:
                    return {"status": "failed", "error": "Task not found"}
                
                # Preserve artifacts if they exist
                artifacts_preserved = False
                artifact_references = []
                
                if task.artifacts:
                    try:
                        # Create archive artifact for the task
                        archive_artifact = await self._create_archive_artifact(task, archive_reason)
                        artifacts_preserved = True
                        artifact_references = task.artifacts + [archive_artifact["accessible_via"]]
                    except Exception as e:
                        self.logger.warning(f"Failed to preserve artifacts for task {task_id}: {str(e)}")
                        artifact_references = task.artifacts or []
                
                # Create comprehensive archive data
                archive_data = {
                    "task_metadata": {
                        "task_id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "specialist_type": task.specialist_type,
                        "status": task.status,
                        "dependencies": task.dependencies,
                        "estimated_effort": task.estimated_effort
                    },
                    "execution_data": {
                        "results": task.results,
                        "artifacts": task.artifacts,
                        "file_operations_count": task.file_operations_count,
                        "verification_status": task.verification_status
                    },
                    "timeline": {
                        "created_at": task.created_at.isoformat() if task.created_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "archived_at": datetime.utcnow().isoformat()
                    },
                    "archive_metadata": {
                        "reason": archive_reason,
                        "stale_reasons": task_info.get("stale_reasons", []),
                        "recommended_action": task_info.get("recommended_action", "unknown")
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
    
    async def _create_archive_artifact(self, task: SubTaskModel, archive_reason: str) -> Dict[str, Any]:
        """Create an archive artifact preserving task details.
        
        Args:
            task: Task being archived
            archive_reason: Reason for archival
            
        Returns:
            Archive artifact information
        """
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

## Original Artifacts
{json.dumps(task.artifacts, indent=2) if task.artifacts else 'No artifacts'}

## File Operations
- **Operations Count**: {task.file_operations_count}
- **Verification Status**: {task.verification_status}

---
*This archive was created automatically by the MCP Task Orchestrator maintenance system.*
"""
        
        return self.artifact_manager.store_artifact(
            task_id=f"archive_{task.task_id}",
            summary=f"Archive of {task.specialist_type} task: {task.title[:50]}...",
            detailed_work=archive_content,
            artifact_type="archive"
        )
    
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up expired archive records based on retention policies.
        
        Returns:
            Cleanup operation results
        """
        self.logger.info("Starting cleanup of expired archives")
        
        try:
            with self.state_manager.session_scope() as session:
                current_time = datetime.utcnow()
                
                # Find expired archives
                expired_archives = session.query(TaskArchiveModel).filter(
                    TaskArchiveModel.expires_at <= current_time
                ).all()
                
                if not expired_archives:
                    return {
                        "status": "completed",
                        "archives_cleaned": 0,
                        "message": "No expired archives found"
                    }
                
                cleanup_results = []
                
                for archive in expired_archives:
                    try:
                        # Optionally preserve critical archives beyond expiration
                        if self._should_preserve_archive(archive):
                            # Extend retention for critical archives
                            archive.expires_at = current_time + timedelta(days=30)
                            cleanup_results.append({
                                "archive_id": archive.id,
                                "original_task_id": archive.original_task_id,
                                "action": "retention_extended",
                                "reason": "Critical archive preserved"
                            })
                        else:
                            # Delete the expired archive
                            session.delete(archive)
                            cleanup_results.append({
                                "archive_id": archive.id,
                                "original_task_id": archive.original_task_id,
                                "action": "deleted",
                                "reason": "Expired archive removed"
                            })
                    
                    except Exception as e:
                        self.logger.error(f"Error processing archive {archive.id}: {str(e)}")
                        cleanup_results.append({
                            "archive_id": archive.id,
                            "original_task_id": archive.original_task_id,
                            "action": "failed",
                            "error": str(e)
                        })
                
                session.commit()
                
                deleted_count = sum(1 for r in cleanup_results if r["action"] == "deleted")
                extended_count = sum(1 for r in cleanup_results if r["action"] == "retention_extended")
                
                self.logger.info(f"Archive cleanup completed: {deleted_count} deleted, {extended_count} extended")
                
                return {
                    "status": "completed",
                    "archives_cleaned": deleted_count,
                    "archives_extended": extended_count,
                    "cleanup_details": cleanup_results
                }
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired archives: {str(e)}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _should_preserve_archive(self, archive: TaskArchiveModel) -> bool:
        """Determine if an archive should be preserved beyond its expiration.
        
        Args:
            archive: Archive record to evaluate
            
        Returns:
            True if the archive should be preserved
        """
        # Preserve archives with significant artifacts
        if archive.artifacts_preserved and len(archive.artifact_references) > 2:
            return True
        
        # Preserve archives of completed tasks that took significant effort
        if archive.archive_reason == "completed":
            archived_data = archive.archived_data or {}
            execution_data = archived_data.get("execution_data", {})
            
            if execution_data.get("file_operations_count", 0) > 10:
                return True
        
        # Preserve archives with critical failure information
        if archive.archive_reason in ["dependency_failure", "critical_error"]:
            return True
        
        return False

    
    async def perform_workspace_cleanup(self, aggressive: bool = False) -> Dict[str, Any]:
        """Perform comprehensive workspace cleanup operations.
        
        Args:
            aggressive: Whether to perform aggressive cleanup including borderline cases
            
        Returns:
            Workspace cleanup results
        """
        self.logger.info(f"Starting workspace cleanup (aggressive={aggressive})")
        
        cleanup_results = {
            "stale_tasks_processed": 0,
            "orphaned_tasks_removed": 0,
            "incomplete_workflows_resolved": 0,
            "archives_cleaned": 0,
            "performance_improvements": [],
            "errors": []
        }
        
        try:
            # 1. Detect and process stale tasks
            stale_tasks = await self.detect_stale_tasks(comprehensive_scan=True)
            
            for stale_task in stale_tasks:
                try:
                    if stale_task["auto_cleanup_eligible"] or aggressive:
                        action = stale_task["recommended_action"]
                        
                        if action in ["archive_stale_task", "archive_workflow"]:
                            archive_result = await self.archive_task(stale_task, "stale")
                            if archive_result["status"] == "success":
                                cleanup_results["stale_tasks_processed"] += 1
                        
                        elif action == "remove_orphaned_task":
                            removal_result = await self._remove_orphaned_task_completely(stale_task)
                            if removal_result["status"] == "success":
                                cleanup_results["orphaned_tasks_removed"] += 1
                        
                        elif action == "resolve_dependencies_or_archive" and aggressive:
                            # In aggressive mode, archive tasks with failed dependencies
                            archive_result = await self.archive_task(stale_task, "dependency_failure")
                            if archive_result["status"] == "success":
                                cleanup_results["stale_tasks_processed"] += 1
                
                except Exception as e:
                    self.logger.error(f"Error processing stale task {stale_task['task_id']}: {str(e)}")
                    cleanup_results["errors"].append({
                        "task_id": stale_task["task_id"],
                        "operation": "stale_task_processing",
                        "error": str(e)
                    })
            
            # 2. Resolve incomplete workflows
            incomplete_workflows = await self._identify_incomplete_workflows()
            
            for workflow in incomplete_workflows:
                try:
                    if workflow["should_cleanup"] or aggressive:
                        workflow_result = await self._resolve_incomplete_workflow(workflow, aggressive)
                        if workflow_result["status"] == "success":
                            cleanup_results["incomplete_workflows_resolved"] += 1
                
                except Exception as e:
                    self.logger.error(f"Error resolving workflow {workflow['parent_task_id']}: {str(e)}")
                    cleanup_results["errors"].append({
                        "parent_task_id": workflow["parent_task_id"],
                        "operation": "workflow_resolution",
                        "error": str(e)
                    })
            
            # 3. Clean up expired archives
            archive_cleanup = await self.cleanup_expired_archives()
            cleanup_results["archives_cleaned"] = archive_cleanup.get("archives_cleaned", 0)
            
            # 4. Perform database optimizations
            if aggressive:
                performance_improvements = await self._optimize_database_performance()
                cleanup_results["performance_improvements"] = performance_improvements
            
            # 5. Update stale task tracking
            await self._update_stale_task_tracking(stale_tasks)
            
            cleanup_results["status"] = "completed"
            cleanup_results["total_actions"] = (
                cleanup_results["stale_tasks_processed"] +
                cleanup_results["orphaned_tasks_removed"] + 
                cleanup_results["incomplete_workflows_resolved"] +
                cleanup_results["archives_cleaned"]
            )
            
            self.logger.info(f"Workspace cleanup completed: {cleanup_results['total_actions']} total actions")
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"Error during workspace cleanup: {str(e)}")
            cleanup_results["status"] = "failed"
            cleanup_results["error"] = str(e)
            return cleanup_results
    
    async def _remove_orphaned_task_completely(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        """Completely remove an orphaned task with proper cleanup.
        
        Args:
            task_info: Information about the orphaned task
            
        Returns:
            Removal operation result
        """
        task_id = task_info["task_id"]
        
        try:
            with self.state_manager.session_scope() as session:
                # Get the task
                task = session.query(SubTaskModel).filter_by(task_id=task_id).first()
                
                if not task:
                    return {"status": "failed", "error": "Task not found"}
                
                # Create minimal archive record for audit trail
                archive_data = {
                    "task_id": task.task_id,
                    "title": task.title,
                    "specialist_type": task.specialist_type,
                    "removal_reason": "orphaned_task_cleanup",
                    "removed_at": datetime.utcnow().isoformat()
                }
                
                archive_record = TaskArchiveModel(
                    original_task_id=task.task_id,
                    parent_task_id=task.parent_task_id,
                    archive_reason="orphaned",
                    archived_data=archive_data,
                    artifacts_preserved=False,
                    expires_at=datetime.utcnow() + timedelta(days=7)  # Short retention for orphaned tasks
                )
                
                session.add(archive_record)
                
                # Record lifecycle transition
                lifecycle_record = TaskLifecycleModel(
                    task_id=task.task_id,
                    lifecycle_stage=TaskLifecycleState.ARCHIVED.value,
                    previous_stage=task.status,
                    transition_reason="Removed: orphaned task cleanup",
                    automated_transition=True
                )
                
                session.add(lifecycle_record)
                
                # Remove the task
                session.delete(task)
                
                session.commit()
                
                self.logger.info(f"Completely removed orphaned task {task_id}")
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "action": "removed_orphaned_task"
                }
                
        except Exception as e:
            self.logger.error(f"Error removing orphaned task {task_id}: {str(e)}")
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e)
            }
    
    async def _identify_incomplete_workflows(self) -> List[Dict[str, Any]]:
        """Identify workflows that are incomplete and may need resolution.
        
        Returns:
            List of incomplete workflow information
        """
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
    
    async def _resolve_incomplete_workflow(self, workflow_info: Dict[str, Any], aggressive: bool) -> Dict[str, Any]:
        """Resolve an incomplete workflow through archival or completion.
        
        Args:
            workflow_info: Information about the incomplete workflow
            aggressive: Whether to use aggressive cleanup
            
        Returns:
            Resolution operation result
        """
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
                
                elif "high_failure_rate" in cleanup_reasons:
                    # Too many failures - archive the entire workflow
                    result = await self._archive_entire_workflow(parent_task_id, subtasks, "high_failure_rate")
                    action = "archived_failed_workflow"
                
                elif "stalled_workflow" in cleanup_reasons:
                    # Stalled workflow - archive with stalled reason
                    result = await self._archive_entire_workflow(parent_task_id, subtasks, "stalled")
                    action = "archived_stalled_workflow"
                
                else:
                    # Default: partial cleanup of obviously failed tasks
                    result = await self._partial_workflow_cleanup(subtasks, session)
                    action = "partial_cleanup"
                
                return {
                    "status": "success",
                    "parent_task_id": parent_task_id,
                    "action": action,
                    "details": result
                }
                
        except Exception as e:
            self.logger.error(f"Error resolving incomplete workflow {parent_task_id}: {str(e)}")
            return {
                "status": "failed",
                "parent_task_id": parent_task_id,
                "error": str(e)
            }
    
    async def _archive_entire_workflow(self, parent_task_id: str, subtasks: List[SubTaskModel], reason: str) -> Dict[str, Any]:
        """Archive an entire workflow and all its subtasks.
        
        Args:
            parent_task_id: Parent task ID
            subtasks: List of all subtasks in the workflow
            reason: Reason for archival
            
        Returns:
            Archive operation result
        """
        archived_tasks = []
        
        with self.state_manager.session_scope() as session:
            # Archive each subtask
            for subtask in subtasks:
                task_info = {
                    "task_id": subtask.task_id,
                    "title": subtask.title,
                    "specialist_type": subtask.specialist_type,
                    "status": subtask.status
                }
                
                archive_result = await self.archive_task(task_info, reason)
                archived_tasks.append({
                    "task_id": subtask.task_id,
                    "status": archive_result["status"]
                })
            
            # Archive the parent task
            parent_task = session.query(TaskBreakdownModel).filter_by(
                parent_task_id=parent_task_id
            ).first()
            
            if parent_task:
                # Create workflow archive record
                workflow_archive_data = {
                    "parent_task_id": parent_task_id,
                    "description": parent_task.description,
                    "complexity": parent_task.complexity,
                    "subtasks_archived": len(archived_tasks),
                    "archive_reason": reason,
                    "archived_at": datetime.utcnow().isoformat()
                }
                
                workflow_archive = TaskArchiveModel(
                    original_task_id=f"workflow_{parent_task_id}",
                    parent_task_id=parent_task_id,
                    archive_reason=f"workflow_{reason}",
                    archived_data=workflow_archive_data,
                    artifacts_preserved=False,
                    expires_at=datetime.utcnow() + timedelta(days=self.archive_retention_config.get(reason, 30))
                )
                
                session.add(workflow_archive)
                session.delete(parent_task)
                session.commit()
        
        return {
            "archived_subtasks": len(archived_tasks),
            "workflow_archived": True,
            "reason": reason
        }
    
    async def _optimize_database_performance(self) -> List[Dict[str, Any]]:
        """Perform database optimizations for better performance.
        
        Returns:
            List of optimization actions performed
        """
        optimizations = []
        
        try:
            with self.state_manager.session_scope() as session:
                # Analyze and optimize database indexes
                session.execute("ANALYZE")
                optimizations.append({
                    "action": "database_analyze",
                    "status": "completed",
                    "description": "Updated database statistics for query optimization"
                })
                
                # Clean up any database fragmentation (SQLite specific)
                session.execute("VACUUM")
                optimizations.append({
                    "action": "database_vacuum",
                    "status": "completed", 
                    "description": "Reduced database file size and fragmentation"
                })
                
                session.commit()
                
        except Exception as e:
            self.logger.error(f"Error optimizing database performance: {str(e)}")
            optimizations.append({
                "action": "database_optimization",
                "status": "failed",
                "error": str(e)
            })
        
        return optimizations
    
    async def _update_stale_task_tracking(self, stale_tasks: List[Dict[str, Any]]) -> None:
        """Update the stale task tracking records.
        
        Args:
            stale_tasks: List of detected stale tasks
        """
        try:
            with self.state_manager.session_scope() as session:
                for stale_task in stale_tasks:
                    # Check if tracking record already exists
                    existing_record = session.query(StaleTaskTrackingModel).filter_by(
                        task_id=stale_task["task_id"]
                    ).first()
                    
                    if existing_record:
                        # Update existing record
                        existing_record.stale_indicators = [r["reason"] for r in stale_task["stale_reasons"]]
                        existing_record.auto_cleanup_eligible = stale_task["auto_cleanup_eligible"]
                        existing_record.detection_metadata = {
                            "last_detection": datetime.utcnow().isoformat(),
                            "max_severity": stale_task["max_severity"],
                            "recommended_action": stale_task["recommended_action"]
                        }
                    else:
                        # Create new tracking record
                        tracking_record = StaleTaskTrackingModel(
                            task_id=stale_task["task_id"],
                            last_activity_at=datetime.utcnow() - timedelta(hours=stale_task["age_hours"]),
                            stale_indicators=[r["reason"] for r in stale_task["stale_reasons"]],
                            auto_cleanup_eligible=stale_task["auto_cleanup_eligible"],
                            detection_metadata={
                                "first_detection": datetime.utcnow().isoformat(),
                                "max_severity": stale_task["max_severity"],
                                "recommended_action": stale_task["recommended_action"]
                            }
                        )
                        session.add(tracking_record)
                
                session.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating stale task tracking: {str(e)}")
    
    async def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about task lifecycle management.
        
        Returns:
            Dictionary containing lifecycle statistics
        """
        try:
            with self.state_manager.session_scope() as session:
                # Current task distribution
                current_stats = {}
                for status in ['active', 'pending', 'completed', 'failed']:
                    count = session.query(SubTaskModel).filter_by(status=status).count()
                    current_stats[status] = count
                
                # Archive statistics
                total_archives = session.query(TaskArchiveModel).count()
                archive_by_reason = {}
                
                archive_reasons = session.query(TaskArchiveModel.archive_reason).distinct().all()
                for (reason,) in archive_reasons:
                    count = session.query(TaskArchiveModel).filter_by(archive_reason=reason).count()
                    archive_by_reason[reason] = count
                
                # Lifecycle transition statistics
                recent_transitions = session.query(TaskLifecycleModel).filter(
                    TaskLifecycleModel.created_at >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                # Stale task tracking statistics
                stale_tasks_tracked = session.query(StaleTaskTrackingModel).count()
                auto_cleanup_eligible = session.query(StaleTaskTrackingModel).filter_by(
                    auto_cleanup_eligible=True
                ).count()
                
                return {
                    "current_tasks": current_stats,
                    "total_current_tasks": sum(current_stats.values()),
                    "archives": {
                        "total_archived": total_archives,
                        "by_reason": archive_by_reason
                    },
                    "lifecycle_transitions": {
                        "recent_transitions_7days": recent_transitions
                    },
                    "stale_task_tracking": {
                        "total_tracked": stale_tasks_tracked,
                        "auto_cleanup_eligible": auto_cleanup_eligible
                    },
                    "generated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting lifecycle statistics: {str(e)}")
            return {
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
