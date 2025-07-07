"""
Stale Task Detection Service

Handles detection and classification of stale tasks based on various criteria
including inactivity timeout, workflow abandonment, and dependency failures.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum

# NOTE: Infrastructure imports removed for Clean Architecture compliance
# Database connections should be injected through repository interfaces
# Error handling should be applied at the infrastructure/application layer

logger = logging.getLogger(__name__)


class StaleTaskReason(Enum):
    """Enumeration of reasons why a task might be considered stale."""
    INACTIVITY_TIMEOUT = "inactivity_timeout"
    ABANDONED_WORKFLOW = "abandoned_workflow"
    ORPHANED_TASK = "orphaned_task"
    DEPENDENCY_FAILURE = "dependency_failure"
    SPECIALIST_UNAVAILABLE = "specialist_unavailable"
    USER_ABANDONED = "user_abandoned"


class StaleTaskDetectionService:
    """Service for detecting and classifying stale tasks."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Stale detection configuration
        self.stale_detection_config = {
            'inactivity_threshold_hours': 24,
            'abandonment_threshold_hours': 72,
            'dependency_check_depth': 3,
            'specialist_timeout_hours': 12,
            'max_retries': 3,
            'orphan_detection_enabled': True,
            'auto_cleanup_threshold_days': 7
        }
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=3, base_delay=0.5),
        component="StaleTaskDetectionService",
        operation="detect_stale_tasks"
    )
    async def detect_stale_tasks(self) -> List[Dict[str, Any]]:
        """
        Detect tasks that are stale based on various criteria.
        
        Returns:
            List of stale task information with reasons and recommended actions
        """
        stale_tasks = []
        
        async with self.db_manager.session_scope() as session:
            # Get all active tasks
            from ...db.models import SubTaskModel, TaskStatus
            from sqlalchemy import select
            
            result = await session.execute(
                select(SubTaskModel).where(
                    SubTaskModel.status.in_([
                        TaskStatus.ACTIVE.value,
                        TaskStatus.PENDING.value,
                        TaskStatus.IN_PROGRESS.value
                    ])
                )
            )
            active_tasks = result.scalars().all()
            
            for task in active_tasks:
                stale_info = await self._analyze_task_staleness(task, session)
                if stale_info:
                    stale_tasks.append(stale_info)
        
        logger.info(f"Detected {len(stale_tasks)} stale tasks")
        return stale_tasks
    
    async def _analyze_task_staleness(self, task, session) -> Optional[Dict[str, Any]]:
        """Analyze a specific task for staleness indicators."""
        current_time = datetime.utcnow()
        task_age = current_time - task.created_at
        
        stale_reasons = []
        severity = "low"
        
        # Check inactivity timeout
        if task.last_activity_at:
            inactivity_duration = current_time - task.last_activity_at
        else:
            inactivity_duration = task_age
        
        inactivity_threshold = timedelta(hours=self.stale_detection_config['inactivity_threshold_hours'])
        if inactivity_duration > inactivity_threshold:
            stale_reasons.append({
                'reason': StaleTaskReason.INACTIVITY_TIMEOUT.value,
                'duration_hours': inactivity_duration.total_seconds() / 3600,
                'threshold_hours': self.stale_detection_config['inactivity_threshold_hours']
            })
            severity = "medium"
        
        # Check workflow abandonment
        workflow_abandonment = await self._check_workflow_abandonment(task, session)
        if workflow_abandonment:
            stale_reasons.append(workflow_abandonment)
            severity = "high"
        
        # Check dependency failures
        dependency_failures = await self._check_dependency_failures(task, session)
        if dependency_failures:
            stale_reasons.extend(dependency_failures)
            severity = "high"
        
        # Check for orphaned tasks
        if await self._is_orphaned_task(task, session):
            stale_reasons.append({
                'reason': StaleTaskReason.ORPHANED_TASK.value,
                'description': 'Task has no parent or valid workflow context'
            })
            severity = "high"
        
        if not stale_reasons:
            return None
        
        recommended_action = self._determine_recommended_action(task, stale_reasons, severity)
        
        return {
            'task_id': task.task_id,
            'parent_task_id': task.parent_task_id,
            'title': task.title,
            'status': task.status,
            'created_at': task.created_at.isoformat(),
            'last_activity_at': task.last_activity_at.isoformat() if task.last_activity_at else None,
            'age_hours': task_age.total_seconds() / 3600,
            'stale_reasons': stale_reasons,
            'severity': severity,
            'recommended_action': recommended_action,
            'auto_cleanup_eligible': self._is_auto_cleanup_eligible(task, stale_reasons, severity)
        }
    
    async def _check_workflow_abandonment(self, task, session) -> Optional[Dict[str, Any]]:
        """Check if the workflow containing this task has been abandoned."""
        if not task.parent_task_id:
            return None
        
        try:
            from ...db.models import TaskBreakdownModel
            from sqlalchemy import select
            
            # Get parent task breakdown
            result = await session.execute(
                select(TaskBreakdownModel).where(
                    TaskBreakdownModel.parent_task_id == task.parent_task_id
                )
            )
            parent_breakdown = result.scalar_one_or_none()
            
            if not parent_breakdown:
                return {
                    'reason': StaleTaskReason.ABANDONED_WORKFLOW.value,
                    'description': 'Parent task breakdown not found'
                }
            
            # Check if any subtasks in the workflow have been active recently
            result = await session.execute(
                select(SubTaskModel).where(
                    SubTaskModel.parent_task_id == task.parent_task_id
                )
            )
            sibling_tasks = result.scalars().all()
            
            current_time = datetime.utcnow()
            abandonment_threshold = timedelta(
                hours=self.stale_detection_config['abandonment_threshold_hours']
            )
            
            recent_activity = False
            for sibling in sibling_tasks:
                if sibling.last_activity_at:
                    time_since_activity = current_time - sibling.last_activity_at
                    if time_since_activity < abandonment_threshold:
                        recent_activity = True
                        break
            
            if not recent_activity:
                return {
                    'reason': StaleTaskReason.ABANDONED_WORKFLOW.value,
                    'description': f'No activity in workflow for {abandonment_threshold.total_seconds() / 3600} hours',
                    'workflow_size': len(sibling_tasks)
                }
        
        except Exception as e:
            logger.warning(f"Error checking workflow abandonment for task {task.task_id}: {str(e)}")
        
        return None
    
    async def _check_dependency_failures(self, task, session) -> List[Dict[str, Any]]:
        """Check if task dependencies have failed or are blocking progress."""
        dependency_failures = []
        
        try:
            # Check if task has dependencies (this would depend on your dependency model)
            # For now, implement basic dependency checking
            
            # Check if specialist is available (simplified check)
            if hasattr(task, 'specialist_type') and task.specialist_type:
                specialist_timeout = timedelta(
                    hours=self.stale_detection_config['specialist_timeout_hours']
                )
                
                if task.last_activity_at:
                    time_since_activity = datetime.utcnow() - task.last_activity_at
                    if time_since_activity > specialist_timeout:
                        dependency_failures.append({
                            'reason': StaleTaskReason.SPECIALIST_UNAVAILABLE.value,
                            'specialist_type': task.specialist_type,
                            'hours_waiting': time_since_activity.total_seconds() / 3600
                        })
        
        except Exception as e:
            logger.warning(f"Error checking dependencies for task {task.task_id}: {str(e)}")
        
        return dependency_failures
    
    async def _is_orphaned_task(self, task, session) -> bool:
        """Check if task is orphaned (no valid parent or workflow context)."""
        if not task.parent_task_id:
            return True
        
        try:
            from ...db.models import TaskBreakdownModel
            from sqlalchemy import select
            
            # Check if parent task breakdown exists
            result = await session.execute(
                select(TaskBreakdownModel).where(
                    TaskBreakdownModel.parent_task_id == task.parent_task_id
                )
            )
            parent_breakdown = result.scalar_one_or_none()
            
            return parent_breakdown is None
        
        except Exception as e:
            logger.warning(f"Error checking orphan status for task {task.task_id}: {str(e)}")
            return False
    
    def _determine_recommended_action(self, task, stale_reasons: List[Dict], severity: str) -> str:
        """Determine the recommended action for a stale task."""
        if severity == "high":
            # Check if it's an orphaned task or abandoned workflow
            for reason in stale_reasons:
                if reason.get('reason') in [
                    StaleTaskReason.ORPHANED_TASK.value,
                    StaleTaskReason.ABANDONED_WORKFLOW.value
                ]:
                    return "archive_immediately"
        
        if severity == "medium":
            # Long inactivity suggests archiving
            for reason in stale_reasons:
                if (reason.get('reason') == StaleTaskReason.INACTIVITY_TIMEOUT.value and
                    reason.get('duration_hours', 0) > 168):  # 1 week
                    return "archive_after_review"
        
        # Default actions based on severity
        if severity == "high":
            return "investigate_and_resolve"
        elif severity == "medium":
            return "notify_and_monitor"
        else:
            return "monitor_only"
    
    def _is_auto_cleanup_eligible(self, task, stale_reasons: List[Dict], severity: str) -> bool:
        """Determine if task is eligible for automatic cleanup."""
        if not self.stale_detection_config.get('orphan_detection_enabled', False):
            return False
        
        # Only auto-cleanup orphaned tasks or clearly abandoned workflows
        auto_cleanup_reasons = [
            StaleTaskReason.ORPHANED_TASK.value,
            StaleTaskReason.ABANDONED_WORKFLOW.value
        ]
        
        for reason in stale_reasons:
            if reason.get('reason') in auto_cleanup_reasons:
                # Check age threshold
                task_age = datetime.utcnow() - task.created_at
                age_threshold = timedelta(
                    days=self.stale_detection_config['auto_cleanup_threshold_days']
                )
                return task_age > age_threshold
        
        return False