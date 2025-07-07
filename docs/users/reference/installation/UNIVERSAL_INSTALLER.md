

# Universal MCP Task Orchestrator Installer

The Universal Installer is a comprehensive installation solution that automatically detects and configures MCP Task Orchestrator for all known MCP-capable environments.

#

# Supported MCP Clients

#

## ✅ Fully Supported

| Client | Windows | macOS | Linux | WSL | Workspace Support | Notes |
|--------|---------|--------|--------|-----|------------------|-------|
| **Claude Desktop** | ✅ | ✅ | ✅ | ✅ | ❌ | Requires restart |
| **Claude Code (CLI)** | ✅ | ✅ | ✅ | ✅ | ✅ | No restart needed |
| **Cursor IDE** | ✅ | ✅ | ✅ | ✅ | ✅ | No restart needed |
| **Windsurf** | ✅ | ✅ | ✅ | ✅ | ❌ | Access via MCP panel |
| **VS Code (GitHub Copilot)** | ✅ | ✅ | ✅ | ✅ | ✅ | Requires Copilot subscription |
| **Continue.dev** | ✅ | ✅ | ✅ | ✅ | ✅ | Extension-based |

#

## 🔄 Configuration Methods

- **File-based**: Direct JSON configuration file editing

- **CLI-based**: Command-line interface configuration (Claude Code)

- **UI-based**: In-application configuration panels

#

# Installation

#

## Quick Installation (Recommended)

#

### For Standard Python Environments

```bash

# Install from PyPI

pip install mcp-task-orchestrator

# Run universal setup

mcp-task-orchestrator-cli setup

```text

#

### For Externally Managed Environments (WSL, Ubuntu 23.04+, etc.)

If you get an "externally-managed-environment" error, use one of these methods:

**Option 1: Virtual Environment (Recommended)**

```text
bash

# Create and activate virtual environment

python -m venv mcp-orchestrator-env
source mcp-orchestrator-env/bin/activate  

# Linux/WSL/macOS

# OR

mcp-orchestrator-env\Scripts\activate     

# Windows

# Install and setup

pip install mcp-task-orchestrator
mcp-task-orchestrator-cli setup

```text
text

**Option 2: pipx (Isolated Installation)**

```text
bash

# Install pipx if not already installed

sudo apt install pipx  

# Ubuntu/Debian

# OR

brew install pipx       

# macOS

# OR

pip install --user pipx 

# Other systems

# Install and run

pipx install mcp-task-orchestrator
pipx run mcp-task-orchestrator-cli setup

```text
text

**Option 3: System Override (Not Recommended)**

```text
bash

# Only if you understand the risks

pip install --break-system-packages mcp-task-orchestrator
mcp-task-orchestrator-cli setup

```text
text

#

## Alternative Commands

```text
bash

# Use the dedicated universal installer

mcp-task-orchestrator-cli universal-setup

# Check dependencies first

mcp-task-orchestrator-cli check-deps

```text

#

# How It Works

#

## 1. Environment Detection

The installer automatically detects:

- **Operating System**: Windows, macOS, Linux, WSL

- **MCP Clients**: All installed and supported clients **in the current environment**

- **Running Processes**: Warns if clients need to be closed

- **Configuration Scope**: Global vs workspace-specific options

#

### Important: Cross-Environment Considerations

**WSL (Windows Subsystem for Linux)**:

- When running from WSL, only WSL-compatible clients are detected (Claude Code, VS Code extensions)

- Windows applications like Claude Desktop are **not configured from WSL** even if their config files are visible

- To configure Windows applications, run the installer from Windows PowerShell/Command Prompt

**Native Windows**:

- Detects and configures all Windows applications (Claude Desktop, Cursor, VS Code, etc.)

- Can also configure WSL-based tools if accessible

**macOS/Linux**:

- Detects and configures native applications for the respective platform

#

## 2. Dependency Verification

Checks for all required dependencies:

- `mcp` >= 1.9.0

- `pydantic` >= 2.0.0

- `jinja2` >= 3.1.0

- `pyyaml` >= 6.0.0 (imported as `yaml`)

