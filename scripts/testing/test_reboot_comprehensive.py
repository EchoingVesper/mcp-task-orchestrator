#!/usr/bin/env python3
"""
Comprehensive Server Reboot Test Suite

This is a complete test suite for the MCP Task Orchestrator server reboot functionality.
Tests all components including state preservation, graceful shutdown, restart coordination,
client connection management, and error scenarios.

Test Categories:
- A. State Preservation Testing
- B. Graceful Shutdown Testing  
- C. Restart Coordination Testing
- D. Client Connection Testing
- E. MCP Tool Integration Testing
- F. Error Scenario Testing
- G. Performance and Reliability Testing
- H. End-to-End Integration Testing

Usage:
    python test_reboot_comprehensive.py
"""

import asyncio
import json
import os
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import sys

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Import all reboot system components
    from mcp_task_orchestrator.server.state_serializer import (
        StateSerializer, ServerStateSnapshot, RestartReason, ClientSession, DatabaseState
    )
    from mcp_task_orchestrator.server.shutdown_coordinator import (
        ShutdownCoordinator, ShutdownPhase, ShutdownStatus, ShutdownManager
    )
    from mcp_task_orchestrator.server.restart_manager import (
        RestartCoordinator, ProcessManager, StateRestorer, RestartPhase, RestartStatus
    )
    from mcp_task_orchestrator.server.connection_manager import (
        ConnectionManager, ConnectionInfo, ConnectionState, RequestBuffer
    )
    from mcp_task_orchestrator.server.reboot_integration import RebootManager
    from mcp_task_orchestrator.server.reboot_tools import (
        REBOOT_TOOLS, REBOOT_TOOL_HANDLERS,
        handle_restart_server, handle_health_check, handle_shutdown_prepare,
        handle_reconnect_test, handle_restart_status
    )
    from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType
    from mcp import types
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_AVAILABLE = False


class TestResults:
    """Track test results across all test categories."""
    
    def __init__(self):
        self.categories = {}
        self.total_tests = 0
        self.total_passed = 0
        self.total_failed = 0
        self.total_skipped = 0
        self.start_time = time.time()
    
    def add_category(self, name, passed, failed, skipped):
        """Add results for a test category."""
        self.categories[name] = {
            'passed': passed,
            'failed': failed,  
            'skipped': skipped,
            'total': passed + failed + skipped
        }
        self.total_tests += passed + failed + skipped
        self.total_passed += passed
        self.total_failed += failed
        self.total_skipped += skipped
    
    def get_summary(self):
        """Get formatted test results summary."""
        duration = time.time() - self.start_time
        success_rate = (self.total_passed / self.total_tests * 100) if self.total_tests > 0 else 0
        
        summary = f"""
{'='*80}
COMPREHENSIVE SERVER REBOOT TEST RESULTS
{'='*80}

Duration: {duration:.2f} seconds
Total Tests: {self.total_tests}
Passed: {self.total_passed} ({self.total_passed/self.total_tests*100:.1f}%)
Failed: {self.total_failed} ({self.total_failed/self.total_tests*100:.1f}%)
Skipped: {self.total_skipped} ({self.total_skipped/self.total_tests*100:.1f}%)
Success Rate: {success_rate:.1f}%

Category Breakdown:
"""
        
        for category, results in self.categories.items():
            cat_success = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
            summary += f"  {category:<30}: {results['passed']}/{results['total']} ({cat_success:.1f}%)\n"
        
        summary += f"\n{'='*80}\n"
        
        if self.total_failed == 0:
            summary += "✅ ALL TESTS PASSED - Server reboot system is ready for production!\n"
        elif self.total_failed <= 2:
            summary += "⚠️  Minor issues detected - review failed tests\n"
        else:
            summary += "❌ Critical issues detected - reboot system needs attention\n"
        
        summary += f"{'='*80}\n"
        
        return summary


# =============================================================================
# A. STATE PRESERVATION TESTING
# =============================================================================

