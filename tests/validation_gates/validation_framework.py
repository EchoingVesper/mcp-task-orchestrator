#!/usr/bin/env python3
"""
MCP Task Orchestrator Validation Framework

A comprehensive validation framework for testing all 16 MCP Task Orchestrator tools
with systematic validation gates, automated testing, and progress tracking.

Usage:
    python validation_framework.py --tool orchestrator_get_status --level basic
    python validation_framework.py --all --level all
    python validation_framework.py --report
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestLevel(Enum):
    """Test validation levels."""
    BASIC = "basic"
    EDGE_CASES = "edge_cases"
    INTEGRATION = "integration"
    ALL = "all"


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASS = "pass"
    FAIL = "fail"
    RETRY = "retry"
    BLOCKED = "blocked"
    WARNING = "warning"


class Priority(Enum):
    """Test priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Complexity(Enum):
    """Tool complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    status: TestStatus
    duration: float
    error: Optional[str] = None
    warning: Optional[str] = None
    output: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


@dataclass
class ValidationGate:
    """Validation gate for a specific test category."""
    name: str
    description: str
    tests: List[str]
    required_setup: List[str]
    success_criteria: List[str]
    
    def __post_init__(self):
        if not self.tests:
            raise ValueError(f"ValidationGate '{self.name}' must have at least one test")


@dataclass
class ToolSpec:
    """Specification for an MCP tool."""
    name: str
    category: str
    priority: Priority
    complexity: Complexity
    description: str
    required_params: List[str]
    optional_params: List[str]
    validation_gates: Dict[TestLevel, ValidationGate]
    
    @property
    def total_tests(self) -> int:
        """Total number of tests for this tool."""
        return sum(len(gate.tests) for gate in self.validation_gates.values())


class ValidationFramework:
    """Main validation framework for MCP Task Orchestrator tools."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("tests/validation_results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Test results storage
        self.results: Dict[str, Dict[TestLevel, List[TestResult]]] = {}
        
        # Tool specifications
        self.tools = self._initialize_tool_specs()
        
        # Statistics
        self.start_time = None
        self.total_tests_run = 0
        self.total_passed = 0
        self.total_failed = 0
        
    def _initialize_tool_specs(self) -> Dict[str, ToolSpec]:
        """Initialize all tool specifications with validation gates."""
        tools = {}
        
        # Core Orchestration Tools
        tools.update(self._get_core_tools())
        
        # Generic Task Management Tools
        tools.update(self._get_task_tools())
        
        # Server Reboot Tools
        tools.update(self._get_reboot_tools())
        
        return tools
    
    def _get_core_tools(self) -> Dict[str, ToolSpec]:
        """Get core orchestration tool specifications."""
        return {
            "orchestrator_initialize_session": ToolSpec(
                name="orchestrator_initialize_session",
                category="core",
                priority=Priority.HIGH,
                complexity=Complexity.MODERATE,
                description="Initialize a new task orchestration session",
                required_params=[],
                optional_params=["working_directory"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core session initialization tests",
                        tests=[
                            "test_default_initialization",
                            "test_custom_directory",
                            "test_session_state_creation",
                            "test_return_format"
                        ],
                        required_setup=["clean_database", "valid_working_directory"],
                        success_criteria=["session_created", "database_initialized", "valid_response"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_invalid_directory",
                            "test_permission_denied",
                            "test_existing_session",
                            "test_concurrent_initialization"
                        ],
                        required_setup=["test_directories", "permission_scenarios"],
                        success_criteria=["proper_error_handling", "graceful_degradation"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_database_integration",
                            "test_workspace_detection",
                            "test_state_manager_integration",
                            "test_multi_client_support"
                        ],
                        required_setup=["database_server", "workspace_files", "multi_client_env"],
                        success_criteria=["full_system_integration", "performance_acceptable"]
                    )
                }
            ),
            
            "orchestrator_get_status": ToolSpec(
                name="orchestrator_get_status",
                category="core",
                priority=Priority.MEDIUM,
                complexity=Complexity.SIMPLE,
                description="Get current status of all active tasks",
                required_params=[],
                optional_params=["include_completed"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core status retrieval tests",
                        tests=[
                            "test_default_status",
                            "test_include_completed",
                            "test_json_format",
                            "test_response_time"
                        ],
                        required_setup=["sample_tasks", "database_connection"],
                        success_criteria=["status_retrieved", "valid_format", "acceptable_performance"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_empty_database",
                            "test_large_dataset",
                            "test_db_connection_failure",
                            "test_concurrent_requests"
                        ],
                        required_setup=["various_db_states", "performance_test_data"],
                        success_criteria=["handles_empty_state", "performance_under_load"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_realtime_updates",
                            "test_performance_metrics",
                            "test_health_correlation",
                            "test_cross_session_visibility"
                        ],
                        required_setup=["realtime_system", "monitoring_system"],
                        success_criteria=["realtime_accuracy", "system_coherence"]
                    )
                }
            ),
            
            "orchestrator_synthesize_results": ToolSpec(
                name="orchestrator_synthesize_results",
                category="core",
                priority=Priority.HIGH,
                complexity=Complexity.COMPLEX,
                description="Combine completed subtasks into final result",
                required_params=["parent_task_id"],
                optional_params=[],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core result synthesis tests",
                        tests=[
                            "test_single_parent_synthesis",
                            "test_multiple_subtasks",
                            "test_artifact_combination",
                            "test_result_format"
                        ],
                        required_setup=["parent_task", "completed_subtasks", "artifacts"],
                        success_criteria=["synthesis_complete", "artifacts_combined", "valid_output"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_missing_parent_id",
                            "test_incomplete_subtasks",
                            "test_circular_dependencies",
                            "test_large_result_sets"
                        ],
                        required_setup=["complex_task_structures", "edge_case_data"],
                        success_criteria=["error_handling", "graceful_failures"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_task_status_updates",
                            "test_artifact_management",
                            "test_dependency_resolution",
                            "test_performance_under_load"
                        ],
                        required_setup=["full_workflow", "artifact_system", "performance_env"],
                        success_criteria=["workflow_integrity", "performance_acceptable"]
                    )
                }
            )
        }
    
    def _get_task_tools(self) -> Dict[str, ToolSpec]:
        """Get task management tool specifications."""
        return {
            "orchestrator_plan_task": ToolSpec(
                name="orchestrator_plan_task",
                category="task_management",
                priority=Priority.HIGH,
                complexity=Complexity.COMPLEX,
                description="Create a new task with rich metadata",
                required_params=["title", "description"],
                optional_params=["task_type", "parent_task_id", "complexity", "specialist_type"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core task creation tests",
                        tests=[
                            "test_minimal_task_creation",
                            "test_full_parameter_creation",
                            "test_task_id_generation",
                            "test_database_persistence"
                        ],
                        required_setup=["database_connection", "clean_state"],
                        success_criteria=["task_created", "id_generated", "persisted"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_missing_required_fields",
                            "test_invalid_enum_values",
                            "test_extremely_long_inputs",
                            "test_special_characters"
                        ],
                        required_setup=["validation_test_data"],
                        success_criteria=["proper_validation", "error_messages"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_parent_child_relationships",
                            "test_dependency_chain_validation",
                            "test_specialist_assignment",
                            "test_workflow_integration"
                        ],
                        required_setup=["task_hierarchy", "specialist_system"],
                        success_criteria=["relationships_valid", "workflow_coherent"]
                    )
                }
            ),
            
            # Add more task tools here...
            "orchestrator_query_tasks": ToolSpec(
                name="orchestrator_query_tasks",
                category="task_management",
                priority=Priority.HIGH,
                complexity=Complexity.COMPLEX,
                description="Query and filter tasks with advanced capabilities",
                required_params=[],
                optional_params=["status", "task_type", "specialist_type", "search_text"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core query functionality tests",
                        tests=[
                            "test_no_filters_query",
                            "test_single_filter_query",
                            "test_multiple_filter_combination",
                            "test_pagination_support"
                        ],
                        required_setup=["sample_tasks", "database_connection"],
                        success_criteria=["query_results", "pagination_works", "valid_format"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_invalid_filter_values",
                            "test_large_result_sets",
                            "test_complex_query_combinations",
                            "test_performance_edge_cases"
                        ],
                        required_setup=["large_dataset", "complex_queries"],
                        success_criteria=["handles_invalid_input", "performance_acceptable"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_realtime_result_updates",
                            "test_cross_session_queries",
                            "test_permission_filtering",
                            "test_performance_optimization"
                        ],
                        required_setup=["multi_session_env", "permission_system"],
                        success_criteria=["realtime_accuracy", "security_compliance"]
                    )
                }
            )
        }
    
    def _get_reboot_tools(self) -> Dict[str, ToolSpec]:
        """Get server reboot tool specifications."""
        return {
            "orchestrator_restart_server": ToolSpec(
                name="orchestrator_restart_server",
                category="reboot",
                priority=Priority.HIGH,
                complexity=Complexity.VERY_COMPLEX,
                description="Trigger graceful server restart with state preservation",
                required_params=[],
                optional_params=["graceful", "preserve_state", "timeout", "reason"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core restart functionality tests",
                        tests=[
                            "test_graceful_restart_request",
                            "test_state_preservation",
                            "test_timeout_handling",
                            "test_reason_logging"
                        ],
                        required_setup=["server_instance", "state_data"],
                        success_criteria=["restart_initiated", "state_preserved", "proper_logging"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_emergency_restart",
                            "test_concurrent_restart_requests",
                            "test_invalid_timeout_values",
                            "test_state_corruption_handling"
                        ],
                        required_setup=["edge_case_scenarios", "corrupted_state"],
                        success_criteria=["handles_emergencies", "prevents_corruption"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_client_reconnection",
                            "test_database_consistency",
                            "test_task_state_preservation",
                            "test_performance_monitoring"
                        ],
                        required_setup=["full_system", "client_connections", "monitoring"],
                        success_criteria=["full_system_recovery", "no_data_loss"]
                    )
                }
            ),
            
            "orchestrator_health_check": ToolSpec(
                name="orchestrator_health_check",
                category="reboot",
                priority=Priority.HIGH,
                complexity=Complexity.MODERATE,
                description="Check server health and operational readiness",
                required_params=[],
                optional_params=["include_reboot_readiness", "include_connection_status"],
                validation_gates={
                    TestLevel.BASIC: ValidationGate(
                        name="Basic Functionality",
                        description="Core health check tests",
                        tests=[
                            "test_basic_health_status",
                            "test_reboot_readiness_check",
                            "test_connection_status",
                            "test_database_status"
                        ],
                        required_setup=["running_server", "database_connection"],
                        success_criteria=["health_reported", "status_accurate", "valid_format"]
                    ),
                    TestLevel.EDGE_CASES: ValidationGate(
                        name="Edge Cases",
                        description="Boundary conditions and error scenarios",
                        tests=[
                            "test_degraded_system_states",
                            "test_partial_service_failures",
                            "test_timeout_scenarios",
                            "test_resource_exhaustion"
                        ],
                        required_setup=["degraded_states", "failure_scenarios"],
                        success_criteria=["detects_issues", "proper_error_reporting"]
                    ),
                    TestLevel.INTEGRATION: ValidationGate(
                        name="Integration",
                        description="Cross-system integration tests",
                        tests=[
                            "test_system_monitoring",
                            "test_performance_correlation",
                            "test_automated_remediation",
                            "test_realtime_updates"
                        ],
                        required_setup=["monitoring_system", "automation_framework"],
                        success_criteria=["monitoring_integrated", "automation_working"]
                    )
                }
            )
        }
    
    async def run_validation_gate(self, tool_name: str, level: TestLevel) -> List[TestResult]:
        """Run a specific validation gate for a tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_spec = self.tools[tool_name]
        if level not in tool_spec.validation_gates:
            raise ValueError(f"Tool {tool_name} has no {level.value} validation gate")
        
        gate = tool_spec.validation_gates[level]
        results = []
        
        logger.info(f"Running {level.value} validation gate for {tool_name}")
        
        # Check setup requirements
        setup_ok = await self._verify_setup_requirements(gate.required_setup)
        if not setup_ok:
            results.append(TestResult(
                name=f"setup_verification",
                status=TestStatus.BLOCKED,
                duration=0.0,
                error="Required setup not available"
            ))
            return results
        
        # Run each test in the gate
        for test_name in gate.tests:
            try:
                result = await self._run_individual_test(tool_name, test_name, level)
                results.append(result)
            except Exception as e:
                logger.error(f"Error running test {test_name}: {e}")
                results.append(TestResult(
                    name=test_name,
                    status=TestStatus.FAIL,
                    duration=0.0,
                    error=str(e)
                ))
        
        # Store results
        if tool_name not in self.results:
            self.results[tool_name] = {}
        self.results[tool_name][level] = results
        
        return results
    
    async def _verify_setup_requirements(self, requirements: List[str]) -> bool:
        """Verify that setup requirements are met."""
        for requirement in requirements:
            if not await self._check_requirement(requirement):
                logger.error(f"Setup requirement not met: {requirement}")
                return False
        return True
    
    async def _check_requirement(self, requirement: str) -> bool:
        """Check if a specific requirement is met."""
        # Implementation depends on the requirement type
        requirement_checks = {
            "database_connection": self._check_database_connection,
            "clean_database": self._check_clean_database,
            "sample_tasks": self._check_sample_tasks,
            "running_server": self._check_running_server,
            "valid_working_directory": self._check_valid_working_directory,
        }
        
        checker = requirement_checks.get(requirement)
        if checker:
            return await checker()
        else:
            logger.warning(f"Unknown requirement: {requirement}")
            return True  # Assume met for unknown requirements
    
    async def _check_database_connection(self) -> bool:
        """Check if database connection is available."""
        # Mock implementation - replace with actual database check
        return True
    
    async def _check_clean_database(self) -> bool:
        """Check if database is in clean state."""
        # Mock implementation - replace with actual database check
        return True
    
    async def _check_sample_tasks(self) -> bool:
        """Check if sample tasks are available."""
        # Mock implementation - replace with actual task check
        return True
    
    async def _check_running_server(self) -> bool:
        """Check if server is running."""
        # Mock implementation - replace with actual server check
        return True
    
    async def _check_valid_working_directory(self) -> bool:
        """Check if working directory is valid."""
        # Mock implementation - replace with actual directory check
        return True
    
    async def _run_individual_test(self, tool_name: str, test_name: str, level: TestLevel) -> TestResult:
        """Run an individual test and return result."""
        start_time = time.time()
        
        logger.info(f"Running test: {test_name} for {tool_name} ({level.value})")
        
        try:
            # Mock test execution - replace with actual test implementations
            await asyncio.sleep(0.1)  # Simulate test execution time
            
            # For demonstration, make some tests fail
            if "invalid" in test_name or "error" in test_name:
                status = TestStatus.FAIL
                error = f"Mock failure for {test_name}"
            elif "warning" in test_name:
                status = TestStatus.WARNING
                error = None
            else:
                status = TestStatus.PASS
                error = None
            
            duration = time.time() - start_time
            
            result = TestResult(
                name=test_name,
                status=status,
                duration=duration,
                error=error,
                output=f"Mock output for {test_name}"
            )
            
            # Update statistics
            self.total_tests_run += 1
            if status == TestStatus.PASS:
                self.total_passed += 1
            elif status == TestStatus.FAIL:
                self.total_failed += 1
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.total_tests_run += 1
            self.total_failed += 1
            
            return TestResult(
                name=test_name,
                status=TestStatus.FAIL,
                duration=duration,
                error=str(e)
            )
    
    async def run_all_tools(self, level: TestLevel = TestLevel.ALL) -> Dict[str, Dict[TestLevel, List[TestResult]]]:
        """Run validation for all tools."""
        self.start_time = time.time()
        
        logger.info(f"Starting validation for all {len(self.tools)} tools at {level.value} level")
        
        all_results = {}
        
        for tool_name in self.tools:
            tool_results = {}
            
            if level == TestLevel.ALL:
                # Run all levels
                for test_level in [TestLevel.BASIC, TestLevel.EDGE_CASES, TestLevel.INTEGRATION]:
                    results = await self.run_validation_gate(tool_name, test_level)
                    tool_results[test_level] = results
            else:
                # Run specific level
                results = await self.run_validation_gate(tool_name, level)
                tool_results[level] = results
            
            all_results[tool_name] = tool_results
        
        return all_results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tools = len(self.tools)
        completed_tools = len(self.results)
        
        # Calculate statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for tool_results in self.results.values():
            for level_results in tool_results.values():
                for result in level_results:
                    total_tests += 1
                    if result.status == TestStatus.PASS:
                        passed_tests += 1
                    elif result.status == TestStatus.FAIL:
                        failed_tests += 1
        
        # Build report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_tools": total_tools,
                "completed_tools": completed_tools,
                "completion_rate": (completed_tools / total_tools * 100) if total_tools > 0 else 0,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "pass_rate": if total_tests > 0 else 0
            },
            "tool_results": {},
            "failed_tests": [],
            "performance_metrics": {
                "total_runtime": time.time() - self.start_time if self.start_time else 0,
                "average_test_time": 0
            }
        }
        
        # Add detailed tool results
        for tool_name, tool_results in self.results.items():
            tool_summary = {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "levels": {}
            }
            
            for level, results in tool_results.items():
                level_summary = {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.status == TestStatus.PASS),
                    "failed": sum(1 for r in results if r.status == TestStatus.FAIL),
                    "tests": [
                        {
                            "name": r.name,
                            "status": r.status.value,
                            "duration": r.duration,
                            "error": r.error
                        }
                        for r in results
                    ]
                }
                
                tool_summary["levels"][level.value] = level_summary
                tool_summary["total_tests"] += level_summary["total"]
                tool_summary["passed"] += level_summary["passed"]
                tool_summary["failed"] += level_summary["failed"]
                
                # Collect failed tests
                for result in results:
                    if result.status == TestStatus.FAIL:
                        report["failed_tests"].append({
                            "tool": tool_name,
                            "level": level.value,
                            "test": result.name,
                            "error": result.error
                        })
            
            report["tool_results"][tool_name] = tool_summary
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> Path:
        """Save test report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"
        
        report_path = self.output_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to: {report_path}")
        return report_path
    
    def update_tracking_file(self) -> None:
        """Update the markdown tracking file with current results."""
        tracking_file = Path("tests/validation_gates/MCP_TOOLS_TESTING_TRACKER.md")
        
        if not tracking_file.exists():
            logger.warning("Tracking file not found, cannot update")
            return
        
        # Read current tracking file
        with open(tracking_file, 'r') as f:
            content = f.read()
        
        # Update with current results
        # This is a simplified implementation - in practice, you'd want more sophisticated parsing
        for tool_name, tool_results in self.results.items():
            for level, results in tool_results.items():
                for result in results:
                    if result.status == TestStatus.PASS:
                        # Update checkboxes to checked
                        content = content.replace(
                            f"- [ ] **{level.value.replace('_', ' ').title()}**",
                            f"- [x] **{level.value.replace('_', ' ').title()}**"
                        )
        
        # Save updated tracking file
        with open(tracking_file, 'w') as f:
            f.write(content)
        
        logger.info("Tracking file updated with current results")


