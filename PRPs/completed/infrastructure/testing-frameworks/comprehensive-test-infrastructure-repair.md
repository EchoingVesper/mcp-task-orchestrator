# PRP: Comprehensive Test Infrastructure Repair - MCP Task Orchestrator v2.0

## Executive Summary

**Feature**: Fix all remaining broken tests (18 failing test files) to achieve 95%+ test pass rate following the v2.0 clean architecture migration.

**Current State**: 104/277 security tests passing (37.5% overall), with 22/22 authentication tests and 24/24 template security tests at 100% success rate.

**Target State**: 95%+ overall test pass rate with all critical functionality validated through comprehensive test suite.

**Business Value**: Ensures production readiness, maintains security validation, and provides confidence for v2.0 release deployment.

## Enhanced Context Engineering References

### Critical AI Documentation
```yaml
- file: PRPs/ai_docs/test-failure-analysis.md
  why: "Comprehensive analysis of 18 failing test files categorized by failure type with architectural mapping"
  sections: ["Test Failure Categories", "Working Test Patterns", "Architectural Import Mapping", "Fix Strategy Priorities"]

- file: PRPs/ai_docs/systematic-testing-framework.md  
  why: "Testing methodology and validation framework for clean architecture"
  sections: ["Async Testing Patterns", "Security Testing Integration", "Performance Validation"]

- file: PRPs/ai_docs/security-patterns.md
  why: "Security validation and testing patterns with authentication/authorization"
  sections: ["Authentication Testing", "Authorization Testing", "Input Validation Testing"]

- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server testing patterns with async/await and dependency injection"
  sections: ["MCP Tool Testing", "Server Integration Testing", "Protocol Validation"]

- file: PRPs/ai_docs/database-integration-patterns.md
  why: "Database testing patterns with SQLite/async repositories"
  sections: ["Repository Testing", "Connection Management", "Test Data Isolation"]
```

### Key Working Patterns (Reference Implementation)
- **Security Tests**: `tests/security/test_authentication.py` (22/22 passing)
- **Template Tests**: `tests/security/template_system/test_template_security.py` (24/24 passing)
- **Test Utilities**: `tests/security/conftest.py` (comprehensive fixture patterns)
- **Database Utils**: `tests/utils/db_test_utils.py` (managed connection patterns)

## Problem Analysis

### Test Failure Categories (18 Files)

#### 1. Legacy Model Import Errors (High Priority - 10+ files)
**Root Cause**: Tests importing deprecated domain models from v1.x architecture

**Example Broken Pattern**:
```python
# BROKEN (v1.x)
from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskResult

# CORRECT (v2.0 Clean Architecture)
from mcp_task_orchestrator.domain.entities.task import Task
from mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult
from mcp_task_orchestrator.domain.value_objects.task_status import TaskStatus
```

**Affected Files**:
- `tests/test_db_persistence.py`
- `tests/test_enhanced_integration.py` 
- `tests/test_context_continuity.py`
- `tests/test_custom_roles.py`
- `tests/integration/test_orchestrator.py`
- `tests/integration/test_task_execution.py`

#### 2. Installer Path Import Errors (Medium Priority - 2 files)
```python
# BROKEN
from installer.client_detector import ClientDetector

# CORRECT  
from mcp_task_orchestrator_cli.platforms.client_detector import ClientDetector
```

#### 3. Missing Module Import Errors (Medium Priority - 3-4 files)
Modules moved to archives or consolidated during migration.

#### 4. Relative Import Errors (Low Priority - 4-5 files)
Package structure changes breaking relative imports.

#### 5. Missing Role Loader Functions (Low Priority - 3 files)
Functions removed as part of clean architecture refactoring.

## Implementation Blueprint

### Phase 1: Critical Legacy Model Migration (Priority: High)

```python
# Step 1: Update Domain Entity Imports
# File: tests/test_db_persistence.py (and 9 other files)

# OLD IMPORTS TO REPLACE:
from mcp_task_orchestrator.orchestrator.models import (
    TaskBreakdown, SubTask, TaskResult, TaskStatus, ComplexityLevel, SpecialistType
)

# NEW CLEAN ARCHITECTURE IMPORTS:
from mcp_task_orchestrator.domain.entities.task import Task, TaskAttribute, TaskDependency
from mcp_task_orchestrator.domain.value_objects.task_status import TaskStatus
from mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel  
from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType
from mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult

# Step 2: Update Test Logic for Hierarchical Tasks
# OLD: TaskBreakdown with separate SubTask entities
task_breakdown = TaskBreakdown(
    main_task="Implement feature",
    subtasks=[SubTask(title="Step 1"), SubTask(title="Step 2")]
)

# NEW: Hierarchical Task structure  
parent_task = Task(
    title="Implement feature",
    description="Main task",
    task_type=TaskType.STANDARD
)
child_task_1 = Task(
    title="Step 1", 
    parent_task_id=parent_task.id,
    task_type=TaskType.STANDARD
)
```

