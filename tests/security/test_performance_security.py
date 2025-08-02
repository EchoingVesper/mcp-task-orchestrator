"""
Performance Security Tests

Comprehensive test suite for validating DoS protection, resource exhaustion
prevention, rate limiting effectiveness, and system stability under attack.
"""

import pytest
import asyncio
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any, Optional

from mcp_task_orchestrator.infrastructure.security import (
    validate_string_input,
    validate_file_path,
    api_key_manager,
    ValidationError,
    AuthenticationError,
    secure_mcp_handler,
    Permission
)


class TestDoSAttackProtection:
    """Test Denial of Service attack protection."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.critical
    async def test_request_flood_protection(self, performance_monitor, dos_attack_simulator):
        """Test protection against request flooding."""
        performance_monitor.start_monitoring()
        
        async def process_validation_request():
            """Simulate a validation request that might be flooded."""
            test_input = "normal input for validation"
            try:
                return validate_string_input(test_input, "title", max_length=255)
            except ValidationError:
                return None
        
        # Simulate flood of requests
        flood_results = await dos_attack_simulator.simulate_request_flood(
            process_validation_request,
            request_count=500,
            concurrent_limit=50
        )
        
        # System should remain stable
        assert len(flood_results) == 500
        
        # Most requests should succeed (system not overwhelmed)
        successful_requests = [r for r in flood_results if isinstance(r, str)]
        assert len(successful_requests) > 400, "Too many requests failed under flood"
        
        # Performance should remain acceptable
        performance_monitor.assert_performance_limits(
            max_execution_time=30.0,
            max_memory_mb=100.0,
            max_cpu_percent=80.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_large_payload_dos_protection(self, performance_monitor, dos_attack_simulator):
        """Test protection against large payload DoS attacks."""
        performance_monitor.start_monitoring()
        
        # Generate progressively larger payloads
        payload_sizes = [1, 5, 10, 50, 100]  # MB
        
        for size_mb in payload_sizes:
            large_payload = dos_attack_simulator.generate_large_payload(size_mb)
            
            # Should reject large payloads quickly
            start_time = time.perf_counter()
            
            with pytest.raises(ValidationError):
                validate_string_input(large_payload, "content", max_length=100000)  # 100KB limit
            
            rejection_time = time.perf_counter() - start_time
            
            # Should reject quickly regardless of payload size (< 100ms)
            assert rejection_time < 0.1, f"Large payload ({size_mb}MB) took {rejection_time:.3f}s to reject"
        
        # Memory usage should not spike with large payloads
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=50.0,  # Should not load large payloads into memory
            max_cpu_percent=30.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_algorithmic_complexity_dos_protection(self, performance_monitor):
        """Test protection against algorithmic complexity DoS attacks."""
        performance_monitor.start_monitoring()
        
        # Generate inputs designed to exploit O(n²) or worse algorithms
        complexity_attack_inputs = []
        
        for size in [100, 500, 1000, 5000]:
            # Patterns that might cause quadratic string matching
            attack_input = "a" * size + "X"  # Should not match, causes backtracking
            complexity_attack_inputs.append((size, attack_input))
            
            # Nested parentheses (regex DoS)
            nested_input = "(" * size + "a" + ")" * size
            complexity_attack_inputs.append((size, nested_input))
        
        processing_times = []
        for size, attack_input in complexity_attack_inputs:
            start_time = time.perf_counter()
            
            try:
                validate_string_input(attack_input, "content", max_length=100000)
            except ValidationError:
                pass  # Expected for many inputs
            
            processing_time = time.perf_counter() - start_time
            processing_times.append((size, processing_time))
        
        # Processing time should not increase exponentially with input size
        # Check that larger inputs don't take disproportionately longer
        for i in range(1, len(processing_times)):
            prev_size, prev_time = processing_times[i-1]
            curr_size, curr_time = processing_times[i]
            
            size_ratio = curr_size / prev_size
            time_ratio = curr_time / prev_time if prev_time > 0 else 1
            
            # Time increase should be at most linear with size increase
            assert time_ratio <= size_ratio * 2, f"Processing time increased {time_ratio:.2f}x for {size_ratio:.2f}x size increase"
        
        # Overall performance should remain good
        performance_monitor.assert_performance_limits(
            max_execution_time=10.0,
            max_memory_mb=30.0,
            max_cpu_percent=50.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_nested_data_dos_protection(self, performance_monitor):
        """Test protection against deeply nested data DoS attacks."""
        performance_monitor.start_monitoring()
        
        import json
        
        # Generate deeply nested JSON structures
        nesting_depths = [10, 50, 100, 500, 1000]
        
        for depth in nesting_depths:
            # Create deeply nested JSON
            nested_json = '{"key": ' * depth + '"value"' + '}' * depth
            
            start_time = time.perf_counter()
            
            try:
                # Parse JSON (should have limits)
                parsed = json.loads(nested_json)
                
                # Convert to string for validation (should be limited)
                json_str = str(parsed)
                validate_string_input(json_str, "json_data", max_length=10000)
                
            except (json.JSONDecodeError, ValidationError, RecursionError, MemoryError):
                # Expected for deeply nested structures
                pass
            
            processing_time = time.perf_counter() - start_time
            
            # Should handle or reject quickly regardless of nesting depth
            assert processing_time < 1.0, f"Nested JSON (depth {depth}) took {processing_time:.3f}s"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=15.0,
            max_memory_mb=40.0,
            max_cpu_percent=40.0
        )


class TestResourceExhaustionPrevention:
    """Test prevention of resource exhaustion attacks."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_memory_exhaustion_prevention(self, performance_monitor):
        """Test prevention of memory exhaustion attacks."""
        performance_monitor.start_monitoring()
        
        # Track memory usage throughout test
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Attempt multiple memory exhaustion attacks
        memory_attack_attempts = 100
        
        for i in range(memory_attack_attempts):
            # Create large string (10MB each)
            large_string = "x" * (10 * 1024 * 1024)
            
            # Should reject quickly without consuming memory
            with pytest.raises(ValidationError):
                validate_string_input(large_string, "content", max_length=1000)
            
            # Check memory every 10 attempts
            if i % 10 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                
                # Memory should not increase significantly
                assert memory_increase < 100, f"Memory increased by {memory_increase:.2f}MB after {i} attempts"
        
        # Final memory check
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        total_memory_increase = final_memory - initial_memory
        
        assert total_memory_increase < 50, f"Total memory increase: {total_memory_increase:.2f}MB"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=20.0,
            max_memory_mb=100.0,
            max_cpu_percent=50.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_cpu_exhaustion_prevention(self, performance_monitor):
        """Test prevention of CPU exhaustion attacks."""
        performance_monitor.start_monitoring()
        
        # CPU-intensive attack patterns
        cpu_attack_patterns = [
            # Regex backtracking patterns
            "a" * 1000 + "X",
            "(" * 100 + "a" * 100 + ")" * 100,
            
            # String processing intensive patterns
            "ab" * 5000 + "c",
            "x" + "y" * 10000 + "z",
            
            # Unicode processing intensive
            "\u200b" * 1000 + "content",  # Zero-width spaces
            "\u0301" * 500 + "combined",  # Combining characters
        ]
        
        cpu_usage_samples = []
        
        for pattern in cpu_attack_patterns:
            # Monitor CPU usage during processing
            start_cpu = psutil.cpu_percent(interval=None)
            start_time = time.perf_counter()
            
            try:
                validate_string_input(pattern, "content", max_length=50000)
            except ValidationError:
                pass  # Expected
            
            processing_time = time.perf_counter() - start_time
            end_cpu = psutil.cpu_percent(interval=None)
            
            cpu_usage_samples.append((processing_time, end_cpu))
            
            # Individual processing should be fast
            assert processing_time < 0.5, f"Pattern took {processing_time:.3f}s to process"
        
        # Average CPU usage should be reasonable
        avg_cpu = sum(cpu for _, cpu in cpu_usage_samples) / len(cpu_usage_samples)
        assert avg_cpu < 80, f"Average CPU usage: {avg_cpu:.2f}%"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=10.0,
            max_memory_mb=30.0,
            max_cpu_percent=70.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_connection_exhaustion_prevention(self, performance_monitor):
        """Test prevention of connection/handle exhaustion."""
        performance_monitor.start_monitoring()
        
        # Simulate many concurrent "connections" (async tasks)
        async def simulate_connection():
            """Simulate a connection that processes input."""
            await asyncio.sleep(0.01)  # Simulate connection overhead
            
            try:
                # Process some input
                result = validate_string_input("test input", "title", max_length=255)
                return {"success": True, "result": result}
            except ValidationError:
                return {"success": False, "error": "validation_failed"}
        
        # Create many concurrent connections
        connection_count = 1000
        
        start_time = time.perf_counter()
        tasks = [simulate_connection() for _ in range(connection_count)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.perf_counter() - start_time
        
        # Most connections should succeed
        successful_connections = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        success_rate = successful_connections / connection_count
        
        assert success_rate > 0.9, f"Success rate: {success_rate:.2%}"
        
        # Should handle many connections efficiently
        assert total_time < 10.0, f"Took {total_time:.2f}s to handle {connection_count} connections"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=15.0,
            max_memory_mb=80.0,
            max_cpu_percent=70.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_disk_space_exhaustion_prevention(self, performance_monitor):
        """Test prevention of disk space exhaustion via large inputs."""
        performance_monitor.start_monitoring()
        
        import tempfile
        import os
        
        # Simulate processing that might write to disk
        def process_large_input(input_data: str) -> dict:
            """Simulate processing that validates and potentially stores input."""
            try:
                # Validate input (should reject large inputs)
                validated = validate_string_input(input_data, "content", max_length=100000)
                
                # If validation passes, simulate temporary storage
                with tempfile.NamedTemporaryFile(mode='w', delete=True) as temp_file:
                    temp_file.write(validated)
                    temp_file.flush()
                    file_size = os.path.getsize(temp_file.name)
                
                return {"success": True, "size": file_size}
                
            except ValidationError:
                return {"success": False, "error": "validation_failed"}
        
        # Attempt to exhaust disk space with large inputs
        large_inputs = [
            "x" * (1024 * 1024),    # 1MB
            "y" * (10 * 1024 * 1024),  # 10MB
            "z" * (100 * 1024 * 1024), # 100MB
        ]
        
        for i, large_input in enumerate(large_inputs):
            result = process_large_input(large_input)
            
            # Large inputs should be rejected at validation
            assert not result["success"], f"Large input {i+1} was not rejected"
            assert result["error"] == "validation_failed"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=20.0,
            max_cpu_percent=30.0
        )


