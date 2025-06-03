# Generic Task Model Workflow Patterns

> **Audience**: Development Teams, Project Managers, DevOps Engineers  
> **Version**: 2.0  
> **Created**: 2025-06-03  
> **Focus**: Practical workflow patterns using Generic Task Model

## Overview

This document provides proven workflow patterns using the Generic Task Model. Each pattern includes MCP tool usage, task hierarchies, and dependency management for real-world scenarios.

## Development Workflow Patterns

### Pattern 1: Agile Sprint Planning

#### Sprint Setup with Generic Tasks
```json
// Create sprint epic
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "sprint",
    "attributes": {
      "title": "Sprint 23 - User Management Features",
      "sprint_number": 23,
      "start_date": "2025-06-16",
      "end_date": "2025-06-30", 
      "team": "backend_team",
      "sprint_goal": "Complete user authentication and profile management",
      "capacity": "80 story_points",
      "scrum_master": "alice_johnson"
    }
  }
}

// Add user stories to sprint
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "user_story",
    "parent_task_id": "sprint_23_backend",
    "attributes": {
      "title": "As a user, I want to reset my password",
      "story_points": 8,
      "priority": "high",
      "acceptance_criteria": [
        "User receives reset email within 2 minutes",
        "Reset link expires after 24 hours", 
        "New password meets security requirements"
      ],
      "definition_of_done": [
        "Feature implemented and tested",
        "Code reviewed and approved",
        "Documentation updated"
      ]
    }
  }
}

// Break story into tasks
{
  "tool": "orchestrator_create_from_template",
  "arguments": {
    "template_id": "user_story_breakdown_v1",
    "parameters": {
      "story_title": "password_reset",
      "complexity": "moderate",
      "backend_effort": "6 points",
      "frontend_effort": "2 points"
    },
    "parent_task_id": "story_password_reset"
  }
}
```

### Pattern 2: Feature Flag Deployment

#### Progressive Feature Rollout with MCP Tools
```json
// Create feature flag deployment task
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "feature_flag_deployment",
    "attributes": {
      "title": "Advanced Search Feature Rollout",
      "feature_flag": "advanced_search_v2",
      "rollout_strategy": "progressive",
      "success_metrics": [
        "search_performance < 200ms",
        "user_satisfaction > 4.5/5",
        "error_rate < 0.1%"
      ],
      "rollback_triggers": [
        "error_rate > 1%",
        "performance_degradation > 20%"
      ]
    }
  }
}

// Add rollout stages with dependencies
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "deployment_stage",
    "parent_task_id": "feature_advanced_search_rollout",
    "attributes": {
      "title": "Beta User Rollout (10%)",
      "stage": "beta",
      "rollout_percentage": 10,
      "monitoring_dashboard": "feature_flag_metrics_beta"
    }
  }
}

{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "beta_rollout_stage",
    "dependencies": [
      {
        "dependency_task_id": "internal_testing_stage",
        "dependency_type": "completion",
        "description": "Internal testing must pass before beta rollout"
      }
    ]
  }
}
```

## DevOps and Infrastructure Patterns

### Pattern 3: Multi-Environment Deployment Pipeline

```json
// Infrastructure deployment across environments
{
  "tool": "orchestrator_create_from_template",
  "arguments": {
    "template_id": "multi_env_deployment_v1",
    "parameters": {
      "change_description": "Kubernetes cluster upgrade to v1.28",
      "environments": ["dev", "staging", "production"],
      "risk_level": "high",
      "maintenance_window": "2025-06-15T02:00:00Z"
    }
  }
}

// This creates:
// Infrastructure Change: Kubernetes Upgrade
// ├── Dev Environment Deployment
// │   ├── Pre-deployment validation
// │   ├── Upgrade execution
// │   └── Post-deployment testing
// ├── Staging Environment Deployment (depends on dev)
// │   ├── Pre-deployment validation  
// │   ├── Upgrade execution
// │   └── Post-deployment testing
// └── Production Environment Deployment (depends on staging)
//     ├── Pre-deployment validation
//     ├── Upgrade execution
//     └── Post-deployment testing
```

### Pattern 4: Incident Response Workflow

