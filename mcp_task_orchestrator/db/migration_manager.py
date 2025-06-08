"""
Core database migration management system.

This module provides automatic schema detection and migration capabilities
for the MCP Task Orchestrator database using SQLAlchemy introspection.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sqlalchemy import (
    create_engine, inspect, MetaData, Table, Column, 
    String, DateTime, Text, Integer, Boolean, event, text
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .models import Base, TaskBreakdownModel, SubTaskModel


logger = logging.getLogger(__name__)


@dataclass
class MigrationOperation:
    """Represents a single migration operation."""
    operation_type: str  # 'ADD_COLUMN', 'DROP_COLUMN', 'CREATE_TABLE', 'DROP_TABLE'
    table_name: str
    details: Dict[str, Any]
    rollback_sql: Optional[str] = None


@dataclass
class SchemaDifference:
    """Represents differences between model and database schema."""
    missing_tables: List[str]
    extra_tables: List[str]
    table_differences: Dict[str, List[str]]
    requires_migration: bool = False


class MigrationManager:
    """
    Manages automatic database schema migrations using SQLAlchemy introspection.
    
    Detects schema differences between SQLAlchemy models and actual database
    schema, generates safe migration operations, and executes them with
    rollback capability.
    """
    
    def __init__(self, database_url: str, models_module=None):
        """
        Initialize migration manager.
        
        Args:
            database_url: SQLAlchemy database URL
            models_module: Module containing SQLAlchemy models (defaults to .models)
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.inspector = inspect(self.engine)
        self.metadata = Base.metadata if models_module is None else models_module.metadata
        self.session_factory = sessionmaker(bind=self.engine)
        
        # Migration state
        self._migration_lock = False
        self._current_migration_id = None
        
        logger.info(f"Migration manager initialized for {database_url}")
    
    def detect_schema_differences(self) -> SchemaDifference:
        """
        Detect differences between SQLAlchemy models and actual database schema.
        
        Returns:
            SchemaDifference object containing detected differences
        """
        logger.info("Detecting schema differences...")
        
        try:
            # Get table names from models and database
            model_tables = set(self.metadata.tables.keys())
            db_tables = set(self.inspector.get_table_names())
            
            # Find missing and extra tables
            missing_tables = list(model_tables - db_tables)
            extra_tables = list(db_tables - model_tables)
            
            # Check existing tables for column differences
            table_differences = {}
            for table_name in model_tables.intersection(db_tables):
                diffs = self._compare_table_schema(table_name)
                if diffs:
                    table_differences[table_name] = diffs
            
            differences = SchemaDifference(
                missing_tables=missing_tables,
                extra_tables=extra_tables,
                table_differences=table_differences,
                requires_migration=bool(missing_tables or table_differences)
            )
            
            logger.info(f"Schema analysis complete: {len(missing_tables)} missing tables, "
                       f"{len(table_differences)} tables with differences")
            
            return differences
            
        except Exception as e:
            logger.error(f"Failed to detect schema differences: {e}")
            raise
    
    def _compare_table_schema(self, table_name: str) -> List[str]:
        """
        Compare schema of a specific table between model and database.
        
        Args:
            table_name: Name of table to compare
            
        Returns:
            List of difference descriptions
        """
        differences = []
        
        try:
            # Get model columns
            model_table = self.metadata.tables[table_name]
            model_columns = {col.name: col for col in model_table.columns}
            
            # Get database columns
            db_columns = {col['name']: col for col in self.inspector.get_columns(table_name)}
            
            # Find missing columns (in model but not in database)
            missing_columns = set(model_columns.keys()) - set(db_columns.keys())
            for col_name in missing_columns:
                col = model_columns[col_name]
                differences.append(f"Missing column: {col_name} ({col.type})")
            
            # Find extra columns (in database but not in model)
            extra_columns = set(db_columns.keys()) - set(model_columns.keys())
            for col_name in extra_columns:
                differences.append(f"Extra column: {col_name}")
            
            # Check existing columns for type differences
            for col_name in set(model_columns.keys()).intersection(set(db_columns.keys())):
                model_col = model_columns[col_name]
                db_col = db_columns[col_name]
                
                # Simple type comparison (could be enhanced)
                model_type_str = str(model_col.type).upper()
                db_type_str = str(db_col['type']).upper()
                
                if model_type_str != db_type_str:
                    differences.append(f"Type mismatch for {col_name}: "
                                     f"model={model_type_str}, db={db_type_str}")
            
        except Exception as e:
            logger.error(f"Failed to compare table schema for {table_name}: {e}")
            differences.append(f"Schema comparison failed: {e}")
        
        return differences
    
    def generate_migration_operations(self, differences: SchemaDifference) -> List[MigrationOperation]:
        """
        Generate migration operations from detected schema differences.
        
        Args:
            differences: SchemaDifference object from detect_schema_differences
            
        Returns:
            List of MigrationOperation objects
        """
        operations = []
        
        try:
            # Create missing tables
            for table_name in differences.missing_tables:
                if table_name in self.metadata.tables:
                    operations.append(MigrationOperation(
                        operation_type='CREATE_TABLE',
                        table_name=table_name,
                        details={'table_obj': self.metadata.tables[table_name]},
                        rollback_sql=f"DROP TABLE IF EXISTS {table_name};"
                    ))
            
            # Handle table differences (mainly missing columns)
            for table_name, diffs in differences.table_differences.items():
                for diff in diffs:
                    if diff.startswith('Missing column:'):
                        # Extract column name from difference description
                        col_name = diff.split(':')[1].strip().split(' ')[0]
                        model_table = self.metadata.tables[table_name]
                        
                        if col_name in [col.name for col in model_table.columns]:
                            col = next(col for col in model_table.columns if col.name == col_name)
                            operations.append(MigrationOperation(
                                operation_type='ADD_COLUMN',
                                table_name=table_name,
                                details={'column': col},
                                rollback_sql=f"ALTER TABLE {table_name} DROP COLUMN {col_name};"
                            ))
            
            logger.info(f"Generated {len(operations)} migration operations")
            return operations
            
        except Exception as e:
            logger.error(f"Failed to generate migration operations: {e}")
            raise
    
    def execute_migrations(self, operations: List[MigrationOperation]) -> bool:
        """
        Execute migration operations with transaction safety.
        
        Args:
            operations: List of MigrationOperation objects to execute
            
        Returns:
            True if all migrations succeeded, False otherwise
        """
        if not operations:
            logger.info("No migration operations to execute")
            return True
        
        if self._migration_lock:
            logger.warning("Migration already in progress")
            return False
        
        self._migration_lock = True
        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._current_migration_id = migration_id
        
        logger.info(f"Starting migration {migration_id} with {len(operations)} operations")
        
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Create migration history table if it doesn't exist
                    self._ensure_migration_history_table(conn)
                    
                    # Execute each operation
                    for i, operation in enumerate(operations):
                        logger.info(f"Executing operation {i+1}/{len(operations)}: "
                                   f"{operation.operation_type} on {operation.table_name}")
                        
                        success = self._execute_single_operation(conn, operation)
                        if not success:
                            logger.error(f"Migration operation failed: {operation}")
                            return False
                    
                    # Record successful migration
                    self._record_migration_success(conn, migration_id, operations)
                    
                    logger.info(f"Migration {migration_id} completed successfully")
                    return True
                
        except Exception as e:
            logger.error(f"Migration {migration_id} failed: {e}")
            return False
        
        finally:
            self._migration_lock = False
            self._current_migration_id = None
    
    def _execute_single_operation(self, conn, operation: MigrationOperation) -> bool:
        """Execute a single migration operation."""
        try:
            if operation.operation_type == 'CREATE_TABLE':
                table_obj = operation.details['table_obj']
                table_obj.create(conn, checkfirst=True)
                
            elif operation.operation_type == 'ADD_COLUMN':
                column = operation.details['column']
                # SQLite doesn't support ADD COLUMN with all constraints
                # This is a simplified implementation
                col_type = str(column.type)
                default_clause = ""
                
                if column.default is not None:
                    if isinstance(column.default.arg, str):
                        default_clause = f" DEFAULT '{column.default.arg}'"
                    else:
                        default_clause = f" DEFAULT {column.default.arg}"
                
                sql = (f"ALTER TABLE {operation.table_name} "
                      f"ADD COLUMN {column.name} {col_type}{default_clause};")
                
                conn.execute(text(sql))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute operation {operation.operation_type}: {e}")
            return False
    
    def _ensure_migration_history_table(self, conn):
        """Ensure migration history table exists."""
        create_sql = """
        CREATE TABLE IF NOT EXISTS migration_history (
            id INTEGER PRIMARY KEY,
            version STRING NOT NULL,
            name STRING NOT NULL,
            applied_at DATETIME NOT NULL,
            checksum STRING NOT NULL,
            status STRING DEFAULT 'completed',
            rollback_sql TEXT
        );
        """
        conn.execute(text(create_sql))
    
    def _record_migration_success(self, conn, migration_id: str, operations: List[MigrationOperation]):
        """Record successful migration in history table."""
        import hashlib
        
        # Create checksum from operations
        operation_summary = str([op.operation_type + op.table_name for op in operations])
        checksum = hashlib.md5(operation_summary.encode()).hexdigest()
        
        # Combine rollback SQL
        rollback_sql = "; ".join([op.rollback_sql for op in operations if op.rollback_sql])
        
        insert_sql = """
        INSERT INTO migration_history (version, name, applied_at, checksum, rollback_sql)
        VALUES (?, ?, ?, ?, ?)
        """
        
        conn.execute(text(insert_sql), (
            "1.0.0",  # Version - could be made configurable
            migration_id,
            datetime.now(),
            checksum,
            rollback_sql
        ))
    
    def check_migration_needed(self) -> bool:
        """
        Quick check if migration is needed.
        
        Returns:
            True if migration is required, False otherwise
        """
        try:
            differences = self.detect_schema_differences()
            return differences.requires_migration
        except Exception as e:
            logger.error(f"Failed to check migration status: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get migration history.
        
        Returns:
            List of migration records
        """
        try:
            with self.engine.connect() as conn:
                # Check if migration history table exists
                if not self.inspector.has_table('migration_history'):
                    return []
                
                result = conn.execute("SELECT * FROM migration_history ORDER BY applied_at DESC")
                return [dict(row) for row in result]
                
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []