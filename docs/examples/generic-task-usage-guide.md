# Generic Task Model Usage Guide

> **Audience**: Developers, Project Managers, MCP Tool Users  
> **Version**: 2.0  
> **Created**: 2025-06-03  
> **Status**: Implementation Examples

## Overview

This guide provides practical examples of using the new Generic Task Model (v2.0) with real-world scenarios, code samples, and workflow patterns. The examples demonstrate the power and flexibility of the unified task architecture.

## Quick Start Examples

### Basic Task Creation

#### Simple Task with Attributes
```python
# Creating a basic feature task with flexible attributes
from mcp_task_orchestrator.models import GenericTask

# Simple feature task
feature_task = GenericTask(
    task_id="feature_auth_123",
    task_type="feature_epic",
    attributes={
        "title": "Implement User Authentication",
        "description": "Add login, logout, and session management",
        "priority": "high",
        "estimated_effort": "3 weeks",
        "assigned_team": "backend",
        "labels": ["security", "user-management"],
        "acceptance_criteria": [
            "Users can log in with email/password",
            "Sessions persist across browser restarts",
            "Logout clears all session data",
            "Password reset functionality works"
        ]
    }
)
```

#### Task with Child Tasks (Hierarchical Structure)
```python
# Parent epic with child feature tasks
epic_task = GenericTask(
    task_id="epic_user_system",
    task_type="epic",
    attributes={
        "title": "Complete User Management System",
        "description": "Full user lifecycle management",
        "priority": "critical",
        "estimated_duration": "8 weeks"
    }
)

# Child tasks automatically reference parent
auth_task = GenericTask(
    task_id="feature_auth_456",
    task_type="feature",
    parent_task_id="epic_user_system",  # Links to parent epic
    attributes={
        "title": "User Authentication",
        "estimated_effort": "3 weeks"
    }
)

profile_task = GenericTask(
    task_id="feature_profile_789",
    task_type="feature", 
    parent_task_id="epic_user_system",
    attributes={
        "title": "User Profile Management",
        "estimated_effort": "2 weeks"
    }
)
```

### Using Dependencies Between Tasks

#### Sequential Dependencies
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
```

#### Complex Dependency Patterns
```python
# Multiple dependency types in a deployment workflow
code_review_task = GenericTask(
    task_id="review_auth_code",
    task_type="specialist_task",
    attributes={"title": "Code Review", "specialist_type": "reviewer"}
)

security_audit_task = GenericTask(
    task_id="security_audit_auth",
    task_type="specialist_task", 
    attributes={"title": "Security Audit", "specialist_type": "security_specialist"}
)

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
        ),
        TaskDependency(
            dependency_task_id="impl_user_auth",
            dependency_type=DependencyType.COMPLETION,
            description="Implementation must be complete"
        )
    ]
)
```

## Using the New v2.0 MCP Tools

### Creating Tasks with the Generic API

#### Basic Task Creation
```json
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "feature_epic",
    "attributes": {
      "title": "E-commerce Shopping Cart",
      "description": "Complete shopping cart functionality with persistence",
      "priority": "high",
      "estimated_effort": "4 weeks",
      "business_value": "Enable customers to purchase multiple items"
    }
  }
}
```

#### Creating Nested Task Hierarchies
```json
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "epic",
    "attributes": {
      "title": "E-commerce Platform v2.0",
      "description": "Complete platform redesign with modern architecture"
    }
  }
}

{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "feature",
    "parent_task_id": "epic_ecommerce_v2",
    "attributes": {
      "title": "Shopping Cart Feature",
      "description": "Add, remove, modify cart items with persistence"
    }
  }
}

{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "specialist_task",
    "parent_task_id": "feature_shopping_cart",
    "attributes": {
      "title": "Design Cart Data Model",
      "specialist_type": "architect",
      "estimated_effort": "3 days"
    }
  }
}
```

### Template-Based Workflows

#### Creating a Feature Development Template
```json
{
  "tool": "orchestrator_create_from_template",
  "arguments": {
    "template_id": "feature_development_v1",
    "parameters": {
      "feature_name": "user_notifications",
      "complexity": "moderate",
      "team": "frontend",
      "deadline": "2025-07-15",
      "business_priority": "high"
    },
    "parent_task_id": "epic_user_experience"
  }
}
```

This creates a complete hierarchy:
```
Epic: User Experience
└── Feature: User Notifications
    ├── Architecture Task: Design notification system
    ├── Implementation Task: Build notification components  
    ├── Testing Task: Create notification tests
    └── Review Task: Code review and approval
