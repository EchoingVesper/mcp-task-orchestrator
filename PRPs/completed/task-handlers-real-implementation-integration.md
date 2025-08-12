name: "Task Handlers Real Implementation Integration"
description: |

#

# Purpose

Replace mock implementations in task handlers with real integrations to the existing orchestrator system, implementing missing functionality where no existing system exists.

#

# Core Principles

1. **Leverage Existing Systems**: Use proven orchestrator components where they exist

2. **Clean Architecture**: Maintain Clean Architecture patterns established in the consolidation PRP

3. **Real Database Integration**: Connect to actual database and state management

4. **Backward Compatibility**: Ensure existing workflows continue to work

---

#

# Goal

Upgrade the task handler implementations from mock responses to real functionality by:

1. Integrating with existing TaskOrchestrator, StateManager, and SpecialistManager

2. Implementing missing functionality where gaps exist

3. Maintaining the Clean Architecture use case patterns

4. Ensuring proper database persistence and state management

#

# Why

- **Production Readiness**: Mock implementations are not suitable for production use

- **Feature Completeness**: Users expect real task execution and completion functionality

- **Data Persistence**: Tasks should be properly stored and retrievable

- **System Integration**: New handlers should work with existing orchestrator ecosystem

#

# What

Transform the current mock-based handlers into real implementations:

```yaml

# CURRENT (Mock Implementation)

MockTaskUseCase:
  - Returns static mock task objects
  - No database persistence
  - No real specialist context

MockExecuteTaskUseCase:
  - Returns mock execution context
  - No real specialist assignment
  - No task status updates

MockCompleteTaskUseCase:
  - Returns mock completion responses
  - No artifact storage
  - No real state changes

# DESIRED (Real Implementation)

RealTaskUseCase:
  - Integrates with existing TaskOrchestrator
  - Persists to real database via StateManager
  - Returns actual Task objects

RealExecuteTaskUseCase:
  - Uses existing SpecialistManager for context
  - Updates task status in database
  - Provides real execution instructions

RealCompleteTaskUseCase:
  - Stores artifacts using existing system
  - Updates task completion in StateManager
  - Triggers any completion workflows

```text

#

#

# Success Criteria

- [ ] All mock implementations replaced with real functionality

- [ ] Integration with existing TaskOrchestrator, StateManager, SpecialistManager

- [ ] Tasks properly persisted to database

- [ ] Specialist context generation working

- [ ] Artifact storage functional

- [ ] All existing tests pass with real implementations

- [ ] New integration tests validate end-to-end functionality

#

# All Needed Context

#

#

# Documentation & References

```text
yaml

# MUST READ - Include these in your context window

- file: mcp_task_orchestrator/orchestrator/task_orchestration_service.py
  why: Main orchestrator that has existing task management functionality
  

- file: mcp_task_orchestrator/orchestrator/orchestration_state_manager.py
  why: State management for task persistence
  

- file: mcp_task_orchestrator/orchestrator/specialist_management_service.py
  why: Specialist context generation and assignment
  

- file: mcp_task_orchestrator/infrastructure/mcp/handlers/db_integration.py
  why: Current mock implementations to replace
  

- file: mcp_task_orchestrator/application/usecases/execute_task.py
  why: Use case interfaces that need real implementations
  

- file: mcp_task_orchestrator/application/usecases/complete_task.py
  why: Use case interfaces that need real implementations

- file: mcp_task_orchestrator/orchestrator/generic_models.py
  why: Task models and types used throughout system

```text

#

#

# Current Codebase Analysis

```text
bash

# Existing orchestrator components to leverage:

mcp_task_orchestrator/orchestrator/
├── task_orchestration_service.py     

# Main orchestrator with task lifecycle

├── orchestration_state_manager.py    

# Task persistence and state management

├── specialist_management_service.py  

# Specialist context and assignment

├── generic_models.py                 

# Task models and enums

└── artifacts.py                      

# Artifact storage system

# Mock implementations to replace:

mcp_task_orchestrator/infrastructure/mcp/handlers/
└── db_integration.py                 

# MockTaskUseCase, MockExecuteTaskUseCase, MockCompleteTaskUseCase

# Use cases needing real dependency injection:

mcp_task_orchestrator/application/usecases/
├── execute_task.py                   

# Needs real TaskRepository, SpecialistService

├── complete_task.py                  

# Needs real TaskRepository, ArtifactService

└── manage_tasks.py                   

# Needs real repository connection

```text