- `aiofiles` >= 23.0.0

- `psutil` >= 5.9.0

- `filelock` >= 3.12.0

- `sqlalchemy` >= 2.0.0

- `alembic` >= 1.10.0

- `typer` >= 0.9.0

- `rich` >= 13.0.0

#

## 3. Server Module Location

Automatically finds the MCP Task Orchestrator server module using multiple detection methods:

1. Package installation location (PyPI install)

2. ImportLib module detection

3. Site-packages search

4. User site-packages search

5. Source code detection (development installs)

#

## 4. Client Configuration

For each detected client:

- **Creates backups** of existing configurations

- **Configures MCP server entry** with correct paths and arguments

- **Handles workspace vs global scope** based on client capabilities

- **Uses appropriate Python executable** for the environment

#

# Configuration Details

#

## Claude Desktop

**Configuration File Locations:**

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

- Linux: `~/.config/Claude/claude_desktop_config.json`

**Configuration Format:**

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}

```text
text

**Important Notes:**

- ⚠️ **Must restart Claude Desktop** after configuration

- Only supports global configuration (no workspace-specific)

#

## Claude Code (CLI)

**Configuration Method:** CLI commands (no direct file editing)

**Installer Commands Used:**

```text
bash

# Workspace scope (preferred)

claude mcp add-json --scope workspace --name task-orchestrator '{"command":"python","args":["-m","mcp_task_orchestrator.server"],"env":{}}'

# Global scope (fallback)

claude mcp add-json --scope user --name task-orchestrator '{"command":"python","args":["-m","mcp_task_orchestrator.server"],"env":{}}'

```text
text

**Important Notes:**

- ✅ No restart required - changes take effect immediately

- Supports both workspace and global scopes

- Uses Claude Code's built-in MCP management

#

## Cursor IDE

**Configuration File Locations:**

- Global: `~/.cursor/mcp.json`

- Workspace: `{workspace}/.cursor/mcp.json`

**Configuration Format:**

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}

```text
text

**Important Notes:**

- ✅ No restart required - use refresh button in MCP panel

- Supports both global and workspace configurations

- User can choose scope during installation

#

## Windsurf

**Configuration File Location:**

- All platforms: `~/.codeium/windsurf/mcp_config.json`

**Configuration Format:**

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}

```text
text

**Access Method:**

- CMD/Ctrl + Shift + P → "MCP Configuration Panel"

**Important Notes:**

- ✅ No restart required - use refresh button in MCP panel

- Global configuration only

#

## VS Code (GitHub Copilot)

**Configuration File Locations:**

- Global: Platform-specific `settings.json`

- Workspace: `{workspace}/.vscode/mcp.json`

**Workspace Configuration (Recommended):**

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}

```text
text

**Requirements:**

- GitHub Copilot subscription

- Agent Mode enabled in VS Code

**Important Notes:**

- ✅ No restart required - hot reload supported

- Workspace configuration preferred for MCP

#

## Continue.dev

**Configuration File Locations:**

- Global: `~/.continue/config.json`

- Workspace: `{workspace}/.continue/config.json`

**Configuration Format:**

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}

```text
text

**Important Notes:**

- ✅ No restart required

- Supports both global and workspace configurations

- Extension-based, works with VS Code and other editors

#

# Troubleshooting

#

## Common Issues

#

### 1. "No MCP clients detected"

**Cause:** No supported MCP clients are installed or configuration files don't exist yet.

**Solution:**

- Install at least one supported MCP client

- For new installations, try running the client once to create initial config files

#

### 2. "Missing dependencies: pyyaml"

**Cause:** Bug in dependency detection - PyYAML is installed but imported as `yaml`.

**Solution:**

- This is a known issue that doesn't affect functionality

- The universal installer includes a fix for this detection bug

#

### 3. "Failed to configure [Client]"

**Cause:** Client application is running and has locked the configuration file.

**Solution:**

- Close the MCP client application

- Run the installer again

- Some clients (Claude Desktop) require a restart anyway

#

### 4. "Permission denied" errors

**Cause:** Insufficient permissions to write configuration files.

**Solution:**

- Run installer with appropriate permissions

- Check file/directory ownership

- On Linux/macOS: May need to adjust file permissions

#

### 5. "Externally managed environment" error

**Cause:** Modern Python environments (WSL, Ubuntu 23.04+, some Docker containers) prevent direct pip installs to protect system packages.

**Solution:**
Use a virtual environment or pipx:

```text
bash

