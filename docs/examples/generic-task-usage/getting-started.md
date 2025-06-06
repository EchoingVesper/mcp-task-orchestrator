# Getting Started with Generic Task Model

> **Navigation**: [Docs Home](../../README.md) > [Examples](../README.md) > [Generic Task Usage](README.md) > Getting Started

## Overview

The Generic Task Model (v2.0) provides a unified approach to task management with flexible attributes, hierarchical structure, and rich dependency support. This guide will get you started with the basics.

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

## Key Concepts

### Task Types
- **epic**: Large organizational units containing multiple features
- **feature**: Individual product features or capabilities
- **specialist_task**: Work assigned to specific specialist roles
- **bug_fix**: Bug resolution tasks
- **deployment**: Deployment and release tasks
- **approval_gate**: Approval checkpoints in workflows

### Attributes System
The flexible attributes system allows you to store any task-specific information:

```python
attributes={
    # Standard fields
    "title": "Task title",
    "description": "Detailed description",
    "priority": "high|medium|low",
    
    # Team and assignment
    "assigned_team": "backend",
    "assigned_developer": "john_doe",
    
    # Business context
    "business_value": "Increase conversion by 15%",
    "stakeholders": ["product", "engineering"],
    
    # Technical details
    "estimated_effort": "2 weeks",
    "complexity": "moderate",
    "labels": ["security", "performance"]
}
```

### Task Status
All tasks follow a standard lifecycle:
- **draft**: Initial creation state
- **active**: Currently being worked on
- **blocked**: Waiting for dependencies or approvals
- **completed**: Successfully finished
- **failed**: Failed or cancelled

## Creating Your First Task

### Step 1: Import the Model
```python
from mcp_task_orchestrator.models import GenericTask
```

### Step 2: Define Task Attributes
```python
task_attributes = {
    "title": "My First Task",
    "description": "Learning to use the generic task model",
    "priority": "medium",
    "estimated_effort": "1 day"
}
```

### Step 3: Create the Task
```python
my_task = GenericTask(
    task_id="my_first_task_001",
    task_type="feature",
    attributes=task_attributes
)
```

### Step 4: Save the Task
```python
# Using the orchestrator API
await orchestrator.save_task(my_task)
```

## What's Next?

- **[Basic Operations](basic-operations.md)** - Learn to create, update, and manage tasks
- **[Dependencies](dependencies.md)** - Understand task relationships and dependencies
- **[Task Types](task-types.md)** - Explore different task types and when to use them

---

**Related Documentation**:
- [API Quick Reference](reference/api-reference.md)
- [Migration Guide](migration-guide.md)
- [Troubleshooting](troubleshooting.md)