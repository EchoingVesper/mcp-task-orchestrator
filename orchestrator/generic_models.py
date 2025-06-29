"""
Generic Task Model - Pydantic Models for v2.0

This module defines the comprehensive Pydantic models for the unified Generic Task System.
These models replace the dual-model system (TaskBreakdown + SubTask) with a flexible,
extensible architecture supporting rich task management capabilities.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from pydantic import BaseModel, Field, validator, root_validator, ValidationError
import json
from pathlib import Path
import re


# ============================================
# Enumerations
# ============================================

class TaskType(str, Enum):
    """Types of tasks in the system."""
    STANDARD = "standard"
    BREAKDOWN = "breakdown"  # Root task that breaks down into subtasks
    MILESTONE = "milestone"
    REVIEW = "review"
    APPROVAL = "approval"
    RESEARCH = "research"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Current status of a task."""
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class LifecycleStage(str, Enum):
    """Lifecycle stage of a task."""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    ACTIVE = "active"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class DependencyType(str, Enum):
    """Types of dependencies between tasks."""
    COMPLETION = "completion"  # Task B starts after Task A completes
    DATA = "data"  # Task B needs output from Task A
    APPROVAL = "approval"  # Task B needs approval from Task A
    PREREQUISITE = "prerequisite"  # Task B requires Task A to exist
    BLOCKS = "blocks"  # Task A blocks Task B
    RELATED = "related"  # Informational relationship


class DependencyStatus(str, Enum):
    """Status of a dependency."""
    PENDING = "pending"
    SATISFIED = "satisfied"
    FAILED = "failed"
    WAIVED = "waived"
    CHECKING = "checking"


class QualityGateLevel(str, Enum):
    """Quality gate levels for task validation."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"


class EventType(str, Enum):
    """Types of task events."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    LIFECYCLE_CHANGED = "lifecycle_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    UNBLOCKED = "unblocked"
    ARCHIVED = "archived"
    DELETED = "deleted"
    DEPENDENCY_ADDED = "dependency_added"
    DEPENDENCY_SATISFIED = "dependency_satisfied"
    ATTRIBUTE_CHANGED = "attribute_changed"
    ARTIFACT_ADDED = "artifact_added"
    COMMENT_ADDED = "comment_added"
    MIGRATED = "migrated"


class EventCategory(str, Enum):
    """Categories of events."""
    LIFECYCLE = "lifecycle"
    DATA = "data"
    SYSTEM = "system"
    USER = "user"
    AUTOMATION = "automation"


class AttributeType(str, Enum):
    """Types for extensible attributes."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    JSON = "json"
    REFERENCE = "reference"  # Reference to another entity


class ArtifactType(str, Enum):
    """Types of artifacts."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    DESIGN = "design"
    TEST = "test"
    CONFIG = "config"
    DATA = "data"
    GENERAL = "general"


# ============================================
# Lifecycle State Machine
# ============================================

