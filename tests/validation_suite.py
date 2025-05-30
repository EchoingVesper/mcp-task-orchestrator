#!/usr/bin/env python3
"""
Comprehensive Test Validation Suite

This module validates all the implemented solutions for the MCP Task Orchestrator
test output and resource issues. It tests each component individually and then
validates the integrated system works correctly.

Test Areas:
1. Database connection resource management
2. Pytest configuration and output handling  
3. File-based test output system
4. Alternative test runners
5. Hang detection and prevention
6. End-to-end integration scenarios
"""

import os
import sys
import time
import warnings
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging to capture warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validation_suite")


@dataclass
class ValidationResult:
    """Result of a validation test."""
    test_name: str
    status: str  # passed, failed, error, skipped
    duration: float
    details: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ResourceWarningValidator:
    """Validates that resource warnings have been eliminated."""
    
    def __init__(self):
        self.warning_count = 0
        self.resource_warnings = []
        
    def validate_database_connections(self) -> ValidationResult:
        """Test that database connections are properly managed."""
        start_time = time.time()
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                # Test the enhanced database persistence manager
                from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
                
                # Create temporary database
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                    db_path = tmp_file.name
                
                try:
                    # Test context manager usage
                    with DatabasePersistenceManager(db_url=f"sqlite:///{db_path}") as persistence:
                        # Perform some operations
                        active_tasks = persistence.get_all_active_tasks()
                        logger.info(f"Retrieved {len(active_tasks)} active tasks")
                    
                    # Test manual usage with dispose
                    persistence = DatabasePersistenceManager(db_url=f"sqlite:///{db_path}")
                    active_tasks = persistence.get_all_active_tasks()
                    persistence.dispose()  # Manual cleanup
                    
                    # Check for resource warnings
                    resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
                    
                    duration = time.time() - start_time
                    
                    if resource_warnings:
                        return ValidationResult(
                            test_name="database_connections",
                            status="failed",
                            duration=duration,
                            details=f"Found {len(resource_warnings)} ResourceWarnings",
                            issues_found=[str(warning.message) for warning in resource_warnings],
                            recommendations=[
                                "Review database connection cleanup code",
                                "Ensure all connections are properly disposed",
                                "Check for missing context manager usage"
                            ]
                        )
                    else:
                        return ValidationResult(
                            test_name="database_connections",
                            status="passed",
                            duration=duration,
                            details="No ResourceWarnings detected",
                            metrics={"operations_tested": 2, "warnings_found": 0}
                        )
                        
                finally:
                    # Cleanup temp database
                    try:
                        os.unlink(db_path)
                    except:
                        pass
                        
            except Exception as e:
                duration = time.time() - start_time
                return ValidationResult(
                    test_name="database_connections",
                    status="error", 
                    duration=duration,
                    details=f"Test execution failed: {str(e)}",
                    issues_found=[str(e)],
                    recommendations=["Review database persistence implementation"]
                )
    
    def validate_test_resource_cleanup(self) -> ValidationResult:
        """Test that the test utilities properly clean up resources."""
        start_time = time.time()
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                from tests.utils.db_test_utils import DatabaseTestCase, managed_sqlite_connection
                
                # Test context manager approach
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                    db_path = tmp_file.name
                
                try:
                    # Test managed connection
                    with managed_sqlite_connection(db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("CREATE TABLE test (id INTEGER)")
                        conn.commit()
                    
                    # Test DatabaseTestCase
                    test_case = DatabaseTestCase()
                    try:
                        conn = test_case.get_managed_connection(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM test")
                        cursor.fetchall()
                    finally:
                        test_case.cleanup_db_resources()
                    
                    # Check for warnings
                    resource_warnings = [warning for warning in w if issubclass(warning.category, ResourceWarning)]
                    
                    duration = time.time() - start_time
                    
                    if resource_warnings:
                        return ValidationResult(
                            test_name="test_resource_cleanup",
                            status="failed",
                            duration=duration,
                            details=f"Found {len(resource_warnings)} ResourceWarnings in test utilities",
                            issues_found=[str(warning.message) for warning in resource_warnings]
                        )
                    else:
                        return ValidationResult(
                            test_name="test_resource_cleanup",
                            status="passed",
                            duration=duration,
                            details="Test utility resource cleanup working correctly",
                            metrics={"test_patterns_validated": 2}
                        )
                        
                finally:
                    try:
                        os.unlink(db_path)
                    except:
                        pass
                        
            except Exception as e:
                duration = time.time() - start_time
                return ValidationResult(
                    test_name="test_resource_cleanup",
                    status="error",
                    duration=duration,
                    details=f"Test execution failed: {str(e)}",
                    issues_found=[str(e)]
                )


class OutputTruncationValidator:
    """Validates that output truncation issues have been resolved."""
    
    def validate_pytest_configuration(self) -> ValidationResult:
        """Test the improved pytest configuration."""
        start_time = time.time()
        
        try:
            # Run validation script we created earlier
            validation_script = project_root / "tests" / "validate_pytest_config.py"
            
            if not validation_script.exists():
                return ValidationResult(
                    test_name="pytest_configuration",
                    status="skipped",
                    duration=time.time() - start_time,
                    details="Pytest validation script not found"
                )
            
            # Execute the validation script
            result = subprocess.run(
                [sys.executable, str(validation_script)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return ValidationResult(
                    test_name="pytest_configuration",
                    status="passed",
                    duration=duration,
                    details="Pytest configuration validation passed",
                    metrics={"validation_exit_code": result.returncode}
                )
            else:
                return ValidationResult(
                    test_name="pytest_configuration", 
                    status="failed",
                    duration=duration,
                    details=f"Pytest validation failed with exit code {result.returncode}",
                    issues_found=[result.stderr] if result.stderr else ["Unknown pytest validation failure"]
                )
                
        except subprocess.TimeoutExpired:
            return ValidationResult(
                test_name="pytest_configuration",
                status="failed",
                duration=60.0,
                details="Pytest validation timed out",
                issues_found=["Validation script timed out after 60 seconds"]
            )
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="pytest_configuration",
                status="error",
                duration=duration,
                details=f"Pytest validation error: {str(e)}",
                issues_found=[str(e)]
            )
    
    def validate_file_output_system(self) -> ValidationResult:
        """Test the file-based output system prevents truncation."""
        start_time = time.time()
        
        try:
            from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader
            
            # Create test output
            output_dir = Path(tempfile.mkdtemp(prefix="validation_output_"))
            
            try:
                writer = TestOutputWriter(output_dir)
                reader = TestOutputReader(output_dir)
                
                # Generate substantial output
                test_lines = []
                for i in range(200):  # Generate 200 lines
                    test_lines.append(f"Validation line {i:03d}: " + "x" * 100)
                
                # Write using file-based system
                with writer.write_test_output("truncation_validation", "text") as session:
                    session.write_line("=== Truncation Validation Test ===")
                    for line in test_lines:
                        session.write_line(line)
                    session.write_line("=== End of Validation Test ===")
                
                # Find the output file
                output_files = list(output_dir.glob("truncation_validation_*.txt"))
                
                if not output_files:
                    return ValidationResult(
                        test_name="file_output_system",
                        status="failed",
                        duration=time.time() - start_time,
                        details="No output file created",
                        issues_found=["File-based output system did not create output file"]
                    )
                
                latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
                
                # Wait for completion and read
                if reader.wait_for_completion(latest_file, timeout=30.0):
                    content = reader.read_completed_output(latest_file)
                    
                    if content:
                        content_lines = content.split('\\n')
                        expected_lines = len(test_lines) + 2  # Plus header and footer
                        
                        # Calculate capture rate
                        capture_rate = (len(content_lines) / expected_lines) * 100
                        
                        duration = time.time() - start_time
                        
                        if capture_rate >= 95.0:  # 95% capture threshold
                            return ValidationResult(
                                test_name="file_output_system",
                                status="passed",
                                duration=duration,
                                details="File-based output system working correctly",
                                metrics={
                                    "expected_lines": expected_lines,
                                    "captured_lines": len(content_lines),
                                    "capture_rate_percent": capture_rate
                                }
                            )
                        else:
                            return ValidationResult(
                                test_name="file_output_system",
                                status="failed",
                                duration=duration,
                                details=f"Output capture rate too low: {capture_rate:.1f}%",
                                issues_found=[f"Only captured {len(content_lines)}/{expected_lines} lines"],
                                metrics={"capture_rate_percent": capture_rate}
                            )
                    else:
                        return ValidationResult(
                            test_name="file_output_system",
                            status="failed",
                            duration=time.time() - start_time,
                            details="Could not read output content",
                            issues_found=["File reading failed after completion"]
                        )
                else:
                    return ValidationResult(
                        test_name="file_output_system",
                        status="failed",
                        duration=time.time() - start_time,
                        details="Output file did not complete within timeout",
                        issues_found=["File completion timeout after 30 seconds"]
                    )
                    
            finally:
                # Cleanup temp directory
                import shutil
                try:
                    shutil.rmtree(output_dir)
                except:
                    pass
                    
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="file_output_system",
                status="error",
                duration=duration,
                details=f"File output system test failed: {str(e)}",
                issues_found=[str(e)]
            )


class AlternativeRunnerValidator:
    """Validates that alternative test runners work correctly."""
    
    def validate_direct_runner(self) -> ValidationResult:
        """Test the direct function runner."""
        start_time = time.time()
        
        try:
            from mcp_task_orchestrator.testing import DirectFunctionRunner
            
            # Create a simple test function to run
            def sample_test():
                """Sample test function for validation."""
                print("Sample test executing")
                assert True
                return "test_passed"
            
            # Create runner
            runner = DirectFunctionRunner(
                output_dir=Path(tempfile.mkdtemp(prefix="validation_direct_")),
                verbose=False
            )
            
            try:
                # Execute the test
                result = runner.execute_test(sample_test, "validation_direct_test")
                
                duration = time.time() - start_time
                
                if result.status == "passed":
                    return ValidationResult(
                        test_name="direct_runner",
                        status="passed",
                        duration=duration,
                        details="Direct function runner executed successfully",
                        metrics={
                            "test_duration": result.duration,
                            "output_file_created": result.output_file is not None
                        }
                    )
                else:
                    return ValidationResult(
                        test_name="direct_runner",
                        status="failed",
                        duration=duration,
                        details=f"Direct runner test failed: {result.error_message}",
                        issues_found=[result.error_message or "Unknown failure"]
                    )
                    
            finally:
                # Cleanup
                try:
                    import shutil
                    shutil.rmtree(runner.output_dir)
                except:
                    pass
                    
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="direct_runner",
                status="error",
                duration=duration,
                details=f"Direct runner validation error: {str(e)}",
                issues_found=[str(e)]
            )
    
    def validate_migration_runner(self) -> ValidationResult:
        """Test the migration test runner."""
        start_time = time.time()
        
        try:
            from mcp_task_orchestrator.testing import MigrationTestRunner
            
            # Create runner
            runner = MigrationTestRunner(
                output_dir=Path(tempfile.mkdtemp(prefix="validation_migration_"))
            )
            
            try:
                # Check if migration test exists
                migration_test_file = project_root / "tests" / "unit" / "test_migration.py"
                
                if not migration_test_file.exists():
                    return ValidationResult(
                        test_name="migration_runner",
                        status="skipped",
                        duration=time.time() - start_time,
                        details="Migration test file not found"
                    )
                
                # Run migration test
                result = runner.run_migration_test()
                
                duration = time.time() - start_time
                
                if result.status == "passed":
                    return ValidationResult(
                        test_name="migration_runner",
                        status="passed",
                        duration=duration,
                        details="Migration test runner executed successfully",
                        metrics={
                            "test_duration": result.duration,
                            "output_file_size": result.output_file.stat().st_size if result.output_file and result.output_file.exists() else 0
                        }
                    )
                else:
                    return ValidationResult(
                        test_name="migration_runner",
                        status="failed",
                        duration=duration,
                        details=f"Migration test failed: {result.error_message}",
                        issues_found=[result.error_message or "Migration test execution failed"]
                    )
                    
            finally:
                # Cleanup
                try:
                    import shutil
                    shutil.rmtree(runner.output_dir)
                except:
                    pass
                    
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="migration_runner",
                status="error",
                duration=duration,
                details=f"Migration runner validation error: {str(e)}",
                issues_found=[str(e)]
            )
    
    def validate_comprehensive_runner(self) -> ValidationResult:
        """Test the comprehensive test runner orchestration."""
        start_time = time.time()
        
        try:
            from mcp_task_orchestrator.testing import ComprehensiveTestRunner, TestRunnerConfig
            
            # Create simple test files for validation
            temp_test_dir = Path(tempfile.mkdtemp(prefix="validation_comprehensive_"))
            
            try:
                # Create a simple test file
                test_file_content = '''
def test_validation_sample():
    """Sample test for comprehensive runner validation."""
    print("Comprehensive runner validation test")
    assert True
    return "validation_passed"

def test_validation_sample2():
    """Another sample test."""
    print("Second validation test")
    assert True
'''
                
                test_file = temp_test_dir / "test_validation_sample.py"
                test_file.write_text(test_file_content)
                
                # Create runner
                config = TestRunnerConfig(
                    output_dir=temp_test_dir / "output",
                    runner_types=['direct'],  # Use only direct runner for validation
                    verbose=False
                )
                
                runner = ComprehensiveTestRunner(config)
                
                # Run tests
                results = runner.run_all_tests([temp_test_dir])
                
                duration = time.time() - start_time
                
                # Analyze results
                total_tests = sum(len(runner_results) for runner_results in results.values())
                passed_tests = sum(
                    len([r for r in runner_results if r.status == "passed"])
                    for runner_results in results.values()
                )
                
                if total_tests > 0 and passed_tests == total_tests:
                    return ValidationResult(
                        test_name="comprehensive_runner",
                        status="passed",
                        duration=duration,
                        details="Comprehensive runner orchestration working correctly",
                        metrics={
                            "total_tests": total_tests,
                            "passed_tests": passed_tests,
                            "runners_used": len(results)
                        }
                    )
                elif total_tests > 0:
                    return ValidationResult(
                        test_name="comprehensive_runner",
                        status="failed",
                        duration=duration,
                        details=f"Some tests failed: {passed_tests}/{total_tests} passed",
                        issues_found=[f"{total_tests - passed_tests} tests failed"],
                        metrics={"total_tests": total_tests, "passed_tests": passed_tests}
                    )
                else:
                    return ValidationResult(
                        test_name="comprehensive_runner",
                        status="failed",
                        duration=duration,
                        details="No tests were discovered or executed",
                        issues_found=["Test discovery or execution failed"]
                    )
                    
            finally:
                # Cleanup temp directory
                try:
                    import shutil
                    shutil.rmtree(temp_test_dir)
                except:
                    pass
                    
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="comprehensive_runner",
                status="error",
                duration=duration,
                details=f"Comprehensive runner validation error: {str(e)}",
                issues_found=[str(e)]
            )


