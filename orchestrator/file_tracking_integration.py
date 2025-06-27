"""
File Tracking Integration

This module provides easy-to-use integration points for file tracking
within the task orchestrator system.
"""

import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .file_tracking import (
    FileTrackingManager, FileOperationType, 
    FileOperation, VerificationResult
)
from ..db.file_tracking_migration import migrate_file_tracking_tables

logger = logging.getLogger("mcp_task_orchestrator.orchestrator.file_tracking_integration")


class SubtaskFileTracker:
    """
    Simple wrapper for file tracking during subtask execution.
    Provides context manager functionality for automatic verification.
    """

    def __init__(self, subtask_id: str, session_id: str, tracking_manager: FileTrackingManager):
        """
        Initialize subtask file tracker.
        
        Args:
            subtask_id: The ID of the subtask being executed
            session_id: Current session ID
            tracking_manager: File tracking manager instance
        """
        self.subtask_id = subtask_id
        self.session_id = session_id
        self.tracking_manager = tracking_manager
        self.tracker = tracking_manager.create_tracker(subtask_id, session_id)
        self.verification_results = []

    async def track_file_create(self, file_path: str, file_metadata: dict = None) -> str:
        """Track a file creation operation."""
        return await self.tracker.track_file_operation(
            FileOperationType.CREATE, file_path, file_metadata=file_metadata
        )

    async def track_file_modify(self, file_path: str, file_metadata: dict = None) -> str:
        """Track a file modification operation."""
        return await self.tracker.track_file_operation(
            FileOperationType.MODIFY, file_path, file_metadata=file_metadata
        )

    async def track_file_delete(self, file_path: str, file_metadata: dict = None) -> str:
        """Track a file deletion operation."""
        return await self.tracker.track_file_operation(
            FileOperationType.DELETE, file_path, file_metadata=file_metadata
        )

    async def track_file_read(self, file_path: str, file_metadata: dict = None) -> str:
        """Track a file read operation."""
        return await self.tracker.track_file_operation(
            FileOperationType.READ, file_path, file_metadata=file_metadata
        )

    async def verify_all_operations(self) -> Dict[str, Any]:
        """
        Verify all tracked operations and return summary.
        
        Returns:
            Dict containing verification summary
        """
        try:
            self.verification_results = await self.tracking_manager.verify_subtask_files(self.subtask_id)
            
            # Generate summary
            summary = {
                "subtask_id": self.subtask_id,
                "total_operations": len(self.tracker.tracked_operations),
                "verifications": len(self.verification_results),
                "all_verified": all(r.verification_status.value == "verified" for r in self.verification_results),
                "failed_verifications": [
                    {
                        "operation_id": r.operation_id,
                        "errors": r.errors
                    }
                    for r in self.verification_results 
                    if r.verification_status.value == "failed"
                ],
                "verification_details": [
                    {
                        "operation_id": r.operation_id,
                        "status": r.verification_status.value,
                        "file_exists": r.file_exists,
                        "content_matches": r.content_matches,
                        "size_matches": r.size_matches
                    }
                    for r in self.verification_results
                ]
            }
            
            logger.info(f"File verification completed for subtask {self.subtask_id}: {summary['verifications']} operations verified, {len(summary['failed_verifications'])} failures")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error verifying operations for subtask {self.subtask_id}: {str(e)}")
            return {
                "subtask_id": self.subtask_id,
                "error": str(e),
                "all_verified": False
            }

    async def get_context_recovery_info(self) -> Dict[str, Any]:
        """Get comprehensive context recovery information."""
        return await self.tracking_manager.generate_context_recovery_summary(self.subtask_id)