class LifecycleStateMachine:
    """Defines valid lifecycle transitions."""
    
    # Valid transitions: from_stage -> [allowed_to_stages]
    TRANSITIONS = {
        LifecycleStage.CREATED: [
            LifecycleStage.PLANNING,
            LifecycleStage.READY,
            LifecycleStage.ACTIVE,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.PLANNING: [
            LifecycleStage.READY,
            LifecycleStage.BLOCKED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.READY: [
            LifecycleStage.ACTIVE,
            LifecycleStage.BLOCKED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.ACTIVE: [
            LifecycleStage.BLOCKED,
            LifecycleStage.REVIEW,
            LifecycleStage.COMPLETED,
            LifecycleStage.FAILED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.BLOCKED: [
            LifecycleStage.READY,
            LifecycleStage.ACTIVE,
            LifecycleStage.FAILED,
            LifecycleStage.ARCHIVED
        ],
        LifecycleStage.REVIEW: [
            LifecycleStage.ACTIVE,
            LifecycleStage.COMPLETED,
            LifecycleStage.FAILED
        ],
        LifecycleStage.COMPLETED: [
            LifecycleStage.ARCHIVED,
            LifecycleStage.SUPERSEDED
        ],
        LifecycleStage.FAILED: [
            LifecycleStage.ARCHIVED,
            LifecycleStage.SUPERSEDED
        ],
        LifecycleStage.ARCHIVED: [],  # Terminal state
        LifecycleStage.SUPERSEDED: []  # Terminal state
    }
    
    @classmethod
    def can_transition(cls, from_stage: LifecycleStage, to_stage: LifecycleStage) -> bool:
        """Check if a transition is valid."""
        return to_stage in cls.TRANSITIONS.get(from_stage, [])
    
    @classmethod
    def get_allowed_transitions(cls, current_stage: LifecycleStage) -> List[LifecycleStage]:
        """Get list of allowed transitions from current stage."""
        return cls.TRANSITIONS.get(current_stage, [])


# ============================================
# Core Models
# ============================================

class TaskAttribute(BaseModel):
    """Extensible attribute for tasks (EAV pattern)."""
    attribute_name: str = Field(..., description="Name of the attribute")
    attribute_value: str = Field(..., description="Value stored as string")
    attribute_type: AttributeType = Field(..., description="Type for parsing")
    attribute_category: Optional[str] = Field(None, description="Category for grouping")
    is_indexed: bool = Field(default=False, description="Whether to index for fast lookup")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('attribute_value')
    def validate_value_format(cls, v, values):
        """Validate value format based on type."""
        if 'attribute_type' not in values:
            return v
            
        attr_type = values['attribute_type']
        
        if attr_type == AttributeType.NUMBER:
            try:
                float(v)
            except ValueError:
                raise ValueError(f"Value '{v}' is not a valid number")
                
        elif attr_type == AttributeType.BOOLEAN:
            if v.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                raise ValueError(f"Value '{v}' is not a valid boolean")
                
        elif attr_type == AttributeType.DATE:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Value '{v}' is not a valid ISO date")
                
        elif attr_type == AttributeType.JSON:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(f"Value '{v}' is not valid JSON")
                
        return v
    
    def get_typed_value(self) -> Any:
        """Get the value parsed to its proper type."""
        if self.attribute_type == AttributeType.STRING:
            return self.attribute_value
        elif self.attribute_type == AttributeType.NUMBER:
            return float(self.attribute_value)
        elif self.attribute_type == AttributeType.BOOLEAN:
            return self.attribute_value.lower() in ['true', '1', 'yes']
        elif self.attribute_type == AttributeType.DATE:
            return datetime.fromisoformat(self.attribute_value)
        elif self.attribute_type == AttributeType.JSON:
            return json.loads(self.attribute_value)
        else:
            return self.attribute_value


class TaskDependency(BaseModel):
    """Represents a dependency between tasks."""
    dependency_id: Optional[int] = Field(None, description="Database ID")
    dependent_task_id: str = Field(..., description="Task that has the dependency")
    prerequisite_task_id: str = Field(..., description="Task that must be satisfied")
    dependency_type: DependencyType = Field(..., description="Type of dependency")
    dependency_status: DependencyStatus = Field(default=DependencyStatus.PENDING)
    
    # Configuration
    is_mandatory: bool = Field(default=True, description="Whether dependency must be satisfied")
    auto_satisfy: bool = Field(default=False, description="Auto-satisfy when prerequisite completes")
    satisfaction_criteria: Optional[Dict[str, Any]] = Field(None, description="Specific criteria")
    
    # Data dependencies
    output_artifact_ref: Optional[str] = Field(None, description="Reference to output artifact")
    input_parameter_name: Optional[str] = Field(None, description="Parameter to receive data")
    
    # Waiver support
    waived_at: Optional[datetime] = None
    waived_by: Optional[str] = None
    waiver_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    satisfied_at: Optional[datetime] = None
    
    @root_validator
    def validate_dependency_logic(cls, values):
        """Validate dependency configuration logic."""
        dep_type = values.get('dependency_type')
        
        # Data dependencies should have artifact/parameter info
        if dep_type == DependencyType.DATA:
            if not values.get('output_artifact_ref') or not values.get('input_parameter_name'):
                raise ValueError("Data dependencies must specify output_artifact_ref and input_parameter_name")
        
        # Waiver validation
        if values.get('waived_at'):
            if not values.get('waived_by') or not values.get('waiver_reason'):
                raise ValueError("Waived dependencies must have waived_by and waiver_reason")
            values['dependency_status'] = DependencyStatus.WAIVED
            
        return values
    
    def can_satisfy(self, prerequisite_status: TaskStatus) -> bool:
        """Check if dependency can be satisfied based on prerequisite status."""
        if self.dependency_status == DependencyStatus.WAIVED:
            return True
            
        if self.dependency_type == DependencyType.COMPLETION:
            return prerequisite_status == TaskStatus.COMPLETED
        elif self.dependency_type == DependencyType.APPROVAL:
            return prerequisite_status in [TaskStatus.COMPLETED, TaskStatus.ACTIVE]
        else:
            # For other types, specific logic would be needed
            return prerequisite_status == TaskStatus.COMPLETED


class TaskEvent(BaseModel):
    """Represents an event in the task lifecycle."""
    event_id: Optional[int] = Field(None, description="Database ID")
    task_id: str = Field(..., description="Task this event relates to")
    event_type: EventType = Field(..., description="Type of event")
    event_category: EventCategory = Field(..., description="Category of event")
    
    # Event details
    event_data: Optional[Dict[str, Any]] = Field(None, description="Event-specific data")
    previous_value: Optional[str] = Field(None, description="For change events")
    new_value: Optional[str] = Field(None, description="For change events")
    
    # Metadata
    triggered_by: str = Field(..., description="What triggered the event")
    actor_id: Optional[str] = Field(None, description="Who/what triggered it")
    session_id: Optional[str] = Field(None, description="Session correlation")
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('event_data', pre=True)
    def ensure_dict(cls, v):
        """Ensure event_data is a dict."""
        if v is None:
            return {}
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {"raw": v}
        return v


class TaskArtifact(BaseModel):
    """Represents an artifact produced by a task."""
    artifact_id: str = Field(..., description="Unique artifact identifier")
    task_id: str = Field(..., description="Task that produced this")
    artifact_type: ArtifactType = Field(..., description="Type of artifact")
    artifact_name: str = Field(..., description="Human-readable name")
    
    # Content
    content: Optional[str] = Field(None, description="Text content")
    content_hash: Optional[str] = Field(None, description="Content hash for verification")
    file_reference: Optional[str] = Field(None, description="File system reference")
    file_size: Optional[int] = Field(None, description="Size in bytes")
    
    # Metadata
    mime_type: Optional[str] = Field(None, description="MIME type")
    encoding: str = Field(default="utf-8", description="Content encoding")
    is_primary: bool = Field(default=False, description="Primary output of task")
    visibility: str = Field(default="private", description="Access level")
    
    # Versioning
    version: int = Field(default=1, description="Version number")
    previous_version_id: Optional[str] = Field(None, description="Previous version")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @root_validator
    def validate_content_storage(cls, values):
        """Ensure artifact has either content or file reference."""
        if not values.get('content') and not values.get('file_reference'):
            raise ValueError("Artifact must have either content or file_reference")
        return values


class GenericTask(BaseModel):
    """Unified task model supporting hierarchical task management."""
    
    # Identification
    task_id: str = Field(..., description="Unique task identifier")
    parent_task_id: Optional[str] = Field(None, description="Parent task for hierarchy")
    
    # Basic information
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Detailed description")
    task_type: TaskType = Field(default=TaskType.STANDARD, description="Type of task")
    
    # Hierarchy management
    hierarchy_path: str = Field(..., description="Materialized path for tree queries")
    hierarchy_level: int = Field(default=0, description="Depth in hierarchy")
    position_in_parent: int = Field(default=0, description="Order among siblings")
    
    # Status and lifecycle
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    lifecycle_stage: LifecycleStage = Field(default=LifecycleStage.CREATED)
    
    # Complexity and effort
    complexity: ComplexityLevel = Field(default=ComplexityLevel.MODERATE)
    estimated_effort: Optional[str] = Field(None, description="Estimated time/effort")
    actual_effort: Optional[str] = Field(None, description="Actual time/effort")
    
    # Assignment
    specialist_type: Optional[SpecialistType] = None
    assigned_to: Optional[str] = Field(None, description="Assigned user/agent")
    
    # Context and configuration
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Results
    results: Optional[str] = None
    summary: Optional[str] = None
    
    # Quality and validation
    quality_gate_level: QualityGateLevel = Field(default=QualityGateLevel.STANDARD)
    verification_status: str = Field(default="pending")
    
    # Automation
    auto_maintenance_enabled: bool = Field(default=True)
    is_template: bool = Field(default=False)
    template_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    # Runtime collections (not stored in DB directly)
    attributes: List[TaskAttribute] = Field(default_factory=list)
    dependencies: List[TaskDependency] = Field(default_factory=list)
    artifacts: List[TaskArtifact] = Field(default_factory=list)
    events: List[TaskEvent] = Field(default_factory=list)
    children: List['GenericTask'] = Field(default_factory=list)
    
    @validator('hierarchy_path')
    def validate_hierarchy_path(cls, v, values):
        """Validate hierarchy path format."""
        if not v.startswith('/'):
            raise ValueError("Hierarchy path must start with /")
        
        # Ensure path ends with task_id
        task_id = values.get('task_id')
        if task_id and not v.endswith(f"/{task_id}"):
            v = f"{v}/{task_id}" if not v.endswith('/') else f"{v}{task_id}"
            
        return v
    
    @root_validator
    def validate_lifecycle_consistency(cls, values):
        """Ensure status and lifecycle stage are consistent."""
        status = values.get('status')
        lifecycle = values.get('lifecycle_stage')
        
        # Map status to appropriate lifecycle stages
        status_lifecycle_map = {
            TaskStatus.PENDING: [LifecycleStage.CREATED, LifecycleStage.PLANNING, LifecycleStage.READY],
            TaskStatus.ACTIVE: [LifecycleStage.ACTIVE],
            TaskStatus.IN_PROGRESS: [LifecycleStage.ACTIVE],
            TaskStatus.BLOCKED: [LifecycleStage.BLOCKED],
            TaskStatus.COMPLETED: [LifecycleStage.COMPLETED, LifecycleStage.REVIEW],
            TaskStatus.FAILED: [LifecycleStage.FAILED],
            TaskStatus.CANCELLED: [LifecycleStage.ARCHIVED],
            TaskStatus.ARCHIVED: [LifecycleStage.ARCHIVED, LifecycleStage.SUPERSEDED]
        }
        
        allowed_lifecycles = status_lifecycle_map.get(status, [])
        if lifecycle not in allowed_lifecycles:
            # Auto-correct to appropriate lifecycle
            if allowed_lifecycles:
                values['lifecycle_stage'] = allowed_lifecycles[0]
                
        return values
    
    def can_transition_to(self, new_stage: LifecycleStage) -> bool:
        """Check if task can transition to a new lifecycle stage."""
        return LifecycleStateMachine.can_transition(self.lifecycle_stage, new_stage)
    
    def get_allowed_transitions(self) -> List[LifecycleStage]:
        """Get list of allowed lifecycle transitions."""
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
        # Convert dicts to JSON strings for storage
        if data.get('context'):
            data['context'] = json.dumps(data['context'])
        if data.get('configuration'):
            data['configuration'] = json.dumps(data['configuration'])
        return data
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Enable forward reference resolution
GenericTask.update_forward_refs()


# ============================================
# Template Models
# ============================================

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
    
    def instantiate(self, parameters: Dict[str, Any], parent_task_id: Optional[str] = None) -> List[GenericTask]:
        """Create task instances from template."""
        validated_params = self.validate_parameters(parameters)
        
        # Process task structure with parameter substitution
        tasks = []
        
        def substitute_params(text: str, params: Dict[str, Any]) -> str:
            """Replace {{param}} with actual values."""
            for key, value in params.items():
                text = text.replace(f"{{{{{key}}}}}", str(value))
            return text
        
        def create_tasks_from_structure(structure: Dict[str, Any], parent_id: Optional[str] = None,
                                      parent_path: str = "") -> List[GenericTask]:
            """Recursively create tasks from structure."""
            created = []
            
            for task_key, task_def in structure.items():
                # Create task ID
                task_id = f"{self.template_id}_{task_key}_{datetime.now().timestamp()}"
                
                # Build hierarchy path
                hierarchy_path = f"{parent_path}/{task_id}" if parent_path else f"/{task_id}"
                
                # Create task
                task = GenericTask(
                    task_id=task_id,
                    parent_task_id=parent_id,
                    title=substitute_params(task_def.get('title', ''), validated_params),
                    description=substitute_params(task_def.get('description', ''), validated_params),
                    task_type=TaskType(task_def.get('type', 'standard')),
                    hierarchy_path=hierarchy_path,
                    hierarchy_level=len(hierarchy_path.split('/')) - 2,
                    specialist_type=task_def.get('specialist_type'),
                    estimated_effort=task_def.get('estimated_effort'),
                    template_id=self.template_id
                )
                
                created.append(task)
                
                # Process children
                if 'children' in task_def:
                    child_tasks = create_tasks_from_structure(
                        task_def['children'], task_id, hierarchy_path
                    )
                    created.extend(child_tasks)
                    
            return created
        
        tasks = create_tasks_from_structure(self.task_structure, parent_task_id)
        
        # Increment usage count
        self.usage_count += 1
        self.last_used_at = datetime.now()
        
        return tasks


# ============================================
# Backward Compatibility Support
# ============================================

def create_generic_task_from_breakdown(breakdown: 'TaskBreakdown') -> GenericTask:
    """Convert old TaskBreakdown to GenericTask."""
    task_id = breakdown.parent_task_id
    return GenericTask(
        task_id=task_id,
        parent_task_id=None,
        title=f"Task Breakdown: {breakdown.description[:100]}",
        description=breakdown.description,
        task_type=TaskType.BREAKDOWN,
        hierarchy_path=f"/{task_id}",
        hierarchy_level=0,
        complexity=breakdown.complexity,
        context={"original_context": breakdown.context} if breakdown.context else {},
        created_at=breakdown.created_at
    )


def create_generic_task_from_subtask(subtask: 'SubTask', parent_task_id: str,
                                   parent_path: str, position: int = 0) -> GenericTask:
    """Convert old SubTask to GenericTask."""
    task_id = subtask.task_id
    hierarchy_path = f"{parent_path}/{task_id}"
    
    # Map old status to new lifecycle
    lifecycle_map = {
        'pending': LifecycleStage.CREATED,
        'active': LifecycleStage.ACTIVE,
        'completed': LifecycleStage.COMPLETED,
        'blocked': LifecycleStage.BLOCKED,
        'failed': LifecycleStage.FAILED,
        'archived': LifecycleStage.ARCHIVED
    }
    
    task = GenericTask(
        task_id=task_id,
        parent_task_id=parent_task_id,
        title=subtask.title,
        description=subtask.description,
        task_type=TaskType.STANDARD,
        hierarchy_path=hierarchy_path,
        hierarchy_level=len(hierarchy_path.split('/')) - 2,
        position_in_parent=position,
        status=subtask.status,
        lifecycle_stage=lifecycle_map.get(subtask.status.value, LifecycleStage.CREATED),
        specialist_type=subtask.specialist_type,
        estimated_effort=subtask.estimated_effort,
        results=subtask.results,
        created_at=subtask.created_at,
        completed_at=subtask.completed_at
    )
    
    # Convert artifacts
    for i, artifact in enumerate(subtask.artifacts):
        task.artifacts.append(TaskArtifact(
            artifact_id=f"{task_id}_artifact_{i}",
            task_id=task_id,
            artifact_type=ArtifactType.GENERAL,
            artifact_name=f"Artifact {i}",
            content=artifact if isinstance(artifact, str) else json.dumps(artifact)
        ))
    
    # Convert dependencies
    for dep_id in subtask.dependencies:
        task.dependencies.append(TaskDependency(
            dependent_task_id=task_id,
            prerequisite_task_id=dep_id,
            dependency_type=DependencyType.COMPLETION
        ))
    
    return task


# Import existing enums for backward compatibility
from .models import ComplexityLevel, SpecialistType