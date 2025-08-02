#!/usr/bin/env python3
"""
Example Usage of MCP Task Orchestrator Validation Framework

This script demonstrates how to use the validation framework to test
MCP Task Orchestrator tools systematically.

Usage:
    python run_example.py
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Import validation framework components
from validation_framework import ValidationFramework, TestLevel
from test_runner import TestRunner
from issue_resolution_workflows import IssueResolutionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_single_tool_validation():
    """Example: Test a single tool with comprehensive validation."""
    print("=" * 60)
    print("EXAMPLE 1: Single Tool Comprehensive Validation")
    print("=" * 60)
    
    # Initialize framework
    framework = ValidationFramework()
    
    # Test orchestrator_get_status tool at all levels
    tool_name = "orchestrator_get_status"
    
    print(f"Testing {tool_name} at all validation levels...")
    
    # Test basic functionality
    print("\n1. Basic Functionality Tests:")
    basic_results = await framework.run_validation_gate(tool_name, TestLevel.BASIC)
    for result in basic_results:
        status_icon = "✅" if result.status.value == "pass" else "❌"
        print(f"   {status_icon} {result.name}: {result.status.value}")
        if result.error:
            print(f"      Error: {result.error}")
    
    # Test edge cases
    print("\n2. Edge Case Tests:")
    edge_results = await framework.run_validation_gate(tool_name, TestLevel.EDGE_CASES)
    for result in edge_results:
        status_icon = "✅" if result.status.value == "pass" else "❌"
        print(f"   {status_icon} {result.name}: {result.status.value}")
        if result.error:
            print(f"      Error: {result.error}")
    
    # Test integration
    print("\n3. Integration Tests:")
    integration_results = await framework.run_validation_gate(tool_name, TestLevel.INTEGRATION)
    for result in integration_results:
        status_icon = "✅" if result.status.value == "pass" else "❌"
        print(f"   {status_icon} {result.name}: {result.status.value}")
        if result.error:
            print(f"      Error: {result.error}")
    
    # Generate report
    report = framework.generate_report()
    print(f"\n📊 Summary:")
    print(f"   Total tests: {report['summary']['total_tests']}")
    print(f"   Passed: {report['summary']['passed_tests']}")
    print(f"   Failed: {report['summary']['failed_tests']}")
    print(f"   Pass rate: {report['summary']['pass_rate']:.1f}%")


async def example_automated_test_runner():
    """Example: Use automated test runner with retry logic."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Automated Test Runner with Retry Logic")
    print("=" * 60)
    
    # Initialize test runner
    runner = TestRunner(
        stop_on_failure=False,
        max_retries=2,
        retry_delay=0.5
    )
    
    # Test a tool with retry logic
    tool_name = "orchestrator_plan_task"
    
    print(f"Testing {tool_name} with automated retry logic...")
    
    result = await runner.run_single_tool(tool_name, TestLevel.BASIC)
    
    print(f"\n📋 Test Results:")
    print(f"   Tool: {result['tool']}")
    print(f"   Status: {result['status']}")
    print(f"   Attempt: {result['attempt']}")
    print(f"   Total tests: {result.get('total_tests', 0)}")
    print(f"   Passed: {result.get('passed', 0)}")
    print(f"   Failed: {result.get('failed', 0)}")
    
    if result.get('failures'):
        print(f"\n❌ Failures:")
        for failure in result['failures']:
            print(f"   - {failure['test']}: {failure['error']}")


async def example_issue_resolution():
    """Example: Demonstrate issue resolution workflows."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Issue Resolution Workflows")
    print("=" * 60)
    
    # Initialize issue resolution manager
    manager = IssueResolutionManager()
    
    # Test error messages and resolution
    test_errors = [
        "Database connection failed: could not connect to database",
        "Server not running: connection refused",
        "Permission denied: access denied to file /tmp/test.db",
        "Server timeout: request timed out after 30 seconds"
    ]
    
    print("Testing automated issue resolution...")
    
    for i, error in enumerate(test_errors, 1):
        print(f"\n{i}. Error: {error}")
        
        # Identify issue type
        issue_type = manager.identify_issue(error)
        print(f"   🔍 Identified issue: {issue_type}")
        
        if issue_type:
            # Attempt resolution
            result = await manager.auto_resolve_from_error(error)
            
            status_icon = "✅" if result.success else "❌"
            print(f"   {status_icon} Resolution: {result.success}")
            
            if result.steps_taken:
                print(f"   📝 Steps taken:")
                for step in result.steps_taken:
                    print(f"      - {step}")
            
            if result.recommendations:
                print(f"   💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"      - {rec}")
        else:
            print(f"   ❓ No automatic resolution available")


async def example_priority_based_testing():
    """Example: Run tests based on tool priority."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 4: Priority-Based Testing")
    print("=" * 60)
    
    # Initialize test runner
    runner = TestRunner()
    
    print("Running tests based on tool priority (HIGH → MEDIUM → LOW)...")
    
    # Run priority-based tests
    results = await runner.run_priority_based(TestLevel.BASIC)
    
    print(f"\n📊 Priority-Based Test Results:")
    print(f"   Tools tested: {len(results)}")
    print(f"   Success rate: {runner.successful_runs / runner.total_runs * 100:.1f}%")
    
    # Show results by priority
    framework = ValidationFramework()
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for tool_name, tool_spec in framework.tools.items():
        if tool_name in results:
            if tool_spec.priority.value == "high":
                high_priority.append((tool_name, results[tool_name]))
            elif tool_spec.priority.value == "medium":
                medium_priority.append((tool_name, results[tool_name]))
            else:
                low_priority.append((tool_name, results[tool_name]))
    
    for priority, tools in [("HIGH", high_priority), ("MEDIUM", medium_priority), ("LOW", low_priority)]:
        if tools:
            print(f"\n   {priority} Priority Tools:")
            for tool_name, result in tools:
                status_icon = "✅" if result["status"] == "success" else "❌"
                print(f"      {status_icon} {tool_name}: {result['status']}")


