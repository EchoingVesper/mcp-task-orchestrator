"""
Staging package for temporary file operations in MCP Task Orchestrator.

This package provides the infrastructure for staging temporary files with atomic operations,
streaming support, and comprehensive cleanup mechanisms.
"""

from .staging_manager import (
    StagingManager,
    StagingContext,
    StreamingChunk,
    StagingOperation,
    StagingStatus,
    StagingError,
    StagingIntegrityError,
    StagingCleanupError,
    AtomicMoveError,
    create_staging_manager
)

__all__ = [
    'StagingManager',
    'StagingContext', 
    'StreamingChunk',
    'StagingOperation',
    'StagingStatus',
    'StagingError',
    'StagingIntegrityError',
    'StagingCleanupError',
    'AtomicMoveError',
    'create_staging_manager'
]

__version__ = '1.0.0'
