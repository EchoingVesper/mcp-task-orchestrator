

# 🔧 Feature Specification: Mode/Role System Enhancement

**Feature ID**: `MODE_ROLE_ENHANCEMENT_V2`  
**Priority**: HIGH ⭐ - Critical for session-mode binding  
**Category**: Core Infrastructure  
**Estimated Effort**: 2-3 weeks  
**Created**: 2025-06-01  
**Status**: [RESEARCH] - Specification complete, ready for approval  

---

#

# 📋 Overview

Enhance the MCP Task Orchestrator's role system to support dynamic mode selection, automatic role configuration management, and session-mode binding. This system transforms the static role configuration into a flexible, session-aware specialization framework.

#

# 🎯 Objectives

1. **Dynamic Mode Selection**: Allow switching between different specialist role configurations per session

2. **Automatic Role Management**: Copy default roles to project directories and manage updates

3. **Session-Mode Binding**: Link sessions to specific role configurations with validation

4. **Recovery & Resilience**: Handle missing or corrupted role files gracefully

5. **Multi-Project Support**: Enable different projects to use different specialist configurations

#

# 🏗️ Current vs. Enhanced Architecture

#

## Current Role System (v1.4.1)

```text
Static Configuration:
config/default_roles.yaml → Hardcoded role definitions
                          → Single global configuration
                          → No per-project customization
                          → No session awareness

```text

#

## Enhanced Mode System (v2.0)

```text

Dynamic Mode System:
config/default_roles.yaml → Project .task_orchestrator/roles/ → Session Mode Binding
                                    ↓                                ↓
                            User customizations              Active session uses
                            Multiple .yaml files             selected mode configuration
                            Version control ready            Automatic validation
                            Recovery mechanisms               Fallback to defaults

```text

#

# 🛠️ New MCP Tools Specification

#

## 1. `orchestrator_mode_select`

**Purpose**: Select and bind a mode configuration to the active session

**Parameters**:

```text
json
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
text

**Example Usage**:

```text
json
{
  "mode_file": "development_roles.yaml",
  "validate_first": true,
  "auto_copy_if_missing": true,
  "backup_current": true
}

```text
text

**Response**:

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
text

#

## 2. `orchestrator_mode_list`

**Purpose**: List available modes and their status

**Parameters**:

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
text

**Response**:

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
text

#

## 3. `orchestrator_mode_validate`

**Purpose**: Validate mode configuration without activating

**Parameters**:

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
text

#

## 4. `orchestrator_mode_create`

**Purpose**: Create new mode configuration from template

**Parameters**:

```text
json
{
  "mode_name": {
    "type": "string", 
    "description": "Name for new mode configuration"
  },
  "base_template": {
    "type": "string",
    "default": "default_roles.yaml", 
    "description": "Template to copy from"
  },
  "specialist_customizations": {
    "type": "object",
    "description": "Custom role definitions to add/override"
  }
}

```text
text

#

# 🗂️ Enhanced Directory Structure

#

## Project Directory Layout

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

# 📝 Mode Configuration Format

#

## Enhanced YAML Structure

```text
yaml

# example: development_roles.yaml

mode_metadata:
  name: "Development Project Mode"
  description: "Enhanced roles for software development projects"
  version: "2.0.0"
  created_by: "user_name"
  created_at: "2025-06-01T10:00:00Z"
  compatible_versions: ["1.4.0+"]
  
mode_configuration:
  default_complexity: "moderate"
  auto_task_routing: true
  max_subtask_depth: 5
  progress_aggregation: "weighted"
  

# Standard orchestrator roles (required)

