# Developer Documentation

## Architecture Overview

The unified MCP Task Orchestrator uses a modular plugin architecture for client configuration:

```
installer/
├── __init__.py                 # Main package
├── main_installer.py           # UnifiedInstaller class
├── client_detector.py          # ClientDetector utility
├── cleanup.py                  # ProjectCleanup utility
└── clients/                    # Client implementations
    ├── base_client.py          # MCPClient interface
    ├── claude_client.py        # Claude Desktop
    ├── cursor_client.py        # Cursor IDE
    ├── windsurf_client.py      # Windsurf
    └── vscode_client.py        # VS Code (Cline)
```

## Core Classes

### MCPClient (Abstract Base)
```python
class MCPClient(ABC):
    @abstractmethod
    def detect_installation(self) -> bool
    @abstractmethod  
    def get_config_path(self) -> Path
    @abstractmethod
    def create_configuration(self) -> bool
```

### UnifiedInstaller
Main orchestrator that:
1. Ensures virtual environment exists
2. Installs dependencies
3. Detects available clients
4. Configures each detected client

### ClientDetector
Utility for:
- Auto-detecting installed MCP clients
- Providing detailed status information
- Managing client instances

## Client Configuration Formats

Each MCP client requires different configuration formats:

### Claude Desktop
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "path/to/python.exe",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "cwd": "path/to/project"
    }
  }
}
```

### Cursor IDE  
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "path/to/python.exe", 
      "args": ["-m", "mcp_task_orchestrator.server"],
      "env": {}
    }
  }
}
```

## Adding New Clients

1. Create new client class inheriting from `MCPClient`
2. Implement required methods
3. Add to `clients/__init__.py` registry
4. Test detection and configuration
