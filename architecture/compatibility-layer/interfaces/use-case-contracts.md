# Use Case Interface Contracts

## Overview

This document defines the exact interface contracts for all CleanArchTaskUseCase methods to ensure consistent JSON-serializable responses and eliminate the MockTaskResult class.

## Core Design Principle

**ALL USE CASE METHODS MUST RETURN `Dict[str, Any]` STRUCTURES THAT ARE DIRECTLY JSON-SERIALIZABLE**

No wrapper classes, no objects with `.dict()` methods, no custom serialization required.

## Interface Contracts

### CleanArchTaskUseCase.create_task()

```python
async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new task using Clean Architecture.
    
    Args:
        task_data: Task creation parameters
        
    Returns:
        Dict with structure:
        {
            "task_id": str,           # Generated task ID
            "title": str,             # Task title
            "description": str,       # Task description  
            "status": str,            # Task status (always "pending" for new tasks)
            "task_type": str,         # Task type ("standard", "breakdown", etc.)
            "complexity": str,        # Complexity level ("simple", "moderate", "complex")
            "specialist_type": str,   # Specialist assignment ("generic", "coder", etc.)
            "created_at": str,        # ISO format timestamp
            "updated_at": str,        # ISO format timestamp
            "metadata": Dict[str, Any], # Additional context data
            "message": str            # Success message with task ID
        }
        
    Raises:
        OrchestrationError: If task creation fails
    """
```

### CleanArchTaskUseCase.update_task()

```python
async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing task using Clean Architecture.
    
    Args:
        task_id: ID of task to update
        update_data: Fields to update
        
    Returns:
        Dict with structure:
        {
            "task_id": str,           # Task ID that was updated
            "title": str,             # Current task title
            "description": str,       # Current task description
            "status": str,            # Current task status
            "task_type": str,         # Current task type
            "complexity": str,        # Current complexity level
            "specialist_type": str,   # Current specialist assignment
            "created_at": str,        # ISO format timestamp (original)
            "updated_at": str,        # ISO format timestamp (updated)
            "completed_at": str | None, # ISO format timestamp or null
            "metadata": Dict[str, Any], # Current metadata context
            "changes_applied": List[str] # List of fields that were updated
        }
        
    Raises:
        OrchestrationError: If task not found or update fails
    """
```

### CleanArchTaskUseCase.query_tasks()

```python
async def query_tasks(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Query tasks using Clean Architecture with structured response.
    
    Args:
        filters: Query filters and pagination options
        
    Returns:
        Dict with structure:
        {
            "tasks": List[Dict[str, Any]], # List of task dictionaries (formatted per _format_task_response)
            "total_count": int,            # Total number of matching tasks
            "page_count": int,             # Number of pages available
            "current_page": int,           # Current page number (1-based)
            "page_size": int,              # Number of tasks per page
            "has_more": bool,              # Whether more pages exist
            "filters_applied": List[str],  # List of filters that were applied
            "query_metadata": Dict[str, Any] # Additional query context
        }
        
    Raises:
        OrchestrationError: If query execution fails
    """
```

### CleanArchTaskUseCase.delete_task() - NEW METHOD

```python
async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
    """
    Delete or archive a task with dependency checking.
    
    Args:
        task_id: ID of task to delete
        force: Whether to force deletion despite dependencies
        archive_instead: Whether to archive instead of delete
        
    Returns:
        Dict with structure:
        {
            "task_id": str,              # Task ID that was processed
            "action_taken": str,         # "deleted", "archived", or "blocked"
            "dependent_tasks": List[str], # IDs of tasks that depend on this one
            "warnings": List[str],       # Any warnings about the operation
            "metadata": Dict[str, Any],  # Additional operation context
            "message": str               # Human-readable result message
        }
        
    Raises:
        OrchestrationError: If task not found or operation fails
    """
```

### CleanArchTaskUseCase.cancel_task() - NEW METHOD

```python
async def cancel_task(self, task_id: str, reason: str = "", preserve_work: bool = True) -> Dict[str, Any]:
    """
    Cancel an in-progress task with graceful state management.
    
    Args:
        task_id: ID of task to cancel
        reason: Reason for cancellation
        preserve_work: Whether to preserve work artifacts
        
    Returns:
        Dict with structure:
        {
            "task_id": str,              # Task ID that was cancelled
            "previous_status": str,      # Status before cancellation
            "cancelled_at": str,         # ISO format timestamp
            "reason": str,               # Cancellation reason
            "work_preserved": bool,      # Whether artifacts were preserved
            "artifact_count": int,       # Number of artifacts preserved
            "dependent_tasks_updated": List[str], # IDs of dependent tasks updated
            "message": str               # Human-readable result message
        }
        
    Raises:
        OrchestrationError: If task not found, not cancellable, or operation fails
    """
```

## Common Response Format

### Task Dictionary Structure (_format_task_response)

Every task representation in responses MUST follow this structure:

```python
{
    "task_id": str,                    # Unique task identifier
    "title": str,                      # Task title
    "description": str,                # Task description
    "status": str,                     # Current status (string value, not enum)
    "task_type": str,                  # Task type (string value, not enum)
    "complexity": str,                 # Complexity level (string value, not enum)
    "specialist_type": str,            # Specialist assignment (string value, not enum)
    "created_at": str,                 # ISO format timestamp
    "updated_at": str,                 # ISO format timestamp
    "completed_at": str | None,        # ISO format timestamp or null
    "due_date": str | None,            # ISO format timestamp or null
    "estimated_effort": str | None,    # Human-readable effort estimate
    "metadata": Dict[str, Any]         # Additional context (always a dict, never a string)
}
```

## Critical Implementation Requirements

### 1. No MockTaskResult Usage
- NEVER return MockTaskResult instances
- NEVER call `.dict()` methods on responses
- ALL responses must be native Python dictionaries

### 2. JSON Serialization Guarantee
- All values must be JSON-serializable types: str, int, float, bool, list, dict, None
- Convert datetime objects to ISO format strings
- Convert enum objects to their string values
- Ensure nested dictionaries are also JSON-serializable

### 3. Error Handling Consistency
- Always raise `OrchestrationError` for business logic failures
- Include meaningful error messages with context
- Log errors with appropriate detail level

### 4. Timestamp Handling
- ALL timestamps as ISO format strings (not datetime objects)
- Use `datetime.utcnow().isoformat()` for consistency
- Handle None values appropriately in responses

### 5. Metadata Management
- Metadata ALWAYS returned as Dict[str, Any]
- NEVER return metadata as JSON string
- Parse JSON strings to dicts before including in responses

## Validation Rules

1. **Response Structure Validation**: Each method's response MUST match its contract exactly
2. **JSON Serialization Test**: `json.dumps(response)` must succeed without errors
3. **Type Consistency**: All fields must have consistent types across calls
4. **Null Handling**: Optional fields must handle None values gracefully
5. **Error Response Format**: Exceptions must provide structured error information

This interface contract ensures that all use case methods return predictable, JSON-serializable responses that work seamlessly with the MCP handler layer without requiring wrapper classes or custom serialization logic.