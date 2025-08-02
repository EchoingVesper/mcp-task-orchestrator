
# CLAUDE.md

**[CURRENT]** Claude Code guidance for Core Package in MCP Task Orchestrator

⚠️ **File Size Compliant**: This file is kept under 400 lines for Claude Code stability

#
# Status Header

- **Status**: [CURRENT]

- **Context**: Core Implementation Package

- **Architecture Layer**: All layers (Domain, Application, Infrastructure, Presentation)

#
# Context Analysis

#
## Package Purpose

Core implementation of the MCP Task Orchestrator following Clean Architecture and Domain-Driven Design principles.

#
## Scope

- Domain entities, value objects, and business logic

- Application use cases and orchestration workflows

- Infrastructure implementations (database, MCP, monitoring)

- Presentation layer (MCP server, CLI interfaces)

#
## Architectural Role

This package implements the complete 4-layer Clean Architecture:

- **Domain**: Innermost layer with business logic and entities

- **Application**: Use cases and application services

- **Infrastructure**: External concerns and implementations

- **Presentation**: User interfaces and external APIs

#
# Core Commands

#
## Development Operations

```bash

# Install package in development mode

pip install -e ".[dev]"

# Run dependency injection server (recommended)

MCP_TASK_ORCHESTRATOR_USE_DI=true python -m mcp_task_orchestrator.server

# Run legacy mode

MCP_TASK_ORCHESTRATOR_USE_DI=false python -m mcp_task_orchestrator.server

# Run dedicated DI-only server

python -m mcp_task_orchestrator.server_with_di

```text

#
## Testing

```text
bash

# Run unit tests for core package

pytest mcp_task_orchestrator/tests/ -m unit

# Run integration tests

pytest mcp_task_orchestrator/tests/ -m integration

# Test specific layer

pytest mcp_task_orchestrator/domain/tests/
pytest mcp_task_orchestrator/application/tests/

```text

#
# Package Structure

```text
bash
mcp_task_orchestrator/
├── domain/              
# Business logic (innermost layer)
│   ├── entities/        
# Core business objects
│   ├── value_objects/   
# Immutable domain types
│   ├── services/        
# Domain business logic
│   ├── repositories/    
# Abstract data access interfaces
│   └── exceptions/      
# Domain-specific errors
├── application/         
# Use cases and orchestration
│   ├── usecases/        
# Business workflow orchestration
│   ├── dto/             
# Data transfer objects
│   └── interfaces/      
# External service contracts
├── infrastructure/      
# External concerns
│   ├── database/        
# Repository implementations
│   ├── mcp/             
# MCP protocol adapters
│   ├── monitoring/      
# Health checks and metrics
│   ├── error_handling/  
# Retry and recovery strategies
│   └── dependency_injection/  
# Service container
└── presentation/        
# User interfaces
    ├── mcp_server/      
# MCP server implementation
    └── cli/             
# Command-line interfaces

```text

#
# Development Patterns

#
## Adding New Domain Entity

1. Create entity in `domain/entities/` with business logic and invariants

2. Add value objects in `domain/value_objects/` for entity properties

3. Define repository interface in `domain/repositories/`

4. Implement repository in `infrastructure/database/sqlite/`

5. Register services in DI container configuration

#
## Adding New Use Case

1. Create use case in `application/usecases/` following command pattern

2. Define request/response DTOs in `application/dto/`

3. Add required domain services to support the use case

4. Register use case in DI container

5. Create MCP handler in `infrastructure/mcp/handlers.py`

#
## Adding New MCP Tool

1. Create use case in `application/usecases/` for business logic

2. Add MCP handler in `infrastructure/mcp/handlers.py` using the use case

3. Update tool definitions in `mcp_request_handlers.py`

4. Add integration tests covering the full flow

5. Document tool usage and examples

#
# Integration Points

#
## MCP Tool Integration

- All MCP tools are implemented as use cases in the application layer

- Handlers in `infrastructure/mcp/` adapt MCP protocol to use cases

- Tool definitions managed in `mcp_request_handlers.py`

#
## Clean Architecture Integration

- **Dependency Rule**: Dependencies point inward toward domain

- **Use Case Flow**: Presentation → Application → Domain → Infrastructure

