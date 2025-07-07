

# Error Codes - Quick Reference

*1500 char limit - Error handling and recovery*

#

# Orchestrator Errors

#

## Invalid Task State

- **Error**: "Task not found" / "Invalid task ID"

- **Cause**: Using wrong task_id or deleted task

- **Fix**: Use `orchestrator_get_status()` to check active tasks

#

## Planning Errors  

- **Error**: "Invalid subtasks_json format"

- **Cause**: Malformed JSON in plan_task()

- **Fix**: Ensure subtasks array has required fields: title, description, specialist_type

#

## Dependency Errors

- **Error**: "Circular dependency detected"  

- **Cause**: Subtask A depends on B, B depends on A

- **Fix**: Review dependency chain, remove circular references

#

## Session Errors

- **Error**: "No active session"

- **Cause**: Using orchestrator without initialize_session()

- **Fix**: Always call `orchestrator_initialize_session()` first

#

# Integration Errors

#

## Tool Conflicts

- **Error**: File operation fails during orchestration

- **Cause**: File locks, permissions, concurrent access

- **Fix**: Complete current subtask before starting new operations

#

## Context Loss

- **Error**: Specialist context missing

- **Cause**: Skipping execute_subtask() step

- **Fix**: Always get specialist context before working

#

## State Mismatch

- **Error**: Task marked complete but not finished

- **Cause**: Premature completion marking

- **Fix**: Use "in_progress" status until fully complete

#

# Recovery Patterns

#

## Graceful Retry

1. Check status with `orchestrator_get_status()`

2. Identify failed subtask

3. Re-execute with `orchestrator_execute_subtask()`

4. Complete properly with `orchestrator_complete_subtask()`

#

## Workflow Reset

1. Start new session with `orchestrator_initialize_session()`

2. Re-plan with lessons learned

3. Resume from stable checkpoint

#

## Best Practices

- Always check status before major operations

- Use specific error messages in complete_subtask()

- Mark subtasks as "blocked" if unable to proceed
