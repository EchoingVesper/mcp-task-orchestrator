

# Database-Backed Persistence

#

# Overview

The MCP Task Orchestrator now supports a robust database-backed persistence mechanism that replaces the previous file-based system. This implementation eliminates lock contention issues and provides proper transaction support.

#

# Features

- **Transaction Support**: All operations are wrapped in database transactions

- **Concurrent Access**: Multiple processes can safely access the database simultaneously

- **Error Handling**: Improved error handling and recovery

- **Backward Compatibility**: Maintains the same API as the file-based system

- **Migration Support**: Tools for migrating existing tasks to the new database

#

# Implementation Details

#

## Technology Stack

- **SQLAlchemy**: A powerful ORM with transaction support

- **SQLite**: A lightweight, serverless database engine

- **Alembic**: Database migration tool (for future schema changes)

#

## Architecture

The database persistence implementation follows the same interface as the file-based system, allowing for a smooth transition. The key components are:

1. **Database Models**: SQLAlchemy ORM models that map directly to the domain models

2. **Persistence Manager**: Handles database operations with proper transaction boundaries

3. **Migration Tools**: Utilities for migrating from file-based to database-backed persistence

4. **Factory Pattern**: A factory function that creates the appropriate persistence manager

#

# Usage

#

## Configuration

You can enable the database-backed persistence in one of the following ways:

1. **Environment Variable**:

   

```bash
   export MCP_TASK_ORCHESTRATOR_USE_DB=true
   ```

2. **Programmatically**:

   ```

python
   from mcp_task_orchestrator.persistence_factory import create_persistence_manager
   
   

# Create a database-backed persistence manager

   persistence = create_persistence_manager(use_database=True)
   

```text

3. **StateManager Initialization**:

   ```

python
   from mcp_task_orchestrator.orchestrator.state import StateManager
   
   

# Create a state manager with database-backed persistence

   state_manager = StateManager(use_database=True)
   

```text

#

## Database URL

By default, the database is stored in a SQLite file in the persistence directory. You can customize the database URL:

1. **Environment Variable**:

   ```

bash
   export MCP_TASK_ORCHESTRATOR_DB_URL="sqlite:///path/to/database.db"
   

```text

2. **Programmatically**:

   ```

python
   from mcp_task_orchestrator.persistence_factory import create_persistence_manager
   
   

# Create a persistence manager with a custom database URL

   persistence = create_persistence_manager(
       db_url="sqlite:///path/to/database.db",
       use_database=True
   )
   

```text

#

# Migration

To migrate existing tasks from the file-based system to the database-backed system, use the provided migration script:

```text
text
bash
python migrate_to_db.py

```text

#

## Options

- `--base-dir`: Base directory for the persistence storage (default: current directory)

- `--db-url`: SQLAlchemy database URL (default: SQLite database in base directory)

- `--dry-run`: Perform a dry run without actually migrating data

#

## Example

```text
bash
python migrate_to_db.py --base-dir /path/to/base/dir --db-url "sqlite:///path/to/database.db"

```text

#

# Troubleshooting

#

## Logging

The database persistence implementation logs detailed information about its operations. Logs are stored in the `.task_orchestrator/logs/db_persistence.log` file.

#

## Common Issues

1. **Migration Failures**: If migration fails, check the migration log for details. You can run the migration script with the `--dry-run` option to see what would be migrated without making any changes.

2. **Database Errors**: If you encounter database errors, check the db_persistence.log file for details. Common issues include permission problems and disk space limitations.

3. **Compatibility Issues**: If you encounter compatibility issues, you can switch back to the file-based system by setting `MCP_TASK_ORCHESTRATOR_USE_DB=false`.

#

# Development

#

## Adding New Features

When adding new features to the database persistence implementation, follow these guidelines:

1. **Maintain API Compatibility**: Ensure that any changes maintain compatibility with the existing API.

2. **Use Transactions**: Wrap all database operations in transactions using the `session_scope` context manager.

3. **Handle Errors**: Properly handle errors and provide meaningful error messages.

4. **Add Tests**: Add unit tests for new features to ensure they work correctly.

#

## Testing

To run the database persistence tests:

```text
bash
python -m unittest tests.test_db_persistence
```text
