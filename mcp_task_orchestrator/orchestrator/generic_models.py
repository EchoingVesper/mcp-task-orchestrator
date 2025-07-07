"""
Task Model - Consolidated exports for v2.0

This module now serves as a consolidated export point for the task system models
that have been decomposed into focused domain modules for better maintainability.

The original 828-line file has been decomposed into:
- domain/entities/task_models.py - Core Task entity and related models
- domain/entities/template_models.py - Task template system  
- domain/entities/lifecycle_models.py - Lifecycle state machine
- domain/value_objects/enums.py - All enum definitions

This provides better separation of concerns, improved maintainability,
and aligns with Clean Architecture principles.
"""

# Import all models from their new locations
from ..domain.entities.task_models import (
    Task, TaskAttribute, TaskDependency, TaskEvent, TaskArtifact
)
from ..domain.entities.template_models import (
    TaskTemplate, TemplateParameter
)
from ..domain.entities.lifecycle_models import (
    LifecycleStateMachine
)
from ..domain.value_objects.enums import (
    TaskType,
    TaskStatus,
    LifecycleStage,
    DependencyType,
    DependencyStatus,
    QualityGateLevel,
    EventType,
    EventCategory,
    AttributeType,
    ArtifactType
)
from ..domain.value_objects.complexity_level import ComplexityLevel
from ..domain.value_objects.flexible_specialist_type import validate_specialist_type

# Re-export everything for backward compatibility
__all__ = [
    # Main entities
    'Task',
    'TaskAttribute', 
    'TaskDependency',
    'TaskEvent',
    'TaskArtifact',
    'TaskTemplate',
    'TemplateParameter',
    'LifecycleStateMachine',
    
    # Enums
    'TaskType',
    'TaskStatus', 
    'LifecycleStage',
    'DependencyType',
    'DependencyStatus',
    'QualityGateLevel',
    'EventType',
    'EventCategory',
    'AttributeType',
    'ArtifactType',
    
    # Value objects
    'ComplexityLevel',
    'validate_specialist_type',
    
    # Legacy aliases
    'GenericTask'
]

# Maintain backward compatibility by creating aliases for legacy code
GenericTask = Task  # Alias for legacy code that imports GenericTask