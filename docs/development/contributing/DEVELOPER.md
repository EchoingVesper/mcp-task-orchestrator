# Developer Documentation

## Architecture Overview

The MCP Task Orchestrator consists of two main components:

1. **Unified Installation System**: A modular plugin architecture for client configuration
2. **Task Orchestration System**: An LLM-powered task breakdown and specialist coordination system

### Task Model Architecture (v2.0+)

The Generic Task Model provides a unified, flexible approach to task management:

```python
# Unified task model replaces TaskBreakdown + SubTask
from mcp_task_orchestrator.models import GenericTask, TaskDependency

# Create any type of task with flexible attributes
task = GenericTask(
    task_id="feature_123",
    task_type="feature_epic",
    attributes={
        "title": "User Authentication System",
        "priority": "high",
        "team": "backend",
        "estimated_effort": "3 weeks"
    }
)

# Add dependencies between tasks
dependency = TaskDependency(
    dependency_task_id="architecture_456", 
    dependency_type="completion",
    description="Architecture must be complete before implementation"
)
task.dependencies.append(dependency)
```

### Installation Architecture

The unified MCP Task Orchestrator uses a modular plugin architecture for client configuration:

```bash
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

## Task Orchestration Architecture

### Overview

The Task Orchestration system uses an LLM-powered approach to break down complex tasks into specialized subtasks. Instead of using pattern matching, it leverages the intelligence of the calling LLM to analyze tasks and create structured breakdowns.

```bash
mcp_task_orchestrator/
├── orchestrator/              # Core orchestration components
│   ├── __init__.py           # Package initialization
│   ├── core.py               # TaskOrchestrator class
│   ├── models.py             # Data models
│   ├── specialists.py        # Specialist management
│   └── state.py              # State persistence
├── server.py                 # MCP server implementation
└── config/                   # Configuration files
    ├── specialists.yaml      # Specialist definitions
    └── templates/            # Prompt templates
```

### Core Components

#### TaskOrchestrator

The `TaskOrchestrator` class manages the task breakdown and specialist coordination process:

```python
class TaskOrchestrator:
    async def initialize_session(self) -> Dict:  # Provides context to the LLM
    async def plan_task(self, description: str, complexity: str, subtasks_json: str, context: str = "") -> TaskBreakdown:  # Creates task breakdown from LLM-provided subtasks
    async def get_specialist_context(self, task_id: str) -> str:  # Gets specialist prompts
    async def complete_subtask(self, task_id: str, results: str, artifacts: List[str], next_action: str) -> Dict:  # Records results
    async def synthesize_results(self, parent_task_id: str) -> str:  # Combines results
```

#### StateManager

The `StateManager` class handles persistence of tasks, subtasks, and results using SQLite:

```python
class StateManager:
    async def store_task_breakdown(self, breakdown: TaskBreakdown):  # Stores task breakdown
    async def get_subtask(self, task_id: str) -> Optional[SubTask]:  # Retrieves subtask
    async def update_subtask(self, subtask: SubTask):  # Updates subtask
    async def get_subtasks_for_parent(self, parent_task_id: str) -> List[SubTask]:  # Gets all subtasks
```

#### SpecialistManager

The `SpecialistManager` class provides role-specific prompts and contexts:

```python
class SpecialistManager:
    async def get_specialist_prompt(self, specialist_type: SpecialistType, subtask: SubTask) -> str:  # Gets prompt
    async def synthesize_task_results(self, parent_task_id: str, completed_subtasks: List[SubTask]) -> str:  # Synthesizes
```

### Data Flow

1. **Initialization**: LLM calls `initialize_session` to get context about task orchestration
2. **Task Analysis**: LLM analyzes task and creates JSON-formatted subtasks
3. **Task Planning**: LLM calls `plan_task` with subtasks, which are stored in the database
4. **Subtask Execution**: For each subtask:
   - LLM calls `get_specialist_context` to get specialist prompt
   - LLM completes task in specialist mode
   - LLM calls `complete_subtask` to record results
5. **Result Synthesis**: LLM calls `synthesize_results` to combine all subtask results

### Adding New Specialist Types

1. Add new enum value to `SpecialistType` in models.py
2. Add specialist configuration to specialists.yaml
3. Create prompt template in config/templates/ (optional)

## MCP Server Implementation

The MCP server exposes the Task Orchestrator functionality through MCP tools:

- `orchestrator_initialize_session` - Initialize a new task orchestration session
- `orchestrator_plan_task` - Create a task breakdown from LLM-analyzed subtasks
- `orchestrator_execute_subtask` - Get specialist context for a subtask
- `orchestrator_complete_subtask` - Mark a subtask as complete
- `orchestrator_synthesize_results` - Combine completed subtasks into a final result
- `orchestrator_get_status` - Get current status of all tasks
