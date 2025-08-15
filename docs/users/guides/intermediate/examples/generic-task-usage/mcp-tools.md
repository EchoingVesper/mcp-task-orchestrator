

# MCP Tools Integration

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > MCP Tools Integration

#

# Using the v2.0 MCP Tools

The Generic Task Model provides a comprehensive MCP API for creating, managing, and querying tasks. This guide covers the key MCP tools and their usage patterns.

#

# Task Creation Tools

#

#

# orchestrator_create_generic_task

Create a new generic task with flexible attributes:

```json
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "feature_epic",
    "attributes": {
      "title": "User Dashboard Redesign",
      "description": "Complete overhaul of user dashboard with modern UI",
      "priority": "high",
      "estimated_effort": "6 weeks",
      "assigned_team": "frontend",
      "business_value": "Improve user engagement and retention",
      "stakeholders": ["product", "design", "engineering"]
    },
    "parent_task_id": "epic_ux_improvements"
  }
}

```text

Response:

```text
json
{
  "status": "success",
  "task_id": "feature_dashboard_redesign_001",
  "task_type": "feature_epic",
  "created_at": "2025-06-04T10:30:00Z",
  "hierarchy_level": 2
}

```text
text

#

#

# orchestrator_create_from_template

Create tasks from predefined templates:

```text
json
{
  "tool": "orchestrator_create_from_template",
  "arguments": {
    "template_id": "feature_development_v1",
    "parameters": {
      "feature_name": "user_notifications",
      "complexity": "moderate",
      "team": "backend",
      "deadline": "2025-07-15",
      "business_priority": "high"
    },
    "parent_task_id": "epic_user_experience"
  }
}

```text

This automatically creates a structured workflow:

```text

Epic: User Experience
└── Feature: User Notifications
    ├── Architecture Task: Design notification system
    ├── Implementation Task: Build notification components  
    ├── Testing Task: Create notification tests
    └── Review Task: Code review and approval

```text
text

#

# Task Query Tools

#

#

# orchestrator_query_tasks

Powerful querying with filters, sorting, and pagination:

```text
json
{
  "tool": "orchestrator_query_tasks",
  "arguments": {
    "filters": {
      "task_type": ["feature", "specialist_task"],
      "status": ["active", "blocked"],
      "attributes": {
        "priority": "high",
        "assigned_team": "backend"
      },
      "created_after": "2025-06-01T00:00:00Z"
    },
    "sort": {
      "field": "updated_at",
      "direction": "desc"
    },
    "limit": 50,
    "include_hierarchy": true,
    "include_dependencies": true
  }
}

```text

#

#

# orchestrator_get_task_hierarchy

Get complete task trees:

```text
json
{
  "tool": "orchestrator_get_task_hierarchy",
  "arguments": {
    "root_task_id": "epic_mobile_app_v2",
    "include_completed": false,
    "max_depth": 4,
    "include_statistics": true
  }
}

```text

Response includes hierarchy statistics:

```text
json
{
  "root_task": {...},
  "hierarchy": [...],
  "statistics": {
    "total_tasks": 45,
    "completed_tasks": 12,
    "active_tasks": 8,
    "blocked_tasks": 2,
    "completion_percentage": 26.7,
    "estimated_remaining_effort": "12 weeks"
  }
}

```text
text

#

# Task Management Tools

#

#

# orchestrator_update_task

Update task attributes and metadata:

```text
json
{
  "tool": "orchestrator_update_task",
  "arguments": {
    "task_id": "feature_user_auth_123",
    "updates": {
      "attributes": {
        "priority": "critical",
        "assigned_developer": "senior_dev_jane",
        "estimated_effort": "4 weeks",
        "complexity": "high",
        "risk_factors": ["security_requirements", "legacy_integration"],
        "milestone": "Q3_2025_release"
      },
      "status": "active"
    },
    "update_reason": "Increased priority due to security requirements"
  }
}

```text

#

#

# orchestrator_manage_dependencies

