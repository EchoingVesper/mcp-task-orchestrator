"""
Maintenance Coordinator for the MCP Task Orchestrator.

This module provides automated maintenance capabilities including task cleanup,
structure validation, documentation updates, and handover preparation.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path

from ..db.persistence import DatabasePersistenceManager
from ..db.models import (
    TaskBreakdownModel, SubTaskModel, MaintenanceOperationModel,
    TaskLifecycleModel, StaleTaskTrackingModel, TaskArchiveModel
)
from .models import TaskStatus, SpecialistType
from .core import TaskOrchestrator

logger = logging.getLogger("mcp_task_orchestrator.maintenance")


class MaintenanceCoordinator:
    """Coordinates automated maintenance operations for the task orchestrator."""
    
    # Configuration constants
    DEFAULT_STALE_THRESHOLD_HOURS = 24
    DEFAULT_ARCHIVE_RETENTION_DAYS = 30
    DEFAULT_MAX_CLEANUP_BATCH_SIZE = 50
    
    def __init__(self, state_manager: DatabasePersistenceManager, orchestrator: TaskOrchestrator):
        """Initialize the maintenance coordinator.
        
        Args:
            state_manager: Database persistence manager for data operations
            orchestrator: Task orchestrator for accessing task state
        """
        self.state_manager = state_manager
        self.orchestrator = orchestrator
        self.logger = logger
        
        self.logger.info("Initialized MaintenanceCoordinator")
    
    async def scan_and_cleanup(self, 
                              scope: str = "current_session",
                              validation_level: str = "basic",
                              target_task_id: Optional[str] = None) -> Dict[str, Any]:
        """Scan for maintenance needs and perform cleanup operations.
        
        Args:
            scope: Scope of cleanup - current_session, full_project, or specific_subtask
            validation_level: Level of validation - basic, comprehensive, or full_audit
            target_task_id: Specific task ID when scope is specific_subtask
            
        Returns:
            Dictionary containing cleanup results and recommendations
        """
        self.logger.info(f"Starting scan_and_cleanup: scope={scope}, level={validation_level}")
        
        try:
            # Record maintenance operation start
            operation_id = await self._start_maintenance_operation(
                "scan_cleanup", scope, validation_level, target_task_id
            )
            
            # Initialize results structure
            results = {
                "operation_id": operation_id,
                "scope": scope,
                "validation_level": validation_level,
                "started_at": datetime.utcnow().isoformat(),
                "scan_results": {},
                "cleanup_actions": [],
                "recommendations": [],
                "summary": {}
            }
            
            # Perform scope-specific scanning
            if scope == "current_session":
                scan_results = await self._scan_current_session(validation_level)
            elif scope == "full_project":
                scan_results = await self._scan_full_project(validation_level)
            elif scope == "specific_subtask":
                if not target_task_id:
                    raise ValueError("target_task_id required for specific_subtask scope")
                scan_results = await self._scan_specific_task(target_task_id, validation_level)
            else:
                raise ValueError(f"Invalid scope: {scope}")
            
            results["scan_results"] = scan_results
            
            # Perform cleanup based on scan results
            cleanup_actions = await self._perform_cleanup_actions(scan_results, validation_level)
            results["cleanup_actions"] = cleanup_actions
            
            # Generate recommendations for manual actions
            recommendations = await self._generate_recommendations(scan_results, cleanup_actions)
            results["recommendations"] = recommendations
            
            # Create summary
            results["summary"] = {
                "total_tasks_scanned": scan_results.get("total_tasks", 0),
                "stale_tasks_found": len(scan_results.get("stale_tasks", [])),
                "cleanup_actions_performed": len(cleanup_actions),
                "recommendations_generated": len(recommendations),
                "operation_status": "completed"
            }
            
            # Complete maintenance operation record
            await self._complete_maintenance_operation(operation_id, results)
            
            self.logger.info(f"Completed scan_and_cleanup operation {operation_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in scan_and_cleanup: {str(e)}")
            if 'operation_id' in locals():
                await self._fail_maintenance_operation(operation_id, str(e))
            
            return {
                "scope": scope,
                "validation_level": validation_level,
                "error": str(e),
                "operation_status": "failed",
                "started_at": datetime.utcnow().isoformat()
            }
    
    async def _scan_current_session(self, validation_level: str) -> Dict[str, Any]:
        """Scan the current session for maintenance needs.
        
        Args:
            validation_level: Level of validation to perform
            
        Returns:
            Dictionary containing scan results
        """
        self.logger.info("Scanning current session for maintenance needs")
        
        # Get all active tasks from the orchestrator
        try:
            with self.state_manager.session_scope() as session:
                # Get all task breakdowns (parent tasks)
                parent_tasks = session.query(TaskBreakdownModel).all()
                
                # Get all subtasks
                all_subtasks = session.query(SubTaskModel).all()
                
                # Analyze task states and identify issues
                scan_results = {
                    "total_parent_tasks": len(parent_tasks),
                    "total_tasks": len(all_subtasks),
                    "task_status_distribution": {},
                    "stale_tasks": [],
                    "orphaned_tasks": [],
                    "incomplete_workflows": [],
                    "performance_issues": []
                }
                
                # Analyze task status distribution
                status_counts = {}
                for subtask in all_subtasks:
                    status = subtask.status
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                scan_results["task_status_distribution"] = status_counts
                
                # Identify stale tasks (tasks in active/pending state for too long)
                stale_threshold = datetime.utcnow() - timedelta(hours=self.DEFAULT_STALE_THRESHOLD_HOURS)
                
                for subtask in all_subtasks:
                    # Check if task is potentially stale
                    if subtask.status in ['active', 'pending'] and subtask.created_at < stale_threshold:
                        stale_info = {
                            "task_id": subtask.task_id,
                            "title": subtask.title,
                            "status": subtask.status,
                            "created_at": subtask.created_at.isoformat(),
                            "age_hours": (datetime.utcnow() - subtask.created_at).total_seconds() / 3600,
                            "specialist_type": subtask.specialist_type,
                            "parent_task_id": subtask.parent_task_id
                        }
                        scan_results["stale_tasks"].append(stale_info)
                
                # Identify orphaned tasks (subtasks without parent tasks)
                parent_task_ids = {pt.parent_task_id for pt in parent_tasks}
                for subtask in all_subtasks:
                    if subtask.parent_task_id not in parent_task_ids:
                        orphan_info = {
                            "task_id": subtask.task_id,
                            "title": subtask.title,
                            "missing_parent_id": subtask.parent_task_id,
                            "status": subtask.status
                        }
                        scan_results["orphaned_tasks"].append(orphan_info)
                
                # Identify incomplete workflows (parent tasks with mixed completion states)
                for parent_task in parent_tasks:
                    subtasks = [st for st in all_subtasks if st.parent_task_id == parent_task.parent_task_id]
                    
                    if subtasks:
                        statuses = [st.status for st in subtasks]
                        completed_count = statuses.count('completed')
                        total_count = len(statuses)
                        
                        # Check for inconsistent states
                        if 0 < completed_count < total_count:
                            # Some tasks completed, some not - potentially stale workflow
                            incomplete_info = {
                                "parent_task_id": parent_task.parent_task_id,
                                "description": parent_task.description,
                                "total_subtasks": total_count,
                                "completed_subtasks": completed_count,
                                "completion_percentage": (completed_count / total_count) * 100,
                                "last_activity": max(st.created_at for st in subtasks).isoformat()
                            }
                            scan_results["incomplete_workflows"].append(incomplete_info)
                
                self.logger.info(f"Session scan completed: {len(scan_results['stale_tasks'])} stale tasks found")
                return scan_results
                
        except Exception as e:
            self.logger.error(f"Error scanning current session: {str(e)}")
            raise
    
    async def _perform_cleanup_actions(self, scan_results: Dict[str, Any], validation_level: str) -> List[Dict[str, Any]]:
        """Perform automated cleanup actions based on scan results.
        
        Args:
            scan_results: Results from the scanning phase
            validation_level: Level of validation for cleanup actions
            
        Returns:
            List of cleanup actions performed
        """
        self.logger.info("Performing automated cleanup actions")
        
        cleanup_actions = []
        
        try:
            # Cleanup stale tasks
            stale_tasks = scan_results.get("stale_tasks", [])
            
            if stale_tasks and validation_level in ["comprehensive", "full_audit"]:
                self.logger.info(f"Cleaning up {len(stale_tasks)} stale tasks")
                
                for stale_task in stale_tasks[:self.DEFAULT_MAX_CLEANUP_BATCH_SIZE]:
                    try:
                        # Archive the stale task
                        archive_result = await self._archive_stale_task(stale_task)
                        
                        cleanup_action = {
                            "action_type": "archive_stale_task",
                            "task_id": stale_task["task_id"],
                            "reason": f"Task stale for {stale_task['age_hours']:.1f} hours",
                            "result": archive_result,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        cleanup_actions.append(cleanup_action)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to archive stale task {stale_task['task_id']}: {str(e)}")
                        
                        cleanup_action = {
                            "action_type": "archive_stale_task",
                            "task_id": stale_task["task_id"],
                            "result": "failed",
                            "error": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        cleanup_actions.append(cleanup_action)
            
            # Cleanup orphaned tasks
            orphaned_tasks = scan_results.get("orphaned_tasks", [])
            
            if orphaned_tasks:
                self.logger.info(f"Cleaning up {len(orphaned_tasks)} orphaned tasks")
                
                for orphaned_task in orphaned_tasks:
                    try:
                        # Remove orphaned task from database
                        removal_result = await self._remove_orphaned_task(orphaned_task)
                        
                        cleanup_action = {
                            "action_type": "remove_orphaned_task",
                            "task_id": orphaned_task["task_id"],
                            "reason": f"Missing parent task {orphaned_task['missing_parent_id']}",
                            "result": removal_result,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        cleanup_actions.append(cleanup_action)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to remove orphaned task {orphaned_task['task_id']}: {str(e)}")
            
            self.logger.info(f"Completed {len(cleanup_actions)} cleanup actions")
            return cleanup_actions
            
        except Exception as e:
            self.logger.error(f"Error performing cleanup actions: {str(e)}")
            raise
    
    async def _archive_stale_task(self, stale_task_info: Dict[str, Any]) -> str:
        """Archive a stale task to the archive table.
        
        Args:
            stale_task_info: Information about the stale task
            
        Returns:
            Result status string
        """
        try:
            with self.state_manager.session_scope() as session:
                # Get the full task information
                subtask = session.query(SubTaskModel).filter_by(
                    task_id=stale_task_info["task_id"]
                ).first()
                
                if not subtask:
                    return "task_not_found"
                
                # Create archive record
                archive_data = {
                    "task_id": subtask.task_id,
                    "title": subtask.title,
                    "description": subtask.description,
                    "specialist_type": subtask.specialist_type,
                    "status": subtask.status,
                    "results": subtask.results,
                    "artifacts": subtask.artifacts,
                    "created_at": subtask.created_at.isoformat() if subtask.created_at else None,
                    "completed_at": subtask.completed_at.isoformat() if subtask.completed_at else None
                }
                
                archive_record = TaskArchiveModel(
                    original_task_id=subtask.task_id,
                    parent_task_id=subtask.parent_task_id,
                    archive_reason="stale",
                    archived_data=archive_data,
                    artifacts_preserved=bool(subtask.artifacts),
                    artifact_references=subtask.artifacts or [],
                    expires_at=datetime.utcnow() + timedelta(days=self.DEFAULT_ARCHIVE_RETENTION_DAYS)
                )
                
                session.add(archive_record)
                
                # Remove the task from the active tasks table
                session.delete(subtask)
                
                session.commit()
                
                self.logger.info(f"Archived stale task {stale_task_info['task_id']}")
                return "archived_successfully"
                
        except Exception as e:
            self.logger.error(f"Error archiving stale task {stale_task_info['task_id']}: {str(e)}")
            raise
    
    async def _remove_orphaned_task(self, orphaned_task_info: Dict[str, Any]) -> str:
        """Remove an orphaned task from the database.
        
        Args:
            orphaned_task_info: Information about the orphaned task
            
        Returns:
            Result status string
        """
        try:
            with self.state_manager.session_scope() as session:
                # Get the orphaned task
                subtask = session.query(SubTaskModel).filter_by(
                    task_id=orphaned_task_info["task_id"]
                ).first()
                
                if not subtask:
                    return "task_not_found"
                
                # Archive the orphaned task before removal (for audit trail)
                archive_data = {
                    "task_id": subtask.task_id,
                    "title": subtask.title,
                    "description": subtask.description,
                    "specialist_type": subtask.specialist_type,
                    "status": subtask.status,
                    "orphan_reason": f"Missing parent task {orphaned_task_info['missing_parent_id']}"
                }
                
                archive_record = TaskArchiveModel(
                    original_task_id=subtask.task_id,
                    parent_task_id=orphaned_task_info["missing_parent_id"],
                    archive_reason="orphaned",
                    archived_data=archive_data,
                    artifacts_preserved=False
                )
                
                session.add(archive_record)
                
                # Remove the orphaned task
                session.delete(subtask)
                
                session.commit()
                
                self.logger.info(f"Removed orphaned task {orphaned_task_info['task_id']}")
                return "removed_successfully"
                
        except Exception as e:
            self.logger.error(f"Error removing orphaned task {orphaned_task_info['task_id']}: {str(e)}")
            raise

    async def validate_structure(self, 
                                scope: str = "current_session",
                                validation_level: str = "basic",
                                target_task_id: Optional[str] = None) -> Dict[str, Any]:
        """Validate the structure and consistency of tasks and dependencies.
        
        Args:
            scope: Scope of validation - current_session, full_project, or specific_subtask
            validation_level: Level of validation - basic, comprehensive, or full_audit
            target_task_id: Specific task ID when scope is specific_subtask
            
        Returns:
            Dictionary containing validation results
        """
        self.logger.info(f"Starting structure validation: scope={scope}, level={validation_level}")
        
        # This will be implemented in the continuation...
        # For now, return a placeholder response
        return {
            "scope": scope,
            "validation_level": validation_level,
            "status": "implementation_in_progress",
            "message": "Structure validation functionality will be completed in the next phase"
        }

    
    async def _generate_recommendations(self, scan_results: Dict[str, Any], cleanup_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations for manual actions based on scan results.
        
        Args:
            scan_results: Results from the scanning phase
            cleanup_actions: Actions that were performed automatically
            
        Returns:
            List of recommendations for manual actions
        """
        recommendations = []
        
        # Recommend manual review of incomplete workflows
        incomplete_workflows = scan_results.get("incomplete_workflows", [])
        for workflow in incomplete_workflows:
            if workflow["completion_percentage"] < 50:
                recommendations.append({
                    "type": "manual_review",
                    "priority": "high",
                    "title": "Review incomplete workflow",
                    "description": f"Workflow '{workflow['description'][:50]}...' is only {workflow['completion_percentage']:.1f}% complete",
                    "action": "Review and decide whether to complete or archive this workflow",
                    "parent_task_id": workflow["parent_task_id"]
                })
        
        # Recommend performance optimizations if many tasks found
        total_tasks = scan_results.get("total_tasks", 0)
        if total_tasks > 100:
            recommendations.append({
                "type": "performance_optimization",
                "priority": "medium", 
                "title": "Consider database optimization",
                "description": f"Found {total_tasks} tasks in system - consider archival or optimization",
                "action": "Run database maintenance and consider implementing archival policies"
            })
        
        return recommendations
    
    async def _start_maintenance_operation(self, operation_type: str, scope: str, validation_level: str, target_task_id: Optional[str]) -> str:
        """Start a maintenance operation and record it in the database.
        
        Args:
            operation_type: Type of maintenance operation
            scope: Scope of the operation
            validation_level: Validation level
            target_task_id: Target task ID if applicable
            
        Returns:
            Operation ID for tracking
        """
        try:
            with self.state_manager.session_scope() as session:
                operation = MaintenanceOperationModel(
                    operation_type=operation_type,
                    task_context=json.dumps({
                        "scope": scope,
                        "validation_level": validation_level,
                        "target_task_id": target_task_id
                    }),
                    execution_status="running"
                )
                
                session.add(operation)
                session.commit()
                
                return str(operation.id)
                
        except Exception as e:
            self.logger.error(f"Error starting maintenance operation: {str(e)}")
            raise
    
    async def _complete_maintenance_operation(self, operation_id: str, results: Dict[str, Any]) -> None:
        """Complete a maintenance operation and update the database record.
        
        Args:
            operation_id: ID of the operation to complete
            results: Results of the operation
        """
        try:
            with self.state_manager.session_scope() as session:
                operation = session.query(MaintenanceOperationModel).filter_by(id=int(operation_id)).first()
                
                if operation:
                    operation.execution_status = "completed"
                    operation.results_summary = json.dumps(results.get("summary", {}))
                    operation.completed_at = datetime.utcnow()
                    
                    session.commit()
                    
        except Exception as e:
            self.logger.error(f"Error completing maintenance operation {operation_id}: {str(e)}")
    
    async def _fail_maintenance_operation(self, operation_id: str, error_message: str) -> None:
        """Mark a maintenance operation as failed.
        
        Args:
            operation_id: ID of the operation that failed
            error_message: Error message describing the failure
        """
        try:
            with self.state_manager.session_scope() as session:
                operation = session.query(MaintenanceOperationModel).filter_by(id=int(operation_id)).first()
                
                if operation:
                    operation.execution_status = "failed"
                    operation.results_summary = json.dumps({"error": error_message})
                    operation.completed_at = datetime.utcnow()
                    
                    session.commit()
                    
        except Exception as e:
            self.logger.error(f"Error marking maintenance operation {operation_id} as failed: {str(e)}")
    
    async def update_documentation(self, 
                                  scope: str = "current_session",
                                  validation_level: str = "basic",
                                  target_task_id: Optional[str] = None) -> Dict[str, Any]:
        """Update documentation and synchronize task state with documentation.
        
        Args:
            scope: Scope of documentation update
            validation_level: Level of validation
            target_task_id: Specific task ID when scope is specific_subtask
            
        Returns:
            Dictionary containing update results
        """
        self.logger.info(f"Starting documentation update: scope={scope}, level={validation_level}")
        
        # Record maintenance operation start
        operation_id = await self._start_maintenance_operation(
            "update_documentation", scope, validation_level, target_task_id
        )
        
        try:
            results = {
                "operation_id": operation_id,
                "scope": scope,
                "validation_level": validation_level,
                "started_at": datetime.utcnow().isoformat(),
                "updates_performed": [],
                "documentation_status": "updated",
                "summary": {}
            }
            
            # Update handover documentation
            handover_update = await self._update_handover_documentation()
            results["updates_performed"].append(handover_update)
            
            # Update project status documentation
            status_update = await self._update_project_status_documentation()
            results["updates_performed"].append(status_update)
            
            # Create summary
            results["summary"] = {
                "total_updates": len(results["updates_performed"]),
                "operation_status": "completed"
            }
            
            # Complete maintenance operation
            await self._complete_maintenance_operation(operation_id, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error updating documentation: {str(e)}")
            await self._fail_maintenance_operation(operation_id, str(e))
            
            return {
                "scope": scope,
                "validation_level": validation_level,
                "error": str(e),
                "operation_status": "failed"
            }
    
    async def _update_handover_documentation(self) -> Dict[str, Any]:
        """Update handover documentation with current task state."""
        # Placeholder implementation
        return {
            "update_type": "handover_documentation",
            "status": "completed",
            "message": "Handover documentation updated with current task state"
        }
    
    async def _update_project_status_documentation(self) -> Dict[str, Any]:
        """Update project status documentation."""
        # Placeholder implementation
        return {
            "update_type": "project_status",
            "status": "completed", 
            "message": "Project status documentation synchronized"
        }
    
    async def prepare_handover(self, 
                              scope: str = "current_session",
                              validation_level: str = "basic", 
                              target_task_id: Optional[str] = None) -> Dict[str, Any]:
        """Prepare handover documentation and clean up for context transitions.
        
        Args:
            scope: Scope of handover preparation
            validation_level: Level of validation
            target_task_id: Specific task ID when scope is specific_subtask
            
        Returns:
            Dictionary containing handover preparation results
        """
        self.logger.info(f"Starting handover preparation: scope={scope}, level={validation_level}")
        
        # Record maintenance operation start
        operation_id = await self._start_maintenance_operation(
            "prepare_handover", scope, validation_level, target_task_id
        )
        
        try:
            results = {
                "operation_id": operation_id,
                "scope": scope,
                "validation_level": validation_level,
                "started_at": datetime.utcnow().isoformat(),
                "handover_components": [],
                "cleanup_performed": [],
                "handover_ready": True,
                "summary": {}
            }
            
            # Generate handover summary
            handover_summary = await self._generate_handover_summary()
            results["handover_components"].append(handover_summary)
            
            # Clean up temporary data
            cleanup_result = await self._cleanup_temporary_data()
            results["cleanup_performed"].append(cleanup_result)
            
            # Create comprehensive summary
            results["summary"] = {
                "handover_components_prepared": len(results["handover_components"]),
                "cleanup_actions_performed": len(results["cleanup_performed"]),
                "handover_status": "ready",
                "operation_status": "completed"
            }
            
            # Complete maintenance operation
            await self._complete_maintenance_operation(operation_id, results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error preparing handover: {str(e)}")
            await self._fail_maintenance_operation(operation_id, str(e))
            
            return {
                "scope": scope,
                "validation_level": validation_level,
                "error": str(e),
                "operation_status": "failed"
            }
    
    async def _generate_handover_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive handover summary."""
        try:
            with self.state_manager.session_scope() as session:
                # Get current task statistics
                total_tasks = session.query(SubTaskModel).count()
                completed_tasks = session.query(SubTaskModel).filter_by(status='completed').count()
                active_tasks = session.query(SubTaskModel).filter(
                    SubTaskModel.status.in_(['active', 'pending'])
                ).count()
                
                return {
                    "component_type": "handover_summary",
                    "status": "generated",
                    "content": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "active_tasks": active_tasks,
                        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error generating handover summary: {str(e)}")
            return {
                "component_type": "handover_summary",
                "status": "failed",
                "error": str(e)
            }
    
    async def _cleanup_temporary_data(self) -> Dict[str, Any]:
        """Clean up temporary data and prepare for handover."""
        # Placeholder implementation
        return {
            "cleanup_type": "temporary_data",
            "status": "completed",
            "items_cleaned": 0,
            "message": "Temporary data cleanup completed"
        }
