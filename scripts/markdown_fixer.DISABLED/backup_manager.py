"""
Backup Manager for safe file modifications.

Provides comprehensive backup and restore capabilities for markdown files.
"""

import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BackupManager:
    """Manages backup and restore operations for markdown files."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups. If None, uses project root/backups/
        """
        self.backup_dir = backup_dir or Path("backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_registry: Dict[Path, Path] = {}
        
    def create_backup(self, file_path: Path) -> Path:
        """
        Create a timestamped backup of a file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If backup directory is not writable
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Source file does not exist: {file_path}")
            
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # microseconds to ms
        backup_name = f"{file_path.name}.backup.{timestamp}"
        
        # Preserve directory structure in backup
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            # If file is not relative to cwd, use its absolute path structure
            relative_path = Path(*file_path.absolute().parts[1:])  # Remove root slash
        backup_path = self.backup_dir / relative_path.parent / backup_name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file with metadata
        shutil.copy2(file_path, backup_path)
        
        # Register backup
        self.backup_registry[file_path] = backup_path
        
        return backup_path
    
    def restore_backup(self, file_path: Path) -> bool:
        """
        Restore the most recent backup of a file.
        
        Args:
            file_path: Path to the original file
            
        Returns:
            True if restore was successful, False otherwise
        """
        if file_path in self.backup_registry:
            backup_path = self.backup_registry[file_path]
            if backup_path.exists():
                shutil.copy2(backup_path, file_path)
                return True
        
        # Look for backup files if not in registry
        backup_pattern = f"{file_path.name}.backup.*"
        relative_path = file_path.relative_to(Path.cwd())
        backup_dir = self.backup_dir / relative_path.parent
        
        if backup_dir.exists():
            backups = list(backup_dir.glob(backup_pattern))
            if backups:
                # Get most recent backup
                latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
                shutil.copy2(latest_backup, file_path)
                return True
        
        return False
    
    def get_backup_path(self, file_path: Path) -> Optional[Path]:
        """
        Get the backup path for a file.
        
        Args:
            file_path: Path to the original file
            
        Returns:
            Path to backup file or None if not found
        """
        return self.backup_registry.get(file_path)
    
    def list_backups(self) -> List[Path]:
        """
        List all backup files.
        
        Returns:
            List of backup file paths
        """
        return list(self.backup_registry.values())
    
    def cleanup_old_backups(self, days_old: int = 7) -> int:
        """
        Remove backup files older than specified number of days.
        
        Args:
            days_old: Number of days to keep backups
            
        Returns:
            Number of files deleted
        """
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for backup_path in self.backup_dir.rglob("*.backup.*"):
            try:
                if backup_path.stat().st_mtime < cutoff_time:
                    backup_path.unlink()
                    deleted_count += 1
            except OSError:
                # File may have been deleted already
                pass
        
        return deleted_count
    
    def emergency_restore_all(self) -> Dict[Path, bool]:
        """
        Restore all files from their most recent backups.
        
        Returns:
            Dictionary mapping file paths to restore success status
        """
        results = {}
        
        for original_path, backup_path in self.backup_registry.items():
            if backup_path.exists():
                try:
                    shutil.copy2(backup_path, original_path)
                    results[original_path] = True
                except Exception:
                    results[original_path] = False
            else:
                results[original_path] = False
        
        return results