- **Data Flow**: Infrastructure → Domain → Application → Presentation

- **Separation of Concerns**: Each layer has distinct responsibilities

#
## Database Integration

- Repository pattern with abstract interfaces in domain layer

- SQLite implementations in infrastructure layer

- Automatic migrations and workspace-aware organization

- Connection management with resource cleanup

#
# Troubleshooting

#
## Common Issues

- **Import Errors**: Check dependency injection container registration

- **Database Issues**: Verify workspace detection and migration status

- **MCP Protocol Issues**: Check handler registration and tool definitions

- **Resource Leaks**: Ensure proper context manager usage for database connections

#
## Debugging

```text
bash

# Health check and diagnostics

python tools/diagnostics/health_check.py

# Performance monitoring

python tools/diagnostics/performance_monitor.py --monitor

# MCP protocol testing

python scripts/diagnostics/test_mcp_protocol.py
```text

#
## Performance Considerations

- Use dependency injection for service lifetime management

- Implement proper resource cleanup in repository implementations

- Monitor database connection usage and cleanup

- Use file-based output for long test results

#
# Cross-References

#
## Related CLAUDE.md Files

- **Main Guide**: [CLAUDE.md](../CLAUDE.md) - Essential quick-reference

- **Detailed Guide**: [CLAUDE-detailed.md](../CLAUDE-detailed.md) - Comprehensive architecture

- **Documentation Architecture**: [docs/CLAUDE.md](../docs/CLAUDE.md) - Complete documentation system

- **Testing Guide**: [tests/CLAUDE.md](../tests/CLAUDE.md) - Testing infrastructure

- **Scripts Reference**: [scripts/CLAUDE.md](../scripts/CLAUDE.md) - Utilities and diagnostics

#
## Related Documentation

- [Clean Architecture Guide](../docs/developers/architecture/clean-architecture-guide.md)

- [Generic Task Implementation Guide](../docs/developers/architecture/generic-task-implementation-guide.md)

- [Database Schema Documentation](../docs/developers/architecture/database-schema-enhancements.md)

#
# Quality Checklist

- [ ] File size under 400 lines for Claude Code stability

- [ ] Status header current and reflects all architecture layers

- [ ] Clean Architecture layers properly documented

- [ ] All package structure accurately reflects current organization

- [ ] Commands tested and functional across all layers

- [ ] Cross-references accurate and up-to-date

- [ ] Development patterns reflect current best practices

- [ ] Integration points completely documented

- [ ] Troubleshooting addresses real implementation issues

- [ ] Accessibility guidelines followed (proper heading hierarchy)

- [ ] Code blocks specify language (bash, python, yaml, etc.)

- [ ] Related documentation links verified

#
# Maintenance Notes

#
## Update Procedures

- Follow clean architecture principles when adding new features

- Maintain separation of concerns between layers

- Update dependency injection container when adding new services

- Ensure proper test coverage for all layers

#
## Validation Requirements

- All entities must have proper invariant validation

- Use cases must have proper request/response DTOs

- Infrastructure implementations must follow repository interfaces

- All public APIs must have integration tests

- **Template Compliance**: Must pass `python scripts/validation/validate_template_compliance.py`

- **Cross-Reference Accuracy**: Must pass `python scripts/validation/validate_cross_references.py`

- **Style Guide Compliance**: Must follow [Style Guide](../style-guide.md) standards

- **Architecture Compliance**: Must maintain clean architecture principles

#
## Dependencies

- Domain layer has no external dependencies

- Application layer depends only on domain abstractions

- Infrastructure layer implements domain abstractions

- Presentation layer orchestrates through application layer

#
# Accessibility Notes

- **Heading Hierarchy**: Always follow proper H1 → H2 → H3 structure

- **Screen Reader Compatibility**: Use descriptive link text and alt text

- **Language Specification**: All code blocks must specify language

- **Consistent Navigation**: Cross-references enable logical navigation paths

- **Clean Architecture Clarity**: Layer separation clearly explained

---

📋 **This core package implements the complete Clean Architecture. See [CLAUDE.md](../CLAUDE.md) for essential commands, [Style Guide](../style-guide.md) for writing standards, and [CLAUDE-detailed.md](../CLAUDE-detailed.md) for comprehensive implementation details.**
