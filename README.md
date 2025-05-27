# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 1.2](https://img.shields.io/badge/version-1.2-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v1.2)

A Model Context Protocol server for task orchestration with specialized AI roles and automatic client configuration.

## 🎯 Overview

The MCP Task Orchestrator provides sophisticated task decomposition and specialized prompting for complex project management across multiple MCP-compatible clients.

## ✨ Key Features

- **LLM-Powered Task Breakdown**: Leverages the calling LLM's intelligence for flexible task decomposition
- **Unified Installation**: One-command setup for all supported MCP clients
- **Auto-Detection**: Automatically finds and configures installed clients  
- **Customizable Specialist Roles**: Project-specific role definitions with automatic example file creation
- **Specialist Modes**: Role-specific prompts (Architect, Implementer, Debugger, Documenter, and more)
- **State Management**: Tracks task progress and dependencies
- **Single Session**: Works within one conversation - no multiple LLM instances

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- One or more supported MCP clients

### Supported Clients

- **Claude Desktop** - Anthropic's desktop application
- **Cursor IDE** - AI-powered code editor
- **Windsurf** - Codeium's development environment  
- **VS Code** - With Cline extension

### Installation

```bash
# Clone and install
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator

# One-command installation
python install.py
```

The installer automatically:
✅ Creates isolated virtual environment  
✅ Installs dependencies  
✅ Detects your MCP clients  
✅ Configures each client  
✅ Cleans up obsolete files

### After Installation

1. **Restart your MCP clients** (Claude Desktop, Cursor, etc.)
2. **Look for 'task-orchestrator'** in available tools/servers
3. **Start orchestrating!** Try: "Plan and implement a web scraper"

## 🛠️ Advanced Installation

### Specific Clients Only

```bash
python install.py --clients claude-desktop cursor-ide
```

### Verify Installation

```bash
python test_detection.py    # Check client detection
python test_validation.py   # Validate configurations  
```

### Manual Configuration

If you prefer manual setup, see `docs/MANUAL_INSTALLATION.md`

## 📋 How It Works

### LLM-Powered Task Orchestration

**Step 1:** Initialize the orchestration session to get guidance

```python
response = await call_tool("orchestrator_initialize_session", {})
```

**Step 2:** Analyze the task and create JSON-formatted subtasks

```python
subtasks_json = [
  {
    "title": "System Architecture Design",
    "description": "Design the web scraper architecture",
    "specialist_type": "architect",
    "dependencies": [],
    "estimated_effort": "30-45 minutes"
  },
  # Additional subtasks...
]
```

**Step 3:** Submit the task with your structured subtasks

```python
response = await call_tool("orchestrator_plan_task", {
    "description": "Create a Python web scraper for news articles",
    "subtasks_json": json.dumps(subtasks_json),
    "complexity_level": "moderate"
})
```

**Step 4:** Execute each subtask with specialist context

**Step 5:** Synthesize results into a comprehensive solution

Each specialist brings focused expertise while maintaining context across the entire project.

### Available Tools

- `orchestrator_initialize_session` - Initialize a new task orchestration session
- `orchestrator_plan_task` - Create a task breakdown from LLM-analyzed subtasks
- `orchestrator_execute_subtask` - Execute with specialist context
- `orchestrator_complete_subtask` - Mark tasks complete
- `orchestrator_synthesize_results` - Combine results
- `orchestrator_get_status` - Check progress

## 🔧 Configuration

The installer handles configuration automatically, but you can customize:

### Claude Desktop

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "path/to/venv/python.exe",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "cwd": "path/to/project"
    }
  }
}
```

### Other Clients

Each client has slightly different configuration formats. The installer handles these differences automatically.

## 🆘 Troubleshooting

### Common Issues

#### "No MCP clients detected"

- Ensure Claude Desktop, Cursor, Windsurf, or VS Code is installed
- Try running clients once before installation

#### "Configuration failed"  

- Check file permissions in config directories
- Run installer as administrator if needed

#### "Module not found errors"

- Virtual environment may be corrupted
- Delete `venv_mcp` folder and reinstall

### Getting Help

1. Check `TEST_REPORT.md` for known issues
2. Run diagnostic scripts in project root
3. Open an issue with log output

## 🤝 Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines.

## 📄 License

MIT License - Copyright (c) 2025 Echoing Vesper - see `LICENSE` file for details.

## 🙏 Acknowledgments

- Built for the Model Context Protocol ecosystem
- Inspired by advanced orchestration patterns
- Designed for single-session efficiency

---

**Ready to orchestrate?** `python install.py` and start building!
