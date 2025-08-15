

# Database Issues Troubleshooting Guide

#

# Common Database Problems

#

#

# 1. Database Lock Errors

**Symptoms:**

- "database is locked" error messages

- Tasks hanging during database operations  

- SQLite busy errors

**Diagnosis:**

```bash

# Check for active database connections

python scripts/diagnostics/diagnose_db.py

# Verify database file permissions

ls -la task_orchestrator.db*

# Check for stale lock files

ls -la .task_orchestrator/locks/

```text

**Solutions:**

```text
text
bash

# Clean up stale locks

python scripts/diagnostics/check_status.py --cleanup-locks

# Force unlock database (use with caution)

python scripts/diagnostics/diagnose_db.py --force-unlock

# Restart with fresh database connection

python scripts/maintenance/run_with_db.py --reset-connections

```text
text

#

#

# 2. Performance Issues

**Symptoms:**

- Slow database operations (>5 seconds)

- High CPU usage during database access

- Memory usage growing over time

**Diagnosis:**

```text
bash

# Run performance benchmark

python tests/performance/performance_benchmark.py

# Check database statistics  

python scripts/diagnostics/diagnose_db.py --stats

# Monitor resource usage

python scripts/diagnostics/check_status.py --monitor
```text
text

**Solutions:**

- Run database optimization: `VACUUM` and `ANALYZE`

- Check for missing indexes on frequently queried columns

- Consider increasing database cache size

- Monitor and close unused connections
