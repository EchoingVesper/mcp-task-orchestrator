# CRITICAL-02: Artifact System Path Resolution Failure

## Priority: 🚨 CRITICAL - BLOCKS ARTIFACT SYSTEM

## Issue Summary
The artifact creation system is failing to resolve correct file paths, causing artifacts to be created in wrong locations or not at all, leading to silent failures and potential context crashes.

## Root Cause Analysis
1. **Base path detection failure** - System points to AppData instead of project directory
2. **Silent failure mode** - Failed artifact creation doesn't throw errors
3. **Metadata/file mismatch** - Metadata created but actual artifact files missing
4. **Cross-platform path issues** - Windows path handling inconsistencies

## Evidence from Investigation
```
Expected: E:\My Work\Programming\MCP Servers\mcp-task-orchestrator\.task_orchestrator\artifacts\
Actual:   C:\Users\Fiona\AppData\Local\AnthropicClaude\app-0.9.3\.task_orchestrator\artifacts\

Metadata paths point to:
"C:\\Users\\Fiona\\AppData\\Local\\AnthropicClaude\\app-0.9.3\\.task_orchestrator\\artifacts\\..."

But artifacts should be in project directory:
"E:\\My Work\\Programming\\MCP Servers\\mcp-task-orchestrator\\.task_orchestrator\\artifacts\\..."
```

## Failed Tasks Evidence
- `documenter_3c9aec`: Has metadata but missing primary artifact file
- `documenter_d9c968`: Has metadata but only mirrored structure, no primary file
- Multiple other tasks with similar pattern

## Solutions (In Order of Preference)

### Solution A: Fix Base Path Detection
```python
def get_correct_base_path():
    # Get the actual project directory, not AppData
    import os
    current_file = os.path.abspath(__file__)
    # Navigate up to project root
    project_root = os.path.dirname(os.path.dirname(current_file))
    return os.path.join(project_root, '.task_orchestrator', 'artifacts')
```
### Solution B: Add Validation and Error Handling
```python
def create_artifact_with_validation(task_id, content, metadata):
    artifact_path = get_artifact_path(task_id)
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        
        # Write artifact
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Validate creation
        if not os.path.exists(artifact_path):
            raise FileNotFoundError(f"Artifact creation failed: {artifact_path}")
            
        # Write metadata only after successful artifact creation
        write_metadata(metadata)
        
        return {"success": True, "path": artifact_path}
        
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Solution C: Emergency Fallback Mode
```python
# If path resolution fails, use project-relative paths
def get_safe_artifact_path(task_id):
    try:
        return get_correct_base_path()
    except:
        # Fallback to project directory + artifacts
        return "./task_orchestrator/artifacts"
```

## Implementation Steps
1. **Identify current path detection logic** in artifact creation
2. **Fix base path resolution** to use project directory
3. **Add validation** that artifacts are actually created
4. **Add error handling** for failed artifact creation
5. **Test with existing task IDs** to verify fix

## Files to Investigate
- `mcp_task_orchestrator/orchestrator/enhanced_handlers.py` (likely location)
- Any artifact creation logic in `orchestrator/` directory
- Configuration files that set base paths

## Success Criteria
- [ ] Artifacts created in correct project directory
- [ ] Metadata paths match actual artifact locations  
- [ ] Failed artifact creation throws clear errors
- [ ] Existing tasks can create artifacts successfully

## Estimated Time: 1-2 hours for complete fix