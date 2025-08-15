
# Security Test Suite

#
# Overview

The MCP Task Orchestrator Security Test Suite provides comprehensive validation of all security measures implemented in the system. This test suite covers authentication, authorization, input validation, path traversal protection, information disclosure prevention, and attack vector simulation.

#
# Test Structure

```text
tests/security/
├── __init__.py                    
# Security test package initialization
├── conftest.py                   
# Security test fixtures and utilities
├── test_authentication.py       
# API key validation and authentication tests
├── test_authorization.py        
# RBAC and permission enforcement tests
├── test_input_validation.py     
# XSS, injection, and input sanitization tests
├── test_path_traversal.py       
# Directory traversal and file system security tests
├── test_information_disclosure.py 
# Error sanitization and information leakage tests
├── test_attack_vectors.py       
# Multi-vector attack simulation tests
├── test_performance_security.py 
# DoS and resource exhaustion tests
└── README.md                    
# This documentation

```text

#
# Test Categories

#
## 1. Authentication Tests (`test_authentication.py`)

**Purpose**: Validate API key authentication, rate limiting, and session management security.

**Key Test Areas**:

- API key validation (valid, invalid, malformed, expired)

- Rate limiting on authentication attempts

- Brute force protection

- Session management security

- Timing attack mitigation

**Critical Tests**:

- `test_valid_api_key_authentication`

- `test_invalid_api_key_rejection`

- `test_expired_api_key_rejection`

- `test_brute_force_protection`

#
## 2. Authorization Tests (`test_authorization.py`)

**Purpose**: Validate Role-Based Access Control (RBAC) and permission enforcement.

**Key Test Areas**:

- Role hierarchy enforcement

- Permission boundary testing

- Privilege escalation prevention

- Resource access control

- Cross-tenant data isolation

**Critical Tests**:

- `test_basic_permission_enforcement`

- `test_role_hierarchy_enforcement`

- `test_privilege_escalation_prevention`

- `test_secure_mcp_handler_success`

#
## 3. Input Validation Tests (`test_input_validation.py`)

**Purpose**: Validate XSS prevention, SQL injection protection, and input sanitization.

**Key Test Areas**:

- XSS payload rejection (basic, encoded, DOM-based)

- SQL injection prevention

- Command injection protection

- JSON injection detection

- Unicode normalization attacks

- Type confusion prevention

**Critical Tests**:

- `test_basic_xss_payload_rejection`

- `test_xss_in_task_creation`

- `test_command_injection_prevention`

- `test_json_structure_injection`

#
## 4. Path Traversal Tests (`test_path_traversal.py`)

**Purpose**: Validate path traversal protection and file system security.

**Key Test Areas**:

- Directory traversal prevention

- Absolute path injection protection

- Encoded path traversal detection

- Null byte injection prevention

- Symbolic link attack prevention

- Special file access prevention

**Critical Tests**:

- `test_basic_directory_traversal_prevention`

- `test_absolute_path_injection`

- `test_null_byte_path_injection`

- `test_special_file_access_prevention`

#
## 5. Information Disclosure Tests (`test_information_disclosure.py`)

**Purpose**: Validate error message sanitization and sensitive data protection.

**Key Test Areas**:

- Stack trace sanitization

- File path sanitization

- Database schema information removal

- API key and token sanitization

- Debug information suppression

- Timing attack mitigation

**Critical Tests**:

- `test_stack_trace_sanitization`

- `test_file_path_sanitization`

- `test_database_schema_sanitization`

- `test_api_key_sanitization`

#
## 6. Attack Vector Simulation Tests (`test_attack_vectors.py`)

**Purpose**: Simulate comprehensive multi-vector attacks and advanced evasion techniques.

**Key Test Areas**:

- Chained exploit attempts

- Edge case combinations

- Malformed MCP protocol messages

- Advanced evasion techniques

- Resource exhaustion attacks

- Real-world attack scenarios

**Critical Tests**:

- `test_xss_to_path_traversal_chain`

- `test_malformed_json_messages`

- `test_comprehensive_multi_vector_attack`

- `test_sustained_attack_campaign`

#
## 7. Performance Security Tests (`test_performance_security.py`)  

**Purpose**: Validate DoS protection and system stability under attack.

**Key Test Areas**:

- Request flood protection

- Large payload DoS protection

- Algorithmic complexity DoS prevention

- Memory exhaustion prevention

- CPU exhaustion prevention

- Rate limiting effectiveness