```json
// Critical security incident
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "security_incident",
    "attributes": {
      "title": "CRITICAL: Potential Data Breach Detected",
      "severity": "critical",
      "incident_id": "SEC-2025-0603-001",
      "affected_systems": ["user_database", "auth_service"],
      "incident_commander": "security_team_lead",
      "stakeholders": ["ciso", "cto", "legal_team"]
    },
    "lifecycle_stage": "active"
  }
}

// Immediate response tasks
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "incident_response_task",
    "parent_task_id": "sec_incident_001",
    "attributes": {
      "title": "Immediate Containment",
      "sla": "15 minutes",
      "actions": [
        "Isolate affected systems",
        "Revoke potentially compromised credentials",
        "Enable enhanced monitoring"
      ]
    }
  }
}
```

## Quality Assurance Patterns

### Pattern 5: Comprehensive Testing Strategy

```json
// Multi-level testing for payment feature
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "testing_epic",
    "attributes": {
      "title": "Payment Processing Feature Testing",
      "feature_under_test": "payment_processing_v2",
      "compliance_testing": ["pci_dss", "sox_compliance"],
      "performance_targets": {
        "response_time": "< 500ms",
        "throughput": "> 1000 tps",
        "availability": "99.99%"
      }
    }
  }
}

// Testing phases with proper sequencing
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "testing_phase",
    "parent_task_id": "testing_payment_processing",
    "attributes": {
      "title": "Unit Testing Phase",
      "coverage_target": "90%",
      "test_frameworks": ["jest", "pytest"]
    }
  }
}

{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "integration_testing_phase",
    "dependencies": [
      {
        "dependency_task_id": "unit_testing_phase",
        "dependency_type": "completion",
        "description": "Unit tests must pass before integration testing"
      }
    ]
  }
}
```

## Data Pipeline Patterns

### Pattern 6: ETL Pipeline with Quality Gates

```json
// Customer analytics pipeline
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "data_pipeline",
    "attributes": {
      "title": "Customer Analytics ETL Pipeline",
      "schedule": "daily_at_2am",
      "data_sources": ["orders_db", "customer_db"],
      "compliance_requirements": ["gdpr", "ccpa"]
    }
  }
}

// Pipeline stages with data quality checks
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "data_extraction",
    "parent_task_id": "pipeline_customer_analytics",
    "attributes": {
      "title": "Extract Customer Data",
      "quality_checks": [
        "row_count_validation",
        "schema_validation",
        "data_freshness_check"
      ]
    }
  }
}

{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "data_transformation",
    "parent_task_id": "pipeline_customer_analytics",
    "attributes": {
      "title": "Transform Customer Data",
      "data_quality_rules": [
        "completeness > 95%",
        "validity > 98%"
      ]
    }
  }
}

{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "data_transformation_task",
    "dependencies": [
      {
        "dependency_task_id": "data_extraction_task",
        "dependency_type": "completion",
        "description": "Extraction must complete before transformation"
      }
    ]
  }
}
```

## Template Creation Examples

### Pattern 7: Domain-Specific Templates

```python
# E-commerce feature template
ecommerce_template = {
    "template_id": "ecommerce_feature_v1",
    "name": "E-commerce Feature Development",
    "parameters_schema": {
        "type": "object",
        "properties": {
            "feature_name": {"type": "string"},
            "business_impact": {"type": "string"},
            "customer_segment": {
                "type": "string",
                "enum": ["b2b", "b2c", "marketplace"]
            },
            "revenue_impact": {"type": "string"}
        },
        "required": ["feature_name", "business_impact"]
    },
    "task_structure": {
        "root_task": {
            "task_type": "ecommerce_feature",
            "attributes": {
                "title": "E-commerce Feature: {feature_name}",
                "business_impact": "{business_impact}",
                "target_segment": "{customer_segment}"
            },
            "children": [
                {
                    "task_type": "business_validation",
                    "attributes": {
                        "title": "Business Case Validation",
                        "validation_criteria": [
                            "Market research completed",
                            "ROI projection validated"
                        ]
                    }
                },
                {
                    "task_type": "technical_design",
                    "attributes": {
                        "title": "Technical Design & Architecture"
                    },
                    "dependencies": ["business_validation"]
                },
                {
                    "task_type": "implementation_phase",
                    "attributes": {
                        "title": "Feature Implementation"
                    },
                    "dependencies": ["technical_design"]
                }
            ]
        }
    }
}

# Usage example
{
  "tool": "orchestrator_create_from_template",
  "arguments": {
    "template_id": "ecommerce_feature_v1",
    "parameters": {
      "feature_name": "one_click_checkout",
      "business_impact": "Reduce cart abandonment by 25%",
      "customer_segment": "b2c",
      "revenue_impact": "$2M annual increase"
    }
  }
}
```

