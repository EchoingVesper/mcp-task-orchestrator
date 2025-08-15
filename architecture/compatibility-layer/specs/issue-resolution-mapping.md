# Issue Resolution Mapping

## Overview

This document maps each GitHub issue to specific architectural components and implementation requirements in the unified compatibility layer.

## Issue #46: MockTask JSON Serialization Error

### Problem Analysis
- `MockTaskResult` class still exists in `db_integration.py` (lines 84-97)
- Used by `create_task` method in `db_integration.py` (lines 161, 164)
- Also referenced in `update_task` return type (line 170)
- Creates JSON serialization errors when MCP handlers try to process responses

### Architecture Solution
**Component**: Response Formatter + Use Case Interface Contracts

**Implementation Requirements**:
1. **Remove MockTaskResult Class Entirely**
   ```python
   # DELETE: Lines 84-120 in db_integration.py
   class MockTaskResult:  # <-- REMOVE THIS ENTIRE CLASS
   ```

2. **Update create_task Method**
   ```python
   # BEFORE: return MockTaskResult(task)
   # AFTER: return ResponseFormatter.format_create_response(task_dict)
   ```

3. **Update update_task Method**
   ```python
   # BEFORE: return MockTaskResult(updated_task)
   # AFTER: return ResponseFormatter.format_update_response(task_dict, changes)
   ```

**Validation**: 
- No references to MockTaskResult in codebase
- All responses pass `json.dumps()` test
- MCP handlers receive dict responses only

---

## Issue #47: orchestrator_update_task Response Formatting

### Problem Analysis
- Handler expects either dict or object with `.dict()` method
- Error "'str' object is not a mapping" suggests response formatting failure
- Compatibility code exists but something in the chain fails

### Architecture Solution
**Component**: Response Formatter + Error Handling Patterns

**Implementation Requirements**:
1. **Standardize update_task Response**
   ```python
   async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
       # ... business logic ...
       return self.formatter.format_update_response(updated_task, changes_applied)
   ```

2. **Add Response Validation**
   ```python
   def format_update_response(self, task_dict: Dict[str, Any], changes: List[str]) -> Dict[str, Any]:
       validated_response = {
           "task_id": str(task_dict["id"]),
           "title": str(task_dict["title"]),
           # ... all fields as strings/appropriate types
           "changes_applied": changes
       }
       
       # Validate JSON serialization
       try:
           json.dumps(validated_response)
       except (TypeError, ValueError) as e:
           raise SerializationError("update_response", e)
       
       return validated_response
   ```

3. **Improve Handler Error Handling**
   ```python
   # Add type checking in handler
   if not isinstance(updated_task, dict):
       raise OrchestrationError(f"Invalid response type: {type(updated_task)}")
   ```

**Validation**:
- update_task always returns Dict[str, Any]
- No string mapping errors in MCP responses
- Comprehensive error logging for debugging

---

## Issue #48: Missing delete_task Implementation

### Problem Analysis
- `handle_delete_task` calls `use_case.delete_task()`
- `CleanArchTaskUseCase` has NO `delete_task` method
- Expected signature: `async def delete_task(task_id: str, force: bool, archive_instead: bool) -> Dict[str, Any]`

### Architecture Solution
**Component**: Use Case Interface Contracts + Error Handling Patterns

**Implementation Requirements**:
1. **Add delete_task Method Interface**
   ```python
   async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
       """Delete or archive a task with dependency checking."""
   ```

2. **Implement Business Logic**
   ```python
   async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]:
       try:
           # 1. Validate task exists
           task = self.task_repository.get_task(task_id)
           self.validate_task_exists(task_id, task)
           
           # 2. Check dependencies if not force
           if not force:
               dependent_tasks = await self._get_dependent_tasks(task_id)
               if dependent_tasks:
                   raise DependencyError(task_id, dependent_tasks)
           
           # 3. Archive or delete based on flag
           if archive_instead:
               action = await self._archive_task(task_id)
               action_taken = "archived"
           else:
               action = await self._delete_task(task_id)
               action_taken = "deleted"
           
           # 4. Format response
           return self.formatter.format_delete_response(task_id, action_taken, {
               "dependent_tasks": dependent_tasks if not force else [],
               "force_applied": force,
               "archive_mode": archive_instead
           })
           
       except Exception as e:
           self.handle_error(e, "delete_task", {"task_id": task_id})
   ```

3. **Add Helper Methods**
   ```python
   async def _get_dependent_tasks(self, task_id: str) -> List[str]:
       """Get list of tasks that depend on this task."""
   
   async def _archive_task(self, task_id: str) -> Dict[str, Any]:
       """Archive task by setting status to archived."""
   
   async def _delete_task(self, task_id: str) -> Dict[str, Any]:
       """Permanently delete task from repository."""
   ```

**Validation**:
- delete_task method exists and callable
- Returns consistent Dict[str, Any] structure
- Handles dependency conflicts gracefully
- Supports both archive and delete modes

---

## Issue #49: Missing cancel_task Implementation

### Problem Analysis
- `handle_cancel_task` calls `use_case.cancel_task()`
- `CleanArchTaskUseCase` has NO `cancel_task` method
- Expected signature: `async def cancel_task(task_id: str, reason: str, preserve_work: bool) -> Dict[str, Any]`

### Architecture Solution
**Component**: Use Case Interface Contracts + Error Handling Patterns

**Implementation Requirements**:
1. **Add cancel_task Method Interface**
   ```python
   async def cancel_task(self, task_id: str, reason: str = "", preserve_work: bool = True) -> Dict[str, Any]:
       """Cancel an in-progress task with graceful state management."""
   ```

2. **Implement Business Logic**
   ```python
   async def cancel_task(self, task_id: str, reason: str = "", preserve_work: bool = True) -> Dict[str, Any]:
       try:
           # 1. Validate task exists
           task = self.task_repository.get_task(task_id)
           self.validate_task_exists(task_id, task)
           
           # 2. Check if task is cancellable
           current_status = task["status"]
           cancellable_statuses = ["pending", "in_progress", "active"]
           self.validate_task_state(task_id, current_status, cancellable_statuses)
           
           # 3. Preserve work artifacts if requested
           artifact_count = 0
           if preserve_work and current_status == "in_progress":
               artifact_count = await self._preserve_work_artifacts(task_id)
           
           # 4. Update task status to cancelled
           updates = {
               "status": "cancelled",
               "cancelled_at": datetime.utcnow().isoformat(),
               "updated_at": datetime.utcnow().isoformat()
           }
           
           success = self.task_repository.update_task(task_id, updates)
           if not success:
               raise DatabaseError("cancel_task")
           
           # 5. Update dependent tasks
           dependent_tasks = await self._update_dependent_tasks_for_cancellation(task_id)
           
           # 6. Format response
           return self.formatter.format_cancel_response(task_id, {
               "previous_status": current_status,
               "reason": reason,
               "work_preserved": preserve_work,
               "artifact_count": artifact_count,
               "dependent_tasks_updated": dependent_tasks,
               "cancelled_at": updates["cancelled_at"]
           })
           
       except Exception as e:
           self.handle_error(e, "cancel_task", {"task_id": task_id, "reason": reason})
   ```

3. **Add Helper Methods**
   ```python
   async def _preserve_work_artifacts(self, task_id: str) -> int:
       """Preserve work artifacts for cancelled task."""
   
   async def _update_dependent_tasks_for_cancellation(self, task_id: str) -> List[str]:
       """Update tasks that depend on the cancelled task."""
   ```

**Validation**:
- cancel_task method exists and callable
- Returns consistent Dict[str, Any] structure
- Validates task state before cancellation
- Handles work preservation appropriately
- Updates dependent tasks correctly

---

## Issue #50: orchestrator_query_tasks Format Mismatch

### Problem Analysis
- `CleanArchTaskUseCase.query_tasks` returns simple list of dicts
- Handler expects either list or dict with "tasks" key
- Error "list indices must be integers or slices, not str" suggests improper access

### Architecture Solution
**Component**: Response Formatter + Use Case Interface Contracts

**Implementation Requirements**:
1. **Standardize query_tasks Response**
   ```python
   async def query_tasks(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
       """Query tasks with structured response format."""
       try:
           # ... business logic to get tasks ...
           
           return self.formatter.format_query_response(tasks, {
               "filters_applied": applied_filters,
               "page_count": page_count,
               "current_page": current_page,
               "page_size": page_size,
               "has_more": has_more,
               "metadata": query_metadata
           })
           
       except Exception as e:
           self.handle_error(e, "query_tasks", {"filters": filters})
   ```

2. **Update Response Formatter**
   ```python
   def format_query_response(self, tasks: List[Dict[str, Any]], query_context: Dict[str, Any]) -> Dict[str, Any]:
       """Format query response with consistent structure."""
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

3. **Update Handler Logic**
   ```python
   # Handler should always expect dict response now
   query_result = await use_case.query_tasks(args)
   
   # No need for list/dict checking - always dict now
   response_data = {
       "status": "success",
       "message": f"Found {query_result['total_count']} tasks",
       "query_summary": {
           "filters_applied": query_result["filters_applied"],
           "pagination": {
               "total_count": query_result["total_count"],
               "page_count": query_result["page_count"],
               "has_more": query_result["has_more"]
           }
       },
       "tasks": query_result["tasks"]
   }
   ```

**Validation**:
- query_tasks always returns Dict[str, Any] with "tasks" key
- No list index errors in handlers
- Consistent pagination metadata
- All task dictionaries properly formatted

---

## Implementation Priority Order

Based on dependencies and risk assessment:

### Phase 1: Foundation (Low Risk)
1. **Issue #46** - Remove MockTaskResult class
   - Update db_integration.py methods
   - Test JSON serialization

### Phase 2: Core Functionality (Medium Risk)  
2. **Issue #50** - Fix query_tasks format
   - Implement ResponseFormatter.format_query_response
   - Update CleanArchTaskUseCase.query_tasks
   - Test handler integration

3. **Issue #47** - Fix update_task response
   - Implement ResponseFormatter.format_update_response
   - Add response validation
   - Test error handling

### Phase 3: New Features (High Risk)
4. **Issue #48** - Implement delete_task
   - Add method to CleanArchTaskUseCase
   - Implement dependency checking
   - Add archive/delete logic

5. **Issue #49** - Implement cancel_task
   - Add method to CleanArchTaskUseCase
   - Implement state validation
   - Add work preservation logic

## Cross-Issue Dependencies

- **Response Formatter**: Required for issues #46, #47, #50
- **Error Handling Patterns**: Required for issues #47, #48, #49
- **Interface Contracts**: Foundation for all issues
- **JSON Serialization Validation**: Critical for issues #46, #47, #50

This mapping ensures systematic resolution of all issues while building a robust, maintainable compatibility layer architecture.