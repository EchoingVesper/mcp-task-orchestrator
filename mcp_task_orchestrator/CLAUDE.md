# MCP Task Orchestrator - Core Package

## Clean Architecture Implementation

**Domain-Driven Design with Clean Architecture**: This package implements a complete DDD/Clean Architecture solution.

## Package Structure

### Core Layers
- **`domain/`** - Business logic, entities, value objects (innermost layer)
- **`application/`** - Use cases and application services  
- **`infrastructure/`** - External concerns (database, MCP, monitoring)
- **`presentation/`** - MCP server and CLI interfaces

### Legacy Components (Being Phased Out)
- **`orchestrator/`** - Legacy orchestration logic (transitioning to domain)
- **`db/`** - Legacy database layer (replaced by infrastructure/database)

## Development Guidelines

### Layer Dependencies
- **Domain**: No external dependencies 
- **Application**: Depends only on domain
- **Infrastructure**: Implements domain/application interfaces
- **Presentation**: Orchestrates application use cases

### Key Patterns
- **Repository Pattern**: Abstract data access in domain, implement in infrastructure
- **Dependency Injection**: Service container with lifetime management
- **Error Handling**: Domain exceptions with infrastructure recovery strategies

## Important Files
- `server_with_di.py` - Clean architecture entry point
- `server.py` - Legacy entry point (will be deprecated)
- `domain/entities/` - Core business objects
- `infrastructure/di/container.py` - Service registration

## File Size Warnings
Critical files needing refactoring:
- `db/generic_repository.py` (1180 lines) 
- `orchestrator/task_lifecycle.py` (1132 lines)
- `orchestrator/generic_models.py` (786 lines)