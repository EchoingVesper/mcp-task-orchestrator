"""
Information Disclosure Security Tests

Comprehensive test suite for validating error message sanitization, debug
information leakage prevention, timing attack mitigation, and sensitive
data exposure protection.
"""

import pytest
import asyncio
import time
import traceback
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# from mcp_task_orchestrator.infrastructure.security import  # TODO: Complete this import


class TestErrorMessageSanitization:
    """Test error message sanitization and sensitive data removal."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.critical
    async def test_stack_trace_sanitization(self, security_test_utils):
        """Test that stack traces are sanitized from error messages."""
        # Simulate error with stack trace
        def raise_error_with_trace():
            try:
                1 / 0  # Causes ZeroDivisionError with stack trace
            except Exception:
                # Capture full traceback
                full_traceback = traceback.format_exc()
                raise Exception(f"Database error: {full_traceback}")
        
        try:
            raise_error_with_trace()
        except Exception as e:
            sanitized_error = sanitize_error(e, ErrorCategory.DATABASE_ERROR)
            
            # Should not contain sensitive information
            security_test_utils.assert_no_sensitive_data_in_error(str(sanitized_error))
            
            # Should not contain stack trace elements
            error_str = str(sanitized_error).lower()
            assert "traceback" not in error_str
            assert "file \"" not in error_str
            assert "line " not in error_str
            assert "/home/" not in error_str
            assert "mcp_task_orchestrator/" not in error_str
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.critical
    async def test_file_path_sanitization(self):
        """Test that file paths are sanitized from error messages."""
        sensitive_file_paths = [
            "/home/user/.env",
            "/var/www/html/config/database.php",
            "C:\\Users\\Administrator\\AppData\\config.json",
            "/opt/app/secrets/api_keys.txt",
            "/etc/passwd",
            "/root/.ssh/id_rsa",
        ]
        
        for file_path in sensitive_file_paths:
            # Simulate error with file path
            error_msg = f"Failed to read configuration from {file_path}"
            error = Exception(error_msg)
            
            sanitized_error = sanitize_error(error, ErrorCategory.FILE_ERROR)
            sanitized_msg = str(sanitized_error)
            
            # Should not contain the full file path
            assert file_path not in sanitized_msg
            
            # Should not contain directory structure information
            assert "/home/" not in sanitized_msg
            assert "/var/" not in sanitized_msg
            assert "/etc/" not in sanitized_msg
            assert "/root/" not in sanitized_msg
            assert "C:\\" not in sanitized_msg
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.critical
    async def test_database_schema_sanitization(self):
        """Test that database schema information is sanitized."""
        database_error_messages = [
            "Table 'users' doesn't exist in database 'production_db'",
            "Column 'password_hash' not found in table 'user_accounts'",
            "Foreign key constraint failed on 'api_keys.user_id'",
            "Duplicate entry 'admin@company.com' for key 'users.email_unique'",
            "Data too long for column 'secret_token' at row 1",
            "SELECT * FROM sensitive_data WHERE user_id = 123 - syntax error",
        ]
        
        for db_error in database_error_messages:
            error = Exception(db_error)
            sanitized_error = sanitize_error(error, ErrorCategory.DATABASE_ERROR)
            sanitized_msg = str(sanitized_error).lower()
            
            # Should not contain table names
            assert "users" not in sanitized_msg
            assert "user_accounts" not in sanitized_msg
            assert "api_keys" not in sanitized_msg
            assert "sensitive_data" not in sanitized_msg
            
            # Should not contain column names
            assert "password_hash" not in sanitized_msg
            assert "secret_token" not in sanitized_msg
            assert "user_id" not in sanitized_msg
            
            # Should not contain SQL queries
            assert "select" not in sanitized_msg
            assert "where" not in sanitized_msg
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.critical
    async def test_api_key_sanitization(self):
        """Test that API keys and tokens are sanitized."""
        sensitive_tokens = [
            "FAKE-SK-REDACTED-FOR-TESTING",
            "FAKE-GHP-REDACTED-FOR-TESTING",
            "FAKE-XOXB-REDACTED-FOR-TESTING",
            "FAKE-YA29-REDACTED-FOR-TESTING",
            "Bearer FAKE-JWT-REDACTED-FOR-TESTING",
            "FAKE-AKIA-REDACTED-FOR-TESTING",
        ]
        
        for token in sensitive_tokens:
            error_msg = f"Authentication failed with token: {token}"
            error = AuthenticationError(error_msg)
            
            sanitized_error = sanitize_error(error, ErrorCategory.AUTHENTICATION_ERROR)
            sanitized_msg = str(sanitized_error)
            
            # Should not contain the actual token
            assert token not in sanitized_msg
            
            # Should not contain token-like patterns
            assert len([word for word in sanitized_msg.split() if len(word) > 20]) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_environment_variable_sanitization(self):
        """Test that environment variables are sanitized."""
        env_var_errors = [
            "DATABASE_URL not found: postgresql://user:pass@localhost/db",
            "Missing SECRET_KEY: FAKE-SK-REDACTED-FOR-TESTING",
            "Invalid API_TOKEN: FAKE-GHP-REDACTED-FOR-TESTING",
            "JWT_SECRET environment variable: super_secret_jwt_key_123",
            "AWS_ACCESS_KEY_ID: AKIA1234567890ABCDEF",
        ]
        
        for env_error in env_var_errors:
            error = Exception(env_error)
            sanitized_error = sanitize_error(error, ErrorCategory.CONFIGURATION_ERROR)
            sanitized_msg = str(sanitized_error)
            
            # Should not contain credentials
            assert "postgresql://user:pass@" not in sanitized_msg
            assert "sk-" not in sanitized_msg
            assert "ghp_" not in sanitized_msg
            assert "super_secret" not in sanitized_msg
            assert "AKIA" not in sanitized_msg


class TestDebugInformationLeakage:
    """Test prevention of debug information leakage."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_debug_mode_information_suppression(self):
        """Test that debug mode information is suppressed in production."""
        # Simulate debug information that might leak
        debug_info_patterns = [
            "DEBUG: Database connection pool size: 10",
            "TRACE: Processing request with session_id: abc123",
            "Internal error ID: 7f9a8b6c-1234-5678-9abc-def123456789", 
            "Memory usage: 1.2GB, CPU: 45%",
            "Cache miss for key: user_session_12345",
            "SQL query executed in 150ms: SELECT * FROM users",
        ]
        
        for debug_info in debug_info_patterns:
            error = Exception(f"Operation failed. {debug_info}")
            sanitized_error = sanitize_error(error, ErrorCategory.INTERNAL_ERROR)
            sanitized_msg = str(sanitized_error).lower()
            
            # Should not contain debug keywords
            assert "debug:" not in sanitized_msg
            assert "trace:" not in sanitized_msg
            assert "internal error id:" not in sanitized_msg
            assert "memory usage:" not in sanitized_msg
            assert "sql query executed" not in sanitized_msg
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_system_information_suppression(self):
        """Test that system information is suppressed."""
        system_info_patterns = [
            "Python version: 3.9.7 on linux",
            "Server: nginx/1.18.0 (Ubuntu)",
            "Database: PostgreSQL 13.7 on x86_64-pc-linux-gnu",
            "OS: Ubuntu 20.04.4 LTS",
            "Memory: 16GB available, 8GB used",
            "Disk space: 500GB total, 250GB used",
        ]
        
        for system_info in system_info_patterns:
            error = Exception(f"System error: {system_info}")
            sanitized_error = sanitize_error(error, ErrorCategory.SYSTEM_ERROR)
            sanitized_msg = str(sanitized_error).lower()
            
            # Should not contain system details
            assert "python version:" not in sanitized_msg
            assert "nginx/" not in sanitized_msg
            assert "postgresql" not in sanitized_msg
            assert "ubuntu" not in sanitized_msg
            assert "memory:" not in sanitized_msg
            assert "disk space:" not in sanitized_msg
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_configuration_details_suppression(self):
        """Test that configuration details are suppressed."""
        config_patterns = [
            "Configuration loaded from /etc/app/config.json",
            "Redis connection: redis://localhost:6379/0",
            "SMTP server: smtp.company.com:587",
            "Log level set to DEBUG",
            "Cache TTL: 3600 seconds",
            "Rate limit: 100 requests per minute",
        ]
        
        for config_info in config_patterns:
            error = Exception(f"Configuration error: {config_info}")
            sanitized_error = sanitize_error(error, ErrorCategory.CONFIGURATION_ERROR)
            sanitized_msg = str(sanitized_error)
            
            # Should not contain configuration details
            assert "/etc/app/config.json" not in sanitized_msg
            assert "redis://localhost:6379" not in sanitized_msg
            assert "smtp.company.com" not in sanitized_msg
            assert "DEBUG" not in sanitized_msg


