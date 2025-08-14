# Pydantic V2 Migration Subtasks

**Purpose**: Migrate from Pydantic V1 to V2 patterns to eliminate warnings  
**Local LLM Ready**: Pattern-based replacements suitable for automation  
**Executive Dysfunction Support**: One pattern per task, clear before/after examples

## Migration Patterns

### Pattern 1: @validator → @field_validator
- **Count**: 54 warnings detected
- **Files**: Domain entities (task.py, task_models.py)
- **Complexity**: Medium (requires parameter changes)

### Pattern 2: Config class → ConfigDict
- **Count**: Multiple warnings
- **Files**: All Pydantic models
- **Complexity**: Low (direct replacement)

### Pattern 3: update_forward_refs → model_rebuild
- **Count**: 2 instances
- **Files**: task.py, task_models.py  
- **Complexity**: Low (method name change)

## Task Structure

Each task handles one pattern across all affected files to maintain consistency.