name: "Base PRP Template v2 - Context-Rich with Validation Loops"
description: |

#
# Purpose

Template optimized for AI agents to implement features with sufficient context and self-validation capabilities to achieve working code through iterative refinement.

#
# Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats

2. **Security-First Design**: Integrate security considerations throughout, not as afterthoughts

3. **Validation Loops**: Provide executable tests/lints the AI can run and fix

4. **Information Dense**: Use keywords and patterns from the codebase

5. **Progressive Success**: Start simple, validate, then enhance

---

#
# Goal

[What needs to be built - be specific about the end state and desires]

#
# Why

- [Business value and user impact]

- [Integration with existing features]

- [Problems this solves and for whom]

#
# What

[User-visible behavior and technical requirements]

#
## Success Criteria

- [ ] [Specific measurable outcomes]

- [ ] **Security**: All inputs validated, no high-severity security issues in scans

- [ ] **Authentication**: Proper authentication/authorization implemented where needed

- [ ] **Error Handling**: No sensitive information disclosed in error messages

#
# All Needed Context

#
## Documentation & References (list all context needed to implement the feature)

```yaml

# MUST READ - Include these in your context window

- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server implementation patterns with Python/async"
  sections: ["Core Principles", "Error Handling", "Security Patterns"]

- file: PRPs/ai_docs/database-integration-patterns.md
  why: "Async database patterns with SQLite/aiosqlite"
  sections: ["Connection Management", "Security Patterns", "Error Handling"]

- file: PRPs/ai_docs/security-patterns.md
  why: "Security validation and protection patterns"
  sections: ["Input Validation", "Error Sanitization", "Authentication"]

- url: [Official API docs URL]
  why: [Specific sections/methods you'll need]

- file: [path/to/example.py]
  why: [Pattern to follow, gotchas to avoid]

- doc: [Library documentation URL]
  section: [Specific section about common pitfalls]
  critical: [Key insight that prevents common errors]

- docfile: [PRPs/ai_docs/file.md]
  why: [docs that the user has pasted in to the project]

```text

#
## Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase

```text
bash

```text

#
## Desired Codebase tree with files to be added and responsibility of file

```bash

```text

#
## Known Gotchas of our codebase & Library Quirks

```python

# CRITICAL: [Library name] requires [specific setup]

# Example: FastAPI requires async functions for endpoints

# Example: This ORM doesn't support batch inserts over 1000 records

# Example: We use pydantic v2 and

# SECURITY: Critical security requirements

# CRITICAL: MCP servers must log to stderr, never stdout (protocol violation)

# CRITICAL: All user input must be validated with Pydantic schemas

# CRITICAL: File paths must be validated to prevent traversal attacks

# CRITICAL: Database errors must be sanitized before returning to client

# CRITICAL: Use async context managers for database connections to prevent leaks

# CRITICAL: Rate limiting required for public API endpoints to prevent DoS

```text

#
# Implementation Blueprint

#
## Data models and structure

Create the core data models with security-first validation to ensure type safety and consistency.

```python

# PATTERN: Security-first data models with comprehensive validation

from pydantic import BaseModel, Field, validator
from typing import Literal

class FeatureRequest(BaseModel):
    """Secure request model with comprehensive validation."""
    
    
# SECURITY: Define strict field validation
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    priority: Literal["low", "medium", "high"] = Field(default="medium")
    
    @validator('title')
    def validate_title(cls, v):
        """SECURITY: Validate title for security issues."""
        if any(pattern in v.lower() for pattern in ['<script', 'javascript:', 'data:']):
            raise ValueError('Title contains potentially dangerous content')
        if '../' in v or '..\\' in v:
            raise ValueError('Title contains invalid path characters')
        return v.strip()
    
    class Config:
        
# SECURITY: Strict validation mode
        extra = 'forbid'  
# Reject unknown fields
        str_strip_whitespace = True
        validate_assignment = True

Examples:
 - orm models with security constraints
 - pydantic models with input validation
 - pydantic schemas with XSS prevention
 - pydantic validators with security checks

```text

#
## List of tasks to be completed to fulfill the PRP in the order they should be completed

