# Session Management Tools (7 tools)

## Overview
Session management tools enable multiple concurrent sessions, session lifecycle management, and context switching. These tools transform the orchestrator from single-session to multi-session capable.

---

## `orchestrator_session_create`
**Purpose**: Create new session with comprehensive setup  
**Error Handling**: Validation, rollback on failure, cleanup  
**Performance**: <2s execution time, atomic operations  

### Parameters
```json
{
  "parameters": {
    "name": {
      "type": "string",
      "required": true,
      "max_length": 100,
      "validation": "^[a-zA-Z0-9_\\s-]+$",
      "description": "Human-readable session name"
    },
    "description": {
      "type": "string", 
      "required": false,
      "max_length": 500,
      "description": "Detailed session description"
    },
    "project_root": {
      "type": "string",
      "required": true,
      "validation": "absolute_path",
      "description": "Absolute path to project directory"
    },
    "mode_file": {
      "type": "string",
      "required": false,
      "default": "default_roles.yaml",
      "validation": "yaml_file_exists_or_template",
      "description": "Role configuration file"
    },
    "auto_activate": {
      "type": "boolean",
      "default": true,
      "description": "Automatically activate session after creation"
    },
    "initial_backup": {
      "type": "boolean", 
      "default": true,
      "description": "Create initial backup after setup"
    }
  }
}
```

### Response
```json
{
  "session_id": "string",
  "session_name": "string", 
  "status": "active|created",
  "directory_structure": "object",
  "mode_configuration": "object",
  "backup_created": "boolean",
  "warnings": "array"
}
```

### Error Conditions
- `DirectoryNotAccessible`: Project root path invalid or inaccessible
- `ModeFileInvalid`: Role configuration file malformed or missing
- `ActiveSessionExists`: Cannot auto-activate with existing active session
- `InsufficientPermissions`: Cannot create session directory structure

---

## `orchestrator_session_activate`
**Purpose**: Activate session as single active session  
**Validation**: Session exists, can be activated, proper state transitions  

### Parameters
```json
{
  "parameters": {
    "session_id": {
      "type": "string",
      "required": true,
      "validation": "session_exists",
      "description": "Session identifier to activate"
    },
    "force_deactivate_current": {
      "type": "boolean",
      "default": false,
      "description": "Force deactivate current active session"
    },
    "backup_current_state": {
      "type": "boolean",
      "default": true,
      "description": "Backup current session state before switching"
    }
  }
}
```

### Response
```json
{
  "activated_session": "object",
  "previous_session": "object|null",
  "backup_created": "boolean",
  "context_loaded": "boolean"
}
```

---

## `orchestrator_session_list`
**Purpose**: List all sessions with filtering and sorting  
**Performance**: Optimized queries, pagination support  

### Parameters
```json
{
  "parameters": {
    "status_filter": {
      "type": "array",
      "items": ["active", "paused", "completed", "archived", "cancelled"],
      "description": "Filter by session status"
    },
    "include_archived": {
      "type": "boolean",
      "default": false,
      "description": "Include archived sessions"
    },
    "sort_by": {
      "type": "string",
      "enum": ["created_at", "last_activity", "name", "progress"],
      "default": "last_activity",
      "description": "Sort criteria"
    },
    "sort_order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    },
    "limit": {
      "type": "integer",
      "default": 50,
      "max": 1000,
      "description": "Maximum sessions to return"
    }
  }
}
```

### Response
```json
{
  "sessions": [
    {
      "session_id": "string",
      "name": "string",
      "status": "string",
      "created_at": "ISO datetime",
      "last_activity": "ISO datetime",
      "task_count": "integer",
      "completion_percentage": "float",
      "project_root": "string"
    }
  ],
  "total_count": "integer",
  "active_session_id": "string|null"
}
```

---

## `orchestrator_session_pause`
**Purpose**: Pause active session safely  
**Safety**: Ensures clean state, creates checkpoint  

### Parameters
```json
{
  "parameters": {
    "session_id": {
      "type": "string",
      "required": false,
      "description": "Session to pause (defaults to active session)"
    },
    "create_checkpoint": {
      "type": "boolean",
      "default": true,
      "description": "Create checkpoint before pausing"
    },
    "reason": {
      "type": "string",
      "max_length": 200,
      "description": "Reason for pausing (for tracking)"
    }
  }
}
```

---

## `orchestrator_session_resume`
**Purpose**: Resume paused session with context restoration  

### Parameters
```json
{
  "parameters": {
    "session_id": {
      "type": "string",
      "required": true,
      "validation": "session_exists_and_paused"
    },
    "restore_from_checkpoint": {
      "type": "boolean",
      "default": true,
      "description": "Restore from last checkpoint"
    },
    "activate_after_resume": {
      "type": "boolean", 
      "default": true,
      "description": "Activate session after resuming"
    }
  }
}
```

---

## `orchestrator_session_complete`
**Purpose**: Mark session as completed with final validation  

### Parameters
```json
{
  "parameters": {
    "session_id": {
      "type": "string",
      "required": false,
      "description": "Session to complete (defaults to active)"
    },
    "final_summary": {
      "type": "string",
      "max_length": 1000,
      "description": "Final session summary and outcomes"
    },
    "create_final_backup": {
      "type": "boolean",
      "default": true,
      "description": "Create final backup before completion"
    },
    "validate_all_tasks": {
      "type": "boolean",
      "default": true,
      "description": "Validate all tasks are properly resolved"
    }
  }
}
```

---

## `orchestrator_session_archive`
**Purpose**: Archive session with compression and export options  

### Parameters
```json
{
  "parameters": {
    "session_id": {
      "type": "string", 
      "required": true,
      "validation": "session_exists_and_completed"
    },
    "compression_level": {
      "type": "integer",
      "min": 1,
      "max": 9,
      "default": 6,
      "description": "Compression level for archive"
    },
    "include_artifacts": {
      "type": "boolean",
      "default": true,
      "description": "Include artifacts in archive"
    },
    "export_format": {
      "type": "string",
      "enum": ["zip", "tar.gz", "json"],
      "default": "zip",
      "description": "Archive format"
    },
    "export_path": {
      "type": "string",
      "required": false,
      "validation": "writable_directory",
      "description": "Custom export location"
    }
  }
}
```

---

## Session State Transitions

```
Created ──activate──→ Active ──pause──→ Paused
   │                     │                │
   │                     │                │
   └─────activate────────┘                │
                         │                │
                         └──resume────────┘
                         │
                         └──complete──→ Completed ──archive──→ Archived
                         │
                         └──cancel────→ Cancelled
```

---

**Next**: [Task Organization Tools](./03-task-organization.md) - 6 tools for advanced task management