name: "Task Tools Consolidation and Naming Cleanup"
description: |

#

# Purpose

Consolidate redundant task-related MCP tools, eliminate "subtask" terminology, and improve naming consistency across the task orchestration API.

#

# Core Principles

1. **Clean Architecture**: Maintain existing Clean Architecture patterns with use cases and domain entities

2. **API Consistency**: Follow REST API naming conventions and workflow orchestration best practices

3. **Backward Compatibility**: Minimize breaking changes where possible

4. **Domain Alignment**: Align tool names with the domain concept that tasks with dependencies replaced subtasks

---

#

# Goal

Clean up and consolidate the MCP task tools by:

1. Removing legacy tools with "subtask" terminology  

2. Renaming "generic" tools to remove unnecessary qualifiers

3. Creating new tools using Clean Architecture patterns

4. Ensuring consistent, intuitive API naming

#

# Why

- **User Experience**: Eliminates confusion between `plan_task` vs `create_generic_task`

- **API Consistency**: Aligns with industry standards (GitHub, Asana APIs use consistent naming)

- **Maintainability**: Reduces code duplication between legacy and modern implementations

- **Domain Accuracy**: "Subtasks" no longer exist as a concept - they're just tasks with dependencies

#

# What

Transform the current tool set from:

```yaml

# CURRENT (Problematic)

orchestrator_plan_task           

# Legacy, simplified handler in core_handlers.py

orchestrator_execute_subtask     

# Uses outdated "subtask" terminology  

orchestrator_complete_subtask    

# Uses outdated "subtask" terminology

orchestrator_create_generic_task 

# Unnecessary "generic" qualifier, but has full Clean Architecture

# DESIRED (Clean)

orchestrator_plan_task     

# Renamed from create_generic_task, full Clean Architecture

orchestrator_execute_task  

# Replaces execute_subtask, Clean Architecture

orchestrator_complete_task 

# Replaces complete_subtask, Clean Architecture  

```text

**ARCHITECTURE CHANGE**: Move from simplified handlers to Clean Architecture

- **Before**: core_handlers.py (simplified JSON responses, no use cases)

- **After**: generic_task_handlers.py (full use case integration, domain entities)

#

#

# Success Criteria

- [ ] All tools use consistent "task" terminology (no "subtask" or "generic")

- [ ] All task tools use Clean Architecture patterns with use cases

- [ ] Backward compatibility maintained for critical workflows

- [ ] All existing tests pass with updated tool names

- [ ] Tool routing handles new names correctly

#

# All Needed Context

#

#

# Documentation & References

```text
yaml

# MUST READ - Include these in your context window

- file: mcp_task_orchestrator/infrastructure/mcp/tool_definitions.py
  why: Current tool definitions that need updating
  

- file: mcp_task_orchestrator/infrastructure/mcp/handlers/generic_task_handlers.py  
  why: Clean Architecture pattern to follow for new handlers
  

- file: mcp_task_orchestrator/infrastructure/mcp/handlers/core_handlers.py
  why: Legacy handlers to remove/replace
  

- file: mcp_task_orchestrator/infrastructure/mcp/tool_router.py
  why: Tool routing that needs updating

- url: https://developers.asana.com/docs/quick-start
  why: Industry standard task API patterns (POST /tasks, GET /tasks)
  

- url: https://restfulapi.net/resource-naming/
  why: REST API naming conventions and best practices

- docfile: docs/temp/task-tools-consolidation-investigation.md
  why: Detailed analysis of current state and requirements

```text

#

#

# Current Codebase tree (relevant sections)

```text
bash
mcp_task_orchestrator/
├── infrastructure/mcp/
│   ├── tool_definitions.py           

# Tool definitions to update

│   ├── tool_router.py               

# Routing to update

│   └── handlers/
│       ├── core_handlers.py         

# Legacy handlers to remove

│       └── generic_task_handlers.py 

# Pattern to follow

├── application/usecases/
│   ├── orchestrate_task.py          

# Existing use case patterns

│   └── __init__.py                  

# May need new use cases

└── domain/
    ├── entities/task.py             

# Task entity

    └── services/                    

# Domain services

```text

#

#

# Desired Codebase tree with files to be added

