# Maintenance Coordinator User Guide

*Automated task cleanup, validation, and handover preparation for optimal workflow management*

## Overview

The Maintenance Coordinator is an automated system that helps keep your MCP Task Orchestrator environment clean, organized, and performing optimally. It provides intelligent task cleanup, structure validation, documentation synchronization, and handover preparation capabilities.

## Key Benefits

- **Automated Cleanup**: Automatically identifies and archives stale or orphaned tasks
- **Performance Optimization**: Prevents database bloat and improves system responsiveness
- **Structure Validation**: Ensures task hierarchies and dependencies remain consistent
- **Handover Preparation**: Streamlines context transitions and project handoffs
- **Audit Trail**: Maintains complete records of all maintenance operations

## Quick Start

### Basic Usage
```
"Use the maintenance coordinator to scan and cleanup the current session"
```

### Advanced Usage
```
"Run a comprehensive scan and cleanup of the full project with detailed validation"
```

## Available Actions

### 1. Scan and Cleanup (`scan_cleanup`)
Identifies and automatically resolves common task management issues.

**What it does:**
- Scans for stale tasks (pending/active for >24 hours)
- Identifies orphaned tasks (missing parent references)
- Detects incomplete workflows
- Performs automatic cleanup based on validation level
- Generates recommendations for manual review

**When to use:**
- Regular maintenance (weekly/bi-weekly)
- Before project handoffs
- When system performance seems slow
- After long development sessions

**Example:**
```json
{
  "action": "scan_cleanup",
  "scope": "current_session",
  "validation_level": "comprehensive"
}
```

### 2. Structure Validation (`validate_structure`)
Validates task hierarchies, dependencies, and data consistency.

**What it does:**
- Checks parent-child task relationships
- Validates dependency chains
- Identifies circular dependencies
- Verifies data integrity
- Reports inconsistencies

**When to use:**
- Before critical milestones
- After complex task restructuring
- When unexpected errors occur
- For quality assurance audits

**Example:**
```json
{
  "action": "validate_structure", 
  "scope": "full_project",
  "validation_level": "full_audit"
}
```

### 3. Documentation Update (`update_documentation`)
Synchronizes task state with documentation and updates project status.

**What it does:**
- Updates handover documentation
- Synchronizes task status with documentation
- Refreshes project status reports
- Maintains documentation consistency

**When to use:**
- Before project handoffs
- At milestone completions
- For status reporting
- During documentation reviews

**Example:**
```json
{
  "action": "update_documentation",
  "scope": "current_session",
  "validation_level": "basic"
}
```

### 4. Handover Preparation (`prepare_handover`)
Prepares comprehensive handover documentation and cleans up temporary data.

**What it does:**
- Generates handover summaries
- Cleans up temporary files
- Consolidates task status
- Prepares transition documentation

**When to use:**
- End of development sessions
- Project transfers
- Context limit approaching
- Before long breaks

**Example:**
```json
{
  "action": "prepare_handover",
  "scope": "current_session", 
  "validation_level": "comprehensive"
}
```

## Scope Options

### Current Session (`current_session`)
- **Focus**: Active tasks in the current conversation
- **Performance**: Fast execution
- **Use case**: Regular maintenance, session cleanup
- **Recommended**: For routine operations

### Full Project (`full_project`)
- **Focus**: All tasks across the entire project
- **Performance**: Longer execution time
- **Use case**: Comprehensive audits, major cleanups
- **Recommended**: For periodic deep maintenance

### Specific Subtask (`specific_subtask`)
- **Focus**: Single task and its immediate dependencies
- **Performance**: Very fast execution
- **Use case**: Targeted investigation, specific issue resolution
- **Recommended**: For troubleshooting specific problems
- **Requires**: `target_task_id` parameter

## Validation Levels

### Basic (`basic`)
- **Speed**: Fast
- **Coverage**: Essential validations only
- **Actions**: Safe, non-destructive operations
- **Use case**: Regular maintenance, quick checks

### Comprehensive (`comprehensive`)
- **Speed**: Moderate
- **Coverage**: Thorough analysis and cleanup
- **Actions**: Automated archival of stale tasks
- **Use case**: Weekly maintenance, performance optimization

### Full Audit (`full_audit`)
- **Speed**: Slower
- **Coverage**: Complete system validation
- **Actions**: All available maintenance operations
- **Use case**: Quality assurance, before major releases

## Best Practices

### Regular Maintenance Schedule
```
Daily: Basic current_session scan_cleanup
Weekly: Comprehensive current_session scan_cleanup
Monthly: Full_project comprehensive scan_cleanup
Quarterly: Full_project full_audit validation
```

### Before Handoffs
1. Run `prepare_handover` with comprehensive validation
2. Review generated recommendations
3. Address any critical issues
4. Run `update_documentation` to ensure consistency

