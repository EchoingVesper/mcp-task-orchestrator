# MCP Task Orchestrator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version 1.3.1](https://img.shields.io/badge/version-1.3.1-green.svg)](https://github.com/EchoingVesper/mcp-task-orchestrator/releases/tag/v1.3.1)

> **AI-powered task orchestration and workflow automation for Model Context Protocol (MCP) environments**

A sophisticated Model Context Protocol server that provides intelligent task decomposition, specialized AI agent roles, and seamless workflow orchestration across multiple MCP-compatible clients including Claude Desktop, Cursor IDE, Windsurf, and VS Code.

## 🔍 Keywords

`model-context-protocol` `mcp` `ai-orchestration` `task-automation` `workflow-management` `ai-agents` `llm-tools` `project-management` `claude-desktop` `cursor-ide` `windsurf` `vscode` `cline` `anthropic` `ai-framework` `multi-agent-system` `python` `developer-tools` `ai-automation` `task-scheduling` `intelligent-workflows`

## 🎯 Overview

The MCP Task Orchestrator revolutionizes complex project management by providing sophisticated **AI-powered task decomposition** and **specialized prompting** for multi-step workflows. Unlike traditional task management tools, it leverages the intelligence of Large Language Models (LLMs) to break down complex projects into manageable, context-aware subtasks with specialist AI roles.

### 🎭 What Makes This Different?

- **Intelligent Task Breakdown**: Uses LLM reasoning to analyze complex projects and create optimized task sequences
- **Specialist AI Roles**: Architect, Implementer, Debugger, Documenter, and custom roles with domain-specific expertise
- **Universal MCP Integration**: Works seamlessly across all major MCP clients with zero configuration
- **Persistent Workflows**: Never lose progress with automatic state management and crash recovery
- **Single-Session Orchestration**: Complete complex projects within one conversation thread

## ✨ Key Features

### 🧠 **LLM-Powered Intelligence**
- **Smart Task Decomposition**: Automatically breaks complex projects into logical, manageable subtasks
- **Context-Aware Planning**: Understands dependencies, prerequisites, and optimal task ordering
- **Adaptive Complexity Handling**: Scales from simple automation to enterprise-level project orchestration

### 🎯 **Specialist AI Roles**
- **Architect Role**: System design, architecture planning, technology selection
- **Implementer Role**: Code development, feature implementation, technical execution  
- **Debugger Role**: Issue diagnosis, troubleshooting, error resolution
- **Documenter Role**: Documentation creation, API reference, user guides
- **Custom Roles**: Project-specific specialist definitions with auto-generated examples

### 🔄 **Workflow Orchestration**
- **Unified Installation**: One-command setup for all supported MCP clients
- **Auto-Detection**: Automatically finds and configures installed development environments
- **State Management**: Real-time progress tracking with dependency resolution
- **Task Persistence**: Crash-proof workflows with automatic state recovery
- **Single Session**: Complete multi-step projects without context switching

### 🛠️ **Developer Experience**
- **Zero Configuration**: Automatic client detection and setup
- **IDE Integration**: Native support for Claude Desktop, Cursor, Windsurf, VS Code + Cline
- **Live Monitoring**: Real-time task progress and execution status
- **Error Recovery**: Intelligent handling of failed tasks with retry mechanisms

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (Latest Python recommended for best performance)
- **One or more MCP clients** (Claude Desktop, Cursor IDE, Windsurf, or VS Code with Cline)

### Supported Development Environments

| Client | Description | Integration Level |
|--------|-------------|------------------|
| **Claude Desktop** | Anthropic's official desktop application | ✅ Native |
| **Cursor IDE** | AI-powered code editor with advanced features | ✅ Native |
| **Windsurf** | Codeium's intelligent development environment | ✅ Native |
| **VS Code** | With Cline extension for MCP support | ✅ Extension |

### Installation