```text
bash
mcp_task_orchestrator/
├── application/usecases/
│   ├── execute_task.py              

# NEW: Execute task use case

│   └── complete_task.py             

# NEW: Complete task use case  

├── infrastructure/mcp/handlers/
│   └── task_handlers.py             

# MODIFY: Add execute/complete handlers RENAMED: from "generic_task_handlers.py"

├── infrastructure/mcp/
│   ├── tool_definitions.py          

# MODIFY: Update tool definitions

│   └── tool_router.py              

# MODIFY: Update routing

└── tests/
    ├── unit/test_task_handlers.py   

# NEW: Tests for new handlers

    ├── integration/test_task_execution.py  

# RENAME: from test_subtask_execution.py

    └── integration/test_complete_task.py   

# RENAME: from test_complete_subtask.py

```text

#

#

# Known Gotchas of our codebase & Library Quirks

```text
python

# CRITICAL: Clean Architecture requires use case injection via DI integration

from .db_integration import get_generic_task_use_case
use_case = get_generic_task_use_case()  

# Always get use case first

# CRITICAL: NEW use cases will need similar DI integration pattern:

from .db_integration import get_execute_task_use_case, get_complete_task_use_case

# CRITICAL: Artifact storage prevents context limit issues (complex pattern from investigation)

artifact_refs = await self.artifact_service.store_artifacts(
    task_id, 
    completion_data["detailed_work"],
    artifact_type=completion_data.get("artifact_type", "general")
)

# CRITICAL: Enum serialization for JSON responses

for field in ["status", "lifecycle_stage", "complexity", "specialist_type"]:
    if task_dict.get(field) and hasattr(task_dict[field], 'value'):
        task_dict[field] = task_dict[field].value

# CRITICAL: DateTime serialization  

for field in ["created_at", "updated_at", "due_date"]:
    if task_dict.get(field):
        task_dict[field] = task_dict[field].isoformat()

# PATTERN: All handlers must return List[types.TextContent]

return [types.TextContent(type="text", text=json.dumps(response, indent=2))]

# ERROR HANDLING: Use OrchestrationError for domain errors

from ....domain.exceptions import OrchestrationError

# CRITICAL: Legacy vs Clean Architecture handler locations:

# - Legacy: mcp_task_orchestrator/infrastructure/mcp/handlers/core_handlers.py  

# - Modern: mcp_task_orchestrator/infrastructure/mcp/handlers/generic_task_handlers.py

```text

#

# Implementation Blueprint

#

#

# Data models and structure

No new data models needed - using existing Task entity:

```python

# Existing domain entities to use:

from ....domain.entities.task import Task, TaskStatus, TaskType
from ....domain.value_objects.complexity_level import ComplexityLevel
from ....domain.value_objects.specialist_type import SpecialistType

```text

#

#

# List of tasks to be completed in order

