"""
Task Archival Service

Handles comprehensive task archival operations including archive artifact creation,
retention management, and cleanup of expired archives.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

# NOTE: Infrastructure imports removed for Clean Architecture compliance
# Database connections should be injected through repository interfaces  
# Error handling should be applied at the infrastructure/application layer

logger = logging.getLogger(__name__)


class ArchivalResult:
    """Result of a task archival operation."""
    
    def __init__(self, success: bool, task_id: str, archive_id: Optional[str] = None, 
                 error: Optional[str] = None, artifacts_created: Optional[List[str]] = None):
        self.success = success
        self.task_id = task_id
        self.archive_id = archive_id
        self.error = error
        self.artifacts_created = artifacts_created or []


class TaskArchivalService:
    """Service for handling task archival operations."""
    
    def __init__(self, db_manager: DatabaseManager, artifact_manager=None):
        self.db_manager = db_manager
        self.artifact_manager = artifact_manager
        
        # Archive retention configuration
        self.archive_retention_config = {
            'default_retention_days': 90,
            'priority_task_retention_days': 180,
            'failed_task_retention_days': 30,
            'max_archive_size_mb': 100,
            'compress_archives': True,
            'preserve_critical_artifacts': True
        }
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=3, base_delay=0.5),
        component="TaskArchivalService",
        operation="archive_task"
    )
    async def archive_task(self, task_id: str, reason: str = "stale", 
                          preserve_artifacts: bool = True) -> ArchivalResult:
        """
        Archive a task with comprehensive data preservation.
        
        Args:
            task_id: ID of the task to archive
            reason: Reason for archival
            preserve_artifacts: Whether to preserve task artifacts
            
        Returns:
            ArchivalResult with operation details
        """
        try:
            async with self.db_manager.session_scope() as session:
                # Get task details
                from ...db.models import SubTaskModel, TaskStatus
                from sqlalchemy import select
                
                result = await session.execute(
                    select(SubTaskModel).where(SubTaskModel.task_id == task_id)
                )
                task = result.scalar_one_or_none()
                
                if not task:
                    return ArchivalResult(
                        success=False,
                        task_id=task_id,
                        error=f"Task {task_id} not found"
                    )
                
                # Prepare archive data
                archive_data = await self._prepare_archive_data(task, session)
                
                # Create archive record
                archive_id = await self._create_archive_record(
                    task, archive_data, reason, session
                )
                
                # Create archive artifacts if requested
                artifacts_created = []
                if preserve_artifacts and self.artifact_manager:
                    artifacts_created = await self._create_archive_artifact(
                        task, archive_data, archive_id
                    )
                
                # Update task status to archived
                task.status = TaskStatus.ARCHIVED.value
                task.archived_at = datetime.utcnow()
                task.archive_reason = reason
                task.archive_id = archive_id
                
                await session.commit()
                
                logger.info(f"Successfully archived task {task_id} with archive ID {archive_id}")
                
                return ArchivalResult(
                    success=True,
                    task_id=task_id,
                    archive_id=archive_id,
                    artifacts_created=artifacts_created
                )
        
        except Exception as e:
            logger.error(f"Failed to archive task {task_id}: {str(e)}")
            return ArchivalResult(
                success=False,
                task_id=task_id,
                error=str(e)
            )
    
    async def _prepare_archive_data(self, task, session) -> Dict[str, Any]:
        """Prepare comprehensive archive data for a task."""
        archive_data = {
            'task_id': task.task_id,
            'parent_task_id': task.parent_task_id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'specialist_type': getattr(task, 'specialist_type', None),
            'created_at': task.created_at.isoformat(),
            'last_activity_at': task.last_activity_at.isoformat() if task.last_activity_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'results': getattr(task, 'results', None),
            'artifacts': getattr(task, 'artifacts', []),
            'metadata': getattr(task, 'metadata', {}),
            'archive_timestamp': datetime.utcnow().isoformat()
        }
        
        # Include parent task information if available
        if task.parent_task_id:
            try:
                from ...db.models import TaskBreakdownModel
                from sqlalchemy import select
                
                result = await session.execute(
                    select(TaskBreakdownModel).where(
                        TaskBreakdownModel.parent_task_id == task.parent_task_id
                    )
                )
                parent_breakdown = result.scalar_one_or_none()
                
                if parent_breakdown:
                    archive_data['parent_context'] = {
                        'parent_task_id': parent_breakdown.parent_task_id,
                        'description': parent_breakdown.description,
                        'complexity': parent_breakdown.complexity,
                        'created_at': parent_breakdown.created_at.isoformat()
                    }
            except Exception as e:
                logger.warning(f"Could not retrieve parent context for task {task.task_id}: {str(e)}")
        
        # Include workflow context (sibling tasks)
        if task.parent_task_id:
            try:
                from ...db.models import SubTaskModel
                from sqlalchemy import select
                
                result = await session.execute(
                    select(SubTaskModel).where(
                        SubTaskModel.parent_task_id == task.parent_task_id
                    )
                )
                sibling_tasks = result.scalars().all()
                
                archive_data['workflow_context'] = {
                    'total_siblings': len(sibling_tasks),
                    'completed_siblings': len([t for t in sibling_tasks if t.status == 'completed']),
                    'failed_siblings': len([t for t in sibling_tasks if t.status == 'failed']),
                    'workflow_progress': self._calculate_workflow_progress(sibling_tasks)
                }
            except Exception as e:
                logger.warning(f"Could not retrieve workflow context for task {task.task_id}: {str(e)}")
        
        return archive_data
    
    async def _create_archive_record(self, task, archive_data: Dict[str, Any], 
                                   reason: str, session) -> str:
        """Create a database record for the archived task."""
        from ...db.models import TaskArchiveModel
        import uuid
        
        archive_id = f"arch_{uuid.uuid4().hex[:12]}"
        
        # Calculate retention date
        retention_days = self._get_retention_days(task, reason)
        retention_date = datetime.utcnow() + timedelta(days=retention_days)
        
        archive_record = TaskArchiveModel(
            archive_id=archive_id,
            original_task_id=task.task_id,
            parent_task_id=task.parent_task_id,
            archive_reason=reason,
            archive_data=json.dumps(archive_data),
            archived_at=datetime.utcnow(),
            retention_until=retention_date,
            archive_size_bytes=len(json.dumps(archive_data).encode('utf-8')),
            preservation_priority=self._determine_preservation_priority(task, archive_data)
        )
        
        session.add(archive_record)
        await session.flush()  # Get the ID
        
        return archive_id
    
    async def _create_archive_artifact(self, task, archive_data: Dict[str, Any], 
                                     archive_id: str) -> List[str]:
        """Create archive artifacts using the artifact manager."""
        if not self.artifact_manager:
            return []
        
        artifacts_created = []
        
        try:
            # Create comprehensive archive artifact
            archive_content = {
                'type': 'task_archive',
                'version': '1.0',
                'archive_id': archive_id,
                'data': archive_data,
                'metadata': {
                    'archived_by': 'TaskArchivalService',
                    'compression': self.archive_retention_config.get('compress_archives', False),
                    'preservation_level': 'standard'
                }
            }
            
            # Create main archive artifact
            main_artifact = await self.artifact_manager.create_artifact(
                task_id=task.task_id,
                content=json.dumps(archive_content, indent=2),
                artifact_type='archive',
                filename=f"task_archive_{archive_id}.json",
                metadata={'archive_id': archive_id, 'type': 'complete_archive'}
            )
            
            if main_artifact:
                artifacts_created.append(main_artifact.get('artifact_id'))
            
            # Create summary artifact for quick access
            summary_content = {
                'task_id': task.task_id,
                'archive_id': archive_id,
                'title': archive_data.get('title'),
                'status': archive_data.get('status'),
                'archived_at': archive_data.get('archive_timestamp'),
                'summary': self._generate_archive_summary(archive_data)
            }
            
            summary_artifact = await self.artifact_manager.create_artifact(
                task_id=task.task_id,
                content=json.dumps(summary_content, indent=2),
                artifact_type='summary',
                filename=f"task_summary_{archive_id}.json",
                metadata={'archive_id': archive_id, 'type': 'archive_summary'}
            )
            
            if summary_artifact:
                artifacts_created.append(summary_artifact.get('artifact_id'))
        
        except Exception as e:
            logger.warning(f"Failed to create archive artifacts for task {task.task_id}: {str(e)}")
        
        return artifacts_created
    
    @handle_errors(
        auto_retry=True,
        retry_policy=ExponentialBackoffPolicy(max_attempts=2, base_delay=1.0),
        component="TaskArchivalService",
        operation="cleanup_expired_archives"
    )
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up expired archive records and artifacts."""
        cleanup_stats = {
            'archives_processed': 0,
            'archives_deleted': 0,
            'artifacts_deleted': 0,
            'errors': []
        }
        
        try:
            async with self.db_manager.session_scope() as session:
                from ...db.models import TaskArchiveModel
                from sqlalchemy import select, delete
                
                # Find expired archives
                current_time = datetime.utcnow()
                result = await session.execute(
                    select(TaskArchiveModel).where(
                        TaskArchiveModel.retention_until < current_time
                    )
                )
                expired_archives = result.scalars().all()
                
                cleanup_stats['archives_processed'] = len(expired_archives)
                
                for archive in expired_archives:
                    try:
                        # Check if archive should be preserved
                        if await self._should_preserve_archive(archive):
                            logger.info(f"Preserving archive {archive.archive_id} due to preservation rules")
                            continue
                        
                        # Delete associated artifacts
                        if self.artifact_manager and hasattr(archive, 'original_task_id'):
                            try:
                                deleted_artifacts = await self.artifact_manager.delete_task_artifacts(
                                    archive.original_task_id
                                )
                                cleanup_stats['artifacts_deleted'] += len(deleted_artifacts)
                            except Exception as e:
                                cleanup_stats['errors'].append(f"Failed to delete artifacts for archive {archive.archive_id}: {str(e)}")
                        
                        # Delete archive record
                        await session.delete(archive)
                        cleanup_stats['archives_deleted'] += 1
                        
                    except Exception as e:
                        cleanup_stats['errors'].append(f"Failed to process archive {archive.archive_id}: {str(e)}")
                
                await session.commit()
        
        except Exception as e:
            logger.error(f"Failed to cleanup expired archives: {str(e)}")
            cleanup_stats['errors'].append(str(e))
        
        logger.info(f"Archive cleanup completed: {cleanup_stats}")
        return cleanup_stats
    
    async def _should_preserve_archive(self, archive) -> bool:
        """Determine if an archive should be preserved despite expiration."""
        # Check preservation priority
        if archive.preservation_priority == 'critical':
            return True
        
        # Check if it's a high-value archive
        if archive.preservation_priority == 'high':
            # Extend retention for high-priority archives
            extended_retention = archive.retention_until + timedelta(days=30)
            if datetime.utcnow() < extended_retention:
                return True
        
        # Check archive size - preserve small archives longer
        if (self.archive_retention_config.get('preserve_critical_artifacts', False) and
            archive.archive_size_bytes < 1024 * 1024):  # < 1MB
            return True
        
        return False
    
    def _get_retention_days(self, task, reason: str) -> int:
        """Calculate retention days based on task and archive reason."""
        if reason == 'failed' or task.status == 'failed':
            return self.archive_retention_config['failed_task_retention_days']
        elif getattr(task, 'priority', None) == 'high':
            return self.archive_retention_config['priority_task_retention_days']
        else:
            return self.archive_retention_config['default_retention_days']
    
    def _determine_preservation_priority(self, task, archive_data: Dict[str, Any]) -> str:
        """Determine the preservation priority for an archive."""
        # Critical if task has results or significant artifacts
        if (archive_data.get('results') and 
            len(archive_data.get('artifacts', [])) > 0):
            return 'critical'
        
        # High if task was part of a completed workflow
        workflow_context = archive_data.get('workflow_context', {})
        if workflow_context.get('workflow_progress', 0) > 0.8:
            return 'high'
        
        # High if task ran for a significant time
        if task.created_at and task.last_activity_at:
            duration = task.last_activity_at - task.created_at
            if duration.total_seconds() > 3600 * 4:  # 4 hours
                return 'high'
        
        return 'standard'
    
    def _calculate_workflow_progress(self, sibling_tasks) -> float:
        """Calculate workflow completion progress."""
        if not sibling_tasks:
            return 0.0
        
        completed_count = len([t for t in sibling_tasks if t.status == 'completed'])
        return completed_count / len(sibling_tasks)
    
    def _generate_archive_summary(self, archive_data: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the archived task."""
        summary_parts = []
        
        if archive_data.get('title'):
            summary_parts.append(f"Task: {archive_data['title']}")
        
        if archive_data.get('status'):
            summary_parts.append(f"Status: {archive_data['status']}")
        
        if archive_data.get('specialist_type'):
            summary_parts.append(f"Specialist: {archive_data['specialist_type']}")
        
        workflow_context = archive_data.get('workflow_context', {})
        if workflow_context:
            progress = workflow_context.get('workflow_progress', 0)
            summary_parts.append(f"Workflow Progress: {progress:.1%}")
        
        duration_info = self._calculate_task_duration(archive_data)
        if duration_info:
            summary_parts.append(duration_info)
        
        return ". ".join(summary_parts)
    
    def _calculate_task_duration(self, archive_data: Dict[str, Any]) -> Optional[str]:
        """Calculate and format task duration."""
        try:
            created_str = archive_data.get('created_at')
            activity_str = archive_data.get('last_activity_at') or archive_data.get('completed_at')
            
            if created_str and activity_str:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                activity = datetime.fromisoformat(activity_str.replace('Z', '+00:00'))
                duration = activity - created
                
                if duration.total_seconds() > 3600:
                    hours = duration.total_seconds() / 3600
                    return f"Duration: {hours:.1f} hours"
                else:
                    minutes = duration.total_seconds() / 60
                    return f"Duration: {minutes:.0f} minutes"
        except Exception as e:
            logger.debug(f"Could not calculate task duration: {str(e)}")
        
        return None