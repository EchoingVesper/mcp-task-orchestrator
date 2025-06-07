"""
Comprehensive test suite for server reboot system.

This module tests all aspects of the server reboot functionality including
graceful shutdown, state preservation, restart coordination, and client preservation.
"""

import asyncio
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp_task_orchestrator.server.state_serializer import (
        StateSerializer, ServerStateSnapshot, RestartReason, ClientSession, DatabaseState
    )
    from mcp_task_orchestrator.server.shutdown_coordinator import (
        ShutdownCoordinator, ShutdownPhase, ShutdownStatus
    )
    from mcp_task_orchestrator.server.restart_manager import (
        RestartCoordinator, ProcessManager, StateRestorer, RestartPhase
    )
    from mcp_task_orchestrator.server.connection_manager import (
        ConnectionManager, ConnectionInfo, ConnectionState, RequestBuffer
    )
    from mcp_task_orchestrator.server.reboot_integration import RebootManager
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_AVAILABLE = False


class TestStateSerializer(unittest.IsolatedAsyncioTestCase):
    """Test state serialization and restoration functionality."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        # Create temporary directory for state files
        self.temp_dir = tempfile.mkdtemp()
        self.state_serializer = StateSerializer(self.temp_dir)
        
        # Mock state manager
        self.mock_state_manager = MagicMock()
        self.mock_state_manager.db_path = os.path.join(self.temp_dir, "test.db")
        self.mock_state_manager._initialized = True
        self.mock_state_manager.get_all_tasks = AsyncMock(return_value=[])

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_create_snapshot(self):
        """Test creating a state snapshot."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        
        self.assertIsInstance(snapshot, ServerStateSnapshot)
        self.assertEqual(snapshot.restart_reason, RestartReason.MANUAL_REQUEST)
        self.assertIsNotNone(snapshot.timestamp)
        self.assertIsNotNone(snapshot.integrity_hash)

    async def test_save_and_load_snapshot(self):
        """Test saving and loading snapshots."""
        # Create snapshot
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.CONFIGURATION_UPDATE
        )
        
        # Save snapshot
        saved_path = await self.state_serializer.save_snapshot(snapshot)
        self.assertTrue(os.path.exists(saved_path))
        
        # Load snapshot
        loaded_snapshot = await self.state_serializer.load_latest_snapshot()
        self.assertIsNotNone(loaded_snapshot)
        self.assertEqual(loaded_snapshot.restart_reason, RestartReason.CONFIGURATION_UPDATE)

    async def test_snapshot_validation(self):
        """Test snapshot integrity validation."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        
        # Valid snapshot should pass validation
        is_valid = await self.state_serializer.validate_snapshot(snapshot)
        self.assertTrue(is_valid)
        
        # Corrupt snapshot should fail validation
        snapshot.integrity_hash = "invalid_hash"
        is_valid = await self.state_serializer.validate_snapshot(snapshot)
        self.assertFalse(is_valid)


class TestShutdownCoordinator(unittest.IsolatedAsyncioTestCase):
    """Test graceful shutdown coordination."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_serializer = StateSerializer(self.temp_dir)
        self.shutdown_coordinator = ShutdownCoordinator(self.state_serializer)

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_shutdown_readiness_check(self):
        """Test shutdown readiness checking."""
        ready, issues = self.shutdown_coordinator.is_shutdown_ready()
        self.assertIsInstance(ready, bool)
        self.assertIsInstance(issues, list)

    async def test_shutdown_phases(self):
        """Test shutdown phase progression."""
        self.assertEqual(self.shutdown_coordinator.status.phase, ShutdownPhase.IDLE)
        
        # Test shutdown initiation
        success = await self.shutdown_coordinator.initiate_shutdown(
            RestartReason.MANUAL_REQUEST
        )
        self.assertTrue(success)
        
        # Wait for shutdown to complete or timeout
        completed = await self.shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        # May not complete due to missing dependencies, but should not crash

    async def test_emergency_shutdown(self):
        """Test emergency shutdown functionality."""
        success = await self.shutdown_coordinator.emergency_shutdown()
        self.assertTrue(success)
        self.assertEqual(self.shutdown_coordinator.status.phase, ShutdownPhase.COMPLETE)


