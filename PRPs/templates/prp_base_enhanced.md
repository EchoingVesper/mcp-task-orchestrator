name: "Enhanced PRP Template v2 - Context Engineering with Security-First Design"
description: |

#
# Purpose

**Enhanced PRP Template** optimized for AI agents to implement production-ready features using proven context engineering principles, security-first design, and systematic validation frameworks.

#
# Core Context Engineering Principles

1. **Context is King**: Provide comprehensive documentation, examples, patterns, and gotchas

2. **Security-First Design**: Integrate security considerations throughout, not as afterthoughts

3. **Prescriptive Implementation**: Specify exact file paths, line numbers, and method signatures

4. **Multi-Stage Validation**: Implement comprehensive validation gates with specific commands

5. **Progressive Success**: Start with architecture, validate incrementally, then enhance

---

#
# Goal

**[SPECIFIC END STATE]**: Define exactly what needs to be built with measurable success criteria

[What needs to be built - be ultra-specific about the end state, user-visible behavior, and technical requirements]

#
## Success Criteria (Measurable & Testable)

- [ ] **Functional**: [Specific measurable outcomes with test commands]

- [ ] **Security**: [Specific security validations that must pass]

- [ ] **Performance**: [Specific performance benchmarks that must be met]

- [ ] **Integration**: [Specific integration points that must work]

#
# Why

#
## Business Value & User Impact

- [Clear business justification and user benefit]

- [Integration with existing features and workflow]

- [Problems this solves and for whom]

#
## Technical Justification

- [How this fits into existing architecture]

- [Technical debt this addresses]

- [Performance or security improvements]

#
# What

#
## User-Visible Behavior

[Detailed description of what users will experience]

#
## Technical Requirements

[Specific technical specifications and constraints]

#
## Security Requirements

- **Authentication**: [How users/systems will be authenticated]

- **Authorization**: [What permissions are required]

- **Input Validation**: [What inputs need validation and how]

- **Data Protection**: [What data needs protection and how]

- **Audit Requirements**: [What needs to be logged for security]

#
# All Needed Context

#
## CRITICAL Documentation & References

```yaml

# MUST READ - Include these in your context window for implementation

- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server implementation patterns with Python/async"
  sections: ["Core Principles", "Server Initialization", "Error Handling"]
  

- file: PRPs/ai_docs/database-integration-patterns.md  
  why: "Async database patterns with SQLite/aiosqlite"
  sections: ["Connection Management", "Repository Pattern", "Migration Patterns"]
  

- file: PRPs/ai_docs/security-patterns.md
  why: "Security validation and protection patterns"
  sections: ["Input Validation", "Authentication", "Error Sanitization"]
  

- file: PRPs/ai_docs/context-engineering-guide.md
  why: "Context engineering methodology and best practices"
  sections: ["Context Engineering Principle", "Validation Framework"]

# ARCHITECTURE REFERENCES

- file: [path/to/relevant/architecture/file.py]
  why: [Specific patterns to follow, gotchas to avoid]
  lines: [X-Y] 
# Specific line ranges that are relevant
  critical: [Key insight that prevents common errors]

# IMPLEMENTATION EXAMPLES  

- file: [path/to/similar/implementation.py]
  why: [Pattern to mirror, existing integration to follow]
  method: [specific_method_name] 
# Exact method to reference
  

# LIBRARY DOCUMENTATION

- url: [Official API docs URL]
  section: [Specific section about the feature you need]
  critical: [Key insight about library usage or gotchas]

```text

#
## Current Codebase Architecture

```text
bash

# Run this command to understand current structure:

tree -I '__pycache__|*.pyc|.git|node_modules' --dirsfirst -L 3

# Expected structure (document what you find):

src/
├── domain/           
# Business logic and entities
├── application/      
# Use cases and services  
├── infrastructure/   
# Database, MCP, external services
└── presentation/     
# MCP server, CLI interfaces

```text

#
## Desired Architecture After Implementation

