
# CLI PROMPT: Comprehensive Security Test Suite for MCP Task Orchestrator

#

# MISSION

Build a complete security test suite for the MCP Task Orchestrator's security infrastructure, covering authentication, authorization, input validation, path traversal prevention, and audit logging. Implement rigorous testing until all components are proven to work in actual use.

#

# PROJECT CONTEXT

#

## Architecture Overview

The MCP Task Orchestrator follows Clean Architecture with these layers:

- **Domain**: `mcp_task_orchestrator/domain/` - Business logic and entities

- **Application**: `mcp_task_orchestrator/application/` - Use cases and workflows  

- **Infrastructure**: `mcp_task_orchestrator/infrastructure/` - External concerns

- **Presentation**: `mcp_task_orchestrator/presentation/` - MCP server and CLI

#

## Security Infrastructure Location

All security components are in `mcp_task_orchestrator/infrastructure/security/`:

1. **`authentication.py`** - API key management with SHA256 hashing

2. **`authorization.py`** - Role-Based Access Control (RBAC) system

3. **`validators.py`** - XSS and injection prevention, path traversal protection

4. **`audit_logger.py`** - Security event logging and monitoring

5. **`error_sanitization.py`** - Error mapping to prevent information disclosure

6. **`__init__.py`** - Unified security framework exports

#

## Existing Test Structure

Current tests are in `tests/` directory with:

- `tests/unit/` - Unit tests

- `tests/integration/` - Integration tests

- `tests/CLAUDE.md` - Testing guidance

#

# DETAILED IMPLEMENTATION REQUIREMENTS

#

## Phase 1: Test Structure Creation

Create the following directory structure:

```text
tests/security/
├── __init__.py
├── conftest.py                          
# Shared fixtures
├── test_authentication.py               
# API key management tests
├── test_authorization.py                
# RBAC system tests  
├── test_validators.py                   
# Input validation tests
├── test_audit_logger.py                
# Security logging tests
├── test_error_sanitization.py          
# Error mapping tests
├── test_integration_security.py        
# End-to-end security tests
├── test_security_performance.py        
# Performance under attack
├── fixtures/                           
# Test data and fixtures
│   ├── __init__.py
│   ├── security_test_data.py          
# Attack vectors and test data
│   └── mock_security_contexts.py      
# Mock authentication contexts
└── attack_vectors/                     
# Security test payloads
    ├── xss_payloads.py                
# Cross-site scripting vectors
    ├── injection_payloads.py          
# SQL/command injection vectors
    └── path_traversal_payloads.py     
# Directory traversal vectors
```text

#
## Phase 2: Authentication Testing (`test_authentication.py`)

**Test Coverage Requirements:**
```text
python
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

from mcp_task_orchestrator.infrastructure.security import (
    APIKeyManager, generate_api_key, validate_api_key, 
    require_auth, AuthenticationError
)

class TestAPIKeyManager:
    """Test suite for API key management system."""
    
    def test_api_key_generation(self):
        """Test secure API key generation with proper entropy."""
        
# Test basic key generation
        
# Test key with expiration
        
# Test key with custom metadata
        
# Verify key format and entropy
        
    def test_api_key_hashing(self):
        """Test SHA256 hashing of API keys."""
        
# Test hash consistency  
        
# Test hash uniqueness
        
# Verify no plain text storage
        
    def test_api_key_validation(self):
        """Test API key validation logic."""
        
# Test valid key validation
        
# Test expired key rejection
        
# Test invalid key rejection
        
# Test usage count tracking
        
    def test_api_key_storage(self):
        """Test persistent storage of API keys."""
        
# Test key storage and retrieval
        
# Test file permissions
        
# Test storage location security
        
    def test_authentication_decorator(self):
        """Test @require_auth decorator functionality."""
        
# Test successful authentication
        
# Test authentication failure
        
# Test decorator with async functions
        
# Test authentication metadata injection
        
    def test_authentication_edge_cases(self):
        """Test edge cases and error conditions."""
        
# Test malformed API keys
        
# Test concurrent access
        
# Test storage corruption handling
        
# Test memory exhaustion protection

```text

**Specific Test Requirements:**

- **Attack Vector Testing**: Include malformed keys, injection attempts in key data

- **Concurrent Access**: Test thread safety of key validation

- **Performance Testing**: Validate response times under load

- **Security Validation**: Ensure no key material leaks in logs or errors

#
## Phase 3: Authorization Testing (`test_authorization.py`)

**Test Coverage Requirements:**
```text
python
import pytest
from mcp_task_orchestrator.infrastructure.security import (
    Permission, Role, RoleManager, UserRoleManager,
    require_permission, require_role, has_permission,
    AuthorizationError
)

class TestRoleBasedAccessControl:
    """Test suite for RBAC authorization system."""
    
    def test_role_hierarchy(self):
        """Test role hierarchy and inheritance."""
        
# Test role creation and hierarchy
        
# Test permission inheritance
        
# Test role comparison and ordering
        
    def test_permission_checking(self):
        """Test permission validation logic."""
        
# Test specific permission checks
        
# Test permission aggregation
        
# Test permission delegation
        
    def test_authorization_decorators(self):
        """Test authorization decorator functions."""
        
# Test @require_permission decorator
        
# Test @require_role decorator  
        
# Test decorator composition
        
# Test error handling in decorators
        
    def test_user_role_management(self):
        """Test user-role assignment and management."""
        
# Test role assignment
        
# Test role revocation
        
# Test multiple roles per user
        
# Test role persistence
        
    def test_rbac_edge_cases(self):
        """Test RBAC edge cases and security boundaries."""
        
# Test privilege escalation attempts
        
# Test role tampering attempts
        
# Test authorization bypass attempts
        
# Test concurrent role modifications

```text

