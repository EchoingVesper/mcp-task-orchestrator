

# Testing Best Practices Guide

#

# Quick Start

#

#

# 1. Use File-Based Output for All Tests

**Do this:**

```python
from mcp_task_orchestrator.testing import TestOutputWriter

writer = TestOutputWriter(output_dir)
with writer.write_test_output("my_test", "text") as session:
    session.write_line("Test output here...")

```text

**Not this:**

```text
text
python
print("Test output...")  

# May be truncated

```text
text

#

#

# 2. Use Alternative Test Runners

**Do this:**

```text
python
from mcp_task_orchestrator.testing import DirectFunctionRunner

runner = DirectFunctionRunner(output_dir=Path("outputs"))
result = runner.execute_test(my_test_function, "test_name")

```text
text

**Not this:**

```text
bash
pytest my_test.py  

# May have truncation issues

```text
text

#

#

# 3. Use Context Managers for Database Connections

**Do this:**

```text
python
from tests.utils.db_test_utils import managed_sqlite_connection

with managed_sqlite_connection("test.db") as conn:
    

# Work with connection

    pass  

# Automatic cleanup

```text
text

**Not this:**

```text
python
import sqlite3
conn = sqlite3.connect("test.db")

# Work with connection

conn.close()  

# May not be called on exceptions

```text
text

#

#

# 4. Add Hang Protection

**Do this:**

```text
python
from mcp_task_orchestrator.monitoring.hang_detection import with_hang_detection

@with_hang_detection("my_operation", timeout=30.0)
async def my_operation():
    

# Protected operation

    pass

```text
text

**Not this:**

```text
python
async def my_operation():
    

# Unprotected - may hang forever

    pass

```text
text

#

# Common Patterns

#

#

# Testing Database Operations

```text
python
from tests.utils.db_test_utils import DatabaseTestCase

class MyTest(DatabaseTestCase):
    def test_database_operation(self):
        with self.get_managed_connection("test.db") as conn:
            

# Test database operations

            pass
        

# Cleanup happens automatically

```text

#

#

# Testing Long-Running Operations

```text
python
from mcp_task_orchestrator.testing import TestOutputWriter
from mcp_task_orchestrator.monitoring.hang_detection import with_hang_detection

@with_hang_detection("long_test", timeout=60.0)
async def test_long_operation():
    writer = TestOutputWriter(output_dir)
    with writer.write_test_output("long_test", "text") as session:
        session.write_line("Starting long operation...")
        

# Long operation here

        session.write_line("Operation completed")

```text

#

#

# Safe Test Output Reading

```text
python
from mcp_task_orchestrator.testing import TestOutputReader

reader = TestOutputReader(output_dir)
output_file = find_latest_output_file("test_name")

if reader.wait_for_completion(output_file, timeout=30.0):
    content = reader.read_completed_output(output_file)
    

# Process complete content

else:
    print("Test did not complete within timeout")

```text

#

# Validation Checklist

Before deploying tests:

- [ ] Use file-based output for substantial output

- [ ] Add hang protection for operations > 10 seconds  

- [ ] Use context managers for all database connections

- [ ] Test with alternative runners, not just pytest

- [ ] Validate no ResourceWarnings in test runs

- [ ] Ensure proper cleanup in test teardown

- [ ] Test timeout scenarios work correctly

#

# Quick Commands

```text
bash

# Test resource cleanup

python tests/test_resource_cleanup.py

# Test hang detection

python tests/test_hang_detection.py

# Demo file output system

python tests/demo_file_output_system.py

# Demo alternative runners

python tests/demo_alternative_runners.py

# Run enhanced migration test

python tests/enhanced_migration_test.py
```text

#

# Need Help?

- Check [TESTING_IMPROVEMENTS.md](TESTING_IMPROVEMENTS.md) for detailed documentation

- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

- Examine test files in `tests/` directory for examples