```text
bash

# Document the intended structure after your changes:

src/
├── domain/
│   ├── entities/
│   │   └── [new_entity.py]     
# [Responsibility description]
│   └── services/
│       └── [new_service.py]    
# [Responsibility description]
├── infrastructure/
│   ├── mcp/handlers/
│   │   └── [new_handler.py]    
# [Responsibility description]
│   └── database/
│       └── [new_repository.py] 
# [Responsibility description]
└── tests/
    ├── unit/
    │   └── [test_new_feature.py]  
# [Test responsibility]
    └── integration/
        └── [test_integration.py]  
# [Integration test responsibility]

```text

#
## CRITICAL: Known Gotchas & Library Quirks

```text
python

# CRITICAL: [Library/Framework] specific requirements

# Example: FastAPI requires async functions for endpoints

# Example: SQLAlchemy async requires explicit session.commit()

# Example: MCP servers must log to stderr, never stdout

# CRITICAL: Our codebase specific patterns

# Example: Repository pattern requires database URL in constructor

# Example: All MCP handlers must use secure_mcp_handler wrapper

# Example: Database connections must use context managers for cleanup

# CRITICAL: Security requirements that must be followed

# Example: All user input must be validated with Pydantic schemas

# Example: File paths must be validated to prevent traversal attacks

# Example: Database errors must be sanitized before returning to client

# CRITICAL: Performance constraints to be aware of

# Example: Database queries must use pagination for large datasets

# Example: File operations must have size limits to prevent DoS

# Example: Async operations should use semaphores for concurrency control

```text

#
## Integration Security Analysis

```text
yaml

# SECURITY: Analyze integration points for security requirements

AUTHENTICATION_REQUIREMENTS:
  - API endpoints: [Authentication method required]
  - Database access: [Authorization level needed]
  - File operations: [Path validation requirements]

AUTHORIZATION_REQUIREMENTS:
  - User roles: [What roles can perform this action]
  - Resource access: [What resources need access control]
  - Operation permissions: [What operations require special permissions]

INPUT_VALIDATION_REQUIREMENTS:
  - User inputs: [All inputs that need validation]
  - File uploads: [File type and size restrictions]
  - Database inputs: [SQL injection prevention requirements]

DATA_PROTECTION_REQUIREMENTS:
  - Sensitive data: [What data needs encryption/protection]
  - Logging: [What should/shouldn't be logged]
  - Error messages: [What information can be revealed in errors]

```text

#
# Implementation Blueprint

#
## Data Models and Validation Schemas

```text
python

# PATTERN: Security-first data models with comprehensive validation

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal
from datetime import datetime

class [FeatureName]Request(BaseModel):
    """Secure request model with comprehensive validation."""
    
    
# SECURITY: Define strict field validation
    field_name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Field description with constraints"
    )
    
    
# SECURITY: Use Literal types for enums to prevent injection
    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Priority level"
    )
    
    @validator('field_name')
    def validate_field_name(cls, v):
        """SECURITY: Validate field for security issues."""
        
# SECURITY: Basic XSS prevention
        dangerous_patterns = ['<script', 'javascript:', 'data:']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('Field contains potentially dangerous content')
        
        
# SECURITY: Prevent path traversal
        if '../' in v or '..\\' in v:
            raise ValueError('Field contains invalid path characters')
        
        return v.strip()
    
    class Config:
        
# SECURITY: Strict validation mode
        extra = 'forbid'  
# Reject unknown fields
        str_strip_whitespace = True
        validate_assignment = True

class [FeatureName]Response(BaseModel):
    """Response model with secure data handling."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

```text

#
## Prescriptive Implementation Tasks