#
## Phase 4: Input Validation Testing (`test_validators.py`)

**Critical Test Coverage:**
```text
python
import pytest
from mcp_task_orchestrator.infrastructure.security import (
    validate_string_input, validate_file_path, validate_task_id,
    is_safe_input, ValidationError
)
from .attack_vectors.xss_payloads import XSS_PAYLOADS
from .attack_vectors.injection_payloads import INJECTION_PAYLOADS
from .attack_vectors.path_traversal_payloads import PATH_TRAVERSAL_PAYLOADS

class TestInputValidation:
    """Comprehensive input validation security testing."""
    
    @pytest.mark.parametrize("xss_payload", XSS_PAYLOADS)
    def test_xss_prevention(self, xss_payload):
        """Test XSS attack prevention across all input vectors."""
        
# Test script tag injection
        
# Test event handler injection
        
# Test encoded payload injection
        
# Test polyglot payload injection
        
    @pytest.mark.parametrize("injection_payload", INJECTION_PAYLOADS)  
    def test_injection_prevention(self, injection_payload):
        """Test SQL/command injection prevention."""
        
# Test SQL injection attempts
        
# Test command injection attempts
        
# Test LDAP injection attempts
        
# Test NoSQL injection attempts
        
    @pytest.mark.parametrize("traversal_payload", PATH_TRAVERSAL_PAYLOADS)
    def test_path_traversal_prevention(self, traversal_payload):
        """Test path traversal attack prevention."""
        
# Test directory traversal attempts
        
# Test absolute path injection
        
# Test symlink exploitation
        
# Test Unicode bypass attempts
        
    def test_input_sanitization(self):
        """Test input sanitization effectiveness."""
        
# Test whitespace handling
        
# Test encoding normalization
        
# Test length limit enforcement
        
# Test special character handling
        
    def test_validation_performance(self):
        """Test validation performance under load."""
        
# Test large input handling
        
# Test repeated validation calls
        
# Test memory usage during validation
        
# Test DoS resilience

```text

**Attack Vector Data Files:**
Create `tests/security/attack_vectors/xss_payloads.py`:
```text
python
"""XSS attack vectors for security testing."""

XSS_PAYLOADS = [
    
# Basic script injection
    "<script>alert('XSS')</script>",
    "<script>console.log('XSS')</script>",
    
    
# Event handler injection  
    "<img src=x onerror=alert('XSS')>",
    "<body onload=alert('XSS')>",
    
    
# Encoded payloads
    "%3Cscript%3Ealert('XSS')%3C/script%3E",
    "&#60;script&#62;alert('XSS')&#60;/script&#62;",
    
    
# Advanced vectors
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>",
    "<iframe src=javascript:alert('XSS')>",
    
    
# Polyglot payloads
    "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */onerror=alert('XSS') )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert('XSS')//\\x3e",
]

```text

#
## Phase 5: Integration Testing (`test_integration_security.py`)

**End-to-End Security Tests:**
```text
python
import pytest
import asyncio
from unittest.mock import patch
from mcp_task_orchestrator.infrastructure.security import (
    secure_mcp_handler, initialize_security, get_security_status
)

class TestSecurityIntegration:
    """Test complete security framework integration."""
    
    def test_secure_mcp_handler_flow(self):
        """Test complete MCP handler security flow."""
        
# Test successful authentication + authorization
        
# Test authentication failure handling
        
# Test authorization failure handling
        
# Test error sanitization integration
        
    def test_security_framework_initialization(self):
        """Test security framework startup and configuration."""
        
# Test component initialization order
        
# Test configuration loading
        
# Test dependency resolution
        
# Test failure recovery
        
    def test_audit_logging_integration(self):
        """Test security audit logging across all components."""
        
# Test authentication event logging
        
# Test authorization event logging
        
# Test validation failure logging
        
# Test log integrity and tamper detection
        
    def test_error_sanitization_integration(self):
        """Test error sanitization with all security components."""
        
# Test sanitized authentication errors
        
# Test sanitized authorization errors
        
# Test sanitized validation errors
        
# Test information disclosure prevention
        
    def test_performance_under_attack(self):
        """Test system performance under security stress."""
        
# Test brute force attack resilience
        
# Test DoS attack resilience
        
# Test resource exhaustion protection
        
# Test concurrent attack handling

```text

#
## Phase 6: Performance and Load Testing (`test_security_performance.py`)

