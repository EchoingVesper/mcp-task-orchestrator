"""
Input Validation Security Tests

Comprehensive test suite for validating XSS prevention, SQL injection protection,
command injection prevention, JSON injection detection, and input sanitization.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from mcp_task_orchestrator.infrastructure.security import (
    XSSValidator,
    PathValidator,
    ParameterValidator,
    ValidationError,
    xss_validator,
    path_validator,
    parameter_validator,
    validate_string_input,
    validate_file_path,
    validate_task_id,
    is_safe_input
)

from mcp_task_orchestrator.domain.entities.task import Task


class TestXSSPrevention:
    """Test XSS attack prevention and input sanitization."""
    
    @pytest.mark.asyncio
    @pytest.mark.xss
    @pytest.mark.critical
    async def test_basic_xss_payload_rejection(self, xss_payloads):
        """Test basic XSS payload rejection."""
        for payload in xss_payloads:
            with pytest.raises(ValidationError) as exc_info:
                validate_string_input(payload, "title", max_length=1000)
            
            # Ensure error message doesn't leak the payload
            error_msg = str(exc_info.value).lower()
            assert "xss" in error_msg or "invalid" in error_msg or "unsafe" in error_msg
            assert payload not in str(exc_info.value)  # Don't leak payload in error
    
    @pytest.mark.asyncio
    @pytest.mark.xss
    @pytest.mark.critical
    async def test_xss_in_task_creation(self, xss_payloads):
        """Test XSS prevention in task creation."""
        for payload in xss_payloads:
            # Test in task title
            with pytest.raises(ValidationError):
                Task(
                    title=payload,
                    description="Safe description"
                )
            
            # Test in task description  
            with pytest.raises(ValidationError):
                Task(
                    title="Safe title",
                    description=payload
                )
    
    @pytest.mark.asyncio
    @pytest.mark.xss
    async def test_encoded_xss_payload_detection(self):
        """Test detection of encoded XSS payloads."""
        encoded_payloads = [
            # URL encoding
            "%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E",
            "%3CSCRIPT%3Ealert%28%27xss%27%29%3C%2FSCRIPT%3E",
            
            # HTML entity encoding
            "&lt;script&gt;alert('xss')&lt;/script&gt;",
            "&#60;script&#62;alert('xss')&#60;/script&#62;",
            "&#x3C;script&#x3E;alert('xss')&#x3C;/script&#x3E;",
            
            # Double encoding
            "%253Cscript%253Ealert%2528%2527xss%2527%2529%253C%252Fscript%253E",
            
            # Unicode encoding
            "\u003cscript\u003ealert('xss')\u003c/script\u003e",
            "\\u003cscript\\u003ealert('xss')\\u003c/script\\u003e",
            
            # Base64 encoding
            "PHNjcmlwdD5hbGVydCgneHNzJyk8L3NjcmlwdD4=",  # <script>alert('xss')</script>
        ]
        
        for payload in encoded_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "content", max_length=1000)
    
    @pytest.mark.asyncio
    @pytest.mark.xss
    async def test_dom_based_xss_prevention(self):
        """Test prevention of DOM-based XSS vectors."""
        dom_xss_payloads = [
            "javascript:alert('xss')",
            "vbscript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgneHNzJyk8L3NjcmlwdD4=",
            "about:blank",
            "javascript:void(0)",
            "javascript:/**/alert('xss')",
            "javascript:eval('alert(\"xss\")')",
        ]
        
        for payload in dom_xss_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "url", max_length=500)
                
            # Also test as part of larger content
            with pytest.raises(ValidationError):
                validate_string_input(f"Click here: {payload}", "content", max_length=1000)
    
    @pytest.mark.asyncio 
    @pytest.mark.xss
    async def test_css_injection_prevention(self):
        """Test prevention of CSS injection attacks."""
        css_injection_payloads = [
            "<style>body{background:url('javascript:alert(\"xss\")')}</style>",
            "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",
            "@import 'javascript:alert(\"xss\")';",
            "expression(alert('xss'))",
            "url('javascript:alert(\"xss\")')",
            "background: url(javascript:alert('xss'))",
            "style=\"background: url('javascript:alert(\\\"xss\\\")')\""
        ]
        
        for payload in css_injection_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "style", max_length=1000)
    
    @pytest.mark.asyncio
    @pytest.mark.xss
    async def test_filter_evasion_techniques(self):
        """Test XSS filter evasion technique detection."""
        evasion_payloads = [
            # Null byte injection
            "<script\x00>alert('xss')</script>",
            "<script\u0000>alert('xss')</script>",
            
            # Case variations
            "<ScRiPt>alert('xss')</ScRiPt>",
            "<SCRIPT>alert('xss')</SCRIPT>",
            
            # Whitespace variations
            "< script >alert('xss')< / script >",
            "<\tscript\t>alert('xss')<\t/\tscript\t>",
            "<\nscript\n>alert('xss')<\n/\nscript\n>",
            "<\rscript\r>alert('xss')<\r/\rscript\r>",
            
            # Comment injection
            "<script>/**/alert('xss')/**/</script>",
            "<script><!-- -->alert('xss')<!-- --></script>",
            
            # Fragmented tags
            "<scr<script>ipt>alert('xss')</script>",
            "<<script>script>alert('xss')<</script>/script>",
            
            # Alternative event handlers
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "<body onload=alert('xss')>",
            "<iframe onload=alert('xss')>",
        ]
        
        for payload in evasion_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "content", max_length=1000)


class TestSQLInjectionPrevention:
    """Test SQL injection prevention (even with SQLite)."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_sql_injection_patterns(self):
        """Test SQL injection pattern detection in inputs."""
        sql_injection_payloads = [
            # Classic SQL injection
            "'; DROP TABLE tasks; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            
            # Union-based injection
            "' UNION SELECT * FROM users --",
            "' UNION ALL SELECT NULL,NULL,NULL --",
            "1' UNION SELECT username,password FROM users--",
            
            # Boolean-based blind injection
            "' AND (SELECT COUNT(*) FROM tasks) > 0 --",
            "' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 64 --",
            
            # Time-based blind injection
            "'; WAITFOR DELAY '00:00:10' --",
            "' OR SLEEP(10) --",
            "'; SELECT pg_sleep(10) --",
            
            # Error-based injection
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
            
            # SQLite specific
            "'; UPDATE sqlite_master SET sql='evil' WHERE type='table' --",
            "' AND (SELECT sql FROM sqlite_master WHERE type='table') --",
        ]
        
        for payload in sql_injection_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "search_query", max_length=500)
            
            # Also test in other contexts
            with pytest.raises(ValidationError):
                validate_task_id(payload)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_parameterized_query_safe_inputs(self):
        """Test that safe inputs for parameterized queries are allowed."""
        safe_inputs = [
            "normal task title",
            "Task with numbers 123",
            "Task-with-dashes_and_underscores",
            "Task with (parentheses) and [brackets]",
            "O'Reilly task title",  # Single quote in normal context
            "50% complete task",
            "Task #123 for project X",
        ]
        
        for safe_input in safe_inputs:
            try:
                # These should pass validation
                result = validate_string_input(safe_input, "title", max_length=255)
                assert result == safe_input or isinstance(result, str)
            except ValidationError:
                pytest.fail(f"Safe input '{safe_input}' was incorrectly rejected")


