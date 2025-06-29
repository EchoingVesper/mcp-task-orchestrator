"""
File writer utilities with staging support for MCP Task Orchestrator.

This module provides high-level file writing utilities that use the staging system
to handle interruptions and provide atomic file operations.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

import aiofiles
from .manager import StagingManager, WriteMode, get_staging_manager
from .utils import StagingUtils, StagingValidator

logger = logging.getLogger("mcp_task_orchestrator.staging.writers")


class ChunkingStrategy(Enum):
    """Strategies for chunking content during writes."""
    FIXED_SIZE = "fixed_size"
    LINE_BASED = "line_based"
    PARAGRAPH_BASED = "paragraph_based"
    ADAPTIVE = "adaptive"


@dataclass
class WriteConfig:
    """Configuration for file write operations."""
    chunk_size: int = 8192  # 8KB default
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.FIXED_SIZE
    enable_compression: bool = False
    validate_integrity: bool = True
    auto_commit: bool = True
    backup_original: bool = False
    max_retries: int = 3
    retry_delay: float = 0.5


class StreamingFileWriter:
    """
    Streaming file writer with staging support.
    
    Provides atomic file writing with interruption recovery for large content.
    """
    
    def __init__(self, target_path: Union[str, Path], 
                 config: Optional[WriteConfig] = None,
                 staging_manager: Optional[StagingManager] = None):
        """
        Initialize streaming file writer.
        
        Args:
            target_path: Final target path for the file
            config: Write configuration
            staging_manager: Optional staging manager instance
        """
        self.target_path = Path(target_path)
        self.config = config or WriteConfig()
        self.staging_manager = staging_manager
        self.request_id: Optional[str] = None
        self._initialized = False
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is None:
            # Normal completion - commit if auto_commit enabled
            if self.config.auto_commit:
                await self.commit()
        else:
            # Exception occurred - cancel operation
            await self.cancel()
        
        await self.cleanup()
    
    async def initialize(self) -> bool:
        """
        Initialize the writer and create staging operation.
        
        Returns:
            True if initialization successful
        """
        try:
            # Get staging manager
            if self.staging_manager is None:
                self.staging_manager = await get_staging_manager()
            
            # Validate target path
            is_valid, error_msg = StagingValidator.validate_file_path(str(self.target_path))
            if not is_valid:
                raise ValueError(f"Invalid target path: {error_msg}")
            
            # Backup original file if requested
            if self.config.backup_original and self.target_path.exists():
                await self._backup_original()
            
            # Create staging operation
            self.request_id = await self.staging_manager.create_staging_operation(
                target_path=self.target_path,
                mode=WriteMode.STREAM
            )
            
            self._initialized = True
            logger.info(f"Initialized streaming writer for {self.target_path} (request: {self.request_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize streaming writer: {str(e)}")
            return False
    
    async def write(self, content: str) -> bool:
        """
        Write content to staging file.
        
        Args:
            content: Content to write
            
        Returns:
            True if write successful
        """
        if not self._initialized or not self.request_id:
            raise RuntimeError("Writer not initialized")
        
        try:
            # Use staging manager to write content
            return await self.staging_manager.write_content(
                request_id=self.request_id,
                content=content,
                append=True  # Always append for streaming
            )
            
        except Exception as e:
            logger.error(f"Failed to write content: {str(e)}")
            return False
    
    async def write_chunks(self, content: str) -> bool:
        """
        Write content in chunks based on configured strategy.
        
        Args:
            content: Content to write
            
        Returns:
            True if all chunks written successfully
        """
        if not self._initialized:
            raise RuntimeError("Writer not initialized")
        
        try:
            chunks = self._create_chunks(content)
            
            for i, chunk in enumerate(chunks):
                success = await self.write(chunk)
                if not success:
                    logger.error(f"Failed to write chunk {i + 1}/{len(chunks)}")
                    return False
                
                # Small delay between chunks to prevent overwhelming the system
                if i < len(chunks) - 1:
                    await asyncio.sleep(0.01)
            
            logger.debug(f"Successfully wrote {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write chunks: {str(e)}")
            return False
    
    @asynccontextmanager
    async def stream_writer(self):
        """
        Get direct access to streaming file handle.
        
        Yields:
            Async file handle for direct writing
        """
        if not self._initialized or not self.request_id:
            raise RuntimeError("Writer not initialized")
        
        async with self.staging_manager.stream_writer(self.request_id) as f:
            yield f
    
    async def commit(self) -> bool:
        """
        Commit the staging operation to final target.
        
        Returns:
            True if commit successful
        """
        if not self._initialized or not self.request_id:
            return False
        
        try:
            success = await self.staging_manager.commit_operation(
                request_id=self.request_id,
                validate_integrity=self.config.validate_integrity
            )
            
            if success:
                logger.info(f"Successfully committed file: {self.target_path}")
            else:
                logger.error(f"Failed to commit file: {self.target_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during commit: {str(e)}")
            return False
    
    async def cancel(self) -> bool:
        """
        Cancel the staging operation.
        
        Returns:
            True if cancellation successful
        """
        if not self._initialized or not self.request_id:
            return False
        
        try:
            success = await self.staging_manager.cancel_operation(self.request_id)
            logger.info(f"Cancelled staging operation: {self.request_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error during cancellation: {str(e)}")
            return False
    
    async def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current status of the staging operation.
        
        Returns:
            Status dictionary or None if not available
        """
        if not self._initialized or not self.request_id:
            return None
        
        return await self.staging_manager.get_operation_status(self.request_id)
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self._initialized = False
        self.request_id = None
    
    def _create_chunks(self, content: str) -> List[str]:
        """
        Create chunks based on configured strategy.
        
        Args:
            content: Content to chunk
            
        Returns:
            List of content chunks
        """
        if self.config.chunking_strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(content)
        elif self.config.chunking_strategy == ChunkingStrategy.LINE_BASED:
            return self._chunk_line_based(content)
        elif self.config.chunking_strategy == ChunkingStrategy.PARAGRAPH_BASED:
            return self._chunk_paragraph_based(content)
        elif self.config.chunking_strategy == ChunkingStrategy.ADAPTIVE:
            return self._chunk_adaptive(content)
        else:
            # Default to fixed size
            return self._chunk_fixed_size(content)
    
    def _chunk_fixed_size(self, content: str) -> List[str]:
        """Chunk content into fixed-size pieces."""
        chunks = []
        for i in range(0, len(content), self.config.chunk_size):
            chunks.append(content[i:i + self.config.chunk_size])
        return chunks
    
    def _chunk_line_based(self, content: str) -> List[str]:
        """Chunk content by lines, respecting chunk size limits."""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            
            if current_size + line_size > self.config.chunk_size and current_chunk:
                # Current chunk would exceed limit, finalize it
                chunks.append('\n'.join(current_chunk) + '\n')
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_paragraph_based(self, content: str) -> List[str]:
        """Chunk content by paragraphs, respecting chunk size limits."""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph) + 2  # +2 for double newline
            
            if current_size + paragraph_size > self.config.chunk_size and current_chunk:
                # Current chunk would exceed limit, finalize it
                chunks.append('\n\n'.join(current_chunk) + '\n\n')
                current_chunk = [paragraph]
                current_size = paragraph_size
            else:
                current_chunk.append(paragraph)
                current_size += paragraph_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_adaptive(self, content: str) -> List[str]:
        """Adaptive chunking based on content structure."""
        # Start with paragraph-based chunking
        if '\n\n' in content:
            return self._chunk_paragraph_based(content)
        # Fall back to line-based
        elif '\n' in content:
            return self._chunk_line_based(content)
        # Use fixed size for unstructured content
        else:
            return self._chunk_fixed_size(content)
    
    async def _backup_original(self) -> None:
        """Create backup of original file."""
        if not self.target_path.exists():
            return
        
        backup_path = self.target_path.with_suffix(
            f"{self.target_path.suffix}.backup.{int(asyncio.get_event_loop().time())}"
        )
        
        try:
            await StagingUtils.safe_file_operation(
                self.target_path.rename, backup_path
            )
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {str(e)}")


