
# MCP Task Orchestrator - Quick Start Guide

Get up and running with AI-powered task orchestration in under 10 minutes.

## Overview

This quick start guide provides the fastest path to getting the MCP Task Orchestrator working with your MCP client. You'll install the package, configure your client, and run your first orchestrated task.

**Document Type**: Quick Start Guide  
**Target Audience**: Developers new to MCP Task Orchestrator  
**Prerequisites**: Python 3.8+, MCP-compatible client installed  
**Last Updated**: 2025-01-13  
**Estimated Time**: 5-10 minutes
## What This Does

Transforms Claude (or other MCP clients) into an intelligent project manager that breaks down complex tasks into specialist-driven workflows. Automatically detects your project workspace and saves files in the right locations.

**Example:** Ask Claude to *"Build a Python web scraper with testing and documentation"* → Get a structured plan with architect, implementer, and tester specialists working together, with all artifacts saved in your project directory.

## Step 1: Prerequisites Check

```bash
# Verify you have these installed:
python --version  # Should be 3.8+
node --version    # Should be 16+ (for some MCP clients)
```

## Step 2: One-Command Install

### From PyPI (Recommended)
```bash
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli setup
```

### From Source
```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python install.py
```

> **Installation Notice**: The installer automatically detects common MCP clients and configures them. Troubleshooting may be required for specific system configurations.

## Step 3: Restart Your MCP Client
- **Claude Desktop**: Restart the entire app
- **Cursor/VS Code**: Reload window (Ctrl+Shift+P → "Reload Window")
- **Windsurf**: Reload window
## Step 4: Verify It's Working

Open your MCP client and look for `task-orchestrator` in tools/servers. Try saying:
```
"Create a task to add a simple hello world function to this project"
```

You'll notice the orchestrator automatically:
- Detects your project workspace (Git root, package.json, etc.)
- Creates tasks associated with this specific project
- Saves any artifacts in appropriate project locations

## Step 5: Test Workspace Features (Recommended)

Try workspace detection:
```
"Check what workspace the orchestrator detected for this project"
```

This should show you the detected project root and explain why it chose that location.
## Troubleshooting

### "No MCP clients detected"
1. Install at least one supported client:
   - [Claude Desktop](https://claude.ai/download)
   - [Cursor](https://cursor.sh/)
   - [VS Code](https://code.visualstudio.com/) + [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Run the client once before installing
3. Re-run `python install.py`

### "Could not connect" or "Server failed to start"
1. **Restart your MCP client completely** (most common fix)
2. Check your configuration file was updated:
   - **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
   - **Cursor**: `.cursor/mcp.json` in your project or home directory
3. Verify paths are absolute (not relative):

   ```json
   {
     "mcpServers": {
       "task-orchestrator": {
         "command": "/full/path/to/python",  // ✅ Good
         "args": ["-m", "mcp_task_orchestrator.server"]
       }
     }
   }
   ```

### "Module not found" or Import Errors
1. Delete the virtual environment and reinstall:
   ```bash
   rm -rf venv_mcp      # Linux/Mac
   rmdir /s venv_mcp    # Windows
   ```
2. Then run the installer:
   ```bash
   python install.py
   ```

### Database/Maintenance Issues
1. **Database errors**: Delete `.task_orchestrator/` folder and restart
2. **Maintenance coordinator not responding**: Check if database was properly initialized
3. **Task persistence not working**: Verify `.task_orchestrator/database/` directory exists

### Windows-Specific Issues
1. Run Command Prompt as Administrator (not PowerShell)
2. Add Node.js to your PATH manually if needed
3. Use absolute paths in configuration

## What's Next

Once you have it working:

1. **Try a simple task**: `"Plan and implement a basic Python script with error handling"`
2. **Explore specialist roles**: Ask for an architect, implementer, or debugger perspective
3. **Test maintenance features**: `"Use maintenance coordinator to scan and optimize the system"`
4. **Check the status**: Use `orchestrator_get_status` to see task progress
5. **Read the full docs**: [Complete documentation](docs/) for advanced features including the [Maintenance Coordinator Guide](docs/users/guides/maintenance-coordinator-guide.md)

## Still Need Help

1. **Run diagnostics**: `python scripts/diagnostics/verify_tools.py`
2. **Check logs**: Look for `mcp-server-task-orchestrator.log` files
3. **GitHub Issues**: [Report a problem](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)

---

*This guide gets you started quickly. For comprehensive features, configuration options, and advanced usage, see the [full documentation](README.md).*
