# Migration Guide

## Upgrading from Previous Versions

If you previously installed MCP Task Orchestrator using the old methods, follow this guide to migrate to the unified installation system.

## Before You Start

**Backup your existing configurations** (optional but recommended):
- Claude Desktop: Copy `%APPDATA%\Claude\claude_desktop_config.json`
- Other clients: Copy relevant config files

## Migration Steps

### 1. Clean Up Old Installation
```bash
# This removes obsolete files automatically
python installer/cleanup.py
```

### 2. Run New Unified Installer  
```bash
python install.py
```

### 3. Verify Migration
```bash
python test_validation.py
```

## What Gets Cleaned Up

The migration automatically removes:
- `install_bundled.py` (obsolete embedded Python approach)
- `install_for_claude.py` (obsolete single-client installer)
- `bundled/` directory (failed embedded Python)
- `temp_calculator_project/` (test files)
- Other obsolete installation files

## What's New

- **🎯 Single Command**: One installer for all clients
- **🔍 Auto-Detection**: Finds installed clients automatically
- **🧹 Cleanup**: Removes obsolete files
- **🔧 Better Error Handling**: Improved validation and testing
- **📚 Better Documentation**: Comprehensive guides

## Troubleshooting Migration

**"Configuration conflicts"**
- The new installer merges with existing configs safely
- Your existing MCP servers remain unchanged

**"Virtual environment issues"**  
- Delete `venv_mcp/` directory and reinstall
- The new installer creates a fresh environment

**"Missing tools after migration"**
- Restart all MCP client applications
- Check that `task-orchestrator` appears in tools list

## Rollback (if needed)

If you need to rollback:
1. Restore backed-up configuration files
2. Delete `venv_mcp/` directory
3. Use your previous installation method

The migration is designed to be safe and reversible.
