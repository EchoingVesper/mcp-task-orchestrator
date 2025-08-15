# Migrate @validator to @field_validator

**Task ID**: `cicd-pydantic-01`  
**Type**: Pattern Migration  
**Local LLM Ready**: ✅ High  
**Estimated Duration**: 45 minutes  
**Priority**: 🟡 Medium

## Objective

Replace all Pydantic V1 `@validator` decorators with V2 `@field_validator` across the codebase.

## Affected Files

- `mcp_task_orchestrator/domain/entities/task.py` (4 validators)
- `mcp_task_orchestrator/domain/entities/task_models.py` (6 validators)

## Migration Pattern

**Old Pattern (V1)**:
```python
from pydantic import validator

@validator('field_name')
def validate_field(cls, v):
    return v
```

**New Pattern (V2)**:
```python
from pydantic import field_validator

@field_validator('field_name')
@classmethod
def validate_field(cls, v):
    return v
```

## Specific Changes Required

### File: `task.py`

**Line 235**: 
```python
# Old
@validator('attribute_value')
def validate_attribute_value(cls, v):

# New  
@field_validator('attribute_value')
@classmethod
def validate_attribute_value(cls, v):
```

**Line 374**:
```python
# Old
@validator('event_data', pre=True)
def validate_event_data(cls, v):

# New
@field_validator('event_data', mode='before')
@classmethod
def validate_event_data(cls, v):
```

**Lines 498, 509**: Similar pattern for other validators

### File: `task_models.py`

Apply same pattern to all 6 `@validator` instances.

## Import Updates

Add to imports in both files:
```python
from pydantic import field_validator  # Add this
# Remove or update: from pydantic import validator
```

## Validation

**Test migration**:
```bash
python -c "from mcp_task_orchestrator.domain.entities.task import Task; print('Task model loads')"
python -c "from mcp_task_orchestrator.domain.entities.task_models import GenericTask; print('GenericTask model loads')"
```

**Check warnings reduction**:
```bash
python -m pytest tests/unit/test_persistence.py -W error::DeprecationWarning
```

## Success Criteria

- [ ] All 10 `@validator` decorators replaced with `@field_validator`
- [ ] All validator functions have `@classmethod` decorator
- [ ] `pre=True` parameters converted to `mode='before'`
- [ ] Import statements updated
- [ ] No Pydantic V1 deprecation warnings for validators
- [ ] Models still load and function correctly

## Local LLM Prompt Template

```
Migrate Pydantic V1 validators to V2 in this Python file:

FILE_CONTENT: {file_content}

Apply these transformations:
1. Replace @validator with @field_validator
2. Add @classmethod decorator to validator methods
3. Convert pre=True to mode='before'
4. Update imports: add field_validator, optionally remove validator
5. Preserve all validation logic unchanged

Return the complete migrated file content.
```

## Agent Instructions

1. Read both affected files
2. Apply migration pattern systematically  
3. Update imports
4. Test model loading
5. Verify warning reduction
6. Commit with descriptive message