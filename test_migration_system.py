#!/usr/bin/env python3
"""
Test script for the automatic database migration system.

This script validates the core functionality of the migration system
including schema detection, migration execution, and rollback capabilities.
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem, execute_startup_migration
from mcp_task_orchestrator.db.models import Base
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime


def test_basic_migration_detection():
    """Test basic schema detection and migration generation."""
    print("=== Testing Basic Migration Detection ===")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Create empty database
        engine = create_engine(database_url)
        
        # Initialize migration system
        migration_system = AutoMigrationSystem(database_url)
        
        # Check migration status (should need migration)
        status = migration_system.check_migration_status()
        print(f"Migration needed: {status['migration_needed']}")
        print(f"Missing tables: {status['schema_differences']['missing_tables']}")
        print(f"Complexity: {status['migration_complexity']}")
        
        assert status['migration_needed'], "Should detect missing tables"
        assert len(status['schema_differences']['missing_tables']) > 0, "Should find missing tables"
        
        print("✓ Basic migration detection test passed")
        
    except Exception as e:
        print(f"✗ Basic migration detection test failed: {e}")
        raise
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_migration_execution():
    """Test migration execution with backup."""
    print("\n=== Testing Migration Execution ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Create temporary backup directory
        with tempfile.TemporaryDirectory() as backup_dir:
            backup_path = Path(backup_dir)
            
            # Initialize migration system
            migration_system = AutoMigrationSystem(database_url, backup_path)
            
            # Execute migration
            result = migration_system.execute_auto_migration()
            
            print(f"Migration success: {result.success}")
            print(f"Operations executed: {result.operations_executed}")
            print(f"Execution time: {result.execution_time_ms}ms")
            print(f"Backup created: {result.backup_created}")
            
            if result.warnings:
                print(f"Warnings: {result.warnings}")
            
            if result.error_message:
                print(f"Error: {result.error_message}")
            
            assert result.success, f"Migration should succeed: {result.error_message}"
            assert result.migration_needed, "Should have detected migration need"
            assert result.operations_executed > 0, "Should have executed operations"
            
            # Verify tables were created
            engine = create_engine(database_url)
            inspector = engine.inspect(engine)
            table_names = inspector.get_table_names()
            
            print(f"Created tables: {table_names}")
            assert 'task_breakdowns' in table_names, "Should create task_breakdowns table"
            assert 'subtasks' in table_names, "Should create subtasks table"
            assert 'migration_history' in table_names, "Should create migration_history table"
            
            print("✓ Migration execution test passed")
    
    except Exception as e:
        print(f"✗ Migration execution test failed: {e}")
        raise
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_no_migration_needed():
    """Test behavior when no migration is needed."""
    print("\n=== Testing No Migration Needed ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Create database with all tables
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        
        # Initialize migration system
        migration_system = AutoMigrationSystem(database_url)
        
        # Check status
        status = migration_system.check_migration_status()
        print(f"Migration needed: {status['migration_needed']}")
        
        # Execute migration
        result = migration_system.execute_auto_migration()
        print(f"Migration success: {result.success}")
        print(f"Migration needed: {result.migration_needed}")
        print(f"Operations executed: {result.operations_executed}")
        
        assert result.success, "Should succeed even when no migration needed"
        assert not result.migration_needed, "Should detect no migration needed"
        assert result.operations_executed == 0, "Should execute no operations"
        
        print("✓ No migration needed test passed")
    
    except Exception as e:
        print(f"✗ No migration needed test failed: {e}")
        raise
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_startup_migration_function():
    """Test the startup migration convenience function."""
    print("\n=== Testing Startup Migration Function ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Execute startup migration
        result = execute_startup_migration(database_url)
        
        print(f"Startup migration success: {result.success}")
        print(f"Migration needed: {result.migration_needed}")
        print(f"Operations executed: {result.operations_executed}")
        
        assert result.success, f"Startup migration should succeed: {result.error_message}"
        
        print("✓ Startup migration function test passed")
    
    except Exception as e:
        print(f"✗ Startup migration function test failed: {e}")
        raise
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_migration_history():
    """Test migration history tracking."""
    print("\n=== Testing Migration History ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Initialize and run migration
        migration_system = AutoMigrationSystem(database_url)
        result = migration_system.execute_auto_migration()
        
        assert result.success, "Migration should succeed"
        
        # Check migration history
        history = migration_system.history_manager.get_migration_history()
        print(f"Migration history entries: {len(history)}")
        
        if history:
            latest = history[0]
            print(f"Latest migration: {latest['name']} - {latest['status']}")
        
        # Get statistics
        stats = migration_system.history_manager.get_migration_statistics()
        print(f"Total migrations: {stats['total_migrations']}")
        print(f"Success rate: {stats['success_rate']}%")
        
        assert len(history) > 0, "Should have migration history entries"
        assert stats['total_migrations'] > 0, "Should have migration statistics"
        
        print("✓ Migration history test passed")
    
    except Exception as e:
        print(f"✗ Migration history test failed: {e}")
        raise
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_system_health():
    """Test system health reporting."""
    print("\n=== Testing System Health ===")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        database_url = f"sqlite:///{db_path}"
        
        # Initialize and run migration
        migration_system = AutoMigrationSystem(database_url)
        result = migration_system.execute_auto_migration()
        
        assert result.success, "Migration should succeed"
        
        # Get health status
        health = migration_system.get_system_health()
        
        print(f"Overall health: {health['overall_health']}")
        print(f"Health score: {health['health_score']}")
        print(f"Recent failures: {health['recent_failures']}")
        print(f"Recommendations: {health['recommendations']}")
        
        assert health['overall_health'] in ['HEALTHY', 'WARNING', 'CRITICAL'], "Should have valid health status"
        assert 0 <= health['health_score'] <= 100, "Health score should be 0-100"
        assert isinstance(health['recommendations'], list), "Should have recommendations list"
        
        print("✓ System health test passed")
    
    except Exception as e:
        print(f"✗ System health test failed: {e}")
        raise
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def main():
    """Run all tests."""
    print("Starting Migration System Tests")
    print("=" * 50)
    
    try:
        test_basic_migration_detection()
        test_migration_execution()
        test_no_migration_needed()
        test_startup_migration_function()
        test_migration_history()
        test_system_health()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("The automatic database migration system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()