```text
yaml
Task 1 - Create Execute Task Use Case:
CREATE mcp_task_orchestrator/application/usecases/execute_task.py:
  - MIRROR pattern from: orchestrate_task.py
  - IMPLEMENT: get_task_execution_context() method
  - RETURN: specialist context and execution instructions

Task 2 - Create Complete Task Use Case:  
CREATE mcp_task_orchestrator/application/usecases/complete_task.py:
  - MIRROR pattern from: orchestrate_task.py
  - IMPLEMENT: complete_task_with_artifacts() method  
  - HANDLE: artifact storage and status updates

Task 3 - Add New Handlers:
MODIFY mcp_task_orchestrator/infrastructure/mcp/handlers/generic_task_handlers.py:
  - INJECT after existing handlers
  - ADD: handle_execute_task() function
  - ADD: handle_complete_task() function
  - MIRROR: existing handler patterns for error handling

Task 4 - Update Tool Definitions:
MODIFY mcp_task_orchestrator/infrastructure/mcp/tool_definitions.py:
  - REMOVE: lines 32-57 (orchestrator_plan_task definition in get_core_orchestration_tools)
  - REMOVE: lines 60-71 (orchestrator_execute_subtask definition in get_core_orchestration_tools)
  - REMOVE: lines 74-114 (orchestrator_complete_subtask definition in get_core_orchestration_tools)
  - ADD: orchestrator_execute_task definition to get_generic_task_tools() function
  - ADD: orchestrator_complete_task definition to get_generic_task_tools() function  
  - RENAME: line 151 "orchestrator_create_generic_task" to "orchestrator_plan_task"

Task 5 - Update Tool Router:
MODIFY mcp_task_orchestrator/infrastructure/mcp/tool_router.py:
  - REMOVE: lines 50-55 (legacy routing: plan_task, execute_subtask, complete_subtask)
  - ADD: elif name == "orchestrator_execute_task": return await handle_execute_task(arguments)
  - ADD: elif name == "orchestrator_complete_task": return await handle_complete_task(arguments)
  - UPDATE: line 64 "orchestrator_create_generic_task" to "orchestrator_plan_task"

Task 6 - Clean Up Legacy Handlers:
MODIFY mcp_task_orchestrator/infrastructure/mcp/handlers/core_handlers.py:
  - REMOVE: handle_plan_task() function (lines 65-76)
  - REMOVE: handle_execute_subtask() function (lines 79-90)
  - REMOVE: handle_complete_subtask() function (lines 93-106)
  - PRESERVE: other core handlers (initialize_session, synthesize_results, get_status, maintenance_coordinator)

Task 7 - Update Existing Tests:
UPDATE tests/integration/test_subtask_execution.py:
  - FIND: "orchestrator_execute_subtask" calls
  - REPLACE: with "orchestrator_execute_task"
  - RENAME FILE: to test_task_execution.py
  
UPDATE tests/integration/test_complete_subtask.py:
  - FIND: "orchestrator_complete_subtask" calls  
  - REPLACE: with "orchestrator_complete_task"
  - RENAME FILE: to test_complete_task.py

CREATE tests/unit/test_task_handlers.py:
  - TEST: handle_execute_task with valid/invalid inputs
  - TEST: handle_complete_task with artifact storage
  - MIRROR: test patterns from existing handler tests

```text

#

#

# Per task pseudocode

```text
python

# Task 1 - Execute Task Use Case

class ExecuteTaskUseCase:
    async def get_execution_context(self, task_id: str) -> ExecutionContext:
        

# PATTERN: Validate task exists and is executable

        task = await self.task_repository.get_by_id(task_id)
        if not task or task.status != TaskStatus.PENDING:
            raise OrchestrationError(f"Task {task_id} not ready for execution")
        
        

# PATTERN: Get specialist context from domain service

        specialist_context = await self.specialist_service.get_context(
            task.specialist_type, task.description
        )
        
        

# PATTERN: Update task status

        task.status = TaskStatus.IN_PROGRESS
        await self.task_repository.update(task)
        
        return ExecutionContext(
            task=task,
            specialist_context=specialist_context,
            instructions=self.generate_instructions(task)
        )

# Task 2 - Complete Task Use Case  

class CompleteTaskUseCase:
    async def complete_with_artifacts(self, task_id: str, completion_data: dict) -> Task:
        

# PATTERN: Validate completion data

        if not completion_data.get("summary"):
            raise OrchestrationError("Summary required for task completion")
            
        

# PATTERN: Store artifacts to prevent context limits

        artifact_refs = await self.artifact_service.store_artifacts(
            task_id, completion_data["detailed_work"]
        )
        
        

# PATTERN: Update task with completion

        task = await self.task_repository.get_by_id(task_id)
        task.status = TaskStatus.COMPLETED
        task.completion_summary = completion_data["summary"]
        task.artifact_references = artifact_refs
        
        return await self.task_repository.update(task)

# Task 3 - New Handlers Pattern

async def handle_execute_task(args: Dict[str, Any]) -> List[types.TextContent]:
    try:
        

# PATTERN: Extract and validate required fields

        task_id = args.get("task_id")
        if not task_id:
            

# PATTERN: Standard error response format

            return create_error_response("Missing required field: task_id")
        
        

# PATTERN: Get use case and execute

        use_case = get_execute_task_use_case()  

# DI integration

        execution_context = await use_case.get_execution_context(task_id)
        
        

# PATTERN: Format response with next steps

        response = {
            "status": "ready_for_execution",
            "task_id": task_id,
            "specialist_context": execution_context.specialist_context,
            "instructions": execution_context.instructions,
            "next_steps": [
                "Execute the task using provided context",
                "Use orchestrator_complete_task when finished"
            ]
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except OrchestrationError as e:
        

# PATTERN: Domain error handling

        return create_error_response(str(e), "orchestrator_execute_task")

```text

#

#

# Integration Points