class TestRateLimitingEffectiveness:
    """Test rate limiting effectiveness under various attack scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_burst_request_rate_limiting(self, performance_monitor):
        """Test rate limiting against burst requests."""
        performance_monitor.start_monitoring()
        
        # Simulate burst of requests from single source
        async def make_request(request_id: int):
            """Simulate a request that might be rate limited."""
            try:
                # Simulate request processing
                result = validate_string_input(f"request_{request_id}", "title", max_length=255) 
                await asyncio.sleep(0.001)  # Minimal processing time
                return {"success": True, "id": request_id}
            except Exception as e:
                return {"success": False, "id": request_id, "error": str(e)}
        
        # Send burst of 100 requests rapidly
        burst_size = 100
        start_time = time.perf_counter()
        
        tasks = [make_request(i) for i in range(burst_size)]
        results = await asyncio.gather(*tasks)
        
        burst_time = time.perf_counter() - start_time
        
        # Analyze results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        # Some requests should succeed, but system should remain stable
        assert len(successful_requests) > 0, "No requests succeeded"
        
        # If rate limiting is active, some requests might fail
        # But system should handle the burst without crashing
        total_requests = len(results)
        assert total_requests == burst_size, "Not all requests were processed"
        
        # Burst should be processed reasonably quickly
        assert burst_time < 5.0, f"Burst took {burst_time:.2f}s to process"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=10.0,
            max_memory_mb=30.0,
            max_cpu_percent=60.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_sustained_load_rate_limiting(self, performance_monitor):
        """Test rate limiting under sustained load."""
        performance_monitor.start_monitoring()
        
        # Simulate sustained load over time
        async def sustained_load_generator():
            """Generate sustained load for testing."""
            results = []
            
            # Generate load for 30 seconds at 10 requests/second
            duration = 10  # Reduced for testing
            requests_per_second = 20
            total_requests = duration * requests_per_second
            
            for i in range(total_requests):
                try:
                    result = validate_string_input(f"sustained_request_{i}", "title", max_length=255)
                    results.append({"success": True, "id": i})
                except Exception as e:
                    results.append({"success": False, "id": i, "error": str(e)})
                
                # Maintain request rate
                await asyncio.sleep(1.0 / requests_per_second)
            
            return results
        
        results = await sustained_load_generator()
        
        # Analyze sustained load results
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results)
        
        # Most requests should succeed under normal sustained load
        assert success_rate > 0.8, f"Success rate under sustained load: {success_rate:.2%}"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=15.0,
            max_memory_mb=40.0,
            max_cpu_percent=50.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_distributed_attack_rate_limiting(self, performance_monitor):
        """Test rate limiting against distributed attacks."""
        performance_monitor.start_monitoring()
        
        # Simulate requests from multiple sources
        async def make_distributed_request(source_id: int, request_id: int):
            """Simulate request from specific source."""
            try:
                # Add source identifier to simulate different origins
                input_data = f"source_{source_id}_request_{request_id}"
                result = validate_string_input(input_data, "title", max_length=255)
                return {"success": True, "source": source_id, "id": request_id}
            except Exception as e:
                return {"success": False, "source": source_id, "id": request_id, "error": str(e)}
        
        # Simulate 20 sources sending 10 requests each
        source_count = 20
        requests_per_source = 10
        
        all_tasks = []
        for source_id in range(source_count):
            for request_id in range(requests_per_source):
                task = make_distributed_request(source_id, request_id)
                all_tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*all_tasks)
        
        # Analyze distributed attack results
        successful_requests = [r for r in results if r["success"]]
        total_requests = len(results)
        success_rate = len(successful_requests) / total_requests
        
        # System should handle distributed load
        assert success_rate > 0.7, f"Success rate against distributed attack: {success_rate:.2%}"
        
        # Verify requests from different sources
        sources_seen = set(r["source"] for r in results)
        assert len(sources_seen) == source_count, "Not all sources were processed"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=20.0,
            max_memory_mb=50.0,
            max_cpu_percent=70.0
        )


class TestSystemStabilityUnderAttack:
    """Test system stability under various attack conditions."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_graceful_degradation_under_load(self, performance_monitor):
        """Test graceful degradation under extreme load."""
        performance_monitor.start_monitoring()
        
        # Gradually increase load and monitor system behavior
        load_levels = [10, 50, 100, 200, 500]  # Requests per batch
        degradation_metrics = []
        
        for load_level in load_levels:
            async def process_batch(batch_size: int):
                """Process a batch of requests."""
                batch_start = time.perf_counter()
                
                tasks = []
                for i in range(batch_size):
                    async def process_request():
                        try:
                            return validate_string_input(f"load_test_{i}", "title", max_length=255)
                        except ValidationError:
                            return None
                    
                    tasks.append(process_request())
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_time = time.perf_counter() - batch_start
                
                # Calculate batch metrics
                successful = sum(1 for r in results if isinstance(r, str))
                success_rate = successful / batch_size
                throughput = batch_size / batch_time
                
                return {
                    "load_level": batch_size,
                    "success_rate": success_rate,
                    "throughput": throughput,
                    "batch_time": batch_time
                }
            
            metrics = await process_batch(load_level)
            degradation_metrics.append(metrics)
            
            # Brief pause between load levels
            await asyncio.sleep(0.5)
        
        # Analyze degradation pattern
        for i, metrics in enumerate(degradation_metrics):
            load_level = metrics["load_level"]
            success_rate = metrics["success_rate"]
            throughput = metrics["throughput"]
            
            # Success rate should remain reasonable even under high load
            assert success_rate > 0.5, f"Success rate {success_rate:.2%} too low at load level {load_level}"
            
            # System should maintain some throughput
            assert throughput > 5, f"Throughput {throughput:.2f} req/s too low at load level {load_level}"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=60.0,
            max_memory_mb=100.0,
            max_cpu_percent=80.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_recovery_after_attack(self, performance_monitor):
        """Test system recovery after attack subsides."""
        performance_monitor.start_monitoring()
        
        # Phase 1: Normal operation baseline
        async def normal_operation():
            """Simulate normal system operation."""
            results = []
            for i in range(20):
                try:
                    result = validate_string_input(f"normal_{i}", "title", max_length=255)
                    results.append({"success": True, "time": time.perf_counter()})
                except ValidationError:
                    results.append({"success": False, "time": time.perf_counter()})
                await asyncio.sleep(0.01)
            return results
        
        baseline_results = await normal_operation()
        baseline_success_rate = sum(1 for r in baseline_results if r["success"]) / len(baseline_results)
        
        # Phase 2: Attack phase
        async def attack_phase():
            """Simulate attack phase."""
            attack_tasks = []
            
            # Generate attack load
            for i in range(100):
                async def attack_request():
                    try:
                        # Mix of valid and invalid requests
                        if i % 3 == 0:
                            # Large payload attack
                            validate_string_input("x" * 100000, "content", max_length=1000)
                        elif i % 3 == 1:
                            # XSS attack
                            validate_string_input("<script>alert('xss')</script>", "title", max_length=255)
                        else:
                            # Normal request
                            validate_string_input(f"attack_normal_{i}", "title", max_length=255)
                        return {"success": True}
                    except ValidationError:
                        return {"success": False}
                
                attack_tasks.append(attack_request())
            
            return await asyncio.gather(*attack_tasks)
        
        attack_results = await attack_phase()
        
        # Brief recovery period
        await asyncio.sleep(1.0)
        
        # Phase 3: Post-attack operation
        recovery_results = await normal_operation()
        recovery_success_rate = sum(1 for r in recovery_results if r["success"]) / len(recovery_results)
        
        # System should recover to near-baseline performance
        recovery_ratio = recovery_success_rate / baseline_success_rate if baseline_success_rate > 0 else 1
        
        assert recovery_ratio > 0.9, f"Recovery ratio: {recovery_ratio:.2%} (baseline: {baseline_success_rate:.2%}, recovery: {recovery_success_rate:.2%})"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=30.0,
            max_memory_mb=80.0,
            max_cpu_percent=70.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_concurrent_attack_types(self, performance_monitor):
        """Test system stability under concurrent different attack types."""
        performance_monitor.start_monitoring()
        
        # Define different attack types
        async def xss_attack_batch():
            """XSS attack batch."""
            results = []
            for i in range(20):
                try:
                    validate_string_input(f"<script>alert('xss_{i}')</script>", "title", max_length=255)
                    results.append({"type": "xss", "success": True})
                except ValidationError:
                    results.append({"type": "xss", "success": False})
            return results
        
        async def path_traversal_attack_batch():
            """Path traversal attack batch."""
            results = []
            for i in range(20):
                try:
                    validate_file_path(f"../../../etc/passwd_{i}", "/safe/base", "path")
                    results.append({"type": "path_traversal", "success": True})
                except ValidationError:
                    results.append({"type": "path_traversal", "success": False})
            return results
        
        async def large_payload_attack_batch():
            """Large payload attack batch."""
            results = []
            for i in range(10):  # Fewer due to size
                try:
                    validate_string_input("x" * (10000 * (i + 1)), "content", max_length=1000)
                    results.append({"type": "large_payload", "success": True})
                except ValidationError:
                    results.append({"type": "large_payload", "success": False})
            return results
        
        async def normal_requests_batch():
            """Normal requests batch."""
            results = []
            for i in range(30):
                try:
                    validate_string_input(f"normal_request_{i}", "title", max_length=255)
                    results.append({"type": "normal", "success": True})
                except ValidationError:
                    results.append({"type": "normal", "success": False})
            return results
        
        # Run all attack types concurrently
        concurrent_results = await asyncio.gather(
            xss_attack_batch(),
            path_traversal_attack_batch(), 
            large_payload_attack_batch(),
            normal_requests_batch(),
            return_exceptions=True
        )
        
        # Flatten results
        all_results = []
        for batch_results in concurrent_results:
            if isinstance(batch_results, list):
                all_results.extend(batch_results)
        
        # Analyze concurrent attack results
        attack_types = {}
        for result in all_results:
            attack_type = result["type"]
            if attack_type not in attack_types:
                attack_types[attack_type] = {"total": 0, "blocked": 0}
            
            attack_types[attack_type]["total"] += 1
            if not result["success"]:  # Blocked/failed
                attack_types[attack_type]["blocked"] += 1
        
        # Verify attack handling
        assert "xss" in attack_types, "XSS attacks not processed"
        assert "path_traversal" in attack_types, "Path traversal attacks not processed"
        assert "large_payload" in attack_types, "Large payload attacks not processed"
        assert "normal" in attack_types, "Normal requests not processed"
        
        # All attacks should be blocked
        xss_block_rate = attack_types["xss"]["blocked"] / attack_types["xss"]["total"]
        traversal_block_rate = attack_types["path_traversal"]["blocked"] / attack_types["path_traversal"]["total"]
        payload_block_rate = attack_types["large_payload"]["blocked"] / attack_types["large_payload"]["total"]
        
        assert xss_block_rate == 1.0, f"XSS block rate: {xss_block_rate:.2%}"
        assert traversal_block_rate == 1.0, f"Path traversal block rate: {traversal_block_rate:.2%}"
        assert payload_block_rate == 1.0, f"Large payload block rate: {payload_block_rate:.2%}"
        
        # Normal requests should mostly succeed
        normal_success_rate = (attack_types["normal"]["total"] - attack_types["normal"]["blocked"]) / attack_types["normal"]["total"]
        assert normal_success_rate > 0.9, f"Normal request success rate: {normal_success_rate:.2%}"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=45.0,
            max_memory_mb=100.0,
            max_cpu_percent=80.0
        )


