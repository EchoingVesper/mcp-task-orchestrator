# Generic Task Model Implementation Guide

> **Document Type**: Implementation Specification  
> **Version**: 2.0  
> **Created**: 2025-06-03  
> **Target Release**: v2.0  
> **Status**: Implementation Ready

## Overview

This guide provides detailed implementation specifications for the Generic Task Model, covering database schema design, API implementation, migration strategies, and integration patterns.

## Implementation Architecture

### Core Components

#### 1. Database Schema Implementation

**Primary Tables**:
```sql
-- Core generic tasks table
CREATE TABLE generic_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    parent_task_id VARCHAR(50),
    template_id VARCHAR(50),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    lifecycle_stage VARCHAR(20) NOT NULL DEFAULT 'draft',
    hierarchy_path TEXT,  -- Materialized path for efficient queries
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    superseded_by VARCHAR(50),
    
    FOREIGN KEY (parent_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES task_templates(template_id),
    FOREIGN KEY (superseded_by) REFERENCES generic_tasks(task_id)
);

-- Flexible attributes using EAV pattern
CREATE TABLE task_attributes (
    task_id VARCHAR(50) NOT NULL,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value JSON NOT NULL,
    attribute_type VARCHAR(20) NOT NULL DEFAULT 'string',  -- string, number, boolean, array, object
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (task_id, attribute_name),
    FOREIGN KEY (task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE
);

-- Task dependencies with rich relationship modeling
CREATE TABLE task_dependencies (
    dependent_task_id VARCHAR(50) NOT NULL,
    dependency_task_id VARCHAR(50) NOT NULL,
    dependency_type VARCHAR(20) NOT NULL,  -- completion, data, approval, prerequisite
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, satisfied, blocked
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    satisfied_at TIMESTAMP,
    
    PRIMARY KEY (dependent_task_id, dependency_task_id),
    FOREIGN KEY (dependent_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (dependency_task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE
);

-- Task templates for reusable patterns
CREATE TABLE task_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    template_structure JSON NOT NULL,  -- Complete task hierarchy definition
    parameters_schema JSON,  -- JSON Schema for template parameters
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Task lifecycle events for auditing and plugins
CREATE TABLE task_events (
    event_id VARCHAR(50) PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- created, status_changed, dependency_satisfied, etc.
    event_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES generic_tasks(task_id) ON DELETE CASCADE
);
```

**Performance Indexes**:
```sql
-- Hierarchy and relationship indexes
CREATE INDEX idx_tasks_parent_id ON generic_tasks(parent_task_id);
CREATE INDEX idx_tasks_hierarchy_path ON generic_tasks(hierarchy_path);
CREATE INDEX idx_tasks_type_status ON generic_tasks(task_type, status);
CREATE INDEX idx_tasks_lifecycle_stage ON generic_tasks(lifecycle_stage);
CREATE INDEX idx_tasks_template_id ON generic_tasks(template_id);

-- Attribute queries
CREATE INDEX idx_attributes_name_value ON task_attributes(attribute_name, attribute_value);
CREATE INDEX idx_attributes_task_name ON task_attributes(task_id, attribute_name);

-- Dependency resolution
CREATE INDEX idx_dependencies_dependent ON task_dependencies(dependent_task_id, status);
CREATE INDEX idx_dependencies_dependency ON task_dependencies(dependency_task_id, status);

-- Event tracking
CREATE INDEX idx_events_task_type ON task_events(task_id, event_type);
CREATE INDEX idx_events_created_at ON task_events(created_at);

-- Template management
CREATE INDEX idx_templates_category ON task_templates(category, is_active);
```

#### 2. Pydantic Models Implementation

```python
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator

class TaskStatus(str, Enum):
    """Enhanced task status with lifecycle awareness."""
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"

class LifecycleStage(str, Enum):
    """Task lifecycle stages for state machine."""
    DRAFT = "draft"          # Initial creation
    READY = "ready"          # Dependencies satisfied, ready to start
    ACTIVE = "active"        # In progress
    BLOCKED = "blocked"      # Cannot proceed
    REVIEW = "review"        # Awaiting review/approval
    COMPLETED = "completed"  # Successfully finished
    ARCHIVED = "archived"    # Archived for historical reference
    SUPERSEDED = "superseded" # Replaced by another task

class DependencyType(str, Enum):
    """Types of task dependencies."""
    COMPLETION = "completion"     # Task must complete before dependent can start
    DATA = "data"                # Dependent needs output/data from this task
    APPROVAL = "approval"        # Approval required before dependent can proceed
    PREREQUISITE = "prerequisite" # Condition that must be met

class TaskDependency(BaseModel):
    """Represents a dependency relationship between tasks."""
    dependency_task_id: str = Field(..., description="Task that this task depends on")
    dependency_type: DependencyType = Field(..., description="Type of dependency relationship")
    status: str = Field(default="pending", description="Current dependency status")
    description: Optional[str] = Field(None, description="Human-readable dependency description")

class GenericTask(BaseModel):
    """Unified task model replacing TaskBreakdown and SubTask."""
    
    # Core Identity
    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task (feature_epic, specialist_task, etc.)")
    template_id: Optional[str] = Field(None, description="Template this task was created from")
    
    # Hierarchical Structure
    parent_task_id: Optional[str] = Field(None, description="Parent task for nested structures")
    child_task_ids: List[str] = Field(default_factory=list, description="Child task IDs")
    hierarchy_path: Optional[str] = Field(None, description="Materialized path for efficient queries")
    
    # State Management
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    lifecycle_stage: LifecycleStage = Field(default=LifecycleStage.DRAFT, description="Lifecycle stage")
    
    # Dependencies and Relationships
    dependencies: List[TaskDependency] = Field(default_factory=list, description="Task dependencies")
    superseded_by: Optional[str] = Field(None, description="Task that supersedes this one")
    
    # Flexible Attributes (replaces fixed fields)
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Flexible task attributes")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    # Computed Properties
    @property
    def is_root_task(self) -> bool:
        """Check if this is a root task (no parent)."""
        return self.parent_task_id is None
    
    @property
    def is_leaf_task(self) -> bool:
        """Check if this is a leaf task (no children)."""
        return len(self.child_task_ids) == 0
    
    @property
    def depth_level(self) -> int:
        """Calculate depth level from hierarchy path."""
        if not self.hierarchy_path:
            return 0
        return len(self.hierarchy_path.split('/')) - 2  # Subtract for empty first element and root
    
    def can_transition_to(self, target_stage: LifecycleStage) -> bool:
        """Check if transition to target stage is allowed."""
        valid_transitions = {
            LifecycleStage.DRAFT: [LifecycleStage.READY, LifecycleStage.ARCHIVED],
            LifecycleStage.READY: [LifecycleStage.ACTIVE, LifecycleStage.BLOCKED, LifecycleStage.ARCHIVED],
            LifecycleStage.ACTIVE: [LifecycleStage.BLOCKED, LifecycleStage.REVIEW, LifecycleStage.COMPLETED],
            LifecycleStage.BLOCKED: [LifecycleStage.READY, LifecycleStage.ACTIVE, LifecycleStage.ARCHIVED],
            LifecycleStage.REVIEW: [LifecycleStage.ACTIVE, LifecycleStage.COMPLETED, LifecycleStage.BLOCKED],
            LifecycleStage.COMPLETED: [LifecycleStage.ARCHIVED, LifecycleStage.SUPERSEDED],
            LifecycleStage.ARCHIVED: [],  # Terminal state
            LifecycleStage.SUPERSEDED: []  # Terminal state
        }
        return target_stage in valid_transitions.get(self.lifecycle_stage, [])

class TaskTemplate(BaseModel):
    """Template for creating reusable task patterns."""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Template description and use cases")
    category: str = Field(..., description="Template category (development, deployment, review)")
    version: str = Field(default="1.0", description="Template version")
    
    # Template Structure
    task_structure: Dict[str, Any] = Field(..., description="Task hierarchy definition")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema for parameters")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True, description="Whether template is available for use")

class TaskEvent(BaseModel):
    """Event emitted during task lifecycle changes."""
    event_id: str = Field(..., description="Unique event identifier")
    task_id: str = Field(..., description="Task that triggered the event")
    event_type: str = Field(..., description="Type of event")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    created_at: datetime = Field(default_factory=datetime.now)
```

