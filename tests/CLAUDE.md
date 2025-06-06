# Testing Development - Claude Code Guide

<critical_file_size_warning>
⚠️ **CRITICAL: FILE SIZE LIMITS FOR CLAUDE CODE STABILITY** ⚠️

**Maximum File Size**: 500 lines (300-400 lines recommended)
**Risk**: Files exceeding 500 lines can cause Claude Code to crash

**Test Files in THIS Directory Exceeding Limits**:
- `validation_suite.py` (837 lines) - HIGH RISK
- `unit/test_generic_repository.py` (676 lines) - HIGH RISK
- `unit/test_generic_models.py` (562 lines) - MEDIUM RISK
- `integration/test_maintenance_integration.py` (517 lines) - MEDIUM RISK

**Testing Best Practices**:
1. Split large test suites into focused test modules
2. Use test classes to group related tests
3. Consider separate files for fixtures and utilities
4. Keep individual test files under 400 lines
</critical_file_size_warning>

<testing_context_analysis>
You are working within the enhanced testing infrastructure. Before proceeding with any testing work:

1. **Identify Testing Scope**: Unit tests, integration tests, or performance validation?
2. **Choose Appropriate Runner**: Enhanced runners vs traditional pytest?
3. **Resource Management**: Will tests create database connections or file handles?
4. **Output Requirements**: Do you need complete output capture or can you use standard logging?
5. **Integration Needs**: Are you testing components that interact with the orchestrator?
</testing_context_analysis>

Testing-specific guidance for the MCP Task Orchestrator's enhanced testing infrastructure.

## Enhanced Testing Architecture

**Enhanced Infrastructure**: Advanced testing framework with alternative runners, file-based output, and hang detection.

### Testing Categories
- `unit/` - Component isolation testing (fast execution < 5s)
- `integration/` - Cross-component validation
- `performance/` - Load testing and benchmarking
- `fixtures/` - Test data and configuration
- `utils/` - Test utilities and helpers

## Testing Strategy Decision Framework

<testing_strategy_reasoning>
**When to Use Enhanced vs Traditional Testing**:

**Use Enhanced Runners When**:
- Tests might produce large amounts of output
- Testing database operations that could hang
- Need complete test result capture across sessions
- Working with resource-intensive operations
- Debugging complex integration scenarios

**Use Traditional Pytest When**:
- Simple unit tests with minimal output
- Quick validation of small changes
- CI/CD pipeline integration (where enhanced runners aren't available)
- Standard TDD workflows with fast feedback

**Decision Process**:
1. **Analyze Test Complexity**: Simple logic vs complex integrations?
2. **Evaluate Resource Usage**: Database connections, file operations, network calls?
3. **Consider Output Requirements**: Standard logging vs complete capture?
4. **Assess Reliability Needs**: Critical path testing vs quick validation?
</testing_strategy_reasoning>

## Testing Context Commands

### Enhanced Test Runners (Preferred)
<enhanced_testing_workflow>
**Primary Testing Approach** (Recommended):
```bash
# Comprehensive alternative test runner
python simple_test_runner.py

# Full validation suite with detailed reporting
python test_validation_runner.py

# Resource management validation (prevents ResourceWarnings)
python test_resource_cleanup.py

# Hang detection and timeout testing
python test_hang_detection.py
```

**Traditional Testing** (Fallback):
```bash
# Standard pytest execution
python -m pytest -v

# Category-specific testing
python -m pytest unit/ -v        # Fast unit tests
python -m pytest integration/ -v # Cross-component tests
python -m pytest performance/ -v # Performance benchmarks
```

**Reasoning**: Enhanced runners prevent output truncation, include hang detection, and provide better resource management than standard pytest.
</enhanced_testing_workflow>

## Enhanced Testing Features

### File-Based Output System
- **No Output Truncation**: Complete test results captured in files
- **Detailed Logging**: Comprehensive execution traces
- **Result Persistence**: Test outputs saved for analysis
- **Cross-Session Continuity**: Results available across contexts

### Alternative Test Runners
- **DirectFunctionRunner**: Execute test functions directly
- **TestOutputWriter**: Managed file-based output sessions
- **Hang Detection**: Timeout mechanisms prevent test hanging
- **Resource Management**: Automatic cleanup of database connections

### Resource Management
- **Managed Connections**: `managed_sqlite_connection` context manager
- **Automatic Cleanup**: No ResourceWarnings or connection leaks
- **Connection Pooling**: Optimized database access patterns
- **Health Monitoring**: Connection state validation

## Testing Best Practices and Patterns

<unit_testing_reasoning>
**Unit Testing Strategy** (< 5 second execution):

**When to Use**:
- Testing single component in isolation
- Business logic validation
- Fast feedback for TDD workflows
- Simple input/output validation

**Implementation Pattern**:
```python
def test_task_breakdown_logic():
    """
    Unit Test Reasoning:
    1. Test single component in isolation
    2. Mock external dependencies
    3. Focus on business logic validation
    4. Ensure fast execution for TDD workflows
    """
    # Mock external dependencies
    with patch('mcp_task_orchestrator.db.persistence.get_db_connection') as mock_db:
        # Test core logic without database dependency
        result = orchestrator.analyze_task_complexity("simple task")
        assert result.complexity_level == "simple"
```
</unit_testing_reasoning>

<integration_testing_reasoning>
**Integration Testing Strategy** (Cross-component validation):

**When to Use**:
- Testing components working together
- End-to-end workflow validation
- Database integration testing
- Error propagation validation

**Implementation Pattern**:
```python
async def test_full_orchestration_workflow():
    """
    Integration Test Reasoning:
    1. Test components working together
    2. Use real database connections (managed)
    3. Validate end-to-end workflows
    4. Test error propagation between components
    """
    with managed_sqlite_connection("integration_test.db") as conn:
        # End-to-end workflow testing with real database
        result = await orchestrator.coordinate_execution(breakdown.id)
        assert result.status == "completed"
```
</integration_testing_reasoning>

### Testing Workflow
1. **Enhanced Runners**: Use alternative test runners for reliability
2. **Resource Validation**: Check connection cleanup with resource tests
3. **File Output**: Leverage file-based output for complex scenarios
4. **Hang Prevention**: Include timeout mechanisms in all operations

### Integration with Orchestrator
- **Testing Specialist**: Use tester specialist for comprehensive validation
- **Artifact Storage**: Store test results as artifacts for cross-context access
- **Maintenance Coordination**: Use maintenance coordinator for test cleanup

---

**Enhanced Testing**: This directory uses advanced testing infrastructure. Prefer enhanced runners over standard pytest for reliability.
