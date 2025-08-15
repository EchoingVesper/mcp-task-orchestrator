"""
Use case for orchestrating tasks.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from ...domain import (
    Task,
    OrchestrationError,
    TaskValidationError
)
from ...domain.services.orchestration_coordinator import OrchestrationCoordinator
from ..dto import TaskPlanRequest, TaskPlanResponse


@dataclass
class OrchestrateTaskUseCase:
    """
    Application use case for orchestrating complex tasks.
    
    This use case coordinates the planning and execution of tasks
    using the domain services.
    """
    coordinator: OrchestrationCoordinator
    
    async def plan_task(self, request: TaskPlanRequest) -> TaskPlanResponse:
        """
        Plan a complex task by breaking it down into subtasks.
        
        Args:
            request: Task planning request with description and metadata
            
        Returns:
            TaskPlanResponse with the breakdown and execution plan
            
        Raises:
            TaskValidationError: If the request is invalid
            OrchestrationError: If planning fails
        """
        try:
            # Validate request
            validation_errors = self._validate_request(request)
            if validation_errors:
                raise TaskValidationError(
                    "Invalid task plan request",
                    validation_errors
                )
            
            # Use coordinator to create task breakdown
            breakdown = await self.coordinator.plan_task(
                description=request.description,
                complexity=request.complexity_level,
                subtasks_json=request.subtasks_json,
                context=request.context
            )
            
            # Convert to response DTO
            return TaskPlanResponse(
                success=True,
                parent_task_id=breakdown.parent_task_id,
                description=breakdown.description,
                complexity=breakdown.complexity.value,
                subtasks=[
                    {
                        'task_id': st.task_id,
                        'title': st.title,
                        'description': st.description,
                        'specialist_type': st.specialist_type,
                        'dependencies': st.dependencies,
                        'estimated_effort': st.estimated_effort
                    }
                    for st in breakdown.subtasks
                ],
                execution_order=self._calculate_execution_order(breakdown),
                estimated_duration=self._estimate_duration(breakdown)
            )
            
        except (TaskValidationError, OrchestrationError):
            raise
        except Exception as e:
            raise OrchestrationError(
                f"Failed to plan task: {str(e)}",
                {"request": request.__dict__}
            )
    
    def _validate_request(self, request: TaskPlanRequest) -> list[str]:
        """Validate the task plan request."""
        errors = []
        
        if not request.description:
            errors.append("Task description is required")
        
        if len(request.description) < 10:
            errors.append("Task description must be at least 10 characters")
        
        if request.subtasks_json:
            try:
                import json
                json.loads(request.subtasks_json)
            except json.JSONDecodeError:
                errors.append("Invalid subtasks JSON format")
        
        return errors
    
    def _calculate_execution_order(self, breakdown: Task) -> list[list[str]]:
        """Calculate optimal execution order for subtasks."""
        levels = breakdown.get_execution_order()
        return [[st.task_id for st in level] for level in levels]
    
    def _estimate_duration(self, breakdown: Task) -> int:
        """Estimate total duration in minutes."""
        # Simple estimation based on complexity
        base_duration = breakdown.complexity.expected_duration_minutes
        subtask_factor = len(breakdown.subtasks) * 0.5
        return int(base_duration * (1 + subtask_factor))