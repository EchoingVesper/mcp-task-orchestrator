#!/usr/bin/env python3
"""
Convenience scripts for alternative test runners.

These scripts provide easy-to-use alternatives to pytest commands.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_migration_test():
    """Run the migration test that was having truncation issues."""
    print("🔄 Running Migration Test (Alternative to pytest)")
    print("="*60)
    
    try:
        from mcp_task_orchestrator.testing.direct_runner import MigrationTestRunner
        
        runner = MigrationTestRunner()
        result = runner.run_migration_test()
        
        if result.status == "passed":
            print("\\n✅ SUCCESS: Migration test completed without issues!")
            print(f"📁 Complete output: {result.output_file}")
            return True
        else:
            print("\\n❌ FAILED: Migration test encountered issues")
            print(f"Error: {result.error_message}")
            print(f"📁 Error details: {result.output_file}")
            return False
            
    except Exception as e:
        print(f"💥 Failed to run migration test: {str(e)}")
        return False


def run_all_tests():
    """Run all tests using the comprehensive runner."""
    print("🚀 Running All Tests (Alternative to pytest)")
    print("="*60)
    
    try:
        from mcp_task_orchestrator.testing.comprehensive_runner import ComprehensiveTestRunner, TestRunnerConfig
        
        config = TestRunnerConfig(
            runner_types=['direct', 'integration', 'migration'],
            verbose=True
        )
        
        runner = ComprehensiveTestRunner(config)
        
        # Find test directories
        test_paths = []
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            test_paths.append(tests_dir)
        
        if not test_paths:
            print("⚠️ No test directories found")
            return False
        
        results = runner.run_all_tests(test_paths)
        
        # Check overall success
        success = all(
            all(r.status == "passed" for r in runner_results)
            for runner_results in results.values()
        )
        
        if success:
            print("\\n🎉 SUCCESS: All tests passed!")
        else:
            print("\\n❌ FAILURE: Some tests failed")
        
        return success
        
    except Exception as e:
        print(f"💥 Failed to run tests: {str(e)}")
        return False


def run_integration_tests():
    """Run only integration tests."""
    print("🔧 Running Integration Tests (Alternative to pytest)")
    print("="*60)
    
    try:
        from mcp_task_orchestrator.testing.integration_runner import IntegrationTestRunner
        
        runner = IntegrationTestRunner()
        
        # Find integration test directories
        test_paths = []
        integration_dirs = [
            project_root / "tests" / "integration",
            project_root / "tests"  # Will auto-detect integration tests
        ]
        
        for path in integration_dirs:
            if path.exists():
                test_paths.append(path)
        
        if not test_paths:
            print("⚠️ No integration test directories found")
            return False
        
        results = runner.run_all_tests(test_paths)
        success = all(r.status == "passed" for r in results)
        
        if success:
            print("\\n✅ SUCCESS: All integration tests passed!")
        else:
            print("\\n❌ FAILURE: Some integration tests failed")
        
        return success
        
    except Exception as e:
        print(f"💥 Failed to run integration tests: {str(e)}")
        return False


def compare_with_pytest():
    """Compare output between pytest and alternative runners."""
    print("📊 Comparing pytest vs Alternative Test Runners")
    print("="*60)
    
    # Run with pytest
    print("\\n🔍 Running with pytest...")
    pytest_cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    try:
        pytest_result = subprocess.run(
            pytest_cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,
            cwd=str(project_root)
        )
        pytest_success = pytest_result.returncode == 0
        pytest_output_lines = len(pytest_result.stdout.split('\\n'))
        
        print(f"   Pytest result: {'PASSED' if pytest_success else 'FAILED'}")
        print(f"   Pytest output lines: {pytest_output_lines}")
        
    except subprocess.TimeoutExpired:
        print("   Pytest result: TIMEOUT")
        pytest_success = False
        pytest_output_lines = 0
    except Exception as e:
        print(f"   Pytest result: ERROR - {str(e)}")
        pytest_success = False
        pytest_output_lines = 0
    
    # Run with alternative runner
    print("\\n🔧 Running with alternative runner...")
    
    try:
        alt_success = run_all_tests()
        
        print(f"   Alternative result: {'PASSED' if alt_success else 'FAILED'}")
        
        # Count output files
        from mcp_task_orchestrator.testing.comprehensive_runner import TestRunnerConfig
        config = TestRunnerConfig()
        output_files = list(config.output_dir.rglob("*.txt"))
        total_output_lines = 0
        
        for output_file in output_files:
            try:
                with open(output_file, 'r') as f:
                    total_output_lines += len(f.readlines())
            except:
                pass
        
        print(f"   Alternative output files: {len(output_files)}")
        print(f"   Alternative total output lines: {total_output_lines}")
        
    except Exception as e:
        print(f"   Alternative result: ERROR - {str(e)}")
        alt_success = False
        total_output_lines = 0
    
    # Summary
    print("\\n📋 Comparison Summary:")
    print(f"   Pytest: {'✅' if pytest_success else '❌'} ({pytest_output_lines} lines)")
    print(f"   Alternative: {'✅' if alt_success else '❌'} ({total_output_lines} lines)")
    
    if total_output_lines > pytest_output_lines:
        print("\\n🎯 Alternative runner captured more output (no truncation)")
    elif total_output_lines < pytest_output_lines:
        print("\\n⚠️ Alternative runner captured less output")
    else:
        print("\\n📊 Similar output volume")
    
    return alt_success


# Command-line interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Alternative Test Runner Scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Migration test command
    migration_parser = subparsers.add_parser("migration", help="Run migration test")
    
    # All tests command
    all_parser = subparsers.add_parser("all", help="Run all tests")
    
    # Integration tests command
    integration_parser = subparsers.add_parser("integration", help="Run integration tests")
    
    # Comparison command
    compare_parser = subparsers.add_parser("compare", help="Compare with pytest")
    
    args = parser.parse_args()
    
    if args.command == "migration":
        success = run_migration_test()
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "compare":
        success = compare_with_pytest()
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
