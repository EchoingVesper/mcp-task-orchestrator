

# MCP Task Orchestrator - Error Handling Consolidation & Refactoring Plan

#

# Overview

This document outlines a comprehensive refactoring plan to consolidate duplicate error handling code and address critical code quality issues in the MCP Task Orchestrator project.

#

# Executive Summary

**Primary Issue**: The codebase has excellent error handling infrastructure (`infrastructure/error_handling/`) but most modules bypass it, leading to 200+ lines of duplicate error handling code.

**Solution**: Systematically refactor manual error handling to use the established infrastructure, decompose oversized files, and improve type safety.

#

# 1. Critical Error Handling Consolidation

#

#

# 1.1 Duplicate Retry Logic (HIGH Priority - 4 hours)

**Problem**: Manual retry loops duplicated in 6+ methods in `task_orchestration_service.py`

**Current Duplicate Pattern**:

```python

# Found in 6+ methods (lines 147-176, 180-230, 273-350, etc.)

max_retries = 2
retry_delay = 0.1
for attempt in range(max_retries):
    try:
        

# operation

        break
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout [operation] (attempt {attempt+1}/{max_retries}): {str(e)}")
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay)
            retry_delay *= 1.5
        else:
            raise ValueError(f"Operation failed after {max_retries} attempts")

```text

**Fix**: Use existing `@handle_errors` decorator from `infrastructure/error_handling/decorators.py`

**Implementation**:

```text
text
python

# In: mcp_task_orchestrator/orchestrator/task_orchestration_service.py

from ..infrastructure.error_handling.decorators import handle_errors
from ..infrastructure.error_handling.retry_coordinator import RetryPolicy

@handle_errors(
    retry_policy=RetryPolicy.EXPONENTIAL_BACKOFF,
    max_retries=2,
    timeout_seconds=30
)
async def plan_task(self, description: str, complexity: ComplexityLevel, subtasks_json: str, context: Optional[str] = None):
    

# Remove manual retry logic (lines 147-176)

    

# Keep only business logic

```text

**Files to modify**:

- `mcp_task_orchestrator/orchestrator/task_orchestration_service.py` (methods: `plan_task`, `get_specialist_context`, `complete_subtask_with_artifacts`, `complete_subtask`, `synthesize_results`, `get_status`)

#

#

# 1.2 Duplicate Error Response Formatting (HIGH Priority - 2 hours)

**Problem**: Error response dictionaries duplicated 50+ times

**Current Duplicate Pattern**:

```text
python

# Found in lines 325-331, 346-352, 426-432, 442-448, etc.

return {
    "task_id": task_id,
    "status": "error",
    "error": str(e),
    "results_recorded": False,
    "parent_task_progress": {"progress": "unknown", "error": str(e)},
    "next_recommended_task": None
}

```text

**Fix**: Create centralized error response builder

**Implementation**:

```text
python

# New file: mcp_task_orchestrator/application/dto/error_responses.py

from pydantic import BaseModel
from typing import Optional, Dict, Any

class TaskErrorResponse(BaseModel):
    task_id: str
    status: str = "error"
    error: str
    results_recorded: bool = False
    parent_task_progress: Dict[str, str]
    next_recommended_task: Optional[str] = None

class ErrorResponseBuilder:
    @staticmethod
    def task_error(task_id: str, error: Exception) -> TaskErrorResponse:
        return TaskErrorResponse(
            task_id=task_id,
            error=str(error),
            parent_task_progress={"progress": "unknown", "error": str(error)}
        )

```text

**Usage**:

```text
python

# Replace all duplicate patterns with:

return ErrorResponseBuilder.task_error(task_id, e).dict()

```text

#

#

# 1.3 Database Error Handling Consolidation (MEDIUM Priority - 3 hours)

**Problem**: Database error patterns duplicated across all DB modules

**Current Pattern**:

```text
python

# Found in migration.py, backup_manager.py, auto_migration.py

try:
    

# database operation

except Exception as e:
    logger.error(f"Database operation failed: {str(e)}")
    

# cleanup or rollback

    raise

```text

