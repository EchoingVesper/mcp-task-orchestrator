# Installation Troubleshooting Guide

## Common Installation Issues

### 1. Permission Denied Errors

**Symptoms**: `PermissionError` or `Access denied` during installation

**Solutions**:
```bash
# Linux/macOS: Use appropriate permissions
sudo python -m mcp_task_orchestrator_cli.secure_installer_cli

# Windows: Run as Administrator
# Right-click Command Prompt → "Run as administrator"

# Alternative: Install to user directory
pip install --user mcp-task-orchestrator
```

### 2. Python Version Compatibility

**Symptoms**: `SyntaxError` or version-related import errors

**Check Python version**:
```bash
python --version
# Required: Python 3.9 or higher
```

**Solutions**:
```bash
# Use specific Python version
python3.11 -m pip install mcp-task-orchestrator
python3.11 -m mcp_task_orchestrator_cli.secure_installer_cli

# Update Python (recommended)
# Download from python.org or use system package manager
```

### 3. MCP Client Not Detected

**Symptoms**: "No supported MCP clients found" error

**Manual client specification**:
```bash
python -m mcp_task_orchestrator_cli.secure_installer_cli --clients claude-desktop,cursor
```

**Client detection troubleshooting**:
```bash
# Check client detection
python -m mcp_task_orchestrator_cli.cross_tool_compatibility --check

# Verify client configuration paths
python scripts/diagnostics/debug_mcp_connections.py
```

### 4. Configuration File Conflicts

**Symptoms**: Existing configuration conflicts or backup failures

**Resolution**:
```bash
# Force backup and reinstall
python -m mcp_task_orchestrator_cli.secure_installer_cli --force-backup

# Restore from backup if needed
python -m mcp_task_orchestrator_cli.validation_backup_system --restore
```

### 5. Network/Connectivity Issues

**Symptoms**: Download failures or timeout errors

**Solutions**:
```bash
# Use offline installation
pip install mcp-task-orchestrator --no-deps

# Install with timeout adjustment
pip install --timeout 300 mcp-task-orchestrator

# Use alternative index
pip install -i https://pypi.org/simple/ mcp-task-orchestrator
```

## Error Code Reference

### Installation Error Codes

- **E001**: Permission denied accessing configuration directory
- **E002**: Python version incompatibility (< 3.9)
- **E003**: MCP client not found or not supported
- **E004**: Configuration backup failure
- **E005**: Network connectivity issues
- **E006**: Corrupted installation package
- **E007**: Insufficient disk space
- **E008**: Conflicting package versions

### Resolution Commands by Error Code

```bash
# E001: Permission issues
sudo python -m mcp_task_orchestrator_cli.secure_installer_cli

# E002: Python version
python3.11 -m mcp_task_orchestrator_cli.secure_installer_cli

# E003: Client not found
python -m mcp_task_orchestrator_cli.secure_installer_cli --clients claude-desktop

# E004: Backup failure
python -m mcp_task_orchestrator_cli.secure_installer_cli --skip-backup

# E005: Network issues
pip install mcp-task-orchestrator --no-deps --offline

# E006: Corrupted package
pip uninstall mcp-task-orchestrator && pip install mcp-task-orchestrator

# E007: Disk space
df -h  # Check available space, clean up if needed

# E008: Package conflicts
pip install mcp-task-orchestrator --force-reinstall
```

## Platform-Specific Issues

### Windows

**PowerShell Execution Policy**:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy if needed (run as Administrator)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Path Issues**:
```cmd
# Add Python to PATH if not found
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"
```

### macOS

**Homebrew Python Conflicts**:
```bash
# Use system Python or specific version
/usr/bin/python3 -m pip install mcp-task-orchestrator

# Or use Homebrew Python consistently
/opt/homebrew/bin/python3 -m pip install mcp-task-orchestrator
```

**Security Settings**:
```bash
# If blocked by Gatekeeper
sudo spctl --master-disable
# Install, then re-enable
sudo spctl --master-enable
```

### Linux

**Package Manager Conflicts**:
```bash
# Use virtual environment
python3 -m venv mcp_venv
source mcp_venv/bin/activate
pip install mcp-task-orchestrator
```

**System Package Issues**:
```bash
# Install system dependencies
sudo apt-get install python3-dev python3-pip  # Ubuntu/Debian
sudo yum install python3-devel python3-pip    # RHEL/CentOS
```

## Diagnostic Commands

### Pre-Installation Checks

```bash
# System compatibility
python scripts/diagnostics/check_status.py

# MCP client detection
python -m mcp_task_orchestrator_cli.cross_tool_compatibility --scan

# Dependency validation
pip check mcp-task-orchestrator
```

### Post-Installation Validation

```bash
# Installation verification
python -c "import mcp_task_orchestrator; print('Success')"

# Server test
python -m mcp_task_orchestrator.server --test

# Client connectivity
python scripts/diagnostics/debug_mcp_connections.py
```

### Performance Diagnostics

```bash
# Memory usage check
python scripts/diagnostics/check_status.py --memory

# Installation speed benchmark
time python -m mcp_task_orchestrator_cli.secure_installer_cli --batch

# Configuration validation
python -m mcp_task_orchestrator_cli.validation_backup_system --validate
```

## Recovery Procedures

### Complete Reinstallation

```bash
# 1. Uninstall completely
python -m mcp_task_orchestrator_cli.secure_uninstaller_cli --force

# 2. Clean pip cache
pip cache purge

# 3. Fresh installation
pip install mcp-task-orchestrator
python -m mcp_task_orchestrator_cli.secure_installer_cli
```

### Configuration Reset

```bash
# Backup current configuration
python -m mcp_task_orchestrator_cli.validation_backup_system --backup

# Reset to defaults
python -m mcp_task_orchestrator_cli.secure_installer_cli --reset

# Restore if needed
python -m mcp_task_orchestrator_cli.validation_backup_system --restore latest
```

## Getting Help

### Self-Service Resources
- **User Guide**: `/docs/current/installation/user-guide.md`
- **Compatibility Matrix**: `/docs/current/installation/compatibility-matrix.md`
- **Security Features**: `/docs/current/installation/security-features.md`

### Diagnostic Information Collection
```bash
# Generate diagnostic report
python scripts/diagnostics/check_status.py --full-report > diagnostic_report.txt

# Include system information:
# - Python version
# - Operating system
# - MCP client versions
# - Error messages
# - Installation command used
```

### Emergency Rollback
```bash
# If installation causes issues, restore previous state
python -m mcp_task_orchestrator_cli.validation_backup_system --emergency-restore

# This will:
# - Restore all configuration backups
# - Remove installed components
# - Verify system integrity
```