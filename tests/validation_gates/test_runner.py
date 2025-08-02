#!/usr/bin/env python3
"""
Automated Test Runner for MCP Task Orchestrator Tools

This module provides automated test execution with continuous validation,
immediate issue resolution workflows, and comprehensive reporting.

Usage:
    python test_runner.py --tool orchestrator_get_status --level basic
    python test_runner.py --run-all --stop-on-failure
    python test_runner.py --continuous --interval 300
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import argparse

# Import our validation framework
from validation_framework import ValidationFramework, TestLevel, TestStatus, TestResult
from tool_test_cases import TestCaseRegistry

logger = logging.getLogger(__name__)


class TestRunner:
    """Automated test runner with systematic validation and issue resolution."""
    
    def __init__(self, 
                 output_dir: Path = None,
                 stop_on_failure: bool = False,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        self.output_dir = output_dir or Path("tests/validation_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stop_on_failure = stop_on_failure
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize framework and registry
        self.framework = ValidationFramework(self.output_dir)
        self.registry = TestCaseRegistry()
        
        # Runtime state
        self.running = False
        self.failed_tools: Set[str] = set()
        self.retry_counts: Dict[str, int] = {}
        self.last_run_time = None
        
        # Statistics
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def run_single_tool(self, tool_name: str, level: TestLevel) -> Dict[str, Any]:
        """Run tests for a single tool with retry logic."""
        logger.info(f"Starting test run for {tool_name} at {level.value} level")
        
        attempt = 0
        max_attempts = self.max_retries + 1
        
        while attempt < max_attempts:
            try:
                # Run the validation gate
                results = await self.framework.run_validation_gate(tool_name, level)
                
                # Check if any tests failed
                failed_tests = [r for r in results if r.status == TestStatus.FAIL]
                
                if failed_tests and attempt < max_attempts - 1:
                    logger.warning(f"Tool {tool_name} failed {len(failed_tests)} tests on attempt {attempt + 1}")
                    
                    # Apply issue resolution workflows
                    resolution_applied = await self._apply_issue_resolution(tool_name, failed_tests)
                    
                    if resolution_applied:
                        logger.info(f"Applied issue resolution for {tool_name}, retrying...")
                        attempt += 1
                        await asyncio.sleep(self.retry_delay)
                        continue
                
                # Success or max attempts reached
                run_summary = {
                    "tool": tool_name,
                    "level": level.value,
                    "attempt": attempt + 1,
                    "status": "success" if not failed_tests else "failed",
                    "total_tests": len(results),
                    "passed": len([r for r in results if r.status == TestStatus.PASS]),
                    "failed": len(failed_tests),
                    "results": results,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                if failed_tests:
                    self.failed_tools.add(tool_name)
                    run_summary["failures"] = [
                        {
                            "test": r.name,
                            "error": r.error,
                            "duration": r.duration
                        }
                        for r in failed_tests
                    ]
                else:
                    self.failed_tools.discard(tool_name)
                
                return run_summary
                
            except Exception as e:
                logger.error(f"Error running {tool_name} on attempt {attempt + 1}: {e}")
                
                if attempt < max_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                    attempt += 1
                else:
                    return {
                        "tool": tool_name,
                        "level": level.value,
                        "attempt": attempt + 1,
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        
        return {
            "tool": tool_name,
            "level": level.value,
            "status": "max_attempts_exceeded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def _apply_issue_resolution(self, tool_name: str, failed_tests: List[TestResult]) -> bool:
        """Apply automated issue resolution workflows."""
        logger.info(f"Applying issue resolution for {tool_name}")
        
        resolution_applied = False
        
        for test in failed_tests:
            if not test.error:
                continue
            
            # Database connection issues
            if "database" in test.error.lower() or "connection" in test.error.lower():
                logger.info(f"Attempting database connection fix for {test.name}")
                await self._fix_database_connection()
                resolution_applied = True
            
            # Permission issues
            elif "permission" in test.error.lower():
                logger.info(f"Attempting permission fix for {test.name}")
                await self._fix_permission_issues()
                resolution_applied = True
            
            # Timeout issues
            elif "timeout" in test.error.lower():
                logger.info(f"Adjusting timeout settings for {test.name}")
                await self._adjust_timeout_settings()
                resolution_applied = True
            
            # Server not running
            elif "server" in test.error.lower() and "not" in test.error.lower():
                logger.info(f"Attempting server restart for {test.name}")
                await self._restart_server()
                resolution_applied = True
            
            # Generic retry for other issues
            else:
                logger.info(f"Applying generic retry resolution for {test.name}")
                await asyncio.sleep(0.5)  # Brief pause
                resolution_applied = True
        
        return resolution_applied
    
    async def _fix_database_connection(self):
        """Fix database connection issues."""
        # Mock implementation - replace with actual database fixes
        logger.info("Reinitializing database connection")
        await asyncio.sleep(0.1)
    
    async def _fix_permission_issues(self):
        """Fix permission-related issues."""
        # Mock implementation - replace with actual permission fixes
        logger.info("Adjusting file permissions")
        await asyncio.sleep(0.1)
    
    async def _adjust_timeout_settings(self):
        """Adjust timeout settings for better reliability."""
        # Mock implementation - replace with actual timeout adjustments
        logger.info("Adjusting timeout settings")
        await asyncio.sleep(0.1)
    
    async def _restart_server(self):
        """Restart the MCP server."""
        # Mock implementation - replace with actual server restart
        logger.info("Restarting MCP server")
        await asyncio.sleep(0.1)
    
    async def run_all_tools(self, level: TestLevel) -> Dict[str, Any]:
        """Run tests for all tools systematically."""
        logger.info(f"Starting systematic test run for all tools at {level.value} level")
        
        tools = list(self.framework.tools.keys())
        results = {}
        
        for tool_name in tools:
            if not self.running:
                logger.info("Stopping test run due to shutdown signal")
                break
            
            # Run tests for this tool
            tool_result = await self.run_single_tool(tool_name, level)
            results[tool_name] = tool_result
            
            # Update statistics
            self.total_runs += 1
            if tool_result["status"] == "success":
                self.successful_runs += 1
            else:
                self.failed_runs += 1
            
            # Stop on failure if requested
            if self.stop_on_failure and tool_result["status"] != "success":
                logger.error(f"Stopping test run due to failure in {tool_name}")
                break
            
            # Brief pause between tools
            await asyncio.sleep(0.1)
        
        # Generate comprehensive report
        report = self.framework.generate_report()
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.value,
            "completed_tools": len(results),
            "total_tools": len(tools),
            "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0,
            "failed_tools": list(self.failed_tools),
            "tool_results": results,
            "comprehensive_report": report
        }
    
    async def run_continuous(self, interval: int = 300, level: TestLevel = TestLevel.ALL):
        """Run tests continuously at specified intervals."""
        logger.info(f"Starting continuous test runner with {interval}s interval")
        
        self.running = True
        
        while self.running:
            try:
                logger.info("Starting continuous test cycle")
                
                # Run all tools
                cycle_results = await self.run_all_tools(level)
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.output_dir / f"continuous_results_{timestamp}.json"
                
                with open(results_file, 'w') as f:
                    json.dump(cycle_results, f, indent=2)
                
                logger.info(f"Continuous cycle completed. Results saved to {results_file}")
                
                # Update last run time
                self.last_run_time = datetime.now(timezone.utc)
                
                # Wait for next cycle
                if self.running:
                    logger.info(f"Waiting {interval}s for next cycle...")
                    await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in continuous test cycle: {e}")
                if self.running:
                    await asyncio.sleep(10)  # Brief pause before retry
        
        logger.info("Continuous test runner stopped")
    
    async def run_priority_based(self, level: TestLevel) -> Dict[str, Any]:
        """Run tests based on tool priority (HIGH -> MEDIUM -> LOW)."""
        logger.info(f"Starting priority-based test run at {level.value} level")
        
        # Group tools by priority
        priority_groups = {
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        for tool_name, tool_spec in self.framework.tools.items():
            priority_groups[tool_spec.priority.value.upper()].append(tool_name)
        
        results = {}
        
        # Run tests in priority order
        for priority in ["HIGH", "MEDIUM", "LOW"]:
            if not self.running:
                break
            
            logger.info(f"Running {priority} priority tools")
            
            for tool_name in priority_groups[priority]:
                if not self.running:
                    break
                
                tool_result = await self.run_single_tool(tool_name, level)
                results[tool_name] = tool_result
                
                # Update statistics
                self.total_runs += 1
                if tool_result["status"] == "success":
                    self.successful_runs += 1
                else:
                    self.failed_runs += 1
                
                # Stop on failure if requested
                if self.stop_on_failure and tool_result["status"] != "success":
                    logger.error(f"Stopping priority run due to failure in {tool_name}")
                    return results
        
        return results
    
    async def validate_single_tool_comprehensive(self, tool_name: str) -> Dict[str, Any]:
        """Run comprehensive validation for a single tool (all levels)."""
        logger.info(f"Starting comprehensive validation for {tool_name}")
        
        levels = [TestLevel.BASIC, TestLevel.EDGE_CASES, TestLevel.INTEGRATION]
        level_results = {}
        
        for level in levels:
            if not self.running:
                break
            
            logger.info(f"Running {level.value} tests for {tool_name}")
            level_result = await self.run_single_tool(tool_name, level)
            level_results[level.value] = level_result
            
            # Stop if level failed and immediate issue resolution didn't work
            if level_result["status"] != "success":
                logger.warning(f"{tool_name} failed at {level.value} level")
                
                if self.stop_on_failure:
                    break
        
        return {
            "tool": tool_name,
            "comprehensive_validation": True,
            "levels_tested": list(level_results.keys()),
            "level_results": level_results,
            "overall_status": "success" if all(r["status"] == "success" for r in level_results.values()) else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """Generate real-time progress report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "last_run": self.last_run_time.isoformat() if self.last_run_time else None,
            "statistics": {
                "total_runs": self.total_runs,
                "successful_runs": self.successful_runs,
                "failed_runs": self.failed_runs,
                "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0
            },
            "failed_tools": list(self.failed_tools),
            "retry_counts": self.retry_counts,
            "running": self.running
        }
    
    def save_progress_report(self, filename: str = None) -> Path:
        """Save progress report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"progress_report_{timestamp}.json"
        
        report_path = self.output_dir / filename
        report = self.generate_progress_report()
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Progress report saved to: {report_path}")
        return report_path


async def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Automated Test Runner for MCP Task Orchestrator")
    
    # Test execution options
    parser.add_argument("--tool", type=str, help="Specific tool to test")
    parser.add_argument("--level", type=str, choices=["basic", "edge_cases", "integration", "all"], 
                       default="basic", help="Test level to run")
    parser.add_argument("--run-all", action="store_true", help="Run all tools")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive validation for tool")
    parser.add_argument("--priority-based", action="store_true", help="Run tests based on priority")
    
    # Continuous testing options
    parser.add_argument("--continuous", action="store_true", help="Run continuous testing")
    parser.add_argument("--interval", type=int, default=300, help="Continuous testing interval in seconds")
    
    # Test runner options
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop on first failure")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retry attempts")
    parser.add_argument("--retry-delay", type=float, default=1.0, help="Delay between retries")
    parser.add_argument("--output", type=str, help="Output directory for results")
    
    # Reporting options
    parser.add_argument("--progress-report", action="store_true", help="Generate progress report only")
    
    args = parser.parse_args()
    
    # Initialize test runner
    output_dir = Path(args.output) if args.output else None
    runner = TestRunner(
        output_dir=output_dir,
        stop_on_failure=args.stop_on_failure,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay
    )
    
    # Progress report only
    if args.progress_report:
        report_path = runner.save_progress_report()
        print(f"Progress report saved to: {report_path}")
        return
    
    # Test execution
    try:
        if args.continuous:
            # Continuous testing
            await runner.run_continuous(args.interval, TestLevel(args.level))
            
        elif args.comprehensive and args.tool:
            # Comprehensive validation for single tool
            result = await runner.validate_single_tool_comprehensive(args.tool)
            print(f"Comprehensive validation for {args.tool}:")
            print(f"Overall status: {result['overall_status']}")
            print(f"Levels tested: {result['levels_tested']}")
            
        elif args.priority_based:
            # Priority-based testing
            results = await runner.run_priority_based(TestLevel(args.level))
            print(f"Priority-based testing completed:")
            print(f"Tools tested: {len(results)}")
            print(f"Success rate: {runner.successful_runs / runner.total_runs * 100:.1f}%")
            
        elif args.run_all:
            # Run all tools
            results = await runner.run_all_tools(TestLevel(args.level))
            print(f"All tools testing completed:")
            print(f"Success rate: {results['success_rate']:.1f}%")
            print(f"Failed tools: {results['failed_tools']}")
            
        elif args.tool:
            # Single tool testing
            result = await runner.run_single_tool(args.tool, TestLevel(args.level))
            print(f"Tool {args.tool} testing completed:")
            print(f"Status: {result['status']}")
            print(f"Tests: {result.get('passed', 0)}/{result.get('total_tests', 0)} passed")
            
        else:
            print("Error: Must specify a testing mode")
            print("Use --help for available options")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Test runner interrupted by user")
        runner.running = False
    
    except Exception as e:
        logger.error(f"Test runner error: {e}")
        sys.exit(1)
    
    finally:
        # Save final progress report
        runner.save_progress_report("final_progress_report.json")
        
        # Update tracking file
        runner.framework.update_tracking_file()
        
        print(f"\nFinal Statistics:")
        print(f"Total runs: {runner.total_runs}")
        print(f"Successful runs: {runner.successful_runs}")
        print(f"Failed runs: {runner.failed_runs}")
        print(f"Success rate: {runner.successful_runs / runner.total_runs * 100:.1f}%" if runner.total_runs > 0 else "No runs completed")


if __name__ == "__main__":
    asyncio.run(main())