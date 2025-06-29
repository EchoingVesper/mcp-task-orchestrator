#!/usr/bin/env python3
"""
Enhanced Migration Test with File-Based Output

This module demonstrates how to integrate the file-based output system
with the existing migration test to prevent timing issues where LLM
calls check results before the test has finished writing output.
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from testing_utils.file_output_system import TestOutputWriter, TestOutputReader
from testing_utils.pytest_integration import file_output_test


class EnhancedMigrationTestRunner:
    """Enhanced test runner for migration tests with file-based output."""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent / "migration_test_outputs"
        
        self.output_dir = Path(output_dir)
        self.writer = TestOutputWriter(self.output_dir)
        self.reader = TestOutputReader(self.output_dir)
    
    def run_migration_test_with_file_output(self, tmp_path_str: str):
        """
        Run the migration test with comprehensive file-based output capture.
        
        This version writes all output to files that can be safely read
        by LLM calls after the test completes, preventing timing issues.
        """
        
        test_name = f"migration_test_{int(time.time())}"
        
        with self.writer.write_test_output(test_name, "text") as session:
            try:
                # Write test header
                session.write_line("="*60)
                session.write_line("ENHANCED MIGRATION TEST WITH FILE OUTPUT")
                session.write_line("="*60)
                session.write_line(f"Test Name: {test_name}")
                session.write_line(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                session.write_line(f"Temp Path: {tmp_path_str}")
                session.write_line("")
                
                # Import and run the original migration test logic
                from tests.unit.test_migration import create_test_db, ArtifactsMigrator
                import tempfile
                import sqlite3
                from pathlib import Path
                
                # Create test database
                session.write_line("=== Creating Test Database ===")
                
                if tmp_path_str.startswith("MockTmpPath"):
                    # Handle the mock case from run_migration_test.py
                    db_path = Path(project_root) / "test_artifacts_temp" / "test_artifacts.db"
                    db_path.parent.mkdir(exist_ok=True)
                else:
                    db_path = Path(tmp_path_str) / "test_artifacts.db"
                
                session.write_line(f"Database path: {db_path}")
                
                create_test_db(str(db_path))
                session.write_line("✅ Test database created successfully")
                
                # Print initial database state
                session.write_line("\\n=== Initial Database State ===")
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM subtasks ORDER BY task_id")
                rows = cursor.fetchall()
                session.write_line("Subtasks table (before migration):")
                for row in rows:
                    session.write_line(f"  {row}")
                conn.close()
                
                # Run the migration
                session.write_line("\\n=== Running Migration ===")
                migrator = ArtifactsMigrator(str(db_path))
                result = migrator.run_migration()
                
                if result:
                    session.write_line("✅ Migration completed successfully")
                else:
                    session.write_line("❌ Migration failed")
                    raise Exception("Migration failed")
                
                # Print post-migration database state with detailed analysis
                session.write_line("\\n=== Post-Migration Database State (Detailed) ===")
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get summary information
                cursor.execute("SELECT task_id, parent_task_id, LENGTH(artifacts) as len, SUBSTR(artifacts, 1, 100) as preview FROM subtasks ORDER BY task_id")
                rows = cursor.fetchall()
                session.write_line("Subtasks table (summary after migration):")
                for row in rows:
                    task_id, parent_id, length, preview = row
                    session.write_line(f"  {task_id}: parent={parent_id}, len={length}, preview={preview!r}")
                
                # Detailed record content analysis
                session.write_line("\\n=== Detailed Migration Verification ===")
                cursor.execute("SELECT task_id, artifacts FROM subtasks WHERE artifacts IS NOT NULL ORDER BY task_id")
                rows = cursor.fetchall()
                
                verification_results = {}
                
                for task_id, artifacts_json in rows:
                    session.write_line(f"\\nAnalyzing Task ID: {task_id}")
                    session.write_line(f"Raw JSON: {artifacts_json!r}")
                    
                    try:
                        parsed = json.loads(artifacts_json)
                        session.write_line(f"Parsed successfully: {parsed}")
                        session.write_line(f"Type: {type(parsed)}")
                        
                        if isinstance(parsed, list):
                            session.write_line(f"Array length: {len(parsed)}")
                            for i, item in enumerate(parsed):
                                session.write_line(f"  Item {i}: {item!r} (type: {type(item)})")
                            verification_results[task_id] = "VALID_ARRAY"
                        else:
                            session.write_line(f"⚠️ Not an array: {type(parsed)}")
                            verification_results[task_id] = "INVALID_TYPE"
                            
                    except json.JSONDecodeError as e:
                        session.write_line(f"❌ JSON parsing failed: {e}")
                        verification_results[task_id] = "INVALID_JSON"
                    except Exception as e:
                        session.write_line(f"❌ Unexpected error: {e}")
                        verification_results[task_id] = "ERROR"
                
                # Verify NULL/empty cases
                session.write_line("\\n=== NULL/Empty Cases Verification ===")
                cursor.execute("""
                    SELECT task_id, artifacts, 
                           CASE 
                               WHEN artifacts IS NULL THEN 'NULL' 
                               WHEN TRIM(artifacts) = '' THEN 'EMPTY_STRING' 
                               ELSE 'HAS_VALUE' 
                           END as status
                    FROM subtasks 
                    ORDER BY task_id
                """)
                all_rows = cursor.fetchall()
                
                session.write_line("All subtasks with artifacts status:")
                null_empty_count = 0
                for task_id, artifacts, status in all_rows:
                    session.write_line(f"  {task_id}: {status}, value: {artifacts!r}")
                    if status in ['NULL', 'EMPTY_STRING']:
                        null_empty_count += 1
                
                session.write_line(f"\\nFound {null_empty_count} NULL/empty artifact records")
                
                conn.close()
                
                # Final verification summary
                session.write_line("\\n=== Final Verification Summary ===")
                total_records = len(verification_results)
                valid_records = sum(1 for status in verification_results.values() if status == "VALID_ARRAY")
                
                session.write_line(f"Total records processed: {total_records}")
                session.write_line(f"Valid arrays after migration: {valid_records}")
                session.write_line(f"NULL/empty records: {null_empty_count}")
                
                if valid_records == total_records:
                    session.write_line("✅ ALL MIGRATION VALIDATIONS PASSED")
                    test_result = "PASSED"
                else:
                    session.write_line(f"❌ VALIDATION ISSUES: {total_records - valid_records} failed validations")
                    test_result = "FAILED"
                
                # Write completion marker
                session.write_line("\\n" + "="*60)
                session.write_line("MIGRATION TEST COMPLETED")
                session.write_line("="*60)
                session.write_line(f"Final Result: {test_result}")
                session.write_line(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                session.write_line(f"Output File: {session.output_path}")
                session.write_line("="*60)
                
                return test_result == "PASSED"
                
            except Exception as e:
                # Write error information
                session.write_line("\\n" + "="*60)
                session.write_line("MIGRATION TEST FAILED")
                session.write_line("="*60)
                session.write_line(f"Error: {str(e)}")
                session.write_line(f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                session.write_line("="*60)
                raise
    
    def wait_for_test_completion_and_read(self, test_name: str, timeout: float = 30.0) -> tuple[bool, str]:
        """
        Wait for a test to complete and then safely read its output.
        
        This is the key function that prevents timing issues - it ensures
        the test has completely finished writing before attempting to read.
        
        Returns:
            tuple: (success: bool, content: str)
        """
        
        # Find output files for this test
        output_files = list(self.output_dir.glob(f"{test_name}_*.txt"))
        
        if not output_files:
            return False, "No output files found for test"
        
        # Get the most recent output file
        latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
        
        # Wait for completion
        completed = self.reader.wait_for_completion(latest_file, timeout)
        
        if not completed:
            return False, f"Test did not complete within {timeout} seconds"
        
        # Safely read the completed output
        content = self.reader.read_completed_output(latest_file)
        
        if content is None:
            return False, "Failed to read completed output"
        
        return True, content
    
    def get_latest_test_output_file(self) -> Path:
        """Get the path to the most recently created test output file."""
        output_files = list(self.output_dir.glob("migration_test_*.txt"))
        
        if not output_files:
            return None
        
        return max(output_files, key=lambda f: f.stat().st_mtime)


def run_enhanced_migration_test_standalone():
    """
    Standalone function to run the enhanced migration test.
    
    This can be called directly to run the migration test with file output,
    similar to how the original run_migration_test.py works.
    """
    
    print("=== Running Enhanced Migration Test (Standalone) ===")
    
    # Create test runner
    runner = EnhancedMigrationTestRunner()
    
    # Create mock temp path (similar to original script)
    class MockTmpPath:
        def __init__(self):
            self.path = Path(project_root) / "test_artifacts_temp"
            os.makedirs(self.path, exist_ok=True)
        
        def __str__(self):
            return str(self.path)
    
    mock_tmp_path = MockTmpPath()
    
    try:
        # Run the test
        print("Starting migration test with file output...")
        success = runner.run_migration_test_with_file_output(str(mock_tmp_path))
        
        # Get the output file location
        output_file = runner.get_latest_test_output_file()
        
        if success:
            print("\\n✅ Enhanced migration test completed successfully!")
            print(f"📁 Complete output written to: {output_file}")
            print("\\n🔍 LLM systems can now safely read the output file after checking for completion marker.")
        else:
            print("\\n❌ Enhanced migration test failed!")
            print(f"📁 Error details written to: {output_file}")
        
        return success
        
    except Exception as e:
        print(f"\\n💥 Test execution failed: {str(e)}")
        return False
    finally:
        # Clean up temporary directory
        temp_dir = Path(project_root) / "test_artifacts_temp"
        if temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


if __name__ == "__main__":
    success = run_enhanced_migration_test_standalone()
    sys.exit(0 if success else 1)