Add, remove, or modify task dependencies:

```text
json
{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "deploy_payment_gateway",
    "operation": "add",
    "dependencies": [
      {
        "dependency_task_id": "security_audit_payment",
        "dependency_type": "approval",
        "description": "Security audit must approve payment processing implementation",
        "criticality": "high"
      },
      {
        "dependency_task_id": "pci_compliance_verification",
        "dependency_type": "completion",
        "description": "PCI compliance verification must be complete",
        "criticality": "critical"
      },
      {
        "dependency_task_id": "load_testing_payment",
        "dependency_type": "completion",
        "description": "Load testing must validate payment system performance"
      }
    ]
  }
}

```text

#

# Template Management Tools

#

#

# orchestrator_create_template

Create reusable task templates:

```text
json
{
  "tool": "orchestrator_create_template",
  "arguments": {
    "template_id": "bug_fix_workflow_v2",
    "name": "Bug Fix Workflow",
    "description": "Standard workflow for bug fixes with investigation, implementation, and testing",
    "category": "maintenance",
    "parameters_schema": {
      "type": "object",
      "properties": {
        "bug_title": {"type": "string"},
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "affected_component": {"type": "string"},
        "reporter": {"type": "string"},
        "assigned_developer": {"type": "string"}
      },
      "required": ["bug_title", "severity", "affected_component"]
    },
    "task_structure": {
      "root_task": {
        "task_type": "bug_fix",
        "attributes": {
          "title": "Bug: {bug_title}",
          "severity": "{severity}",
          "affected_component": "{affected_component}",
          "reported_by": "{reporter}",
          "assigned_to": "{assigned_developer}"
        },
        "children": [
          {
            "task_type": "specialist_task",
            "attributes": {
              "title": "Investigate: {bug_title}",
              "specialist_type": "debugger",
              "estimated_effort": "2-4 hours"
            }
          },
          {
            "task_type": "specialist_task",
            "attributes": {
              "title": "Fix: {bug_title}",
              "specialist_type": "implementer",
              "estimated_effort": "4-8 hours"
            },
            "dependencies": ["investigation_task"]
          },
          {
            "task_type": "specialist_task",
            "attributes": {
              "title": "Test Fix: {bug_title}",
              "specialist_type": "tester",
              "estimated_effort": "1-2 hours"
            },
            "dependencies": ["fix_task"]
          }
        ]
      }
    }
  }
}

```text

#

#

# orchestrator_list_templates

Browse available templates:

```text
json
{
  "tool": "orchestrator_list_templates",
  "arguments": {
    "category": "development",
    "include_usage_stats": true,
    "sort_by": "popularity"
  }
}

```text

#

# Advanced Query Tools

#

#

# orchestrator_analyze_dependencies

Analyze dependency relationships and bottlenecks:

```text
json
{
  "tool": "orchestrator_analyze_dependencies",
  "arguments": {
    "scope": "project",
    "project_id": "mobile_app_v2",
    "analysis_type": "bottlenecks",
    "include_recommendations": true
  }
}

```text

Response:

```text
json
{
  "analysis_results": {
    "critical_path": ["design_auth", "implement_auth", "test_auth", "deploy_auth"],
    "bottlenecks": [
      {
        "task_id": "security_review_001",
        "blocking_tasks": 8,
        "estimated_delay_impact": "2 weeks",
        "recommendation": "Assign additional security reviewer"
      }
    ],
    "parallel_opportunities": [
      {
        "task_group": ["frontend_impl", "backend_impl", "mobile_impl"],
        "potential_time_savings": "3 weeks"
      }
    ]
  }
}

```text
text

#

#

# orchestrator_get_metrics

Get project and task metrics:

```text
json
{
  "tool": "orchestrator_get_metrics",
  "arguments": {
    "metric_types": ["velocity", "completion_rate", "effort_accuracy"],
    "time_period": "last_30_days",
    "group_by": ["team", "task_type"],
    "include_trends": true
  }
}

```text

