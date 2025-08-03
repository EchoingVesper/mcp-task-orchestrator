# MCP Task Orchestrator API Reference

Complete reference for all 28 MCP tools available in the Task Orchestrator.

## Overview

The MCP Task Orchestrator provides 28 tools organized into 4 categories:

- **[Core Orchestration Tools](#core-orchestration-tools)** (10 tools) - Main task management
- **[Template System Tools](#template-system-tools)** (13 tools) - Template creation and management  
- **[Server Management Tools](#server-management-tools)** (5 tools) - Server lifecycle and health
- **[Advanced Tools](#advanced-tools)** - Specialized functionality

## Core Orchestration Tools

### Session Management

#### `orchestrator_initialize_session`
Initialize a new task orchestration session with guidance for effective task breakdown.

**Parameters:**
- `working_directory` (optional): Path where .task_orchestrator should be created

**Returns:**
- Session ID and metadata
- Working directory detection results
- Database initialization status

**Example:**
```python
# Initialize in current directory
orchestrator_initialize_session()

# Initialize in specific directory
orchestrator_initialize_session(working_directory="/path/to/project")
```

#### `orchestrator_get_status`
Get current status of all active tasks and their progress.

**Parameters:**
- `include_completed` (default: false): Whether to include completed tasks

**Returns:**
- Active task list with status
- Session information
- Progress statistics

**Example:**
```python
# Get active tasks only
orchestrator_get_status()

# Include completed tasks
orchestrator_get_status(include_completed=True)
```

### Task Management

#### `orchestrator_plan_task`
Create a new task with rich metadata and flexible structure.

**Parameters:**
- `title` (required): Task title
- `description` (required): Detailed task description
- `complexity` (default: "moderate"): Task complexity level (trivial, simple, moderate, complex, very_complex)
- `task_type` (default: "standard"): Type of task (standard, breakdown, milestone, review, approval, research, implementation, testing, documentation, deployment, custom)
- `specialist_type` (optional): Specialist type for assignment (analyst, coder, tester, documenter, reviewer, architect, devops, researcher, coordinator, generic)
- `parent_task_id` (optional): Parent task ID for hierarchy
- `dependencies` (optional): List of prerequisite task IDs
- `estimated_effort` (optional): Estimated effort (e.g., '2 hours', '1 day')
- `due_date` (optional): Due date in ISO format
- `context` (optional): Additional context data

**Returns:**
- Task ID
- Task metadata
- Assigned specialist information

**Example:**
```python
orchestrator_plan_task(
    title="Implement user authentication",
    description="Create secure JWT-based authentication system with password hashing",
    complexity="complex",
    task_type="implementation",
    specialist_type="architect",
    estimated_effort="2 days"
)
```

#### `orchestrator_execute_task`
Get specialist context and prompts for executing a specific task.

**Parameters:**
- `task_id` (required): ID of the task to execute

**Returns:**
- Specialist-specific context and prompts
- Task execution guidance
- Required tools and resources

**Example:**
```python
orchestrator_execute_task(task_id="task_12345")
```

#### `orchestrator_complete_task`
Mark a task as complete and store detailed work as artifacts to prevent context limit issues.

**Parameters:**
- `task_id` (required): ID of the completed task
- `summary` (required): Brief summary of what was accomplished
- `detailed_work` (required): Full detailed work content to store as artifacts
- `next_action` (required): What should happen next (continue, needs_revision, blocked, complete)
- `artifact_type` (default: "general"): Type of artifact (code, documentation, analysis, design, test, config, general)
- `file_paths` (optional): List of original file paths being referenced
- `legacy_artifacts` (optional): Legacy artifacts field for backward compatibility

**Returns:**
- Completion status
- Artifact storage confirmation
- Next action recommendations

**Example:**
```python
orchestrator_complete_task(
    task_id="task_12345",
    summary="Implemented JWT authentication with secure token handling",
    detailed_work="Complete implementation with security audit results...",
    next_action="continue",
    artifact_type="code",
    file_paths=["src/auth.py", "tests/test_auth.py"]
)
```

#### `orchestrator_update_task`
Update an existing task's properties.

**Parameters:**
- `task_id` (required): ID of task to update
- `title` (optional): New task title
- `description` (optional): New task description
- `status` (optional): New task status (pending, active, in_progress, blocked, completed, failed, cancelled, archived)
- `complexity` (optional): New complexity level
- `specialist_type` (optional): New specialist assignment
- `estimated_effort` (optional): New estimated effort
- `due_date` (optional): New due date in ISO format
- `context` (optional): Updated context data

**Returns:**
- Updated task information
- Change history

**Example:**
```python
orchestrator_update_task(
    task_id="task_12345",
    status="in_progress",
    estimated_effort="3 days"
)
```

#### `orchestrator_query_tasks`
Query and filter tasks with advanced search capabilities.

**Parameters:**
- `search_text` (optional): Search in title and description
- `status` (optional): Filter by task status array
- `task_type` (optional): Filter by task type array
- `specialist_type` (optional): Filter by specialist type array
- `complexity` (optional): Filter by complexity level array
- `parent_task_id` (optional): Filter by parent task
- `created_after` (optional): Filter tasks created after this date (ISO format)
- `created_before` (optional): Filter tasks created before this date (ISO format)
- `limit` (default: 100): Maximum number of results
- `offset` (default: 0): Number of results to skip
- `include_children` (default: false): Include child tasks in results
- `include_artifacts` (default: false): Include task artifacts in results

**Returns:**
- Filtered task list
- Total count
- Search metadata

**Example:**
```python
# Find all security-related tasks
orchestrator_query_tasks(
    search_text="security",
    status=["completed"],
    include_artifacts=True
)

# Find recent architecture tasks
orchestrator_query_tasks(
    specialist_type=["architect"],
    created_after="2024-01-01T00:00:00Z",
    limit=10
)
```

### Advanced Task Operations

#### `orchestrator_delete_task`
Safely delete a task and handle its dependencies.

**Parameters:**
- `task_id` (required): ID of task to delete
- `force` (default: false): Force deletion even if task has dependents
- `archive_instead` (default: true): Archive task instead of permanent deletion

**Returns:**
- Deletion status
- Affected dependencies

#### `orchestrator_cancel_task`
Cancel an in-progress task gracefully.

**Parameters:**
- `task_id` (required): ID of task to cancel
- `reason` (optional): Reason for cancellation
- `preserve_work` (default: true): Whether to preserve work artifacts

**Returns:**
- Cancellation status
- Preserved artifact information

#### `orchestrator_synthesize_results`
Combine completed subtasks into a final comprehensive result.

**Parameters:**
- `parent_task_id` (required): ID of the parent task to synthesize

**Returns:**
- Synthesized result
- Combined artifact summary
- Completion metrics

## Template System Tools

The Template System provides powerful automation for creating and managing task templates.

### Template Management

#### `template_create`
Create a new JSON5 template in the template system.

**Parameters:**
- `template_id` (required): Unique template identifier (alphanumeric, underscore, hyphen only)
- `template_content` (required): JSON5 template content
- `category` (default: "user"): Template category (user, shared)
- `overwrite` (default: false): Whether to overwrite existing template

**Returns:**
- Creation status
- Template validation results

**Example:**
```python
template_create(
    template_id="api-development",
    template_content='''{
        name: "API Development Template",
        description: "Template for building REST APIs",
        tasks: [
            {title: "Design API", specialist: "architect"},
            {title: "Implement endpoints", specialist: "coder"},
            {title: "Write tests", specialist: "tester"}
        ]
    }''',
    category="shared"
)
```

#### `template_list`
List available templates with optional filtering.

**Parameters:**
- `category` (optional): Filter by template category (builtin, user, shared)
- `include_metadata` (default: false): Include full template metadata

**Returns:**
- Template list with metadata
- Category information

#### `template_load`
Load a template and show its content and structure.

**Parameters:**
- `template_id` (required): Template ID to load
- `category` (optional): Specific category to search (builtin, user, shared)

**Returns:**
- Template content
- Structure analysis
- Parameter requirements

#### `template_instantiate`
Create tasks from a template with parameter substitution.

**Parameters:**
- `template_id` (required): Template to instantiate
- `parameters` (required): Parameter values for template substitution
- `create_tasks` (default: false): Whether to create actual tasks in the orchestrator

**Returns:**
- Generated task structure
- Parameter substitution results
- Created task IDs (if create_tasks=true)

**Example:**
```python
template_instantiate(
    template_id="web-app-development",
    parameters={
        "app_name": "TaskManager",
        "database": "PostgreSQL",
        "frontend": "React"
    },
    create_tasks=True
)
```

### Template Validation and Management

#### `template_validate`
Validate template syntax, structure, and security.

**Parameters:**
- `template_content` (required): JSON5 template content to validate

**Returns:**
- Validation results
- Error details
- Security assessment

#### `template_delete`
Delete a template from storage.

**Parameters:**
- `template_id` (required): Template ID to delete
- `category` (optional): Category to search (user, shared)

**Returns:**
- Deletion status

#### `template_info`
Get detailed information about a template.

**Parameters:**
- `template_id` (required): Template ID to analyze
- `category` (optional): Specific category to search

**Returns:**
- Detailed template metadata
- Usage statistics
- Parameter analysis

### Template Libraries

#### `template_install_examples`
Install example templates to get started with the template system.

**Parameters:**
- `category` (default: "shared"): Category to install examples in (user, shared)
- `overwrite` (default: false): Whether to overwrite existing examples

**Returns:**
- Installation status
- Installed template list

#### `template_install_default_library`
Install the default template library.

**Parameters:**
- `category` (default: "all"): Category of templates to install (all, development, research, creative, business, self_development)
- `overwrite` (default: false): Whether to overwrite existing templates

**Returns:**
- Installation status
- Installed template details

#### `template_get_installation_status`
Get status of template installations and coverage.

**Returns:**
- Installation statistics
- Available template categories
- Coverage analysis

#### `template_validate_all`
Validate all installed templates for security and syntax.

**Parameters:**
- `category` (optional): Specific category to validate (builtin, user, shared)

**Returns:**
- Validation results for all templates
- Security assessment summary

#### `template_uninstall`
Uninstall a template.

**Parameters:**
- `template_id` (required): Template ID to uninstall
- `category` (default: "user"): Template category

**Returns:**
- Uninstallation status

## Server Management Tools

### Health and Status

#### `orchestrator_health_check`
Check server health and readiness for operations.

**Parameters:**
- `include_database_status` (default: true): Whether to include database status
- `include_connection_status` (default: true): Whether to include client connection status
- `include_reboot_readiness` (default: true): Whether to include restart readiness in health check

**Returns:**
- Overall health status
- Component-specific health information
- Performance metrics

#### `orchestrator_restart_server`
Trigger a graceful server restart with state preservation.

**Parameters:**
- `graceful` (default: true): Whether to perform graceful shutdown
- `preserve_state` (default: true): Whether to preserve server state across restart
- `reason` (default: "manual_request"): Reason for the restart (configuration_update, schema_migration, error_recovery, manual_request, emergency_shutdown)
- `timeout` (default: 30): Maximum time to wait for restart completion (seconds, 10-300)

**Returns:**
- Restart status
- State preservation results

#### `orchestrator_shutdown_prepare`
Check server readiness for graceful shutdown.

**Parameters:**
- `check_active_tasks` (default: true): Whether to check for active tasks
- `check_client_connections` (default: true): Whether to check client connections
- `check_database_state` (default: true): Whether to check database state

**Returns:**
- Shutdown readiness status
- Blocking conditions

### Connection Management

#### `orchestrator_reconnect_test`
Test client reconnection capability and connection status.

**Parameters:**
- `session_id` (optional): Specific session ID to test
- `include_reconnection_stats` (default: true): Whether to include reconnection statistics
- `include_buffer_status` (default: true): Whether to include request buffer status

**Returns:**
- Connection test results
- Reconnection capabilities

#### `orchestrator_restart_status`
Get current status of restart operation.

**Parameters:**
- `include_error_details` (default: true): Whether to include detailed error information
- `include_history` (default: false): Whether to include restart history

**Returns:**
- Restart operation status
- Error details (if any)
- Historical restart information

## Advanced Tools

### Maintenance

#### `orchestrator_maintenance_coordinator`
Automated maintenance task coordination for task cleanup, validation, and handover preparation.

**Parameters:**
- `action` (required): Type of maintenance action (scan_cleanup, validate_structure, update_documentation, prepare_handover)
- `scope` (default: "current_session"): Scope of operation (current_session, full_project, specific_subtask)
- `target_task_id` (optional): Specific task ID for maintenance (required when scope is 'specific_subtask')
- `validation_level` (default: "basic"): Level of validation (basic, comprehensive, full_audit)

**Returns:**
- Maintenance operation results
- Cleanup statistics
- Validation findings

**Example:**
```python
# Clean up completed tasks
orchestrator_maintenance_coordinator(
    action="scan_cleanup",
    scope="current_session"
)

# Comprehensive validation
orchestrator_maintenance_coordinator(
    action="validate_structure",
    validation_level="comprehensive"
)
```

## Usage Examples

### Basic Workflow

```python
# 1. Initialize session
orchestrator_initialize_session(working_directory="/my/project")

# 2. Plan a complex task
task_id = orchestrator_plan_task(
    title="Build user dashboard",
    description="Create interactive dashboard with real-time data",
    complexity="complex"
)

# 3. Execute the task
orchestrator_execute_task(task_id=task_id)

# 4. Complete with artifacts
orchestrator_complete_task(
    task_id=task_id,
    summary="Dashboard implemented with React and WebSocket integration",
    detailed_work="Full implementation details...",
    next_action="continue",
    artifact_type="code"
)

# 5. Check status
orchestrator_get_status(include_completed=True)
```

### Template-Based Development

```python
# 1. Install template library
template_install_default_library(category="development")

# 2. List available templates
templates = template_list(category="builtin")

# 3. Create tasks from template
template_instantiate(
    template_id="microservice-development",
    parameters={
        "service_name": "user-service",
        "database": "PostgreSQL",
        "auth": "JWT"
    },
    create_tasks=True
)
```

### Maintenance and Monitoring

```python
# Regular health check
health = orchestrator_health_check()

# Query task history
recent_tasks = orchestrator_query_tasks(
    created_after="2024-01-01T00:00:00Z",
    status=["completed"],
    include_artifacts=True
)

# Maintenance cleanup
orchestrator_maintenance_coordinator(
    action="scan_cleanup",
    validation_level="comprehensive"
)
```

## Error Handling

All tools return structured error information when operations fail:

```python
{
    "success": false,
    "error": "TaskNotFound",
    "message": "Task with ID 'invalid_task' not found",
    "details": {
        "task_id": "invalid_task",
        "available_tasks": ["task_123", "task_456"]
    }
}
```

Common error types:
- `TaskNotFound`: Specified task doesn't exist
- `InvalidParameters`: Required parameters missing or invalid
- `PermissionDenied`: Operation not allowed in current context
- `TemplateError`: Template syntax or validation error
- `DatabaseError`: Database operation failed
- `ServerError`: Internal server error

## Tool Categories Summary

| Category | Tool Count | Purpose |
|----------|------------|---------|
| Core Orchestration | 10 | Task management, execution, and lifecycle |
| Template System | 13 | Template creation, validation, and instantiation |
| Server Management | 5 | Health monitoring, restarts, and connections |

## Next Steps

- **[Quick Start Guide](../../quick-start/README.md)** - Get started with the orchestrator
- **[Core Concepts](../users/guides/core-concepts.md)** - Understand the fundamentals
- **[Template Guide](../users/guides/advanced/templates.md)** - Master the template system
- **[Troubleshooting](../users/troubleshooting/README.md)** - Resolve common issues