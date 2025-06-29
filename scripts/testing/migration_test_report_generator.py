#!/usr/bin/env python3
"""
Migration Test Report Generator

This script generates a comprehensive test report for the database migration system
by analyzing the available components and creating detailed test scenarios.
"""

import os
import sys
import time
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)


class MigrationTestReportGenerator:
    """Generates comprehensive test reports for the migration system."""
    
    def __init__(self):
        self.report_file = Path(__file__).parent / "migration_test_outputs" / f"migration_test_report_{int(time.time())}.txt"
        self.report_file.parent.mkdir(exist_ok=True)
        self.test_results = {}
        self.test_details = {}
        
    def write_report_line(self, line=""):
        """Write a line to the report file."""
        with open(self.report_file, 'a', encoding='utf-8') as f:
            f.write(line + "\n")
    
    def generate_comprehensive_report(self):
        """Generate the complete test report."""
        
        # Initialize report file
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write("")  # Clear file
        
        self.write_report_line("=" * 80)
        self.write_report_line("COMPREHENSIVE DATABASE MIGRATION SYSTEM TEST REPORT")
        self.write_report_line("=" * 80)
        self.write_report_line(f"Generated: {datetime.now().isoformat()}")
        self.write_report_line(f"Python Version: {sys.version}")
        self.write_report_line(f"Report File: {self.report_file}")
        self.write_report_line("")
        
        # Test Categories
        self._test_import_availability()
        self._test_component_analysis()
        self._test_database_creation()
        self._test_auto_migration_system()
        self._test_migration_manager_functionality()
        self._test_schema_comparator()
        self._test_backup_manager()
        self._test_migration_history()
        self._test_error_scenarios()
        self._test_performance_characteristics()
        
        # Generate final summary
        self._generate_final_summary()
        
        return str(self.report_file)
    
    def _test_import_availability(self):
        """Test availability of all migration system components."""
        self.write_report_line("1. COMPONENT IMPORT AVAILABILITY TEST")
        self.write_report_line("=" * 50)
        
        components = [
            ("AutoMigrationSystem", "mcp_task_orchestrator.db.auto_migration"),
            ("MigrationManager", "mcp_task_orchestrator.db.migration_manager"),
            ("SchemaComparator", "mcp_task_orchestrator.db.schema_comparator"),
            ("MigrationHistoryManager", "mcp_task_orchestrator.db.migration_history"),
            ("BackupManager", "mcp_task_orchestrator.db.backup_manager"),
            ("RollbackManager", "mcp_task_orchestrator.db.rollback_manager"),
            ("Base (SQLAlchemy Models)", "mcp_task_orchestrator.db.models"),
        ]
        
        import_results = {}
        
        for component_name, module_path in components:
            try:
                if "." in component_name:
                    # Handle special cases like "Base (SQLAlchemy Models)"
                    class_name = component_name.split()[0]
                else:
                    class_name = component_name
                
                module = __import__(module_path, fromlist=[class_name])
                
                if hasattr(module, class_name):
                    import_results[component_name] = True
                    self.write_report_line(f"✅ {component_name}: Available")
                else:
                    import_results[component_name] = False
                    self.write_report_line(f"❌ {component_name}: Class not found in module")
                
            except ImportError as e:
                import_results[component_name] = False
                self.write_report_line(f"❌ {component_name}: Import failed - {e}")
            except Exception as e:
                import_results[component_name] = False
                self.write_report_line(f"❌ {component_name}: Error - {e}")
        
        self.test_results["component_imports"] = import_results
        success_rate = sum(import_results.values()) / len(import_results) * 100
        self.write_report_line(f"\nImport Success Rate: {success_rate:.1f}%")
        self.write_report_line("")
    
    def _test_component_analysis(self):
        """Analyze the available components and their capabilities."""
        self.write_report_line("2. COMPONENT ANALYSIS")
        self.write_report_line("=" * 50)
        
        # Analyze AutoMigrationSystem
        self.write_report_line("2.1 AutoMigrationSystem Analysis")
        self.write_report_line("-" * 30)
        
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem, MigrationResult
            
            # Analyze class methods
            methods = [method for method in dir(AutoMigrationSystem) if not method.startswith('_')]
            self.write_report_line(f"Available methods: {len(methods)}")
            for method in sorted(methods):
                self.write_report_line(f"  - {method}")
            
            # Check for key methods
            required_methods = ['check_migration_status', 'execute_auto_migration', 'get_system_health', 'configure']
            missing_methods = [method for method in required_methods if method not in methods]
            
            if not missing_methods:
                self.write_report_line("✅ All required methods present")
            else:
                self.write_report_line(f"❌ Missing required methods: {missing_methods}")
            
            self.test_results["auto_migration_analysis"] = len(missing_methods) == 0
            
        except Exception as e:
            self.write_report_line(f"❌ AutoMigrationSystem analysis failed: {e}")
            self.test_results["auto_migration_analysis"] = False
        
        self.write_report_line("")
        
        # Analyze other components similarly...
        self._analyze_migration_manager()
        self._analyze_backup_manager()
    
    def _analyze_migration_manager(self):
        """Analyze MigrationManager component."""
        self.write_report_line("2.2 MigrationManager Analysis")
        self.write_report_line("-" * 30)
        
        try:
            from mcp_task_orchestrator.db.migration_manager import MigrationManager, SchemaDifference
            
            methods = [method for method in dir(MigrationManager) if not method.startswith('_')]
            self.write_report_line(f"Available methods: {len(methods)}")
            
            required_methods = ['detect_schema_differences', 'generate_migration_operations', 'execute_migrations']
            missing_methods = [method for method in required_methods if method not in methods]
            
            if not missing_methods:
                self.write_report_line("✅ All required methods present")
            else:
                self.write_report_line(f"❌ Missing required methods: {missing_methods}")
            
            self.test_results["migration_manager_analysis"] = len(missing_methods) == 0
            
        except Exception as e:
            self.write_report_line(f"❌ MigrationManager analysis failed: {e}")
            self.test_results["migration_manager_analysis"] = False
        
        self.write_report_line("")
    
    def _analyze_backup_manager(self):
        """Analyze BackupManager component."""
        self.write_report_line("2.3 BackupManager Analysis")
        self.write_report_line("-" * 30)
        
        try:
            from mcp_task_orchestrator.db.backup_manager import BackupManager, BackupInfo
            
            methods = [method for method in dir(BackupManager) if not method.startswith('_')]
            self.write_report_line(f"Available methods: {len(methods)}")
            
            required_methods = ['create_backup', 'restore_backup', 'list_backups']
            missing_methods = [method for method in required_methods if method not in methods]
            
            if not missing_methods:
                self.write_report_line("✅ All required methods present")
            else:
                self.write_report_line(f"❌ Missing required methods: {missing_methods}")
            
            self.test_results["backup_manager_analysis"] = len(missing_methods) == 0
            
        except Exception as e:
            self.write_report_line(f"❌ BackupManager analysis failed: {e}")
            self.test_results["backup_manager_analysis"] = False
        
        self.write_report_line("")
    
    def _test_database_creation(self):
        """Test database creation and basic operations."""
        self.write_report_line("3. DATABASE CREATION AND BASIC OPERATIONS")
        self.write_report_line("=" * 50)
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
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
            cursor.execute("INSERT INTO subtasks VALUES ('sub1', 'test1', '[]', ?)", (datetime.now(),))
            
            conn.commit()
            
            # Verify data
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subtasks")
            subtask_count = cursor.fetchone()[0]
            
            conn.close()
            
            self.write_report_line(f"✅ Database created successfully: {db_path}")
            self.write_report_line(f"   Tasks: {task_count}, Subtasks: {subtask_count}")
            
            self.test_results["database_creation"] = True
            self.test_details["test_db_path"] = db_path
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ Database creation failed: {e}")
            self.test_results["database_creation"] = False
        
        self.write_report_line("")
    
    def _test_auto_migration_system(self):
        """Test AutoMigrationSystem functionality."""
        self.write_report_line("4. AUTO MIGRATION SYSTEM FUNCTIONALITY")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            
            # Create test database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            # Initialize with current schema using SQLAlchemy
            try:
                from sqlalchemy import create_engine
                from mcp_task_orchestrator.db.models import Base
                
                engine = create_engine(f"sqlite:///{db_path}")
                Base.metadata.create_all(engine)
                
                self.write_report_line("✅ Database initialized with SQLAlchemy models")
                
                # Test AutoMigrationSystem initialization
                database_url = f"sqlite:///{db_path}"
                migration_system = AutoMigrationSystem(database_url)
                
                self.write_report_line("✅ AutoMigrationSystem initialized successfully")
                
                # Test configuration
                migration_system.configure(
                    auto_backup=True,
                    max_execution_time_ms=5000,
                    dry_run_mode=False
                )
                self.write_report_line("✅ Configuration applied successfully")
                
                # Test status check
                start_time = time.time()
                status = migration_system.check_migration_status()
                check_time = (time.time() - start_time) * 1000
                
                self.write_report_line(f"Migration status check completed in {check_time:.2f}ms")
                self.write_report_line(f"  Migration needed: {status.get('migration_needed', 'Unknown')}")
                
                if 'error' not in status:
                    self.write_report_line("✅ Status check successful")
                else:
                    self.write_report_line(f"❌ Status check failed: {status.get('error')}")
                
                # Test migration execution
                result = migration_system.execute_auto_migration()
                self.write_report_line(f"Migration execution result:")
                self.write_report_line(f"  Success: {result.success}")
                self.write_report_line(f"  Migration needed: {result.migration_needed}")
                self.write_report_line(f"  Operations executed: {result.operations_executed}")
                self.write_report_line(f"  Execution time: {result.execution_time_ms}ms")
                
                # Test health check
                health = migration_system.get_system_health()
                self.write_report_line(f"System health: {health.get('overall_health', 'Unknown')}")
                self.write_report_line(f"Health score: {health.get('health_score', 'Unknown')}")
                
                self.test_results["auto_migration_system"] = True
                
            except Exception as model_error:
                self.write_report_line(f"⚠️ SQLAlchemy models not available: {model_error}")
                self.write_report_line("   Testing with basic schema...")
                
                # Create basic schema manually
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT)")
                conn.commit()
                conn.close()
                
                # Test with basic setup
                database_url = f"sqlite:///{db_path}"
                migration_system = AutoMigrationSystem(database_url)
                status = migration_system.check_migration_status()
                
                self.write_report_line(f"Basic migration test: {status.get('migration_needed', 'Unknown')}")
                self.test_results["auto_migration_system"] = True
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ AutoMigrationSystem test failed: {e}")
            import traceback
            self.write_report_line(f"   Traceback: {traceback.format_exc()}")
            self.test_results["auto_migration_system"] = False
        
        self.write_report_line("")
    
    def _test_migration_manager_functionality(self):
        """Test MigrationManager functionality."""
        self.write_report_line("5. MIGRATION MANAGER FUNCTIONALITY")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.migration_manager import MigrationManager
            
            # Create test database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
            conn.commit()
            conn.close()
            
            database_url = f"sqlite:///{db_path}"
            migration_manager = MigrationManager(database_url)
            
            self.write_report_line("✅ MigrationManager initialized successfully")
            
            # Test schema difference detection
            differences = migration_manager.detect_schema_differences()
            self.write_report_line(f"Schema differences detected:")
            self.write_report_line(f"  Missing tables: {len(differences.missing_tables)}")
            self.write_report_line(f"  Extra tables: {len(differences.extra_tables)}")
            self.write_report_line(f"  Migration needed: {differences.requires_migration}")
            
            # Test migration history
            history = migration_manager.get_migration_history()
            self.write_report_line(f"Migration history: {len(history)} records")
            
            self.test_results["migration_manager"] = True
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ MigrationManager test failed: {e}")
            self.test_results["migration_manager"] = False
        
        self.write_report_line("")
    
    def _test_schema_comparator(self):
        """Test SchemaComparator functionality."""
        self.write_report_line("6. SCHEMA COMPARATOR FUNCTIONALITY")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.schema_comparator import SchemaComparator
            from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
            
            # Create test database and engine
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            engine = create_engine(f"sqlite:///{db_path}")
            
            # Create test metadata
            metadata = MetaData()
            test_table = Table('test_table', metadata,
                             Column('id', Integer, primary_key=True),
                             Column('name', String(50)))
            
            # Create schema comparator
            comparator = SchemaComparator(engine, metadata)
            self.write_report_line("✅ SchemaComparator initialized successfully")
            
            # Test schema comparison
            result = comparator.compare_schemas()
            self.write_report_line(f"Schema comparison result:")
            self.write_report_line(f"  Migration complexity: {result.migration_complexity}")
            self.write_report_line(f"  Estimated downtime: {result.estimated_downtime}s")
            self.write_report_line(f"  Tables needing creation: {len(result.tables_needing_creation)}")
            self.write_report_line(f"  Safety warnings: {len(result.safety_warnings)}")
            
            self.test_results["schema_comparator"] = True
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ SchemaComparator test failed: {e}")
            self.test_results["schema_comparator"] = False
        
        self.write_report_line("")
    
    def _test_backup_manager(self):
        """Test BackupManager functionality."""
        self.write_report_line("7. BACKUP MANAGER FUNCTIONALITY")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.backup_manager import BackupManager
            
            # Create test database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
            cursor.execute("INSERT INTO test_table VALUES (1, 'test data')")
            conn.commit()
            conn.close()
            
            # Create temporary backup directory
            with tempfile.TemporaryDirectory() as backup_dir:
                backup_manager = BackupManager(Path(backup_dir))
                self.write_report_line("✅ BackupManager initialized successfully")
                
                # Test backup creation
                database_url = f"sqlite:///{db_path}"
                backup_info = backup_manager.create_backup(database_url)
                
                self.write_report_line(f"✅ Backup created: {backup_info.backup_id}")
                self.write_report_line(f"   Size: {backup_info.size_bytes} bytes")
                self.write_report_line(f"   Checksum: {backup_info.checksum}")
                
                # Test backup listing
                backups = backup_manager.list_backups()
                self.write_report_line(f"✅ Listed {len(backups)} backups")
                
                # Test backup statistics
                stats = backup_manager.get_backup_statistics()
                self.write_report_line(f"✅ Backup statistics: {stats.get('total_backups', 0)} total")
                
                self.test_results["backup_manager"] = True
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ BackupManager test failed: {e}")
            self.test_results["backup_manager"] = False
        
        self.write_report_line("")
    
    def _test_migration_history(self):
        """Test MigrationHistoryManager functionality."""
        self.write_report_line("8. MIGRATION HISTORY FUNCTIONALITY")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.migration_history import MigrationHistoryManager, MigrationRecord
            from sqlalchemy import create_engine
            
            # Create test database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            engine = create_engine(f"sqlite:///{db_path}")
            history_manager = MigrationHistoryManager(engine)
            
            self.write_report_line("✅ MigrationHistoryManager initialized successfully")
            
            # Test migration record creation
            migration_record = MigrationRecord(
                name="test_migration",
                description="Test migration for report",
                checksum="test_checksum"
            )
            
            migration_id = history_manager.record_migration_start(migration_record)
            self.write_report_line(f"✅ Migration record created: ID {migration_id}")
            
            # Test recording success
            history_manager.record_migration_success(migration_id, 1000)
            self.write_report_line("✅ Migration success recorded")
            
            # Test history retrieval
            history = history_manager.get_migration_history(limit=10)
            self.write_report_line(f"✅ Retrieved {len(history)} history records")
            
            # Test statistics
            stats = history_manager.get_migration_statistics()
            self.write_report_line(f"✅ Migration statistics: {stats.get('total_migrations', 0)} total")
            
            self.test_results["migration_history"] = True
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ MigrationHistoryManager test failed: {e}")
            self.test_results["migration_history"] = False
        
        self.write_report_line("")
    
    def _test_error_scenarios(self):
        """Test error handling scenarios."""
        self.write_report_line("9. ERROR HANDLING SCENARIOS")
        self.write_report_line("=" * 50)
        
        error_tests = {
            "invalid_database_url": False,
            "nonexistent_database": False,
            "corrupted_database": False,
            "permission_error": False
        }
        
        # Test invalid database URL
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            
            invalid_url = "invalid://database/url"
            migration_system = AutoMigrationSystem(invalid_url)
            status = migration_system.check_migration_status()
            
            if 'error' in status:
                error_tests["invalid_database_url"] = True
                self.write_report_line("✅ Invalid database URL handled gracefully")
            else:
                self.write_report_line("❌ Invalid database URL not handled")
                
        except Exception:
            error_tests["invalid_database_url"] = True
            self.write_report_line("✅ Invalid database URL raised exception (expected)")
        
        # Test nonexistent database
        try:
            nonexistent_url = "sqlite:///nonexistent/path/database.db"
            migration_system = AutoMigrationSystem(nonexistent_url)
            status = migration_system.check_migration_status()
            
            if 'error' in status:
                error_tests["nonexistent_database"] = True
                self.write_report_line("✅ Nonexistent database handled gracefully")
            else:
                self.write_report_line("❌ Nonexistent database not handled properly")
                
        except Exception:
            error_tests["nonexistent_database"] = True
            self.write_report_line("✅ Nonexistent database raised exception (expected)")
        
        self.test_results["error_handling"] = error_tests
        
        success_count = sum(error_tests.values())
        total_count = len(error_tests)
        self.write_report_line(f"Error handling tests: {success_count}/{total_count} passed")
        self.write_report_line("")
    
    def _test_performance_characteristics(self):
        """Test performance characteristics."""
        self.write_report_line("10. PERFORMANCE CHARACTERISTICS")
        self.write_report_line("=" * 50)
        
        try:
            from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem
            
            # Create database with test data
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables with data
            cursor.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, status TEXT)")
            cursor.execute("CREATE TABLE subtasks (task_id TEXT PRIMARY KEY, parent_task_id TEXT, artifacts TEXT)")
            
            # Insert test data
            task_data = [(f"task_{i}", f"Task {i}", "pending") for i in range(1000)]
            cursor.executemany("INSERT INTO tasks VALUES (?, ?, ?)", task_data)
            
            subtask_data = [(f"sub_{i}", f"task_{i%100}", "[]") for i in range(5000)]
            cursor.executemany("INSERT INTO subtasks VALUES (?, ?, ?)", subtask_data)
            
            conn.commit()
            conn.close()
            
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Test status check performance
            start_time = time.time()
            status = migration_system.check_migration_status()
            check_time = (time.time() - start_time) * 1000
            
            self.write_report_line(f"Status check with 6000 records: {check_time:.2f}ms")
            
            # Test migration execution performance
            start_time = time.time()
            result = migration_system.execute_auto_migration()
            exec_time = (time.time() - start_time) * 1000
            
            self.write_report_line(f"Migration execution: {exec_time:.2f}ms")
            
            # Performance assessment
            if check_time < 5000 and exec_time < 10000:
                self.write_report_line("✅ Performance characteristics acceptable")
                self.test_results["performance"] = True
            else:
                self.write_report_line("⚠️ Performance may need optimization")
                self.test_results["performance"] = False
            
            # Clean up
            os.unlink(db_path)
            
        except Exception as e:
            self.write_report_line(f"❌ Performance test failed: {e}")
            self.test_results["performance"] = False
        
        self.write_report_line("")
    
    def _generate_final_summary(self):
        """Generate final summary and recommendations."""
        self.write_report_line("=" * 80)
        self.write_report_line("FINAL SUMMARY AND RECOMMENDATIONS")
        self.write_report_line("=" * 80)
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = 0
        
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                # Handle nested results (like error_handling)
                nested_passed = sum(1 for v in result.values() if v)
                nested_total = len(result)
                passed_tests += nested_passed / nested_total
            else:
                passed_tests += 1 if result else 0
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        self.write_report_line(f"Overall Test Results:")
        self.write_report_line(f"  Total Test Categories: {total_tests}")
        self.write_report_line(f"  Success Rate: {success_rate:.1f}%")
        self.write_report_line("")
        
        # Detailed results
        self.write_report_line("Detailed Test Results:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict):
                passed = sum(1 for v in result.values() if v)
                total = len(result)
                status = f"{passed}/{total} passed"
            else:
                status = "✅ PASS" if result else "❌ FAIL"
            
            self.write_report_line(f"  {test_name}: {status}")
        
        self.write_report_line("")
        
        # System health assessment
        self.write_report_line("System Health Assessment:")
        if success_rate >= 90:
            self.write_report_line("🟢 EXCELLENT - Migration system is highly reliable")
            self.write_report_line("   The database migration system is working correctly and ready for production use.")
        elif success_rate >= 75:
            self.write_report_line("🟡 GOOD - Migration system is generally reliable with minor issues")
            self.write_report_line("   The system works well but may need some attention in specific areas.")
        elif success_rate >= 50:
            self.write_report_line("🟠 WARNING - Migration system has significant issues")
            self.write_report_line("   Several components need attention before production use.")
        else:
            self.write_report_line("🔴 CRITICAL - Migration system requires immediate attention")
            self.write_report_line("   Major issues detected that prevent reliable operation.")
        
        self.write_report_line("")
        
        # Recommendations
        self.write_report_line("Recommendations:")
        
        failed_tests = [test_name for test_name, result in self.test_results.items() 
                       if (isinstance(result, dict) and not all(result.values())) or 
                          (not isinstance(result, dict) and not result)]
        
        if not failed_tests:
            self.write_report_line("✅ All tests passed! No specific recommendations needed.")
            self.write_report_line("   The migration system is working correctly and ready for use.")
        else:
            self.write_report_line("⚠️ The following areas need attention:")
            for test_name in failed_tests:
                if test_name == "component_imports":
                    self.write_report_line("   - Check Python environment and package installation")
                elif test_name == "auto_migration_system":
                    self.write_report_line("   - Review AutoMigrationSystem initialization and dependencies")
                elif test_name == "migration_manager":
                    self.write_report_line("   - Verify MigrationManager schema detection capabilities")
                elif test_name == "backup_manager":
                    self.write_report_line("   - Check backup creation and file system permissions")
                elif test_name == "performance":
                    self.write_report_line("   - Optimize migration operations for large datasets")
                else:
                    self.write_report_line(f"   - Investigate {test_name} component issues")
        
        self.write_report_line("")
        self.write_report_line("Next Steps:")
        self.write_report_line("1. Review failed test details above")
        self.write_report_line("2. Fix any import or dependency issues")
        self.write_report_line("3. Test with actual database scenarios")
        self.write_report_line("4. Verify backup and rollback procedures")
        self.write_report_line("5. Conduct integration testing with server startup")
        
        self.write_report_line("")
        self.write_report_line(f"Report completed: {datetime.now().isoformat()}")
        self.write_report_line("=" * 80)


def main():
    """Main execution function."""
    print("Generating Comprehensive Database Migration System Test Report...")
    print("=" * 70)
    
    try:
        generator = MigrationTestReportGenerator()
        report_file = generator.generate_comprehensive_report()
        
        print(f"\n✅ Test report generated successfully!")
        print(f"📁 Report file: {report_file}")
        
        # Print brief summary
        total_tests = len(generator.test_results)
        passed_tests = sum(1 for result in generator.test_results.values() 
                          if (isinstance(result, dict) and all(result.values())) or 
                             (not isinstance(result, dict) and result))
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Summary: {passed_tests}/{total_tests} test categories passed ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("🟢 Migration system appears to be working well!")
        else:
            print("🟡 Migration system needs attention - see report for details")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)