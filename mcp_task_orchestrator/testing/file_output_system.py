#!/usr/bin/env python3
"""
File-Based Test Output System

This module provides a robust system for writing test outputs to files with
atomic operations, completion signaling, and safe reading mechanisms to prevent
timing issues where consumers check results before tests have finished writing.

Key Features:
- Atomic file writes to prevent partial reads
- Completion signaling with .done files
- Multiple output formats (JSON, text, structured)
- Safe read operations with timeout and retry
- Integration with existing test frameworks
- Thread-safe operations for concurrent tests
"""

import os
import json
import time
import threading
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, TextIO
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import fcntl
import logging

logger = logging.getLogger("test_output_system")


@dataclass
class TestOutputMetadata:
    """Metadata for test output files."""
    test_name: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "running"  # running, completed, failed, timeout
    output_format: str = "text"
    file_size: int = 0
    line_count: int = 0
    checksum: Optional[str] = None


class AtomicFileWriter:
    """Handles atomic file writing operations."""
    
    def __init__(self, output_path: Union[str, Path]):
        self.output_path = Path(output_path)
        self.temp_path = self.output_path.with_suffix('.tmp')
        self.done_path = self.output_path.with_suffix('.done')
        self.metadata_path = self.output_path.with_suffix('.meta.json')
        self._lock = threading.Lock()
    
    def __enter__(self):
        """Context manager entry - creates temp file for writing."""
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open temp file for writing
        self._temp_file = open(self.temp_path, 'w', encoding='utf-8', buffering=1)
        
        # On Unix systems, use file locking for additional safety
        if hasattr(fcntl, 'flock'):
            try:
                fcntl.flock(self._temp_file.fileno(), fcntl.LOCK_EX)
            except (OSError, AttributeError):
                pass  # File locking not available or failed
        
        return self._temp_file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - commits the write atomically."""
        try:
            # Close and flush the temp file
            if hasattr(fcntl, 'flock'):
                try:
                    fcntl.flock(self._temp_file.fileno(), fcntl.LOCK_UN)
                except (OSError, AttributeError):
                    pass
            
            self._temp_file.close()
            
            if exc_type is None:
                # No exception - commit the file atomically
                self._commit_file()
            else:
                # Exception occurred - clean up temp file
                self._cleanup_temp_file()
        except Exception as e:
            logger.error(f"Error in AtomicFileWriter exit: {str(e)}")
            self._cleanup_temp_file()
    
    def _commit_file(self):
        """Atomically move temp file to final location and create completion marker."""
        try:
            # Move temp file to final location (atomic on most filesystems)
            shutil.move(str(self.temp_path), str(self.output_path))
            
            # Create completion marker file
            with open(self.done_path, 'w') as done_file:
                done_file.write(f"completed_at:{datetime.utcnow().isoformat()}\\n")
                done_file.write(f"file_size:{self.output_path.stat().st_size}\\n")
            
            logger.debug(f"Atomically committed file: {self.output_path}")
            
        except Exception as e:
            logger.error(f"Failed to commit file {self.output_path}: {str(e)}")
            self._cleanup_temp_file()
            raise
    
    def _cleanup_temp_file(self):
        """Clean up temporary file if it exists."""
        try:
            if self.temp_path.exists():
                self.temp_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to clean up temp file {self.temp_path}: {str(e)}")