task_orchestrator:
  role_definition: "You are a Task Orchestrator focused on breaking down complex tasks"
  expertise:
    - "Breaking down complex tasks into manageable subtasks"
    - "Assigning appropriate specialist roles to each subtask"
    - "Managing dependencies between subtasks"
    - "Tracking progress and coordinating work"
  approach:
    - "Carefully analyze the requirements and context"
    - "Identify logical components that can be worked on independently"
    - "Create a clear dependency structure between subtasks"
  output_format: "Structured task breakdown with clear objectives"
  specialist_roles:
    architect: "System design and architecture planning"
    implementer: "Writing code and implementing features"
    debugger: "Fixing issues and optimizing performance"
    documenter: "Creating documentation and guides"
    reviewer: "Code review and quality assurance"
    tester: "Testing and validation"
    researcher: "Research and information gathering"

# Standard specialist roles (customizable)

architect:
  role_definition: "Senior Software Architect with expertise in system design"
  expertise:
    - "System design and architecture patterns"
    - "Technology selection and trade-offs analysis"
    - "Scalability, performance, and reliability planning"
  approach:
    - "Think systematically about requirements and constraints"
    - "Consider scalability, maintainability, security implications"
    - "Provide clear architectural decisions with rationale"
  output_format: "Structured architectural plans with clear decisions"

# Custom roles for this mode

security_auditor:
  role_definition: "Security Analysis Specialist focusing on threat assessment"
  expertise:
    - "OWASP security standards and best practices"
    - "Penetration testing methodologies"
    - "Secure coding practices and vulnerability assessment"
    - "Compliance frameworks (SOX, HIPAA, GDPR)"
  approach:
    - "Focus on security implications of all decisions"
    - "Identify potential vulnerabilities and attack vectors"
    - "Ensure compliance with security standards"
    - "Provide mitigation strategies for identified risks"
  output_format: "Security assessment reports with risk ratings and mitigation plans"

performance_optimizer:
  role_definition: "Performance Engineering Specialist"
  expertise:
    - "Performance profiling and optimization techniques"
    - "Scalability analysis and capacity planning"
    - "Database optimization and query tuning"
    - "Frontend and backend performance optimization"
  approach:
    - "Establish performance baselines and targets"
    - "Identify bottlenecks and optimization opportunities"
    - "Recommend specific optimization strategies"
    - "Validate performance improvements"
  output_format: "Performance analysis with specific optimization recommendations"

# Mode-specific configuration

task_routing_rules:
  security_tasks:
    required_specialist: "security_auditor"
    secondary_review: "architect"
    complexity_boost: 1  

# Increase complexity for security tasks

  
  performance_tasks:
    required_specialist: "performance_optimizer"
    secondary_review: ["architect", "implementer"]
    parallel_execution: false  

# Performance tasks should be sequential

validation_rules:
  required_roles: ["task_orchestrator", "architect", "implementer", "documenter"]
  optional_roles: ["security_auditor", "performance_optimizer", "tester", "reviewer"]
  minimum_specialist_count: 4
  maximum_specialist_count: 12

```text

#

# 🔄 Automatic Role Management System

#

## Role Copying Architecture

```text
python
class RoleManagementSystem:
    def __init__(self, project_root: Path, config_dir: Path):
        self.project_root = project_root
        self.config_dir = config_dir
        self.roles_dir = project_root / ".task_orchestrator" / "roles"
        self.modes_dir = project_root / ".task_orchestrator" / "modes"
        
    async def initialize_project_roles(self):
        """Initialize role directory for new project."""
        
        

# Create directory structure

        self.roles_dir.mkdir(parents=True, exist_ok=True)
        self.modes_dir.mkdir(parents=True, exist_ok=True)
        
        

# Copy default roles if directory is empty

        if not any(self.roles_dir.glob("*.yaml")):
            await self.copy_default_roles()
        
        

# Create initial project_roles.yaml if it doesn't exist

        project_roles_file = self.roles_dir / "project_roles.yaml"
        if not project_roles_file.exists():
            await self.create_project_specific_roles()
    
    async def copy_default_roles(self):
        """Copy all default role configurations to project directory."""
        
        default_files = [
            "default_roles.yaml",
            "example_roles.yaml",  

# If exists

        ]
        
        for filename in default_files:
            source = self.config_dir / filename
            if source.exists():
                target = self.roles_dir / filename
                
                

