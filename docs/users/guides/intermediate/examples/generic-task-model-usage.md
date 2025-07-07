

# Generic Task Model Usage Examples

This document demonstrates how to use the new Generic Task Model in practice.

#

# Basic Task Creation

```python
from mcp_task_orchestrator.orchestrator.generic_models import (
    GenericTask, TaskType, TaskStatus, LifecycleStage,
    ComplexityLevel, SpecialistType
)

# Create a root task (similar to old TaskBreakdown)

root_task = GenericTask(
    task_id="feature_123",
    title="Implement User Authentication",
    description="Implement complete user authentication system with OAuth support",
    task_type=TaskType.BREAKDOWN,
    hierarchy_path="/feature_123",
    complexity=ComplexityLevel.COMPLEX,
    specialist_type=SpecialistType.ARCHITECT
)

# Create subtasks

design_task = GenericTask(
    task_id="design_auth",
    parent_task_id="feature_123",
    title="Design Authentication Architecture",
    description="Design the authentication system architecture including OAuth flow",
    task_type=TaskType.STANDARD,
    hierarchy_path="/feature_123/design_auth",
    hierarchy_level=1,
    position_in_parent=0,
    specialist_type=SpecialistType.ARCHITECT,
    estimated_effort="1 day"
)

implement_task = GenericTask(
    task_id="impl_auth",
    parent_task_id="feature_123",
    title="Implement Authentication Backend",
    description="Implement the authentication backend with JWT tokens",
    task_type=TaskType.IMPLEMENTATION,
    hierarchy_path="/feature_123/impl_auth",
    hierarchy_level=1,
    position_in_parent=1,
    specialist_type=SpecialistType.IMPLEMENTER,
    estimated_effort="3 days"
)

```text

#

# Working with Custom Attributes

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import AttributeType

# Add custom attributes to tasks

implement_task.add_attribute("priority", "high", AttributeType.STRING, "metadata")
implement_task.add_attribute("story_points", 8, AttributeType.NUMBER, "planning")
implement_task.add_attribute("requires_security_review", True, AttributeType.BOOLEAN, "compliance")

# Add complex configuration

oauth_config = {
    "providers": ["google", "github"],
    "scopes": ["email", "profile"],
    "redirect_uri": "/auth/callback"
}
implement_task.add_attribute("oauth_config", oauth_config, AttributeType.JSON, "configuration")

# Retrieve attributes

priority = implement_task.get_attribute("priority")  

# Returns "high"

points = implement_task.get_attribute("story_points")  

# Returns 8.0

config = implement_task.get_attribute("oauth_config")  

# Returns dict

```text

#

# Managing Dependencies

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import DependencyType

# Add completion dependency

implement_task.add_dependency(
    prerequisite_task_id="design_auth",
    dep_type=DependencyType.COMPLETION,
    mandatory=True,
    auto_satisfy=True
)

# Add data dependency

test_task = GenericTask(
    task_id="test_auth",
    parent_task_id="feature_123",
    title="Test Authentication System",
    description="Comprehensive testing of auth system",
    task_type=TaskType.TESTING,
    hierarchy_path="/feature_123/test_auth",
    hierarchy_level=1,
    specialist_type=SpecialistType.TESTER
)

# Test task needs implementation output

data_dep = TaskDependency(
    dependent_task_id="test_auth",
    prerequisite_task_id="impl_auth",
    dependency_type=DependencyType.DATA,
    output_artifact_ref="auth_api_spec",
    input_parameter_name="api_endpoints"
)
test_task.dependencies.append(data_dep)

# Check if dependencies are satisfied

can_start, blocking_deps = test_task.check_dependencies_satisfied()
if not can_start:
    print(f"Task blocked by {len(blocking_deps)} dependencies")

```text

#

# Lifecycle Management

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import EventType, EventCategory

# Check allowed transitions

current_stage = implement_task.lifecycle_stage
allowed = implement_task.get_allowed_transitions()
print(f"From {current_stage}, can transition to: {allowed}")

# Transition task through lifecycle

if implement_task.can_transition_to(LifecycleStage.ACTIVE):
    implement_task.lifecycle_stage = LifecycleStage.ACTIVE
    implement_task.status = TaskStatus.IN_PROGRESS
    implement_task.started_at = datetime.now()
    
    

# Record the transition event

    implement_task.record_event(
        EventType.LIFECYCLE_CHANGED,
        EventCategory.LIFECYCLE,
        triggered_by="system",
        data={
            "from": "ready",
            "to": "active",
            "reason": "All dependencies satisfied"
        }
    )

# Complete the task

implement_task.lifecycle_stage = LifecycleStage.COMPLETED
implement_task.status = TaskStatus.COMPLETED
implement_task.completed_at = datetime.now()
implement_task.actual_effort = "2.5 days"

# Record completion

implement_task.record_event(
    EventType.COMPLETED,
    EventCategory.LIFECYCLE,
    triggered_by="user",
    data={"completion_notes": "All tests passing"}
)