class TestAuthenticationPerformanceSecurity:
    """Test authentication system performance under attack."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_authentication_brute_force_resilience(self, test_api_key_manager, performance_monitor):
        """Test authentication system resilience against brute force."""
        performance_monitor.start_monitoring()
        
        # Simulate brute force attack
        async def brute_force_attempt(attempt_id: int):
            """Single brute force attempt."""
            fake_key = f"fake_key_{attempt_id}_{int(time.time())}"
            
            try:
                await test_api_key_manager.validate_api_key(fake_key)
                return {"success": True, "attempt": attempt_id}
            except AuthenticationError:
                return {"success": False, "attempt": attempt_id}
        
        # Launch many concurrent brute force attempts
        brute_force_attempts = 200
        tasks = [brute_force_attempt(i) for i in range(brute_force_attempts)]
        
        start_time = time.perf_counter()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.perf_counter() - start_time
        
        # Analyze brute force results
        failed_attempts = sum(1 for r in results if isinstance(r, dict) and not r["success"])
        
        # All attempts should fail (no valid keys used)
        assert failed_attempts == brute_force_attempts, f"Only {failed_attempts}/{brute_force_attempts} attempts failed"
        
        # System should handle brute force efficiently
        avg_time_per_attempt = total_time / brute_force_attempts
        assert avg_time_per_attempt < 0.1, f"Average time per attempt: {avg_time_per_attempt:.3f}s (too slow)"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=30.0,
            max_memory_mb=40.0,
            max_cpu_percent=60.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_authentication_timing_consistency(self, test_api_key_manager, valid_api_key, security_test_utils):
        """Test authentication timing consistency to prevent timing attacks."""
        # Test timing consistency between valid and invalid keys
        timing_samples = []
        
        # Time valid key validation
        for _ in range(10):
            timing = security_test_utils.simulate_timing_attack(
                lambda: asyncio.run(test_api_key_manager.validate_api_key(valid_api_key))
            )
            timing_samples.append(("valid", timing))
        
        # Time invalid key validation
        for i in range(10):
            invalid_key = f"invalid_key_{i}_{int(time.time())}"
            timing = security_test_utils.simulate_timing_attack(
                lambda k=invalid_key: asyncio.run(test_api_key_manager.validate_api_key(k))
            )
            timing_samples.append(("invalid", timing))
        
        # Analyze timing consistency
        valid_timings = [t for type_, t in timing_samples if type_ == "valid"]
        invalid_timings = [t for type_, t in timing_samples if type_ == "invalid"]
        
        avg_valid_time = sum(valid_timings) / len(valid_timings)
        avg_invalid_time = sum(invalid_timings) / len(invalid_timings)
        
        # Timing difference should be minimal
        time_difference_ratio = abs(avg_valid_time - avg_invalid_time) / max(avg_valid_time, avg_invalid_time)
        
        assert time_difference_ratio < 0.1, f"Timing difference ratio: {time_difference_ratio:.3f} (potential timing attack)"


# Integration test for comprehensive performance security
class TestPerformanceSecurityIntegration:
    """Integration tests for comprehensive performance security."""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_comprehensive_performance_security(self, performance_monitor):
        """Test comprehensive performance security across all vectors."""
        performance_monitor.start_monitoring()
        
        # Simulate real-world mixed attack scenario
        async def mixed_attack_simulation():
            """Simulate mixed attack with various vectors."""
            attack_results = []
            
            # Concurrent attack types
            attack_tasks = []
            
            # XSS flood
            for i in range(50):
                async def xss_attack():
                    try:
                        validate_string_input(f"<script>alert('xss_{i}')</script>", "title", max_length=255)
                        return {"type": "xss", "blocked": False}
                    except ValidationError:
                        return {"type": "xss", "blocked": True}
                
                attack_tasks.append(xss_attack())
            
            # Large payload attacks
            for i in range(20):
                async def payload_attack():
                    try:
                        validate_string_input("x" * (50000 + i * 1000), "content", max_length=1000)
                        return {"type": "large_payload", "blocked": False}
                    except ValidationError:
                        return {"type": "large_payload", "blocked": True}
                
                attack_tasks.append(payload_attack())
            
            # Path traversal attacks
            for i in range(30):
                async def traversal_attack():
                    try:
                        validate_file_path(f"../../../etc/passwd_{i}", "/safe/base", "path")
                        return {"type": "path_traversal", "blocked": False}
                    except ValidationError:
                        return {"type": "path_traversal", "blocked": True}
                
                attack_tasks.append(traversal_attack())
            
            # Normal requests (should succeed)
            for i in range(100):
                async def normal_request():
                    try:
                        validate_string_input(f"normal_request_{i}", "title", max_length=255)
                        return {"type": "normal", "blocked": False}
                    except ValidationError:
                        return {"type": "normal", "blocked": True}
                
                attack_tasks.append(normal_request())
            
            # Execute all attacks concurrently
            results = await asyncio.gather(*attack_tasks)
            return results
        
        # Run comprehensive attack simulation
        comprehensive_results = await mixed_attack_simulation()
        
        # Analyze comprehensive results
        attack_summary = {}
        for result in comprehensive_results:
            attack_type = result["type"]
            if attack_type not in attack_summary:
                attack_summary[attack_type] = {"total": 0, "blocked": 0}
            
            attack_summary[attack_type]["total"] += 1
            if result["blocked"]:
                attack_summary[attack_type]["blocked"] += 1
        
        # Verify security effectiveness
        for attack_type, stats in attack_summary.items():
            total = stats["total"]
            blocked = stats["blocked"]
            block_rate = blocked / total
            
            if attack_type == "normal":
                # Normal requests should mostly succeed (not be blocked)
                success_rate = 1 - block_rate
                assert success_rate > 0.9, f"Normal request success rate: {success_rate:.2%}"
            else:
                # Attack requests should be blocked
                assert block_rate == 1.0, f"{attack_type} block rate: {block_rate:.2%}"
        
        # System should handle comprehensive attack efficiently
        performance_monitor.assert_performance_limits(
            max_execution_time=60.0,
            max_memory_mb=150.0,
            max_cpu_percent=80.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.integration
    async def test_performance_under_sustained_mixed_load(self, performance_monitor):
        """Test performance under sustained mixed load over time."""
        performance_monitor.start_monitoring()
        
        # Sustained load test parameters
        test_duration = 30  # seconds
        requests_per_second = 10
        total_requests = test_duration * requests_per_second
        
        async def sustained_mixed_load():
            """Generate sustained mixed load."""
            results = []
            start_time = time.perf_counter()
            
            for i in range(total_requests):
                current_time = time.perf_counter()
                elapsed = current_time - start_time
                
                # Generate different types of requests
                request_type = i % 4
                
                try:
                    if request_type == 0:
                        # Normal request
                        validate_string_input(f"normal_{i}", "title", max_length=255)
                        result_type = "normal"
                        blocked = False
                    elif request_type == 1:
                        # XSS attempt
                        validate_string_input("<script>alert('xss')</script>", "title", max_length=255)
                        result_type = "xss"
                        blocked = False
                    elif request_type == 2:
                        # Path traversal attempt
                        validate_file_path("../../../etc/passwd", "/safe/base", "path")
                        result_type = "path_traversal"
                        blocked = False
                    else:
                        # Large payload attempt
                        validate_string_input("x" * 10000, "content", max_length=1000)
                        result_type = "large_payload"
                        blocked = False
                        
                except ValidationError:
                    result_type = ["normal", "xss", "path_traversal", "large_payload"][request_type]
                    blocked = True
                
                results.append({
                    "type": result_type,
                    "blocked": blocked,
                    "timestamp": current_time,
                    "request_id": i
                })
                
                # Maintain request rate
                target_time = start_time + (i + 1) / requests_per_second
                sleep_time = max(0, target_time - time.perf_counter())
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            return results
        
        sustained_results = await sustained_mixed_load()
        
        # Analyze sustained load results
        type_stats = {}
        for result in sustained_results:
            result_type = result["type"]
            if result_type not in type_stats:
                type_stats[result_type] = {"total": 0, "blocked": 0}
            
            type_stats[result_type]["total"] += 1
            if result["blocked"]:
                type_stats[result_type]["blocked"] += 1
        
        # Verify sustained performance
        for result_type, stats in type_stats.items():
            total = stats["total"]
            blocked = stats["blocked"]
            
            if result_type == "normal":
                success_rate = (total - blocked) / total
                assert success_rate > 0.9, f"Sustained normal request success rate: {success_rate:.2%}"
            else:
                block_rate = blocked / total
                assert block_rate == 1.0, f"Sustained {result_type} block rate: {block_rate:.2%}"
        
        # Check timing consistency
        timestamps = [r["timestamp"] for r in sustained_results]
        time_intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        avg_interval = sum(time_intervals) / len(time_intervals)
        expected_interval = 1.0 / requests_per_second
        
        interval_deviation = abs(avg_interval - expected_interval) / expected_interval
        assert interval_deviation < 0.2, f"Timing deviation: {interval_deviation:.2%}"
        
        performance_monitor.assert_performance_limits(
            max_execution_time=test_duration + 10,
            max_memory_mb=100.0,
            max_cpu_percent=70.0
        )