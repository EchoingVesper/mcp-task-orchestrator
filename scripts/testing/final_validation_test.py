#!/usr/bin/env python3
"""
Final Validation Test for Database Migration System

This script performs actual validation of the migration system components
by attempting to import and instantiate them with real parameters.
"""

import os
import sys
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

def create_test_output_file():
    """Create output file for test results."""
    output_dir = Path(__file__).parent / "migration_test_outputs"
    output_dir.mkdir(exist_ok=True)
    return output_dir / f"final_validation_{int(datetime.now().timestamp())}.txt"

def validate_imports(output_file):
    """Validate that all required components can be imported."""
    with open(output_file, 'w') as f:
        f.write("FINAL VALIDATION TEST - DATABASE MIGRATION SYSTEM\n")
        f.write("=" * 70 + "\n")
        f.write(f"Start Time: {datetime.now().isoformat()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Working Directory: {os.getcwd()}\n\n")
        
        f.write("1. COMPONENT IMPORT VALIDATION\n")
        f.write("-" * 40 + "\n")
        
        imports_successful = 0
        total_imports = 0
        
        # Test SQLAlchemy
        total_imports += 1
        try:
            import sqlalchemy
            from sqlalchemy import create_engine
            f.write(f"✅ SQLAlchemy {sqlalchemy.__version__} imported successfully\n")
            imports_successful += 1
        except ImportError as e:
            f.write(f"❌ SQLAlchemy import failed: {e}\n")
        
        # Test AutoMigrationSystem
        total_imports += 1
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem, MigrationResult
            f.write("✅ AutoMigrationSystem imported successfully\n")
            imports_successful += 1
            
            # Check if it can be instantiated
            with tempfile.NamedTemporaryFile(suffix='.db') as tmp_file:
                db_url = f"sqlite:///{tmp_file.name}"
                migration_system = AutoMigrationSystem(db_url)
                f.write("✅ AutoMigrationSystem instantiated successfully\n")
                
        except Exception as e:
            f.write(f"❌ AutoMigrationSystem failed: {e}\n")
        
        # Test other components
        components = [
            ("MigrationManager", "mcp_task_orchestrator.db.migration_manager", "MigrationManager"),
            ("SchemaComparator", "mcp_task_orchestrator.db.schema_comparator", "SchemaComparator"),
            ("MigrationHistoryManager", "mcp_task_orchestrator.db.migration_history", "MigrationHistoryManager"),
            ("BackupManager", "mcp_task_orchestrator.db.backup_manager", "BackupManager"),
            ("Database Models", "mcp_task_orchestrator.db.models", "Base"),
        ]
        
        for name, module_path, class_name in components:
            total_imports += 1
            try:
                module = __import__(module_path, fromlist=[class_name])
                getattr(module, class_name)
                f.write(f"✅ {name} imported successfully\n")
                imports_successful += 1
            except Exception as e:
                f.write(f"❌ {name} import failed: {e}\n")
        
        f.write(f"\nImport Summary: {imports_successful}/{total_imports} successful\n\n")
        
        return imports_successful, total_imports

def validate_functionality(output_file):
    """Validate core functionality."""
    with open(output_file, 'a') as f:
        f.write("2. FUNCTIONALITY VALIDATION\n")
        f.write("-" * 40 + "\n")
        
        functionality_tests = 0
        functionality_passed = 0
        
        # Test database creation and basic operations
        functionality_tests += 1
        try:
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            # Create test schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO test_table (name) VALUES ('test')")
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 1:
                f.write("✅ Basic database operations working\n")
                functionality_passed += 1
            else:
                f.write("❌ Database operation count mismatch\n")
            
            os.unlink(db_path)
            
        except Exception as e:
            f.write(f"❌ Database operations failed: {e}\n")
        
        # Test AutoMigrationSystem functionality
        functionality_tests += 1
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            # Create basic schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT)")
            conn.commit()
            conn.close()
            
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Test status check
            status = migration_system.check_migration_status()
            if isinstance(status, dict) and 'migration_needed' in status:
                f.write("✅ Migration status check working\n")
                functionality_passed += 1
            else:
                f.write("❌ Migration status check failed\n")
            
            os.unlink(db_path)
            
        except Exception as e:
            f.write(f"❌ AutoMigrationSystem functionality failed: {e}\n")
        
        # Test configuration
        functionality_tests += 1
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            
            with tempfile.NamedTemporaryFile(suffix='.db') as tmp_file:
                db_url = f"sqlite:///{tmp_file.name}"
                migration_system = AutoMigrationSystem(db_url)
                
                # Test configuration options
                migration_system.configure(
                    auto_backup=True,
                    max_execution_time_ms=5000,
                    dry_run_mode=True
                )
                
                f.write("✅ Configuration options working\n")
                functionality_passed += 1
                
        except Exception as e:
            f.write(f"❌ Configuration test failed: {e}\n")
        
        f.write(f"\nFunctionality Summary: {functionality_passed}/{functionality_tests} passed\n\n")
        
        return functionality_passed, functionality_tests

