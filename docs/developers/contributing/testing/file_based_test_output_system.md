

# File-Based Test Output System Documentation

#

# Overview

The File-Based Test Output System solves the critical timing issue where LLM calls check test results before tests have finished writing their output, resulting in truncated or incomplete data being read.

#

# The Problem

In the original MCP Task Orchestrator testing setup:

1. **Tests write extensive output** to stdout using `print()` statements

2. **LLM systems call pytest** and attempt to read results immediately

3. **Timing race condition** occurs where LLM reads before test finishes writing

4. **Truncated output** is captured, missing critical test information

5. **Unreliable test validation** results from incomplete data

#

# The Solution

The File-Based Test Output System provides:

#

## Core Features

- **Atomic File Writes**: Prevents reading partially written files

- **Completion Signaling**: `.done` files indicate when tests are finished

- **Safe Reading**: Wait-and-verify pattern ensures complete output

- **Thread-Safe Operations**: Supports concurrent test execution

- **Multiple Formats**: Text, JSON, and structured output support

#

## Key Components

#

### 1. TestOutputWriter

Handles writing test output to files with atomic operations:

```python
from mcp_task_orchestrator.testing import TestOutputWriter

writer = TestOutputWriter("./test_outputs")

with writer.write_test_output("my_test", "text") as session:
    session.write_line("Test output line")
    session.write_json({"key": "value"})
    

# File is atomically committed when context exits

```text

#

### 2. TestOutputReader

Safely reads completed test output files:

```text
python
from mcp_task_orchestrator.testing import TestOutputReader

reader = TestOutputReader("./test_outputs")

# Wait for test completion (prevents reading truncated output)

if reader.wait_for_completion("test_output.txt", timeout=30):
    content = reader.read_completed_output("test_output.txt")
    

# Content is guaranteed to be complete

```text

#

### 3. Pytest Integration

Seamless integration with existing pytest tests:

```text
python
from mcp_task_orchestrator.testing import file_output_test

@file_output_test("my_test_name")
def test_example():
    print("This output will be captured to a file")
    print("LLM systems can safely read it after completion")
    assert True

```text

#

# Usage Examples

#

## Basic Usage

```text
python
#!/usr/bin/env python3
from mcp_task_orchestrator.testing import TestOutputWriter, TestOutputReader

# Writing test output

writer = TestOutputWriter()
with writer.write_test_output("migration_test", "text") as session:
    session.write_line("=== Starting Migration Test ===")
    
    

# Simulate test work

    for i in range(100):
        session.write_line(f"Processing record {i}")
    
    session.write_line("=== Test Completed Successfully ===")

# Reading test output (from LLM system)

reader = TestOutputReader()
output_file = "migration_test_20240530_123456.txt"

# Wait for completion (this prevents timing issues!)

if reader.wait_for_completion(output_file, timeout=60):
    content = reader.read_completed_output(output_file)
    print(f"Test output ({len(content)} chars): {content}")
else:
    print("Test did not complete within timeout")

```text

#

## Integration with Existing Tests

For the migration test that was experiencing truncation:

```text
python

# Enhanced migration test

from tests.enhanced_migration_test import EnhancedMigrationTestRunner

# Run the test

runner = EnhancedMigrationTestRunner()
success = runner.run_migration_test_with_file_output("/tmp/test")

# Get output file location  

output_file = runner.get_latest_test_output_file()

# LLM system can now safely wait and read

success, content = runner.wait_for_test_completion_and_read("migration_test")
if success:
    

# Process complete test output

    analyze_migration_results(content)

```text

#

# File Structure

The system creates several files for each test:

```text

test_outputs/
├── migration_test_20240530_123456.txt      

# Main output file

├── migration_test_20240530_123456.done     

# Completion marker

├── migration_test_20240530_123456.meta.json 

# Test metadata

└── migration_test_20240530_123456.tmp      

# Temporary file (during writing)

```text

#

## File Types

- **`.txt`**: Main test output content

- **`.done`**: Completion marker with timestamp and file size

