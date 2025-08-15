"""
Recovery Manager for emergency rollback and disaster recovery.

Provides comprehensive recovery capabilities for markdown fixing operations.
"""

import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .backup_manager import BackupManager


class RecoveryManager:
    """Manages emergency recovery and rollback operations."""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize recovery manager.
        
        Args:
            backup_dir: Directory containing backups
        """
        self.backup_dir = backup_dir or Path("backups")
        self.backup_manager = BackupManager(self.backup_dir)
        self.recovery_log_path = self.backup_dir / "recovery.log"
        
    def emergency_restore_all(self) -> Dict[Path, bool]:
        """
        Emergency restore all files from their most recent backups.
        
        Returns:
            Dictionary mapping file paths to restore success status
        """
        self._log_recovery_action("emergency_restore_all", "Starting emergency restore of all files")
        
        results = {}
        backup_files = list(self.backup_dir.rglob("*.backup.*"))
        
        if not backup_files:
            self._log_recovery_action("emergency_restore_all", "No backup files found")
            return results
        
        # Group backups by original file
        file_backups: Dict[Path, List[Path]] = {}
        
        for backup_path in backup_files:
            original_path = self._extract_original_path(backup_path)
            if original_path:
                if original_path not in file_backups:
                    file_backups[original_path] = []
                file_backups[original_path].append(backup_path)
        
        # Restore each file from its most recent backup
        for original_path, backups in file_backups.items():
            try:
                # Find most recent backup
                latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
                
                # Restore file
                if original_path.parent.exists() or self._create_parent_dirs(original_path):
                    shutil.copy2(latest_backup, original_path)
                    results[original_path] = True
                    self._log_recovery_action("restore_file", f"Restored {original_path} from {latest_backup}")
                else:
                    results[original_path] = False
                    self._log_recovery_action("restore_error", f"Could not create parent directories for {original_path}")
                    
            except Exception as e:
                results[original_path] = False
                self._log_recovery_action("restore_error", f"Failed to restore {original_path}: {e}")
        
        self._log_recovery_action("emergency_restore_all", f"Completed. Restored {sum(results.values())} of {len(results)} files")
        return results
    
    def restore_specific_files(self, file_paths: List[Path]) -> Dict[Path, bool]:
        """
        Restore specific files from backups.
        
        Args:
            file_paths: List of file paths to restore
            
        Returns:
            Dictionary mapping file paths to restore success status
        """
        results = {}
        
        for file_path in file_paths:
            try:
                success = self.backup_manager.restore_backup(file_path)
                results[file_path] = success
                
                if success:
                    self._log_recovery_action("restore_file", f"Restored {file_path}")
                else:
                    self._log_recovery_action("restore_error", f"No backup found for {file_path}")
                    
            except Exception as e:
                results[file_path] = False
                self._log_recovery_action("restore_error", f"Failed to restore {file_path}: {e}")
        
        return results
    
    def restore_directory(self, directory: Path) -> Dict[Path, bool]:
        """
        Restore all files in a directory from backups.
        
        Args:
            directory: Directory to restore
            
        Returns:
            Dictionary mapping file paths to restore success status
        """
        self._log_recovery_action("restore_directory", f"Starting restore of directory: {directory}")
        
        # Find all markdown files in directory
        md_files = []
        if directory.exists():
            for pattern in ['*.md', '**/*.md']:
                md_files.extend(directory.glob(pattern))
        
        return self.restore_specific_files(md_files)
    
    def create_recovery_point(self, description: str = None) -> Path:
        """
        Create a recovery point with current state.
        
        Args:
            description: Optional description of the recovery point
            
        Returns:
            Path to recovery point directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recovery_point_dir = self.backup_dir / "recovery_points" / timestamp
        recovery_point_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "description": description or "Manual recovery point",
            "created_at": datetime.now().isoformat(),
            "files": []
        }
        
        # Find all markdown files and copy them
        docs_dir = Path("docs")
        if docs_dir.exists():
            for pattern in ['*.md', '**/*.md']:
                for md_file in docs_dir.glob(pattern):
                    if 'archives' not in str(md_file):  # Skip archives
                        try:
                            # Preserve directory structure
                            relative_path = md_file.relative_to(docs_dir)
                            target_path = recovery_point_dir / relative_path
                            target_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            shutil.copy2(md_file, target_path)
                            metadata["files"].append(str(relative_path))
                        except Exception as e:
                            self._log_recovery_action("recovery_point_error", f"Failed to backup {md_file}: {e}")
        
        # Save metadata
        with open(recovery_point_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._log_recovery_action("recovery_point", f"Created recovery point: {recovery_point_dir}")
        return recovery_point_dir
    
    def list_recovery_points(self) -> List[Dict]:
        """
        List available recovery points.
        
        Returns:
            List of recovery point metadata
        """
        recovery_points = []
        recovery_points_dir = self.backup_dir / "recovery_points"
        
        if recovery_points_dir.exists():
            for rp_dir in recovery_points_dir.iterdir():
                if rp_dir.is_dir():
                    metadata_file = rp_dir / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file) as f:
                                metadata = json.load(f)
                            metadata["path"] = str(rp_dir)
                            recovery_points.append(metadata)
                        except Exception:
                            pass
        
        return sorted(recovery_points, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def restore_from_recovery_point(self, recovery_point_dir: Path) -> Dict[Path, bool]:
        """
        Restore files from a specific recovery point.
        
        Args:
            recovery_point_dir: Path to recovery point directory
            
        Returns:
            Dictionary mapping file paths to restore success status
        """
        self._log_recovery_action("restore_recovery_point", f"Restoring from recovery point: {recovery_point_dir}")
        
        results = {}
        docs_dir = Path("docs")
        
        if not recovery_point_dir.exists():
            self._log_recovery_action("restore_error", f"Recovery point does not exist: {recovery_point_dir}")
            return results
        
        # Find all files in recovery point
        for md_file in recovery_point_dir.rglob("*.md"):
            try:
                # Calculate target path
                relative_path = md_file.relative_to(recovery_point_dir)
                target_path = docs_dir / relative_path
                
                # Create parent directories if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(md_file, target_path)
                results[target_path] = True
                
            except Exception as e:
                results[target_path] = False
                self._log_recovery_action("restore_error", f"Failed to restore {md_file}: {e}")
        
        self._log_recovery_action("restore_recovery_point", f"Completed. Restored {sum(results.values())} of {len(results)} files")
        return results
    
    def get_backup_status(self) -> Dict:
        """
        Get status of backup system.
        
        Returns:
            Dictionary with backup status information
        """
        backup_files = list(self.backup_dir.rglob("*.backup.*"))
        recovery_points = self.list_recovery_points()
        
        status = {
            "backup_directory": str(self.backup_dir),
            "backup_files_count": len(backup_files),
            "recovery_points_count": len(recovery_points),
            "disk_usage": self._calculate_disk_usage(),
            "oldest_backup": None,
            "newest_backup": None
        }
        
        if backup_files:
            oldest = min(backup_files, key=lambda p: p.stat().st_mtime)
            newest = max(backup_files, key=lambda p: p.stat().st_mtime)
            status["oldest_backup"] = {
                "path": str(oldest),
                "timestamp": datetime.fromtimestamp(oldest.stat().st_mtime).isoformat()
            }
            status["newest_backup"] = {
                "path": str(newest),
                "timestamp": datetime.fromtimestamp(newest.stat().st_mtime).isoformat()
            }
        
        return status
    
    def _extract_original_path(self, backup_path: Path) -> Optional[Path]:
        """
        Extract original file path from backup file name.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Original file path or None if can't be determined
        """
        try:
            # Remove backup suffix (e.g., .backup.20240107_143022)
            name_parts = backup_path.name.split('.backup.')
            if len(name_parts) == 2:
                original_name = name_parts[0]
                
                # Reconstruct path relative to backup directory
                relative_path = backup_path.relative_to(self.backup_dir)
                original_relative = relative_path.parent / original_name
                
                # Convert back to absolute path in docs directory
                return Path("docs") / original_relative.relative_to(Path("docs"))
                
        except Exception:
            pass
        
        return None
    
    def _create_parent_dirs(self, file_path: Path) -> bool:
        """
        Create parent directories for a file path.
        
        Args:
            file_path: File path
            
        Returns:
            True if successful
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _calculate_disk_usage(self) -> Dict:
        """Calculate disk usage of backup directory."""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in self.backup_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count
            }
        except Exception:
            return {"error": "Could not calculate disk usage"}
    
    def _log_recovery_action(self, action: str, message: str) -> None:
        """
        Log recovery action to recovery log file.
        
        Args:
            action: Action type
            message: Log message
        """
        try:
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {action}: {message}\n"
            
            with open(self.recovery_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            # Don't fail if logging fails
            pass