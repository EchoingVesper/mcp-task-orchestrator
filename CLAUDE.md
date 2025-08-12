# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Tools Integration

@/home/aya/.claude/mcp-tools-core.md

Available MCP servers provide search, development, and automation capabilities. See user memory for detailed usage patterns.

## Project Overview

The MCP Task Orchestrator is a Model Context Protocol server that provides intelligent task orchestration, specialized AI roles, and persistent memory for AI-assisted development. It follows Clean Architecture and Domain-Driven Design principles with a complete layered structure.

## Critical Directives

### ***CRITICAL***: Task Orchestrator Failure Protocol

**If the MCP Task Orchestrator ever fails to function:**

1. **STOP** - Do not proceed with current task or "work around" the issue
2. **DIAGNOSE** - Immediately spawn a diagnostic agent to identify the issue:
   ```bash
   # Check MCP connection
   claude mcp list 2>/dev/null | grep task-orchestrator || echo "Not connected"
   
   # Run health check
   python tools/diagnostics/health_check.py
   
   # Check server logs
   tail -n 50 ~/.claude/logs/mcp-*.log 2>/dev/null || echo "No logs found"
   ```
3. **FIX** - Spawn a dedicated fix agent with these priorities:
   - Follow detailed procedures in `PRPs/protocols/orchestrator-fix-protocol.md`
   - Fix known issues in the orchestrator code
   - Restart the MCP server if needed: `claude mcp restart task-orchestrator`
   - If changes were made to server code: `pip install -e . && claude mcp restart task-orchestrator`
   - Update documentation if Claude Code restart is required
4. **VERIFY** - Test the fix with `orchestrator_health_check` tool
5. **RESUME** - Only continue original task after verification

**Never say "the orchestrator isn't working, let's continue without it"**

### ***CRITICAL***: Git Commit After Every Task

**After completing ANY development task:**

1. **ALWAYS** review changes: `git status && git diff`
2. **COMMIT** with descriptive message:
   ```bash
   git add -A
   git commit -m "type(scope): description"
   # Examples:
   # fix(orchestrator): resolve connection timeout issue
   # feat(prp): add orchestrator integration to PRP process
   # docs(claude): add critical failure protocol
   ```
3. Include orchestrator task ID in commit if applicable
4. Never leave uncommitted changes between tasks

### ***CRITICAL***: Auto-Recovery for Orchestrator Changes

**When modifying orchestrator code:**

1. After any change to `mcp_task_orchestrator/` files:
   ```bash
   # Reinstall and restart
   pip install -e . && claude mcp restart task-orchestrator
   
   # Verify connection
   claude mcp list | grep task-orchestrator
   ```
2. If restart fails, notify user that Claude Code restart may be needed
3. Test with health check before proceeding

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

# Lint markdown files
markdownlint docs/ *.md
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

### Server Modes

```bash
# Run server in dependency injection mode (default)
MCP_TASK_ORCHESTRATOR_USE_DI=true python -m mcp_task_orchestrator.server

# Run server in legacy mode
MCP_TASK_ORCHESTRATOR_USE_DI=false python -m mcp_task_orchestrator.server

# Use dedicated DI-only server
python -m mcp_task_orchestrator.server_with_di
```

### Debugging and Diagnostics

```bash
# Comprehensive health check and diagnostics
python tools/diagnostics/health_check.py

# Real-time performance monitoring
python tools/diagnostics/performance_monitor.py --monitor --duration 120

# Run diagnostic analysis
python tools/diagnostics/health_check.py --diagnostics

# Generate full system report
python tools/diagnostics/health_check.py --report system_report.json

# MCP protocol testing
python scripts/diagnostics/test_mcp_protocol.py
```

## Clean Architecture Overview

The MCP Task Orchestrator follows **Clean Architecture** and **Domain-Driven Design** principles:

### Architecture Layers

**1. Domain Layer** (`mcp_task_orchestrator/domain/`):
- **Entities**: Core business objects (Task, Specialist, OrchestrationSession, WorkItem)
- **Value Objects**: Immutable types (TaskStatus, SpecialistType, ExecutionResult, TimeWindow)
- **Exceptions**: Domain-specific error hierarchy with severity levels and recovery strategies
- **Services**: Domain business logic (TaskBreakdownService, SpecialistAssignmentService, etc.)
- **Repositories**: Abstract interfaces for data access