```

#### Using Bug Fix Template
```json
{
  "tool": "orchestrator_create_from_template", 
  "arguments": {
    "template_id": "bug_fix_workflow_v1",
    "parameters": {
      "bug_title": "Cart items disappear on page refresh",
      "severity": "high", 
      "affected_component": "shopping_cart",
      "reporter": "qa_team",
      "assigned_developer": "john_doe"
    }
  }
}
```

### Dependency Management

#### Adding Complex Dependencies
```json
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
```

#### Querying Tasks with Complex Filters
```json
{
  "tool": "orchestrator_query_tasks",
  "arguments": {
    "filters": {
      "task_type": ["feature", "specialist_task"],
      "status": ["active", "blocked"],
      "attributes": {
        "priority": "high",
        "assigned_team": "backend"
      }
    },
    "sort": {
      "field": "created_at",
      "direction": "desc"
    },
    "limit": 20,
    "include_hierarchy": true
  }
}
```

## Real-World Workflow Examples

### Example 1: Complete Feature Development Workflow

```python
"""
Complete workflow for developing a new feature using Generic Task Model.
This example shows how to create a realistic feature development process.
"""

async def create_feature_development_workflow():
    # 1. Create epic-level task
    epic = GenericTask(
        task_id="epic_real_time_chat",
        task_type="epic",
        attributes={
            "title": "Real-time Chat System",
            "description": "Add real-time messaging capabilities to the platform",
            "business_value": "Increase user engagement and retention",
            "priority": "high",
            "estimated_duration": "6 weeks",
            "stakeholders": ["product_team", "engineering", "design"],
            "success_metrics": [
                "Message delivery time < 100ms",
                "Support for 1000+ concurrent users",
                "99.9% uptime requirement"
            ]
        }
    )
    
    # 2. Break down into features
    features = [
        GenericTask(
            task_id="feature_message_system",
            task_type="feature",
            parent_task_id="epic_real_time_chat",
            attributes={
                "title": "Core Messaging System",
                "description": "Send, receive, and store messages",
                "estimated_effort": "3 weeks"
            }
        ),
        GenericTask(
            task_id="feature_user_presence",
            task_type="feature", 
            parent_task_id="epic_real_time_chat",
            attributes={
                "title": "User Presence Indicators",
                "description": "Show online/offline status and typing indicators",
                "estimated_effort": "1 week"
            }
        ),
        GenericTask(
            task_id="feature_chat_ui",
            task_type="feature",
            parent_task_id="epic_real_time_chat", 
            attributes={
                "title": "Chat User Interface",
                "description": "Responsive chat interface with message history",
                "estimated_effort": "2 weeks"
            }
        )
    ]
    
    # 3. Create specialist tasks for core messaging
    specialist_tasks = [
        GenericTask(
            task_id="arch_messaging_system",
            task_type="specialist_task",
            parent_task_id="feature_message_system",
            attributes={
                "title": "Design Messaging Architecture",
                "specialist_type": "architect",
                "estimated_effort": "3 days",
                "deliverables": [
                    "WebSocket connection architecture",
                    "Message storage schema design", 
                    "Scalability and performance plan"
                ]
            }
        ),
        GenericTask(
            task_id="impl_websocket_server",
            task_type="specialist_task",
            parent_task_id="feature_message_system",
            attributes={
                "title": "Implement WebSocket Server",
                "specialist_type": "implementer",
                "estimated_effort": "1 week"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="arch_messaging_system",
                    dependency_type=DependencyType.COMPLETION,
                    description="Architecture must be complete before implementation"
                )
            ]
        ),
        GenericTask(
            task_id="impl_message_storage",
            task_type="specialist_task",
            parent_task_id="feature_message_system", 
            attributes={
                "title": "Implement Message Storage",
                "specialist_type": "implementer",
                "estimated_effort": "4 days"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="arch_messaging_system",
                    dependency_type=DependencyType.COMPLETION
                )
            ]
        ),
        GenericTask(
            task_id="test_messaging_system",
            task_type="specialist_task",
            parent_task_id="feature_message_system",
            attributes={
                "title": "Test Messaging System", 
                "specialist_type": "tester",
                "estimated_effort": "3 days",
                "test_scenarios": [
                    "Message delivery under load",
                    "Connection reliability testing",
                    "Message ordering and consistency"
                ]
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id="impl_websocket_server",
                    dependency_type=DependencyType.COMPLETION
                ),
                TaskDependency(
                    dependency_task_id="impl_message_storage", 
                    dependency_type=DependencyType.COMPLETION
                )
            ]
        )
    ]
    
    return {
        "epic": epic,
        "features": features,
        "specialist_tasks": specialist_tasks,
        "total_tasks": 1 + len(features) + len(specialist_tasks)
    }
