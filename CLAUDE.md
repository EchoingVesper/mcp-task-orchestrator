# MCP Task Orchestrator - Claude Code Development Guide

This file provides context and guidance for Claude Code development sessions in the MCP Task Orchestrator project.

## Project Overview

**Version**: 1.4.1 (stable, production-ready)  
**Architecture**: Python-based MCP server with SQLite persistence and enhanced features  
**Location**: `E:\My Work\Programming\MCP Servers\mcp-task-orchestrator`

### Key Capabilities
- **Task Orchestration**: Intelligent breakdown with specialized AI roles
- **Artifact Storage**: Context limit prevention for complex workflows
- **Maintenance Coordination**: Automated task lifecycle management
- **Enhanced Testing**: Advanced infrastructure with alternative runners
- **Feature Management**: 8 approved features with implementation roadmap

## Quick Commands

### System Diagnostics
```bash
# Comprehensive health check
python scripts/diagnostics/check_status.py

# Installation verification  
python scripts/diagnostics/verify_tools.py

# Database optimization
python scripts/diagnostics/diagnose_db.py
```

### Enhanced Testing
```bash
# Enhanced test runners (preferred)
python simple_test_runner.py
python test_validation_runner.py

# Resource management validation
python tests/test_resource_cleanup.py

# Traditional pytest (still supported)
python -m pytest tests/ -v
```

### Development Server
```bash
# Launch orchestrator
python -m mcp_task_orchestrator.server
python launch_orchestrator.py

# CLI interface
python launch_cli.py
```

## Claude Code Integration

### Context-Specific Development
- **Root Context**: Universal project guidance (current directory)
- **Documentation**: `cd docs && claude` for multi-audience documentation workflows
- **Testing**: `cd tests && claude` for enhanced testing procedures  
- **Core Implementation**: `cd mcp_task_orchestrator && claude` for orchestrator development
- **Diagnostics**: `cd scripts && claude` for system tools and troubleshooting

### Enhanced Orchestrator Workflows
- **Artifact System**: Seamless integration with Claude Code file operations
- **Maintenance Coordination**: Automated task lifecycle and cleanup
- **Testing Infrastructure**: Optimized for Claude Code development patterns
- **Feature Management**: Strategic planning and implementation tracking

## Architecture

### Core Components
- **Orchestrator Core** (`orchestrator/`): Task breakdown and specialist management
- **Database Persistence** (`db/`): SQLAlchemy ORM with SQLite backend  
- **Testing Infrastructure** (`testing/`): Enhanced framework with alternative runners
- **Monitoring Systems** (`monitoring/`): Diagnostics and health checking

### Development Patterns
- **Async Safety**: All database operations with proper timeout handling
- **Singleton Management**: Lazy initialization for core components
- **Error Recovery**: Retry mechanisms with exponential backoff
- **Type Safety**: Pydantic models for data validation

## Git Workflow

### Repository Sync (CRITICAL)
**NEVER make individual file changes without considering full repository state.**

```bash
# Before any changes
git status
git pull origin main

# After making changes  
git status
git add [related-files]
git commit -m "feat: descriptive message"
git push origin main
```

### Atomic Development
- Group related changes in single commits
- Test thoroughly before committing
- Push only complete, working features
- Use descriptive commit messages with scope

## Enhanced Features (v1.4.1)

### Artifact Storage System
- **Context Limit Prevention**: Detailed work stored as filesystem artifacts
- **Cross-Session Continuity**: Complete history preservation across contexts
- **Professional Handovers**: Comprehensive documentation for team transitions
- **File Integration**: Works with all MCP file operation tools

### Maintenance Coordinator
- **Automated Management**: `orchestrator_maintenance_coordinator` tool
- **Cleanup Operations**: Smart removal of stale tasks with artifact preservation
- **Structure Validation**: Task hierarchy and data integrity analysis
- **Handover Preparation**: Complete transition documentation generation

### Advanced Testing Infrastructure  
- **Enhanced Runners**: Alternative to pytest with improved reliability
- **File-Based Output**: Complete result capture without truncation
- **Hang Detection**: Timeout mechanisms and process monitoring
- **Resource Management**: Automatic cleanup of connections and resources

## Development Guidelines

### Code Quality Standards
- Use `black` for formatting: `black mcp_task_orchestrator/ tests/`
- Organize imports with `isort`: `isort mcp_task_orchestrator/ tests/`
- Type checking with `mypy` when available
- Comprehensive error handling and input validation

### Testing Best Practices
- Prefer enhanced test runners over standard pytest
- Use file-based output for complex test scenarios
- Include timeout mechanisms for all operations
- Validate resource cleanup in database tests

### Database Operations
- Use managed connections with proper cleanup
- Implement retry logic with exponential backoff
- Leverage WAL mode for better concurrency
- Monitor connection health and performance

## Project Structure

```
mcp-task-orchestrator/
├── .task_orchestrator/           # Runtime state and custom roles
├── docs/                        # Multi-audience documentation
│   ├── llm-agents/              # AI-optimized documentation
│   ├── user-guide/              # Human-readable guides
│   ├── architecture/            # System design records
│   ├── testing/                 # Testing documentation
│   ├── troubleshooting/         # Issue resolution guides
│   └── prompts/features/        # Feature lifecycle management
├── mcp_task_orchestrator/       # Main Python package
│   ├── orchestrator/           # Core orchestration logic
│   ├── db/                     # Database persistence layer
│   ├── testing/                # Enhanced testing infrastructure
│   └── monitoring/             # Diagnostics and monitoring
├── tests/                      # Test suite with alternative runners
├── scripts/diagnostics/        # System diagnostic tools
└── architecture/               # Architectural documentation
```

## Troubleshooting

### Common Issues
- **Database Schema**: Run `python scripts/diagnostics/diagnose_db.py` for analysis
- **Installation**: Use `python scripts/diagnostics/verify_tools.py` for validation
- **Testing Failures**: Try enhanced runners: `python simple_test_runner.py`
- **Resource Warnings**: Use resource cleanup validation tests

### Emergency Procedures
- **Database Issues**: Emergency schema fix scripts available in project root
- **Test Hanging**: Enhanced infrastructure includes hang detection and timeouts
- **Context Limits**: Artifact storage system prevents work loss in complex sessions

## Performance Optimization

### Development Workflow
1. **Health Check**: Run diagnostics before major work
2. **Git Sync**: Always pull latest changes before development
3. **Feature Development**: Make logical, atomic changes
4. **Enhanced Testing**: Use improved test infrastructure
5. **Validation**: Verify system health after changes

### Resource Management
- Close resource-intensive tools when done
- Use enhanced testing for reliable validation
- Monitor database performance with diagnostic tools
- Leverage artifact storage for complex workflows

---

**For specialized contexts**: Use `cd <directory> && claude` to access area-specific guidance and workflows.