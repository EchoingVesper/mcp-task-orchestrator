---
feature_id: "MODE_ROLE_DIRECTORY_STRUCTURE"
version: "2.0.0"
status: "Planned"
priority: "High"
category: "Infrastructure"
dependencies: ["MODE_ROLE_ENHANCEMENT_V2"]
size_lines: 265
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/2.2-planned/mode-role-system/README.md"
  - "docs/developers/planning/features/2.2-planned/mode-role-system/role-management.md"
module_type: "specification"
modularized_from: "docs/developers/planning/features/2.2-planned/[PLANNED]_mode_role_system_enhancement.md"
---

# Directory Structure: Enhanced Mode System

This document specifies the enhanced directory structure for the mode/role system.

#
# Project Directory Layout

```text
project_root/
├── .task_orchestrator/
│   ├── roles/                          
# Mode configurations
│   │   ├── project_roles.yaml         
# Project-specific roles (default)
│   │   ├── default_roles.yaml         
# Copy of system defaults
│   │   ├── development_mode.yaml      
# Custom development configuration
│   │   ├── research_mode.yaml         
# Research project configuration
│   │   └── custom_analytics.yaml      
# Custom analytics roles
│   ├── modes/                          
# Mode management
│   │   ├── active_mode.yaml           
# Current active mode reference
│   │   ├── mode_history.yaml          
# Mode switching history
│   │   └── validation_cache.yaml      
# Cached validation results
│   ├── backups/                        
# Mode backups
│   │   ├── mode_backup_20250601_143022.yaml
│   │   └── session_mode_backup_abc123.yaml
│   └── sessions/                       
# Session-specific data
│       └── [session_id]/
│           ├── session.md              
# Human-readable session file
│           └── mode_binding.yaml       
# Session-mode binding details

```text

#
# Directory Purposes

#
## `/roles/` Directory

**Purpose**: Store all mode configuration files for the project

**File Types**:

- `*.yaml` - Mode configuration files

- Each file defines a complete set of specialist roles

- Files can inherit from system defaults or other configurations

**Key Files**:

- `project_roles.yaml` - Default mode for the project

- `default_roles.yaml` - Copy of system-wide defaults

- Custom mode files with descriptive names

**Management**:

- Automatically created when project is initialized

- System defaults copied on first run

- Version control friendly (commit with project)

#
## `/modes/` Directory

**Purpose**: Store mode management metadata and state

**Key Files**:

#
### `active_mode.yaml`

```text
yaml

# Current active mode reference

active_mode:
  mode_file: "development_mode.yaml"
  activated_at: "2025-06-01T14:30:22Z"
  session_id: "session_abc123"
  validation_status: "valid"
  backup_available: true
  
mode_metadata:
  last_validation: "2025-06-01T14:30:20Z"
  validation_result: "passed"
  specialist_count: 9
  custom_roles_count: 2

```text

#
### `mode_history.yaml`

```text
yaml

# Mode switching history

mode_history:
  - timestamp: "2025-06-01T14:30:22Z"
    from_mode: "default_roles.yaml"
    to_mode: "development_mode.yaml"
    session_id: "session_abc123"
    reason: "user_request"
    success: true
    
  - timestamp: "2025-06-01T10:15:30Z"
    from_mode: null
    to_mode: "default_roles.yaml"
    session_id: "session_abc123"
    reason: "session_initialization"
    success: true

```text

#
### `validation_cache.yaml`

```text
yaml

# Cached validation results

validation_cache:
  "development_mode.yaml":
    last_validated: "2025-06-01T14:30:20Z"
    file_hash: "sha256:abc123..."
    validation_result: "valid"
    specialist_roles: ["architect", "implementer", "tester", "documenter"]
    custom_roles: ["security_auditor", "performance_optimizer"]
    warnings: []
    errors: []
    
  "default_roles.yaml":
    last_validated: "2025-06-01T10:00:00Z"
    file_hash: "sha256:def456..."
    validation_result: "valid"
    specialist_roles: ["architect", "implementer", "documenter", "reviewer"]
    custom_roles: []
    warnings: []
    errors: []

```text

#
## `/backups/` Directory

**Purpose**: Store automatic backups of mode configurations

**Backup Types**:

#
### Mode Backups

```text
text
mode_backup_YYYYMMDD_HHMMSS.yaml

```text

- Created before mode switches

- Include complete mode configuration

- Timestamped for easy identification

#
### Session Backups

```text
text
session_mode_backup_[session_id].yaml

```text

- Session-specific mode backups

