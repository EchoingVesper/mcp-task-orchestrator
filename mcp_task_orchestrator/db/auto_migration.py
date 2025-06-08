"""
Automatic database migration system integration.

This module provides a high-level API for the automatic database migration
system, integrating schema detection, migration execution, and rollback
capabilities for seamless server startup integration.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .migration_manager import MigrationManager, MigrationOperation, SchemaDifference
from .schema_comparator import SchemaComparator, SchemaComparisonResult
from .migration_history import MigrationHistoryManager, MigrationRecord
from .backup_manager import BackupManager, BackupInfo
from .rollback_manager import RollbackManager
from .models import Base


logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of an automatic migration attempt."""
    success: bool
    migration_needed: bool = False
    operations_executed: int = 0
    execution_time_ms: int = 0
    backup_created: bool = False
    backup_info: Optional[BackupInfo] = None
    error_message: Optional[str] = None
    migration_ids: List[int] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.migration_ids is None:
            self.migration_ids = []
        if self.warnings is None:
            self.warnings = []


class AutoMigrationSystem:
    """
    Comprehensive automatic database migration system.
    
    Provides a high-level interface for automatic schema detection,
    migration execution, and rollback capabilities designed for
    server startup integration.
    """
    
    def __init__(self, database_url: str, backup_directory: Optional[Path] = None):
        """
        Initialize automatic migration system.
        
        Args:
            database_url: SQLAlchemy database URL
            backup_directory: Optional backup directory path
        """
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        
        # Initialize components
        self.migration_manager = MigrationManager(database_url)
        self.schema_comparator = SchemaComparator(self.engine, Base.metadata)
        self.history_manager = MigrationHistoryManager(self.engine)
        self.backup_manager = BackupManager(backup_directory)
        self.rollback_manager = RollbackManager(self.engine, self.backup_manager)
        
        # Configuration
        self.auto_backup = True
        self.max_execution_time_ms = 30000  # 30 seconds
        self.dry_run_mode = False
        
        logger.info(f"Auto migration system initialized for {database_url}")
    
    def check_migration_status(self) -> Dict[str, Any]:
        """
        Check current migration status without executing changes.
        
        Returns:
            Dictionary with migration status information
        """
        logger.info("Checking migration status...")
        
        try:
            start_time = time.time()
            
            # Detect schema differences
            differences = self.migration_manager.detect_schema_differences()
            
            # Get detailed comparison
            comparison_result = self.schema_comparator.compare_schemas()
            
            # Get migration history
            recent_migrations = self.history_manager.get_migration_history(limit=10)
            failed_migrations = self.history_manager.get_failed_migrations(since_hours=24)
            
            # Get backup statistics
            backup_stats = self.backup_manager.get_backup_statistics()
            
            check_time_ms = int((time.time() - start_time) * 1000)
            
            status = {
                'migration_needed': differences.requires_migration,
                'schema_differences': {
                    'missing_tables': differences.missing_tables,
                    'extra_tables': differences.extra_tables,
                    'table_differences_count': len(differences.table_differences),
                },
                'migration_complexity': comparison_result.migration_complexity,
                'estimated_downtime_seconds': comparison_result.estimated_downtime,
                'safety_warnings': comparison_result.safety_warnings,
                'recent_migrations_count': len(recent_migrations),
                'failed_migrations_24h': len(failed_migrations),
                'backup_statistics': backup_stats,
                'check_time_ms': check_time_ms,
                'last_check': datetime.now().isoformat()
            }
            
            logger.info(f"Migration status check complete in {check_time_ms}ms: "
                       f"migration_needed={status['migration_needed']}")
            
            return status
            
        except Exception as e:
            logger.error(f"Migration status check failed: {e}")
            return {
                'error': str(e),
                'migration_needed': False,
                'check_time_ms': int((time.time() - start_time) * 1000),
                'last_check': datetime.now().isoformat()
            }
    
    def execute_auto_migration(self, force_backup: bool = None) -> MigrationResult:
        """
        Execute automatic migration if needed.
        
        Args:
            force_backup: Override auto_backup setting
            
        Returns:
            MigrationResult with execution details
        """
        logger.info("Starting automatic migration execution...")
        
        start_time = time.time()
        result = MigrationResult(success=False)
        
        try:
            # Check if migration is needed
            differences = self.migration_manager.detect_schema_differences()
            result.migration_needed = differences.requires_migration
            
            if not result.migration_needed:
                result.success = True
                result.execution_time_ms = int((time.time() - start_time) * 1000)
                logger.info("No migration needed - database schema is up to date")
                return result
            
            # Get detailed analysis
            comparison_result = self.schema_comparator.compare_schemas()
            
            # Add safety warnings
            result.warnings.extend(comparison_result.safety_warnings)
            
            # Check execution time estimate
            if comparison_result.estimated_downtime * 1000 > self.max_execution_time_ms:
                result.error_message = (
                    f"Estimated execution time ({comparison_result.estimated_downtime}s) "
                    f"exceeds maximum allowed ({self.max_execution_time_ms/1000}s)"
                )
                return result
            
            # Create backup if enabled
            backup_enabled = force_backup if force_backup is not None else self.auto_backup
            if backup_enabled:
                batch_id = self.history_manager._generate_batch_id()
                backup_info = self.backup_manager.create_backup(self.database_url, migration_batch_id=batch_id)
                result.backup_created = True
                result.backup_info = backup_info
                logger.info(f"Backup created: {backup_info.backup_id}")
            
            # Generate and execute migrations
            operations = self.migration_manager.generate_migration_operations(differences)
            result.operations_executed = len(operations)
            
            if self.dry_run_mode:
                logger.info(f"DRY RUN: Would execute {len(operations)} migration operations")
                result.success = True
                result.execution_time_ms = int((time.time() - start_time) * 1000)
                return result
            
            # Execute migrations with history tracking
            migration_success = self._execute_with_tracking(operations, result)
            
            if migration_success:
                result.success = True
                logger.info(f"Migration completed successfully: {len(operations)} operations")
            else:
                result.error_message = "Migration execution failed"
                logger.error("Migration execution failed")
            
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            return result
            
        except Exception as e:
            result.error_message = f"Migration failed with exception: {e}"
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Auto migration failed: {e}")
            return result
    
    def _execute_with_tracking(self, operations: List[MigrationOperation], result: MigrationResult) -> bool:
        """Execute migrations with proper history tracking."""
        
        try:
            batch_id = self.history_manager._generate_batch_id()
            
            # Record each operation
            for i, operation in enumerate(operations):
                migration_record = MigrationRecord(
                    name=f"auto_migration_{operation.operation_type}_{operation.table_name}",
                    description=f"{operation.operation_type} on table {operation.table_name}",
                    checksum=self.history_manager.calculate_checksum(str(operation.details)),
                    rollback_sql=operation.rollback_sql,
                    migration_type="automatic"
                )
                
                # Record start
                migration_id = self.history_manager.record_migration_start(migration_record, batch_id)
                result.migration_ids.append(migration_id)
                
                # Execute operation
                operation_start = time.time()
                
                with self.engine.connect() as conn:
                    with conn.begin():
                        success = self.migration_manager._execute_single_operation(
                            conn, operation
                        )
                
                operation_time_ms = int((time.time() - operation_start) * 1000)
                
                if success:
                    self.history_manager.record_migration_success(migration_id, operation_time_ms)
                    logger.info(f"Operation {i+1}/{len(operations)} completed: {operation.operation_type}")
                else:
                    error_msg = f"Failed to execute {operation.operation_type} on {operation.table_name}"
                    self.history_manager.record_migration_failure(migration_id, error_msg, operation_time_ms)
                    logger.error(error_msg)
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Migration execution with tracking failed: {e}")
            return False
    
    def rollback_last_migration(self, use_backup: bool = True) -> Dict[str, Any]:
        """
        Rollback the last migration.
        
        Args:
            use_backup: Whether to use backup restoration
            
        Returns:
            Dictionary with rollback results
        """
        logger.info("Starting rollback of last migration...")
        
        try:
            # Get last migration
            recent_migrations = self.history_manager.get_migration_history(limit=1)
            if not recent_migrations:
                return {
                    'success': False,
                    'error': 'No migrations found to rollback'
                }
            
            last_migration = recent_migrations[0]
            migration_id = last_migration['id']
            
            # Execute rollback
            rollback_result = self.rollback_manager.rollback_migration(migration_id, use_backup)
            
            return {
                'success': rollback_result.success,
                'migration_id': migration_id,
                'migration_name': last_migration['name'],
                'execution_time_ms': rollback_result.execution_time_ms,
                'backup_restored': rollback_result.backup_restored,
                'error_message': rollback_result.error_message
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall migration system health status.
        
        Returns:
            Dictionary with health information
        """
        try:
            # Get migration statistics
            migration_stats = self.history_manager.get_migration_statistics()
            
            # Get backup statistics
            backup_stats = self.backup_manager.get_backup_statistics()
            
            # Check for recent failures
            failed_migrations = self.history_manager.get_failed_migrations(since_hours=24)
            
            # Calculate health score
            health_score = self._calculate_health_score(migration_stats, failed_migrations)
            
            return {
                'overall_health': 'HEALTHY' if health_score >= 80 else 'WARNING' if health_score >= 60 else 'CRITICAL',
                'health_score': health_score,
                'migration_statistics': migration_stats,
                'backup_statistics': backup_stats,
                'recent_failures': len(failed_migrations),
                'recommendations': self._generate_health_recommendations(migration_stats, failed_migrations),
                'last_health_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'overall_health': 'UNKNOWN',
                'health_score': 0,
                'error': str(e),
                'last_health_check': datetime.now().isoformat()
            }
    
    def _calculate_health_score(self, migration_stats: Dict[str, Any], failed_migrations: List[Dict]) -> int:
        """Calculate system health score (0-100)."""
        
        score = 100
        
        # Deduct for recent failures
        score -= len(failed_migrations) * 10
        
        # Deduct for low success rate
        success_rate = migration_stats.get('success_rate', 100)
        if success_rate < 90:
            score -= (90 - success_rate) * 2
        
        # Deduct for long execution times
        avg_time = migration_stats.get('average_execution_time_ms', 0)
        if avg_time > 5000:  # More than 5 seconds
            score -= min(20, (avg_time - 5000) / 1000 * 2)
        
        return max(0, min(100, score))
    
    def _generate_health_recommendations(self, migration_stats: Dict[str, Any], failed_migrations: List[Dict]) -> List[str]:
        """Generate health recommendations based on system status."""
        
        recommendations = []
        
        if failed_migrations:
            recommendations.append(f"Review {len(failed_migrations)} recent migration failures")
        
        success_rate = migration_stats.get('success_rate', 100)
        if success_rate < 90:
            recommendations.append(f"Migration success rate is low ({success_rate:.1f}%) - investigate causes")
        
        avg_time = migration_stats.get('average_execution_time_ms', 0)
        if avg_time > 10000:
            recommendations.append("Average migration time is high - consider optimization")
        
        total_migrations = migration_stats.get('total_migrations', 0)
        if total_migrations > 100:
            recommendations.append("Consider cleaning up old migration records")
        
        if not recommendations:
            recommendations.append("System is healthy - no action required")
        
        return recommendations
    
    def configure(self, **kwargs):
        """
        Configure migration system settings.
        
        Args:
            **kwargs: Configuration options (auto_backup, max_execution_time_ms, dry_run_mode)
        """
        if 'auto_backup' in kwargs:
            self.auto_backup = kwargs['auto_backup']
            logger.info(f"Auto backup set to: {self.auto_backup}")
        
        if 'max_execution_time_ms' in kwargs:
            self.max_execution_time_ms = kwargs['max_execution_time_ms']
            logger.info(f"Max execution time set to: {self.max_execution_time_ms}ms")
        
        if 'dry_run_mode' in kwargs:
            self.dry_run_mode = kwargs['dry_run_mode']
            logger.info(f"Dry run mode set to: {self.dry_run_mode}")


# Convenience function for server startup integration
def execute_startup_migration(database_url: str, backup_directory: Optional[Path] = None) -> MigrationResult:
    """
    Execute automatic migration for server startup.
    
    This is the main entry point for server startup integration.
    
    Args:
        database_url: SQLAlchemy database URL
        backup_directory: Optional backup directory
        
    Returns:
        MigrationResult with execution details
    """
    logger.info("Executing startup migration check...")
    
    try:
        # Initialize migration system
        migration_system = AutoMigrationSystem(database_url, backup_directory)
        
        # Configure for startup (conservative settings)
        migration_system.configure(
            auto_backup=True,
            max_execution_time_ms=15000,  # 15 seconds max for startup
            dry_run_mode=False
        )
        
        # Execute migration
        result = migration_system.execute_auto_migration()
        
        if result.success:
            if result.migration_needed:
                logger.info(f"Startup migration completed: {result.operations_executed} operations in {result.execution_time_ms}ms")
            else:
                logger.info("Startup migration check: No migration needed")
        else:
            logger.error(f"Startup migration failed: {result.error_message}")
        
        return result
        
    except Exception as e:
        logger.error(f"Startup migration failed with exception: {e}")
        return MigrationResult(
            success=False,
            error_message=str(e)
        )