async def main():
    """Main entry point for the validation framework."""
    parser = argparse.ArgumentParser(description="MCP Task Orchestrator Validation Framework")
    parser.add_argument("--tool", type=str, help="Specific tool to test")
    parser.add_argument("--level", type=str, choices=["basic", "edge_cases", "integration", "all"], 
                       default="basic", help="Test level to run")
    parser.add_argument("--all", action="store_true", help="Run all tools")
    parser.add_argument("--report", action="store_true", help="Generate report only")
    parser.add_argument("--output", type=str, help="Output directory for results")
    
    args = parser.parse_args()
    
    # Initialize framework
    output_dir = Path(args.output) if args.output else None
    framework = ValidationFramework(output_dir)
    
    if args.report:
        # Generate report from existing results
        report = framework.generate_report()
        report_path = framework.save_report(report)
        print(f"Report generated: {report_path}")
        return
    
    # Run tests
    if args.all:
        results = await framework.run_all_tools(TestLevel(args.level))
    elif args.tool:
        if args.tool not in framework.tools:
            print(f"Error: Unknown tool '{args.tool}'")
            print(f"Available tools: {list(framework.tools.keys())}")
            sys.exit(1)
        
        results = await framework.run_validation_gate(args.tool, TestLevel(args.level))
    else:
        print("Error: Must specify either --tool or --all")
        sys.exit(1)
    
    # Generate and save report
    report = framework.generate_report()
    report_path = framework.save_report(report)
    
    # Update tracking file
    framework.update_tracking_file()
    
    # Print summary
    print(f"\nValidation Summary:")
    print(f"Tests run: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed_tests']}")
    print(f"Failed: {report['summary']['failed_tests']}")
    print(f"Pass rate: {report['summary']['pass_rate']:.1f}%")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())