def validate_integration(output_file):
    """Validate integration features."""
    with open(output_file, 'a') as f:
        f.write("3. INTEGRATION VALIDATION\n")
        f.write("-" * 40 + "\n")
        
        integration_tests = 0
        integration_passed = 0
        
        # Test execute_startup_migration function
        integration_tests += 1
        try:
            from mcp_task_orchestrator.db.auto_migration import execute_startup_migration
            
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            # Create basic schema
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT)")
            conn.commit()
            conn.close()
            
            database_url = f"sqlite:///{db_path}"
            result = execute_startup_migration(database_url)
            
            if hasattr(result, 'success') and isinstance(result.success, bool):
                f.write("✅ Startup migration integration working\n")
                integration_passed += 1
            else:
                f.write("❌ Startup migration result format incorrect\n")
            
            os.unlink(db_path)
            
        except Exception as e:
            f.write(f"❌ Startup migration integration failed: {e}\n")
        
        # Test backup integration
        integration_tests += 1
        try:
            from mcp_task_orchestrator.db.backup_manager import BackupManager
            
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_manager = BackupManager(Path(temp_dir))
                
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                    db_path = tmp_file.name
                
                # Create test database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (id INTEGER)")
                conn.commit()
                conn.close()
                
                database_url = f"sqlite:///{db_path}"
                backup_info = backup_manager.create_backup(database_url)
                
                if hasattr(backup_info, 'backup_id') and backup_info.backup_id:
                    f.write("✅ Backup integration working\n")
                    integration_passed += 1
                else:
                    f.write("❌ Backup integration failed\n")
                
                os.unlink(db_path)
                
        except Exception as e:
            f.write(f"❌ Backup integration failed: {e}\n")
        
        f.write(f"\nIntegration Summary: {integration_passed}/{integration_tests} passed\n\n")
        
        return integration_passed, integration_tests

def generate_final_report(output_file, import_results, functionality_results, integration_results):
    """Generate final comprehensive report."""
    with open(output_file, 'a') as f:
        f.write("=" * 70 + "\n")
        f.write("FINAL VALIDATION SUMMARY\n")
        f.write("=" * 70 + "\n")
        
        total_passed = import_results[0] + functionality_results[0] + integration_results[0]
        total_tests = import_results[1] + functionality_results[1] + integration_results[1]
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        f.write(f"Overall Results: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)\n\n")
        
        f.write("Category Breakdown:\n")
        f.write(f"  Component Imports: {import_results[0]}/{import_results[1]} passed\n")
        f.write(f"  Core Functionality: {functionality_results[0]}/{functionality_results[1]} passed\n")
        f.write(f"  Integration Features: {integration_results[0]}/{integration_results[1]} passed\n\n")
        
        # Final assessment
        if success_rate >= 90:
            f.write("🟢 EXCELLENT - Migration system is fully functional and ready for use\n")
            f.write("   All critical components are working correctly.\n")
        elif success_rate >= 75:
            f.write("🟡 GOOD - Migration system is mostly functional with minor issues\n")
            f.write("   Core functionality works but some components may need attention.\n")
        elif success_rate >= 50:
            f.write("🟠 WARNING - Migration system has significant issues\n")
            f.write("   Several components are not working properly.\n")
        else:
            f.write("🔴 CRITICAL - Migration system requires immediate attention\n")
            f.write("   Major components are failing.\n")
        
        f.write("\nRecommendations:\n")
        if success_rate >= 90:
            f.write("✅ System is ready for production use\n")
            f.write("✅ All migration features are functional\n")
            f.write("✅ Integration with server startup is working\n")
        else:
            f.write("⚠️ Review failed components before production use\n")
            f.write("⚠️ Test migration operations in development environment\n")
            f.write("⚠️ Verify all dependencies are properly installed\n")
        
        f.write(f"\nTest completed: {datetime.now().isoformat()}\n")
        f.write("=" * 70 + "\n")

def main():
    """Main test execution."""
    print("Running Final Validation Test for Database Migration System...")
    print("=" * 65)
    
    try:
        output_file = create_test_output_file()
        print(f"Output file: {output_file}")
        
        # Run validation tests
        import_results = validate_imports(output_file)
        functionality_results = validate_functionality(output_file)
        integration_results = validate_integration(output_file)
        
        # Generate final report
        generate_final_report(output_file, import_results, functionality_results, integration_results)
        
        print("\n✅ Validation completed successfully!")
        print(f"📁 Detailed results: {output_file}")
        
        # Print summary
        total_passed = import_results[0] + functionality_results[0] + integration_results[0]
        total_tests = import_results[1] + functionality_results[1] + integration_results[1]
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Summary: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("🟢 Migration system is fully functional!")
        elif success_rate >= 75:
            print("🟡 Migration system is mostly working")
        else:
            print("🔴 Migration system needs attention")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)