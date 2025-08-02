

# Task Artifact: architect_fe43b9

**Type:** design
**Created:** 2025-06-03 11:17:15 UTC
**Summary:** Designed a comprehensive generic task model with nesting, chaining, templates, and flexible attributes based on user requirements

#

# Referenced Files

- `/docs/prompts/features/proposed/generic-task-model-design.md`

#

# Detailed Work

# Generic Task Model Design

#

# Executive Summary

I've designed a new generic task model that eliminates the artificial distinction between tasks and subtasks, introducing a unified, nestable task structure with support for chaining, templates, prerequisites, and advanced lifecycle management. This design provides maximum flexibility while maintaining type safety and performance.

#

# Core Design Principles

1. **Unified Task Model** - No separate subtask concept; all tasks can contain other tasks

2. **Composition Over Inheritance** - Tasks are composed of behaviors rather than inheriting from rigid classes

3. **Template-Based Instantiation** - Repeatable tasks are templates that can be instantiated

4. **Event-Driven Architecture** - Lifecycle changes trigger events for extensibility

5. **Flexible Attribute System** - Tasks can have custom attributes without schema changes

#

# Task Model Architecture

#

#

# Abstract Base Task

```python
class GenericTask:
    """Base task model with extensible properties and behaviors."""
    
    

# Core Identity

    task_id: str                    

# Unique identifier

    task_type: str                  

# References task type registry

    template_id: Optional[str]      

# If instantiated from template

    version: int                    

# For tracking changes

    
    

# Hierarchical Structure

    parent_task_id: Optional[str]   

# For nesting

    child_task_ids: List[str]       

# Nested tasks

    
    

# Dependencies and Chaining

    depends_on: List[TaskDependency]     

# Tasks that must complete first

    blocks: List[str]                    

# Tasks that depend on this

    chain_position: Optional[int]        

# Position in a task chain

    chain_id: Optional[str]              

# Chain this task belongs to

    
    

# State and Lifecycle

    status: TaskStatus              

# Current status

    lifecycle_stage: str            

# Created, Active, Suspended, etc.

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    archived_at: Optional[datetime]
    superseded_by: Optional[str]    

# Task that replaced this one

    
    

# Completion Requirements

    prerequisites: List[Prerequisite]     

# Must be satisfied before completion

    completion_criteria: CompletionCriteria
    
    

# Flexible Attributes

    attributes: Dict[str, Any]      

# Custom attributes per task type

    metadata: Dict[str, Any]        

# System metadata

    
    

# Execution Context

    assigned_to: Optional[str]      

# Specialist type or user

    priority: int
    estimated_effort: Optional[str]
    actual_effort: Optional[str]
    
    

# Results and Artifacts

    results: Optional[TaskResult]
    artifacts: List[ArtifactReference]

```text

#

#

# Task Types and Templates

```text
python
class TaskType:
    """Defines a type of task with its schema and behaviors."""
    
    type_id: str                    

# Unique identifier

    name: str
    description: str
    category: TaskCategory          

# Template, Standard, System

    
    

# Schema Definition

    required_attributes: List[AttributeDefinition]
    optional_attributes: List[AttributeDefinition]
    
    

# Behavior Configuration

    lifecycle_hooks: Dict[str, List[HookReference]]
    validators: List[ValidatorReference]
    processors: List[ProcessorReference]
    
    

# Template Configuration (for repeatable tasks)

    is_template: bool
    instantiation_rules: InstantiationRules
    parameter_schema: Dict[str, Any]  

# Parameters when instantiating

    
    

# Constraints

    can_have_children: bool
    max_nesting_depth: Optional[int]
    allowed_child_types: Optional[List[str]]
    allowed_parent_types: Optional[List[str]]

```text

#

#

# Dependency and Chaining System

```text
python
class TaskDependency:
    """Represents a dependency between tasks."""
    
    dependency_type: DependencyType  

# COMPLETION, DATA, APPROVAL

    task_id: str                    

# Task that must be satisfied

    condition: Optional[str]        

# Additional condition expression

    is_blocking: bool              

# Whether this blocks execution

    inheritance_rule: str          

# How children inherit this dependency

class TaskChain:
    """Represents a sequence of tasks that must execute in order."""
    
    chain_id: str
    name: str
    tasks: List[ChainedTask]       

# Ordered list of tasks

    repeat_rule: Optional[RepeatRule]  

# For recurring chains

    
class ChainedTask:
    """A task within a chain with position and transitions."""
    
    task_id: str
    position: int
    transition_condition: Optional[str]  

# Condition to move to next

    on_failure: FailureStrategy     

# What to do if task fails

```text

