

# Installation Guide

#

# Prerequisites

#

## System Requirements

- Python 3.8 or higher

- Git (for installation)

- Claude Desktop, Cursor, Windsurf, or VS Code (MCP client)

#

## Environment Setup

Ensure you have a compatible MCP client installed:

- **Claude Desktop**: Download from [Claude.ai](https://claude.ai/download)

- **Cursor**: Download from [Cursor.sh](https://cursor.sh)

- **Windsurf**: Download from [Windsurf.ai](https://windsurf.ai)

- **VS Code**: Install MCP extension from marketplace

#

# Installation Methods

#

## Method 1: PyPI Installation (Recommended)

```bash

# Install from PyPI

pip install mcp-task-orchestrator

# Install with development tools

pip install mcp-task-orchestrator[dev]

```text

#

## Method 2: Development Installation

```text
bash

# Clone repository

git clone https://github.com/your-org/mcp-task-orchestrator.git
cd mcp-task-orchestrator

# Install in development mode

pip install -e ".[dev]"

```text

#

# MCP Client Configuration

#

## Claude Desktop Setup

1. Open Claude Desktop settings

2. Navigate to MCP servers configuration

3. Add MCP Task Orchestrator:

```text
json
{
  "mcp-task-orchestrator": {
    "command": "python",
    "args": ["-m", "mcp_task_orchestrator.server"],
    "env": {
      "MCP_TASK_ORCHESTRATOR_USE_DI": "true"
    }
  }
}

```text

#

## Cursor/Windsurf Setup

Add to your MCP configuration file:

```text
yaml
servers:
  mcp-task-orchestrator:
    command: python
    args: ["-m", "mcp_task_orchestrator.server"]
    env:
      MCP_TASK_ORCHESTRATOR_USE_DI: "true"

```text

#

## VS Code Setup

Install the MCP extension and configure the server in your workspace settings.

#

# Verification

#

## Test Installation

1. Restart your MCP client

2. Look for "mcp-task-orchestrator" in available tools

3. Try the health check:

```text
bash

# Command line verification

python -m mcp_task_orchestrator.tools.diagnostics.health_check
```text

#

## Expected Tools

You should see these MCP tools available:

- `orchestrator_initialize` - Start new orchestration

- `orchestrator_plan` - Create task breakdown

- `orchestrator_execute` - Run task execution

- `orchestrator_complete` - Finish task

- `orchestrator_synthesize` - Combine results

- `orchestrator_status` - Check progress

#

# Troubleshooting

#

## Common Issues

**Tools not appearing**: Restart MCP client after configuration changes

**Permission errors**: Ensure Python environment has write access

**Connection failures**: Check Python path and environment variables

**Database issues**: Verify write permissions in project directory

#

## Getting Help

- [Common Issues Guide](../troubleshooting/common-issues/installation-problems.md)

- [Diagnostic Tools](../troubleshooting/diagnostic-tools/health-checks.md)

- [Full Troubleshooting Guide](../troubleshooting/)

#

# Next Steps

- [First Task Tutorial](first-task.md) - Complete your first orchestration

- [Basic Configuration](../guides/basic/configuration.md) - Customize your setup