# Copy with metadata preservation

                shutil.copy2(source, target)
                
                

# Add project-specific metadata

                await self.add_project_metadata(target)
                
                self.log(f"Copied {filename} to project roles directory")
    
    async def detect_role_changes(self):
        """Monitor for changes in role configurations."""
        
        

# Check for new files in config directory

        config_files = set(f.name for f in self.config_dir.glob("*.yaml"))
        project_files = set(f.name for f in self.roles_dir.glob("*.yaml"))
        
        new_files = config_files - project_files
        
        

# Offer to copy new template files

        for filename in new_files:
            if filename not in ["project_roles.yaml"]:  

# Skip project-specific files

                offer_to_copy = await self.prompt_user_for_copy(filename)
                if offer_to_copy:
                    await self.copy_role_file(filename)
    
    async def validate_role_file(self, filename: str) -> ValidationResult:
        """Validate role configuration file."""
        
        filepath = self.roles_dir / filename
        if not filepath.exists():
            return ValidationResult(
                valid=False,
                error="File does not exist",
                suggestions=["Copy from config directory", "Create new from template"]
            )
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            

# Validate required sections

            validation_errors = []
            
            if 'task_orchestrator' not in config:
                validation_errors.append("Missing required 'task_orchestrator' section")
            
            if 'specialist_roles' not in config.get('task_orchestrator', {}):
                validation_errors.append("Missing 'specialist_roles' in task_orchestrator")
            
            

# Validate specialist role definitions

            specialist_roles = config.get('task_orchestrator', {}).get('specialist_roles', {})
            required_roles = ['architect', 'implementer', 'documenter']
            
            for role in required_roles:
                if role not in specialist_roles:
                    validation_errors.append(f"Missing required specialist role: {role}")
                
                if role in config:  

# Check if role is defined

                    role_config = config[role]
                    if 'role_definition' not in role_config:
                        validation_errors.append(f"Role '{role}' missing role_definition")
            
            if validation_errors:
                return ValidationResult(
                    valid=False,
                    errors=validation_errors,
                    warnings=[],
                    suggestions=self.generate_repair_suggestions(validation_errors)
                )
            
            return ValidationResult(valid=True, role_count=len(config.keys()) - 1)  

# Exclude metadata

            
        except yaml.YAMLError as e:
            return ValidationResult(
                valid=False,
                error=f"YAML parsing error: {str(e)}",
                suggestions=["Check YAML syntax", "Restore from backup"]
            )

```text

#

# 🔗 Session-Mode Binding System

#

## Session-Mode Integration

```text
python
class SessionModeBinding:
    def __init__(self, session_manager, mode_manager):
        self.session_manager = session_manager
        self.mode_manager = mode_manager
    
    async def bind_session_to_mode(self, session_id: str, mode_file: str):
        """Bind active session to specific mode configuration."""
        
        

# Validate session is active

        active_session = await self.session_manager.get_active_session()
        if not active_session or active_session.session_id != session_id:
            raise SessionNotActiveError("Session must be active to bind mode")
        
        

# Validate mode file exists and is valid

        validation_result = await self.mode_manager.validate_mode(mode_file)
        if not validation_result.valid:
            raise InvalidModeError(f"Mode validation failed: {validation_result.errors}")
        
        

# Create binding record

        binding = SessionModeBinding(
            session_id=session_id,
            mode_file=mode_file,
            bound_at=datetime.utcnow(),
            validation_result=validation_result
        )
        
        

# Save binding to database

        await self.db.save_session_mode_binding(binding)
        
        

# Update session context with mode information

        await self.update_session_context_with_mode(session_id, mode_file)
        
        

# Cache mode configuration for performance

        await self.cache_mode_configuration(session_id, mode_file)
        
        return binding
    
    async def get_session_mode_context(self, session_id: str) -> ModeContext:
        """Get complete mode context for session."""
        
        binding = await self.db.get_session_mode_binding(session_id)
        if not binding:
            

