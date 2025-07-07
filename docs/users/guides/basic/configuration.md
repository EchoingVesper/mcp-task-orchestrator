

# Basic Configuration

#

# Configuration Files

MCP Task Orchestrator uses YAML configuration files stored in your project's `.task_orchestrator/` directory.

#

# Default Configuration

When you first initialize a project, a default configuration is created:

```yaml

# .task_orchestrator/config.yaml

workspace:
  name: "default"
  database_path: ".task_orchestrator/workspace.db"
  
specialists:
  default_roles:
    - architect
    - implementer
    - reviewer
    - documenter
    
orchestration:
  max_concurrent_tasks: 3
  timeout_minutes: 30
  auto_synthesize: true

quality:
  require_review: true
  save_artifacts: true
  error_recovery: "auto"

```text

#

# Basic Customization

#

## Specialist Preferences

Customize which specialists are used by default:

```text
yaml
specialists:
  default_roles:
    - implementer    

# Focus on coding

    - debugger      

# Include debugging

    

# Remove architect for simple tasks

    
  role_preferences:
    implementer:
      coding_style: "pythonic"
      test_coverage: true
    reviewer:
      strict_mode: false

```text

#

## Timeout Settings

Adjust timeouts for your project complexity:

```text
yaml
orchestration:
  timeout_minutes: 60      

# Longer for complex tasks

  task_timeout: 15         

# Per-task timeout

  synthesis_timeout: 10    

# Result combination timeout

```text

#

## Workspace Settings

Configure workspace behavior:

```text
yaml
workspace:
  auto_cleanup: true       

# Clean up old artifacts

  backup_frequency: "daily"
  max_artifact_size: "10MB"

```text

#

# Environment Configuration

#

## MCP Client Settings

Configure MCP server behavior through environment variables:

```text
bash

# Enable dependency injection (recommended)

export MCP_TASK_ORCHESTRATOR_USE_DI=true

# Set database location

export MCP_TASK_ORCHESTRATOR_DB_PATH="/custom/path/orchestrator.db"

# Enable debug logging

export MCP_TASK_ORCHESTRATOR_LOG_LEVEL=debug

```text

#

## Project-Specific Settings

Create `.env` file in your project root:

```text
bash

# .env

MCP_WORKSPACE_NAME=my-project
MCP_DEFAULT_COMPLEXITY=intermediate
MCP_AUTO_SAVE_ARTIFACTS=true

```text

#

# Common Configuration Patterns

#

## Code-Heavy Projects

```text
yaml
specialists:
  default_roles:
    - architect
    - implementer
    - debugger
    - reviewer
    
  role_preferences:
    implementer:
      focus: "clean_code"
      test_driven: true
    reviewer:
      check_performance: true

```text

#

## Documentation Projects

```text
yaml
specialists:
  default_roles:
    - researcher
    - documenter
    - reviewer
    
  role_preferences:
    documenter:
      style: "user_friendly"
      include_examples: true

```text

#

## Research and Analysis

```text
yaml
specialists:
  default_roles:
    - researcher
    - architect
    - documenter
    
orchestration:
  max_concurrent_tasks: 1  

# Sequential for research

  deep_analysis: true

```text

#

# Configuration Validation

#

## Check Your Configuration

```text
bash

# Test configuration

python -m mcp_task_orchestrator.tools.diagnostics.validate_config

# Expected output: All configuration valid

```text

#

## Common Configuration Errors

**Invalid specialist roles**: Check spelling of role names
**Timeout too low**: Increase for complex tasks
**Database permission errors**: Check file permissions
**Missing workspace directory**: Ensure `.task_orchestrator/` exists

#

# Advanced Settings

#

## Custom Specialist Definitions

Create custom specialist roles:

```yaml
specialists:
  custom_roles:
    security_expert:
      base_role: "reviewer"
      focus: "security"
      tools: ["static_analysis", "vulnerability_scan"]
      
    ui_designer:
      base_role: "implementer"  
      focus: "user_interface"
      tools: ["design_review", "accessibility_check"]

```text

#

## Quality Gates

Configure automated quality checks:

```text
yaml
quality:
  gates:
    - name: "code_review"
      required: true
      timeout: 300
    - name: "documentation"
      required: false
      auto_generate: true
```text

#

# Troubleshooting Configuration

#

## Configuration Not Loading

- Check YAML syntax with online validator

- Verify file permissions are readable

- Ensure `.task_orchestrator/` directory exists

#

## Specialists Not Working

- Verify role names match available specialists

- Check custom role definitions

- Test with default configuration first

#

## Performance Issues

- Reduce `max_concurrent_tasks` for resource constraints

- Increase timeouts for complex projects

- Enable `auto_cleanup` to manage disk space

#

# Next Steps

- Learn about [specialist coordination](../intermediate/specialist-coordination.md)

- Explore [custom roles](../../reference/specialists/)

- See [troubleshooting guide](../../troubleshooting/common-issues/)
