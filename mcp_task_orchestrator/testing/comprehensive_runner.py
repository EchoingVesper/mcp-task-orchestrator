#!/usr/bin/env python3
"""
Comprehensive Test Runner

This is the main entry point for the alternative test running system.
It orchestrates different specialized runners and provides a unified
interface for executing all types of tests without pytest.
"""

import sys
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .direct_runner import DirectFunctionRunner, MigrationTestRunner
from .integration_runner import IntegrationTestRunner, AsyncTestRunner
from .base_test_runner import TestResult, TestSuite


@dataclass
class TestRunnerConfig:
    """Configuration for the comprehensive test runner."""
    output_dir: Optional[Path] = None
    runner_types: List[str] = None  # ['direct', 'integration', 'migration', 'async']
    timeout_per_test: float = 600.0
    stop_on_first_failure: bool = False
    parallel_execution: bool = False
    verbose: bool = True
    cleanup_outputs: bool = False
    
    def __post_init__(self):
        if self.runner_types is None:
            self.runner_types = ['direct', 'integration']
        
        if self.output_dir is None:
            self.output_dir = Path.cwd() / "comprehensive_test_outputs"


class ComprehensiveTestRunner:
    """
    Main test runner that orchestrates different specialized runners.
    
    This runner automatically detects test types and uses the appropriate
    specialized runner for optimal results.
    """
    
    def __init__(self, config: TestRunnerConfig = None):
        self.config = config or TestRunnerConfig()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize specialized runners
        self.runners = {}
        self._initialize_runners()
        
        # Execution tracking
        self.execution_summary = {
            'start_time': None,
            'end_time': None,
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_errors': 0,
            'runner_results': {},
            'output_files': []
        }
    
    def _initialize_runners(self):
        """Initialize all the specialized test runners."""
        runner_output_dir = self.config.output_dir
        
        if 'direct' in self.config.runner_types:
            self.runners['direct'] = DirectFunctionRunner(
                runner_output_dir / "direct", 
                self.config.verbose
            )
        
        if 'migration' in self.config.runner_types:
            self.runners['migration'] = MigrationTestRunner(
                runner_output_dir / "migration"
            )
        
        if 'integration' in self.config.runner_types:
            self.runners['integration'] = IntegrationTestRunner(
                runner_output_dir / "integration", 
                self.config.verbose
            )
        
        if 'async' in self.config.runner_types:
            self.runners['async'] = AsyncTestRunner(
                runner_output_dir / "async", 
                self.config.verbose
            )
        
        # Configure all runners
        for runner in self.runners.values():
            runner.configure(
                timeout_per_test=self.config.timeout_per_test,
                stop_on_first_failure=self.config.stop_on_first_failure
            )
    
    def detect_test_type(self, test_path: Path) -> List[str]:
        """
        Automatically detect what type of test runners should handle a test file.
        
        Returns a list of runner types that should process this test.
        """
        test_path = Path(test_path)
        runner_types = []
        
        # Read file content to analyze
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for migration-specific patterns
            if 'migration' in test_path.name.lower() or 'migrate' in content.lower():
                if 'migration' in self.config.runner_types:
                    runner_types.append('migration')
            
            # Check for async patterns
            if 'async def test_' in content or 'await ' in content:
                if 'async' in self.config.runner_types:
                    runner_types.append('async')
            
            # Check for integration test patterns
            if ('integration' in str(test_path).lower() or 
                'orchestrator' in content or 'StateManager' in content or
                'TaskOrchestrator' in content):
                if 'integration' in self.config.runner_types:
                    runner_types.append('integration')
            
            # Default to direct runner if no specific patterns found
            if not runner_types and 'direct' in self.config.runner_types:
                runner_types.append('direct')
                
        except Exception as e:
            if self.config.verbose:
                print(f"⚠️ Could not analyze {test_path}: {str(e)}")
            # Default to direct runner on analysis failure
            if 'direct' in self.config.runner_types:
                runner_types.append('direct')
        
        return runner_types
    
    def run_all_tests(self, test_paths: List[Union[str, Path]]) -> Dict[str, List[TestResult]]:
        """
        Run all tests using the appropriate specialized runners.
        
        Returns a dictionary mapping runner names to their test results.
        """
        self.execution_summary['start_time'] = datetime.utcnow()
        
        if self.config.verbose:
            print("\\n" + "="*80)
            print("COMPREHENSIVE TEST RUNNER")
            print("="*80)
            print(f"Start time: {self.execution_summary['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Output directory: {self.config.output_dir}")
            print(f"Available runners: {list(self.runners.keys())}")
            print()
        
        # Group test paths by runner type
        runner_test_mapping = {}
        
        for test_path in test_paths:
            test_path = Path(test_path)
            
            if test_path.is_file():
                # Single test file
                runner_types = self.detect_test_type(test_path)
                for runner_type in runner_types:
                    if runner_type not in runner_test_mapping:
                        runner_test_mapping[runner_type] = []
                    runner_test_mapping[runner_type].append(test_path)
                    
            elif test_path.is_dir():
                # Directory of tests
                for test_file in test_path.rglob("test_*.py"):
                    runner_types = self.detect_test_type(test_file)
                    for runner_type in runner_types:
                        if runner_type not in runner_test_mapping:
                            runner_test_mapping[runner_type] = []
                        runner_test_mapping[runner_type].append(test_file)
        
        # Execute tests with each appropriate runner
        all_results = {}
        
        for runner_type, test_files in runner_test_mapping.items():
            if runner_type not in self.runners:
                if self.config.verbose:
                    print(f"⚠️ Runner type '{runner_type}' not available, skipping {len(test_files)} tests")
                continue
            
            if self.config.verbose:
                print(f"\\n🚀 Running {len(test_files)} tests with {runner_type} runner")
                print("-" * 60)
            
            try:
                runner = self.runners[runner_type]
                results = runner.run_all_tests(test_files)
                all_results[runner_type] = results
                
                # Update summary
                self.execution_summary['runner_results'][runner_type] = {
                    'test_count': len(results),
                    'passed': len([r for r in results if r.status == 'passed']),
                    'failed': len([r for r in results if r.status == 'failed']),
                    'errors': len([r for r in results if r.status == 'error'])
                }
                
                # Collect output files
                output_files = [r.output_file for r in results if r.output_file]
                self.execution_summary['output_files'].extend(output_files)
                
                if self.config.verbose:
                    passed = self.execution_summary['runner_results'][runner_type]['passed']
                    total = self.execution_summary['runner_results'][runner_type]['test_count']
                    print(f"✅ {runner_type} runner completed: {passed}/{total} tests passed")
                
            except Exception as e:
                if self.config.verbose:
                    print(f"❌ {runner_type} runner failed: {str(e)}")
                
                # Record runner failure
                self.execution_summary['runner_results'][runner_type] = {
                    'test_count': len(test_files),
                    'passed': 0,
                    'failed': 0,
                    'errors': len(test_files),
                    'runner_error': str(e)
                }
        
        self.execution_summary['end_time'] = datetime.utcnow()
        
        # Calculate totals
        for runner_stats in self.execution_summary['runner_results'].values():
            self.execution_summary['total_tests'] += runner_stats['test_count']
            self.execution_summary['total_passed'] += runner_stats['passed']
            self.execution_summary['total_failed'] += runner_stats['failed']
            self.execution_summary['total_errors'] += runner_stats['errors']
        
        # Print comprehensive summary
        self._print_comprehensive_summary()
        
        return all_results
    
    def run_specific_test(self, test_name: str, runner_type: str = None) -> Optional[TestResult]:
        """
        Run a specific test by name using the specified or auto-detected runner.
        
        This is useful for running individual tests like the migration test.
        """
        if runner_type and runner_type not in self.runners:
            raise ValueError(f"Runner type '{runner_type}' not available")
        
        # Special handling for known tests
        if test_name == "migration" or "migration" in test_name.lower():
            if 'migration' in self.runners:
                migration_runner = self.runners['migration']
                return migration_runner.run_migration_test()
        
        # General test execution
        # First, try to find the test file
        test_paths = [
            project_root / "tests" / "unit" / f"test_{test_name}.py",
            project_root / "tests" / "integration" / f"test_{test_name}.py",
            project_root / "tests" / f"test_{test_name}.py"
        ]
        
        test_file = None
        for path in test_paths:
            if path.exists():
                test_file = path
                break
        
        if not test_file:
            raise FileNotFoundError(f"Could not find test file for '{test_name}'")
        
        # Auto-detect runner type if not specified
        if not runner_type:
            runner_types = self.detect_test_type(test_file)
            runner_type = runner_types[0] if runner_types else 'direct'
        
        # Execute the test
        runner = self.runners[runner_type]
        results = runner.run_all_tests([test_file])
        
        # Return the first result (assuming single test)
        return results[0] if results else None
    
    def _print_comprehensive_summary(self):
        """Print a comprehensive summary of all test execution."""
        if not self.config.verbose:
            return
        
        duration = (self.execution_summary['end_time'] - self.execution_summary['start_time']).total_seconds()
        
        print("\\n" + "="*80)
        print("COMPREHENSIVE TEST EXECUTION SUMMARY")
        print("="*80)
        
        print(f"📊 Overall Statistics:")
        print(f"   Total tests: {self.execution_summary['total_tests']}")
        print(f"   Passed: {self.execution_summary['total_passed']}")
        print(f"   Failed: {self.execution_summary['total_failed']}")
        print(f"   Errors: {self.execution_summary['total_errors']}")
        print(f"   Duration: {duration:.2f} seconds")
        print()
        
        print(f"🔧 Runner Breakdown:")
        for runner_type, stats in self.execution_summary['runner_results'].items():
            if 'runner_error' in stats:
                print(f"   {runner_type}: RUNNER ERROR - {stats['runner_error']}")
            else:
                print(f"   {runner_type}: {stats['passed']}/{stats['test_count']} passed")
        print()
        
        print(f"📁 Output Files: {len(self.execution_summary['output_files'])}")
        print(f"   Location: {self.config.output_dir}")
        
        # Overall result
        success_rate = (self.execution_summary['total_passed'] / 
                       max(self.execution_summary['total_tests'], 1)) * 100
        
        print("\\n" + "="*80)
        if success_rate == 100.0:
            print("🎉 ALL TESTS PASSED!")
        elif success_rate >= 80.0:
            print(f"✅ MOSTLY SUCCESSFUL ({success_rate:.1f}% passed)")
        else:
            print(f"❌ MANY FAILURES ({success_rate:.1f}% passed)")
        print("="*80)
    
    def get_test_output(self, test_name: str, runner_type: str = None) -> Optional[str]:
        """Get the output for a specific test from any runner."""
        if runner_type and runner_type in self.runners:
            return self.runners[runner_type].get_test_output(test_name)
        
        # Search all runners
        for runner in self.runners.values():
            output = runner.get_test_output(test_name)
            if output:
                return output
        
        return None
    
    def cleanup_outputs(self):
        """Clean up output files if configured to do so."""
        if not self.config.cleanup_outputs:
            return
        
        try:
            import shutil
            if self.config.output_dir.exists():
                shutil.rmtree(self.config.output_dir)
                if self.config.verbose:
                    print(f"🧹 Cleaned up output directory: {self.config.output_dir}")
        except Exception as e:
            if self.config.verbose:
                print(f"⚠️ Failed to cleanup outputs: {str(e)}")


