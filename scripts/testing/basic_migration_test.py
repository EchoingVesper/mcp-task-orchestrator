#!/usr/bin/env python3
"""
Basic Database Migration System Test

A simplified test suite that focuses on core migration functionality
without complex dependencies.
"""

import os
import sys
import time
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Test basic imports first
def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
        print("✅ AutoMigrationSystem imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AutoMigrationSystem: {e}")
        return False
    
    try:
        from mcp_task_orchestrator.db.migration_manager import MigrationManager
        print("✅ MigrationManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MigrationManager: {e}")
        return False
    
    try:
        from sqlalchemy import create_engine
        print("✅ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SQLAlchemy: {e}")
        return False
    
    return True


def test_database_creation():
    """Test basic database creation and schema."""
    print("\nTesting database creation...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create basic schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE subtasks (
                task_id TEXT PRIMARY KEY,
                parent_task_id TEXT,
                artifacts TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_task_id) REFERENCES tasks(id)
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO tasks VALUES ('test1', 'Test Task', 'pending', ?)", (datetime.now(),))
        cursor.execute("INSERT INTO subtasks VALUES ('sub1', 'test1', NULL, ?)", (datetime.now(),))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database created successfully at {db_path}")
        return db_path
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        # Clean up
        try:
            os.unlink(db_path)
        except:
            pass
        return None