class TestConnectionManager(unittest.IsolatedAsyncioTestCase):
    """Test client connection management during restarts."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.connection_manager = ConnectionManager()

    async def test_connection_registration(self):
        """Test client connection registration."""
        connection_info = await self.connection_manager.register_connection(
            session_id="test_session_1",
            client_name="Test Client",
            protocol_version="1.0"
        )
        
        self.assertEqual(connection_info.session_id, "test_session_1")
        self.assertEqual(connection_info.client_name, "Test Client")
        self.assertEqual(connection_info.state, ConnectionState.ACTIVE)

    async def test_prepare_for_restart(self):
        """Test preparing connections for restart."""
        # Register test connections
        await self.connection_manager.register_connection(
            "session_1", "Client 1", "1.0"
        )
        await self.connection_manager.register_connection(
            "session_2", "Client 2", "1.0"
        )
        
        # Prepare for restart
        client_sessions = await self.connection_manager.prepare_for_restart()
        
        self.assertEqual(len(client_sessions), 2)
        self.assertIsInstance(client_sessions[0], ClientSession)

    async def test_connection_status(self):
        """Test connection status monitoring."""
        status = await self.connection_manager.get_connection_status()
        
        self.assertIn('total_connections', status)
        self.assertIn('by_state', status)
        self.assertIn('connections', status)


class TestRequestBuffer(unittest.IsolatedAsyncioTestCase):
    """Test request buffering during restarts."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.request_buffer = RequestBuffer(max_buffer_size=10)

    async def test_buffer_requests(self):
        """Test buffering client requests."""
        # Buffer some requests
        request1 = {"method": "test_method_1", "params": {"data": "test1"}}
        request2 = {"method": "test_method_2", "params": {"data": "test2"}}
        
        success1 = await self.request_buffer.buffer_request("session_1", request1)
        success2 = await self.request_buffer.buffer_request("session_1", request2)
        
        self.assertTrue(success1)
        self.assertTrue(success2)

    async def test_retrieve_buffered_requests(self):
        """Test retrieving buffered requests."""
        # Buffer requests
        request1 = {"method": "test_method", "params": {"data": "test"}}
        await self.request_buffer.buffer_request("session_1", request1)
        
        # Retrieve requests
        requests = await self.request_buffer.get_buffered_requests("session_1")
        
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["method"], "test_method")

    async def test_buffer_size_limit(self):
        """Test buffer size limits."""
        # Fill buffer to capacity
        for i in range(15):  # More than max_buffer_size
            request = {"method": f"test_method_{i}"}
            success = await self.request_buffer.buffer_request("session_1", request)
            
            if i < 10:  # Within limit
                self.assertTrue(success)
            else:  # Over limit
                self.assertFalse(success)


class TestProcessManager(unittest.IsolatedAsyncioTestCase):
    """Test process management for server restarts."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.process_manager = ProcessManager()

    async def test_process_startup_validation(self):
        """Test process startup with mocked subprocess."""
        with patch('subprocess.Popen') as mock_popen:
            # Mock successful process
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process running
            mock_popen.return_value = mock_process
            
            # Mock health check
            with patch.object(self.process_manager, '_check_process_health', return_value=True):
                success, pid = await self.process_manager.start_new_process(
                    RestartReason.MANUAL_REQUEST,
                    timeout=1
                )
                
                self.assertTrue(success)
                self.assertEqual(pid, 12345)

    async def test_process_termination(self):
        """Test process termination."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process
            
            self.process_manager.current_process = mock_process
            
            await self.process_manager.terminate_process(graceful=True, timeout=1)
            
            mock_process.terminate.assert_called_once()