```

### Example 2: Bug Fix and Hotfix Workflow

```python
"""
Example workflow for handling bug fixes with different severity levels.
Shows how to use task attributes for priority and escalation.
"""

async def create_bug_fix_workflow(bug_report):
    # Determine workflow based on severity
    severity = bug_report["severity"]
    
    if severity == "critical":
        # Critical bug - immediate hotfix workflow
        hotfix_task = GenericTask(
            task_id=f"hotfix_{bug_report['id']}",
            task_type="hotfix",
            attributes={
                "title": f"CRITICAL: {bug_report['title']}",
                "description": bug_report["description"],
                "severity": "critical",
                "impact": bug_report["impact"],
                "affected_users": bug_report["affected_users"],
                "sla_deadline": "4 hours",
                "escalation_contacts": ["engineering_manager", "cto"],
                "rollback_plan": "Immediate rollback if issues detected"
            },
            lifecycle_stage=LifecycleStage.ACTIVE  # Skip draft, go straight to active
        )
        
        # Critical bugs get immediate specialist assignment
        fix_task = GenericTask(
            task_id=f"fix_critical_{bug_report['id']}",
            task_type="specialist_task",
            parent_task_id=hotfix_task.task_id,
            attributes={
                "title": "Implement Critical Fix",
                "specialist_type": "debugger",
                "assigned_developer": "on_call_developer",
                "estimated_effort": "2 hours",
                "testing_required": "automated tests + manual verification"
            }
        )
        
    else:
        # Regular bug - standard workflow
        bug_task = GenericTask(
            task_id=f"bug_{bug_report['id']}",
            task_type="bug_fix",
            attributes={
                "title": bug_report["title"],
                "description": bug_report["description"],
                "severity": severity,
                "reported_by": bug_report["reporter"],
                "steps_to_reproduce": bug_report["steps"],
                "expected_behavior": bug_report["expected"],
                "actual_behavior": bug_report["actual"]
            }
        )
        
        # Standard workflow tasks
        investigation_task = GenericTask(
            task_id=f"investigate_{bug_report['id']}",
            task_type="specialist_task",
            parent_task_id=bug_task.task_id,
            attributes={
                "title": "Investigate Bug",
                "specialist_type": "debugger",
                "estimated_effort": "4 hours"
            }
        )
        
        fix_task = GenericTask(
            task_id=f"fix_{bug_report['id']}",
            task_type="specialist_task", 
            parent_task_id=bug_task.task_id,
            attributes={
                "title": "Implement Fix",
                "specialist_type": "implementer", 
                "estimated_effort": "1 day"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id=investigation_task.task_id,
                    dependency_type=DependencyType.COMPLETION,
                    description="Root cause must be identified before fixing"
                )
            ]
        )
        
        test_task = GenericTask(
            task_id=f"test_fix_{bug_report['id']}",
            task_type="specialist_task",
            parent_task_id=bug_task.task_id,
            attributes={
                "title": "Test Bug Fix",
                "specialist_type": "tester",
                "estimated_effort": "2 hours"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id=fix_task.task_id,
                    dependency_type=DependencyType.COMPLETION
                )
            ]
        )
    
    return {"workflow_created": True, "severity": severity}