def test_auto_migration_system(db_path):
    """Test AutoMigrationSystem basic functionality."""
    print("\nTesting AutoMigrationSystem...")
    
    try:
        from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
        
        database_url = f"sqlite:///{db_path}"
        migration_system = AutoMigrationSystem(database_url)
        
        print("✅ AutoMigrationSystem initialized")
        
        # Test status check
        status = migration_system.check_migration_status()
        print(f"Migration status: {status.get('migration_needed', 'Unknown')}")
        print(f"Check time: {status.get('check_time_ms', 'Unknown')}ms")
        
        if 'error' not in status:
            print("✅ Status check successful")
        else:
            print(f"❌ Status check failed: {status.get('error')}")
            return False
        
        # Test migration execution
        result = migration_system.execute_auto_migration()
        print("Migration execution result:")
        print(f"  Success: {result.success}")
        print(f"  Migration needed: {result.migration_needed}")
        print(f"  Execution time: {result.execution_time_ms}ms")
        
        if result.success:
            print("✅ Migration execution successful")
        else:
            print(f"❌ Migration execution failed: {result.error_message}")
            return False
        
        # Test health check
        health = migration_system.get_system_health()
        print(f"System health: {health.get('overall_health', 'Unknown')}")
        
        if health.get('overall_health') in ['HEALTHY', 'WARNING']:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {health}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AutoMigrationSystem test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_migration_manager(db_path):
    """Test MigrationManager functionality."""
    print("\nTesting MigrationManager...")
    
    try:
        from mcp_task_orchestrator.db.migration_manager import MigrationManager
        
        database_url = f"sqlite:///{db_path}"
        migration_manager = MigrationManager(database_url)
        
        print("✅ MigrationManager initialized")
        
        # Test schema difference detection
        differences = migration_manager.detect_schema_differences()
        print("Schema differences detected:")
        print(f"  Missing tables: {len(differences.missing_tables)}")
        print(f"  Extra tables: {len(differences.extra_tables)}")
        print(f"  Table differences: {len(differences.table_differences)}")
        print(f"  Migration needed: {differences.requires_migration}")
        
        print("✅ Schema difference detection successful")
        
        # Test migration history
        history = migration_manager.get_migration_history()
        print(f"Migration history: {len(history)} records")
        
        print("✅ Migration history retrieval successful")
        
        return True
        
    except Exception as e:
        print(f"❌ MigrationManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration_options(db_path):
    """Test configuration options."""
    print("\nTesting configuration options...")
    
    try:
        from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
        
        database_url = f"sqlite:///{db_path}"
        migration_system = AutoMigrationSystem(database_url)
        
        # Test various configurations
        configs = [
            {"auto_backup": True, "max_execution_time_ms": 5000, "dry_run_mode": False},
            {"auto_backup": False, "max_execution_time_ms": 1000, "dry_run_mode": True},
        ]
        
        for i, config in enumerate(configs):
            migration_system.configure(**config)
            print(f"✅ Configuration {i+1} applied successfully")
        
        # Test dry run mode
        migration_system.configure(dry_run_mode=True)
        result = migration_system.execute_auto_migration()
        
        if result.success:
            print("✅ Dry run mode test successful")
        else:
            print(f"❌ Dry run mode test failed: {result.error_message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_error_handling(db_path):
    """Test error handling scenarios."""
    print("\nTesting error handling...")
    
    try:
        from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
        
        # Test with invalid database URL
        try:
            invalid_url = "sqlite:///nonexistent/path/that/does/not/exist.db"
            migration_system = AutoMigrationSystem(invalid_url)
            status = migration_system.check_migration_status()
            
            if 'error' in status:
                print("✅ Invalid database URL handled gracefully")
            else:
                print("❌ Invalid database URL not handled properly")
                return False
                
        except Exception:
            print("✅ Invalid database URL raised exception as expected")
        
        # Test timeout handling
        database_url = f"sqlite:///{db_path}"
        migration_system = AutoMigrationSystem(database_url)
        migration_system.configure(max_execution_time_ms=1)  # Very short timeout
        
        result = migration_system.execute_auto_migration()
        # This should either succeed quickly or fail with timeout
        print("✅ Timeout handling test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def run_performance_test(db_path):
    """Run basic performance tests."""
    print("\nRunning performance tests...")
    
    try:
        from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
        
        database_url = f"sqlite:///{db_path}"
        
        # Add some test data for performance testing
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insert 1000 test records
        test_data = [(f"task_{i}", f"Test Task {i}", "pending") for i in range(1000)]
        cursor.executemany("INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)", test_data)
        conn.commit()
        conn.close()
        
        migration_system = AutoMigrationSystem(database_url)
        
        # Test status check performance
        start_time = time.time()
        status = migration_system.check_migration_status()
        check_time = (time.time() - start_time) * 1000
        
        print(f"Status check with 1000 records: {check_time:.2f}ms")
        
        if check_time < 5000:  # Should be under 5 seconds
            print("✅ Performance test passed")
            return True
        else:
            print("❌ Performance test failed - too slow")
            return False
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def main():
    """Main test runner."""
    print("=" * 60)
    print("BASIC DATABASE MIGRATION SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Python Version: {sys.version}")
    
    test_results = {}
    
    # Run tests
    test_results["imports"] = test_imports()
    
    if test_results["imports"]:
        db_path = test_database_creation()
        if db_path:
            test_results["database_creation"] = True
            test_results["auto_migration_system"] = test_auto_migration_system(db_path)
            test_results["migration_manager"] = test_migration_manager(db_path)
            test_results["configuration_options"] = test_configuration_options(db_path)
            test_results["error_handling"] = test_error_handling(db_path)
            test_results["performance"] = run_performance_test(db_path)
            
            # Clean up
            try:
                os.unlink(db_path)
                print(f"\nCleaned up test database: {db_path}")
            except:
                pass
        else:
            test_results["database_creation"] = False
    else:
        # Skip other tests if imports fail
        for test_name in ["database_creation", "auto_migration_system", "migration_manager", 
                         "configuration_options", "error_handling", "performance"]:
            test_results[test_name] = False
    
    # Generate report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print("\nRecommendations:")
    if failed_tests == 0:
        print("✅ All tests passed! The migration system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the following:")
        for test_name, result in test_results.items():
            if not result:
                print(f"  - {test_name}: Requires investigation")
    
    print(f"\nEnd Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)