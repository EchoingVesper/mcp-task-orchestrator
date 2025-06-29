# MCP Server Configuration Reference Guide

> **Authority**: Based on official MCP documentation, Python SDK, and working server implementations  
> **Purpose**: Definitive guide for configuring MCP servers, especially Python-based servers  
> **Focus**: Resolving Claude Desktop connection issues and environment setup

## Executive Summary

MCP (Model Context Protocol) servers require careful environment and configuration management. Key findings:

- **Virtual Environment**: Recommended but not strictly required
- **Python Path Resolution**: Critical for client connections
- **Configuration Format**: JSON-based with specific schema requirements
- **Environment Variables**: Limited inheritance, explicit configuration needed
- **Debugging Tools**: Official MCP Inspector available for validation

## 1. MCP Architecture Overview

### Client-Server Model
```
MCP Host (Claude Desktop) → MCP Client → MCP Server (Your Python Server)
```

- **1:1 Connections**: Each client maintains dedicated server connections
- **Limited Environment**: Servers inherit only USER, HOME, PATH by default
- **Absolute Paths Required**: Relative paths cause connection failures

## 2. Python Environment Best Practices

### Official Recommendations

Based on the Python SDK documentation:

#### Primary Method: Using `uv` (Universal Package Manager)
```bash
# Create project with uv (recommended)
uv init mcp-server-project
cd mcp-server-project
uv add "mcp[cli]"
```

#### Alternative Method: pip + Virtual Environment
```bash
# Traditional approach
python -m venv mcp-server-env
source mcp-server-env/bin/activate  # Linux/macOS
# OR
mcp-server-env\Scripts\activate     # Windows
pip install "mcp[cli]"
```

### Environment Isolation

**Virtual Environment Benefits:**
- Dependency isolation
- Reproducible environments
- Avoiding system Python conflicts
- Cross-platform consistency

**When Required:**
- Multi-server deployments
- Conflicting dependencies
- Production environments
- WSL/complex environments (like Claude Code)

## 3. Server Implementation Patterns

### Entry Point Configuration

Based on official server examples:

```python
# Standard MCP server structure
from mcp.server.fastmcp import FastMCP
import asyncio

mcp = FastMCP("MyServer")

@mcp.tool()
def my_tool(param: str) -> str:
    return f"Result: {param}"

def main():
    # CLI argument handling
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Configuration file")
    args = parser.parse_args()
    
    # Start server
    asyncio.run(mcp.run())

if __name__ == "__main__":
    main()
```

### Project Structure (pyproject.toml)
```toml
[project]
name = "mcp-server-myserver"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0.0"
]

[project.scripts]
mcp-server-myserver = "mcp_server_myserver:main"
```

## 4. Client Configuration

### Claude Desktop Configuration

