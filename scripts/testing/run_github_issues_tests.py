#!/usr/bin/env python3
"""
GitHub Issues #46-50 Test Runner and Reporter

This script runs comprehensive tests for all 5 GitHub issue fixes and
generates detailed reports on test results and validation status.

Usage:
    python run_github_issues_tests.py [--worktree] [--compatibility-layer] [--missing-methods] [--all]
    
Options:
    --worktree WORKTREE     Test specific worktree (compatibility-layer or missing-methods)
    --compatibility-layer  Test compatibility layer fixes (#46, #47, #50)
    --missing-methods       Test missing methods fixes (#48, #49)
    --all                   Test both worktrees (default)
    --verbose               Verbose output
    --json-report          Generate JSON test report
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class GitHubIssuesTestRunner:
    """Test runner for GitHub Issues #46-50 fixes."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = {}
        self.start_time = datetime.now()
        
        # Define test categories by issue
        self.test_categories = {
            "issue_46": {
                "name": "MockTask JSON Serialization",
                "worktree": "compatibility-layer",
                "test_classes": [
                    "TestGitHubIssue46MockTaskSerialization"
                ]
            },
            "issue_47": {
                "name": "update_task Response Formatting", 
                "worktree": "compatibility-layer",
                "test_classes": [
                    "TestGitHubIssue47UpdateTaskResponseFormatting"
                ]
            },
            "issue_48": {
                "name": "delete_task Implementation",
                "worktree": "missing-methods", 
                "test_classes": [
                    "TestGitHubIssue48DeleteTaskImplementation"
                ]
            },
            "issue_49": {
                "name": "cancel_task Implementation",
                "worktree": "missing-methods",
                "test_classes": [
                    "TestGitHubIssue49CancelTaskImplementation"
                ]
            },
            "issue_50": {
                "name": "query_tasks Format Mismatch",
                "worktree": "compatibility-layer",
                "test_classes": [
                    "TestGitHubIssue50QueryTasksFormatMismatch"
                ]
            }
        }
        
        # Integration and regression tests
        self.integration_tests = {
            "mcp_integration": {
                "name": "MCP Handler Integration",
                "test_classes": [
                    "TestIntegrationThroughMCPHandlers"
                ]
            },
            "error_handling": {
                "name": "Error Handling and Edge Cases",
                "test_classes": [
                    "TestErrorHandlingAndEdgeCases"
                ]
            },
            "regression": {
                "name": "Regression Validation",
                "test_classes": [
                    "TestRegressionValidation"
                ]
            }
        }
    
    def print_banner(self):
        """Print test runner banner."""
        print("=" * 80)
        print("GitHub Issues #46-50 Comprehensive Test Suite")
        print("=" * 80)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def run_pytest_command(self, test_path: str, test_filter: str = None) -> Tuple[int, str, str]:
        """Run pytest command and capture output."""
        cmd = [
            sys.executable, "-m", "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--no-header",
            "--json-report",
            "--json-report-file=/tmp/pytest_report.json"
        ]
        
        if test_filter:
            cmd.extend(["-k", test_filter])
        
        if self.verbose:
            print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Test timed out after 5 minutes"
        except Exception as e:
            return -1, "", f"Error running tests: {str(e)}"
    
    def test_issue_fixes(self, worktree_filter: str = None) -> Dict[str, Any]:
        """Test all issue fixes."""
        results = {}
        
        print("Testing Individual Issue Fixes")
        print("-" * 50)
        
        for issue_id, issue_info in self.test_categories.items():
            if worktree_filter and issue_info["worktree"] != worktree_filter:
                continue
                
            print(f"\nTesting {issue_id.upper()}: {issue_info['name']}")
            print(f"Worktree: {issue_info['worktree']}")
            
            # Determine test path based on worktree
            worktree_path = f"/home/aya/dev/mcp-servers/worktrees/{issue_info['worktree']}"
            test_path = f"{worktree_path}/tests/integration/test_github_issues_46_50_comprehensive.py"
            
            # Run tests for this issue
            test_filter = " or ".join(issue_info["test_classes"])
            returncode, stdout, stderr = self.run_pytest_command(test_path, test_filter)
            
            results[issue_id] = {
                "name": issue_info["name"],
                "worktree": issue_info["worktree"],
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "passed": returncode == 0
            }
            
            if returncode == 0:
                print(f"  ✅ {issue_id.upper()} tests PASSED")
            else:
                print(f"  ❌ {issue_id.upper()} tests FAILED (exit code: {returncode})")
                if self.verbose and stderr:
                    print(f"  Error: {stderr}")
        
        return results
    
    def test_integration_and_regression(self, worktree_filter: str = None) -> Dict[str, Any]:
        """Test integration and regression scenarios."""
        results = {}
        
        print("\n\nTesting Integration and Regression")
        print("-" * 50)
        
        for test_id, test_info in self.integration_tests.items():
            print(f"\nTesting {test_info['name']}")
            
            # For integration tests, we test both worktrees unless filtered
            worktrees_to_test = []
            if worktree_filter:
                worktrees_to_test = [worktree_filter]
            else:
                worktrees_to_test = ["compatibility-layer", "missing-methods"]
            
            test_results = []
            
            for worktree in worktrees_to_test:
                worktree_path = f"/home/aya/dev/mcp-servers/worktrees/{worktree}"
                test_path = f"{worktree_path}/tests/integration/test_github_issues_46_50_comprehensive.py"
                
                test_filter = " or ".join(test_info["test_classes"])
                returncode, stdout, stderr = self.run_pytest_command(test_path, test_filter)
                
                test_results.append({
                    "worktree": worktree,
                    "returncode": returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "passed": returncode == 0
                })
                
                if returncode == 0:
                    print(f"  ✅ {worktree} tests PASSED")
                else:
                    print(f"  ❌ {worktree} tests FAILED (exit code: {returncode})")
            
            results[test_id] = {
                "name": test_info["name"],
                "results": test_results,
                "overall_passed": all(r["passed"] for r in test_results)
            }
        
        return results
    
    def validate_json_serialization(self) -> Dict[str, Any]:
        """Validate JSON serialization across all components."""
        print("\n\nValidating JSON Serialization")
        print("-" * 50)
        
        # This would ideally test actual serialization scenarios
        # For now, we'll run specific serialization tests
        
        validation_results = {
            "compatibility_layer": {"passed": False, "details": []},
            "missing_methods": {"passed": False, "details": []}
        }
        
        for worktree in ["compatibility-layer", "missing-methods"]:
            print(f"\nValidating {worktree} serialization...")
            
            worktree_path = f"/home/aya/dev/mcp-servers/worktrees/{worktree}"
            test_path = f"{worktree_path}/tests/integration/test_github_issues_46_50_comprehensive.py"
            
            # Run serialization-specific tests
            test_filter = "serialization or json"
            returncode, stdout, stderr = self.run_pytest_command(test_path, test_filter)
            
            validation_results[worktree]["passed"] = returncode == 0
            validation_results[worktree]["details"] = {
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr
            }
            
            if returncode == 0:
                print(f"  ✅ {worktree} serialization validation PASSED")
            else:
                print(f"  ❌ {worktree} serialization validation FAILED")
        
        return validation_results
    
    def generate_comprehensive_report(self, issue_results: Dict, integration_results: Dict, 
                                    serialization_results: Dict) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        # Count overall results
        total_issues = len(issue_results)
        passed_issues = sum(1 for r in issue_results.values() if r["passed"])
        
        total_integration = len(integration_results)
        passed_integration = sum(1 for r in integration_results.values() if r["overall_passed"])
        
        serialization_passed = all(r["passed"] for r in serialization_results.values())
        
        overall_success = (
            passed_issues == total_issues and 
            passed_integration == total_integration and
            serialization_passed
        )
        
        report = {
            "metadata": {
                "test_run_id": f"github_issues_46_50_{int(self.start_time.timestamp())}",
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "overall_success": overall_success
            },
            "summary": {
                "issue_fixes": {
                    "total": total_issues,
                    "passed": passed_issues,
                    "failed": total_issues - passed_issues,
                    "success_rate": passed_issues / total_issues if total_issues > 0 else 0
                },
                "integration_tests": {
                    "total": total_integration,
                    "passed": passed_integration,
                    "failed": total_integration - passed_integration,
                    "success_rate": passed_integration / total_integration if total_integration > 0 else 0
                },
                "serialization_validation": {
                    "passed": serialization_passed,
                    "details": serialization_results
                }
            },
            "detailed_results": {
                "issue_fixes": issue_results,
                "integration_tests": integration_results,
                "serialization_validation": serialization_results
            },
            "recommendations": self.generate_recommendations(issue_results, integration_results, serialization_results)
        }
        
        return report
    
    def generate_recommendations(self, issue_results: Dict, integration_results: Dict, 
                               serialization_results: Dict) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check issue fix results
        failed_issues = [issue_id for issue_id, result in issue_results.items() if not result["passed"]]
        if failed_issues:
            recommendations.append(f"Fix failing issue tests: {', '.join(failed_issues)}")
        
        # Check integration results
        failed_integration = [test_id for test_id, result in integration_results.items() if not result["overall_passed"]]
        if failed_integration:
            recommendations.append(f"Fix failing integration tests: {', '.join(failed_integration)}")
        
        # Check serialization
        failed_serialization = [worktree for worktree, result in serialization_results.items() if not result["passed"]]
        if failed_serialization:
            recommendations.append(f"Fix serialization issues in: {', '.join(failed_serialization)}")
        
        # Success recommendations
        if not recommendations:
            recommendations.extend([
                "All tests passed! Ready for PR creation.",
                "Consider running integration tests with actual MCP server.",
                "Validate changes with real orchestrator session.",
                "Update documentation to reflect all fixes."
            ])
        
        return recommendations
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Print human-readable summary report."""
        print("\n\n" + "=" * 80)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        metadata = report["metadata"]
        summary = report["summary"]
        
        print(f"Test Run ID: {metadata['test_run_id']}")
        print(f"Duration: {metadata['duration_seconds']:.2f} seconds")
        print(f"Overall Success: {'✅ PASSED' if metadata['overall_success'] else '❌ FAILED'}")
        print()
        
        # Issue fixes summary
        issue_summary = summary["issue_fixes"]
        print(f"Issue Fixes: {issue_summary['passed']}/{issue_summary['total']} passed " +
              f"({issue_summary['success_rate']:.0%} success rate)")
        
        # Integration tests summary
        integration_summary = summary["integration_tests"]
        print(f"Integration Tests: {integration_summary['passed']}/{integration_summary['total']} passed " +
              f"({integration_summary['success_rate']:.0%} success rate)")
        
        # Serialization summary
        serialization_summary = summary["serialization_validation"]
        print(f"Serialization Validation: {'✅ PASSED' if serialization_summary['passed'] else '❌ FAILED'}")
        
        # Recommendations
        print("\nRecommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "=" * 80)
    
    def save_json_report(self, report: Dict[str, Any], filename: str = None):
        """Save detailed JSON report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"github_issues_46_50_test_report_{timestamp}.json"
        
        report_path = Path(__file__).parent / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\nDetailed JSON report saved to: {report_path}")
        return report_path


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="GitHub Issues #46-50 Test Runner")
    parser.add_argument("--worktree", choices=["compatibility-layer", "missing-methods"],
                       help="Test specific worktree only")
    parser.add_argument("--compatibility-layer", action="store_true",
                       help="Test compatibility layer fixes (#46, #47, #50)")
    parser.add_argument("--missing-methods", action="store_true", 
                       help="Test missing methods fixes (#48, #49)")
    parser.add_argument("--all", action="store_true", default=True,
                       help="Test both worktrees (default)")
    parser.add_argument("--verbose", action="store_true",
                       help="Verbose output")
    parser.add_argument("--json-report", action="store_true",
                       help="Generate JSON test report")
    
    args = parser.parse_args()
    
    # Determine worktree filter
    worktree_filter = None
    if args.worktree:
        worktree_filter = args.worktree
    elif args.compatibility_layer:
        worktree_filter = "compatibility-layer"
    elif args.missing_methods:
        worktree_filter = "missing-methods"
    
    # Create test runner
    runner = GitHubIssuesTestRunner(verbose=args.verbose)
    runner.print_banner()
    
    try:
        # Run all test categories
        issue_results = runner.test_issue_fixes(worktree_filter)
        integration_results = runner.test_integration_and_regression(worktree_filter)
        serialization_results = runner.validate_json_serialization()
        
        # Generate comprehensive report
        report = runner.generate_comprehensive_report(
            issue_results, integration_results, serialization_results
        )
        
        # Print summary
        runner.print_summary_report(report)
        
        # Save JSON report if requested
        if args.json_report:
            runner.save_json_report(report)
        
        # Exit with appropriate code
        exit_code = 0 if report["metadata"]["overall_success"] else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nUnexpected error during test run: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()