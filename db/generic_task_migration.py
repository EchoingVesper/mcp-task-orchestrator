"""
Generic Task Model Migration Module

This module provides the migration infrastructure to transition from the current
dual-model system (TaskBreakdown + SubTask) to the unified GenericTask model.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sqlite3
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class GenericTaskMigration:
    """Handles migration from old task model to generic task model."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
        self.migration_stats = {
            "task_breakdowns_migrated": 0,
            "subtasks_migrated": 0,
            "dependencies_created": 0,
            "attributes_created": 0,
            "events_created": 0,
            "errors": []
        }
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_schema_sql(self, sql_file_path: str) -> None:
        """Execute the schema SQL file to create new tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Read and execute the schema file
            with open(sql_file_path, 'r') as f:
                schema_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                try:
                    cursor.execute(statement)
                except sqlite3.Error as e:
                    logger.error(f"Error executing statement: {e}")
                    logger.error(f"Statement: {statement[:100]}...")
            
            conn.commit()
            logger.info("Schema created successfully")
    
    def create_migration_record(self, migration_name: str) -> int:
        """Create a migration record and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO schema_migrations (migration_name, migration_type, status, started_at)
                VALUES (?, 'data', 'running', ?)
            """, (migration_name, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def migrate_task_breakdown(self, conn: sqlite3.Connection, migration_id: int, 
                              task_breakdown: sqlite3.Row) -> str:
        """Migrate a single task breakdown to generic task."""
        cursor = conn.cursor()
        
        # Generate hierarchy path for root task
        task_id = task_breakdown['parent_task_id']
        hierarchy_path = f"/{task_id}"
        
        # Insert into generic_tasks
        cursor.execute("""
            INSERT INTO generic_tasks (
                task_id, parent_task_id, title, description, task_type,
                hierarchy_path, hierarchy_level, status, lifecycle_stage,
                complexity, context, created_at
            ) VALUES (?, NULL, ?, ?, 'breakdown', ?, 0, 'active', 'active', ?, ?, ?)
        """, (
            task_id,
            f"Task Breakdown: {task_breakdown['description'][:100]}",
            task_breakdown['description'],
            hierarchy_path,
            task_breakdown['complexity'],
            task_breakdown['context'],
            task_breakdown['created_at']
        ))
        
        # Create legacy mapping
        cursor.execute("""
            INSERT INTO legacy_task_mapping (old_task_id, new_task_id, old_task_type, migration_id)
            VALUES (?, ?, 'task_breakdown', ?)
        """, (task_id, task_id, migration_id))
        
        # Create initial event
        cursor.execute("""
            INSERT INTO task_events (task_id, event_type, event_category, event_data, triggered_by)
            VALUES (?, 'migrated', 'system', ?, 'migration')
        """, (task_id, json.dumps({"from": "task_breakdown", "migration_id": migration_id})))
        
        self.migration_stats["task_breakdowns_migrated"] += 1
        self.migration_stats["events_created"] += 1
        
        return task_id
    
    def migrate_subtask(self, conn: sqlite3.Connection, migration_id: int,
                       subtask: sqlite3.Row, parent_hierarchy_path: str,
                       position: int) -> str:
        """Migrate a single subtask to generic task."""
        cursor = conn.cursor()
        
        # Generate hierarchy path
        task_id = subtask['task_id']
        hierarchy_path = f"{parent_hierarchy_path}/{task_id}"
        hierarchy_level = len(hierarchy_path.split('/')) - 2  # Subtract empty string and root
        
        # Determine lifecycle stage from status
        lifecycle_stage_map = {
            'pending': 'created',
            'in_progress': 'active',
            'completed': 'completed',
            'failed': 'failed',
            'cancelled': 'archived'
        }
        lifecycle_stage = lifecycle_stage_map.get(subtask['status'], 'active')
        
        # Insert into generic_tasks
        cursor.execute("""
            INSERT INTO generic_tasks (
                task_id, parent_task_id, title, description, task_type,
                hierarchy_path, hierarchy_level, position_in_parent,
                status, lifecycle_stage, specialist_type,
                estimated_effort, results, verification_status,
                quality_gate_level, auto_maintenance_enabled,
                created_at, completed_at
            ) VALUES (?, ?, ?, ?, 'subtask', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            subtask['parent_task_id'],
            subtask['title'],
            subtask['description'],
            hierarchy_path,
            hierarchy_level,
            position,
            subtask['status'],
            lifecycle_stage,
            subtask['specialist_type'],
            subtask['estimated_effort'],
            subtask['results'],
            subtask['verification_status'],
            subtask['quality_gate_level'],
            subtask['auto_maintenance_enabled'],
            subtask['created_at'],
            subtask['completed_at']
        ))
        
        # Migrate artifacts if present
        if subtask['artifacts']:
            artifacts = json.loads(subtask['artifacts'])
            for i, artifact in enumerate(artifacts):
                self._migrate_artifact(conn, task_id, artifact, i)
        
        # Create custom attributes for subtask-specific fields
        if subtask['prerequisite_satisfaction_required']:
            cursor.execute("""
                INSERT INTO task_attributes (task_id, attribute_name, attribute_value, attribute_type, attribute_category)
                VALUES (?, 'prerequisite_satisfaction_required', 'true', 'boolean', 'migration')
            """, (task_id,))
            self.migration_stats["attributes_created"] += 1
        
        if subtask['file_operations_count'] > 0:
            cursor.execute("""
                INSERT INTO task_attributes (task_id, attribute_name, attribute_value, attribute_type, attribute_category)
                VALUES (?, 'file_operations_count', ?, 'number', 'migration')
            """, (task_id, str(subtask['file_operations_count'])))
            self.migration_stats["attributes_created"] += 1
        
        # Create legacy mapping
        cursor.execute("""
            INSERT INTO legacy_task_mapping (old_task_id, new_task_id, old_task_type, migration_id)
            VALUES (?, ?, 'subtask', ?)
        """, (task_id, task_id, migration_id))
        
        # Create migration event
        cursor.execute("""
            INSERT INTO task_events (task_id, event_type, event_category, event_data, triggered_by)
            VALUES (?, 'migrated', 'system', ?, 'migration')
        """, (task_id, json.dumps({
            "from": "subtask",
            "migration_id": migration_id,
            "original_status": subtask['status']
        })))
        
        self.migration_stats["subtasks_migrated"] += 1
        self.migration_stats["events_created"] += 1
        
        return task_id
    
    def _migrate_artifact(self, conn: sqlite3.Connection, task_id: str, 
                         artifact: Any, index: int) -> None:
        """Migrate an artifact to the new schema."""
        cursor = conn.cursor()
        
        # Determine artifact structure based on type
        if isinstance(artifact, dict):
            artifact_id = f"{task_id}_artifact_{index}"
            artifact_name = artifact.get('name', f'Artifact {index}')
            artifact_type = artifact.get('type', 'general')
            content = artifact.get('content', json.dumps(artifact))
        else:
            artifact_id = f"{task_id}_artifact_{index}"
            artifact_name = f'Artifact {index}'
            artifact_type = 'general'
            content = str(artifact)
        
        cursor.execute("""
            INSERT INTO task_artifacts (
                artifact_id, task_id, artifact_type, artifact_name,
                content, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (artifact_id, task_id, artifact_type, artifact_name, content, index == 0))
    
    def migrate_dependencies(self, conn: sqlite3.Connection) -> None:
        """Migrate subtask dependencies to the new dependency table."""
        cursor = conn.cursor()
        
        # Get all subtasks with dependencies
        cursor.execute("SELECT task_id, dependencies FROM subtasks WHERE dependencies != '[]'")
        subtasks = cursor.fetchall()
        
        for subtask in subtasks:
            dependencies = json.loads(subtask['dependencies'])
            for dep_task_id in dependencies:
                # Check if both tasks exist in generic_tasks
                cursor.execute("""
                    SELECT COUNT(*) as count FROM generic_tasks 
                    WHERE task_id IN (?, ?)
                """, (subtask['task_id'], dep_task_id))
                
                if cursor.fetchone()['count'] == 2:
                    # Create dependency relationship
                    cursor.execute("""
                        INSERT OR IGNORE INTO task_dependencies (
                            dependent_task_id, prerequisite_task_id,
                            dependency_type, dependency_status
                        ) VALUES (?, ?, 'completion', 'pending')
                    """, (subtask['task_id'], dep_task_id))
                    self.migration_stats["dependencies_created"] += 1
    
    def run_migration(self) -> Dict[str, Any]:
        """Execute the complete migration process."""
        logger.info("Starting Generic Task Model migration...")
        
        # Create schema if needed
        schema_path = Path(__file__).parent / "generic_task_schema.sql"
        if schema_path.exists():
            self.execute_schema_sql(str(schema_path))
        
        migration_id = self.create_migration_record("generic_task_model_v2.0")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Migrate task breakdowns
                cursor.execute("SELECT * FROM task_breakdowns ORDER BY created_at")
                task_breakdowns = cursor.fetchall()
                
                for task_breakdown in task_breakdowns:
                    try:
                        parent_id = self.migrate_task_breakdown(conn, migration_id, task_breakdown)
                        
                        # Migrate associated subtasks
                        cursor.execute("""
                            SELECT * FROM subtasks 
                            WHERE parent_task_id = ? 
                            ORDER BY created_at
                        """, (task_breakdown['parent_task_id'],))
                        subtasks = cursor.fetchall()
                        
                        parent_path = f"/{parent_id}"
                        for position, subtask in enumerate(subtasks):
                            self.migrate_subtask(conn, migration_id, subtask, parent_path, position)
                        
                    except Exception as e:
                        logger.error(f"Error migrating task breakdown {task_breakdown['parent_task_id']}: {e}")
                        self.migration_stats["errors"].append({
                            "task_id": task_breakdown['parent_task_id'],
                            "error": str(e)
                        })
                
                # Migrate dependencies after all tasks are migrated
                self.migrate_dependencies(conn)
                
                # Update migration record
                cursor.execute("""
                    UPDATE schema_migrations 
                    SET status = 'completed',
                        completed_at = ?,
                        records_processed = ?,
                        records_failed = ?
                    WHERE migration_id = ?
                """, (
                    datetime.now(),
                    self.migration_stats["task_breakdowns_migrated"] + self.migration_stats["subtasks_migrated"],
                    len(self.migration_stats["errors"]),
                    migration_id
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schema_migrations 
                    SET status = 'failed',
                        error_message = ?
                    WHERE migration_id = ?
                """, (str(e), migration_id))
                conn.commit()
            raise
        
        logger.info(f"Migration completed: {self.migration_stats}")
        return self.migration_stats
    
    def validate_migration(self) -> Dict[str, Any]:
        """Validate the migration results."""
        validation_results = {
            "counts_match": False,
            "dependencies_preserved": False,
            "data_integrity": False,
            "details": {}
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check record counts
            cursor.execute("SELECT COUNT(*) as count FROM task_breakdowns")
            old_breakdowns = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM subtasks")
            old_subtasks = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM generic_tasks")
            new_tasks = cursor.fetchone()['count']
            
            validation_results["counts_match"] = (old_breakdowns + old_subtasks) == new_tasks
            validation_results["details"]["old_total"] = old_breakdowns + old_subtasks
            validation_results["details"]["new_total"] = new_tasks
            
            # Check dependencies
            cursor.execute("SELECT COUNT(*) as count FROM task_dependencies")
            dep_count = cursor.fetchone()['count']
            validation_results["dependencies_preserved"] = dep_count > 0
            validation_results["details"]["dependencies"] = dep_count
            
            # Basic data integrity check
            cursor.execute("""
                SELECT COUNT(*) as orphans FROM generic_tasks 
                WHERE parent_task_id IS NOT NULL 
                AND parent_task_id NOT IN (SELECT task_id FROM generic_tasks)
            """)
            orphans = cursor.fetchone()['orphans']
            validation_results["data_integrity"] = orphans == 0
            validation_results["details"]["orphaned_tasks"] = orphans
        
        return validation_results


def rollback_migration(db_path: str, migration_id: int) -> None:
    """Rollback a specific migration."""
    # This would implement the rollback logic
    # For now, it's a placeholder
    logger.warning("Rollback functionality not yet implemented")
    

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generic_task_migration.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    migration = GenericTaskMigration(db_path)
    
    try:
        results = migration.run_migration()
        print(f"Migration completed successfully: {results}")
        
        validation = migration.validate_migration()
        print(f"Validation results: {validation}")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)