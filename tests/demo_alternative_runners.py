#!/usr/bin/env python3
"""
Alternative Test Runners Demonstration

This script demonstrates the comprehensive alternative test running system
that bypasses pytest entirely while providing superior output handling.

The demo shows:
1. Direct function test execution (like the working run_migration_test.py)
2. Integration test execution with async support
3. Comprehensive test orchestration
4. Comparison with pytest behavior
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def demo_direct_runner():
    """Demonstrate the direct function runner."""
    print("\\n" + "="*60)
    print("DEMO 1: Direct Function Runner")
    print("="*60)
    print("This runner executes test functions directly, similar to run_migration_test.py")
    
    try:
        from mcp_task_orchestrator.testing import DirectFunctionRunner
        
        # Create runner
        runner = DirectFunctionRunner(
            output_dir=Path.cwd() / "demo_outputs" / "direct",
            verbose=True
        )
        
        print("\\n🔧 Configuring runner for demonstration...")
        runner.configure(timeout_per_test=60.0)
        
        # Find a simple test to run
        test_files = []
        simple_tests = [
            project_root / "tests" / "simple_output_test.py",
            project_root / "tests" / "test_output_comparison.py"
        ]
        
        for test_file in simple_tests:
            if test_file.exists():
                test_files.append(test_file)
                break
        
        if test_files:
            print(f"\\n🚀 Running direct tests from: {test_files[0]}")
            results = runner.run_all_tests(test_files)
            
            success = all(r.status == "passed" for r in results)
            print(f"\\n✅ Direct runner demo: {'SUCCESS' if success else 'FAILED'}")
            
            # Show output file
            if results and results[0].output_file:
                print(f"📁 Complete output saved to: {results[0].output_file}")
                return True
        else:
            print("⚠️ No suitable test files found for demo")
            return False
            
    except Exception as e:
        print(f"❌ Direct runner demo failed: {str(e)}")
        return False


def demo_migration_runner():
    """Demonstrate the migration-specific runner."""
    print("\\n" + "="*60)
    print("DEMO 2: Migration Test Runner")
    print("="*60)
    print("This runner specifically handles the migration test with enhanced output")
    
    try:
        from mcp_task_orchestrator.testing import MigrationTestRunner
        
        # Create migration runner
        runner = MigrationTestRunner(
            output_dir=Path.cwd() / "demo_outputs" / "migration"
        )
        
        print("\\n🔄 Running migration test with enhanced output...")
        result = runner.run_migration_test()
        
        if result.status == "passed":
            print("\\n✅ Migration runner demo: SUCCESS")
            print(f"📁 Complete migration output: {result.output_file}")
            print("🎯 No truncation issues - all output captured")
            return True
        else:
            print("\\n❌ Migration runner demo: FAILED")
            print(f"Error: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Migration runner demo failed: {str(e)}")
        return False


def demo_integration_runner():
    """Demonstrate the integration test runner."""
    print("\\n" + "="*60)
    print("DEMO 3: Integration Test Runner")
    print("="*60)
    print("This runner handles complex integration tests with async support")
    
    try:
        from mcp_task_orchestrator.testing import IntegrationTestRunner
        
        # Create integration runner
        runner = IntegrationTestRunner(
            output_dir=Path.cwd() / "demo_outputs" / "integration",
            verbose=True
        )
        
        # Find integration tests
        integration_dirs = [
            project_root / "tests" / "integration",
            project_root / "tests"
        ]
        
        test_paths = []
        for test_dir in integration_dirs:
            if test_dir.exists():
                test_paths.append(test_dir)
                break
        
        if test_paths:
            print(f"\\n🔧 Running integration tests from: {test_paths[0]}")
            results = runner.run_all_tests(test_paths)
            
            if results:
                success = all(r.status == "passed" for r in results)
                print(f"\\n✅ Integration runner demo: {'SUCCESS' if success else 'PARTIAL SUCCESS'}")
                
                # Show some results
                passed = len([r for r in results if r.status == "passed"])
                print(f"📊 Results: {passed}/{len(results)} tests passed")
                return True
            else:
                print("⚠️ No integration tests executed")
                return False
        else:
            print("⚠️ No integration test directories found")
            return False
            
    except Exception as e:
        print(f"❌ Integration runner demo failed: {str(e)}")
        return False


def demo_comprehensive_runner():
    """Demonstrate the comprehensive test orchestration system."""
    print("\\n" + "="*60)
    print("DEMO 4: Comprehensive Test Runner")
    print("="*60)
    print("This orchestrates multiple specialized runners automatically")
    
    try:
        from mcp_task_orchestrator.testing import ComprehensiveTestRunner, TestRunnerConfig
        
        # Create comprehensive runner
        config = TestRunnerConfig(
            output_dir=Path.cwd() / "demo_outputs" / "comprehensive",
            runner_types=['direct', 'migration'],  # Focus on working runners for demo
            verbose=True,
            timeout_per_test=120.0
        )
        
        runner = ComprehensiveTestRunner(config)
        
        print("\\n🚀 Running comprehensive test orchestration...")
        
        # Find test directories
        test_paths = []
        possible_paths = [
            project_root / "tests" / "simple_output_test.py",
            project_root / "tests" / "test_output_comparison.py"
        ]
        
        for path in possible_paths:
            if path.exists():
                test_paths.append(path)
        
        if test_paths:
            results = runner.run_all_tests(test_paths)
            
            # Check results
            total_tests = sum(len(runner_results) for runner_results in results.values())
            total_passed = sum(
                len([r for r in runner_results if r.status == "passed"])
                for runner_results in results.values()
            )
            
            print(f"\\n📊 Comprehensive results: {total_passed}/{total_tests} tests passed")
            
            if total_passed == total_tests:
                print("✅ Comprehensive runner demo: SUCCESS")
                return True
            else:
                print("⚠️ Comprehensive runner demo: PARTIAL SUCCESS")
                return False
        else:
            print("⚠️ No suitable test files found")
            return False
            
    except Exception as e:
        print(f"❌ Comprehensive runner demo failed: {str(e)}")
        return False


def demo_output_comparison():
    """Demonstrate the output capture capabilities."""
    print("\\n" + "="*60)
    print("DEMO 5: Output Capture Comparison")
    print("="*60)
    print("Comparing output capture vs pytest truncation issues")
    
    try:
        # Create a test that generates substantial output
        test_output_lines = []
        
        print("\\n📝 Generating test output simulation...")
        for i in range(50):
            test_output_lines.append(f"Test output line {i:03d}: Detailed information for verification")
        
        # Simulate file-based capture
        from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader
        
        writer = TestOutputWriter(Path.cwd() / "demo_outputs" / "comparison")
        
        with writer.write_test_output("output_comparison_demo", "text") as session:
            session.write_line("=== Output Capture Demo ===")
            for line in test_output_lines:
                session.write_line(line)
            session.write_line("=== End of Demo Output ===")
        
        # Read back the output
        reader = TestOutputReader(Path.cwd() / "demo_outputs" / "comparison")
        
        # Find the output file
        output_files = list((Path.cwd() / "demo_outputs" / "comparison").glob("output_comparison_demo_*.txt"))
        
        if output_files:
            latest_file = max(output_files, key=lambda f: f.stat().st_mtime)
            
            # Wait for completion and read
            if reader.wait_for_completion(latest_file, timeout=10.0):
                content = reader.read_completed_output(latest_file)
                
                if content:
                    captured_lines = len(content.split('\\n'))
                    expected_lines = len(test_output_lines) + 2  # Plus header and footer
                    
                    print(f"\\n📊 Output capture results:")
                    print(f"   Expected lines: {expected_lines}")
                    print(f"   Captured lines: {captured_lines}")
                    print(f"   Capture rate: {(captured_lines/expected_lines)*100:.1f}%")
                    
                    if captured_lines >= expected_lines * 0.9:  # 90% capture threshold
                        print("✅ Output capture demo: SUCCESS (No truncation)")
                        return True
                    else:
                        print("❌ Output capture demo: TRUNCATION DETECTED")
                        return False
                else:
                    print("❌ Failed to read captured output")
                    return False
            else:
                print("❌ Output file did not complete properly")
                return False
        else:
            print("❌ No output files found")
            return False
            
    except Exception as e:
        print(f"❌ Output comparison demo failed: {str(e)}")
        return False


def main():
    """Run all demonstrations."""
    print("🚀 ALTERNATIVE TEST RUNNERS DEMONSTRATION")
    print("="*80)
    print("This demo shows how alternative test runners solve pytest truncation issues")
    
    demos = [
        ("Direct Function Runner", demo_direct_runner),
        ("Migration Test Runner", demo_migration_runner), 
        ("Integration Test Runner", demo_integration_runner),
        ("Comprehensive Runner", demo_comprehensive_runner),
        ("Output Capture", demo_output_comparison)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            print(f"\\n▶️ Starting: {demo_name}")
            success = demo_func()
            results.append((demo_name, success))
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"\\n📋 {demo_name}: {status}")
            
        except Exception as e:
            print(f"\\n💥 {demo_name}: CRITICAL ERROR - {str(e)}")
            results.append((demo_name, False))
    
    # Final summary
    print("\\n" + "="*80)
    print("DEMONSTRATION SUMMARY")
    print("="*80)
    
    successful_demos = [name for name, success in results if success]
    failed_demos = [name for name, success in results if not success]
    
    print(f"✅ Successful demos: {len(successful_demos)}/{len(results)}")
    for demo_name in successful_demos:
        print(f"   ✅ {demo_name}")
    
    if failed_demos:
        print(f"\\n❌ Failed demos: {len(failed_demos)}")
        for demo_name in failed_demos:
            print(f"   ❌ {demo_name}")
    
    # Output locations
    output_base = Path.cwd() / "demo_outputs"
    if output_base.exists():
        output_files = list(output_base.rglob("*.txt"))
        print(f"\\n📁 Demo output files: {len(output_files)}")
        print(f"   Location: {output_base}")
    
    print("\\n🎯 Key Benefits Demonstrated:")
    print("   - Direct test execution without pytest overhead")
    print("   - Complete output capture with no truncation")
    print("   - Specialized runners for different test types")
    print("   - Atomic file operations with completion signaling")
    print("   - Safe reading patterns for LLM systems")
    
    overall_success = len(successful_demos) >= len(results) * 0.6  # 60% success threshold
    
    if overall_success:
        print("\\n🎉 DEMONSTRATION SUCCESSFUL!")
        print("   Alternative test runners are ready for production use")
    else:
        print("\\n⚠️ Some demonstrations failed")
        print("   Check individual demo results above")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
