

# Basic Operations

> **Navigation**: [Docs Home](../../README.md) > [Examples](../../../../../../README.md) > [Generic Task Usage](../../../../../README.md) > Basic Operations

#

# Task Creation Operations

#

#

# Creating Tasks with the Generic API

#

#

#

# Basic Task Creation

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

```text

#

#

#

# Creating Nested Task Hierarchies

```text
json
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

```text

#

# Query and Retrieval Operations

#

#

# Querying Tasks with Complex Filters

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

```text

#

#

# Getting Task Hierarchies

```text
json
{
  "tool": "orchestrator_get_task_hierarchy",
  "arguments": {
    "root_task_id": "epic_user_system",
    "include_completed": false,
    "max_depth": 3
  }
}

```text

#

# Task Update Operations

#

#

# Updating Task Attributes

```text
json
{
  "tool": "orchestrator_update_task",
  "arguments": {
    "task_id": "feature_auth_123",
    "updates": {
      "attributes": {
        "priority": "critical",
        "assigned_developer": "senior_dev_01",
        "estimated_effort": "4 weeks",
        "status_notes": "Complexity increased due to security requirements"
      }
    }
  }
}

```text

#

#

# Changing Task Status

```text
json
{
  "tool": "orchestrator_update_task_status",
  "arguments": {
    "task_id": "impl_user_auth",
    "new_status": "active",
    "status_reason": "All dependencies completed, starting implementation"
  }
}

```text

#

# Batch Operations

#

#

# Creating Multiple Related Tasks

```text
python
async def create_feature_tasks_batch():
    """Example of creating multiple related tasks efficiently."""
    
    

# Create parent epic

    epic_task = GenericTask(
        task_id="epic_notification_system",
        task_type="epic",
        attributes={
            "title": "Notification System",
            "description": "Complete user notification system",
            "estimated_duration": "6 weeks"
        }
    )
    
    

# Create child features

    features = [
        GenericTask(
            task_id="feature_email_notifications",
            task_type="feature",
            parent_task_id="epic_notification_system",
            attributes={
                "title": "Email Notifications",
                "estimated_effort": "2 weeks"
            }
        ),
        GenericTask(
            task_id="feature_push_notifications",
            task_type="feature",
            parent_task_id="epic_notification_system",
            attributes={
                "title": "Push Notifications",
                "estimated_effort": "3 weeks"
            }
        ),
        GenericTask(
            task_id="feature_sms_notifications",
            task_type="feature",
            parent_task_id="epic_notification_system",
            attributes={
                "title": "SMS Notifications",
                "estimated_effort": "1 week"
            }
        )
    ]
    
    

# Save all tasks

    await orchestrator.save_task(epic_task)
    for feature in features:
        await orchestrator.save_task(feature)
    
    return {"epic": epic_task, "features": features}

```text

#

#

# Bulk Status Updates

```text
json
{
  "tool": "orchestrator_bulk_update",
  "arguments": {
    "task_ids": ["task_001", "task_002", "task_003"],
    "updates": {
      "status": "completed",
      "attributes": {
        "completion_date": "2025-06-15",
        "completed_by": "dev_team_alpha"
      }
    }
  }
}

```text

#

# Common Task Patterns

#

#

# Feature Development Pattern

```text
python
async def create_standard_feature(feature_name: str, complexity: str = "moderate"):
    """Standard pattern for feature development tasks."""
    
    

# Main feature task

    feature_task = GenericTask(
        task_id=f"feature_{feature_name.lower().replace(' ', '_')}",
        task_type="feature",
        attributes={
            "title": f"Feature: {feature_name}",
            "complexity": complexity,
            "estimated_effort": {
                "simple": "1 week",
                "moderate": "2-3 weeks", 
                "complex": "4-6 weeks"
            }[complexity]
        }
    )
    
    

# Standard specialist tasks

    specialist_tasks = [
        GenericTask(
            task_id=f"arch_{feature_name.lower().replace(' ', '_')}",
            task_type="specialist_task",
            parent_task_id=feature_task.task_id,
            attributes={
                "title": f"Design {feature_name} Architecture",
                "specialist_type": "architect",
                "estimated_effort": "2-3 days"
            }
        ),
        GenericTask(
            task_id=f"impl_{feature_name.lower().replace(' ', '_')}",
            task_type="specialist_task",
            parent_task_id=feature_task.task_id,
            attributes={
                "title": f"Implement {feature_name}",
                "specialist_type": "implementer",
                "estimated_effort": "1-2 weeks"
            }
        ),
        GenericTask(
            task_id=f"test_{feature_name.lower().replace(' ', '_')}",
            task_type="specialist_task",
            parent_task_id=feature_task.task_id,
            attributes={
                "title": f"Test {feature_name}",
                "specialist_type": "tester",
                "estimated_effort": "2-3 days"
            }
        )
    ]
    
    return {"feature": feature_task, "specialist_tasks": specialist_tasks}

```text