#### 3. Database Operations Implementation

```python
class GenericTaskRepository:
    """Repository for generic task data operations."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def create_task(self, task: GenericTask) -> GenericTask:
        """Create a new generic task."""
        
        # Insert main task record
        task_data = {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'parent_task_id': task.parent_task_id,
            'template_id': task.template_id,
            'status': task.status.value,
            'lifecycle_stage': task.lifecycle_stage.value,
            'hierarchy_path': await self._compute_hierarchy_path(task.parent_task_id, task.task_id),
            'superseded_by': task.superseded_by,
            'created_at': task.created_at,
            'updated_at': task.updated_at,
            'completed_at': task.completed_at
        }
        
        await self.db.execute(
            "INSERT INTO generic_tasks (...) VALUES (...)",
            task_data
        )
        
        # Insert attributes
        for attr_name, attr_value in task.attributes.items():
            await self.db.execute(
                "INSERT INTO task_attributes (task_id, attribute_name, attribute_value, attribute_type) VALUES (?, ?, ?, ?)",
                (task.task_id, attr_name, json.dumps(attr_value), self._infer_type(attr_value))
            )
        
        # Insert dependencies
        for dependency in task.dependencies:
            await self.db.execute(
                "INSERT INTO task_dependencies (dependent_task_id, dependency_task_id, dependency_type, description) VALUES (?, ?, ?, ?)",
                (task.task_id, dependency.dependency_task_id, dependency.dependency_type.value, dependency.description)
            )
        
        # Emit creation event
        await self._emit_event(task.task_id, "task.created", {"task_type": task.task_type})
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[GenericTask]:
        """Retrieve a task with all its attributes and dependencies."""
        
        # Get main task record
        task_row = await self.db.fetchone(
            "SELECT * FROM generic_tasks WHERE task_id = ?",
            (task_id,)
        )
        
        if not task_row:
            return None
        
        # Get attributes
        attr_rows = await self.db.fetchall(
            "SELECT attribute_name, attribute_value FROM task_attributes WHERE task_id = ?",
            (task_id,)
        )
        attributes = {row['attribute_name']: json.loads(row['attribute_value']) for row in attr_rows}
        
        # Get dependencies
        dep_rows = await self.db.fetchall(
            "SELECT dependency_task_id, dependency_type, status, description FROM task_dependencies WHERE dependent_task_id = ?",
            (task_id,)
        )
        dependencies = [
            TaskDependency(
                dependency_task_id=row['dependency_task_id'],
                dependency_type=DependencyType(row['dependency_type']),
                status=row['status'],
                description=row['description']
            ) for row in dep_rows
        ]
        
        # Get child task IDs
        child_rows = await self.db.fetchall(
            "SELECT task_id FROM generic_tasks WHERE parent_task_id = ?",
            (task_id,)
        )
        child_task_ids = [row['task_id'] for row in child_rows]
        
        # Construct GenericTask object
        return GenericTask(
            task_id=task_row['task_id'],
            task_type=task_row['task_type'],
            template_id=task_row['template_id'],
            parent_task_id=task_row['parent_task_id'],
            child_task_ids=child_task_ids,
            hierarchy_path=task_row['hierarchy_path'],
            status=TaskStatus(task_row['status']),
            lifecycle_stage=LifecycleStage(task_row['lifecycle_stage']),
            dependencies=dependencies,
            superseded_by=task_row['superseded_by'],
            attributes=attributes,
            created_at=task_row['created_at'],
            updated_at=task_row['updated_at'],
            completed_at=task_row['completed_at']
        )
    
    async def query_tasks(
        self, 
        filters: Dict[str, Any] = None,
        sort_field: str = "created_at",
        sort_direction: str = "desc",
        limit: Optional[int] = None,
        include_hierarchy: bool = False
    ) -> List[GenericTask]:
        """Flexible task querying with filters and sorting."""
        
        where_clauses = []
        params = []
        
        if filters:
            if 'task_type' in filters:
                if isinstance(filters['task_type'], list):
                    placeholders = ','.join(['?' for _ in filters['task_type']])
                    where_clauses.append(f"task_type IN ({placeholders})")
                    params.extend(filters['task_type'])
                else:
                    where_clauses.append("task_type = ?")
                    params.append(filters['task_type'])
            
            if 'status' in filters:
                if isinstance(filters['status'], list):
                    placeholders = ','.join(['?' for _ in filters['status']])
                    where_clauses.append(f"status IN ({placeholders})")
                    params.extend(filters['status'])
                else:
                    where_clauses.append("status = ?")
                    params.append(filters['status'])
            
            if 'parent_task_id' in filters:
                where_clauses.append("parent_task_id = ?")
                params.append(filters['parent_task_id'])
            
            # Attribute-based filtering
            if 'attributes' in filters:
                for attr_name, attr_value in filters['attributes'].items():
                    where_clauses.append(
                        "task_id IN (SELECT task_id FROM task_attributes WHERE attribute_name = ? AND attribute_value = ?)"
                    )
                    params.extend([attr_name, json.dumps(attr_value)])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        order_sql = f"ORDER BY {sort_field} {sort_direction.upper()}"
        limit_sql = f"LIMIT {limit}" if limit else ""
        
        query = f"""
            SELECT task_id FROM generic_tasks 
            WHERE {where_sql} 
            {order_sql} 
            {limit_sql}
        """
        
        task_ids = await self.db.fetchall(query, params)
        tasks = []
        
        for row in task_ids:
            task = await self.get_task(row['task_id'])
            if task:
                tasks.append(task)
        
        return tasks

    async def _compute_hierarchy_path(self, parent_task_id: Optional[str], task_id: str) -> str:
        """Compute materialized path for efficient hierarchy queries."""
        if not parent_task_id:
            return f"/root/{task_id}"
        
        parent_path_row = await self.db.fetchone(
            "SELECT hierarchy_path FROM generic_tasks WHERE task_id = ?",
            (parent_task_id,)
        )
        
        if parent_path_row:
            return f"{parent_path_row['hierarchy_path']}/{task_id}"
        else:
            return f"/root/{task_id}"  # Fallback if parent not found
    
    def _infer_type(self, value: Any) -> str:
        """Infer attribute type for storage."""
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"
    
    async def _emit_event(self, task_id: str, event_type: str, event_data: Dict[str, Any]):
        """Emit task lifecycle event."""
        event_id = f"event_{uuid4().hex[:8]}"
        await self.db.execute(
            "INSERT INTO task_events (event_id, task_id, event_type, event_data) VALUES (?, ?, ?, ?)",
            (event_id, task_id, event_type, json.dumps(event_data))
        )
```

## Migration Strategy

### Phase 1: Backward Compatibility Layer

```python
class LegacyCompatibilityLayer:
    """Maintains API compatibility during migration."""
    
    def __init__(self, generic_task_repo: GenericTaskRepository):
        self.repo = generic_task_repo
    
    async def orchestrator_plan_task_legacy(
        self, description: str, subtasks_json: str, complexity: str = "moderate", context: str = None
    ):
        """Legacy orchestrator_plan_task implementation using generic tasks."""
        
        # Create parent task
        parent_task_id = f"task_{uuid4().hex[:8]}"
        parent_task = GenericTask(
            task_id=parent_task_id,
            task_type="breakdown",
            attributes={
                "description": description,
                "complexity": complexity,
                "context": context or ""
            }
        )
        await self.repo.create_task(parent_task)
        
        # Parse and create child tasks
        subtasks_data = json.loads(subtasks_json)
        created_subtasks = []
        
        for subtask_data in subtasks_data:
            child_task_id = f"{subtask_data['specialist_type']}_{uuid4().hex[:6]}"
            child_task = GenericTask(
                task_id=child_task_id,
                task_type="specialist_task",
                parent_task_id=parent_task_id,
                attributes={
                    "title": subtask_data.get("title", ""),
                    "description": subtask_data.get("description", ""),
                    "specialist_type": subtask_data.get("specialist_type", ""),
                    "estimated_effort": subtask_data.get("estimated_effort", "medium"),
                    "dependencies": subtask_data.get("dependencies", [])
                }
            )
            
            # Convert dependencies to new format
            if subtask_data.get("dependencies"):
                child_task.dependencies = [
                    TaskDependency(
                        dependency_task_id=dep_id,
                        dependency_type=DependencyType.COMPLETION,
                        description=f"Depends on completion of {dep_id}"
                    ) for dep_id in subtask_data["dependencies"]
                ]
            
            await self.repo.create_task(child_task)
            created_subtasks.append({
                "task_id": child_task_id,
                "title": child_task.attributes.get("title", ""),
                "specialist_type": child_task.attributes.get("specialist_type", ""),
                "status": child_task.status.value
            })
        
        # Return legacy format
        return {
            "task_created": True,
            "parent_task_id": parent_task_id,
            "description": description,
            "complexity": complexity,
            "subtasks": created_subtasks,
            "next_steps": "Use orchestrator_execute_subtask to start working on individual subtasks"
        }
```

