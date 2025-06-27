# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Building and Testing
```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests
pytest -m "not slow"     # Skip slow tests

# Run single test file
pytest tests/test_server.py -v

# Alternative test runners (more reliable output)
python tests/test_resource_cleanup.py
python tests/test_hang_detection.py
python tests/enhanced_migration_test.py
```

### Linting and Formatting
```bash
# Format code with Black
black mcp_task_orchestrator/

# Sort imports
isort mcp_task_orchestrator/

# Type checking (if mypy is configured)
mypy mcp_task_orchestrator/
```

### Package Management
```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install locally
pip install -e .

# PyPI release
python scripts/release/pypi_release_simple.py
```

## Architecture Overview

### Core Components

1. **MCP Server** (`mcp_task_orchestrator/server.py`): Main Model Context Protocol server that handles incoming requests and coordinates task execution.

2. **Task Orchestration System** (`mcp_task_orchestrator/orchestrator/`):
   - `core.py`: Core orchestration logic for task breakdown and management
   - `specialists.py`: Role-based specialist implementations (Architect, Implementer, etc.)
   - `maintenance.py`: Automated cleanup and optimization features
   - `generic_models.py`: Flexible task model supporting any task type

3. **Database Layer** (`mcp_task_orchestrator/db/`):
   - SQLite-based persistence with automatic migrations
   - `generic_repository.py`: Generic task storage and retrieval
   - `migration_manager.py`: Handles schema evolution
   - `workspace_migration.py`: Workspace-aware database management

4. **Installation System** (`mcp_task_orchestrator_cli/`):
   - Modular client detection and configuration
   - Support for Claude Desktop, Cursor, Windsurf, VS Code
   - Secure installation with validation and rollback

5. **Testing Infrastructure** (`mcp_task_orchestrator/testing/`):
   - File-based output system to prevent truncation
   - Alternative test runners for reliability
   - Comprehensive hang detection

### Task Flow

1. **Initialization**: `orchestrator_initialize_session` creates workspace context
2. **Planning**: `orchestrator_plan_task` breaks down complex tasks with LLM
3. **Execution**: `orchestrator_execute_subtask` runs tasks with specialist roles
4. **Completion**: `orchestrator_complete_subtask` stores artifacts and results
5. **Synthesis**: `orchestrator_synthesize_results` combines outputs

### Key Design Patterns

- **Workspace Paradigm**: Automatically detects project root and saves artifacts appropriately
- **Generic Task Model**: Flexible task representation supporting any workflow
- **Specialist Roles**: Domain-specific AI personas for different task types
- **Artifact Management**: Prevents context limits by storing large outputs to disk
- **Maintenance Automation**: Built-in cleanup and optimization features

## Important Considerations

### File Size Limits
- Keep files under 500 lines (300-400 recommended) to prevent Claude Code crashes
- Large files requiring refactoring:
  - `db/generic_repository.py` (1180 lines)
  - `orchestrator/task_lifecycle.py` (1132 lines)
  - `orchestrator/generic_models.py` (786 lines)

### Database Handling
- Always use context managers for database connections
- Resource cleanup is critical to prevent warnings
- Migrations run automatically on startup

### Testing Best Practices
- Use file-based output for long test results
- Alternative test runners available for reliability
- Resource warnings indicate connection leaks

### Security Considerations
- Never commit API keys or tokens
- Installer validates all operations
- Configuration backups created automatically

### Common Development Tasks

#### Adding a New MCP Tool
1. Add tool handler in `enhanced_handlers.py`
2. Update tool list in documentation
3. Add integration tests
4. Update README with usage examples

#### Adding a New Specialist Role
1. Create role definition in `config/default_roles.yaml`
2. Test role loading with `test_role_loader.py`
3. Document role capabilities
4. Add usage examples

#### Debugging Issues
```bash
# Check system health
python scripts/diagnostics/check_status.py

# Database diagnostics
python scripts/diagnostics/diagnose_db.py

# Server diagnostics
python scripts/diagnostics/diagnose_server.py

# MCP protocol testing
python scripts/diagnostics/test_mcp_protocol.py
```

## Development Workflow

1. Create feature branch from `main`
2. Write tests first (TDD approach)
3. Implement features incrementally
4. Run full test suite before commits
5. Update documentation as needed
6. Submit PR with clear description

## Project-Specific Notes

- Workspace detection looks for `.git`, `package.json`, `pyproject.toml`
- `.task_orchestrator/` directory created in project root
- Custom roles can be defined per-project
- Database stored in workspace-specific location
- Supports multiple concurrent MCP clients