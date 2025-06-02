"""
Temporary File Staging System for MCP Task Orchestrator

This module implements the temporary file staging infrastructure with atomic operations,
cleanup mechanisms, and support for both streaming and batch file operations.

Based on the architectural design in artifact_51d1fee6.
"""

import os
import uuid
import json
import asyncio
import hashlib
import shutil
import aiofiles
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, AsyncContextManager
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from enum import Enum

logger = logging.getLogger("mcp_task_orchestrator.staging")


class StagingOperation(Enum):
    """Types of staging operations."""
    STREAMING = "streaming"
    BATCH = "batch"
    RESUME = "resume"


class StagingStatus(Enum):
    """Status of staging operations."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANING_UP = "cleaning_up"


@dataclass
class StagingContext:
    """Context for staging operations with comprehensive metadata."""
    
    request_id: str
    staging_path: Path
    operation_type: StagingOperation
    status: StagingStatus
    created_at: datetime
    
    # File paths
    partial_file: Path
    metadata_file: Path
    checkpoints_dir: Path
    final_file: Optional[Path] = None
    
    # Operation metadata
    estimated_size: int = 0
    bytes_written: int = 0
    chunks_written: int = 0
    checkpoints_created: int = 0
    
    # Integrity tracking
    current_checksum: str = ""
    expected_checksum: str = ""
    
    # Timing information
    last_activity: datetime = None
    completion_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'request_id': self.request_id,
            'staging_path': str(self.staging_path),
            'operation_type': self.operation_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'partial_file': str(self.partial_file),
            'metadata_file': str(self.metadata_file),
            'checkpoints_dir': str(self.checkpoints_dir),
            'final_file': str(self.final_file) if self.final_file else None,
            'estimated_size': self.estimated_size,
            'bytes_written': self.bytes_written,
            'chunks_written': self.chunks_written,
            'checkpoints_created': self.checkpoints_created,
            'current_checksum': self.current_checksum,
            'expected_checksum': self.expected_checksum,
            'last_activity': self.last_activity.isoformat(),
            'completion_time': self.completion_time.isoformat() if self.completion_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StagingContext':
        """Create from dictionary."""
        return cls(
            request_id=data['request_id'],
            staging_path=Path(data['staging_path']),
            operation_type=StagingOperation(data['operation_type']),
            status=StagingStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            partial_file=Path(data['partial_file']),
            metadata_file=Path(data['metadata_file']),
            checkpoints_dir=Path(data['checkpoints_dir']),
            final_file=Path(data['final_file']) if data.get('final_file') else None,
            estimated_size=data.get('estimated_size', 0),
            bytes_written=data.get('bytes_written', 0),
            chunks_written=data.get('chunks_written', 0),
            checkpoints_created=data.get('checkpoints_created', 0),
            current_checksum=data.get('current_checksum', ''),
            expected_checksum=data.get('expected_checksum', ''),
            last_activity=datetime.fromisoformat(data['last_activity']),
            completion_time=datetime.fromisoformat(data['completion_time']) if data.get('completion_time') else None
        )


@dataclass
class StreamingChunk:
    """Represents a chunk of streaming data."""
    
    request_id: str
    chunk_id: str
    position: int
    data: str
    timestamp: datetime
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate SHA-256 checksum of chunk data."""
        return hashlib.sha256(self.data.encode('utf-8')).hexdigest()
    
    def size_bytes(self) -> int:
        """Get size of chunk in bytes."""
        return len(self.data.encode('utf-8'))


class StagingError(Exception):
    """Base exception for staging operations."""
    pass


class StagingIntegrityError(StagingError):
    """Exception for integrity validation failures."""
    pass


class StagingCleanupError(StagingError):
    """Exception for cleanup operation failures."""
    pass


class AtomicMoveError(StagingError):
    """Exception for atomic move operation failures."""
    pass