**Performance Requirements:**
```text
python
import pytest
import time
import concurrent.futures
from mcp_task_orchestrator.infrastructure.security import validate_api_key

class TestSecurityPerformance:
    """Test security system performance under load."""
    
    def test_authentication_performance(self):
        """Test authentication performance benchmarks."""
        
# Target: <50ms per validation
        
# Test concurrent validations
        
# Test cache effectiveness
        
# Test memory usage patterns
        
    def test_validation_performance(self):
        """Test input validation performance."""
        
# Target: <10ms per validation
        
# Test large input handling
        
# Test complex pattern matching
        
# Test DoS resilience
        
    def test_concurrent_access_performance(self):
        """Test performance under concurrent access."""
        
# Test thread safety performance
        
# Test lock contention
        
# Test scalability limits
        
# Test degradation patterns

```text

#
# IMPLEMENTATION METHODOLOGY

#
## Step 1: Environment Setup

1. Read all security module files to understand the APIs

2. Create test directory structure

3. Set up pytest configuration and fixtures

4. Create shared test utilities

#
## Step 2: Component Testing

1. Implement authentication tests with real API key generation/validation

2. Implement authorization tests with actual permission checking

3. Implement validation tests with comprehensive attack vectors

4. Implement audit logging tests with log verification

5. Implement error sanitization tests with information disclosure checks

#
## Step 3: Integration Testing

1. Test complete security flows end-to-end

2. Test error handling across component boundaries

3. Test performance under realistic load

4. Test security under attack conditions

#
## Step 4: Validation and Hardening

1. Run all tests and achieve 100% pass rate

2. Measure test coverage and achieve >95% coverage

3. Run performance benchmarks and meet targets

4. Document security test results and recommendations

#
# SUCCESS CRITERIA

#
## Functional Requirements

- [ ] All security components have comprehensive test coverage (>95%)

- [ ] All tests pass consistently

- [ ] Attack vector tests demonstrate protection effectiveness  

- [ ] Performance tests meet defined benchmarks

- [ ] Integration tests validate end-to-end security flows

- [ ] Error handling tests prevent information disclosure

#
## Security Requirements  

- [ ] XSS attack vectors are blocked and logged

- [ ] Injection attack vectors are prevented

- [ ] Path traversal attacks are stopped

- [ ] Authentication bypasses are impossible

- [ ] Authorization escalation is prevented

- [ ] Audit logs capture all security events

#
## Performance Requirements

- [ ] API key validation: <50ms per operation

- [ ] Input validation: <10ms per operation  

- [ ] Concurrent operations scale without degradation

- [ ] System remains responsive under attack load

- [ ] Memory usage stays within acceptable bounds

#
# VALIDATION STEPS

#
## 1. Run Complete Test Suite

```text
bash

# Run all security tests

pytest tests/security/ -v --tb=short

# Run with coverage measurement

pytest tests/security/ --cov=mcp_task_orchestrator.infrastructure.security --cov-report=html

# Run performance tests

pytest tests/security/test_security_performance.py -v --tb=short

```text

#
## 2. Security Validation

```text
bash  

# Test against attack vectors

pytest tests/security/test_validators.py -k "test_xss" -v
pytest tests/security/test_validators.py -k "test_injection" -v
pytest tests/security/test_validators.py -k "test_path_traversal" -v

```text

#
## 3. Integration Validation

```text
bash

# Test complete security framework

pytest tests/security/test_integration_security.py -v

# Test error handling

python -c "
from mcp_task_orchestrator.infrastructure.security import get_security_status
print('Security Status:', get_security_status())
"
```text

#
# CRITICAL IMPLEMENTATION NOTES

1. **Read Security Modules First**: Start by reading all files in `mcp_task_orchestrator/infrastructure/security/` to understand the APIs and patterns.

2. **Use Real Components**: Do not mock security components - test the actual implementations to validate real security effectiveness.

3. **Attack Vector Focus**: The XSS, injection, and path traversal tests are critical - these must demonstrate actual protection.

4. **Performance Validation**: Security cannot compromise performance - all benchmarks must be met.

5. **Integration Testing**: Test the complete `@secure_mcp_handler` decorator flow with real authentication and authorization.

6. **Error Handling**: Verify that security errors are properly sanitized and don't leak sensitive information.

7. **Audit Logging**: Ensure all security events are properly logged with sufficient detail for security monitoring.

#
# EXPECTED DELIVERABLES

Upon completion, you should have:

- Complete test suite in `tests/security/` with 100% passing tests

- Attack vector datasets proving security effectiveness  

- Performance benchmarks meeting defined targets

- Integration tests validating end-to-end security

- Comprehensive documentation of security test coverage

- Evidence that the security framework functions correctly in actual use

#
# FINAL VALIDATION

Before declaring success:

1. Run the complete test suite and achieve 100% pass rate

2. Verify attack vectors are actually blocked (not just handled)

3. Confirm performance benchmarks are met under load

4. Test the security framework with the actual MCP server

5. Validate that audit logs are generated correctly

6. Ensure error sanitization prevents information disclosure

The goal is a production-ready security test suite that proves the MCP Task Orchestrator's security infrastructure is robust, performant, and effective against real-world attacks.