```text
yaml

# CRITICAL: Follow this exact order for implementation

Task 1: Create Domain Entities
FILE: src/domain/entities/[feature_name].py
PATTERN: Mirror existing entity at src/domain/entities/task.py:15-45
IMPLEMENT:
  - Create [FeatureName] class with validation
  - Add business logic methods 
  - Include security validation in entity methods
  - Follow existing naming conventions exactly
VALIDATE: Entity passes unit tests and validation

Task 2: Implement Repository Interface  
FILE: src/domain/repositories/[feature_name]_repository.py
PATTERN: Follow abstract repository at src/domain/repositories/task_repository.py:20-60
IMPLEMENT:
  - Create abstract interface with async methods
  - Define method signatures matching existing patterns
  - Include security considerations in interface documentation
VALIDATE: Interface compiles and follows architectural patterns

Task 3: Create Database Repository Implementation
FILE: src/infrastructure/database/sqlite/[feature_name]_repository.py  
PATTERN: Mirror implementation at src/infrastructure/database/sqlite/task_repository.py:40-120
IMPLEMENT:
  - Implement async database operations using context managers
  - Add comprehensive error handling with security-safe messages
  - Include transaction management and rollback handling
  - Follow existing connection pool patterns exactly
SECURITY: 
  - Sanitize all database errors before logging
  - Use parameterized queries to prevent SQL injection
  - Validate all inputs before database operations
VALIDATE: Repository passes integration tests with real database

Task 4: Create Use Case Implementation
FILE: src/application/usecases/[feature_name]/[action]_use_case.py
PATTERN: Follow use case at src/application/usecases/task_management/create_task_use_case.py:25-80
IMPLEMENT:
  - Create use case class with single responsibility
  - Add input validation using Pydantic schemas
  - Implement business logic delegation to domain services
  - Include comprehensive error handling
SECURITY:
  - Validate all inputs at use case boundary
  - Implement authorization checks
  - Add audit logging for security-relevant operations
VALIDATE: Use case passes unit tests with mocked dependencies

Task 5: Create MCP Handler
FILE: src/infrastructure/mcp/handlers/[feature_name]_handlers.py
PATTERN: Mirror handler at src/infrastructure/mcp/handlers/task_handlers.py:30-90
IMPLEMENT:
  - Create async MCP tool handler
  - Use secure_mcp_handler wrapper for security
  - Convert domain exceptions to MCP errors properly
  - Follow existing error sanitization patterns exactly
SECURITY:
  - Use rate limiting decorator if applicable
  - Sanitize all error messages for client consumption
  - Log security events to audit logger
VALIDATE: Handler passes MCP integration tests

Task 6: Register MCP Tool
FILE: src/infrastructure/mcp/tool_definitions.py  
LOCATION: Add to existing function at line ~45
PATTERN: Follow existing tool registration pattern
IMPLEMENT:
  - Add tool definition with comprehensive JSON schema
  - Include security validation in schema definition
  - Document all parameters with examples
VALIDATE: Tool appears in MCP tool list and accepts valid inputs

Task 7: Add Integration Tests
FILE: tests/integration/test_[feature_name]_integration.py
PATTERN: Follow integration test at tests/integration/test_task_management.py:50-150
IMPLEMENT:
  - Test full end-to-end workflow through MCP interface
  - Include security test cases for malicious inputs
  - Test error handling and edge cases
  - Include performance tests for large datasets
SECURITY:
  - Test XSS prevention in input validation
  - Test SQL injection prevention
  - Test path traversal prevention
  - Test rate limiting if applicable
VALIDATE: All integration tests pass with real components

```text

#
## Security Implementation Checklist

