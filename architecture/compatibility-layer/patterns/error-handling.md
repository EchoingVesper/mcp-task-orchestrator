# Error Handling Patterns Architecture

## Overview

This document defines standardized error handling patterns for the compatibility layer, ensuring consistent error processing, recovery strategies, and user-friendly error responses across all use case methods.

## Error Hierarchy

### 1. Domain Errors (Business Logic)

```python
class OrchestrationError(Exception):
    """Base exception for orchestration domain errors."""
    
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_code = error_code or "ORCHESTRATION_ERROR"
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()

class TaskNotFoundError(OrchestrationError):
    """Task does not exist in the system."""
    
    def __init__(self, task_id: str):
        super().__init__(
            message=f"Task {task_id} not found",
            error_code="TASK_NOT_FOUND",
            context={"task_id": task_id}
        )

class TaskStateError(OrchestrationError):
    """Task is in invalid state for requested operation."""
    
    def __init__(self, task_id: str, current_status: str, required_status: str):
        super().__init__(
            message=f"Task {task_id} is {current_status}, but {required_status} is required",
            error_code="INVALID_TASK_STATE",
            context={
                "task_id": task_id,
                "current_status": current_status,
                "required_status": required_status
            }
        )

class DependencyError(OrchestrationError):
    """Task has unresolved dependencies."""
    
    def __init__(self, task_id: str, dependent_tasks: List[str]):
        super().__init__(
            message=f"Task {task_id} has {len(dependent_tasks)} dependent tasks",
            error_code="DEPENDENCY_CONFLICT",
            context={
                "task_id": task_id,
                "dependent_tasks": dependent_tasks
            }
        )
```

### 2. Validation Errors (Input Constraints)

```python
class ValidationError(Exception):
    """Base exception for input validation errors."""
    
    def __init__(self, field: str, value: Any, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        super().__init__(f"Validation failed for {field}: {constraint}")

class RequiredFieldError(ValidationError):
    """Required field is missing or empty."""
    
    def __init__(self, field: str):
        super().__init__(field, None, "field is required")

class InvalidEnumError(ValidationError):
    """Field value is not a valid enum option."""
    
    def __init__(self, field: str, value: Any, valid_options: List[str]):
        super().__init__(
            field, value, 
            f"must be one of {valid_options}, got {value}"
        )
```

### 3. Infrastructure Errors (External Dependencies)

```python
class InfrastructureError(Exception):
    """Base exception for infrastructure failures."""
    
    def __init__(self, service: str, operation: str, cause: Exception = None):
        self.service = service
        self.operation = operation
        self.cause = cause
        super().__init__(f"{service} failed during {operation}: {str(cause) if cause else 'unknown error'}")

class DatabaseError(InfrastructureError):
    """Database operation failed."""
    
    def __init__(self, operation: str, cause: Exception = None):
        super().__init__("database", operation, cause)

class SerializationError(InfrastructureError):
    """JSON serialization failed."""
    
    def __init__(self, data_type: str, cause: Exception = None):
        super().__init__("serializer", f"serialize {data_type}", cause)
```

## Error Handling Strategies

### 1. Use Case Error Handling

```python
class ErrorHandlingMixin:
    """Mixin providing standard error handling for use cases."""
    
    def handle_error(self, error: Exception, operation: str, context: Dict[str, Any] = None) -> None:
        """Standard error handling and logging."""
        
        # Log error with context
        logger.error(
            f"Error in {operation}: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "operation": operation,
                "context": context or {},
                "traceback": traceback.format_exc()
            }
        )
        
        # Re-raise with appropriate error type
        if isinstance(error, (OrchestrationError, ValidationError)):
            # Domain errors pass through unchanged
            raise error
        elif isinstance(error, Exception):
            # Convert infrastructure errors
            raise OrchestrationError(
                f"{operation} failed: {str(error)}",
                error_code="OPERATION_FAILED",
                context=context or {}
            )

    def validate_task_exists(self, task_id: str, task_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate task exists and return validated data."""
        if not task_data:
            raise TaskNotFoundError(task_id)
        return task_data
    
    def validate_task_state(self, task_id: str, current_status: str, required_statuses: List[str]) -> None:
        """Validate task is in required state."""
        if current_status not in required_statuses:
            raise TaskStateError(task_id, current_status, " or ".join(required_statuses))
```

### 2. Response Error Formatting

```python
class ErrorResponseFormatter:
    """Formats error responses consistently across all use cases."""
    
    @staticmethod
    def format_error_response(error: Exception, operation: str) -> Dict[str, Any]:
        """Format any exception into standardized error response."""
        
        if isinstance(error, OrchestrationError):
            return {
                "success": False,
                "error": {
                    "type": "orchestration_error",
                    "code": error.error_code,
                    "message": str(error),
                    "context": error.context,
                    "timestamp": error.timestamp
                },
                "operation": operation
            }
        
        elif isinstance(error, ValidationError):
            return {
                "success": False,
                "error": {
                    "type": "validation_error",
                    "code": "INVALID_INPUT",
                    "message": str(error),
                    "field": error.field,
                    "constraint": error.constraint,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "operation": operation
            }
        
        elif isinstance(error, InfrastructureError):
            return {
                "success": False,
                "error": {
                    "type": "infrastructure_error",
                    "code": "SERVICE_UNAVAILABLE",
                    "message": f"{error.service} service failed",
                    "operation": error.operation,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "operation": operation
            }
        
        else:
            # Unknown error - provide minimal safe details
            return {
                "success": False,
                "error": {
                    "type": "unknown_error",
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "operation": operation
            }
```

