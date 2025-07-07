"""
Domain services for MCP Task Orchestrator.

This package contains domain services that implement business logic
using the repository interfaces, keeping the domain layer independent
of infrastructure concerns.
"""

from .task_service import TaskService
from .task_breakdown_service import TaskBreakdownService
from .specialist_assignment_service import SpecialistAssignmentService
from .progress_tracking_service import ProgressTrackingService
from .result_synthesis_service import ResultSynthesisService
from .orchestration_coordinator import OrchestrationCoordinator

__all__ = [
    'TaskService',
    'TaskBreakdownService',
    'SpecialistAssignmentService',
    'ProgressTrackingService',
    'ResultSynthesisService',
    'OrchestrationCoordinator'
]