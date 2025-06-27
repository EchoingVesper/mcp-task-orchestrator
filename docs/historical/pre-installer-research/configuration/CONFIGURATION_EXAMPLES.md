# MCP Configuration Examples

## Real-World Working Configurations

### Task Orchestrator (PyPI Package)

**Claude Desktop (Windows):**
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

**Claude Desktop (macOS):**
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "/usr/bin/python3",
      "args": ["-m", "mcp_task_orchestrator.server"]
    }
  }
}
```

**Cursor Configuration:**
```json
{
  "task-orchestrator": {
    "command": "python",
    "args": ["-m", "mcp_task_orchestrator.server"]
  }
}
```

### Supabase MCP Server

**With Environment Variables:**
```json
{
  "mcpServers": {
    "supabase": {
      "command": "python",
      "args": ["-m", "supabase_mcp_server"],
      "env": {
        "SUPABASE_URL": "https://xxxxx.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      }
    }
  }
}
```

### File System Server (Node.js)

**Claude Desktop:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["/path/to/mcp-filesystem/index.js"],
      "env": {
        "ALLOWED_PATHS": "/home/user/documents,/home/user/projects"
      }
    }
  }
}
```

### GitHub MCP Server

**With API Token:**
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    }
  }
}
```

## Platform-Specific Examples

### Windows Examples

**System Python Installation:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "C:\\Python311\\python.exe",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

**User Python Installation:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "C:\\Users\\username\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

**Virtual Environment:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "C:\\projects\\mcp\\venv\\Scripts\\python.exe",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

### macOS Examples

**Homebrew Python:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "/opt/homebrew/bin/python3",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

**pyenv Python:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "/Users/username/.pyenv/versions/3.11.0/bin/python",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

### Linux Examples

**System Python:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "/usr/bin/python3",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

**Conda Environment:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "/home/user/miniconda3/envs/mcp/bin/python",
      "args": ["-m", "my_mcp_server"]
    }
  }
}
```

## Complex Server Configurations

### Server with Multiple Arguments

```json
{
  "mcpServers": {
    "advanced-server": {
      "command": "python",
      "args": [
        "-m", 
        "advanced_mcp_server",
        "--port", "8080",
        "--mode", "production",
        "--config", "/path/to/config.json"
      ],
      "env": {
        "LOG_LEVEL": "INFO",
        "CACHE_DIR": "/tmp/mcp_cache"
      }
    }
  }
}
```

### Multiple Servers Configuration

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "py",
      "args": ["-3", "-m", "mcp_task_orchestrator.server"]
    },
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "filesystem": {
      "command": "node",
      "args": ["/opt/mcp-servers/filesystem/index.js"],
      "env": {
        "ALLOWED_PATHS": "/home/user/documents"
      }
    },
    "database": {
      "command": "python",
      "args": ["-m", "mcp_database_server"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/db"
      }
    }
  }
}
```

## Development Configurations

### Local Development Server

```json
{
  "mcpServers": {
    "dev-server": {
      "command": "python",
      "args": ["/home/user/projects/my-mcp-server/src/server.py"],
      "env": {
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG",
        "RELOAD": "true"
      }
    }
  }
}
```

### Editable Installation

```json
{
  "mcpServers": {
    "editable-server": {
      "command": "/path/to/dev/venv/bin/python",
      "args": ["-m", "my_mcp_server.server"],
      "env": {
        "PYTHONPATH": "/path/to/my-mcp-server/src"
      }
    }
  }
}
```

## Debugging Configurations

### Verbose Logging

```json
{
  "mcpServers": {
    "debug-server": {
      "command": "python",
      "args": [
        "-m", 
        "my_mcp_server",
        "--verbose",
        "--log-file", "/tmp/mcp_debug.log"
      ],
      "env": {
        "MCP_DEBUG": "1",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### With Python Debugging

```json
{
  "mcpServers": {
    "debug-server": {
      "command": "python",
      "args": [
        "-m", 
        "pdb",
        "-m",
        "my_mcp_server"
      ]
    }
  }
}
```

## Special Use Cases

### WSL Configuration

**Windows Side (for Claude Desktop):**
```json
{
  "mcpServers": {
    "wsl-server": {
      "command": "wsl",
      "args": [
        "python3",
        "-m",
        "my_mcp_server"
      ]
    }
  }
}
```

### Docker-based Server

```json
{
  "mcpServers": {
    "docker-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "my-mcp-server:latest"
      ]
    }
  }
}
```

### Remote Server via SSH

```json
{
  "mcpServers": {
    "remote-server": {
      "command": "ssh",
      "args": [
        "user@remote-host",
        "python3 -m my_mcp_server"
      ]
    }
  }
}
```

## Troubleshooting Examples

### Testing Configuration

**Step 1: Test command directly**
```bash
# Windows
py -3 -m mcp_task_orchestrator.server

# macOS/Linux
python3 -m mcp_task_orchestrator.server
```

**Step 2: Use MCP Inspector**
```bash
npx @modelcontextprotocol/inspector python -m mcp_task_orchestrator.server
```

### Common Fixes

**Fix: Module not found**
```json
{
  "mcpServers": {
    "fixed-server": {
      "command": "/exact/path/to/correct/python",
      "args": ["-m", "package_name"],
      "env": {
        "PYTHONPATH": "/path/to/site-packages"
      }
    }
  }
}
```

**Fix: Permission denied**
```json
{
  "mcpServers": {
    "fixed-server": {
      "command": "python",
      "args": ["-m", "package_name"],
      "env": {
        "HOME": "/home/user",
        "TEMP": "/tmp"
      }
    }
  }
}
```

## Configuration Validation

### JSON Validation Script

```python
import json
import sys

def validate_mcp_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check for required fields
    for server_name, server_config in config.get('mcpServers', {}).items():
        if 'command' not in server_config:
            print(f"Error: {server_name} missing 'command'")
            return False
        if 'args' not in server_config:
            print(f"Error: {server_name} missing 'args'")
            return False
    
    print("Configuration valid!")
    return True

if __name__ == "__main__":
    validate_mcp_config(sys.argv[1])
```

### Testing Script

```bash
#!/bin/bash
# test_mcp_config.sh

CONFIG_FILE="$1"
SERVER_NAME="$2"

# Extract command and args from JSON
COMMAND=$(jq -r ".mcpServers.\"$SERVER_NAME\".command" "$CONFIG_FILE")
ARGS=$(jq -r ".mcpServers.\"$SERVER_NAME\".args[]" "$CONFIG_FILE")

# Test execution
echo "Testing: $COMMAND $ARGS"
$COMMAND $ARGS
```

## Best Practices Demonstrated

1. **Always use absolute paths** for reliability
2. **Specify Python version** explicitly
3. **Use module execution** (`-m`) for packages
4. **Keep environment variables** minimal
5. **Test configurations** before deployment
6. **Document special requirements**
7. **Use platform-appropriate** commands
8. **Handle errors gracefully**