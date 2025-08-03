# Troubleshooting Guide

Quick solutions to common issues with the MCP Task Orchestrator.

## Installation Issues

### MCP Tools Not Showing Up

**Symptoms**: Task orchestrator tools don't appear in your MCP client.

**Solutions**:

1. **Check Configuration**:
   ```json
   // Verify your MCP client config
   {
     "mcpServers": {
       "task-orchestrator": {
         "command": "python",
         "args": ["-m", "mcp_task_orchestrator.server"],
         "env": {}
       }
     }
   }
   ```

2. **Verify Installation**:
   ```bash
   # Test the server directly
   python -m mcp_task_orchestrator.server
   
   # Check if package is installed
   pip list | grep mcp-task-orchestrator
   ```

3. **Check Python Path**:
   ```bash
   # Ensure Python is accessible
   which python
   python --version
   
   # Use full Python path if needed
   {
     "command": "/usr/bin/python3",
     "args": ["-m", "mcp_task_orchestrator.server"]
   }
   ```

4. **Restart Your MCP Client**: After configuration changes, restart your client completely.

### Import Errors

**Symptoms**: `ModuleNotFoundError` or import-related errors.

**Solutions**:

1. **Reinstall Package**:
   ```bash
   pip uninstall mcp-task-orchestrator
   pip install mcp-task-orchestrator
   ```

2. **Check Python Version**:
   ```bash
   python --version  # Should be 3.8+
   ```

3. **Virtual Environment Issues**:
   ```bash
   # If using venv, ensure it's activated
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   pip install mcp-task-orchestrator
   ```

### Permission Errors

**Symptoms**: Can't create `.task_orchestrator` directory or database files.

**Solutions**:

1. **Check Directory Permissions**:
   ```bash
   # Ensure write access to project directory
   ls -la /path/to/your/project
   chmod 755 /path/to/your/project
   ```

2. **Use Different Directory**:
   ```python
   # Initialize in a writable directory
   orchestrator_initialize_session(working_directory="/tmp/test-project")
   ```

## Runtime Issues

### Database Errors

**Symptoms**: SQLite errors, database corruption, or connection issues.

**Solutions**:

1. **Reset Database**:
   ```bash
   # Remove corrupted database
   rm .task_orchestrator/tasks.db
   
   # Reinitialize
   orchestrator_initialize_session()
   ```

2. **Check Disk Space**:
   ```bash
   df -h  # Ensure sufficient disk space
   ```

3. **Database Recovery**:
   ```bash
   # Backup current database
   cp .task_orchestrator/tasks.db .task_orchestrator/tasks.db.backup
   
   # Try to repair
   sqlite3 .task_orchestrator/tasks.db "PRAGMA integrity_check;"
   ```

### Task Execution Failures

**Symptoms**: Tasks fail to execute or complete unexpectedly.

**Solutions**:

1. **Check Task Status**:
   ```python
   # View current task status
   orchestrator_get_status(include_completed=True)
   
   # Query specific task
   orchestrator_query_tasks(search_text="your task name")
   ```

2. **Review Error Logs**:
   ```python
   # Check for error details
   task_details = orchestrator_query_tasks(
       task_id="problematic_task_id",
       include_artifacts=True
   )
   ```

3. **Restart Session**:
   ```python
   # Sometimes a fresh session helps
   orchestrator_initialize_session()
   ```

### Memory Issues

**Symptoms**: Slow performance, high memory usage, or crashes.

**Solutions**:

1. **Clean Up Old Tasks**:
   ```python
   # Run maintenance cleanup
   orchestrator_maintenance_coordinator(
       action="scan_cleanup",
       scope="full_project"
   )
   ```

2. **Limit Task Complexity**:
   ```python
   # Break large tasks into smaller subtasks
   orchestrator_plan_task(
       title="Large Task - Part 1",
       complexity="moderate"  # Instead of "very_complex"
   )
   ```

3. **Archive Completed Work**:
   ```bash
   # Move old artifacts to archive
   mkdir .task_orchestrator/archives
   mv .task_orchestrator/artifacts/old_* .task_orchestrator/archives/
   ```

## Configuration Issues

### Working Directory Detection

**Symptoms**: Orchestrator creates `.task_orchestrator` in wrong location.

**Solutions**:

1. **Specify Working Directory**:
   ```python
   # Always specify the correct path
   orchestrator_initialize_session(
       working_directory="/correct/project/path"
   )
   ```

2. **Check Current Directory**:
   ```bash
   pwd  # Verify you're in the right directory
   cd /path/to/your/project
   ```

3. **Git Repository Detection**:
   ```bash
   # Ensure you're in a git repository
   git status
   
   # Or initialize one
   git init
   ```

### Template Issues

**Symptoms**: Template validation errors or instantiation failures.

**Solutions**:

1. **Validate Template Syntax**:
   ```python
   # Check your template syntax
   template_validate(template_content="your template content")
   ```

2. **Check Template Parameters**:
   ```python
   # Ensure all required parameters are provided
   template_info(template_id="your_template")
   ```

3. **Reset Template System**:
   ```python
   # Reinstall default templates
   template_install_default_library(overwrite=True)
   ```

## Performance Issues

### Slow Response Times