### Phase 2: Architecture Alignment (Priority: Medium)

```python
# Step 1: Fix Installer Module Paths
# Files: tests/unit/test_detection.py, tests/unit/test_working_directory.py

# OLD IMPORT:
from installer.client_detector import ClientDetector

# NEW IMPORT:
from mcp_task_orchestrator_cli.platforms.client_detector import ClientDetector

# Step 2: Update Dependency Injection in Tests
from mcp_task_orchestrator.infrastructure.di.service_configuration import (
    create_configured_container, get_default_config
)

@pytest.fixture
def configured_container():
    config = get_default_config()
    container = create_configured_container(config)
    return container

def test_service_resolution(configured_container):
    task_repo = configured_container.get_service(TaskRepository)
    assert task_repo is not None
```

### Phase 3: Test Infrastructure Modernization (Priority: Low)

```python
# Step 1: Fix Async Test Patterns
@pytest.mark.asyncio  # CRITICAL: Add this marker
async def test_async_operation(self):
    result = await some_async_function()
    assert result is not None

# Step 2: Add Security Test Integration
@pytest.fixture
def clean_security_state():
    security_audit_logger.clear_logs()
    yield
    security_audit_logger.clear_logs()

# Step 3: Add Performance Monitoring
@pytest.fixture
def performance_monitor():
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    yield monitor
    monitor.assert_performance_limits(max_execution_time=30.0)
```

## Security Integration Requirements

### Authentication Testing Patterns
```python
# Follow working pattern from tests/security/test_authentication.py
@pytest.mark.asyncio
@pytest.mark.authentication  
async def test_protected_endpoint(self, test_api_key_manager, valid_api_key):
    with patch('mcp_task_orchestrator.infrastructure.security.auth_validator') as mock_auth:
        mock_auth.validate_api_key.return_value = (True, {"user_id": "test"})
        result = await protected_handler(context, args, api_key=valid_api_key)
        assert result["success"] is True
```

### Input Validation Testing
```python
# XSS Prevention Testing
@pytest.mark.parametrize("xss_payload", [
    "<script>alert('xss')</script>",
    "javascript:alert('xss')",
    "<img src=x onerror=alert('xss')>"
])
def test_xss_prevention(xss_payload):
    with pytest.raises(ValidationError):
        validate_string_input(xss_payload, field_name="title")
```

## Multi-Stage Validation Framework

### Stage 1: Syntax & Security Validation
```bash
# Pre-commit validation
ruff check . --fix
mypy mcp_task_orchestrator/ --strict
bandit -r mcp_task_orchestrator/ -f json -o security_report.json
safety check --json --output safety_report.json
```

### Stage 2: Unit Testing with Security Focus  
```bash
# Core unit tests with security markers
pytest tests/unit/ -v --cov=mcp_task_orchestrator --cov-fail-under=80
pytest tests/security/ -v -m "authentication or authorization"
pytest tests/ -v -m "security and not slow"
```

### Stage 3: Integration & Database Testing
```bash
# Integration validation
pytest tests/integration/ -v --tb=short
python scripts/validate_database_schema.py
python scripts/test_mcp_compatibility.py
```

### Stage 4: Security & Performance Validation
```bash
# Security audit
python scripts/security_audit.py --comprehensive
pytest tests/ -v -m "performance" --maxfail=3
python scripts/performance_benchmark.py --baseline
```

### Stage 5: Production Readiness Validation  
```bash
# End-to-end validation
python scripts/e2e_validation.py --full-suite
python scripts/production_readiness_check.py
pytest tests/ -v --cov=mcp_task_orchestrator --cov-report=html --cov-fail-under=90
```

## Implementation Tasks (Execution Order)

### Task 1: Legacy Model Import Migration
- [ ] Update 10+ test files with new domain entity imports
- [ ] Replace TaskBreakdown usage with hierarchical Task structure
- [ ] Update SubTask references to parent-child Task relationships
- [ ] Migrate TaskResult to ExecutionResult value object
- [ ] Fix enum imports (TaskStatus, ComplexityLevel, SpecialistType)

