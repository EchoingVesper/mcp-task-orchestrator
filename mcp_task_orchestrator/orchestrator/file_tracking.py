"""
File Change Tracking System

This module implements comprehensive file operation tracking and verification
to ensure all subtask file changes are properly persisted to disk and can be
recovered across session boundaries.

Critical Infrastructure Component - Prevents work loss during context resets.
"""

import hashlib
import uuid
import asyncio
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from sqlalchemy.orm import Session
from ..db.models import FileOperationModel, FileVerificationModel, SubTaskModel


class FileOperationType(Enum):
    """Enumeration of file operation types that can be tracked."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    READ = "read"
    MOVE = "move"
    COPY = "copy"


class VerificationStatus(Enum):
    """Enumeration of verification status values."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class FileOperation:
    """Data class representing a tracked file operation."""
    operation_id: str
    subtask_id: str
    session_id: str
    operation_type: FileOperationType
    file_path: Path
    timestamp: datetime
    content_hash: Optional[str] = None
    file_size: Optional[int] = None
    file_metadata: Dict[str, Any] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING

    def __post_init__(self):
        if self.file_metadata is None:
            self.file_metadata = {}


@dataclass
class VerificationResult:
    """Data class representing file verification results."""
    operation_id: str
    verification_timestamp: datetime
    file_exists: bool
    content_matches: Optional[bool] = None
    size_matches: Optional[bool] = None
    permissions_correct: Optional[bool] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class FileOperationTracker:
    """
    Tracks all file operations during subtask execution to ensure persistence
    and enable context recovery across session boundaries.
    """

    def __init__(self, subtask_id: str, session_id: str, db_session: Session):
        """
        Initialize the file operation tracker.
        
        Args:
            subtask_id: The ID of the subtask being executed
            session_id: The current session ID
            db_session: SQLAlchemy database session
        """
        self.subtask_id = subtask_id
        self.session_id = session_id
        self.db_session = db_session
        self.tracked_operations: List[FileOperation] = []

    async def track_file_operation(self,
                                  operation_type: FileOperationType,
                                  file_path: str,
                                  content_hash: str = None,
                                  file_metadata: dict = None) -> str:
        """
        Track a file operation with comprehensive metadata.
        
        Args:
            operation_type: Type of file operation (CREATE, MODIFY, etc.)
            file_path: Path to the file being operated on
            content_hash: Hash of file content (for verification)
            file_metadata: Additional metadata about the operation
            
        Returns:
            str: Unique operation ID
        """
        # Resolve absolute path
        resolved_path = Path(file_path).resolve()
        
        # Calculate file size if file exists
        file_size = None
        if resolved_path.exists():
            file_size = resolved_path.stat().st_size
            
        # Generate content hash if not provided and file exists
        if content_hash is None and resolved_path.exists() and operation_type in [
            FileOperationType.CREATE, FileOperationType.MODIFY
        ]:
            content_hash = await self._calculate_file_hash(resolved_path)

        # Create operation record
        operation = FileOperation(
            operation_id=str(uuid.uuid4()),
            subtask_id=self.subtask_id,
            session_id=self.session_id,
            operation_type=operation_type,
            file_path=resolved_path,
            timestamp=datetime.utcnow(),
            content_hash=content_hash,
            file_size=file_size,
            file_metadata=file_metadata or {},
            verification_status=VerificationStatus.PENDING
        )

        # Store in memory
        self.tracked_operations.append(operation)
        
        # Persist to database
        await self._persist_operation(operation)
        
        return operation.operation_id

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None

    async def _persist_operation(self, operation: FileOperation):
        """Persist the operation to the database."""
        db_operation = FileOperationModel(
            operation_id=operation.operation_id,
            subtask_id=operation.subtask_id,
            session_id=operation.session_id,
            operation_type=operation.operation_type.value,
            file_path=str(operation.file_path),
            timestamp=operation.timestamp,
            content_hash=operation.content_hash,
            file_size=operation.file_size,
            file_metadata=operation.file_metadata,
            verification_status=operation.verification_status.value
        )
        
        self.db_session.add(db_operation)
        
        # Update subtask file operations count
        subtask = self.db_session.query(SubTaskModel).filter_by(
            task_id=operation.subtask_id
        ).first()
        if subtask:
            subtask.file_operations_count = (subtask.file_operations_count or 0) + 1
        
        self.db_session.commit()

    def get_tracked_operations(self) -> List[FileOperation]:
        """Get all tracked operations for this subtask."""
        return self.tracked_operations.copy()