- System stability under attack

**Critical Tests**:

- `test_request_flood_protection`

- `test_large_payload_dos_protection`

- `test_memory_exhaustion_prevention`

- `test_graceful_degradation_under_load`

#
# Usage Instructions

#
## Running All Security Tests

```text
bash

# Run all security tests

pytest tests/security/ -v

# Run with coverage

pytest tests/security/ --cov=mcp_task_orchestrator.infrastructure.security --cov-report=html

# Run only critical security tests

pytest tests/security/ -m critical -v

# Run all security tests with detailed output

pytest tests/security/ -v -s --tb=long

```text

#
## Running Specific Test Categories

```text
bash

# Authentication tests

pytest tests/security/ -m authentication -v

# Authorization tests  

pytest tests/security/ -m authorization -v

# XSS prevention tests

pytest tests/security/ -m xss -v

# Path traversal tests

pytest tests/security/ -m path_traversal -v

# Performance security tests

pytest tests/security/ -m performance -v

# Attack simulation tests

pytest tests/security/ -m attack_simulation -v

# Information disclosure tests

pytest tests/security/ -m information_disclosure -v

```text

#
## Running Individual Test Files

```text
bash

# Authentication tests only

pytest tests/security/test_authentication.py -v

# Input validation tests only

pytest tests/security/test_input_validation.py -v

# Performance security tests only

pytest tests/security/test_performance_security.py -v

```text

#
## Running Specific Test Classes or Methods

```text
bash

# Specific test class

pytest tests/security/test_authentication.py::TestAPIKeyValidation -v

# Specific test method

pytest tests/security/test_authentication.py::TestAPIKeyValidation::test_valid_api_key_authentication -v

# Multiple specific tests

pytest tests/security/test_authentication.py::TestAPIKeyValidation::test_valid_api_key_authentication tests/security/test_authorization.py::TestRoleBasedAccessControl::test_basic_permission_enforcement -v

```text

#
# Test Configuration

#
## Environment Variables

```text
bash

# Set environment for testing

export ENVIRONMENT=test

# Enable debug logging for tests

export LOG_LEVEL=DEBUG

# Set test database path

export TEST_DB_PATH=/tmp/test_security.db

```text

#
## Pytest Configuration

The security tests use the following pytest markers (defined in `pytest.ini`):

- `security` - All security tests

- `authentication` - Authentication tests

- `authorization` - Authorization tests  

- `xss` - XSS prevention tests

- `path_traversal` - Path traversal tests

- `critical` - Critical security tests

- `attack_simulation` - Attack simulation tests

- `information_disclosure` - Information disclosure tests

- `input_validation` - Input validation tests

- `performance` - Performance security tests

- `integration` - Integration security tests

#
## Performance Test Configuration

Performance tests include built-in limits:

```text
python

# Default performance limits

max_execution_time = 30.0  
# seconds
max_memory_mb = 100.0      
# megabytes  
max_cpu_percent = 80.0     
# CPU usage percentage

```text

These can be adjusted in the `performance_monitor` fixture in `conftest.py`.

#
# Test Fixtures and Utilities

#
## Key Fixtures

- `temp_api_key_storage` - Temporary API key storage for isolated testing

- `test_api_key_manager` - Isolated API key manager instance

- `valid_api_key` - Valid API key for testing

- `expired_api_key` - Expired API key for testing

- `admin_api_key` - Admin API key with all permissions

- `test_user_basic` - Basic user with minimal permissions

- `test_user_manager` - Manager user with elevated permissions

- `test_user_admin` - Admin user with all permissions

- `mock_mcp_context` - Mock MCP context for testing

- `xss_payloads` - Comprehensive XSS attack payloads

- `path_traversal_payloads` - Path traversal attack payloads

- `command_injection_payloads` - Command injection attack payloads

- `json_injection_payloads` - JSON injection attack payloads

- `performance_monitor` - Performance monitoring utilities

- `dos_attack_simulator` - DoS attack simulation utilities

- `security_test_utils` - General security testing utilities

#
## Utility Functions

- `assert_no_sensitive_data_in_error(error_message)` - Verify error messages don't leak sensitive data

- `simulate_timing_attack(func, *args, **kwargs)` - Measure function execution time

- `generate_malformed_unicode()` - Generate malformed Unicode strings

- `generate_large_payload(size_mb)` - Generate large payloads for testing

- `simulate_request_flood(target_function, request_count, concurrent_limit)` - Simulate request flooding