```bash
# Clone the repository
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator

# One-command installation with automatic client detection
python run_installer.py
```

> **Why `run_installer.py`?** This optimized installer resolves import path issues and ensures reliable installation across all Python environments. It provides the same functionality as the previous method with improved error handling and compatibility.

**The optimized installer automatically:**
✅ Creates isolated Python virtual environment  
✅ Installs all required dependencies with correct versions
✅ Detects your installed MCP clients  
✅ Configures each client with optimal settings  
✅ Cleans up any obsolete configuration files  
✅ Validates installation integrity and resolves import conflicts

### After Installation

1. **Restart your MCP clients** (Claude Desktop, Cursor, etc.)
2. **Verify integration**: Look for 'task-orchestrator' in available tools/servers
3. **Start orchestrating**: Try example: *"Plan and implement a Python web scraper for news articles"*

## 🛠️ Advanced Installation Options

### Target Specific Clients

```bash
# Install for specific development environments only
python run_installer.py --clients claude-desktop cursor-ide

# Install for VS Code + Cline only  
python run_installer.py --clients vscode
```

### Installation Verification

```bash
# Comprehensive client detection test
python test_detection.py

# Validate all configurations
python test_validation.py

# Full system health check
python scripts/diagnostics/verify_tools.py
```

### Manual Configuration

For advanced users who prefer manual setup, see detailed instructions in [`docs/MANUAL_INSTALLATION.md`](docs/MANUAL_INSTALLATION.md)

## 📋 How It Works: Intelligent Workflow Orchestration

### The LLM-Powered Orchestration Process

The MCP Task Orchestrator uses a sophisticated **5-step intelligent workflow** that leverages the calling LLM's reasoning capabilities:

**Step 1: Session Initialization**
```python
# Initialize orchestration with intelligent guidance
response = await call_tool("orchestrator_initialize_session", {})
```

**Step 2: Intelligent Task Analysis**
```python
# LLM analyzes the project and creates structured subtasks
subtasks_json = [
  {
    "title": "System Architecture Design",
    "description": "Design scalable web scraper architecture with rate limiting",
    "specialist_type": "architect",
    "dependencies": [],
    "estimated_effort": "30-45 minutes",
    "complexity": "moderate"
  },
  {
    "title": "Core Implementation",
    "description": "Implement web scraping logic with error handling",
    "specialist_type": "implementer", 
    "dependencies": ["System Architecture Design"],
    "estimated_effort": "60-90 minutes",
    "complexity": "high"
  },
  {
    "title": "Testing & Validation",
    "description": "Create comprehensive test suite and validate functionality",
    "specialist_type": "debugger",
    "dependencies": ["Core Implementation"],
    "estimated_effort": "45-60 minutes", 
    "complexity": "moderate"
  }
  # Additional intelligent subtasks...
]
```

**Step 3: Orchestrated Task Planning**
```python
# Submit structured task plan with complexity assessment
response = await call_tool("orchestrator_plan_task", {
    "description": "Create a Python web scraper for news articles with rate limiting and error handling",
    "subtasks_json": json.dumps(subtasks_json),
    "complexity_level": "moderate"
})
```

**Step 4: Specialist-Driven Execution**
Each subtask is executed with **specialist context** that provides:
- Role-specific prompting and expertise
- Domain knowledge and best practices  
- Task-appropriate tools and methodologies
- Quality assurance and validation criteria

**Step 5: Intelligent Synthesis**
Results are combined into a comprehensive solution with:
- Integration testing and validation
- Documentation generation
- Performance optimization recommendations
- Deployment and maintenance guidelines

### Available Orchestration Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| `orchestrator_initialize_session` | Start new orchestration | Project kickoff with intelligent guidance |
| `orchestrator_plan_task` | Create task breakdown | LLM-powered project decomposition |
| `orchestrator_execute_subtask` | Execute with specialist context | Role-specific task execution |
| `orchestrator_complete_subtask` | Mark tasks complete | Progress tracking and validation |
| `orchestrator_synthesize_results` | Combine results | Comprehensive solution assembly |
| `orchestrator_get_status` | Check progress | Real-time workflow monitoring |