async def example_comprehensive_validation():
    """Example: Comprehensive validation of a single tool."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 5: Comprehensive Tool Validation")
    print("=" * 60)
    
    # Initialize test runner
    runner = TestRunner()
    
    # Run comprehensive validation
    tool_name = "orchestrator_initialize_session"
    
    print(f"Running comprehensive validation for {tool_name}...")
    
    result = await runner.validate_single_tool_comprehensive(tool_name)
    
    print(f"\n📋 Comprehensive Validation Results:")
    print(f"   Tool: {result['tool']}")
    print(f"   Overall status: {result['overall_status']}")
    print(f"   Levels tested: {result['levels_tested']}")
    
    for level, level_result in result['level_results'].items():
        status_icon = "✅" if level_result["status"] == "success" else "❌"
        print(f"   {status_icon} {level.upper()}: {level_result['status']} "
              f"({level_result.get('passed', 0)}/{level_result.get('total_tests', 0)} passed)")


async def example_generate_reports():
    """Example: Generate comprehensive reports."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 6: Report Generation")
    print("=" * 60)
    
    # Initialize framework
    framework = ValidationFramework()
    
    # Run a few tests to have data for reporting
    await framework.run_validation_gate("orchestrator_get_status", TestLevel.BASIC)
    await framework.run_validation_gate("orchestrator_plan_task", TestLevel.BASIC)
    
    # Generate comprehensive report
    report = framework.generate_report()
    
    print("📊 Generated comprehensive test report:")
    print(f"   Timestamp: {report['timestamp']}")
    print(f"   Total tools: {report['summary']['total_tools']}")
    print(f"   Completed tools: {report['summary']['completed_tools']}")
    print(f"   Total tests: {report['summary']['total_tests']}")
    print(f"   Pass rate: {report['summary']['pass_rate']:.1f}%")
    
    # Save report
    report_path = framework.save_report(report)
    print(f"   💾 Report saved to: {report_path}")
    
    # Update tracking file
    framework.update_tracking_file()
    print(f"   📋 Tracking file updated")


async def example_full_workflow():
    """Example: Complete validation workflow."""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 7: Complete Validation Workflow")
    print("=" * 60)
    
    # Initialize test runner
    runner = TestRunner()
    
    # Select a few tools for demonstration
    test_tools = [
        "orchestrator_get_status",
        "orchestrator_plan_task",
        "orchestrator_health_check"
    ]
    
    print("Running complete validation workflow...")
    
    all_results = {}
    
    for tool_name in test_tools:
        print(f"\n🔧 Testing {tool_name}...")
        
        # Run comprehensive validation
        result = await runner.validate_single_tool_comprehensive(tool_name)
        all_results[tool_name] = result
        
        # Show immediate results
        status_icon = "✅" if result["overall_status"] == "success" else "❌"
        print(f"   {status_icon} {tool_name}: {result['overall_status']}")
        
        # Brief pause between tools
        await asyncio.sleep(0.1)
    
    # Generate final summary
    print(f"\n📊 Final Workflow Summary:")
    successful_tools = sum(1 for r in all_results.values() if r["overall_status"] == "success")
    total_tools = len(all_results)
    
    print(f"   Tools tested: {total_tools}")
    print(f"   Successful: {successful_tools}")
    print(f"   Failed: {total_tools - successful_tools}")
    print(f"   Success rate: {successful_tools / total_tools * 100:.1f}%")
    
    # Save final progress report
    progress_path = runner.save_progress_report("workflow_example_progress.json")
    print(f"   💾 Progress report saved to: {progress_path}")


async def main():
    """Run all examples."""
    print("🚀 MCP Task Orchestrator Validation Framework Examples")
    print("=" * 60)
    
    # Run examples
    await example_single_tool_validation()
    await example_automated_test_runner()
    await example_issue_resolution()
    await example_priority_based_testing()
    await example_comprehensive_validation()
    await example_generate_reports()
    await example_full_workflow()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed successfully!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Review the generated reports and tracking file")
    print("2. Run validation for additional tools")
    print("3. Set up continuous testing for critical tools")
    print("4. Customize test cases for your specific needs")


if __name__ == "__main__":
    asyncio.run(main())