# MCP Task Orchestrator - Configuration Guide

This guide explains how to configure and customize the MCP Task Orchestrator for your specific needs.

## Configuration Overview

The MCP Task Orchestrator uses several types of configuration:

1. **Client Configuration**: How MCP clients connect to the Task Orchestrator
2. **Specialist Templates**: Customizing the specialist prompts and roles
3. **Server Configuration**: General server settings and behavior
4. **Database Configuration**: State persistence and task tracking## Client Configuration

The MCP Task Orchestrator CLI automatically configures your MCP clients during installation. Each client has a different configuration format and location:

### Claude Desktop

**Location**:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Format**:

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["path/to/mcp_task_orchestrator/server.py"],
      "env": {}
    }
  }
}
```

### Windsurf

**Location**: `~/.windsurf/settings.json`

**Format**:

```json
{
  "name": "Task Orchestrator",
  "serverType": "local", 
  "command": "python",
  "args": ["path/to/mcp_task_orchestrator/server.py"],
  "workingDirectory": "path/to/mcp_task_orchestrator"
}
```

### Cursor

**Location**: `~/.cursor/settings.json`

**Format**: Depends on Cursor's specific MCP implementation

### VS Code

**Location**:

- Windows: `%APPDATA%\Code\User\settings.json`
- macOS: `~/Library/Application Support/Code/User/settings.json`
- Linux: `~/.config/Code/User/settings.json`

**Format**: Depends on the VS Code MCP extension being used## Specialist Templates

The MCP Task Orchestrator uses specialist templates to define the roles and prompts for different specialist types. You can customize these templates to better suit your needs.

### Template Location

Specialist templates are stored in the `config` directory of your installation:

- Default templates: `mcp_task_orchestrator/config/specialists.yaml`
- User templates: `~/.mcp_task_orchestrator/specialists.yaml`

The user templates take precedence over the default templates if both exist.

### Template Format

Specialist templates are defined in YAML format:

```yaml
specialists:
  architect:
    name: "System Architect"
    description: "Expert in system design and architecture planning"
    prompt_template: |
      ## Role
      You are a System Architect focused on designing robust, scalable systems
      ## Your Expertise
      • System design patterns and best practices
      • Architectural trade-offs and decision-making
      • Technical requirements analysis
      • Component and service design
      • Integration patterns and strategies
      • Performance and scalability considerations
      • Security architecture

      ## Your Approach
      • Start with a high-level overview of the system
      • Break down complex systems into manageable components
      • Consider scalability, reliability, and maintainability
      • Document design decisions and their rationales
      • Provide clear diagrams and visual representations
      • Consider both functional and non-functional requirements
      • Evaluate trade-offs between different approaches

      ## Expected Output Format
      Comprehensive architectural documents with diagrams, component descriptions, and implementation guidance

      ## Current Task
      **Title:** {{task_title}}
      **Description:** {{task_description}}

      ## Instructions
      You are now operating in ARCHITECT MODE. Focus entirely on this role and apply your specialized expertise to complete the task described above.
      
      When you have completed this task, be sure to:
      1. Provide a clear summary of what was accomplished
      2. List any artifacts or deliverables created
      3. Mention any recommendations for next steps

      Remember: You are the architect specialist for this task. Apply your expertise accordingly.
```

### Customizing Templates

To customize a specialist template:

1. Create a copy of the default template in your user directory:

   ```bash
   mkdir -p ~/.mcp_task_orchestrator
   cp mcp_task_orchestrator/config/specialists.yaml ~/.mcp_task_orchestrator/
   ```

2. Edit the template to suit your needs:

   ```bash
   nano ~/.mcp_task_orchestrator/specialists.yaml
   ```

3. Restart the MCP Task Orchestrator server for the changes to take effect## Server Configuration

The MCP Task Orchestrator server can be configured using environment variables or a configuration file.

### Environment Variables

- `MCP_TASK_ORCHESTRATOR_DB_PATH`: Path to the SQLite database file (default: `~/.mcp_task_orchestrator/task_orchestrator.db`)
- `MCP_TASK_ORCHESTRATOR_CONFIG_DIR`: Path to the configuration directory (default: `~/.mcp_task_orchestrator`)
- `MCP_TASK_ORCHESTRATOR_LOG_LEVEL`: Logging level (default: `INFO`)

### Configuration File

You can create a `config.yaml` file in the configuration directory to override default settings:

```yaml
# Server configuration
server:
  name: "task-orchestrator"
  log_level: "INFO"

# Database configuration
database:
  path: "~/.mcp_task_orchestrator/task_orchestrator.db"

# Task configuration
tasks:
  max_subtasks: 10
  default_complexity: "moderate"
```

## Database Configuration

The MCP Task Orchestrator uses SQLite for state persistence and task tracking. The database file is stored at `~/.mcp_task_orchestrator/task_orchestrator.db` by default.

### Database Schema

The database schema includes tables for:

- `tasks`: Parent tasks and their metadata
- `subtasks`: Individual subtasks and their relationships
- `specialists`: Specialist types and their templates
- `results`: Task results and artifacts

### Backup and Recovery

It's a good practice to periodically back up the database file:

```bash
# Create a backup
cp ~/.mcp_task_orchestrator/task_orchestrator.db ~/.mcp_task_orchestrator/task_orchestrator.db.backup
```

To restore from a backup:

```bash
# Restore from backup
cp ~/.mcp_task_orchestrator/task_orchestrator.db.backup ~/.mcp_task_orchestrator/task_orchestrator.db
```

## Advanced Configuration

### Custom Specialist Types

You can add your own specialist types by adding them to the `specialists.yaml` file:

```yaml
specialists:
  my_custom_specialist:
    name: "My Custom Specialist"
    description: "Expert in my custom domain"
    prompt_template: |
      ## Role
      You are a Custom Specialist focused on...
      # ... rest of the template
```

### Task Planning Customization

You can customize how tasks are broken down by modifying the task planning templates in the configuration file.