#

#

# Known Integration Points

```text
python

# EXISTING ORCHESTRATOR INTERFACES TO USE:

class TaskOrchestrator:
    async def plan_task(...) -> TaskBreakdown
    async def get_specialist_context(task_id: str) -> str
    async def complete_task(task_id: str, summary: str, artifacts: List[str], next_action: str) -> dict

class StateManager:
    async def store_task_breakdown(breakdown: TaskBreakdown)
    async def get_task(task_id: str) -> SubTask
    async def update_task_status(task_id: str, status: TaskStatus)
    async def get_all_tasks() -> List[SubTask]

class SpecialistManager:
    def get_specialist_context(specialist_type: SpecialistType, task_description: str) -> str
    def get_specialist_prompts(specialist_type: SpecialistType) -> List[str]

# GAPS TO IMPLEMENT:

- Direct task creation (not part of breakdown)

- Individual task execution context (separate from specialist context)

- Artifact storage integration

- Task completion with detailed work storage

```text

#

#

# Desired Integration Architecture

```text
python

# New factory functions should use existing orchestrator:

def get_real_task_use_case() -> TaskUseCase:
    

# Use existing orchestrator components

    state_manager = StateManager()
    orchestrator = TaskOrchestrator(state_manager, SpecialistManager())
    return RealTaskUseCase(orchestrator, state_manager)

def get_real_execute_task_use_case() -> ExecuteTaskUseCase:
    

# Integrate with existing specialist and state management

    state_manager = StateManager()
    specialist_manager = SpecialistManager()
    return RealExecuteTaskUseCase(state_manager, specialist_manager)

def get_real_complete_task_use_case() -> CompleteTaskUseCase:
    

# Use existing artifact and state systems

    state_manager = StateManager()
    artifact_service = ArtifactService()  

# May need to implement

    return RealCompleteTaskUseCase(state_manager, artifact_service)

```text

#

# Implementation Blueprint

#

#

# Data models and structure

Use existing models from `orchestrator/generic_models.py`:

```text
python

# Existing models to use:

from ...orchestrator.generic_models import (
    Task, TaskStatus, TaskType, LifecycleStage,
    TaskAttribute, TaskDependency, TaskEvent, TaskArtifact
)

# Existing orchestrator services:

from ...orchestrator.task_orchestration_service import TaskOrchestrator
from ...orchestrator.orchestration_state_manager import StateManager
from ...orchestrator.specialist_management_service import SpecialistManager

```text

#

#

# List of tasks to be completed in order

```text
yaml
Task 1 - Analyze Existing Orchestrator Capabilities:
RESEARCH existing orchestrator interfaces:
  - STUDY: task_orchestration_service.py methods and capabilities
  - STUDY: orchestration_state_manager.py persistence patterns
  - STUDY: specialist_management_service.py context generation
  - IDENTIFY: gaps where new functionality needs implementation
  - DOCUMENT: integration mapping between use cases and existing services

Task 2 - Implement Real Task Use Case:
REPLACE MockTaskUseCase in db_integration.py:
  - INTEGRATE: with existing TaskOrchestrator for task creation
  - IMPLEMENT: direct task creation method if missing from orchestrator
  - ENSURE: proper Task model returned (not mock)
  - TEST: task creation persistence through StateManager

Task 3 - Implement Real Execute Task Use Case:
REPLACE MockExecuteTaskUseCase in db_integration.py:
  - INTEGRATE: with existing SpecialistManager for context generation
  - IMPLEMENT: task status update to IN_PROGRESS via StateManager
  - GENERATE: real execution instructions based on task and specialist
  - ENSURE: ExecutionContextResponse contains real data
  - TEST: task execution context generation and status updates

Task 4 - Implement Real Complete Task Use Case:
REPLACE MockCompleteTaskUseCase in db_integration.py:
  - INTEGRATE: with existing artifact storage system
  - IMPLEMENT: artifact storage if missing (investigate orchestrator/artifacts.py)
  - UPDATE: task status to COMPLETED via StateManager
  - STORE: detailed work as artifacts to prevent context limits
  - ENSURE: TaskCompletionResponse contains real artifact references
  - TEST: task completion with artifact storage

Task 5 - Update Use Case Implementations:
MODIFY execute_task.py and complete_task.py:
  - UPDATE: constructor dependencies to use real services
  - IMPLEMENT: missing service interfaces if needed
  - ENSURE: Clean Architecture patterns maintained
  - TEST: use cases work with real dependencies

Task 6 - Integration Testing:
CREATE comprehensive integration tests:
  - TEST: full workflow plan_task → execute_task → complete_task
  - VERIFY: database persistence at each step
  - VALIDATE: artifact storage and retrieval
  - ENSURE: specialist context generation accuracy
  - TEST: error handling with real database operations

Task 7 - Performance and Error Handling:
ENHANCE real implementations:
  - ADD: proper error handling for database failures
  - IMPLEMENT: retry logic for transient failures
  - ADD: performance logging and metrics
  - ENSURE: resource cleanup (database connections, etc.)
  - TEST: error scenarios and recovery

```text

