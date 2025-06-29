"""
Domain value objects for the MCP Task Orchestrator.

Value objects are immutable objects that represent domain concepts
without identity. They are compared by value rather than reference.
"""

from .task_status import TaskStatus, TaskComplexity, TaskPriority
from .specialist_type import SpecialistType, SpecialistCapability
from .execution_result import ExecutionResult, ExecutionStatus
from .artifact_reference import ArtifactReference, ArtifactType
from .time_window import TimeWindow, Duration

__all__ = [
    'TaskStatus',
    'TaskComplexity', 
    'TaskPriority',
    'SpecialistType',
    'SpecialistCapability',
    'ExecutionResult',
    'ExecutionStatus',
    'ArtifactReference',
    'ArtifactType',
    'TimeWindow',
    'Duration'
]