#!/usr/bin/env python3
"""
Direct Function Test Runner

This runner executes test functions directly without any pytest infrastructure,
similar to the successful run_migration_test.py approach. It's designed for
maximum reliability and minimal overhead.
"""

import sys
import time
import traceback
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
import tempfile
import shutil

from .base_test_runner import BaseTestRunner, TestResult, TestSuite

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class DirectFunctionRunner(BaseTestRunner):
    """
    Executes test functions directly with minimal overhead.
    
    This runner is most similar to the working run_migration_test.py approach
    and provides maximum compatibility with existing test functions.
    """
    
    def __init__(self, output_dir: Union[str, Path] = None, verbose: bool = True):
        super().__init__(output_dir, verbose)
        
        # Configure for direct execution
        self.config.update({
            'timeout_per_test': 600.0,  # 10 minutes for complex tests
            'mock_pytest_fixtures': True,
            'provide_temp_dirs': True,
            'cleanup_temp_dirs': True
        })
    
    def discover_tests(self, test_path: Union[str, Path]) -> List[TestSuite]:
        """
        Discover test functions by importing modules and finding test_* functions.
        """
        test_path = Path(test_path)
        suites = []
        
        if test_path.is_file() and test_path.suffix == '.py':
            # Single test file
            suite = self._discover_from_file(test_path)
            if suite and suite.tests:
                suites.append(suite)
                
        elif test_path.is_dir():
            # Directory of test files
            for test_file in test_path.rglob("test_*.py"):
                suite = self._discover_from_file(test_file)
                if suite and suite.tests:
                    suites.append(suite)
        
        return suites
    
    def _discover_from_file(self, test_file: Path) -> Optional[TestSuite]:
        """Discover test functions from a single Python file."""
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(
                test_file.stem, test_file
            )
            if not spec or not spec.loader:
                if self.verbose:
                    print(f"⚠️ Could not load spec for {test_file}")
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find test functions
            test_functions = []
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and name.startswith('test_'):
                    test_functions.append(obj)
            
            if not test_functions:
                return None
            
            # Look for setup/teardown functions
            setup_func = getattr(module, 'setup_module', None)
            teardown_func = getattr(module, 'teardown_module', None)
            
            return TestSuite(
                name=test_file.stem,
                tests=test_functions,
                setup_func=setup_func,
                teardown_func=teardown_func,
                metadata={'file_path': str(test_file)}
            )
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to discover tests from {test_file}: {str(e)}")
            return None
    
    def execute_test(self, test_func: Callable, test_name: str) -> TestResult:
        """Execute a single test function with comprehensive output capture."""
        start_time = time.time()
        
        with self.capture_output(test_name) as output_session:
            try:
                if self.verbose:
                    print(f"\\n🔧 Executing: {test_name}")
                
                # Write test header to output
                if output_session:
                    output_session.write_line("="*60)
                    output_session.write_line(f"DIRECT FUNCTION TEST: {test_name}")
                    output_session.write_line("="*60)
                    output_session.write_line(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    output_session.write_line("")
                
                # Prepare test environment
                test_args, test_kwargs = self._prepare_test_environment(test_func)
                
                # Execute the test function
                print(f"Starting test: {test_name}")
                result = test_func(*test_args, **test_kwargs)
                print(f"Test completed: {test_name}")
                
                # Write success marker
                if output_session:
                    output_session.write_line("")
                    output_session.write_line("="*60)
                    output_session.write_line("TEST COMPLETED SUCCESSFULLY")
                    output_session.write_line("="*60)
                
                duration = time.time() - start_time
                
                return TestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    output_file=output_session.output_path if output_session else None,
                    metadata={'result': result}
                )
                
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                tb_info = traceback.format_exc()
                
                # Write error information
                if output_session:
                    output_session.write_line("")
                    output_session.write_line("="*60)
                    output_session.write_line("TEST FAILED WITH ERROR")
                    output_session.write_line("="*60)
                    output_session.write_line(f"Error: {error_msg}")
                    output_session.write_line("Traceback:")
                    output_session.write_line(tb_info)
                    output_session.write_line("="*60)
                
                print(f"❌ Test failed: {test_name} - {error_msg}")
                
                return TestResult(
                    test_name=test_name,
                    status="failed",
                    duration=duration,
                    output_file=output_session.output_path if output_session else None,
                    error_message=error_msg,
                    traceback_info=tb_info
                )
    
    def _prepare_test_environment(self, test_func: Callable) -> tuple:
        """
        Prepare the test environment by providing mock fixtures and arguments.
        
        This mimics pytest fixture behavior for tests that expect certain arguments.
        """
        import inspect
        
        # Get function signature
        sig = inspect.signature(test_func)
        test_args = []
        test_kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'tmp_path':
                # Provide temporary path (like pytest tmp_path fixture)
                tmp_dir = self._create_temp_directory()
                if param.annotation == Path or 'Path' in str(param.annotation):
                    test_kwargs[param_name] = tmp_dir
                else:
                    test_kwargs[param_name] = str(tmp_dir)
                    
            elif param_name == 'capsys':
                # Provide mock capsys fixture
                test_kwargs[param_name] = self._create_mock_capsys()
                
            elif param_name in ['tmpdir', 'tmpdir_factory']:
                # Provide temporary directory
                test_kwargs[param_name] = self._create_temp_directory()
                
            # Add more fixture mocks as needed
        
        return test_args, test_kwargs
    
    def _create_temp_directory(self) -> Path:
        """Create a temporary directory for tests."""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_runner_"))
        
        # Register for cleanup
        if not hasattr(self, '_temp_dirs'):
            self._temp_dirs = []
        self._temp_dirs.append(temp_dir)
        
        return temp_dir
    
    def _create_mock_capsys(self):
        """Create a mock capsys object for tests that expect it."""
        class MockCapsys:
            def readouterr(self):
                class CaptureResult:
                    def __init__(self):
                        self.out = ""
                        self.err = ""
                return CaptureResult()
        
        return MockCapsys()
    
    def cleanup_temp_directories(self):
        """Clean up temporary directories created during testing."""
        if hasattr(self, '_temp_dirs'):
            for temp_dir in self._temp_dirs:
                try:
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir)
                        if self.verbose:
                            print(f"🧹 Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Failed to cleanup {temp_dir}: {str(e)}")
            
            self._temp_dirs.clear()
    
    def run_all_tests(self, test_paths: List[Union[str, Path]]) -> List[TestResult]:
        """Run all tests with cleanup of temporary resources."""
        try:
            return super().run_all_tests(test_paths)
        finally:
            if self.config['cleanup_temp_dirs']:
                self.cleanup_temp_directories()