**Fix**: Use existing database error handling infrastructure

**Implementation**:

```text
python

# Modify: mcp_task_orchestrator/infrastructure/database/connection_manager.py

from ..error_handling.decorators import handle_errors
from ..error_handling.recovery_strategies import DatabaseRecoveryStrategy

class DatabaseManager:
    @handle_errors(recovery_strategy=DatabaseRecoveryStrategy.ROLLBACK_AND_RETRY)
    async def execute_with_recovery(self, operation: Callable):
        

# Centralized database error handling

```text

#

# 2. File Decomposition (CRITICAL Priority)

#

#

# 2.1 task_lifecycle.py Decomposition (8 hours)

**Problem**: 1132 lines, single class with 4 responsibilities

**Location**: `mcp_task_orchestrator/orchestrator/task_lifecycle.py`

**Fix**: Split into 4 focused services

**Implementation Plan**:

1. **Create**: `mcp_task_orchestrator/domain/services/stale_task_detection_service.py`

```text
python
class StaleTaskDetectionService:
    async def detect_stale_tasks(self) -> List[Task]:
        

# Move lines 81-252 from task_lifecycle.py

    
    async def _check_workflow_abandonment(self) -> bool:
        

# Move lines 153-205, split into smaller methods

```text

2. **Create**: `mcp_task_orchestrator/domain/services/task_archival_service.py`

```text
python
class TaskArchivalService:
    async def archive_task(self, task_id: str) -> ArchivalResult:
        

# Move lines 335-495, split into:

        

# - prepare_archive_data()

        

# - create_archive_record()

        

# - cleanup_original_task()

```text

3. **Create**: `mcp_task_orchestrator/domain/services/workspace_cleanup_service.py`

```text
python
class WorkspaceCleanupService:
    async def perform_workspace_cleanup(self) -> CleanupResult:
        

# Move lines 629-755, break down 76-line method

```text

4. **Create**: `mcp_task_orchestrator/domain/services/lifecycle_analytics_service.py`

```text
python
class LifecycleAnalyticsService:
    def generate_lifecycle_metrics(self) -> LifecycleMetrics:
        

# Move lines 1067-1132

```text

#

#

# 2.2 generic_models.py Decomposition (6 hours)

**Problem**: 828 lines, 25+ classes with mixed responsibilities

**Location**: `mcp_task_orchestrator/orchestrator/generic_models.py`

**Fix**: Split into domain-specific modules

**Implementation Plan**:

1. **Create**: `mcp_task_orchestrator/domain/entities/task_models.py`

```text
python

# Move Task, TaskAttribute, TaskDependency (lines 429-625)

```text

2. **Create**: `mcp_task_orchestrator/domain/entities/event_models.py`

```python

# Move TaskEvent, EventType enums (lines 94-379)

```text

3. **Create**: `mcp_task_orchestrator/domain/entities/artifact_models.py`

```python

# Move TaskArtifact, ArtifactType (lines 387-421)

```text

4. **Create**: `mcp_task_orchestrator/domain/entities/template_models.py`

```python

# Move TaskTemplate, TemplateParameter (lines 641-end)

```text

5. **Create**: `mcp_task_orchestrator/domain/value_objects/enums.py`

```python

# Move all enum definitions

```text

#

# 3. Type Safety Improvements (MEDIUM Priority)

#

#

# 3.1 Missing Pydantic Models for I/O (4 hours)

**Problem**: MCP handlers use `Dict[str, Any]` instead of typed models

**Fix**: Create comprehensive request/response DTOs

**Implementation**:

```python

# New file: mcp_task_orchestrator/application/dto/mcp_requests.py

class TaskPlanRequestDto(BaseModel):
    description: str
    complexity: ComplexityLevel
    subtasks_json: str
    context: Optional[str] = None

class TaskCompletionRequestDto(BaseModel):
    task_id: str
    summary: str
    detailed_work: str
    artifacts: List[str] = Field(default_factory=list)
    next_action: Literal["continue", "needs_revision", "blocked", "complete"]

# New file: mcp_task_orchestrator/application/dto/mcp_responses.py

class TaskPlanResponseDto(BaseModel):
    parent_task_id: str
    subtasks: List[SubTaskDto]
    total_subtasks: int
    complexity: ComplexityLevel
    estimated_completion_time: Optional[str] = None

class StatusResponseDto(BaseModel):
    active_tasks: List[TaskSummaryDto]
    completed_tasks: List[TaskSummaryDto]
    session_summary: SessionSummaryDto

```text