## Use Case Implementation Pattern

```python
class CleanArchTaskUseCase(ErrorHandlingMixin):
    """Example implementation with error handling."""
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update task with comprehensive error handling."""
        try:
            # Validate inputs
            if not task_id:
                raise RequiredFieldError("task_id")
            
            if not update_data:
                raise ValidationError("update_data", update_data, "cannot be empty")
            
            # Get existing task
            existing_task = self.task_repository.get_task(task_id)
            self.validate_task_exists(task_id, existing_task)
            
            # Validate state if status change requested
            if "status" in update_data:
                new_status = update_data["status"]
                current_status = existing_task["status"]
                
                # Business rule: can't complete a cancelled task
                if current_status == "cancelled" and new_status == "completed":
                    raise TaskStateError(task_id, current_status, "not cancelled")
            
            # Perform update
            success = self.task_repository.update_task(task_id, update_data)
            if not success:
                raise DatabaseError("update_task")
            
            # Get updated task and format response
            updated_task = self.task_repository.get_task(task_id)
            return self.formatter.format_update_response(updated_task, list(update_data.keys()))
            
        except Exception as e:
            self.handle_error(e, "update_task", {"task_id": task_id, "update_data": update_data})
```

## Error Recovery Strategies

### 1. Graceful Degradation

```python
async def query_tasks_with_fallback(self, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Query tasks with fallback to basic query if advanced filters fail."""
    try:
        return await self.query_tasks_advanced(filters)
    except InfrastructureError:
        logger.warning("Advanced query failed, falling back to basic query")
        return await self.query_tasks_basic(filters)
```

### 2. Retry Logic

```python
async def create_task_with_retry(self, task_data: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
    """Create task with retry logic for transient failures."""
    for attempt in range(max_retries):
        try:
            return await self.create_task(task_data)
        except DatabaseError as e:
            if attempt == max_retries - 1:
                raise e
            logger.warning(f"Create task attempt {attempt + 1} failed, retrying...")
            await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
```

### 3. Partial Success Handling

```python
async def delete_multiple_tasks(self, task_ids: List[str]) -> Dict[str, Any]:
    """Delete multiple tasks with partial success reporting."""
    results = {
        "successful": [],
        "failed": [],
        "warnings": []
    }
    
    for task_id in task_ids:
        try:
            delete_result = await self.delete_task(task_id)
            results["successful"].append({
                "task_id": task_id,
                "action": delete_result["action_taken"]
            })
        except TaskNotFoundError:
            results["warnings"].append(f"Task {task_id} not found")
        except DependencyError as e:
            results["failed"].append({
                "task_id": task_id,
                "error": str(e),
                "dependent_tasks": e.context["dependent_tasks"]
            })
        except Exception as e:
            results["failed"].append({
                "task_id": task_id,
                "error": str(e)
            })
    
    return {
        "total_requested": len(task_ids),
        "successful_count": len(results["successful"]),
        "failed_count": len(results["failed"]),
        "warning_count": len(results["warnings"]),
        "results": results
    }
```

## Handler Integration

```python
async def handle_update_task(args: Dict[str, Any]) -> List[types.TextContent]:
    """MCP handler with integrated error handling."""
    try:
        use_case = await get_clean_task_use_case()
        result = await use_case.update_task(args.get("task_id"), args)
        
        return format_mcp_success_response(
            data=result,
            message=f"Task {args.get('task_id')} updated successfully"
        )
        
    except (OrchestrationError, ValidationError) as e:
        error_response = ErrorResponseFormatter.format_error_response(e, "update_task")
        return [types.TextContent(
            type="text",
            text=json.dumps(error_response, indent=2)
        )]
    
    except Exception as e:
        # Log unexpected errors but don't expose details
        logger.error(f"Unexpected error in handle_update_task: {e}")
        error_response = ErrorResponseFormatter.format_error_response(e, "update_task")
        return [types.TextContent(
            type="text", 
            text=json.dumps(error_response, indent=2)
        )]
```

This error handling architecture provides:
- **Consistent Error Types**: Standardized error hierarchy for all failure modes
- **Graceful Degradation**: Fallback strategies for non-critical failures  
- **Structured Logging**: Comprehensive error context for debugging
- **User-Friendly Messages**: Clear, actionable error messages
- **Recovery Strategies**: Retry logic and partial success handling
- **Security**: Safe error exposure without revealing internal details