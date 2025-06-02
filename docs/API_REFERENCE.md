# MCP Task Orchestrator API Reference

*Complete reference for all orchestrator tools and parameters*

## Overview

The MCP Task Orchestrator provides 7 core tools for intelligent task breakdown, execution, and maintenance. All tools follow the Model Context Protocol (MCP) specification and are designed for seamless integration with Claude, Cursor, Windsurf, and VS Code.

## Tool Categories

### Workflow Management
- [`orchestrator_initialize_session`](#orchestrator_initialize_session) - Start orchestration workflow
- [`orchestrator_plan_task`](#orchestrator_plan_task) - Create structured task breakdown
- [`orchestrator_execute_subtask`](#orchestrator_execute_subtask) - Get specialist context
- [`orchestrator_complete_subtask`](#orchestrator_complete_subtask) - Complete tasks with artifacts
- [`orchestrator_synthesize_results`](#orchestrator_synthesize_results) - Combine results

### Status & Maintenance  
- [`orchestrator_get_status`](#orchestrator_get_status) - Check workflow progress
- [`orchestrator_maintenance_coordinator`](#orchestrator_maintenance_coordinator) - Automated maintenance

## Tool Specifications

### orchestrator_initialize_session

**Purpose**: Initialize a new task orchestration session with specialist context.

**Status**: ⚠️ *Planned migration to `orchestrator_start_workflow`*

```json
{
  "tool": "orchestrator_initialize_session",
  "arguments": {}
}
```

**Parameters**: None

**Returns**:
```json
{
  "session_initialized": true,
  "orchestrator_context": {
    "role": "Task Orchestrator", 
    "capabilities": ["Breaking down complex tasks", "Managing dependencies", "..."],
    "specialist_roles": {
      "architect": "System design and architecture planning",
      "implementer": "Writing code and implementing features",
      "debugger": "Fixing issues and optimizing performance",
      "documenter": "Creating documentation and guides",
      "reviewer": "Code review and quality assurance",
      "tester": "Testing and validation",
      "researcher": "Research and information gathering"
    }
  },
  "instructions": "I'll help you break down complex tasks...",
  "active_tasks": [...],  // If resuming interrupted workflows
  "recovery_info": {...}  // If tasks found from previous sessions
}
```

**Use Cases**:
- Starting any new orchestration workflow
- Resuming interrupted sessions
- Getting available specialist roles
- Setting up orchestration context

**Example**:
```
"Initialize a new orchestration session to begin project planning"
```

---

### orchestrator_plan_task

**Purpose**: Create a structured breakdown of complex tasks into manageable subtasks.

```json
{
  "tool": "orchestrator_plan_task",
  "arguments": {
    "description": "Build a Python web scraper with testing and documentation",
    "subtasks_json": "[{\"title\": \"Design scraper architecture\", \"description\": \"Plan scalable scraping system\", \"specialist_type\": \"architect\", \"dependencies\": [], \"estimated_effort\": \"medium\"}, ...]",
    "complexity_level": "moderate",
    "context": "E-commerce product data extraction project"
  }
}
```

**Parameters**:
- `description` (required): High-level description of the complex task
- `subtasks_json` (required): JSON string containing array of subtask objects
- `complexity_level` (optional): "simple" | "moderate" | "complex" | "very_complex" 
- `context` (optional): Additional context about the project or requirements

**Subtask Object Schema**:
```json
{
  "title": "string (required)",
  "description": "string (required)", 
  "specialist_type": "string (required) - architect|implementer|debugger|documenter|reviewer|tester|researcher",
  "dependencies": "array (optional) - list of dependent subtask titles",
  "estimated_effort": "string (optional) - low|medium|high"
}
```

**Returns**:
```json
{
  "task_created": true,
  "parent_task_id": "task_abc123",
  "description": "Build a Python web scraper...",
  "complexity": "moderate",
  "subtasks": [
    {
      "task_id": "architect_def456",
      "title": "Design scraper architecture", 
      "specialist_type": "architect",
      "dependencies": []
    }
  ],
  "next_steps": "Use orchestrator_execute_subtask to start working on individual subtasks"
}
```

**Best Practices**:
- Break tasks into 3-8 subtasks for optimal management
- Ensure each subtask is independently executable
- Use appropriate specialist types for each subtask
- Include dependencies only when necessary
- Provide clear, actionable descriptions

---

### orchestrator_execute_subtask

**Purpose**: Retrieve specialist context and guidance for executing a specific subtask.

```json
{
  "tool": "orchestrator_execute_subtask", 
  "arguments": {
    "task_id": "architect_def456"
  }
}
```

**Parameters**:
- `task_id` (required): Task ID from orchestrator_plan_task response

**Returns**:
```json
{
  "specialist_context": {
    "role": "Senior Software Architect",
    "expertise": ["System design", "Architecture patterns", "..."],
    "approach": "Think systematically about requirements...",
    "task_details": {
      "task_id": "architect_def456",
      "title": "Design scraper architecture",
      "description": "Plan scalable scraping system",
      "specialist_type": "architect"
    }
  },
  "instructions": "Please complete this task as the architect specialist..."
}
```

**Workflow**:
1. Call this before starting work on any subtask
2. Follow the specialist guidance provided
3. Apply the specialist's expertise and approach
4. Complete the work using the specialist context

---

### orchestrator_complete_subtask

**Purpose**: Mark a subtask as complete and store detailed work with artifact management.

```json
{
  "tool": "orchestrator_complete_subtask",
  "arguments": {
    "task_id": "architect_def456",
    "summary": "Completed scalable web scraper architecture design",
    "detailed_work": "# Scraper Architecture Design\n\n## Overview\n...",
    "file_paths": ["/project/architecture.md", "/project/diagrams/system.png"],
    "artifact_type": "design",
    "next_action": "continue"
  }
}
```

**Parameters**:
- `task_id` (required): Task ID from execute_subtask
- `summary` (required): Brief summary of work completed
- `detailed_work` (required): Full detailed content of the work performed
- `file_paths` (optional): Array of file paths created or modified
- `artifact_type` (optional): "code" | "documentation" | "analysis" | "design" | "test" | "config" | "general"
- `next_action` (required): "continue" | "needs_revision" | "blocked" | "complete"

**Returns**:
```json
{
  "task_id": "architect_def456",
  "status": "completed",
  "results_recorded": true,
  "parent_task_progress": {
    "progress": "in_progress", 
    "parent_task_id": "task_abc123",
    "completed_subtasks": 1,
    "total_subtasks": 4,
    "progress_percentage": 25.0
  },
  "artifact_created": true,
  "artifact_info": {
    "artifact_id": "artifact_xyz789",
    "summary": "Completed scalable web scraper architecture design",
    "artifact_type": "design",
    "accessible_via": ".task_orchestrator/artifacts/architect_def456/artifact_xyz789.md"
  },
  "context_saving": {
    "detailed_work_length": 2847,
    "stored_in_filesystem": true,
    "prevents_context_limit": true
  }
}
```

**Key Features**:
- **Artifact Storage**: Automatically stores detailed work to prevent context limits
- **Progress Tracking**: Updates parent task completion percentage
- **File Management**: Tracks created/modified files
- **Context Preservation**: Maintains work history across sessions

---

### orchestrator_synthesize_results

**Purpose**: Combine all completed subtask results into a comprehensive final output.

```json
{
  "tool": "orchestrator_synthesize_results",
  "arguments": {
    "parent_task_id": "task_abc123"
  }
}
```

**Parameters**:
- `parent_task_id` (required): Parent task ID from orchestrator_plan_task

**Returns**:
```json
{
  "synthesis_complete": true,
  "parent_task_id": "task_abc123", 
  "task_description": "Build a Python web scraper...",
  "completed_subtasks": 4,
  "synthesis": {
    "overview": "Complete web scraper solution with...",
    "key_deliverables": ["Scraper architecture", "Implementation code", "..."],
    "artifacts_created": [...],
    "next_steps": [...]
  },
  "artifacts": {
    "total_artifacts": 4,
    "artifact_summary": [...],
    "access_instructions": "Artifacts are stored in .task_orchestrator/artifacts/"
  }
}
```

**Best Practices**:
- Only call after all subtasks are completed
- Review synthesis output for completeness
- Use artifacts for detailed implementation access
- Save synthesis results for project documentation

---

### orchestrator_get_status

**Purpose**: Check the current progress of workflows and system health.

**Status**: ⚠️ *Planned migration to `orchestrator_check_status`*

```json
{
  "tool": "orchestrator_get_status",
  "arguments": {
    "include_completed": false
  }
}
```

**Parameters**:
- `include_completed` (optional): Boolean, whether to include completed tasks in output

**Returns**:
```json
{
  "active_tasks": [
    {
      "parent_task_id": "task_abc123",
      "description": "Build a Python web scraper...",
      "subtasks": [
        {
          "task_id": "architect_def456",
          "title": "Design scraper architecture",
          "status": "completed"
        }
      ],
      "progress": {
        "completed": 1,
        "total": 4, 
        "percentage": 25.0
      }
    }
  ],
  "system_status": {
    "total_active_tasks": 3,
    "health": "good",
    "recommendations": []
  }
}
```

**Use Cases**:
- Checking workflow progress
- Understanding next steps
- Monitoring system health
- Planning session handoffs

---

### orchestrator_maintenance_coordinator

**Purpose**: Automated system maintenance, cleanup, and optimization.

**Status**: ⚠️ *Planned migration to `orchestrator_maintain_system`*

```json
{
  "tool": "orchestrator_maintenance_coordinator",
  "arguments": {
    "action": "scan_cleanup",
    "scope": "current_session", 
    "validation_level": "comprehensive"
  }
}
```

**Parameters**:
- `action` (required): "scan_cleanup" | "validate_structure" | "update_documentation" | "prepare_handover"
- `scope` (optional): "current_session" | "full_project" | "specific_subtask" (default: "current_session")
- `validation_level` (optional): "basic" | "comprehensive" | "full_audit" (default: "basic")
- `target_task_id` (optional): Required when scope is "specific_subtask"

**Action Types**:

#### scan_cleanup
Identifies and cleans up stale or problematic tasks.

```json
{
  "operation_id": "maint_001",
  "scope": "current_session",
  "scan_results": {
    "total_tasks_scanned": 15,
    "stale_tasks_found": 2,
    "orphaned_tasks": 0,
    "incomplete_workflows": 1
  },
  "cleanup_actions": [
    {
      "action_type": "archive_stale_task",
      "task_id": "old_task_123",
      "reason": "Task stale for 36.2 hours",
      "result": "archived_successfully"
    }
  ],
  "recommendations": [
    {
      "type": "manual_review",
      "priority": "medium",
      "title": "Review incomplete workflow",
      "description": "Workflow 'Database migration' is 40% complete"
    }
  ]
}
```

#### validate_structure  
Checks task hierarchies and data consistency.

#### update_documentation
Synchronizes task state with documentation.

#### prepare_handover
Prepares comprehensive handover documentation.

**Common Usage Patterns**:
```json
// Daily maintenance
{"action": "scan_cleanup", "scope": "current_session", "validation_level": "basic"}

// Performance optimization
{"action": "scan_cleanup", "scope": "full_project", "validation_level": "comprehensive"}

// Before handoffs
{"action": "prepare_handover", "validation_level": "comprehensive"}

// Health checks
{"action": "validate_structure", "scope": "full_project", "validation_level": "full_audit"}
```

## Error Handling

### Common Error Types

#### Tool Not Found
```json
{
  "error": "Unknown tool: invalid_tool_name",
  "available_tools": ["orchestrator_initialize_session", "..."]
}
```

#### Invalid Parameters
```json
{
  "error": "Missing required parameter: task_id",
  "required_parameters": ["task_id"],
  "provided_parameters": []
}
```

#### Task Not Found
```json
{
  "error": "Task not found: invalid_task_123",
  "suggestion": "Use orchestrator_get_status to see available tasks"
}
```

#### Timeout Errors
```json
{
  "error": "Operation timed out",
  "action": "scan_cleanup", 
  "suggestions": "Try again with smaller scope or basic validation level"
}
```

### Error Recovery

1. **Invalid Task IDs**: Use `orchestrator_get_status` to get valid task IDs
2. **Timeout Issues**: Reduce scope or validation level for maintenance operations
3. **Missing Parameters**: Check parameter requirements in this reference
4. **Database Issues**: Restart MCP client or delete `.task_orchestrator/database/` to reset

## Best Practices

### Workflow Management
1. **Always initialize** sessions before creating task plans
2. **Break tasks appropriately** - 3-8 subtasks per plan
3. **Use specific descriptions** for subtasks and summaries
4. **Match specialist types** to task requirements
5. **Complete tasks promptly** to maintain workflow momentum

### Artifact Management
1. **Use detailed_work parameter** for comprehensive content storage
2. **Specify artifact_type** for better organization
3. **Include file_paths** when creating or modifying files
4. **Access artifacts** via provided file paths for detailed content

### Maintenance & Performance
1. **Run regular maintenance** - daily basic cleanup recommended
2. **Monitor task counts** - keep active tasks under 100 for optimal performance
3. **Use handover preparation** before context transitions
4. **Archive completed workflows** to maintain system health

### Error Prevention
1. **Validate task IDs** before operations
2. **Check system status** regularly
3. **Use appropriate scopes** for maintenance operations
4. **Follow dependency order** in subtask execution

## Integration Examples

### Basic Workflow
```json
// 1. Initialize session
{"tool": "orchestrator_initialize_session"}

// 2. Create task plan
{"tool": "orchestrator_plan_task", "arguments": {"description": "...", "subtasks_json": "[...]"}}

// 3. Execute each subtask
{"tool": "orchestrator_execute_subtask", "arguments": {"task_id": "specialist_123"}}

// 4. Complete each subtask  
{"tool": "orchestrator_complete_subtask", "arguments": {"task_id": "specialist_123", "summary": "...", "detailed_work": "...", "next_action": "continue"}}

// 5. Synthesize results
{"tool": "orchestrator_synthesize_results", "arguments": {"parent_task_id": "task_abc"}}
```

### Maintenance Workflow
```json
// Regular cleanup
{"tool": "orchestrator_maintenance_coordinator", "arguments": {"action": "scan_cleanup", "scope": "current_session"}}

// Before handoff
{"tool": "orchestrator_maintenance_coordinator", "arguments": {"action": "prepare_handover", "validation_level": "comprehensive"}}

// Health check
{"tool": "orchestrator_maintenance_coordinator", "arguments": {"action": "validate_structure", "scope": "full_project"}}
```

## Tool Name Migration

Several tools are planned for name improvements to enhance usability:

| Current Name | Planned Name | Migration Timeline |
|-------------|-------------|-------------------|
| `orchestrator_initialize_session` | `orchestrator_start_workflow` | 6-month transition |
| `orchestrator_maintenance_coordinator` | `orchestrator_maintain_system` | 6-month transition |
| `orchestrator_get_status` | `orchestrator_check_status` | 6-month transition |

During the transition period, both names will work. See [Tool Naming Migration Guide](./TOOL_NAMING_MIGRATION.md) for details.

---

*For comprehensive guides and examples, see the [User Guide](./docs/user-guide/) and [LLM Agent Documentation](./docs/llm-agents/).*