**2. Application Layer** (`mcp_task_orchestrator/application/`):
- **Use Cases**: Orchestrate business workflows (OrchestrateTask, ManageSpecialists, TrackProgress)
- **DTOs**: Data transfer objects for clean boundaries between layers
- **Interfaces**: External service contracts (NotificationService, ExternalApiClient)

**3. Infrastructure Layer** (`mcp_task_orchestrator/infrastructure/`):
- **Database**: SQLite implementations of repository interfaces
- **MCP Protocol**: Request/response adapters and server implementation
- **Configuration**: Environment-aware config management and validation
- **Monitoring**: Comprehensive health checks, metrics, and diagnostics
- **Error Handling**: Centralized error processing, retry logic, and recovery strategies
- **Dependency Injection**: Service container with lifetime management

**4. Presentation Layer** (`mcp_task_orchestrator/presentation/`):
- **MCP Server**: Clean architecture entry point with DI integration
- **CLI Interface**: Command-line tools with health checks and configuration management

### Key Architectural Components

**Task Orchestration System** (`mcp_task_orchestrator/orchestrator/`):
- `task_orchestration_service.py`: Core orchestration logic
- `specialist_management_service.py`: Role-based specialist implementations
- `orchestration_state_manager.py`: State management
- `maintenance.py`: Automated cleanup and optimization features
- `generic_models.py`: Flexible task model supporting any task type

**Database Layer** (`mcp_task_orchestrator/db/` + `infrastructure/database/`):
- Repository pattern with abstract interfaces and SQLite implementations
- Automatic migrations with rollback capabilities
- Connection management with resource cleanup
- Workspace-aware database organization

**Installation System** (`mcp_task_orchestrator_cli/`):
- Modular client detection and configuration
- Support for Claude Desktop, Cursor, Windsurf, VS Code
- Secure installation with validation and rollback

### Clean Architecture Task Flow

1. **Presentation** → **Application**: MCP request received, validated, and routed to use case
2. **Application** → **Domain**: Use case orchestrates domain services with business logic
3. **Domain** → **Infrastructure**: Domain services access data through repository interfaces
4. **Infrastructure** → **Database**: Repository implementations handle data persistence
5. **Domain** ← **Infrastructure**: Results flow back through the layers
6. **Presentation** ← **Application**: Clean response returned to MCP client

## Important Considerations

### File Size Limits

Keep files under 500 lines (300-400 recommended) to prevent Claude Code crashes. Large files requiring refactoring:
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

## Clean Architecture Development Practices

### Adding a New Domain Entity

1. Create entity in `domain/entities/` with business logic and invariants
2. Add value objects in `domain/value_objects/` for entity properties
3. Define repository interface in `domain/repositories/`
4. Implement repository in `infrastructure/database/sqlite/`
5. Create domain service if complex business logic is needed
6. Register services in DI container configuration

### Adding a New Use Case

1. Create use case in `application/usecases/` following command pattern
2. Define request/response DTOs in `application/dto/`
3. Add any required domain services to support the use case
4. Register use case in DI container
5. Create MCP handler in `infrastructure/mcp/handlers.py`
6. Update MCP server tool definitions

### Adding a New MCP Tool

1. Create use case in `application/usecases/` for the business logic
2. Add MCP handler in `infrastructure/mcp/handlers.py` using the use case
3. Update tool definitions in `mcp_request_handlers.py`
4. Add integration tests covering the full flow
5. Document tool usage and examples

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

## File Organization Guidelines

### Root Directory Guidelines

Keep the root directory clean. Only place essential files directly in the repository root:

**Allowed in Root:**
- Core project files: `README.md`, `CHANGELOG.md`, `LICENSE`, `CONTRIBUTING.md`
- Configuration files: `pyproject.toml`, `setup.py`, `requirements.txt`
- Critical documentation: `CLAUDE.md`, `QUICK_START.md`, `TESTING_INSTRUCTIONS.md`
- Build artifacts: `build/`, `dist/`, `*.egg-info/`

