#!/usr/bin/env python3
"""
Base Test Runner Framework

This module provides a foundation for creating alternative test runners that
bypass pytest entirely while providing comprehensive output capture, error
handling, and test execution capabilities.

Key Design Principles:
- Direct test execution (no pytest overhead)
- Comprehensive output capture without truncation
- Modular and extensible architecture
- Robust error handling and reporting
- Integration with file-based output system
"""

import os
import sys
import time
import traceback
import importlib.util
import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader

logger = logging.getLogger("test_runner")


@dataclass
class TestResult:
    """Represents the result of a single test execution."""
    test_name: str
    status: str  # passed, failed, error, skipped
    duration: float
    output_file: Optional[Path] = None
    error_message: Optional[str] = None
    traceback_info: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Represents a collection of tests to be executed."""
    name: str
    tests: List[Callable]
    setup_func: Optional[Callable] = None
    teardown_func: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseTestRunner(ABC):
    """
    Abstract base class for alternative test runners.
    
    Provides common functionality for test discovery, execution, and reporting
    while allowing subclasses to implement specific test execution strategies.
    """
    
    def __init__(self, output_dir: Union[str, Path] = None, verbose: bool = True):
        if output_dir is None:
            output_dir = Path.cwd() / "test_runner_outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.verbose = verbose
        self.test_writer = TestOutputWriter(self.output_dir)
        self.test_reader = TestOutputReader(self.output_dir)
        
        # Test execution tracking
        self.executed_tests: List[TestResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Configuration
        self.config = {
            'timeout_per_test': 300.0,  # 5 minutes per test
            'max_retries': 1,
            'stop_on_first_failure': False,
            'capture_stdout': True,
            'capture_stderr': True,
            'detailed_tracebacks': True
        }
    
    def configure(self, **kwargs):
        """Update runner configuration."""
        self.config.update(kwargs)
        if self.verbose:
            print(f"Updated configuration: {kwargs}")
    
    @abstractmethod
    def discover_tests(self, test_path: Union[str, Path]) -> List[TestSuite]:
        """Discover tests from the given path. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def execute_test(self, test_func: Callable, test_name: str) -> TestResult:
        """Execute a single test. Must be implemented by subclasses."""
        pass
    
    def run_test_suite(self, test_suite: TestSuite) -> List[TestResult]:
        """Execute all tests in a test suite."""
        results = []
        
        if self.verbose:
            print(f"\\n{'='*60}")
            print(f"Running Test Suite: {test_suite.name}")
            print(f"{'='*60}")
        
        # Run suite setup
        if test_suite.setup_func:
            try:
                if self.verbose:
                    print("Running suite setup...")
                test_suite.setup_func()
                if self.verbose:
                    print("✅ Suite setup completed")
            except Exception as e:
                if self.verbose:
                    print(f"❌ Suite setup failed: {str(e)}")
                # Create a failed result for setup
                setup_result = TestResult(
                    test_name=f"{test_suite.name}_setup",
                    status="failed",
                    duration=0.0,
                    error_message=str(e),
                    traceback_info=traceback.format_exc()
                )
                results.append(setup_result)
                return results  # Skip tests if setup fails
        
        # Execute tests
        for test_func in test_suite.tests:
            test_name = f"{test_suite.name}.{test_func.__name__}"
            
            try:
                result = self.execute_test(test_func, test_name)
                results.append(result)
                
                if self.verbose:
                    status_symbol = "✅" if result.status == "passed" else "❌"
                    print(f"{status_symbol} {test_name} ({result.duration:.2f}s): {result.status}")
                
                # Stop on first failure if configured
                if result.status in ["failed", "error"] and self.config['stop_on_first_failure']:
                    if self.verbose:
                        print("⚠️ Stopping on first failure as configured")
                    break
                    
            except Exception as e:
                # Handle test execution framework errors
                error_result = TestResult(
                    test_name=test_name,
                    status="error",
                    duration=0.0,
                    error_message=f"Test execution error: {str(e)}",
                    traceback_info=traceback.format_exc()
                )
                results.append(error_result)
                
                if self.verbose:
                    print(f"💥 {test_name}: EXECUTION ERROR - {str(e)}")
        
        # Run suite teardown
        if test_suite.teardown_func:
            try:
                if self.verbose:
                    print("Running suite teardown...")
                test_suite.teardown_func()
                if self.verbose:
                    print("✅ Suite teardown completed")
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Suite teardown failed: {str(e)}")
                # Create a warning result for teardown
                teardown_result = TestResult(
                    test_name=f"{test_suite.name}_teardown",
                    status="failed",
                    duration=0.0,
                    error_message=str(e),
                    traceback_info=traceback.format_exc()
                )
                results.append(teardown_result)
        
        return results
    
    def run_all_tests(self, test_paths: List[Union[str, Path]]) -> List[TestResult]:
        """Run all tests from the given paths."""
        self.start_time = datetime.utcnow()
        all_results = []
        
        if self.verbose:
            print(f"\\n🚀 Starting test execution at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Output directory: {self.output_dir}")
        
        try:
            # Discover all test suites
            all_suites = []
            for test_path in test_paths:
                try:
                    suites = self.discover_tests(test_path)
                    all_suites.extend(suites)
                    if self.verbose:
                        print(f"📁 Discovered {len(suites)} test suites from {test_path}")
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Failed to discover tests from {test_path}: {str(e)}")
            
            if not all_suites:
                if self.verbose:
                    print("⚠️ No test suites found!")
                return all_results
            
            # Execute all test suites
            for suite in all_suites:
                suite_results = self.run_test_suite(suite)
                all_results.extend(suite_results)
                self.executed_tests.extend(suite_results)
        
        finally:
            self.end_time = datetime.utcnow()
            
        # Generate summary
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, results: List[TestResult]):
        """Print a comprehensive test execution summary."""
        if not self.verbose:
            return
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Count results by status
        status_counts = {}
        for result in results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        print(f"\\n{'='*60}")
        print("TEST EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total tests: {len(results)}")
        print(f"Execution time: {total_duration:.2f} seconds")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Status breakdown
        for status, count in status_counts.items():
            symbol = {"passed": "✅", "failed": "❌", "error": "💥", "skipped": "⏭️"}.get(status, "❓")
            print(f"{symbol} {status.upper()}: {count}")
        
        # Show failed tests
        failed_tests = [r for r in results if r.status in ["failed", "error"]]
        if failed_tests:
            print(f"\\n❌ FAILED TESTS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  - {result.test_name}: {result.error_message or 'No error message'}")
        
        # Overall result
        overall_success = all(r.status == "passed" for r in results if r.status != "skipped")
        
        print(f"\\n{'='*60}")
        if overall_success:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        print(f"{'='*60}")
        
        # Output file locations
        output_files = [r.output_file for r in results if r.output_file]
        if output_files:
            print(f"\\n📁 Test output files: {len(output_files)}")
            print(f"   Location: {self.output_dir}")
    
    @contextmanager
    def capture_output(self, test_name: str):
        """Context manager for capturing test output."""
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        output_session = None
        
        try:
            if self.config['capture_stdout'] or self.config['capture_stderr']:
                # Use file-based output system
                output_session = self.test_writer.write_test_output(test_name, "text")
                output_session.__enter__()
                
                # Create custom stdout/stderr that writes to both console and file
                class TeeWriter:
                    def __init__(self, original, session):
                        self.original = original
                        self.session = session
                    
                    def write(self, text):
                        self.original.write(text)  # Console output
                        if self.session and text.strip():  # File output (skip empty lines)
                            self.session.write_line(text.rstrip())
                    
                    def flush(self):
                        self.original.flush()
                
                if self.config['capture_stdout']:
                    sys.stdout = TeeWriter(original_stdout, output_session)
                if self.config['capture_stderr']:
                    sys.stderr = TeeWriter(original_stderr, output_session)
            
            yield output_session
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
            # Close output session
            if output_session:
                try:
                    output_session.__exit__(None, None, None)
                except Exception as e:
                    print(f"Warning: Failed to close output session: {str(e)}")
    
    def get_test_output(self, test_name: str, timeout: float = 30.0) -> Optional[str]:
        """Get the output for a specific test, waiting for completion if necessary."""
        # Find the output file for the test
        output_files = list(self.output_dir.glob(f"{test_name}_*.txt"))
        
        if not output_files:
            return None
        
        # Get the most recent file
        latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
        
        # Wait for completion and read
        if self.test_reader.wait_for_completion(latest_file, timeout):
            return self.test_reader.read_completed_output(latest_file)
        
        return None
