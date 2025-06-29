# HIGH-01: Context Limit Detection and Prevention System

## Priority: 🔴 HIGH - PREVENTS FUTURE CRASHES

## Issue Summary
Claude Desktop has no visible context limit indicator, leading to unexpected crashes when limits are exceeded during large operations. Need proactive detection and handover mechanisms.

## Current Problem
- No way to detect approaching context limits
- Large content operations can unexpectedly crash Claude Desktop
- No automatic handover or chunking before limits are reached
- Loss of work when context resets occur

## Proposed Solutions

### Solution A: Content Size Estimation
```python
def estimate_context_usage(content):
    # Rough estimation of context tokens
    # 1 token ≈ 4 characters for English text
    estimated_tokens = len(content) / 4
    return estimated_tokens

def should_trigger_handover(current_context_estimate, new_content):
    CONTEXT_LIMIT = 200000  # Conservative estimate
    HANDOVER_THRESHOLD = 0.8  # Trigger at 80% capacity
    
    total_estimate = current_context_estimate + estimate_context_usage(new_content)
    return total_estimate > (CONTEXT_LIMIT * HANDOVER_THRESHOLD)
```

### Solution B: Proactive Chunking System
```python
def orchestrator_smart_complete_subtask(task_id, summary, detailed_work, next_action):
    if should_trigger_handover(get_current_context_estimate(), detailed_work):
        # Split into multiple smaller completions
        chunks = chunk_large_content(detailed_work, max_size=5000)
        
        for i, chunk in enumerate(chunks):
            chunk_task_id = f"{task_id}_chunk_{i}"
            orchestrator_complete_subtask(chunk_task_id, f"{summary} (Part {i+1})", chunk, next_action)
        
        return {"status": "chunked", "chunks": len(chunks)}
    else:
        return orchestrator_complete_subtask(task_id, summary, detailed_work, next_action)
```
### Solution C: Handover Preparation Tool
```python
def prepare_context_handover():
    """Prepare comprehensive handover information before context limit"""
    return {
        "active_tasks": get_active_tasks(),
        "recent_completions": get_recent_completions(limit=10),
        "pending_work": get_pending_work_summary(),
        "artifacts_created": list_recent_artifacts(),
        "next_steps": generate_continuation_plan(),
        "handover_prompt": generate_handover_prompt()
    }
```

## Implementation Steps
1. **Add context usage tracking** to orchestrator operations
2. **Implement size estimation** for content and responses
3. **Create automatic chunking** for large operations
4. **Add handover preparation** tool to orchestrator
5. **Test with progressively larger** content to find limits

## Integration Points
- Add to `orchestrator_complete_subtask` for automatic chunking
- Add to `orchestrator_plan_task` for upfront size estimation
- Create new tool `orchestrator_prepare_handover` for manual use

## Success Criteria
- [ ] Automatic detection of large content before processing
- [ ] Proactive chunking of oversized operations
- [ ] Clean handover preparation when approaching limits
- [ ] No unexpected context crashes during normal operations

## Estimated Time: 2-3 hours for full implementation