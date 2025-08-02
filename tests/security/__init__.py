"""
Security Test Suite for MCP Task Orchestrator

This package contains comprehensive security tests for the MCP Task Orchestrator,
validating all security measures including authentication, authorization, input
validation, path traversal protection, information disclosure prevention, and
attack vector simulation.

Test Categories:
- Authentication: API key validation, rate limiting, brute force protection
- Authorization: RBAC enforcement, privilege escalation prevention
- Input Validation: XSS, SQL injection, command injection protection
- Path Traversal: Directory traversal and file system security
- Information Disclosure: Error sanitization and debug leakage prevention
- Attack Vectors: Comprehensive multi-vector attack simulation
- Performance Security: DoS and resource exhaustion protection

Usage:
    # Run all security tests
    pytest tests/security/ -v

    # Run specific security category
    pytest tests/security/ -m authentication -v
    pytest tests/security/ -m xss -v
    pytest tests/security/ -m critical -v

    # Run with coverage
    pytest tests/security/ --cov=mcp_task_orchestrator.infrastructure.security

Security Test Markers:
    @pytest.mark.security - All security tests
    @pytest.mark.authentication - Authentication tests
    @pytest.mark.authorization - Authorization tests
    @pytest.mark.xss - XSS prevention tests
    @pytest.mark.path_traversal - Path security tests
    @pytest.mark.performance - Performance security tests
    @pytest.mark.critical - Critical security tests
"""

__version__ = "1.0.0"
__author__ = "MCP Task Orchestrator Security Team"

# Security test categories
SECURITY_TEST_CATEGORIES = {
    "authentication": "API key validation and authentication flow tests",
    "authorization": "RBAC and permission enforcement tests", 
    "input_validation": "XSS, injection, and input sanitization tests",
    "path_traversal": "Directory traversal and file system security tests",
    "information_disclosure": "Error sanitization and information leakage tests",
    "attack_vectors": "Multi-vector attack simulation tests",
    "performance_security": "DoS and resource exhaustion tests"
}

# Critical security tests that must always pass
CRITICAL_SECURITY_TESTS = [
    "test_api_key_validation",
    "test_xss_prevention",
    "test_path_traversal_protection", 
    "test_error_sanitization",
    "test_privilege_escalation_prevention"
]