# Claude Code Integration Patterns

*1500 char limit - Key coordination patterns*

## Integration Architecture
**Task Orchestrator**: Planning, coordination, workflow state
**Claude Code**: File operations, code execution, implementation

## Sequential Pattern (Recommended)
1. `orchestrator_initialize_session()` - Start orchestration
2. `orchestrator_plan_task()` - Create structured subtasks  
3. `orchestrator_execute_subtask(task_id)` - Get specialist context
4. **Use Claude Code tools** - File operations, implementation
5. `orchestrator_complete_subtask()` - Record results
6. **Repeat 3-5** for each subtask
7. `orchestrator_synthesize_results()` - Final output

## Resource Coordination

### File Operations
- **Orchestrator**: Plans which files to work on, manages dependencies
- **Claude Code**: Executes file reading, writing, editing operations

### State Management  
- **Orchestrator**: Task progress, dependencies, workflow state
- **Claude Code**: File system state, execution context

### Error Handling
- **Orchestrator**: Workflow-level recovery, retry coordination
- **Claude Code**: File-level errors, execution failures

## Best Practices
- Always plan with orchestrator before using Claude Code
- Use specific specialist types for focused operations
- Complete subtasks before moving to next operation
- Maintain shared context between both systems

## Common Workflow
```
Plan → Execute → [Claude Code ops] → Complete → Repeat → Synthesize
```