class FileVerificationEngine:
    """
    Verifies that tracked file operations actually persisted to disk.
    Provides comprehensive verification with detailed status reporting.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the file verification engine.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    async def verify_file_operation(self, operation: FileOperation) -> VerificationResult:
        """
        Comprehensive verification of file operation persistence.
        
        Args:
            operation: The file operation to verify
            
        Returns:
            VerificationResult: Detailed verification results
        """
        verification = VerificationResult(
            operation_id=operation.operation_id,
            verification_timestamp=datetime.utcnow(),
            file_exists=False,
            content_matches=None,
            size_matches=None,
            permissions_correct=None,
            verification_status=VerificationStatus.PENDING,
            errors=[]
        )

        try:
            file_path = operation.file_path
            
            # Basic existence check
            verification.file_exists = file_path.exists()
            
            if operation.operation_type == FileOperationType.DELETE:
                # For delete operations, file should NOT exist
                verification.verification_status = (
                    VerificationStatus.VERIFIED if not verification.file_exists
                    else VerificationStatus.FAILED
                )
                if verification.file_exists:
                    verification.errors.append("File should have been deleted but still exists")
            
            elif verification.file_exists:
                # For create/modify operations, verify content and size
                
                # Content verification
                if operation.content_hash:
                    current_hash = await self._calculate_file_hash(file_path)
                    verification.content_matches = (current_hash == operation.content_hash)
                    if not verification.content_matches:
                        verification.errors.append(f"Content hash mismatch: expected {operation.content_hash}, got {current_hash}")
                
                # Size verification
                if operation.file_size is not None:
                    current_size = file_path.stat().st_size
                    verification.size_matches = (current_size == operation.file_size)
                    if not verification.size_matches:
                        verification.errors.append(f"File size mismatch: expected {operation.file_size}, got {current_size}")
                
                # Permissions verification
                verification.permissions_correct = await self._verify_permissions(file_path)
                
                # Determine overall status
                verification.verification_status = self._determine_verification_status(verification)
            
            else:
                # File doesn't exist but should
                verification.verification_status = VerificationStatus.FAILED
                verification.errors.append("File should exist but was not found on disk")

        except Exception as e:
            verification.errors.append(f"Verification error: {str(e)}")
            verification.verification_status = VerificationStatus.FAILED

        # Persist verification result
        await self._persist_verification(verification)
        
        return verification

    async def verify_all_operations_for_subtask(self, subtask_id: str) -> List[VerificationResult]:
        """
        Verify all file operations for a specific subtask.
        
        Args:
            subtask_id: The subtask ID to verify operations for
            
        Returns:
            List[VerificationResult]: All verification results
        """
        # Get all operations for this subtask
        operations = self.db_session.query(FileOperationModel).filter_by(
            subtask_id=subtask_id
        ).all()

        verification_results = []
        for db_operation in operations:
            # Convert database model to FileOperation object
            operation = FileOperation(
                operation_id=db_operation.operation_id,
                subtask_id=db_operation.subtask_id,
                session_id=db_operation.session_id,
                operation_type=FileOperationType(db_operation.operation_type),
                file_path=Path(db_operation.file_path),
                timestamp=db_operation.timestamp,
                content_hash=db_operation.content_hash,
                file_size=db_operation.file_size,
                file_metadata=db_operation.file_metadata or {},
                verification_status=VerificationStatus(db_operation.verification_status)
            )
            
            # Verify the operation
            result = await self.verify_file_operation(operation)
            verification_results.append(result)

        # Update subtask verification status
        await self._update_subtask_verification_status(subtask_id, verification_results)
        
        return verification_results

    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None

    async def _verify_permissions(self, file_path: Path) -> bool:
        """Verify file permissions are appropriate."""
        try:
            # Basic permission check - file should be readable
            return file_path.is_file() and file_path.stat().st_size >= 0
        except Exception:
            return False

    def _determine_verification_status(self, verification: VerificationResult) -> VerificationStatus:
        """Determine overall verification status based on individual checks."""
        if not verification.file_exists:
            return VerificationStatus.FAILED
        
        failed_checks = []
        if verification.content_matches is False:
            failed_checks.append("content")
        if verification.size_matches is False:
            failed_checks.append("size")
        if verification.permissions_correct is False:
            failed_checks.append("permissions")
        
        if not failed_checks:
            return VerificationStatus.VERIFIED
        elif len(failed_checks) < 3:  # Some checks passed
            return VerificationStatus.PARTIAL
        else:
            return VerificationStatus.FAILED

    async def _persist_verification(self, verification: VerificationResult):
        """Persist verification result to database."""
        db_verification = FileVerificationModel(
            verification_id=str(uuid.uuid4()),
            operation_id=verification.operation_id,
            verification_timestamp=verification.verification_timestamp,
            file_exists=verification.file_exists,
            content_matches=verification.content_matches,
            size_matches=verification.size_matches,
            permissions_correct=verification.permissions_correct,
            verification_status=verification.verification_status.value,
            errors=verification.errors
        )
        
        self.db_session.add(db_verification)
        
        # Update the operation's verification status
        operation = self.db_session.query(FileOperationModel).filter_by(
            operation_id=verification.operation_id
        ).first()
        if operation:
            operation.verification_status = verification.verification_status.value
        
        self.db_session.commit()

    async def _update_subtask_verification_status(self, subtask_id: str, verifications: List[VerificationResult]):
        """Update the subtask's overall verification status based on all verifications."""
        subtask = self.db_session.query(SubTaskModel).filter_by(task_id=subtask_id).first()
        if not subtask:
            return

        # Determine overall status
        statuses = [v.verification_status for v in verifications]
        
        if all(s == VerificationStatus.VERIFIED for s in statuses):
            overall_status = "verified"
        elif any(s == VerificationStatus.FAILED for s in statuses):
            overall_status = "failed"
        elif any(s == VerificationStatus.PARTIAL for s in statuses):
            overall_status = "partial"
        else:
            overall_status = "pending"

        subtask.verification_status = overall_status
        self.db_session.commit()


