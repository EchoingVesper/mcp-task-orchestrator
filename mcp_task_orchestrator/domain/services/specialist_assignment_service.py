"""
Specialist Assignment Service - Handles specialist role assignment and context generation.

This service is responsible for matching tasks with appropriate specialists
and generating the context needed for specialists to complete their work.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..repositories import TaskRepository, StateRepository, SpecialistRepository
from ..value_objects.specialist_type import SpecialistType
from ..value_objects.task_status import TaskStatus
from ...orchestrator.role_loader import get_roles


class SpecialistAssignmentService:
    """
    Service for assigning specialists to tasks and generating context.
    
    This service encapsulates the logic for specialist selection,
    context preparation, and assignment tracking.
    """
    
    def __init__(self,
                 task_repository: TaskRepository,
                 state_repository: StateRepository,
                 specialist_repository: SpecialistRepository,
                 project_dir: Optional[str] = None):
        """
        Initialize the specialist assignment service.
        
        Args:
            task_repository: Repository for task persistence
            state_repository: Repository for state persistence
            specialist_repository: Repository for specialist management
            project_dir: Project directory for loading custom roles
        """
        self.task_repo = task_repository
        self.state_repo = state_repository
        self.specialist_repo = specialist_repository
        self.project_dir = project_dir
        self._roles_cache = None
    
    async def get_specialist_context(self, task_id: str) -> str:
        """
        Generate context for a specialist to work on a specific task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Context string for the specialist
            
        Raises:
            ValueError: If task not found or invalid
        """
        # Get task details
        task = self.task_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Get parent task for additional context
        parent_task = None
        if task.get('parent_task_id'):
            parent_task = self.task_repo.get_task(task['parent_task_id'])
        
        # Get specialist type from task metadata
        specialist_type = task.get('metadata', {}).get('specialist', 'implementer')
        
        # Get role definition
        role_def = self._get_role_definition(specialist_type)
        
        # Get dependencies context
        dependencies_context = await self._get_dependencies_context(task_id)
        
        # Get any existing artifacts
        artifacts = self.task_repo.get_task_artifacts(task_id)
        artifacts_context = self._format_artifacts_context(artifacts)
        
        # Build specialist context
        context_parts = []
        
        # Role introduction
        if role_def:
            context_parts.append(f"Role: {role_def.get('name', specialist_type.title())}")
            
            if 'expertise' in role_def:
                context_parts.append("\nExpertise:")
                for expertise in role_def['expertise']:
                    context_parts.append(f"- {expertise}")
            
            if 'approach' in role_def:
                context_parts.append("\nApproach:")
                for approach in role_def['approach']:
                    context_parts.append(f"- {approach}")
        
        # Task context
        context_parts.append(f"\n\nTask: {task.get('title', 'Untitled')}")
        
        if task.get('description'):
            context_parts.append(f"\nDescription: {task['description']}")
        
        # Parent task context
        if parent_task:
            context_parts.append(f"\n\nParent Task: {parent_task.get('title', 'Untitled')}")
            if parent_task.get('description'):
                context_parts.append(f"Context: {parent_task['description']}")
        
        # Dependencies
        if dependencies_context:
            context_parts.append(f"\n\nDependencies:\n{dependencies_context}")
        
        # Existing work
        if artifacts_context:
            context_parts.append(f"\n\nExisting Work:\n{artifacts_context}")
        
        # Additional metadata
        metadata = task.get('metadata', {})
        if metadata:
            relevant_metadata = {
                k: v for k, v in metadata.items() 
                if k not in ['specialist', 'session_id']
            }
            if relevant_metadata:
                context_parts.append(f"\n\nAdditional Context:")
                for key, value in relevant_metadata.items():
                    context_parts.append(f"- {key}: {value}")
        
        # Completion criteria
        context_parts.append("\n\nTo complete this task successfully:")
        context_parts.append("1. Review the task description and any dependencies")
        context_parts.append("2. Apply your specialized expertise to solve the problem")
        context_parts.append("3. Provide clear, well-structured output")
        context_parts.append("4. Include any relevant artifacts or code")
        
        # Record context generation
        self.state_repo.record_event(
            task.get('session_id'),
            'specialist_context_generated',
            {
                'task_id': task_id,
                'specialist_type': specialist_type
            }
        )
        
        return "\n".join(context_parts)
    
    async def assign_specialist(self, 
                              task_id: str, 
                              specialist_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Assign a specialist to a task.
        
        Args:
            task_id: Task to assign
            specialist_type: Optional override for specialist type
            
        Returns:
            Assignment details including specialist info
        """
        # Get task
        task = self.task_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Determine specialist type
        if not specialist_type:
            specialist_type = task.get('metadata', {}).get('specialist', 'implementer')
        
        # Get recommended specialist
        specialist_id = self.specialist_repo.get_recommended_specialist(
            task_type=task.get('type', 'generic'),
            task_context={
                'complexity': task.get('metadata', {}).get('complexity', 'medium'),
                'description': task.get('description', '')
            }
        )
        
        # If no recommendation, get any available specialist of the type
        if not specialist_id:
            specialists = self.specialist_repo.list_specialists(
                category=specialist_type,
                active_only=True,
                limit=1
            )
            if specialists:
                specialist_id = specialists[0]['id']
        
        # Create or get specialist if needed
        if not specialist_id:
            specialist_id = await self._create_default_specialist(specialist_type)
        
        # Record assignment
        assignment = {
            'task_id': task_id,
            'specialist_id': specialist_id,
            'specialist_type': specialist_type,
            'assigned_at': datetime.utcnow().isoformat()
        }
        
        # Update task metadata
        metadata = task.get('metadata', {})
        metadata['assigned_specialist_id'] = specialist_id
        metadata['assignment_timestamp'] = assignment['assigned_at']
        
        self.task_repo.update_task(task_id, {'metadata': metadata})
        
        # Record usage
        self.specialist_repo.record_specialist_usage(
            specialist_id,
            task_id,
            {'assignment_type': 'automatic'}
        )
        
        # Record event
        self.state_repo.record_event(
            task.get('session_id'),
            'specialist_assigned',
            assignment
        )
        
        return assignment
    
    def _get_role_definition(self, specialist_type: str) -> Optional[Dict[str, Any]]:
        """Get role definition from configuration."""
        if self._roles_cache is None:
            self._roles_cache = get_roles(self.project_dir) or {}
        
        # Try exact match
        if specialist_type in self._roles_cache:
            return self._roles_cache[specialist_type]
        
        # Try with _specialist suffix
        specialist_key = f"{specialist_type}_specialist"
        if specialist_key in self._roles_cache:
            return self._roles_cache[specialist_key]
        
        # Return default definition
        return self._get_default_role_definition(specialist_type)
    
    def _get_default_role_definition(self, specialist_type: str) -> Dict[str, Any]:
        """Get default role definition for common specialist types."""
        defaults = {
            'architect': {
                'name': 'Software Architect',
                'expertise': [
                    'System design and architecture',
                    'Design patterns and best practices',
                    'Technology selection and evaluation',
                    'Scalability and performance planning'
                ],
                'approach': [
                    'Analyze requirements and constraints',
                    'Design modular and maintainable solutions',
                    'Consider non-functional requirements',
                    'Document architectural decisions'
                ]
            },
            'implementer': {
                'name': 'Software Developer',
                'expertise': [
                    'Writing clean, efficient code',
                    'Implementing features and functionality',
                    'Following coding standards',
                    'Unit testing and debugging'
                ],
                'approach': [
                    'Understand requirements thoroughly',
                    'Write well-structured code',
                    'Include appropriate error handling',
                    'Add comments and documentation'
                ]
            },
            'debugger': {
                'name': 'Debug Specialist',
                'expertise': [
                    'Identifying and fixing bugs',
                    'Performance optimization',
                    'Root cause analysis',
                    'Testing and validation'
                ],
                'approach': [
                    'Reproduce and isolate issues',
                    'Analyze error messages and logs',
                    'Apply systematic debugging techniques',
                    'Verify fixes do not introduce new issues'
                ]
            },
            'reviewer': {
                'name': 'Code Reviewer',
                'expertise': [
                    'Code quality assessment',
                    'Best practices enforcement',
                    'Security review',
                    'Performance analysis'
                ],
                'approach': [
                    'Review code for correctness',
                    'Check adherence to standards',
                    'Identify potential issues',
                    'Provide constructive feedback'
                ]
            },
            'tester': {
                'name': 'QA Specialist',
                'expertise': [
                    'Test planning and design',
                    'Test execution and automation',
                    'Bug reporting and tracking',
                    'Quality assurance processes'
                ],
                'approach': [
                    'Design comprehensive test cases',
                    'Execute systematic testing',
                    'Document findings clearly',
                    'Verify acceptance criteria'
                ]
            }
        }
        
        return defaults.get(specialist_type, {
            'name': specialist_type.title(),
            'expertise': ['Domain expertise'],
            'approach': ['Apply specialized knowledge']
        })
    
    async def _get_dependencies_context(self, task_id: str) -> str:
        """Get context about task dependencies."""
        dependencies = self.task_repo.get_task_dependencies(task_id)
        if not dependencies:
            return ""
        
        context_parts = []
        for dep_id in dependencies:
            dep_task = self.task_repo.get_task(dep_id)
            if dep_task:
                status = dep_task.get('status', 'unknown')
                title = dep_task.get('title', 'Untitled')
                context_parts.append(f"- {title} (Status: {status})")
                
                # Include results if completed
                if status == 'completed':
                    artifacts = self.task_repo.get_task_artifacts(dep_id)
                    result_artifacts = [
                        a for a in artifacts 
                        if a.get('type') == 'result'
                    ]
                    if result_artifacts:
                        context_parts.append(f"  Result: {result_artifacts[0].get('content', 'No content')}")
        
        return "\n".join(context_parts)
    
    def _format_artifacts_context(self, artifacts: List[Dict[str, Any]]) -> str:
        """Format artifacts for context."""
        if not artifacts:
            return ""
        
        context_parts = []
        for artifact in artifacts:
            name = artifact.get('name', 'Unnamed')
            type_ = artifact.get('type', 'unknown')
            content = artifact.get('content')
            
            if content:
                # Truncate large content
                if isinstance(content, str) and len(content) > 500:
                    content = content[:500] + "... (truncated)"
                elif isinstance(content, dict):
                    content = json.dumps(content, indent=2)[:500] + "... (truncated)"
                
                context_parts.append(f"- {name} ({type_}):\n  {content}")
        
        return "\n".join(context_parts)
    
    async def _create_default_specialist(self, specialist_type: str) -> str:
        """Create a default specialist if none exists."""
        role_def = self._get_role_definition(specialist_type)
        
        specialist_data = {
            'name': f"default_{specialist_type}",
            'category': specialist_type,
            'description': role_def.get('name', specialist_type.title()),
            'configuration': {
                'expertise': role_def.get('expertise', []),
                'approach': role_def.get('approach', [])
            }
        }
        
        return self.specialist_repo.create_specialist(specialist_data)