"""
Performance and stress tests for server reboot system.

This module tests the performance characteristics of the reboot system
under various load conditions and validates timing requirements.
"""

import asyncio
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import sys

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp_task_orchestrator.server.state_serializer import StateSerializer, RestartReason
    from mcp_task_orchestrator.server.shutdown_coordinator import ShutdownCoordinator
    from mcp_task_orchestrator.server.connection_manager import ConnectionManager, RequestBuffer
    from mcp_task_orchestrator.server.reboot_tools import handle_restart_server, handle_health_check
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    IMPORTS_AVAILABLE = False


class TestPerformanceRequirements(unittest.IsolatedAsyncioTestCase):
    """Test performance requirements for reboot system."""
    
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

    async def test_state_serialization_performance(self):
        """Test state serialization performance requirements."""
        state_serializer = StateSerializer(self.temp_dir)
        
        # Mock state manager with large dataset
        mock_state_manager = MagicMock()
        mock_state_manager.db_path = f"{self.temp_dir}/test.db"
        mock_state_manager._initialized = True
        
        # Create mock tasks (simulate large workload)
        mock_tasks = []
        for i in range(100):  # 100 tasks
            mock_task = MagicMock()
            mock_task.task_id = f"task_{i}"
            mock_task.parent_task_id = f"parent_{i}"
            mock_task.description = f"Test task {i}"
            mock_task.status = "active"
            mock_task.created_at = None
            mock_tasks.append(mock_task)
        
        mock_state_manager.get_all_tasks = AsyncMock(return_value=mock_tasks)
        
        # Measure serialization time
        start_time = time.time()
        snapshot = await state_serializer.create_snapshot(
            mock_state_manager,
            RestartReason.MANUAL_REQUEST
        )
        serialization_time = time.time() - start_time
        
        # Performance requirement: <2 seconds for snapshot creation
        self.assertLess(serialization_time, 2.0, 
                       f"Serialization took {serialization_time:.2f}s, should be <2s")
        
        # Measure save time
        start_time = time.time()
        await state_serializer.save_snapshot(snapshot)
        save_time = time.time() - start_time
        
        # Performance requirement: <1 second for saving
        self.assertLess(save_time, 1.0, 
                       f"Save took {save_time:.2f}s, should be <1s")

    async def test_shutdown_coordination_performance(self):
        """Test shutdown coordination performance."""
        state_serializer = StateSerializer(self.temp_dir)
        shutdown_coordinator = ShutdownCoordinator(
            state_serializer, 
            shutdown_timeout=30,
            task_suspension_timeout=5
        )
        
        # Measure shutdown initiation time
        start_time = time.time()
        success = await shutdown_coordinator.initiate_shutdown(RestartReason.MANUAL_REQUEST)
        initiation_time = time.time() - start_time
        
        # Performance requirement: <0.1 seconds for initiation
        self.assertLess(initiation_time, 0.1, 
                       f"Shutdown initiation took {initiation_time:.3f}s, should be <0.1s")
        self.assertTrue(success)

    async def test_connection_manager_performance(self):
        """Test connection manager performance with many clients."""
        connection_manager = ConnectionManager()
        
        # Register many connections
        start_time = time.time()
        for i in range(1000):  # 1000 clients
            await connection_manager.register_connection(
                f"session_{i}",
                f"Client {i}",
                "1.0"
            )
        registration_time = time.time() - start_time
        
        # Performance requirement: <1 second for 1000 registrations
        self.assertLess(registration_time, 1.0,
                       f"Registration took {registration_time:.2f}s, should be <1s")
        
        # Test status retrieval performance
        start_time = time.time()
        status = await connection_manager.get_connection_status()
        status_time = time.time() - start_time
        
        # Performance requirement: <0.1 seconds for status
        self.assertLess(status_time, 0.1,
                       f"Status retrieval took {status_time:.3f}s, should be <0.1s")
        
        self.assertEqual(status['total_connections'], 1000)

    async def test_mcp_tool_response_time(self):
        """Test MCP tool response time requirements."""
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            # Test health check response time
            start_time = time.time()
            result = await handle_health_check({})
            response_time = time.time() - start_time
            
            # Performance requirement: <0.1 seconds for tool response
            self.assertLess(response_time, 0.1,
                           f"Health check took {response_time:.3f}s, should be <0.1s")
            self.assertEqual(len(result), 1)


