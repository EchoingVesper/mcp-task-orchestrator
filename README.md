
# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 2.0.0](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v2.0.0)

A Model Context Protocol server that transforms how you work with AI by automatically documenting every decision, implementation, and test as you build. Think of it as the memory layer for AI-assisted development that ensures no context is ever lost.

## Overview

The MCP Task Orchestrator provides intelligent task orchestration, specialized AI roles, and persistent memory for AI-assisted development. Built with Clean Architecture principles, it automatically detects project structure and saves artifacts appropriately.

**Document Type**: Project Overview & User Guide  
**Target Audience**: Developers using MCP clients (Claude Desktop, Cursor, VS Code, etc.)  
**Prerequisites**: Python 3.8+, MCP-compatible client  
**Last Updated**: 2025-01-13

## Key Features

- **Documentation Automation**: Every task generates comprehensive, searchable artifacts
- **Specialist AI Roles**: Architect, Implementer, Tester, Reviewer, Documenter, and more
- **Persistent Memory**: Never lose context - all decisions and implementations are preserved
- **Workspace Awareness**: Automatically detects project structure and saves artifacts appropriately
- **Template System**: 13 tools for creating reusable task templates
- **Clean Architecture**: Built with modern software design principles
- **Universal MCP Compatibility**: Works across Claude Desktop, Cursor, Windsurf, VS Code + extensions

## Quick Start

### Prerequisites
- Python 3.8+
- One or more MCP clients (Claude Desktop, Cursor IDE, Windsurf, or VS Code with extensions)

### Installation
1. **Install**: `pip install mcp-task-orchestrator`
2. **Configure**: Add to your MCP client configuration
3. **Use**: "Initialize task orchestrator session and help me build a REST API"

### Verification
Try this in your MCP client:
```
"Initialize a new orchestration session and plan a Python script for processing CSV files"
```

See the [Quick Start Guide](docs/users/quick-start/) for detailed setup instructions.

## How It Works

**Instead of monolithic responses:**
```
User: "Build a Python web scraper for news articles"
Claude: [Provides a single, basic response with minimal code]
```

**You get structured specialist workflows:**
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

Result: Complete implementation with:
✓ Error handling patterns ✓ Test coverage ✓ Documentation ✓ Best practices
```

Each step provides specialist context and expertise rather than generic responses.

## Core Features

- **LLM-powered task decomposition**: Automatically breaks complex projects into logical subtasks
- **Specialist AI roles**: Architect, Implementer, Debugger, Documenter with domain-specific expertise
- **Automated maintenance**: Built-in cleanup, optimization, and health monitoring
- **Task persistence**: SQLite database with automatic recovery and archival
- **Artifact management**: Prevents context limits with intelligent file storage
- **Workspace intelligence**: Automatically detects Git repositories, project files, and saves artifacts appropriately
- **Customizable roles**: Edit `.task_orchestrator/roles/project_roles.yaml` to adapt roles for your project
- **Single-session completion**: Finish complex projects in one conversation
- **Smart artifact placement**: Files are saved relative to your project root, not random locations

## Installation

### Universal Installer (Recommended)

The universal installer provides comprehensive support for all major MCP clients with flexible installation options.

**Quick Install - Auto-detect all clients:**
```bash
# Download and run the universal installer
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python install.py

# Auto-detects and configures all compatible MCP clients
# Restart your MCP clients - the orchestrator tools will be available automatically
```

**PyPI Installation with Manual Configuration:**
```bash
# Install from PyPI
pip install mcp-task-orchestrator

# Then configure your MCP client manually (see configuration section below)
```

**Install to specific clients:**
```bash
# Configure specific clients only
python install.py --clients claude,cursor

# Skip MCP configuration entirely (manual setup)
python install.py --no-clients

# Development installation with all tools
python install.py --dev

# Install in user directory
python install.py --user
```

**Advanced installation options:**
```bash
# Force PyPI installation even in development
python install.py --source pypi

# Install specific version
python install.py --version 2.0.0

