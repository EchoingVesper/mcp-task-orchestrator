

# Clean Architecture Guide for MCP Task Orchestrator

This guide explains the clean architecture implementation and how to work with the new layered structure.

#

# Architecture Overview

The MCP Task Orchestrator follows **Clean Architecture** principles with strict separation of concerns across four main layers:

```text
┌─────────────────────────────────────────┐
│              Presentation               │ ← Entry points (MCP server, CLI)
├─────────────────────────────────────────┤
│              Application                │ ← Use cases and workflows
├─────────────────────────────────────────┤
│                Domain                   │ ← Business logic and rules
├─────────────────────────────────────────┤
│            Infrastructure               │ ← External concerns (DB, MCP, etc.)
└─────────────────────────────────────────┘

```text

#

## Dependency Rule

Dependencies always point **inward**:

- Presentation → Application → Domain

- Infrastructure → Domain (through interfaces)

- No dependencies flow outward

#

# Layer Responsibilities

#

## Domain Layer (`domain/`)

**Purpose**: Core business logic and rules
**Dependencies**: None (inner-most layer)

```text

domain/
├── entities/           

# Core business objects

│   ├── task.py
│   ├── specialist.py
│   └── orchestration.py
├── value_objects/      

# Immutable value types

│   ├── task_status.py
│   └── execution_result.py
├── services/           

# Domain business logic

│   ├── task_breakdown_service.py
│   └── orchestration_coordinator.py
├── repositories/       

# Data access interfaces

│   ├── task_repository.py
│   └── state_repository.py
└── exceptions/         

# Domain-specific errors

    ├── task_errors.py
    └── specialist_errors.py

```text

**Key Principles**:

- Contains no dependencies on external frameworks

- Defines interfaces for data access (repositories)

- Implements core business rules and validation

- Uses ubiquitous language from domain model

#

## Application Layer (`application/`)

**Purpose**: Orchestrate business workflows
**Dependencies**: Domain layer only

```text

application/
├── usecases/          

# Application workflows

│   ├── orchestrate_task.py
│   ├── manage_specialists.py
│   └── track_progress.py
├── dto/               

# Data transfer objects

│   ├── task_dtos.py
│   └── progress_dtos.py
└── interfaces/        

# External service contracts

    ├── notification_service.py
    └── external_api_client.py

```text

**Key Principles**:

- Coordinates domain services to fulfill use cases

- Defines interfaces for external services

- Contains no business logic (delegates to domain)

- Uses DTOs for data transfer across boundaries

#

## Infrastructure Layer (`infrastructure/`)

**Purpose**: External system integrations
**Dependencies**: Domain and Application interfaces

```text

infrastructure/
├── database/          

# Data persistence

│   ├── sqlite/
│   └── repository_factory.py
├── mcp/              

# MCP protocol handling

│   ├── handlers.py
│   └── server.py
├── config/           

# Configuration management

├── monitoring/       

# System monitoring

├── error_handling/   

# Error infrastructure

└── di/              

# Dependency injection

```text

**Key Principles**:

- Implements domain repository interfaces

- Handles external system integration

- Contains framework-specific code

- Provides concrete implementations

#

## Presentation Layer (`presentation/`)

**Purpose**: System entry points
**Dependencies**: Application layer

```text

presentation/
├── mcp_server.py     

# MCP server entry point

└── cli.py           

# Command-line interface

```text

**Key Principles**:

- Handles input validation and formatting

- Routes requests to appropriate use cases

- Manages session and authentication

- Contains no business logic

#

# Development Patterns

#

## Adding a New Feature

1. **Start with Domain**:
   
```text
python
   

# domain/entities/new_entity.py

   class NewEntity:
       def __init__(self, name: str):
           self._validate_name(name)
           self.name = name
       
       def _validate_name(self, name: str):
           if not name or len(name) < 3:
               raise ValidationError("Name must be at least 3 characters")
   
```text
text

2. **Define Repository Interface**:
   
```text
python
   

# domain/repositories/new_entity_repository.py

   from abc import ABC, abstractmethod
   
   class NewEntityRepository(ABC):
       @abstractmethod
       async def save(self, entity: NewEntity) -> str:
           pass
       
       @abstractmethod
       async def find_by_id(self, entity_id: str) -> Optional[NewEntity]:
           pass
   
```text
text

3. **Create Use Case**:
   
```text
python
   

# application/usecases/manage_new_entity.py

   class CreateNewEntityUseCase:
       def __init__(self, repository: NewEntityRepository):
           self.repository = repository
       
       async def execute(self, request: CreateNewEntityRequest) -> CreateNewEntityResponse:
           entity = NewEntity(request.name)
           entity_id = await self.repository.save(entity)
           return CreateNewEntityResponse(entity_id=entity_id)
   
```text
text

4. **Implement Repository**:
   
```text
python
   

# infrastructure/database/sqlite/sqlite_new_entity_repository.py

   class SQLiteNewEntityRepository(NewEntityRepository):
       async def save(self, entity: NewEntity) -> str:
           

# SQLite-specific implementation

           pass
   
```text
text

5. **Add Presentation Handler**:
   
```text
python
   

# infrastructure/mcp/handlers.py

   async def handle_create_new_entity(request):
       use_case = container.get_service(CreateNewEntityUseCase)
       response = await use_case.execute(request)
       return response
   
```text
text

