

# API Quick Reference

> **Navigation**: [Docs Home](../../../README.md) > [Examples](../../README.md) > [Generic Task Usage](../../../../../../../README.md) > [Reference](../../../../../../../README.md#reference) > API Reference

#

# GenericTask Model

#

#

# Constructor

```python
GenericTask(
    task_id: str,
    task_type: str,
    attributes: Dict[str, Any] = {},
    parent_task_id: Optional[str] = None,
    dependencies: List[TaskDependency] = [],
    status: TaskStatus = TaskStatus.DRAFT,
    lifecycle_stage: LifecycleStage = LifecycleStage.CREATED,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None
)

```text

#

#

# Key Properties

- `task_id`: Unique identifier for the task

- `task_type`: Type of task (epic, feature, specialist_task, etc.)

- `attributes`: Flexible key-value storage for task metadata

- `parent_task_id`: ID of parent task for hierarchical structure

- `dependencies`: List of TaskDependency objects

- `status`: Current task status (draft, active, completed, etc.)

#

#

# Common Task Types

- `epic`: Large organizational units

- `feature`: Individual product features

- `specialist_task`: Work for specific specialist roles

- `bug_fix`: Bug resolution tasks

- `deployment`: Deployment and release tasks

- `approval_gate`: Approval checkpoints

#

# TaskDependency Model

#

#

# Constructor

```text
python
TaskDependency(
    dependency_task_id: str,
    dependency_type: DependencyType,
    description: str = "",
    conditions: Optional[Dict[str, Any]] = None
)

```text

#

#

# Dependency Types

- `DependencyType.COMPLETION`: Task must be completed

- `DependencyType.APPROVAL`: Task must be approved

- `DependencyType.INFORMATION`: Need information/artifacts from task

#

# MCP Tools Reference

#

#

# Task Creation

#

#

#

# orchestrator_create_generic_task

Create a new generic task.

**Arguments:**

```text
json
{
  "task_type": "string (required)",
  "attributes": "object (optional)",
  "parent_task_id": "string (optional)",
  "dependencies": "array (optional)"
}

```text
text

**Example:**

```text
json
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "feature",
    "attributes": {
      "title": "User Authentication",
      "priority": "high",
      "estimated_effort": "2 weeks"
    }
  }
}

```text
text

#

#

#

# orchestrator_create_from_template

Create tasks from a predefined template.

**Arguments:**

```text
json
{
  "template_id": "string (required)",
  "parameters": "object (required)",
  "parent_task_id": "string (optional)"
}

```text
text

#

#

# Task Querying

#

#

#

# orchestrator_query_tasks

Query tasks with filters and sorting.

**Arguments:**

```text
json
{
  "filters": {
    "task_type": "array of strings (optional)",
    "status": "array of strings (optional)",
    "attributes": "object (optional)",
    "created_after": "ISO datetime (optional)",
    "created_before": "ISO datetime (optional)"
  },
  "sort": {
    "field": "string (optional)",
    "direction": "asc|desc (optional)"
  },
  "limit": "number (optional)",
  "offset": "number (optional)",
  "include_hierarchy": "boolean (optional)"
}

```text
text

#

#

#

# orchestrator_get_task_hierarchy

Get complete task tree.

**Arguments:**

```text
json
{
  "root_task_id": "string (required)",
  "max_depth": "number (optional)",
  "include_completed": "boolean (optional)",
  "include_statistics": "boolean (optional)"
}

```text
text

#

#

# Task Management

#

#

#

# orchestrator_update_task

Update task attributes and status.

**Arguments:**

```text
json
{
  "task_id": "string (required)",
  "updates": {
    "attributes": "object (optional)",
    "status": "string (optional)"
  },
  "update_reason": "string (optional)"
}

```text
text

#

#

#

# orchestrator_manage_dependencies

Add, remove, or modify task dependencies.

**Arguments:**

```text
json
{
  "task_id": "string (required)",
  "operation": "add|remove|update (required)",
  "dependencies": "array (for add/update)",
  "dependency_ids": "array (for remove)"
}

```text
text

#

#

# Bulk Operations

#

#

#

# orchestrator_bulk_update

Update multiple tasks at once.

**Arguments:**

```text
json
{
  "task_ids": "array of strings (optional)",
  "filters": "object (optional)",
  "updates": "object (required)",
  "dry_run": "boolean (optional)"
}

```text
text

#

#

#

# orchestrator_batch_create

Create multiple related tasks efficiently.

**Arguments:**

```text
json
{
  "tasks": "array of task objects (required)",
  "auto_link_dependencies": "boolean (optional)",
  "generate_specialist_tasks": "boolean (optional)"
}

```text
text

#

# Status Values

#

#

# Task Status

- `draft`: Initial creation state

- `active`: Currently being worked on

- `blocked`: Waiting for dependencies

- `completed`: Successfully finished

- `failed`: Failed or cancelled

- `approved`: Approved (for approval gates)

#

#

# Lifecycle Stages

- `created`: Task has been created

- `planned`: Task is planned but not started

- `active`: Task is actively being worked on

- `completed`: Task is finished

- `archived`: Task has been archived

#

# Common Attribute Patterns

#

#

# Standard Attributes

```text
json
{
  "title": "Human-readable task title",
  "description": "Detailed task description",
  "priority": "low|medium|high|critical",
  "estimated_effort": "Time estimate (e.g., '2 weeks')",
  "assigned_team": "Team responsible for the task",
  "assigned_developer": "Individual assigned",
  "labels": ["array", "of", "tags"],
  "business_value": "Description of business impact"
}

```text

#

#

# Specialist Task Attributes

```text
json
{
  "specialist_type": "architect|implementer|tester|reviewer|debugger",
  "estimated_effort": "Time estimate",
  "deliverables": ["list", "of", "expected", "outputs"],
  "tools_required": ["development", "tools", "needed"],
  "complexity": "simple|moderate|complex"
}

```text

#

#

# Feature Task Attributes

```text
json
{
  "acceptance_criteria": ["list", "of", "criteria"],
  "success_metrics": ["measurable", "outcomes"],
  "user_stories": ["as a user", "i want"],
  "epic_link": "parent_epic_id",
  "release_target": "2025-Q3"
}

```text

#

#

# Bug Fix Attributes

```text
json
{
  "severity": "low|medium|high|critical",
  "steps_to_reproduce": "How to reproduce the bug",
  "expected_behavior": "What should happen",
  "actual_behavior": "What actually happens",
  "affected_versions": ["1.2.0", "1.2.1"],
  "reporter": "person_who_reported",
  "environment": "production|staging|development"
}

```text

#

# Error Handling

#

#

# Common Error Types

- `ValidationError`: Invalid task data

- `TaskNotFoundError`: Task ID doesn't exist

- `CircularDependencyError`: Dependency would create cycle

- `ParentTaskNotFoundError`: Parent task doesn't exist

- `TemplateNotFoundError`: Template ID doesn't exist

#

#

# Error Response Format

```text
json
{
  "status": "error",
  "error_type": "ValidationError",
  "message": "Human-readable error message",
  "field": "specific_field_with_error",
  "suggestion": "How to fix the error"
}
```text

#

# Performance Guidelines

#

#

# Query Optimization

- Use specific filters to reduce result sets

- Implement pagination for large datasets

- Use `include_hierarchy: false` when hierarchy not needed

- Cache frequently accessed data

#

#

# Batch Operations

- Use `orchestrator_batch_create` for multiple related tasks

- Use `orchestrator_bulk_update` for mass updates

- Group related operations together

#

#

# Dependency Management

- Validate dependencies before adding

- Use appropriate dependency types

- Avoid excessive dependency chains

- Check for circular dependencies

#

# Best Practices

#

#

# Task Modeling

1. Use descriptive task types and titles

2. Store contextual information in attributes

3. Design clear dependency chains

4. Plan for template reuse

#

#

# API Usage

1. Validate inputs before API calls

2. Handle errors gracefully

3. Use appropriate batch operations

4. Implement retry logic for transient failures

#

#

# Performance

1. Use filters to reduce query scope

2. Implement caching for frequently accessed data

3. Monitor query performance

4. Archive old completed tasks

---

**Related Documentation**:

- **Back to**: [Generic Task Usage Guide](../../../../../../../README.md)

- **See also**: [Troubleshooting](../troubleshooting.md)

- **Next**: [Migration Guide](../migration-guide.md)
