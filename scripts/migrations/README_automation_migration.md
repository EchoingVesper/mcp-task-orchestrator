# Automation Maintenance Database Migration

## Overview

This migration adds the necessary database schema changes for the Automation Maintenance Enhancement feature in MCP Task Orchestrator v1.4.1.

## What This Migration Does

1. **Adds automation columns to the `subtasks` table:**
   - `prerequisite_satisfaction_required` (BOOLEAN, default: False)
   - `auto_maintenance_enabled` (BOOLEAN, default: True)
   - `quality_gate_level` (TEXT, default: 'standard')

2. **Creates maintenance-related tables:**
   - `task_prerequisites` - For managing task dependencies
   - `maintenance_operations` - For tracking maintenance activities
   - `project_health_metrics` - For monitoring project health

3. **Updates existing records** with appropriate default values

4. **Creates a backup** of your database before making changes

## Running the Migration

### From Project Root

```bash
# Run the migration
python run_automation_migration.py

# Verify only (no changes)
python run_automation_migration.py --verify-only
```

### Direct Script Execution

```bash
# Run from anywhere
python scripts/migrations/migrate_automation_maintenance.py

# Specify custom database path
python scripts/migrations/migrate_automation_maintenance.py --db-path /path/to/orchestrator.db

# Verify only
python scripts/migrations/migrate_automation_maintenance.py --verify-only
```

## Testing the Migration

Run the test script to verify the migration works correctly:

```bash
python tests/test_automation_migration.py
```

## Backup and Recovery

The migration automatically creates a backup before making changes:
- Backup location: `~/.task_orchestrator/orchestrator.db.backup_YYYYMMDD_HHMMSS`
- To restore: Simply copy the backup file back to `orchestrator.db`

## Troubleshooting

### Migration Fails

1. Check the logs for specific error messages
2. Restore from the automatic backup
3. Ensure the database file is not locked by another process
4. Verify you have write permissions to the database directory

### Server Startup Issues

If you experience server startup issues after migration:

1. Check that the models file has the columns uncommented
2. Verify all required tables exist using:
   ```bash
   python scripts/migrations/migrate_automation_maintenance.py --verify-only
   ```
3. Review the server logs for specific SQLAlchemy errors

### Column Already Exists

The migration is idempotent - it checks for existing columns/tables before adding them. Running it multiple times is safe.

## Post-Migration Steps

1. **Restart the orchestrator server** to pick up the schema changes
2. **Run the maintenance coordinator** to start benefiting from the new features:
   ```python
   # Example: Scan for stale tasks
   orchestrator_maintenance_coordinator(
       action="scan_cleanup",
       scope="current_session"
   )
   ```

## Schema Details

### Subtasks Table Additions

- **prerequisite_satisfaction_required**: Whether prerequisites must be satisfied before task execution
- **auto_maintenance_enabled**: Whether automatic maintenance is enabled for this task
- **quality_gate_level**: The quality gate level (standard, enhanced, strict)

### New Tables

#### task_prerequisites
- Manages dependencies between tasks
- Tracks prerequisite satisfaction status

#### maintenance_operations  
- Records all maintenance activities
- Tracks cleanup operations and their results

#### project_health_metrics
- Monitors overall project health
- Tracks metrics like task completion rates, stale task counts

## Related Documentation

- [Automation Maintenance Enhancement Feature](../../docs/prompts/features/approved/[APPROVED]_automation_maintenance_enhancement.md)
- [Database Schema Enhancements](../../architecture/database-schema-enhancements.md)
- [Task Lifecycle Management](../../docs/prompts/maintenance_coordinator_implementation.md)