class StagingManager:
    """
    Manages temporary file staging with atomic operations and cleanup.
    
    This class provides the core infrastructure for temporary file operations
    with support for streaming writes, atomic moves, and comprehensive cleanup.
    """
    
    def __init__(self, base_staging_dir: Path, cleanup_interval_hours: int = 24):
        """
        Initialize the staging manager.
        
        Args:
            base_staging_dir: Base directory for staging operations
            cleanup_interval_hours: Hours between automatic cleanup runs
        """
        self.staging_dir = base_staging_dir / "streaming"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        
        self.cleanup_interval = timedelta(hours=cleanup_interval_hours)
        self.active_contexts: Dict[str, StagingContext] = {}
        
        # Create lock for thread safety
        self._lock = asyncio.Lock()
        
        logger.info(f"Initialized StagingManager with directory: {self.staging_dir}")
    
    async def create_staging(self, 
                           request_id: str, 
                           operation_type: StagingOperation = StagingOperation.BATCH,
                           estimated_size: int = 0) -> StagingContext:
        """
        Create isolated staging environment for request.
        
        Args:
            request_id: Unique identifier for the request
            operation_type: Type of staging operation
            estimated_size: Estimated size of final content
            
        Returns:
            StagingContext with initialized staging environment
        """
        async with self._lock:
            # Generate unique staging directory
            session_id = uuid.uuid4().hex[:8]
            staging_path = self.staging_dir / f"{request_id}_{session_id}"
            
            # Ensure staging path doesn't exist (should be unique)
            if staging_path.exists():
                raise StagingError(f"Staging path already exists: {staging_path}")
            
            # Create staging directory structure
            staging_path.mkdir(parents=True, exist_ok=False)
            checkpoints_dir = staging_path / "checkpoints"
            checkpoints_dir.mkdir(exist_ok=False)
            
            # Create staging context
            context = StagingContext(
                request_id=request_id,
                staging_path=staging_path,
                operation_type=operation_type,
                status=StagingStatus.INITIALIZING,
                created_at=datetime.utcnow(),
                partial_file=staging_path / "response.partial",
                metadata_file=staging_path / "metadata.json",
                checkpoints_dir=checkpoints_dir,
                estimated_size=estimated_size
            )
            
            # Save initial metadata
            await self._save_metadata(context)
            
            # Update context status
            context.status = StagingStatus.ACTIVE
            context.last_activity = datetime.utcnow()
            await self._save_metadata(context)
            
            # Register active context
            self.active_contexts[request_id] = context
            
            logger.info(f"Created staging environment for request {request_id} at {staging_path}")
            return context
    
    async def append_chunk(self, request_id: str, chunk: StreamingChunk) -> None:
        """
        Append chunk to staging file with atomic operations.
        
        Args:
            request_id: Request identifier
            chunk: StreamingChunk to append
        """
        context = await self._get_active_context(request_id)
        
        try:
            # Validate chunk integrity
            expected_checksum = chunk._calculate_checksum()
            if chunk.checksum != expected_checksum:
                raise StagingIntegrityError(f"Chunk checksum mismatch for {chunk.chunk_id}")
            
            # Atomic append operation
            async with aiofiles.open(context.partial_file, 'ab') as f:
                data_bytes = chunk.data.encode('utf-8')
                await f.write(data_bytes)
                await f.fsync()  # Force to disk for durability
            
            # Update context metrics
            context.bytes_written += chunk.size_bytes()
            context.chunks_written += 1
            context.last_activity = datetime.utcnow()
            
            # Update running checksum
            context.current_checksum = await self._calculate_file_checksum(context.partial_file)
            
            # Save updated metadata
            await self._save_metadata(context)
            
            logger.debug(f"Appended chunk {chunk.chunk_id} to {request_id} "
                        f"({chunk.size_bytes()} bytes, total: {context.bytes_written})")
            
        except Exception as e:
            logger.error(f"Failed to append chunk {chunk.chunk_id} to {request_id}: {str(e)}")
            context.status = StagingStatus.FAILED
            await self._save_metadata(context)
            raise StagingError(f"Chunk append failed: {str(e)}") from e
    
    async def write_batch_content(self, request_id: str, content: str) -> None:
        """
        Write complete content in batch mode.
        
        Args:
            request_id: Request identifier
            content: Complete content to write
        """
        context = await self._get_active_context(request_id)
        
        try:
            # Write content atomically
            async with aiofiles.open(context.partial_file, 'w', encoding='utf-8') as f:
                await f.write(content)
                await f.fsync()
            
            # Update context metrics
            content_bytes = len(content.encode('utf-8'))
            context.bytes_written = content_bytes
            context.chunks_written = 1
            context.last_activity = datetime.utcnow()
            
            # Calculate checksum
            context.current_checksum = await self._calculate_file_checksum(context.partial_file)
            
            # Save updated metadata
            await self._save_metadata(context)
            
            logger.info(f"Wrote batch content to {request_id} ({content_bytes} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to write batch content to {request_id}: {str(e)}")
            context.status = StagingStatus.FAILED
            await self._save_metadata(context)
            raise StagingError(f"Batch write failed: {str(e)}") from e
    
    async def finalize_staging(self, request_id: str) -> Path:
        """
        Finalize staging content and prepare for atomic move.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Path to finalized content file
        """
        context = await self._get_active_context(request_id)
        
        try:
            context.status = StagingStatus.FINALIZING
            await self._save_metadata(context)
            
            # Validate complete file integrity
            await self._validate_complete_file(context)
            
            # Create final content file
            final_file = context.staging_path / "response.final"
            
            # Copy with integrity verification
            async with aiofiles.open(context.partial_file, 'r', encoding='utf-8') as src:
                content = await src.read()
                
            async with aiofiles.open(final_file, 'w', encoding='utf-8') as dst:
                await dst.write(content)
                await dst.fsync()
            
            # Verify final file integrity
            final_checksum = await self._calculate_file_checksum(final_file)
            if final_checksum != context.current_checksum:
                raise StagingIntegrityError("Final file checksum mismatch")
            
            # Update context
            context.final_file = final_file
            context.status = StagingStatus.COMPLETED
            context.completion_time = datetime.utcnow()
            await self._save_metadata(context)
            
            logger.info(f"Finalized staging for {request_id}: {final_file}")
            return final_file
            
        except Exception as e:
            logger.error(f"Failed to finalize staging for {request_id}: {str(e)}")
            context.status = StagingStatus.FAILED
            await self._save_metadata(context)
            raise StagingError(f"Staging finalization failed: {str(e)}") from e
    
    async def atomic_move_to_production(self, staging_file: Path, production_path: Path) -> None:
        """
        Atomic move from staging to production location.
        
        Args:
            staging_file: Source file in staging
            production_path: Target production path
        """
        try:
            # Ensure production directory exists
            production_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if same filesystem for true atomic move
            staging_stat = staging_file.stat()
            production_stat = production_path.parent.stat()
            
            if staging_stat.st_dev == production_stat.st_dev:
                # Same filesystem - true atomic move
                staging_file.rename(production_path)
                logger.info(f"Atomic move (same filesystem): {staging_file} -> {production_path}")
            else:
                # Different filesystem - copy, verify, then delete
                await self._cross_filesystem_atomic_move(staging_file, production_path)
                logger.info(f"Atomic move (cross filesystem): {staging_file} -> {production_path}")
                
        except Exception as e:
            logger.error(f"Atomic move failed: {staging_file} -> {production_path}: {str(e)}")
            raise AtomicMoveError(f"Atomic move failed: {str(e)}") from e
    
    async def cleanup_staging(self, request_id: str) -> None:
        """
        Clean up staging area for completed request.
        
        Args:
            request_id: Request identifier to clean up
        """
        try:
            # Remove from active contexts
            context = self.active_contexts.pop(request_id, None)
            
            if context and context.staging_path.exists():
                # Remove staging directory and all contents
                shutil.rmtree(context.staging_path)
                logger.info(f"Cleaned up staging for {request_id}: {context.staging_path}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup staging for {request_id}: {str(e)}")
            raise StagingCleanupError(f"Staging cleanup failed: {str(e)}") from e
    
    async def cleanup_stale_staging(self, max_age_hours: int = 24) -> int:
        """
        Clean up stale staging directories.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of directories cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        try:
            if not self.staging_dir.exists():
                return 0
            
            for staging_dir in self.staging_dir.iterdir():
                if not staging_dir.is_dir():
                    continue
                
                # Check metadata file for last activity
                metadata_file = staging_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        async with aiofiles.open(metadata_file, 'r') as f:
                            metadata = json.loads(await f.read())
                        
                        last_activity = datetime.fromisoformat(metadata['last_activity'])
                        
                        if last_activity < cutoff_time:
                            # Remove stale staging directory
                            shutil.rmtree(staging_dir)
                            cleaned_count += 1
                            logger.info(f"Cleaned up stale staging: {staging_dir}")
                            
                    except Exception as e:
                        logger.warning(f"Error checking staging dir {staging_dir}: {str(e)}")
                else:
                    # No metadata file - check directory modification time
                    dir_stat = staging_dir.stat()
                    dir_time = datetime.fromtimestamp(dir_stat.st_mtime)
                    
                    if dir_time < cutoff_time:
                        shutil.rmtree(staging_dir)
                        cleaned_count += 1
                        logger.info(f"Cleaned up orphaned staging: {staging_dir}")
            
            logger.info(f"Cleaned up {cleaned_count} stale staging directories")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during stale staging cleanup: {str(e)}")
            raise StagingCleanupError(f"Stale cleanup failed: {str(e)}") from e
    
    async def get_staging_info(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get staging information for request.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Staging information dictionary or None if not found
        """
        context = self.active_contexts.get(request_id)
        if context:
            return context.to_dict()
        
        # Check for persisted staging
        for staging_dir in self.staging_dir.iterdir():
            if staging_dir.is_dir() and staging_dir.name.startswith(request_id):
                metadata_file = staging_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        async with aiofiles.open(metadata_file, 'r') as f:
                            return json.loads(await f.read())
                    except Exception as e:
                        logger.warning(f"Error reading metadata for {request_id}: {str(e)}")
        
        return None
    
    async def list_active_staging(self) -> List[Dict[str, Any]]:
        """
        List all active staging operations.
        
        Returns:
            List of staging context dictionaries
        """
        active_staging = []
        
        # Add active contexts
        for context in self.active_contexts.values():
            active_staging.append(context.to_dict())
        
        # Add persisted staging operations
        if self.staging_dir.exists():
            for staging_dir in self.staging_dir.iterdir():
                if staging_dir.is_dir():
                    metadata_file = staging_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            async with aiofiles.open(metadata_file, 'r') as f:
                                metadata = json.loads(await f.read())
                            
                            # Check if not already in active contexts
                            request_id = metadata['request_id']
                            if request_id not in self.active_contexts:
                                active_staging.append(metadata)
                                
                        except Exception as e:
                            logger.warning(f"Error reading staging metadata: {str(e)}")
        
        return active_staging
    
    @asynccontextmanager
    async def staging_operation(self, 
                               request_id: str, 
                               operation_type: StagingOperation = StagingOperation.BATCH,
                               estimated_size: int = 0,
                               auto_cleanup: bool = True) -> AsyncContextManager[StagingContext]:
        """
        Context manager for staging operations with automatic cleanup.
        
        Args:
            request_id: Request identifier
            operation_type: Type of staging operation
            estimated_size: Estimated content size
            auto_cleanup: Whether to automatically cleanup on exit
            
        Yields:
            StagingContext for the operation
        """
        context = await self.create_staging(request_id, operation_type, estimated_size)
        
        try:
            yield context
        except Exception as e:
            logger.error(f"Error in staging operation {request_id}: {str(e)}")
            context.status = StagingStatus.FAILED
            await self._save_metadata(context)
            raise
        finally:
            if auto_cleanup:
                try:
                    await self.cleanup_staging(request_id)
                except Exception as e:
                    logger.error(f"Error cleaning up staging {request_id}: {str(e)}")
    
    # Private helper methods
    
    async def _get_active_context(self, request_id: str) -> StagingContext:
        """Get active staging context or raise error."""
        context = self.active_contexts.get(request_id)
        if not context:
            raise StagingError(f"No active staging context for {request_id}")
        return context
    
    async def _save_metadata(self, context: StagingContext) -> None:
        """Save staging context metadata to file."""
        try:
            metadata = context.to_dict()
            async with aiofiles.open(context.metadata_file, 'w') as f:
                await f.write(json.dumps(metadata, indent=2))
        except Exception as e:
            logger.error(f"Failed to save metadata for {context.request_id}: {str(e)}")
            raise StagingError(f"Metadata save failed: {str(e)}") from e
    
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        hash_sha256 = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _validate_complete_file(self, context: StagingContext) -> None:
        """Validate complete file integrity."""
        if not context.partial_file.exists():
            raise StagingIntegrityError(f"Partial file missing: {context.partial_file}")
        
        # Check file size
        file_size = context.partial_file.stat().st_size
        if context.bytes_written > 0 and file_size != context.bytes_written:
            raise StagingIntegrityError(
                f"File size mismatch: expected {context.bytes_written}, got {file_size}"
            )
        
        # Verify checksum
        current_checksum = await self._calculate_file_checksum(context.partial_file)
        if context.current_checksum and current_checksum != context.current_checksum:
            raise StagingIntegrityError("File checksum validation failed")
    
    async def _cross_filesystem_atomic_move(self, source: Path, dest: Path) -> None:
        """Atomic move across different filesystems."""
        # Create temporary file in destination directory
        temp_dest = dest.parent / f".tmp_{dest.name}_{uuid.uuid4().hex[:8]}"
        
        try:
            # Copy source to temporary destination
            async with aiofiles.open(source, 'rb') as src_f:
                async with aiofiles.open(temp_dest, 'wb') as dst_f:
                    while chunk := await src_f.read(64 * 1024):  # 64KB chunks
                        await dst_f.write(chunk)
                    await dst_f.fsync()
            
            # Verify copy integrity
            source_checksum = await self._calculate_file_checksum(source)
            dest_checksum = await self._calculate_file_checksum(temp_dest)
            
            if source_checksum != dest_checksum:
                raise AtomicMoveError("Cross-filesystem copy integrity check failed")
            
            # Atomic rename in destination filesystem
            temp_dest.rename(dest)
            
            # Remove source file
            source.unlink()
            
        except Exception as e:
            # Clean up temporary file on failure
            if temp_dest.exists():
                try:
                    temp_dest.unlink()
                except Exception:
                    pass
            raise AtomicMoveError(f"Cross-filesystem atomic move failed: {str(e)}") from e


# Factory function for easy integration
def create_staging_manager(base_dir: Union[str, Path], 
                          cleanup_interval_hours: int = 24) -> StagingManager:
    """
    Factory function to create a StagingManager instance.
    
    Args:
        base_dir: Base directory for staging operations
        cleanup_interval_hours: Hours between cleanup runs
        
    Returns:
        Configured StagingManager instance
    """
    base_path = Path(base_dir) if isinstance(base_dir, str) else base_dir
    staging_dir = base_path / ".task_orchestrator"
    
    return StagingManager(staging_dir, cleanup_interval_hours)
