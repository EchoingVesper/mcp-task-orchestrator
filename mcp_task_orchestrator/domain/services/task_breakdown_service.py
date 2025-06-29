"""
Task Breakdown Service - Handles task decomposition and planning.

This service is responsible for analyzing complex tasks and breaking them
down into manageable subtasks with proper dependencies and assignments.
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..repositories import TaskRepository, StateRepository, SpecialistRepository
from ...orchestrator.models import (
    TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel
)


class TaskBreakdownService:
    """
    Service for breaking down complex tasks into subtasks.
    
    This service encapsulates the logic for task decomposition,
    dependency analysis, and initial task planning.
    """
    
    def __init__(self, 
                 task_repository: TaskRepository,
                 state_repository: StateRepository,
                 specialist_repository: SpecialistRepository):
        """
        Initialize the task breakdown service.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
            specialist_repository: Repository for specialist management
        """
        self.task_repo = task_repository
        self.state_repo = state_repository
        self.specialist_repo = specialist_repository
    
    async def plan_task(self, 
                       description: str, 
                       complexity: str, 
                       subtasks_json: str, 
                       context: str = "",
                       session_id: Optional[str] = None) -> TaskBreakdown:
        """
        Create a task breakdown from LLM-provided subtasks.
        
        Args:
            description: Main task description
            complexity: Task complexity level
            subtasks_json: JSON string containing subtask definitions
            context: Additional context for the task
            session_id: Optional session ID for tracking
            
        Returns:
            TaskBreakdown object with planned subtasks
        """
        # Parse subtasks JSON
        try:
            subtasks_data = json.loads(subtasks_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid subtasks JSON: {e}")
        
        # Create main task
        main_task_id = str(uuid.uuid4())
        main_task = TaskBreakdown(
            id=main_task_id,
            description=description,
            complexity_level=ComplexityLevel(complexity.lower()),
            subtasks=[],
            dependencies={},
            estimated_effort=0
        )
        
        # Create session if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            await self._create_session(session_id, description)
        
        # Create main task in repository
        self.task_repo.create_task({
            'id': main_task_id,
            'session_id': session_id,
            'title': description[:100],  # First 100 chars as title
            'description': description,
            'type': 'main',
            'status': 'planning',
            'metadata': {
                'complexity': complexity,
                'context': context
            }
        })
        
        # Process subtasks
        subtask_mapping = {}  # For tracking dependencies
        
        for subtask_data in subtasks_data:
            subtask = self._create_subtask(
                subtask_data, 
                main_task_id,
                session_id
            )
            main_task.subtasks.append(subtask)
            subtask_mapping[subtask_data.get('id', subtask.id)] = subtask.id
            
            # Persist subtask
            self.task_repo.create_task({
                'id': subtask.id,
                'session_id': session_id,
                'parent_task_id': main_task_id,
                'title': subtask.title,
                'description': subtask.description,
                'type': 'subtask',
                'status': subtask.status.value,
                'metadata': {
                    'specialist': subtask.assigned_specialist.value,
                    'estimated_effort': subtask.estimated_effort,
                    'complexity': subtask.complexity.value
                }
            })
        
        # Process dependencies
        for subtask_data in subtasks_data:
            subtask_id = subtask_mapping.get(subtask_data.get('id'))
            dependencies = subtask_data.get('dependencies', [])
            
            if subtask_id and dependencies:
                main_task.dependencies[subtask_id] = []
                
                for dep_id in dependencies:
                    if dep_id in subtask_mapping:
                        actual_dep_id = subtask_mapping[dep_id]
                        main_task.dependencies[subtask_id].append(actual_dep_id)
                        
                        # Record dependency in repository
                        self.task_repo.add_task_dependency(
                            subtask_id, 
                            actual_dep_id
                        )
        
        # Calculate total estimated effort
        main_task.estimated_effort = sum(
            subtask.estimated_effort for subtask in main_task.subtasks
        )
        
        # Update main task status
        self.task_repo.update_task_status(main_task_id, 'planned')
        
        # Record planning event
        self.state_repo.record_event(
            session_id,
            'task_planned',
            {
                'task_id': main_task_id,
                'subtask_count': len(main_task.subtasks),
                'total_effort': main_task.estimated_effort
            }
        )
        
        return main_task
    
    def _create_subtask(self, 
                       subtask_data: Dict[str, Any], 
                       parent_id: str,
                       session_id: str) -> SubTask:
        """
        Create a SubTask object from data.
        
        Args:
            subtask_data: Dictionary containing subtask information
            parent_id: Parent task ID
            session_id: Session ID
            
        Returns:
            SubTask object
        """
        subtask_id = str(uuid.uuid4())
        
        # Determine specialist type
        specialist_str = subtask_data.get('specialist', 'implementer').lower()
        try:
            specialist = SpecialistType(specialist_str)
        except ValueError:
            specialist = SpecialistType.IMPLEMENTER
        
        # Determine complexity
        complexity_str = subtask_data.get('complexity', 'medium').lower()
        try:
            complexity = ComplexityLevel(complexity_str)
        except ValueError:
            complexity = ComplexityLevel.MEDIUM
        
        return SubTask(
            id=subtask_id,
            parent_id=parent_id,
            title=subtask_data.get('title', 'Untitled Task'),
            description=subtask_data.get('description', ''),
            assigned_specialist=specialist,
            complexity=complexity,
            estimated_effort=subtask_data.get('estimated_effort', 1),
            status=TaskStatus.PENDING,
            dependencies=[]  # Will be set later
        )
    
    async def _create_session(self, session_id: str, description: str):
        """Create a new session for task tracking."""
        self.state_repo.save_session(session_id, {
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'metadata': {
                'main_task_description': description
            }
        })
    
    async def validate_breakdown(self, breakdown: TaskBreakdown) -> List[str]:
        """
        Validate a task breakdown for issues.
        
        Args:
            breakdown: TaskBreakdown to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for circular dependencies
        if self._has_circular_dependencies(breakdown.dependencies):
            errors.append("Circular dependencies detected")
        
        # Check for orphaned dependencies
        task_ids = {task.id for task in breakdown.subtasks}
        for task_id, deps in breakdown.dependencies.items():
            if task_id not in task_ids:
                errors.append(f"Dependencies defined for non-existent task: {task_id}")
            
            for dep_id in deps:
                if dep_id not in task_ids:
                    errors.append(f"Dependency references non-existent task: {dep_id}")
        
        # Check for reasonable effort estimates
        for task in breakdown.subtasks:
            if task.estimated_effort <= 0:
                errors.append(f"Task '{task.title}' has invalid effort estimate")
            elif task.estimated_effort > 100:
                errors.append(f"Task '{task.title}' has unreasonably high effort estimate")
        
        # Check for specialist availability
        for task in breakdown.subtasks:
            specialist_type = task.assigned_specialist.value
            specialists = self.specialist_repo.list_specialists(
                category=specialist_type,
                active_only=True
            )
            if not specialists:
                errors.append(f"No active specialist available for type: {specialist_type}")
        
        return errors
    
    def _has_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> bool:
        """Check if the dependency graph has cycles."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependencies:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False