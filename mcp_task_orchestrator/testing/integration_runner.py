#!/usr/bin/env python3
"""
Integration Test Runner

This runner is designed for integration tests that require async operations,
database connections, and complex setup/teardown procedures.
"""

import asyncio
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union

from .base_test_runner import BaseTestRunner, TestResult, TestSuite

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class IntegrationTestRunner(BaseTestRunner):
    """
    Specialized runner for integration tests with async support and
    database connection management.
    """
    
    def __init__(self, output_dir: Union[str, Path] = None, verbose: bool = True):
        super().__init__(output_dir, verbose)
        
        # Configure for integration tests
        self.config.update({
            'timeout_per_test': 1200.0,  # 20 minutes for integration tests
            'support_async_tests': True,
            'manage_database_connections': True,
            'setup_test_environment': True,
            'parallel_execution': False  # Sequential by default for stability
        })
        
        # Integration test specific state
        self.database_managers = []
        self.async_loop = None
    
    def discover_tests(self, test_path: Union[str, Path]) -> List[TestSuite]:
        """Discover integration tests with async support."""
        test_path = Path(test_path)
        suites = []
        
        if test_path.is_file() and test_path.suffix == '.py':
            suite = self._discover_integration_tests_from_file(test_path)
            if suite and suite.tests:
                suites.append(suite)
        elif test_path.is_dir():
            for test_file in test_path.rglob("test_*.py"):
                if "integration" in str(test_file) or "integration" in test_file.parent.name:
                    suite = self._discover_integration_tests_from_file(test_file)
                    if suite and suite.tests:
                        suites.append(suite)
        
        return suites
    
    def _discover_integration_tests_from_file(self, test_file: Path) -> Optional[TestSuite]:
        """Discover integration tests with special handling for async functions."""
        try:
            import importlib.util
            
            spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find test functions (including async)
            test_functions = []
            async_test_functions = []
            
            for name in dir(module):
                obj = getattr(module, name)
                if callable(obj) and name.startswith('test_'):
                    if asyncio.iscoroutinefunction(obj):
                        async_test_functions.append(obj)
                    else:
                        test_functions.append(obj)
            
            all_tests = test_functions + async_test_functions
            
            if not all_tests:
                return None
            
            # Look for setup/teardown functions
            setup_func = getattr(module, 'setup_module', None)
            teardown_func = getattr(module, 'teardown_module', None)
            
            return TestSuite(
                name=f"integration_{test_file.stem}",
                tests=all_tests,
                setup_func=setup_func,
                teardown_func=teardown_func,
                metadata={
                    'file_path': str(test_file),
                    'has_async_tests': len(async_test_functions) > 0,
                    'async_test_count': len(async_test_functions)
                }
            )
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to discover integration tests from {test_file}: {str(e)}")
            return None
    
    def execute_test(self, test_func: Callable, test_name: str) -> TestResult:
        """Execute a test function with async support and enhanced error handling."""
        start_time = time.time()
        
        with self.capture_output(test_name) as output_session:
            try:
                if self.verbose:
                    print(f"\\n🔧 Executing integration test: {test_name}")
                
                # Write test header
                if output_session:
                    output_session.write_line("="*60)
                    output_session.write_line(f"INTEGRATION TEST: {test_name}")
                    output_session.write_line("="*60)
                    output_session.write_line(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    output_session.write_line(f"Test type: {'ASYNC' if asyncio.iscoroutinefunction(test_func) else 'SYNC'}")
                    output_session.write_line("")
                
                # Setup test environment
                self._setup_integration_environment()
                
                # Execute based on function type
                if asyncio.iscoroutinefunction(test_func):
                    result = self._execute_async_test(test_func, test_name, output_session)
                else:
                    result = self._execute_sync_test(test_func, test_name, output_session)
                
                # Write success marker
                if output_session:
                    output_session.write_line("")
                    output_session.write_line("="*60)
                    output_session.write_line("INTEGRATION TEST COMPLETED SUCCESSFULLY")
                    output_session.write_line("="*60)
                
                duration = time.time() - start_time
                
                return TestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    output_file=output_session.output_path if output_session else None,
                    metadata={'result': result, 'test_type': 'integration'}
                )
                
            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)
                tb_info = traceback.format_exc()
                
                # Write error information
                if output_session:
                    output_session.write_line("")
                    output_session.write_line("="*60)
                    output_session.write_line("INTEGRATION TEST FAILED")
                    output_session.write_line("="*60)
                    output_session.write_line(f"Error: {error_msg}")
                    output_session.write_line("Traceback:")
                    output_session.write_line(tb_info)
                    output_session.write_line("="*60)
                
                print(f"❌ Integration test failed: {test_name} - {error_msg}")
                
                return TestResult(
                    test_name=test_name,
                    status="failed",
                    duration=duration,
                    output_file=output_session.output_path if output_session else None,
                    error_message=error_msg,
                    traceback_info=tb_info
                )
            finally:
                # Cleanup test environment
                self._cleanup_integration_environment()
    
    def _execute_async_test(self, test_func: Callable, test_name: str, output_session) -> Any:
        """Execute an async test function."""
        if output_session:
            output_session.write_line("Executing async test function...")
        
        print(f"🔄 Running async integration test: {test_name}")
        
        # Create or use existing event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Prepare arguments
        test_args, test_kwargs = self._prepare_integration_environment(test_func)
        
        # Run the async test with timeout
        try:
            result = loop.run_until_complete(
                asyncio.wait_for(
                    test_func(*test_args, **test_kwargs),
                    timeout=self.config['timeout_per_test']
                )
            )
            
            if output_session:
                output_session.write_line("✅ Async test completed successfully")
            
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Async test {test_name} timed out after {self.config['timeout_per_test']} seconds"
            if output_session:
                output_session.write_line(f"❌ {error_msg}")
            raise TimeoutError(error_msg)
    
    def _execute_sync_test(self, test_func: Callable, test_name: str, output_session) -> Any:
        """Execute a synchronous test function."""
        if output_session:
            output_session.write_line("Executing sync test function...")
        
        print(f"⚙️ Running sync integration test: {test_name}")
        
        # Prepare arguments
        test_args, test_kwargs = self._prepare_integration_environment(test_func)
        
        # Execute the test
        result = test_func(*test_args, **test_kwargs)
        
        if output_session:
            output_session.write_line("✅ Sync test completed successfully")
        
        return result
    
    def _setup_integration_environment(self):
        """Setup the integration test environment."""
        if self.verbose:
            print("🔧 Setting up integration test environment...")
        
        # Initialize database connections if needed
        if self.config['manage_database_connections']:
            self._setup_database_connections()
        
        # Setup other integration test requirements
        # (This can be extended based on specific needs)
    
    def _cleanup_integration_environment(self):
        """Cleanup the integration test environment."""
        if self.verbose:
            print("🧹 Cleaning up integration test environment...")
        
        # Cleanup database connections
        self._cleanup_database_connections()
        
        # Other cleanup tasks
    
    def _setup_database_connections(self):
        """Setup database connections for integration tests."""
        try:
            # Import database managers
            from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
            
            # Create test database manager
            test_db_manager = DatabasePersistenceManager(
                base_dir=self.output_dir / "test_db",
                db_url="sqlite:///test_integration.db"
            )
            
            self.database_managers.append(test_db_manager)
            
            if self.verbose:
                print("✅ Database connections established")
                
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to setup database connections: {str(e)}")
    
    def _cleanup_database_connections(self):
        """Cleanup database connections."""
        for db_manager in self.database_managers:
            try:
                if hasattr(db_manager, 'dispose'):
                    db_manager.dispose()
                elif hasattr(db_manager, 'engine'):
                    db_manager.engine.dispose()
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Failed to cleanup database manager: {str(e)}")
        
        self.database_managers.clear()
    
    def _prepare_integration_environment(self, test_func: Callable) -> tuple:
        """Prepare the integration test environment with appropriate fixtures."""
        import inspect
        import tempfile
        
        sig = inspect.signature(test_func)
        test_args = []
        test_kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'state_manager':
                # Provide StateManager instance
                try:
                    from mcp_task_orchestrator.orchestrator.state import StateManager
                    test_kwargs[param_name] = StateManager(base_dir=str(self.output_dir))
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Could not provide StateManager: {str(e)}")
                    
            elif param_name == 'orchestrator':
                # Provide TaskOrchestrator instance
                try:
                    from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
                    from mcp_task_orchestrator.orchestrator.state import StateManager
                    from mcp_task_orchestrator.orchestrator.specialists import SpecialistManager
                    
                    state_manager = StateManager(base_dir=str(self.output_dir))
                    specialist_manager = SpecialistManager()
                    test_kwargs[param_name] = TaskOrchestrator(state_manager, specialist_manager)
                except Exception as e:
                    if self.verbose:
                        print(f"⚠️ Could not provide TaskOrchestrator: {str(e)}")
                    
            elif param_name == 'persistence':
                # Provide persistence manager
                if self.database_managers:
                    test_kwargs[param_name] = self.database_managers[0]
                    
            elif param_name in ['tmp_path', 'tmpdir']:
                # Provide temporary directory
                temp_dir = Path(tempfile.mkdtemp(prefix="integration_test_"))
                test_kwargs[param_name] = temp_dir
        
        return test_args, test_kwargs