## Integration Patterns

### Event System Integration

```python
class TaskEventSystem:
    """Event system for task lifecycle management."""
    
    def __init__(self):
        self.event_handlers = {}
    
    def register_handler(self, event_type: str, handler_func):
        """Register event handler for specific event types."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler_func)
    
    async def emit_event(self, task_id: str, event_type: str, event_data: Dict[str, Any]):
        """Emit event and call all registered handlers."""
        event = TaskEvent(
            event_id=f"event_{uuid4().hex[:8]}",
            task_id=task_id,
            event_type=event_type,
            event_data=event_data
        )
        
        # Store event in database
        await self._store_event(event)
        
        # Call registered handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Event handler failed for {event_type}: {e}")

# Example: GitHub Integration Plugin
class GitHubIntegrationPlugin:
    def __init__(self, github_client):
        self.github = github_client
    
    async def on_task_created(self, event: TaskEvent):
        """Create GitHub issue when task is created."""
        if event.event_data.get("task_type") == "github_issue":
            task = await task_repo.get_task(event.task_id)
            if task and task.attributes.get("create_github_issue"):
                await self.github.create_issue(
                    title=task.attributes.get("title", "New Task"),
                    body=task.attributes.get("description", ""),
                    labels=task.attributes.get("labels", [])
                )
    
    async def on_status_changed(self, event: TaskEvent):
        """Update GitHub issue when task status changes."""
        if event.event_data.get("new_status") == "completed":
            await self.github.close_issue(event.task_id)
```

## Testing Strategy

### Unit Tests for Generic Task Model