#

#

# Bug Fix Pattern

```text
python
async def create_bug_fix_workflow(bug_info: dict):
    """Standard pattern for bug fix workflows."""
    
    severity = bug_info.get("severity", "medium")
    
    

# Main bug fix task

    bug_task = GenericTask(
        task_id=f"bug_{bug_info['id']}",
        task_type="bug_fix",
        attributes={
            "title": bug_info["title"],
            "severity": severity,
            "reported_by": bug_info.get("reporter", "unknown"),
            "steps_to_reproduce": bug_info.get("steps", ""),
            "priority": {"critical": "high", "high": "high", "medium": "medium", "low": "low"}[severity]
        }
    )
    
    

# Bug fix workflow tasks

    workflow_tasks = []
    
    

# Investigation always required

    workflow_tasks.append(GenericTask(
        task_id=f"investigate_{bug_info['id']}",
        task_type="specialist_task",
        parent_task_id=bug_task.task_id,
        attributes={
            "title": "Investigate Bug",
            "specialist_type": "debugger",
            "estimated_effort": "2-4 hours"
        }
    ))
    
    

# Fix implementation

    workflow_tasks.append(GenericTask(
        task_id=f"fix_{bug_info['id']}",
        task_type="specialist_task",
        parent_task_id=bug_task.task_id,
        attributes={
            "title": "Implement Fix",
            "specialist_type": "implementer",
            "estimated_effort": "4-8 hours"
        }
    ))
    
    

# Testing based on severity

    if severity in ["critical", "high"]:
        workflow_tasks.append(GenericTask(
            task_id=f"test_fix_{bug_info['id']}",
            task_type="specialist_task",
            parent_task_id=bug_task.task_id,
            attributes={
                "title": "Test Bug Fix",
                "specialist_type": "tester",
                "estimated_effort": "1-2 hours"
            }
        ))
    
    return {"bug_task": bug_task, "workflow_tasks": workflow_tasks}

```text

#

# Error Handling

#

#

# Common Validation Errors

```text
python

# Task ID validation

try:
    task = GenericTask(
        task_id="",  

# Invalid: empty task ID

        task_type="feature"
    )
except ValueError as e:
    print(f"Validation error: {e}")

# Parent task validation

try:
    child_task = GenericTask(
        task_id="child_task",
        task_type="feature",
        parent_task_id="nonexistent_parent"  

# Will fail if parent doesn't exist

    )
    await orchestrator.save_task(child_task)
except ParentTaskNotFoundError as e:
    print(f"Parent task error: {e}")

```text

#

#

# Best Practices for Error Handling

```text
python
async def safe_task_creation(task_data: dict):
    """Example of robust task creation with error handling."""
    
    try:
        

# Validate required fields

        if not task_data.get("task_id"):
            raise ValueError("task_id is required")
        
        if not task_data.get("task_type"):
            raise ValueError("task_type is required")
        
        

# Create task

        task = GenericTask(**task_data)
        
        

# Validate parent exists if specified

        if task.parent_task_id:
            parent = await orchestrator.get_task(task.parent_task_id)
            if not parent:
                raise ValueError(f"Parent task {task.parent_task_id} not found")
        
        

# Save task

        result = await orchestrator.save_task(task)
        return {"status": "success", "task_id": task.task_id}
        
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
```text

---

**Related Documentation**:

- **Previous**: [Getting Started](getting-started.md)

- **Next**: [Dependencies & Relationships](dependencies.md)

- **See also**: [MCP Tools Integration](mcp-tools.md)