#

# Bulk Operations

#

#

# orchestrator_bulk_update

Update multiple tasks at once:

```text
json
{
  "tool": "orchestrator_bulk_update",
  "arguments": {
    "filters": {
      "task_type": "specialist_task",
      "attributes": {"assigned_team": "backend"}
    },
    "updates": {
      "attributes": {
        "sprint": "sprint_2025_q3_01",
        "updated_by": "team_lead_backend"
      }
    },
    "dry_run": false,
    "update_reason": "Assigning tasks to Q3 Sprint 1"
  }
}

```text

#

#

# orchestrator_batch_create

Create multiple related tasks efficiently:

```text
json
{
  "tool": "orchestrator_batch_create",
  "arguments": {
    "tasks": [
      {
        "task_type": "feature",
        "attributes": {"title": "User Profile Page"},
        "parent_task_id": "epic_user_system"
      },
      {
        "task_type": "feature", 
        "attributes": {"title": "User Settings Page"},
        "parent_task_id": "epic_user_system"
      },
      {
        "task_type": "feature",
        "attributes": {"title": "User Preferences"},
        "parent_task_id": "epic_user_system"
      }
    ],
    "auto_link_dependencies": true,
    "generate_specialist_tasks": true
  }
}

```text

#

# Integration Patterns

#

#

# Claude Code Integration

Using MCP tools within Claude Code workflows:

```text
python

# Example of using MCP tools in a development workflow

async def create_feature_with_claude_code():
    """Example of creating a feature using MCP tools via Claude Code."""
    
    

# Step 1: Create the main feature task

    feature_result = await mcp_call({
        "tool": "orchestrator_create_generic_task",
        "arguments": {
            "task_type": "feature",
            "attributes": {
                "title": "Real-time Chat Feature",
                "description": "Add real-time messaging to the platform",
                "estimated_effort": "4 weeks",
                "priority": "high"
            }
        }
    })
    
    feature_id = feature_result["task_id"]
    
    

# Step 2: Create specialist tasks using template

    workflow_result = await mcp_call({
        "tool": "orchestrator_create_from_template",
        "arguments": {
            "template_id": "feature_development_v1",
            "parameters": {
                "feature_name": "real_time_chat",
                "complexity": "moderate"
            },
            "parent_task_id": feature_id
        }
    })
    
    

# Step 3: Add custom dependencies

    await mcp_call({
        "tool": "orchestrator_manage_dependencies",
        "arguments": {
            "task_id": f"{feature_id}_deploy",
            "operation": "add",
            "dependencies": [
                {
                    "dependency_task_id": "infrastructure_websockets",
                    "dependency_type": "completion",
                    "description": "WebSocket infrastructure must be ready"
                }
            ]
        }
    })
    
    return {"feature_id": feature_id, "workflow_created": True}
```text

#

#

# Error Handling in MCP Tools

MCP tools return structured error responses for validation failures and other issues. See [Troubleshooting](troubleshooting.md) for detailed error handling patterns.

#

# Best Practices

#

#

# Efficient API Usage

1. **Batch Operations**: Use bulk tools when operating on multiple tasks

2. **Selective Queries**: Use filters to reduce response size

3. **Caching**: Cache frequently accessed hierarchies and templates

4. **Error Handling**: Always handle MCP tool errors gracefully

#

#

# Tool Selection Guidelines

- **Creating single tasks**: Use `orchestrator_create_generic_task`

- **Creating structured workflows**: Use `orchestrator_create_from_template`

- **Querying with flexibility**: Use `orchestrator_query_tasks`

- **Managing relationships**: Use `orchestrator_manage_dependencies`

- **Bulk operations**: Use `orchestrator_bulk_update` or `orchestrator_batch_create`

---

**Related Documentation**:

- **Previous**: [Dependencies & Relationships](dependencies.md)

- **Next**: [Complex Workflows](complex-workflows.md)

- **See also**: [API Quick Reference](../../../../referenceapi-reference.md)