# Virtual environment method

python -m venv mcp-orchestrator-env
source mcp-orchestrator-env/bin/activate
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli setup

# OR pipx method

pipx install mcp-task-orchestrator
pipx run mcp-task-orchestrator-cli setup

```text
text

#

### 6. "Claude Desktop not detected in WSL"

**Cause:** This is intentional behavior - Claude Desktop runs in Windows, not WSL.

**Solution:**

- To configure Claude Desktop: Run the installer from Windows (PowerShell/Command Prompt)
  
```text
cmd
  pip install mcp-task-orchestrator
  mcp-task-orchestrator-cli setup
  
```text
text

- To configure WSL tools only: Run from WSL (current behavior is correct)

- For both environments: Run the installer once in each environment

#

## Verification

After installation, verify the configuration:

#

### Claude Code (Current Environment)

```text
bash
claude mcp list

```text

#

### Claude Desktop

1. Restart Claude Desktop

2. Check that "task-orchestrator" appears in available tools

3. Try using a Task Orchestrator tool

#

### Other Clients

1. Open the MCP configuration panel in the client

2. Verify "task-orchestrator" is listed

3. Check connection status (should show as connected)

#

# Advanced Usage

#

## Custom Python Path

If you need to specify a custom Python executable:

```text
bash

# Set environment variable

export PYTHON_PATH=/path/to/custom/python

# Or modify the configuration files manually after installation

```text

#

## Workspace-Specific Installation

For clients that support workspace configurations:

1. Navigate to your project directory

2. Run the installer from within the workspace

3. Choose "workspace scope" when prompted

#

## Multiple Workspaces

The installer can be run in each workspace directory to create workspace-specific configurations. This is particularly useful for:

- Different Python environments per project

- Project-specific Task Orchestrator configurations

- Isolated development environments

#

# Development and Testing

#

## Testing the Installer

```bash

# Test dependency detection

python -c "from mcp_task_orchestrator_cli.universal_installer import UniversalInstaller; UniversalInstaller().check_dependencies()"

# Test client detection

python -c "from mcp_task_orchestrator_cli.universal_installer import UniversalInstaller; UniversalInstaller().detect_clients()"

# Run dry-run (detection only)

mcp-task-orchestrator-cli universal-setup

```text

#

## Adding New Clients

To add support for a new MCP client:

1. Create a new configuration class inheriting from `MCPClientConfig`

2. Implement `detect()`, `configure()`, and optionally `check_running()` methods

3. Add the class to `UniversalInstaller.clients` list

4. Update this documentation

#

# Security Considerations

#

## Configuration Backups

The installer automatically creates timestamped backups of existing configuration files before making changes:

```text

original_config.json → original_config.backup.1672531200.json

```text

#

## Environment Variables

Sensitive information should use environment variables in the MCP configuration:

```text
json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {
        "API_KEY": "${API_KEY}",
        "SECRET_TOKEN": "${SECRET_TOKEN}"
      }
    }
  }
}
```text

#

## File Permissions

The installer respects existing file permissions and creates new files with appropriate restrictions:

- Configuration files: Read/write for user only

- Backup files: Same permissions as original

#

# Contributing

#

## Reporting Issues

When reporting installer issues, please include:

1. Operating system and version

2. Python version and installation method

3. Which MCP clients you have installed

4. Full error output from the installer

5. Relevant configuration file contents (with sensitive data removed)

#

## Testing New Environments

If you're using the installer in a new environment:

1. Test with the `universal-setup` command first

2. Verify all detected clients are configured correctly

3. Report any issues or missing client support

4. Consider contributing support for new clients

This universal installer ensures consistent, reliable installation across all supported MCP environments while handling the specific requirements and quirks of each client implementation.
