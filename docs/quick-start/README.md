# Quick Start Guide

Get up and running with MCP Task Orchestrator in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- An MCP-compatible client (Claude Desktop, Cursor, Windsurf, or VS Code)

## Installation

### 1. Install the Package

```bash
pip install mcp-task-orchestrator
```

### 2. Configure Your MCP Client

#### For Claude Desktop

Edit your Claude configuration file:

**Mac/Linux**: `~/.config/claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}
```

#### For Cursor/Windsurf

Add to your workspace `.mcp/config.json`:

```json
{
  "servers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

### 3. Restart Your Client

The Task Orchestrator tools should now be available in your MCP client.

## Your First Task

### Basic Task Breakdown

Ask your AI assistant to use the Task Orchestrator:

```
Use the task orchestrator to help me create a Python script that 
downloads weather data and sends email alerts for severe weather.
```

The orchestrator will:

1. **Initialize a session** in your current directory
2. **Break down the task** into manageable subtasks
3. **Assign specialists** (Architect, Implementer, Tester, etc.)
4. **Execute each subtask** with the appropriate specialist
5. **Save all artifacts** to `.task_orchestrator/` in your project

### What You Get

After execution, you'll have:

```
your-project/
├── .task_orchestrator/
│   ├── tasks.db           # All task history and decisions
│   ├── artifacts/         # Generated code and documents
│   │   ├── weather_client.py
│   │   ├── email_alerts.py
│   │   ├── tests/
│   │   └── README.md
│   └── sessions/          # Work session data
├── weather_monitor.py     # Final integrated solution
└── requirements.txt       # Dependencies
```

## Core Concepts

### Tasks and Subtasks

Every complex task is broken down hierarchically:

```
Main Task: "Build weather alert system"
├── Design the architecture
├── Implement weather data fetching
├── Create email alert system
├── Add error handling
├── Write tests
└── Create documentation
```

### Specialist Roles

Different specialists handle different aspects:

- **Architect**: System design and technology choices
- **Implementer**: Writing the actual code
- **Tester**: Creating comprehensive tests
- **Reviewer**: Code review and improvements
- **Documenter**: User and developer documentation

### Artifacts

Everything generated is saved as artifacts:

- Code files
- Test suites
- Documentation
- Design decisions
- Review comments

### Context Preservation

The system remembers everything:

```python
# Query previous decisions
"Show me all tasks related to error handling"

# Understand implementation choices  
"Why did we choose requests over urllib?"

# Review test coverage
"What edge cases did we test for?"
```

## Common Commands

### Initialize a New Session
```
Initialize a task orchestrator session for my project
```

### Plan a Complex Task
```
Plan the implementation of [your task description]
```

### Execute with Specific Specialist
```
Have the architect design a solution for [problem]
```

### Query Task History
```
Show me all completed tasks related to [topic]
```

### Generate Documentation
```
Create user documentation for the [feature] we just built
```

## Best Practices

### 1. Start with Clear Goals

```
❌ "Make a web scraper"
✅ "Create a web scraper for news articles that handles rate limiting, 
   saves to PostgreSQL, and can run on a schedule"
```

### 2. Let Specialists Do Their Jobs

Don't override specialist recommendations without good reason. They're designed to catch common issues.

### 3. Review Generated Artifacts

The orchestrator creates working code, but you should review and customize it for your specific needs.

### 4. Use Task History

Previous tasks inform future work. Reference earlier decisions when building related features.

## Troubleshooting

### Tools Not Showing Up

1. Check your MCP client configuration
2. Ensure Python is in your PATH
3. Verify installation: `python -m mcp_task_orchestrator.server`

### Database Errors

The orchestrator creates a SQLite database in `.task_orchestrator/`. If you see database errors:

1. Check write permissions in your project directory
2. Remove `.task_orchestrator/tasks.db` to start fresh

### Import Errors

Ensure you have Python 3.8+ and all dependencies:

```bash
pip install --upgrade mcp-task-orchestrator
```

## Next Steps

- Read the [Core Concepts](../users/guides/core-concepts.md) guide
- Explore [Example Workflows](../users/guides/intermediate/examples/)
- Learn about [Custom Roles](../users/guides/advanced/custom-roles.md)

## Getting Help

- Check the [Troubleshooting Guide](../users/troubleshooting/README.md)
- Review [Common Issues](../users/troubleshooting/common-issues/)
- Report bugs at our [GitHub repository](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)