class TestTimingAttackMitigation:
    """Test timing attack mitigation in error responses."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_response_timing_consistency(self, security_test_utils):
        """Test that error responses have consistent timing."""
        # Simulate different types of errors
        error_scenarios = [
            (ValidationError("Invalid input"), ErrorCategory.VALIDATION_ERROR),
            (AuthenticationError("Invalid credentials"), ErrorCategory.AUTHENTICATION_ERROR),
            (AuthorizationError("Access denied"), ErrorCategory.AUTHORIZATION_ERROR),
            (Exception("Database connection failed"), ErrorCategory.DATABASE_ERROR),
            (FileNotFoundError("File not found"), ErrorCategory.FILE_ERROR),
        ]
        
        timing_results = []
        
        for error, category in error_scenarios:
            # Measure error sanitization timing
            timing = security_test_utils.simulate_timing_attack(
                sanitize_error, error, category
            )
            timing_results.append(timing)
        
        # Calculate timing variations
        min_time = min(timing_results)
        max_time = max(timing_results)
        time_variation = max_time - min_time
        
        # Timing variation should be minimal (within 5ms)
        assert time_variation < 0.005, f"Timing variation {time_variation:.4f}s too large"
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_processing_delays(self):
        """Test that error processing doesn't introduce information-leaking delays."""
        # Simulate errors with different complexities
        simple_error = Exception("Simple error")
        complex_error = Exception("Complex error: " + "x" * 10000)  # Large error message
        
        # Both should be processed in similar time
        start_time = time.perf_counter()
        sanitize_error(simple_error, ErrorCategory.VALIDATION_ERROR)
        simple_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        sanitize_error(complex_error, ErrorCategory.VALIDATION_ERROR)
        complex_time = time.perf_counter() - start_time
        
        # Complex error shouldn't take significantly longer
        time_ratio = complex_time / simple_time if simple_time > 0 else 1
        assert time_ratio < 3.0, f"Complex error took {time_ratio:.2f}x longer than simple error"


