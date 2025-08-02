

# Sequential Coordination Pattern

*1800 char limit - Step-by-step cross-server coordination*

#

# Pattern Overview

Orchestrator plans and coordinates while Claude Code executes operations in sequence. Prevents conflicts and ensures proper dependency management.

#

# Implementation Steps

#

#

# Phase 1: Initialization and Planning

```text

1. orchestrator_initialize_session() - Establishes context

2. orchestrator_plan_task(description, subtasks_json) 

- Creates structured breakdown, assigns specialists, maps dependencies

```text

#

#

# Phase 2: Sequential Execution

```text

For each subtask in dependency order:

3. orchestrator_execute_subtask(task_id) - Specialist mode & context

4. [Claude Code Operations] - File ops, code analysis, execution

5. orchestrator_complete_subtask() - Record results, update progress

```text

#

#

# Phase 3: Synthesis

```text

6. orchestrator_synthesize_results(parent_task_id)

- Combines outputs, creates final result, artifact list
```text

#

# Coordination Benefits

- **No Conflicts**: Sequential execution prevents resource conflicts

- **Clear Dependencies**: Enforces proper ordering

- **Progress Tracking**: Maintains workflow visibility

- **Error Isolation**: Issues contained to specific subtasks

- **Context Preservation**: Maintains project state

#

# Best Practices

- Complete each subtask before starting next

- Use Claude Code tools only during subtask execution

- Record all artifacts in completion calls

- Follow dependency order strictly

**Use When**: File operations, complex workflows, multi-step processes
