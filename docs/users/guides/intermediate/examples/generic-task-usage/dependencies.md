

# Dependencies & Relationships

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > Dependencies

#

# Understanding Task Dependencies

Task dependencies define relationships between tasks that affect execution order and approval flows. The Generic Task Model supports multiple dependency types for complex workflow modeling.

#

# Dependency Types

#

#

# Completion Dependencies

Tasks that must finish before another can start:

```python
from mcp_task_orchestrator.models import TaskDependency, DependencyType

# Architecture must complete before implementation

architecture_task = GenericTask(
    task_id="arch_user_auth",
    task_type="specialist_task",
    attributes={
        "title": "Design Authentication Architecture",
        "specialist_type": "architect",
        "estimated_effort": "1 week"
    }
)

implementation_task = GenericTask(
    task_id="impl_user_auth", 
    task_type="specialist_task",
    attributes={
        "title": "Implement Authentication System",
        "specialist_type": "implementer",
        "estimated_effort": "2 weeks"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="arch_user_auth",
            dependency_type=DependencyType.COMPLETION,
            description="Architecture design must be complete before implementation"
        )
    ]
)

```text

#

#

# Approval Dependencies

Tasks that require explicit approval before proceeding:

```text
python

# Code review approval required before deployment

deployment_task = GenericTask(
    task_id="deploy_auth_system",
    task_type="deployment",
    attributes={
        "title": "Deploy Authentication System",
        "environment": "production"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="review_auth_code",
            dependency_type=DependencyType.APPROVAL,
            description="Code review approval required"
        ),
        TaskDependency(
            dependency_task_id="security_audit_auth",
            dependency_type=DependencyType.APPROVAL,
            description="Security audit must pass"
        )
    ]
)

```text

#

#

# Information Dependencies

Tasks that need information or artifacts from other tasks:

```text
python

# Testing needs implementation artifacts

testing_task = GenericTask(
    task_id="test_auth_system",
    task_type="specialist_task",
    attributes={
        "title": "Test Authentication System",
        "specialist_type": "tester"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="impl_user_auth",
            dependency_type=DependencyType.INFORMATION,
            description="Need implementation artifacts and documentation for testing"
        )
    ]
)

```text

#

# Complex Dependency Patterns

#

#

# Sequential Workflow

```text
python

# Linear dependency chain: Design → Implement → Test → Review → Deploy

tasks = [
    GenericTask(
        task_id="design_feature",
        task_type="specialist_task",
        attributes={"title": "Design Feature", "specialist_type": "architect"}
    ),
    GenericTask(
        task_id="implement_feature",
        task_type="specialist_task",
        attributes={"title": "Implement Feature", "specialist_type": "implementer"},
        dependencies=[
            TaskDependency("design_feature", DependencyType.COMPLETION)
        ]
    ),
    GenericTask(
        task_id="test_feature",
        task_type="specialist_task",
        attributes={"title": "Test Feature", "specialist_type": "tester"},
        dependencies=[
            TaskDependency("implement_feature", DependencyType.COMPLETION)
        ]
    ),
    GenericTask(
        task_id="review_feature",
        task_type="specialist_task",
        attributes={"title": "Review Feature", "specialist_type": "reviewer"},
        dependencies=[
            TaskDependency("test_feature", DependencyType.COMPLETION)
        ]
    ),
    GenericTask(
        task_id="deploy_feature",
        task_type="deployment",
        attributes={"title": "Deploy Feature"},
        dependencies=[
            TaskDependency("review_feature", DependencyType.APPROVAL)
        ]
    )
]

```text

#

#

# Parallel Dependencies

