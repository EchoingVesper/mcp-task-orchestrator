# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 1.3.1](https://img.shields.io/badge/version-1.3.1-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v1.3.1)

A Model Context Protocol server that breaks down complex tasks into structured workflows with specialized AI roles. Works with Claude Desktop, Cursor IDE, Windsurf, and VS Code.

## What it does - Input to Output Example

**Instead of this:**
```
User: "Build a Python web scraper for news articles"
Claude: [Provides a single, monolithic response with basic code]
```

**You get this structured workflow:**
```
User: "Build a Python web scraper for news articles"

Step 1: Architect Role
├── System design with rate limiting and error handling
├── Technology selection (requests vs scrapy)  
├── Data structure planning
└── Scalability considerations

Step 2: Implementer Role  
├── Core scraping logic implementation
├── Error handling and retries
├── Data parsing and cleaning
└── Configuration management

Step 3: Tester Role
├── Unit tests for core functions
├── Integration tests with live sites
├── Error condition testing
└── Performance validation

Step 4: Documenter Role
├── Usage documentation
├── API reference
├── Configuration guide
└── Troubleshooting guide

Final Result: Complete, production-ready web scraper with:
✓ Robust error handling
✓ Comprehensive test suite  
✓ Full documentation
✓ Best practices implementation
```

Each step provides specialist context and expertise rather than generic responses.

## Key Features

- **LLM-powered task decomposition**: Automatically breaks complex projects into logical subtasks
- **Specialist AI roles**: Architect, Implementer, Debugger, Documenter with domain-specific expertise
  - **Customizeable roles**: Change the roles to better suit your own project
- **Universal MCP compatibility**: Works across Claude Desktop, Cursor, Windsurf, VS Code + Cline
- **Task persistence**: Recovers interrupted workflows automatically
- **Single-session completion**: Finish complex projects in one conversation

## Quick Start

### Prerequisites

- Python 3.8+ 
- One or more MCP clients (Claude Desktop, Cursor IDE, Windsurf, or VS Code with Cline extension)

### Installation

```bash
# Clone and install
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python run_installer.py

# Restart your MCP client
# Look for 'task-orchestrator' in available tools
```

The installer automatically detects your MCP clients and configures them appropriately.

### Verification

Try this in your MCP client:
```
"Initialize a new orchestration session and plan a Python script for processing CSV files"
```

## How It Works

The orchestrator uses a five-step process:

1. **Session Initialization** - Sets up the orchestration environment
2. **Task Analysis** - LLM analyzes your request and creates structured subtasks  
3. **Task Planning** - Organizes subtasks with dependencies and complexity assessment
4. **Specialist Execution** - Each subtask runs with role-specific context and expertise
5. **Result Synthesis** - Combines outputs into a comprehensive solution

### Available Tools

| Tool | Purpose |
|------|---------|
| `orchestrator_initialize_session` | Start new workflow |
| `orchestrator_plan_task` | Create task breakdown |
| `orchestrator_execute_subtask` | Execute with specialist context |
| `orchestrator_complete_subtask` | Mark tasks complete |
| `orchestrator_synthesize_results` | Combine results |
| `orchestrator_get_status` | Check progress |

## Supported Environments

| Client | Description | Status |
|--------|-------------|---------|
| **Claude Desktop** | Anthropic's desktop application | ✅ Supported |
| **Cursor IDE** | AI-powered code editor | ✅ Supported |
| **Windsurf** | Codeium's development environment | ✅ Supported |
| **VS Code** | With Cline extension | ✅ Supported |

## Task Persistence

Version 1.3.0 includes task persistence to handle workflow interruptions:

- **Automatic state saving** after significant changes
- **Crash recovery** for interrupted workflows  
- **Context preservation** across sessions
- **Dependency tracking** for complex task relationships

Task state is stored locally in `.task_orchestrator/` directory.

## Common Use Cases

### Software Development
- Full-stack web applications
- API development with testing
- Database schema design
- DevOps pipeline setup

### Data Science  
- Machine learning pipelines
- Data analysis workflows
- Research project planning
- Model deployment strategies

### Documentation & Content
- Technical documentation
- Code review and refactoring
- Testing strategy development
- Content creation workflows

## Configuration

The installer handles configuration automatically. For manual setup or customization, see [`docs/MANUAL_INSTALLATION.md`](docs/MANUAL_INSTALLATION.md).

### Custom Specialist Roles

Create project-specific specialists by adding YAML files to `.task_orchestrator/roles/`:

```yaml
name: "Security Auditor"
description: "Security analysis and vulnerability assessment"
expertise:
  - "OWASP security standards"
  - "Penetration testing methodologies"
  - "Secure coding practices"
prompts:
  - "Focus on security implications"
  - "Identify potential vulnerabilities"
  - "Ensure compliance with security standards"
```

## Troubleshooting

### Common Issues

**"No MCP clients detected"**
- Ensure at least one supported client is installed
- Run the client once before installation
- Check installation paths and permissions

**"Configuration failed"**
- Verify file permissions in configuration directories
- Try running installer as administrator/sudo
- Check for conflicting MCP server configurations

**"Module not found errors"**
- Delete `venv_mcp` folder and reinstall
- Ensure Python 3.8+ is accessible
- Check virtual environment integrity

### Diagnostic Tools

```bash
# System health check
python scripts/diagnostics/check_status.py

# Database optimization  
python scripts/diagnostics/diagnose_db.py

# Installation verification
python scripts/diagnostics/verify_tools.py
```

For comprehensive troubleshooting, see [`docs/troubleshooting/`](docs/troubleshooting/).

## Project Structure

```
mcp-task-orchestrator/
├── docs/                      # Documentation
├── tests/                     # Test suite
├── scripts/                   # Utilities and diagnostics
├── mcp_task_orchestrator/     # Core application
├── data/                      # Database files
└── examples/                  # Usage examples
```

## Testing

```bash
# Activate environment
source venv_mcp/bin/activate  # Linux/Mac
venv_mcp\Scripts\activate     # Windows

# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=mcp_task_orchestrator --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Update documentation as needed
5. Submit a pull request

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed guidelines.

## Documentation

- [`docs/installation.md`](docs/installation.md) - Installation and setup
- [`docs/usage.md`](docs/usage.md) - Usage examples and workflows
- [`docs/configuration.md`](docs/configuration.md) - Configuration options
- [`docs/development/`](docs/development/) - Technical implementation
- [`docs/testing/`](docs/testing/) - Testing procedures

## Important Disclaimers

**This software is provided "as is" without warranty of any kind.** It is intended for development and experimentation purposes. The authors make no claims about its suitability for production, critical systems, or any specific use case.

**Use at your own risk.** The authors disclaim all liability for any damages or losses resulting from the use of this software, including but not limited to data loss, system failure, or business interruption.

**Not production-ready without thorough testing.** This is a development tool that should be thoroughly tested and validated before any production use.

## License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

**Copyright (c) 2025 Echoing Vesper**

## Resources

- **Repository**: [https://github.com/EchoingVesper/mcp-task-orchestrator](https://github.com/EchoingVesper/mcp-task-orchestrator)
- **Issues**: [Report problems or request features](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
- **Documentation**: [Complete docs](docs/)

---

**Get started:**
```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator  
python run_installer.py
```
