# Testing Development - Claude Code Guide

Testing-specific guidance for the MCP Task Orchestrator's enhanced testing infrastructure.

## Enhanced Testing Architecture

**Enhanced Infrastructure**: Advanced testing framework with alternative runners, file-based output, and hang detection.

### Testing Categories
- `unit/` - Component isolation testing (fast execution < 5s)
- `integration/` - Cross-component validation
- `performance/` - Load testing and benchmarking
- `fixtures/` - Test data and configuration
- `utils/` - Test utilities and helpers

## Testing Context Commands

### Enhanced Test Runners (Preferred)
```bash
# Alternative test runner (more reliable than pytest)
python simple_test_runner.py

# Comprehensive validation suite
python test_validation_runner.py

# Resource management validation
python test_resource_cleanup.py

# Hang detection testing
python test_hang_detection.py
```

### File-Based Output System
```bash
# Demonstrate file-based output (prevents truncation)
python demo_file_output_system.py

# Show alternative test runners
python demo_alternative_runners.py

# Enhanced migration testing
python enhanced_migration_test.py
```

### Traditional Testing (Still Supported)
```bash
# Standard pytest execution
python -m pytest -v

# Specific test categories
python -m pytest unit/ -v
python -m pytest integration/ -v
python -m pytest performance/ -v
```

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

## Testing Best Practices

### Enhanced Testing Patterns
```python
# File-based output (prevents truncation)
from mcp_task_orchestrator.testing import TestOutputWriter
writer = TestOutputWriter(output_dir)
with writer.write_test_output("my_test", "text") as session:
    session.write_line("Test output here...")

# Alternative test runners (more reliable than pytest)
from mcp_task_orchestrator.testing import DirectFunctionRunner
runner = DirectFunctionRunner(output_dir=Path("outputs"))
result = runner.execute_test(my_test_function, "test_name")

# Database connections (prevents resource warnings)
from tests.utils.db_test_utils import managed_sqlite_connection
with managed_sqlite_connection("test.db") as conn:
    # Database operations with guaranteed cleanup
    pass
```

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
