#!/usr/bin/env python3
"""
Test to verify that database connection resource warnings have been resolved.

This test validates that:
1. SQLite connections are properly closed
2. SQLAlchemy engines are properly disposed 
3. No ResourceWarnings are generated during test execution
"""

import sys
import os
import tempfile
import warnings
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from tests.utils.db_test_utils import managed_sqlite_connection, managed_persistence_manager, DatabaseTestCase


def test_sqlite_connection_cleanup():
    """Test that SQLite connections are properly closed."""
    print("Testing SQLite connection cleanup...")
    
    # Track warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Create a temporary database file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Test context manager approach
            with managed_sqlite_connection(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
                cursor.execute("INSERT INTO test VALUES (1, 'test')")
                conn.commit()
            
            # Test manual approach with DatabaseTestCase
            db_test = DatabaseTestCase()
            try:
                conn = db_test.get_managed_connection(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM test")
                rows = cursor.fetchall()
                assert len(rows) == 1
                print(f"✅ Retrieved {len(rows)} rows successfully")
            finally:
                db_test.cleanup_db_resources()
            
            # Check for ResourceWarnings
            resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
            
            if resource_warnings:
                print(f"❌ Found {len(resource_warnings)} ResourceWarnings:")
                for warning in resource_warnings:
                    print(f"  - {warning.message}")
                return False
            else:
                print("✅ No ResourceWarnings found for SQLite connections")
                return True
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(db_path)
            except:
                pass


def test_persistence_manager_cleanup():
    """Test that DatabasePersistenceManager properly disposes of resources."""
    print("Testing DatabasePersistenceManager cleanup...")
    
    # Track warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Create a temporary directory for persistence
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test context manager approach
            with managed_persistence_manager(base_dir=temp_dir) as persistence:
                # Perform some operations
                active_tasks = persistence.get_all_active_tasks()
                print(f"✅ Retrieved {len(active_tasks)} active tasks")
            
            # Test manual approach
            db_test = DatabaseTestCase()
            try:
                persistence = db_test.get_managed_persistence(base_dir=temp_dir)
                # Perform some operations
                active_tasks = persistence.get_all_active_tasks()
                print(f"✅ Retrieved {len(active_tasks)} active tasks with manual approach")
            finally:
                db_test.cleanup_db_resources()
        
        # Check for ResourceWarnings
        resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
        
        if resource_warnings:
            print(f"❌ Found {len(resource_warnings)} ResourceWarnings:")
            for warning in resource_warnings:
                print(f"  - {warning.message}")
            return False
        else:
            print("✅ No ResourceWarnings found for DatabasePersistenceManager")
            return True


def test_migration_script_connections():
    """Test that the migration script properly manages connections."""
    print("Testing migration script connection management...")
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create a test database with migration-eligible data
        with managed_sqlite_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subtasks (
                    task_id TEXT PRIMARY KEY,
                    parent_task_id TEXT,
                    artifacts TEXT
                )
            ''')
            
            # Insert test data
            cursor.execute(
                "INSERT INTO subtasks (task_id, parent_task_id, artifacts) VALUES (?, ?, ?)",
                ('test1', 'parent1', 'test_file.txt')
            )
            conn.commit()
        
        # Import and test the migration
        from scripts.migrations.migrate_artifacts import ArtifactsMigrator
        
        # Track warnings during migration
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            migrator = ArtifactsMigrator(db_path)
            result = migrator.run_migration()
            
            assert result is True, "Migration should succeed"
            print("✅ Migration completed successfully")
            
            # Check for ResourceWarnings
            resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
            
            if resource_warnings:
                print(f"❌ Found {len(resource_warnings)} ResourceWarnings in migration:")
                for warning in resource_warnings:
                    print(f"  - {warning.message}")
                return False
            else:
                print("✅ No ResourceWarnings found in migration script")
                return True
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(db_path)
        except:
            pass


def main():
    """Run all resource cleanup tests."""
    print("=== Testing Database Resource Cleanup ===\n")
    
    tests = [
        test_sqlite_connection_cleanup,
        test_persistence_manager_cleanup,
        test_migration_script_connections
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()  # Add spacing between tests
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {str(e)}")
            results.append(False)
            print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All database resource cleanup tests passed!")
        return True
    else:
        print("❌ Some tests failed - resource cleanup issues still exist")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