```text
yaml
Task 1: Create Secure Data Models
CREATE src/domain/entities/new_feature.py:
  - MIRROR pattern from: src/domain/entities/task.py
  - IMPLEMENT Pydantic validation with security checks
  - INCLUDE XSS prevention in text field validators
  - PRESERVE existing naming conventions

Task 2: Implement Repository with Security
CREATE src/infrastructure/database/new_feature_repository.py:
  - MIRROR pattern from: src/infrastructure/database/task_repository.py  
  - USE async context managers for connection management
  - SANITIZE database errors before logging
  - IMPLEMENT parameterized queries to prevent SQL injection

Task 3: Create Secure MCP Handler
CREATE src/infrastructure/mcp/handlers/new_feature_handlers.py:
  - MIRROR pattern from: src/infrastructure/mcp/handlers/task_handlers.py
  - USE secure_mcp_handler wrapper for security
  - VALIDATE all inputs with Pydantic schemas
  - SANITIZE error messages for client consumption

...(...)

Task N:
...

```text

#
## Per task pseudocode as needed added to each task

```python

# Task 1: Secure Feature Implementation

# Pseudocode with CRITICAL security details - don't write entire code
async def new_feature(param: str) -> Result:
    
# SECURITY: Always validate input first with Pydantic schema
    try:
        validated_request = FeatureRequest(param=param)  
# raises ValidationError
    except ValidationError as e:
        
# SECURITY: Log validation failure for audit
        logger.warning(f"Input validation failed: {e}")
        raise McpError(-32602, "Invalid input provided")

    
# SECURITY: Check authorization before processing
    if not has_permission(current_user, "create_feature"):
        logger.warning(f"Unauthorized access attempt by {current_user}")
        raise McpError(-32603, "Access denied")

    
# PATTERN: Use async context managers for database connections
    try:
        async with get_connection() as conn:  
# see src/db/pool.py
            
# SECURITY: Use parameterized queries to prevent SQL injection
            result = await conn.execute(
                "INSERT INTO features (name, data) VALUES (?, ?)",
                (validated_request.name, validated_request.data)
            )
            
    except DatabaseError as e:
        
# SECURITY: Sanitize database errors before logging
        logger.error(f"Database operation failed: {e}")
        raise McpError(-32603, "Database operation failed")
    
    except Exception as e:
        
# SECURITY: Generic error handling - don't leak internal details
        logger.exception(f"Unexpected error in new_feature: {e}")
        raise McpError(-32603, "Internal server error")

    
# PATTERN: Standardized response format
    return format_response(result)  
# see src/utils/responses.py

```text

#
## Integration Points

```text
yaml
DATABASE:
  - migration: "Add column 'feature_enabled' to users table"
  - index: "CREATE INDEX idx_feature_lookup ON users(feature_id)"

CONFIG:
  - add to: config/settings.py
  - pattern: "FEATURE_TIMEOUT = int(os.getenv('FEATURE_TIMEOUT', '30'))"

ROUTES:
  - add to: src/api/routes.py
  - pattern: "router.include_router(feature_router, prefix='/feature')"

```text

#
# Validation Loop

#
## Level 1: Syntax & Security Validation

```text
bash

# Run these FIRST - fix any errors before proceeding

ruff check src/new_feature.py --fix  
# Auto-fix what's possible
mypy src/new_feature.py              
# Type checking
bandit -r src/new_feature.py         
# Security vulnerability scanning
safety check                        
# Dependency vulnerability check

# Expected: No syntax errors, no type errors, no high-severity security issues

# If errors: READ each error carefully, understand root cause, fix code, re-run

```text

#
## Level 2: Unit Tests each new feature/file/function use existing test patterns

```text
python

# CREATE test_new_feature.py with these test cases including security tests:

@pytest.mark.asyncio
async def test_happy_path():
    """Basic functionality works"""
    result = await new_feature("valid_input")
    assert result.status == "success"

@pytest.mark.asyncio
async def test_input_validation_security():
    """SECURITY: Test XSS and injection prevention"""
    malicious_inputs = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "../../../etc/passwd",
        "'; DROP TABLE users; --"
    ]
    
    for malicious_input in malicious_inputs:
        with pytest.raises(ValidationError):
            await new_feature(malicious_input)

@pytest.mark.asyncio
async def test_error_handling_security():
    """SECURITY: Test that errors don't leak sensitive information"""
    with mock.patch('database.execute', side_effect=DatabaseError("Connection failed: user='admin' password='secret'")):
        with pytest.raises(McpError) as exc_info:
            await new_feature("valid_input")
        
        
# SECURITY: Ensure sensitive info not in error message
        assert "password" not in exc_info.value.message.lower()
        assert "secret" not in exc_info.value.message
        assert exc_info.value.message == "Database operation failed"

@pytest.mark.asyncio
async def test_authorization():
    """SECURITY: Test authorization controls"""
    with mock.patch('has_permission', return_value=False):
        with pytest.raises(McpError) as exc_info:
            await new_feature("valid_input")
        
        assert exc_info.value.code == -32603
        assert "Access denied" in exc_info.value.message

```text