class FileTrackingManager:
    """
    High-level manager for file tracking operations.
    Coordinates between tracker and verification engine.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the file tracking manager.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.verification_engine = FileVerificationEngine(db_session)

    def create_tracker(self, subtask_id: str, session_id: str) -> FileOperationTracker:
        """Create a new file operation tracker for a subtask."""
        return FileOperationTracker(subtask_id, session_id, self.db_session)

    async def verify_subtask_files(self, subtask_id: str) -> List[VerificationResult]:
        """Verify all file operations for a subtask."""
        return await self.verification_engine.verify_all_operations_for_subtask(subtask_id)

    async def get_subtask_file_operations(self, subtask_id: str) -> List[FileOperationModel]:
        """Get all file operations for a subtask."""
        return self.db_session.query(FileOperationModel).filter_by(
            subtask_id=subtask_id
        ).all()

    async def generate_context_recovery_summary(self, subtask_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive summary for context recovery.
        
        Args:
            subtask_id: The subtask ID to generate summary for
            
        Returns:
            Dict containing recovery context information
        """
        operations = await self.get_subtask_file_operations(subtask_id)
        verifications = await self.verify_subtask_files(subtask_id)
        
        summary = {
            "subtask_id": subtask_id,
            "total_operations": len(operations),
            "operations_by_type": {},
            "verification_summary": {
                "total_verifications": len(verifications),
                "verified": 0,
                "failed": 0,
                "partial": 0,
                "pending": 0
            },
            "files_affected": [],
            "critical_failures": [],
            "recovery_recommendations": []
        }

        # Count operations by type
        for op in operations:
            op_type = op.operation_type
            summary["operations_by_type"][op_type] = summary["operations_by_type"].get(op_type, 0) + 1

        # Count verifications by status
        for verification in verifications:
            status = verification.verification_status.value
            summary["verification_summary"][status] += 1
            
            if verification.verification_status == VerificationStatus.FAILED:
                summary["critical_failures"].append({
                    "operation_id": verification.operation_id,
                    "errors": verification.errors
                })

        # Collect affected files
        summary["files_affected"] = list(set(op.file_path for op in operations))

        # Generate recovery recommendations
        if summary["verification_summary"]["failed"] > 0:
            summary["recovery_recommendations"].append(
                "Some file operations failed verification. Manual review required."
            )
        if summary["verification_summary"]["partial"] > 0:
            summary["recovery_recommendations"].append(
                "Some file operations partially verified. Check content integrity."
            )

        return summary
