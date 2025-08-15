---
feature_id: "MODE_ROLE_MCP_TOOLS"
version: "2.0.0"
status: "Planned"
priority: "High"
category: "Infrastructure"
dependencies: ["MODE_ROLE_ENHANCEMENT_V2"]
size_lines: 385
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/2.2-planned/mode-role-system/README.md"
  - "docs/developers/planning/features/2.2-planned/mode-role-system/session-integration.md"
module_type: "specification"
modularized_from: "docs/developers/planning/features/2.2-planned/[PLANNED]_mode_role_system_enhancement.md"
---

# MCP Tools Specification

This document specifies the new MCP tools for mode/role system management.

#
# 1. `orchestrator_mode_select`

**Purpose**: Select and bind a mode configuration to the active session

#
## Parameters

```json
{
  "mode_file": {
    "type": "string",
    "description": "Path to .yaml role configuration file",
    "examples": [
      "default_roles.yaml",
      "project_roles.yaml", 
      "custom_development_mode.yaml",
      "/absolute/path/to/custom_roles.yaml"
    ],
    "validation": "Must exist in .task_orchestrator/roles/ directory"
  },
  "validate_first": {
    "type": "boolean", 
    "default": true,
    "description": "Validate mode configuration before binding"
  },
  "auto_copy_if_missing": {
    "type": "boolean",
    "default": true, 
    "description": "Copy from config directory if file doesn't exist"
  },
  "backup_current": {
    "type": "boolean",
    "default": true,
    "description": "Backup current session mode before switching"
  }
}

```text

#
## Example Usage

```text
json
{
  "mode_file": "development_roles.yaml",
  "validate_first": true,
  "auto_copy_if_missing": true,
  "backup_current": true
}

```text

#
## Response

```text
json
{
  "success": true,
  "mode_activated": "development_roles.yaml",
  "session_id": "session_abc123",
  "mode_details": {
    "specialist_roles": ["architect", "implementer", "tester", "documenter"],
    "custom_roles": ["security_auditor", "performance_optimizer"],
    "default_complexity": "moderate",
    "auto_task_routing": true
  },
  "previous_mode": "default_roles.yaml",
  "backup_location": ".task_orchestrator/backups/mode_backup_20250601_143022.yaml"
}

```text

#
# 2. `orchestrator_mode_list`

**Purpose**: List available modes and their status

#
## Parameters

```text
json
{
  "include_invalid": {
    "type": "boolean",
    "default": false,
    "description": "Include modes that failed validation"
  },
  "show_details": {
    "type": "boolean", 
    "default": false,
    "description": "Include detailed role information for each mode"
  },
  "scan_config_directory": {
    "type": "boolean",
    "default": true,
    "description": "Also scan project config directory for available templates"
  }
}

```text

#
## Response

```text
json
{
  "active_session": "session_abc123",
  "current_mode": "development_roles.yaml",
  "available_modes": [
    {
      "filename": "default_roles.yaml",
      "status": "valid",
      "specialist_count": 7,
      "last_modified": "2025-06-01T10:30:00Z",
      "is_current": false,
      "description": "Standard orchestrator roles"
    },
    {
      "filename": "development_roles.yaml", 
      "status": "valid",
      "specialist_count": 9,
      "last_modified": "2025-06-01T14:15:00Z",
      "is_current": true,
      "description": "Enhanced roles for software development projects"
    },
    {
      "filename": "research_roles.yaml",
      "status": "invalid", 
      "error": "Missing required 'researcher' role definition",
      "last_modified": "2025-05-28T09:00:00Z",
      "is_current": false
    }
  ],
  "config_templates": [
    {
      "filename": "analytics_roles.yaml",
      "description": "Specialized roles for data analytics projects",
      "available_for_copy": true
    }
  ]
}

```text

#
# 3. `orchestrator_mode_validate`

**Purpose**: Validate mode configuration without activating

#
## Parameters

```text
json
{
  "mode_file": {
    "type": "string",
    "description": "Mode file to validate"
  },
  "repair_if_possible": {
    "type": "boolean",
    "default": false,
    "description": "Attempt automatic repair of common issues"
  }
}

```text

#
## Response

```text
json
{
  "is_valid": true,
  "mode_file": "development_roles.yaml",
  "validation_details": {
    "required_roles_present": true,
    "yaml_syntax_valid": true,
    "role_definitions_complete": true,
    "custom_roles_valid": true
  },
  "specialist_roles": [
    "architect", "implementer", "tester", "documenter", 
    "reviewer", "coordinator", "researcher"
  ],
  "custom_roles": [
    "security_auditor", "performance_optimizer"
  ],
  "warnings": [],
  "errors": []
}

```text

#
## Error Response

```text
json
{
  "is_valid": false,
  "mode_file": "broken_roles.yaml",
  "validation_details": {
    "required_roles_present": false,
    "yaml_syntax_valid": true,
    "role_definitions_complete": false,
    "custom_roles_valid": false
  },
  "errors": [
    "Missing required role: 'coordinator'",
    "Custom role 'data_scientist' missing required 'prompt' field"
  ],
  "warnings": [
    "Role 'legacy_specialist' appears to be unused"
  ],
  "repair_suggestions": [
    "Add coordinator role definition",
    "Complete data_scientist role configuration"
  ]
}

```text