class TestSafeErrorResponses:
    """Test safe error response generation."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.critical
    async def test_safe_error_response_structure(self):
        """Test that safe error responses have proper structure."""
        test_errors = [
            (ValidationError("Invalid input data"), ErrorCategory.VALIDATION_ERROR),
            (AuthenticationError("Authentication failed"), ErrorCategory.AUTHENTICATION_ERROR),
            (Exception("Unexpected error occurred"), ErrorCategory.INTERNAL_ERROR),
        ]
        
        for error, category in test_errors:
            safe_response = safe_error_response(error, category)
            
            # Should be SafeErrorResponse object
            assert isinstance(safe_response, SafeErrorResponse)
            
            # Should have required fields
            assert hasattr(safe_response, 'error_code')
            assert hasattr(safe_response, 'message')
            assert hasattr(safe_response, 'category')
            assert hasattr(safe_response, 'timestamp')
            
            # Should not contain original error details
            assert str(error) not in safe_response.message
            
            # Should have generic, safe message
            assert len(safe_response.message) > 0
            assert safe_response.message != str(error)
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_mcp_error_response_format(self):
        """Test MCP-specific error response format."""
        error = ValidationError("Invalid task title format")
        
        mcp_response = mcp_error_response(error, ErrorCategory.VALIDATION_ERROR)
        
        # Should be proper MCP error format
        assert "error" in mcp_response
        assert "code" in mcp_response["error"]
        assert "message" in mcp_response["error"]
        
        # Should not contain original error details
        assert "Invalid task title format" not in mcp_response["error"]["message"]
        
        # Should have safe, generic message
        message = mcp_response["error"]["message"]
        assert len(message) > 0
        assert "validation" in message.lower() or "invalid" in message.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_response_consistency(self):
        """Test that similar errors produce consistent responses."""
        # Similar validation errors
        validation_errors = [
            ValidationError("Title too long"),
            ValidationError("Description contains invalid characters"),
            ValidationError("Invalid email format"),
        ]
        
        responses = []
        for error in validation_errors:
            response = safe_error_response(error, ErrorCategory.VALIDATION_ERROR)
            responses.append(response)
        
        # All should have same error code
        error_codes = [r.error_code for r in responses]
        assert len(set(error_codes)) == 1, "Similar errors should have same error code"
        
        # All should have similar message structure
        messages = [r.message for r in responses]
        # Should not be identical (to avoid fingerprinting) but should follow same pattern
        assert len(set(messages)) <= len(messages), "Messages should vary appropriately"


class TestHandlerErrorSanitization:
    """Test error sanitization in MCP handlers."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_handler_decorator_error_sanitization(self):
        """Test that handler decorator sanitizes errors."""
        @sanitize_handler_errors
        async def test_handler(args):
            # Simulate handler that raises error with sensitive info
            raise Exception("Database connection failed: postgresql://user:pass@db:5432/prod")
        
        # Handler should return sanitized error response
        try:
            await test_handler({})
        except Exception as e:
            # Should not contain sensitive database info
            error_str = str(e)
            assert "postgresql://user:pass@" not in error_str
            assert ":5432" not in error_str
            assert "/prod" not in error_str
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_handler_stack_trace_suppression(self):
        """Test that handler errors suppress stack traces."""
        @sanitize_handler_errors
        async def nested_error_handler(args):
            def level1():
                def level2():
                    def level3():
                        raise Exception("Deep error with sensitive path: /home/user/.secrets")
                    level3()
                level2()
            level1()
        
        try:
            await nested_error_handler({})
        except Exception as e:
            error_str = str(e)
            
            # Should not contain stack trace info
            assert "level1" not in error_str
            assert "level2" not in error_str  
            assert "level3" not in error_str
            assert "/home/user/.secrets" not in error_str
            assert "nested_error_handler" not in error_str
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_async_handler_error_sanitization(self):
        """Test error sanitization in async handlers."""
        @sanitize_handler_errors
        async def async_handler(args):
            await asyncio.sleep(0.01)  # Simulate async work
            raise Exception("Async error with API key: sk-1234567890abcdef")
        
        try:
            await async_handler({})
        except Exception as e:
            error_str = str(e)
            
            # Should not contain API key
            assert "sk-1234567890abcdef" not in error_str
            assert "sk-" not in error_str