class BatchFileWriter:
    """
    Batch file writer for multiple file operations.
    
    Provides atomic batch operations with rollback capability.
    """
    
    def __init__(self, config: Optional[WriteConfig] = None,
                 staging_manager: Optional[StagingManager] = None):
        """
        Initialize batch file writer.
        
        Args:
            config: Write configuration
            staging_manager: Optional staging manager instance
        """
        self.config = config or WriteConfig()
        self.staging_manager = staging_manager
        self.operations: Dict[str, str] = {}  # file_path -> request_id
        self._initialized = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is None:
            # Normal completion - commit if auto_commit enabled
            if self.config.auto_commit:
                await self.commit_all()
        else:
            # Exception occurred - cancel all operations
            await self.cancel_all()
    
    async def initialize(self) -> bool:
        """
        Initialize the batch writer.
        
        Returns:
            True if initialization successful
        """
        try:
            # Get staging manager
            if self.staging_manager is None:
                self.staging_manager = await get_staging_manager()
            
            self._initialized = True
            logger.info("Initialized batch file writer")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize batch writer: {str(e)}")
            return False
    
    async def add_file(self, file_path: Union[str, Path], content: str) -> bool:
        """
        Add file to batch operation.
        
        Args:
            file_path: Target file path
            content: File content
            
        Returns:
            True if file added successfully
        """
        if not self._initialized:
            raise RuntimeError("Batch writer not initialized")
        
        file_path = Path(file_path)
        file_key = str(file_path)
        
        try:
            # Validate file path
            is_valid, error_msg = StagingValidator.validate_file_path(file_key)
            if not is_valid:
                logger.error(f"Invalid file path: {error_msg}")
                return False
            
            # Create staging operation
            request_id = await self.staging_manager.create_staging_operation(
                target_path=file_path,
                mode=WriteMode.BATCH
            )
            
            # Write content
            success = await self.staging_manager.write_content(
                request_id=request_id,
                content=content
            )
            
            if success:
                self.operations[file_key] = request_id
                logger.debug(f"Added file to batch: {file_path}")
                return True
            else:
                logger.error(f"Failed to write content for: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add file to batch: {str(e)}")
            return False
    
    async def add_files(self, files: Dict[Union[str, Path], str]) -> int:
        """
        Add multiple files to batch operation.
        
        Args:
            files: Dictionary mapping file paths to content
            
        Returns:
            Number of files successfully added
        """
        success_count = 0
        
        for file_path, content in files.items():
            if await self.add_file(file_path, content):
                success_count += 1
        
        logger.info(f"Added {success_count}/{len(files)} files to batch")
        return success_count
    
    async def commit_all(self) -> bool:
        """
        Commit all files in the batch.
        
        Returns:
            True if all files committed successfully
        """
        if not self._initialized:
            return False
        
        success_count = 0
        
        for file_path, request_id in self.operations.items():
            try:
                success = await self.staging_manager.commit_operation(
                    request_id=request_id,
                    validate_integrity=self.config.validate_integrity
                )
                
                if success:
                    success_count += 1
                else:
                    logger.error(f"Failed to commit file: {file_path}")
                    
            except Exception as e:
                logger.error(f"Error committing file {file_path}: {str(e)}")
        
        all_success = success_count == len(self.operations)
        
        if all_success:
            logger.info(f"Successfully committed all {success_count} files")
        else:
            logger.error(f"Committed {success_count}/{len(self.operations)} files")
        
        return all_success
    
    async def cancel_all(self) -> bool:
        """
        Cancel all files in the batch.
        
        Returns:
            True if all operations cancelled successfully
        """
        if not self._initialized:
            return False
        
        success_count = 0
        
        for file_path, request_id in self.operations.items():
            try:
                success = await self.staging_manager.cancel_operation(request_id)
                if success:
                    success_count += 1
            except Exception as e:
                logger.error(f"Error cancelling file {file_path}: {str(e)}")
        
        logger.info(f"Cancelled {success_count}/{len(self.operations)} operations")
        return success_count == len(self.operations)
    
    async def get_batch_status(self) -> Dict[str, Any]:
        """
        Get status of all operations in the batch.
        
        Returns:
            Dictionary with batch status information
        """
        status_summary = {
            'total_files': len(self.operations),
            'files': {},
            'status_counts': {},
            'total_size': 0
        }
        
        for file_path, request_id in self.operations.items():
            try:
                op_status = await self.staging_manager.get_operation_status(request_id)
                if op_status:
                    status_summary['files'][file_path] = op_status
                    
                    # Count status types
                    status_type = op_status.get('status', 'unknown')
                    status_summary['status_counts'][status_type] = (
                        status_summary['status_counts'].get(status_type, 0) + 1
                    )
                    
                    # Sum total size
                    status_summary['total_size'] += op_status.get('content_size', 0)
                    
            except Exception as e:
                logger.error(f"Error getting status for {file_path}: {str(e)}")
        
        return status_summary