```text

#

# Working with Templates

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import (
    TaskTemplate, TemplateParameter
)

# Create a reusable template for code reviews

review_template = TaskTemplate(
    template_id="code_review_v1",
    template_name="Standard Code Review Process",
    template_category="development",
    description="Template for standard code review workflow",
    parameters=[
        TemplateParameter(
            name="feature_name",
            type="string",
            description="Name of the feature being reviewed",
            required=True
        ),
        TemplateParameter(
            name="reviewer_count",
            type="number",
            description="Number of reviewers required",
            required=False,
            default=2
        )
    ],
    task_structure={
        "review_root": {
            "title": "Code Review: {{feature_name}}",
            "description": "Complete code review for {{feature_name}}",
            "type": "review",
            "specialist_type": "reviewer",
            "children": {
                "code_review": {
                    "title": "Review Code Changes",
                    "description": "Review code implementation for {{feature_name}}",
                    "type": "review",
                    "specialist_type": "reviewer",
                    "estimated_effort": "2 hours"
                },
                "security_review": {
                    "title": "Security Review",
                    "description": "Review security implications of {{feature_name}}",
                    "type": "review",
                    "specialist_type": "reviewer",
                    "estimated_effort": "1 hour"
                },
                "test_review": {
                    "title": "Test Coverage Review",
                    "description": "Review test coverage for {{feature_name}}",
                    "type": "review",
                    "specialist_type": "tester",
                    "estimated_effort": "1 hour"
                }
            }
        }
    }
)

# Instantiate the template

review_tasks = review_template.instantiate(
    parameters={"feature_name": "OAuth Integration"},
    parent_task_id="feature_123"
)

# The template creates all tasks with proper hierarchy

for task in review_tasks:
    print(f"{task.title} at level {task.hierarchy_level}")

```text

#

# Managing Artifacts

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import TaskArtifact, ArtifactType

# Add artifacts to completed task

auth_spec = TaskArtifact(
    artifact_id="auth_api_spec_v1",
    task_id="impl_auth",
    artifact_type=ArtifactType.DOCUMENTATION,
    artifact_name="Authentication API Specification",
    content="""
    

# Authentication API

    
    

#
# Endpoints

    - POST /auth/login
    - POST /auth/logout
    - POST /auth/refresh
    - GET /auth/user
    """,
    mime_type="text/markdown",
    is_primary=True
)

implement_task.artifacts.append(auth_spec)

# Add code artifact

auth_code = TaskArtifact(
    artifact_id="auth_impl_v1",
    task_id="impl_auth",
    artifact_type=ArtifactType.CODE,
    artifact_name="auth_service.py",
    file_reference="/src/services/auth_service.py",
    file_size=4096,
    mime_type="text/x-python"
)

implement_task.artifacts.append(auth_code)

```text

#

# Database Storage Example

```text
python

# Convert task to storage format

storage_dict = implement_task.to_dict_for_storage()

# This returns a dict with:

# - All scalar fields

# - Datetime fields as ISO strings

# - Context/config as JSON strings

# - Excludes runtime collections (attributes, dependencies, etc.)

# Store in database

cursor.execute("""
    INSERT INTO generic_tasks (
        task_id, parent_task_id, title, description,
        task_type, hierarchy_path, hierarchy_level,
        status, lifecycle_stage, specialist_type,
        estimated_effort, actual_effort, results,
        context, configuration,
        created_at, updated_at, started_at, completed_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    storage_dict['task_id'],
    storage_dict['parent_task_id'],
    storage_dict['title'],
    

# ... etc

))

# Store attributes separately

for attr in implement_task.attributes:
    cursor.execute("""
        INSERT INTO task_attributes (
            task_id, attribute_name, attribute_value,
            attribute_type, attribute_category, is_indexed
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        implement_task.task_id,
        attr.attribute_name,
        attr.attribute_value,
        attr.attribute_type,
        attr.attribute_category,
        attr.is_indexed
    ))

```text

#

# Migration from Old Models

```text
python
from mcp_task_orchestrator.orchestrator.generic_models import (
    create_generic_task_from_breakdown,
    create_generic_task_from_subtask
)
from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask

# Convert old TaskBreakdown

old_breakdown = TaskBreakdown(
    parent_task_id="old_task_123",
    description="Legacy task breakdown",
    complexity=ComplexityLevel.MODERATE,
    subtasks=[]
)

new_root = create_generic_task_from_breakdown(old_breakdown)

# Convert old SubTask

old_subtask = SubTask(
    task_id="old_sub_1",
    title="Legacy subtask",
    description="A subtask from the old system",
    specialist_type=SpecialistType.IMPLEMENTER,
    dependencies=["dep1", "dep2"],
    estimated_effort="1 day"
)

new_subtask = create_generic_task_from_subtask(
    old_subtask,
    parent_task_id=new_root.task_id,
    parent_path=new_root.hierarchy_path,
    position=0
)

```text

#

# Event Stream Processing

```text
python

# Query all events for a task

task_events = implement_task.events

# Filter events by type

status_changes = [
    e for e in task_events 
    if e.event_type == EventType.STATUS_CHANGED
]

# Process events for audit trail

for event in task_events:
    print(f"{event.created_at}: {event.event_type} by {event.triggered_by}")
    if event.event_data:
        print(f"  Data: {event.event_data}")

# Create event-driven notifications

def on_task_completed(event: TaskEvent):
    if event.event_type == EventType.COMPLETED:
        

# Send notification

        notify_stakeholders(event.task_id, event.event_data)
```text

This comprehensive example demonstrates the flexibility and power of the new Generic Task Model, showing how it unifies the previous dual-model system while adding extensive new capabilities for task management, custom attributes, dependencies, templates, and event tracking.
