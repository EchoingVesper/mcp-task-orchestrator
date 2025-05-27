# Installation Guide

## Quick Start

1. **Clone repository**

   ```bash
   git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```

2. **Run installer**

   ```bash
   python install.py
   ```

3. **Restart MCP clients** (Claude Desktop, Cursor, Windsurf, VS Code)

4. **Verify**: Look for "task-orchestrator" in available tools

## Supported Clients

- **Claude Desktop** - `%APPDATA%\Claude\claude_desktop_config.json`
- **Cursor IDE** - `~/.cursor/mcp.json`
- **Windsurf** - `~/.codeium/windsurf/mcp_config.json`
- **VS Code (Cline)** - `~/.vscode/mcp.json`

## Advanced Options

```bash
# Specific clients only
python install.py --clients claude-desktop

# Test detection
python test_detection.py

# Validate configurations  
python test_validation.py

# Clean obsolete files
python installer/cleanup.py
```

## What the Installer Does

1. ✅ Creates isolated virtual environment (`venv_mcp/`)
2. ✅ Installs all dependencies (mcp, psutil, etc.)
3. ✅ Detects installed MCP clients automatically
4. ✅ Creates correct configuration for each client
5. ✅ Removes obsolete files from previous attempts

## Manual Configuration

If automatic installation fails, see manual configuration examples in each client's documentation.

## Troubleshooting

- **No clients detected**: Ensure clients are installed and run once
- **Permission errors**: Run as administrator/sudo if needed  
- **Module errors**: Delete `venv_mcp/` and reinstall

For detailed troubleshooting, see `TEST_REPORT.md`.
