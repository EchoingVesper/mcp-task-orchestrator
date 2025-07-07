"""
Use case for completing tasks.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from ...domain import (
    TaskRepository,
    TaskService,
    ArtifactService,
    Task,
    TaskStatus,
    ExecutionResult,
    ArtifactReference,
    OrchestrationError,
    TaskValidationError
)
from ..dto import TaskCompletionRequest, TaskCompletionResponse


@dataclass
class CompleteTaskUseCase:
    """
    Application use case for completing tasks.
    
    This use case handles task completion with artifact storage
    to prevent context limit issues.
    """
    task_repository: TaskRepository
    task_service: TaskService
    artifact_service: ArtifactService
    
    async def complete_task_with_artifacts(self, 
                                          task_id: str, 
                                          completion_data: Dict[str, Any]) -> TaskCompletionResponse:
        """
        Complete a task and store detailed work as artifacts.
        
        Args:
            task_id: ID of the task to complete
            completion_data: Completion data including summary, detailed work, etc.
            
        Returns:
            TaskCompletionResponse with completion status and artifact references
            
        Raises:
            TaskValidationError: If completion data is invalid
            OrchestrationError: If completion fails
        """
        try:
            # Retrieve task from repository
            task = await self.task_repository.get_by_id(task_id)
            if not task:
                raise TaskValidationError(
                    f"Task {task_id} not found",
                    {"task_id": task_id}
                )
            
            # Validate completion data
            validation_errors = self._validate_completion_data(completion_data)
            if validation_errors:
                raise TaskValidationError(
                    "Invalid completion data",
                    validation_errors
                )
            
            # Validate task can be completed
            if task.status != TaskStatus.IN_PROGRESS:
                raise TaskValidationError(
                    f"Task must be IN_PROGRESS to complete, but is {task.status.value}",
                    {"task_id": task_id, "status": task.status.value}
                )
            
            # Store detailed work as artifacts
            artifact_refs = await self._store_work_artifacts(
                task_id,
                completion_data.get("detailed_work", ""),
                completion_data.get("artifact_type", "general"),
                completion_data.get("file_paths", [])
            )
            
            # Create execution result
            execution_result = ExecutionResult(
                success=True,
                summary=completion_data["summary"],
                detailed_output=f"Work stored in {len(artifact_refs)} artifacts",
                artifacts_created=artifact_refs,
                metrics={
                    "completion_time": datetime.utcnow().isoformat(),
                    "artifact_count": len(artifact_refs),
                    "next_action": completion_data.get("next_action", "complete")
                }
            )
            
            # Update task with completion
            task.status = TaskStatus.COMPLETED
            task.execution_result = execution_result
            task.completed_at = datetime.utcnow()
            
            # Handle legacy artifacts field if provided
            if completion_data.get("legacy_artifacts"):
                task.artifacts.extend(completion_data["legacy_artifacts"])
            
            # Save updated task
            await self.task_repository.update(task)
            
            # Determine next steps based on next_action
            next_steps = self._determine_next_steps(
                completion_data.get("next_action", "complete"),
                task
            )
            
            # Create response
            return TaskCompletionResponse(
                success=True,
                task_id=task_id,
                message=f"Task '{task.title}' completed successfully",
                summary=completion_data["summary"],
                artifact_count=len(artifact_refs),
                artifact_references=[ref.to_dict() for ref in artifact_refs],
                next_action=completion_data.get("next_action", "complete"),
                next_steps=next_steps,
                completion_time=datetime.utcnow().isoformat()
            )
            
        except (TaskValidationError, OrchestrationError):
            raise
        except Exception as e:
            raise OrchestrationError(
                f"Failed to complete task {task_id}: {str(e)}",
                {"task_id": task_id}
            )
    
    def _validate_completion_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Validate task completion data."""
        errors = {}
        
        # Required fields
        if not data.get("summary"):
            errors["summary"] = "Summary is required for task completion"
        
        if not data.get("detailed_work"):
            errors["detailed_work"] = "Detailed work content is required"
        
        if not data.get("next_action"):
            errors["next_action"] = "Next action is required (continue/needs_revision/blocked/complete)"
        
        # Validate next_action value
        valid_actions = ["continue", "needs_revision", "blocked", "complete"]
        if data.get("next_action") not in valid_actions:
            errors["next_action"] = f"Invalid next_action. Must be one of: {valid_actions}"
        
        # Validate artifact_type if provided
        if data.get("artifact_type"):
            valid_types = ["code", "documentation", "analysis", "design", "test", "config", "general"]
            if data["artifact_type"] not in valid_types:
                errors["artifact_type"] = f"Invalid artifact_type. Must be one of: {valid_types}"
        
        return errors
    
    async def _store_work_artifacts(self, 
                                   task_id: str, 
                                   detailed_work: str,
                                   artifact_type: str,
                                   file_paths: List[str]) -> List[ArtifactReference]:
        """Store detailed work as artifacts to prevent context limits."""
        artifacts = []
        
        # Split work into chunks if it's very large (>10K chars)
        chunk_size = 10000
        if len(detailed_work) > chunk_size:
            chunks = [detailed_work[i:i+chunk_size] 
                     for i in range(0, len(detailed_work), chunk_size)]
        else:
            chunks = [detailed_work]
        
        # Store each chunk as an artifact
        for i, chunk in enumerate(chunks):
            artifact_ref = await self.artifact_service.store_artifact(
                task_id=task_id,
                content=chunk,
                artifact_type=artifact_type,
                metadata={
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_paths": file_paths if i == 0 else [],
                    "stored_at": datetime.utcnow().isoformat()
                }
            )
            artifacts.append(artifact_ref)
        
        return artifacts
    
    def _determine_next_steps(self, next_action: str, task: Task) -> List[str]:
        """Determine next steps based on the next action."""
        if next_action == "complete":
            return [
                "Task has been marked as completed",
                "Review the stored artifacts for detailed work",
                "Check if any dependent tasks can now be started"
            ]
        elif next_action == "continue":
            return [
                "Task work has been saved but more work is needed",
                "Continue with the next phase of implementation",
                "Use orchestrator_execute_task to resume work"
            ]
        elif next_action == "needs_revision":
            return [
                "Task needs revision based on completion attempt",
                "Review the stored work and feedback",
                "Update task requirements and re-execute"
            ]
        elif next_action == "blocked":
            return [
                "Task is blocked and cannot proceed",
                "Identify and resolve the blocking issues",
                "Update task status when blockers are resolved"
            ]
        else:
            return ["Task completion processed"]