## Advanced Query Patterns

### Pattern 8: Performance Analytics and Reporting

```json
// Query overdue tasks for management dashboard
{
  "tool": "orchestrator_query_tasks",
  "arguments": {
    "filters": {
      "status": ["active", "blocked"],
      "lifecycle_stage": ["active", "review"]
    },
    "custom_filter": "created_at < DATE_SUB(NOW(), INTERVAL 2 WEEK)",
    "sort": {
      "field": "created_at",
      "direction": "asc"
    },
    "include_hierarchy": true
  }
}

// Team performance analysis
{
  "tool": "orchestrator_query_tasks",
  "arguments": {
    "filters": {
      "attributes": {
        "assigned_team": "backend_team"
      },
      "status": "completed"
    },
    "date_range": {
      "start": "2025-05-01", 
      "end": "2025-05-31"
    },
    "include_metrics": true
  }
}

// Find tasks blocked by dependencies
{
  "tool": "orchestrator_query_tasks",
  "arguments": {
    "filters": {
      "status": "blocked",
      "has_dependencies": true
    },
    "include_dependency_status": true,
    "sort": {
      "field": "updated_at",
      "direction": "asc"
    }
  }
}
```

## Maintenance and Operations Patterns

### Pattern 9: Scheduled Maintenance Workflow

```json
// Database maintenance with coordination
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "scheduled_maintenance",
    "attributes": {
      "title": "Q2 2025 Database Maintenance",
      "maintenance_window": {
        "start": "2025-06-29T02:00:00Z",
        "end": "2025-06-29T06:00:00Z"
      },
      "business_impact": "minimal - read-only mode",
      "rollback_time_limit": "30_minutes"
    }
  }
}

// Pre-maintenance preparation
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "maintenance_preparation",
    "parent_task_id": "db_maintenance_q2_2025",
    "attributes": {
      "title": "Verify Database Backups",
      "completion_deadline": "24_hours_before_maintenance"
    }
  }
}

// Maintenance execution with dependencies
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "maintenance_execution",
    "parent_task_id": "db_maintenance_q2_2025",
    "attributes": {
      "title": "Execute Database Optimization",
      "estimated_duration": "2_hours"
    }
  }
}

{
  "tool": "orchestrator_manage_dependencies",
  "arguments": {
    "task_id": "execute_db_optimization",
    "dependencies": [
      {
        "dependency_task_id": "verify_db_backups",
        "dependency_type": "completion",
        "description": "Backup verification required before optimization"
      }
    ]
  }
}
```

## Integration Patterns

### Pattern 10: External System Integration

```json
// GitHub integration workflow
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "github_integration",
    "attributes": {
      "title": "Sync with GitHub Repository",
      "repository": "company/main-product",
      "sync_direction": "bidirectional",
      "github_labels": ["orchestrator-managed"],
      "auto_create_issues": true
    }
  }
}

// JIRA integration for enterprise workflows  
{
  "tool": "orchestrator_create_generic_task",
  "arguments": {
    "task_type": "jira_integration",
    "attributes": {
      "title": "Enterprise Project Management Sync",
      "jira_project": "PROJ",
      "field_mappings": {
        "priority": "jira_priority",
        "assigned_team": "jira_component"
      },
      "sync_frequency": "real_time"
    }
  }
}

// Slack notification integration
{
  "tool": "orchestrator_manage_lifecycle",
  "arguments": {
    "task_id": "critical_bug_fix_123",
    "lifecycle_stage": "completed",
    "notes": "Bug fix deployed and verified",
    "notify_channels": ["#dev-team", "#stakeholders"]
  }
}
```

These workflow patterns demonstrate the power and flexibility of the Generic Task Model across various domains and use cases. Each pattern can be customized and extended based on specific organizational needs while maintaining consistency and best practices.