class AsyncTestRunner(IntegrationTestRunner):
    """
    Specialized runner focused specifically on async test execution.
    """
    
    def __init__(self, output_dir: Union[str, Path] = None, verbose: bool = True):
        super().__init__(output_dir, verbose)
        
        # Configure specifically for async tests
        self.config.update({
            'timeout_per_test': 300.0,  # 5 minutes for async tests
            'support_async_tests': True,
            'manage_database_connections': False,  # Let tests manage their own connections
            'parallel_execution': True  # Async tests can often run in parallel
        })
    
    def discover_tests(self, test_path: Union[str, Path]) -> List[TestSuite]:
        """Discover only async test functions."""
        suites = super().discover_tests(test_path)
        
        # Filter to only include async tests
        async_suites = []
        for suite in suites:
            async_tests = [test for test in suite.tests if asyncio.iscoroutinefunction(test)]
            if async_tests:
                async_suite = TestSuite(
                    name=f"async_{suite.name}",
                    tests=async_tests,
                    setup_func=suite.setup_func,
                    teardown_func=suite.teardown_func,
                    metadata={**suite.metadata, 'async_only': True}
                )
                async_suites.append(async_suite)
        
        return async_suites


if __name__ == "__main__":
    # Command-line interface for integration test runner
    import argparse
    
    parser = argparse.ArgumentParser(description="Integration Test Runner")
    parser.add_argument("test_paths", nargs="+", help="Paths to integration test files")
    parser.add_argument("--output-dir", help="Output directory for test results")
    parser.add_argument("--runner-type", choices=["integration", "async"], default="integration",
                       help="Type of integration runner")
    parser.add_argument("--timeout", type=float, help="Timeout per test in seconds")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    if args.runner_type == "async":
        runner = AsyncTestRunner(args.output_dir, not args.quiet)
    else:
        runner = IntegrationTestRunner(args.output_dir, not args.quiet)
    
    if args.timeout:
        runner.configure(timeout_per_test=args.timeout)
    
    try:
        results = runner.run_all_tests(args.test_paths)
        success = all(r.status == "passed" for r in results)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"💥 Integration test execution failed: {str(e)}")
        sys.exit(1)