```text
bash

# Run and iterate until passing:

uv run pytest test_new_feature.py -v

# If failing: Read error, understand root cause, fix code, re-run (never mock to pass)

```text

#
## Level 3: Integration Test

```bash

# Start the service

uv run python -m src.main --dev

# Test the endpoint

curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test_value"}'

# Expected: {"status": "success", "data": {...}}

# If error: Check logs at logs/app.log for stack trace

```text

#
## Level 4: Security & Performance Validation

```text
bash

# SECURITY: Comprehensive security validation

python scripts/security_audit.py               
# Custom security audit script
pytest tests/security/ -v                      
# Security-specific tests
python scripts/penetration_test.py             
# Basic penetration testing

# PERFORMANCE: Performance and load testing  

python scripts/performance_benchmark.py        
# Performance benchmarks
locust -f tests/load/locustfile.py --headless  
# Load testing (if applicable)

# INTEGRATION: Creative validation methods

# - End-to-end user journey testing with security scenarios

# - Rate limiting tests with high-volume requests  

# - Authentication bypass attempt testing

# - Input fuzzing for edge case discovery

# - Database injection attempt testing

# - File upload security testing (if applicable)

# Expected: No high-severity security issues, performance within benchmarks

# If issues: Address security vulnerabilities first, then optimize performance
```text

#
# Final Security & Quality Validation Checklist

#
## Code Quality

- [ ] All tests pass: `uv run pytest tests/ -v --cov=src --cov-fail-under=80`

- [ ] No linting errors: `uv run ruff check src/`

- [ ] No type errors: `uv run mypy src/`

- [ ] Manual test successful: [specific curl/command]

#
## Security Validation

- [ ] No high-severity security issues: `bandit -r src/ && safety check`

- [ ] Input validation prevents XSS: Security tests pass

- [ ] SQL injection prevention verified: Database tests pass

- [ ] Path traversal prevention tested: File operation tests pass

- [ ] Authentication/authorization working: Auth tests pass

- [ ] Error messages don't leak sensitive info: Error handling tests pass

#
## System Integration

- [ ] Error cases handled gracefully with secure error messages

- [ ] Logs are informative but don't contain sensitive data

- [ ] Rate limiting functional (if applicable)

- [ ] Database connections properly managed with context managers

- [ ] MCP protocol compliance verified

#
## Documentation & Security

- [ ] Security considerations documented

- [ ] Authentication/authorization requirements documented

- [ ] Performance characteristics documented

- [ ] Deployment security checklist completed (if applicable)

---

#
# Anti-Patterns to Avoid

#
## Security Anti-Patterns

- ❌ **Input Trust**: Don't trust user input - always validate with Pydantic schemas

- ❌ **Information Disclosure**: Don't include stack traces, passwords, or internal paths in client responses

- ❌ **Generic Error Messages**: Don't return vague errors - provide actionable feedback without leaking info

- ❌ **Missing Authorization**: Don't assume authentication equals authorization - check permissions explicitly

- ❌ **Logging Sensitive Data**: Don't log passwords, tokens, or personal information in plaintext

#
## Implementation Anti-Patterns

- ❌ Don't create new patterns when existing ones work

- ❌ Don't skip validation because "it should work"

- ❌ Don't ignore failing tests - fix them

- ❌ Don't use sync functions in async context

- ❌ Don't hardcode values that should be config

- ❌ Don't catch all exceptions - be specific

#
## Architecture Anti-Patterns  

- ❌ **Resource Leaks**: Don't forget resource cleanup - always use context managers for database connections

- ❌ **Layer Violations**: Don't let domain entities import infrastructure code - respect dependency direction

- ❌ **Protocol Violations**: Don't write to stdout in MCP servers - use stderr for logging
