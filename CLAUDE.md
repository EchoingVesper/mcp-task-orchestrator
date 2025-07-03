# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Tools Integration
@/home/aya/.claude/mcp-tools-core.md

Available MCP servers provide search, development, and automation capabilities. See user memory for detailed usage patterns.

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

### Server Modes
```bash
# Run server in dependency injection mode (default)
MCP_TASK_ORCHESTRATOR_USE_DI=true python -m mcp_task_orchestrator.server

# Run server in legacy mode
MCP_TASK_ORCHESTRATOR_USE_DI=false python -m mcp_task_orchestrator.server

# Use dedicated DI-only server
python -m mcp_task_orchestrator.server_with_di
```

## Clean Architecture Overview

The MCP Task Orchestrator now follows **Clean Architecture** and **Domain-Driven Design** principles with a complete layered structure:

### Architecture Layers

**1. Domain Layer** (`mcp_task_orchestrator/domain/`):
- **Entities**: Core business objects (Task, Specialist, OrchestrationSession, WorkItem)
- **Value Objects**: Immutable types (TaskStatus, SpecialistType, ExecutionResult, TimeWindow)
- **Exceptions**: Domain-specific error hierarchy with severity levels and recovery strategies
- **Services**: Domain business logic (TaskBreakdownService, SpecialistAssignmentService, etc.)
- **Repositories**: Abstract interfaces for data access (TaskRepository, StateRepository, SpecialistRepository)

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

**1. Dependency Injection System**:
- ServiceContainer with lifetime management (singleton, transient, scoped)
- Fluent service registration API with automatic dependency resolution
- Hybrid mode supporting both clean architecture and legacy compatibility

**2. Error Handling Infrastructure**:
- Comprehensive exception hierarchy with severity levels (LOW, MEDIUM, HIGH, CRITICAL)
- Automatic retry policies (exponential backoff, linear, fixed delay)
- Intelligent recovery strategies for tasks, specialists, and infrastructure
- Centralized error logging with structured analytics

**3. Monitoring and Diagnostics**:
- Real-time system monitoring with configurable alerts
- Performance metrics collection with trend analysis
- Comprehensive health checks for all system components
- Diagnostic tools with automated recommendations

**4. Task Orchestration System** (`mcp_task_orchestrator/orchestrator/`):
   - `task_orchestration_service.py`: Core orchestration logic (renamed from core.py)
   - `specialist_management_service.py`: Role-based specialist implementations (renamed from specialists.py)
   - `orchestration_state_manager.py`: State management (renamed from state.py)
   - `maintenance.py`: Automated cleanup and optimization features
   - `generic_models.py`: Flexible task model supporting any task type

**5. Database Layer** (`mcp_task_orchestrator/db/` + `infrastructure/database/`):
   - Repository pattern with abstract interfaces and SQLite implementations
   - Automatic migrations with rollback capabilities
   - Connection management with resource cleanup
   - Workspace-aware database organization

**6. Installation System** (`mcp_task_orchestrator_cli/`):
   - Modular client detection and configuration
   - Support for Claude Desktop, Cursor, Windsurf, VS Code
   - Secure installation with validation and rollback

**7. Testing Infrastructure** (`testing_utils/`):
   - File-based output system to prevent truncation
   - Alternative test runners for reliability
   - Comprehensive hang detection and resource management

### Domain-Driven Design Implementation

**Ubiquitous Language**: Core domain concepts consistently used across all layers
- **Task**: Unit of work with lifecycle, complexity, and specialist requirements
- **Specialist**: Role-based AI persona with specific capabilities and context
- **Orchestration Session**: Bounded context for related tasks and state
- **Work Item**: Atomic unit of executable work within a task
- **Artifact**: Stored output from task execution to prevent context limits

**Domain Services** (`domain/services/`):
- `TaskBreakdownService`: Handles task planning and decomposition
- `SpecialistAssignmentService`: Manages specialist selection and context
- `ProgressTrackingService`: Tracks task status and progress
- `ResultSynthesisService`: Combines results from subtasks
- `OrchestrationCoordinator`: Composes all services for complete workflows

### Clean Architecture Task Flow

1. **Presentation** → **Application**: MCP request received, validated, and routed to use case
2. **Application** → **Domain**: Use case orchestrates domain services with business logic
3. **Domain** → **Infrastructure**: Domain services access data through repository interfaces
4. **Infrastructure** → **Database**: Repository implementations handle data persistence
5. **Domain** ← **Infrastructure**: Results flow back through the layers
6. **Presentation** ← **Application**: Clean response returned to MCP client

### SOLID Principles Implementation

- **Single Responsibility**: Each service has one clear purpose (task breakdown, specialist assignment, etc.)
- **Open/Closed**: New specialists and task types can be added without modifying existing code
- **Liskov Substitution**: Repository implementations are interchangeable through interfaces
- **Interface Segregation**: Small, focused interfaces (TaskRepository, StateRepository, etc.)
- **Dependency Inversion**: High-level modules depend on abstractions, not concretions

### Key Design Patterns

- **Clean Architecture**: Dependency flow always points inward toward domain
- **Domain-Driven Design**: Rich domain model with ubiquitous language
- **Repository Pattern**: Abstract data access with pluggable implementations
- **Dependency Injection**: Automatic resolution with configurable lifetimes
- **Strategy Pattern**: Pluggable retry policies and recovery strategies
- **Observer Pattern**: Event-driven error handling and metrics collection
- **Command Pattern**: Use cases encapsulate business operations
- **Factory Pattern**: Service creation through DI container
- **Adapter Pattern**: Infrastructure adapters for external services

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

### Clean Architecture Development Practices

#### Adding a New Domain Entity
1. Create entity in `domain/entities/` with business logic and invariants
2. Add value objects in `domain/value_objects/` for entity properties
3. Define repository interface in `domain/repositories/`
4. Implement repository in `infrastructure/database/sqlite/`
5. Create domain service if complex business logic is needed
6. Register services in DI container configuration

#### Adding a New Use Case
1. Create use case in `application/usecases/` following command pattern
2. Define request/response DTOs in `application/dto/`
3. Add any required domain services to support the use case
4. Register use case in DI container
5. Create MCP handler in `infrastructure/mcp/handlers.py`
6. Update MCP server tool definitions

#### Adding a New MCP Tool (Clean Architecture Way)
1. Create use case in `application/usecases/` for the business logic
2. Add MCP handler in `infrastructure/mcp/handlers.py` using the use case
3. Update tool definitions in `mcp_request_handlers.py`
4. Add integration tests covering the full flow
5. Document tool usage and examples

#### Adding Error Handling
1. Define domain exceptions in `domain/exceptions/` with appropriate severity
2. Use `@handle_errors` decorator for automatic retry and recovery
3. Add specific error handlers in `infrastructure/error_handling/handlers.py`
4. Configure recovery strategies for new error types
5. Test error scenarios and recovery paths

#### Adding Monitoring
1. Add metrics using `record_metric()`, `increment_counter()`, or `track_performance()`
2. Create health checks in monitoring system for new components
3. Add alerts for critical thresholds using `AlertRule`
4. Include component in diagnostic runner for troubleshooting

#### Debugging Issues (Modern Tools)
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