```text
yaml

# CRITICAL: Security requirements that MUST be implemented

INPUT_VALIDATION:
  - [ ] All user inputs validated with Pydantic schemas
  - [ ] XSS prevention implemented for text fields
  - [ ] SQL injection prevention with parameterized queries
  - [ ] Path traversal prevention for file operations
  - [ ] File upload restrictions (size, type, location)

AUTHENTICATION_AUTHORIZATION:
  - [ ] Authentication required for protected endpoints
  - [ ] Role-based authorization implemented where needed
  - [ ] Session management secure (if applicable)
  - [ ] API key validation implemented (if applicable)

ERROR_HANDLING:
  - [ ] Database errors sanitized before client response
  - [ ] Internal errors logged but not exposed to client
  - [ ] Security violations logged to audit log
  - [ ] Stack traces never exposed in production

DATA_PROTECTION:
  - [ ] Sensitive data encrypted at rest (if applicable)
  - [ ] Sensitive data not logged in plaintext
  - [ ] Data access logged for audit trail
  - [ ] Personal data handling complies with privacy requirements

SECURITY_TESTING:
  - [ ] Security unit tests for input validation
  - [ ] Integration tests for authentication/authorization
  - [ ] Penetration testing for common vulnerabilities
  - [ ] Security scanning passes without high-severity issues

```text

#
# Multi-Stage Validation Framework

#
## Stage 1: Syntax & Security Validation

```text
bash

# CRITICAL: Run these FIRST - fix any errors before proceeding

ruff check . --fix                    
# Auto-fix style issues
mypy src/                            
# Type checking validation
bandit -r src/                       
# Security vulnerability scanning
safety check                        
# Dependency vulnerability check

# EXPECTED: No syntax errors, no type errors, no high-severity security issues

# IF ERRORS: Read each error carefully, understand root cause, fix code, re-run

```text

#
## Stage 2: Unit Testing with Security Focus

```text
python

# CREATE comprehensive unit tests following this pattern:

import pytest
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError

@pytest.mark.asyncio
async def test_happy_path():
    """Test normal functionality works correctly."""
    
# Test implementation here
    pass

@pytest.mark.asyncio  
async def test_input_validation_security():
    """Test security-focused input validation."""
    
# SECURITY: Test XSS prevention
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<iframe src='javascript:alert(1)'></iframe>"
    ]
    
    for malicious_input in malicious_inputs:
        with pytest.raises(ValidationError):
            await your_function(malicious_input)

@pytest.mark.asyncio
async def test_error_handling_security():
    """Test that errors don't leak sensitive information."""
    with patch('your_module.database_operation') as mock_db:
        mock_db.side_effect = Exception("Database connection failed: user='admin' password='secret'")
        
        with pytest.raises(Exception) as exc_info:
            await your_function("valid_input")
        
        
# SECURITY: Ensure sensitive info not in error message
        assert "password" not in str(exc_info.value).lower()
        assert "secret" not in str(exc_info.value)

@pytest.mark.asyncio
async def test_authorization():
    """Test authorization controls work correctly."""
    
# Test unauthorized access is denied
    
# Test authorized access is permitted
    
# Test role-based access control
    pass

```text

```text
bash

# Run unit tests with coverage:

pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80

# EXPECTED: All tests pass, >80% code coverage

# IF FAILING: Read error messages, understand failures, fix code (never mock to pass)

```text

#
## Stage 3: Integration & Database Testing

```text
bash

# CRITICAL: Test real database operations and MCP integration

pytest tests/integration/ -v                    
# Integration tests
python scripts/validate_database_schema.py      
# Database schema validation
python scripts/test_mcp_protocol_compliance.py  
# MCP protocol validation

# EXPECTED: All integration tests pass, database schema valid, MCP protocol compliant

# IF ERRORS: Check database connectivity, schema migrations, MCP tool registration

```text

#
## Stage 4: Security & Performance Validation

```text
bash

# CRITICAL: Security and performance validation

python scripts/security_audit.py               
# Custom security audit
pytest tests/security/ -v                      
# Security-specific tests  
python scripts/performance_benchmark.py        
# Performance benchmarks
locust -f tests/load/locustfile.py --headless  
# Load testing (if applicable)

# EXPECTED: No high-severity security issues, performance within acceptable ranges

# IF ISSUES: Address security vulnerabilities first, then optimize performance

```text

#
## Stage 5: End-to-End & Production Readiness

