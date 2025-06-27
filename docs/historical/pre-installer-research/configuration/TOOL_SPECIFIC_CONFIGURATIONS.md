# Tool-Specific MCP Configuration Guide

## Overview

Different AI coding tools implement MCP support with varying configuration requirements. This guide provides specific configuration instructions for each major tool.

## Claude Desktop

### Platform Configuration Locations

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Configuration Example

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "py",
      "args": ["-3", "-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

### Special Considerations

- Supports full MCP protocol
- Handles server lifecycle automatically
- Shows hammer icon when MCP servers connected
- Restart required after configuration changes

## Claude Code

### Configuration

Claude Code uses the same configuration as Claude Desktop:
- **WSL**: Uses Windows Claude Desktop config
- **Native Linux**: Uses Linux config location

### WSL-Specific Notes

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python3",  // WSL Python
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

**Important for WSL:**
- Python paths differ between Windows and WSL
- Use WSL Python for WSL-installed packages
- Windows Python for Windows-installed packages

## Cursor IDE

### Configuration Location

1. Open Cursor Settings
2. Navigate to MCP section
3. Click "Add new global MCP server"
4. Paste configuration

### Configuration Format

```json
{
  "task-orchestrator": {
    "command": "python",
    "args": ["-m", "mcp_task_orchestrator.server"]
  }
}
```

**Note:** Cursor expects server configuration without the outer `mcpServers` wrapper.

### Cursor-Specific Features

- Simpler configuration interface
- Global MCP servers available across projects
- Automatic server restart on configuration change
- Built-in MCP server management UI

## Windsurf IDE

### Configuration Process

1. Open Windsurf Settings
2. Find MCP configuration section
3. Add MCP server configuration
4. Save and restart

### Configuration Example

```json
{
  "task-orchestrator": {
    "command": "python",
    "args": ["-m", "mcp_task_orchestrator.server"]
  }
}
```

### Windsurf Considerations

- Similar to Cursor configuration
- Prefers minimal environment setup
- Good cross-platform support
- Handles server lifecycle well

## GitHub Copilot (VS Code)

### Requirements

- VS Code version 1.99 or later
- GitHub Copilot extension
- MCP support is in preview

### Configuration Steps

1. Open VS Code Settings (JSON)
2. Add MCP configuration under GitHub Copilot settings

### Example Configuration

```json
{
  "github.copilot.mcp.servers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}
```

### Limitations

- Preview feature (as of 2025)
- Limited to Agent Mode
- Not all MCP features supported yet
- May require additional VS Code configuration

## Roo Code

### Status

- Limited MCP support information available
- Configuration method unclear
- Check Roo Code documentation for updates

### Potential Configuration

If supported, likely follows similar pattern:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["-m", "package.server"]
    }
  }
}
```

## Cline

### Status

- MCP support status unclear
- May support through VS Code integration
- Check Cline documentation for current status

### Potential Configuration

If using VS Code integration, would follow VS Code MCP patterns.

## Platform-Specific Considerations

### Windows

**Python Command Options:**
```json
// Option 1: Python Launcher (recommended)
{
  "command": "py",
  "args": ["-3", "-m", "package"]
}

// Option 2: Full path
{
  "command": "C:\\Python311\\python.exe",
  "args": ["-m", "package"]
}

// Option 3: If Python in PATH
{
  "command": "python",
  "args": ["-m", "package"]
}
```

### macOS

**Python Command Options:**
```json
// Option 1: System Python 3
{
  "command": "/usr/bin/python3",
  "args": ["-m", "package"]
}

// Option 2: Homebrew Python
{
  "command": "/opt/homebrew/bin/python3",
  "args": ["-m", "package"]
}

// Option 3: Virtual environment
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "package"]
}
```

### Linux

**Python Command Options:**
```json
// Option 1: System Python
{
  "command": "/usr/bin/python3",
  "args": ["-m", "package"]
}

// Option 2: Virtual environment
{
  "command": "/home/user/venv/bin/python",
  "args": ["-m", "package"]
}
```

## Multi-Tool Configuration Strategy

### Approach 1: Tool-Specific Configurations

Maintain separate configurations for each tool:
- `claude_config.json`
- `cursor_config.json`
- `windsurf_config.json`

### Approach 2: Universal Installer

Use an installer script that:
1. Detects installed tools
2. Finds correct config locations
3. Applies appropriate configuration
4. Validates installation

### Approach 3: Registry-Based System

Centralized configuration that:
1. Maintains tool registry
2. Auto-detects Python environments
3. Generates tool-specific configs
4. Handles updates gracefully

## Configuration Testing

### 1. Direct Command Test

```bash
# Test the exact command from config
python -m mcp_task_orchestrator.server
```

### 2. MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m mcp_task_orchestrator.server
```

### 3. Tool-Specific Validation

- **Claude Desktop**: Look for hammer icon
- **Cursor/Windsurf**: Check MCP panel in settings
- **VS Code**: Check GitHub Copilot output panel

## Troubleshooting by Tool

### Claude Desktop Issues

1. **Server not appearing**
   - Check config file location
   - Validate JSON syntax
   - Restart Claude Desktop

2. **Server crashes**
   - Check Python path
   - Verify package installation
   - Check error logs

### Cursor/Windsurf Issues

1. **Configuration not saving**
   - Use settings UI properly
   - Check for syntax errors
   - Ensure proper permissions

2. **Server not starting**
   - Validate Python command
   - Check package installation
   - Review console output

### VS Code/GitHub Copilot Issues

1. **MCP not available**
   - Update VS Code to 1.99+
   - Update GitHub Copilot extension
   - Enable preview features

2. **Server connection fails**
   - Check VS Code settings
   - Validate configuration format
   - Review extension logs

## Best Practices Summary

1. **Use absolute paths** where possible
2. **Test commands directly** before configuring
3. **Keep configurations minimal**
4. **Document Python environments** used
5. **Validate with MCP Inspector**
6. **Check tool-specific documentation** for updates
7. **Maintain consistent naming** across tools
8. **Use platform-appropriate Python commands**