```text
yaml
DATABASE:
  - existing: Uses current Task entity and repositories
  - no migrations: No schema changes required
  
CONFIG:
  - no changes: Uses existing configuration
  
ROUTING:
  - update: tool_router.py tool name mappings
  - preserve: All existing routing patterns
  
DI CONTAINER:
  - add: ExecuteTaskUseCase registration
  - add: CompleteTaskUseCase registration
  - pattern: Same as existing use case registrations

```text

#

# Validation Loop

#

#

# Level 1: Syntax & Style  

```text
bash

# Run these FIRST - fix any errors before proceeding

ruff check mcp_task_orchestrator/ --fix
mypy mcp_task_orchestrator/

# Expected: No errors. If errors, READ and fix immediately.

```text

#

#

# Level 2: Unit Tests

```python

# CREATE tests/unit/test_task_handlers.py

def test_execute_task_success():
    """Execute task returns specialist context"""
    args = {"task_id": "valid-task-id"}
    result = await handle_execute_task(args)
    response = json.loads(result[0].text)
    assert response["status"] == "ready_for_execution"
    assert "specialist_context" in response

def test_execute_task_missing_id():
    """Execute task fails without task_id"""
    args = {}
    result = await handle_execute_task(args)
    response = json.loads(result[0].text)
    assert "error" in response
    assert "task_id" in response["error"]

def test_complete_task_with_artifacts():
    """Complete task stores artifacts"""
    args = {
        "task_id": "valid-task-id",
        "summary": "Task completed successfully", 
        "detailed_work": "Detailed implementation...",
        "next_action": "complete"
    }
    result = await handle_complete_task(args)
    response = json.loads(result[0].text)
    assert response["status"] == "success"

```text

```text
bash

# Run and iterate until passing:

pytest tests/unit/test_task_handlers.py -v
pytest tests/integration/test_task_execution.py -v
pytest tests/integration/test_complete_task.py -v

```text

#

#

# Level 2.5: Specific Tool Validation

```text
bash

# Verify tool names updated correctly

python -c "
from mcp_task_orchestrator.infrastructure.mcp.tool_definitions import get_all_tools
tools = [t.name for t in get_all_tools()]
assert 'orchestrator_plan_task' in tools
assert 'orchestrator_execute_task' in tools  
assert 'orchestrator_complete_task' in tools
assert 'orchestrator_execute_subtask' not in tools
assert 'orchestrator_complete_subtask' not in tools
assert 'orchestrator_create_generic_task' not in tools
print('✅ All tool names updated correctly')
"

# Expected: Success message. If assertion fails, check tool_definitions.py updates

```text

#

#

# Level 3: Integration Test

```bash

# Test tool routing

python scripts/diagnostics/verify_tools.py

# Expected: All tools load without errors

# If failing: Check tool_definitions.py and tool_router.py syntax

# Test MCP protocol

python scripts/diagnostics/test_mcp_protocol.py

# Expected: All new tools respond correctly

# If failing: Check handler implementations and imports

```text

#

# Final validation Checklist

- [ ] All tests pass: `pytest tests/ -v`

- [ ] No linting errors: `ruff check mcp_task_orchestrator/`

- [ ] No type errors: `mypy mcp_task_orchestrator/`

- [ ] Tool verification: `python scripts/diagnostics/verify_tools.py`

- [ ] MCP protocol test: `python scripts/diagnostics/test_mcp_protocol.py`

- [ ] Tool names validated: All execute/complete tools renamed, no "subtask" or "generic" terms

- [ ] Legacy code removed: core_handlers.py cleaned up, tool_definitions.py updated

- [ ] Test files renamed: subtask_execution → task_execution, complete_subtask → complete_task

- [ ] DI integration working: New use cases registered and accessible via get_*_use_case()

- [ ] Clean Architecture maintained: All new handlers follow generic_task_handlers.py patterns

---

#

# Anti-Patterns to Avoid

- ❌ Don't create new architectural patterns - follow existing Clean Architecture

- ❌ Don't skip error handling - use OrchestrationError consistently

- ❌ Don't hardcode responses - use existing response formatting patterns  

- ❌ Don't break existing tool contracts - maintain response structures

- ❌ Don't ignore test failures - fix them before proceeding

- ❌ Don't mix legacy and modern patterns - use Clean Architecture consistently
