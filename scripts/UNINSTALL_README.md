# MCP Task Orchestrator - Uninstall Guide

This directory contains comprehensive uninstall scripts to safely remove MCP Task Orchestrator from all MCP client configurations without affecting other servers.

## Quick Start

### Windows
```cmd
# Run the batch script
uninstall_orchestrator.bat

# Or run Python script directly
python uninstall_orchestrator.py
```

### Linux/macOS
```bash
# Run the shell script
./uninstall_orchestrator.sh

# Or run Python script directly
python3 uninstall_orchestrator.py
```

## Script Options

### Dry Run (Recommended First)
Test what would be removed without making changes:
```bash
python uninstall_orchestrator.py --dry-run
```

### Specific Clients Only
Remove from specific MCP clients only:
```bash
python uninstall_orchestrator.py --clients claude_desktop windsurf
```

### Custom Backup Location
Specify where to save configuration backups:
```bash
python uninstall_orchestrator.py --backup-dir /path/to/backups
```

### Quiet Mode
Minimize output (errors only):
```bash
python uninstall_orchestrator.py --quiet
```

## What the Scripts Do

### ✅ Safe Operations
- **Backup configurations** before making changes
- **Detect all MCP clients** (Claude Desktop, Windsurf, Cursor, VS Code)
- **Remove only orchestrator entries** from MCP server configurations
- **Preserve other MCP servers** and user settings
- **Cross-platform support** (Windows, macOS, Linux)
- **Detailed logging** with backup location information

### 🎯 Target Configurations
The scripts will remove MCP Task Orchestrator from these client configurations:

**Claude Desktop**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Windsurf**
- Windows: `%APPDATA%\Windsurf\User\globalStorage\windsurf-ai.windsurf\config.json`
- macOS: `~/Library/Application Support/Windsurf/User/globalStorage/windsurf-ai.windsurf/config.json`
- Linux: `~/.config/Windsurf/User/globalStorage/windsurf-ai.windsurf/config.json`

**Cursor**
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp-config.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/mcp-config.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp-config.json`

**VS Code**
- Windows: `%APPDATA%\Code\User\globalStorage\mcp-config.json`
- macOS: `~/Library/Application Support/Code/User/globalStorage/mcp-config.json`
- Linux: `~/.config/Code/User/globalStorage/mcp-config.json`

## Complete Uninstall Process

### 1. Run Uninstall Script
```bash
# Test first (recommended)
python uninstall_orchestrator.py --dry-run

# Actual uninstall
python uninstall_orchestrator.py
```

### 2. Exit Claude Code
**Important**: Exit Claude Code completely after running the uninstall script.

### 3. Restart MCP Clients
Restart any MCP clients that were configured:
- Claude Desktop
- Cursor
- Windsurf
- VS Code with Cline extension

### 4. Remove Python Package
```bash
pip uninstall mcp-task-orchestrator
```

## Recovery

### Restore Configurations
If needed, restore original configurations from backups:

```bash
# Backups are saved to ./mcp_config_backups/ by default
cp mcp_config_backups/claude_desktop_config_backup.json "path/to/claude/config.json"
```

### Reinstall Package
```bash
pip install mcp-task-orchestrator
# Then reconfigure with: mcp-task-orchestrator setup
```

## Troubleshooting

### Script Not Found
Ensure you're in the correct directory:
```bash
cd /path/to/mcp-task-orchestrator/scripts
```

### Permission Issues
On Unix systems, ensure script is executable:
```bash
chmod +x uninstall_orchestrator.sh
```

### Python Not Found
Ensure Python is installed and in PATH:
```bash
python --version
# or
python3 --version
```

### Configuration File Issues
If JSON files are corrupted, the script will skip them and log errors. Check the backup files for recovery.

## Script Features

### Detection Intelligence
- Identifies orchestrator servers by name patterns
- Checks command patterns and arguments
- Handles various naming conventions

### Safety Measures
- Creates backups before modification
- Validates JSON syntax before changes
- Preserves other MCP server configurations
- Provides detailed logging

### Cross-Platform Support
- Automatic platform detection
- Platform-specific configuration paths
- Universal Python script + platform helpers

## Support

If you encounter issues:

1. Check the log file: `uninstall_orchestrator.log`
2. Run with `--dry-run` first to see what would be changed
3. Verify backup files are created properly
4. Ensure you have proper permissions for config directories

The scripts are designed to be safe and non-destructive, always preserving your other MCP configurations.