```

### Example 3: Release Pipeline with Approvals

```python
"""
Complex release pipeline showing approval dependencies and gate-based workflow.
Demonstrates how to model complex organizational processes.
"""

async def create_release_pipeline_workflow(release_version):
    # Main release task
    release_task = GenericTask(
        task_id=f"release_{release_version}",
        task_type="release",
        attributes={
            "title": f"Release {release_version}",
            "version": release_version,
            "release_type": "minor",
            "target_date": "2025-07-01",
            "release_notes_required": True,
            "communication_plan": "internal_announcement + customer_notification"
        }
    )
    
    # Quality gates that must pass
    quality_gates = [
        GenericTask(
            task_id=f"qa_testing_{release_version}",
            task_type="specialist_task",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Complete QA Testing",
                "specialist_type": "tester",
                "test_suites": ["regression", "integration", "performance"],
                "estimated_effort": "3 days"
            }
        ),
        GenericTask(
            task_id=f"security_review_{release_version}",
            task_type="specialist_task", 
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Security Review",
                "specialist_type": "security_specialist",
                "review_areas": ["authentication", "data_protection", "api_security"],
                "estimated_effort": "1 day"
            }
        ),
        GenericTask(
            task_id=f"performance_validation_{release_version}",
            task_type="specialist_task",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Performance Validation",
                "specialist_type": "performance_engineer",
                "benchmarks": ["load_testing", "stress_testing", "capacity_planning"],
                "estimated_effort": "2 days"
            }
        )
    ]
    
    # Approval gates
    approval_tasks = [
        GenericTask(
            task_id=f"product_approval_{release_version}",
            task_type="approval_gate",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Product Manager Approval",
                "approver_role": "product_manager",
                "approval_criteria": ["features_complete", "acceptance_criteria_met"],
                "estimated_effort": "2 hours"
            }
        ),
        GenericTask(
            task_id=f"engineering_approval_{release_version}",
            task_type="approval_gate",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Engineering Manager Approval", 
                "approver_role": "engineering_manager",
                "approval_criteria": ["code_quality", "test_coverage", "documentation"],
                "estimated_effort": "1 hour"
            }
        )
    ]
    
    # Deployment tasks with complex dependencies
    deployment_tasks = [
        GenericTask(
            task_id=f"deploy_staging_{release_version}",
            task_type="deployment",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Deploy to Staging",
                "environment": "staging",
                "estimated_effort": "30 minutes"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id=gate.task_id,
                    dependency_type=DependencyType.COMPLETION,
                    description=f"Quality gate must pass: {gate.attributes['title']}"
                ) for gate in quality_gates
            ]
        ),
        GenericTask(
            task_id=f"staging_validation_{release_version}",
            task_type="specialist_task",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Staging Environment Validation",
                "specialist_type": "tester",
                "validation_checklist": ["smoke_tests", "integration_validation", "user_acceptance"],
                "estimated_effort": "4 hours"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id=f"deploy_staging_{release_version}",
                    dependency_type=DependencyType.COMPLETION
                )
            ]
        ),
        GenericTask(
            task_id=f"deploy_production_{release_version}",
            task_type="deployment",
            parent_task_id=release_task.task_id,
            attributes={
                "title": "Deploy to Production",
                "environment": "production",
                "rollback_plan": "automated_rollback_enabled",
                "monitoring_required": True,
                "estimated_effort": "1 hour"
            },
            dependencies=[
                # All approvals required
                *[TaskDependency(
                    dependency_task_id=approval.task_id,
                    dependency_type=DependencyType.APPROVAL,
                    description=f"Approval required: {approval.attributes['title']}"
                ) for approval in approval_tasks],
                # Staging validation must pass
                TaskDependency(
                    dependency_task_id=f"staging_validation_{release_version}",
                    dependency_type=DependencyType.COMPLETION,
                    description="Staging validation must pass before production deployment"
                )
            ]
        )
    ]
    
    return {
        "release_task": release_task,
        "quality_gates": quality_gates,
        "approval_tasks": approval_tasks, 
        "deployment_tasks": deployment_tasks,
        "total_dependencies": sum(len(task.dependencies) for task in deployment_tasks)
    }