## 💾 Task Persistence & Recovery

**Version 1.3.0** introduces enterprise-grade **task persistence** to prevent workflow interruption:

### Automatic State Management
- **Real-time Saving**: Task state automatically saved after every significant change
- **Crash Recovery**: Interrupted workflows automatically detected and resumable
- **Context Preservation**: Full conversation context maintained across sessions
- **Dependency Tracking**: Complex task relationships preserved during recovery

### Persistent Storage Architecture
- **Role Configuration**: Specialist definitions stored in `.task_orchestrator/roles/`
- **Workflow State**: Active task progress saved in secure database
- **Concurrent Safety**: File locking prevents corruption during parallel access
- **Backup Systems**: Automatic incremental backups of critical workflow data

For detailed persistence architecture, see [Task Persistence Documentation](docs/persistence.md).

## 🎯 Real-World Use Cases

### Software Development Projects
- **Web Application Development**: Full-stack project orchestration from design to deployment
- **API Development**: RESTful service creation with testing and documentation
- **Database Schema Design**: Data modeling, migration scripts, and optimization
- **DevOps Pipeline Setup**: CI/CD configuration, containerization, monitoring

### Data Science & AI Projects  
- **Machine Learning Pipelines**: Data preprocessing, model training, evaluation, deployment
- **Data Analysis Workflows**: ETL processes, statistical analysis, visualization
- **Research Projects**: Literature review, experiment design, result analysis
- **AI Model Integration**: Fine-tuning, inference optimization, production deployment

### Content & Documentation
- **Technical Documentation**: API docs, user guides, architectural documentation
- **Content Creation**: Blog posts, tutorials, marketing materials
- **Code Review & Refactoring**: Quality assurance, optimization, modernization
- **Testing Strategies**: Unit tests, integration tests, performance benchmarks

## 🔧 Configuration & Customization

### Automatic Configuration

The installer handles all configuration automatically, but advanced users can customize:

#### Claude Desktop Configuration
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "path/to/venv/python.exe",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "cwd": "path/to/project",
      "env": {
        "PYTHONPATH": "path/to/project"
      }
    }
  }
}
```

#### Cursor IDE Configuration
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "path/to/venv/python",
      "args": ["-m", "mcp_task_orchestrator.server"],
      "cwd": "path/to/project"
    }
  }
}
```

### Custom Specialist Roles

Create project-specific specialist definitions:

```yaml
# .task_orchestrator/roles/custom_specialist.yaml
name: "Security Auditor"
description: "Specialized in security analysis and vulnerability assessment"
expertise:
  - "OWASP security standards"
  - "Penetration testing methodologies"  
  - "Secure coding practices"
  - "Compliance frameworks"
prompts:
  - "Focus on security implications of all recommendations"
  - "Identify potential vulnerabilities and mitigation strategies"
  - "Ensure compliance with industry security standards"
```

## 🆘 Troubleshooting Guide

### Common Installation Issues

#### "No MCP clients detected"
**Solution:**
- Ensure at least one supported client is installed
- Try running clients once before installation
- Check client installation paths and permissions

#### "Configuration failed"
**Solution:**  
- Verify file permissions in configuration directories
- Run installer as administrator/sudo if needed
- Check for conflicting MCP server configurations

#### "Module not found errors"
**Solution:**
- Virtual environment may be corrupted
- Delete `venv_mcp` folder and reinstall: `rm -rf venv_mcp && python run_installer.py`
- Ensure Python 3.8+ is installed and accessible

### Performance Optimization

#### Database Performance
```bash
# Optimize database for better performance
python scripts/diagnostics/diagnose_db.py --optimize

# Clean up stale task locks
python scripts/diagnostics/check_status.py --cleanup-locks
```

