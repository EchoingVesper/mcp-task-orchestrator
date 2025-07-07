"""
Legacy models - DEPRECATED

This module previously contained legacy TaskBreakdown and SubTask models.
All functionality has been migrated to the unified Task model.

Use the Task model from domain.entities.task instead:
    from ..domain.entities.task import Task, TaskType, TaskStatus

Legacy models SubTask, TaskBreakdown, and TaskResult have been removed.
The Task model is now properly located in the domain layer following Clean Architecture.
"""

# Re-export from domain layer for backward compatibility
from ..domain.entities.task import Task, TaskType, TaskStatus, LifecycleStage
from ..domain.value_objects.specialist_type import SpecialistType
from ..domain.value_objects.complexity_level import ComplexityLevel

# Export common types
__all__ = [
    'Task', 
    'TaskType', 
    'TaskStatus', 
    'LifecycleStage',
    'SpecialistType',
    'ComplexityLevel'
]