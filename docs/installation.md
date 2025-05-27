# MCP Task Orchestrator - Installation Guide

This guide provides detailed instructions for installing and configuring the MCP Task Orchestrator on different platforms.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation Methods

There are several ways to install the MCP Task Orchestrator:

1. **Automated Installation Scripts** (Recommended)
2. **Manual Installation** using pip
3. **Development Installation** from source## Automated Installation (Recommended)

The automated installation scripts will:
- Install the MCP Task Orchestrator package
- Detect installed MCP clients
- Configure the clients to use the Task Orchestrator
- Validate the installation

### Windows

1. Open PowerShell as Administrator
2. Clone the repository:
   ```powershell
   git clone https://github.com/windsurf/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```
3. Run the installation script:
   ```powershell
   .\scripts\install.ps1
   ```
4. Follow the on-screen instructions

### macOS

1. Open Terminal
2. Clone the repository:
   ```bash
   git clone https://github.com/windsurf/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```
3. Make the installation script executable:
   ```bash
   chmod +x ./scripts/install.sh
   ```
4. Run the installation script:
   ```bash
   ./scripts/install.sh
   ```
5. Follow the on-screen instructions

### Linux

1. Open Terminal
2. Clone the repository:
   ```bash
   git clone https://github.com/windsurf/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```
3. Make the installation script executable:
   ```bash
   chmod +x ./scripts/install.sh
   ```
4. Run the installation script:
   ```bash
   ./scripts/install.sh
   ```
5. Follow the on-screen instructions## Manual Installation

If the automated installation scripts don't work for your environment, you can manually install and configure the MCP Task Orchestrator.

### Installing the Package

1. Clone the repository:
   ```bash
   git clone https://github.com/windsurf/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

### Configuring MCP Clients

After installing the package, you can use the CLI to configure your MCP clients:

```bash
# Configure all detected MCP clients
python -m mcp_task_orchestrator_cli.cli install <path_to_server.py>

# Configure specific clients
python -m mcp_task_orchestrator_cli.cli install <path_to_server.py> --client claude_desktop

# Force reconfiguration of already configured clients
python -m mcp_task_orchestrator_cli.cli install <path_to_server.py> --force
```

Replace `<path_to_server.py>` with the absolute path to the server.py file in your installation, for example:
```bash
python -m mcp_task_orchestrator_cli.cli install C:\Users\username\mcp-task-orchestrator\mcp_task_orchestrator\server.py
```

## Development Installation

For development purposes, you can install the package in development mode:

1. Clone the repository:
   ```bash
   git clone https://github.com/windsurf/mcp-task-orchestrator.git
   cd mcp-task-orchestrator
   ```

2. Install the package with development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Configure MCP clients:
   ```bash
   python -m mcp_task_orchestrator_cli.cli install <path_to_server.py>
   ```## Troubleshooting

If you encounter issues during installation or configuration, try these troubleshooting steps:

### Common Issues

#### Client Not Detected

If the installer doesn't detect your MCP client:

1. Verify the client is installed and has been run at least once
2. Check if the client's configuration file exists at the expected location
3. Try specifying the client explicitly:
   ```bash
   python -m mcp_task_orchestrator_cli.cli install <path_to_server.py> --client claude_desktop
   ```

#### Configuration Not Applied

If the configuration is not applied correctly:

1. Restart the MCP client completely
2. Check if the configuration file was modified:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`
3. Try forcing reconfiguration:
   ```bash
   python -m mcp_task_orchestrator_cli.cli install <path_to_server.py> --force
   ```

#### Server Not Starting

If the MCP server doesn't start:

1. Check if Python 3.8+ is installed and in your PATH
2. Verify all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Check for error messages in the client's console or logs

### Getting Help

If you continue to experience issues:

1. Check the [GitHub Issues](https://github.com/windsurf/mcp-task-orchestrator/issues) for similar problems
2. Create a new issue with detailed information about your problem
3. Include your operating system, Python version, and client information

## Updating

To update an existing installation:

```bash
# Pull the latest changes
git pull

# Update the package
pip install -e .

# Update client configurations
python -m mcp_task_orchestrator_cli.cli update <path_to_server.py>
```

## Uninstalling

To uninstall the MCP Task Orchestrator:

```bash
# Remove client configurations
python -m mcp_task_orchestrator_cli.cli uninstall --all

# Uninstall the package
pip uninstall mcp-task-orchestrator
```