# Convenience functions

async def write_file_atomically(file_path: Union[str, Path], content: str,
                               config: Optional[WriteConfig] = None) -> bool:
    """
    Write file atomically with staging support.
    
    Args:
        file_path: Target file path
        content: File content
        config: Optional write configuration
        
    Returns:
        True if file written successfully
    """
    async with StreamingFileWriter(file_path, config) as writer:
        return await writer.write(content)


async def write_files_batch(files: Dict[Union[str, Path], str],
                           config: Optional[WriteConfig] = None) -> bool:
    """
    Write multiple files atomically as a batch.
    
    Args:
        files: Dictionary mapping file paths to content
        config: Optional write configuration
        
    Returns:
        True if all files written successfully
    """
    async with BatchFileWriter(config) as writer:
        success_count = await writer.add_files(files)
        if success_count == len(files):
            return await writer.commit_all()
        else:
            await writer.cancel_all()
            return False


async def stream_large_content(file_path: Union[str, Path], 
                              content_generator: AsyncGenerator[str, None],
                              config: Optional[WriteConfig] = None) -> bool:
    """
    Stream large content to file with staging support.
    
    Args:
        file_path: Target file path
        content_generator: Async generator yielding content chunks
        config: Optional write configuration
        
    Returns:
        True if streaming completed successfully
    """
    async with StreamingFileWriter(file_path, config) as writer:
        async with writer.stream_writer() as f:
            async for chunk in content_generator:
                await f.write(chunk)
        return True
