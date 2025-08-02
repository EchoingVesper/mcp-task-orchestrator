"""
Task Models - Core task entities for the domain layer.

Contains the main Task entity and related models extracted from generic_models.py
to improve modularity and reduce file size.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from pydantic import BaseModel, Field, validator, root_validator, model_validator

# Import value objects
from ..value_objects.complexity_level import ComplexityLevel
from ..value_objects.flexible_specialist_type import validate_specialist_type
from ..value_objects.enums import (
    TaskType, TaskStatus, LifecycleStage, DependencyType, DependencyStatus,
    EventType, EventCategory, AttributeType, ArtifactType
)


class TaskAttribute(BaseModel):
    """Custom attributes for tasks with type safety."""
    attribute_name: str
    attribute_value: str  # Stored as string, converted based on type
    attribute_type: AttributeType = AttributeType.STRING
    attribute_category: Optional[str] = None
    is_indexed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_typed_value(self) -> Any:
        """Get the attribute value converted to its proper type."""
        if self.attribute_type == AttributeType.NUMBER:
            try:
                return float(self.attribute_value)
            except ValueError:
                return 0.0
        elif self.attribute_type == AttributeType.BOOLEAN:
            return self.attribute_value.lower() in ['true', '1', 'yes', 'on']
        elif self.attribute_type == AttributeType.DATE:
            try:
                return datetime.fromisoformat(self.attribute_value)
            except ValueError:
                return None
        elif self.attribute_type == AttributeType.JSON:
            try:
                return json.loads(self.attribute_value)
            except (json.JSONDecodeError, ValueError):
                return {}
        else:
            return self.attribute_value


class TaskDependency(BaseModel):
    """Represents a dependency relationship between tasks."""
    dependent_task_id: str
    prerequisite_task_id: str
    dependency_type: DependencyType = DependencyType.COMPLETION
    dependency_status: DependencyStatus = DependencyStatus.PENDING
    is_mandatory: bool = True
    auto_satisfy: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    satisfied_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    def mark_satisfied(self, notes: Optional[str] = None):
        """Mark this dependency as satisfied."""
        self.dependency_status = DependencyStatus.SATISFIED
        self.satisfied_at = datetime.utcnow()
        if notes:
            self.notes = notes


class TaskArtifact(BaseModel):
    """Represents an artifact associated with a task."""
    artifact_id: str
    task_id: str
    artifact_type: ArtifactType = ArtifactType.GENERAL
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_temporary: bool = False
    
    @validator('artifact_id')
    def validate_artifact_id(cls, v):
        if not v or not v.strip():
            raise ValueError("Artifact ID cannot be empty")
        return v


class TaskEvent(BaseModel):
    """Represents an event in the task lifecycle."""
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    task_id: str
    event_type: EventType
    event_category: EventCategory = EventCategory.SYSTEM
    event_data: Dict[str, Any] = Field(default_factory=dict)
    triggered_by: str = "system"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    
    @validator('event_data')
    def validate_event_data(cls, v):
        if v is None:
            return {}
        return v


class Task(BaseModel):
    """
    Comprehensive Task model for the unified task system.
    
    This model replaces the dual-model system with a flexible, extensible architecture
    supporting rich task management capabilities.
    """
    
    # Core identification
    task_id: str
    parent_task_id: Optional[str] = None
    
    # Basic information
    title: str
    description: str
    task_type: TaskType = TaskType.STANDARD
    
    # Status and lifecycle
    status: TaskStatus = TaskStatus.PENDING
    lifecycle_stage: LifecycleStage = LifecycleStage.CREATED
    
    # Hierarchy and organization
    hierarchy_path: str = "/"
    hierarchy_level: int = 0
    position_in_parent: Optional[int] = None
    tags: Set[str] = Field(default_factory=set)
    
    # Assignment and specialization
    specialist_type: Optional[str] = None
    assigned_to: Optional[str] = None
    
    # Priority and complexity
    priority: int = Field(default=5, ge=1, le=10)
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    estimated_effort: Optional[str] = None
    actual_effort: Optional[str] = None
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    # Work tracking
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    result: Optional[str] = None
    error: Optional[str] = None
    
    # Extensible data
    context: Dict[str, Any] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    
    # Quality gates
    quality_gates: List[str] = Field(default_factory=list)
    quality_gate_level: str = "basic"  # basic, standard, comprehensive, custom
    
    # Collections (managed separately in repository)
    attributes: List[TaskAttribute] = Field(default_factory=list)
    dependencies: List[TaskDependency] = Field(default_factory=list)
    artifacts: List[TaskArtifact] = Field(default_factory=list)
    events: List[TaskEvent] = Field(default_factory=list)
    children: List["Task"] = Field(default_factory=list)
    
    # Soft delete support
    is_deleted: bool = False
    
    @validator('specialist_type')
    def validate_specialist_type_format(cls, v):
        """Validate specialist type format."""
        if v is not None:
            return validate_specialist_type(v)
        return v
    
    @validator('hierarchy_path')
    def validate_hierarchy_path(cls, v):
        """Ensure hierarchy path is valid."""
        if not v.startswith('/'):
            return f"/{v}"
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not empty."""
        if not v or not v.strip():
            raise ValueError("Task title cannot be empty")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not empty."""
        if not v or not v.strip():
            raise ValueError("Task description cannot be empty")
        return v.strip()
    
    @model_validator(mode='before')
    def validate_hierarchy_consistency(cls, values):
        """Validate hierarchy consistency."""
        hierarchy_path = values.get('hierarchy_path', '/')
        hierarchy_level = values.get('hierarchy_level', 0)
        parent_task_id = values.get('parent_task_id')
        
        # Root tasks should have level 0 and path "/"
        if parent_task_id is None:
            if hierarchy_level != 0:
                values['hierarchy_level'] = 0
            if hierarchy_path not in ['/', f"/{values.get('task_id', '')}"] and values.get('task_id'):
                values['hierarchy_path'] = f"/{values['task_id']}"
        
        return values
    
    @model_validator(mode='before')
    def validate_temporal_consistency(cls, values):
        """Validate temporal field consistency."""
        created_at = values.get('created_at')
        started_at = values.get('started_at')
        completed_at = values.get('completed_at')
        
        if started_at and created_at and started_at < created_at:
            raise ValueError("Started time cannot be before created time")
        
        if completed_at and started_at and completed_at < started_at:
            raise ValueError("Completed time cannot be before started time")
        
        if completed_at and created_at and completed_at < created_at:
            raise ValueError("Completed time cannot be before created time")
        
        return values
    
    def is_terminal(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.ARCHIVED]
    
    def is_active(self) -> bool:
        """Check if task is actively being worked on."""
        return self.status in [TaskStatus.ACTIVE, TaskStatus.IN_PROGRESS]
    
    def can_transition_to(self, new_stage: LifecycleStage) -> bool:
        """Check if transition to new lifecycle stage is allowed."""
        # Import here to avoid circular imports
        from ..models.lifecycle import LifecycleStateMachine
        return LifecycleStateMachine.can_transition(self.lifecycle_stage, new_stage)
    
    def get_allowed_transitions(self) -> List[LifecycleStage]:
        """Get list of allowed lifecycle transitions."""
        # Import here to avoid circular imports
        from ..models.lifecycle import LifecycleStateMachine
        return LifecycleStateMachine.get_allowed_transitions(self.lifecycle_stage)
    
    def add_attribute(self, name: str, value: Any, attr_type: AttributeType = AttributeType.STRING,
                     category: Optional[str] = None, indexed: bool = False) -> TaskAttribute:
        """Add a custom attribute to the task."""
        # Convert value to string based on type
        if attr_type == AttributeType.JSON:
            str_value = json.dumps(value)
        elif attr_type == AttributeType.DATE and isinstance(value, datetime):
            str_value = value.isoformat()
        else:
            str_value = str(value)
            
        attr = TaskAttribute(
            attribute_name=name,
            attribute_value=str_value,
            attribute_type=attr_type,
            attribute_category=category,
            is_indexed=indexed
        )
        self.attributes.append(attr)
        return attr
    
    def get_attribute(self, name: str) -> Optional[Any]:
        """Get a custom attribute value by name."""
        for attr in self.attributes:
            if attr.attribute_name == name:
                return attr.get_typed_value()
        return None
    
    def add_dependency(self, prerequisite_task_id: str, dep_type: DependencyType = DependencyType.COMPLETION,
                      mandatory: bool = True, auto_satisfy: bool = False) -> TaskDependency:
        """Add a dependency to another task."""
        dep = TaskDependency(
            dependent_task_id=self.task_id,
            prerequisite_task_id=prerequisite_task_id,
            dependency_type=dep_type,
            is_mandatory=mandatory,
            auto_satisfy=auto_satisfy
        )
        self.dependencies.append(dep)
        return dep
    
    def check_dependencies_satisfied(self) -> Tuple[bool, List[TaskDependency]]:
        """Check if all mandatory dependencies are satisfied."""
        unsatisfied = []
        for dep in self.dependencies:
            if dep.is_mandatory and dep.dependency_status not in [DependencyStatus.SATISFIED, DependencyStatus.WAIVED]:
                unsatisfied.append(dep)
        return len(unsatisfied) == 0, unsatisfied
    
    def record_event(self, event_type: EventType, category: EventCategory,
                    triggered_by: str = "system", data: Optional[Dict] = None) -> TaskEvent:
        """Record an event for this task."""
        event = TaskEvent(
            task_id=self.task_id,
            event_type=event_type,
            event_category=category,
            event_data=data or {},
            triggered_by=triggered_by
        )
        self.events.append(event)
        return event
    
    def to_dict_for_storage(self) -> Dict[str, Any]:
        """Convert to dict for database storage (excludes runtime collections)."""
        data = self.dict(exclude={'attributes', 'dependencies', 'artifacts', 'events', 'children'})
        # Convert datetime objects to ISO strings
        for key in ['created_at', 'updated_at', 'started_at', 'completed_at', 'due_date', 'deleted_at']:
            if data.get(key):
                data[key] = data[key].isoformat()
        # Convert dicts to JSON strings for storage (including empty dicts)
        if 'context' in data and data['context'] is not None:
            data['context'] = json.dumps(data['context'])
        if 'configuration' in data and data['configuration'] is not None:
            data['configuration'] = json.dumps(data['configuration'])
        return data
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Enable forward reference resolution
Task.update_forward_refs()