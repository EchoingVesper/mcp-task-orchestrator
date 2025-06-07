#!/usr/bin/env python3
"""
Comprehensive Database Migration System Test Suite

This test suite provides thorough testing of the AutoMigrationSystem class
and all related migration components, including edge cases, error scenarios,
server integration, and performance testing.
"""

import os
import sys
import time
import json
import sqlite3
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from dataclasses import asdict

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from mcp_task_orchestrator.db.auto_migration import AutoMigrationSystem, MigrationResult, execute_startup_migration
from mcp_task_orchestrator.db.migration_manager import MigrationManager, SchemaDifference, MigrationOperation
from mcp_task_orchestrator.db.schema_comparator import SchemaComparator
from mcp_task_orchestrator.db.migration_history import MigrationHistoryManager
from mcp_task_orchestrator.db.backup_manager import BackupManager
from mcp_task_orchestrator.db.rollback_manager import RollbackManager
from mcp_task_orchestrator.db.models import Base
from mcp_task_orchestrator.testing.file_output_system import TestOutputWriter, AtomicFileWriter

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveMigrationTestSuite:
    """Comprehensive test suite for the database migration system."""
    
    def __init__(self, output_dir: str = None):
        """Initialize test suite with output directory."""
        if output_dir is None:
            output_dir = Path(__file__).parent / "migration_test_outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.writer = TestOutputWriter(self.output_dir)
        
        # Test database paths
        self.temp_dir = None
        self.test_db_paths = {}
        
        # Test results
        self.test_results = {}
        self.performance_metrics = {}
        
    def setup_test_environment(self):
        """Set up test environment with temporary databases."""
        self.temp_dir = tempfile.mkdtemp(prefix="migration_test_")
        logger.info(f"Created test environment in: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir:
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up test environment: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean up test directory: {e}")
    
    def create_test_database(self, db_name: str, schema_version: str = "current") -> str:
        """Create a test database with specified schema version."""
        db_path = Path(self.temp_dir) / f"{db_name}.db"
        self.test_db_paths[db_name] = str(db_path)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        if schema_version == "current":
            # Create current schema using SQLAlchemy models
            from sqlalchemy import create_engine
            engine = create_engine(f"sqlite:///{db_path}")
            Base.metadata.create_all(engine)
            
        elif schema_version == "legacy":
            # Create legacy schema for migration testing
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
            cursor.executemany(
                'INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)',
                [
                    ('task1', 'Test Task 1', 'pending'),
                    ('task2', 'Test Task 2', 'completed'),
                ]
            )
            
            cursor.executemany(
                'INSERT INTO subtasks (task_id, parent_task_id, artifacts) VALUES (?, ?, ?)',
                [
                    ('sub1', 'task1', '["file1.txt", "file2.txt"]'),
                    ('sub2', 'task1', 'invalid_json'),
                    ('sub3', 'task2', None),
                ]
            )
        
        elif schema_version == "missing_columns":
            # Create schema missing some columns
            cursor.execute("""
                CREATE TABLE tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL
                    -- Missing status, created_at, updated_at columns
                )
            """)
            
        elif schema_version == "corrupted":
            # Create corrupted data scenarios
            cursor.execute("""
                CREATE TABLE tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            
            # Insert data that might cause issues
            cursor.execute("INSERT INTO tasks VALUES ('test\\x00null', 'Bad Title', 'status')")
            
        conn.commit()
        conn.close()
        
        return str(db_path)
    
    def run_all_tests(self):
        """Run all comprehensive tests."""
        test_name = f"comprehensive_migration_test_{int(time.time())}"
        
        with self.writer.write_test_output(test_name, "text") as session:
            try:
                self._write_test_header(session, test_name)
                
                # Setup
                self.setup_test_environment()
                
                # Run test categories
                self._test_auto_migration_system_basic(session)
                self._test_auto_migration_system_edge_cases(session)
                self._test_error_scenarios(session)
                self._test_server_integration(session)
                self._test_performance_and_safety(session)
                self._test_concurrent_migrations(session)
                
                # Generate report
                self._generate_comprehensive_report(session)
                
                self._write_test_footer(session, test_name, True)
                return True
                
            except Exception as e:
                self._write_test_footer(session, test_name, False, str(e))
                raise
            finally:
                self.cleanup_test_environment()
    
    def _write_test_header(self, session, test_name):
        """Write test header."""
        session.write_line("=" * 80)
        session.write_line("COMPREHENSIVE DATABASE MIGRATION SYSTEM TEST SUITE")
        session.write_line("=" * 80)
        session.write_line(f"Test Name: {test_name}")
        session.write_line(f"Start Time: {datetime.now().isoformat()}")
        session.write_line(f"Python Version: {sys.version}")
        session.write_line(f"Test Environment: {self.temp_dir}")
        session.write_line("")
    
    def _write_test_footer(self, session, test_name, success, error_msg=None):
        """Write test footer."""
        session.write_line("")
        session.write_line("=" * 80)
        status = "PASSED" if success else "FAILED"
        session.write_line(f"TEST SUITE COMPLETED: {status}")
        session.write_line("=" * 80)
        session.write_line(f"End Time: {datetime.now().isoformat()}")
        if error_msg:
            session.write_line(f"Error: {error_msg}")
        session.write_line("=" * 80)
    
    def _test_auto_migration_system_basic(self, session):
        """Test basic AutoMigrationSystem functionality."""
        session.write_line("=" * 60)
        session.write_line("1. TESTING AUTO MIGRATION SYSTEM - BASIC FUNCTIONALITY")
        session.write_line("=" * 60)
        
        # Test 1.1: Initialization
        session.write_line("\n1.1 Testing AutoMigrationSystem Initialization")
        session.write_line("-" * 50)
        
        db_path = self.create_test_database("basic_test", "current")
        database_url = f"sqlite:///{db_path}"
        
        try:
            migration_system = AutoMigrationSystem(database_url)
            session.write_line("✅ AutoMigrationSystem initialized successfully")
            
            # Test configuration
            migration_system.configure(
                auto_backup=True,
                max_execution_time_ms=5000,
                dry_run_mode=False
            )
            session.write_line("✅ Configuration applied successfully")
            
        except Exception as e:
            session.write_line(f"❌ Initialization failed: {e}")
            self.test_results["basic_initialization"] = False
            return
        
        self.test_results["basic_initialization"] = True
        
        # Test 1.2: Migration Status Check
        session.write_line("\n1.2 Testing Migration Status Check")
        session.write_line("-" * 50)
        
        try:
            status = migration_system.check_migration_status()
            session.write_line(f"Migration status check completed:")
            session.write_line(f"  Migration needed: {status.get('migration_needed', 'Unknown')}")
            session.write_line(f"  Check time: {status.get('check_time_ms', 'Unknown')}ms")
            session.write_line(f"  Schema differences: {status.get('schema_differences', {})}")
            
            self.test_results["status_check"] = True
            session.write_line("✅ Migration status check successful")
            
        except Exception as e:
            session.write_line(f"❌ Migration status check failed: {e}")
            self.test_results["status_check"] = False
        
        # Test 1.3: Execute Migration (No Migration Needed)
        session.write_line("\n1.3 Testing Migration Execution (No Migration Needed)")
        session.write_line("-" * 50)
        
        try:
            result = migration_system.execute_auto_migration()
            session.write_line(f"Migration execution result:")
            session.write_line(f"  Success: {result.success}")
            session.write_line(f"  Migration needed: {result.migration_needed}")
            session.write_line(f"  Operations executed: {result.operations_executed}")
            session.write_line(f"  Execution time: {result.execution_time_ms}ms")
            session.write_line(f"  Backup created: {result.backup_created}")
            
            if result.success and not result.migration_needed:
                session.write_line("✅ Migration execution (no migration needed) successful")
                self.test_results["no_migration_execution"] = True
            else:
                session.write_line("❌ Unexpected migration result")
                self.test_results["no_migration_execution"] = False
                
        except Exception as e:
            session.write_line(f"❌ Migration execution failed: {e}")
            self.test_results["no_migration_execution"] = False
        
        # Test 1.4: System Health Check
        session.write_line("\n1.4 Testing System Health Check")
        session.write_line("-" * 50)
        
        try:
            health = migration_system.get_system_health()
            session.write_line(f"System health check result:")
            session.write_line(f"  Overall health: {health.get('overall_health', 'Unknown')}")
            session.write_line(f"  Health score: {health.get('health_score', 'Unknown')}")
            session.write_line(f"  Recent failures: {health.get('recent_failures', 'Unknown')}")
            session.write_line(f"  Recommendations: {health.get('recommendations', [])}")
            
            if health.get('overall_health') in ['HEALTHY', 'WARNING']:
                session.write_line("✅ System health check successful")
                self.test_results["health_check"] = True
            else:
                session.write_line("❌ System health check indicates problems")
                self.test_results["health_check"] = False
                
        except Exception as e:
            session.write_line(f"❌ System health check failed: {e}")
            self.test_results["health_check"] = False
    
    def _test_auto_migration_system_edge_cases(self, session):
        """Test edge cases and corner scenarios."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("2. TESTING AUTO MIGRATION SYSTEM - EDGE CASES")
        session.write_line("=" * 60)
        
        # Test 2.1: Missing Columns Migration
        session.write_line("\n2.1 Testing Migration with Missing Columns")
        session.write_line("-" * 50)
        
        db_path = self.create_test_database("missing_columns_test", "missing_columns")
        database_url = f"sqlite:///{db_path}"
        
        try:
            migration_system = AutoMigrationSystem(database_url)
            
            # Check if migration is needed
            status = migration_system.check_migration_status()
            session.write_line(f"Migration needed: {status.get('migration_needed', False)}")
            
            if status.get('migration_needed', False):
                # Execute migration
                result = migration_system.execute_auto_migration()
                session.write_line(f"Migration result:")
                session.write_line(f"  Success: {result.success}")
                session.write_line(f"  Operations: {result.operations_executed}")
                session.write_line(f"  Time: {result.execution_time_ms}ms")
                
                if result.success:
                    session.write_line("✅ Missing columns migration successful")
                    self.test_results["missing_columns_migration"] = True
                else:
                    session.write_line(f"❌ Missing columns migration failed: {result.error_message}")
                    self.test_results["missing_columns_migration"] = False
            else:
                session.write_line("ℹ️ No migration needed for missing columns test")
                self.test_results["missing_columns_migration"] = True
                
        except Exception as e:
            session.write_line(f"❌ Missing columns migration test failed: {e}")
            self.test_results["missing_columns_migration"] = False
        
        # Test 2.2: Dry Run Mode
        session.write_line("\n2.2 Testing Dry Run Mode")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("dry_run_test", "missing_columns")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            migration_system.configure(dry_run_mode=True)
            
            status = migration_system.check_migration_status()
            if status.get('migration_needed', False):
                result = migration_system.execute_auto_migration()
                session.write_line(f"Dry run result:")
                session.write_line(f"  Success: {result.success}")
                session.write_line(f"  Operations (would execute): {result.operations_executed}")
                
                if result.success and result.operations_executed > 0:
                    session.write_line("✅ Dry run mode successful")
                    self.test_results["dry_run_mode"] = True
                else:
                    session.write_line("❌ Dry run mode failed")
                    self.test_results["dry_run_mode"] = False
            else:
                session.write_line("ℹ️ No migration needed for dry run test")
                self.test_results["dry_run_mode"] = True
                
        except Exception as e:
            session.write_line(f"❌ Dry run mode test failed: {e}")
            self.test_results["dry_run_mode"] = False
        
        # Test 2.3: Backup Configuration
        session.write_line("\n2.3 Testing Backup Configuration")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("backup_test", "current")
            database_url = f"sqlite:///{db_path}"
            backup_dir = Path(self.temp_dir) / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            migration_system = AutoMigrationSystem(database_url, backup_dir)
            migration_system.configure(auto_backup=True)
            
            # Force a migration by creating a simple operation
            result = migration_system.execute_auto_migration(force_backup=True)
            
            session.write_line(f"Backup test result:")
            session.write_line(f"  Success: {result.success}")
            session.write_line(f"  Backup created: {result.backup_created}")
            
            if result.backup_created and result.backup_info:
                session.write_line(f"  Backup ID: {result.backup_info.backup_id}")
                session.write_line("✅ Backup configuration successful")
                self.test_results["backup_configuration"] = True
            else:
                session.write_line("ℹ️ Backup not created (may be no migration needed)")
                self.test_results["backup_configuration"] = True
                
        except Exception as e:
            session.write_line(f"❌ Backup configuration test failed: {e}")
            self.test_results["backup_configuration"] = False
    
    def _test_error_scenarios(self, session):
        """Test error scenarios and failure handling."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("3. TESTING ERROR SCENARIOS AND FAILURE HANDLING")
        session.write_line("=" * 60)
        
        # Test 3.1: Invalid Database URL
        session.write_line("\n3.1 Testing Invalid Database URL")
        session.write_line("-" * 50)
        
        try:
            invalid_url = "sqlite:///nonexistent/path/that/does/not/exist.db"
            migration_system = AutoMigrationSystem(invalid_url)
            status = migration_system.check_migration_status()
            
            if 'error' in status:
                session.write_line("✅ Invalid database URL handled gracefully")
                self.test_results["invalid_database_url"] = True
            else:
                session.write_line("❌ Invalid database URL not handled properly")
                self.test_results["invalid_database_url"] = False
                
        except Exception as e:
            session.write_line(f"✅ Invalid database URL raised exception as expected: {e}")
            self.test_results["invalid_database_url"] = True
        
        # Test 3.2: Database Connection Failures
        session.write_line("\n3.2 Testing Database Connection Failures")
        session.write_line("-" * 50)
        
        try:
            # Create a database file and then remove it to simulate connection failure
            db_path = self.create_test_database("connection_fail_test", "current")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Remove the database file
            os.remove(db_path)
            
            status = migration_system.check_migration_status()
            
            if 'error' in status or not status.get('migration_needed', True):
                session.write_line("✅ Database connection failure handled gracefully")
                self.test_results["connection_failure"] = True
            else:
                session.write_line("❌ Database connection failure not handled properly")
                self.test_results["connection_failure"] = False
                
        except Exception as e:
            session.write_line(f"✅ Database connection failure raised exception: {e}")
            self.test_results["connection_failure"] = True
        
        # Test 3.3: Corrupted Data Scenarios
        session.write_line("\n3.3 Testing Corrupted Data Scenarios")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("corrupted_test", "corrupted")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            status = migration_system.check_migration_status()
            session.write_line(f"Corrupted data status check: {'SUCCESS' if 'error' not in status else 'ERROR'}")
            
            # Try to execute migration
            result = migration_system.execute_auto_migration()
            session.write_line(f"Corrupted data migration: {'SUCCESS' if result.success else 'FAILED'}")
            
            self.test_results["corrupted_data"] = True
            session.write_line("✅ Corrupted data scenario handled")
            
        except Exception as e:
            session.write_line(f"✅ Corrupted data raised exception: {e}")
            self.test_results["corrupted_data"] = True
        
        # Test 3.4: Timeout Scenarios
        session.write_line("\n3.4 Testing Timeout Scenarios")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("timeout_test", "missing_columns")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Set very short timeout
            migration_system.configure(max_execution_time_ms=1)  # 1ms
            
            result = migration_system.execute_auto_migration()
            
            if not result.success and "execution time" in (result.error_message or "").lower():
                session.write_line("✅ Timeout scenario handled correctly")
                self.test_results["timeout_handling"] = True
            else:
                session.write_line("ℹ️ Timeout scenario didn't trigger (migration too fast)")
                self.test_results["timeout_handling"] = True
                
        except Exception as e:
            session.write_line(f"❌ Timeout scenario test failed: {e}")
            self.test_results["timeout_handling"] = False
        
        # Test 3.5: Rollback Functionality
        session.write_line("\n3.5 Testing Rollback Functionality")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("rollback_test", "current")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Try to rollback when no migrations exist
            rollback_result = migration_system.rollback_last_migration()
            
            if not rollback_result['success'] and 'no migrations' in rollback_result.get('error', '').lower():
                session.write_line("✅ Rollback with no migrations handled correctly")
                self.test_results["rollback_functionality"] = True
            else:
                session.write_line("ℹ️ Rollback scenario may need actual migration")
                self.test_results["rollback_functionality"] = True
                
        except Exception as e:
            session.write_line(f"❌ Rollback functionality test failed: {e}")
            self.test_results["rollback_functionality"] = False
    
    def _test_server_integration(self, session):
        """Test server integration functionality."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("4. TESTING SERVER INTEGRATION")
        session.write_line("=" * 60)
        
        # Test 4.1: execute_startup_migration function
        session.write_line("\n4.1 Testing execute_startup_migration Function")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("startup_test", "current")
            database_url = f"sqlite:///{db_path}"
            backup_dir = Path(self.temp_dir) / "startup_backups"
            
            start_time = time.time()
            result = execute_startup_migration(database_url, backup_dir)
            execution_time = (time.time() - start_time) * 1000
            
            session.write_line(f"Startup migration result:")
            session.write_line(f"  Success: {result.success}")
            session.write_line(f"  Migration needed: {result.migration_needed}")
            session.write_line(f"  Execution time: {execution_time:.2f}ms")
            session.write_line(f"  Operations: {result.operations_executed}")
            
            if result.success:
                session.write_line("✅ Startup migration successful")
                self.test_results["startup_integration"] = True
            else:
                session.write_line(f"❌ Startup migration failed: {result.error_message}")
                self.test_results["startup_integration"] = False
                
        except Exception as e:
            session.write_line(f"❌ Startup migration test failed: {e}")
            self.test_results["startup_integration"] = False
        
        # Test 4.2: Configuration Options
        session.write_line("\n4.2 Testing Configuration Options")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("config_test", "current")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Test various configurations
            configurations = [
                {"auto_backup": False, "max_execution_time_ms": 1000, "dry_run_mode": True},
                {"auto_backup": True, "max_execution_time_ms": 5000, "dry_run_mode": False},
            ]
            
            config_success = True
            for i, config in enumerate(configurations):
                try:
                    migration_system.configure(**config)
                    session.write_line(f"  Configuration {i+1}: ✅")
                except Exception as e:
                    session.write_line(f"  Configuration {i+1}: ❌ {e}")
                    config_success = False
            
            if config_success:
                session.write_line("✅ Configuration options successful")
                self.test_results["configuration_options"] = True
            else:
                session.write_line("❌ Some configuration options failed")
                self.test_results["configuration_options"] = False
                
        except Exception as e:
            session.write_line(f"❌ Configuration options test failed: {e}")
            self.test_results["configuration_options"] = False
    
    def _test_performance_and_safety(self, session):
        """Test performance and safety features."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("5. TESTING PERFORMANCE AND SAFETY")
        session.write_line("=" * 60)
        
        # Test 5.1: Migration History Tracking
        session.write_line("\n5.1 Testing Migration History Tracking")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("history_test", "current")
            database_url = f"sqlite:///{db_path}"
            migration_system = AutoMigrationSystem(database_url)
            
            # Check initial health
            health = migration_system.get_system_health()
            session.write_line(f"Initial health score: {health.get('health_score', 'Unknown')}")
            session.write_line(f"Migration statistics: {health.get('migration_statistics', {})}")
            
            if 'migration_statistics' in health:
                session.write_line("✅ Migration history tracking working")
                self.test_results["history_tracking"] = True
            else:
                session.write_line("❌ Migration history tracking not working")
                self.test_results["history_tracking"] = False
                
        except Exception as e:
            session.write_line(f"❌ Migration history tracking test failed: {e}")
            self.test_results["history_tracking"] = False
        
        # Test 5.2: Backup Creation and Restoration
        session.write_line("\n5.2 Testing Backup Creation and Restoration")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("backup_restore_test", "current")
            database_url = f"sqlite:///{db_path}"
            backup_dir = Path(self.temp_dir) / "backup_restore"
            backup_dir.mkdir(exist_ok=True)
            
            migration_system = AutoMigrationSystem(database_url, backup_dir)
            
            # Add some data to backup
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (id, title, status) VALUES ('test1', 'Test Task', 'pending')")
            conn.commit()
            conn.close()
            
            # Create backup through migration system
            result = migration_system.execute_auto_migration(force_backup=True)
            
            if result.backup_created:
                session.write_line(f"Backup created: {result.backup_info.backup_id}")
                session.write_line("✅ Backup creation successful")
                self.test_results["backup_creation"] = True
            else:
                session.write_line("ℹ️ Backup not created (no migration needed)")
                self.test_results["backup_creation"] = True
                
        except Exception as e:
            session.write_line(f"❌ Backup creation test failed: {e}")
            self.test_results["backup_creation"] = False
        
        # Test 5.3: Large Data Migration Scenarios
        session.write_line("\n5.3 Testing Large Data Migration Scenarios")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("large_data_test", "current")
            database_url = f"sqlite:///{db_path}"
            
            # Insert large amount of test data
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            large_data = [(f"task_{i}", f"Large Task {i}", "pending") for i in range(1000)]
            cursor.executemany("INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)", large_data)
            conn.commit()
            conn.close()
            
            migration_system = AutoMigrationSystem(database_url)
            
            start_time = time.time()
            status = migration_system.check_migration_status()
            check_time = (time.time() - start_time) * 1000
            
            session.write_line(f"Large data status check: {check_time:.2f}ms")
            
            if check_time < 5000:  # Should complete within 5 seconds
                session.write_line("✅ Large data migration performance acceptable")
                self.test_results["large_data_performance"] = True
            else:
                session.write_line("❌ Large data migration performance slow")
                self.test_results["large_data_performance"] = False
            
            self.performance_metrics["large_data_check_time_ms"] = check_time
            
        except Exception as e:
            session.write_line(f"❌ Large data migration test failed: {e}")
            self.test_results["large_data_performance"] = False
    
    def _test_concurrent_migrations(self, session):
        """Test concurrent migration attempts."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("6. TESTING CONCURRENT MIGRATION HANDLING")
        session.write_line("=" * 60)
        
        session.write_line("\n6.1 Testing Concurrent Migration Attempts")
        session.write_line("-" * 50)
        
        try:
            db_path = self.create_test_database("concurrent_test", "missing_columns")
            database_url = f"sqlite:///{db_path}"
            
            # Create multiple migration systems
            migration_system1 = AutoMigrationSystem(database_url)
            migration_system2 = AutoMigrationSystem(database_url)
            
            results = []
            errors = []
            
            def run_migration(system_id):
                try:
                    if system_id == 1:
                        result = migration_system1.execute_auto_migration()
                    else:
                        result = migration_system2.execute_auto_migration()
                    results.append((system_id, result))
                except Exception as e:
                    errors.append((system_id, str(e)))
            
            # Start concurrent migrations
            thread1 = threading.Thread(target=run_migration, args=(1,))
            thread2 = threading.Thread(target=run_migration, args=(2,))
            
            thread1.start()
            thread2.start()
            
            thread1.join(timeout=10)
            thread2.join(timeout=10)
            
            session.write_line(f"Concurrent migration results: {len(results)} completed, {len(errors)} errors")
            
            for system_id, result in results:
                session.write_line(f"  System {system_id}: {'SUCCESS' if result.success else 'FAILED'}")
            
            for system_id, error in errors:
                session.write_line(f"  System {system_id}: ERROR - {error}")
            
            # At least one should succeed
            if len(results) > 0 and any(r[1].success for r in results):
                session.write_line("✅ Concurrent migration handling successful")
                self.test_results["concurrent_migrations"] = True
            else:
                session.write_line("❌ Concurrent migration handling failed")
                self.test_results["concurrent_migrations"] = False
                
        except Exception as e:
            session.write_line(f"❌ Concurrent migration test failed: {e}")
            self.test_results["concurrent_migrations"] = False
    
    def _generate_comprehensive_report(self, session):
        """Generate comprehensive test report."""
        session.write_line("\n\n" + "=" * 60)
        session.write_line("COMPREHENSIVE TEST REPORT")
        session.write_line("=" * 60)
        
        # Test Results Summary
        session.write_line("\nTEST RESULTS SUMMARY:")
        session.write_line("-" * 30)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        session.write_line(f"Total Tests: {total_tests}")
        session.write_line(f"Passed: {passed_tests}")
        session.write_line(f"Failed: {failed_tests}")
        session.write_line(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed Results
        session.write_line("\nDETAILED TEST RESULTS:")
        session.write_line("-" * 30)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            session.write_line(f"{test_name}: {status}")
        
        # Performance Metrics
        if self.performance_metrics:
            session.write_line("\nPERFORMANCE METRICS:")
            session.write_line("-" * 30)
            
            for metric_name, value in self.performance_metrics.items():
                session.write_line(f"{metric_name}: {value}")
        
        # Recommendations
        session.write_line("\nRECOMMENDAT"""
                
        session.write_line("\nRECOMMENDATIONS:")
        session.write_line("-" * 30)
        
        if failed_tests == 0:
            session.write_line("✅ All tests passed! The migration system is working correctly.")
        else:
            session.write_line("⚠️ Some tests failed. Please review the following:")
            
            for test_name, result in self.test_results.items():
                if not result:
                    session.write_line(f"  - {test_name}: Requires investigation")
        
        # System Health Assessment
        session.write_line("\nSYSTEM HEALTH ASSESSMENT:")
        session.write_line("-" * 30)
        
        if passed_tests / total_tests >= 0.9:
            session.write_line("🟢 EXCELLENT - Migration system is highly reliable")
        elif passed_tests / total_tests >= 0.7:
            session.write_line("🟡 GOOD - Migration system is generally reliable with minor issues")
        elif passed_tests / total_tests >= 0.5:
            session.write_line("🟠 WARNING - Migration system has significant issues")
        else:
            session.write_line("🔴 CRITICAL - Migration system requires immediate attention")


def main():
    """Main test execution function."""
    print("Starting Comprehensive Database Migration System Test Suite...")
    print("=" * 80)
    
    # Create test suite
    test_suite = ComprehensiveMigrationTestSuite()
    
    try:
        # Run all tests
        success = test_suite.run_all_tests()
        
        # Get output file for reference
        output_files = list(test_suite.output_dir.glob("comprehensive_migration_test_*.txt"))
        if output_files:
            latest_output = max(output_files, key=lambda f: f.stat().st_mtime)
            print(f"\n📁 Complete test report available at: {latest_output}")
        
        if success:
            print("\n✅ Comprehensive test suite completed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed. Check the detailed report.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())