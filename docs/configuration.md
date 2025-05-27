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

- Default templates: `mcp_task_orchestrator/config/default_roles.yaml`
- Project-specific templates: `<project_directory>/*_roles.yaml`

The MCP Task Orchestrator will look for role definition files in the following order of precedence:

1. Project-specific role files (any file with a name ending in `_roles.yaml` in the project directory)
2. Default role file (`config/default_roles.yaml`)

This allows you to have different sets of specialist roles for different projects.

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

You can add your own specialist types by adding them to the `default_roles.yaml` file or creating a project-specific role file:

```yaml
my_custom_specialist:
  role_definition: "You are a Custom Specialist focused on..."
  expertise:
    - "Expertise area 1"
    - "Expertise area 2"
  approach:
    - "Approach step 1"
    - "Approach step 2"
  output_format: "Expected output format description"
```

### Project-Specific Role Files

You can create project-specific role files to customize the specialist roles for a particular project. These files should be named with a suffix of `_roles.yaml` and placed in the project directory.

#### Automatic Example File Creation

When the MCP Task Orchestrator is run in a directory without any role definition files, it will automatically create an `example_roles.yaml` file in that directory. This file contains a commented-out version of the default roles that you can use as a template for creating your own custom roles.

To use this example file:

1. Rename it to have a suffix of `_roles.yaml` (e.g., `project_roles.yaml` or `custom_roles.yaml`)
2. Uncomment and modify the sections you want to customize
3. Restart the MCP Task Orchestrator server

For example, to create a set of specialist roles for a web development project, you might create a file called `web_dev_roles.yaml` in your project directory:

```yaml
# Web Development Specialist Roles

task_orchestrator:
  role_definition: "You are a Web Development Task Orchestrator"
  expertise:
    - "Breaking down web development tasks into manageable subtasks"
    - "Assigning appropriate specialist roles to each subtask"
    - "Managing dependencies between web development components"
    - "Tracking progress and coordinating work"
  approach:
    - "Analyze the web development requirements and context"
    - "Identify logical components (frontend, backend, database, etc.)"
    - "Create a clear dependency structure between subtasks"
    - "Assign appropriate specialist roles to each subtask"
    - "Estimate effort required for each component"
  output_format: "Structured task breakdown with clear objectives, specialist assignments, effort estimation, and dependency relationships"
  specialist_roles:
    frontend_developer: "Building user interfaces and client-side functionality"
    backend_developer: "Implementing server-side logic and APIs"
    database_specialist: "Designing and optimizing database schemas"
    ui_designer: "Creating user interface designs and assets"
    tester: "Testing and validating web applications"

frontend_developer:
  role_definition: "You are a Senior Frontend Developer focused on building user interfaces"
  expertise:
    - "HTML, CSS, and JavaScript development"
    - "Frontend frameworks (React, Vue, Angular)"
    - "Responsive design and cross-browser compatibility"
    - "Web accessibility standards"
    - "Frontend performance optimization"
  approach:
    - "Build modular, reusable UI components"
    - "Ensure responsive design for all screen sizes"
    - "Optimize for performance and loading speed"
    - "Follow accessibility best practices"
    - "Write clean, maintainable code with proper documentation"
  output_format: "Well-structured frontend code with component documentation and usage examples"

# Additional specialist roles...
```

When the MCP Task Orchestrator is run in a directory containing this file, it will use these custom roles instead of the default roles.

### Task Planning Customization

You can customize how tasks are broken down by modifying the task planning templates in the configuration file.