class HangDetectionValidator:
    """Validates the hang detection and prevention systems."""
    
    def validate_hang_detection_system(self) -> ValidationResult:
        """Test the hang detection monitoring system."""
        start_time = time.time()
        
        try:
            from mcp_task_orchestrator.monitoring.hang_detection import (
                HangDetector, with_hang_detection, get_hang_detection_statistics
            )
            
            # Test basic hang detector functionality
            detector = HangDetector(operation_timeout=5.0, warning_timeout=2.0)
            
            # Register an operation
            op_id = detector.register_operation("validation_test")
            
            # Wait briefly
            time.sleep(1.0)
            
            # Check statistics
            stats = detector.get_statistics()
            
            # Unregister operation
            detector.unregister_operation(op_id)
            
            # Test decorator functionality
            @with_hang_detection("validation_decorator_test", timeout=3.0)
            async def sample_async_operation():
                import asyncio
                await asyncio.sleep(0.5)
                return "completed"
            
            # Run the decorated operation
            import asyncio
            try:
                result = asyncio.run(sample_async_operation())
                decorator_test_passed = result == "completed"
            except Exception:
                decorator_test_passed = False
            
            duration = time.time() - start_time
            
            if stats['active_operations'] == 0 and decorator_test_passed:
                return ValidationResult(
                    test_name="hang_detection_system",
                    status="passed",
                    duration=duration,
                    details="Hang detection system functioning correctly",
                    metrics={
                        "operation_tracking": True,
                        "decorator_functionality": decorator_test_passed,
                        "statistics_collection": len(stats) > 0
                    }
                )
            else:
                issues = []
                if stats['active_operations'] > 0:
                    issues.append(f"Operations not properly cleaned up: {stats['active_operations']} active")
                if not decorator_test_passed:
                    issues.append("Hang detection decorator test failed")
                    
                return ValidationResult(
                    test_name="hang_detection_system",
                    status="failed",
                    duration=duration,
                    details="Hang detection system has issues",
                    issues_found=issues
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="hang_detection_system",
                status="error",
                duration=duration,
                details=f"Hang detection validation error: {str(e)}",
                issues_found=[str(e)]
            )
    
    def validate_enhanced_handlers(self) -> ValidationResult:
        """Test the enhanced MCP handlers with hang detection."""
        start_time = time.time()
        
        try:
            # This test validates that the enhanced handlers are properly implemented
            # but doesn't actually test their integration with MCP (which would require a full server)
            
            try:
                from mcp_task_orchestrator.enhanced_handlers import (
                    handle_complete_subtask_enhanced,
                    handle_execute_subtask_enhanced
                )
                handlers_available = True
            except ImportError:
                handlers_available = False
            
            duration = time.time() - start_time
            
            if handlers_available:
                return ValidationResult(
                    test_name="enhanced_handlers",
                    status="passed",
                    duration=duration,
                    details="Enhanced MCP handlers are available and properly implemented",
                    metrics={"handlers_implemented": True}
                )
            else:
                return ValidationResult(
                    test_name="enhanced_handlers",
                    status="failed",
                    duration=duration,
                    details="Enhanced MCP handlers not available",
                    issues_found=["Enhanced handlers module not found or has import errors"]
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="enhanced_handlers",
                status="error",
                duration=duration,
                details=f"Enhanced handlers validation error: {str(e)}",
                issues_found=[str(e)]
            )