```

## Template Usage Examples

### Creating Custom Templates

#### Feature Development Template Definition
```python
"""
Example of creating a reusable template for feature development.
Templates enable consistent workflows across teams.
"""

feature_development_template = TaskTemplate(
    template_id="feature_development_v2",
    name="Feature Development Workflow",
    description="Standard workflow for developing new features with design, implementation, testing, and review phases",
    category="development", 
    parameters_schema={
        "type": "object",
        "properties": {
            "feature_name": {
                "type": "string",
                "description": "Name of the feature being developed"
            },
            "complexity": {
                "type": "string", 
                "enum": ["simple", "moderate", "complex"],
                "default": "moderate",
                "description": "Complexity level of the feature"
            },
            "team": {
                "type": "string",
                "description": "Team responsible for the feature"
            },
            "estimated_duration": {
                "type": "string",
                "description": "Expected duration (e.g., '2 weeks', '1 month')"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "critical"],
                "default": "medium"
            }
        },
        "required": ["feature_name", "team"]
    },
    task_structure={
        "root_task": {
            "task_type": "feature",
            "attributes": {
                "title": "Feature: {feature_name}",
                "description": "Development of {feature_name} feature",
                "priority": "{priority}",
                "assigned_team": "{team}",
                "estimated_duration": "{estimated_duration}",
                "complexity": "{complexity}"
            },
            "children": [
                {
                    "task_type": "specialist_task",
                    "attributes": {
                        "title": "Design {feature_name} Architecture", 
                        "specialist_type": "architect",
                        "estimated_effort": "2-3 days",
                        "deliverables": [
                            "Technical specification",
                            "API design", 
                            "Database schema changes",
                            "Architecture diagrams"
                        ]
                    }
                },
                {
                    "task_type": "specialist_task",
                    "attributes": {
                        "title": "Implement {feature_name}",
                        "specialist_type": "implementer", 
                        "estimated_effort": "1-2 weeks",
                        "implementation_notes": "Follow established coding standards and patterns"
                    },
                    "dependencies": ["architecture_task"]
                },
                {
                    "task_type": "specialist_task",
                    "attributes": {
                        "title": "Test {feature_name}",
                        "specialist_type": "tester",
                        "estimated_effort": "2-3 days",
                        "test_types": ["unit", "integration", "e2e"]
                    },
                    "dependencies": ["implementation_task"]
                },
                {
                    "task_type": "specialist_task",
                    "attributes": {
                        "title": "Review {feature_name} Implementation",
                        "specialist_type": "reviewer",
                        "estimated_effort": "1 day",
                        "review_checklist": [
                            "Code quality and standards",
                            "Test coverage",
                            "Documentation completeness",
                            "Performance considerations"
                        ]
                    },
                    "dependencies": ["implementation_task", "testing_task"]
                }
            ]
        }
    }
)
```

### Advanced Template Patterns

#### Multi-Phase Project Template
```python
"""
Complex template for multi-phase projects with gates and milestones.
Shows how to model enterprise-level project structures.
"""

