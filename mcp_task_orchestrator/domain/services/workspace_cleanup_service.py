"""
Workspace Cleanup Service

Handles comprehensive workspace cleanup operations including orphaned task removal,
incomplete workflow resolution, and database optimization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple

# NOTE: Infrastructure imports removed for Clean Architecture compliance
# Database connections should be injected through repository interfaces
# Error handling should be applied at the infrastructure/application layer
from .stale_task_detection_service import StaleTaskDetectionService
from .task_archival_service import TaskArchivalService


logger = logging.getLogger(__name__)


class CleanupResult:
    """Result of a workspace cleanup operation."""
    
    def __init__(self):
        self.orphaned_tasks_removed = 0
        self.incomplete_workflows_resolved = 0
        self.workflows_archived = 0
        self.database_optimizations = 0
        self.errors = []
        self.warnings = []
        self.total_space_freed_mb = 0.0
        self.execution_time_seconds = 0.0


class WorkspaceCleanupService:
    """Service for comprehensive workspace cleanup operations."""
    
    def __init__(self, db_manager: DatabaseManager, 
                 stale_detection_service: StaleTaskDetectionService,
                 archival_service: TaskArchivalService):
        self.db_manager = db_manager
        self.stale_detection_service = stale_detection_service
        self.archival_service = archival_service
        
        # Cleanup configuration
        self.cleanup_config = {
            'max_cleanup_duration_minutes': 30,
            'orphan_removal_enabled': True,
            'workflow_resolution_enabled': True,
            'database_optimization_enabled': True,
            'safety_checks_enabled': True,
            'backup_before_cleanup': False,
            'max_tasks_per_batch': 50
        }
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=2.0),
        component="WorkspaceCleanupService",
        operation="perform_workspace_cleanup"
    )
    async def perform_workspace_cleanup(self, aggressive: bool = False) -> CleanupResult:
        """
        Perform comprehensive workspace cleanup.
        
        Args:
            aggressive: Whether to perform aggressive cleanup (removes more data)
            
        Returns:
            CleanupResult with detailed cleanup statistics
        """
        start_time = datetime.utcnow()
        result = CleanupResult()
        
        try:
            logger.info("Starting workspace cleanup operation")
            
            # Phase 1: Remove orphaned tasks
            if self.cleanup_config['orphan_removal_enabled']:
                orphan_result = await self._remove_orphaned_tasks(aggressive)
                result.orphaned_tasks_removed = orphan_result['removed_count']
                result.errors.extend(orphan_result.get('errors', []))
            
            # Phase 2: Resolve incomplete workflows
            if self.cleanup_config['workflow_resolution_enabled']:
                workflow_result = await self._resolve_incomplete_workflows(aggressive)
                result.incomplete_workflows_resolved = workflow_result['resolved_count']
                result.workflows_archived = workflow_result['archived_count']
                result.errors.extend(workflow_result.get('errors', []))
            
            # Phase 3: Database optimization
            if self.cleanup_config['database_optimization_enabled']:
                optimization_result = await self._optimize_database_performance()
                result.database_optimizations = optimization_result['optimizations_applied']
                result.total_space_freed_mb = optimization_result.get('space_freed_mb', 0.0)
                result.errors.extend(optimization_result.get('errors', []))
            
            # Phase 4: Update stale task tracking
            await self._update_stale_task_tracking()
            
            # Calculate execution time
            end_time = datetime.utcnow()
            result.execution_time_seconds = (end_time - start_time).total_seconds()
            
            logger.info(f"Workspace cleanup completed in {result.execution_time_seconds:.2f} seconds")
            logger.info(f"Cleanup summary: {result.orphaned_tasks_removed} orphans removed, "
                       f"{result.incomplete_workflows_resolved} workflows resolved, "
                       f"{result.workflows_archived} workflows archived")
            
        except Exception as e:
            logger.error(f"Workspace cleanup failed: {str(e)}")
            result.errors.append(f"Cleanup operation failed: {str(e)}")
        
        return result
    
    async def _remove_orphaned_tasks(self, aggressive: bool = False) -> Dict[str, Any]:
        """Remove tasks that are orphaned (no valid parent or workflow context)."""
        result = {'removed_count': 0, 'errors': []}
        
        try:
            async with self.db_manager.session_scope() as session:
                from ...db.models import SubTaskModel, TaskBreakdownModel
                from sqlalchemy import select, and_, or_
                
                # Find orphaned tasks
                orphaned_query = select(SubTaskModel).where(
                    or_(
                        SubTaskModel.parent_task_id.is_(None),
                        ~select(TaskBreakdownModel.parent_task_id).where(
                            TaskBreakdownModel.parent_task_id == SubTaskModel.parent_task_id
                        ).exists()
                    )
                )
                
                if not aggressive:
                    # Only remove old orphaned tasks in non-aggressive mode
                    cutoff_date = datetime.utcnow() - timedelta(days=7)
                    orphaned_query = orphaned_query.where(SubTaskModel.created_at < cutoff_date)
                
                orphaned_result = await session.execute(orphaned_query)
                orphaned_tasks = orphaned_result.scalars().all()
                
                logger.info(f"Found {len(orphaned_tasks)} orphaned tasks")
                
                # Process orphaned tasks in batches
                batch_size = self.cleanup_config['max_tasks_per_batch']
                for i in range(0, len(orphaned_tasks), batch_size):
                    batch = orphaned_tasks[i:i + batch_size]
                    
                    for task in batch:
                        try:
                            await self._remove_orphaned_task_completely(task, session)
                            result['removed_count'] += 1
                        except Exception as e:
                            error_msg = f"Failed to remove orphaned task {task.task_id}: {str(e)}"
                            result['errors'].append(error_msg)
                            logger.warning(error_msg)
                
                await session.commit()
        
        except Exception as e:
            logger.error(f"Failed to remove orphaned tasks: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    async def _remove_orphaned_task_completely(self, task, session):
        """Completely remove an orphaned task and its associated data."""
        task_id = task.task_id
        
        try:
            # Remove task artifacts if artifact manager is available
            if hasattr(self.archival_service, 'artifact_manager') and self.archival_service.artifact_manager:
                try:
                    await self.archival_service.artifact_manager.delete_task_artifacts(task_id)
                except Exception as e:
                    logger.warning(f"Failed to delete artifacts for task {task_id}: {str(e)}")
            
            # Remove associated records (events, attributes, etc.)
            await self._cleanup_task_associations(task, session)
            
            # Remove the task itself
            await session.delete(task)
            
            logger.debug(f"Completely removed orphaned task {task_id}")
        
        except Exception as e:
            logger.error(f"Failed to completely remove task {task_id}: {str(e)}")
            raise
    
    async def _cleanup_task_associations(self, task, session):
        """Clean up all database associations for a task."""
        task_id = task.task_id
        
        try:
            # Clean up task events if they exist
            from ...db.models import TaskEventModel
            from sqlalchemy import delete
            
            try:
                await session.execute(
                    delete(TaskEventModel).where(TaskEventModel.task_id == task_id)
                )
            except Exception:
                # Table might not exist in all configurations
                pass
            
            # Clean up task attributes if they exist
            try:
                from ...db.models import TaskAttributeModel
                await session.execute(
                    delete(TaskAttributeModel).where(TaskAttributeModel.task_id == task_id)
                )
            except Exception:
                # Table might not exist in all configurations
                pass
            
            # Clean up stale task tracking
            try:
                from ...db.models import StaleTaskTrackingModel
                await session.execute(
                    delete(StaleTaskTrackingModel).where(StaleTaskTrackingModel.task_id == task_id)
                )
            except Exception:
                # Table might not exist in all configurations
                pass
        
        except Exception as e:
            logger.warning(f"Some task associations could not be cleaned up for {task_id}: {str(e)}")
    
    async def _resolve_incomplete_workflows(self, aggressive: bool = False) -> Dict[str, Any]:
        """Identify and resolve incomplete workflows."""
        result = {'resolved_count': 0, 'archived_count': 0, 'errors': []}
        
        try:
            incomplete_workflows = await self._identify_incomplete_workflows(aggressive)
            
            for workflow_info in incomplete_workflows:
                try:
                    resolution_result = await self._resolve_incomplete_workflow(
                        workflow_info, aggressive
                    )
                    
                    if resolution_result['action'] == 'archived':
                        result['archived_count'] += 1
                    else:
                        result['resolved_count'] += 1
                
                except Exception as e:
                    error_msg = f"Failed to resolve workflow {workflow_info.get('parent_task_id', 'unknown')}: {str(e)}"
                    result['errors'].append(error_msg)
                    logger.warning(error_msg)
        
        except Exception as e:
            logger.error(f"Failed to resolve incomplete workflows: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    async def _identify_incomplete_workflows(self, aggressive: bool = False) -> List[Dict[str, Any]]:
        """Identify workflows that are incomplete or stalled."""
        incomplete_workflows = []
        
        try:
            async with self.db_manager.session_scope() as session:
                from ...db.models import TaskBreakdownModel, SubTaskModel
                from sqlalchemy import select, func
                
                # Get all task breakdowns with their subtask counts
                breakdown_query = select(
                    TaskBreakdownModel,
                    func.count(SubTaskModel.task_id).label('total_subtasks'),
                    func.count(
                        func.case(
                            (SubTaskModel.status == 'completed', SubTaskModel.task_id)
                        )
                    ).label('completed_subtasks'),
                    func.count(
                        func.case(
                            (SubTaskModel.status == 'failed', SubTaskModel.task_id)
                        )
                    ).label('failed_subtasks')
                ).outerjoin(
                    SubTaskModel, TaskBreakdownModel.parent_task_id == SubTaskModel.parent_task_id
                ).group_by(TaskBreakdownModel.parent_task_id)
                
                result = await session.execute(breakdown_query)
                workflows = result.all()
                
                current_time = datetime.utcnow()
                
                for breakdown, total_subtasks, completed_subtasks, failed_subtasks in workflows:
                    # Calculate workflow age and activity
                    workflow_age = current_time - breakdown.created_at
                    
                    # Determine if workflow is incomplete
                    is_incomplete = False
                    reason = None
                    
                    if total_subtasks == 0:
                        is_incomplete = True
                        reason = "no_subtasks"
                    elif failed_subtasks > 0 and completed_subtasks + failed_subtasks == total_subtasks:
                        is_incomplete = True
                        reason = "all_tasks_terminal"
                    elif workflow_age > timedelta(days=14 if aggressive else 30):
                        completion_rate = completed_subtasks / total_subtasks if total_subtasks > 0 else 0
                        if completion_rate < 0.5:
                            is_incomplete = True
                            reason = "low_completion_rate"
                    
                    if is_incomplete:
                        incomplete_workflows.append({
                            'parent_task_id': breakdown.parent_task_id,
                            'description': breakdown.description,
                            'created_at': breakdown.created_at,
                            'total_subtasks': total_subtasks,
                            'completed_subtasks': completed_subtasks,
                            'failed_subtasks': failed_subtasks,
                            'completion_rate': completed_subtasks / total_subtasks if total_subtasks > 0 else 0,
                            'age_days': workflow_age.days,
                            'reason': reason
                        })
        
        except Exception as e:
            logger.error(f"Failed to identify incomplete workflows: {str(e)}")
        
        return incomplete_workflows
    
    async def _resolve_incomplete_workflow(self, workflow_info: Dict[str, Any], 
                                         aggressive: bool = False) -> Dict[str, Any]:
        """Resolve a specific incomplete workflow."""
        parent_task_id = workflow_info['parent_task_id']
        reason = workflow_info['reason']
        
        try:
            # Determine resolution strategy
            if reason == "no_subtasks" or (aggressive and workflow_info['completion_rate'] < 0.1):
                # Archive the entire workflow
                await self._archive_entire_workflow(parent_task_id, reason)
                return {'action': 'archived', 'parent_task_id': parent_task_id}
            
            elif reason == "all_tasks_terminal":
                # Mark workflow as completed or failed based on success rate
                success_rate = workflow_info['completed_subtasks'] / workflow_info['total_subtasks']
                if success_rate >= 0.7:
                    await self._mark_workflow_completed(parent_task_id)
                    return {'action': 'completed', 'parent_task_id': parent_task_id}
                else:
                    await self._mark_workflow_failed(parent_task_id)
                    return {'action': 'failed', 'parent_task_id': parent_task_id}
            
            elif reason == "low_completion_rate":
                # Archive workflow if it's old and has low completion
                if workflow_info['age_days'] > 30:
                    await self._archive_entire_workflow(parent_task_id, reason)
                    return {'action': 'archived', 'parent_task_id': parent_task_id}
                else:
                    # Mark for monitoring
                    await self._mark_workflow_for_monitoring(parent_task_id)
                    return {'action': 'monitoring', 'parent_task_id': parent_task_id}
            
            return {'action': 'no_action', 'parent_task_id': parent_task_id}
        
        except Exception as e:
            logger.error(f"Failed to resolve workflow {parent_task_id}: {str(e)}")
            raise
    
    async def _archive_entire_workflow(self, parent_task_id: str, reason: str):
        """Archive an entire workflow including all its subtasks."""
        async with self.db_manager.session_scope() as session:
            from ...db.models import SubTaskModel, TaskBreakdownModel
            from sqlalchemy import select, update
            
            # Get all subtasks for the workflow
            result = await session.execute(
                select(SubTaskModel).where(SubTaskModel.parent_task_id == parent_task_id)
            )
            subtasks = result.scalars().all()
            
            # Archive each subtask
            for subtask in subtasks:
                if subtask.status not in ['archived', 'completed']:
                    archive_result = await self.archival_service.archive_task(
                        subtask.task_id, 
                        reason=f"workflow_cleanup_{reason}",
                        preserve_artifacts=True
                    )
                    
                    if not archive_result.success:
                        logger.warning(f"Failed to archive subtask {subtask.task_id}: {archive_result.error}")
            
            # Update the breakdown status
            await session.execute(
                update(TaskBreakdownModel)
                .where(TaskBreakdownModel.parent_task_id == parent_task_id)
                .values(status='archived', archived_at=datetime.utcnow())
            )
            
            await session.commit()
            logger.info(f"Archived entire workflow {parent_task_id} with {len(subtasks)} subtasks")
    
    async def _mark_workflow_completed(self, parent_task_id: str):
        """Mark a workflow as completed."""
        async with self.db_manager.session_scope() as session:
            from ...db.models import TaskBreakdownModel
            from sqlalchemy import update
            
            await session.execute(
                update(TaskBreakdownModel)
                .where(TaskBreakdownModel.parent_task_id == parent_task_id)
                .values(status='completed', completed_at=datetime.utcnow())
            )
            
            await session.commit()
            logger.info(f"Marked workflow {parent_task_id} as completed")
    
    async def _mark_workflow_failed(self, parent_task_id: str):
        """Mark a workflow as failed."""
        async with self.db_manager.session_scope() as session:
            from ...db.models import TaskBreakdownModel
            from sqlalchemy import update
            
            await session.execute(
                update(TaskBreakdownModel)
                .where(TaskBreakdownModel.parent_task_id == parent_task_id)
                .values(status='failed', failed_at=datetime.utcnow())
            )
            
            await session.commit()
            logger.info(f"Marked workflow {parent_task_id} as failed")
    
    async def _mark_workflow_for_monitoring(self, parent_task_id: str):
        """Mark a workflow for continued monitoring."""
        async with self.db_manager.session_scope() as session:
            from ...db.models import StaleTaskTrackingModel
            from sqlalchemy import select
            
            # Check if already being tracked
            result = await session.execute(
                select(StaleTaskTrackingModel).where(
                    StaleTaskTrackingModel.task_id == parent_task_id
                )
            )
            existing_tracking = result.scalar_one_or_none()
            
            if not existing_tracking:
                tracking_record = StaleTaskTrackingModel(
                    task_id=parent_task_id,
                    first_detected_at=datetime.utcnow(),
                    detection_reason='incomplete_workflow_monitoring',
                    severity='medium',
                    auto_cleanup_eligible=False
                )
                session.add(tracking_record)
                await session.commit()
                logger.info(f"Added workflow {parent_task_id} to monitoring")
    
    async def _optimize_database_performance(self) -> Dict[str, Any]:
        """Optimize database performance through cleanup and maintenance."""
        result = {'optimizations_applied': 0, 'space_freed_mb': 0.0, 'errors': []}
        
        try:
            async with self.db_manager.session_scope() as session:
                # Optimization 1: Clean up old tracking records
                from ...db.models import StaleTaskTrackingModel
                from sqlalchemy import delete
                
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                deleted_tracking = await session.execute(
                    delete(StaleTaskTrackingModel).where(
                        StaleTaskTrackingModel.first_detected_at < cutoff_date
                    )
                )
                
                if deleted_tracking.rowcount > 0:
                    result['optimizations_applied'] += 1
                    logger.info(f"Cleaned up {deleted_tracking.rowcount} old tracking records")
                
                # Optimization 2: Update statistics (if supported by database)
                try:
                    await session.execute("ANALYZE")
                    result['optimizations_applied'] += 1
                    logger.info("Updated database statistics")
                except Exception:
                    # Not all databases support ANALYZE
                    pass
                
                # Optimization 3: Cleanup empty space (if supported)
                try:
                    await session.execute("VACUUM")
                    result['optimizations_applied'] += 1
                    result['space_freed_mb'] = 5.0  # Estimated
                    logger.info("Performed database vacuum")
                except Exception:
                    # Not all databases support VACUUM
                    pass
                
                await session.commit()
        
        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            result['errors'].append(str(e))
        
        return result
    
    async def _update_stale_task_tracking(self):
        """Update stale task tracking records based on current state."""
        try:
            # Get current stale tasks
            stale_tasks = await self.stale_detection_service.detect_stale_tasks()
            
            async with self.db_manager.session_scope() as session:
                from ...db.models import StaleTaskTrackingModel
                from sqlalchemy import select
                
                # Update tracking for each stale task
                for stale_task in stale_tasks:
                    task_id = stale_task['task_id']
                    
                    # Check if already being tracked
                    result = await session.execute(
                        select(StaleTaskTrackingModel).where(
                            StaleTaskTrackingModel.task_id == task_id
                        )
                    )
                    tracking_record = result.scalar_one_or_none()
                    
                    if tracking_record:
                        # Update existing record
                        tracking_record.last_detected_at = datetime.utcnow()
                        tracking_record.severity = stale_task['severity']
                        tracking_record.auto_cleanup_eligible = stale_task['auto_cleanup_eligible']
                    else:
                        # Create new tracking record
                        new_tracking = StaleTaskTrackingModel(
                            task_id=task_id,
                            first_detected_at=datetime.utcnow(),
                            last_detected_at=datetime.utcnow(),
                            detection_reason=stale_task['stale_reasons'][0]['reason'] if stale_task['stale_reasons'] else 'unknown',
                            severity=stale_task['severity'],
                            auto_cleanup_eligible=stale_task['auto_cleanup_eligible']
                        )
                        session.add(new_tracking)
                
                await session.commit()
                logger.info(f"Updated tracking for {len(stale_tasks)} stale tasks")
        
        except Exception as e:
            logger.error(f"Failed to update stale task tracking: {str(e)}")