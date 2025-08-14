"""
Comprehensive Test Suite for Error Handling Decorators.

Tests all error handling infrastructure including decorators, context managers,
retry policies, and recovery strategies.
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
from datetime import datetime

# Import error handling components
from mcp_task_orchestrator.infrastructure.error_handling.decorators import handle_errors
from mcp_task_orchestrator.infrastructure.error_handling.retry_coordinator import RetryPolicy
from mcp_task_orchestrator.domain.exceptions import BaseOrchestrationError, ValidationError


class TestHandleErrorsDecorator:
    """Test suite for the @handle_errors decorator."""
    
    @pytest.mark.asyncio
    async def test_handle_errors_async_success(self):
        """Test successful async function execution."""
        @handle_errors(component="TestComponent", operation="test_operation")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    def test_handle_errors_sync_success(self):
        """Test successful sync function execution."""
        @handle_errors(component="TestComponent", operation="test_operation")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_handle_errors_async_with_exception(self):
        """Test async function with exception."""
        @handle_errors(component="TestComponent", operation="test_operation", log_errors=True)
        async def test_function():
            raise ValidationError("field", "invalid", ["test error"])
        
        with pytest.raises(ValidationError):
            await test_function()
    
    def test_handle_errors_sync_with_exception(self):
        """Test sync function with exception."""
        @handle_errors(component="TestComponent", operation="test_operation", log_errors=True)
        def test_function():
            raise OrchestrationError("Test error", error_code="TEST_ERROR")
        
        with pytest.raises(OrchestrationError):
            test_function()
    
    @pytest.mark.asyncio
    async def test_handle_errors_with_retry_policy(self):
        """Test error handling with retry policy."""
        call_count = 0
        
        @handle_errors(
            component="TestComponent",
            operation="test_retry",
            auto_retry=True,
            retry_policy=ExponentialBackoffPolicy(max_attempts=3)
        )
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OrchestrationError("Temporary error", error_code="TEMP_ERROR")
            return "success_after_retry"
        
        result = await test_function()
        assert result == "success_after_retry"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_handle_errors_retry_exhausted(self):
        """Test retry exhaustion scenario."""
        @handle_errors(
            component="TestComponent",
            operation="test_retry_exhausted",
            auto_retry=True,
            retry_policy=FixedDelayPolicy(max_attempts=2, delay_seconds=0.1)
        )
        async def test_function():
            raise OrchestrationError("Persistent error", error_code="PERSISTENT_ERROR")
        
        with pytest.raises(OrchestrationError):
            await test_function()
    
    def test_handle_errors_specific_error_types(self):
        """Test handling only specific error types."""
        @handle_errors(
            error_types=[ValidationError],
            component="TestComponent",
            operation="test_specific_errors"
        )
        def test_function(error_type):
            if error_type == "validation":
                raise ValidationError("field", "invalid", ["test error"])
            elif error_type == "orchestration":
                raise OrchestrationError("Test error", error_code="TEST_ERROR")
            return "success"
        
        # ValidationError should be handled
        with pytest.raises(ValidationError):
            test_function("validation")
        
        # OrchestrationError should pass through unhandled
        with pytest.raises(OrchestrationError):
            test_function("orchestration")
        
        # Success case
        result = test_function("success")
        assert result == "success"


class TestSuppressErrorsDecorator:
    """Test suite for the @suppress_errors decorator."""
    
    def test_suppress_errors_success(self):
        """Test successful function execution."""
        @suppress_errors([ValueError], default_return="default")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_suppress_errors_suppressed(self):
        """Test error suppression."""
        @suppress_errors([ValueError, TypeError], default_return="suppressed")
        def test_function(error_type):
            if error_type == "value":
                raise ValueError("Test value error")
            elif error_type == "type":
                raise TypeError("Test type error")
            return "success"
        
        # Suppressed errors
        assert test_function("value") == "suppressed"
        assert test_function("type") == "suppressed"
        
        # Success case
        assert test_function("success") == "success"
    
    def test_suppress_errors_not_suppressed(self):
        """Test that non-specified errors are not suppressed."""
        @suppress_errors([ValueError], default_return="suppressed")
        def test_function():
            raise RuntimeError("Not suppressed")
        
        with pytest.raises(RuntimeError):
            test_function()


class TestErrorContext:
    """Test suite for ErrorContext context manager."""
    
    @pytest.mark.asyncio
    async def test_error_context_async_success(self):
        """Test async context manager with success."""
        async with ErrorContext("TestComponent", "test_operation") as ctx:
            assert ctx.component == "TestComponent"
            assert ctx.operation == "test_operation"
    
    @pytest.mark.asyncio
    async def test_error_context_async_with_error(self):
        """Test async context manager with error."""
        with patch('mcp_task_orchestrator.infrastructure.error_handling.logging_handlers.get_error_logger') as mock_logger:
            mock_error_logger = Mock()
            mock_logger.return_value = mock_error_logger
            
            with pytest.raises(ValueError):
                async with ErrorContext("TestComponent", "test_operation"):
                    raise ValueError("Test error")
            
            # Verify error was logged
            mock_error_logger.log_error.assert_called_once()
    
    def test_error_context_sync_success(self):
        """Test sync context manager with success."""
        with ErrorContext("TestComponent", "test_operation") as ctx:
            assert ctx.component == "TestComponent"
            assert ctx.operation == "test_operation"
    
    def test_error_context_sync_with_error(self):
        """Test sync context manager with error."""
        with patch('mcp_task_orchestrator.infrastructure.error_handling.logging_handlers.get_error_logger') as mock_logger:
            mock_error_logger = Mock()
            mock_logger.return_value = mock_error_logger
            
            with pytest.raises(ValueError):
                with ErrorContext("TestComponent", "test_operation"):
                    raise ValueError("Test error")
            
            # Verify error was logged
            mock_error_logger.log_error.assert_called_once()


class TestWithErrorContextDecorator:
    """Test suite for @with_error_context decorator."""
    
    def test_with_error_context_success(self):
        """Test successful function execution with context."""
        @with_error_context("TestComponent", "test_operation")
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_with_error_context_orchestration_error(self):
        """Test error context addition to OrchestrationError."""
        @with_error_context("TestComponent", "test_operation", additional_info="test")
        def test_function():
            error = OrchestrationError("Test error", error_code="TEST_ERROR")
            raise error
        
        with pytest.raises(OrchestrationError) as exc_info:
            test_function()
        
        error = exc_info.value
        assert error.context["component"] == "TestComponent"
        assert error.context["operation"] == "test_operation"
        assert error.context["additional_info"] == "test"
    
    def test_with_error_context_other_error(self):
        """Test that non-OrchestrationError exceptions pass through unchanged."""
        @with_error_context("TestComponent", "test_operation")
        def test_function():
            raise ValueError("Not an orchestration error")
        
        with pytest.raises(ValueError):
            test_function()


class TestSafeCallFunctions:
    """Test suite for safe_call and safe_call_async functions."""
    
    def test_safe_call_success(self):
        """Test safe_call with successful function."""
        def test_function(x, y):
            return x + y
        
        result = safe_call(test_function, 2, 3)
        assert result == 5
    
    def test_safe_call_with_error(self):
        """Test safe_call with function that raises error."""
        def test_function():
            raise ValueError("Test error")
        
        result = safe_call(test_function, default="default_value")
        assert result == "default_value"
    
    @pytest.mark.asyncio
    async def test_safe_call_async_success(self):
        """Test safe_call_async with successful function."""
        async def test_function(x, y):
            return x * y
        
        result = await safe_call_async(test_function, 3, 4)
        assert result == 12
    
    @pytest.mark.asyncio
    async def test_safe_call_async_with_error(self):
        """Test safe_call_async with function that raises error."""
        async def test_function():
            raise RuntimeError("Async test error")
        
        result = await safe_call_async(test_function, default="async_default")
        assert result == "async_default"


class TestValidateInputDecorator:
    """Test suite for @validate_input decorator."""
    
    def test_validate_input_success(self):
        """Test successful input validation."""
        def is_positive(x):
            return isinstance(x, (int, float)) and x > 0
        
        @validate_input(is_positive, "Value must be positive")
        def test_function(x, y):
            return x + y
        
        result = test_function(5, 3)
        assert result == 8
    
    def test_validate_input_failure_args(self):
        """Test input validation failure with positional args."""
        def is_string(x):
            return isinstance(x, str)
        
        @validate_input(is_string, "Value must be string")
        def test_function(x):
            return x.upper()
        
        with pytest.raises(ValidationError) as exc_info:
            test_function(123)
        
        error = exc_info.value
        assert "Value must be string" in error.validation_errors
    
    def test_validate_input_failure_kwargs(self):
        """Test input validation failure with keyword args."""
        def is_positive(x):
            return isinstance(x, (int, float)) and x > 0
        
        @validate_input(is_positive, "Value must be positive")
        def test_function(x=1, y=2):
            return x + y
        
        with pytest.raises(ValidationError) as exc_info:
            test_function(x=5, y=-3)
        
        error = exc_info.value
        assert "Value must be positive" in error.validation_errors


class TestRetryPolicies:
    """Test suite for retry policy implementations."""
    
    def test_exponential_backoff_policy(self):
        """Test exponential backoff calculation."""
        policy = ExponentialBackoffPolicy(max_attempts=4, base_delay=1.0, max_delay=10.0)
        
        assert policy.should_retry(1) == True
        assert policy.should_retry(3) == True
        assert policy.should_retry(4) == False
        
        # Test delay calculation
        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0
    
    def test_linear_backoff_policy(self):
        """Test linear backoff calculation."""
        policy = LinearBackoffPolicy(max_attempts=3, base_delay=2.0, increment=1.5)
        
        assert policy.should_retry(1) == True
        assert policy.should_retry(2) == True
        assert policy.should_retry(3) == False
        
        # Test delay calculation
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 3.5
        assert policy.get_delay(3) == 5.0
    
    def test_fixed_delay_policy(self):
        """Test fixed delay policy."""
        policy = FixedDelayPolicy(max_attempts=3, delay_seconds=0.5)
        
        assert policy.should_retry(1) == True
        assert policy.should_retry(2) == True
        assert policy.should_retry(3) == False
        
        # Test delay calculation
        assert policy.get_delay(1) == 0.5
        assert policy.get_delay(2) == 0.5
        assert policy.get_delay(3) == 0.5


class TestIntegrationScenarios:
    """Integration tests for complete error handling workflows."""
    
    @pytest.mark.asyncio
    async def test_mcp_handler_error_flow(self):
        """Test complete error flow in MCP handler context."""
        
        # Simulate MCP handler with multiple error handling layers
        @handle_errors(
            component="MCPHandler",
            operation="test_handler",
            auto_retry=True,
            retry_policy=ExponentialBackoffPolicy(max_attempts=2),
            log_errors=True
        )
        async def mock_handler(args: Dict[str, Any]):
            # Simulate validation
            if not args.get("task_id"):
                raise ValidationError("task_id", None, ["task_id is required"])
            
            # Simulate business logic error
            if args.get("fail_mode") == "orchestration":
                raise OrchestrationError("Service unavailable", error_code="SERVICE_ERROR")
            
            return {"status": "success", "data": args}
        
        # Test success case
        result = await mock_handler({"task_id": "123", "data": "test"})
        assert result["status"] == "success"
        
        # Test validation error
        with pytest.raises(ValidationError):
            await mock_handler({})
        
        # Test orchestration error with retry
        with pytest.raises(OrchestrationError):
            await mock_handler({"task_id": "123", "fail_mode": "orchestration"})
    
    @pytest.mark.asyncio
    async def test_database_error_recovery(self):
        """Test database error handling and recovery scenarios."""
        
        connection_attempts = 0
        
        @handle_errors(
            component="DatabaseService",
            operation="query",
            auto_retry=True,
            retry_policy=LinearBackoffPolicy(max_attempts=3, base_delay=0.1),
            auto_recover=True
        )
        async def mock_database_query():
            nonlocal connection_attempts
            connection_attempts += 1
            
            # Simulate transient database error
            if connection_attempts < 3:
                raise OrchestrationError("Database connection failed", error_code="DB_CONNECTION_ERROR")
            
            return {"rows": [{"id": 1, "name": "test"}]}
        
        result = await mock_database_query()
        assert result["rows"][0]["name"] == "test"
        assert connection_attempts == 3
    
    def test_performance_impact_measurement(self):
        """Test that error handling doesn't significantly impact performance."""
        import time
        
        @handle_errors(component="PerformanceTest", operation="baseline")
        def baseline_function():
            return sum(range(1000))
        
        def undecorated_function():
            return sum(range(1000))
        
        # Measure baseline performance
        start_time = time.time()
        for _ in range(100):
            undecorated_function()
        baseline_time = time.time() - start_time
        
        # Measure decorated performance
        start_time = time.time()
        for _ in range(100):
            baseline_function()
        decorated_time = time.time() - start_time
        
        # Error handling overhead should be minimal
        overhead_ratio = decorated_time / baseline_time
        assert overhead_ratio < 1.5, f"Error handling overhead too high: {overhead_ratio:.2f}x"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])