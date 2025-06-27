# MCP Server Configuration Best Practices

## Official Configuration Schema

### Basic Configuration Structure

The official MCP configuration follows this schema:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "string",  // Required - command to execute
      "args": ["array"],    // Required - arguments to pass
      "env": {}            // Optional - environment variables
    }
  }
}
```

### Required Fields

1. **command**: The executable to run
   - Always use absolute paths
   - For Python: `/path/to/python` or `py` (Windows)
   - For Node.js: `/path/to/node`

2. **args**: Array of command arguments
   - For Python modules: `["-m", "module.name"]`
   - For scripts: `["/path/to/script.py"]`
   - For Node.js: `["/path/to/index.js"]`

3. **env**: Optional environment variables
   - Only add when necessary
   - Inherits USER, HOME, PATH by default

## Python Package-Based Server Configuration

### Recommended Pattern

```json
{
  "mcpServers": {
    "my-python-server": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "mcp_package_name.server"]
    }
  }
}
```

### Platform-Specific Python Commands

**Windows:**
```json
{
  "command": "py",  // Python Launcher (recommended)
  "args": ["-3", "-m", "mcp_package_name.server"]
}
```

**macOS/Linux:**
```json
{
  "command": "/usr/bin/python3",
  "args": ["-m", "mcp_package_name.server"]
}
```

**Virtual Environment:**
```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "mcp_package_name.server"]
}
```

### Why Module Execution Pattern?

Using `python -m module.name` is preferred because:
- Ensures proper package imports
- Works regardless of current directory
- Handles namespace packages correctly
- Compatible with all installation methods

## PATH and Environment Variable Handling

### Default Environment Variables

MCP servers inherit only these variables by default:
- `USER` - Current username
- `HOME` - Home directory path
- `PATH` - System PATH

### When to Add Environment Variables

**Add environment variables only when:**
1. API keys or credentials needed
2. Custom configuration paths required
3. Special Python paths needed (rare)
4. Tool-specific settings

**Example with API key:**
```json
{
  "mcpServers": {
    "api-server": {
      "command": "python",
      "args": ["-m", "api_server"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### PATH Variable Best Practices

1. **Don't dump entire user PATH**
   - Avoid: `"PATH": "C:\\entire\\system\\path;..."`
   - Security risk and unnecessary

2. **Use absolute paths instead**
   - Better: `"command": "C:\\Python311\\python.exe"`
   - More reliable and secure

3. **Add to PATH only when necessary**
   ```json
   {
     "env": {
       "PATH": "${PATH};C:\\additional\\path"  // Note: Not all clients support ${PATH}
     }
   }
   ```

## Development vs Production Configurations

### Development Configuration

**Characteristics:**
- Can use relative paths (for testing)
- More verbose logging
- Debug environment variables
- Direct script execution

**Example:**
```json
{
  "mcpServers": {
    "dev-server": {
      "command": "python",
      "args": ["./src/server.py"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "debug"
      }
    }
  }
}
```

### Production Configuration

**Characteristics:**
- Always use absolute paths
- Minimal environment variables
- Module execution pattern
- Error handling configured

**Example:**
```json
{
  "mcpServers": {
    "prod-server": {
      "command": "/usr/bin/python3",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {
        "LOG_LEVEL": "warning"
      }
    }
  }
}
```

## Common Pitfalls and Solutions

### 1. Relative Path Issues

**Problem:**
```json
{
  "command": "python",
  "args": ["./server.py"]  // Fails if working directory changes
}
```

**Solution:**
```json
{
  "command": "/absolute/path/to/python",
  "args": ["-m", "package.server"]  // Always works
}
```

### 2. Python Not Found

**Problem:**
```json
{
  "command": "python",  // May not be in PATH
  "args": ["-m", "server"]
}
```

**Solution (Windows):**
```json
{
  "command": "py",  // Python Launcher always available
  "args": ["-3", "-m", "server"]
}
```

**Solution (Unix):**
```json
{
  "command": "/usr/bin/python3",  // Explicit path
  "args": ["-m", "server"]
}
```

### 3. Wrong Python Environment

**Problem:**
- Package installed in virtual environment
- Using system Python to run it

**Solution:**
```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "package.server"]
}
```

### 4. Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'package'
```

**Solutions:**

1. **Verify installation:**
   ```bash
   /path/to/python -m pip list | grep package-name
   ```

2. **Add PYTHONPATH if needed:**
   ```json
   {
     "env": {
       "PYTHONPATH": "/path/to/site-packages"
     }
   }
   ```

3. **Use correct Python:**
   ```json
   {
     "command": "/same/python/as/pip/install"
   }
   ```

### 5. Platform-Specific Paths

**Problem:**
```json
{
  "command": "C:\\Python\\python.exe"  // Windows-only path
}
```

**Solution - Use Python Launcher:**
```json
{
  "command": "py",  // Cross-platform on Windows
  "args": ["-3", "-m", "package"]
}
```

**Solution - Conditional Configuration:**
Some tools support platform detection, but this varies by client.

## Validation Best Practices

### 1. Test with MCP Inspector

```bash
npx @modelcontextprotocol/inspector /path/to/python -m package.server
```

### 2. Validate JSON Syntax

```bash
python -m json.tool config.json
```

### 3. Test Command Directly

```bash
# Test the exact command from configuration
/path/to/python -m package.server
```

### 4. Check Server Output

Ensure server outputs valid MCP protocol messages:
```json
Content-Length: 107

{"jsonrpc":"2.0","method":"initialized","params":{}}
```

## Configuration Organization

### Single Server

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

### Multiple Servers

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator.server"]
    },
    "file-server": {
      "command": "node",
      "args": ["/path/to/file-server/index.js"]
    },
    "database-server": {
      "command": "python",
      "args": ["-m", "mcp_database.server"],
      "env": {
        "DATABASE_URL": "postgresql://localhost/mydb"
      }
    }
  }
}
```

## Summary Checklist

- [ ] Use absolute paths for commands
- [ ] Use `-m` pattern for Python packages
- [ ] Minimal environment variables
- [ ] Validate with MCP Inspector
- [ ] Test command directly first
- [ ] Check correct Python environment
- [ ] Handle platform differences
- [ ] Document any special requirements