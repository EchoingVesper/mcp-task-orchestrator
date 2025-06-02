# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 1.4.0](https://img.shields.io/badge/version-1.4.0-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v1.4.0)

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
✓ Robust error handling ✓ Comprehensive test suite ✓ Full documentation ✓ Best practices
```

Each step provides specialist context and expertise rather than generic responses.

## Key Features

- **LLM-powered task decomposition**: Automatically breaks complex projects into logical subtasks
- **Specialist AI roles**: Architect, Implementer, Debugger, Documenter with domain-specific expertise
- **Automated maintenance**: Built-in cleanup, optimization, and health monitoring
- **Task persistence**: SQLite database with automatic recovery and archival
- **Artifact management**: Prevents context limits with intelligent file storage
- **Customizable roles**: Edit `.task_orchestrator/roles/project_roles.yaml` to adapt roles for your project
- **Universal MCP compatibility**: Works across Claude Desktop, Cursor, Windsurf, VS Code + Cline
- **Single-session completion**: Finish complex projects in one conversation

## Quick Start

### Prerequisites
- Python 3.8+ 
- One or more MCP clients (Claude Desktop, Cursor IDE, Windsurf, or VS Code with Cline extension)

### Installation
```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python run_installer.py
# Restart your MCP client and look for 'task-orchestrator' in available tools
```

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
| `orchestrator_complete_subtask` | Mark tasks complete with artifacts |
| `orchestrator_synthesize_results` | Combine results |
| `orchestrator_get_status` | Check progress |
| `orchestrator_maintenance_coordinator` | **NEW**: Automated cleanup and optimization |

### Maintenance & Automation Features

The orchestrator includes intelligent maintenance capabilities:

- **Automatic Cleanup**: Detects and archives stale tasks (>24 hours)
- **Performance Optimization**: Prevents database bloat and maintains responsiveness  
- **Structure Validation**: Ensures task hierarchies remain consistent
- **Handover Preparation**: Streamlines context transitions and project handoffs
- **Health Monitoring**: Provides system status and optimization recommendations

**Quick maintenance**: `"Use the maintenance coordinator to scan and cleanup the current session"`

For detailed guidance, see the [Maintenance Coordinator Guide](docs/user-guide/maintenance-coordinator-guide.md).

## Supported Environments

| Client | Description | Status |
|--------|-------------|---------|
| **Claude Desktop** | Anthropic's desktop application | ✅ Supported |
| **Cursor IDE** | AI-powered code editor | ✅ Supported |
| **Windsurf** | Codeium's development environment | ✅ Supported |
| **VS Code** | With Cline extension | ✅ Supported |

## Configuration & Customization

The installer handles configuration automatically. For manual setup, see [`docs/MANUAL_INSTALLATION.md`](docs/MANUAL_INSTALLATION.md).

### Custom Specialist Roles

Create project-specific specialists by editing `.task_orchestrator/roles/project_roles.yaml`:

```yaml
security_auditor:
  role_definition: "You are a Security Analysis Specialist"
  expertise:
    - "OWASP security standards"
    - "Penetration testing methodologies"  
    - "Secure coding practices"
  approach:
    - "Focus on security implications"
    - "Identify potential vulnerabilities"
    - "Ensure compliance with security standards"
```

The file is automatically created when you start a new orchestration session in any directory.

## Common Use Cases

**Software Development**: Full-stack web applications, API development with testing, database schema design, DevOps pipeline setup

**Data Science**: Machine learning pipelines, data analysis workflows, research project planning, model deployment strategies

**Documentation & Content**: Technical documentation, code review and refactoring, testing strategy development, content creation workflows

## Troubleshooting

### Common Issues

**"No MCP clients detected"** - Ensure at least one supported client is installed and run it once before installation

**"Configuration failed"** - Check file permissions, try running installer as administrator/sudo

**"Module not found errors"** - Delete `venv_mcp` folder and reinstall: `rm -rf venv_mcp && python run_installer.py`

### Diagnostic Tools

```bash
python scripts/diagnostics/check_status.py        # System health check
python scripts/diagnostics/diagnose_db.py         # Database optimization  
python scripts/diagnostics/verify_tools.py        # Installation verification
```

For comprehensive troubleshooting, see [`docs/troubleshooting/`](docs/troubleshooting/).

## Testing & Development

### Enhanced Testing Infrastructure

The MCP Task Orchestrator now includes robust testing improvements that eliminate common issues:

- **✅ No Output Truncation**: File-based output system prevents test output truncation
- **✅ No Resource Warnings**: Proper database connection management eliminates ResourceWarnings  
- **✅ No Test Hanging**: Comprehensive hang detection and timeout mechanisms
- **✅ Alternative Test Runners**: Bypass pytest limitations with specialized runners

### Quick Test Commands

```bash
# Activate environment
source venv_mcp/bin/activate  # Linux/Mac
venv_mcp\Scripts\activate     # Windows

# Run enhanced testing suite
python tests/test_resource_cleanup.py     # Validate resource management
python tests/test_hang_detection.py       # Test hang prevention systems
python tests/enhanced_migration_test.py   # Run migration test with full output

# Demonstrate improved testing features
python tests/demo_file_output_system.py   # Show file-based output system
python tests/demo_alternative_runners.py  # Show alternative test runners

# Traditional pytest (still supported)
python -m pytest tests/ -v
```

### Testing Best Practices

For reliable test execution, use the new testing infrastructure:

```python
# File-based output (prevents truncation)
from mcp_task_orchestrator.testing import TestOutputWriter
writer = TestOutputWriter(output_dir)
with writer.write_test_output("my_test", "text") as session:
    session.write_line("Test output here...")

# Alternative test runners (more reliable than pytest)
from mcp_task_orchestrator.testing import DirectFunctionRunner
runner = DirectFunctionRunner(output_dir=Path("outputs"))
result = runner.execute_test(my_test_function, "test_name")

# Database connections (prevents resource warnings)
from tests.utils.db_test_utils import managed_sqlite_connection
with managed_sqlite_connection("test.db") as conn:
    # Database operations with guaranteed cleanup
    pass
```

📖 **Documentation**: 
- [Testing Best Practices](docs/TESTING_BEST_PRACTICES.md) - Quick reference guide
- [Testing Improvements](docs/TESTING_IMPROVEMENTS.md) - Comprehensive documentation

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines and [`docs/`](docs/) for complete documentation.

## Important Disclaimers

**This software is provided "as is" without warranty of any kind.** It is intended for development and experimentation purposes. The authors make no claims about its suitability for production, critical systems, or any specific use case.

**Use at your own risk.** The authors disclaim all liability for any damages or losses resulting from the use of this software, including but not limited to data loss, system failure, or business interruption.

**Not production-ready without thorough testing.** This is a development tool that should be thoroughly tested and validated before any production use.

## License & Resources

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

- **Repository**: [https://github.com/EchoingVesper/mcp-task-orchestrator](https://github.com/EchoingVesper/mcp-task-orchestrator)
- **Issues**: [Report problems or request features](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
- **Documentation**: [Complete docs](docs/)

**Copyright (c) 2025 Echoing Vesper**
