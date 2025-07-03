"""
Domain entities for the MCP Task Orchestrator.

Entities are the core business objects with unique identities.
They encapsulate business logic and maintain state.
"""

from .task import Task, TaskType, TaskStatus, LifecycleStage
from .specialist import Specialist, SpecialistContext
from .orchestration import OrchestrationSession, WorkItem

__all__ = [
    'Task',
    'TaskType',
    'TaskStatus', 
    'LifecycleStage',
    'Specialist',
    'SpecialistContext',
    'OrchestrationSession',
    'WorkItem'
]