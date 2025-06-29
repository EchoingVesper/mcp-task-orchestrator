"""
Stale task detection logic for the task lifecycle manager.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from ...db.models import TaskBreakdownModel, SubTaskModel
from .base import TaskLifecycleState, StaleTaskReason, LifecycleConfig, logger


class StaleTaskDetector:
    """Handles detection of stale tasks based on various criteria."""
    
    def __init__(self, state_manager):
        """Initialize the stale task detector.
        
        Args:
            state_manager: Database persistence manager
        """
        self.state_manager = state_manager
        self.logger = logger
        self.stale_detection_config = LifecycleConfig.STALE_DETECTION_CONFIG
    
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
        """Check if a task is part of an abandoned workflow."""
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
        """Check if a task has failed dependencies that make it stale."""
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
        """Determine the recommended action based on stale reasons."""
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
        """Determine if a task is eligible for automatic cleanup."""
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