"""
Integration tests for MCP reboot tools.

This module tests the MCP tool interface for server reboot functionality,
ensuring all tools work correctly and handle edge cases properly.
"""

import asyncio
import json
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp_task_orchestrator.server.reboot_tools import (
        REBOOT_TOOLS, REBOOT_TOOL_HANDLERS,
        handle_restart_server, handle_health_check, handle_shutdown_prepare,
        handle_reconnect_test, handle_restart_status
    )
    from mcp_task_orchestrator.server.state_serializer import RestartReason
    from mcp import types
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_AVAILABLE = False


class TestMCPToolDefinitions(unittest.TestCase):
    """Test MCP tool definitions and schemas."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    def test_tool_registration(self):
        """Test that all required tools are registered."""
        expected_tools = [
            "orchestrator_restart_server",
            "orchestrator_health_check",
            "orchestrator_shutdown_prepare", 
            "orchestrator_reconnect_test",
            "orchestrator_restart_status"
        ]
        
        tool_names = [tool.name for tool in REBOOT_TOOLS]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names, 
                         f"Tool {expected_tool} not found in registered tools")

    def test_tool_schemas(self):
        """Test tool schema definitions."""
        for tool in REBOOT_TOOLS:
            self.assertIsInstance(tool, types.Tool)
            self.assertIsNotNone(tool.name)
            self.assertIsNotNone(tool.description)
            self.assertIsNotNone(tool.inputSchema)
            
            # Validate schema structure
            schema = tool.inputSchema
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)

    def test_handler_registration(self):
        """Test that all tools have corresponding handlers."""
        for tool in REBOOT_TOOLS:
            self.assertIn(tool.name, REBOOT_TOOL_HANDLERS, 
                         f"Handler for {tool.name} not found")

    def test_restart_server_schema(self):
        """Test restart server tool schema."""
        restart_tool = next(tool for tool in REBOOT_TOOLS 
                           if tool.name == "orchestrator_restart_server")
        
        properties = restart_tool.inputSchema["properties"]
        
        # Check required properties exist
        expected_properties = ["graceful", "preserve_state", "timeout", "reason"]
        for prop in expected_properties:
            self.assertIn(prop, properties)
        
        # Check reason enum values
        reason_enum = properties["reason"]["enum"]
        expected_reasons = ["configuration_update", "schema_migration", 
                          "error_recovery", "manual_request", "emergency_shutdown"]
        for reason in expected_reasons:
            self.assertIn(reason, reason_enum)


class TestRestartServerTool(unittest.IsolatedAsyncioTestCase):
    """Test restart server tool functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_valid_restart_request(self):
        """Test valid restart server request."""
        args = {
            "graceful": True,
            "preserve_state": True,
            "timeout": 30,
            "reason": "manual_request"
        }
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.trigger_restart.return_value = {
                "success": True,
                "phase": "complete",
                "progress": 100.0,
                "message": "Restart completed successfully"
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_server(args)
            
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], types.TextContent)
            
            response_data = json.loads(result[0].text)
            self.assertTrue(response_data["success"])
            self.assertTrue(response_data["graceful"])
            self.assertTrue(response_data["preserve_state"])

    async def test_invalid_restart_reason(self):
        """Test restart with invalid reason."""
        args = {
            "reason": "invalid_reason"
        }
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.trigger_restart.return_value = {
                "success": True,
                "phase": "complete"
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_server(args)
            response_data = json.loads(result[0].text)
            
            # Should default to manual_request
            mock_manager.trigger_restart.assert_called_with(
                RestartReason.MANUAL_REQUEST, 30
            )

    async def test_restart_tool_error_handling(self):
        """Test restart tool error handling."""
        args = {"graceful": True}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_get_manager.side_effect = Exception("Manager initialization failed")
            
            result = await handle_restart_server(args)
            response_data = json.loads(result[0].text)
            
            self.assertFalse(response_data["success"])
            self.assertIn("error", response_data)


class TestHealthCheckTool(unittest.IsolatedAsyncioTestCase):
    """Test health check tool functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_basic_health_check(self):
        """Test basic health check."""
        args = {}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_health_check(args)
            response_data = json.loads(result[0].text)
            
            self.assertIn("healthy", response_data)
            self.assertIn("timestamp", response_data)
            self.assertIn("server_version", response_data)
            self.assertIn("checks", response_data)

    async def test_health_check_with_options(self):
        """Test health check with specific options."""
        args = {
            "include_reboot_readiness": True,
            "include_connection_status": False,
            "include_database_status": True
        }
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_health_check(args)
            response_data = json.loads(result[0].text)
            
            self.assertIn("reboot_readiness", response_data["checks"])
            self.assertIn("database", response_data["checks"])

    async def test_health_check_failure(self):
        """Test health check with system failures."""
        args = {}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.side_effect = Exception("System error")
            mock_get_manager.return_value = mock_manager
            
            result = await handle_health_check(args)
            response_data = json.loads(result[0].text)
            
            self.assertFalse(response_data["healthy"])
            self.assertIn("reboot_readiness", response_data["checks"])
            self.assertIn("error", response_data["checks"]["reboot_readiness"])


class TestShutdownPrepareTool(unittest.IsolatedAsyncioTestCase):
    """Test shutdown preparation tool functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_shutdown_prepare_ready(self):
        """Test shutdown preparation when system is ready."""
        args = {}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {"maintenance_mode": False}
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_shutdown_prepare(args)
            response_data = json.loads(result[0].text)
            
            self.assertTrue(response_data["ready_for_shutdown"])
            self.assertEqual(len(response_data["blocking_issues"]), 0)
            self.assertIn("checks", response_data)

    async def test_shutdown_prepare_not_ready(self):
        """Test shutdown preparation when system is not ready."""
        args = {}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": False,
                "issues": ["Active operations in progress"],
                "details": {"maintenance_mode": True}
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_shutdown_prepare(args)
            response_data = json.loads(result[0].text)
            
            self.assertFalse(response_data["ready_for_shutdown"])
            self.assertGreater(len(response_data["blocking_issues"]), 0)

    async def test_shutdown_prepare_selective_checks(self):
        """Test shutdown preparation with selective checks."""
        args = {
            "check_active_tasks": True,
            "check_database_state": False,
            "check_client_connections": True
        }
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_shutdown_prepare(args)
            response_data = json.loads(result[0].text)
            
            self.assertIn("active_tasks", response_data["checks"])
            self.assertNotIn("database", response_data["checks"])
            self.assertIn("client_connections", response_data["checks"])


class TestReconnectTestTool(unittest.IsolatedAsyncioTestCase):
    """Test reconnection test tool functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_reconnect_test_all_sessions(self):
        """Test reconnection test for all sessions."""
        args = {}
        
        result = await handle_reconnect_test(args)
        response_data = json.loads(result[0].text)
        
        self.assertTrue(response_data["test_completed"])
        self.assertIn("timestamp", response_data)
        self.assertIn("results", response_data)

    async def test_reconnect_test_specific_session(self):
        """Test reconnection test for specific session."""
        args = {"session_id": "test_session_123"}
        
        result = await handle_reconnect_test(args)
        response_data = json.loads(result[0].text)
        
        self.assertTrue(response_data["test_completed"])
        self.assertIn("session_test", response_data["results"])
        self.assertEqual(
            response_data["results"]["session_test"]["session_id"],
            "test_session_123"
        )

    async def test_reconnect_test_with_options(self):
        """Test reconnection test with various options."""
        args = {
            "include_buffer_status": True,
            "include_reconnection_stats": True
        }
        
        result = await handle_reconnect_test(args)
        response_data = json.loads(result[0].text)
        
        self.assertIn("buffer_status", response_data["results"])
        self.assertIn("reconnection_stats", response_data["results"])


class TestRestartStatusTool(unittest.IsolatedAsyncioTestCase):
    """Test restart status tool functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_restart_status_basic(self):
        """Test basic restart status."""
        args = {}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_shutdown_status.return_value = {
                "phase": "idle",
                "progress": 0.0,
                "message": "Ready for restart",
                "errors": []
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_status(args)
            response_data = json.loads(result[0].text)
            
            self.assertIn("current_status", response_data)
            self.assertIn("timestamp", response_data)
            self.assertEqual(response_data["current_status"]["phase"], "idle")

    async def test_restart_status_with_errors(self):
        """Test restart status with error details."""
        args = {"include_error_details": True}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_shutdown_status.return_value = {
                "phase": "failed",
                "progress": 50.0,
                "message": "Restart failed",
                "errors": ["Database connection failed", "State serialization error"]
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_status(args)
            response_data = json.loads(result[0].text)
            
            self.assertIn("errors", response_data["current_status"])
            self.assertEqual(len(response_data["current_status"]["errors"]), 2)

    async def test_restart_status_without_errors(self):
        """Test restart status without error details."""
        args = {"include_error_details": False}
        
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_shutdown_status.return_value = {
                "phase": "complete",
                "progress": 100.0,
                "message": "Restart completed",
                "errors": ["Some error"]
            }
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_status(args)
            response_data = json.loads(result[0].text)
            
            self.assertNotIn("errors", response_data["current_status"])
            self.assertIn("error_count", response_data["current_status"])


class TestToolErrorHandling(unittest.IsolatedAsyncioTestCase):
    """Test error handling across all tools."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_all_tools_handle_exceptions(self):
        """Test that all tools handle exceptions gracefully."""
        tools_to_test = [
            ("orchestrator_restart_server", handle_restart_server),
            ("orchestrator_health_check", handle_health_check),
            ("orchestrator_shutdown_prepare", handle_shutdown_prepare),
            ("orchestrator_reconnect_test", handle_reconnect_test),
            ("orchestrator_restart_status", handle_restart_status)
        ]
        
        for tool_name, handler in tools_to_test:
            with self.subTest(tool=tool_name):
                # Force an exception in the handler
                with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
                    mock_get_manager.side_effect = Exception("Test exception")
                    
                    result = await handler({})
                    
                    self.assertEqual(len(result), 1)
                    self.assertIsInstance(result[0], types.TextContent)
                    
                    response_data = json.loads(result[0].text)
                    
                    # Should have error information
                    self.assertIn("error", response_data)
                    self.assertIn("Test exception", response_data["error"])


async def run_tool_integration_tests():
    """Run all MCP tool integration tests."""
    if not IMPORTS_AVAILABLE:
        print("⚠️  Warning: Required modules not available - skipping integration tests")
        return True
    
    test_cases = [
        TestMCPToolDefinitions,
        TestRestartServerTool,
        TestHealthCheckTool,
        TestShutdownPrepareTool,
        TestReconnectTestTool,
        TestRestartStatusTool,
        TestToolErrorHandling
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_case_class in test_cases:
        print(f"\n--- Running {test_case_class.__name__} ---")
        
        # Get test methods
        test_methods = [method for method in dir(test_case_class) 
                       if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            print(f"  Running {test_method}...")
            
            try:
                # Create test instance
                test_instance = test_case_class()
                
                # Run setup
                if hasattr(test_instance, 'asyncSetUp'):
                    await test_instance.asyncSetUp()
                elif hasattr(test_instance, 'setUp'):
                    test_instance.setUp()
                
                # Run test
                test_func = getattr(test_instance, test_method)
                if asyncio.iscoroutinefunction(test_func):
                    await test_func()
                else:
                    test_func()
                
                # Run teardown
                if hasattr(test_instance, 'asyncTearDown'):
                    await test_instance.asyncTearDown()
                elif hasattr(test_instance, 'tearDown'):
                    test_instance.tearDown()
                
                print(f"    ✓ {test_method} PASSED")
                passed_tests += 1
                
            except Exception as e:
                print(f"    ✗ {test_method} FAILED: {e}")
                failed_tests += 1
    
    print(f"\n--- MCP Tool Integration Test Results ---")
    print(f"Total: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = asyncio.run(run_tool_integration_tests())
    exit(0 if success else 1)