**Correct Configuration Pattern:**
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": [
        "-m", 
        "mcp_task_orchestrator.server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/installation"
      }
    }
  }
}
```

**Critical Requirements:**
- Use absolute paths for `command`
- Use module execution (`-m`) instead of direct script execution
- Set environment variables explicitly
- Test Python path resolution

### Environment Variable Handling

**Limited Inheritance:**
- Servers inherit: USER, HOME, PATH
- Custom variables must be explicit

**Explicit Configuration:**
```json
{
  "mcpServers": {
    "myserver": {
      "command": "/full/path/to/python",
      "args": ["-m", "mypackage.server"],
      "env": {
        "PYTHONPATH": "/custom/path",
        "CONFIG_FILE": "/path/to/config.json",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 5. Python Path Resolution

### The Core Problem

**Issue**: Claude Desktop may use different Python than package installation

**Common Scenarios:**
- System Python vs User Python (Windows)
- Multiple Python versions installed
- Virtual environment vs global installation
- WSL vs Windows Python

### Detection Strategy

```python
def find_correct_python():
    """Find Python executable with required package installed."""
    import subprocess
    import sys
    
    candidates = [
        sys.executable,  # Current Python
        "python",        # System PATH
        "python3",       # Unix style
        "py -3",         # Windows Launcher
    ]
    
    # Windows-specific user paths
    if platform.system() == "Windows":
        user_paths = [
            f"{os.environ.get('USERPROFILE')}\\AppData\\Local\\Programs\\Python\\",
            f"{os.environ.get('LOCALAPPDATA')}\\Programs\\Python\\",
        ]
        
        for base_path in user_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    if item.startswith('Python'):
                        python_exe = os.path.join(base_path, item, 'python.exe')
                        if os.path.exists(python_exe):
                            candidates.append(python_exe)
    
    # Test each candidate
    for python_cmd in candidates:
        try:
            cmd_parts = python_cmd.split() if " " in python_cmd else [python_cmd]
            cmd_parts.extend(["-c", "import mcp_task_orchestrator; print('OK')"])
            
            result = subprocess.run(cmd_parts, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "OK" in result.stdout:
                return python_cmd
        except Exception:
            continue
    
    return sys.executable  # Fallback
```

## 6. Debugging and Validation

### MCP Inspector Usage

**Installation:**
```bash
# No installation required
npx @modelcontextprotocol/inspector
```

**Server Testing:**
```bash
# Test your server directly
npx @modelcontextprotocol/inspector python -m mcp_task_orchestrator.server

# With custom arguments
npx @modelcontextprotocol/inspector python -m myserver --config config.json
```

**What Inspector Validates:**
- Server connectivity
- Tool/resource availability
- Protocol compliance
- Error handling
- Environment setup

### Debugging Workflow

1. **Test with Inspector First**
   ```bash
   npx @modelcontextprotocol/inspector python -m mcp_task_orchestrator.server
   ```

2. **Validate Configuration**
   - Check JSON syntax
   - Verify absolute paths
   - Test Python executable
   - Confirm environment variables

3. **Check Claude Desktop Logs**
   - Look for ModuleNotFoundError
   - Check Python path usage
   - Verify environment inheritance

4. **Iterative Testing**
   - Make changes
   - Test with Inspector
   - Update client config
   - Restart Claude Desktop

## 7. Cross-Platform Considerations

### Windows Specific

**Python Launcher Recommended:**
```json
{
  "command": "py",
  "args": ["-3", "-m", "mcp_task_orchestrator.server"]
}
```

**User vs System Python:**
- Check `%USERPROFILE%\AppData\Local\Programs\Python\`
- Use Python Launcher (`py -3`) for user installs
- Avoid `C:\Program Files\Python*` paths in configs

### WSL/Linux

**Virtual Environment Paths:**
```bash
# Activate and get Python path
source venv/bin/activate
which python  # Use this path in config
```

**Configuration:**
```json
{
  "command": "/full/path/to/venv/bin/python",
  "args": ["-m", "mcp_task_orchestrator.server"]
}
```

### macOS

**Homebrew Python:**
```bash
# Common paths
/opt/homebrew/bin/python3
/usr/local/bin/python3
```

## 8. Installation Script Improvements

### Registry-Based Installer Enhancements

Based on research findings, our installer should:

#### 1. Python Detection Enhancement
```python
def _find_correct_python(self) -> str:
    """Enhanced Python detection using official patterns."""
    # Test current Python first
    if self._test_python_installation(sys.executable):
        return sys.executable
    
    # Use platform-specific detection
    if platform.system() == "Windows":
        return self._find_windows_python()
    else:
        return self._find_unix_python()

def _test_python_installation(self, python_path: str) -> bool:
    """Test if Python has our package installed."""
    try:
        cmd = [python_path, "-c", "import mcp_task_orchestrator; print(mcp_task_orchestrator.__file__)"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and "mcp_task_orchestrator" in result.stdout
    except Exception:
        return False
```

#### 2. Configuration Generation
```python
def create_claude_config(self, python_path: str) -> dict:
    """Create proper Claude Desktop configuration."""
    return {
        "mcpServers": {
            "task-orchestrator": {
                "command": python_path,
                "args": ["-m", "mcp_task_orchestrator.server"],
                "env": {
                    "PYTHONPATH": str(Path(mcp_task_orchestrator.__file__).parent.parent)
                }
            }
        }
    }
```

#### 3. Validation Integration
```python
def validate_configuration(self, config_path: Path) -> bool:
    """Validate configuration using MCP Inspector."""
    try:
        # Use MCP Inspector for validation
        cmd = ["npx", "@modelcontextprotocol/inspector", "--cli", 
               config["mcpServers"]["task-orchestrator"]["command"],
               *config["mcpServers"]["task-orchestrator"]["args"]]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception:
        return False
```

## 9. Troubleshooting Common Issues

### ModuleNotFoundError

**Cause**: Python path mismatch between config and installation

**Solution**:
1. Find correct Python: `python -c "import mcp_task_orchestrator; print('OK')"`
2. Update config with exact Python path
3. Add PYTHONPATH if needed

### Server Disconnected

**Cause**: Environment variable inheritance issues

**Solution**:
```json
{
  "env": {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "PYTHONPATH": "/path/to/package",
    "HOME": "/home/user"
  }
}
```

### Permission Denied

**Cause**: Executable permissions or paths

**Solution**:
1. Use absolute paths
2. Check executable permissions
3. Test command manually

## 10. Implementation Action Items

### Immediate Fixes for Our Installer

1. **Enhanced Python Detection**
   - Implement comprehensive Python discovery
   - Test each candidate with actual import
   - Prefer user installations over system

2. **Configuration Validation**
   - Integrate MCP Inspector testing
   - Validate configs before saving
   - Provide clear error messages

3. **Environment Explicit Setup**
   - Always set PYTHONPATH
   - Include required environment variables
   - Test environment inheritance

4. **Cross-Platform Robustness**
   - Platform-specific Python detection
   - Handle Windows Python Launcher
   - Support virtual environments

### Testing Protocol

1. **Test with Inspector**: `npx @modelcontextprotocol/inspector python -m mcp_task_orchestrator.server`
2. **Validate Config**: Check JSON syntax and paths
3. **Test Python Path**: Verify module import works
4. **Claude Desktop Test**: Full integration test

---

## Conclusion

The key to successful MCP server configuration is:

1. **Correct Python Path**: Use the Python where the package is installed
2. **Absolute Paths**: Never use relative paths in configs
3. **Explicit Environment**: Set required variables explicitly
4. **Validation**: Use MCP Inspector for testing
5. **Cross-Platform Awareness**: Handle platform-specific differences

This guide provides the foundation for fixing our Claude Desktop connection issues and creating robust installation scripts.