- **`.meta.json`**: Test metadata (name, duration, status, etc.)

- **`.tmp`**: Temporary file during writing (automatically cleaned up)

#

# Configuration

#

## Custom Output Directory

```text
python
from mcp_task_orchestrator.testing import configure_pytest_integration

# Configure custom output location

configure_pytest_integration("/custom/test/outputs")

```text

#

## Timeout Settings

```text
python

# Wait for test completion with custom timeout

reader.wait_for_completion(output_file, timeout=120.0)  

# 2 minutes

# Check completion without waiting

if reader.is_completed(output_file):
    content = reader.read_completed_output(output_file)

```text

#

# Error Handling

The system provides robust error handling:

```text
python
try:
    with writer.write_test_output("test", "text") as session:
        session.write_line("Test output")
        raise Exception("Test failed")
except Exception:
    

# File is automatically cleaned up

    

# Error is recorded in metadata

    pass

# Reading with error handling

content = reader.read_completed_output(output_file)
if content is None:
    print("Failed to read output (file not completed or error)")

```text

#

# Performance Considerations

- **Minimal Overhead**: < 5ms per test for file operations

- **Concurrent Safe**: Multiple tests can run simultaneously  

- **Atomic Operations**: No risk of corrupted files

- **Cleanup**: Temporary files automatically removed

#

# Migration Guide

#

## From Direct pytest Output

**Before** (problematic):

```text
python
def test_migration():
    print("Starting migration...")
    

# ... test logic ...

    print("Migration complete")

# LLM calls pytest and may read truncated output

```text
text

**After** (reliable):

```python
@file_output_test("migration_test")
def test_migration():
    print("Starting migration...")  

# Captured to file

    

# ... test logic ...

    print("Migration complete")     

# Guaranteed in file

# LLM waits for completion then reads full output

```text

#

## From Custom Test Runners

**Before**:

```text
python
def run_test():
    print("Test output")
    

# Output may be truncated when read

```text
text

**After**:

```text
python
from mcp_task_orchestrator.testing import TestOutputWriter

def run_test():
    writer = TestOutputWriter()
    with writer.write_test_output("test", "text") as session:
        session.write_line("Test output")
        

# Output guaranteed complete when context exits

```text
text

#

# Best Practices

1. **Always Use Timeouts**: Set reasonable timeouts for test completion

2. **Check Completion**: Verify tests completed before reading output

3. **Handle Failures**: Check for error conditions in metadata

4. **Clean Naming**: Use descriptive test names for output files

5. **Monitor Performance**: Track test duration and output size

#

# Troubleshooting

#

## Common Issues

**Issue**: Files not being created
**Solution**: Check output directory permissions and disk space

**Issue**: Tests hanging
**Solution**: Verify timeout settings and check for deadlocks

**Issue**: Incomplete output
**Solution**: Ensure using atomic writes and completion checking

#

## Debug Information

```text
python

# Check active test sessions

from mcp_task_orchestrator.testing import get_pytest_output_statistics

stats = get_pytest_output_statistics()
print(f"Active sessions: {stats['active_sessions']}")
print(f"Output directory: {stats['output_directory']}")

```text

#

# Advanced Usage

#

## Custom Output Formats

```text
python

# JSON output

with writer.write_test_output("test", "json") as session:
    session.write_json({"results": test_data})

# Structured output with metadata

with writer.write_test_output("test", "structured") as session:
    session.write_structured_data({
        "test_phase": "migration",
        "records_processed": 100,
        "success": True
    })

```text

#

## Concurrent Test Monitoring

```text
python
import asyncio
from mcp_task_orchestrator.testing import TestOutputReader

async def monitor_tests():
    reader = TestOutputReader()
    
    while True:
        

# Check for new completed tests

        completed_files = reader.list_completed_outputs()
        for file in completed_files:
            if not processed(file):
                content = reader.read_completed_output(file)
                process_test_results(content)
        
        await asyncio.sleep(1.0)
```text

This system completely eliminates the timing issues that were causing test output truncation in the MCP Task Orchestrator.
