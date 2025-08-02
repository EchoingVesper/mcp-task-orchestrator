#!/usr/bin/env python3
"""
Comprehensive MCP Tools Validator

This script performs real validation of all MCP Task Orchestrator tools
with systematic testing and progress tracking.
"""

import asyncio
import json
import logging
import sys
import time
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_task_orchestrator.infrastructure.mcp.tool_router import route_tool_call
from mcp import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestLevel(Enum):
    """Test validation levels."""
    BASIC = "basic"
    EDGE_CASES = "edge_cases"
    INTEGRATION = "integration"


@dataclass
class TestResult:
    """Individual test result."""
    tool_name: str
    test_name: str
    level: TestLevel
    status: TestStatus
    duration: float
    details: str = ""
    error: Optional[str] = None
    response: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ToolTestConfig:
    """Configuration for testing a specific tool."""
    name: str
    category: str
    basic_params: Dict[str, Any]
    edge_case_params: List[Dict[str, Any]]
    success_criteria: List[str]
    requires_setup: bool = False
    setup_tool: Optional[str] = None


class ComprehensiveToolValidator:
    """Validates all MCP Task Orchestrator tools systematically."""
    
    def __init__(self):
        self.test_workspace = None
        self.test_task_id = None
        self.session_initialized = False
        self.results: List[TestResult] = []
        self.tools_config = self._initialize_tools_config()
        
    def _initialize_tools_config(self) -> Dict[str, ToolTestConfig]:
        """Initialize configuration for all tools."""
        return {
            # Core Orchestration Tools
            "orchestrator_initialize_session": ToolTestConfig(
                name="orchestrator_initialize_session",
                category="core",
                basic_params={},
                edge_case_params=[
                    {"working_directory": "/invalid/path/does/not/exist"},
                    {"working_directory": ""},
                ],
                success_criteria=["session_id", "workspace_path"]
            ),
            
            "orchestrator_get_status": ToolTestConfig(
                name="orchestrator_get_status",
                category="core",
                basic_params={},
                edge_case_params=[
                    {"include_completed": True},
                    {"include_completed": False},
                ],
                success_criteria=["tasks"],
                requires_setup=True
            ),
            
            "orchestrator_synthesize_results": ToolTestConfig(
                name="orchestrator_synthesize_results",
                category="core",
                basic_params={"parent_task_id": "placeholder"},  # Will be replaced
                edge_case_params=[
                    {"parent_task_id": "non_existent_task"},
                    {},  # Missing required parameter
                ],
                success_criteria=["synthesis_complete", "combined_results"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            # Task Management Tools
            "orchestrator_plan_task": ToolTestConfig(
                name="orchestrator_plan_task",
                category="task",
                basic_params={
                    "title": "Test Task",
                    "description": "A test task for validation"
                },
                edge_case_params=[
                    {"title": "Missing Description"},  # Missing required field
                    {
                        "title": "Invalid Enums",
                        "description": "Test with invalid enums",
                        "task_type": "invalid_type",
                        "complexity": "invalid_complexity"
                    },
                    {
                        "title": "Very Long Title " * 100,
                        "description": "Test with extremely long inputs"
                    }
                ],
                success_criteria=["task_id", "created"],
                requires_setup=True
            ),
            
            "orchestrator_update_task": ToolTestConfig(
                name="orchestrator_update_task",
                category="task",
                basic_params={
                    "task_id": "placeholder",  # Will be replaced
                    "description": "Updated description"
                },
                edge_case_params=[
                    {"task_id": "non_existent_task", "status": "completed"},
                    {"task_id": "placeholder", "status": "invalid_status"},
                ],
                success_criteria=["updated", "task_id"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            "orchestrator_delete_task": ToolTestConfig(
                name="orchestrator_delete_task",
                category="task",
                basic_params={"task_id": "placeholder"},  # Will be replaced
                edge_case_params=[
                    {"task_id": "non_existent_task"},
                    {"task_id": "placeholder", "force": True},
                ],
                success_criteria=["deleted", "archived"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            "orchestrator_cancel_task": ToolTestConfig(
                name="orchestrator_cancel_task",
                category="task",
                basic_params={
                    "task_id": "placeholder",  # Will be replaced
                    "reason": "Test cancellation"
                },
                edge_case_params=[
                    {"task_id": "non_existent_task"},
                    {"task_id": "placeholder", "preserve_work": False},
                ],
                success_criteria=["cancelled", "status"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            "orchestrator_query_tasks": ToolTestConfig(
                name="orchestrator_query_tasks",
                category="task",
                basic_params={},
                edge_case_params=[
                    {"status": ["pending", "in_progress"]},
                    {"search_text": "test"},
                    {"limit": 5, "offset": 0},
                ],
                success_criteria=["tasks", "total_count"],
                requires_setup=True
            ),
            
            "orchestrator_execute_task": ToolTestConfig(
                name="orchestrator_execute_task",
                category="task",
                basic_params={"task_id": "placeholder"},  # Will be replaced
                edge_case_params=[
                    {"task_id": "non_existent_task"},
                ],
                success_criteria=["execution_context", "specialist_prompt"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            "orchestrator_complete_task": ToolTestConfig(
                name="orchestrator_complete_task",
                category="task",
                basic_params={
                    "task_id": "placeholder",  # Will be replaced
                    "summary": "Task completed successfully",
                    "detailed_work": "Detailed work description here",
                    "next_action": "continue"
                },
                edge_case_params=[
                    {
                        "task_id": "non_existent_task",
                        "summary": "Test",
                        "detailed_work": "Test",
                        "next_action": "complete"
                    },
                    {
                        "task_id": "placeholder",
                        "summary": "Large artifact test",
                        "detailed_work": "x" * 10000,  # Large content
                        "next_action": "complete",
                        "artifact_type": "documentation"
                    }
                ],
                success_criteria=["completed", "artifacts_stored"],
                requires_setup=True,
                setup_tool="orchestrator_plan_task"
            ),
            
            "orchestrator_maintenance_coordinator": ToolTestConfig(
                name="orchestrator_maintenance_coordinator",
                category="maintenance",
                basic_params={"action": "scan_cleanup"},
                edge_case_params=[
                    {"action": "validate_structure"},
                    {"action": "update_documentation"},
                    {"action": "invalid_action"},  # Invalid action
                ],
                success_criteria=["action_completed", "results"],
                requires_setup=True
            ),
            
            # Reboot Tools
            "orchestrator_restart_server": ToolTestConfig(
                name="orchestrator_restart_server",
                category="reboot",
                basic_params={
                    "graceful": True,
                    "preserve_state": True,
                    "timeout": 30,
                    "reason": "manual_request"
                },
                edge_case_params=[
                    {"timeout": -1},  # Invalid timeout
                    {"reason": "invalid_reason"},
                ],
                success_criteria=["restart_initiated", "phase"],
                requires_setup=True
            ),
            
            "orchestrator_health_check": ToolTestConfig(
                name="orchestrator_health_check",
                category="reboot",
                basic_params={},
                edge_case_params=[
                    {
                        "include_reboot_readiness": True,
                        "include_connection_status": True,
                        "include_database_status": True
                    },
                ],
                success_criteria=["healthy", "timestamp", "checks"],
                requires_setup=True
            ),
            
            "orchestrator_shutdown_prepare": ToolTestConfig(
                name="orchestrator_shutdown_prepare",
                category="reboot",
                basic_params={},
                edge_case_params=[
                    {
                        "check_active_tasks": True,
                        "check_database_state": True,
                        "check_client_connections": True
                    },
                ],
                success_criteria=["ready_for_shutdown", "checks"],
                requires_setup=True
            ),
            
            "orchestrator_reconnect_test": ToolTestConfig(
                name="orchestrator_reconnect_test",
                category="reboot",
                basic_params={},
                edge_case_params=[
                    {"session_id": "test_session_123"},
                    {
                        "include_buffer_status": True,
                        "include_reconnection_stats": True
                    },
                ],
                success_criteria=["test_completed", "results"],
                requires_setup=True
            ),
            
            "orchestrator_restart_status": ToolTestConfig(
                name="orchestrator_restart_status",
                category="reboot",
                basic_params={},
                edge_case_params=[
                    {"include_history": True},
                    {"include_error_details": False},
                ],
                success_criteria=["current_status", "timestamp"],
                requires_setup=True
            ),
        }
    
    async def setup_test_environment(self) -> bool:
        """Setup test environment for all tests."""
        try:
            # Create temporary workspace
            self.test_workspace = tempfile.mkdtemp(prefix="mcp_validation_")
            logger.info(f"Created test workspace: {self.test_workspace}")
            
            # Initialize session
            result = await route_tool_call("orchestrator_initialize_session", {
                "working_directory": self.test_workspace
            })
            
            if result and len(result) > 0:
                response = json.loads(result[0].text)
                if "session_id" in response or response.get("success"):
                    self.session_initialized = True
                    logger.info("Test session initialized successfully")
                    return True
                    
            logger.error("Failed to initialize test session")
            return False
            
        except Exception as e:
            logger.error(f"Error setting up test environment: {e}")
            return False
    
    async def cleanup_test_environment(self) -> None:
        """Cleanup test environment after tests."""
        try:
            if self.test_workspace:
                import shutil
                shutil.rmtree(self.test_workspace)
                logger.info("Cleaned up test workspace")
        except Exception as e:
            logger.error(f"Error cleaning up test environment: {e}")
    
    async def run_tool_test(self, tool_name: str, level: TestLevel) -> TestResult:
        """Run a specific test for a tool."""
        config = self.tools_config.get(tool_name)
        if not config:
            return TestResult(
                tool_name=tool_name,
                test_name=f"{tool_name}_{level.value}",
                level=level,
                status=TestStatus.ERROR,
                duration=0.0,
                error="Tool configuration not found"
            )
        
        start_time = time.time()
        
        try:
            # Setup if required
            if config.requires_setup and not await self._setup_tool_test(config):
                return TestResult(
                    tool_name=tool_name,
                    test_name=f"{tool_name}_{level.value}",
                    level=level,
                    status=TestStatus.SKIPPED,
                    duration=time.time() - start_time,
                    details="Setup failed"
                )
            
            # Get test parameters
            if level == TestLevel.BASIC:
                params = await self._prepare_params(config.basic_params, config)
                result = await self._execute_tool_test(tool_name, params, config.success_criteria)
            
            elif level == TestLevel.EDGE_CASES:
                # Run multiple edge case tests
                edge_results = []
                for edge_params in config.edge_case_params:
                    prepared_params = await self._prepare_params(edge_params, config)
                    edge_result = await self._execute_tool_test(tool_name, prepared_params, config.success_criteria, expect_error=True)
                    edge_results.append(edge_result)
                
                # Aggregate edge case results
                all_passed = all(r.status in [TestStatus.PASSED, TestStatus.SKIPPED] for r in edge_results)
                result = TestResult(
                    tool_name=tool_name,
                    test_name=f"{tool_name}_edge_cases",
                    level=level,
                    status=TestStatus.PASSED if all_passed else TestStatus.FAILED,
                    duration=time.time() - start_time,
                    details=f"Tested {len(edge_results)} edge cases"
                )
            
            elif level == TestLevel.INTEGRATION:
                # Integration tests - test with other tools
                result = await self._run_integration_test(tool_name, config)
            
            else:
                result = TestResult(
                    tool_name=tool_name,
                    test_name=f"{tool_name}_{level.value}",
                    level=level,
                    status=TestStatus.SKIPPED,
                    duration=time.time() - start_time,
                    details="Test level not implemented"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error testing {tool_name} at {level.value}: {e}")
            return TestResult(
                tool_name=tool_name,
                test_name=f"{tool_name}_{level.value}",
                level=level,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e)
            )
    
    async def _setup_tool_test(self, config: ToolTestConfig) -> bool:
        """Setup required data for tool testing."""
        try:
            if config.setup_tool == "orchestrator_plan_task" and not self.test_task_id:
                # Create a test task
                result = await route_tool_call("orchestrator_plan_task", {
                    "title": "Validation Test Task",
                    "description": "Task created for validation testing"
                })
                
                if result and len(result) > 0:
                    response = json.loads(result[0].text)
                    if "task_id" in response:
                        self.test_task_id = response["task_id"]
                        logger.info(f"Created test task: {self.test_task_id}")
                        return True
                        
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    async def _prepare_params(self, params: Dict[str, Any], config: ToolTestConfig) -> Dict[str, Any]:
        """Prepare parameters by replacing placeholders."""
        prepared = params.copy()
        
        # Replace placeholders
        if "task_id" in prepared and prepared["task_id"] == "placeholder":
            prepared["task_id"] = self.test_task_id or "test_task_123"
            
        if "parent_task_id" in prepared and prepared["parent_task_id"] == "placeholder":
            prepared["parent_task_id"] = self.test_task_id or "test_parent_123"
            
        return prepared
    
    async def _execute_tool_test(
        self, 
        tool_name: str, 
        params: Dict[str, Any], 
        success_criteria: List[str],
        expect_error: bool = False
    ) -> TestResult:
        """Execute a single tool test."""
        start_time = time.time()
        
        try:
            # Call the tool
            result = await route_tool_call(tool_name, params)
            
            if result and len(result) > 0:
                response_text = result[0].text
                response_data = json.loads(response_text)
                
                # Check success criteria
                if expect_error:
                    # For edge cases, we expect proper error handling
                    is_success = "error" in response_data or response_data.get("status") == "error"
                    details = "Properly handled edge case" if is_success else "Failed to handle edge case"
                else:
                    # For basic tests, check success criteria
                    is_success = self._check_success_criteria(response_data, success_criteria)
                    details = "All success criteria met" if is_success else f"Missing criteria: {success_criteria}"
                
                return TestResult(
                    tool_name=tool_name,
                    test_name=f"{tool_name}_test",
                    level=TestLevel.BASIC,
                    status=TestStatus.PASSED if is_success else TestStatus.FAILED,
                    duration=time.time() - start_time,
                    details=details,
                    response=response_data
                )
            else:
                return TestResult(
                    tool_name=tool_name,
                    test_name=f"{tool_name}_test",
                    level=TestLevel.BASIC,
                    status=TestStatus.FAILED,
                    duration=time.time() - start_time,
                    details="Empty response from tool"
                )
                
        except Exception as e:
            return TestResult(
                tool_name=tool_name,
                test_name=f"{tool_name}_test",
                level=TestLevel.BASIC,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e)
            )
    
    def _check_success_criteria(self, response: Dict[str, Any], criteria: List[str]) -> bool:
        """Check if response meets success criteria."""
        # Check for explicit error
        if "error" in response and response["error"]:
            return False
            
        # Check for explicit success
        if "success" in response and not response["success"]:
            return False
            
        # Check specific criteria
        for criterion in criteria:
            if criterion not in response:
                # Check nested fields
                if "." in criterion:
                    parts = criterion.split(".")
                    current = response
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return False
                else:
                    return False
                    
        return True
    
    async def _run_integration_test(self, tool_name: str, config: ToolTestConfig) -> TestResult:
        """Run integration test for a tool."""
        start_time = time.time()
        
        # Simple integration test - just check if tool works with setup
        try:
            params = await self._prepare_params(config.basic_params, config)
            result = await self._execute_tool_test(tool_name, params, config.success_criteria)
            
            return TestResult(
                tool_name=tool_name,
                test_name=f"{tool_name}_integration",
                level=TestLevel.INTEGRATION,
                status=result.status,
                duration=time.time() - start_time,
                details="Integration with setup data successful" if result.status == TestStatus.PASSED else "Integration failed"
            )
            
        except Exception as e:
            return TestResult(
                tool_name=tool_name,
                test_name=f"{tool_name}_integration",
                level=TestLevel.INTEGRATION,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e)
            )
    
    async def validate_all_tools(self) -> Dict[str, Any]:
        """Validate all tools systematically."""
        logger.info("Starting comprehensive tool validation")
        
        # Setup test environment
        if not await self.setup_test_environment():
            return {
                "success": False,
                "error": "Failed to setup test environment",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        try:
            # Test each tool at each level
            for tool_name in self.tools_config:
                logger.info(f"Testing tool: {tool_name}")
                
                for level in [TestLevel.BASIC, TestLevel.EDGE_CASES, TestLevel.INTEGRATION]:
                    result = await self.run_tool_test(tool_name, level)
                    self.results.append(result)
                    
                    # Brief pause between tests
                    await asyncio.sleep(0.1)
            
            # Generate summary
            total_tests = len(self.results)
            passed_tests = sum(1 for r in self.results if r.status == TestStatus.PASSED)
            failed_tests = sum(1 for r in self.results if r.status == TestStatus.FAILED)
            error_tests = sum(1 for r in self.results if r.status == TestStatus.ERROR)
            skipped_tests = sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
            
            # Group results by tool
            tool_results = {}
            for result in self.results:
                if result.tool_name not in tool_results:
                    tool_results[result.tool_name] = []
                tool_results[result.tool_name].append({
                    "level": result.level.value,
                    "status": result.status.value,
                    "duration": result.duration,
                    "details": result.details,
                    "error": result.error
                })
            
            return {
                "success": failed_tests == 0 and error_tests == 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "skipped": skipped_tests,
                    "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
                },
                "tool_results": tool_results
            }
            
        finally:
            await self.cleanup_test_environment()
    
    def save_results(self, filename: str = None) -> Path:
        """Save validation results to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_results_{timestamp}.json"
        
        output_path = Path("tests/validation_results") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert results to serializable format
        results_data = []
        for result in self.results:
            results_data.append({
                "tool_name": result.tool_name,
                "test_name": result.test_name,
                "level": result.level.value,
                "status": result.status.value,
                "duration": result.duration,
                "details": result.details,
                "error": result.error,
                "timestamp": result.timestamp.isoformat()
            })
        
        with open(output_path, 'w') as f:
            json.dump({
                "validation_run": datetime.now(timezone.utc).isoformat(),
                "results": results_data
            }, f, indent=2)
        
        logger.info(f"Results saved to: {output_path}")
        return output_path


async def main():
    """Run comprehensive validation."""
    validator = ComprehensiveToolValidator()
    
    print("MCP Task Orchestrator - Comprehensive Tool Validation")
    print("=" * 60)
    
    # Run validation
    results = await validator.validate_all_tools()
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total Tests: {results['summary']['total_tests']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Errors: {results['summary']['errors']}")
    print(f"Skipped: {results['summary']['skipped']}")
    print(f"Pass Rate: {results['summary']['pass_rate']:.1f}%")
    
    # Print tool-specific results
    print("\nTool Results:")
    for tool_name, tool_tests in results['tool_results'].items():
        statuses = [t['status'] for t in tool_tests]
        overall = "PASS" if all(s in ["passed", "skipped"] for s in statuses) else "FAIL"
        print(f"  {tool_name}: {overall}")
        for test in tool_tests:
            print(f"    - {test['level']}: {test['status']}")
    
    # Save results
    output_path = validator.save_results()
    print(f"\nDetailed results saved to: {output_path}")
    
    # Update tracking file
    # TODO: Update MCP_TOOLS_TESTING_TRACKER.md with results
    
    return results


if __name__ == "__main__":
    asyncio.run(main())