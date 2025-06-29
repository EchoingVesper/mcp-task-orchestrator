# Generic Task Model Design

## Feature Overview
**Status**: CRITICAL ⭐⭐⭐  
**Category**: Core Architecture Enhancement  
**Priority**: FOUNDATIONAL - Enables all v2.0 features  
**Version**: 2.0  
**Date**: 2025-06-03 (Updated)  
**Author**: Task Orchestrator Architecture Team  
**Implementation Timeline**: 8-10 weeks (Phases 1-4)

## Executive Summary

This document outlines a comprehensive redesign of the MCP Task Orchestrator's task model to create a more generic, flexible, and extensible system. The new design eliminates the artificial distinction between tasks and subtasks, introducing a unified, nestable task structure with support for chaining, templates, prerequisites, and advanced lifecycle management.

## Problem Statement

The current task orchestrator has several limitations:
- Fixed task model with hardcoded fields
- Separate "task" and "subtask" concepts create unnecessary complexity
- No support for task chaining or complex dependencies
- Limited extensibility without modifying core code
- No template system for repeatable workflows
- Inadequate lifecycle management and supersession detection

## Proposed Solution

### Core Design Principles

1. **Unified Task Model** - No separate subtask concept; all tasks can contain other tasks
2. **Composition Over Inheritance** - Tasks are composed of behaviors rather than inheriting from rigid classes
3. **Template-Based Instantiation** - Repeatable tasks are templates that can be instantiated
4. **Event-Driven Architecture** - Lifecycle changes trigger events for extensibility
5. **Flexible Attribute System** - Tasks can have custom attributes without schema changes

### Key Components

#### 1. Generic Task Structure
```python
class GenericTask:
    # Core Identity
    task_id: str
    task_type: str
    template_id: Optional[str]
    
    # Hierarchical Structure
    parent_task_id: Optional[str]
    child_task_ids: List[str]
    
    # Dependencies and Chaining
    depends_on: List[TaskDependency]
    chain_position: Optional[int]
    
    # Flexible Attributes
    attributes: Dict[str, Any]
    
    # Lifecycle Management
    status: TaskStatus
    lifecycle_stage: str
    superseded_by: Optional[str]
```

#### 2. Task Templates
- Predefined task structures for common workflows
- Instantiable with parameters
- Examples: GitHub workflows, deployment pipelines, review processes

#### 3. Dependency System
- **Completion Dependencies**: Task B requires Task A to complete first
- **Data Dependencies**: Task B needs output from Task A
- **Approval Dependencies**: Human or automated approval required

#### 4. Prerequisites
- Conditions that must be met before task completion
- Examples: "version number updated", "tests passed", "approval received"
- Can be automatically checked or manually verified

#### 5. Lifecycle Management
- Rich state machine with stages: draft, ready, active, blocked, review, completed, archived, superseded
- Event emission at each transition
- Automatic detection of superseded tasks

## Technical Architecture

### Database Schema

```sql
-- Core task table
CREATE TABLE tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    parent_task_id VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    lifecycle_stage VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    superseded_by VARCHAR(50)
);

-- Flexible attributes (EAV pattern)
CREATE TABLE task_attributes (
    task_id VARCHAR(50) NOT NULL,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value JSON NOT NULL,
    PRIMARY KEY (task_id, attribute_name)
);

-- Dependencies
CREATE TABLE task_dependencies (
    dependent_task_id VARCHAR(50) NOT NULL,
    dependency_task_id VARCHAR(50) NOT NULL,
    dependency_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (dependent_task_id, dependency_task_id)
);
```

### Event System

All task lifecycle changes emit events that can be intercepted:
- `task.created`
- `task.status_changed`
- `task.dependency_satisfied`
- `task.superseded`
- `task.completed`

## Implementation Approach

### Phase 1: Foundation (Weeks 1-2)
1. Design and implement core GenericTask model
2. Create database schema with migration tools
3. Build basic CRUD operations

### Phase 2: Advanced Features (Weeks 3-4)
1. Implement template system
2. Add dependency and chaining support
3. Build prerequisite checking system

### Phase 3: Lifecycle & Events (Weeks 5-6)
1. Implement lifecycle state machine
2. Add event system with hooks
3. Build supersession detection

### Phase 4: Integration (Weeks 7-8)
1. Update MCP tools for new model
2. Create migration tools for existing data
3. Build compatibility layer

## Benefits

1. **Flexibility**: Any task structure can be represented
2. **Reusability**: Templates reduce duplicate work
3. **Clarity**: Explicit dependencies and relationships
4. **Extensibility**: Plugin system support through events
5. **Maintainability**: Clean separation of concerns

## Example Use Cases

### 1. Feature Development Workflow
```python
# Template instantiation creates:
# - Create Feature Branch (GitHub task)
# - Implementation Tasks (nested)
#   - Design Review
#   - Code Implementation
#   - Testing
# - Create Pull Request (GitHub task)
# - Code Review
# - Merge to Main (GitHub task)
```

### 2. Deployment Pipeline
```python
# With prerequisites:
# - Version number must be updated
# - All tests must pass
# - Two approvals required
# Then automatically:
# - Build artifacts
# - Deploy to staging
# - Run smoke tests
# - Deploy to production
```

## Success Metrics

1. Existing functionality remains intact
2. New task types can be added without code changes
3. Complex workflows can be modeled easily
4. Performance remains within 10% of current system
5. Developer satisfaction increases

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Migration complexity | High | Phased approach with compatibility layer |
| Performance degradation | Medium | Optimize queries, add caching |
| Learning curve | Medium | Comprehensive documentation and examples |

## Dependencies

- Plugin Architecture Design
- Database Schema Evolution
- API Design and Tool Updates

## Implementation Strategy

### Migration Approach (Zero-Downtime)

#### Phase 1: Schema Preparation (Week 1)
```sql
-- Create new generic task tables alongside existing
CREATE TABLE generic_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    parent_task_id VARCHAR(50),
    template_id VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    lifecycle_stage VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    superseded_by VARCHAR(50),
    FOREIGN KEY (parent_task_id) REFERENCES generic_tasks(task_id),
    FOREIGN KEY (template_id) REFERENCES task_templates(template_id)
);

-- Compatibility layer for existing tools
CREATE VIEW legacy_task_breakdowns AS 
SELECT task_id as parent_task_id, description, complexity, context, created_at 
FROM generic_tasks WHERE parent_task_id IS NULL;

CREATE VIEW legacy_subtasks AS
SELECT task_id, parent_task_id, title, description, specialist_type, 
       JSON_EXTRACT(attributes, '$.dependencies') as dependencies,
       JSON_EXTRACT(attributes, '$.estimated_effort') as estimated_effort,
       status, created_at
FROM generic_tasks WHERE parent_task_id IS NOT NULL;
```

#### Phase 2: Data Migration (Week 2)
```python
async def migrate_existing_data():
    """Migrate from dual-model to unified model."""
    
    # Migrate parent tasks
    for breakdown in task_breakdowns:
        generic_task = GenericTask(
            task_id=breakdown.parent_task_id,
            task_type="breakdown",
            parent_task_id=None,
            attributes={
                "description": breakdown.description,
                "complexity": breakdown.complexity,
                "context": breakdown.context
            }
        )
        await save_generic_task(generic_task)
    
    # Migrate subtasks as child tasks
    for subtask in subtasks:
        generic_task = GenericTask(
            task_id=subtask.task_id,
            task_type="specialist_task",
            parent_task_id=subtask.parent_task_id,
            attributes={
                "title": subtask.title,
                "description": subtask.description,
                "specialist_type": subtask.specialist_type,
                "dependencies": subtask.dependencies,
                "estimated_effort": subtask.estimated_effort
            }
        )
        await save_generic_task(generic_task)
```

#### Phase 3: API Compatibility (Week 3)
```python
# Maintain existing MCP tools with compatibility layer
async def orchestrator_plan_task_legacy(description: str, subtasks_json: str):
    """Legacy API maintained via generic task model."""
    
    # Create parent generic task
    parent_task = GenericTask(
        task_id=generate_task_id(),
        task_type="breakdown",
        attributes={"description": description}
    )
    
    # Create child generic tasks
    subtasks = json.loads(subtasks_json)
    for subtask_data in subtasks:
        child_task = GenericTask(
            task_id=f"{subtask_data['specialist_type']}_{generate_id()}",
            task_type="specialist_task",
            parent_task_id=parent_task.task_id,
            attributes=subtask_data
        )
        await save_generic_task(child_task)
    
    return legacy_format_response(parent_task)
```

#### Phase 4: New Generic API (Week 4)
```python
# New MCP tools for generic task model
@server.tool("orchestrator_create_generic_task")
async def create_generic_task(
    task_type: str,
    parent_task_id: Optional[str] = None,
    template_id: Optional[str] = None,
    attributes: Dict[str, Any] = None
):
    """Create a new generic task with flexible attributes."""
    
@server.tool("orchestrator_create_from_template")
async def create_from_template(
    template_id: str,
    parameters: Dict[str, Any],
    parent_task_id: Optional[str] = None
):
    """Instantiate a task from a template with parameters."""
    
@server.tool("orchestrator_manage_dependencies")
async def manage_dependencies(
    task_id: str,
    dependencies: List[TaskDependency]
):
    """Add or update task dependencies."""
```

### Template System Implementation

#### Template Definition Structure
```python
class TaskTemplate:
    template_id: str
    name: str
    description: str
    category: str  # "development", "deployment", "review"
    parameters: List[TemplateParameter]
    task_structure: Dict[str, Any]
    
class TemplateParameter:
    name: str
    type: str  # "string", "number", "boolean", "list"
    required: bool
    default_value: Optional[Any]
    description: str

# Example: Feature Development Template
feature_development_template = TaskTemplate(
    template_id="feature_development_v1",
    name="Feature Development Workflow",
    parameters=[
        TemplateParameter("feature_name", "string", True, None, "Name of the feature"),
        TemplateParameter("complexity", "string", False, "moderate", "Feature complexity level")
    ],
    task_structure={
        "root_task": {
            "task_type": "feature_epic",
            "attributes": {"name": "{feature_name}", "complexity": "{complexity}"},
            "children": [
                {
                    "task_type": "specialist_task",
                    "attributes": {
                        "title": "Design {feature_name}",
                        "specialist_type": "architect",
                        "dependencies": []
                    }
                },
                {
                    "task_type": "specialist_task", 
                    "attributes": {
                        "title": "Implement {feature_name}",
                        "specialist_type": "implementer",
                        "dependencies": ["design_task"]
                    }
                }
            ]
        }
    }
)
```

### Event System Architecture

#### Event Emission Points
```python
class TaskEventEmitter:
    async def emit_task_created(self, task: GenericTask):
        await self.emit("task.created", {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "parent_task_id": task.parent_task_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_status_changed(self, task: GenericTask, old_status: str, new_status: str):
        await self.emit("task.status_changed", {
            "task_id": task.task_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        })
    
    async def emit_dependency_satisfied(self, task: GenericTask, dependency: TaskDependency):
        await self.emit("task.dependency_satisfied", {
            "task_id": task.task_id,
            "dependency_task_id": dependency.dependency_task_id,
            "dependency_type": dependency.dependency_type,
            "timestamp": datetime.now().isoformat()
        })
```

#### Plugin Hook System
```python
class TaskPlugin:
    """Base class for task lifecycle plugins."""
    
    async def on_task_created(self, event_data: Dict[str, Any]):
        """Called when a new task is created."""
        pass
    
    async def on_status_changed(self, event_data: Dict[str, Any]):
        """Called when task status changes."""
        pass
    
    async def on_dependency_satisfied(self, event_data: Dict[str, Any]):
        """Called when a task dependency is satisfied."""
        pass

# Example plugin: GitHub Integration
class GitHubIntegrationPlugin(TaskPlugin):
    async def on_task_created(self, event_data: Dict[str, Any]):
        if event_data.get("task_type") == "github_issue":
            await self.create_github_issue(event_data)
    
    async def on_status_changed(self, event_data: Dict[str, Any]):
        if event_data["new_status"] == "completed":
            await self.close_github_issue(event_data["task_id"])
```

## Performance Optimization Strategy

### Database Query Optimization
```sql
-- Materialized path for efficient hierarchy queries
ALTER TABLE generic_tasks ADD COLUMN hierarchy_path TEXT;
UPDATE generic_tasks SET hierarchy_path = '/root/' || task_id WHERE parent_task_id IS NULL;

-- Composite indexes for common query patterns
CREATE INDEX idx_tasks_parent_status ON generic_tasks(parent_task_id, status);
CREATE INDEX idx_tasks_type_lifecycle ON generic_tasks(task_type, lifecycle_stage);
CREATE INDEX idx_tasks_hierarchy_path ON generic_tasks(hierarchy_path);
CREATE INDEX idx_attributes_task_name ON task_attributes(task_id, attribute_name);

-- Efficient dependency queries
CREATE INDEX idx_dependencies_dependent ON task_dependencies(dependent_task_id);
CREATE INDEX idx_dependencies_dependency ON task_dependencies(dependency_task_id);
```

### Caching Strategy
```python
class TaskCacheManager:
    """In-memory caching for frequently accessed task trees."""
    
    def __init__(self):
        self.task_cache = {}
        self.hierarchy_cache = {}
        self.template_cache = {}
    
    async def get_task_tree(self, root_task_id: str) -> Dict[str, GenericTask]:
        """Get entire task tree with caching."""
        if root_task_id not in self.hierarchy_cache:
            tree = await self.load_task_tree_from_db(root_task_id)
            self.hierarchy_cache[root_task_id] = tree
        return self.hierarchy_cache[root_task_id]
    
    async def invalidate_task_tree(self, task_id: str):
        """Invalidate cache when task tree changes."""
        root_id = await self.find_root_task_id(task_id)
        if root_id in self.hierarchy_cache:
            del self.hierarchy_cache[root_id]
```

## Open Questions

1. Should we support task versioning for auditing?
2. How deep should task nesting be allowed?
3. Should templates be stored in database or files?
4. What's the best UI/UX for managing complex task relationships?

## Next Steps

1. Review and approve design
2. Create detailed technical specifications
3. Build proof of concept
4. Plan migration strategy

## References

- Current Architecture Analysis (artifact_4edb9fd4)
- Plugin Architecture Design (upcoming)
- Database Evolution Strategy (upcoming)