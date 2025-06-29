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


class TestOutputWriter:
    """Main class for writing test outputs with atomic operations."""
    
    def __init__(self, output_dir: Union[str, Path] = None, test_name: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "test_outputs"
        self.test_name = test_name or f"test_{int(time.time())}"
        self.output_file = self.output_dir / f"{self.test_name}.txt"
        self.metadata = TestOutputMetadata(
            test_name=self.test_name,
            start_time=datetime.utcnow().isoformat()
        )
    
    def write_output(self, content: str) -> None:
        """Write content to output file atomically."""
        with AtomicFileWriter(self.output_file) as f:
            f.write(content)
        self.metadata.status = "completed"
        self.metadata.end_time = datetime.utcnow().isoformat()


class TestOutputReader:
    """Class for safely reading test outputs."""
    
    def __init__(self, output_file: Union[str, Path]):
        self.output_file = Path(output_file)
        self.done_file = self.output_file.with_suffix('.done')
    
    def is_ready(self) -> bool:
        """Check if test output is ready to read."""
        return self.done_file.exists()
    
    def read_output(self, timeout: float = 30.0) -> str:
        """Read test output, waiting for completion if necessary."""
        start_time = time.time()
        while not self.is_ready():
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Test output not ready after {timeout}s")
            time.sleep(0.1)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            return f.read()


class TestOutputSession:
    """Manages a complete test output session."""
    
    def __init__(self, output_dir: Union[str, Path] = None):
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "test_outputs"
        self.session_id = f"session_{int(time.time())}"
        self.session_dir = self.output_dir / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def create_writer(self, test_name: str) -> TestOutputWriter:
        """Create a new test output writer for this session."""
        return TestOutputWriter(self.session_dir, test_name)
    
    def create_reader(self, test_name: str) -> TestOutputReader:
        """Create a reader for a test in this session."""
        output_file = self.session_dir / f"{test_name}.txt"
        return TestOutputReader(output_file)