#

#

# Prerequisites and Completion Criteria

```text
python
class Prerequisite:
    """A requirement that must be met before task completion."""
    
    prerequisite_id: str
    type: PrerequisiteType         

# FILE_EXISTS, VERSION_UPDATED, TEST_PASSED, etc.

    description: str
    check_expression: str          

# Expression to evaluate

    auto_satisfy: bool            

# Can system automatically satisfy this?

    satisfaction_action: Optional[str]  

# Action to take to satisfy

    
class CompletionCriteria:
    """Defines when a task can be considered complete."""
    
    all_children_complete: bool    

# Must all nested tasks be done?

    prerequisites_satisfied: bool  

# Must all prerequisites be met?

    manual_verification: bool      

# Requires human verification?

    custom_criteria: List[str]     

# Additional expressions to evaluate

```text

#

#

# Lifecycle Management

```text
python
class TaskLifecycle:
    """Manages task state transitions and events."""
    
    STAGES = [
        "draft",      

# Being planned

        "ready",      

# Ready to start

        "active",     

# Being worked on

        "suspended",  

# Temporarily paused

        "blocked",    

# Waiting on dependencies

        "review",     

# Under review

        "completed",  

# Successfully done

        "failed",     

# Failed to complete

        "archived",   

# Archived for history

        "superseded"  

# Replaced by another task

    ]
    
    TRANSITIONS = {
        ("draft", "ready"): "validate_task",
        ("ready", "active"): "start_task",
        ("active", "suspended"): "suspend_task",
        ("active", "blocked"): "check_dependencies",
        ("blocked", "active"): "dependencies_satisfied",
        ("active", "review"): "submit_for_review",
        ("review", "completed"): "approve_completion",
        ("review", "active"): "request_changes",
        ("*", "archived"): "archive_task",
        ("*", "superseded"): "supersede_task"
    }

```text

#

#

# Supersession Detection

```text
python
class SupersessionDetector:
    """Detects when tasks have been superseded by other work."""
    
    detection_rules: List[SupersessionRule]
    
class SupersessionRule:
    """Rule for detecting task supersession."""
    
    rule_id: str
    name: str
    
    

# Detection Criteria

    file_overlap_threshold: float   

# % of files that overlap

    description_similarity: float   

# Semantic similarity threshold

    time_gap: timedelta           

# How old before checking

    status_filter: List[str]      

# Only check tasks in these statuses

    
    

# Actions

    auto_supersede: bool          

# Automatically mark as superseded

    notify: bool                  

# Notify for manual review

    suggest_merge: bool           

# Suggest merging tasks

```text

#

# Database Schema Evolution

#

#

# Core Tables

```text
sql
-- Main task table with essential fields
CREATE TABLE tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL,
    template_id VARCHAR(50),
    version INTEGER DEFAULT 1,
    parent_task_id VARCHAR(50),
    status VARCHAR(20) NOT NULL,
    lifecycle_stage VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    archived_at TIMESTAMP,
    superseded_by VARCHAR(50),
    
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (task_type) REFERENCES task_types(type_id),
    FOREIGN KEY (template_id) REFERENCES task_templates(template_id)
);

-- Flexible attribute storage (EAV pattern)
CREATE TABLE task_attributes (
    task_id VARCHAR(50) NOT NULL,
    attribute_name VARCHAR(100) NOT NULL,
    attribute_value JSON NOT NULL,
    attribute_type VARCHAR(50) NOT NULL,
    
    PRIMARY KEY (task_id, attribute_name),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- Task dependencies for chaining
CREATE TABLE task_dependencies (
    dependent_task_id VARCHAR(50) NOT NULL,
    dependency_task_id VARCHAR(50) NOT NULL,
    dependency_type VARCHAR(20) NOT NULL,
    condition TEXT,
    is_blocking BOOLEAN DEFAULT TRUE,
    
    PRIMARY KEY (dependent_task_id, dependency_task_id),
    FOREIGN KEY (dependent_task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (dependency_task_id) REFERENCES tasks(task_id)
);

-- Prerequisites for completion
CREATE TABLE task_prerequisites (
    task_id VARCHAR(50) NOT NULL,
    prerequisite_id VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    check_expression TEXT NOT NULL,
    is_satisfied BOOLEAN DEFAULT FALSE,
    satisfied_at TIMESTAMP,
    
    PRIMARY KEY (task_id, prerequisite_id),
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- Task type definitions
CREATE TABLE task_types (
    type_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL,
    schema_definition JSON NOT NULL,
    is_template BOOLEAN DEFAULT FALSE,
    can_have_children BOOLEAN DEFAULT TRUE,
    max_nesting_depth INTEGER
);

-- Task templates for repeatable tasks
CREATE TABLE task_templates (
    template_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,
    default_attributes JSON,
    instantiation_rules JSON,
    
    FOREIGN KEY (task_type) REFERENCES task_types(type_id)
);

```text