class TestCommandInjectionPrevention:
    """Test command injection prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.critical
    async def test_command_injection_prevention(self, command_injection_payloads):
        """Test command injection payload rejection."""
        for payload in command_injection_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "filename", max_length=255)
            
            # Test in path context
            with pytest.raises(ValidationError):
                validate_file_path(payload, "/safe/base/path", "file_path")
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_shell_metacharacter_detection(self):
        """Test detection of shell metacharacters."""
        shell_metacharacters = [
            "file; rm -rf /",
            "file && cat /etc/passwd",
            "file || whoami",
            "file | cat",
            "file > /tmp/evil",
            "file < /etc/passwd",
            "file `whoami`",
            "file $(whoami)",
            "file & background_command",
            "file\nrm -rf /",
            "file\r\nformat C:",
        ]
        
        for payload in shell_metacharacters:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "command", max_length=255)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_environment_variable_injection(self):
        """Test environment variable injection prevention."""
        env_injection_payloads = [
            "${PATH}",
            "$HOME/evil",
            "$(env)",
            "`env`",
            "%PATH%",
            "%USERPROFILE%\\evil",
            "$IFS$()cat$IFS/etc/passwd",
            "${HOME:0:1}etc/passwd",
        ]
        
        for payload in env_injection_payloads:
            with pytest.raises(ValidationError):
                validate_file_path(payload, "/safe/base", "path")


class TestJSONInjectionPrevention:
    """Test JSON injection and manipulation prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_json_structure_injection(self, json_injection_payloads):
        """Test JSON structure injection prevention."""
        for payload in json_injection_payloads:
            # Test direct string validation
            with pytest.raises(ValidationError):
                validate_string_input(payload, "json_data", max_length=10000)
            
            # Test as part of larger JSON
            malicious_json = f'{{"title": "normal", "data": {payload}}}'
            with pytest.raises(ValidationError):
                validate_string_input(malicious_json, "json_content", max_length=10000)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_prototype_pollution_prevention(self):
        """Test prototype pollution attack prevention."""
        prototype_pollution_payloads = [
            '{"__proto__": {"admin": true}}',
            '{"constructor": {"prototype": {"admin": true}}}',
            '{"__proto__.admin": "true"}',
            '{"constructor.prototype.admin": "true"}',
            '{"__defineGetter__": "admin"}',
            '{"__defineSetter__": "admin"}',
            '{"__lookupGetter__": "admin"}',
            '{"__lookupSetter__": "admin"}',
        ]
        
        for payload in prototype_pollution_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "json_config", max_length=1000)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_json_deserialization_attacks(self):
        """Test JSON deserialization attack prevention."""
        deserialization_payloads = [
            '{"$$CLASS$$": "java.lang.Runtime"}',
            '{"@class": "java.lang.Runtime"}',
            '{"_class": "subprocess.Popen"}',
            '{"__class__": "os.system"}',
            '{"rce": {"@type": "java.lang.Class"}}',
            '{"exploit": {"javaClass": "java.lang.Runtime"}}',
        ]
        
        for payload in deserialization_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "serialized_data", max_length=1000)