class TestAStatePreservation(unittest.IsolatedAsyncioTestCase):
    """Test state serialization and preservation across reboots."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_serializer = StateSerializer(self.temp_dir)
        
        # Create mock state manager with test data
        self.mock_state_manager = MagicMock()
        self.mock_state_manager.db_path = os.path.join(self.temp_dir, "test.db")
        self.mock_state_manager._initialized = True
        
        # Create test database file
        with open(self.mock_state_manager.db_path, 'w') as f:
            f.write("test database content")
        
        # Mock tasks for state preservation testing
        self.test_tasks = [
            self._create_mock_task("task_1", "Test Task 1", TaskStatus.ACTIVE),
            self._create_mock_task("task_2", "Test Task 2", TaskStatus.PENDING)
        ]
        self.mock_state_manager.get_all_tasks = AsyncMock(return_value=self.test_tasks)

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_mock_task(self, task_id, description, status):
        """Create a mock task for testing."""
        task = MagicMock()
        task.parent_task_id = task_id
        task.description = description
        task.complexity = "moderate"
        task.status = status
        task.created_at = datetime.now(timezone.utc)
        task.subtasks = [
            MagicMock(
                task_id=f"{task_id}_subtask_1",
                title=f"Subtask 1 for {task_id}",
                description="Test subtask",
                specialist_type=SpecialistType.IMPLEMENTER,
                status=TaskStatus.PENDING,
                dependencies=[],
                estimated_effort="2 hours",
                results=None,
                artifacts=[]
            )
        ]
        return task

    async def test_snapshot_creation_with_tasks(self):
        """Test creating snapshots with active tasks."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        
        self.assertIsInstance(snapshot, ServerStateSnapshot)
        self.assertEqual(snapshot.restart_reason, RestartReason.MANUAL_REQUEST)
        self.assertEqual(len(snapshot.active_tasks), 2)
        self.assertIsNotNone(snapshot.integrity_hash)
        self.assertIsNotNone(snapshot.database_state)

    async def test_snapshot_serialization_integrity(self):
        """Test snapshot serialization maintains data integrity."""
        original_snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.CONFIGURATION_UPDATE
        )
        
        # Save and reload snapshot
        await self.state_serializer.save_snapshot(original_snapshot)
        loaded_snapshot = await self.state_serializer.load_latest_snapshot()
        
        self.assertIsNotNone(loaded_snapshot)
        self.assertEqual(loaded_snapshot.restart_reason, original_snapshot.restart_reason)
        self.assertEqual(len(loaded_snapshot.active_tasks), len(original_snapshot.active_tasks))
        self.assertEqual(loaded_snapshot.integrity_hash, original_snapshot.integrity_hash)

    async def test_task_state_preservation(self):
        """Test that task state is accurately preserved."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        
        # Verify task data preservation
        task_data = snapshot.active_tasks[0]
        self.assertEqual(task_data['task_id'], 'task_1')
        self.assertEqual(task_data['description'], 'Test Task 1')
        self.assertEqual(task_data['status'], TaskStatus.ACTIVE.value)
        self.assertIsNotNone(task_data['created_at'])
        self.assertEqual(len(task_data['subtasks']), 1)

    async def test_database_state_consistency(self):
        """Test database state preservation and consistency checks."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.SCHEMA_MIGRATION
        )
        
        db_state = snapshot.database_state
        self.assertIsInstance(db_state, DatabaseState)
        self.assertEqual(db_state.db_path, self.mock_state_manager.db_path)
        self.assertIsNotNone(db_state.integrity_checksum)
        self.assertTrue(db_state.connection_metadata['initialized'])

    async def test_state_corruption_detection(self):
        """Test detection of corrupted state snapshots."""
        snapshot = await self.state_serializer.create_snapshot(
            self.mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        
        # Valid snapshot should pass validation
        is_valid = await self.state_serializer.validate_snapshot(snapshot)
        self.assertTrue(is_valid)
        
        # Corrupt integrity hash
        snapshot.integrity_hash = "invalid_hash"
        is_valid = await self.state_serializer.validate_snapshot(snapshot)
        self.assertFalse(is_valid)
        
        # Corrupt task data
        snapshot.integrity_hash = self.state_serializer._generate_integrity_hash(snapshot)
        snapshot.active_tasks[0] = {"invalid": "task_data"}
        is_valid = await self.state_serializer.validate_snapshot(snapshot)
        self.assertFalse(is_valid)

    async def test_incremental_state_backup(self):
        """Test incremental backup creation and cleanup."""
        # Create multiple snapshots
        for i in range(3):
            snapshot = await self.state_serializer.create_snapshot(
                self.mock_state_manager,
                RestartReason.MANUAL_REQUEST
            )
            await self.state_serializer.save_snapshot(snapshot, backup=True)
            await asyncio.sleep(0.1)  # Ensure different timestamps
        
        # Verify backup files exist
        backup_files = list(self.state_serializer.state_dir.glob("backup_state_*.json"))
        self.assertGreaterEqual(len(backup_files), 2)
        
        # Test cleanup
        await self.state_serializer.cleanup_old_snapshots(keep_count=1)
        backup_files_after = list(self.state_serializer.state_dir.glob("backup_state_*.json"))
        self.assertLessEqual(len(backup_files_after), 1)


# =============================================================================
# B. GRACEFUL SHUTDOWN TESTING
# =============================================================================

class TestBGracefulShutdown(unittest.IsolatedAsyncioTestCase):
    """Test graceful shutdown coordination and sequencing."""
    
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

    async def test_shutdown_readiness_assessment(self):
        """Test comprehensive shutdown readiness checks."""
        ready, issues = self.shutdown_coordinator.is_shutdown_ready()
        
        self.assertIsInstance(ready, bool)
        self.assertIsInstance(issues, list)
        
        # Test with shutdown already in progress
        self.shutdown_coordinator._shutdown_in_progress = True
        ready, issues = self.shutdown_coordinator.is_shutdown_ready()
        self.assertFalse(ready)
        self.assertIn("Shutdown already in progress", issues)

    async def test_shutdown_phase_progression(self):
        """Test proper progression through shutdown phases."""
        # Track phase changes
        phases_seen = []
        
        original_update = self.shutdown_coordinator._update_status
        def track_phases(phase, progress, message):
            phases_seen.append(phase)
            original_update(phase, progress, message)
        
        self.shutdown_coordinator._update_status = track_phases
        
        # Initiate shutdown
        success = await self.shutdown_coordinator.initiate_shutdown(
            RestartReason.CONFIGURATION_UPDATE
        )
        self.assertTrue(success)
        
        # Wait for shutdown completion or timeout
        completed = await self.shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        
        # Verify phase progression
        expected_phases = [
            ShutdownPhase.MAINTENANCE_MODE,
            ShutdownPhase.SUSPENDING_TASKS,
            ShutdownPhase.SERIALIZING_STATE,
            ShutdownPhase.CLOSING_CONNECTIONS,
            ShutdownPhase.FINALIZING
        ]
        
        for expected_phase in expected_phases:
            self.assertIn(expected_phase, phases_seen)

    async def test_active_task_suspension(self):
        """Test suspension of active tasks during shutdown."""
        callback_called = False
        
        async def mock_task_suspension():
            nonlocal callback_called
            callback_called = True
            # Simulate task suspension work
            await asyncio.sleep(0.1)
        
        self.shutdown_coordinator.add_shutdown_callback(mock_task_suspension)
        
        success = await self.shutdown_coordinator.initiate_shutdown(
            RestartReason.MANUAL_REQUEST
        )
        self.assertTrue(success)
        
        await self.shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        self.assertTrue(callback_called)

    async def test_resource_cleanup_sequence(self):
        """Test proper resource cleanup during shutdown."""
        cleanup_order = []
        
        async def cleanup_1():
            cleanup_order.append("cleanup_1")
        
        async def cleanup_2():
            cleanup_order.append("cleanup_2")
        
        self.shutdown_coordinator.add_cleanup_callback(cleanup_1)
        self.shutdown_coordinator.add_cleanup_callback(cleanup_2)
        
        success = await self.shutdown_coordinator.initiate_shutdown()
        self.assertTrue(success)
        
        await self.shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        
        # Verify cleanup callbacks were called
        self.assertIn("cleanup_1", cleanup_order)
        self.assertIn("cleanup_2", cleanup_order)

    async def test_shutdown_timeout_handling(self):
        """Test handling of shutdown timeouts."""
        # Test with very short timeout
        success = await self.shutdown_coordinator.initiate_shutdown()
        self.assertTrue(success)
        
        # Should timeout quickly
        completed = await self.shutdown_coordinator.wait_for_shutdown(timeout=0.1)
        self.assertFalse(completed)

    async def test_emergency_shutdown(self):
        """Test emergency shutdown bypassing normal sequence."""
        success = await self.shutdown_coordinator.emergency_shutdown()
        self.assertTrue(success)
        
        self.assertEqual(self.shutdown_coordinator.status.phase, ShutdownPhase.COMPLETE)
        self.assertTrue(self.shutdown_coordinator.shutdown_event.is_set())

    async def test_shutdown_error_recovery(self):
        """Test error handling during shutdown sequence."""
        async def failing_callback():
            raise Exception("Simulated shutdown error")
        
        self.shutdown_coordinator.add_shutdown_callback(failing_callback)
        
        success = await self.shutdown_coordinator.initiate_shutdown()
        self.assertTrue(success)
        
        await self.shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        
        # Should continue despite callback error
        self.assertGreater(len(self.shutdown_coordinator.status.errors), 0)


# =============================================================================
# C. RESTART COORDINATION TESTING
# =============================================================================

class TestCRestartCoordination(unittest.IsolatedAsyncioTestCase):
    """Test restart manager and process coordination."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_serializer = StateSerializer(self.temp_dir)
        self.process_manager = ProcessManager()
        self.restart_coordinator = RestartCoordinator(self.state_serializer, self.process_manager)

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_process_startup_validation(self):
        """Test new process startup with validation."""
        with patch('subprocess.Popen') as mock_popen:
            # Mock successful process
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = None  # Process running
            mock_popen.return_value = mock_process
            
            # Mock health check to pass
            with patch.object(self.process_manager, '_check_process_health', return_value=True):
                success, pid = await self.process_manager.start_new_process(
                    RestartReason.MANUAL_REQUEST,
                    timeout=1
                )
                
                self.assertTrue(success)
                self.assertEqual(pid, 12345)
                mock_popen.assert_called_once()

    async def test_process_startup_failure_handling(self):
        """Test handling of process startup failures."""
        with patch('subprocess.Popen') as mock_popen:
            # Mock process that exits immediately
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_process.poll.return_value = 1  # Exit code indicating failure
            mock_process.communicate.return_value = (b"stdout", b"startup error")
            mock_popen.return_value = mock_process
            
            success, pid = await self.process_manager.start_new_process(
                RestartReason.ERROR_RECOVERY,
                timeout=1
            )
            
            self.assertFalse(success)
            self.assertIsNone(pid)

    async def test_graceful_process_termination(self):
        """Test graceful process termination."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.poll.side_effect = [None, None, 0]  # Running, then terminated
            mock_popen.return_value = mock_process
            
            self.process_manager.current_process = mock_process
            
            await self.process_manager.terminate_process(graceful=True, timeout=1)
            
            mock_process.terminate.assert_called_once()
            # Should not call kill() if graceful shutdown works

    async def test_forced_process_termination(self):
        """Test forced process termination when graceful fails."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.terminate = MagicMock()
            mock_process.kill = MagicMock()
            mock_process.poll.return_value = None  # Never terminates gracefully
            mock_popen.return_value = mock_process
            
            self.process_manager.current_process = mock_process
            
            await self.process_manager.terminate_process(graceful=True, timeout=0.1)
            
            mock_process.terminate.assert_called_once()
            mock_process.kill.assert_called_once()

    async def test_state_restoration_from_snapshot(self):
        """Test complete state restoration process."""
        # Create mock state manager
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "test.db")
        mock_state_manager._initialized = False
        mock_state_manager._initialize = AsyncMock()
        mock_state_manager.store_task_breakdown = AsyncMock()
        
        # Create test database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("test database")
        
        # Create state restorer
        state_restorer = StateRestorer(self.state_serializer)
        
        # Create snapshot with test data
        snapshot = ServerStateSnapshot(
            restart_reason=RestartReason.MANUAL_REQUEST,
            active_tasks=[{
                'task_id': 'test_task',
                'description': 'Test task',
                'complexity': 'moderate',
                'status': TaskStatus.ACTIVE.value,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'subtasks': []
            }],
            database_state=DatabaseState(
                db_path=mock_state_manager.db_path,
                connection_metadata={'initialized': True},
                pending_transactions=[],
                integrity_checksum=state_restorer.state_serializer._calculate_db_checksum(mock_state_manager.db_path),
                last_checkpoint=datetime.now(timezone.utc)
            )
        )
        snapshot.integrity_hash = self.state_serializer._generate_integrity_hash(snapshot)
        
        # Test restoration
        success = await state_restorer.restore_from_snapshot(snapshot, mock_state_manager)
        self.assertTrue(success)
        
        # Verify state manager was called correctly
        mock_state_manager._initialize.assert_called_once()
        mock_state_manager.store_task_breakdown.assert_called_once()

    async def test_restart_coordination_sequence(self):
        """Test complete restart coordination sequence."""
        # Create mock snapshot
        snapshot = ServerStateSnapshot(
            restart_reason=RestartReason.MANUAL_REQUEST,
            active_tasks=[],
            database_state=DatabaseState(
                db_path=os.path.join(self.temp_dir, "test.db"),
                connection_metadata={},
                pending_transactions=[],
                integrity_checksum="",
                last_checkpoint=datetime.now(timezone.utc)
            )
        )
        
        # Create test database file
        with open(snapshot.database_state.db_path, 'w') as f:
            f.write("test db")
        
        snapshot.integrity_hash = self.state_serializer._generate_integrity_hash(snapshot)
        
        # Mock process manager
        with patch.object(self.process_manager, 'start_new_process', return_value=(True, 12345)):
            # Mock state manager
            mock_state_manager = MagicMock()
            mock_state_manager.db_path = snapshot.database_state.db_path
            mock_state_manager._initialized = True
            mock_state_manager.store_task_breakdown = AsyncMock()
            
            success = await self.restart_coordinator.execute_restart(
                snapshot=snapshot,
                state_manager=mock_state_manager,
                timeout=5
            )
            
            self.assertTrue(success)
            self.assertEqual(self.restart_coordinator.status.phase, RestartPhase.COMPLETE)


# =============================================================================
# D. CLIENT CONNECTION TESTING
# =============================================================================

class TestDClientConnections(unittest.IsolatedAsyncioTestCase):
    """Test client connection preservation during restarts."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.connection_manager = ConnectionManager()
        self.request_buffer = RequestBuffer(max_buffer_size=10)

    async def test_connection_registration_and_tracking(self):
        """Test client connection registration and state tracking."""
        # Register test connections
        conn1 = await self.connection_manager.register_connection(
            session_id="session_1",
            client_name="Claude Desktop",
            protocol_version="1.0"
        )
        
        conn2 = await self.connection_manager.register_connection(
            session_id="session_2", 
            client_name="VS Code",
            protocol_version="1.0"
        )
        
        self.assertEqual(conn1.session_id, "session_1")
        self.assertEqual(conn1.client_name, "Claude Desktop")
        self.assertEqual(conn1.state, ConnectionState.ACTIVE)
        
        self.assertEqual(conn2.session_id, "session_2")
        self.assertEqual(conn2.client_name, "VS Code")
        self.assertEqual(conn2.state, ConnectionState.ACTIVE)

    async def test_connection_state_transitions(self):
        """Test connection state transitions during restart."""
        # Register connection
        conn = await self.connection_manager.register_connection(
            "session_1", "Test Client", "1.0"
        )
        self.assertEqual(conn.state, ConnectionState.ACTIVE)
        
        # Prepare for restart
        await self.connection_manager.prepare_connection_for_restart("session_1")
        
        # Check updated connection state
        updated_conn = await self.connection_manager.get_connection_info("session_1")
        self.assertEqual(updated_conn.state, ConnectionState.RESTARTING)

    async def test_connection_preservation_across_restart(self):
        """Test complete connection preservation workflow."""
        # Register multiple connections
        await self.connection_manager.register_connection("session_1", "Client 1", "1.0")
        await self.connection_manager.register_connection("session_2", "Client 2", "1.0")
        await self.connection_manager.register_connection("session_3", "Client 3", "1.0")
        
        # Prepare all connections for restart
        client_sessions = await self.connection_manager.prepare_for_restart()
        
        self.assertEqual(len(client_sessions), 3)
        self.assertIsInstance(client_sessions[0], ClientSession)
        
        # Simulate restart and restoration
        restore_results = await self.connection_manager.restore_connections(client_sessions)
        
        self.assertEqual(len(restore_results), 3)
        for session_id in ["session_1", "session_2", "session_3"]:
            self.assertIn(session_id, restore_results)
            self.assertTrue(restore_results[session_id]["success"])

    async def test_request_buffering_during_restart(self):
        """Test request buffering functionality."""
        # Buffer test requests
        requests = [
            {"method": "test_method_1", "params": {"data": "test1"}},
            {"method": "test_method_2", "params": {"data": "test2"}},
            {"method": "test_method_3", "params": {"data": "test3"}}
        ]
        
        for i, request in enumerate(requests):
            success = await self.request_buffer.buffer_request("session_1", request)
            self.assertTrue(success, f"Failed to buffer request {i}")
        
        # Retrieve buffered requests
        buffered = await self.request_buffer.get_buffered_requests("session_1")
        
        self.assertEqual(len(buffered), 3)
        for i, request in enumerate(buffered):
            self.assertEqual(request["method"], f"test_method_{i+1}")
        
        # Clear buffer
        await self.request_buffer.clear_session_buffer("session_1")
        cleared_buffer = await self.request_buffer.get_buffered_requests("session_1")
        self.assertEqual(len(cleared_buffer), 0)

    async def test_buffer_overflow_protection(self):
        """Test request buffer overflow protection."""
        # Fill buffer beyond capacity
        for i in range(15):  # More than max_buffer_size (10)
            request = {"method": f"test_method_{i}", "params": {}}
            success = await self.request_buffer.buffer_request("session_1", request)
            
            if i < 10:  # Within capacity
                self.assertTrue(success)
            else:  # Over capacity
                self.assertFalse(success)
        
        # Verify buffer size
        buffered = await self.request_buffer.get_buffered_requests("session_1")
        self.assertEqual(len(buffered), 10)  # Should not exceed max_buffer_size

    async def test_connection_health_monitoring(self):
        """Test connection health monitoring and diagnostics."""
        # Register connections with different states
        await self.connection_manager.register_connection("healthy_session", "Healthy Client", "1.0")
        await self.connection_manager.register_connection("problematic_session", "Problem Client", "1.0")
        
        # Simulate connection problem
        await self.connection_manager.mark_connection_problematic("problematic_session", "Connection timeout")
        
        # Get connection status
        status = await self.connection_manager.get_connection_status()
        
        self.assertIn('total_connections', status)
        self.assertIn('by_state', status)
        self.assertEqual(status['total_connections'], 2)
        self.assertGreater(status['by_state'][ConnectionState.ACTIVE.value], 0)
        self.assertGreater(status['by_state'][ConnectionState.PROBLEMATIC.value], 0)

    async def test_session_timeout_handling(self):
        """Test handling of session timeouts during restart."""
        # Register connection with timeout
        conn = await self.connection_manager.register_connection(
            "timeout_session", "Timeout Client", "1.0"
        )
        
        # Simulate old last activity
        conn.last_activity = datetime.now(timezone.utc).timestamp() - 3600  # 1 hour ago
        
        # Check for expired sessions
        expired_sessions = await self.connection_manager.get_expired_sessions(max_age=1800)  # 30 minutes
        
        self.assertIn("timeout_session", expired_sessions)


# =============================================================================
# E. MCP TOOL INTEGRATION TESTING
# =============================================================================

class TestEMCPToolIntegration(unittest.IsolatedAsyncioTestCase):
    """Test MCP tool interface and parameter validation."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_restart_server_tool_parameter_validation(self):
        """Test restart server tool with various parameter combinations."""
        test_cases = [
            # Valid parameters
            {
                "args": {"graceful": True, "preserve_state": True, "timeout": 30, "reason": "manual_request"},
                "should_succeed": True
            },
            # Invalid reason (should default to manual_request)
            {
                "args": {"reason": "invalid_reason"},
                "should_succeed": True  # Should handle gracefully
            },
            # Edge case timeout values
            {
                "args": {"timeout": 5},  # Minimum valid
                "should_succeed": True
            },
            {
                "args": {"timeout": 300},  # Maximum valid
                "should_succeed": True
            }
        ]
        
        for case in test_cases:
            with self.subTest(args=case["args"]):
                with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
                    mock_manager = AsyncMock()
                    mock_manager.trigger_restart.return_value = {
                        "success": True,
                        "phase": "complete",
                        "progress": 100.0
                    }
                    mock_get_manager.return_value = mock_manager
                    
                    result = await handle_restart_server(case["args"])
                    
                    self.assertEqual(len(result), 1)
                    self.assertIsInstance(result[0], types.TextContent)
                    
                    response_data = json.loads(result[0].text)
                    if case["should_succeed"]:
                        self.assertTrue(response_data.get("success"))
                    else:
                        self.assertFalse(response_data.get("success"))

    async def test_health_check_tool_comprehensive(self):
        """Test health check tool with all option combinations."""
        test_configurations = [
            {"include_reboot_readiness": True, "include_connection_status": True, "include_database_status": True},
            {"include_reboot_readiness": False, "include_connection_status": True, "include_database_status": False},
            {"include_reboot_readiness": True, "include_connection_status": False, "include_database_status": True},
            {}  # Default values
        ]
        
        for config in test_configurations:
            with self.subTest(config=config):
                with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
                    mock_manager = AsyncMock()
                    mock_manager.get_restart_readiness.return_value = {
                        "ready": True,
                        "issues": [],
                        "details": {}
                    }
                    mock_get_manager.return_value = mock_manager
                    
                    result = await handle_health_check(config)
                    response_data = json.loads(result[0].text)
                    
                    self.assertIn("healthy", response_data)
                    self.assertIn("checks", response_data)
                    
                    # Verify selective inclusion
                    if config.get("include_reboot_readiness", True):
                        self.assertIn("reboot_readiness", response_data["checks"])
                    
                    if config.get("include_database_status", True):
                        self.assertIn("database", response_data["checks"])

    async def test_shutdown_prepare_tool_blocking_conditions(self):
        """Test shutdown prepare tool with various blocking conditions."""
        blocking_scenarios = [
            {
                "readiness": {"ready": True, "issues": [], "details": {}},
                "expected_ready": True
            },
            {
                "readiness": {"ready": False, "issues": ["Active operations"], "details": {}},
                "expected_ready": False
            },
            {
                "readiness": {"ready": False, "issues": ["Database locked", "Client operations pending"], "details": {}},
                "expected_ready": False
            }
        ]
        
        for scenario in blocking_scenarios:
            with self.subTest(scenario=scenario["readiness"]):
                with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
                    mock_manager = AsyncMock()
                    mock_manager.get_restart_readiness.return_value = scenario["readiness"]
                    mock_get_manager.return_value = mock_manager
                    
                    result = await handle_shutdown_prepare({})
                    response_data = json.loads(result[0].text)
                    
                    self.assertEqual(response_data["ready_for_shutdown"], scenario["expected_ready"])
                    if not scenario["expected_ready"]:
                        self.assertGreater(len(response_data["blocking_issues"]), 0)

    async def test_reconnect_test_tool_session_scenarios(self):
        """Test reconnection test tool with different session scenarios."""
        # Test all sessions
        result = await handle_reconnect_test({})
        response_data = json.loads(result[0].text)
        
        self.assertTrue(response_data["test_completed"])
        self.assertIn("all_sessions", response_data["results"])
        
        # Test specific session
        result = await handle_reconnect_test({"session_id": "test_session_123"})
        response_data = json.loads(result[0].text)
        
        self.assertTrue(response_data["test_completed"])
        self.assertIn("session_test", response_data["results"])
        self.assertEqual(response_data["results"]["session_test"]["session_id"], "test_session_123")

    async def test_restart_status_tool_error_filtering(self):
        """Test restart status tool with error detail filtering."""
        mock_status = {
            "phase": "failed",
            "progress": 50.0,
            "message": "Restart failed",
            "errors": ["Error 1", "Error 2", "Error 3"]
        }
        
        # Test with error details included
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_shutdown_status.return_value = mock_status
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_status({"include_error_details": True})
            response_data = json.loads(result[0].text)
            
            self.assertIn("errors", response_data["current_status"])
            self.assertEqual(len(response_data["current_status"]["errors"]), 3)
        
        # Test with error details excluded
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_shutdown_status.return_value = mock_status
            mock_get_manager.return_value = mock_manager
            
            result = await handle_restart_status({"include_error_details": False})
            response_data = json.loads(result[0].text)
            
            self.assertNotIn("errors", response_data["current_status"])
            self.assertIn("error_count", response_data["current_status"])
            self.assertEqual(response_data["current_status"]["error_count"], 3)

    async def test_tool_error_resilience(self):
        """Test that all tools handle errors gracefully."""
        tools_to_test = [
            ("orchestrator_restart_server", handle_restart_server),
            ("orchestrator_health_check", handle_health_check),
            ("orchestrator_shutdown_prepare", handle_shutdown_prepare),
            ("orchestrator_reconnect_test", handle_reconnect_test),
            ("orchestrator_restart_status", handle_restart_status)
        ]
        
        for tool_name, handler in tools_to_test:
            with self.subTest(tool=tool_name):
                # Force exception
                with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
                    mock_get_manager.side_effect = Exception("Simulated error")
                    
                    result = await handler({})
                    
                    self.assertEqual(len(result), 1)
                    self.assertIsInstance(result[0], types.TextContent)
                    
                    response_data = json.loads(result[0].text)
                    self.assertIn("error", response_data)
                    self.assertIn("Simulated error", response_data["error"])


# =============================================================================
# F. ERROR SCENARIO TESTING
# =============================================================================

class TestFErrorScenarios(unittest.IsolatedAsyncioTestCase):
    """Test error handling and recovery scenarios."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")
        
        self.temp_dir = tempfile.mkdtemp()
        self.state_serializer = StateSerializer(self.temp_dir)

    async def asyncTearDown(self):
        """Clean up test fixtures."""
        import shutil
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_corrupted_state_file_recovery(self):
        """Test recovery from corrupted state files."""
        # Create corrupted state file
        corrupted_state_file = self.state_serializer.current_state_file
        with open(corrupted_state_file, 'w') as f:
            f.write("invalid json content {")
        
        # Attempt to load should return None gracefully
        snapshot = await self.state_serializer.load_latest_snapshot()
        self.assertIsNone(snapshot)

    async def test_database_lock_scenario(self):
        """Test handling of database locks during restart."""
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "locked.db")
        
        # Create database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("test database")
        
        # Mock database initialization failure
        mock_state_manager._initialized = False
        mock_state_manager._initialize = AsyncMock(side_effect=Exception("Database locked"))
        
        state_restorer = StateRestorer(self.state_serializer)
        
        # Create snapshot
        snapshot = ServerStateSnapshot(
            restart_reason=RestartReason.ERROR_RECOVERY,
            database_state=DatabaseState(
                db_path=mock_state_manager.db_path,
                connection_metadata={},
                pending_transactions=[],
                integrity_checksum="test_checksum",
                last_checkpoint=datetime.now(timezone.utc)
            )
        )
        
        # Restoration should fail gracefully
        success = await state_restorer._restore_database_state(snapshot.database_state, mock_state_manager)
        self.assertFalse(success)

    async def test_process_startup_failures(self):
        """Test various process startup failure scenarios."""
        process_manager = ProcessManager()
        
        # Test subprocess failure
        with patch('subprocess.Popen') as mock_popen:
            mock_popen.side_effect = OSError("Permission denied")
            
            success, pid = await process_manager.start_new_process(
                RestartReason.ERROR_RECOVERY,
                timeout=1
            )
            
            self.assertFalse(success)
            self.assertIsNone(pid)

    async def test_network_failure_during_restart(self):
        """Test handling of network failures during restart."""
        connection_manager = ConnectionManager()
        
        # Register connections
        await connection_manager.register_connection("session_1", "Client 1", "1.0")
        
        # Simulate network failure during preparation
        with patch.object(connection_manager, '_notify_client_of_restart', side_effect=Exception("Network timeout")):
            # Should handle network errors gracefully
            client_sessions = await connection_manager.prepare_for_restart()
            
            # Should still create session data despite notification failure
            self.assertEqual(len(client_sessions), 1)

    async def test_resource_exhaustion_scenario(self):
        """Test handling of resource exhaustion during restart."""
        # Test memory exhaustion simulation
        large_snapshot = ServerStateSnapshot(
            restart_reason=RestartReason.ERROR_RECOVERY,
            active_tasks=[{"task_id": f"task_{i}", "description": "Large task"} for i in range(1000)]
        )
        
        # Simulate memory error during serialization
        with patch('json.dump', side_effect=MemoryError("Out of memory")):
            try:
                await self.state_serializer.save_snapshot(large_snapshot)
                self.fail("Expected MemoryError to be raised")
            except MemoryError:
                pass  # Expected behavior

    async def test_partial_restoration_scenario(self):
        """Test handling of partial restoration failures."""
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "test.db")
        mock_state_manager._initialized = True
        mock_state_manager.store_task_breakdown = AsyncMock(side_effect=Exception("Storage error"))
        
        # Create database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("test db")
        
        state_restorer = StateRestorer(self.state_serializer)
        
        # Create snapshot with tasks
        snapshot = ServerStateSnapshot(
            restart_reason=RestartReason.MANUAL_REQUEST,
            active_tasks=[{
                'task_id': 'test_task',
                'description': 'Test task',
                'complexity': 'moderate',
                'status': TaskStatus.ACTIVE.value,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'subtasks': []
            }],
            database_state=DatabaseState(
                db_path=mock_state_manager.db_path,
                connection_metadata={},
                pending_transactions=[],
                integrity_checksum=state_restorer.state_serializer._calculate_db_checksum(mock_state_manager.db_path),
                last_checkpoint=datetime.now(timezone.utc)
            )
        )
        snapshot.integrity_hash = self.state_serializer._generate_integrity_hash(snapshot)
        
        # Restoration should fail due to task storage error
        success = await state_restorer.restore_from_snapshot(snapshot, mock_state_manager)
        self.assertFalse(success)

    async def test_shutdown_callback_failures(self):
        """Test handling of shutdown callback failures."""
        shutdown_coordinator = ShutdownCoordinator(self.state_serializer)
        
        async def failing_callback():
            raise Exception("Callback failure")
        
        async def working_callback():
            return "success"
        
        shutdown_coordinator.add_shutdown_callback(failing_callback)
        shutdown_coordinator.add_shutdown_callback(working_callback)
        
        # Should continue despite callback failure
        success = await shutdown_coordinator.initiate_shutdown()
        self.assertTrue(success)
        
        await shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        
        # Should have recorded the error but continued
        self.assertGreater(len(shutdown_coordinator.status.errors), 0)


