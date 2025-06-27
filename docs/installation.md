# Installation Guide

## Quick Start

### Option 1: Install from PyPI (Recommended)

```bash
pip install mcp-task-orchestrator
python -m mcp_task_orchestrator_cli install
```

**Note**: The installer automatically detects your MCP clients and configures them with the optimal settings for multi-project use.

### Option 2: Install from Source

1. **Clone repository**

   ```bash
   git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```

2. **Install dependencies and run installer**

   ```bash
   pip install -e .
   python -m mcp_task_orchestrator_cli install
   ```

3. **Restart MCP clients** (Claude Desktop, Claude Code, Cursor, Windsurf)

4. **Verify Installation**: Follow the verification steps below

## CLI Installation Options

### Auto-detect Installation (Recommended)
```bash
python -m mcp_task_orchestrator_cli install
```
Automatically detects and configures all compatible MCP clients.

### Client-Specific Installation

**Claude Desktop (Global Multi-Project)**
```bash
python -m mcp_task_orchestrator_cli install --client claude_desktop
```
Installs globally, works across multiple projects using dynamic directory detection.

**Claude Code (Project-Specific)**
```bash
python -m mcp_task_orchestrator_cli install --client claude_code --scope project
```
Installs for the current project directory only. Run this command in each project where you want to use the orchestrator.

**Windsurf and Cursor (Project-Aware)**
```bash
python -m mcp_task_orchestrator_cli install --client windsurf,cursor
```
These clients automatically detect project context when opened in project folders.

**Multiple Clients**
```bash
python -m mcp_task_orchestrator_cli install --client claude_desktop,windsurf,cursor
```

### Advanced Options

**Set Default Working Directory**
```bash
python -m mcp_task_orchestrator_cli install --client claude_desktop --working-dir "/path/to/project"
```

**Force Reconfiguration**
```bash
python -m mcp_task_orchestrator_cli install --force
```

**Custom Server Name**
```bash
python -m mcp_task_orchestrator_cli install --name "my-orchestrator"
```

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

## Supported MCP Clients

| Client | Configuration | Multi-Project Support | Installation Method |
|--------|---------------|---------------------|-------------------|
| **Claude Desktop** | JSON config file | ✅ Dynamic detection | Global installation |
| **Claude Code** | CLI integration | ✅ Per-project | Project-specific installation |
| **Windsurf** | JSON config file | ✅ Built-in context | Global installation |
| **Cursor** | JSON config file | ✅ Built-in context | Global installation |
| **VS Code + Cline** | JSON config file | ⚠️ Limited | In development |

## Multi-Project Workflow

### Claude Desktop Approach (Recommended)
1. **Install once globally**: `python -m mcp_task_orchestrator_cli install --client claude_desktop`
2. **Works everywhere**: The orchestrator automatically detects your current project
3. **Project-specific data**: Each project gets its own `.task_orchestrator` directory
4. **Use anywhere**: Open Claude Desktop from any project directory

### Claude Code Approach (Per-Project)
1. **Install per project**: `cd /path/to/project && python -m mcp_task_orchestrator_cli install --client claude_code --scope project`
2. **Project isolation**: Each project has its own orchestrator configuration
3. **Fine-grained control**: Different projects can use different orchestrator versions
4. **No conflicts**: Projects don't interfere with each other

### How Project Detection Works
The orchestrator automatically detects your project directory using:
- **Git repositories** (`.git` directory detection)
- **Project markers** (`package.json`, `pyproject.toml`, `Cargo.toml`, etc.)
- **MCP client context** (working directory from your editor)
- **Explicit parameters** (`working_directory` in `orchestrator_initialize_session`)

Each project gets its own:
- Task database (`.task_orchestrator/task_orchestrator.db`)
- Artifact storage (`.task_orchestrator/artifacts/`)
- Custom role definitions (`.task_orchestrator/roles/project_roles.yaml`)

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

## Troubleshooting

### Common Installation Issues

**Claude Code not detected**
```bash
# Verify Claude Code CLI is available
claude --version

# If not found, install Claude Code first
# Then re-run the installer
python -m mcp_task_orchestrator_cli install --client claude_code
```

**Configuration file not found**
```bash
# Make sure your MCP client has been opened at least once
# to create the configuration directory, then re-run installer
python -m mcp_task_orchestrator_cli install --force
```

**Already configured warning**
```bash
# Use --force to overwrite existing configuration
python -m mcp_task_orchestrator_cli install --force
```

**Permission errors**
```bash
# Check file permissions for config directories
# On Windows: %APPDATA%\Claude\
# On macOS: ~/Library/Application Support/Claude/
# On Linux: ~/.config/Claude/
```

### Client-Specific Notes

**Claude Desktop**: 
- Installs globally, works across all projects automatically
- Uses dynamic directory detection for per-project task storage
- No hardcoded working directory - adapts to your current project

**Claude Code**: 
- Install per-project for best experience: `--scope project`
- Each project gets its own orchestrator configuration
- Must be run from within the project directory

**Windsurf/Cursor**: 
- Install globally, automatically detect project when opened in folders
- Built-in project context awareness
- No additional configuration needed per project

### Getting Help

**View installer options**
```bash
python -m mcp_task_orchestrator_cli install --help
```

**Check which clients are detected**
```bash
python -m mcp_task_orchestrator_cli install --no-auto-detect --client claude_desktop
```

**Debug installation issues**
Check the installer output for specific error messages and client detection results.

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