#### Memory Management
```bash
# Monitor system resource usage
python scripts/diagnostics/check_status.py --monitor

# Run memory-optimized server
python scripts/maintenance/run_optimized_server.py
```

### Getting Help

1. **Check Known Issues**: Review [`TEST_REPORT.md`](TEST_REPORT.md) for documented problems
2. **Run Diagnostics**: Execute diagnostic scripts in project root
3. **Community Support**: Open an issue with detailed logs and system information
4. **Documentation**: Comprehensive guides available in [`docs/troubleshooting/`](docs/troubleshooting/)

## 📁 Project Structure

```
mcp-task-orchestrator/
├── docs/                       # Comprehensive documentation
│   ├── development/           # Technical implementation guides
│   ├── testing/              # Test guides and reports
│   ├── troubleshooting/      # Diagnostic and issue resolution
│   ├── prompts/              # Context prompts and examples
│   └── examples/             # Usage examples and tutorials
├── tests/                    # Complete test suite
│   ├── integration/          # End-to-end workflow tests
│   ├── unit/                 # Component-level tests
│   ├── performance/          # Performance benchmarks
│   └── fixtures/             # Test utilities and helpers
├── scripts/                  # Utility and maintenance scripts
│   ├── diagnostics/          # System diagnostic tools
│   ├── migrations/           # Data migration scripts
│   ├── maintenance/          # System maintenance utilities
│   └── deployment/           # Installation and deployment
├── mcp_task_orchestrator/    # Core application code
├── data/                     # Database and data files
├── logs/                     # Log files (gitignored)
└── examples/                 # Usage examples and demos
```

## 🧪 Testing & Quality Assurance

### Comprehensive Test Suite

The project includes a **multi-tier testing framework** organized by purpose and scope:

#### Running Tests

```bash
# Activate virtual environment
source venv_mcp/bin/activate  # Linux/Mac
venv_mcp\Scripts\activate     # Windows

# Run complete test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests  
python -m pytest tests/performance/ -v   # Performance benchmarks

# Generate coverage reports
python -m pytest tests/ --cov=mcp_task_orchestrator --cov-report=html
```

#### Test Categories

| Test Type | Location | Purpose |
|-----------|----------|---------|
| **Unit Tests** | `tests/unit/` | Isolated component testing |
| **Integration Tests** | `tests/integration/` | Full workflow validation |
| **Performance Tests** | `tests/performance/` | Benchmarks and load testing |
| **Test Fixtures** | `tests/fixtures/` | Utilities and test helpers |

For comprehensive testing documentation, see [`docs/testing/test-suite-guide.md`](docs/testing/test-suite-guide.md).

## 🔧 Development & Maintenance Tools

### Diagnostic & Monitoring Scripts

```bash
# System health check and status monitoring
python scripts/diagnostics/check_status.py

# Database analysis and optimization
python scripts/diagnostics/diagnose_db.py

# MCP server diagnostics and validation
python scripts/diagnostics/diagnose_server.py

# Complete installation verification
python scripts/diagnostics/verify_tools.py
```

### Development Servers

```bash
# Run development server with hot reloading
python scripts/maintenance/simple_server.py

# Run with database optimization enabled
python scripts/maintenance/run_with_db.py

# Performance-optimized production server
python scripts/maintenance/run_optimized_server.py
```

For complete diagnostic and development guide, see [`docs/troubleshooting/diagnostic-tools.md`](docs/troubleshooting/diagnostic-tools.md).

## 📚 Documentation & Resources

### User Documentation
- [`docs/installation.md`](docs/installation.md) - Detailed installation instructions and troubleshooting
- [`docs/usage.md`](docs/usage.md) - Usage examples, workflows, and best practices
- [`docs/configuration.md`](docs/configuration.md) - Configuration options and customization

