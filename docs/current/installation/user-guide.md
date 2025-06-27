# MCP Task Orchestrator - Installation Guide

## Overview

The MCP Task Orchestrator provides secure, automated installation across all supported MCP clients. The installer features zero-vulnerability design, cross-platform compatibility, and surgical precision installation that preserves existing configurations.

## Supported Platforms

- **Operating Systems**: Windows, macOS, Linux
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **MCP Clients**: Claude Desktop, Cursor, Windsurf, VS Code, Zed, Claude Code

## Installation Methods

### Method 1: Automated Secure Installer (Recommended)

The secure installer provides enterprise-grade safety and cross-tool compatibility:

```bash
# Install via pip
pip install mcp-task-orchestrator

# Run the secure installer
python -m mcp_task_orchestrator_cli.secure_installer_cli

# Follow the interactive prompts to select your MCP clients
```

### Method 2: Universal Installer

For batch installation across multiple clients:

```bash
# Run universal installer
python -m mcp_task_orchestrator_cli.universal_installer

# Select installation options:
# - Single client or multi-client installation
# - Automatic client detection
# - Configuration validation
```

### Method 3: PyPI Package Installation

Direct installation from PyPI:

```bash
# Latest stable version
pip install mcp-task-orchestrator

# Specific version
pip install mcp-task-orchestrator==1.7.1

# Development version
pip install --pre mcp-task-orchestrator
```

## Quick Start

### 1. Installation

```bash
pip install mcp-task-orchestrator
python -m mcp_task_orchestrator_cli.secure_installer_cli
```

### 2. Verification

```bash
# Test the installation
python -c "import mcp_task_orchestrator; print('Installation successful')"

# Start the server
python -m mcp_task_orchestrator.server
```

### 3. First Task

```python
# In your MCP client, test the connection
import mcp_task_orchestrator

# Initialize a new session
orchestrator_initialize_session()

# Create your first task
orchestrator_plan_task(
    description="Create a simple Python script",
    subtasks_json='[{"title": "Write hello world script", "description": "Create hello.py", "specialist_type": "implementer"}]'
)
```

## Installation Features

### Security Features
- **Zero vulnerabilities**: All 38 identified security issues resolved
- **Input validation**: Comprehensive sanitization of all user inputs
- **Permission checks**: Validates file and directory access permissions
- **Backup creation**: Automatic configuration backups before changes
- **Rollback capability**: Restore previous configurations on failure

### Cross-Platform Compatibility
- **Path handling**: Universal path resolution across platforms
- **Client detection**: Automatic MCP client discovery
- **Version validation**: Python and dependency version checking
- **Environment isolation**: Virtual environment support

### Performance Optimization
- **Fast installation**: < 5 seconds for single client
- **Multi-client efficiency**: < 15 seconds for all supported clients
- **Memory efficiency**: < 50MB memory usage during installation
- **Concurrent processing**: Parallel client configuration

## Installation Options

### Interactive Mode (Default)
```bash
python -m mcp_task_orchestrator_cli.secure_installer_cli
```

Provides:
- Client selection menu
- Configuration preview
- Confirmation prompts
- Progress indicators
- Error reporting

### Batch Mode
```bash
python -m mcp_task_orchestrator_cli.secure_installer_cli --batch --clients claude-desktop,cursor
```

Supports:
- Non-interactive installation
- Client specification via command line
- Automated CI/CD integration
- Silent installation mode

### Development Mode
```bash
python -m mcp_task_orchestrator_cli.secure_installer_cli --dev
```

Features:
- Development server configuration
- Debug logging enabled
- Hot reload support
- Enhanced error reporting

## Troubleshooting

### Common Installation Issues

#### Permission Errors
```bash
# Linux/macOS: Use sudo if needed
sudo python -m mcp_task_orchestrator_cli.secure_installer_cli

# Windows: Run as Administrator
# Right-click Command Prompt → Run as Administrator
```

#### Python Version Issues
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m mcp_task_orchestrator_cli.secure_installer_cli
```

#### Client Not Detected
```bash
# Manual client specification
python -m mcp_task_orchestrator_cli.secure_installer_cli --clients claude-desktop

# Verify client installation
python -m mcp_task_orchestrator_cli.cross_tool_compatibility --check
```

### Validation Commands

```bash
# Comprehensive validation
python -m mcp_task_orchestrator_cli.validation_backup_system --validate

# Client connectivity test
python scripts/diagnostics/debug_mcp_connections.py

# Performance benchmark
python scripts/diagnostics/check_status.py
```

## Next Steps

After installation:

1. **Test the connection**: Verify MCP client can communicate with the server
2. **Read the user guide**: `/docs/current/user-guide/getting-started.md`
3. **Try example workflows**: `/docs/current/user-guide/real-world-examples/`
4. **Configure integrations**: Set up with your development tools

## Support

- **Documentation**: `/docs/current/`
- **Troubleshooting**: `/docs/troubleshooting/`
- **Examples**: `/docs/current/user-guide/real-world-examples/`
- **API Reference**: `/docs/current/api/`

For additional support, see the troubleshooting guide or check the project's issue tracker.