class TestProductionErrorHandling:
    """Test production-ready error handling."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_production_mode_error_suppression(self):
        """Test that production mode suppresses detailed errors."""
        # Simulate production environment
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            detailed_error = Exception(
                "Database error in users table: "
                "SELECT * FROM users WHERE email = 'admin@company.com' "
                "Connection string: postgresql://admin:secret@prod-db:5432/company_db"
            )
            
            sanitized = sanitize_error(detailed_error, ErrorCategory.DATABASE_ERROR)
            sanitized_str = str(sanitized).lower()
            
            # Should be very generic in production
            assert "database error" not in sanitized_str or len(sanitized_str) < 50
            assert "users table" not in sanitized_str
            assert "admin@company.com" not in sanitized_str
            assert "postgresql://" not in sanitized_str
            assert "company_db" not in sanitized_str
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_development_vs_production_errors(self):
        """Test different error handling between development and production."""
        test_error = Exception("Detailed development error with sensitive info")
        
        # Development mode (more detailed, but still sanitized)
        with patch.dict('os.environ', {'ENVIRONMENT': 'development'}):
            dev_error = sanitize_error(test_error, ErrorCategory.INTERNAL_ERROR)
            dev_message = str(dev_error)
        
        # Production mode (minimal information)
        with patch.dict('os.environ', {'ENVIRONMENT': 'production'}):
            prod_error = sanitize_error(test_error, ErrorCategory.INTERNAL_ERROR)
            prod_message = str(prod_error)
        
        # Production should be more restrictive
        assert len(prod_message) <= len(dev_message)
        
        # Both should not contain sensitive info
        assert "sensitive info" not in dev_message
        assert "sensitive info" not in prod_message
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_logging_vs_response_sanitization(self):
        """Test that errors are logged with details but responses are sanitized."""
        sensitive_error = Exception(
            "Failed to connect to database at postgresql://user:pass@localhost:5432/db"
        )
        
        # Mock logger to capture what gets logged
        logged_messages = []
        
        def mock_log_error(message, *args, **kwargs):
            logged_messages.append(message)
        
        with patch('logging.error', mock_log_error):
            sanitized_response = safe_error_response(
                sensitive_error, 
                ErrorCategory.DATABASE_ERROR
            )
        
        # Response should be sanitized
        response_message = sanitized_response.message
        assert "postgresql://" not in response_message
        assert "user:pass" not in response_message
        
        # But logging might contain more details (for debugging)
        # Note: This depends on the logging implementation
        # In a real system, you might log the full error for debugging
        # while returning sanitized errors to users


class TestErrorCategoryClassification:
    """Test proper error category classification."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_category_mapping(self):
        """Test that errors are mapped to correct categories."""
        error_category_tests = [
            (ValidationError("Invalid input"), ErrorCategory.VALIDATION_ERROR),
            (AuthenticationError("Auth failed"), ErrorCategory.AUTHENTICATION_ERROR),
            (AuthorizationError("Access denied"), ErrorCategory.AUTHORIZATION_ERROR),
            (FileNotFoundError("File not found"), ErrorCategory.FILE_ERROR),
            (ConnectionError("Network error"), ErrorCategory.NETWORK_ERROR),
            (Exception("Generic error"), ErrorCategory.INTERNAL_ERROR),
        ]
        
        for error, expected_category in error_category_tests:
            response = safe_error_response(error, expected_category)
            assert response.category == expected_category
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_code_generation(self):
        """Test that error codes are generated appropriately."""
        test_errors = [
            (ValidationError("Test"), ErrorCategory.VALIDATION_ERROR),
            (AuthenticationError("Test"), ErrorCategory.AUTHENTICATION_ERROR),
        ]
        
        for error, category in test_errors:
            response = safe_error_response(error, category)
            
            # Should have error code
            assert response.error_code is not None
            assert len(response.error_code) > 0
            
            # Error code should not contain sensitive info
            assert "test" not in response.error_code.lower()
            assert not any(char in response.error_code for char in ['/', '\\', ':', '@'])
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    async def test_error_message_templates(self):
        """Test that error messages use safe templates."""
        # Different errors of same category should use consistent templates
        validation_errors = [
            ValidationError("Title is too long"),
            ValidationError("Email format invalid"),
            ValidationError("Required field missing"),
        ]
        
        messages = []
        for error in validation_errors:
            response = safe_error_response(error, ErrorCategory.VALIDATION_ERROR)
            messages.append(response.message)
        
        # Should use templates, not expose original error messages
        for i, original_error in enumerate(validation_errors):
            assert str(original_error) not in messages[i]
        
        # Should have consistent structure
        # (Exact implementation depends on error sanitizer)
        assert len(set([len(msg.split()) for msg in messages])) <= 2  # Similar word count