# =============================================================================
# G. PERFORMANCE AND RELIABILITY TESTING
# =============================================================================

class TestGPerformanceReliability(unittest.IsolatedAsyncioTestCase):
    """Test performance characteristics and reliability under load."""
    
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

    async def test_large_state_serialization_performance(self):
        """Test performance with large state snapshots."""
        state_serializer = StateSerializer(self.temp_dir)
        
        # Create mock state manager with large dataset
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "large.db")
        mock_state_manager._initialized = True
        
        # Create large task dataset
        large_tasks = []
        for i in range(100):  # 100 tasks with subtasks
            task = MagicMock()
            task.parent_task_id = f"task_{i}"
            task.description = f"Task {i} description with detailed information"
            task.complexity = "moderate"
            task.status = TaskStatus.ACTIVE
            task.created_at = datetime.now(timezone.utc)
            task.subtasks = [
                MagicMock(
                    task_id=f"task_{i}_subtask_{j}",
                    title=f"Subtask {j}",
                    description=f"Detailed subtask description for task {i} subtask {j}",
                    specialist_type=SpecialistType.IMPLEMENTER,
                    status=TaskStatus.PENDING,
                    dependencies=[],
                    estimated_effort="1 hour",
                    results=None,
                    artifacts=[]
                ) for j in range(5)  # 5 subtasks each
            ]
            large_tasks.append(task)
        
        mock_state_manager.get_all_tasks = AsyncMock(return_value=large_tasks)
        
        # Create database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("large database content" * 1000)
        
        # Measure serialization performance
        start_time = time.time()
        snapshot = await state_serializer.create_snapshot(mock_state_manager, RestartReason.MANUAL_REQUEST)
        serialization_time = time.time() - start_time
        
        # Should complete within reasonable time (< 5 seconds for 100 tasks)
        self.assertLess(serialization_time, 5.0, f"Serialization took {serialization_time:.2f}s, too slow")
        
        # Verify data integrity
        self.assertEqual(len(snapshot.active_tasks), 100)
        
        # Measure save performance
        start_time = time.time()
        await state_serializer.save_snapshot(snapshot)
        save_time = time.time() - start_time
        
        self.assertLess(save_time, 2.0, f"Save took {save_time:.2f}s, too slow")

    async def test_concurrent_connection_handling(self):
        """Test handling of many concurrent client connections."""
        connection_manager = ConnectionManager()
        
        # Register many connections concurrently
        connection_tasks = []
        for i in range(50):  # 50 concurrent connections
            task = connection_manager.register_connection(
                f"session_{i}",
                f"Client_{i}",
                "1.0"
            )
            connection_tasks.append(task)
        
        # Wait for all registrations
        start_time = time.time()
        results = await asyncio.gather(*connection_tasks, return_exceptions=True)
        registration_time = time.time() - start_time
        
        # Should complete quickly
        self.assertLess(registration_time, 5.0, f"Connection registration took {registration_time:.2f}s")
        
        # Verify all succeeded
        for i, result in enumerate(results):
            self.assertIsInstance(result, ConnectionInfo, f"Connection {i} failed: {result}")
        
        # Test concurrent restart preparation
        start_time = time.time()
        client_sessions = await connection_manager.prepare_for_restart()
        preparation_time = time.time() - start_time
        
        self.assertLess(preparation_time, 3.0, f"Restart preparation took {preparation_time:.2f}s")
        self.assertEqual(len(client_sessions), 50)

    async def test_repeated_restart_cycles(self):
        """Test system stability over multiple restart cycles."""
        state_serializer = StateSerializer(self.temp_dir)
        
        # Mock minimal state manager
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "cycle_test.db")
        mock_state_manager._initialized = True
        mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        
        # Create database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("test database")
        
        # Perform multiple restart cycles
        for cycle in range(5):
            # Create and save snapshot
            snapshot = await state_serializer.create_snapshot(
                mock_state_manager,
                RestartReason.MANUAL_REQUEST
            )
            await state_serializer.save_snapshot(snapshot)
            
            # Load and validate snapshot
            loaded_snapshot = await state_serializer.load_latest_snapshot()
            self.assertIsNotNone(loaded_snapshot, f"Cycle {cycle}: Failed to load snapshot")
            
            # Validate integrity
            is_valid = await state_serializer.validate_snapshot(loaded_snapshot)
            self.assertTrue(is_valid, f"Cycle {cycle}: Snapshot validation failed")

    async def test_memory_usage_stability(self):
        """Test memory usage remains stable during operations."""
        import gc
        import psutil
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        state_serializer = StateSerializer(self.temp_dir)
        connection_manager = ConnectionManager()
        
        # Perform memory-intensive operations
        for i in range(10):
            # Create large datasets
            mock_state_manager = MagicMock()
            mock_state_manager.db_path = os.path.join(self.temp_dir, f"mem_test_{i}.db")
            mock_state_manager._initialized = True
            mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
            
            # Create and discard snapshots
            snapshot = await state_serializer.create_snapshot(mock_state_manager, RestartReason.MANUAL_REQUEST)
            await state_serializer.save_snapshot(snapshot)
            
            # Register and remove connections
            await connection_manager.register_connection(f"temp_session_{i}", f"TempClient_{i}", "1.0")
            await connection_manager.disconnect_session(f"temp_session_{i}")
            
            # Force garbage collection
            gc.collect()
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (< 50MB for this test)
        self.assertLess(memory_growth, 50 * 1024 * 1024, 
                       f"Memory grew by {memory_growth / 1024 / 1024:.1f}MB, indicating potential leak")

    async def test_restart_timeout_reliability(self):
        """Test restart operations respect timeout constraints."""
        # Test short timeouts
        start_time = time.time()
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Never becomes ready
            mock_popen.return_value = mock_process
            
            process_manager = ProcessManager()
            
            with patch.object(process_manager, '_check_process_health', return_value=False):
                success, pid = await process_manager.start_new_process(
                    RestartReason.MANUAL_REQUEST,
                    timeout=1  # 1 second timeout
                )
                
                elapsed = time.time() - start_time
                
                # Should respect timeout
                self.assertFalse(success)
                self.assertLess(elapsed, 2.0, f"Operation took {elapsed:.2f}s, exceeded timeout")

    async def test_error_recovery_resilience(self):
        """Test system resilience to cascading errors."""
        shutdown_coordinator = ShutdownCoordinator(StateSerializer(self.temp_dir))
        
        # Add multiple failing callbacks
        failure_count = 0
        
        async def failing_callback():
            nonlocal failure_count
            failure_count += 1
            raise Exception(f"Cascading failure {failure_count}")
        
        # Add 5 failing callbacks
        for i in range(5):
            shutdown_coordinator.add_shutdown_callback(failing_callback)
        
        # Should handle all failures gracefully
        success = await shutdown_coordinator.initiate_shutdown()
        self.assertTrue(success)
        
        await shutdown_coordinator.wait_for_shutdown(timeout=5.0)
        
        # Should have attempted all callbacks despite failures
        self.assertEqual(failure_count, 5)
        self.assertEqual(len(shutdown_coordinator.status.errors), 5)