class TestUnicodeAttackPrevention:
    """Test Unicode-based attack prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_unicode_normalization_attacks(self, security_test_utils):
        """Test Unicode normalization attack prevention."""
        # Get malformed Unicode strings
        malformed_unicode = security_test_utils.generate_malformed_unicode()
        
        for payload in malformed_unicode:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "unicode_content", max_length=255)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_homograph_attacks(self):
        """Test homograph attack prevention."""
        homograph_payloads = [
            # Cyrillic characters that look like Latin
            "аdmin",  # 'а' is Cyrillic
            "раssword",  # 'а' and 'р' are Cyrillic
            
            # Mixed scripts
            "admin＠example.com",  # Full-width @ symbol
            "test＿user",  # Full-width underscore
            
            # Zero-width characters
            "admin\u200badmin",  # Zero-width space
            "test\u2060user",    # Word joiner
            "user\ufeffname",    # Zero-width no-break space
            
            # Bidirectional override
            "admin\u202egnissapword",  # Right-to-left override
            "user\u202dname",          # Left-to-right override
        ]
        
        for payload in homograph_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "username", max_length=255)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_control_character_filtering(self):
        """Test control character filtering."""
        control_char_payloads = [
            "test\x00null",      # Null byte
            "test\x01control",   # Start of heading
            "test\x08backspace", # Backspace
            "test\x0bvtab",      # Vertical tab
            "test\x0cformfeed",  # Form feed
            "test\x1besc",       # Escape
            "test\x7fdel",       # Delete
        ]
        
        for payload in control_char_payloads:
            with pytest.raises(ValidationError):
                validate_string_input(payload, "content", max_length=255)


class TestInputLengthValidation:
    """Test input length and size validation."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_maximum_length_enforcement(self):
        """Test maximum length enforcement."""
        # Test normal length (should pass)
        normal_input = "a" * 100
        result = validate_string_input(normal_input, "title", max_length=255)
        assert len(result) == 100
        
        # Test exceeding maximum length
        too_long_input = "a" * 1000
        with pytest.raises(ValidationError) as exc_info:
            validate_string_input(too_long_input, "title", max_length=255)
        
        assert "length" in str(exc_info.value).lower()
        assert "255" in str(exc_info.value)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_empty_input_handling(self):
        """Test empty input handling."""
        empty_inputs = ["", None, "   ", "\t\n\r"]
        
        for empty_input in empty_inputs:
            # Some fields may allow empty, others may not
            try:
                result = validate_string_input(empty_input, "optional_field", max_length=255, required=False)
                # If allowed, should return cleaned version
                assert result is not None
            except ValidationError:
                # If not allowed, should raise ValidationError
                pass
            
            # Required fields should always reject empty
            with pytest.raises(ValidationError):
                validate_string_input(empty_input, "required_field", max_length=255, required=True)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.performance
    async def test_large_input_performance(self, performance_monitor, dos_attack_simulator):
        """Test performance with large inputs."""
        performance_monitor.start_monitoring()
        
        # Generate progressively larger inputs
        large_inputs = [
            dos_attack_simulator.generate_large_payload(0.1),  # 100KB
            dos_attack_simulator.generate_large_payload(1.0),  # 1MB
            dos_attack_simulator.generate_large_payload(5.0),  # 5MB
        ]
        
        for large_input in large_inputs:
            # Should reject large inputs quickly
            with pytest.raises(ValidationError):
                validate_string_input(large_input, "content", max_length=1000)
        
        # Validation should be fast even for large inputs
        performance_monitor.assert_performance_limits(
            max_execution_time=2.0,
            max_memory_mb=100.0,
            max_cpu_percent=50.0
        )