#
# 4. `orchestrator_mode_create`

**Purpose**: Create new mode configuration from template

#
## Parameters

```text
json
{
  "mode_name": {
    "type": "string", 
    "description": "Name for new mode configuration"
  },
  "template_source": {
    "type": "string",
    "default": "default_roles.yaml",
    "description": "Template to base new mode on"
  },
  "custom_roles": {
    "type": "array",
    "description": "Additional custom roles to include",
    "items": {
      "type": "object",
      "properties": {
        "role_name": {"type": "string"},
        "prompt": {"type": "string"},
        "description": {"type": "string"}
      }
    }
  },
  "mode_settings": {
    "type": "object",
    "description": "Mode-specific configuration overrides",
    "properties": {
      "default_complexity": {"type": "string"},
      "auto_task_routing": {"type": "boolean"},
      "task_distribution": {"type": "string"}
    }
  }
}

```text

#
## Example Usage

```text
json
{
  "mode_name": "analytics_project_mode",
  "template_source": "default_roles.yaml",
  "custom_roles": [
    {
      "role_name": "data_scientist",
      "prompt": "You are a data scientist specialist...",
      "description": "Specialized in data analysis and machine learning"
    },
    {
      "role_name": "visualization_expert", 
      "prompt": "You are a data visualization specialist...",
      "description": "Creates charts, dashboards, and visual reports"
    }
  ],
  "mode_settings": {
    "default_complexity": "high",
    "auto_task_routing": true,
    "task_distribution": "specialized"
  }
}

```text

#
## Response

```text
json
{
  "success": true,
  "mode_created": "analytics_project_mode.yaml",
  "file_path": ".task_orchestrator/roles/analytics_project_mode.yaml",
  "mode_details": {
    "total_roles": 9,
    "standard_roles": 7,
    "custom_roles": 2,
    "mode_settings": {
      "default_complexity": "high",
      "auto_task_routing": true,
      "task_distribution": "specialized"
    }
  },
  "validation_status": "valid",
  "available_for_activation": true
}

```text

#
# 5. `orchestrator_mode_backup`

**Purpose**: Create backup of current mode configuration

#
## Parameters

```text
json
{
  "backup_name": {
    "type": "string",
    "description": "Optional name for backup (timestamp used if not provided)"
  },
  "include_session_binding": {
    "type": "boolean",
    "default": true,
    "description": "Include session-mode binding information"
  }
}

```text

#
## Response

```text
json
{
  "success": true,
  "backup_created": "mode_backup_20250601_143022.yaml",
  "backup_path": ".task_orchestrator/backups/mode_backup_20250601_143022.yaml",
  "backed_up_mode": "development_roles.yaml",
  "session_id": "session_abc123",
  "backup_size": "2.4KB",
  "created_at": "2025-06-01T14:30:22Z"
}

```text

#
# 6. `orchestrator_mode_restore`

**Purpose**: Restore mode configuration from backup

#
## Parameters

```text
json
{
  "backup_file": {
    "type": "string",
    "description": "Backup file to restore from"
  },
  "activate_after_restore": {
    "type": "boolean",
    "default": false,
    "description": "Activate restored mode immediately"
  },
  "restore_session_binding": {
    "type": "boolean",
    "default": true,
    "description": "Restore session-mode binding if available"
  }
}

```text

#
## Response

```text
json
{
  "success": true,
  "restored_mode": "development_roles.yaml",
  "backup_source": "mode_backup_20250601_143022.yaml",
  "mode_activated": false,
  "session_binding_restored": true,
  "validation_status": "valid",
  "restored_at": "2025-06-01T15:45:30Z"
}

```text

#
# Tool Integration Patterns

#
## Error Handling

All mode tools follow consistent error handling patterns:

```text
json
{
  "success": false,
  "error_type": "validation_failed",
  "error_message": "Mode configuration validation failed",
  "error_details": {
    "file": "custom_roles.yaml",
    "line": 23,
    "issue": "Missing required 'prompt' field for role 'data_scientist'"
  },
  "recovery_suggestions": [
    "Add prompt field to data_scientist role",
    "Use orchestrator_mode_validate with repair_if_possible=true"
  ],
  "fallback_mode": "default_roles.yaml"
}

```text

#
## Progress Tracking

Long-running operations provide progress updates:

```text
json
{
  "operation_id": "mode_create_op_123",
  "status": "in_progress",
  "progress": 65,
  "current_step": "Validating custom role definitions",
  "estimated_completion": "2025-06-01T14:32:00Z"
}
```text

#
## Caching and Performance

- **Mode Validation**: Cache validation results for 5 minutes

- **File Monitoring**: Watch mode files for changes

- **Lazy Loading**: Load mode details only when requested

- **Bulk Operations**: Support batch validation of multiple modes

#
## Security Considerations

- **Path Validation**: Prevent directory traversal attacks

- **File Permissions**: Validate file access permissions

- **Content Validation**: Sanitize YAML content before processing

- **Backup Encryption**: Optional encryption for sensitive role data

These MCP tools provide comprehensive mode management capabilities while maintaining security, performance, and reliability standards.