#

## Error Handling Pattern

```text
python
from infrastructure.error_handling import handle_errors, ErrorContext

@handle_errors(
    auto_retry=True,
    auto_recover=True,
    component="task_orchestrator",
    operation="execute_task"
)
async def execute_task(task_id: str):
    async with ErrorContext("task_execution", "execute", task_id=task_id):
        

# Implementation

        pass

```text

#

## Monitoring Pattern

```text
python
from infrastructure.monitoring import track_performance, record_metric

async def process_data():
    with track_performance("data_processing"):
        

# Process data

        record_metric("data.processed_items", item_count)

```text

#

## Testing Patterns

#

### Unit Testing (Domain)

```text
python
def test_task_creation():
    

# Test domain logic in isolation

    task = Task("Test task", complexity=Complexity.SIMPLE)
    assert task.status == TaskStatus.PENDING

```text

#

### Integration Testing (Application)

```text
python
async def test_create_task_use_case():
    

# Test use case with mocked repository

    mock_repo = Mock(spec=TaskRepository)
    use_case = CreateTaskUseCase(mock_repo)
    
    result = await use_case.execute(CreateTaskRequest("Test"))
    assert result.success

```text

#

### End-to-End Testing (Presentation)

```text
python
async def test_mcp_create_task():
    

# Test full MCP request flow

    response = await mcp_client.call_tool("create_task", {"name": "Test"})
    assert response["success"]

```text

#

# Dependency Injection

#

## Service Registration

```text
python

# infrastructure/di/service_configuration.py

def configure_services(container: ServiceContainer):
    

# Register repositories

    container.register(TaskRepository, SQLiteTaskRepository).as_singleton()
    
    

# Register use cases

    container.register(CreateTaskUseCase).as_transient()
    
    

# Register domain services

    container.register(TaskBreakdownService).as_singleton()

```text

#

## Service Resolution

```text
python

# Automatic injection

class CreateTaskUseCase:
    def __init__(self, repository: TaskRepository, breakdown_service: TaskBreakdownService):
        self.repository = repository
        self.breakdown_service = breakdown_service

# Manual resolution

container = get_container()
use_case = container.get_service(CreateTaskUseCase)

```text

#

# Best Practices

#

## Domain Layer

- Keep entities focused on business concepts

- Use value objects for immutable data

- Define clear invariants and validation

- Avoid dependencies on external frameworks

#

## Application Layer

- Keep use cases focused on single workflows

- Use DTOs for data transfer

- Delegate business logic to domain services

- Define interfaces for external dependencies

#

## Infrastructure Layer

- Implement domain interfaces

- Handle framework-specific concerns

- Manage external system integration

- Provide configuration and monitoring

#

## Presentation Layer

- Validate input and format output

- Route to appropriate use cases

- Handle authentication and authorization

- Manage session state

#

# Migration from Legacy Code

#

## Gradual Migration Strategy

1. **Extract Domain Concepts**: Identify core business logic

2. **Create Interfaces**: Define repository abstractions

3. **Implement Services**: Move business logic to domain services

4. **Add Use Cases**: Wrap domain services in application layer

5. **Update Handlers**: Route through use cases instead of direct calls

#

## Legacy Adapter Pattern

```text
python

# infrastructure/adapters/legacy_adapter.py

class LegacyTaskOrchestratorAdapter:
    def __init__(self, create_task_use_case: CreateTaskUseCase):
        self.create_task_use_case = create_task_use_case
    
    async def legacy_create_task(self, task_data: dict):
        

# Adapt legacy interface to new use case

        request = CreateTaskRequest.from_legacy(task_data)
        response = await self.create_task_use_case.execute(request)
        return response.to_legacy_format()

```text

#

# Common Antipatterns to Avoid

#

## ❌ Domain Depending on Infrastructure

```text
python

# WRONG: Domain importing database code

from infrastructure.database import SQLiteConnection

class Task:
    def save(self):
        conn = SQLiteConnection()  

# Domain shouldn't know about SQLite

```text

#

## ✅ Domain Using Interfaces

```text
python

# CORRECT: Domain defines interface, infrastructure implements

class TaskRepository(ABC):
    @abstractmethod
    async def save(self, task: Task) -> str: pass

class Task:
    

# Business logic only, no persistence concerns

    pass

```text

#

## ❌ Use Cases with Business Logic

```text
python

# WRONG: Use case contains business rules

class CreateTaskUseCase:
    async def execute(self, request):
        if len(request.name) < 3:  

# Business rule in use case

            raise ValidationError()

```text

#

## ✅ Use Cases Delegating to Domain

```text
python

# CORRECT: Use case delegates to domain

class CreateTaskUseCase:
    async def execute(self, request):
        task = Task(request.name)  

# Domain handles validation

        return await self.repository.save(task)

```text

#

# Tools and Utilities

#

## Health Checks

```text
bash
python tools/diagnostics/health_check.py --health

```text

#

## Performance Monitoring

```text
bash
python tools/diagnostics/performance_monitor.py --analyze

```text

#

## Architecture Validation

```text
bash

# Check dependency directions (future tool)

python tools/architecture/validate_dependencies.py
```text

This clean architecture provides a solid foundation for maintainable, testable, and scalable code while preserving the domain knowledge and business rules of the MCP Task Orchestrator.
