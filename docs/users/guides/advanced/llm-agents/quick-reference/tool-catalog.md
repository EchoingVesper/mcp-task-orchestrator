

# Tool Catalog - Quick Reference

*1800 char limit - Essential orchestrator tools with automation*

#

# Core Workflow Functions

#

## `orchestrator_initialize_session()` *(→ orchestrator_start_workflow)*

- **Purpose**: Initialize orchestration context and begin workflow

- **Parameters**: None

- **Returns**: Session context, specialist roles, guidance, interrupted task recovery

- **Usage**: Always call first to establish orchestrator mode

#

## `orchestrator_plan_task(description, subtasks_json, complexity_level?, context?)`

- **Purpose**: Create structured task breakdown

- **Required**: description, subtasks_json (array of subtask objects)

- **Optional**: complexity_level (simple/moderate/complex), context

- **Returns**: parent_task_id, subtasks with task_ids

- **Usage**: Provide JSON array of {title, description, specialist_type, dependencies?, estimated_effort?}

#

## `orchestrator_execute_subtask(task_id)`

- **Purpose**: Get specialist context for subtask execution

- **Parameters**: task_id (from plan_task)

- **Returns**: Specialist role context, expertise, approach guidance

- **Usage**: Execute before working on each subtask

#

## `orchestrator_complete_subtask(task_id, summary, detailed_work, next_action, file_paths?, artifact_type?)`

- **Purpose**: Mark subtask complete with artifact storage

- **Required**: task_id, summary, detailed_work, next_action

- **Optional**: file_paths (array), artifact_type (code/documentation/analysis/etc)

- **Returns**: Status, progress info, artifact info, prevents context limits

#

## `orchestrator_synthesize_results(parent_task_id)`

- **Purpose**: Combine all subtask results into final output

- **Parameters**: parent_task_id (from plan_task)

- **Returns**: Complete synthesis, artifacts list, completion status

- **Usage**: Call after all subtasks completed

#

## `orchestrator_get_status(include_completed?)`  *(→ orchestrator_check_status)*

- **Purpose**: Check progress of active tasks and system health

- **Optional**: include_completed (boolean)

- **Returns**: Active tasks, progress percentages, next steps, system status

#

# Automation & Maintenance

#

## `orchestrator_maintenance_coordinator(action, scope?, validation_level?)`  *(→ orchestrator_maintain_system)*

- **Purpose**: Automated system maintenance and optimization

- **Required**: action (scan_cleanup/validate_structure/update_documentation/prepare_handover)

- **Optional**: scope (current_session/full_project/specific_subtask), validation_level (basic/comprehensive/full_audit)

- **Returns**: Maintenance results, cleanup actions, recommendations

- **Usage**: Regular maintenance, performance optimization, handover preparation

#

# Quick Maintenance Commands

- `{"action": "scan_cleanup", "scope": "current_session"}` - Basic cleanup

- `{"action": "prepare_handover", "validation_level": "comprehensive"}` - Session handoff

- `{"action": "validate_structure", "scope": "full_project"}` - System health check

#

# Specialist Types

architect, implementer, debugger, documenter, reviewer, tester, researcher