### Task 2: Architecture Compatibility Updates
- [ ] Fix installer module import paths (2 files)
- [ ] Update role loader function references (3 files) 
- [ ] Implement dependency injection patterns in tests
- [ ] Add missing async markers and proper async fixtures

### Task 3: Test Infrastructure Cleanup
- [ ] Fix relative import paths (4-5 files)
- [ ] Update archived test references
- [ ] Consolidate duplicate test utilities
- [ ] Add comprehensive performance monitoring

### Task 4: Security Test Integration
- [ ] Ensure all tests follow security patterns
- [ ] Add authentication/authorization testing where needed
- [ ] Implement input validation testing for user inputs
- [ ] Add security state cleanup fixtures

### Task 5: Validation and Documentation
- [ ] Run full 5-stage validation framework
- [ ] Update test documentation with new patterns
- [ ] Create migration guide for future test development
- [ ] Validate 95%+ test pass rate achievement

## Code Examples and Patterns

### Working Authentication Test Pattern
```python
# Reference: tests/security/test_authentication.py:33-61
@pytest.mark.asyncio
@pytest.mark.authentication
@pytest.mark.critical
async def test_require_auth_decorator_success(self, mock_mcp_context, test_user_basic):
    with patch('mcp_task_orchestrator.infrastructure.security.authentication.auth_validator.api_key_manager.validate_api_key') as mock_validate:
        mock_validate.return_value = (True, {"user_id": test_user_basic["user_id"], "role": "user"})
        
        @require_auth
        async def protected_handler(context, args, **kwargs):
            return {"success": True, "user": test_user_basic["user_id"]}
        
        context = mock_mcp_context(test_user_basic)
        result = await protected_handler(context, {}, api_key="valid_key_123")
        assert result["success"] is True
```

### Working Database Test Pattern
```python
# Reference: tests/utils/db_test_utils.py:45-67
@contextmanager
def managed_persistence_manager():
    """Context manager for database testing with automatic cleanup."""
    persistence = None
    try:
        persistence = PersistenceManager(":memory:")
        persistence.initialize_database()
        yield persistence
    finally:
        if persistence:
            persistence.close()
```

### Working Async Fixture Pattern
```python
# Reference: tests/security/conftest.py:89-101
@pytest.fixture
async def async_api_key_manager():
    """Async fixture for API key manager testing."""
    manager = APIKeyManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()
```

## Performance and Security Requirements

### Performance Targets
- **Test Execution**: All tests complete within 5 minutes
- **Individual Tests**: No single test exceeds 30 seconds
- **Memory Usage**: Test suite uses <200MB peak memory
- **Coverage**: Maintain >80% code coverage

### Security Requirements  
- **Authentication**: All protected endpoints tested with auth validation
- **Authorization**: Role-based access control thoroughly validated
- **Input Validation**: XSS, SQL injection, path traversal prevention tested
- **Error Handling**: No sensitive information leaked in error messages

## Expected Outcomes

### Success Metrics
- **Test Pass Rate**: 95%+ (from current ~80%)
- **Security Tests**: Maintain 100% pass rate (46/46 tests)
- **Integration Tests**: All MCP compatibility tests passing
- **Performance**: Test suite execution <5 minutes

### Risk Mitigation
- **Low Risk**: Primarily import fixes with minimal business logic changes
- **Rollback Plan**: Git branch with working security tests as fallback
- **Validation**: Comprehensive 5-stage validation ensures no regressions
- **Dependencies**: No external dependencies or breaking changes required

## Context Engineering Validation

**Context Completeness Score**: 9/10
- ✅ Comprehensive failure analysis with categorization
- ✅ Working test patterns as reference implementation  
- ✅ Detailed architectural mapping and import paths
- ✅ Security integration requirements specified
- ✅ Multi-stage validation framework defined
- ⚠️ Could benefit from more specific line-by-line examples

**Security Integration Score**: 10/10  
- ✅ Security-first design maintained throughout
- ✅ Authentication/authorization patterns preserved
- ✅ Input validation testing requirements specified
- ✅ Security audit integration in validation pipeline

**Overall Confidence Score**: 9/10
- ✅ Clear categorization and prioritization of fixes
- ✅ Proven patterns from working tests as foundation
- ✅ Comprehensive validation framework ensures quality
- ✅ Security infrastructure already validated and working
- ⚠️ Some estimation uncertainty for cleanup phase timing

This PRP provides comprehensive context for fixing all remaining test failures while maintaining the security and architectural integrity achieved in the v2.0 clean architecture migration.