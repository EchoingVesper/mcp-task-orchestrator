"""
Task Breakdown Service - Domain Service

This service handles the decomposition of complex tasks into hierarchical subtasks
using the Task model (replacing legacy TaskBreakdown/SubTask models).
"""

import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..repositories import TaskRepository, StateRepository, SpecialistRepository
from ..value_objects.task_status import TaskStatus
from ..value_objects.complexity_level import ComplexityLevel
from ..value_objects.flexible_specialist_type import validate_specialist_type
from ..entities.task import Task, TaskType, LifecycleStage, DependencyType


class TaskBreakdownService:
    """
    Service for breaking down complex tasks into subtasks.
    
    This service encapsulates the logic for task decomposition,
    dependency analysis, and initial task planning using the
    unified Task model.
    """
    
    def __init__(self, 
                 task_repository: TaskRepository,
                 state_repository: StateRepository,
                 specialist_repository: SpecialistRepository):
        """
        Initialize the task breakdown service.
        
        Args:
            task_repository: Repository for task operations
            state_repository: Repository for state management
            specialist_repository: Repository for specialist operations
        """
        self.task_repo = task_repository
        self.state_repo = state_repository
        self.specialist_repo = specialist_repository
    
    async def plan_task(self, 
                       description: str, 
                       complexity: str, 
                       subtasks_json: str, 
                       context: str = "",
                       session_id: Optional[str] = None) -> Task:
        """
        Create a task breakdown from LLM-provided subtasks.
        
        Args:
            description: Main task description
            complexity: Task complexity level
            subtasks_json: JSON string containing subtask definitions
            context: Additional context for the task
            session_id: Optional session ID for tracking
            
        Returns:
            Task object with planned subtasks as children
        """
        # Parse subtasks JSON
        try:
            subtasks_data = json.loads(subtasks_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid subtasks JSON: {e}")
        
        # Create main task
        main_task_id = f"task_{uuid.uuid4().hex[:8]}"
        main_task = Task(
            task_id=main_task_id,
            title=description[:100],  # First 100 chars as title
            description=description,
            task_type=TaskType.BREAKDOWN,
            hierarchy_path=f"/{main_task_id}",
            hierarchy_level=0,
            status=TaskStatus.PENDING,
            lifecycle_stage=LifecycleStage.PLANNING,
            complexity=ComplexityLevel(complexity.lower()),
            context={"original_context": context, "session_id": session_id} if context else {"session_id": session_id}
        )
        
        # Process subtasks
        for i, subtask_data in enumerate(subtasks_data):
            subtask = self._create_subtask(
                subtask_data, 
                main_task_id,
                main_task.hierarchy_path,
                i
            )
            main_task.children.append(subtask)
            
            # Add dependencies if specified
            dependencies = subtask_data.get('dependencies', [])
            for dep_data in dependencies:
                # For now, we'll just store dependency info in context
                # Full dependency resolution would happen when tasks are persisted
                if 'dependencies' not in subtask.context:
                    subtask.context['dependencies'] = []
                subtask.context['dependencies'].append(dep_data)
        
        # Set main task status to planned
        main_task.status = TaskStatus.PENDING
        main_task.lifecycle_stage = LifecycleStage.READY
        
        return main_task
    
    def _create_subtask(self, 
                       subtask_data: Dict[str, Any], 
                       parent_id: str,
                       parent_path: str,
                       position: int) -> Task:
        """
        Create a Task subtask from data.
        
        Args:
            subtask_data: Dictionary containing subtask information
            parent_id: Parent task ID
            parent_path: Parent task hierarchy path
            position: Position in parent task
            
        Returns:
            Task object
        """
        # Generate subtask ID
        subtask_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Extract basic information
        title = subtask_data.get('title', 'Untitled Subtask')
        description = subtask_data.get('description', '')
        specialist_type = subtask_data.get('specialist_type', 'generic')
        estimated_effort = subtask_data.get('estimated_effort', 'Unknown')
        
        # Validate specialist type
        if not validate_specialist_type(specialist_type):
            # Log warning but allow the task to be created
            import logging
            logging.getLogger(__name__).warning(f"Unknown specialist type: {specialist_type}")
        
        # Build hierarchy path
        hierarchy_path = f"{parent_path}/{subtask_id}"
        hierarchy_level = len(hierarchy_path.split('/')) - 2
        
        # Create subtask
        subtask = Task(
            task_id=subtask_id,
            parent_task_id=parent_id,
            title=title,
            description=description,
            task_type=TaskType.STANDARD,
            hierarchy_path=hierarchy_path,
            hierarchy_level=hierarchy_level,
            position_in_parent=position,
            status=TaskStatus.PENDING,
            lifecycle_stage=LifecycleStage.CREATED,
            specialist_type=specialist_type,
            estimated_effort=estimated_effort,
            context={}
        )
        
        return subtask
    
    async def analyze_task_complexity(self, description: str, context: str = "") -> str:
        """
        Analyze task complexity based on description and context.
        
        Args:
            description: Task description
            context: Additional context
            
        Returns:
            Complexity level string
        """
        # Simple heuristic-based complexity analysis
        # In a real implementation, this might use ML or more sophisticated analysis
        
        word_count = len(description.split())
        context_complexity = len(context.split()) if context else 0
        
        # Keywords that indicate complexity
        complex_keywords = [
            'integrate', 'architecture', 'design', 'refactor', 'migrate',
            'optimize', 'scale', 'implement', 'algorithm', 'machine learning',
            'database', 'api', 'microservice', 'distributed', 'concurrent'
        ]
        
        complexity_score = 0
        
        # Base score from word count
        if word_count > 100:
            complexity_score += 3
        elif word_count > 50:
            complexity_score += 2
        elif word_count > 20:
            complexity_score += 1
        
        # Context complexity
        complexity_score += min(context_complexity // 50, 2)
        
        # Keyword analysis
        description_lower = description.lower()
        keyword_matches = sum(1 for keyword in complex_keywords if keyword in description_lower)
        complexity_score += min(keyword_matches, 3)
        
        # Determine complexity level
        if complexity_score >= 6:
            return "very_complex"
        elif complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "moderate"
        else:
            return "simple"
    
    async def estimate_effort(self, subtasks: List[Task]) -> Dict[str, Any]:
        """
        Estimate total effort for a task breakdown.
        
        Args:
            subtasks: List of subtasks
            
        Returns:
            Dictionary with effort estimates
        """
        # Simple effort estimation
        # In practice, this might use historical data or ML models
        
        effort_map = {
            "simple": 1,
            "moderate": 3,
            "complex": 8,
            "very_complex": 21
        }
        
        total_points = 0
        effort_breakdown = {}
        
        for subtask in subtasks:
            complexity = subtask.complexity.value if hasattr(subtask.complexity, 'value') else str(subtask.complexity)
            points = effort_map.get(complexity, 3)
            total_points += points
            
            specialist = subtask.specialist_type or 'generic'
            if specialist not in effort_breakdown:
                effort_breakdown[specialist] = 0
            effort_breakdown[specialist] += points
        
        return {
            "total_story_points": total_points,
            "estimated_hours": total_points * 4,  # Rough conversion
            "effort_by_specialist": effort_breakdown,
            "estimated_duration_days": max(1, total_points // 3)
        }