# Response Formatter Architecture

## Overview

The Response Formatter provides a unified, reusable utility for ensuring all use case responses are consistently structured and JSON-serializable. This eliminates the need for wrapper classes like MockTaskResult and provides a single point of truth for response formatting.

## Core Design

### ResponseFormatter Class

```python
class ResponseFormatter:
    """Unified response formatting for all use case methods."""
    
    @staticmethod
    def format_task_dict(task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a single task dictionary to ensure JSON serialization.
        
        Handles:
        - Timestamp conversion to ISO strings
        - Enum conversion to string values  
        - Metadata JSON parsing
        - None value handling
        """
    
    @staticmethod
    def format_create_response(task_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for create_task operations."""
    
    @staticmethod
    def format_update_response(task_dict: Dict[str, Any], changes: List[str]) -> Dict[str, Any]:
        """Format response for update_task operations."""
    
    @staticmethod  
    def format_query_response(tasks: List[Dict[str, Any]], filters: Dict[str, Any], pagination: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for query_tasks operations."""
    
    @staticmethod
    def format_delete_response(task_id: str, action: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for delete_task operations."""
    
    @staticmethod
    def format_cancel_response(task_id: str, cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for cancel_task operations."""
    
    @staticmethod
    def ensure_json_serializable(data: Any) -> Any:
        """Recursively ensure data structure is JSON-serializable."""
```

## Implementation Details

### 1. Timestamp Standardization

```python
def _convert_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all timestamp fields to ISO format strings."""
    timestamp_fields = [
        "created_at", "updated_at", "completed_at", 
        "due_date", "started_at", "deleted_at", "cancelled_at"
    ]
    
    for field in timestamp_fields:
        if field in data and data[field]:
            if isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
            elif isinstance(data[field], str):
                # Validate and normalize existing ISO strings
                try:
                    parsed = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    data[field] = parsed.isoformat()
                except ValueError:
                    # Invalid timestamp, set to None
                    data[field] = None
    
    return data
```

### 2. Enum Value Conversion

```python
def _convert_enums(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert enum objects to their string values."""
    enum_fields = [
        "status", "task_type", "complexity", 
        "specialist_type", "lifecycle_stage"
    ]
    
    for field in enum_fields:
        if field in data and data[field]:
            if hasattr(data[field], 'value'):
                data[field] = data[field].value
            else:
                # Ensure string representation
                data[field] = str(data[field])
    
    return data
```

### 3. Metadata Processing

```python
def _process_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure metadata is always a dict, never a JSON string."""
    if "metadata" in data:
        metadata = data["metadata"]
        if isinstance(metadata, str):
            try:
                data["metadata"] = json.loads(metadata)
            except (json.JSONDecodeError, TypeError):
                data["metadata"] = {}
        elif metadata is None:
            data["metadata"] = {}
        elif not isinstance(metadata, dict):
            data["metadata"] = {}
    else:
        data["metadata"] = {}
    
    return data
```

### 4. JSON Serialization Validation

```python
def _validate_json_serializable(self, data: Any) -> Any:
    """Recursively validate and fix JSON serialization issues."""
    if isinstance(data, dict):
        return {k: self._validate_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [self._validate_json_serializable(item) for item in data]
    elif isinstance(data, (str, int, float, bool, type(None))):
        return data
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, 'value'):  # Enum
        return data.value
    elif hasattr(data, 'dict'):  # Pydantic model
        return self._validate_json_serializable(data.dict())
    else:
        # Convert unsupported types to string
        return str(data)
```

## Specific Response Formatters

### Create Task Response

```python
def format_create_response(self, task_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Format create_task response with consistent structure."""
    formatted_task = self.format_task_dict(task_dict)
    
    return {
        "task_id": formatted_task["task_id"],
        "title": formatted_task["title"],
        "description": formatted_task["description"],
        "status": formatted_task["status"],
        "task_type": formatted_task["task_type"],
        "complexity": formatted_task["complexity"],
        "specialist_type": formatted_task["specialist_type"],
        "created_at": formatted_task["created_at"],
        "updated_at": formatted_task["updated_at"],
        "metadata": formatted_task["metadata"],
        "message": f"Task created successfully with ID: {formatted_task['task_id']}"
    }
```

### Query Tasks Response

```python
def format_query_response(self, tasks: List[Dict[str, Any]], query_context: Dict[str, Any]) -> Dict[str, Any]:
    """Format query_tasks response with pagination and metadata."""
    formatted_tasks = [self.format_task_dict(task) for task in tasks]
    
    return {
        "tasks": formatted_tasks,
        "total_count": len(formatted_tasks),
        "page_count": query_context.get("page_count", 1),
        "current_page": query_context.get("current_page", 1),
        "page_size": query_context.get("page_size", len(formatted_tasks)),
        "has_more": query_context.get("has_more", False),
        "filters_applied": query_context.get("filters_applied", []),
        "query_metadata": query_context.get("metadata", {})
    }
```

## Error Response Formatting

```python
class ErrorResponseFormatter:
    """Standardized error response formatting."""
    
    @staticmethod
    def format_error_response(error: Exception, operation: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format error responses consistently."""
        return {
            "error": True,
            "error_type": type(error).__name__,
            "message": str(error),
            "operation": operation,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }
```

## Usage in Use Cases

```python
class CleanArchTaskUseCase:
    def __init__(self):
        self.formatter = ResponseFormatter()
    
    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # ... business logic ...
        
        # Use formatter for consistent response
        return self.formatter.format_create_response(task_dict)
    
    async def query_tasks(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        # ... business logic ...
        
        # Use formatter for consistent response
        return self.formatter.format_query_response(tasks, query_context)
```

## Benefits

1. **Consistency**: All responses follow the same formatting patterns
2. **Maintainability**: Single point of change for response structure
3. **Reliability**: Guaranteed JSON serialization without errors
4. **Testability**: Easy to test response formatting in isolation
5. **Reusability**: Same formatter used across all use cases

This response formatter architecture eliminates the need for MockTaskResult and ensures all use case methods return consistent, JSON-serializable dictionary structures.