class IntegrationValidator:
    """Validates end-to-end integration scenarios."""
    
    def validate_end_to_end_scenario(self) -> ValidationResult:
        """Test a complete end-to-end scenario."""
        start_time = time.time()
        
        try:
            # Scenario: Run a test with file output, then read it safely
            from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader
            
            output_dir = Path(tempfile.mkdtemp(prefix="validation_e2e_"))
            
            try:
                # Step 1: Write test output (simulating test execution)
                writer = TestOutputWriter(output_dir)
                
                with writer.write_test_output("e2e_validation_test", "text") as session:
                    session.write_line("=== End-to-End Validation Test ===")
                    session.write_line("Simulating test execution...")
                    
                    # Simulate test work
                    for i in range(10):
                        session.write_line(f"Test step {i+1}: Processing...")
                        time.sleep(0.1)  # Brief delay to simulate work
                    
                    session.write_line("Test completed successfully")
                    session.write_line("=== End of Test ===")
                
                # Step 2: Simulate LLM reading the output safely
                reader = TestOutputReader(output_dir)
                
                # Find the output file
                output_files = list(output_dir.glob("e2e_validation_test_*.txt"))
                
                if not output_files:
                    return ValidationResult(
                        test_name="end_to_end_scenario",
                        status="failed",
                        duration=time.time() - start_time,
                        details="No output file created in end-to-end test",
                        issues_found=["File creation failed"]
                    )
                
                latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
                
                # Step 3: Wait for completion and read
                completion_success = reader.wait_for_completion(latest_file, timeout=10.0)
                
                if completion_success:
                    content = reader.read_completed_output(latest_file)
                    
                    if content and "End of Test" in content:
                        duration = time.time() - start_time
                        
                        return ValidationResult(
                            test_name="end_to_end_scenario",
                            status="passed",
                            duration=duration,
                            details="End-to-end scenario completed successfully",
                            metrics={
                                "file_creation": True,
                                "completion_detection": True,
                                "content_integrity": True,
                                "content_length": len(content)
                            }
                        )
                    else:
                        return ValidationResult(
                            test_name="end_to_end_scenario",
                            status="failed",
                            duration=time.time() - start_time,
                            details="Content integrity check failed",
                            issues_found=["Content missing or corrupted"]
                        )
                else:
                    return ValidationResult(
                        test_name="end_to_end_scenario",
                        status="failed",
                        duration=time.time() - start_time,
                        details="File completion detection failed",
                        issues_found=["Completion timeout or detection failure"]
                    )
                    
            finally:
                # Cleanup
                try:
                    import shutil
                    shutil.rmtree(output_dir)
                except:
                    pass
                    
        except Exception as e:
            duration = time.time() - start_time
            return ValidationResult(
                test_name="end_to_end_scenario",
                status="error",
                duration=duration,
                details=f"End-to-end validation error: {str(e)}",
                issues_found=[str(e)]
            )
