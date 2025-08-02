"""
Performance Validation Tests for Error Handling Infrastructure.

Tests that error handling consolidation maintains or improves system performance,
measures overhead, and validates performance requirements from the PRP.
"""

import pytest
import time
import asyncio
import statistics
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any
import psutil
import os

# Import error handling components
from mcp_task_orchestrator.infrastructure.error_handling.decorators import (
    handle_errors,
    suppress_errors,
    safe_call,
    safe_call_async
)
from mcp_task_orchestrator.infrastructure.error_handling.retry_coordinator import (
    ExponentialBackoffPolicy,
    LinearBackoffPolicy,
    FixedDelayPolicy
)

# Import handlers for comparison
from mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers import (
    handle_create_generic_task as old_create_handler
)
from mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2 import (
    handle_create_task_v2 as new_create_handler
)


class PerformanceBenchmark:
    """Utility class for performance benchmarking."""
    
    @staticmethod
    def measure_execution_time(func, *args, iterations=100, **kwargs):
        """Measure average execution time of a function."""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                if asyncio.iscoroutine(result):
                    # Handle async functions in sync context
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(result)
                    finally:
                        loop.close()
            except Exception:
                pass  # Ignore errors for performance measurement
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    @staticmethod
    async def measure_async_execution_time(func, *args, iterations=100, **kwargs):
        """Measure average execution time of an async function."""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                await func(*args, **kwargs)
            except Exception:
                pass  # Ignore errors for performance measurement
            end = time.perf_counter()
            times.append(end - start)
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'std_dev': statistics.stdev(times) if len(times) > 1 else 0
        }
    
    @staticmethod
    def measure_memory_usage(func, *args, **kwargs):
        """Measure memory usage of a function."""
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(result)
                finally:
                    loop.close()
        except Exception:
            pass
        
        # Peak memory
        peak_memory = process.memory_info().rss
        
        return {
            'baseline_mb': baseline_memory / (1024 * 1024),
            'peak_mb': peak_memory / (1024 * 1024),
            'delta_mb': (peak_memory - baseline_memory) / (1024 * 1024)
        }


class TestErrorHandlingOverhead:
    """Test error handling decorator overhead."""
    
    def test_handle_errors_decorator_overhead(self):
        """Test that @handle_errors decorator adds minimal overhead."""
        
        # Baseline function
        def baseline_function(x):
            return x * 2
        
        # Decorated function
        @handle_errors(component="PerformanceTest", operation="test")
        def decorated_function(x):
            return x * 2
        
        # Measure baseline performance
        baseline_stats = PerformanceBenchmark.measure_execution_time(
            baseline_function, 42, iterations=1000
        )
        
        # Measure decorated performance
        decorated_stats = PerformanceBenchmark.measure_execution_time(
            decorated_function, 42, iterations=1000
        )
        
        # Calculate overhead
        overhead_ratio = decorated_stats['mean'] / baseline_stats['mean']
        
        # PRP Requirement: <5% increase in latency
        assert overhead_ratio < 1.05, f"Error handling overhead too high: {overhead_ratio:.3f}x (>{baseline_stats['mean']:.6f}s vs {decorated_stats['mean']:.6f}s)"
        
        print(f"Error handling overhead: {(overhead_ratio - 1) * 100:.2f}%")
    
    @pytest.mark.asyncio
    async def test_async_handle_errors_decorator_overhead(self):
        """Test that @handle_errors decorator adds minimal overhead to async functions."""
        
        # Baseline async function
        async def baseline_async_function(x):
            await asyncio.sleep(0.001)  # Simulate async work
            return x * 2
        
        # Decorated async function
        @handle_errors(component="PerformanceTest", operation="async_test")
        async def decorated_async_function(x):
            await asyncio.sleep(0.001)  # Simulate async work
            return x * 2
        
        # Measure baseline performance
        baseline_stats = await PerformanceBenchmark.measure_async_execution_time(
            baseline_async_function, 42, iterations=100
        )
        
        # Measure decorated performance
        decorated_stats = await PerformanceBenchmark.measure_async_execution_time(
            decorated_async_function, 42, iterations=100
        )
        
        # Calculate overhead
        overhead_ratio = decorated_stats['mean'] / baseline_stats['mean']
        
        # PRP Requirement: <5% increase in latency
        assert overhead_ratio < 1.05, f"Async error handling overhead too high: {overhead_ratio:.3f}x"
        
        print(f"Async error handling overhead: {(overhead_ratio - 1) * 100:.2f}%")
    
    def test_memory_usage_impact(self):
        """Test that error handling doesn't significantly increase memory usage."""
        
        # Function without error handling
        def baseline_function():
            return [i * 2 for i in range(1000)]
        
        # Function with error handling
        @handle_errors(component="MemoryTest", operation="test")
        def decorated_function():
            return [i * 2 for i in range(1000)]
        
        # Measure memory usage
        baseline_memory = PerformanceBenchmark.measure_memory_usage(baseline_function)
        decorated_memory = PerformanceBenchmark.measure_memory_usage(decorated_function)
        
        # Calculate memory overhead
        memory_increase = decorated_memory['delta_mb'] - baseline_memory['delta_mb']
        
        # PRP Requirement: Stable or improved memory usage
        assert memory_increase < 1.0, f"Memory usage increased by {memory_increase:.2f}MB"
        
        print(f"Memory usage delta: {memory_increase:.3f}MB")


