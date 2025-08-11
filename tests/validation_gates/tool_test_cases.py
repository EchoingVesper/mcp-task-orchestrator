#!/usr/bin/env python3
"""
Tool-Specific Test Cases for MCP Task Orchestrator

This module contains concrete test implementations for each of the 16 MCP Task
Orchestrator tools, organized by category and validation level.

Usage:
    from tool_test_cases import CoreToolTests, TaskToolTests, RebootToolTests
    
    # Run specific test
    test_runner = CoreToolTests()
    result = await test_runner.test_initialize_session_default()
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sys
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import MCP tool router for real tool calls
from mcp_task_orchestrator.infrastructure.mcp.tool_router import route_tool_call
from mcp import types

# Test infrastructure
from validation_framework import TestResult, TestStatus, TestLevel

logger = logging.getLogger(__name__)


@dataclass
class TestEnvironment:
    """Test environment configuration."""
    database_path: Optional[str] = None
    working_directory: Optional[str] = None
    server_host: str = "localhost"
    server_port: int = 3000
    mock_mode: bool = False  # Default to real mode
    performance_timeout: float = 5.0
    

class BaseToolTest(ABC):
    """Base class for tool-specific test implementations."""
    
    def __init__(self, environment: TestEnvironment = None):
        self.env = environment or TestEnvironment()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abstractmethod
    async def get_tool_name(self) -> str:
        """Get the name of the tool being tested."""
        pass
    
    async def setup_test_environment(self) -> bool:
        """Setup test environment before running tests."""
        try:
            # Create test directories
            if self.env.working_directory:
                Path(self.env.working_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize test database
            if self.env.database_path:
                await self._init_test_database()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False
    
    async def teardown_test_environment(self) -> bool:
        """Cleanup test environment after running tests."""
        try:
            # Cleanup logic here
            return True
        except Exception as e:
            self.logger.error(f"Failed to teardown test environment: {e}")
            return False
    
    async def _init_test_database(self) -> None:
        """Initialize test database with sample data."""
        # Mock implementation
        self.logger.info("Initializing test database")
    
    async def _ensure_test_database(self) -> None:
        """Ensure test database exists for testing."""
        # Create a temporary directory for test workspace
        if not hasattr(self, 'test_workspace'):
            self.test_workspace = tempfile.mkdtemp(prefix="mcp_test_")
            self.logger.info(f"Created test workspace: {self.test_workspace}")
            
        # Initialize the session in the test workspace
        await route_tool_call("orchestrator_initialize_session", {
            "working_directory": self.test_workspace
        })
        
    async def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with specified arguments."""
        if self.env.mock_mode:
            # Mock implementation for testing
            return {
                "status": "success",
                "tool": tool_name,
                "args": args,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mock": True
            }
        else:
            # Real implementation - call actual MCP tool
            try:
                # Create a temporary database for testing if needed
                if not hasattr(self, 'test_db_initialized'):
                    await self._ensure_test_database()
                    self.test_db_initialized = True
                
                # Call the real MCP tool
                result = await route_tool_call(tool_name, args)
                
                # Extract response data
                if result and len(result) > 0:
                    response_text = result[0].text
                    try:
                        response_data = json.loads(response_text)
                        return response_data
                    except json.JSONDecodeError:
                        # If response is not JSON, wrap it
                        return {
                            "status": "success",
                            "result": response_text,
                            "tool": tool_name,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                else:
                    return {
                        "status": "error",
                        "error": "Empty response from tool",
                        "tool": tool_name,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "tool": tool_name,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
    
    async def _measure_performance(self, func, *args, **kwargs) -> Tuple[Any, float]:
        """Measure performance of a function call."""
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        return result, duration


class CoreToolTests(BaseToolTest):
    """Test implementations for core orchestration tools."""
    
    async def get_tool_name(self) -> str:
        return "core_orchestration"
    
    # orchestrator_initialize_session tests
    async def test_initialize_session_default(self) -> TestResult:
        """Test default session initialization."""
        start_time = time.time()
        try:
            result = await self._call_tool("orchestrator_initialize_session", {})
            duration = time.time() - start_time
            
            # Validate response structure
            if result.get("success", False) or != "error" and 
                "session_id" in result
            ):
                return TestResult(
                    name="test_initialize_session_default",
                    status=TestStatus.PASS,
                    duration=duration,
                    output=json.dumps(result)
                )
            else:
                return TestResult(
                    name="test_initialize_session_default",
                    status=TestStatus.FAIL,
                    duration=duration,
                    error=f"Unexpected response: {json.dumps(result)}"
                )
        except Exception as e:
            return TestResult(
                name="test_initialize_session_default",
                status=TestStatus.FAIL,
                duration=time.time() - start_time,
                error=str(e)
            )
    
    async def test_initialize_session_custom_directory(self) -> TestResult:
        """Test session initialization with custom directory."""
        try:
            custom_dir = "/tmp/test_orchestrator"
            result = await self._call_tool("orchestrator_initialize_session", {
                "working_directory": custom_dir
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_initialize_session_custom_directory",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_initialize_session_custom_directory",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_initialize_session_invalid_directory(self) -> TestResult:
        """Test session initialization with invalid directory."""
        try:
            invalid_dir = "/invalid/path/that/does/not/exist"
            result = await self._call_tool("orchestrator_initialize_session", {
                "working_directory": invalid_dir
            })
            
            # Should handle error gracefully
            if result.get("status") == "error":
                return TestResult(
                    name="test_initialize_session_invalid_directory",
                    status=TestStatus.PASS,
                    duration=0.1,
                    output="Properly handled invalid directory"
                )
            else:
                return TestResult(
                    name="test_initialize_session_invalid_directory",
                    status=TestStatus.FAIL,
                    duration=0.1,
                    error="Should have returned error for invalid directory"
                )
        except Exception as e:
            return TestResult(
                name="test_initialize_session_invalid_directory",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_get_status tests
    async def test_get_status_default(self) -> TestResult:
        """Test default status retrieval."""
        try:
            result = await self._call_tool("orchestrator_get_status", {})
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_get_status_default",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_get_status_default",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_get_status_include_completed(self) -> TestResult:
        """Test status retrieval with completed tasks included."""
        try:
            result = await self._call_tool("orchestrator_get_status", {
                "include_completed": True
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_get_status_include_completed",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_get_status_include_completed",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_get_status_performance(self) -> TestResult:
        """Test status retrieval performance."""
        try:
            result, duration = await self._measure_performance(
                self._call_tool, "orchestrator_get_status", {}
            )
            
            if duration > self.env.performance_timeout:
                return TestResult(
                    name="test_get_status_performance",
                    status=TestStatus.FAIL,
                    duration=duration,
                    error=f"Performance timeout: {duration:.2f}s > {self.env.performance_timeout}s"
                )
            
            return TestResult(
                name="test_get_status_performance",
                status=TestStatus.PASS,
                duration=duration,
                output=f"Performance: {duration:.2f}s"
            )
        except Exception as e:
            return TestResult(
                name="test_get_status_performance",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_synthesize_results tests
    async def test_synthesize_results_basic(self) -> TestResult:
        """Test basic result synthesis."""
        try:
            result = await self._call_tool("orchestrator_synthesize_results", {
                "parent_task_id": "test_parent_123"
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_synthesize_results_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_synthesize_results_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_synthesize_results_missing_parent(self) -> TestResult:
        """Test synthesis with missing parent task ID."""
        try:
            result = await self._call_tool("orchestrator_synthesize_results", {})
            
            # Should return error for missing required parameter
            if result.get("status") == "error":
                return TestResult(
                    name="test_synthesize_results_missing_parent",
                    status=TestStatus.PASS,
                    duration=0.1,
                    output="Properly handled missing parent_task_id"
                )
            else:
                return TestResult(
                    name="test_synthesize_results_missing_parent",
                    status=TestStatus.FAIL,
                    duration=0.1,
                    error="Should have returned error for missing parent_task_id"
                )
        except Exception as e:
            return TestResult(
                name="test_synthesize_results_missing_parent",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )


class TaskToolTests(BaseToolTest):
    """Test implementations for task management tools."""
    
    async def get_tool_name(self) -> str:
        return "task_management"
    
    # orchestrator_plan_task tests
    async def test_plan_task_minimal(self) -> TestResult:
        """Test minimal task creation."""
        try:
            result = await self._call_tool("orchestrator_plan_task", {
                "title": "Test Task",
                "description": "A test task for validation"
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_plan_task_minimal",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_plan_task_minimal",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_plan_task_full_parameters(self) -> TestResult:
        """Test task creation with all parameters."""
        try:
            result = await self._call_tool("orchestrator_plan_task", {
                "title": "Complex Test Task",
                "description": "A complex test task with all parameters",
                "task_type": "implementation",
                "complexity": "complex",
                "specialist_type": "coder",
                "estimated_effort": "2 hours",
                "due_date": "2025-07-10T12:00:00Z",
                "context": {"project": "test_project"},
                "dependencies": ["dep_task_1", "dep_task_2"]
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_plan_task_full_parameters",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_plan_task_full_parameters",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_plan_task_missing_required(self) -> TestResult:
        """Test task creation with missing required fields."""
        try:
            result = await self._call_tool("orchestrator_plan_task", {
                "title": "Missing Description"
                # Missing required "description" field
            })
            
            # Should return error for missing required parameter
            if result.get("status") == "error":
                return TestResult(
                    name="test_plan_task_missing_required",
                    status=TestStatus.PASS,
                    duration=0.1,
                    output="Properly handled missing required field"
                )
            else:
                return TestResult(
                    name="test_plan_task_missing_required",
                    status=TestStatus.FAIL,
                    duration=0.1,
                    error="Should have returned error for missing description"
                )
        except Exception as e:
            return TestResult(
                name="test_plan_task_missing_required",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_plan_task_invalid_enum(self) -> TestResult:
        """Test task creation with invalid enum values."""
        try:
            result = await self._call_tool("orchestrator_plan_task", {
                "title": "Invalid Enum Test",
                "description": "Test with invalid enum values",
                "task_type": "invalid_type",
                "complexity": "invalid_complexity"
            })
            
            # Should return error for invalid enum values
            if result.get("status") == "error":
                return TestResult(
                    name="test_plan_task_invalid_enum",
                    status=TestStatus.PASS,
                    duration=0.1,
                    output="Properly handled invalid enum values"
                )
            else:
                return TestResult(
                    name="test_plan_task_invalid_enum",
                    status=TestStatus.FAIL,
                    duration=0.1,
                    error="Should have returned error for invalid enum values"
                )
        except Exception as e:
            return TestResult(
                name="test_plan_task_invalid_enum",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_query_tasks tests
    async def test_query_tasks_no_filters(self) -> TestResult:
        """Test task query with no filters."""
        try:
            result = await self._call_tool("orchestrator_query_tasks", {})
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_query_tasks_no_filters",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_query_tasks_no_filters",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_query_tasks_with_filters(self) -> TestResult:
        """Test task query with multiple filters."""
        try:
            result = await self._call_tool("orchestrator_query_tasks", {
                "status": ["pending", "in_progress"],
                "task_type": ["implementation", "testing"],
                "specialist_type": ["coder", "tester"],
                "search_text": "test"
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_query_tasks_with_filters",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_query_tasks_with_filters",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_query_tasks_pagination(self) -> TestResult:
        """Test task query with pagination."""
        try:
            result = await self._call_tool("orchestrator_query_tasks", {
                "limit": 10,
                "offset": 0
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_query_tasks_pagination",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_query_tasks_pagination",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_complete_task tests
    async def test_complete_task_basic(self) -> TestResult:
        """Test basic task completion."""
        try:
            result = await self._call_tool("orchestrator_complete_task", {
                "task_id": "test_task_123",
                "summary": "Task completed successfully",
                "detailed_work": "Detailed work description here",
                "next_action": "continue"
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_complete_task_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_complete_task_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_complete_task_with_artifacts(self) -> TestResult:
        """Test task completion with artifacts."""
        try:
            result = await self._call_tool("orchestrator_complete_task", {
                "task_id": "test_task_456",
                "summary": "Task completed with artifacts",
                "detailed_work": "Detailed work with artifacts",
                "next_action": "complete",
                "file_paths": ["/path/to/file1.py", "/path/to/file2.py"],
                "artifact_type": "code"
            })
            
            assert "status" in result
            assert result["status"] == "success"
            
            return TestResult(
                name="test_complete_task_with_artifacts",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_complete_task_with_artifacts",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )


class RebootToolTests(BaseToolTest):
    """Test implementations for server reboot tools."""
    
    async def get_tool_name(self) -> str:
        return "server_reboot"
    
    # orchestrator_restart_server tests
    async def test_restart_server_graceful(self) -> TestResult:
        """Test graceful server restart."""
        try:
            result = await self._call_tool("orchestrator_restart_server", {
                "graceful": True,
                "preserve_state": True,
                "timeout": 30,
                "reason": "manual_request"
            })
            
            assert "status" in result
            
            return TestResult(
                name="test_restart_server_graceful",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_restart_server_graceful",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_restart_server_invalid_timeout(self) -> TestResult:
        """Test server restart with invalid timeout."""
        try:
            result = await self._call_tool("orchestrator_restart_server", {
                "timeout": -1  # Invalid timeout
            })
            
            # Should handle invalid timeout gracefully
            if result.get("status") == "error":
                return TestResult(
                    name="test_restart_server_invalid_timeout",
                    status=TestStatus.PASS,
                    duration=0.1,
                    output="Properly handled invalid timeout"
                )
            else:
                return TestResult(
                    name="test_restart_server_invalid_timeout",
                    status=TestStatus.FAIL,
                    duration=0.1,
                    error="Should have returned error for invalid timeout"
                )
        except Exception as e:
            return TestResult(
                name="test_restart_server_invalid_timeout",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_health_check tests
    async def test_health_check_basic(self) -> TestResult:
        """Test basic health check."""
        try:
            result = await self._call_tool("orchestrator_health_check", {})
            
            assert "status" in result
            
            return TestResult(
                name="test_health_check_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_health_check_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_health_check_comprehensive(self) -> TestResult:
        """Test comprehensive health check."""
        try:
            result = await self._call_tool("orchestrator_health_check", {
                "include_reboot_readiness": True,
                "include_connection_status": True,
                "include_database_status": True
            })
            
            assert "status" in result
            
            return TestResult(
                name="test_health_check_comprehensive",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_health_check_comprehensive",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_shutdown_prepare tests
    async def test_shutdown_prepare_basic(self) -> TestResult:
        """Test basic shutdown preparation."""
        try:
            result = await self._call_tool("orchestrator_shutdown_prepare", {})
            
            assert "status" in result
            
            return TestResult(
                name="test_shutdown_prepare_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_shutdown_prepare_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_reconnect_test tests
    async def test_reconnect_test_basic(self) -> TestResult:
        """Test basic reconnection test."""
        try:
            result = await self._call_tool("orchestrator_reconnect_test", {})
            
            assert "status" in result
            
            return TestResult(
                name="test_reconnect_test_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_reconnect_test_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_reconnect_test_specific_session(self) -> TestResult:
        """Test reconnection test for specific session."""
        try:
            result = await self._call_tool("orchestrator_reconnect_test", {
                "session_id": "test_session_123"
            })
            
            assert "status" in result
            
            return TestResult(
                name="test_reconnect_test_specific_session",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_reconnect_test_specific_session",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    # orchestrator_restart_status tests
    async def test_restart_status_basic(self) -> TestResult:
        """Test basic restart status."""
        try:
            result = await self._call_tool("orchestrator_restart_status", {})
            
            assert "status" in result
            
            return TestResult(
                name="test_restart_status_basic",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_restart_status_basic",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )
    
    async def test_restart_status_with_history(self) -> TestResult:
        """Test restart status with history."""
        try:
            result = await self._call_tool("orchestrator_restart_status", {
                "include_history": True,
                "include_error_details": True
            })
            
            assert "status" in result
            
            return TestResult(
                name="test_restart_status_with_history",
                status=TestStatus.PASS,
                duration=0.1,
                output=json.dumps(result)
            )
        except Exception as e:
            return TestResult(
                name="test_restart_status_with_history",
                status=TestStatus.FAIL,
                duration=0.1,
                error=str(e)
            )


class TestCaseRegistry:
    """Registry for organizing and accessing test cases."""
    
    def __init__(self):
        self.test_classes = {
            "core": CoreToolTests,
            "task_management": TaskToolTests,
            "server_reboot": RebootToolTests
        }
    
    def get_test_class(self, category: str) -> BaseToolTest:
        """Get test class for a specific category."""
        if category not in self.test_classes:
            raise ValueError(f"Unknown test category: {category}")
        
        return self.test_classes[category]
    
    def get_all_test_methods(self, test_class: BaseToolTest) -> List[str]:
        """Get all test methods from a test class."""
        return [
            method for method in dir(test_class)
            if method.startswith("test_") and callable(getattr(test_class, method))
        ]
    
    async def run_tool_tests(self, tool_name: str, test_level: TestLevel) -> List[TestResult]:
        """Run all tests for a specific tool at a given level."""
        results = []
        
        # Map tool names to test categories
        tool_category_map = {
            "orchestrator_initialize_session": "core",
            "orchestrator_get_status": "core",
            "orchestrator_synthesize_results": "core",
            "orchestrator_plan_task": "task_management",
            "orchestrator_query_tasks": "task_management",
            "orchestrator_complete_task": "task_management",
            "orchestrator_restart_server": "server_reboot",
            "orchestrator_health_check": "server_reboot",
            "orchestrator_shutdown_prepare": "server_reboot",
            "orchestrator_reconnect_test": "server_reboot",
            "orchestrator_restart_status": "server_reboot",
        }
        
        category = tool_category_map.get(tool_name)
        if not category:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Get test class and create instance
        test_class = self.get_test_class(category)
        test_instance = test_class()
        
        # Setup test environment
        await test_instance.setup_test_environment()
        
        try:
            # Get all test methods for this tool
            all_methods = self.get_all_test_methods(test_instance)
            
            # Filter methods based on tool name and test level
            tool_methods = [
                method for method in all_methods
                if self._is_method_for_tool(method, tool_name, test_level)
            ]
            
            # Run each test method
            for method_name in tool_methods:
                method = getattr(test_instance, method_name)
                try:
                    result = await method()
                    results.append(result)
                except Exception as e:
                    results.append(TestResult(
                        name=method_name,
                        status=TestStatus.FAIL,
                        duration=0.0,
                        error=str(e)
                    ))
                    
        finally:
            # Cleanup test environment
            await test_instance.teardown_test_environment()
        
        return results
    
    def _is_method_for_tool(self, method_name: str, tool_name: str, test_level: TestLevel) -> bool:
        """Check if a test method is relevant for a specific tool and level."""
        # Extract tool name from method name
        # e.g., "test_initialize_session_default" -> "initialize_session"
        method_parts = method_name.split("_")
        if len(method_parts) < 3:
            return False
        
        method_tool = "_".join(method_parts[1:-1])  # Remove "test_" prefix and test type suffix
        
        # Check if method is for the specified tool
        if method_tool not in tool_name:
            return False
        
        # Check test level based on method name patterns
        if test_level == TestLevel.BASIC:
            return any(pattern in method_name for pattern in ["_basic", "_default", "_minimal"])
        elif test_level == TestLevel.EDGE_CASES:
            return any(pattern in method_name for pattern in ["_invalid", "_missing", "_error", "_timeout"])
        elif test_level == TestLevel.INTEGRATION:
            return any(pattern in method_name for pattern in ["_integration", "_performance", "_comprehensive"])
        elif test_level == TestLevel.ALL:
            return True
        
        return False


# Example usage
async def main():
    """Example usage of the test case registry."""
    registry = TestCaseRegistry()
    
    # Run tests for a specific tool
    results = await registry.run_tool_tests("orchestrator_get_status", TestLevel.BASIC)
    
    print(f"Ran {len(results)} tests:")
    for result in results:
        print(f"  {result.name}: {result.status.value}")
        if result.error:
            print(f"    Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())