#

#

# 3.2 Missing Type Hints (2 hours)

**Locations**:

- `mcp_task_orchestrator/orchestrator/task_lifecycle.py` lines 289, 323

- `mcp_task_orchestrator/application/usecases/track_progress.py` lines 184, 204

**Fix**: Add complete type annotations

```text
python

# Before:

def _determine_recommended_action(self, task):
    

# ...

# After:

def _determine_recommended_action(self, task: Task) -> RecommendedAction:
    

# ...

```text

#

# 4. Clean Architecture Violations (HIGH Priority)

#

#

# 4.1 Remove Cross-Layer Dependencies (3 hours)

**Problem**: Presentation layer directly importing domain services

**Location**: `mcp_task_orchestrator/presentation/mcp_server.py`

**Fix**: Use dependency injection container

```text
python

# Before:

from ..domain.services import OrchestrationCoordinator

# After:

from ..infrastructure.di import ServiceContainer

class MCPServer:
    def __init__(self):
        self.container = ServiceContainer()
        self.orchestrator = self.container.resolve(OrchestrationCoordinator)
```text

#

# 5. Implementation Timeline

#

#

# Week 1: Critical Error Handling

- [ ] Consolidate retry logic using `@handle_errors` decorator (4h)

- [ ] Create centralized error response builder (2h)

- [ ] Refactor database error handling (3h)

#

#

# Week 2: File Decomposition

- [ ] Split `task_lifecycle.py` into 4 services (8h)

- [ ] Split `generic_models.py` into domain modules (6h)

#

#

# Week 3: Type Safety

- [ ] Create Pydantic request/response DTOs (4h)

- [ ] Add missing type hints (2h)

- [ ] Fix clean architecture violations (3h)

#

#

# Week 4: Testing & Validation

- [ ] Add tests for new error handling (4h)

- [ ] Validate all refactoring with existing tests (4h)

- [ ] Performance testing and optimization (2h)

#

# 6. Success Metrics

#

#

# Code Quality

- **Reduce file sizes**: All files under 500 lines

- **Eliminate duplication**: Remove 200+ lines of duplicate error handling

- **Improve type coverage**: 95%+ type annotation coverage on public APIs

#

#

# Maintainability

- **Single Responsibility**: Each class/module has one clear purpose

- **Clean Architecture**: No cross-layer dependencies

- **Testability**: All new services fully unit testable

#

#

# Performance

- **Error Recovery**: Consistent 100ms response time for error scenarios

- **Memory Usage**: 15% reduction from eliminating duplicate code

- **Startup Time**: No regression from architectural improvements

#

# 7. Risk Mitigation

#

#

# Backward Compatibility

- All refactoring maintains existing public APIs

- Gradual migration with feature flags where needed

- Comprehensive integration tests before each merge

#

#

# Testing Strategy

- Unit tests for all new services

- Integration tests for error handling workflows

- Performance regression tests

- Manual testing of MCP client interactions

#

#

# Rollback Plan

- Each week's changes can be independently rolled back

- Feature flags for new error handling infrastructure

- Monitoring alerts for error rate increases

#

# 8. Quick Wins (Immediate Actions)

These can be implemented in 1-2 hour increments:

1. **Extract `StaleTaskDetectionService`** from TaskLifecycleManager

2. **Create `ErrorResponseBuilder`** utility class

3. **Add type hints** to `track_progress.py` methods

4. **Split enums** from `generic_models.py` into separate file

5. **Replace manual retry** in `plan_task()` method with decorator

Each quick win provides immediate value and can be done without affecting other components.

---

*This refactoring plan prioritizes maintainability, type safety, and architectural cleanliness while maintaining backward compatibility and minimizing risk.*
