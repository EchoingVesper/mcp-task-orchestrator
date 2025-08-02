

# Testing Infrastructure Improvements Guide

#

# Overview

This document describes the major improvements made to the MCP Task Orchestrator testing infrastructure to resolve critical issues with output truncation, resource warnings, and test hanging.

#

# Problems Solved

#

#

# 1. Output Truncation Issues

**Problem**: LLM systems reading test results before tests finished writing, causing truncated or incomplete output.

**Solution**: File-based output system with atomic writes and completion markers.

#

#

# 2. Resource Warning Issues  

**Problem**: SQLite connections and SQLAlchemy engines not properly disposed, generating ResourceWarnings.

**Solution**: Enhanced database persistence with context managers and proper cleanup utilities.

#

#

# 3. Test Hanging Issues

**Problem**: Tests and MCP operations hanging indefinitely without timeout mechanisms.

**Solution**: Comprehensive hang detection and prevention system with configurable timeouts.

#

#

# 4. Pytest Limitations

**Problem**: pytest truncating output and unreliable execution in complex scenarios.

**Solution**: Alternative test runners that bypass pytest entirely while providing superior output handling.

#

# New Testing Components

#

#

# File-Based Output System

The core improvement is a robust file-based output system that prevents timing issues:

```python
from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader

# Writing test output

writer = TestOutputWriter(output_dir)
with writer.write_test_output("my_test", "text") as session:
    session.write_line("Test starting...")
    session.write_line("Test completed successfully")

# Reading test output safely

reader = TestOutputReader(output_dir)
output_files = list(output_dir.glob("my_test_*.txt"))
latest_file = max(output_files, key=lambda f: f.stat().st_mtime)

# Wait for completion before reading

if reader.wait_for_completion(latest_file, timeout=30.0):
    content = reader.read_completed_output(latest_file)
    print("Complete test output:", content)

```text

#

#

# Alternative Test Runners

Multiple specialized test runners are available:

#

#

#

# DirectFunctionRunner

```text
python
from mcp_task_orchestrator.testing import DirectFunctionRunner

runner = DirectFunctionRunner(output_dir=Path("test_outputs"))
result = runner.execute_test(my_test_function, "test_name")

```text

#

#

#

# MigrationTestRunner

```text
python
from mcp_task_orchestrator.testing import MigrationTestRunner

runner = MigrationTestRunner(output_dir=Path("migration_outputs"))
result = runner.run_migration_test()

```text

#

#

#

# ComprehensiveTestRunner

```text
python
from mcp_task_orchestrator.testing import ComprehensiveTestRunner, TestRunnerConfig

config = TestRunnerConfig(
    output_dir=Path("outputs"),
    runner_types=['direct', 'migration', 'integration'],
    verbose=True
)
runner = ComprehensiveTestRunner(config)
results = runner.run_all_tests([test_directory])

```text

#

#

# Hang Detection System

Automatic hang detection and prevention:

```text
python
from mcp_task_orchestrator.monitoring.hang_detection import with_hang_detection

@with_hang_detection("my_operation", timeout=30.0)
async def my_async_operation():
    

# Your operation here

    await some_database_work()
    return "completed"

# Context manager for hang protection

async with hang_protected_operation("context_op", timeout=60.0):
    

# Protected operation

    await long_running_task()

```text

#

#

# Resource Management

Enhanced database persistence with proper cleanup:

```text
python
from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
from tests.utils.db_test_utils import managed_sqlite_connection

# Context manager approach (recommended)

with DatabasePersistenceManager(db_url="sqlite:///test.db") as persistence:
    tasks = persistence.get_all_active_tasks()

# For SQLite connections

with managed_sqlite_connection("test.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
    results = cursor.fetchall()

```text

#

# Migration Guide

#

#

# From Old Testing Patterns

**Old Pattern** (prone to truncation):

```text
python
import subprocess
result = subprocess.run(["python", "-m", "pytest", "test_file.py"], capture_output=True)
print(result.stdout)  

# May be truncated

```text
text

**New Pattern** (reliable):

```text
python
from mcp_task_orchestrator.testing import DirectFunctionRunner
runner = DirectFunctionRunner(output_dir=Path("outputs"))
result = runner.execute_test(test_function, "test_name")

# Complete output available in result.output_file

```text
text

#

#

# From Direct Database Connections

**Old Pattern** (resource warnings):

```python
import sqlite3
conn = sqlite3.connect("test.db")

# ... work ...

conn.close()  

# May not be called on exceptions

```text

**New Pattern** (safe):