# Install from git repository
python install.py --git https://github.com/EchoingVesper/mcp-task-orchestrator.git

# Install in custom virtual environment
python install.py --venv /path/to/venv

# Force overwrite existing installation
python install.py --force
```

**For Externally Managed Environments (WSL, Ubuntu 23.04+):**
```bash
# Create virtual environment first
python -m venv mcp-orchestrator-env
source mcp-orchestrator-env/bin/activate  # Linux/WSL/macOS
# OR: mcp-orchestrator-env\Scripts\activate  # Windows

# Clone and install
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python install.py --venv ../mcp-orchestrator-env
```

**Alternative with pipx:**
```bash
# Install via pipx for isolation
pipx install mcp-task-orchestrator

# Manual MCP configuration required (see configuration section)
```

### Installation Features

- ✅ **Zero vulnerabilities**: All 38 security issues resolved
- ✅ **Cross-platform**: Windows, macOS, Linux support
- ✅ **Multi-client**: Claude Desktop, Cursor, Windsurf, VS Code, Zed, Claude Code
- ✅ **Automatic backups**: Configuration protection and rollback
- ✅ **Performance**: < 5 seconds installation, < 50MB memory usage
- ✅ **Validation**: Comprehensive post-installation verification

### Supported MCP Clients

| Client | Auto-Detection | Installation Method | Multi-Project Support | Status |
|--------|----------------|-------------------|---------------------|---------|
| Claude Desktop | ✅ | JSON configuration | ✅ Dynamic detection | Fully Supported |
| Claude Code | ✅ | CLI integration | ✅ Per-project installs | Fully Supported |
| Windsurf | ✅ | JSON configuration | ✅ Built-in project context | Fully Supported |
| Cursor | ✅ | JSON configuration | ✅ Built-in project context | Fully Supported |
| VS Code | ⚠️ | Extension + config | ⚠️ | In Progress |
| Continue.dev | ⚠️ | JSON configuration | ⚠️ | In Progress |
| Cline | ⚠️ | JSON configuration | ⚠️ | In Progress |

### Troubleshooting Installation

**Quick Diagnostics:**
```bash
# View installation help and options
python install.py --help

# Check installation status
python install.py --status

# Force reconfiguration if already installed
python install.py --force