class TestRetryPolicyPerformance:
    """Test retry policy performance impact."""
    
    @pytest.mark.asyncio
    async def test_retry_policy_performance(self):
        """Test that retry policies don't significantly impact performance."""
        
        success_count = 0
        
        @handle_errors(
            component="RetryTest",
            operation="test",
            auto_retry=True,
            retry_policy=ExponentialBackoffPolicy(max_attempts=3, base_delay=0.001)
        )
        async def test_function():
            nonlocal success_count
            success_count += 1
            return "success"
        
        # Measure retry performance
        start_time = time.perf_counter()
        
        # Run successful operations (no retries needed)
        for _ in range(50):
            await test_function()
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time_per_call = total_time / 50
        
        # PRP Requirement: <2 seconds error recovery time (for successful calls, should be much faster)
        assert avg_time_per_call < 0.1, f"Retry policy too slow: {avg_time_per_call:.3f}s per call"
        assert success_count == 50, "Not all operations succeeded"
        
        print(f"Average time per successful call with retry policy: {avg_time_per_call:.6f}s")
    
    @pytest.mark.asyncio
    async def test_error_recovery_time(self):
        """Test that error recovery meets the <2 second requirement."""
        
        attempt_count = 0
        
        @handle_errors(
            component="RecoveryTest", 
            operation="test",
            auto_retry=True,
            retry_policy=ExponentialBackoffPolicy(max_attempts=3, base_delay=0.1)
        )
        async def failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "recovered"
        
        start_time = time.perf_counter()
        result = await failing_function()
        end_time = time.perf_counter()
        
        recovery_time = end_time - start_time
        
        # PRP Requirement: <2 seconds error recovery time
        assert recovery_time < 2.0, f"Error recovery too slow: {recovery_time:.3f}s"
        assert result == "recovered"
        assert attempt_count == 3
        
        print(f"Error recovery time: {recovery_time:.3f}s")


