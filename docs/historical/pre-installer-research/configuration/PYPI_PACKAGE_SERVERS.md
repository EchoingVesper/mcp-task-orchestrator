# PyPI Package-Based MCP Servers

## Overview

Python Package Index (PyPI) hosts numerous MCP servers that can be installed via pip. This guide covers best practices for installing, configuring, and managing PyPI-based MCP servers.

## Installation Patterns

### 1. Global Installation

**When to use:**
- Single-user systems
- Development machines
- When virtual environments are not required

**Installation:**
```bash
pip install mcp-task-orchestrator
```

**Configuration:**
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

### 2. User Installation

**When to use:**
- Multi-user systems
- No admin privileges
- Personal installations

**Installation:**
```bash
pip install --user mcp-task-orchestrator
```

**Configuration (Windows):**
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "py",
      "args": ["-3", "-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

### 3. Virtual Environment (Recommended)

**When to use:**
- Production deployments
- Multiple Python projects
- Dependency isolation needed

**Setup:**
```bash
# Create virtual environment
python -m venv mcp_env

# Activate (Windows)
mcp_env\Scripts\activate

# Activate (Unix/macOS)
source mcp_env/bin/activate

# Install package
pip install mcp-task-orchestrator
```

**Configuration:**
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "/path/to/mcp_env/bin/python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

## Python Interpreter Path Handling

### Finding the Correct Python

**Windows:**
```bash
# Using Python Launcher
where py

# Finding specific Python
py -3 -c "import sys; print(sys.executable)"

# Finding pip's Python
pip -V  # Shows which Python pip is using
```

**Unix/macOS:**
```bash
# Which Python
which python3

# Python path
python3 -c "import sys; print(sys.executable)"

# Pip's Python
pip3 -V
```

### Platform-Specific Paths

**Windows User Installation:**
```
C:\Users\USERNAME\AppData\Local\Programs\Python\Python311\python.exe
```

**Windows System Installation:**
```
C:\Python311\python.exe
```

**macOS Homebrew:**
```
/opt/homebrew/bin/python3
```

**Linux System:**
```
/usr/bin/python3
```

**Virtual Environment:**
```
/path/to/venv/bin/python
```

## Module Execution Patterns

### Why Use `-m` Flag?

The `-m` flag tells Python to run a module as a script:

```bash
python -m module_name
```

**Benefits:**
1. Handles package imports correctly
2. Works regardless of current directory
3. Ensures proper `__name__` and `__package__`
4. Compatible with namespace packages

### Common Patterns

**Simple module:**
```json
{
  "args": ["-m", "mcp_server"]
}
```

**Submodule:**
```json
{
  "args": ["-m", "mcp_package.server"]
}
```

**With arguments:**
```json
{
  "args": ["-m", "mcp_package.server", "--port", "8080"]
}
```

## Dependency Management

### 1. Requirements File

**Create requirements.txt:**
```txt
mcp-task-orchestrator>=1.6.0
mcp>=0.2.0
```

**Install:**
```bash
pip install -r requirements.txt
```

### 2. Dependency Conflicts

**Check for conflicts:**
```bash
pip check
```

**Resolve conflicts:**
```bash
# Create fresh environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install mcp-server-package
```

### 3. Version Pinning

**Specific version:**
```bash
pip install mcp-task-orchestrator==1.6.0
```

**Version range:**
```bash
pip install "mcp-task-orchestrator>=1.6.0,<2.0.0"
```

## Virtual Environment Best Practices

### 1. Dedicated MCP Environment

```bash
# Create MCP-specific environment
python -m venv ~/.mcp_servers

# Install all MCP servers
~/.mcp_servers/bin/pip install mcp-task-orchestrator
~/.mcp_servers/bin/pip install mcp-filesystem
~/.mcp_servers/bin/pip install mcp-git
```

### 2. Configuration with venv

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "/home/user/.mcp_servers/bin/python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    },
    "filesystem": {
      "command": "/home/user/.mcp_servers/bin/python",
      "args": ["-m", "mcp_filesystem.server"]
    }
  }
}
```

### 3. Activation Not Required

MCP servers run as subprocesses, so virtual environment activation is not needed. Use the full path to the virtual environment's Python.

## Common PyPI MCP Servers

### Example Configurations

**1. mcp-task-orchestrator:**
```json
{
  "command": "python",
  "args": ["-m", "mcp_task_orchestrator.server"]
}
```

**2. supabase-mcp-server:**
```json
{
  "command": "python",
  "args": ["-m", "supabase_mcp_server"],
  "env": {
    "SUPABASE_URL": "your-url",
    "SUPABASE_KEY": "your-key"
  }
}
```

**3. mcp-server-aws:**
```json
{
  "command": "python",
  "args": ["-m", "mcp_server_aws"],
  "env": {
    "AWS_PROFILE": "default"
  }
}
```

## Troubleshooting

### 1. Module Not Found

**Problem:**
```
ModuleNotFoundError: No module named 'mcp_package'
```

**Solutions:**

a) Verify installation:
```bash
pip list | grep mcp-package
```

b) Check Python path:
```bash
python -c "import sys; print(sys.path)"
```

c) Ensure correct Python:
```json
{
  "command": "/exact/path/to/python"
}
```

### 2. Import Errors

**Problem:**
```
ImportError: cannot import name 'server' from 'mcp_package'
```

**Solutions:**

a) Check module structure:
```bash
python -c "import mcp_package; print(dir(mcp_package))"
```

b) Verify entry point:
```bash
pip show mcp-package | grep Entry
```

### 3. Permission Denied

**Problem:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

a) Use user installation:
```bash
pip install --user mcp-package
```

b) Use virtual environment:
```bash
python -m venv local_env
local_env/bin/pip install mcp-package
```

### 4. Version Conflicts

**Problem:**
```
ERROR: pip's dependency resolver found conflicts
```

**Solution:**
Create isolated environment:
```bash
python -m venv clean_env
clean_env/bin/pip install mcp-package
```

## Package Development Mode

### Installing in Development Mode

For local development:
```bash
cd /path/to/mcp-server-project
pip install -e .
```

**Configuration remains the same:**
```json
{
  "command": "python",
  "args": ["-m", "mcp_package.server"]
}
```

## Security Considerations

### 1. Package Verification

**Check package details:**
```bash
pip show mcp-package
```

**Verify on PyPI:**
- Visit https://pypi.org/project/package-name
- Check maintainer
- Review project links
- Look at download statistics

### 2. Isolated Environments

Always use virtual environments for:
- Unknown packages
- Testing new servers
- Production deployments

### 3. Minimal Permissions

Run MCP servers with minimal required permissions:
- File system access restrictions
- Network access limitations
- Environment variable controls

## Best Practices Summary

1. **Use virtual environments** for isolation
2. **Specify exact Python paths** in production
3. **Use `-m` flag** for module execution
4. **Pin versions** for stability
5. **Test installations** before configuring
6. **Document dependencies** clearly
7. **Regularly update** packages
8. **Monitor security advisories**