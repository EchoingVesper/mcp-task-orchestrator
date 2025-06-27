# MCP Task Orchestrator Documentation

## Quick Start

### Installation
```bash
pip install mcp-task-orchestrator
python -m mcp_task_orchestrator_cli.secure_installer_cli
```

### First Use
```python
# Initialize and create your first task
orchestrator_initialize_session()
orchestrator_plan_task(
    description="Your task description",
    subtasks_json='[{"title": "Implementation", "description": "Implement feature", "specialist_type": "implementer"}]'
)
```

## Documentation Structure

### 📦 Current Documentation
**Active, up-to-date documentation for current features**

- **[Installation](current/installation/)** - Installer, uninstaller, and deployment guides
  - [User Guide](current/installation/user-guide.md) - Step-by-step installation
  - [Troubleshooting](current/installation/troubleshooting.md) - Common issues and solutions
  - [Compatibility Matrix](current/installation/compatibility-matrix.md) - Platform and client support
  - [Security Features](current/installation/security-features.md) - Security design and features
  - [API Reference](current/installation/api-reference.md) - Programmatic installation APIs

- **[User Guide](user-guide/)** - End-user documentation
  - [Getting Started](user-guide/getting-started.md) - First steps with the orchestrator
  - [Core Concepts](user-guide/core-concepts.md) - Understanding tasks, specialists, and workflows
  - [Real-World Examples](user-guide/real-world-examples/) - Practical use cases and patterns

- **[API Documentation](api/)** - Technical API reference
  - [Reboot API Reference](api/reboot-api-reference.md) - Server restart and management APIs

- **[Architecture](architecture/)** - System design and decisions
  - [Server Reboot Design](architecture/server-reboot-design.md) - Reboot system architecture
  - [Decision Documentation Framework](architecture/decision-documentation-framework.md) - ADR process

### 🔧 Reference Materials
**Quick reference and lookup information**

- **[Commands](reference/commands.md)** - Complete command reference
- **[Error Codes](reference/error-codes.md)** - Error codes and resolution guide
- **[Compatibility](reference/compatibility.md)** - Platform and version compatibility

### 🏛️ Historical Documentation
**Archived content for reference and research**

- **[Pre-Installer Research](historical/pre-installer-research/)** - Manual configuration research
  - [Configuration Examples](historical/pre-installer-research/configuration/) - Legacy setup methods

### 🤝 Contributing
**Development and contribution guidelines**

- **[Testing](contributing/testing.md)** - Testing procedures and best practices
- **[Documentation](contributing/documentation.md)** - Documentation standards and process
- **[Release Process](contributing/release-process.md)** - Version management and releases

## Documentation for Different Audiences

### 🔰 New Users
Start here for your first experience:
1. [Installation User Guide](current/installation/user-guide.md)
2. [Getting Started](user-guide/getting-started.md)
3. [Basic Examples](user-guide/real-world-examples/)

### 👨‍💻 Developers
Technical documentation and APIs:
1. [API Reference](current/installation/api-reference.md)
2. [Architecture Documentation](architecture/)
3. [Development Guide](development/)

### 🔧 System Administrators
Operations and deployment:
1. [Installation Guide](current/installation/user-guide.md)
2. [Security Features](current/installation/security-features.md)
3. [Troubleshooting](current/installation/troubleshooting.md)
4. [Operations Manual](operations/reboot-operations.md)

### 🤖 AI Assistants
Optimized documentation for LLM integration:
1. [LLM Agent Documentation](llm-agents/)
2. [Quick Reference](llm-agents/quick-reference/)
3. [Workflow Contexts](llm-agents/workflow-contexts/)

## Key Features

### 🛡️ Secure Installation System
- **Zero vulnerabilities**: All 38 security issues resolved
- **Cross-platform support**: Windows, macOS, Linux
- **Multi-client compatibility**: Claude Desktop, Cursor, Windsurf, VS Code, Zed, Claude Code
- **Automatic backups**: Configuration protection and rollback
- **Surgical precision**: Preserves existing configurations

### 🔄 Server Reboot System
- **Graceful restarts**: State preservation across reboots
- **Client connection preservation**: Seamless reconnection
- **Hot reload support**: Configuration updates without disruption
- **Emergency procedures**: Robust failure recovery

### 🎯 Task Orchestration
- **Specialist-based architecture**: Role-specific task execution
- **Multi-step workflows**: Complex task breakdown and coordination
- **Progress tracking**: Real-time status and artifact management
- **Context continuity**: Maintained state across sessions

## Support and Resources

### 📚 Documentation
- **User guides**: Step-by-step instructions for all features
- **API reference**: Complete technical documentation
- **Examples**: Real-world use cases and patterns
- **Troubleshooting**: Common issues and solutions

### 🛠️ Tools and Diagnostics
```bash
# System health check
python scripts/diagnostics/check_status.py

# Installation validation
python -m mcp_task_orchestrator_cli.validation_backup_system --validate

# Connection testing
python scripts/diagnostics/debug_mcp_connections.py
```

### 🆘 Getting Help
1. **Check documentation**: Start with relevant user guides
2. **Run diagnostics**: Use built-in diagnostic tools
3. **Search issues**: Check existing problems and solutions
4. **Community support**: Engage with the community

## Version Information

**Current Version**: 1.7.1  
**Documentation Version**: 2.0 (Reorganized for clarity and usability)  
**Last Updated**: June 2025

### What's New in Documentation 2.0
- **Reorganized structure**: Clear separation of current vs. historical content
- **Enhanced installation docs**: Comprehensive installer and security documentation
- **Improved navigation**: Audience-specific entry points
- **Better cross-references**: Linked related content throughout
- **Archive organization**: Historical content properly categorized

## Quick Links

| Category | Description | Link |
|----------|-------------|------|
| 🚀 **Get Started** | Install and first use | [Installation Guide](current/installation/user-guide.md) |
| 📖 **Learn** | Core concepts and workflows | [User Guide](user-guide/) |
| 🔧 **Reference** | Commands and error codes | [Reference](reference/) |
| 🏗️ **Develop** | APIs and architecture | [API Docs](api/) |
| 🔍 **Troubleshoot** | Problem solving | [Troubleshooting](current/installation/troubleshooting.md) |
| 🤝 **Contribute** | Development guidelines | [Contributing](contributing/) |

---

**Welcome to the MCP Task Orchestrator!** This documentation is designed to help you quickly find what you need, whether you're installing for the first time, developing integrations, or managing deployments.

Choose your path above based on your role and objectives. For questions or improvements to this documentation, see our [contributing guidelines](contributing/documentation.md).