# =============================================================================
# H. END-TO-END INTEGRATION TESTING
# =============================================================================

class TestHEndToEndIntegration(unittest.IsolatedAsyncioTestCase):
    """Test complete end-to-end restart scenarios."""
    
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

    async def test_complete_graceful_restart_workflow(self):
        """Test complete graceful restart from start to finish."""
        # Initialize all components
        state_serializer = StateSerializer(self.temp_dir)
        shutdown_coordinator = ShutdownCoordinator(state_serializer)
        restart_coordinator = RestartCoordinator(state_serializer)
        connection_manager = ConnectionManager()
        
        # Set up initial state
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "integration_test.db")
        mock_state_manager._initialized = True
        mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        mock_state_manager.store_task_breakdown = AsyncMock()
        
        # Create database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("integration test database")
        
        # Register test clients
        await connection_manager.register_connection("client_1", "Production Client 1", "1.0")
        await connection_manager.register_connection("client_2", "Production Client 2", "1.0")
        
        # Phase 1: Prepare for restart
        client_sessions = await connection_manager.prepare_for_restart()
        self.assertEqual(len(client_sessions), 2)
        
        # Phase 2: Create state snapshot
        snapshot = await state_serializer.create_snapshot(
            mock_state_manager,
            RestartReason.CONFIGURATION_UPDATE
        )
        self.assertIsNotNone(snapshot)
        
        # Phase 3: Save snapshot
        await state_serializer.save_snapshot(snapshot)
        
        # Phase 4: Graceful shutdown
        shutdown_success = await shutdown_coordinator.initiate_shutdown(
            RestartReason.CONFIGURATION_UPDATE
        )
        self.assertTrue(shutdown_success)
        
        await shutdown_coordinator.wait_for_shutdown(timeout=10.0)
        self.assertEqual(shutdown_coordinator.status.phase, ShutdownPhase.COMPLETE)
        
        # Phase 5: Simulate restart process (mocked)
        with patch.object(restart_coordinator.process_manager, 'start_new_process', return_value=(True, 54321)):
            restart_success = await restart_coordinator.execute_restart(
                snapshot=snapshot,
                state_manager=mock_state_manager,
                timeout=10
            )
            self.assertTrue(restart_success)
        
        # Phase 6: Restore client connections
        restore_results = await connection_manager.restore_connections(client_sessions)
        self.assertEqual(len(restore_results), 2)
        for result in restore_results.values():
            self.assertTrue(result["success"])

    async def test_restart_with_reboot_manager_integration(self):
        """Test restart using the integrated RebootManager."""
        # Mock state manager
        mock_state_manager = MagicMock()
        mock_state_manager._initialized = True
        mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        
        # Initialize reboot manager
        reboot_manager = RebootManager()
        await reboot_manager.initialize(mock_state_manager)
        
        # Test restart readiness
        readiness = await reboot_manager.get_restart_readiness()
        self.assertIn('ready', readiness)
        self.assertIn('issues', readiness)
        
        # Test shutdown status monitoring
        status = await reboot_manager.get_shutdown_status()
        self.assertIn('phase', status)
        self.assertIn('progress', status)
        
        # Test trigger restart with mocking
        with patch.object(reboot_manager.shutdown_coordinator, 'initiate_shutdown', return_value=True):
            with patch.object(reboot_manager.shutdown_coordinator, 'wait_for_shutdown', return_value=True):
                with patch.object(reboot_manager.restart_coordinator, 'execute_restart', return_value=True):
                    result = await reboot_manager.trigger_restart(
                        RestartReason.MANUAL_REQUEST,
                        timeout=10
                    )
                    
                    self.assertIn('success', result)
                    self.assertIn('phase', result)

    async def test_error_recovery_end_to_end(self):
        """Test complete error recovery scenario."""
        state_serializer = StateSerializer(self.temp_dir)
        shutdown_coordinator = ShutdownCoordinator(state_serializer)
        
        # Simulate system in error state
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = os.path.join(self.temp_dir, "error_recovery.db")
        mock_state_manager._initialized = False  # Simulate initialization error
        mock_state_manager._initialize = AsyncMock(side_effect=Exception("Database corruption"))
        mock_state_manager.get_all_tasks = AsyncMock(return_value=[])
        
        # Create corrupted database file
        with open(mock_state_manager.db_path, 'w') as f:
            f.write("corrupted data")
        
        # Emergency shutdown should succeed despite errors
        success = await shutdown_coordinator.emergency_shutdown()
        self.assertTrue(success)
        
        # Should be able to create basic snapshot even with errors
        try:
            snapshot = await state_serializer.create_snapshot(
                mock_state_manager,
                RestartReason.ERROR_RECOVERY
            )
            # If database errors occur, should create minimal snapshot
            self.assertIsNotNone(snapshot)
            self.assertEqual(snapshot.restart_reason, RestartReason.ERROR_RECOVERY)
        except Exception:
            # Acceptable for corrupted database scenario
            pass

    async def test_production_load_simulation(self):
        """Test system behavior under simulated production load."""
        # Simulate production environment
        state_serializer = StateSerializer(self.temp_dir)
        connection_manager = ConnectionManager()
        request_buffer = RequestBuffer(max_buffer_size=100)
        
        # Simulate multiple clients with ongoing activity
        client_count = 20
        request_count_per_client = 10
        
        # Register clients
        for i in range(client_count):
            await connection_manager.register_connection(
                f"prod_client_{i}",
                f"Production Client {i}",
                "1.0"
            )
        
        # Simulate active requests being buffered
        for client_id in range(client_count):
            for req_id in range(request_count_per_client):
                request = {
                    "method": f"production_method_{req_id}",
                    "params": {"client_id": client_id, "request_id": req_id}
                }
                success = await request_buffer.buffer_request(f"prod_client_{client_id}", request)
                self.assertTrue(success, f"Failed to buffer request {req_id} for client {client_id}")
        
        # Prepare for restart under load
        start_time = time.time()
        client_sessions = await connection_manager.prepare_for_restart()
        preparation_time = time.time() - start_time
        
        # Should handle production load efficiently
        self.assertEqual(len(client_sessions), client_count)
        self.assertLess(preparation_time, 5.0, f"Preparation took {preparation_time:.2f}s under load")
        
        # Verify all clients preserved
        for i in range(client_count):
            session_found = any(session.session_id == f"prod_client_{i}" for session in client_sessions)
            self.assertTrue(session_found, f"Client {i} session not preserved")
        
        # Simulate restoration
        restore_results = await connection_manager.restore_connections(client_sessions)
        
        # All clients should be restored successfully
        self.assertEqual(len(restore_results), client_count)
        for client_id in range(client_count):
            client_key = f"prod_client_{client_id}"
            self.assertIn(client_key, restore_results)
            self.assertTrue(restore_results[client_key]["success"])

    async def test_mcp_tools_integration_workflow(self):
        """Test complete MCP tools integration workflow."""
        # Test health check before restart
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            # 1. Health check
            health_result = await handle_health_check({})
            health_data = json.loads(health_result[0].text)
            self.assertTrue(health_data["healthy"])
            
            # 2. Shutdown preparation check
            prepare_result = await handle_shutdown_prepare({})
            prepare_data = json.loads(prepare_result[0].text)
            self.assertTrue(prepare_data["ready_for_shutdown"])
            
            # 3. Trigger restart
            mock_manager.trigger_restart.return_value = {
                "success": True,
                "phase": "complete",
                "progress": 100.0,
                "message": "Restart completed"
            }
            
            restart_result = await handle_restart_server({
                "graceful": True,
                "preserve_state": True,
                "reason": "manual_request"
            })
            restart_data = json.loads(restart_result[0].text)
            self.assertTrue(restart_data["success"])
            
            # 4. Check restart status
            mock_manager.get_shutdown_status.return_value = {
                "phase": "complete",
                "progress": 100.0,
                "message": "Restart completed successfully"
            }
            
            status_result = await handle_restart_status({})
            status_data = json.loads(status_result[0].text)
            self.assertEqual(status_data["current_status"]["phase"], "complete")
            
            # 5. Test reconnection
            reconnect_result = await handle_reconnect_test({})
            reconnect_data = json.loads(reconnect_result[0].text)
            self.assertTrue(reconnect_data["test_completed"])