**NOT Allowed in Root:**
- Test artifacts (`.json` reports, validation files)
- Migration reports and summaries
- Temporary documentation
- Individual test files
- Backup files
- Log files

### Proper File Placement

**Test Files and Artifacts:**

```bash
tests/                          # All test files
docs/archives/test-artifacts/   # Test validation reports (*.json)
docs/archives/migration-reports/  # Migration summaries and reports
```

**Documentation:**

```bash
docs/users/           # User-facing documentation
docs/developers/      # Developer/contributor documentation  
docs/archives/        # Historical docs, migration reports, test artifacts
```

**Scripts and Tools:**

```bash
scripts/             # Utility scripts organized by purpose
tools/               # Production diagnostic tools
```

## Markdown Guidelines

When creating or editing markdown files, follow these rules to prevent markdownlint warnings:

**Structure Rules:**
- Start files with H1 heading (`# Title`) on first line
- Use proper heading hierarchy without skipping levels
- End files with single newline

**Spacing Rules:**
- Add blank lines before and after headings
- Add blank lines before and after lists
- Add blank lines before and after code fences

**List Formatting:**
- Use consistent ordered list numbering: `1.` for all items
- Use `-` for unordered lists consistently
- Start top-level list items at left margin (0 spaces indentation)

**Code Block Guidelines:**
- Always specify a language for fenced code blocks
- Use `bash`/`shell` for commands, `text` for plain content, `console` for terminal output, `yaml` for configuration, `json` for JSON examples, `python` for Python code
- Add blank lines before and after code blocks

## Status Tagging System

### File Status Tags

Use status tags in square brackets at the beginning of filenames for systematic lifecycle tracking:

**Status Tag Categories:**
- `[CURRENT]` - Active, up-to-date files
- `[IN-PROGRESS]` - Currently being worked on
- `[DRAFT]` - Planned but not yet started
- `[NEEDS-VALIDATION]` - Implementation complete, requires testing
- `[NEEDS-UPDATE]` - Requires updates due to system changes
- `[DEPRECATED]` - Legacy files maintained for reference
- `[COMPLETED]` - Finished work (typically in completed/ folders)

**Files That Should Use Status Tags:**
- PRPs: `[IN-PROGRESS]foundation-stabilization.md`
- Planning documents: `[DRAFT]feature-roadmap.md`
- Implementation guides: `[NEEDS-UPDATE]installation-guide.md`
- Migration documents: `[COMPLETED]v1-to-v2-migration.md`
- Architecture decisions: `[CURRENT]clean-architecture-guide.md`

**Tag Update Requirements:**
- Update tags when file status changes
- Move completed PRPs to completed/ folder with [COMPLETED] tag
- Use [NEEDS-VALIDATION] for implementations requiring testing
- Archive outdated files with [DEPRECATED] before creating new versions

### Status Tag Examples

```bash
# PRPs with lifecycle tracking
PRPs/[IN-PROGRESS]foundation-stabilization-workflow-automation.md
PRPs/[DRAFT]agent-to-agent-architecture-implementation.md
PRPs/completed/[COMPLETED]codebase-standards-modernization.md

# Documentation with maintenance status
docs/[CURRENT]installation-guide.md
docs/[NEEDS-UPDATE]migration-guide-v1.md
docs/[DEPRECATED]legacy-api-reference.md

# Planning and roadmap files
docs/developers/planning/[DRAFT]v3-roadmap.md
docs/developers/planning/[IN-PROGRESS]database-migration-plan.md
```

### Claude Code Hooks Integration

The project includes Claude Code hooks to validate status tag usage:

```bash
# Status tag validator hook
.claude/hooks/status-tag-validator.sh

# Hook configuration in .claude/config.json
{
  "hooks": {
    "post-command": [".claude/hooks/status-tag-validator.sh"]
  }
}
```

## Important Instruction Reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.

### Status Tag Compliance

- ALWAYS include appropriate status tags in filenames for PRPs, planning documents, and lifecycle-managed files
- UPDATE status tags when file status changes during development
- USE Claude Code hooks to validate and remind about status tag maintenance
- MOVE completed PRPs to appropriate folders with [COMPLETED] tags