# Use default mode

            binding = await self.create_default_mode_binding(session_id)
        
        mode_config = await self.load_mode_configuration(binding.mode_file)
        
        return ModeContext(
            session_id=session_id,
            mode_file=binding.mode_file,
            specialist_roles=mode_config.get_specialist_roles(),
            custom_roles=mode_config.get_custom_roles(),
            routing_rules=mode_config.get_routing_rules(),
            configuration=mode_config.get_mode_configuration()
        )

```text

#

## Mode Context for Task Execution

```text
python
async def execute_task_with_mode_context(self, task_id: str, session_id: str):
    """Execute task using session-specific mode context."""
    
    

# Get mode context for session

    mode_context = await self.get_session_mode_context(session_id)
    
    

# Get task details

    task = await self.db.get_task(task_id)
    
    

# Determine specialist using mode-specific routing

    specialist_type = await self.determine_specialist_with_mode(
        task, mode_context.routing_rules
    )
    
    

# Get specialist definition from mode

    specialist_config = mode_context.get_specialist_config(specialist_type)
    
    

# Execute task with mode-specific specialist context

    return await self.execute_task_with_specialist(
        task=task,
        specialist_config=specialist_config,
        mode_context=mode_context
    )

```text

#

# 🚨 Recovery Mechanisms

#

## Missing/Corrupted File Recovery

```text
python
class ModeRecoverySystem:
    def __init__(self, mode_manager, backup_manager):
        self.mode_manager = mode_manager
        self.backup_manager = backup_manager
    
    async def handle_missing_mode_file(self, session_id: str, mode_file: str):
        """Handle scenario where mode file is missing."""
        
        recovery_options = []
        
        

# Option 1: Restore from backup

        backup_files = await self.backup_manager.find_mode_backups(mode_file)
        if backup_files:
            recovery_options.append({
                "type": "restore_backup",
                "description": f"Restore from backup ({len(backup_files)} available)",
                "backups": backup_files
            })
        
        

# Option 2: Copy from config directory

        config_file = self.mode_manager.config_dir / mode_file
        if config_file.exists():
            recovery_options.append({
                "type": "copy_from_config", 
                "description": "Copy fresh template from config directory",
                "source": str(config_file)
            })
        
        

# Option 3: Create from default template

        recovery_options.append({
            "type": "create_from_default",
            "description": "Create new configuration from default template"
        })
        
        

# Option 4: Switch to fallback mode

        recovery_options.append({
            "type": "fallback_mode",
            "description": "Switch session to default_roles.yaml",
            "fallback_mode": "default_roles.yaml"
        })
        
        return recovery_options
    
    async def auto_recover_mode(self, session_id: str, mode_file: str):
        """Attempt automatic recovery of missing mode file."""
        
        

# Try recovery options in order of preference

        recovery_attempts = [
            self.restore_latest_backup,
            self.copy_from_config_directory,
            self.create_from_default_template,
            self.fallback_to_default_mode
        ]
        
        for recovery_method in recovery_attempts:
            try:
                success = await recovery_method(session_id, mode_file)
                if success:
                    await self.log_recovery_success(session_id, mode_file, recovery_method.__name__)
                    return True
            except Exception as e:
                await self.log_recovery_attempt(session_id, mode_file, recovery_method.__name__, str(e))
                continue
        
        

# All recovery attempts failed

        await self.log_recovery_failure(session_id, mode_file)
        return False

```text

#

# 📊 Migration Strategy

#

## Backward Compatibility

- **Existing Sessions**: Continue to work with default_roles.yaml

- **Gradual Migration**: Sessions can be individually migrated to new mode system

- **Legacy Support**: Original role configuration format fully supported

- **Optional Adoption**: Enhanced features are opt-in

#

## Migration Process

```text
python
async def migrate_session_to_mode_system(self, session_id: str):
    """Migrate existing session to use mode system."""
    
    