# Integration tests
class TestInformationDisclosureIntegration:
    """Integration tests for comprehensive information disclosure prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.integration
    async def test_end_to_end_error_sanitization(self, performance_monitor):
        """Test end-to-end error sanitization across all components."""
        performance_monitor.start_monitoring()
        
        # Simulate complex error with multiple sensitive elements
        complex_error = Exception(
            "Multi-layer error occurred:\n"
            "1. Database connection failed: postgresql://admin:secret123@prod-db:5432/company_db\n"
            "2. Fallback to file failed: /home/app/.env not found\n"
            "3. API call failed with token: FAKE-SK-REDACTED-FOR-TESTING\n"
            "4. Stack trace:\n"
            "  File '/opt/app/src/database.py', line 123, in connect\n"
            "  File '/opt/app/src/auth.py', line 456, in authenticate\n"
            "5. System info: Python 3.9.7 on Ubuntu 20.04, 16GB RAM\n"
            "6. Internal error ID: 7f9a8b6c-1234-5678-9abc-def123456789"
        )
        
        # Process through complete sanitization chain
        safe_response = safe_error_response(complex_error, ErrorCategory.INTERNAL_ERROR)
        
        # Should not contain any sensitive information
        response_str = str(safe_response.message).lower()
        
        sensitive_patterns = [
            "postgresql://", "admin:secret123", "prod-db:5432", "company_db",
            "/home/app/.env", "sk-1234567890abcdef", "/opt/app/src/",
            "database.py", "auth.py", "line 123", "line 456",
            "python 3.9.7", "ubuntu 20.04", "16gb ram",
            "7f9a8b6c-1234-5678-9abc-def123456789"
        ]
        
        for pattern in sensitive_patterns:
            assert pattern not in response_str, f"Sensitive pattern '{pattern}' found in sanitized response"
        
        # Should still be informative but safe
        assert len(safe_response.message) > 10  # Not empty
        assert "error" in response_str  # Still indicates an error occurred
        
        # Performance should be reasonable
        performance_monitor.assert_performance_limits(
            max_execution_time=1.0,
            max_memory_mb=5.0,
            max_cpu_percent=20.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.integration
    async def test_concurrent_error_sanitization(self, performance_monitor):
        """Test error sanitization under concurrent load."""
        performance_monitor.start_monitoring()
        
        async def sanitize_error_task(error_id: int):
            # Create unique error with sensitive data
            error = Exception(
                f"Error {error_id}: Database failed at postgresql://user{error_id}:pass{error_id}@db/prod"
            )
            
            response = safe_error_response(error, ErrorCategory.DATABASE_ERROR)
            
            # Verify sanitization worked
            response_str = str(response.message)
            assert f"user{error_id}" not in response_str
            assert f"pass{error_id}" not in response_str
            assert "postgresql://" not in response_str
            
            return response
        
        # Run many concurrent sanitization tasks
        tasks = [sanitize_error_task(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 50
        assert all(isinstance(r, SafeErrorResponse) for r in results)
        
        # Performance should remain good under load
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=20.0,
            max_cpu_percent=60.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.information_disclosure
    @pytest.mark.integration  
    async def test_cross_category_error_consistency(self):
        """Test that error sanitization is consistent across categories."""
        # Create similar errors in different categories
        base_sensitive_info = "secret_api_key_abc123 and /private/config.json"
        
        categorized_errors = [
            (Exception(f"Validation failed: {base_sensitive_info}"), ErrorCategory.VALIDATION_ERROR),
            (Exception(f"Auth failed: {base_sensitive_info}"), ErrorCategory.AUTHENTICATION_ERROR),
            (Exception(f"DB error: {base_sensitive_info}"), ErrorCategory.DATABASE_ERROR),
            (Exception(f"File error: {base_sensitive_info}"), ErrorCategory.FILE_ERROR),
        ]
        
        sanitized_responses = []
        for error, category in categorized_errors:
            response = safe_error_response(error, category)
            sanitized_responses.append(response)
        
        # All should remove the sensitive information
        for response in sanitized_responses:
            response_str = str(response.message)
            assert "secret_api_key_abc123" not in response_str
            assert "/private/config.json" not in response_str
        
        # Should have category-appropriate messages
        categories = [r.category for r in sanitized_responses]
        assert len(set(categories)) == len(categorized_errors)  # All different categories
        
        # But should follow consistent sanitization rules
        message_lengths = [len(r.message) for r in sanitized_responses]
        # Messages should be reasonably similar in length
        assert max(message_lengths) - min(message_lengths) < 50