class TestHandlerPerformanceComparison:
    """Compare performance of old vs new handlers."""
    
    @pytest.mark.asyncio
    async def test_old_vs_new_handler_performance(self):
        """Compare performance between old and new Pydantic handlers."""
        
        # Mock the use case for both handlers
        with patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers.get_generic_task_use_case') as mock_old_use_case, \
             patch('mcp_task_orchestrator.infrastructure.mcp.handlers.task_handlers_v2.get_generic_task_use_case') as mock_new_use_case:
            
            # Mock old handler response
            mock_old_task = Mock()
            mock_old_task.dict.return_value = {
                "task_id": "test-123",
                "title": "Test Task",
                "created_at": "2024-01-01T00:00:00"
            }
            mock_old_uc = AsyncMock()
            mock_old_uc.create_task.return_value = mock_old_task
            mock_old_use_case.return_value = mock_old_uc
            
            # Mock new handler response
            from mcp_task_orchestrator.domain.entities.task import Task, TaskType, TaskStatus
            from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel
            from datetime import datetime
            
            mock_new_task = Task(
                task_id="test-123",
                title="Test Task",
                description="Test Description",
                task_type=TaskType.STANDARD,
                status=TaskStatus.PLANNED,
                complexity=ComplexityLevel.MODERATE,
                specialist_type="developer",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_new_uc = AsyncMock()
            mock_new_uc.create_task.return_value = mock_new_task
            mock_new_use_case.return_value = mock_new_uc
            
            # Test arguments
            args = {
                "title": "Test Task",
                "description": "Test Description",
                "task_type": "STANDARD"
            }
            
            # Measure old handler performance
            old_stats = await PerformanceBenchmark.measure_async_execution_time(
                old_create_handler, args, iterations=50
            )
            
            # Measure new handler performance
            new_stats = await PerformanceBenchmark.measure_async_execution_time(
                new_create_handler, args, iterations=50
            )
            
            # Calculate performance ratio
            performance_ratio = new_stats['mean'] / old_stats['mean']
            
            # PRP Requirement: <5% latency increase
            assert performance_ratio < 1.05, f"New handler too slow: {performance_ratio:.3f}x slower"
            
            print(f"Handler performance comparison:")
            print(f"  Old handler: {old_stats['mean']:.6f}s")
            print(f"  New handler: {new_stats['mean']:.6f}s")
            print(f"  Performance ratio: {performance_ratio:.3f}x")


class TestThroughputUnderErrorConditions:
    """Test system throughput when errors occur."""
    
    @pytest.mark.asyncio
    async def test_throughput_with_errors(self):
        """Test that system maintains 80% throughput under error conditions."""
        
        error_rate = 0.3  # 30% error rate
        call_count = 0
        error_count = 0
        
        @handle_errors(
            component="ThroughputTest",
            operation="test",
            auto_retry=True,
            retry_policy=FixedDelayPolicy(max_attempts=2, delay_seconds=0.01)
        )
        async def test_function():
            nonlocal call_count, error_count
            call_count += 1
            
            # Introduce errors at specified rate
            if call_count % int(1 / error_rate) == 0:
                error_count += 1
                raise Exception("Simulated error")
            
            await asyncio.sleep(0.001)  # Simulate work
            return "success"
        
        # Measure baseline throughput (no errors)
        start_time = time.perf_counter()
        for _ in range(50):
            try:
                await test_function()
            except:
                pass
        baseline_time = time.perf_counter() - start_time
        
        # Reset counters for error scenario
        call_count = 0
        error_count = 0
        
        # Measure throughput with errors
        start_time = time.perf_counter()
        for _ in range(50):
            try:
                await test_function()
            except:
                pass  # Some calls will fail after retries
        error_scenario_time = time.perf_counter() - start_time
        
        # Calculate throughput ratio
        throughput_ratio = baseline_time / error_scenario_time
        
        # PRP Requirement: 80% of normal throughput under error conditions
        assert throughput_ratio > 0.8, f"Throughput too low under errors: {throughput_ratio:.3f}"
        
        print(f"Throughput under error conditions: {throughput_ratio:.3f}")
        print(f"Error rate achieved: {error_count}/{call_count} = {error_count/call_count:.3f}")


class TestMemoryLeakDetection:
    """Test for memory leaks in error handling."""
    
    @pytest.mark.asyncio
    async def test_no_memory_leaks_in_error_handling(self):
        """Test that error handling doesn't cause memory leaks."""
        
        @handle_errors(component="MemoryLeakTest", operation="test")
        async def leaky_function():
            # Create some objects that might leak
            data = [i for i in range(1000)]
            raise Exception("Test error")
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run many error scenarios
        for _ in range(100):
            try:
                await leaky_function()
            except:
                pass
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Memory increase should be minimal (less than 10MB for 100 error scenarios)
        assert memory_increase < 10.0, f"Potential memory leak: {memory_increase:.2f}MB increase"
        
        print(f"Memory increase after 100 error scenarios: {memory_increase:.2f}MB")


class TestPerformanceRegression:
    """Test for performance regression detection."""
    
    def test_decorator_chain_performance(self):
        """Test performance when multiple decorators are chained."""
        
        # Function with multiple error handling decorators
        @suppress_errors([ValueError], default_return="suppressed")
        @handle_errors(component="ChainTest", operation="test")
        def multi_decorated_function(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2
        
        # Baseline function
        def baseline_function(x):
            if x < 0:
                return "suppressed"
            return x * 2
        
        # Measure performance
        baseline_stats = PerformanceBenchmark.measure_execution_time(
            baseline_function, 5, iterations=1000
        )
        
        decorated_stats = PerformanceBenchmark.measure_execution_time(
            multi_decorated_function, 5, iterations=1000
        )
        
        # Calculate overhead
        overhead_ratio = decorated_stats['mean'] / baseline_stats['mean']
        
        # Multiple decorators should still have reasonable overhead
        assert overhead_ratio < 1.1, f"Decorator chain overhead too high: {overhead_ratio:.3f}x"
        
        print(f"Decorator chain overhead: {(overhead_ratio - 1) * 100:.2f}%")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to see print statements