# Check if session already uses mode system

    existing_binding = await self.get_session_mode_binding(session_id)
    if existing_binding:
        return existing_binding
    
    

# Create default mode binding for legacy session

    default_binding = await self.create_default_mode_binding(session_id)
    
    

# Initialize project roles directory if needed

    await self.initialize_project_roles()
    
    

# Offer to customize mode for this session

    customization_opportunity = {
        "session_id": session_id,
        "current_mode": "default_roles.yaml",
        "available_customizations": [
            "Add custom specialist roles",
            "Modify task routing rules",
            "Set project-specific defaults"
        ],
        "migration_complete": True
    }
    
    return customization_opportunity

```text

#

# 🎯 Usage Examples

#

## Basic Mode Selection

```text
json
// Switch to development mode
{
  "tool": "orchestrator_mode_select",
  "parameters": {
    "mode_file": "development_roles.yaml",
    "validate_first": true
  }
}

// Response: Mode activated with security_auditor and performance_optimizer roles

```text

#

## Mode Creation

```text
json
// Create custom analytics mode
{
  "tool": "orchestrator_mode_create", 
  "parameters": {
    "mode_name": "analytics_project.yaml",
    "base_template": "default_roles.yaml",
    "specialist_customizations": {
      "data_scientist": {
        "role_definition": "Data Science Specialist",
        "expertise": ["Statistical analysis", "Machine learning", "Data visualization"]
      }
    }
  }
}

```text

#

## Mode Validation and Recovery

```text
json
// Validate mode before using
{
  "tool": "orchestrator_mode_validate",
  "parameters": {
    "mode_file": "custom_mode.yaml",
    "repair_if_possible": true
  }
}

// List available modes
{
  "tool": "orchestrator_mode_list",
  "parameters": {
    "include_invalid": true,
    "show_details": true
  }
}
```text

#

# 📈 Benefits & Success Metrics

#

## Immediate Benefits

- **Flexibility**: Different projects can use different specialist configurations

- **Customization**: Easy customization of roles for specific project types

- **Resilience**: Automatic recovery from missing or corrupted configurations

- **Version Control**: Role configurations can be versioned with project code

#

## Long-term Benefits

- **Knowledge Capture**: Project-specific expertise captured in role definitions

- **Team Alignment**: Shared understanding of specialist responsibilities

- **Continuous Improvement**: Role definitions evolve with project learning

- **Scalability**: Support for unlimited custom specialist types

#

## Success Metrics

- **Adoption Rate**: % of sessions using custom modes (target: 60%+)

- **Recovery Success**: % of missing file situations auto-recovered (target: 90%+)

- **Customization Usage**: % of projects with custom specialist roles (target: 40%+)

- **System Reliability**: Mode-related errors (target: <1% of tool calls)

---

#

# 🔄 Implementation Roadmap

#

## Phase 1: Core Mode System (Week 1)

- Mode file validation and loading system

- Basic `orchestrator_mode_select` tool

- Session-mode binding database schema

- Automatic role copying mechanism

#

## Phase 2: Enhanced Tools (Week 2)

- `orchestrator_mode_list` and `orchestrator_mode_validate` tools

- `orchestrator_mode_create` tool with templates

- Mode switching and backup systems

- Enhanced validation with repair capabilities

#

## Phase 3: Recovery & Resilience (Week 3)

- Missing file detection and recovery

- Automatic backup creation and restoration

- Error handling and fallback mechanisms

- Migration tools for existing sessions

---

**Next Steps**: 

1. Review and approve mode system specification

2. Design database schema for mode management

3. Implement core mode loading and validation

4. Create enhanced MCP tools for mode management

**Dependencies**:

- Enhanced session management architecture

- Database schema enhancements

- File system monitoring capabilities

**Integration Points**:

- Session management system (mode binding)

- Task execution engine (specialist context)

- MCP tool router (mode-aware tool calls)

- Recovery and backup systems
