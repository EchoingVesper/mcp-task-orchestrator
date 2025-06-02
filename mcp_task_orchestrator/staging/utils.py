"""
Utilities for staging operations in MCP Task Orchestrator.

This module provides helper functions and utilities for staging operations,
file integrity validation, and cross-platform compatibility.
"""

import os
import hashlib
import platform
import asyncio
import aiofiles
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("mcp_task_orchestrator.staging.utils")


class StagingUtils:
    """Utility functions for staging operations."""
    
    @staticmethod
    def generate_request_id(prefix: str = "req") -> str:
        """
        Generate unique request ID.
        
        Args:
            prefix: Prefix for the request ID
            
        Returns:
            Unique request identifier
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        return f"{prefix}_{timestamp}_{unique_id}"
    
    @staticmethod
    async def calculate_checksum(file_path: Path, algorithm: str = "sha256") -> str:
        """
        Calculate checksum of file using specified algorithm.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hexadecimal checksum string
        """
        if algorithm == "sha256":
            hash_obj = hashlib.sha256()
        elif algorithm == "md5":
            hash_obj = hashlib.md5()
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum for {file_path}: {str(e)}")
            raise
    
    @staticmethod
    async def validate_file_integrity(file_path: Path, expected_checksum: str, 
                                    algorithm: str = "sha256") -> bool:
        """
        Validate file integrity against expected checksum.
        
        Args:
            file_path: Path to file
            expected_checksum: Expected checksum value
            algorithm: Hash algorithm used
            
        Returns:
            True if file integrity is valid
        """
        try:
            actual_checksum = await StagingUtils.calculate_checksum(file_path, algorithm)
            return actual_checksum == expected_checksum
        except Exception as e:
            logger.error(f"Error validating file integrity: {str(e)}")
            return False
    
    @staticmethod
    def get_filesystem_info(path: Path) -> Dict[str, Any]:
        """
        Get filesystem information for a path.
        
        Args:
            path: Path to analyze
            
        Returns:
            Dictionary with filesystem information
        """
        try:
            stat_info = path.stat()
            
            return {
                "device_id": stat_info.st_dev,
                "inode": stat_info.st_ino,
                "size": stat_info.st_size,
                "modified_time": datetime.fromtimestamp(stat_info.st_mtime),
                "access_time": datetime.fromtimestamp(stat_info.st_atime),
                "creation_time": datetime.fromtimestamp(stat_info.st_ctime),
                "permissions": oct(stat_info.st_mode)[-3:],
                "platform": platform.system(),
                "filesystem_type": StagingUtils._get_filesystem_type(path)
            }
        except Exception as e:
            logger.error(f"Error getting filesystem info for {path}: {str(e)}")
            return {}
    
    @staticmethod
    def _get_filesystem_type(path: Path) -> str:
        """Get filesystem type for a path (platform-specific)."""
        try:
            system = platform.system()
            
            if system == "Windows":
                # Windows filesystem detection
                import win32api
                drive = str(path).split(":")[0] + ":"
                filesystem_type = win32api.GetVolumeInformation(drive + "\\")[4]
                return filesystem_type
            elif system == "Linux":
                # Linux filesystem detection via /proc/mounts
                with open("/proc/mounts", "r") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 3:
                            mount_point = parts[1]
                            fs_type = parts[2]
                            if str(path).startswith(mount_point):
                                return fs_type
            elif system == "Darwin":
                # macOS filesystem detection
                import subprocess
                result = subprocess.run(
                    ["df", "-T", str(path)], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\\n")
                    if len(lines) > 1:
                        return lines[1].split()[1]
            
            return "unknown"
            
        except Exception:
            return "unknown"
    
    @staticmethod
    def is_same_filesystem(path1: Path, path2: Path) -> bool:
        """
        Check if two paths are on the same filesystem.
        
        Args:
            path1: First path
            path2: Second path
            
        Returns:
            True if paths are on same filesystem
        """
        try:
            stat1 = path1.stat()
            stat2 = path2.stat()
            return stat1.st_dev == stat2.st_dev
        except Exception as e:
            logger.warning(f"Error checking filesystem compatibility: {str(e)}")
            return False
    
    @staticmethod
    async def ensure_directory(path: Path, mode: int = 0o755) -> bool:
        """
        Ensure directory exists with proper permissions.
        
        Args:
            path: Directory path to create
            mode: Directory permissions (Unix-style)
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions on Unix-like systems
            if platform.system() != "Windows":
                path.chmod(mode)
            
            return True
        except Exception as e:
            logger.error(f"Error ensuring directory {path}: {str(e)}")
            return False
    
    @staticmethod
    def get_available_space(path: Path) -> int:
        """
        Get available disk space at path in bytes.
        
        Args:
            path: Path to check
            
        Returns:
            Available space in bytes
        """
        try:
            if platform.system() == "Windows":
                import shutil
                return shutil.disk_usage(path).free
            else:
                stat = os.statvfs(path)
                return stat.f_bavail * stat.f_frsize
        except Exception as e:
            logger.error(f"Error getting available space for {path}: {str(e)}")
            return 0
    
    @staticmethod
    def estimate_operation_time(file_size: int, operation_type: str = "write") -> float:
        """
        Estimate operation time based on file size and operation type.
        
        Args:
            file_size: Size of file in bytes
            operation_type: Type of operation (write, read, copy, move)
            
        Returns:
            Estimated time in seconds
        """
        # Base estimates (MB/s) - conservative values
        operation_speeds = {
            "write": 50,  # 50 MB/s
            "read": 100,  # 100 MB/s
            "copy": 30,   # 30 MB/s
            "move": 200,  # 200 MB/s (same filesystem)
        }
        
        speed_mbps = operation_speeds.get(operation_type, 50)
        file_size_mb = file_size / (1024 * 1024)
        
        # Minimum operation time of 0.1 seconds
        estimated_time = max(0.1, file_size_mb / speed_mbps)
        
        return estimated_time
    
    @staticmethod
    async def safe_file_operation(operation_func, *args, max_retries: int = 3, 
                                 retry_delay: float = 0.5, **kwargs) -> Any:
        """
        Execute file operation with retry logic.
        
        Args:
            operation_func: Function to execute
            *args: Positional arguments for function
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            **kwargs: Keyword arguments for function
            
        Returns:
            Result of operation function
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation_func):
                    return await operation_func(*args, **kwargs)
                else:
                    return operation_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"File operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
        
        # All retries failed
        logger.error(f"File operation failed after {max_retries + 1} attempts")
        raise last_exception
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def format_duration(duration_seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if duration_seconds < 1:
            return f"{duration_seconds * 1000:.0f}ms"
        elif duration_seconds < 60:
            return f"{duration_seconds:.1f}s"
        elif duration_seconds < 3600:
            minutes = int(duration_seconds // 60)
            seconds = duration_seconds % 60
            return f"{minutes}m {seconds:.0f}s"
        else:
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class StagingValidator:
    """Validation utilities for staging operations."""
    
    @staticmethod
    def validate_request_id(request_id: str) -> bool:
        """
        Validate request ID format.
        
        Args:
            request_id: Request identifier to validate
            
        Returns:
            True if request ID is valid
        """
        if not request_id or not isinstance(request_id, str):
            return False
        
        # Basic validation - alphanumeric, underscore, hyphen
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, request_id)) and len(request_id) <= 100
    
    @staticmethod
    def validate_staging_path(path: Path, base_staging_dir: Path) -> bool:
        """
        Validate that staging path is within allowed directory.
        
        Args:
            path: Path to validate
            base_staging_dir: Base staging directory
            
        Returns:
            True if path is valid and safe
        """
        try:
            # Resolve paths to handle symlinks and relative paths
            resolved_path = path.resolve()
            resolved_base = base_staging_dir.resolve()
            
            # Check if path is within base staging directory
            return str(resolved_path).startswith(str(resolved_base))
        except Exception:
            return False
    
    @staticmethod
    def validate_content_size(content: str, max_size_mb: int = 100) -> Tuple[bool, str]:
        """
        Validate content size against limits.
        
        Args:
            content: Content to validate
            max_size_mb: Maximum size in MB
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not content:
            return True, ""
        
        content_size = len(content.encode('utf-8'))
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if content_size > max_size_bytes:
            return False, f"Content size ({StagingUtils.format_file_size(content_size)}) exceeds maximum allowed size ({max_size_mb} MB)"
        
        return True, ""
    
    @staticmethod
    def validate_file_path(file_path: str) -> Tuple[bool, str]:
        """
        Validate file path for security and format.
        
        Args:
            file_path: File path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path cannot be empty"
        
        # Check for path traversal attempts
        dangerous_patterns = ['../', '..\\\\', '.\\\\', './']
        normalized_path = file_path.replace('\\\\', '/').lower()
        
        for pattern in dangerous_patterns:
            if pattern in normalized_path:
                return False, f"Path contains dangerous pattern: {pattern}"
        
        # Check for invalid characters (platform-specific)
        if platform.system() == "Windows":
            invalid_chars = '<>:"|?*'
            for char in invalid_chars:
                if char in file_path:
                    return False, f"Path contains invalid character: {char}"
        
        # Check path length
        if len(file_path) > 260:  # Windows MAX_PATH limitation
            return False, "Path length exceeds maximum allowed"
        
        return True, ""


# Convenience functions
async def create_safe_staging_directory(base_dir: Path, request_id: str) -> Optional[Path]:
    """
    Create a safe staging directory with validation.
    
    Args:
        base_dir: Base staging directory
        request_id: Request identifier
        
    Returns:
        Path to created staging directory or None if failed
    """
    if not StagingValidator.validate_request_id(request_id):
        logger.error(f"Invalid request ID: {request_id}")
        return None
    
    staging_path = base_dir / f"staging_{request_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    if not StagingValidator.validate_staging_path(staging_path, base_dir):
        logger.error(f"Invalid staging path: {staging_path}")
        return None
    
    if await StagingUtils.ensure_directory(staging_path):
        return staging_path
    else:
        return None


def get_staging_statistics(base_staging_dir: Path) -> Dict[str, Any]:
    """
    Get statistics about staging operations.
    
    Args:
        base_staging_dir: Base staging directory
        
    Returns:
        Dictionary with staging statistics
    """
    stats = {
        "total_staging_dirs": 0,
        "total_size_bytes": 0,
        "oldest_staging": None,
        "newest_staging": None,
        "staging_by_status": {},
        "average_file_size": 0
    }
    
    try:
        if not base_staging_dir.exists():
            return stats
        
        staging_dirs = []
        total_size = 0
        
        for staging_dir in base_staging_dir.iterdir():
            if staging_dir.is_dir():
                dir_info = StagingUtils.get_filesystem_info(staging_dir)
                staging_dirs.append(dir_info)
                total_size += dir_info.get("size", 0)
        
        stats["total_staging_dirs"] = len(staging_dirs)
        stats["total_size_bytes"] = total_size
        
        if staging_dirs:
            # Sort by modification time
            staging_dirs.sort(key=lambda x: x.get("modified_time", datetime.min))
            stats["oldest_staging"] = staging_dirs[0]["modified_time"]
            stats["newest_staging"] = staging_dirs[-1]["modified_time"]
            stats["average_file_size"] = total_size // len(staging_dirs)
        
    except Exception as e:
        logger.error(f"Error getting staging statistics: {str(e)}")
    
    return stats
