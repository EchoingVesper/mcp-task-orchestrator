# Tool Catalog - Quick Reference

*1500 char limit - Essential orchestrator tools*

## Core Functions

### `orchestrator_initialize_session()`
- **Purpose**: Initialize orchestration context
- **Parameters**: None
- **Returns**: Session context, specialist roles, guidance
- **Usage**: Always call first to establish orchestrator mode

### `orchestrator_plan_task(description, subtasks_json, complexity_level?, context?)`
- **Purpose**: Create structured task breakdown
- **Required**: description, subtasks_json (array of subtask objects)
- **Optional**: complexity_level (simple/moderate/complex), context
- **Returns**: parent_task_id, subtasks with task_ids
- **Usage**: Provide JSON array of {title, description, specialist_type, dependencies?, estimated_effort?}

### `orchestrator_execute_subtask(task_id)`
- **Purpose**: Get specialist context for subtask execution
- **Parameters**: task_id (from plan_task)
- **Returns**: Specialist role context, expertise, approach guidance
- **Usage**: Execute before working on each subtask

### `orchestrator_complete_subtask(task_id, results, next_action, artifacts?)`
- **Purpose**: Mark subtask complete, record results
- **Required**: task_id, results (summary), next_action (continue/needs_revision/blocked/complete)
- **Optional**: artifacts (array of created files/outputs)
- **Returns**: Status, progress info, next recommended task

### `orchestrator_synthesize_results(parent_task_id)`
- **Purpose**: Combine all subtask results into final output
- **Parameters**: parent_task_id (from plan_task)
- **Returns**: Complete synthesis, artifacts list, completion status
- **Usage**: Call after all subtasks completed

### `orchestrator_get_status(include_completed?)`
- **Purpose**: Check progress of active tasks
- **Optional**: include_completed (boolean)
- **Returns**: All active tasks, progress percentages, next steps

## Specialist Types
architect, implementer, debugger, documenter, reviewer, tester, researcher