### Developer Resources  
- [`docs/development/`](docs/development/) - Technical implementation details and architecture
- [`docs/testing/`](docs/testing/) - Testing guides, procedures, and best practices
- [`docs/troubleshooting/`](docs/troubleshooting/) - Diagnostic guides and issue resolution

### API & Technical Reference
- [`docs/DEVELOPER.md`](docs/DEVELOPER.md) - Complete developer API reference
- [`docs/database_persistence.md`](docs/database_persistence.md) - Database architecture and persistence layer
- [`docs/persistence.md`](docs/persistence.md) - Task persistence and recovery mechanisms

## 🚀 Advanced Usage & Configuration

### Environment Variables & Customization

```bash
# Custom database location for enterprise deployments
export DB_PATH="/path/to/custom/database.db"

# Enable comprehensive debug logging
export DEBUG=true

# Custom timeout settings for long-running tasks
export TASK_TIMEOUT=300

# Performance monitoring and metrics
export ENABLE_METRICS=true
```

### Performance Optimization

```bash
# Run performance-optimized server with caching
python scripts/maintenance/run_optimized_server.py

# Database optimization and maintenance
python scripts/migrations/migrate_artifacts.py --optimize

# Memory usage optimization for large projects
python scripts/maintenance/run_with_memory_optimization.py
```

## 🤝 Contributing to the Project

We welcome contributions from the community! Here's how to get involved:

### Development Setup

1. **Fork** the repository on GitHub
2. **Clone** your fork: `git clone https://github.com/your-username/mcp-task-orchestrator.git`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`  
4. **Install** development dependencies: `pip install -r requirements-dev.txt`
5. **Test** your changes: `python -m pytest tests/ -v`
6. **Document** your changes in appropriate `docs/` files
7. **Commit** your changes: `git commit -m 'Add amazing feature'`
8. **Push** to your branch: `git push origin feature/amazing-feature`
9. **Submit** a Pull Request with detailed description

### Contribution Guidelines

- **Code Quality**: Follow PEP 8 style guidelines and include type hints
- **Testing**: Add tests for new features and ensure all tests pass
- **Documentation**: Update relevant documentation for any changes
- **Performance**: Consider performance implications of changes
- **Compatibility**: Ensure compatibility across all supported MCP clients

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for detailed contribution guidelines and coding standards.

## 📄 License & Legal

This project is licensed under the **MIT License** - see the [`LICENSE`](LICENSE) file for complete details.

**Copyright (c) 2025 Echoing Vesper**

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

## 🔗 Resources & Links

### Official Resources
- **🏠 GitHub Repository**: [https://github.com/EchoingVesper/mcp-task-orchestrator](https://github.com/EchoingVesper/mcp-task-orchestrator)
- **🐛 Issue Tracker**: [https://github.com/EchoingVesper/mcp-task-orchestrator/issues](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)
- **📖 Documentation**: [docs/](docs/)
- **📋 Release Notes**: [RELEASE_NOTES.md](RELEASE_NOTES.md)

### Community & Support
- **💬 Discussions**: GitHub Discussions for community Q&A
- **🎯 Feature Requests**: Issue tracker with enhancement label
- **🤝 Contributors**: See [Contributors](https://github.com/EchoingVesper/mcp-task-orchestrator/graphs/contributors)

## 🙏 Acknowledgments

- **Model Context Protocol Team**: Built for the innovative MCP ecosystem
- **Anthropic**: Inspired by advanced AI orchestration patterns and Claude's capabilities  
- **Open Source Community**: Designed for single-session efficiency and developer productivity
- **Contributors**: Thanks to all who have contributed to making this project better

---

## 🎯 Ready to Transform Your AI Workflows?

**Get started in under 60 seconds:**

```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator  
python run_installer.py
```

**Then try your first orchestrated workflow:**
*"Plan and implement a Python web scraper with rate limiting, error handling, and comprehensive testing"*

🚀 **Experience the power of AI-driven task orchestration today!**