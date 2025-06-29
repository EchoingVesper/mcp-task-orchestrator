"""
Advanced schema comparison utilities for database migrations.

This module provides detailed schema comparison capabilities between
SQLAlchemy models and actual database schemas, supporting complex
migration scenarios and constraint validation.
"""

import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from sqlalchemy import (
    inspect, MetaData, Table, Column, Index, ForeignKey,
    Integer, String, Text, DateTime, Boolean, JSON
)
from sqlalchemy.engine import Engine
from sqlalchemy.types import TypeEngine


logger = logging.getLogger(__name__)


@dataclass
class ColumnDifference:
    """Represents differences in a specific column."""
    column_name: str
    difference_type: str  # 'missing', 'extra', 'type_mismatch', 'constraint_mismatch'
    model_definition: Optional[Dict[str, Any]] = None
    database_definition: Optional[Dict[str, Any]] = None
    migration_action: Optional[str] = None


@dataclass
class TableDifference:
    """Represents differences in a specific table."""
    table_name: str
    missing_in_db: bool = False
    extra_in_db: bool = False
    column_differences: List[ColumnDifference] = field(default_factory=list)
    index_differences: List[str] = field(default_factory=list)
    constraint_differences: List[str] = field(default_factory=list)


@dataclass
class SchemaComparisonResult:
    """Complete schema comparison result."""
    tables_needing_creation: List[str] = field(default_factory=list)
    tables_needing_removal: List[str] = field(default_factory=list)
    table_differences: Dict[str, TableDifference] = field(default_factory=dict)
    migration_complexity: str = "SIMPLE"  # SIMPLE, MODERATE, COMPLEX
    estimated_downtime: float = 0.0  # seconds
    safety_warnings: List[str] = field(default_factory=list)


