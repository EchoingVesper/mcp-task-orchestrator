# MCP Task Orchestrator - Quick Start Guide

*Get up and running with AI-powered task orchestration in under 5 minutes*

## 🎯 What This Does

Transform Claude (or other MCP clients) into an intelligent project manager that breaks down complex tasks into specialist-driven workflows.

**Example:** Ask Claude to *"Build a Python web scraper with testing and documentation"* → Get a structured plan with architect, implementer, and tester specialists working together.

## ⚡ 30-Second Start

### Step 1: Prerequisites Check
```bash
# Verify you have these installed:
python --version  # Should be 3.8+
node --version    # Should be 16+
```

### Step 2: One-Command Install
```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python run_installer.py
```

> **Reliable Installation**: This optimized installer automatically detects your MCP clients and handles all configuration with improved error handling.

### Step 3: Restart Your MCP Client
- **Claude Desktop**: Restart the entire app
- **Cursor/VS Code**: Reload window (Ctrl+Shift+P → "Reload Window")

### Step 4: Verify It's Working
Open your MCP client and look for `task-orchestrator` in tools/servers. Try saying:
*"Initialize a new orchestration session"*

## 🔧 If Something Goes Wrong

### "No MCP clients detected"
1. Install at least one supported client:
   - [Claude Desktop](https://claude.ai/download)
   - [Cursor](https://cursor.sh/)
   - [VS Code](https://code.visualstudio.com/) + [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)

2. Run the client once before installing
3. Re-run `python run_installer.py`

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
   rm -rf venv_mcp  # Linux/Mac
   rmdir /s venv_mcp  # Windows
   python run_installer.py
   ```

### Windows-Specific Issues
1. Run Command Prompt as Administrator (not PowerShell)
2. Add Node.js to your PATH manually if needed
3. Use absolute paths in configuration

## 📚 What's Next?

Once you have it working:

1. **Try a simple task**: *"Plan and implement a basic Python script with error handling"*
2. **Explore specialist roles**: Ask for an architect, implementer, or debugger perspective
3. **Check the status**: Use `orchestrator_get_status` to see task progress
4. **Read the full docs**: [Complete documentation](docs/) for advanced features

## 🆘 Still Need Help?

1. **Run diagnostics**: `python scripts/diagnostics/verify_tools.py`
2. **Check logs**: Look for `mcp-server-task-orchestrator.log` files
3. **GitHub Issues**: [Report a problem](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)

---

*This guide gets you started quickly. For comprehensive features, configuration options, and advanced usage, see the [full documentation](README.md).*
