# Subtask: Per-File Multi-Agent Task Pattern

**Task ID**: `doc-audit-04`  
**Parent**: Documentation Audit & Remediation  
**Type**: Coordination Pattern  
**Priority**: CRITICAL - Core execution pattern  
**Estimated Duration**: Ongoing (per file)

## Objective

Define and execute the 4-agent pattern for EVERY documentation file discovered in inventory.

## The 4-Agent Pattern

For each file, spawn 4 sequential specialist agents:

### Agent 1: Review Specialist
- **Purpose**: Analyze file purpose and placement
- **Duration**: 5 minutes per file
- **Output**: Purpose analysis, placement recommendation

### Agent 2: Content Review Specialist  
- **Purpose**: Verify code alignment and accuracy
- **Duration**: 10 minutes per file
- **Output**: Accuracy assessment, update requirements

### Agent 3: Markdown Fix Specialist
- **Purpose**: Fix corruption and violations
- **Duration**: 10 minutes per file
- **Output**: Clean, valid markdown file

### Agent 4: Organization Specialist
- **Purpose**: Move to correct location
- **Duration**: 5 minutes per file
- **Output**: Final file placement

## Orchestrator Task Creation

```python
def create_per_file_tasks(file_path):
    """Create 4 orchestrator tasks for a single file"""
    
    tasks = []
    
    # Task 1: Review
    task1 = orchestrator_plan_task(
        title=f"Review Analysis: {file_path}",
        description=f"Examine {file_path} for purpose and placement",
        complexity="simple",
        task_type="review",
        specialist_type="review_specialist",
        context={"file_path": file_path}
    )
    tasks.append(task1)
    
    # Task 2: Content Review (depends on Task 1)
    task2 = orchestrator_plan_task(
        title=f"Content Review: {file_path}",
        description=f"Verify accuracy of {file_path}",
        complexity="moderate",
        task_type="review",
        specialist_type="content_review_specialist",
        dependencies=[task1.id],
        context={"file_path": file_path}
    )
    tasks.append(task2)
    
    # Task 3: Markdown Fix (depends on Task 2)
    task3 = orchestrator_plan_task(
        title=f"Markdown Fix: {file_path}",
        description=f"Fix markdown issues in {file_path}",
        complexity="moderate",
        task_type="implementation",
        specialist_type="markdown_fix_specialist",
        dependencies=[task2.id],
        context={"file_path": file_path}
    )
    tasks.append(task3)
    
    # Task 4: Organization (depends on Task 3)
    task4 = orchestrator_plan_task(
        title=f"Organize: {file_path}",
        description=f"Move {file_path} to correct location",
        complexity="simple",
        task_type="implementation",
        specialist_type="organization_specialist",
        dependencies=[task3.id],
        context={"file_path": file_path}
    )
    tasks.append(task4)
    
    return tasks
```

## Execution Pattern

```yaml
for_each_file_in_inventory:
  step_1:
    agent: review_specialist
    action: orchestrator_execute_task
    store: orchestrator_complete_task with artifacts
    
  step_2:
    prerequisite: step_1 complete
    agent: content_review_specialist
    action: orchestrator_execute_task
    input: step_1 artifacts
    store: orchestrator_complete_task with findings
    
  step_3:
    prerequisite: step_2 complete
    agent: markdown_fix_specialist
    action: orchestrator_execute_task
    input: step_2 findings
    store: orchestrator_complete_task with fixed file
    
  step_4:
    prerequisite: step_3 complete
    agent: organization_specialist
    action: orchestrator_execute_task
    input: all previous artifacts
    store: orchestrator_complete_task with final location
```

## Parallelization Strategy

Process files in batches of 10:
- 10 files × 4 agents = 40 concurrent tasks max
- Prevents orchestrator overload
- Maintains progress visibility

## Success Criteria

- [ ] Task creation automated for all files
- [ ] 4-agent pattern consistent
- [ ] Dependencies properly set
- [ ] Artifacts stored for each step
- [ ] Progress trackable via orchestrator_get_status

## Agent Instructions

```yaml
coordinator: documentation_audit_coordinator
manages: 400+ files × 4 agents = 1600+ tasks
tracking: orchestrator_get_status for progress
batching: 10 files at a time
recovery: Resume from last completed batch
```