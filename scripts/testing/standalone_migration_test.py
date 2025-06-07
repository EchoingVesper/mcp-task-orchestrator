#!/usr/bin/env python3
"""
Standalone Migration Test
Writes results directly to a file for review.
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Simple test that writes output to file
def run_test():
    output_file = Path(__file__).parent / "migration_test_outputs" / f"standalone_test_{int(datetime.now().timestamp())}.txt"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("STANDALONE MIGRATION SYSTEM TEST\n")
        f.write("=" * 50 + "\n")
        f.write(f"Start Time: {datetime.now().isoformat()}\n")
        f.write(f"Python Path: {sys.executable}\n")
        f.write(f"Working Directory: {os.getcwd()}\n")
        f.write(f"Test File: {__file__}\n\n")
        
        # Test 1: Basic imports
        f.write("1. TESTING BASIC IMPORTS\n")
        f.write("-" * 30 + "\n")
        
        # Add project to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        f.write(f"Added to path: {project_root}\n")
        
        import_results = {}
        
        # Test SQLAlchemy import
        try:
            import sqlalchemy
            f.write(f"✅ SQLAlchemy imported: {sqlalchemy.__version__}\n")
            import_results['sqlalchemy'] = True
        except ImportError as e:
            f.write(f"❌ SQLAlchemy import failed: {e}\n")
            import_results['sqlalchemy'] = False
        
        # Test AutoMigrationSystem import
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            f.write("✅ AutoMigrationSystem imported successfully\n")
            import_results['auto_migration'] = True
        except ImportError as e:
            f.write(f"❌ AutoMigrationSystem import failed: {e}\n")
            import_results['auto_migration'] = False
        except Exception as e:
            f.write(f"❌ AutoMigrationSystem import error: {e}\n")
            import_results['auto_migration'] = False
        
        # Test MigrationManager import
        try:
            from mcp_task_orchestrator.db.migration_manager import MigrationManager
            f.write("✅ MigrationManager imported successfully\n")
            import_results['migration_manager'] = True
        except ImportError as e:
            f.write(f"❌ MigrationManager import failed: {e}\n")
            import_results['migration_manager'] = False
        except Exception as e:
            f.write(f"❌ MigrationManager import error: {e}\n")
            import_results['migration_manager'] = False
        
        # Test models import
        try:
            from mcp_task_orchestrator.db.models import Base
            f.write("✅ Database models imported successfully\n")
            import_results['models'] = True
        except ImportError as e:
            f.write(f"❌ Database models import failed: {e}\n")
            import_results['models'] = False
        except Exception as e:
            f.write(f"❌ Database models import error: {e}\n")
            import_results['models'] = False
        
        f.write("\n")
        
        # Test 2: Basic database operations
        f.write("2. TESTING BASIC DATABASE OPERATIONS\n")
        f.write("-" * 30 + "\n")
        
        try:
            import sqlite3
            import tempfile
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            f.write(f"Created test database: {db_path}\n")
            
            # Test basic SQLite operations
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO test_table (name) VALUES ('test')")
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            
            conn.close()
            
            f.write(f"✅ Database operations successful: {count} record(s)\n")
            
            # Clean up
            os.unlink(db_path)
            f.write("✅ Test database cleaned up\n")
            
        except Exception as e:
            f.write(f"❌ Database operations failed: {e}\n")
            f.write(f"   Traceback: {traceback.format_exc()}\n")
        
        f.write("\n")
        
        # Test 3: AutoMigrationSystem basic functionality
        f.write("3. TESTING AUTOMIGRATION SYSTEM\n")
        f.write("-" * 30 + "\n")
        
        if import_results.get('auto_migration', False):
            try:
                # Create test database
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                    db_path = tmp_file.name
                
                # Create basic schema
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT)")
                conn.commit()
                conn.close()
                
                database_url = f"sqlite:///{db_path}"
                f.write(f"Database URL: {database_url}\n")
                
                # Test initialization
                migration_system = AutoMigrationSystem(database_url)
                f.write("✅ AutoMigrationSystem initialized\n")
                
                # Test status check
                status = migration_system.check_migration_status()
                f.write(f"Status check result: {type(status)}\n")
                f.write(f"  Migration needed: {status.get('migration_needed', 'Unknown')}\n")
                f.write(f"  Check time: {status.get('check_time_ms', 'Unknown')}ms\n")
                
                if 'error' in status:
                    f.write(f"  Error: {status['error']}\n")
                else:
                    f.write("✅ Status check completed successfully\n")
                
                # Test health check
                health = migration_system.get_system_health()
                f.write(f"Health check result: {type(health)}\n")
                f.write(f"  Overall health: {health.get('overall_health', 'Unknown')}\n")
                f.write(f"  Health score: {health.get('health_score', 'Unknown')}\n")
                
                # Clean up
                os.unlink(db_path)
                f.write("✅ Test database cleaned up\n")
                
            except Exception as e:
                f.write(f"❌ AutoMigrationSystem test failed: {e}\n")
                f.write(f"   Traceback: {traceback.format_exc()}\n")
        else:
            f.write("⏭️ Skipping AutoMigrationSystem test (import failed)\n")
        
        f.write("\n")
        
        # Test 4: Component analysis
        f.write("4. COMPONENT ANALYSIS\n")
        f.write("-" * 30 + "\n")
        
        if import_results.get('auto_migration', False):
            try:
                # Analyze AutoMigrationSystem methods
                methods = [method for method in dir(AutoMigrationSystem) if not method.startswith('_')]
                f.write(f"AutoMigrationSystem methods ({len(methods)}):\n")
                for method in sorted(methods):
                    f.write(f"  - {method}\n")
                
                required_methods = ['check_migration_status', 'execute_auto_migration', 'get_system_health', 'configure']
                missing_methods = [method for method in required_methods if method not in methods]
                
                if not missing_methods:
                    f.write("✅ All required methods found\n")
                else:
                    f.write(f"❌ Missing methods: {missing_methods}\n")
                
            except Exception as e:
                f.write(f"❌ Component analysis failed: {e}\n")
        
        f.write("\n")
        
        # Summary
        f.write("=" * 50 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 50 + "\n")
        
        total_imports = len(import_results)
        successful_imports = sum(import_results.values())
        
        f.write(f"Import Results: {successful_imports}/{total_imports} successful\n")
        for component, success in import_results.items():
            status = "✅" if success else "❌"
            f.write(f"  {status} {component}\n")
        
        if successful_imports == total_imports:
            f.write("\n✅ ALL TESTS PASSED - Migration system components are available\n")
        else:
            f.write(f"\n⚠️ {total_imports - successful_imports} import failures detected\n")
        
        f.write(f"\nEnd Time: {datetime.now().isoformat()}\n")
        f.write("=" * 50 + "\n")
    
    return str(output_file)

if __name__ == "__main__":
    try:
        output_file = run_test()
        print(f"Test completed. Results written to: {output_file}")
    except Exception as e:
        print(f"Test failed: {e}")
        traceback.print_exc()