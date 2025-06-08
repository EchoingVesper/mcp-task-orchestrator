# Installation Guide

## Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli setup
```

**Note**: The `setup` command automatically detects the server module location and configures all detected MCP clients. No manual path configuration needed!

### Option 2: Install from Source

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

4. **Verify Installation**: Follow the verification steps below

## Installation Methods Explained

### PyPI Installation (Recommended)
The `pip install` method is recommended for most users because it:
- **Simplified process**: Single command installation
- **Automatic dependencies**: All requirements handled by pip
- **Version management**: Easy updates with `pip install --upgrade`
- **Standard Python workflow**: Familiar to Python developers

### Source Installation (run_installer.py)

The `run_installer.py` method is the recommended installation approach because it:

- **Resolves import path issues**: Handles Python module path configuration automatically
- **Improves compatibility**: Works reliably across different Python environments and operating systems  
- **Enhanced error handling**: Provides better error messages and recovery guidance
- **Version management**: Ensures correct MCP package versions are installed (1.9.0+)
- **Database setup**: Automatically initializes the task persistence database
- **Maintenance system**: Sets up automated maintenance and cleanup capabilities
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
2. ✅ Installs all dependencies with correct versions (mcp>=1.9.0, psutil, SQLAlchemy, etc.)
3. ✅ Initializes SQLite database for task persistence (`.task_orchestrator/database/`)
4. ✅ Sets up maintenance coordinator and automated cleanup system
5. ✅ Detects installed MCP clients automatically with improved detection logic
6. ✅ Creates correct configuration for each client with robust path handling
7. ✅ Removes obsolete files from previous attempts
8. ✅ Validates installation integrity and resolves import conflicts
9. ✅ Provides detailed logging and error diagnostics

## Post-Installation Verification

### Step 1: Basic Tool Availability
In your MCP client, look for `task-orchestrator` in the available tools/servers list.

### Step 2: Test Core Functionality
Try this command in your MCP client:
```
"Initialize a new orchestration session"
```

Expected response should include:
- Session initialization confirmation
- Available specialist roles (architect, implementer, debugger, etc.)
- Tool usage instructions

### Step 3: Verify Database Setup
Check that the database was created:
```bash
# Should show database files
ls -la .task_orchestrator/database/
```

### Step 4: Test Maintenance Features
Try the maintenance coordinator:
```
"Use the maintenance coordinator to scan the current session"
```

Expected response should include:
- Scan results summary
- Task status analysis
- System health report

### Step 5: Verify Persistence
1. Create a simple task breakdown
2. Restart your MCP client
3. Check that task history is preserved

### Verification Checklist
- [ ] Tool appears in MCP client
- [ ] Session initialization works
- [ ] Database directory exists (`.task_orchestrator/database/`)
- [ ] Maintenance coordinator responds
- [ ] Task persistence across restarts
- [ ] All specialist roles available
- [ ] Artifact system functional

## Manual Configuration

If automatic installation fails, see manual configuration examples in each client's documentation.

## Troubleshooting

### Common Issues Resolved by run_installer.py

- **ImportError with relative imports**: Automatically handled by proper path configuration
- **MCP version conflicts**: Ensures correct package versions (mcp>=1.9.0)
- **Database initialization**: Automatically creates and migrates database schema
- **Maintenance system setup**: Configures automated cleanup and optimization
- **Python environment issues**: Robust virtual environment setup and management

### General Troubleshooting

- **No clients detected**: Ensure clients are installed and run once
- **Permission errors**: Run as administrator/sudo if needed  
- **Module errors**: Delete `venv_mcp/` and reinstall with `python run_installer.py`
- **Database errors**: Delete `.task_orchestrator/database/` and restart server to recreate
- **Maintenance coordinator not working**: Ensure database is properly initialized
- **Configuration issues**: Check logs in project directory for detailed error information

### Database-Specific Issues

- **SQLite errors**: Ensure sufficient disk space and write permissions
- **Database locked**: Close all MCP clients and restart
- **Migration errors**: Delete database directory and let system recreate it
- **Task persistence not working**: Check `.task_orchestrator/database/` directory exists

### Advanced Diagnostics

```bash
# Comprehensive installation validation
python test_detection.py
python test_validation.py

# Check database status
ls -la .task_orchestrator/database/
sqlite3 .task_orchestrator/database/tasks.db ".schema"

# Test maintenance features
python -c "from mcp_task_orchestrator.orchestrator.maintenance import MaintenanceCoordinator; print('Maintenance module OK')"

# Clean install (if needed)
rm -rf venv_mcp/  # Linux/Mac
rm -rf .task_orchestrator/  # Remove database
rmdir /s venv_mcp  # Windows
rmdir /s .task_orchestrator  # Windows
python run_installer.py
```

### New Features Verification

```bash
# Verify new automation features
python -c "
import sqlite3
conn = sqlite3.connect('.task_orchestrator/database/tasks.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
tables = cursor.fetchall()
print('Database tables:', [t[0] for t in tables])
conn.close()
"

# Test maintenance coordinator availability
# In your MCP client: 'Use maintenance coordinator to scan current session'
```

For detailed troubleshooting, see [Maintenance Operations Troubleshooting](./troubleshooting/maintenance-operations.md) and `TEST_REPORT.md`.