class SchemaComparator:
    """
    Advanced schema comparison between SQLAlchemy models and database.
    
    Provides detailed analysis of schema differences with migration
    complexity assessment and safety validation.
    """
    
    def __init__(self, engine: Engine, metadata: MetaData):
        """
        Initialize schema comparator.
        
        Args:
            engine: SQLAlchemy engine for database access
            metadata: SQLAlchemy metadata containing model definitions
        """
        self.engine = engine
        self.metadata = metadata
        self.inspector = inspect(engine)
        
        # Type mapping for SQLite compatibility
        self.type_mappings = {
            'INTEGER': ['INTEGER', 'INT', 'BIGINT'],
            'TEXT': ['TEXT', 'VARCHAR', 'CHAR', 'STRING'],
            'REAL': ['REAL', 'FLOAT', 'DOUBLE'],
            'BLOB': ['BLOB'],
            'DATETIME': ['DATETIME', 'TIMESTAMP'],
            'BOOLEAN': ['BOOLEAN', 'BOOL'],
            'JSON': ['JSON', 'TEXT']  # SQLite stores JSON as TEXT
        }
        
        logger.info("Schema comparator initialized")
    
    def compare_schemas(self) -> SchemaComparisonResult:
        """
        Perform comprehensive schema comparison.
        
        Returns:
            SchemaComparisonResult with detailed analysis
        """
        logger.info("Starting comprehensive schema comparison...")
        
        result = SchemaComparisonResult()
        
        try:
            # Get table lists
            model_tables = set(self.metadata.tables.keys())
            db_tables = set(self.inspector.get_table_names())
            
            # Find tables needing creation/removal
            result.tables_needing_creation = list(model_tables - db_tables)
            result.tables_needing_removal = list(db_tables - model_tables)
            
            # Analyze existing tables
            common_tables = model_tables.intersection(db_tables)
            for table_name in common_tables:
                table_diff = self._compare_table_detailed(table_name)
                if self._has_significant_differences(table_diff):
                    result.table_differences[table_name] = table_diff
            
            # Assess migration complexity
            result.migration_complexity = self._assess_complexity(result)
            result.estimated_downtime = self._estimate_downtime(result)
            result.safety_warnings = self._generate_safety_warnings(result)
            
            logger.info(f"Schema comparison complete: {result.migration_complexity} complexity, "
                       f"{len(result.table_differences)} tables with differences")
            
            return result
            
        except Exception as e:
            logger.error(f"Schema comparison failed: {e}")
            raise
    
    def _compare_table_detailed(self, table_name: str) -> TableDifference:
        """
        Perform detailed comparison of a single table.
        
        Args:
            table_name: Name of table to compare
            
        Returns:
            TableDifference with detailed analysis
        """
        table_diff = TableDifference(table_name=table_name)
        
        try:
            # Get model and database definitions
            model_table = self.metadata.tables[table_name]
            db_columns = {col['name']: col for col in self.inspector.get_columns(table_name)}
            model_columns = {col.name: col for col in model_table.columns}
            
            # Compare columns
            self._compare_columns(model_columns, db_columns, table_diff)
            
            # Compare indexes (if needed)
            self._compare_indexes(table_name, model_table, table_diff)
            
            # Compare constraints
            self._compare_constraints(table_name, model_table, table_diff)
            
        except Exception as e:
            logger.error(f"Failed to compare table {table_name}: {e}")
            table_diff.column_differences.append(
                ColumnDifference(
                    column_name="<error>",
                    difference_type="comparison_error",
                    migration_action=f"Manual review required: {e}"
                )
            )
        
        return table_diff
    
    def _compare_columns(self, model_columns: Dict, db_columns: Dict, table_diff: TableDifference):
        """Compare columns between model and database."""
        
        # Find missing columns (in model but not in database)
        missing_columns = set(model_columns.keys()) - set(db_columns.keys())
        for col_name in missing_columns:
            model_col = model_columns[col_name]
            table_diff.column_differences.append(
                ColumnDifference(
                    column_name=col_name,
                    difference_type="missing",
                    model_definition=self._extract_column_definition(model_col),
                    migration_action="ADD_COLUMN"
                )
            )
        
        # Find extra columns (in database but not in model)
        extra_columns = set(db_columns.keys()) - set(model_columns.keys())
        for col_name in extra_columns:
            table_diff.column_differences.append(
                ColumnDifference(
                    column_name=col_name,
                    difference_type="extra",
                    database_definition=db_columns[col_name],
                    migration_action="DROP_COLUMN"
                )
            )
        
        # Compare existing columns
        common_columns = set(model_columns.keys()).intersection(set(db_columns.keys()))
        for col_name in common_columns:
            model_col = model_columns[col_name]
            db_col = db_columns[col_name]
            
            column_diff = self._compare_column_types(col_name, model_col, db_col)
            if column_diff:
                table_diff.column_differences.append(column_diff)
    
    def _compare_column_types(self, col_name: str, model_col: Column, db_col: Dict) -> Optional[ColumnDifference]:
        """Compare column types and constraints."""
        
        # Normalize type names for comparison
        model_type = self._normalize_type_name(str(model_col.type))
        db_type = self._normalize_type_name(str(db_col['type']))
        
        # Check if types are compatible
        if not self._types_compatible(model_type, db_type):
            return ColumnDifference(
                column_name=col_name,
                difference_type="type_mismatch",
                model_definition=self._extract_column_definition(model_col),
                database_definition=db_col,
                migration_action="ALTER_COLUMN_TYPE"
            )
        
        # Check nullable constraint
        model_nullable = model_col.nullable
        db_nullable = db_col.get('nullable', True)
        
        if model_nullable != db_nullable:
            return ColumnDifference(
                column_name=col_name,
                difference_type="constraint_mismatch",
                model_definition=self._extract_column_definition(model_col),
                database_definition=db_col,
                migration_action="ALTER_COLUMN_CONSTRAINT"
            )
        
        return None
    
    def _normalize_type_name(self, type_str: str) -> str:
        """Normalize type name for comparison."""
        type_str = type_str.upper()
        
        # Handle parameterized types
        if '(' in type_str:
            type_str = type_str.split('(')[0]
        
        # Map to standard types
        for standard_type, variants in self.type_mappings.items():
            if type_str in variants:
                return standard_type
        
        return type_str
    
    def _types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two types are compatible."""
        # Exact match
        if type1 == type2:
            return True
        
        # Check if both types map to the same standard type
        for standard_type, variants in self.type_mappings.items():
            if type1 in variants and type2 in variants:
                return True
        
        return False
    
    def _extract_column_definition(self, column: Column) -> Dict[str, Any]:
        """Extract column definition as dictionary."""
        return {
            'name': column.name,
            'type': str(column.type),
            'nullable': column.nullable,
            'primary_key': column.primary_key,
            'default': str(column.default) if column.default else None,
            'foreign_key': bool(column.foreign_keys)
        }
    
    def _compare_indexes(self, table_name: str, model_table: Table, table_diff: TableDifference):
        """Compare indexes between model and database."""
        try:
            db_indexes = self.inspector.get_indexes(table_name)
            model_indexes = model_table.indexes
            
            # This is a simplified comparison - could be enhanced
            db_index_names = {idx['name'] for idx in db_indexes if idx['name']}
            model_index_names = {idx.name for idx in model_indexes if idx.name}
            
            missing_indexes = model_index_names - db_index_names
            extra_indexes = db_index_names - model_index_names
            
            for idx_name in missing_indexes:
                table_diff.index_differences.append(f"Missing index: {idx_name}")
            
            for idx_name in extra_indexes:
                table_diff.index_differences.append(f"Extra index: {idx_name}")
                
        except Exception as e:
            logger.warning(f"Failed to compare indexes for {table_name}: {e}")
    
    def _compare_constraints(self, table_name: str, model_table: Table, table_diff: TableDifference):
        """Compare constraints between model and database."""
        try:
            # Compare foreign keys
            db_fks = self.inspector.get_foreign_keys(table_name)
            model_fks = []
            
            for column in model_table.columns:
                for fk in column.foreign_keys:
                    model_fks.append({
                        'constrained_columns': [column.name],
                        'referred_table': fk.column.table.name,
                        'referred_columns': [fk.column.name]
                    })
            
            # Simple comparison of foreign key count
            if len(db_fks) != len(model_fks):
                table_diff.constraint_differences.append(
                    f"Foreign key count mismatch: model={len(model_fks)}, db={len(db_fks)}"
                )
                
        except Exception as e:
            logger.warning(f"Failed to compare constraints for {table_name}: {e}")
    
    def _has_significant_differences(self, table_diff: TableDifference) -> bool:
        """Check if table differences are significant enough to require migration."""
        return (
            bool(table_diff.column_differences) or
            bool(table_diff.index_differences) or
            bool(table_diff.constraint_differences)
        )
    
    def _assess_complexity(self, result: SchemaComparisonResult) -> str:
        """Assess migration complexity based on detected differences."""
        
        # Count significant operations
        table_operations = len(result.tables_needing_creation) + len(result.tables_needing_removal)
        column_operations = sum(len(diff.column_differences) for diff in result.table_differences.values())
        
        # Check for complex operations
        has_type_changes = any(
            any(col_diff.difference_type == "type_mismatch" for col_diff in table_diff.column_differences)
            for table_diff in result.table_differences.values()
        )
        
        has_constraint_changes = any(
            bool(table_diff.constraint_differences)
            for table_diff in result.table_differences.values()
        )
        
        # Determine complexity
        if has_type_changes or has_constraint_changes:
            return "COMPLEX"
        elif table_operations > 2 or column_operations > 5:
            return "MODERATE"
        else:
            return "SIMPLE"
    
    def _estimate_downtime(self, result: SchemaComparisonResult) -> float:
        """Estimate migration downtime in seconds."""
        
        # Base time for simple operations
        base_time = 0.1
        
        # Time per table operation
        table_time = len(result.tables_needing_creation) * 0.5
        
        # Time per column operation
        column_operations = sum(len(diff.column_differences) for diff in result.table_differences.values())
        column_time = column_operations * 0.2
        
        # Additional time for complex operations
        complexity_multiplier = {
            "SIMPLE": 1.0,
            "MODERATE": 1.5,
            "COMPLEX": 3.0
        }.get(result.migration_complexity, 1.0)
        
        total_time = (base_time + table_time + column_time) * complexity_multiplier
        return round(total_time, 2)
    
    def _generate_safety_warnings(self, result: SchemaComparisonResult) -> List[str]:
        """Generate safety warnings for the migration."""
        warnings = []
        
        # Warn about table drops
        if result.tables_needing_removal:
            warnings.append(f"Tables will be removed: {', '.join(result.tables_needing_removal)}")
        
        # Warn about column drops
        for table_name, table_diff in result.table_differences.items():
            drop_columns = [
                col_diff.column_name for col_diff in table_diff.column_differences
                if col_diff.difference_type == "extra"
            ]
            if drop_columns:
                warnings.append(f"Columns will be dropped from {table_name}: {', '.join(drop_columns)}")
        
        # Warn about type changes
        type_changes = []
        for table_name, table_diff in result.table_differences.items():
            for col_diff in table_diff.column_differences:
                if col_diff.difference_type == "type_mismatch":
                    type_changes.append(f"{table_name}.{col_diff.column_name}")
        
        if type_changes:
            warnings.append(f"Column types will change: {', '.join(type_changes)}")
        
        # Warn about complex migrations
        if result.migration_complexity == "COMPLEX":
            warnings.append("Complex migration detected - consider manual review")
        
        return warnings