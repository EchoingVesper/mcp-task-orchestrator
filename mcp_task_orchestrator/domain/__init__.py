"""
Domain layer for MCP Task Orchestrator.

This layer contains the core business logic and abstractions that are 
independent of any infrastructure concerns. It defines the business 
entities, repository interfaces, and domain services.
"""

# Import entities
from .entities import (
    Task, TaskType, LifecycleStage,
    Specialist, SpecialistContext,
    OrchestrationSession, WorkItem
)

# Import value objects
from .value_objects import (
    TaskStatus, TaskComplexity, TaskPriority,
    SpecialistType, SpecialistCapability,
    ExecutionResult, ExecutionStatus,
    ArtifactReference,
    TimeWindow, Duration
)

# Import exceptions
from .exceptions import (
    OrchestrationError, TaskNotFoundError, TaskStateError,
    TaskDependencyError, TaskValidationError,
    SessionNotFoundError, SessionStateError,
    SpecialistNotFoundError, SpecialistAssignmentError,
    ArtifactError, ArtifactNotFoundError,
    WorkflowError, ConcurrencyError, ResourceExhaustedError
)

# Import repository interfaces
from .repositories import (
    TaskRepository, StateRepository, SpecialistRepository
)

# Import domain services
from .services import (
    TaskBreakdownService, SpecialistAssignmentService,
    ProgressTrackingService, ResultSynthesisService,
    OrchestrationCoordinator, TaskService
)

__all__ = [
    # Entities
    'Task', 'TaskType', 'LifecycleStage',
    'Specialist', 'SpecialistContext',
    'OrchestrationSession', 'WorkItem',
    
    # Value Objects
    'TaskStatus', 'TaskComplexity', 'TaskPriority',
    'SpecialistType', 'SpecialistCapability',
    'ExecutionResult', 'ExecutionStatus',
    'ArtifactReference',
    'TimeWindow', 'Duration',
    
    # Exceptions
    'OrchestrationError', 'TaskNotFoundError', 'TaskStateError',
    'TaskDependencyError', 'TaskValidationError',
    'SessionNotFoundError', 'SessionStateError',
    'SpecialistNotFoundError', 'SpecialistAssignmentError',
    'ArtifactError', 'ArtifactNotFoundError',
    'WorkflowError', 'ConcurrencyError', 'ResourceExhaustedError',
    
    # Repository Interfaces
    'TaskRepository', 'StateRepository', 'SpecialistRepository',
    
    # Domain Services
    'TaskBreakdownService', 'SpecialistAssignmentService',
    'ProgressTrackingService', 'ResultSynthesisService',
    'OrchestrationCoordinator', 'TaskService'
]