

# Maintenance Operations Troubleshooting Guide

*Comprehensive guide for resolving maintenance coordinator issues*

#

# Common Issues and Solutions

#

## 1. Operation Timeouts

#

### Symptoms

```json
{
  "error": "Operation timed out",
  "action": "scan_cleanup",
  "suggestions": "Try again with a smaller scope or basic validation level"
}

```text

#

### Causes

- Large number of tasks in scope

- Database performance issues

- System resource constraints

- Network connectivity problems

#

### Solutions

1. **Reduce Scope**: Use `current_session` instead of `full_project`

2. **Lower Validation Level**: Start with `basic` instead of `comprehensive`

3. **Break Into Batches**: Run multiple smaller operations

4. **Check Resources**: Ensure adequate memory and CPU availability

#

### Example Recovery

```text
bash

# Instead of this (times out):

{"action": "scan_cleanup", "scope": "full_project", "validation_level": "full_audit"}

# Try this:

{"action": "scan_cleanup", "scope": "current_session", "validation_level": "basic"}

```text

#

## 2. Database Connection Errors

#

### Symptoms

- Connection refused errors

- Database lock timeouts

- Permission denied errors

- SQLite database is locked

#

### Causes

- Concurrent database access

- Insufficient permissions

- Corrupted database files

- File system issues

#

### Solutions

1. **Restart Server**: Stop and restart the MCP server

2. **Check Permissions**: Ensure database files are writable

3. **Wait and Retry**: Allow concurrent operations to complete

4. **Database Repair**: Use SQLite repair tools if needed

#

### Diagnostic Commands

```text
bash

# Check database file permissions

ls -la .task_orchestrator/database/

# Check for lock files

ls -la .task_orchestrator/database/*.lock

# Test database connectivity

sqlite3 .task_orchestrator/database/tasks.db ".schema"

```text

#

## 3. Target Task Not Found

#

### Symptoms

```text
json
{
  "error": "Target task not found",
  "target_task_id": "invalid_task_123",
  "scope": "specific_subtask"
}

```text

#

### Causes

- Incorrect task ID

- Task already archived

- Task from different session

- Typo in task identifier

#

### Solutions

1. **Verify Task ID**: Use `orchestrator_get_status` to list active tasks

2. **Check Archives**: Task may have been previously archived

3. **Use Broader Scope**: Switch to `current_session` or `full_project`

4. **Double-check Spelling**: Ensure task ID is correct

#

### Example Verification

```text
json
// First, check what tasks exist
{"action": "orchestrator_get_status", "include_completed": true}

// Then target the correct task
{"action": "validate_structure", "scope": "specific_subtask", "target_task_id": "correct_task_id"}

```text

#

## 4. No Maintenance Actions Needed

#

### Symptoms

```text
json
{
  "scan_results": {"stale_tasks": [], "orphaned_tasks": []},
  "cleanup_actions": [],
  "summary": {"cleanup_actions_performed": 0}
}

```text

#

### Analysis

This is actually a **positive result** indicating:

- System is well-maintained

- No stale or orphaned tasks exist

- Database is optimized

- Regular maintenance is working

#

### When This Occurs

- After recent maintenance

- In new or small projects

- With good maintenance hygiene

- After successful cleanup operations

#

### No Action Required

This result means your system is healthy and optimized.

#

## 5. Partial Cleanup Failures

#

### Symptoms

```text
json
{
  "cleanup_actions": [
    {"result": "archived_successfully"},
    {"result": "failed", "error": "Permission denied"}
  ]
}

```text

#

### Causes

- Mixed permission issues

- File system constraints

- Concurrent access conflicts

- Disk space limitations

#

### Solutions

1. **Review Successful Actions**: Partial completion is better than none

2. **Address Specific Failures**: Handle failed items individually

3. **Retry Failed Items**: Run maintenance again to catch missed items

4. **Check System Resources**: Ensure adequate disk space and permissions

#

## 6. Memory or Performance Issues

#

### Symptoms

- Slow maintenance operations

- High memory usage during cleanup

