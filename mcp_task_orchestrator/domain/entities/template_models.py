"""
Template Models - Task template entities for reusable task patterns.

Contains template-related models extracted from generic_models.py
to improve modularity and support template-based task creation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..value_objects.enums import TaskType


class TemplateParameter(BaseModel):
    """Defines a parameter for a task template."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, number, boolean, etc)")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if not provided")
    validation: Optional[Dict[str, Any]] = Field(None, description="JSON Schema validation rules")


class TaskTemplate(BaseModel):
    """Reusable task pattern."""
    template_id: str = Field(..., description="Unique template identifier")
    template_name: str = Field(..., description="Human-readable template name")
    template_category: str = Field(..., description="Category for organization")
    template_version: int = Field(default=1, description="Version number")
    
    # Template content
    description: str = Field(..., description="What this template does")
    parameters: List[TemplateParameter] = Field(default_factory=list)
    task_structure: Dict[str, Any] = Field(..., description="Task hierarchy definition")
    
    # Metadata
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=True)
    created_by: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Usage tracking
    usage_count: int = Field(default=0)
    last_used_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    
    def validate_parameters(self, provided_params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate provided parameters against template schema."""
        validated = {}
        
        for param in self.parameters:
            if param.required and param.name not in provided_params:
                if param.default is not None:
                    validated[param.name] = param.default
                else:
                    raise ValueError(f"Required parameter '{param.name}' not provided")
            elif param.name in provided_params:
                # Type validation would go here
                validated[param.name] = provided_params[param.name]
                
        return validated
    
    def instantiate(self, parameters: Dict[str, Any], parent_task_id: Optional[str] = None) -> List['Task']:
        """Create task instances from template."""
        # Import here to avoid circular imports
        from .task_models import Task
        
        validated_params = self.validate_parameters(parameters)
        
        # Process task structure with parameter substitution
        tasks = []
        
        def substitute_params(text: str, params: Dict[str, Any]) -> str:
            """Replace {{param}} with actual values."""
            for key, value in params.items():
                text = text.replace(f"{{{{{key}}}}}", str(value))
            return text
        
        def create_tasks_from_structure(structure: Dict[str, Any], parent_id: Optional[str] = None,
                                      parent_path: str = "") -> List['Task']:
            """Recursively create tasks from structure."""
            created = []
            
            for task_key, task_def in structure.items():
                # Create task ID
                task_id = f"{self.template_id}_{task_key}_{datetime.now().timestamp()}"
                
                # Build hierarchy path
                hierarchy_path = f"{parent_path}/{task_id}" if parent_path else f"/{task_id}"
                
                # Create task
                task = Task(
                    task_id=task_id,
                    parent_task_id=parent_id,
                    title=substitute_params(task_def.get('title', ''), validated_params),
                    description=substitute_params(task_def.get('description', ''), validated_params),
                    task_type=TaskType(task_def.get('type', 'standard')),
                    hierarchy_path=hierarchy_path,
                    hierarchy_level=len(hierarchy_path.split('/')) - 2,
                    specialist_type=task_def.get('specialist_type'),
                    estimated_effort=task_def.get('estimated_effort'),
                    context={'template_id': self.template_id}
                )
                
                created.append(task)
                
                # Process children
                if 'children' in task_def:
                    child_tasks = create_tasks_from_structure(
                        task_def['children'], task_id, hierarchy_path
                    )
                    created.extend(child_tasks)
                    task.children = child_tasks
            
            return created
        
        # Start creation from root level
        tasks = create_tasks_from_structure(self.task_structure, parent_task_id)
        
        # Update usage tracking
        self.usage_count += 1
        self.last_used_at = datetime.now()
        
        return tasks
    
    def get_estimated_total_effort(self) -> Optional[str]:
        """Calculate total estimated effort from all tasks in template."""
        # This would analyze the task_structure to sum up effort estimates
        # Implementation depends on how effort is represented
        return None
    
    def validate_structure(self) -> List[str]:
        """Validate the task structure for consistency."""
        errors = []
        
        def validate_task_def(task_def: Dict[str, Any], path: str = "root"):
            """Recursively validate task definitions."""
            required_fields = ['title', 'description']
            for field in required_fields:
                if field not in task_def:
                    errors.append(f"Missing required field '{field}' in task at {path}")
            
            # Validate task type if specified
            if 'type' in task_def:
                try:
                    TaskType(task_def['type'])
                except ValueError:
                    errors.append(f"Invalid task type '{task_def['type']}' at {path}")
            
            # Validate children recursively
            if 'children' in task_def:
                for child_key, child_def in task_def['children'].items():
                    validate_task_def(child_def, f"{path}.{child_key}")
        
        # Validate each top-level task
        for task_key, task_def in self.task_structure.items():
            validate_task_def(task_def, task_key)
        
        return errors
    
    def get_parameter_placeholders(self) -> List[str]:
        """Extract all parameter placeholders from the template structure."""
        import re
        
        placeholders = set()
        
        def extract_from_dict(data: Dict[str, Any]):
            """Recursively extract placeholders from dictionary."""
            for value in data.values():
                if isinstance(value, str):
                    # Find {{parameter}} patterns
                    matches = re.findall(r'\{\{(\w+)\}\}', value)
                    placeholders.update(matches)
                elif isinstance(value, dict):
                    extract_from_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_from_dict(item)
                        elif isinstance(item, str):
                            matches = re.findall(r'\{\{(\w+)\}\}', item)
                            placeholders.update(matches)
        
        extract_from_dict(self.task_structure)
        extract_from_dict({'description': self.description})
        
        return sorted(list(placeholders))
    
    def clone(self, new_template_id: str, new_name: Optional[str] = None) -> 'TaskTemplate':
        """Create a copy of this template with a new ID."""
        return TaskTemplate(
            template_id=new_template_id,
            template_name=new_name or f"{self.template_name} (Copy)",
            template_category=self.template_category,
            template_version=1,  # Reset version for new template
            description=self.description,
            parameters=self.parameters.copy(),
            task_structure=self.task_structure.copy(),
            is_active=True,
            is_public=self.is_public,
            created_by=self.created_by,
            tags=self.tags.copy(),
            usage_count=0,  # Reset usage count
            last_used_at=None
        )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }