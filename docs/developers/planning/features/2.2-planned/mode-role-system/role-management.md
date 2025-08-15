---
feature_id: "MODE_ROLE_MANAGEMENT"
version: "2.0.0"
status: "Planned"
priority: "High"
category: "Infrastructure"
dependencies: ["MODE_ROLE_ENHANCEMENT_V2"]
size_lines: 315
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/2.2-planned/mode-role-system/README.md"
  - "docs/developers/planning/features/2.2-planned/mode-role-system/directory-structure.md"
module_type: "implementation"
modularized_from: "docs/developers/planning/features/2.2-planned/[PLANNED]_mode_role_system_enhancement.md"
---

# Automatic Role Management System

This document specifies the automatic role management system that handles copying, validation, and maintenance of role configurations.

#
# Role Copying Architecture

```python
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

```text

#
# Role Validation System

```text
python
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
## Validation Rules

#
### Required Sections

1. **task_orchestrator**: Core orchestrator role definition

2. **specialist_roles**: List of available specialist types

3. **Required specialists**: architect, implementer, documenter

#
### Role Definition Requirements

```text
yaml
role_name:
  role_definition: "Clear description of role purpose"
  expertise: ["List of expertise areas"]
  approach: ["Approach guidelines"]
  output_format: "Expected output format"

```text

#
### Validation Checks

- **YAML Syntax**: Valid YAML structure

- **Required Fields**: All mandatory fields present

- **Role Completeness**: All referenced roles fully defined

- **Circular Dependencies**: No circular role references

- **Naming Conventions**: Valid role names (alphanumeric, underscore)

#
# Mode Configuration Format

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
# Automatic Role Updates

#
## Update Detection

```text
python
class RoleUpdateDetector:
    def __init__(self, config_dir: Path, project_roles_dir: Path):
        self.config_dir = config_dir
        self.project_roles_dir = project_roles_dir
        self.file_hashes = {}
    
    async def check_for_updates(self) -> List[UpdateNotification]:
        """Check for updates to system default roles."""
        
        updates = []
        
        for config_file in self.config_dir.glob("*.yaml"):
            project_file = self.project_roles_dir / config_file.name
            
            if project_file.exists():
                config_hash = await self.calculate_file_hash(config_file)
                project_hash = await self.calculate_file_hash(project_file)
                
                if config_hash != project_hash:
                    updates.append(UpdateNotification(
                        file_name=config_file.name,
                        update_type="modified",
                        config_version=await self.extract_version(config_file),
                        project_version=await self.extract_version(project_file)
                    ))
            else:
                updates.append(UpdateNotification(
                    file_name=config_file.name,
                    update_type="new_file",
                    config_version=await self.extract_version(config_file),
                    project_version=None
                ))
        
        return updates
    
    async def apply_update(self, update: UpdateNotification, merge_strategy: str):
        """Apply update using specified merge strategy."""
        
        if merge_strategy == "overwrite":
            await self.overwrite_with_config_version(update)
        elif merge_strategy == "merge":
            await self.merge_configurations(update)
        elif merge_strategy == "ignore":
            await self.mark_update_ignored(update)
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")

```text

#
## Merge Strategies

#
### Overwrite Strategy

- Replace project file with system default

- Create backup of current project file

- Preserve any project-specific metadata

- Log the overwrite operation

#
### Merge Strategy

- Preserve custom roles and modifications

- Update system roles to new versions

- Merge configuration settings intelligently

- Validate merged result

#
### Ignore Strategy

- Mark update as deliberately ignored

- Store reason for ignoring update

- Continue to monitor for future updates

- Allow manual reconsideration later

#
# Recovery Mechanisms

#
## Missing File Recovery

```text
python
class ModeRecoverySystem:
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

```text

#
## Corruption Recovery

```text
python
async def handle_corrupted_mode_file(self, mode_file: str):
    """Handle corrupted mode configuration file."""
    
    
# Attempt syntax repair
    repair_result = await self.attempt_syntax_repair(mode_file)
    if repair_result.success:
        return repair_result
    
    
# Try restoring from backup
    backup_result = await self.restore_from_latest_backup(mode_file)
    if backup_result.success:
        return backup_result
    
    
# Recreate from system defaults
    recreate_result = await self.recreate_from_defaults(mode_file)
    return recreate_result
```text

#
## Automatic Recovery

- **Silent Recovery**: Attempt automatic fixes for common issues

- **User Notification**: Inform user of recovery actions taken

- **Backup Creation**: Always backup before attempting repairs

- **Fallback Strategy**: Graceful degradation to working configuration

This automatic role management system ensures reliable operation while providing flexibility for customization and robust recovery from various failure scenarios.