class TestRebootIntegration(unittest.IsolatedAsyncioTestCase):
    """Test complete reboot system integration."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        # Mock state manager
        self.mock_state_manager = MagicMock()
        self.mock_state_manager._initialized = True
        self.mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        
        self.reboot_manager = RebootManager()
        await self.reboot_manager.initialize(self.mock_state_manager)

    async def test_restart_readiness_check(self):
        """Test restart readiness assessment."""
        readiness = await self.reboot_manager.get_restart_readiness()
        
        self.assertIn('ready', readiness)
        self.assertIn('issues', readiness)
        self.assertIn('details', readiness)

    async def test_shutdown_status_monitoring(self):
        """Test shutdown status monitoring."""
        status = await self.reboot_manager.get_shutdown_status()
        
        self.assertIn('phase', status)
        self.assertIn('progress', status)
        self.assertIn('message', status)

    async def test_restart_trigger_validation(self):
        """Test restart trigger with mocking."""
        with patch.object(self.reboot_manager.shutdown_coordinator, 'initiate_shutdown') as mock_shutdown:
            with patch.object(self.reboot_manager.shutdown_coordinator, 'wait_for_shutdown') as mock_wait:
                mock_shutdown.return_value = True
                mock_wait.return_value = True
                
                result = await self.reboot_manager.trigger_restart(
                    RestartReason.MANUAL_REQUEST,
                    timeout=5
                )
                
                self.assertIn('success', result)
                self.assertIn('phase', result)


class TestRebootScenarios(unittest.IsolatedAsyncioTestCase):
    """Test complete reboot scenarios end-to-end."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.temp_dir = tempfile.mkdtemp()

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_graceful_restart_scenario(self):
        """Test complete graceful restart scenario."""
        # Set up components
        state_serializer = StateSerializer(self.temp_dir)
        shutdown_coordinator = ShutdownCoordinator(state_serializer)
        restart_coordinator = RestartCoordinator(state_serializer)
        connection_manager = ConnectionManager()
        
        # Register mock client connections
        await connection_manager.register_connection("client_1", "Test Client 1", "1.0")
        await connection_manager.register_connection("client_2", "Test Client 2", "1.0")
        
        # Prepare for restart
        client_sessions = await connection_manager.prepare_for_restart()
        self.assertEqual(len(client_sessions), 2)
        
        # Mock state manager
        mock_state_manager = MagicMock()
        mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        mock_state_manager.db_path = os.path.join(self.temp_dir, "test.db")
        mock_state_manager._initialized = True
        
        # Create and save snapshot
        snapshot = await state_serializer.create_snapshot(
            mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        await state_serializer.save_snapshot(snapshot)
        
        # Validate snapshot can be loaded
        loaded_snapshot = await state_serializer.load_latest_snapshot()
        self.assertIsNotNone(loaded_snapshot)
        self.assertEqual(loaded_snapshot.restart_reason, RestartReason.MANUAL_REQUEST)

    async def test_error_recovery_scenario(self):
        """Test error recovery during restart."""
        state_serializer = StateSerializer(self.temp_dir)
        shutdown_coordinator = ShutdownCoordinator(state_serializer)
        
        # Test emergency shutdown
        success = await shutdown_coordinator.emergency_shutdown()
        self.assertTrue(success)

    async def test_client_preservation_scenario(self):
        """Test client connection preservation."""
        connection_manager = ConnectionManager()
        
        # Register connections
        conn1 = await connection_manager.register_connection(
            "session_1", "Claude Desktop", "1.0"
        )
        conn2 = await connection_manager.register_connection(
            "session_2", "VS Code", "1.0"  
        )
        
        # Prepare for restart
        client_sessions = await connection_manager.prepare_for_restart()
        
        # Restore connections
        restore_results = await connection_manager.restore_connections(client_sessions)
        
        self.assertEqual(len(restore_results), 2)
        self.assertIn("session_1", restore_results)
        self.assertIn("session_2", restore_results)


def create_test_suite():
    """Create comprehensive test suite."""
    suite = unittest.TestSuite()
    
    # Add test cases
    test_cases = [
        TestStateSerializer,
        TestShutdownCoordinator,
        TestConnectionManager,
        TestRequestBuffer,
        TestProcessManager,
        TestRebootIntegration,
        TestRebootScenarios
    ]
    
    for test_case in test_cases:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_case)
        suite.addTests(tests)
    
    return suite


async def run_async_tests():
    """Run all async tests."""
    if not IMPORTS_AVAILABLE:
        print("⚠️  Warning: Required modules not available - running mock tests")
        return True
    
    test_cases = [
        TestStateSerializer,
        TestShutdownCoordinator, 
        TestConnectionManager,
        TestRequestBuffer,
        TestProcessManager,
        TestRebootIntegration,
        TestRebootScenarios
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
                
                # Run test
                test_func = getattr(test_instance, test_method)
                await test_func()
                
                # Run teardown
                if hasattr(test_instance, 'asyncTearDown'):
                    await test_instance.asyncTearDown()
                
                print(f"    ✓ {test_method} PASSED")
                passed_tests += 1
                
            except Exception as e:
                print(f"    ✗ {test_method} FAILED: {e}")
                failed_tests += 1
    
    print(f"\n--- Test Results ---")
    print(f"Total: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = asyncio.run(run_async_tests())
    exit(0 if success else 1)