```text
bash

# CRITICAL: Full system validation

python scripts/e2e_validation.py               
# End-to-end workflow testing
python scripts/production_readiness_check.py   
# Production environment validation
docker-compose -f docker-compose.test.yml up   
# Container testing (if applicable)

# EXPECTED: Complete workflows function correctly, system ready for production

# IF ISSUES: Fix integration problems, ensure all dependencies are available
```text

#
# Final Security & Quality Validation Checklist

#
## Code Quality

- [ ] All tests pass: `pytest tests/ -v --cov=src --cov-fail-under=80`

- [ ] No linting errors: `ruff check . && mypy src/`

- [ ] No security issues: `bandit -r src/ && safety check`

- [ ] Performance benchmarks met: `python scripts/performance_benchmark.py`

#
## Security Validation  

- [ ] Input validation prevents XSS: Security tests pass

- [ ] SQL injection prevention verified: Integration tests pass

- [ ] Path traversal prevention tested: File operation tests pass

- [ ] Authentication/authorization working: Security integration tests pass

- [ ] Error messages don't leak sensitive info: Error handling tests pass

- [ ] Audit logging captures security events: Audit tests pass

#
## Integration Validation

- [ ] MCP tool registration successful: Tool appears in MCP tool list

- [ ] Database operations work correctly: Integration tests pass

- [ ] Use case orchestration functions: End-to-end tests pass

- [ ] Error handling propagates correctly: Error scenario tests pass

#
## Documentation & Deployment

- [ ] Code is self-documenting with proper docstrings

- [ ] Security considerations documented in README

- [ ] Performance characteristics documented

- [ ] Deployment procedures validated (if applicable)

- [ ] Monitoring and alerting configured (if applicable)

---

#
# Anti-Patterns to Avoid

#
## Security Anti-Patterns

- ❌ **Input Trust**: Never trust user input - always validate with Pydantic schemas

- ❌ **Generic Error Messages**: Don't return "Internal Server Error" - provide actionable feedback

- ❌ **Information Disclosure**: Never include stack traces, passwords, or internal paths in client responses

- ❌ **Missing Authorization**: Don't assume authentication equals authorization - check permissions explicitly

- ❌ **Logging Sensitive Data**: Never log passwords, tokens, or personal information in plaintext

#
## Implementation Anti-Patterns  

- ❌ **Pattern Deviation**: Don't create new patterns when existing ones work - follow established conventions

- ❌ **Validation Skipping**: Don't skip validation because "it should work" - validate everything

- ❌ **Test Avoidance**: Don't ignore failing tests - fix them or understand why they fail

- ❌ **Async Inconsistency**: Don't mix sync and async code - use async/await consistently throughout

- ❌ **Resource Leaks**: Don't forget resource cleanup - always use context managers for database connections

- ❌ **Hardcoded Values**: Don't hardcode configurations - use environment variables or config files

#
## Architecture Anti-Patterns

- ❌ **Layer Violations**: Don't let domain entities import infrastructure code - respect dependency direction

- ❌ **God Objects**: Don't create classes that do everything - follow single responsibility principle  

- ❌ **Tight Coupling**: Don't directly depend on concrete implementations - use interfaces and dependency injection

- ❌ **Magic Numbers**: Don't use unexplained constants - define named constants with clear meanings

---

#
# Expected Quality Outcomes

#
## Measurable Success Metrics

- **First-Pass Success**: Implementation works correctly on first attempt (>90% target)

- **Security Score**: Zero high-severity security issues in automated scans

- **Test Coverage**: >80% code coverage with meaningful tests

- **Performance**: Meets specified performance benchmarks

- **Code Quality**: Passes all linting and type checking without errors

#
## Production Readiness Indicators

- **Comprehensive Error Handling**: All error scenarios handled gracefully

- **Security Hardening**: All security requirements implemented and tested

- **Monitoring Integration**: Health checks and metrics available

- **Documentation Complete**: Implementation is self-documenting and maintainable

- **Deployment Ready**: Can be deployed to production without additional work

This enhanced template ensures security-first, production-ready implementations through systematic context engineering and comprehensive validation frameworks.
