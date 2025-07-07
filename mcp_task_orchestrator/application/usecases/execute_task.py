"""
Use case for executing tasks.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from ...domain import (
    TaskRepository,
    TaskService,
    SpecialistAssignmentService,
    Task,
    TaskStatus,
    OrchestrationError,
    TaskValidationError
)
from ..dto import ExecutionContextRequest, ExecutionContextResponse


@dataclass
class ExecuteTaskUseCase:
    """
    Application use case for executing tasks.
    
    This use case provides specialist context and instructions
    for task execution.
    """
    task_repository: TaskRepository
    task_service: TaskService
    specialist_service: SpecialistAssignmentService
    
    async def get_task_execution_context(self, task_id: str) -> ExecutionContextResponse:
        """
        Get execution context for a specific task.
        
        Args:
            task_id: ID of the task to execute
            
        Returns:
            ExecutionContextResponse with specialist context and instructions
            
        Raises:
            TaskValidationError: If the task is not ready for execution
            OrchestrationError: If context retrieval fails
        """
        try:
            # Retrieve task from repository
            task = await self.task_repository.get_by_id(task_id)
            if not task:
                raise TaskValidationError(
                    f"Task {task_id} not found",
                    {"task_id": task_id}
                )
            
            # Validate task is ready for execution
            validation_errors = self._validate_task_for_execution(task)
            if validation_errors:
                raise TaskValidationError(
                    f"Task {task_id} not ready for execution",
                    validation_errors
                )
            
            # Get specialist context for the task
            specialist_context = await self.specialist_service.get_specialist_context(
                specialist_type=task.specialist_type,
                task_description=task.description,
                task_context=task.context
            )
            
            # Generate execution instructions
            instructions = self._generate_execution_instructions(task, specialist_context)
            
            # Update task status to in_progress
            task.status = TaskStatus.IN_PROGRESS
            await self.task_repository.update(task)
            
            # Create response
            return ExecutionContextResponse(
                success=True,
                task_id=task_id,
                task_title=task.title,
                task_description=task.description,
                specialist_type=task.specialist_type.value,
                specialist_context=specialist_context.context,
                specialist_prompts=specialist_context.prompts,
                execution_instructions=instructions,
                dependencies_completed=self._check_dependencies_completed(task),
                estimated_effort=task.estimated_effort,
                next_steps=[
                    "Execute the task using the provided specialist context",
                    "Implement the solution following the execution instructions",
                    "Call orchestrator_complete_task when finished with detailed work"
                ]
            )
            
        except (TaskValidationError, OrchestrationError):
            raise
        except Exception as e:
            raise OrchestrationError(
                f"Failed to get execution context for task {task_id}: {str(e)}",
                {"task_id": task_id}
            )
    
    def _validate_task_for_execution(self, task: Task) -> Dict[str, str]:
        """Validate that task is ready for execution."""
        errors = {}
        
        # Check task status
        if task.status not in [TaskStatus.PENDING, TaskStatus.ACTIVE]:
            errors["status"] = f"Task must be PENDING or ACTIVE, but is {task.status.value}"
        
        # Check if already completed
        if task.status == TaskStatus.COMPLETED:
            errors["completed"] = "Task has already been completed"
        
        # Check if blocked
        if task.status == TaskStatus.BLOCKED:
            errors["blocked"] = "Task is currently blocked and cannot be executed"
        
        # Check dependencies
        if task.dependencies:
            incomplete_deps = [
                dep.dependency_task_id 
                for dep in task.dependencies 
                if dep.is_blocking and not dep.is_satisfied
            ]
            if incomplete_deps:
                errors["dependencies"] = f"Blocking dependencies not satisfied: {incomplete_deps}"
        
        return errors
    
    def _generate_execution_instructions(self, task: Task, specialist_context: Any) -> List[str]:
        """Generate specific execution instructions based on task and context."""
        instructions = [
            f"Task: {task.title}",
            f"Type: {task.task_type.value}",
            f"Complexity: {task.complexity.value}",
            ""
        ]
        
        # Add description
        instructions.append("Description:")
        instructions.append(task.description)
        instructions.append("")
        
        # Add specialist guidance
        instructions.append("Specialist Guidance:")
        for prompt in specialist_context.prompts:
            instructions.append(f"- {prompt}")
        instructions.append("")
        
        # Add context-specific instructions
        if task.context:
            instructions.append("Additional Context:")
            for key, value in task.context.items():
                instructions.append(f"- {key}: {value}")
            instructions.append("")
        
        # Add output requirements
        instructions.append("Expected Output:")
        instructions.append("- Implement the solution as described")
        instructions.append("- Provide detailed documentation of work done")
        instructions.append("- Include any code, analysis, or artifacts created")
        instructions.append("- Identify any issues or blockers encountered")
        
        return instructions
    
    def _check_dependencies_completed(self, task: Task) -> bool:
        """Check if all task dependencies are completed."""
        if not task.dependencies:
            return True
        
        return all(
            dep.is_satisfied or not dep.is_blocking
            for dep in task.dependencies
        )