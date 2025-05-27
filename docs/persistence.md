# Task Persistence in MCP Task Orchestrator

## Overview

The MCP Task Orchestrator includes a robust task persistence mechanism to prevent task loss during restarts or context resets. This feature creates a `.task_orchestrator` folder in the project base directory to store persistent state, including task data and role configuration files.

## Directory Structure

```text
.task_orchestrator/
├── roles/                  # Role configuration files
│   ├── default_roles.yaml  # Default roles (migrated from config/specialists.yaml)
│   ├── custom_roles.yaml   # User-defined roles (optional)
│   └── templates/          # Role templates (migrated from config/templates/)
├── tasks/                  # Persisted task state
│   ├── active/             # Currently active tasks
│   └── archive/            # Completed tasks
├── locks/                  # Lock files for concurrent access
└── logs/                   # Persistence-related logs
```

## Features

### Task State Persistence

All task state is automatically persisted to disk in the `.task_orchestrator/tasks/` directory. This includes:

- Task breakdowns
- Subtask details
- Task status
- Results and artifacts

The system automatically saves task state after every significant state change, ensuring that no work is lost even if the orchestrator is restarted or the context is reset.

### Automatic Recovery

When the MCP Task Orchestrator starts, it automatically checks for interrupted tasks in the `.task_orchestrator/tasks/active/` directory. If found, it offers to resume these tasks, allowing seamless continuation of work.

### Role Configuration Persistence

Role configuration files are stored in the `.task_orchestrator/roles/` directory. This includes:

- Default roles (migrated from `config/specialists.yaml`)
- Custom roles (user-defined)
- Role templates (migrated from `config/templates/`)

### Concurrent Access Protection

The persistence mechanism includes file locking to prevent concurrent access to state files. This ensures data integrity even when multiple instances of the orchestrator are running.

## Migration

When upgrading to version 1.3.0 or later, existing configuration files are automatically migrated to the new `.task_orchestrator` directory structure. This includes:

- `config/specialists.yaml` → `.task_orchestrator/roles/default_roles.yaml`
- `config/templates/` → `.task_orchestrator/roles/templates/`

You can also manually migrate your configuration using the provided migration utility:

```bash
python scripts/migrate_to_persistence.py
```

## Configuration

The persistence mechanism can be configured using environment variables:

- `MCP_TASK_ORCHESTRATOR_BASE_DIR`: Base directory for the persistence storage (default: project root)
- `MCP_TASK_ORCHESTRATOR_CONFIG_DIR`: Directory for configuration files (default: `.task_orchestrator/roles/`)

## Troubleshooting

### Stale Lock Files

If the orchestrator crashes or is terminated abruptly, it may leave stale lock files in the `.task_orchestrator/locks/` directory. These are automatically cleaned up after 1 hour, but you can manually remove them if needed.

### Corrupted State Files

If a state file becomes corrupted, the orchestrator will log an error and continue operation. You can manually remove corrupted files from the `.task_orchestrator/tasks/active/` directory.

### Recovering from Backup

The persistence mechanism does not currently include automatic backups. If you need to recover from a backup, you can manually restore the `.task_orchestrator` directory from your backup system.

## Best Practices

1. **Regular Backups**: While the persistence mechanism is robust, it's still a good idea to regularly back up the `.task_orchestrator` directory.

2. **Clean Archiving**: Completed tasks are automatically archived to `.task_orchestrator/tasks/archive/`. You may want to periodically clean this directory to prevent it from growing too large.

3. **Custom Roles**: Store custom role configurations in `.task_orchestrator/roles/custom_roles.yaml` to avoid them being overwritten during updates.

4. **Environment Variables**: Use environment variables to configure the persistence mechanism, especially in containerized environments.

## Technical Details

The persistence mechanism uses a combination of SQLite (for in-memory operations) and JSON files (for persistent storage). This provides both performance and durability.

File operations use atomic writes to prevent corruption, and file locking to prevent concurrent access. The system is designed to be resilient to crashes and unexpected terminations.

## Limitations

- The persistence mechanism does not currently support distributed deployment (multiple servers sharing the same state).
- There is no built-in retention policy for archived tasks. You may need to implement your own cleanup process.
- The persistence mechanism does not include encryption. Sensitive data should not be stored in tasks.
