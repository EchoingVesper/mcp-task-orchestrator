# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Installation and Setup
```bash
# Install project (auto-detects MCP clients)
python run_installer.py

# Manual installation with virtual environment
python -m venv venv_mcp
source venv_mcp/bin/activate  # Linux/Mac
venv_mcp\Scripts\activate     # Windows
pip install -r requirements.txt
pip install -e .
```

### Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v          # Unit tests
python -m pytest tests/integration/ -v   # Integration tests
python -m pytest tests/performance/ -v   # Performance tests

# Run a single test file
python -m pytest tests/unit/test_persistence.py -v

# Run with coverage
python -m pytest tests/ --cov=mcp_task_orchestrator --cov-report=html
```

### Development
```bash
# Run the server directly
python -m mcp_task_orchestrator.server

# Run diagnostics
python scripts/diagnostics/check_status.py        # System health check
python scripts/diagnostics/diagnose_db.py         # Database optimization
python scripts/diagnostics/verify_tools.py        # Verify installation

# Database migration
python scripts/migrate_to_persistence.py
```

### Code Quality
```bash
# Format code
black mcp_task_orchestrator/ tests/

# Sort imports
isort mcp_task_orchestrator/ tests/

# Type checking (if mypy is installed)
mypy mcp_task_orchestrator/
```

## Architecture

### Core Components

**MCP Server (`mcp_task_orchestrator/server.py`)**
- Entry point for the Model Context Protocol server
- Exposes 6 orchestration tools via MCP protocol
- Uses singleton pattern for state management
- Handles async operations with proper timeout management

**Task Orchestrator (`orchestrator/core.py`)**
- Central coordinator for task breakdown and execution
- Implements retry logic with exponential backoff
- Manages specialist assignment and task dependencies
- Optimized for fast database operations (5s timeouts)

**State Manager (`orchestrator/state.py`)**
- Manages persistent state with SQLite backend
- Implements async-safe operations with proper locking
- Handles task recovery and cleanup on startup
- Uses Write-Ahead Logging (WAL) for better concurrency

**Database Persistence (`db/persistence.py`)**
- SQLAlchemy-based persistence layer
- Optimized SQLite configuration for concurrent access
- Implements connection pooling and health checks
- Manages both task data and file-based configurations (roles, logs)

**Specialist System (`orchestrator/specialists.py`)**
- Provides role-specific context for task execution
- Supports custom roles via YAML configuration
- Manages specialist prompts using Jinja2 templates
- Extensible architecture for adding new specialist types

### Key Patterns

1. **Singleton Management**: Core components (StateManager, SpecialistManager, TaskOrchestrator) use lazy initialization to prevent startup conflicts

2. **Async Safety**: All database operations wrapped in async-safe contexts with proper timeout handling

3. **Error Recovery**: Implements retry mechanisms with exponential backoff for transient failures

4. **Task Persistence**: Dual approach - SQLite for task state, filesystem for configuration files

5. **Modular Client Support**: Plugin architecture for MCP client detection and configuration

### Data Flow

1. User initiates orchestration via MCP tool call
2. Server creates/retrieves singleton instances
3. TaskOrchestrator breaks down complex task using LLM
4. StateManager persists task breakdown to database
5. Specialists execute subtasks with role-specific context
6. Results synthesized and returned to user

### Database Schema

- `task_breakdowns`: Parent task information
- `subtasks`: Individual subtask details with relationships
- `lock_tracking`: Manages concurrent access to tasks

## Important Considerations

- Database operations have reduced timeouts (5s) since SQLite is fast
- Use `run_installer.py` for automated setup across different MCP clients
- Custom roles can be defined in `.task_orchestrator/roles/project_roles.yaml`
- The system automatically recovers interrupted tasks on startup
- All async operations must respect the proper locking mechanisms