#

# Key Design Decisions

#

#

# 1. Unified Task Model

- **Decision**: Eliminate subtasks; all tasks can contain other tasks

- **Rationale**: Simpler mental model, more flexibility, recursive operations

- **Trade-off**: Slightly more complex queries for flat task lists

#

#

# 2. EAV Pattern for Attributes

- **Decision**: Use Entity-Attribute-Value pattern for custom attributes

- **Rationale**: Maximum flexibility without schema changes

- **Trade-off**: More complex queries, but can be optimized with views/indexes

#

#

# 3. Template-Based Repeatability

- **Decision**: Templates are special task types that can be instantiated

- **Rationale**: Reusable components without code duplication

- **Trade-off**: Additional complexity in task creation flow

#

#

# 4. Event-Driven Lifecycle

- **Decision**: All state changes emit events for extensibility

- **Rationale**: Enables plugins and custom behaviors

- **Trade-off**: Slight performance overhead for event dispatch

#

#

# 5. Explicit Dependency Tracking

- **Decision**: Store dependencies as first-class relationships

- **Rationale**: Enables complex workflows and clear visualization

- **Trade-off**: More storage and maintenance overhead

#

# Migration Strategy

#

#

# Phase 1: Compatibility Layer

1. Create new tables alongside existing ones

2. Implement adapters to translate between old and new models

3. Dual-write to both systems during transition

#

#

# Phase 2: Gradual Migration

1. Migrate existing tasks to new model

2. Update tools to use new API while maintaining old interface

3. Convert subtasks to nested tasks

#

#

# Phase 3: Cleanup

1. Remove old tables and code

2. Optimize queries for new structure

3. Update documentation

#

# Example Usage Scenarios

#

#

# 1. Feature Development with GitHub Integration

```text
python

# Create a feature template

feature_template = TaskTemplate(
    name="Feature Development Workflow",
    task_type="workflow_template",
    instantiation_rules={
        "auto_create_github_tasks": True,
        "require_branch_name": True
    }
)

# Instantiate for a specific feature

feature_task = create_task_from_template(
    template=feature_template,
    parameters={
        "feature_name": "User Authentication",
        "branch_name": "feature/user-auth"
    }
)

# Automatically creates nested tasks:

# - GitHub: Create Feature Branch

# - Implementation Tasks (nested)

# - GitHub: Create Pull Request

# - Review and Merge

```text

#

#

# 2. Deployment Pipeline with Prerequisites

```python
deployment_task = GenericTask(
    task_type="deployment",
    prerequisites=[
        Prerequisite(
            type="VERSION_UPDATED",
            check_expression="package.version != previous.version"
        ),
        Prerequisite(
            type="TESTS_PASSED",
            check_expression="test_results.failed_count == 0"
        ),
        Prerequisite(
            type="APPROVAL",
            check_expression="approvals.count >= 2"
        )
    ]
)

```text

#

#

# 3. Supersession Detection

```text
python

# System automatically detects:

old_task = get_task("implement_user_login")
new_task = get_task("implement_authentication_system")

# If new_task modifies 80% of the same files as old_task

# and has similar description, suggest supersession

if detect_supersession(old_task, new_task):
    old_task.superseded_by = new_task.task_id
    old_task.lifecycle_stage = "superseded"
```text

#

# Benefits of This Design

1. **Flexibility**: Any task structure can be represented

2. **Extensibility**: New task types without code changes

3. **Reusability**: Templates for common workflows

4. **Clarity**: Dependencies and prerequisites are explicit

5. **Maintainability**: Clean lifecycle management

6. **Scalability**: Efficient storage and querying

#

# Next Steps Recommendations

1. **Plugin Architecture Design** - Build on this event-driven model

2. **API Design** - Create clean interfaces for the new model

3. **Performance Optimization** - Plan for efficient queries on nested structures

4. **Tool Updates** - Design new MCP tools for the generic model

This generic task model provides a solid foundation for a highly flexible and extensible task orchestration system that addresses all the requirements while maintaining clarity and performance.

---

*This artifact was generated by the MCP Task Orchestrator on 2025-06-03 11:17:15 UTC*
*Task ID: architect_fe43b9*