#

#

# Per task pseudocode

```text
python

# Task 2 - Real Task Use Case Implementation

class RealTaskUseCase:
    def __init__(self, orchestrator: TaskOrchestrator, state_manager: StateManager):
        self.orchestrator = orchestrator
        self.state_manager = state_manager
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        

# Convert dict to Task model

        task = Task(
            id=str(uuid.uuid4()),
            title=task_data["title"],
            description=task_data["description"],
            

# ... map other fields

        )
        
        

# Check if orchestrator has direct task creation

        if hasattr(self.orchestrator, 'create_single_task'):
            return await self.orchestrator.create_single_task(task)
        else:
            

# Implement direct task storage via state manager

            await self.state_manager.store_single_task(task)
            return task

# Task 3 - Real Execute Task Use Case Implementation

class RealExecuteTaskUseCase:
    def __init__(self, state_manager: StateManager, specialist_manager: SpecialistManager):
        self.state_manager = state_manager
        self.specialist_manager = specialist_manager
    
    async def get_task_execution_context(self, task_id: str) -> ExecutionContextResponse:
        

# Get real task from database

        task = await self.state_manager.get_task(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        

# Get real specialist context

        specialist_context = self.specialist_manager.get_specialist_context(
            task.specialist_type, task.description
        )
        
        

# Update task status to IN_PROGRESS

        await self.state_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        

# Generate real execution instructions

        instructions = self._generate_real_instructions(task, specialist_context)
        
        return ExecutionContextResponse(
            success=True,
            task_id=task_id,
            task_title=task.title,
            specialist_context=specialist_context,
            

# ... populate with real data

        )

# Task 4 - Real Complete Task Use Case Implementation  

class RealCompleteTaskUseCase:
    def __init__(self, state_manager: StateManager, artifact_service: ArtifactService):
        self.state_manager = state_manager
        self.artifact_service = artifact_service
    
    async def complete_task_with_artifacts(self, task_id: str, completion_data: Dict) -> TaskCompletionResponse:
        

# Get real task

        task = await self.state_manager.get_task(task_id)
        
        

# Store artifacts using real storage

        artifact_refs = await self.artifact_service.store_task_artifacts(
            task_id,
            completion_data["detailed_work"],
            completion_data.get("artifact_type", "general")
        )
        
        

# Update task status and completion data

        await self.state_manager.update_task_completion(
            task_id, 
            TaskStatus.COMPLETED,
            completion_data["summary"],
            artifact_refs
        )
        
        return TaskCompletionResponse(
            success=True,
            task_id=task_id,
            artifact_references=artifact_refs,
            

# ... populate with real completion data

        )

```text

#

#

# Integration Points

```text
yaml
DATABASE:
  - existing: Use StateManager for all database operations
  - persistence: Task storage, status updates, completion tracking
  
ORCHESTRATION:
  - existing: TaskOrchestrator for task lifecycle management
  - integration: Specialist assignment and context generation
  
ARTIFACTS:
  - investigate: Check if orchestrator/artifacts.py provides needed functionality
  - implement: Create ArtifactService if missing
  
STATE_MANAGEMENT:
  - existing: StateManager handles task state transitions
  - extend: May need methods for single task operations (not just breakdowns)

```text

