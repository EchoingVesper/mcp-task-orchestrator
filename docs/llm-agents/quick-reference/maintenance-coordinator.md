# Maintenance Coordinator Quick Reference

*1800-character optimized guide for LLM agents*

## Tool Name
`orchestrator_maintenance_coordinator`

## Actions
- `scan_cleanup` - Scan and clean stale/orphaned tasks  
- `validate_structure` - Check task consistency and dependencies
- `update_documentation` - Sync task state with documentation
- `prepare_handover` - Generate handover docs and cleanup

## Scopes
- `current_session` - Active session only (fast, recommended)
- `full_project` - Entire project (thorough, slower) 
- `specific_subtask` - Single task (requires target_task_id)

## Validation Levels
- `basic` - Safe, fast operations
- `comprehensive` - Includes automated cleanup
- `full_audit` - Complete system validation

## Common Usage Patterns

### Daily Maintenance
```json
{"action": "scan_cleanup", "scope": "current_session", "validation_level": "basic"}
```

### Session Handoff
```json
{"action": "prepare_handover", "scope": "current_session", "validation_level": "comprehensive"}
```

### Performance Issues
```json
{"action": "scan_cleanup", "scope": "full_project", "validation_level": "comprehensive"}
```

### Before Major Changes
```json
{"action": "validate_structure", "scope": "full_project", "validation_level": "full_audit"}
```

### Troubleshooting Specific Task
```json
{"action": "validate_structure", "scope": "specific_subtask", "target_task_id": "task_id_here"}
```

## What Gets Cleaned
- Tasks stale >24 hours (pending/active status)
- Orphaned tasks (missing parent references)
- Incomplete workflows with mixed completion states
- Temporary data and expired artifacts

## Safety Features
- 30-day archive retention for all cleaned tasks
- Atomic operations (complete or rollback)
- Audit trail for all maintenance actions
- Batch processing (max 50 items) prevents overload

## Key Benefits
- Prevents database bloat and improves performance
- Maintains data consistency and structure integrity
- Automates routine maintenance tasks
- Provides comprehensive handover documentation

## Troubleshooting
- **Timeout**: Use smaller scope or basic validation
- **No actions needed**: System already optimized
- **Task not found**: Verify target_task_id with get_status
- **Performance slow**: Run scan_cleanup with comprehensive level

## Best Practice Schedule
- Daily: basic current_session cleanup
- Weekly: comprehensive current_session cleanup  
- Monthly: comprehensive full_project cleanup
- Quarterly: full_audit validation

Use before handoffs, at milestones, or when system performance degrades.