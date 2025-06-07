"""
Database backup management utilities.

This module handles database backup creation, validation, and metadata tracking
for the migration system.
"""

import logging
import os
import shutil
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from sqlalchemy.engine import Engine


logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Information about a database backup."""
    backup_id: str
    original_path: str
    backup_path: str
    created_at: datetime
    size_bytes: int
    checksum: str
    migration_batch_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupInfo':
        """Create BackupInfo from dictionary."""
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class BackupManager:
    """
    Manages database backup creation and metadata.
    
    Handles backup file operations, integrity validation,
    and metadata tracking for migration rollback capabilities.
    """
    
    def __init__(self, backup_directory: Optional[Path] = None):
        """
        Initialize backup manager.
        
        Args:
            backup_directory: Directory for storing backups (defaults to ./backups)
        """
        if backup_directory is None:
            backup_directory = Path.cwd() / "backups" / "migrations"
        
        self.backup_directory = Path(backup_directory)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_directory / "backup_metadata.json"
        
        logger.info(f"Backup manager initialized: {self.backup_directory}")
    
    def create_backup(self, database_url: str, migration_batch_id: Optional[str] = None) -> BackupInfo:
        """
        Create a backup of the current database state.
        
        Args:
            database_url: SQLAlchemy database URL
            migration_batch_id: Optional batch ID for associating backup
            
        Returns:
            BackupInfo with backup details
            
        Raises:
            Exception: If backup creation fails
        """
        logger.info("Creating database backup...")
        
        try:
            # Generate backup ID and paths
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            backup_id = f"backup_{timestamp}"
            
            # Get database file path (assuming SQLite)
            if database_url.startswith('sqlite:///'):
                original_path = database_url[10:]
            else:
                raise ValueError(f"Unsupported database type for backup: {database_url}")
            
            original_path = Path(original_path)
            if not original_path.exists():
                raise FileNotFoundError(f"Database file not found: {original_path}")
            
            # Create backup
            backup_filename = f"{backup_id}_{original_path.name}"
            backup_path = self.backup_directory / backup_filename
            
            shutil.copy2(original_path, backup_path)
            
            # Get backup info
            backup_size = backup_path.stat().st_size
            backup_checksum = self._calculate_file_checksum(backup_path)
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                original_path=str(original_path),
                backup_path=str(backup_path),
                created_at=datetime.now(),
                size_bytes=backup_size,
                checksum=backup_checksum,
                migration_batch_id=migration_batch_id
            )
            
            # Store backup metadata
            self._store_backup_metadata(backup_info)
            
            logger.info(f"Database backup created: {backup_id} ({backup_size} bytes)")
            return backup_info
            
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise
    
    def restore_backup(self, backup_info: BackupInfo) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_info: Backup information
            
        Returns:
            True if restoration succeeded
        """
        try:
            backup_path = Path(backup_info.backup_path)
            original_path = Path(backup_info.original_path)
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Verify backup integrity
            current_checksum = self._calculate_file_checksum(backup_path)
            if current_checksum != backup_info.checksum:
                logger.error(f"Backup integrity check failed for {backup_info.backup_id}")
                return False
            
            # Create temporary backup of current state
            temp_backup = original_path.with_suffix('.tmp_backup')
            if original_path.exists():
                shutil.copy2(original_path, temp_backup)
            
            try:
                # Restore from backup
                shutil.copy2(backup_path, original_path)
                
                # Verify restoration
                if not self._verify_database_integrity(original_path):
                    # Restore from temp backup
                    if temp_backup.exists():
                        shutil.copy2(temp_backup, original_path)
                    logger.error("Database integrity check failed after restoration")
                    return False
                
                # Cleanup temp backup
                if temp_backup.exists():
                    temp_backup.unlink()
                
                logger.info(f"Database restored from backup: {backup_info.backup_id}")
                return True
                
            except Exception as restore_error:
                # Restore from temp backup on failure
                if temp_backup.exists():
                    shutil.copy2(temp_backup, original_path)
                    temp_backup.unlink()
                raise restore_error
                
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_info.backup_id}: {e}")
            return False
    
    def list_backups(self) -> List[BackupInfo]:
        """
        List all available backups.
        
        Returns:
            List of BackupInfo objects
        """
        try:
            if not self.metadata_file.exists():
                return []
            
            with open(self.metadata_file, 'r') as f:
                metadata_list = json.load(f)
            
            backups = [BackupInfo.from_dict(data) for data in metadata_list]
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def find_backup_for_migration(self, migration_time: datetime, batch_id: Optional[str] = None) -> Optional[BackupInfo]:
        """
        Find the most appropriate backup for a migration rollback.
        
        Args:
            migration_time: Time when migration was applied
            batch_id: Optional batch ID to prefer
            
        Returns:
            Most suitable BackupInfo or None
        """
        try:
            backups = self.list_backups()
            
            # Filter backups created before migration
            suitable_backups = [
                backup for backup in backups
                if backup.created_at < migration_time
            ]
            
            if not suitable_backups:
                return None
            
            # Prefer backup from same batch if available
            if batch_id:
                batch_backups = [
                    backup for backup in suitable_backups
                    if backup.migration_batch_id == batch_id
                ]
                if batch_backups:
                    return max(batch_backups, key=lambda b: b.created_at)
            
            # Return most recent suitable backup
            return max(suitable_backups, key=lambda b: b.created_at)
            
        except Exception as e:
            logger.error(f"Failed to find backup for migration: {e}")
            return None
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """
        Clean up old backup files.
        
        Args:
            keep_days: Number of days to keep backups
            
        Returns:
            Number of backups deleted
        """
        logger.info(f"Cleaning up backups older than {keep_days} days...")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            backups = self.list_backups()
            
            deleted_count = 0
            remaining_backups = []
            
            for backup in backups:
                if backup.created_at < cutoff_date:
                    # Delete backup file
                    backup_path = Path(backup.backup_path)
                    if backup_path.exists():
                        backup_path.unlink()
                        logger.debug(f"Deleted backup file: {backup_path}")
                    
                    deleted_count += 1
                else:
                    remaining_backups.append(backup)
            
            # Update metadata file
            if deleted_count > 0:
                self._save_backup_metadata(remaining_backups)
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get backup statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backups = self.list_backups()
            
            if not backups:
                return {
                    'total_backups': 0,
                    'total_size_bytes': 0,
                    'oldest_backup': None,
                    'newest_backup': None,
                    'average_size_bytes': 0
                }
            
            total_size = sum(backup.size_bytes for backup in backups)
            oldest_backup = min(backups, key=lambda b: b.created_at)
            newest_backup = max(backups, key=lambda b: b.created_at)
            
            stats = {
                'total_backups': len(backups),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'oldest_backup': oldest_backup.backup_id,
                'newest_backup': newest_backup.backup_id,
                'average_size_bytes': round(total_size / len(backups), 2)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get backup statistics: {e}")
            return {}
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _verify_database_integrity(self, db_path: Path) -> bool:
        """Verify database integrity using SQLite PRAGMA."""
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                
                if result and result[0] == 'ok':
                    return True
                else:
                    logger.warning(f"Database integrity check result: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")
            return False
    
    def _store_backup_metadata(self, backup_info: BackupInfo):
        """Store backup metadata for later retrieval."""
        try:
            # Load existing metadata
            metadata_list = []
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    metadata_list = json.load(f)
            
            # Add new backup info
            metadata_list.append(backup_info.to_dict())
            
            # Write updated metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata_list, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to store backup metadata: {e}")
    
    def _save_backup_metadata(self, backups: List[BackupInfo]):
        """Save complete backup metadata list."""
        try:
            metadata_list = [backup.to_dict() for backup in backups]
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata_list, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")