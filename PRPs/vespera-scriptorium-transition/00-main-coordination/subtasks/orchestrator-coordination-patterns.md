# Orchestrator Coordination Patterns - Extracted from V2.0

**Parent**: Main Coordination  
**Source**: v2.0-release-meta-prp/meta-coordination-orchestrator.md  
**Purpose**: Critical orchestrator patterns for multi-agent work

## Session Context Passing

### Infrastructure Components
- `SessionContextManager` for maintaining session state across agents
- Active session tracking in `.task_orchestrator/.active_session`
- Environment variable session passing (`MCP_ORCHESTRATOR_SESSION`)
- Session inheritance for spawned agents via Task tool integration

### Implementation Pattern
```python
# When spawning sub-agent
context = {
    "parent_session": current_session_id,
    "inherited_artifacts": parent_artifacts,
    "shared_context": session_context
}
spawn_agent_with_context(context)
```

## Artifact Management Philosophy

### CRITICAL Principles
1. **Context Preservation**: Detailed work stored in artifacts, NOT in redundant summaries
2. **Cross-Agent Communication**: Agents access artifacts from shared sessions
3. **Historical Record**: Complete implementation details preserved
4. **RAG Integration**: Artifacts feed the vector database for context retrieval

### Anti-Pattern Warning
**DO NOT**: Write additional summaries outside of artifacts. The `summary` field in `complete_task` is for database display only - all detailed work goes in `detailed_work` which becomes the artifact.

## Multi-Agent Workflow Patterns

### Phase Orchestration
```yaml
phase_coordination:
  initialization:
    - orchestrator_initialize_session
    - orchestrator_plan_task (parent task)
    - orchestrator_plan_task (subtasks with dependencies)
    
  execution:
    - Agent 1: orchestrator_execute_task
    - Agent 1: orchestrator_complete_task (with artifacts)
    - Agent 2: orchestrator_execute_task (accesses Agent 1 artifacts)
    - Agent 2: orchestrator_complete_task (with artifacts)
    
  synthesis:
    - Main Agent: orchestrator_synthesize_results
    - Main Agent: orchestrator_complete_task (meta-task)
```

### Git Worktree Coordination
```yaml
worktree_strategy:
  per_agent_isolation:
    - Create worktree for each agent/feature
    - Isolated branch per worktree
    - No merge conflicts during parallel work
    
  implementation:
    agent_1: ../worktrees/feature-a
    agent_2: ../worktrees/feature-b
    agent_3: ../worktrees/feature-c
    
  merge_strategy:
    - Complete work in worktree
    - Merge to integration branch
    - Delete worktree after merge
```

## Automated Document Management

### Project-Type Templates
```yaml
template_document_automation:
  project_types:
    software_development:
      auto_managed_docs:
        - /docs/API_REFERENCE.md
        - /docs/CHANGELOG.md
        - /docs/ARCHITECTURE.md
      
    research_project:
      auto_managed_docs:
        - /docs/LITERATURE_REVIEW.md
        - /docs/METHODOLOGY.md
        - /docs/FINDINGS.md
      
    creative_writing:
      auto_managed_docs:
        - /docs/WORLD_BUILDING.md
        - /docs/CHARACTER_SHEETS.md
        - /docs/PLOT_OUTLINE.md
```

### Update Triggers
1. Task completion triggers doc update
2. Artifact analysis for relevant changes
3. Automatic section updates
4. Cross-reference maintenance
5. Version history tracking

## Task Dependency Management

### Dependency Patterns
```python
# Serial dependency
task_b = orchestrator_plan_task(
    title="Task B",
    dependencies=[task_a.id]
)

# Parallel tasks with convergence
task_d = orchestrator_plan_task(
    title="Task D",
    dependencies=[task_b.id, task_c.id]
)

# Conditional dependency
task_e = orchestrator_plan_task(
    title="Task E",
    dependencies=[task_d.id],
    condition="task_d.success"
)
```

## Progress Monitoring

### Real-Time Status
```python
# Get overall progress
status = orchestrator_get_status(include_completed=True)

# Monitor specific task tree
task_status = orchestrator_query_tasks(
    parent_task_id=meta_task_id,
    include_children=True
)

# Track session progress
session_status = orchestrator_session_status(session_id)
```

## Error Recovery Patterns

### Graceful Degradation
```yaml
error_handling:
  task_failure:
    - Preserve partial progress in artifacts
    - Mark task as blocked, not failed
    - Create recovery task
    - Maintain session continuity
    
  agent_crash:
    - Session state preserved
    - Artifacts intact
    - Resume from last checkpoint
    - No work loss
    
  overwhelm_detection:
    - Automatic task simplification
    - Reduce parallel execution
    - Increase checkpoint frequency
    - Switch to low-energy mode
```

## Executive Dysfunction Optimizations

### Momentum Preservation
- Session state persists across sleep
- Artifacts provide context on resume
- Progress visible in orchestrator_get_status
- No re-explanation needed

### Pressure Delegation
- Heavy tasks assigned to specialist agents
- Main agent coordinates, doesn't execute
- Results synthesized automatically
- Cognitive load distributed

### Damage Prevention
- Automatic WIP commits in worktrees
- Session state saved continuously
- Graceful exits on overwhelm
- Recovery procedures documented

## Implementation Checklist

- [ ] Session context passing configured
- [ ] Artifact-centric workflow adopted
- [ ] Git worktrees for agent isolation
- [ ] Document automation templates created
- [ ] Dependency chains properly structured
- [ ] Progress monitoring active
- [ ] Error recovery patterns implemented
- [ ] ED optimizations verified

## Key Takeaways

1. **Artifacts are primary** - Never duplicate in summaries
2. **Sessions provide continuity** - Maintain across agents
3. **Worktrees prevent conflicts** - Isolate agent work
4. **Automation reduces overhead** - Documents update themselves
5. **Dependencies enable parallelism** - Smart task ordering
6. **Recovery is built-in** - No work loss on failure
7. **ED-first design** - Every pattern reduces cognitive load

These patterns should be applied consistently across all multi-agent workflows in the Vespera Scriptorium transition.