enterprise_project_template = TaskTemplate(
    template_id="enterprise_project_v1",
    name="Enterprise Project Workflow",
    description="Multi-phase project template with discovery, planning, implementation, and delivery phases",
    category="enterprise",
    parameters_schema={
        "type": "object",
        "properties": {
            "project_name": {"type": "string"},
            "project_manager": {"type": "string"},
            "budget": {"type": "string"},
            "stakeholders": {
                "type": "array",
                "items": {"type": "string"}
            },
            "delivery_date": {"type": "string", "format": "date"},
            "risk_level": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "default": "medium"
            }
        },
        "required": ["project_name", "project_manager", "delivery_date"]
    },
    task_structure={
        "root_task": {
            "task_type": "project",
            "attributes": {
                "title": "Project: {project_name}",
                "project_manager": "{project_manager}",
                "budget": "{budget}",
                "stakeholders": "{stakeholders}",
                "target_delivery": "{delivery_date}",
                "risk_assessment": "{risk_level}"
            },
            "children": [
                {
                    "task_type": "project_phase",
                    "attributes": {
                        "title": "Discovery Phase",
                        "phase_number": 1,
                        "duration": "2-3 weeks",
                        "gate_criteria": [
                            "Requirements gathered and documented",
                            "Stakeholder alignment achieved", 
                            "Technical feasibility confirmed"
                        ]
                    },
                    "children": [
                        {
                            "task_type": "specialist_task",
                            "attributes": {
                                "title": "Requirements Gathering",
                                "specialist_type": "business_analyst"
                            }
                        },
                        {
                            "task_type": "specialist_task", 
                            "attributes": {
                                "title": "Technical Feasibility Study",
                                "specialist_type": "architect"
                            }
                        }
                    ]
                },
                {
                    "task_type": "project_phase",
                    "attributes": {
                        "title": "Planning Phase",
                        "phase_number": 2,
                        "duration": "3-4 weeks"
                    },
                    "dependencies": ["discovery_phase"],
                    "children": [
                        {
                            "task_type": "specialist_task",
                            "attributes": {
                                "title": "Detailed Project Planning",
                                "specialist_type": "project_manager"
                            }
                        },
                        {
                            "task_type": "specialist_task",
                            "attributes": {
                                "title": "Technical Design",
                                "specialist_type": "architect"
                            }
                        }
                    ]
                }
            ]
        }
    }
)
```

## Migration Examples

### Converting Legacy Tasks to Generic Model

#### Automated Migration Script Example
```python
"""
Example script showing how existing TaskBreakdown and SubTask records
can be automatically converted to the new GenericTask model.
"""

async def migrate_legacy_tasks_to_generic():
    """Convert existing tasks to generic task model during upgrade."""
    
    # Get all existing task breakdowns
    legacy_breakdowns = await get_legacy_task_breakdowns()
    migrated_count = 0
    
    for breakdown in legacy_breakdowns:
        # Convert TaskBreakdown to root GenericTask
        root_task = GenericTask(
            task_id=breakdown.parent_task_id,
            task_type="breakdown",  # Legacy type preserved
            attributes={
                "description": breakdown.description,
                "complexity": breakdown.complexity, 
                "context": breakdown.context,
                "legacy_migration": True,
                "migration_timestamp": datetime.now().isoformat()
            },
            created_at=breakdown.created_at
        )
        
        # Save root task
        await save_generic_task(root_task)
        migrated_count += 1
        
        # Get all subtasks for this breakdown
        legacy_subtasks = await get_legacy_subtasks(breakdown.parent_task_id)
        
        for subtask in legacy_subtasks:
            # Convert SubTask to child GenericTask
            child_task = GenericTask(
                task_id=subtask.task_id,
                task_type="specialist_task",  # Convert to standard type
                parent_task_id=breakdown.parent_task_id,  # Link to parent
                attributes={
                    "title": subtask.title,
                    "description": subtask.description,
                    "specialist_type": subtask.specialist_type,
                    "estimated_effort": subtask.estimated_effort,
                    "legacy_migration": True,
                    "legacy_subtask_id": subtask.task_id,
                    "migration_timestamp": datetime.now().isoformat()
                },
                status=TaskStatus(subtask.status),
                created_at=subtask.created_at,
                completed_at=subtask.completed_at
            )
            
            # Convert legacy dependencies 
            if subtask.dependencies:
                child_task.dependencies = [
                    TaskDependency(
                        dependency_task_id=dep_id,
                        dependency_type=DependencyType.COMPLETION,
                        description=f"Legacy dependency on {dep_id}"
                    ) for dep_id in subtask.dependencies
                ]
            
            # Preserve legacy artifacts and results
            if subtask.results:
                child_task.attributes["legacy_results"] = subtask.results
            if subtask.artifacts:
                child_task.attributes["legacy_artifacts"] = subtask.artifacts
                
            await save_generic_task(child_task)
            migrated_count += 1
    
    return {
        "migration_completed": True,
        "tasks_migrated": migrated_count,
        "legacy_data_preserved": True
    }