- System becomes unresponsive

- Operations never complete

#

### Immediate Actions

1. **Reduce Batch Size**: Use smaller scopes

2. **Basic Validation Only**: Avoid `full_audit` on large datasets

3. **Close Other Applications**: Free up system resources

4. **Monitor Progress**: Check logs for operation status

#

### Long-term Solutions

```text
bash

# Check system resources

free -h                    

# Memory usage

df -h                     

# Disk space

top                       

# CPU usage

# Optimize database

sqlite3 .task_orchestrator/database/tasks.db "VACUUM;"

```text

#

## 7. Archive Recovery Issues

#

### Symptoms

- Need to recover archived task

- Accidentally archived important data

- Archive retention expired

#

### Solutions

1. **Check Archive Table**: Query database for archived tasks

2. **Restore from Archive**: Use database tools to restore if within 30 days

3. **Contact Administrator**: For expired archives or complex recovery

#

### Archive Query Example

```text
sql
SELECT * FROM task_archives 
WHERE original_task_id = 'target_task_id' 
AND expires_at > datetime('now');

```text

#

# Diagnostic Procedures

#

## 1. Basic Health Check

```text
json
{
  "action": "validate_structure",
  "scope": "current_session", 
  "validation_level": "basic"
}

```text

#

## 2. Performance Analysis

```text
json
{
  "action": "scan_cleanup",
  "scope": "current_session",
  "validation_level": "basic"
}

```text

#

## 3. Comprehensive Audit

```text
json
{
  "action": "validate_structure",
  "scope": "full_project",
  "validation_level": "full_audit"
}

```text

#

# Prevention Strategies

#

## Regular Maintenance Schedule

```text

Daily: Basic session cleanup
Weekly: Comprehensive session cleanup
Monthly: Full project cleanup
Quarterly: Complete system audit

```text

#

## Monitoring Guidelines

- Watch for increasing task counts

- Monitor maintenance operation duration

- Track cleanup action frequency

- Review recommendation trends

#

## System Optimization

- Keep active tasks under 100 for optimal performance

- Archive completed workflows promptly

- Run cleanup before major operations

- Monitor disk space and database size

#

# Error Code Reference

| Error Type | Code | Description | Solution |
|------------|------|-------------|----------|
| Timeout | `TIMEOUT` | Operation exceeded time limit | Reduce scope or validation level |
| Permission | `PERM_DENIED` | Insufficient file/database permissions | Check and fix permissions |
| Not Found | `NOT_FOUND` | Target task doesn't exist | Verify task ID with get_status |
| Database | `DB_ERROR` | Database connectivity or corruption | Restart server, check database |
| Resource | `RESOURCE_LIMIT` | Memory or disk constraints | Free resources, reduce batch size |

#

# Emergency Recovery

#

## Complete System Reset

```text
bash

# CAUTION: This will lose all task data

rm -rf .task_orchestrator/database/

# Restart MCP server to recreate database

```text

#

## Database Repair

```bash

# Create backup first

cp .task_orchestrator/database/tasks.db tasks.db.backup

# Repair database

sqlite3 .task_orchestrator/database/tasks.db "PRAGMA integrity_check;"
sqlite3 .task_orchestrator/database/tasks.db "VACUUM;"

```text

#

## Log Analysis

```text
bash

# Check recent maintenance operations

tail -n 100 .task_orchestrator/logs/maintenance.log

# Search for specific errors

grep -i "error" .task_orchestrator/logs/maintenance.log
```text

#

# Getting Help

#

## Information to Collect

1. **Error Message**: Complete error response

2. **Operation Details**: Action, scope, validation level

3. **System Information**: OS, Python version, disk space

4. **Recent Changes**: What was done before the error occurred

5. **Task Count**: Number of active tasks in system

#

## Escalation Path

1. **Self-Service**: Use this troubleshooting guide

2. **Documentation**: Check user guide and FAQ

3. **Community**: Search existing issues and discussions

4. **Support**: Contact development team with collected information

---

*Keep this guide accessible during maintenance operations for quick issue resolution.*
