

# Complex Workflows

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > Complex Workflows

#

# Real-World Workflow Examples

This section demonstrates complex, well-tested workflows using the Generic Task Model for Large-scale development projects.

#

# Example 1: Complete Feature Development Workflow

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

```text

#

# Example 2: Bug Fix and Hotfix Workflow

```text
python
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
            lifecycle_stage=LifecycleStage.ACTIVE  

# Skip draft, go straight to active

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

```text

#

# Example 3: Release Pipeline with Approvals

```text
python
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

```text

#

# Multi-Team Coordination Patterns

#

## Cross-Team Feature Development

```text
python
async def create_cross_team_feature(feature_spec):
    """Create a feature that requires coordination across multiple teams."""
    
    

# Main feature epic

    feature_epic = GenericTask(
        task_id=f"epic_{feature_spec['name']}",
        task_type="epic",
        attributes={
            "title": feature_spec["title"],
            "description": feature_spec["description"],
            "teams_involved": ["frontend", "backend", "mobile", "qa"],
            "coordination_required": True,
            "estimated_duration": "8 weeks"
        }
    )
    
    

# Team-specific feature components

    team_features = {
        "backend": GenericTask(
            task_id=f"backend_{feature_spec['name']}",
            task_type="feature",
            parent_task_id=feature_epic.task_id,
            attributes={
                "title": f"Backend: {feature_spec['title']}",
                "assigned_team": "backend",
                "estimated_effort": "3 weeks",
                "api_endpoints": feature_spec.get("api_endpoints", [])
            }
        ),
        "frontend": GenericTask(
            task_id=f"frontend_{feature_spec['name']}",
            task_type="feature",
            parent_task_id=feature_epic.task_id,
            attributes={
                "title": f"Frontend: {feature_spec['title']}",
                "assigned_team": "frontend",
                "estimated_effort": "2 weeks",
                "ui_components": feature_spec.get("ui_components", [])
            }
        ),
        "mobile": GenericTask(
            task_id=f"mobile_{feature_spec['name']}",
            task_type="feature",
            parent_task_id=feature_epic.task_id,
            attributes={
                "title": f"Mobile: {feature_spec['title']}",
                "assigned_team": "mobile",
                "estimated_effort": "2.5 weeks",
                "platforms": ["ios", "android"]
            }
        )
    }
    
    

# Cross-team integration tasks

    integration_tasks = [
        GenericTask(
            task_id=f"api_contract_{feature_spec['name']}",
            task_type="specialist_task",
            parent_task_id=feature_epic.task_id,
            attributes={
                "title": "Define API Contract",
                "specialist_type": "architect",
                "teams_involved": ["backend", "frontend", "mobile"],
                "estimated_effort": "1 week"
            }
        ),
        GenericTask(
            task_id=f"integration_testing_{feature_spec['name']}",
            task_type="specialist_task",
            parent_task_id=feature_epic.task_id,
            attributes={
                "title": "Cross-Platform Integration Testing",
                "specialist_type": "tester",
                "test_scope": "full_stack_integration",
                "estimated_effort": "1 week"
            },
            dependencies=[
                TaskDependency(
                    dependency_task_id=team_features["backend"].task_id,
                    dependency_type=DependencyType.COMPLETION
                ),
                TaskDependency(
                    dependency_task_id=team_features["frontend"].task_id,
                    dependency_type=DependencyType.COMPLETION
                ),
                TaskDependency(
                    dependency_task_id=team_features["mobile"].task_id,
                    dependency_type=DependencyType.COMPLETION
                )
            ]
        )
    ]
    
    

# Add dependencies between team features and API contract

    for team_feature in team_features.values():
        team_feature.dependencies = [
            TaskDependency(
                dependency_task_id=f"api_contract_{feature_spec['name']}",
                dependency_type=DependencyType.COMPLETION,
                description="API contract must be defined before team implementation"
            )
        ]
    
    return {
        "epic": feature_epic,
        "team_features": team_features,
        "integration_tasks": integration_tasks,
        "coordination_points": len(integration_tasks)
    }

```text

#

## Enterprise Release Coordination

```text
python
async def create_enterprise_release_coordination(release_info):
    """Create a complex enterprise release with multiple products and teams."""
    
    

# Main release coordination task

    release_epic = GenericTask(
        task_id=f"enterprise_release_{release_info['version']}",
        task_type="enterprise_release",
        attributes={
            "title": f"Enterprise Release {release_info['version']}",
            "release_manager": release_info["release_manager"],
            "target_date": release_info["target_date"],
            "products_included": release_info["products"],
            "customer_communication_required": True,
            "regulatory_compliance_required": True
        }
    )
    
    

# Product-specific release tasks

    product_releases = []
    for product in release_info["products"]:
        product_task = GenericTask(
            task_id=f"product_release_{product['name']}_{release_info['version']}",
            task_type="product_release",
            parent_task_id=release_epic.task_id,
            attributes={
                "title": f"{product['name']} Release {release_info['version']}",
                "product_owner": product["owner"],
                "feature_list": product["features"],
                "estimated_effort": product["estimated_effort"]
            }
        )
        product_releases.append(product_task)
    
    

# Cross-cutting concerns

    compliance_tasks = [
        GenericTask(
            task_id=f"security_compliance_{release_info['version']}",
            task_type="compliance_task",
            parent_task_id=release_epic.task_id,
            attributes={
                "title": "Security Compliance Review",
                "compliance_type": "security",
                "required_certifications": ["SOC2", "ISO27001"],
                "estimated_effort": "2 weeks"
            }
        ),
        GenericTask(
            task_id=f"regulatory_compliance_{release_info['version']}",
            task_type="compliance_task",
            parent_task_id=release_epic.task_id,
            attributes={
                "title": "Regulatory Compliance Review",
                "compliance_type": "regulatory",
                "regulations": ["GDPR", "HIPAA", "PCI_DSS"],
                "estimated_effort": "1 week"
            }
        )
    ]
    
    

# Final coordination and go-live

    go_live_task = GenericTask(
        task_id=f"go_live_{release_info['version']}",
        task_type="go_live_event",
        parent_task_id=release_epic.task_id,
        attributes={
            "title": "Coordinated Go-Live",
            "go_live_time": release_info["go_live_time"],
            "rollback_procedures": "enterprise_rollback_plan",
            "monitoring_duration": "48_hours_post_release"
        },
        dependencies=[
            

# All product releases must be complete

            *[TaskDependency(
                dependency_task_id=product.task_id,
                dependency_type=DependencyType.COMPLETION
            ) for product in product_releases],
            

# All compliance tasks must be approved

            *[TaskDependency(
                dependency_task_id=compliance.task_id,
                dependency_type=DependencyType.APPROVAL
            ) for compliance in compliance_tasks]
        ]
    )
    
    return {
        "release_epic": release_epic,
        "product_releases": product_releases,
        "compliance_tasks": compliance_tasks,
        "go_live_task": go_live_task,
        "total_coordination_points": len(product_releases) + len(compliance_tasks)
    }

```text

#

# Workflow Optimization Patterns

#

## Parallel Execution Optimization

```text
python
async def optimize_workflow_for_parallelism(workflow_tasks):
    """Optimize a workflow to maximize parallel execution."""
    
    

# Analyze dependencies to identify parallel opportunities

    dependency_graph = build_dependency_graph(workflow_tasks)
    
    

# Find tasks that can run in parallel

    parallel_groups = identify_parallel_groups(dependency_graph)
    
    

# Create optimized workflow with parallel execution hints

    optimized_workflow = []
    
    for group in parallel_groups:
        if len(group) > 1:
            

# Multiple tasks can run in parallel

            parallel_task = GenericTask(
                task_id=f"parallel_group_{len(optimized_workflow)}",
                task_type="parallel_execution",
                attributes={
                    "title": "Parallel Execution Group",
                    "parallel_tasks": [task.task_id for task in group],
                    "execution_strategy": "parallel",
                    "estimated_time_savings": calculate_time_savings(group)
                }
            )
            optimized_workflow.append(parallel_task)
        else:
            

# Single task

            optimized_workflow.extend(group)
    
    return {
        "original_tasks": len(workflow_tasks),
        "optimized_tasks": len(optimized_workflow),
        "parallel_groups": len([g for g in parallel_groups if len(g) > 1]),
        "estimated_time_savings": sum(calculate_time_savings(g) for g in parallel_groups if len(g) > 1)
    }
```text

---

**Related Documentation**:

- **Previous**: [MCP Tools Integration](mcp-tools.md)

- **Next**: [Performance & Optimization](performance.md)

- **See also**: [Real-World Examples](..)