#

# Validation Loop

#

#

# Level 1: Integration Verification

```text
python

# Verify existing orchestrator capabilities

from mcp_task_orchestrator.orchestrator.task_orchestration_service import TaskOrchestrator
from mcp_task_orchestrator.orchestrator.orchestration_state_manager import StateManager

# Test basic integration

async def test_integration():
    state_manager = StateManager()
    orchestrator = TaskOrchestrator(state_manager, specialist_manager)
    
    

# Verify methods exist

    assert hasattr(orchestrator, 'plan_task')
    assert hasattr(state_manager, 'store_task_breakdown')
    assert hasattr(state_manager, 'get_task')
    
    print("✅ Basic integration verified")

```text

#

#

# Level 2: Real Implementation Tests

```text
python

# Test real task creation

async def test_real_task_creation():
    use_case = get_real_task_use_case()
    task = await use_case.create_task({
        "title": "Real Test Task",
        "description": "Testing real implementation"
    })
    
    assert isinstance(task, Task)  

# Real Task object, not mock

    assert task.id is not None
    print("✅ Real task creation working")

# Test real task execution

async def test_real_task_execution():
    use_case = get_real_execute_task_use_case()
    context = await use_case.get_task_execution_context("real-task-id")
    
    assert context.specialist_context != {"mock": "context"}  

# Real context

    assert len(context.execution_instructions) > 0
    print("✅ Real task execution working")

# Test real task completion

async def test_real_task_completion():
    use_case = get_real_complete_task_use_case()
    response = await use_case.complete_task_with_artifacts("real-task-id", {
        "summary": "Real completion",
        "detailed_work": "Real work done",
        "next_action": "complete"
    })
    
    assert len(response.artifact_references) > 0  

# Real artifacts stored

    assert response.artifact_references[0]["id"] != "mock-artifact"
    print("✅ Real task completion working")

```text

#

#

# Level 3: End-to-End Integration

```text
bash

# Test full workflow with real implementations

python -c "
import asyncio
from mcp_task_orchestrator.infrastructure.mcp.tool_router import route_tool_call

async def test_real_workflow():
    

# Plan task

    plan_result = await route_tool_call('orchestrator_plan_task', {
        'title': 'Real Integration Test',
        'description': 'Test real implementations'
    })
    
    

# Execute task  

    execute_result = await route_tool_call('orchestrator_execute_task', {
        'task_id': 'real-task-id'
    })
    
    

# Complete task

    complete_result = await route_tool_call('orchestrator_complete_task', {
        'task_id': 'real-task-id',
        'summary': 'Real integration test completed',
        'detailed_work': 'All real implementations working',
        'next_action': 'complete'
    })
    
    print('✅ End-to-end real workflow completed')

asyncio.run(test_real_workflow())
"
```text

#

# Final Validation Checklist

- [ ] MockTaskUseCase replaced with RealTaskUseCase using TaskOrchestrator

- [ ] MockExecuteTaskUseCase replaced with RealExecuteTaskUseCase using SpecialistManager

- [ ] MockCompleteTaskUseCase replaced with RealCompleteTaskUseCase using ArtifactService

- [ ] All use cases properly inject real dependencies

- [ ] Database persistence working through StateManager

- [ ] Specialist context generation functional

- [ ] Artifact storage implemented and working

- [ ] Error handling for real database operations

- [ ] Performance monitoring and logging added

- [ ] Integration tests validate end-to-end functionality

- [ ] Existing tests updated to work with real implementations

- [ ] Clean Architecture patterns maintained throughout

---

#

# Anti-Patterns to Avoid

- ❌ Don't bypass existing orchestrator - integrate with it

- ❌ Don't duplicate functionality that already exists

- ❌ Don't break existing Clean Architecture patterns

- ❌ Don't ignore error handling for real database operations

- ❌ Don't skip integration testing with real components

- ❌ Don't leave mock implementations as fallbacks in production code
