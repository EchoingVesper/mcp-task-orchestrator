#!/usr/bin/env python3
"""
Test script for workspace paradigm database migration.

This script tests the database schema migration from session-based to 
workspace-based paradigm, validating all tables, relationships, and data integrity.
"""

import os
import sys
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from mcp_task_orchestrator.db.workspace_migration import WorkspaceMigration, run_workspace_migration
    from mcp_task_orchestrator.orchestrator.directory_detection import DirectoryDetector
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


def create_test_database():
    """Create a test database with sample session-based data."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create existing session-based tables (simplified)
        cursor.execute("""
            CREATE TABLE task_breakdowns (
                parent_task_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                complexity TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE subtasks (
                task_id TEXT PRIMARY KEY,
                parent_task_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                specialist_type TEXT NOT NULL,
                dependencies TEXT DEFAULT '[]',
                estimated_effort TEXT NOT NULL,
                status TEXT NOT NULL,
                results TEXT,
                artifacts TEXT DEFAULT '[]',
                file_operations_count INTEGER DEFAULT 0,
                verification_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                prerequisite_satisfaction_required BOOLEAN DEFAULT FALSE,
                auto_maintenance_enabled BOOLEAN DEFAULT TRUE,
                quality_gate_level TEXT DEFAULT 'standard',
                FOREIGN KEY (parent_task_id) REFERENCES task_breakdowns(parent_task_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE file_operations (
                operation_id TEXT PRIMARY KEY,
                subtask_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                content_hash TEXT,
                file_size INTEGER,
                file_metadata TEXT DEFAULT '{}',
                verification_status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subtask_id) REFERENCES subtasks(task_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE lock_tracking (
                resource_name TEXT PRIMARY KEY,
                locked_at TIMESTAMP NOT NULL,
                locked_by TEXT NOT NULL
            )
        """)
        
        # Insert sample data
        cursor.execute("""
            INSERT INTO task_breakdowns (parent_task_id, description, complexity, context)
            VALUES ('task_123', 'Test task breakdown', 'moderate', 'Test context')
        """)
        
        cursor.execute("""
            INSERT INTO subtasks (
                task_id, parent_task_id, title, description, specialist_type, 
                estimated_effort, status
            ) VALUES (
                'subtask_456', 'task_123', 'Test subtask', 'Test subtask description',
                'implementer', '2 hours', 'pending'
            )
        """)
        
        cursor.execute("""
            INSERT INTO file_operations (
                operation_id, subtask_id, session_id, operation_type, file_path
            ) VALUES (
                'op_789', 'subtask_456', 'session_abc', 'CREATE', '/test/path/file.py'
            )
        """)
        
        cursor.execute("""
            INSERT INTO lock_tracking (resource_name, locked_at, locked_by)
            VALUES ('test_resource', CURRENT_TIMESTAMP, 'test_user')
        """)
        
        conn.commit()
        print(f"Test database created at: {db_path}")
        return db_path
        
    except Exception as e:
        conn.close()
        os.unlink(db_path)
        raise e
    finally:
        conn.close()


def test_workspace_migration():
    """Test the complete workspace migration process."""
    print("=== Testing Workspace Paradigm Migration ===\n")
    
    # Step 1: Create test database with session-based data
    print("1. Creating test database with session-based data...")
    test_db_path = create_test_database()
    
    try:
        # Step 2: Run workspace migration
        print("2. Running workspace migration...")
        db_url = f"sqlite:///{test_db_path}"
        base_dir = str(project_root)
        
        migration_result = run_workspace_migration(db_url=db_url, base_dir=base_dir)
        
        if migration_result['success']:
            print("✓ Migration completed successfully")
            print(f"  Steps completed: {len(migration_result['migration_status']['steps_completed'])}/8")
        else:
            print("✗ Migration failed")
            print(f"  Error: {migration_result['error']}")
            return False
        
        # Step 3: Validate migration results
        print("3. Validating migration results...")
        
        migration = WorkspaceMigration(db_url=db_url, base_dir=base_dir)
        validation_result = migration.validate_migration()
        
        print(f"  Tables created: {'✓' if validation_result['tables_created'] else '✗'}")
        print(f"  Data migrated: {'✓' if validation_result['data_migrated'] else '✗'}")
        print(f"  Workspace detected: {'✓' if validation_result['workspace_detected'] else '✗'}")
        print(f"  Indexes created: {'✓' if validation_result['indexes_created'] else '✗'}")
        print(f"  Total workspaces: {validation_result['total_workspaces']}")
        print(f"  Total workspace tasks: {validation_result['total_workspace_tasks']}")
        
        # Step 4: Test database queries
        print("4. Testing database queries...")
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        try:
            # Test workspace table
            cursor.execute("SELECT COUNT(*) FROM workspaces")
            workspace_count = cursor.fetchone()[0]
            print(f"  Workspaces in database: {workspace_count}")
            
            # Test workspace-task associations
            cursor.execute("SELECT COUNT(*) FROM workspace_tasks")
            association_count = cursor.fetchone()[0]
            print(f"  Workspace-task associations: {association_count}")
            
            # Test updated file operations
            cursor.execute("SELECT COUNT(*) FROM file_operations WHERE workspace_id IS NOT NULL")
            updated_ops = cursor.fetchone()[0]
            print(f"  File operations with workspace_id: {updated_ops}")
            
            # Test backward compatibility view
            cursor.execute("SELECT COUNT(*) FROM session_workspace_mapping")
            mapping_count = cursor.fetchone()[0]
            print(f"  Session-workspace mappings: {mapping_count}")
            
            # Test workspace configuration
            cursor.execute("SELECT COUNT(*) FROM workspace_configurations")
            config_count = cursor.fetchone()[0]
            print(f"  Workspace configurations: {config_count}")
            
        finally:
            conn.close()
        
        # Step 5: Test directory detection integration
        print("5. Testing directory detection integration...")
        try:
            detector = DirectoryDetector(security_checks=True)
            result = detector.detect_project_root(starting_path=base_dir)
            
            print(f"  Detection method: {result.method.value}")
            print(f"  Detection confidence: {result.confidence}/10")
            print(f"  Detected path: {result.detected_path}")
            print(f"  Project markers found: {len(result.project_markers)}")
            print(f"  Git root: {result.git_root or 'Not found'}")
            print(f"  Validation: {'✓' if result.validation.is_valid else '✗'}")
            
        except Exception as e:
            print(f"  Directory detection error: {e}")
        
        print("\n=== Migration Test Summary ===")
        success = (
            migration_result['success'] and
            validation_result['tables_created'] and
            validation_result['data_migrated'] and
            validation_result['indexes_created'] and
            workspace_count > 0 and
            association_count > 0
        )
        
        if success:
            print("✓ All tests passed - Workspace migration is working correctly")
        else:
            print("✗ Some tests failed - Check migration implementation")
            if validation_result['errors']:
                for error in validation_result['errors']:
                    print(f"  Error: {error}")
        
        return success
        
    finally:
        # Cleanup test database
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)
            print(f"\nTest database cleaned up: {test_db_path}")


def test_workspace_detection():
    """Test workspace detection functionality separately."""
    print("\n=== Testing Workspace Detection ===\n")
    
    try:
        detector = DirectoryDetector(security_checks=True)
        
        # Test current directory detection
        result = detector.detect_project_root()
        
        print(f"Current directory detection:")
        print(f"  Path: {result.detected_path}")
        print(f"  Method: {result.method.value}")
        print(f"  Confidence: {result.confidence}/10")
        print(f"  Is valid: {'✓' if result.validation.is_valid else '✗'}")
        print(f"  Is writable: {'✓' if result.validation.is_writable else '✗'}")
        print(f"  Is secure: {'✓' if result.validation.is_secure else '✗'}")
        print(f"  Detection time: {result.detection_time_ms:.2f}ms")
        
        if result.git_root:
            print(f"  Git root: {result.git_root}")
        
        if result.project_markers:
            print(f"  Project markers found ({len(result.project_markers)}):")
            for marker in result.project_markers[:5]:  # Show first 5
                print(f"    - {marker.marker_type}: {marker.file_path.name} (confidence: {marker.confidence})")
        
        if result.validation.warnings:
            print(f"  Warnings:")
            for warning in result.validation.warnings:
                print(f"    - {warning}")
        
        # Test explicit directory detection
        print(f"\nExplicit directory detection (project root):")
        explicit_result = detector.detect_project_root(explicit_directory=str(project_root))
        print(f"  Path: {explicit_result.detected_path}")
        print(f"  Method: {explicit_result.method.value}")
        print(f"  Confidence: {explicit_result.confidence}/10")
        
        return True
        
    except Exception as e:
        print(f"Workspace detection test failed: {e}")
        return False


if __name__ == "__main__":
    print("MCP Task Orchestrator - Workspace Migration Test")
    print("=" * 50)
    
    # Test workspace detection first
    detection_success = test_workspace_detection()
    
    # Test full migration
    migration_success = test_workspace_migration()
    
    # Final result
    overall_success = detection_success and migration_success
    
    print("\n" + "=" * 50)
    if overall_success:
        print("🎉 All workspace migration tests passed!")
        print("The workspace paradigm is ready for implementation.")
    else:
        print("❌ Some tests failed.")
        print("Please review the implementation before proceeding.")
    
    sys.exit(0 if overall_success else 1)