#
# Security Test Best Practices

#
## 1. Comprehensive Coverage

- Test both positive and negative cases

- Include edge cases and boundary conditions

- Test with various input encodings and formats

- Validate error handling and recovery

#
## 2. Performance Validation

- Include performance limits in all tests

- Monitor resource usage during testing

- Test system behavior under load

- Validate graceful degradation

#
## 3. Realistic Attack Simulation

- Use real-world attack patterns

- Test chained and combined attacks

- Include advanced evasion techniques

- Simulate both automated and targeted attacks

#
## 4. Error Message Validation

- Verify error messages don't leak sensitive information

- Test error message consistency

- Validate timing consistency for security

- Check that debugging information is properly sanitized

#
## 5. Isolation and Cleanup

- Use isolated test environments

- Clean up test data after each test

- Avoid side effects between tests

- Use temporary storage and databases

#
# Interpreting Test Results

#
## Successful Security Tests

All security tests should pass, indicating:

- ✅ Attack payloads are properly blocked

- ✅ Error messages are sanitized

- ✅ Performance remains acceptable under attack

- ✅ Authentication and authorization work correctly

- ✅ No sensitive information is leaked

#
## Failed Security Tests

Failed tests indicate potential security vulnerabilities:

- ❌ Attack payloads not blocked - Review input validation

- ❌ Sensitive data in error messages - Review error sanitization

- ❌ Poor performance under attack - Review DoS protection

- ❌ Authentication/authorization bypass - Review security handlers

- ❌ Information disclosure - Review error handling

#
## Performance Test Failures

Performance test failures may indicate:

- Resource exhaustion vulnerabilities

- Inefficient algorithms under attack

- Missing rate limiting

- Poor graceful degradation

- Memory leaks under load

#
# Continuous Integration

#
## GitHub Actions Configuration

```text
yaml
name: Security Tests

on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run security tests
        run: |
          pytest tests/security/ -v --cov=mcp_task_orchestrator.infrastructure.security
      - name: Run critical security tests
        run: |
          pytest tests/security/ -m critical -v

```text

#
## Pre-commit Hooks

```text
yaml

# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: security-tests
        name: Security Tests
        entry: pytest tests/security/ -m critical
        language: system
        pass_filenames: false

```text

#
# Troubleshooting

#
## Common Issues

**Issue**: Tests fail with `ModuleNotFoundError`
**Solution**: Ensure the package is installed in development mode:
```text
bash
pip install -e ".[dev]"

```text

**Issue**: Performance tests fail with timeout
**Solution**: Adjust timeout limits or check system resources:
```text
bash
pytest tests/security/ --timeout=600  
# 10 minute timeout

```text

**Issue**: Tests fail with "fixture not found"
**Solution**: Ensure you're running from the project root directory and `conftest.py` is present.

**Issue**: Security tests pass but shouldn't
**Solution**: Verify test payloads are correct and security infrastructure is properly imported.

#
## Debug Mode

Run tests with debug information:

```text
bash

# Enable debug logging

pytest tests/security/ -v -s --log-cli-level=DEBUG

# Show full tracebacks

pytest tests/security/ -v --tb=long

# Stop on first failure

pytest tests/security/ -x

```text

#
## Performance Debugging

```text
bash

# Run with performance profiling

pytest tests/security/ --profile

# Monitor resource usage

htop &  
# Run in separate terminal
pytest tests/security/ -m performance
```text

#
# Security Test Maintenance

#
## Regular Updates

- Update attack payloads based on new threat intelligence

- Add tests for newly discovered attack vectors

- Review and update performance limits

- Validate test coverage regularly

#
## Adding New Security Tests

1. Create test in appropriate file

2. Add proper markers (`@pytest.mark.security`, etc.)

3. Use existing fixtures and utilities

4. Include performance validation

5. Add comprehensive documentation

6. Update this README if needed

#
## Test Review Checklist

- [ ] Tests cover both positive and negative cases

- [ ] Attack payloads are comprehensive and current

- [ ] Performance limits are reasonable and enforced

- [ ] Error messages are validated for information disclosure

- [ ] Tests are properly isolated and clean up after themselves

- [ ] Documentation is clear and complete

#
# References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

- [CWE/SANS TOP 25](https://cwe.mitre.org/top25/archive/2023/2023_top25_list.html)

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Last Updated**: 2025-07-23  
**Version**: 1.0.0  
**Maintainer**: MCP Task Orchestrator Security Team