class TestTypeConfusionPrevention:
    """Test type confusion attack prevention."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_type_confusion_attacks(self):
        """Test type confusion attack prevention."""
        # Test various non-string types that might bypass validation
        type_confusion_payloads = [
            123,               # Integer
            123.45,            # Float
            True,              # Boolean
            [],                # List
            {},                # Dict
            object(),          # Object
            lambda x: x,       # Function
        ]
        
        for payload in type_confusion_payloads:
            with pytest.raises((ValidationError, TypeError)):
                validate_string_input(payload, "title", max_length=255)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_object_injection_prevention(self):
        """Test object injection prevention."""
        # Simulate attempts to inject objects instead of strings
        object_payloads = [
            {"toString": lambda: "<script>alert('xss')</script>"},
            {"valueOf": lambda: "../../etc/passwd"},
            {"__str__": lambda: "malicious_string"},
        ]
        
        for payload in object_payloads:
            with pytest.raises((ValidationError, TypeError, AttributeError)):
                validate_string_input(payload, "content", max_length=255)


class TestContextualValidation:
    """Test contextual validation based on field purpose."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_email_context_validation(self):
        """Test email-specific validation."""
        # Valid emails should pass
        valid_emails = [
            "user@example.com",
            "test.user+tag@domain.co.uk",
            "user123@subdomain.example.org",
        ]
        
        for email in valid_emails:
            result = validate_string_input(email, "email", max_length=255)
            assert "@" in result
        
        # Invalid/malicious emails should be rejected
        malicious_emails = [
            "user@example.com<script>alert('xss')</script>",
            "user'; DROP TABLE users; --@example.com",
            "user@javascript:alert('xss')",
            "user@../../../etc/passwd",
        ]
        
        for email in malicious_emails:
            with pytest.raises(ValidationError):
                validate_string_input(email, "email", max_length=255)
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    async def test_url_context_validation(self):
        """Test URL-specific validation."""
        # Valid URLs should pass
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.org/path",
            "ftp://files.example.com/file.txt",
        ]
        
        for url in valid_urls:
            result = validate_string_input(url, "url", max_length=500)
            assert "://" in result
        
        # Malicious URLs should be rejected
        malicious_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "http://example.com/../../etc/passwd",
            "https://evil.com/xss?<script>alert('xss')</script>",
        ]
        
        for url in malicious_urls:
            with pytest.raises(ValidationError):
                validate_string_input(url, "url", max_length=500)


