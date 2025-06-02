# CRITICAL-01: Context Crash Prevention from Large Artifact Creation

## Priority: 🚨 CRITICAL - IMMEDIATE ACTION REQUIRED

## Issue Summary
Large `orchestrator_complete_subtask` operations are causing Claude Desktop context crashes when artifact creation fails and content falls back to direct context output, overwhelming the context size limit.

## Root Cause Analysis
1. **Artifact path resolution failures** cause artifact creation to fail silently
2. **Large content** (75KB+ observed) gets output directly to context as fallback
3. **No size validation** before attempting artifact creation
4. **Context limit exceeded** crashes Claude Desktop with no recovery

## Evidence
- Task `documenter_9beb13` created 75KB artifact (2120 lines) that likely caused previous crash
- Multiple artifacts have metadata but missing actual files indicating failed creation
- Path resolution points to wrong directories (AppData vs project location)

## Immediate Solutions (Pick One)

### Option A: Emergency Size Limits (Fastest)
```python
# In orchestrator_complete_subtask
MAX_CONTENT_SIZE = 5000  # 5KB limit
if len(detailed_work) > MAX_CONTENT_SIZE:
    raise ValueError(f"Content too large. Split into smaller subtasks.")
```

### Option B: Force Chunking
```python
def chunk_large_content(content, max_chunk_size=4000):
    if len(content) <= max_chunk_size:
        return [content]
    chunks = []
    # Implementation details below...
```
### Option C: Disable Artifacts Temporarily
```python
# Quick patch - disable artifact creation until path issues fixed
def orchestrator_complete_subtask(task_id, summary, detailed_work, next_action):
    # Skip artifact creation, just return summary
    return {"status": "completed", "summary": summary, "artifacts_disabled": True}
```

## Implementation Steps
1. **Choose emergency solution** (A, B, or C)
2. **Test with small content** first
3. **Validate no crashes** with medium content (10-15KB)
4. **Deploy fix** before attempting large documentation tasks

## Testing Protocol
```python
# Test with progressively larger content
test_sizes = [1000, 5000, 10000, 15000, 20000]
for size in test_sizes:
    test_content = "x" * size
    try:
        result = orchestrator_complete_subtask("test", "summary", test_content, "complete")
        print(f"✅ Size {size}: SUCCESS")
    except Exception as e:
        print(f"❌ Size {size}: FAILED - {e}")
        break
```

## Success Criteria
- [ ] No context crashes with content up to 20KB
- [ ] Clear error messages for oversized content
- [ ] Automatic chunking or rejection of large content
- [ ] Safe fallback when artifacts fail

## Estimated Time: 30-60 minutes for emergency fix