```python
import pytest
from datetime import datetime
from mcp_task_orchestrator.models import GenericTask, TaskDependency, DependencyType

class TestGenericTaskModel:
    
    def test_task_creation(self):
        """Test basic task creation and properties."""
        task = GenericTask(
            task_id="test_task_123",
            task_type="feature_epic",
            attributes={
                "title": "Test Feature",
                "priority": "high"
            }
        )
        
        assert task.task_id == "test_task_123"
        assert task.task_type == "feature_epic"
        assert task.is_root_task is True
        assert task.is_leaf_task is True
        assert task.attributes["title"] == "Test Feature"
    
    def test_hierarchy_relationships(self):
        """Test parent-child relationships."""
        parent = GenericTask(
            task_id="parent_123",
            task_type="epic"
        )
        
        child = GenericTask(
            task_id="child_456",
            task_type="specialist_task",
            parent_task_id="parent_123"
        )
        
        assert parent.is_root_task is True
        assert child.is_root_task is False
        assert child.parent_task_id == "parent_123"
    
    def test_lifecycle_transitions(self):
        """Test lifecycle stage transitions."""
        task = GenericTask(
            task_id="test_123",
            task_type="specialist_task"
        )
        
        # Valid transitions
        assert task.can_transition_to(LifecycleStage.READY) is True
        assert task.can_transition_to(LifecycleStage.ACTIVE) is False  # Must go through READY first
        
        task.lifecycle_stage = LifecycleStage.READY
        assert task.can_transition_to(LifecycleStage.ACTIVE) is True
        assert task.can_transition_to(LifecycleStage.COMPLETED) is False  # Must be ACTIVE first
    
    def test_dependency_management(self):
        """Test task dependency relationships."""
        dependency = TaskDependency(
            dependency_task_id="prereq_123",
            dependency_type=DependencyType.COMPLETION,
            description="Must complete architecture before implementation"
        )
        
        task = GenericTask(
            task_id="impl_456",
            task_type="specialist_task",
            dependencies=[dependency]
        )
        
        assert len(task.dependencies) == 1
        assert task.dependencies[0].dependency_task_id == "prereq_123"
        assert task.dependencies[0].dependency_type == DependencyType.COMPLETION
```

### Integration Tests

```python
class TestGenericTaskRepository:
    
    @pytest.fixture
    async def task_repo(self):
        """Create test repository with in-memory database."""
        # Setup test database and repository
        pass
    
    async def test_create_and_retrieve_task(self, task_repo):
        """Test task creation and retrieval."""
        task = GenericTask(
            task_id="test_create_123",
            task_type="feature_epic",
            attributes={"title": "Test Feature", "priority": "high"}
        )
        
        # Create task
        created_task = await task_repo.create_task(task)
        assert created_task.task_id == "test_create_123"
        
        # Retrieve task
        retrieved_task = await task_repo.get_task("test_create_123")
        assert retrieved_task is not None
        assert retrieved_task.task_id == "test_create_123"
        assert retrieved_task.attributes["title"] == "Test Feature"
    
    async def test_query_tasks_with_filters(self, task_repo):
        """Test flexible task querying."""
        # Create test tasks
        tasks = [
            GenericTask(task_id="task_1", task_type="epic", attributes={"priority": "high"}),
            GenericTask(task_id="task_2", task_type="epic", attributes={"priority": "low"}),
            GenericTask(task_id="task_3", task_type="story", attributes={"priority": "high"})
        ]
        
        for task in tasks:
            await task_repo.create_task(task)
        
        # Query by task type
        epic_tasks = await task_repo.query_tasks(filters={"task_type": "epic"})
        assert len(epic_tasks) == 2
        
        # Query by attributes
        high_priority_tasks = await task_repo.query_tasks(
            filters={"attributes": {"priority": "high"}}
        )
        assert len(high_priority_tasks) == 2
```

## Performance Considerations

### Query Optimization Strategies

1. **Materialized Paths**: Store hierarchy paths for efficient tree queries
2. **Composite Indexes**: Index combinations of frequently queried fields
3. **Attribute Indexing**: Index commonly queried attributes
4. **Connection Pooling**: Efficient database connection management
5. **Query Caching**: Cache frequently accessed task trees

### Scaling Considerations

1. **Database Partitioning**: Partition large task tables by creation date or task type
2. **Read Replicas**: Use read replicas for query-heavy workloads
3. **Event Sourcing**: Consider event sourcing for high-volume audit requirements
4. **Async Processing**: Use background tasks for heavy operations

## Security Considerations

1. **Input Validation**: Validate all task attributes and parameters
2. **Access Control**: Implement role-based access to tasks and templates
3. **Audit Logging**: Log all task modifications and access attempts
4. **Template Security**: Validate template structure to prevent malicious code injection

---

This implementation guide provides the foundation for building the Generic Task Model system. Follow the phased approach to ensure smooth migration and maintain backward compatibility during the transition period.