```text
python

# Multiple parallel tasks feeding into one final task

security_audit = GenericTask(
    task_id="security_audit",
    task_type="specialist_task",
    attributes={"title": "Security Audit", "specialist_type": "security_specialist"}
)

performance_test = GenericTask(
    task_id="performance_test",
    task_type="specialist_task",
    attributes={"title": "Performance Testing", "specialist_type": "performance_engineer"}
)

integration_test = GenericTask(
    task_id="integration_test",
    task_type="specialist_task",
    attributes={"title": "Integration Testing", "specialist_type": "tester"}
)

# Final deployment depends on all three parallel tasks

production_deploy = GenericTask(
    task_id="production_deploy",
    task_type="deployment",
    attributes={"title": "Production Deployment"},
    dependencies=[
        TaskDependency("security_audit", DependencyType.APPROVAL),
        TaskDependency("performance_test", DependencyType.COMPLETION),
        TaskDependency("integration_test", DependencyType.COMPLETION)
    ]
)

```text

#

#

# Diamond Dependencies

```text
python

# Diamond pattern: One task splits into multiple, then converges

initial_design = GenericTask(
    task_id="initial_design",
    task_type="specialist_task",
    attributes={"title": "Initial System Design", "specialist_type": "architect"}
)

# Parallel implementation tracks

frontend_impl = GenericTask(
    task_id="frontend_impl",
    task_type="specialist_task",
    attributes={"title": "Frontend Implementation", "specialist_type": "frontend_dev"},
    dependencies=[TaskDependency("initial_design", DependencyType.COMPLETION)]
)

backend_impl = GenericTask(
    task_id="backend_impl",
    task_type="specialist_task",
    attributes={"title": "Backend Implementation", "specialist_type": "backend_dev"},
    dependencies=[TaskDependency("initial_design", DependencyType.COMPLETION)]
)

# Integration depends on both implementations

integration_task = GenericTask(
    task_id="system_integration",
    task_type="specialist_task",
    attributes={"title": "System Integration", "specialist_type": "integrator"},
    dependencies=[
        TaskDependency("frontend_impl", DependencyType.COMPLETION),
        TaskDependency("backend_impl", DependencyType.COMPLETION)
    ]
)

```text

#

# Managing Dependencies via API

#

#

# Adding Dependencies

```text
json
{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "deploy_payment_system",
    "dependencies": [
      {
        "dependency_task_id": "security_audit_payment",
        "dependency_type": "approval", 
        "description": "Security team must approve payment handling"
      },
      {
        "dependency_task_id": "integration_test_payment",
        "dependency_type": "completion",
        "description": "All integration tests must pass"
      },
      {
        "dependency_task_id": "pci_compliance_review",
        "dependency_type": "approval",
        "description": "PCI compliance review required for payment processing"
      }
    ],
    "operation": "add"
  }
}

```text

#

#

# Removing Dependencies

```text
json
{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "deploy_payment_system",
    "dependency_ids": ["security_audit_payment"],
    "operation": "remove",
    "reason": "Security audit completed and approved"
  }
}

```text

#

#

# Querying Dependencies

```text
json
{
  "tool": "orchestrator_get_dependencies",
  "arguments": {
    "task_id": "deploy_payment_system",
    "include_transitive": true,
    "show_status": true
  }
}

```text

#

# Dependency Validation

#

#

# Circular Dependency Detection

```text
python
async def validate_no_circular_dependencies(task_id: str, new_dependency_id: str):
    """Prevent circular dependencies when adding new dependencies."""
    
    

# Get all dependencies of the new dependency

    dependency_chain = await orchestrator.get_dependency_chain(new_dependency_id)
    
    

# Check if our task is already in that chain

    if task_id in [dep.task_id for dep in dependency_chain]:
        raise CircularDependencyError(
            f"Adding dependency {new_dependency_id} to {task_id} would create a circular dependency"
        )
    
    return True

```text

#

#

# Dependency Status Validation

```text
python
async def check_dependency_readiness(task_id: str):
    """Check if all dependencies are satisfied for a task."""
    
    task = await orchestrator.get_task(task_id)
    dependency_status = []
    
    for dependency in task.dependencies:
        dep_task = await orchestrator.get_task(dependency.dependency_task_id)
        
        if dependency.dependency_type == DependencyType.COMPLETION:
            satisfied = dep_task.status == "completed"
        elif dependency.dependency_type == DependencyType.APPROVAL:
            satisfied = dep_task.status == "approved"
        else:
            satisfied = dep_task.status in ["completed", "approved"]
        
        dependency_status.append({
            "dependency_id": dependency.dependency_task_id,
            "type": dependency.dependency_type.value,
            "satisfied": satisfied,
            "current_status": dep_task.status
        })
    
    all_satisfied = all(dep["satisfied"] for dep in dependency_status)
    
    return {
        "task_id": task_id,
        "dependencies_satisfied": all_satisfied,
        "dependency_details": dependency_status
    }

```text

