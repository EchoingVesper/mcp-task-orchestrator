# Research Synthesis: GitHub Issues #46-50

## Research Completed: 2025-08-15

### Issue #46: MockTask JSON Serialization Error

**Root Cause Identified:**
- `MockTaskResult` class still exists in `db_integration.py` (lines 84-97)
- Used by `create_task` method in `db_integration.py` (lines 161, 164)
- Also referenced in `update_task` return type (line 170)
- The `orchestrator_plan_task` in `tool_router.py` (lines 79-88) correctly returns a dict
- However, other legacy code paths may still try to serialize MockTaskResult objects

**Fix Strategy:**
1. Remove MockTaskResult class entirely from `db_integration.py`
2. Update methods to return dicts directly instead of MockTaskResult wrappers
3. Ensure all serialization paths handle dict responses

**Files to Modify:**
- `mcp_task_orchestrator/infrastructure/mcp/handlers/db_integration.py`

---

### Issue #47: orchestrator_update_task Response Formatting

**Root Cause Identified:**
- The handler in `task_handlers.py` (lines 92-141) expects either dict or object with `.dict()` method
- The `CleanArchTaskUseCase.update_task` (lines 82-124) returns a dict correctly
- However, the error "'str' object is not a mapping" suggests the response isn't being formatted properly
- The handler has compatibility code (lines 110-114) but something in the chain is failing

**Fix Strategy:**
1. Ensure `update_task` in `di_integration.py` always returns a properly formatted dict
2. Add better error handling in the response formatting chain
3. Verify the MCP response adapter handles the dict correctly

**Files to Modify:**
- `mcp_task_orchestrator/infrastructure/mcp/handlers/di_integration.py` (verify return format)
- `mcp_task_orchestrator/infrastructure/mcp/handlers/task_handlers.py` (improve error handling)

---

### Issue #48: Missing delete_task Implementation

**Root Cause Identified:**
- `handle_delete_task` in `task_handlers.py` (lines 143-176) calls `use_case.delete_task()`
- `CleanArchTaskUseCase` in `di_integration.py` has NO `delete_task` method
- Method signature expected: `async def delete_task(self, task_id: str, force: bool = False, archive_instead: bool = True) -> Dict[str, Any]`

**Implementation Requirements:**
1. Check if task exists
2. Check for dependent tasks if not force
3. Either delete or archive based on archive_instead flag
4. Return deletion result dictionary with action_taken field

**Files to Modify:**
- `mcp_task_orchestrator/infrastructure/mcp/handlers/di_integration.py` (add delete_task method)

---

### Issue #49: Missing cancel_task Implementation

**Root Cause Identified:**
- `handle_cancel_task` in `task_handlers.py` (lines 179-242) calls `use_case.cancel_task()`
- `CleanArchTaskUseCase` in `di_integration.py` has NO `cancel_task` method
- Method signature expected: `async def cancel_task(self, task_id: str, reason: str = "", preserve_work: bool = True) -> Dict[str, Any]`

**Implementation Requirements:**
1. Check if task exists and is cancellable (status check)
2. Update task status to 'cancelled'
3. Preserve work artifacts if preserve_work=True
4. Update any dependent tasks
5. Return cancellation result dictionary

**Files to Modify:**
- `mcp_task_orchestrator/infrastructure/mcp/handlers/di_integration.py` (add cancel_task method)

---

### Issue #50: orchestrator_query_tasks Format Mismatch

**Root Cause Identified:**
- `CleanArchTaskUseCase.query_tasks` (lines 126-137) returns a simple list of dicts
- `handle_query_tasks` in `task_handlers.py` (lines 250-324) expects either:
  - A list (handled at line 262-265)
  - A dict with "tasks" key (handled at line 267-269)
- The handler has compatibility code but the error "list indices must be integers or slices, not str" suggests improper access

**Fix Strategy:**
1. Modify `query_tasks` in `di_integration.py` to return structured result:
   ```python
   return {
       "tasks": [self._format_task_response(task) for task in tasks],
       "total_count": len(tasks),
       "filters_applied": [],
       "has_more": False
   }
   ```
2. Or ensure handler properly handles list responses without trying dict access

**Files to Modify:**
- `mcp_task_orchestrator/infrastructure/mcp/handlers/di_integration.py` (modify return format)

---

## Implementation Order Recommendation

Based on dependencies and risk:

1. **Issue #46** - Remove MockTaskResult (low risk, isolated)
2. **Issue #50** - Fix query_tasks format (enables testing other fixes)
3. **Issue #47** - Fix update_task response (builds on query fix)
4. **Issue #48** - Implement delete_task (new functionality)
5. **Issue #49** - Implement cancel_task (new functionality)

## Shared Compatibility Layer Design

All issues point to a need for consistent response formatting between:
- Legacy `db_integration.py` (MockTaskResult objects)
- Clean Architecture `di_integration.py` (dict responses)
- MCP handlers expecting either dicts or objects with `.dict()` method

**Recommendation:** Ensure all use case methods return consistent dict structures that can be directly JSON serialized.

## Risk Assessment

- **Low Risk:** Issue #46 (cosmetic only)
- **Medium Risk:** Issues #47, #50 (functionality works but errors confuse)
- **High Risk:** Issues #48, #49 (core functionality completely broken)

## Testing Requirements

Each fix needs:
1. Unit test for the new/modified method
2. Integration test through MCP handler
3. End-to-end test via orchestrator tools
4. Regression test to ensure no breaks

---

*Research completed by analyzing code paths and error patterns across the Clean Architecture migration.*