### Performance Optimization
- Use `scan_cleanup` when system feels slow
- Monitor stale task counts in reports
- Archive completed workflows periodically
- Keep active task count under 100 for optimal performance

### Troubleshooting Integration
- Start with `validate_structure` for unexplained errors
- Use `specific_subtask` scope for targeted investigation
- Escalate to `full_audit` for persistent issues

## Understanding Output

### Scan Results
```json
{
  "total_tasks_scanned": 45,
  "stale_tasks_found": 3,
  "orphaned_tasks": 1,
  "incomplete_workflows": 2,
  "performance_issues": []
}
```

### Cleanup Actions
```json
{
  "cleanup_actions": [
    {
      "action_type": "archive_stale_task",
      "task_id": "implementer_abc123",
      "reason": "Task stale for 36.2 hours",
      "result": "archived_successfully"
    }
  ]
}
```

### Recommendations
```json
{
  "recommendations": [
    {
      "type": "manual_review",
      "priority": "high",
      "title": "Review incomplete workflow",
      "description": "Workflow 'Database migration' is only 25.0% complete",
      "action": "Review and decide whether to complete or archive this workflow"
    }
  ]
}
```

## Maintenance Operation Tracking

Every maintenance operation is recorded with:
- **Operation ID**: Unique identifier for tracking
- **Timestamp**: When the operation was performed
- **Parameters**: Scope, validation level, and target
- **Results**: Detailed results and actions taken
- **Status**: Success, failure, or partial completion

### Viewing Operation History
Use `orchestrator_get_status` with `include_completed: true` to see recent maintenance operations.

## Troubleshooting

### Common Issues

#### "No maintenance actions needed"
- **Cause**: System is already clean and well-maintained
- **Action**: Normal result, no action needed
- **Prevention**: Indicates good maintenance hygiene

#### "Operation timed out"
- **Cause**: Large dataset or system resource constraints
- **Solution**: Try smaller scope or basic validation level
- **Example**: Use `current_session` instead of `full_project`

#### "Target task not found"
- **Cause**: Invalid `target_task_id` for specific_subtask scope
- **Solution**: Verify task ID with `orchestrator_get_status`
- **Prevention**: Double-check task IDs before targeting

#### "Database connection errors"
- **Cause**: Database connectivity or permission issues
- **Solution**: Check database status and restart if needed
- **Escalation**: Contact system administrator

### Performance Optimization

#### Slow Maintenance Operations
1. Start with `basic` validation level
2. Use `current_session` scope first
3. Upgrade to `comprehensive` only if needed
4. Reserve `full_audit` for scheduled maintenance

#### High Memory Usage
- Maintenance operations are designed to be memory-efficient
- Use batch processing (max 50 items per operation)
- Large projects may require multiple maintenance cycles

### Recovery Procedures

#### Interrupted Maintenance
- Operations are atomic - either complete or rollback
- Rerun the same operation to complete
- Check operation status in logs

#### Accidental Archival
- Archived tasks are preserved for 30 days
- Contact administrator for recovery if needed
- Review `recommendations` before comprehensive cleanup

## Integration Patterns

### With Development Workflows
```
1. Start development session
2. Work on tasks
3. Run basic cleanup before major milestones
4. Run comprehensive cleanup before handoffs
5. Use prepare_handover for session transitions
```

### With CI/CD Pipelines
- Integrate maintenance checks into release processes
- Validate structure before deployments
- Archive completed tasks after releases

### With Team Collaboration
- Run handover preparation before context switches
- Use documentation updates for status synchronization
- Coordinate maintenance schedules across team members

## Advanced Usage

### Batch Operations
For large projects, consider breaking maintenance into smaller operations:
```
1. validate_structure (full_project, basic) - Quick consistency check
2. scan_cleanup (current_session, comprehensive) - Clean active work
3. scan_cleanup (full_project, basic) - Broader cleanup
4. update_documentation (full_project, comprehensive) - Final sync
```

### Custom Maintenance Workflows
Combine maintenance actions for specific scenarios:

**Pre-Release Checklist:**
1. `validate_structure` with `full_audit`
2. `scan_cleanup` with `comprehensive` validation
3. `update_documentation` for status sync
4. `prepare_handover` for release notes

**Daily Maintenance:**
1. `scan_cleanup` with `basic` validation on `current_session`
2. Review recommendations
3. Address high-priority issues

## Security and Safety

### Safe Operations
- All maintenance operations preserve data before cleanup
- Archived tasks are retained for 30 days minimum
- Operations are logged for audit trails

### Data Protection
- Original task data is preserved in archives
- Artifact references are maintained
- Recovery procedures available for 30 days

### Access Control
- Maintenance operations respect existing permissions
- No data modification without proper validation
- All operations are reversible within retention period

---

*For additional help or advanced use cases, see the [Troubleshooting Guide](../troubleshooting/) or contact the development team.*