class TestValidationPerformance:
    """Test validation performance under various conditions."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.performance
    async def test_validation_performance_under_load(self, performance_monitor, xss_payloads):
        """Test validation performance under load."""
        performance_monitor.start_monitoring()
        
        # Validate many inputs rapidly
        for i in range(100):
            # Test safe input
            safe_input = f"safe_input_{i}"
            result = validate_string_input(safe_input, "title", max_length=255)
            assert result == safe_input
            
            # Test malicious input (should be fast to reject)
            if i < len(xss_payloads):
                with pytest.raises(ValidationError):
                    validate_string_input(xss_payloads[i], "title", max_length=255)
        
        # Validation should be fast
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=10.0,
            max_cpu_percent=30.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.performance  
    async def test_regex_dos_prevention(self, performance_monitor):
        """Test prevention of ReDoS (Regular Expression DoS) attacks."""
        performance_monitor.start_monitoring()
        
        # Inputs designed to cause exponential regex backtracking
        redos_payloads = [
            "a" * 1000 + "X",  # Should not match, but cause backtracking
            "(" * 100 + "a" * 100 + ")" * 100,  # Nested groups
            "a" * 50 + "b" * 50 + "c",  # Pattern that causes backtracking
            "x" * 100 + "y" * 100 + "z",  # Another backtracking pattern
        ]
        
        for payload in redos_payloads:
            # Should either validate quickly or reject quickly
            try:
                validate_string_input(payload, "content", max_length=10000)
            except ValidationError:
                pass  # Expected for many payloads
        
        # Should not take excessive time even with crafted inputs
        performance_monitor.assert_performance_limits(
            max_execution_time=2.0,  # Fast rejection important for DoS prevention
            max_memory_mb=20.0,
            max_cpu_percent=50.0
        )


# Integration tests combining multiple validation types
class TestInputValidationIntegration:
    """Integration tests combining multiple validation techniques."""
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.integration
    async def test_comprehensive_input_validation(self, xss_payloads, command_injection_payloads, performance_monitor):
        """Test comprehensive input validation across all categories."""
        performance_monitor.start_monitoring()
        
        all_malicious_payloads = xss_payloads + command_injection_payloads
        
        # Test each payload in different contexts
        contexts = ["title", "description", "filename", "url", "email", "content"]
        
        validation_count = 0
        for context in contexts:
            for payload in all_malicious_payloads[:10]:  # Limit for performance
                with pytest.raises(ValidationError):
                    validate_string_input(payload, context, max_length=1000)
                validation_count += 1
        
        # Should handle many validations efficiently
        assert validation_count > 50
        performance_monitor.assert_performance_limits(
            max_execution_time=10.0,
            max_memory_mb=25.0,
            max_cpu_percent=60.0
        )
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.integration
    async def test_safe_input_flow(self):
        """Test that safe inputs flow through validation correctly."""
        safe_inputs = [
            ("Normal task title", "title"),
            ("This is a safe description with normal content.", "description"),
            ("safe_filename.txt", "filename"),
            ("https://example.com/safe/path", "url"),
            ("user@example.com", "email"),
            ("Safe content with normal text and numbers 123.", "content"),
        ]
        
        for safe_input, context in safe_inputs:
            try:
                result = validate_string_input(safe_input, context, max_length=500)
                # Should return string (possibly sanitized)
                assert isinstance(result, str)
                assert len(result) > 0
            except ValidationError as e:
                pytest.fail(f"Safe input '{safe_input}' in context '{context}' was incorrectly rejected: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.input_validation
    @pytest.mark.integration
    async def test_edge_case_combinations(self):
        """Test edge case combinations of validation rules."""
        edge_cases = [
            # Unicode + XSS
            "\u003cscript\u003ealert('xss')\u003c/script\u003e",
            
            # Long input + XSS  
            "<script>alert('xss')</script>" + "a" * 1000,
            
            # Command injection + Path traversal
            "../../../etc/passwd; cat /etc/shadow",
            
            # JSON injection + XSS
            '{"xss": "<script>alert(\'xss\')</script>"}',
            
            # Multiple encoding layers
            "%253Cscript%253Ealert%2528%2527xss%2527%2529%253C%252Fscript%253E",
        ]
        
        for edge_case in edge_cases:
            with pytest.raises(ValidationError):
                validate_string_input(edge_case, "mixed_content", max_length=2000)