**Symptoms**: Tools take a long time to respond.

**Solutions**:

1. **Health Check**:
   ```python
   # Check overall system health
   orchestrator_health_check()
   ```

2. **Database Optimization**:
   ```python
   # Run maintenance
   orchestrator_maintenance_coordinator(
       action="validate_structure",
       validation_level="comprehensive"
   )
   ```

3. **Reduce Task Complexity**:
   - Break large tasks into smaller pieces
   - Use more specific task descriptions
   - Limit the number of concurrent tasks

### High Resource Usage

**Symptoms**: High CPU or memory usage.

**Solutions**:

1. **Monitor Resource Usage**:
   ```bash
   # Check system resources
   top
   htop
   ```

2. **Restart Server**:
   ```python
   # Graceful server restart
   orchestrator_restart_server(graceful=True)
   ```

3. **Clear Cache**:
   ```bash
   # Clear Python cache
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -type d -exec rm -rf {} +
   ```

## Diagnostic Commands

### System Health

```python
# Comprehensive health check
orchestrator_health_check(
    include_database_status=True,
    include_connection_status=True,
    include_reboot_readiness=True
)
```

### Connection Testing

```python
# Test client connections
orchestrator_reconnect_test(
    include_reconnection_stats=True,
    include_buffer_status=True
)
```

### Database Validation

```python
# Validate task structure
orchestrator_maintenance_coordinator(
    action="validate_structure",
    validation_level="full_audit"
)
```

### Template System Check

```python
# Validate all templates
template_validate_all()

# Check installation status
template_get_installation_status()
```

## Common Error Messages

### "TaskNotFound"

**Cause**: Trying to access a task that doesn't exist.

**Solution**:
```python
# List all available tasks
orchestrator_get_status(include_completed=True)

# Search for tasks
orchestrator_query_tasks(search_text="partial task name")
```

### "PermissionDenied"

**Cause**: Insufficient permissions for the requested operation.

**Solution**:
1. Check file/directory permissions
2. Ensure you're in the correct working directory
3. Verify you have write access to the project

### "DatabaseError"

**Cause**: SQLite database issues.

**Solution**:
1. Check disk space
2. Verify database file isn't corrupted
3. Reset database if necessary (see Database Errors section)

### "TemplateError"

**Cause**: Template syntax or validation issues.

**Solution**:
1. Validate template syntax
2. Check parameter requirements
3. Use known-good templates for testing

## Getting Help

### Diagnostic Information

When reporting issues, include:

1. **System Information**:
   ```bash
   python --version
   pip list | grep mcp-task-orchestrator
   uname -a  # Linux/Mac
   ```

2. **Configuration**:
   - Your MCP client configuration
   - Working directory structure
   - Any custom settings

3. **Error Details**:
   - Full error messages
   - Steps to reproduce
   - Expected vs actual behavior

### Health Report

Generate a comprehensive health report:

```python
# Generate diagnostic information
health = orchestrator_health_check()
status = orchestrator_get_status(include_completed=True)
```

### Log Files

Check for log files in:
- `.task_orchestrator/logs/`
- Your MCP client's log directory
- System logs for Python errors

## Advanced Troubleshooting

### Server Management

```python
# Check restart status
orchestrator_restart_status(include_error_details=True)

# Prepare for shutdown
orchestrator_shutdown_prepare()

# Graceful restart
orchestrator_restart_server(preserve_state=True)
```

### Manual Database Recovery

If automatic recovery fails:

```bash
# Backup current state
cp -r .task_orchestrator .task_orchestrator.backup

# Export data
sqlite3 .task_orchestrator/tasks.db ".dump" > backup.sql

# Recreate database
rm .task_orchestrator/tasks.db
orchestrator_initialize_session()

# Manual data recovery (if needed)
sqlite3 .task_orchestrator/tasks.db < backup.sql
```

### Reset Everything

Last resort - complete reset:

```bash
# Backup important artifacts
cp -r .task_orchestrator/artifacts ./artifacts_backup

# Remove orchestrator data
rm -rf .task_orchestrator

# Reinstall and reinitialize
pip install --upgrade mcp-task-orchestrator
orchestrator_initialize_session()

# Restore important artifacts manually
```

## Prevention

### Best Practices

1. **Regular Maintenance**:
   ```python
   # Run weekly cleanup
   orchestrator_maintenance_coordinator(action="scan_cleanup")
   ```

2. **Monitor Health**:
   ```python
   # Regular health checks
   orchestrator_health_check()
   ```

3. **Backup Important Work**:
   ```bash
   # Backup artifacts regularly
   cp -r .task_orchestrator/artifacts ./backups/$(date +%Y%m%d)
   ```

4. **Keep Software Updated**:
   ```bash
   pip install --upgrade mcp-task-orchestrator
   ```

### Monitoring

Set up regular monitoring:
- Check disk space
- Monitor memory usage
- Validate database integrity
- Test basic functionality

## Support

If problems persist:

1. **Check Documentation**: Review the [API Reference](../reference/api/API_REFERENCE.md)
2. **GitHub Issues**: [Report issues](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
3. **Community**: [GitHub Discussions](https://github.com/EchoingVesper/mcp-task-orchestrator/discussions)