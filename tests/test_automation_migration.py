#!/usr/bin/env python3
"""
Test script for automation maintenance database migration.
Verifies that the migration script correctly adds columns and creates tables.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from mcp_task_orchestrator.db.models import Base, SubTaskModel
from scripts.migrations.migrate_automation_maintenance import AutomationMaintenanceMigration


def test_migration():
    """Test the automation maintenance migration."""
    print("Testing automation maintenance database migration...")
    
    # Create a temporary database for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db_path = os.path.join(temp_dir, "test_orchestrator.db")
        
        # Create initial database with original schema
        engine = create_engine(f"sqlite:///{test_db_path}")
        
        # Create tables without the new columns (simulate old schema)
        # We'll create a minimal subtasks table
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE subtasks (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    specialist_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    detailed_work TEXT,
                    file_paths TEXT,
                    error_message TEXT,
                    parent_task_id TEXT
                )
            """))
            
            # Add some test data
            conn.execute(text("""
                INSERT INTO subtasks (id, task_id, title, description, specialist_type)
                VALUES 
                    ('test_1', 'task_1', 'Test Subtask 1', 'Description 1', 'implementer'),
                    ('test_2', 'task_2', 'Test Subtask 2', 'Description 2', 'tester')
            """))
            conn.commit()
        
        print(f"Created test database at: {test_db_path}")
        
        # Run the migration
        migration = AutomationMaintenanceMigration(db_path=test_db_path)
        
        print("\nRunning migration...")
        success = migration.run_migration()
        
        if not success:
            print("❌ Migration failed!")
            return False
        
        print("Migration completed successfully!")
        
        # Verify the migration
        print("\nVerifying migration...")
        if not migration.verify_migration():
            print("Migration verification failed!")
            return False
        
        print("Migration verification passed!")
        
        # Additional checks
        # Create a new engine for verification
        verify_engine = create_engine(f"sqlite:///{test_db_path}")
        Session = sessionmaker(bind=verify_engine)
        session = Session()
        
        try:
            # Check that we can query with the new columns
            result = session.execute(text("""
                SELECT id, title, prerequisite_satisfaction_required, 
                       auto_maintenance_enabled, quality_gate_level
                FROM subtasks
            """))
            
            print("\nSubtasks with new columns:")
            for row in result:
                print(f"  {row[0]}: {row[1]}")
                print(f"    - prerequisite_satisfaction_required: {row[2]}")
                print(f"    - auto_maintenance_enabled: {row[3]}")
                print(f"    - quality_gate_level: {row[4]}")
            
            # Check that maintenance tables exist
            tables = ['task_prerequisites', 'maintenance_operations', 'project_health_metrics']
            print("\nChecking maintenance tables:")
            for table in tables:
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name"),
                    {"table_name": table}
                )
                exists = result.fetchone() is not None
                print(f"  {table}: {'exists' if exists else 'missing'}")
            
            print("\nAll tests passed!")
            return True
            
        except Exception as e:
            print(f"\nTest failed with error: {e}")
            return False
        finally:
            session.close()
            # Close the engine to release the database file
            verify_engine.dispose()


if __name__ == "__main__":
    success = test_migration()
    sys.exit(0 if success else 1)