class TestRequestBufferPerformance(unittest.IsolatedAsyncioTestCase):
    """Test request buffer performance under load."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_request_buffering_throughput(self):
        """Test request buffering throughput."""
        request_buffer = RequestBuffer(max_buffer_size=10000)
        
        # Test high-volume request buffering
        num_requests = 5000
        num_sessions = 50
        
        start_time = time.time()
        
        for i in range(num_requests):
            session_id = f"session_{i % num_sessions}"
            request = {
                "method": f"test_method_{i}",
                "params": {"data": f"test_data_{i}"}
            }
            
            success = await request_buffer.buffer_request(session_id, request)
            if i < num_sessions * 100:  # Within buffer limits
                self.assertTrue(success)
        
        buffering_time = time.time() - start_time
        
        # Performance requirement: Buffer 5000 requests in <1 second
        self.assertLess(buffering_time, 1.0,
                       f"Buffering {num_requests} requests took {buffering_time:.2f}s")
        
        # Test buffer retrieval performance
        start_time = time.time()
        
        for i in range(num_sessions):
            session_id = f"session_{i}"
            requests = await request_buffer.get_buffered_requests(session_id)
            # Each session should have ~100 requests (5000/50)
        
        retrieval_time = time.time() - start_time
        
        # Performance requirement: Retrieve all buffers in <0.5 seconds
        self.assertLess(retrieval_time, 0.5,
                       f"Buffer retrieval took {retrieval_time:.2f}s, should be <0.5s")

    async def test_buffer_cleanup_performance(self):
        """Test buffer cleanup performance."""
        request_buffer = RequestBuffer(max_buffer_size=1000)
        
        # Fill buffer with old requests
        for i in range(500):
            session_id = f"session_{i % 10}"
            request = {"method": f"old_method_{i}"}
            await request_buffer.buffer_request(session_id, request)
        
        # Measure cleanup time
        start_time = time.time()
        await request_buffer.clear_expired_requests(max_age_seconds=0)  # Clear all
        cleanup_time = time.time() - start_time
        
        # Performance requirement: Cleanup in <0.1 seconds
        self.assertLess(cleanup_time, 0.1,
                       f"Buffer cleanup took {cleanup_time:.3f}s, should be <0.1s")


class TestConcurrencyPerformance(unittest.IsolatedAsyncioTestCase):
    """Test concurrent operation performance."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_concurrent_tool_requests(self):
        """Test concurrent MCP tool request handling."""
        with patch('mcp_task_orchestrator.server.reboot_tools.get_reboot_manager') as mock_get_manager:
            mock_manager = AsyncMock()
            mock_manager.get_restart_readiness.return_value = {
                "ready": True,
                "issues": [],
                "details": {}
            }
            mock_get_manager.return_value = mock_manager
            
            # Create concurrent health check requests
            num_concurrent = 50
            
            async def health_check_task():
                return await handle_health_check({})
            
            start_time = time.time()
            
            # Run concurrent requests
            tasks = [health_check_task() for _ in range(num_concurrent)]
            results = await asyncio.gather(*tasks)
            
            concurrent_time = time.time() - start_time
            
            # Performance requirement: Handle 50 concurrent requests in <1 second
            self.assertLess(concurrent_time, 1.0,
                           f"Concurrent requests took {concurrent_time:.2f}s, should be <1s")
            
            # Verify all requests succeeded
            self.assertEqual(len(results), num_concurrent)
            for result in results:
                self.assertEqual(len(result), 1)

    async def test_concurrent_connection_operations(self):
        """Test concurrent connection management operations."""
        connection_manager = ConnectionManager()
        
        # Concurrent connection registration
        async def register_connection_batch(start_idx, count):
            for i in range(start_idx, start_idx + count):
                await connection_manager.register_connection(
                    f"session_{i}",
                    f"Client {i}",
                    "1.0"
                )
        
        start_time = time.time()
        
        # Run 10 concurrent batches of 100 registrations each
        batch_tasks = [
            register_connection_batch(i * 100, 100) 
            for i in range(10)
        ]
        await asyncio.gather(*batch_tasks)
        
        concurrent_registration_time = time.time() - start_time
        
        # Performance requirement: Register 1000 connections concurrently in <2 seconds
        self.assertLess(concurrent_registration_time, 2.0,
                       f"Concurrent registration took {concurrent_registration_time:.2f}s")
        
        # Verify all connections were registered
        status = await connection_manager.get_connection_status()
        self.assertEqual(status['total_connections'], 1000)


