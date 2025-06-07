"""
Simplified database migration rollback management.

This module provides rollback capabilities using the backup manager
and migration history components.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from sqlalchemy.engine import Engine

from .migration_history import MigrationHistoryManager
from .backup_manager import BackupManager, BackupInfo


logger = logging.getLogger(__name__)


@dataclass
class RollbackResult:
    """Result of a rollback operation."""
    success: bool
    migration_id: int
    execution_time_ms: int
    error_message: Optional[str] = None
    backup_restored: bool = False
    sql_executed: Optional[str] = None


class RollbackManager:
    """
    Manages database rollback operations using backup restoration and SQL rollback.
    
    Provides safe rollback capabilities with backup restoration
    and validation of rollback operations.
    """
    
    def __init__(self, engine: Engine, backup_manager: Optional[BackupManager] = None):
        """
        Initialize rollback manager.
        
        Args:
            engine: SQLAlchemy engine for database access
            backup_manager: Optional backup manager (creates default if None)
        """
        self.engine = engine
        self.database_url = str(engine.url)
        
        # Initialize components
        if backup_manager is None:
            backup_manager = BackupManager()
        self.backup_manager = backup_manager
        self.history_manager = MigrationHistoryManager(engine)
        
        logger.info("Rollback manager initialized")
    
    def create_backup(self, migration_batch_id: Optional[str] = None) -> BackupInfo:
        """
        Create a backup before migration.
        
        Args:
            migration_batch_id: Optional batch ID for associating backup
            
        Returns:
            BackupInfo with backup details
        """
        return self.backup_manager.create_backup(self.database_url, migration_batch_id)
    
    def rollback_migration(self, migration_id: int, use_backup: bool = False) -> RollbackResult:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of migration to rollback
            use_backup: Whether to restore from backup instead of using SQL
            
        Returns:
            RollbackResult with rollback details
        """
        logger.info(f"Starting rollback for migration ID: {migration_id}")
        
        start_time = datetime.now()
        result = RollbackResult(
            success=False,
            migration_id=migration_id,
            execution_time_ms=0
        )
        
        try:
            # Get migration record
            migration_history = self.history_manager.get_migration_history(limit=1000)
            migration_record = next(
                (record for record in migration_history if record['id'] == migration_id),
                None
            )
            
            if not migration_record:
                result.error_message = f"Migration ID {migration_id} not found"
                return result
            
            if migration_record['status'] not in ['completed', 'failed']:
                result.error_message = f"Cannot rollback migration with status: {migration_record['status']}"
                return result
            
            # Perform rollback
            if use_backup:
                result = self._rollback_with_backup(migration_record, result)
            else:
                result = self._rollback_with_sql(migration_record, result)
            
            # Update execution time
            end_time = datetime.now()
            result.execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Record rollback in history
            if result.success:
                self.history_manager.record_migration_rollback(
                    migration_id, 
                    f"Rollback successful ({'backup' if use_backup else 'sql'})"
                )
                logger.info(f"Rollback completed successfully for migration {migration_id}")
            else:
                logger.error(f"Rollback failed for migration {migration_id}: {result.error_message}")
            
            return result
            
        except Exception as e:
            result.error_message = f"Rollback exception: {e}"
            result.execution_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.error(f"Rollback failed with exception: {e}")
            return result
    
    def _rollback_with_sql(self, migration_record: Dict[str, Any], result: RollbackResult) -> RollbackResult:
        """Rollback using stored SQL commands."""
        
        rollback_sql = migration_record.get('rollback_sql')
        if not rollback_sql:
            result.error_message = "No rollback SQL available for this migration"
            return result
        
        try:
            # Execute rollback SQL
            with self.engine.begin() as conn:
                # Split and execute SQL statements
                statements = [stmt.strip() for stmt in rollback_sql.split(';') if stmt.strip()]
                
                for stmt in statements:
                    logger.debug(f"Executing rollback SQL: {stmt}")
                    conn.execute(stmt)
                
                result.sql_executed = rollback_sql
                result.success = True
                
                logger.info(f"Executed {len(statements)} rollback SQL statements")
                
        except Exception as e:
            result.error_message = f"SQL rollback failed: {e}"
            logger.error(f"SQL rollback failed: {e}")
        
        return result
    
    def _rollback_with_backup(self, migration_record: Dict[str, Any], result: RollbackResult) -> RollbackResult:
        """Rollback by restoring from backup."""
        
        try:
            # Find appropriate backup
            migration_time = migration_record['applied_at']
            if isinstance(migration_time, str):
                migration_time = datetime.fromisoformat(migration_time)
            
            batch_id = migration_record.get('batch_id')
            backup_info = self.backup_manager.find_backup_for_migration(migration_time, batch_id)
            
            if not backup_info:
                result.error_message = "No suitable backup found for rollback"
                return result
            
            # Dispose engine connections before file operations
            self.engine.dispose()
            
            # Restore from backup
            success = self.backup_manager.restore_backup(backup_info)
            if success:
                result.success = True
                result.backup_restored = True
                logger.info(f"Successfully restored database from backup: {backup_info.backup_id}")
            else:
                result.error_message = "Backup restoration failed"
                
        except Exception as e:
            result.error_message = f"Backup rollback failed: {e}"
            logger.error(f"Backup rollback failed: {e}")
        
        return result
    
    def get_rollback_candidates(self) -> List[Dict[str, Any]]:
        """
        Get migrations that can be rolled back.
        
        Returns:
            List of migration records that can be rolled back
        """
        try:
            # Get recent migrations
            migrations = self.history_manager.get_migration_history(limit=50)
            
            # Filter rollback candidates
            candidates = []
            for migration in migrations:
                # Can rollback completed or failed migrations
                if migration['status'] in ['completed', 'failed']:
                    # Check if rollback SQL is available or backups exist
                    has_rollback_sql = bool(migration.get('rollback_sql'))
                    
                    migration_time = migration['applied_at']
                    if isinstance(migration_time, str):
                        migration_time = datetime.fromisoformat(migration_time)
                    
                    has_backup = self.backup_manager.find_backup_for_migration(migration_time) is not None
                    
                    if has_rollback_sql or has_backup:
                        migration_info = migration.copy()
                        migration_info['rollback_options'] = {
                            'sql_available': has_rollback_sql,
                            'backup_available': has_backup
                        }
                        candidates.append(migration_info)
            
            logger.info(f"Found {len(candidates)} rollback candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Failed to get rollback candidates: {e}")
            return []
    
    def get_rollback_status(self) -> Dict[str, Any]:
        """
        Get overall rollback system status.
        
        Returns:
            Dictionary with rollback system status
        """
        try:
            candidates = self.get_rollback_candidates()
            backup_stats = self.backup_manager.get_backup_statistics()
            failed_migrations = self.history_manager.get_failed_migrations(since_hours=24)
            
            status = {
                'rollback_candidates': len(candidates),
                'recent_failures': len(failed_migrations),
                'backup_statistics': backup_stats,
                'last_check': datetime.now().isoformat(),
                'recommendations': []
            }
            
            # Generate recommendations
            if failed_migrations:
                status['recommendations'].append(f"Consider rolling back {len(failed_migrations)} recent failed migrations")
            
            if backup_stats['total_backups'] == 0:
                status['recommendations'].append("No backups available - consider enabling automatic backups")
            
            if backup_stats.get('total_size_mb', 0) > 1000:  # > 1GB
                status['recommendations'].append("Large backup storage usage - consider cleanup")
            
            if not status['recommendations']:
                status['recommendations'].append("Rollback system is healthy")
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get rollback status: {e}")
            return {
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }