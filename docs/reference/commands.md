# Command Reference

## Installation Commands

### Secure Installer
```bash
# Interactive installation (recommended)
python -m mcp_task_orchestrator_cli.secure_installer_cli

# Batch installation
python -m mcp_task_orchestrator_cli.secure_installer_cli --batch --clients claude-desktop,cursor

# Development mode
python -m mcp_task_orchestrator_cli.secure_installer_cli --dev --enhanced-security
```

### Universal Installer
```bash
# Multi-client batch installation
python -m mcp_task_orchestrator_cli.universal_installer

# Enterprise deployment
python -m mcp_task_orchestrator_cli.universal_installer --deployment-type enterprise
```

### Uninstaller
```bash
# Interactive uninstallation
python -m mcp_task_orchestrator_cli.secure_uninstaller_cli

# Force uninstallation
python -m mcp_task_orchestrator_cli.secure_uninstaller_cli --force

# Uninstall with backup
python -m mcp_task_orchestrator_cli.secure_uninstaller_cli --create-backup
```

## Server Commands

### Start Server
```bash
# Start server
python -m mcp_task_orchestrator.server

# Start with debug logging
MCP_TASK_ORCHESTRATOR_LOG_LEVEL=DEBUG python -m mcp_task_orchestrator.server

# Test server
python -m mcp_task_orchestrator.server --test
```

### Orchestrator Commands (MCP Tools)

#### Session Management
```python
# Initialize new session
orchestrator_initialize_session()

# Get current status
orchestrator_get_status()
```

#### Task Planning
```python
# Plan new task
orchestrator_plan_task(
    description="Task description",
    subtasks_json='[{"title": "Subtask", "description": "Description", "specialist_type": "implementer"}]'
)

# Execute subtask
orchestrator_execute_subtask(task_id="task_id")

# Complete subtask
orchestrator_complete_subtask(
    task_id="task_id",
    summary="Completion summary",
    detailed_work="Detailed work content",
    next_action="continue"
)

# Synthesize results
orchestrator_synthesize_results(parent_task_id="parent_id")
```

#### Server Management
```python
# Health check
orchestrator_health_check()

# Restart server
orchestrator_restart_server()

# Shutdown preparation
orchestrator_shutdown_prepare()

# Restart status
orchestrator_restart_status()

# Reconnection test
orchestrator_reconnect_test()
```

## Diagnostic Commands

### System Diagnostics
```bash
# Comprehensive health check
python scripts/diagnostics/check_status.py

# MCP connection debugging
python scripts/diagnostics/debug_mcp_connections.py

# Verify installation
python scripts/diagnostics/verify_tools.py

# Database diagnostics
python scripts/diagnostics/diagnose_db.py
```

### Testing Commands
```bash
# Run test suite
python simple_test_runner.py

# Validation tests
python test_validation_runner.py

# Resource cleanup tests
python tests/test_resource_cleanup.py

# Specific test file
python -m pytest tests/test_specific.py -v
```

## Maintenance Commands

### Database Management
```bash
# Database backup
python scripts/maintenance/backup_database.py

# Database optimization
python scripts/maintenance/optimize_database.py

# Schema migration
python scripts/maintenance/migrate_schema.py
```

### File Management
```bash
# Clean temporary files
python scripts/maintenance/cleanup_temp_files.py

# Archive old tasks
python scripts/maintenance/archive_tasks.py

# Backup configurations
python scripts/maintenance/backup_configs.py
```

## Development Commands

### Project Setup
```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

### Release Management
```bash
# Version bump
python scripts/release/bump_version.py --version minor

# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
python scripts/release/upload.py

# Automated release
python scripts/release/pypi_release_automation.py
```

## Environment Variables

### Server Configuration
```bash
# Log level
export MCP_TASK_ORCHESTRATOR_LOG_LEVEL=DEBUG

# Database path
export MCP_TASK_ORCHESTRATOR_DB_PATH=/custom/path/db.sqlite

# State directory
export MCP_TASK_ORCHESTRATOR_STATE_DIR=/custom/state/dir
```

### Development Settings
```bash
# Development mode
export MCP_TASK_ORCHESTRATOR_DEV_MODE=true

# Test database
export MCP_TASK_ORCHESTRATOR_TEST_DB=memory

# Debug features
export MCP_TASK_ORCHESTRATOR_DEBUG_FEATURES=true
```

## Quick References

### Most Common Commands
```bash
# Install
python -m mcp_task_orchestrator_cli.secure_installer_cli

# Start server
python -m mcp_task_orchestrator.server

# Health check
python scripts/diagnostics/check_status.py

# Run tests
python simple_test_runner.py
```

### Emergency Procedures
```bash
# Emergency server restart
python scripts/emergency/force_restart.py

# Restore from backup
python scripts/emergency/restore_backup.py

# Clean reset
python scripts/emergency/clean_reset.py
```