#

# Advanced Dependency Patterns

#

#

# Conditional Dependencies

```text
python

# Dependencies that only apply under certain conditions

conditional_task = GenericTask(
    task_id="conditional_deployment",
    task_type="deployment",
    attributes={
        "title": "Conditional Production Deployment",
        "deployment_strategy": "blue_green"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="load_testing",
            dependency_type=DependencyType.COMPLETION,
            description="Load testing required for production deployments",
            conditions={"deployment_environment": "production"}
        ),
        TaskDependency(
            dependency_task_id="basic_testing",
            dependency_type=DependencyType.COMPLETION,
            description="Basic testing sufficient for staging",
            conditions={"deployment_environment": "staging"}
        )
    ]
)

```text

#

#

# Time-Based Dependencies

```text
python

# Dependencies with time constraints

time_sensitive_task = GenericTask(
    task_id="scheduled_release",
    task_type="deployment",
    attributes={
        "title": "Scheduled Production Release",
        "scheduled_time": "2025-07-01T10:00:00Z"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="final_testing",
            dependency_type=DependencyType.COMPLETION,
            description="Final testing must complete 24 hours before release",
            time_constraint={
                "must_complete_before": "2025-06-30T10:00:00Z"
            }
        )
    ]
)

```text

#

#

# Cross-Project Dependencies

```text
python

# Dependencies on tasks in other projects

cross_project_task = GenericTask(
    task_id="integrate_shared_service",
    task_type="feature",
    attributes={
        "title": "Integrate Shared Authentication Service",
        "project": "mobile_app"
    },
    dependencies=[
        TaskDependency(
            dependency_task_id="shared_auth_service_v2",
            dependency_type=DependencyType.COMPLETION,
            description="Shared auth service v2 must be deployed",
            external_project="platform_services"
        )
    ]
)

```text

#

# Best Practices

#

#

# Dependency Design Guidelines

1. **Clear Descriptions**: Always provide clear descriptions explaining why the dependency exists

2. **Appropriate Types**: Use the correct dependency type (completion vs approval vs information)

3. **Minimal Dependencies**: Only add dependencies that are truly necessary

4. **Avoid Over-Coupling**: Don't create unnecessary tight coupling between unrelated tasks

#

#

# Performance Considerations

```text
python

# Efficient dependency resolution

async def resolve_dependencies_efficiently(task_ids: List[str]):
    """Resolve dependencies for multiple tasks efficiently."""
    
    

# Batch load all tasks and their dependencies

    all_tasks = await orchestrator.get_tasks_batch(task_ids)
    
    

# Extract all dependency IDs

    dependency_ids = set()
    for task in all_tasks:
        for dep in task.dependencies:
            dependency_ids.add(dep.dependency_task_id)
    
    

# Batch load all dependency tasks

    dependency_tasks = await orchestrator.get_tasks_batch(list(dependency_ids))
    dependency_map = {task.task_id: task for task in dependency_tasks}
    
    

# Resolve dependencies

    resolution_results = []
    for task in all_tasks:
        task_dependencies = []
        for dep in task.dependencies:
            dep_task = dependency_map.get(dep.dependency_task_id)
            task_dependencies.append({
                "dependency": dep,
                "task": dep_task,
                "satisfied": check_dependency_satisfied(dep, dep_task)
            })
        
        resolution_results.append({
            "task_id": task.task_id,
            "dependencies": task_dependencies,
            "all_satisfied": all(d["satisfied"] for d in task_dependencies)
        })
    
    return resolution_results
```text

---

**Related Documentation**:

- **Previous**: [Basic Operations](basic-operations.md)

- **Next**: [Task Types & Templates](task-types.md)

- **See also**: [Complex Workflows](complex-workflows.md)
