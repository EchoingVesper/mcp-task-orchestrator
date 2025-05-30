# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 1.3.0](https://img.shields.io/badge/version-1.3.0-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v1.3.0)

A Model Context Protocol server for task orchestration with specialized AI roles and automatic client configuration.

## 🎯 Overview

The MCP Task Orchestrator provides sophisticated task decomposition and specialized prompting for complex project management across multiple MCP-compatible clients.

## ✨ Key Features

- **LLM-Powered Task Breakdown**: Leverages the calling LLM's intelligence for flexible task decomposition
- **Unified Installation**: One-command setup for all supported MCP clients
- **Auto-Detection**: Automatically finds and configures installed clients  
- **Specialist Modes**: Role-specific prompts (Architect, Implementer, Debugger, Documenter, and more)
- **State Management**: Tracks task progress and dependencies
- **Task Persistence**: Prevents task loss during restarts or context resets
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

## 📦 Task Persistence

Version 1.3.0 introduces a robust task persistence mechanism to prevent task loss during restarts or context resets.

- **Automatic Saving**: Task state is automatically saved after every significant change
- **Seamless Recovery**: Interrupted tasks are automatically detected and can be resumed
- **Role Configuration**: Role files are stored in the `.task_orchestrator/roles/` directory
- **Concurrent Access**: File locking prevents data corruption during concurrent access

For more details, see [Task Persistence Documentation](docs/persistence.md).

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
├── docs/                       # Documentation
│   ├── development/           # Technical implementation guides
│   ├── testing/              # Test guides and reports
│   ├── troubleshooting/      # Diagnostic and issue resolution
│   ├── prompts/              # Context prompts
│   └── examples/             # Usage examples
├── tests/                    # Test suite
│   ├── integration/          # End-to-end workflow tests
│   ├── unit/                 # Component-level tests
│   ├── performance/          # Performance benchmarks
│   └── fixtures/             # Test utilities and helpers
├── scripts/                  # Utility scripts
│   ├── diagnostics/          # System diagnostic tools
│   ├── migrations/           # Data migration scripts
│   ├── maintenance/          # System maintenance utilities
│   └── deployment/           # Installation and deployment
├── data/                     # Database and data files
├── logs/                     # Log files (gitignored)
└── examples/                 # Usage examples and demos
```

## 🧪 Testing

The project includes a comprehensive test suite organized by purpose:

### Running Tests

```bash
# Activate virtual environment
source venv_mcp/bin/activate  # Linux/Mac
venv_mcp\Scripts\activate     # Windows

# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests  
python -m pytest tests/performance/ -v   # Performance benchmarks

# Run with coverage
python -m pytest tests/ --cov=mcp_task_orchestrator --cov-report=html
```

### Test Categories

- **Unit Tests** (`tests/unit/`) - Isolated component testing
- **Integration Tests** (`tests/integration/`) - Full workflow validation
- **Performance Tests** (`tests/performance/`) - Benchmarks and load testing
- **Test Fixtures** (`tests/fixtures/`) - Utilities and test helpers

For detailed testing information, see [`docs/testing/test-suite-guide.md`](docs/testing/test-suite-guide.md).

## 🔧 Development Tools

### Diagnostic Scripts

```bash
# System health check
python scripts/diagnostics/check_status.py

# Database analysis
python scripts/diagnostics/diagnose_db.py

# Server diagnostics
python scripts/diagnostics/diagnose_server.py

# Verify installation
python scripts/diagnostics/verify_tools.py
```

### Maintenance Utilities

```bash
# Run development server
python scripts/maintenance/simple_server.py

# Run with database optimization
python scripts/maintenance/run_with_db.py

# Performance-optimized server
python scripts/maintenance/run_optimized_server.py
```

For complete diagnostic guide, see [`docs/troubleshooting/diagnostic-tools.md`](docs/troubleshooting/diagnostic-tools.md).

## 📚 Documentation

### User Guides
- [`docs/installation.md`](docs/installation.md) - Detailed installation instructions
- [`docs/usage.md`](docs/usage.md) - Usage examples and workflows
- [`docs/configuration.md`](docs/configuration.md) - Configuration options

### Developer Documentation  
- [`docs/development/`](docs/development/) - Technical implementation details
- [`docs/testing/`](docs/testing/) - Testing guides and procedures
- [`docs/troubleshooting/`](docs/troubleshooting/) - Diagnostic and troubleshooting

### API Reference
- [`docs/DEVELOPER.md`](docs/DEVELOPER.md) - Developer API reference
- [`docs/database_persistence.md`](docs/database_persistence.md) - Database architecture

## 🔍 Troubleshooting

### Common Issues

#### Database Problems
```bash
# Check database health
python scripts/diagnostics/diagnose_db.py

# Clean up stale locks
python scripts/diagnostics/check_status.py --cleanup-locks
```

#### Performance Issues
```bash
# Run performance benchmark
python tests/performance/performance_benchmark.py

# Monitor system status
python scripts/diagnostics/check_status.py --monitor
```

#### Installation Problems
```bash
# Verify installation
python scripts/diagnostics/verify_tools.py

# Re-run installation
python scripts/deployment/install.py --force
```

For comprehensive troubleshooting, see [`docs/troubleshooting/`](docs/troubleshooting/).

## 🚀 Advanced Usage

### Custom Configurations
```bash
# Custom database location
export DB_PATH="/path/to/custom/database.db"

# Enable debug logging
export DEBUG=true

# Custom timeout settings
export TASK_TIMEOUT=300
```

### Performance Optimization
```bash
# Run optimized server
python scripts/maintenance/run_optimized_server.py

# Database optimization
python scripts/migrations/migrate_artifacts.py --optimize
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`  
3. **Test** your changes: `python -m pytest tests/ -v`
4. **Document** your changes in appropriate `docs/` files
5. **Commit** your changes: `git commit -m 'Add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## 🔗 Links

- **GitHub Repository**: [https://github.com/EchoingVesper/mcp-task-orchestrator](https://github.com/EchoingVesper/mcp-task-orchestrator)
- **Issue Tracker**: [https://github.com/EchoingVesper/mcp-task-orchestrator/issues](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
- **Documentation**: [`docs/`](docs/)
- **Release Notes**: [`RELEASE_NOTES.md`](RELEASE_NOTES.md)

---

🎯 **Ready to orchestrate complex tasks with AI-powered precision!**