def main():
    """Command-line interface for the comprehensive test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner - Alternative to pytest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests in a directory
  python -m mcp_task_orchestrator.testing.comprehensive_runner tests/
  
  # Run specific test types
  python -m mcp_task_orchestrator.testing.comprehensive_runner tests/ --runners direct integration
  
  # Run the migration test specifically
  python -m mcp_task_orchestrator.testing.comprehensive_runner --test migration
  
  # Run with custom timeout and output directory
  python -m mcp_task_orchestrator.testing.comprehensive_runner tests/ --timeout 300 --output-dir ./my_test_outputs
        """
    )
    
    parser.add_argument("test_paths", nargs="*", help="Paths to test files or directories")
    parser.add_argument("--test", help="Run a specific test by name")
    parser.add_argument("--runners", nargs="+", 
                       choices=['direct', 'migration', 'integration', 'async'],
                       default=['direct', 'integration', 'migration'],
                       help="Test runner types to use")
    parser.add_argument("--output-dir", type=Path, help="Output directory for test results")
    parser.add_argument("--timeout", type=float, default=600.0, help="Timeout per test in seconds")
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop on first test failure")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--cleanup", action="store_true", help="Clean up output files after execution")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.test_paths and not args.test:
        parser.error("Must specify either test paths or --test")
    
    # Create configuration
    config = TestRunnerConfig(
        output_dir=args.output_dir,
        runner_types=args.runners,
        timeout_per_test=args.timeout,
        stop_on_first_failure=args.stop_on_failure,
        verbose=not args.quiet,
        cleanup_outputs=args.cleanup
    )
    
    # Create and run tests
    try:
        runner = ComprehensiveTestRunner(config)
        
        if args.test:
            # Run specific test
            result = runner.run_specific_test(args.test)
            success = result and result.status == "passed"
        else:
            # Run all tests
            results = runner.run_all_tests(args.test_paths)
            success = all(
                all(r.status == "passed" for r in runner_results)
                for runner_results in results.values()
            )
        
        # Cleanup if requested
        if args.cleanup:
            runner.cleanup_outputs()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
