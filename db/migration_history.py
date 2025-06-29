"""
Migration history tracking and version management.

This module manages the migration history table and provides
version tracking capabilities for database schema changes.
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, 
    DateTime, Text, Boolean, event, select, update, delete
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger(__name__)


@dataclass
class MigrationRecord:
    """Represents a single migration record."""
    id: Optional[int] = None
    version: str = "1.0.0"
    name: str = ""
    description: str = ""
    applied_at: Optional[datetime] = None
    checksum: str = ""
    status: str = "pending"  # pending, running, completed, failed, rolled_back
    rollback_sql: Optional[str] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    migration_type: str = "automatic"  # automatic, manual, hotfix
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        if data['applied_at']:
            data['applied_at'] = data['applied_at'].isoformat()
        return data


@dataclass
class MigrationBatch:
    """Represents a batch of related migrations."""
    batch_id: str
    migrations: List[MigrationRecord]
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    rollback_required: bool = False


class MigrationHistoryManager:
    """
    Manages migration history and version tracking.
    
    Provides comprehensive tracking of database schema changes
    with rollback capabilities and audit trail.
    """
    
    def __init__(self, engine: Engine):
        """
        Initialize migration history manager.
        
        Args:
            engine: SQLAlchemy engine for database access
        """
        self.engine = engine
        self.metadata = MetaData()
        self._ensure_history_table()
        
        logger.info("Migration history manager initialized")
    
    def _ensure_history_table(self):
        """Ensure migration history table exists with proper schema."""
        
        self.history_table = Table(
            'migration_history',
            self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('version', String(50), nullable=False),
            Column('name', String(255), nullable=False),
            Column('description', Text),
            Column('applied_at', DateTime, nullable=False),
            Column('checksum', String(64), nullable=False),
            Column('status', String(20), nullable=False, default='pending'),
            Column('rollback_sql', Text),
            Column('execution_time_ms', Integer),
            Column('error_message', Text),
            Column('migration_type', String(20), default='automatic'),
            Column('batch_id', String(64)),
            Column('metadata_json', Text),  # For additional data storage
            extend_existing=True
        )
        
        try:
            self.metadata.create_all(self.engine, checkfirst=True)
            logger.info("Migration history table ensured")
        except Exception as e:
            logger.error(f"Failed to create migration history table: {e}")
            raise
    
    def start_migration_batch(self, batch_description: str = "") -> str:
        """
        Start a new migration batch.
        
        Args:
            batch_description: Description of the migration batch
            
        Returns:
            Batch ID for tracking
        """
        batch_id = self._generate_batch_id()
        
        logger.info(f"Starting migration batch {batch_id}: {batch_description}")
        
        # Store batch metadata (could be in separate table if needed)
        batch_metadata = {
            'batch_id': batch_id,
            'description': batch_description,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }
        
        # For now, store in first migration record of batch
        # In a more complex system, this could be a separate table
        return batch_id
    
    def record_migration_start(self, migration_record: MigrationRecord, batch_id: Optional[str] = None) -> int:
        """
        Record the start of a migration.
        
        Args:
            migration_record: Migration record to insert
            batch_id: Optional batch ID for grouping
            
        Returns:
            Migration ID for tracking
        """
        try:
            migration_record.applied_at = datetime.now()
            migration_record.status = "running"
            
            if batch_id:
                metadata_dict = {'batch_id': batch_id}
            else:
                metadata_dict = {}
            
            insert_stmt = self.history_table.insert().values(
                version=migration_record.version,
                name=migration_record.name,
                description=migration_record.description,
                applied_at=migration_record.applied_at,
                checksum=migration_record.checksum,
                status=migration_record.status,
                rollback_sql=migration_record.rollback_sql,
                migration_type=migration_record.migration_type,
                batch_id=batch_id,
                metadata_json=json.dumps(metadata_dict)
            )
            
            with self.engine.connect() as conn:
                result = conn.execute(insert_stmt)
                conn.commit()
                migration_id = result.inserted_primary_key[0]
                
            logger.info(f"Recorded migration start: {migration_record.name} (ID: {migration_id})")
            return migration_id
            
        except Exception as e:
            logger.error(f"Failed to record migration start: {e}")
            raise
    
    def record_migration_success(self, migration_id: int, execution_time_ms: int):
        """
        Record successful migration completion.
        
        Args:
            migration_id: ID of the migration
            execution_time_ms: Execution time in milliseconds
        """
        try:
            update_stmt = (
                update(self.history_table)
                .where(self.history_table.c.id == migration_id)
                .values(
                    status='completed',
                    execution_time_ms=execution_time_ms,
                    error_message=None
                )
            )
            
            with self.engine.connect() as conn:
                conn.execute(update_stmt)
                conn.commit()
                
            logger.info(f"Recorded migration success: ID {migration_id}, {execution_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Failed to record migration success: {e}")
            raise
    
    def record_migration_failure(self, migration_id: int, error_message: str, execution_time_ms: int):
        """
        Record migration failure.
        
        Args:
            migration_id: ID of the migration
            error_message: Error description
            execution_time_ms: Execution time before failure
        """
        try:
            update_stmt = (
                update(self.history_table)
                .where(self.history_table.c.id == migration_id)
                .values(
                    status='failed',
                    execution_time_ms=execution_time_ms,
                    error_message=error_message
                )
            )
            
            with self.engine.connect() as conn:
                conn.execute(update_stmt)
                conn.commit()
                
            logger.error(f"Recorded migration failure: ID {migration_id}, error: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to record migration failure: {e}")
            raise
    
    def record_migration_rollback(self, migration_id: int, rollback_reason: str):
        """
        Record migration rollback.
        
        Args:
            migration_id: ID of the migration
            rollback_reason: Reason for rollback
        """
        try:
            update_stmt = (
                update(self.history_table)
                .where(self.history_table.c.id == migration_id)
                .values(
                    status='rolled_back',
                    error_message=rollback_reason
                )
            )
            
            with self.engine.connect() as conn:
                conn.execute(update_stmt)
                conn.commit()
                
            logger.info(f"Recorded migration rollback: ID {migration_id}, reason: {rollback_reason}")
            
        except Exception as e:
            logger.error(f"Failed to record migration rollback: {e}")
            raise
    
    def get_migration_history(self, limit: int = 50, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get migration history.
        
        Args:
            limit: Maximum number of records to return
            status_filter: Optional status filter
            
        Returns:
            List of migration records
        """
        try:
            select_stmt = select(self.history_table).order_by(self.history_table.c.applied_at.desc())
            
            if status_filter:
                select_stmt = select_stmt.where(self.history_table.c.status == status_filter)
                
            select_stmt = select_stmt.limit(limit)
            
            with self.engine.connect() as conn:
                result = conn.execute(select_stmt)
                records = [dict(row._mapping) for row in result]
                
            logger.info(f"Retrieved {len(records)} migration history records")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    def get_failed_migrations(self, since_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get failed migrations within a time window.
        
        Args:
            since_hours: Hours to look back
            
        Returns:
            List of failed migration records
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=since_hours)
            
            select_stmt = (
                select(self.history_table)
                .where(self.history_table.c.status == 'failed')
                .where(self.history_table.c.applied_at >= cutoff_time)
                .order_by(self.history_table.c.applied_at.desc())
            )
            
            with self.engine.connect() as conn:
                result = conn.execute(select_stmt)
                records = [dict(row._mapping) for row in result]
                
            logger.info(f"Retrieved {len(records)} failed migrations in last {since_hours} hours")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get failed migrations: {e}")
            return []
    
    def get_pending_rollbacks(self) -> List[Dict[str, Any]]:
        """
        Get migrations that might need rollback.
        
        Returns:
            List of migration records that might need rollback
        """
        try:
            # Find failed migrations with rollback SQL
            select_stmt = (
                select(self.history_table)
                .where(self.history_table.c.status == 'failed')
                .where(self.history_table.c.rollback_sql.isnot(None))
                .order_by(self.history_table.c.applied_at.desc())
            )
            
            with self.engine.connect() as conn:
                result = conn.execute(select_stmt)
                records = [dict(row._mapping) for row in result]
                
            logger.info(f"Found {len(records)} migrations with available rollback")
            return records
            
        except Exception as e:
            logger.error(f"Failed to get pending rollbacks: {e}")
            return []
    
    def calculate_checksum(self, data: Any) -> str:
        """
        Calculate checksum for migration data.
        
        Args:
            data: Data to calculate checksum for
            
        Returns:
            MD5 checksum as hex string
        """
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True)
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_part = hashlib.md5(str(datetime.now().microsecond).encode()).hexdigest()[:8]
        return f"batch_{timestamp}_{random_part}"
    
    def get_last_successful_migration(self) -> Optional[Dict[str, Any]]:
        """
        Get the last successful migration.
        
        Returns:
            Last successful migration record or None
        """
        try:
            select_stmt = (
                select(self.history_table)
                .where(self.history_table.c.status == 'completed')
                .order_by(self.history_table.c.applied_at.desc())
                .limit(1)
            )
            
            with self.engine.connect() as conn:
                result = conn.execute(select_stmt)
                row = result.fetchone()
                
                if row:
                    return dict(row._mapping)
                
            return None
            
        except Exception as e:
            logger.error(f"Failed to get last successful migration: {e}")
            return None
    
    def cleanup_old_records(self, keep_days: int = 90) -> int:
        """
        Clean up old migration records.
        
        Args:
            keep_days: Number of days to keep records
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # Only delete completed migrations older than cutoff
            delete_stmt = (
                delete(self.history_table)
                .where(self.history_table.c.status == 'completed')
                .where(self.history_table.c.applied_at < cutoff_date)
            )
            
            with self.engine.connect() as conn:
                result = conn.execute(delete_stmt)
                conn.commit()
                deleted_count = result.rowcount
                
            logger.info(f"Cleaned up {deleted_count} old migration records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old records: {e}")
            return 0
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """
        Get migration statistics.
        
        Returns:
            Dictionary with migration statistics
        """
        try:
            with self.engine.connect() as conn:
                # Count by status
                status_counts = {}
                for status in ['completed', 'failed', 'running', 'rolled_back']:
                    count_stmt = select([self.history_table.c.id.label('count')]).where(
                        self.history_table.c.status == status
                    )
                    result = conn.execute(count_stmt)
                    status_counts[status] = len(list(result))
                
                # Average execution time
                avg_time_stmt = select([self.history_table.c.execution_time_ms]).where(
                    self.history_table.c.status == 'completed'
                )
                result = conn.execute(avg_time_stmt)
                times = [row[0] for row in result if row[0] is not None]
                avg_time = sum(times) / len(times) if times else 0
                
                # Latest migration
                latest_stmt = (
                    select(self.history_table)
                    .order_by(self.history_table.c.applied_at.desc())
                    .limit(1)
                )
                result = conn.execute(latest_stmt)
                latest_row = result.fetchone()
                latest_migration = dict(latest_row._mapping) if latest_row else None
                
                stats = {
                    'total_migrations': sum(status_counts.values()),
                    'status_counts': status_counts,
                    'average_execution_time_ms': round(avg_time, 2),
                    'latest_migration': latest_migration,
                    'success_rate': (
                        status_counts.get('completed', 0) / sum(status_counts.values()) * 100
                        if sum(status_counts.values()) > 0 else 0
                    )
                }
                
                logger.info("Generated migration statistics")
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get migration statistics: {e}")
            return {}