```

## Performance Optimization Examples

### Efficient Task Querying
```python
"""
Examples of optimized querying patterns for the Generic Task Model.
Shows how to leverage indexing and caching for performance.
"""

class OptimizedTaskQueries:
    
    def __init__(self, task_repository, cache_manager):
        self.repo = task_repository
        self.cache = cache_manager
    
    async def get_active_tasks_by_team(self, team_name: str) -> List[GenericTask]:
        """Efficiently query active tasks for a specific team."""
        
        cache_key = f"active_tasks_team_{team_name}"
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Optimized query using indexes
        tasks = await self.repo.query_tasks(
            filters={
                "status": ["active", "blocked"],  # Use indexed status field
                "attributes": {"assigned_team": team_name}  # EAV pattern query
            },
            sort_field="updated_at",
            sort_direction="desc"
        )
        
        # Cache for 5 minutes
        await self.cache.set(cache_key, tasks, ttl=300)
        return tasks
    
    async def get_task_hierarchy_tree(self, root_task_id: str) -> Dict[str, Any]:
        """Get complete task tree with efficient hierarchy loading."""
        
        cache_key = f"task_tree_{root_task_id}"
        cached_tree = await self.cache.get(cache_key)
        if cached_tree:
            return cached_tree
        
        # Use materialized path for efficient tree queries
        tree_tasks = await self.repo.query_tasks(
            filters={
                "hierarchy_path": f"%/{root_task_id}/%"  # Materialized path query
            },
            include_hierarchy=True
        )
        
        # Build tree structure
        tree = self._build_task_tree(tree_tasks, root_task_id)
        
        # Cache the complete tree
        await self.cache.set(cache_key, tree, ttl=600)  # 10 minute cache
        return tree
    
    async def get_dependency_chain(self, task_id: str) -> List[GenericTask]:
        """Get complete dependency chain for a task."""
        
        # Use recursive CTE for dependency resolution
        dependency_ids = await self.repo.get_dependency_chain(task_id)
        
        # Batch load all dependencies
        dependencies = await self.repo.get_tasks_batch(dependency_ids)
        
        return dependencies
    
    def _build_task_tree(self, tasks: List[GenericTask], root_id: str) -> Dict[str, Any]:
        """Build hierarchical tree structure from flat task list."""
        
        task_map = {task.task_id: task for task in tasks}
        tree = {"task": task_map.get(root_id), "children": []}
        
        def build_children(parent_id: str, parent_node: Dict[str, Any]):
            children = [task for task in tasks if task.parent_task_id == parent_id]
            for child in children:
                child_node = {"task": child, "children": []}
                build_children(child.task_id, child_node)
                parent_node["children"].append(child_node)
        
        build_children(root_id, tree)
        return tree
```

## Best Practices and Patterns

### Task Modeling Best Practices

1. **Use Descriptive Task Types**
   ```python
   # Good - descriptive and specific
   task_type="feature_epic"
   task_type="security_audit"
   task_type="performance_optimization"
   
   # Avoid - too generic
   task_type="task"
   task_type="work"
   ```

2. **Leverage Attributes for Flexibility**
   ```python
   # Store contextual information in attributes
   attributes={
       "business_value": "Increase conversion rate by 15%",
       "success_metrics": ["load_time < 2s", "error_rate < 0.1%"],
       "rollback_plan": "Feature flag disable",
       "documentation_links": ["wiki/feature-spec", "docs/api-changes"]
   }
   ```

3. **Design Clear Dependency Chains**
   ```python
   # Use descriptive dependency descriptions
   TaskDependency(
       dependency_task_id="security_review_auth",
       dependency_type=DependencyType.APPROVAL,
       description="Security team must approve authentication changes before deployment"
   )
   ```

4. **Plan for Template Reuse**
   ```python
   # Design templates with parameterization in mind
   template_attributes={
       "title": "{component_name} {action_type}",
       "estimated_effort": "{complexity_multiplier} weeks",
       "team_assignment": "{primary_team}"
   }
   ```

This comprehensive usage guide provides practical examples for implementing and using the Generic Task Model effectively across different scenarios and team structures.