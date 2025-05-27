"""
MCP Task Orchestrator Package

Provides task orchestration capabilities similar to Roo Code's Orchestrator mode,
optimized for single-session LLM interactions.
"""

from .core import TaskOrchestrator
from .models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, 
    ComplexityLevel, TaskResult
)
from .specialists import SpecialistManager
from .state import StateManager

__version__ = "0.1.0"
__all__ = [
    "TaskOrchestrator",
    "TaskBreakdown", 
    "SubTask",
    "TaskStatus",
    "SpecialistType",
    "ComplexityLevel", 
    "TaskResult",
    "SpecialistManager",
    "StateManager"
]