- Created when session ends or mode changes

- Include session context and mode binding

**Backup Content Example**:
```text
yaml

# mode_backup_20250601_143022.yaml

backup_metadata:
  created_at: "2025-06-01T14:30:22Z"
  source_mode: "development_mode.yaml"
  session_id: "session_abc123"
  backup_reason: "mode_switch"
  
original_content:
  
# Complete original mode configuration
  mode_metadata:
    name: "Development Project Mode"
    
# ... rest of configuration

```text

#
## `/sessions/[session_id]/` Directory

**Purpose**: Store session-specific mode binding and context

#
### `mode_binding.yaml`

```text
yaml

# Session-mode binding details

session_mode_binding:
  session_id: "session_abc123"
  mode_file: "development_mode.yaml"
  bound_at: "2025-06-01T14:30:22Z"
  binding_status: "active"
  
mode_context:
  specialist_roles:
    - architect
    - implementer
    - tester
    - documenter
    - reviewer
    - coordinator
    - researcher
  custom_roles:
    - security_auditor
    - performance_optimizer
  
  routing_rules:
    security_tasks:
      required_specialist: "security_auditor"
      secondary_review: "architect"
    performance_tasks:
      required_specialist: "performance_optimizer"
      secondary_review: ["architect", "implementer"]
  
  mode_configuration:
    default_complexity: "moderate"
    auto_task_routing: true
    max_subtask_depth: 5
    progress_aggregation: "weighted"

validation_history:
  - timestamp: "2025-06-01T14:30:20Z"
    validation_result: "valid"
    warnings: []
    errors: []

```text

#
# File Organization Principles

#
## Naming Conventions

**Mode Files**: Descriptive names reflecting purpose

- `development_mode.yaml` - Software development projects

- `research_mode.yaml` - Research and analysis projects

- `analytics_mode.yaml` - Data analytics projects

- `documentation_mode.yaml` - Documentation-focused projects

**Backup Files**: Timestamp-based naming

- Format: `mode_backup_YYYYMMDD_HHMMSS.yaml`

- Example: `mode_backup_20250601_143022.yaml`

**Session Files**: Session ID-based organization

- Directory: `sessions/[session_id]/`

- Files: `session.md`, `mode_binding.yaml`

#
## File Relationships

```text
text
Relationships:
roles/project_roles.yaml ←→ modes/active_mode.yaml
        ↓                           ↓
backups/mode_backup_*.yaml ←→ sessions/[id]/mode_binding.yaml

```text

#
## Access Patterns

1. **Mode Activation**:
- Read: `roles/[mode_file].yaml`
- Validate: Check against `modes/validation_cache.yaml`
- Update: `modes/active_mode.yaml`
- Create: `sessions/[session_id]/mode_binding.yaml`

2. **Mode Switching**:
- Backup: Current mode to `backups/`
- Read: New mode from `roles/`
- Update: `modes/active_mode.yaml` and `modes/mode_history.yaml`
- Update: `sessions/[session_id]/mode_binding.yaml`

3. **Validation**:
- Read: Mode file from `roles/`
- Check: `modes/validation_cache.yaml` for cached results
- Update: Cache with new validation results

#
# Directory Initialization

#
## Automatic Creation

When a project is first initialized:

1. Create `.task_orchestrator/` directory structure

2. Create `roles/` subdirectory

3. Copy `default_roles.yaml` from system configuration

4. Create `project_roles.yaml` based on project detection

5. Initialize `modes/` directory with default metadata

6. Create `backups/` directory for future use

#
## Project Detection Logic

```text
python
async def detect_project_type(project_root: Path) -> str:
    """Detect project type for appropriate default mode."""
    
    
# Check for common project indicators
    if (project_root / "package.json").exists():
        return "web_development_mode"
    elif (project_root / "pyproject.toml").exists():
        return "python_development_mode"
    elif (project_root / "Cargo.toml").exists():
        return "rust_development_mode"
    elif (project_root / "README.md").exists():
        return "documentation_mode"
    else:
        return "default_mode"
```text

#
## Cleanup and Maintenance

#
### Automatic Cleanup

- Remove old backup files (>30 days by default)

- Clean validation cache for deleted mode files

- Archive session directories for completed projects

#
### Manual Maintenance

- `orchestrator_mode_cleanup` tool for manual cleanup

- Validation and repair tools for corrupted configurations

- Migration tools for upgrading directory structure

This directory structure provides organized, scalable storage for mode configurations while maintaining clear separation of concerns and enabling efficient access patterns for the enhanced mode system.
