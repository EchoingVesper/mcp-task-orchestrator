"""
Core staging manager for temporary file operations in MCP Task Orchestrator.

This module provides the main StagingManager class that orchestrates temporary file
staging, atomic operations, and cleanup mechanisms for interrupted write operations.
"""

import asyncio
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum

import aiofiles
from .utils import (
    StagingUtils, 
    StagingValidator, 
    create_safe_staging_directory,
    get_staging_statistics
)

logger = logging.getLogger("mcp_task_orchestrator.staging.manager")


class StagingStatus(Enum):
    """Status of staging operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CLEANING_UP = "cleaning_up"


class WriteMode(Enum):
    """File writing modes."""
    OVERWRITE = "overwrite"
    APPEND = "append"
    CREATE_NEW = "create_new"
    BATCH = "batch"
    STREAM = "stream"


@dataclass
class StagingOperation:
    """Represents a staging operation."""
    request_id: str
    target_path: Path
    staging_path: Path
    mode: WriteMode
    status: StagingStatus
    created_at: datetime
    updated_at: datetime
    content_size: int
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    estimated_completion: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.estimated_completion:
            data['estimated_completion'] = self.estimated_completion.isoformat()
        data['target_path'] = str(self.target_path)
        data['staging_path'] = str(self.staging_path)
        data['mode'] = self.mode.value
        data['status'] = self.status.value
        return data


class StagingManager:
    """
    Main staging manager for temporary file operations.
    
    Provides atomic file operations, streaming support, and cleanup mechanisms
    for handling interrupted write operations in Claude Desktop.
    """
    
    def __init__(self, base_staging_dir: Optional[Path] = None, 
                 cleanup_interval: int = 3600, max_staging_age_hours: int = 24):
        """
        Initialize staging manager.
        
        Args:
            base_staging_dir: Base directory for staging operations
            cleanup_interval: Cleanup interval in seconds
            max_staging_age_hours: Maximum age for staging files in hours
        """
        self.base_staging_dir = base_staging_dir or Path(".task_orchestrator/staging")
        self.cleanup_interval = cleanup_interval
        self.max_staging_age_hours = max_staging_age_hours
        
        # Active operations tracking
        self.operations: Dict[str, StagingOperation] = {}
        self.operation_locks: Dict[str, asyncio.Lock] = {}
        
        # Manager state
        self._initialized = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Configuration
        self.max_concurrent_operations = 10
        self.max_file_size_mb = 100
        self.chunk_size = 8192  # 8KB chunks for streaming
        
    async def initialize(self) -> bool:
        """
        Initialize the staging manager.
        
        Returns:
            True if initialization successful
        """
        try:
            # Ensure base staging directory exists
            if not await StagingUtils.ensure_directory(self.base_staging_dir):
                logger.error(f"Failed to create staging directory: {self.base_staging_dir}")
                return False
            
            # Recover any existing operations
            await self._recover_operations()
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            self._initialized = True
            logger.info(f"Staging manager initialized with directory: {self.base_staging_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize staging manager: {str(e)}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the staging manager gracefully."""
        logger.info("Shutting down staging manager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Complete or cancel active operations
        await self._finalize_operations()
        
        self._initialized = False
        logger.info("Staging manager shutdown complete")
    
    async def create_staging_operation(self, target_path: Union[str, Path], 
                                     mode: WriteMode = WriteMode.OVERWRITE,
                                     request_id: Optional[str] = None) -> str:
        """
        Create a new staging operation.
        
        Args:
            target_path: Final target path for the file
            mode: Write mode for the operation
            request_id: Optional custom request ID
            
        Returns:
            Request ID for the staging operation
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If manager not initialized or limits exceeded
        """
        if not self._initialized:
            raise RuntimeError("Staging manager not initialized")
        
        if len(self.operations) >= self.max_concurrent_operations:
            raise RuntimeError(f"Maximum concurrent operations ({self.max_concurrent_operations}) exceeded")
        
        # Generate or validate request ID
        if request_id is None:
            request_id = StagingUtils.generate_request_id("staging")
        elif not StagingValidator.validate_request_id(request_id):
            raise ValueError(f"Invalid request ID: {request_id}")
        
        if request_id in self.operations:
            raise ValueError(f"Request ID already exists: {request_id}")
        
        # Validate target path
        target_path = Path(target_path)
        is_valid, error_msg = StagingValidator.validate_file_path(str(target_path))
        if not is_valid:
            raise ValueError(f"Invalid target path: {error_msg}")
        
        # Create staging directory
        staging_dir = await create_safe_staging_directory(self.base_staging_dir, request_id)
        if staging_dir is None:
            raise RuntimeError(f"Failed to create staging directory for request: {request_id}")
        
        # Create staging path
        staging_path = staging_dir / target_path.name
        
        # Create operation
        operation = StagingOperation(
            request_id=request_id,
            target_path=target_path,
            staging_path=staging_path,
            mode=mode,
            status=StagingStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            content_size=0
        )
        
        # Store operation and create lock
        self.operations[request_id] = operation
        self.operation_locks[request_id] = asyncio.Lock()
        
        logger.info(f"Created staging operation {request_id} for {target_path}")
        return request_id
    
    async def write_content(self, request_id: str, content: str, 
                          append: bool = False) -> bool:
        """
        Write content to staging file.
        
        Args:
            request_id: Request identifier
            content: Content to write
            append: Whether to append to existing content
            
        Returns:
            True if write successful
        """
        if request_id not in self.operations:
            raise ValueError(f"Unknown request ID: {request_id}")
        
        async with self.operation_locks[request_id]:
            operation = self.operations[request_id]
            
            try:
                # Validate content size
                is_valid, error_msg = StagingValidator.validate_content_size(
                    content, self.max_file_size_mb
                )
                if not is_valid:
                    await self._mark_operation_failed(operation, error_msg)
                    return False
                
                # Update operation status
                operation.status = StagingStatus.IN_PROGRESS
                operation.updated_at = datetime.utcnow()
                
                # Estimate completion time
                content_bytes = len(content.encode('utf-8'))
                estimated_time = StagingUtils.estimate_operation_time(content_bytes, "write")
                operation.estimated_completion = datetime.utcnow() + timedelta(seconds=estimated_time)
                
                # Write content to staging file
                mode = 'a' if append else 'w'
                async with aiofiles.open(operation.staging_path, mode, encoding='utf-8') as f:
                    await f.write(content)
                
                # Update operation
                operation.content_size += content_bytes
                operation.updated_at = datetime.utcnow()
                
                # Calculate checksum if operation is complete
                if operation.mode != WriteMode.STREAM:
                    operation.checksum = await StagingUtils.calculate_checksum(operation.staging_path)
                
                logger.debug(f"Wrote {len(content)} characters to staging file for {request_id}")
                return True
                
            except Exception as e:
                await self._mark_operation_failed(operation, str(e))
                return False
    
    @asynccontextmanager
    async def stream_writer(self, request_id: str):
        """
        Context manager for streaming content to staging file.
        
        Args:
            request_id: Request identifier
            
        Yields:
            Async file handle for writing
        """
        if request_id not in self.operations:
            raise ValueError(f"Unknown request ID: {request_id}")
        
        async with self.operation_locks[request_id]:
            operation = self.operations[request_id]
            
            try:
                operation.status = StagingStatus.IN_PROGRESS
                operation.mode = WriteMode.STREAM
                operation.updated_at = datetime.utcnow()
                
                async with aiofiles.open(operation.staging_path, 'w', encoding='utf-8') as f:
                    yield f
                
                # Update operation after streaming
                stat_info = operation.staging_path.stat()
                operation.content_size = stat_info.st_size
                operation.checksum = await StagingUtils.calculate_checksum(operation.staging_path)
                operation.updated_at = datetime.utcnow()
                
            except Exception as e:
                await self._mark_operation_failed(operation, str(e))
                raise
    
    async def commit_operation(self, request_id: str, 
                             validate_integrity: bool = True) -> bool:
        """
        Commit staging operation to final target.
        
        Args:
            request_id: Request identifier
            validate_integrity: Whether to validate file integrity
            
        Returns:
            True if commit successful
        """
        if request_id not in self.operations:
            raise ValueError(f"Unknown request ID: {request_id}")
        
        async with self.operation_locks[request_id]:
            operation = self.operations[request_id]
            
            try:
                if operation.status == StagingStatus.FAILED:
                    logger.error(f"Cannot commit failed operation: {request_id}")
                    return False
                
                # Validate integrity if requested
                if validate_integrity and operation.checksum:
                    is_valid = await StagingUtils.validate_file_integrity(
                        operation.staging_path, operation.checksum
                    )
                    if not is_valid:
                        await self._mark_operation_failed(operation, "File integrity validation failed")
                        return False
                
                # Ensure target directory exists
                target_dir = operation.target_path.parent
                if not await StagingUtils.ensure_directory(target_dir):
                    await self._mark_operation_failed(operation, f"Failed to create target directory: {target_dir}")
                    return False
                
                # Atomic move operation
                await self._atomic_move(operation.staging_path, operation.target_path)
                
                # Mark operation complete
                operation.status = StagingStatus.COMPLETED
                operation.updated_at = datetime.utcnow()
                
                logger.info(f"Successfully committed operation {request_id} to {operation.target_path}")
                return True
                
            except Exception as e:
                await self._mark_operation_failed(operation, str(e))
                return False
    
    async def cancel_operation(self, request_id: str) -> bool:
        """
        Cancel a staging operation.
        
        Args:
            request_id: Request identifier
            
        Returns:
            True if cancellation successful
        """
        if request_id not in self.operations:
            return False
        
        async with self.operation_locks[request_id]:
            operation = self.operations[request_id]
            
            if operation.status in [StagingStatus.COMPLETED, StagingStatus.FAILED]:
                return False
            
            operation.status = StagingStatus.CANCELLED
            operation.updated_at = datetime.utcnow()
            
            # Clean up staging files
            await self._cleanup_operation(operation)
            
            logger.info(f"Cancelled operation {request_id}")
            return True
    
    async def get_operation_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of staging operation.
        
        Args:
            request_id: Request identifier
            
        Returns:
            Operation status dictionary or None if not found
        """
        if request_id not in self.operations:
            return None
        
        operation = self.operations[request_id]
        status = operation.to_dict()
        
        # Add progress information
        if operation.estimated_completion:
            now = datetime.utcnow()
            if now < operation.estimated_completion:
                time_remaining = (operation.estimated_completion - now).total_seconds()
                status['time_remaining_seconds'] = time_remaining
            else:
                status['time_remaining_seconds'] = 0
        
        # Add file size information
        if operation.staging_path.exists():
            actual_size = operation.staging_path.stat().st_size
            status['actual_file_size'] = actual_size
            status['size_formatted'] = StagingUtils.format_file_size(actual_size)
        
        return status
    
    async def list_operations(self, status_filter: Optional[StagingStatus] = None) -> List[Dict[str, Any]]:
        """
        List all staging operations.
        
        Args:
            status_filter: Optional status filter
            
        Returns:
            List of operation status dictionaries
        """
        operations = []
        
        for request_id in self.operations:
            operation = self.operations[request_id]
            
            if status_filter is None or operation.status == status_filter:
                status = await self.get_operation_status(request_id)
                if status:
                    operations.append(status)
        
        # Sort by creation time (newest first)
        operations.sort(key=lambda x: x['created_at'], reverse=True)
        return operations
    
    async def cleanup_completed_operations(self, max_age_hours: int = 1) -> int:
        """
        Clean up completed operations older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of operations cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        operations_to_remove = []
        
        for request_id, operation in self.operations.items():
            if (operation.status in [StagingStatus.COMPLETED, StagingStatus.FAILED, StagingStatus.CANCELLED] 
                and operation.updated_at < cutoff_time):
                
                await self._cleanup_operation(operation)
                operations_to_remove.append(request_id)
                cleaned_count += 1
        
        # Remove from tracking
        for request_id in operations_to_remove:
            del self.operations[request_id]
            if request_id in self.operation_locks:
                del self.operation_locks[request_id]
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} completed operations")
        
        return cleaned_count
    
    async def get_staging_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive staging statistics.
        
        Returns:
            Dictionary with staging statistics
        """
        base_stats = get_staging_statistics(self.base_staging_dir)
        
        # Add operation statistics
        operation_stats = {
            'active_operations': len(self.operations),
            'operations_by_status': {},
            'total_content_size': 0,
            'average_operation_age_minutes': 0
        }
        
        if self.operations:
            now = datetime.utcnow()
            total_age_minutes = 0
            
            for operation in self.operations.values():
                status = operation.status.value
                operation_stats['operations_by_status'][status] = (
                    operation_stats['operations_by_status'].get(status, 0) + 1
                )
                operation_stats['total_content_size'] += operation.content_size
                
                age_minutes = (now - operation.created_at).total_seconds() / 60
                total_age_minutes += age_minutes
            
            operation_stats['average_operation_age_minutes'] = total_age_minutes / len(self.operations)
        
        # Combine statistics
        combined_stats = {**base_stats, **operation_stats}
        combined_stats['manager_initialized'] = self._initialized
        combined_stats['base_staging_dir'] = str(self.base_staging_dir)
        
        return combined_stats
    
    # Private methods
    
    async def _recover_operations(self) -> None:
        """Recover operations from previous sessions."""
        try:
            if not self.base_staging_dir.exists():
                return
            
            recovered_count = 0
            
            # Look for staging directories
            for staging_dir in self.base_staging_dir.iterdir():
                if staging_dir.is_dir() and staging_dir.name.startswith("staging_"):
                    try:
                        # Extract request ID from directory name
                        parts = staging_dir.name.split("_")
                        if len(parts) >= 2:
                            request_id = parts[1]
                            
                            # Check if this is a recoverable operation
                            if await self._recover_single_operation(staging_dir, request_id):
                                recovered_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to recover operation from {staging_dir}: {str(e)}")
            
            if recovered_count > 0:
                logger.info(f"Recovered {recovered_count} staging operations")
                
        except Exception as e:
            logger.error(f"Error during operation recovery: {str(e)}")
    
    async def _recover_single_operation(self, staging_dir: Path, request_id: str) -> bool:
        """Recover a single operation from staging directory."""
        try:
            # Find staging files
            staging_files = list(staging_dir.glob("*"))
            if not staging_files:
                # Empty directory, clean it up
                shutil.rmtree(staging_dir, ignore_errors=True)
                return False
            
            # For now, mark recovered operations as failed for manual review
            # In a more sophisticated implementation, you could save operation metadata
            for staging_file in staging_files:
                if staging_file.is_file():
                    operation = StagingOperation(
                        request_id=request_id,
                        target_path=Path("unknown"),  # Would need to be saved in metadata
                        staging_path=staging_file,
                        mode=WriteMode.OVERWRITE,
                        status=StagingStatus.FAILED,
                        created_at=datetime.fromtimestamp(staging_file.stat().st_ctime),
                        updated_at=datetime.utcnow(),
                        content_size=staging_file.stat().st_size,
                        error_message="Recovered from previous session - manual review required"
                    )
                    
                    self.operations[request_id] = operation
                    self.operation_locks[request_id] = asyncio.Lock()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error recovering operation {request_id}: {str(e)}")
            return False
    
    async def _atomic_move(self, source: Path, target: Path) -> None:
        """Perform atomic move operation."""
        try:
            # Check if source and target are on same filesystem
            if StagingUtils.is_same_filesystem(source.parent, target.parent):
                # Same filesystem - can use atomic move
                source.rename(target)
                logger.debug(f"Atomic move: {source} -> {target}")
            else:
                # Different filesystem - need to copy then delete
                logger.debug(f"Cross-filesystem move: {source} -> {target}")
                
                # Copy with retry logic
                await StagingUtils.safe_file_operation(
                    shutil.copy2, str(source), str(target)
                )
                
                # Verify copy succeeded
                if target.exists() and target.stat().st_size == source.stat().st_size:
                    source.unlink()
                else:
                    raise RuntimeError("File copy verification failed")
                    
        except Exception as e:
            logger.error(f"Atomic move failed: {source} -> {target}: {str(e)}")
            raise
    
    async def _mark_operation_failed(self, operation: StagingOperation, error_message: str) -> None:
        """Mark operation as failed with error message."""
        operation.status = StagingStatus.FAILED
        operation.error_message = error_message
        operation.updated_at = datetime.utcnow()
        operation.retry_count += 1
        
        logger.error(f"Operation {operation.request_id} failed: {error_message}")
    
    async def _cleanup_operation(self, operation: StagingOperation) -> None:
        """Clean up staging files for operation."""
        try:
            if operation.staging_path.exists():
                # Remove staging file
                operation.staging_path.unlink()
            
            # Remove staging directory if empty
            staging_dir = operation.staging_path.parent
            if staging_dir.exists() and not any(staging_dir.iterdir()):
                staging_dir.rmdir()
                
        except Exception as e:
            logger.warning(f"Error cleaning up operation {operation.request_id}: {str(e)}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        logger.info("Starting staging cleanup loop")
        
        while not self._shutdown_event.is_set():
            try:
                await self.cleanup_completed_operations(self.max_staging_age_hours)
                
                # Wait for next cleanup cycle
                await asyncio.wait_for(
                    self._shutdown_event.wait(), 
                    timeout=self.cleanup_interval
                )
                
            except asyncio.TimeoutError:
                # Normal timeout - continue cleanup cycle
                continue
            except Exception as e:
                logger.error(f"Error in cleanup loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a bit before retrying
    
    async def _finalize_operations(self) -> None:
        """Finalize all active operations during shutdown."""
        logger.info("Finalizing active operations...")
        
        for request_id, operation in list(self.operations.items()):
            if operation.status == StagingStatus.IN_PROGRESS:
                operation.status = StagingStatus.CANCELLED
                operation.error_message = "Operation cancelled during shutdown"
                operation.updated_at = datetime.utcnow()
            
            # Clean up staging files
            await self._cleanup_operation(operation)


# Singleton instance for global use
_staging_manager: Optional[StagingManager] = None


async def get_staging_manager() -> StagingManager:
    """Get the global staging manager instance."""
    global _staging_manager
    
    if _staging_manager is None:
        _staging_manager = StagingManager()
        await _staging_manager.initialize()
    
    return _staging_manager


async def shutdown_staging_manager() -> None:
    """Shutdown the global staging manager."""
    global _staging_manager
    
    if _staging_manager is not None:
        await _staging_manager.shutdown()
        _staging_manager = None