```text
python
from tests.utils.db_test_utils import managed_sqlite_connection
with managed_sqlite_connection("test.db") as conn:
    

# ... work ...

    

# Automatic cleanup guaranteed

```text
text

#

# Best Practices

#

#

# 1. Always Use File-Based Output

For any test that generates substantial output:

```text
python
def my_test_function():
    writer = TestOutputWriter(output_dir)
    with writer.write_test_output("my_test", "text") as session:
        session.write_line("Starting test...")
        

# ... test logic ...

        session.write_line("Test completed")

```text

#

#

# 2. Use Alternative Runners for Complex Tests

Instead of pytest for complex scenarios:

```text
python

# Direct execution with full output capture

runner = DirectFunctionRunner(output_dir=output_dir)
result = runner.execute_test(test_function, test_name)
assert result.status == "passed"

```text

#

#

# 3. Implement Hang Protection

For any potentially long-running operations:

```text
python
@with_hang_detection("database_migration", timeout=300.0)
async def run_migration():
    

# Migration logic with automatic timeout

    pass

```text

#

#

# 4. Use Context Managers for Resources

Always use context managers for database connections:

```text
python

# DatabasePersistenceManager

with DatabasePersistenceManager(db_url=db_url) as persistence:
    

# Operations guaranteed to clean up

# Direct SQLite connections  

with managed_sqlite_connection(db_path) as conn:
    

# Connection guaranteed to close

```text

#

# Troubleshooting

#

#

# Output Files Not Created

**Symptom**: No output files appear in expected directory.

**Solutions**:

1. Check directory permissions

2. Verify `TestOutputWriter` initialization

3. Ensure `write_test_output` context manager is used properly

#

#

# Tests Still Hanging

**Symptom**: Operations hang despite hang detection.

**Solutions**:

1. Verify `@with_hang_detection` decorator is applied

2. Check timeout values are appropriate

3. Use `hang_protected_operation` context manager

4. Check hang detection statistics: `get_hang_detection_statistics()`

#

#

# Resource Warnings Still Appearing

**Symptom**: ResourceWarnings still generated during tests.

**Solutions**:

1. Use `managed_sqlite_connection` instead of direct `sqlite3.connect`

2. Use `DatabasePersistenceManager` context manager

3. Call `cleanup_db_resources()` in test teardown

4. Check for missing `dispose()` calls

#

#

# Truncated Output

**Symptom**: Test output appears incomplete.

**Solutions**:

1. Use file-based output system instead of direct stdout capture

2. Wait for completion using `reader.wait_for_completion()`

3. Use alternative test runners instead of pytest

4. Check for premature file reading

#

# Testing Your Changes

To validate that improvements are working:

1. **Run Resource Cleanup Tests**:

```text
bash
python tests/test_resource_cleanup.py

```text
text

2. **Run Hang Detection Tests**:

```text
bash
python tests/test_hang_detection.py

```text
text

3. **Test File Output System**:

```text
bash
python tests/demo_file_output_system.py

```text
text

4. **Test Alternative Runners**:

```text
bash
python tests/demo_alternative_runners.py

```text
text

5. **Run Enhanced Migration Test**:

```text
bash
python tests/enhanced_migration_test.py

```text
text

#

# Configuration

#

#

# Timeout Settings

Configure hang detection timeouts:

```text
python
from mcp_task_orchestrator.monitoring.hang_detection import configure_hang_detection

configure_hang_detection(
    default_timeout=60.0,
    warning_timeout=30.0,
    check_interval=5.0
)

```text

#

#

# Output Directory Settings

Configure test output locations:

```text
python
from mcp_task_orchestrator.testing import TestRunnerConfig

config = TestRunnerConfig(
    output_dir=Path("custom_test_outputs"),
    runner_types=['direct', 'migration'],
    verbose=True,
    timeout_per_test=120.0
)
```text

#

# Performance Considerations

#

#

# File System Performance

- Use SSD storage for output directories when possible

- Clean up old test output files periodically

- Consider output directory rotation for long-running systems

#

#

# Memory Usage

- File-based output reduces memory pressure compared to in-memory buffering

- Database connections are properly pooled and reused

- Hang detection uses minimal overhead

#

#

# Scaling

- Alternative test runners can execute tests in parallel

- File-based output supports concurrent test execution

- Database connection management scales with connection pooling

#

# Related Documentation

- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting guide

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Database migration documentation  

- [tests/README.md](tests/README.md) - Test-specific documentation

- [pytest_investigation_instructions.md](pytest_investigation_instructions.md) - Background on pytest issues
