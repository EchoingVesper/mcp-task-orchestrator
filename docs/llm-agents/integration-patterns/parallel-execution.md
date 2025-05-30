# Parallel Execution Pattern

*1700 char limit - Concurrent task coordination with synchronization*

## Pattern Overview
Execute independent subtasks simultaneously while maintaining coordination and synchronization points. Use when subtasks have no dependencies and can run concurrently.

## Implementation Steps

### Phase 1: Dependency Analysis
```
1. orchestrator_plan_task() - Identify independent subtasks
2. Group tasks by dependencies and execution requirements
3. Define synchronization points for convergence
```

### Phase 2: Parallel Launch
```
4. For each independent group:
   - orchestrator_execute_subtask(task_id_A)
   - [Claude Code Operations A] - Concurrent execution
   - orchestrator_execute_subtask(task_id_B) 
   - [Claude Code Operations B] - Concurrent execution
```

### Phase 3: Synchronization and Integration
```
5. orchestrator_complete_subtask() for each parallel task
6. Verify all parallel tasks completed successfully
7. orchestrator_synthesize_results() - Combine outputs
```

## Coordination Benefits
- **Speed**: Reduced total execution time
- **Resource Efficiency**: Better utilization of available tools
- **Scalability**: Handles complex workflows with multiple independent paths
- **Flexibility**: Adapts to varying task complexity

## Best Practices
- Ensure true independence between parallel tasks
- Plan synchronization points for integration
- Handle partial failures gracefully
- Monitor resource usage and conflicts

**Use When**: Independent file operations, parallel analysis, concurrent validations