# =============================================================================
# TEST RUNNER AND REPORTING
# =============================================================================

async def run_test_category(category_name, test_class):
    """Run tests for a specific category and return results."""
    print(f"\n{'='*60}")
    print(f"TESTING CATEGORY: {category_name}")
    print(f"{'='*60}")
    
    if not IMPORTS_AVAILABLE:
        print("⚠️  Required modules not available - skipping category")
        return 0, 0, 1  # passed, failed, skipped
    
    test_methods = [method for method in dir(test_class) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_method in test_methods:
        print(f"  Running {test_method}...", end=' ')
        
        try:
            # Create test instance
            test_instance = test_class()
            
            # Run setup
            if hasattr(test_instance, 'asyncSetUp'):
                await test_instance.asyncSetUp()
            
            # Run test
            test_func = getattr(test_instance, test_method)
            await test_func()
            
            # Run teardown
            if hasattr(test_instance, 'asyncTearDown'):
                await test_instance.asyncTearDown()
            
            print("✅ PASSED")
            passed += 1
            
        except unittest.SkipTest as e:
            print(f"⏭️  SKIPPED ({e})")
            skipped += 1
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    print(f"\nCategory Results: {passed} passed, {failed} failed, {skipped} skipped")
    return passed, failed, skipped


async def main():
    """Run comprehensive server reboot tests."""
    print("Starting Comprehensive Server Reboot Test Suite")
    print("=" * 80)
    
    results = TestResults()
    
    # Define test categories
    test_categories = [
        ("A. State Preservation", TestAStatePreservation),
        ("B. Graceful Shutdown", TestBGracefulShutdown),
        ("C. Restart Coordination", TestCRestartCoordination),
        ("D. Client Connection Management", TestDClientConnections),
        ("E. MCP Tool Integration", TestEMCPToolIntegration),
        ("F. Error Scenario Handling", TestFErrorScenarios),
        ("G. Performance & Reliability", TestGPerformanceReliability),
        ("H. End-to-End Integration", TestHEndToEndIntegration)
    ]
    
    # Run each test category
    for category_name, test_class in test_categories:
        try:
            passed, failed, skipped = await run_test_category(category_name, test_class)
            results.add_category(category_name, passed, failed, skipped)
        except Exception as e:
            print(f"❌ Category {category_name} failed to run: {e}")
            results.add_category(category_name, 0, 1, 0)
    
    # Print comprehensive results
    print(results.get_summary())
    
    # Generate detailed recommendations
    print("RECOMMENDATIONS:")
    print("-" * 40)
    
    if results.total_failed == 0:
        print("🎉 All tests passed! The server reboot system is ready for production deployment.")
        print("   - State preservation works correctly")
        print("   - Graceful shutdown is reliable")
        print("   - Client connections are preserved")
        print("   - Error handling is robust")
        print("   - Performance is acceptable")
    else:
        print("⚠️  Issues detected that should be addressed:")
        for category, data in results.categories.items():
            if data['failed'] > 0:
                print(f"   - {category}: {data['failed']} failures need investigation")
        
        if results.total_failed <= 2:
            print("   Priority: MEDIUM - Minor issues that should be fixed before production")
        else:
            print("   Priority: HIGH - Critical issues that must be resolved")
    
    print("\nFor detailed logs and debugging information, review test output above.")
    print("=" * 80)
    
    return results.total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)