# Test dry-run mode to see what would be done
python install.py --dry-run --verbose
```

**Common Issues:**
- **Claude Code not detected**: Ensure Claude Code CLI is installed and `claude --version` works
- **Config file not found**: Make sure the MCP client is installed and has been run at least once
- **Permission errors**: Check file permissions for config directories
- **Already configured**: Use `--force` flag to overwrite existing configurations

**Client-Specific Notes:**
- **Claude Desktop**: Works globally across multiple projects using dynamic detection
- **Claude Code**: Works automatically with per-project detection for best experience
- **Windsurf/Cursor**: Automatically detect project context when opened in project folders

For comprehensive troubleshooting, see [Installation Troubleshooting Guide](docs/users/troubleshooting/common-issues/installation-problems.md).

### Verification
Try this in your MCP client:
```
"Initialize a new orchestration session and plan a Python script for processing CSV files"
```

## Workflow Process

The orchestrator follows a systematic five-step process:

1. **Workspace Detection** - Automatically identifies your project type and root directory
2. **Task Analysis** - LLM analyzes your request and creates structured subtasks
3. **Task Planning** - Organizes subtasks with dependencies and complexity assessment
4. **Specialist Execution** - Each subtask runs with role-specific context and expertise
5. **Result Synthesis** - Combines outputs into a comprehensive solution with workspace-aware artifact placement

### Available Tools

**Core orchestration tools for task management and execution:**

| Tool | Purpose | Parameters |
|------|---------|------------|
| `orchestrator_initialize_session` | Start new workflow | `working_directory` (optional) |
| `orchestrator_plan_task` | Create task breakdown | Required |
| `orchestrator_execute_task` | Execute with specialist context | Required |
| `orchestrator_complete_task` | Mark tasks complete with artifacts | Required |
| `orchestrator_synthesize_results` | Combine results | Required |
| `orchestrator_get_status` | Check progress | Optional |
| `orchestrator_maintenance_coordinator` | Automated cleanup and optimization | Required |

### Maintenance & Automation Features

The orchestrator includes intelligent maintenance capabilities:
- **Automatic Cleanup**: Detects and archives stale tasks (>24 hours)
- **Performance Optimization**: Prevents database bloat and maintains responsiveness
- **Structure Validation**: Ensures task hierarchies remain consistent
- **Handover Preparation**: Streamlines context transitions and project handoffs
- **Health Monitoring**: Provides system status and optimization recommendations

**Quick maintenance**: `"Use the maintenance coordinator to scan and cleanup the current session"`

For detailed guidance, see the [Maintenance Coordinator Guide](docs/users/guides/maintenance-coordinator-guide.md).

## Supported Environments

| Client | Description | Status |
|--------|-------------|---------|
| **Claude Desktop** | Anthropic's desktop application | ✅ Supported |
| **Cursor IDE** | AI-powered code editor | ✅ Supported |
| **Windsurf** | Codeium's development environment | ✅ Supported |
| **VS Code** | With Cline extension | ✅ Supported |

## Configuration & Customization

The universal installer handles all MCP client configuration automatically with zero-vulnerability design. For advanced configuration options, see the [Installation Guide](docs/installation/UNIVERSAL_INSTALLER.md) and [Configuration Reference](docs/users/reference/configuration/configuration.md).

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

**"Module not found errors"** - Try reinstalling in a fresh virtual environment:
```bash
python -m venv fresh_env && source fresh_env/bin/activate && pip install mcp-task-orchestrator
```

### Diagnostic Tools
```bash
# System health check
python scripts/diagnostics/check_status.py

# Database optimization
python scripts/diagnostics/diagnose_db.py

# Installation verification
python scripts/diagnostics/verify_tools.py
```

For comprehensive troubleshooting, see the [Troubleshooting Guide](docs/users/troubleshooting/TROUBLESHOOTING.md) and [Documentation Portal](docs/README.md).

## Testing & Development

### Enhanced Testing Infrastructure

The MCP Task Orchestrator includes robust testing improvements that eliminate common issues:
- **✅ No Output Truncation**: File-based output system prevents test output truncation
- **✅ No Resource Warnings**: Proper database connection management eliminates ResourceWarnings
- **✅ No Test Hanging**: Comprehensive hang detection and timeout mechanisms
- **✅ Alternative Test Runners**: Bypass pytest limitations with specialized runners

### Quick Test Commands
```bash
# Activate your virtual environment (if using one)
source your_venv/bin/activate  # Linux/Mac
your_venv\Scripts\activate     # Windows

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
- [Testing Best Practices](docs/developers/contributing/testing/TESTING_BEST_PRACTICES.md) - Quick reference guide
- [Testing Improvements](docs/developers/contributing/testing/TESTING_IMPROVEMENTS.md) - Comprehensive documentation

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines and [`docs/`](docs/) for complete documentation.

## Important Disclaimers

**This software is provided "as is" without warranty of any kind.** It is intended for development and experimentation purposes. The authors make no claims about its suitability for production, critical systems, or any specific use case.

**Use at your own risk.** The authors disclaim all liability for any damages or losses resulting from the use of this software, including but not limited to data loss, system failure, or business interruption.

**Development tool notice.** This is a development tool that should be thoroughly tested and validated before any production use.

## License & Resources

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

### Links
- **Repository**: [https://github.com/EchoingVesper/mcp-task-orchestrator](https://github.com/EchoingVesper/mcp-task-orchestrator)
- **Issues**: [Report problems or request features](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
- **Documentation**: [Documentation Portal](docs/README.md) | [Installation Guide](docs/installation/UNIVERSAL_INSTALLER.md) | [API Reference](docs/users/reference/api/API_REFERENCE.md)

Copyright (c) 2025 Echoing Vesper