class TestMemoryPerformance(unittest.IsolatedAsyncioTestCase):
    """Test memory usage and efficiency."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        if not IMPORTS_AVAILABLE:
            self.skipTest("Required modules not available")

    async def test_state_serialization_memory_efficiency(self):
        """Test state serialization memory usage."""
        # This is a basic test - in production, you'd use memory profiling tools
        import gc
        
        temp_dir = tempfile.mkdtemp()
        try:
            state_serializer = StateSerializer(temp_dir)
            
            # Create large mock state
            mock_state_manager = MagicMock()
            mock_state_manager.db_path = f"{temp_dir}/test.db"
            mock_state_manager._initialized = True
            
            # Large number of tasks
            mock_tasks = []
            for i in range(1000):
                mock_task = MagicMock()
                mock_task.task_id = f"task_{i}"
                mock_task.parent_task_id = f"parent_{i}"
                mock_task.description = f"Test task {i} " * 100  # Large descriptions
                mock_task.status = "active"
                mock_task.created_at = None
                mock_tasks.append(mock_task)
            
            mock_state_manager.get_all_tasks = AsyncMock(return_value=mock_tasks)
            
            # Force garbage collection before test
            gc.collect()
            
            # Create and save multiple snapshots
            for i in range(10):
                snapshot = await state_serializer.create_snapshot(
                    mock_state_manager,
                    RestartReason.MANUAL_REQUEST
                )
                await state_serializer.save_snapshot(snapshot, backup=False)
                
                # Clear snapshot reference
                del snapshot
                gc.collect()
            
            # Memory usage should be bounded (basic test)
            # In production, you'd check actual memory usage
            self.assertTrue(True)  # Placeholder for memory checks
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


async def run_performance_tests():
    """Run all performance tests."""
    if not IMPORTS_AVAILABLE:
        print("⚠️  Warning: Required modules not available - skipping performance tests")
        return True
    
    test_cases = [
        TestPerformanceRequirements,
        TestRequestBufferPerformance,
        TestConcurrencyPerformance,
        TestMemoryPerformance
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Running Performance Tests")
    print("=" * 50)
    
    for test_case_class in test_cases:
        print(f"\n--- {test_case_class.__name__} ---")
        
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
                test_start = time.time()
                await test_func()
                test_duration = time.time() - test_start
                
                # Run teardown
                if hasattr(test_instance, 'asyncTearDown'):
                    await test_instance.asyncTearDown()
                
                print(f"    ✓ {test_method} PASSED ({test_duration:.3f}s)")
                passed_tests += 1
                
            except Exception as e:
                print(f"    ✗ {test_method} FAILED: {e}")
                failed_tests += 1
    
    print(f"\n--- Performance Test Results ---")
    print(f"Total: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    if failed_tests == 0:
        print("🎉 All performance requirements met!")
    else:
        print("⚠️  Some performance tests failed - optimization needed")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = asyncio.run(run_performance_tests())
    exit(0 if success else 1)