class MigrationTestRunner(DirectFunctionRunner):
    """
    Specialized runner for migration tests with enhanced output capture.
    
    This runner is specifically designed to handle the migration test that
    was experiencing truncation issues.
    """
    
    def __init__(self, output_dir: Union[str, Path] = None):
        super().__init__(output_dir, verbose=True)
        
        # Configure specifically for migration tests
        self.config.update({
            'timeout_per_test': 900.0,  # 15 minutes for migration tests
            'detailed_tracebacks': True,
            'capture_database_operations': True
        })
    
    def run_migration_test(self, test_module_path: str = None) -> TestResult:
        """
        Run the specific migration test with enhanced output.
        
        This method provides a direct way to run the migration test that was
        having truncation issues.
        """
        if test_module_path is None:
            test_module_path = str(project_root / "tests" / "unit" / "test_migration.py")
        
        # Discover the migration test
        suites = self.discover_tests(test_module_path)
        
        if not suites:
            raise ValueError(f"No test suites found in {test_module_path}")
        
        # Find the test_migration function
        migration_test = None
        for suite in suites:
            for test_func in suite.tests:
                if test_func.__name__ == 'test_migration':
                    migration_test = test_func
                    break
            if migration_test:
                break
        
        if not migration_test:
            raise ValueError("test_migration function not found")
        
        # Execute with enhanced output
        print("\\n🔄 Running Migration Test with Enhanced Output")
        print("="*60)
        
        result = self.execute_test(migration_test, "enhanced_migration_test")
        
        # Print results
        if result.status == "passed":
            print("\\n✅ Migration test completed successfully!")
            print(f"📁 Complete output saved to: {result.output_file}")
            print("\\n🔍 Output is now safe for LLM systems to read")
        else:
            print("\\n❌ Migration test failed!")
            print(f"Error: {result.error_message}")
            print(f"📁 Error details saved to: {result.output_file}")
        
        return result


def run_tests_directly(test_paths: List[str], output_dir: str = None, runner_type: str = "direct") -> bool:
    """
    Convenience function to run tests directly without pytest.
    
    Args:
        test_paths: List of paths to test files or directories
        output_dir: Directory to save test outputs
        runner_type: Type of runner ("direct", "migration")
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    
    if runner_type == "migration":
        runner = MigrationTestRunner(output_dir)
    else:
        runner = DirectFunctionRunner(output_dir)
    
    try:
        results = runner.run_all_tests(test_paths)
        
        # Check if all tests passed
        return all(r.status == "passed" for r in results)
        
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Command-line interface for the direct runner
    import argparse
    
    parser = argparse.ArgumentParser(description="Direct Function Test Runner")
    parser.add_argument("test_paths", nargs="+", help="Paths to test files or directories")
    parser.add_argument("--output-dir", help="Output directory for test results")
    parser.add_argument("--runner-type", choices=["direct", "migration"], default="direct",
                       help="Type of test runner to use")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    success = run_tests_directly(
        test_paths=args.test_paths,
        output_dir=args.output_dir,
        runner_type=args.runner_type
    )
    
    sys.exit(0 if success else 1)