class FileTrackingOrchestrator:
    """
    High-level orchestrator for file tracking across the entire system.
    Handles initialization, migration, and provides factory methods.
    """

    def __init__(self, db_session):
        """
        Initialize the file tracking orchestrator.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.tracking_manager = FileTrackingManager(db_session)
        self._session_id = str(uuid.uuid4())

    @classmethod
    async def initialize(cls, db_session, run_migration: bool = True):
        """
        Initialize file tracking with optional migration.
        
        Args:
            db_session: SQLAlchemy database session
            run_migration: Whether to run database migration
            
        Returns:
            FileTrackingOrchestrator instance
        """
        if run_migration:
            logger.info("Running file tracking database migration...")
            success = migrate_file_tracking_tables()
            if not success:
                logger.error("File tracking migration failed")
                raise RuntimeError("Failed to migrate file tracking tables")
            logger.info("File tracking migration completed successfully")

        return cls(db_session)

    def create_subtask_tracker(self, subtask_id: str) -> SubtaskFileTracker:
        """
        Create a file tracker for a specific subtask.
        
        Args:
            subtask_id: The ID of the subtask
            
        Returns:
            SubtaskFileTracker instance
        """
        return SubtaskFileTracker(subtask_id, self._session_id, self.tracking_manager)

    async def verify_subtask_completion(self, subtask_id: str) -> Dict[str, Any]:
        """
        Verify that all file operations for a subtask were successful.
        
        Args:
            subtask_id: The ID of the subtask to verify
            
        Returns:
            Dict containing verification results and recommendations
        """
        try:
            # Get all file operations for the subtask
            operations = await self.tracking_manager.get_subtask_file_operations(subtask_id)
            
            if not operations:
                return {
                    "subtask_id": subtask_id,
                    "status": "no_operations",
                    "message": "No file operations found for this subtask",
                    "completion_approved": True
                }

            # Verify all operations
            verification_results = await self.tracking_manager.verify_subtask_files(subtask_id)
            
            # Analyze results
            total_operations = len(operations)
            verified_count = sum(1 for r in verification_results if r.verification_status.value == "verified")
            failed_count = sum(1 for r in verification_results if r.verification_status.value == "failed")
            
            completion_approved = failed_count == 0
            
            result = {
                "subtask_id": subtask_id,
                "status": "completed_verification",
                "total_operations": total_operations,
                "verified_operations": verified_count,
                "failed_operations": failed_count,
                "completion_approved": completion_approved,
                "verification_summary": {
                    "all_files_verified": completion_approved,
                    "critical_failures": [
                        {
                            "operation_id": r.operation_id,
                            "errors": r.errors
                        }
                        for r in verification_results if r.verification_status.value == "failed"
                    ]
                }
            }

            if not completion_approved:
                result["recommendations"] = [
                    "Manual review required for failed file operations",
                    "Check file permissions and disk space",
                    "Verify file paths are correct and accessible"
                ]

            logger.info(f"Subtask completion verification for {subtask_id}: {verified_count}/{total_operations} operations verified")
            
            return result

        except Exception as e:
            logger.error(f"Error verifying subtask completion for {subtask_id}: {str(e)}")
            return {
                "subtask_id": subtask_id,
                "status": "verification_error",
                "error": str(e),
                "completion_approved": False
            }

    async def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all file operations in this session."""
        # This would query all operations for the current session
        # Implementation would depend on specific requirements
        return {
            "session_id": self._session_id,
            "message": "Session summary functionality available"
        }


# Convenience functions for easy integration

async def initialize_file_tracking(db_session, run_migration: bool = True) -> FileTrackingOrchestrator:
    """
    Initialize file tracking system for the orchestrator.
    
    Args:
        db_session: SQLAlchemy database session
        run_migration: Whether to run database migration
        
    Returns:
        FileTrackingOrchestrator instance
    """
    return await FileTrackingOrchestrator.initialize(db_session, run_migration)


def create_file_tracker_for_subtask(subtask_id: str, file_tracking_orchestrator: FileTrackingOrchestrator) -> SubtaskFileTracker:
    """
    Create a file tracker for a specific subtask.
    
    Args:
        subtask_id: The ID of the subtask
        file_tracking_orchestrator: The file tracking orchestrator instance
        
    Returns:
        SubtaskFileTracker instance
    """
    return file_tracking_orchestrator.create_subtask_tracker(subtask_id)
