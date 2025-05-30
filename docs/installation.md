# Installation Guide

## Quick Start

1. **Clone repository**

   ```bash
   git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```

2. **Run installer**

   ```bash
   python run_installer.py
   ```

3. **Restart MCP clients** (Claude Desktop, Cursor, Windsurf, VS Code)

4. **Verify**: Look for "task-orchestrator" in available tools

## Why run_installer.py?

The `run_installer.py` method is the recommended installation approach because it:

- **Resolves import path issues**: Handles Python module path configuration automatically
- **Improves compatibility**: Works reliably across different Python environments and operating systems  
- **Enhanced error handling**: Provides better error messages and recovery guidance
- **Version management**: Ensures correct MCP package versions are installed (1.9.0+)
- **Robust configuration**: Properly handles edge cases in client detection and setup

## Supported Clients

- **Claude Desktop** - `%APPDATA%\Claude\claude_desktop_config.json`
- **Cursor IDE** - `~/.cursor/mcp.json`
- **Windsurf** - `~/.codeium/windsurf/mcp_config.json`
- **VS Code (Cline)** - `~/.vscode/mcp.json`

## Advanced Options

```bash
# Specific clients only
python run_installer.py --clients claude-desktop

# Test detection
python test_detection.py

# Validate configurations  
python test_validation.py

# Clean obsolete files
python installer/cleanup.py
```

## What the Installer Does

1. ✅ Creates isolated virtual environment (`venv_mcp/`)
2. ✅ Installs all dependencies with correct versions (mcp>=1.9.0, psutil, etc.)
3. ✅ Detects installed MCP clients automatically with improved detection logic
4. ✅ Creates correct configuration for each client with robust path handling
5. ✅ Removes obsolete files from previous attempts
6. ✅ Validates installation integrity and resolves import conflicts
7. ✅ Provides detailed logging and error diagnostics

## Manual Configuration

If automatic installation fails, see manual configuration examples in each client's documentation.

## Troubleshooting

### Common Issues Resolved by run_installer.py

- **ImportError with relative imports**: Automatically handled by proper path configuration
- **MCP version conflicts**: Ensures correct package versions (mcp>=1.9.0)
- **Python environment issues**: Robust virtual environment setup and management

### General Troubleshooting

- **No clients detected**: Ensure clients are installed and run once
- **Permission errors**: Run as administrator/sudo if needed  
- **Module errors**: Delete `venv_mcp/` and reinstall with `python run_installer.py`
- **Configuration issues**: Check logs in project directory for detailed error information

### Advanced Diagnostics

```bash
# Comprehensive installation validation
python test_detection.py
python test_validation.py

# Clean install (if needed)
rm -rf venv_mcp/  # Linux/Mac
rmdir /s venv_mcp  # Windows
python run_installer.py
```

For detailed troubleshooting, see `TEST_REPORT.md`.