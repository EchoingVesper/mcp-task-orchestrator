# Claude Code Isolation Orchestrator

**PRP ID**: `CLAUDE_CODE_ISOLATION_ORCHESTRATOR`
**Parent**: V2_0_ORCHESTRATOR_RELEASE_COORDINATOR
**Phase**: 5 - Async Agent Architecture Foundation
**Priority**: Critical
**Category**: Agent Infrastructure
**Estimated Effort**: 1 week

## Goal

Implement Claude Code subtask isolation to spawn dedicated agent instances with ~100k token contexts,
preventing context pollution and enabling parallel agent execution.

## Why

- Leverage Claude Code's native subtask isolation capabilities
- Prevent context pollution between agent tasks
- Enable true parallel execution with isolated contexts
- Maximize available context window per agent

## What

### Claude Code Agent Spawning

```python
# Claude Code subtask isolation implementation
class ClaudeCodeAgentSpawner:
    """Spawns isolated Claude Code instances for agent tasks"""
    
    async def spawn_isolated_agent(self,
                                  task: AgentTask,
                                  context: Dict[str, Any]) -> AgentInstance:
        """Spawn isolated Claude Code instance with dedicated context"""
        
        # Prepare isolated context (up to 100k tokens)
        isolated_context = self._prepare_isolated_context(task, context)
        
        # Create subtask command for Claude Code
        subtask_command = {
            "tool": "Task",
            "parameters": {
                "description": f"Agent: {task.agent_role}",
                "prompt": self._build_agent_prompt(task, isolated_context),
                "subagent_type": "general-purpose"
            }
        }
        
        # Spawn isolated instance
        agent_instance = await self._execute_subtask(subtask_command)
        
        # Track agent lifecycle
        self.active_agents[agent_instance.id] = agent_instance
        
        return agent_instance
    
    def _prepare_isolated_context(self, 
                                 task: AgentTask,
                                 shared_context: Dict) -> str:
        """Prepare context for isolated agent (max 100k tokens)"""
        context_parts = [
            f"# Agent Role: {task.agent_role}",
            f"# Coordination ID: {task.coordination_id}",
            "",
            "# Task Description",
            task.description,
            "",
            "# Shared Context",
            json.dumps(shared_context, indent=2),
            "",
            "# Required Capabilities",
            self._format_capabilities(task.capabilities_required)
        ]
        
        return "\n".join(context_parts)

```

### Agent Instance Management

```python
# Manage isolated agent instances
class AgentInstanceManager:
    """Manages lifecycle of isolated agent instances"""
    
    def __init__(self):
        self.instances: Dict[str, AgentInstance] = {}
        self.context_usage: Dict[str, int] = {}
    
    async def create_instance(self,
                             task: AgentTask) -> AgentInstance:
        """Create new isolated agent instance"""
        instance = AgentInstance(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_role=task.agent_role,
            context_limit=100000,  # ~100k tokens
            created_at=datetime.now()
        )
        
        # Initialize with clean context
        instance.context = await self._initialize_context(task)
        
        self.instances[instance.id] = instance
        self.context_usage[instance.id] = 0
        
        return instance
    
    async def execute_with_isolation(self,
                                    instance: AgentInstance,
                                    command: str) -> Any:
        """Execute command in isolated context"""
        # Ensure context isolation
        if self.context_usage[instance.id] > 90000:
            # Near context limit, spawn new instance
            instance = await self._respawn_instance(instance)
        
        result = await instance.execute(command)
        
        # Track context usage
        self.context_usage[instance.id] += self._estimate_tokens(command, result)
        
        return result

```

## Integration Points

- Claude Code's native Task tool for subtask spawning
- `mcp_task_orchestrator/infrastructure/agents/claude_code/` - Claude Code provider
- `mcp_task_orchestrator/application/usecases/agent_coordination/` - Coordination layer

## Task List

1. **Implement Agent Spawner** (2 days)
   - Create ClaudeCodeAgentSpawner class
   - Implement context isolation logic
   - Add subtask command generation

2. **Build Instance Manager** (2 days)
   - Implement lifecycle management
   - Add context usage tracking
   - Create respawning logic

3. **Integration & Testing** (2 days)
   - Integrate with coordination workflow
   - Test parallel agent execution
   - Validate context isolation

4. **Documentation** (1 day)
   - Document isolation patterns
   - Create usage examples
   - Update agent architecture docs

## Validation Loop

```bash
# Test agent spawning
pytest tests/agents/test_claude_code_spawner.py -v

# Validate context isolation
python tests/integration/test_context_isolation.py

# Test parallel execution
python tests/performance/test_parallel_agents.py --agents 5

```

## Success Criteria

- [ ] Spawn isolated Claude Code instances
- [ ] Maintain ~100k token contexts
- [ ] Zero context pollution between agents
- [ ] Support 5+ parallel agents
- [ ] Automatic respawning near context limits
- [ ] Complete integration with orchestrator

## Progress Tracking

**Status**: [PENDING]
**Last Updated**: 2025-08-12
**Agent ID**: [Will be assigned by orchestrator]

### Completion Checklist

- [ ] Task planned via orchestrator_plan_task
- [ ] Specialist context created via orchestrator_execute_task  
- [ ] Implementation started
- [ ] Core functionality complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Integration verified
- [ ] Task completed via orchestrator_complete_task
- [ ] Results synthesized

### Implementation Progress

| Component | Status | Notes |
|-----------|--------|-------|
| Core Implementation | ⏳ Pending | |
| Unit Tests | ⏳ Pending | |
| Integration Tests | ⏳ Pending | |
| Documentation | ⏳ Pending | |
| Code Review | ⏳ Pending | |

### Agent Activity Log

```yaml
# Auto-updated by orchestrator agents
agent_activities:
  - timestamp: 
    agent_id: 
    action: "initialized"
    details: "PRP ready for orchestrator assignment"

```

### Blockers & Issues

- None currently identified

### Next Steps

1. Awaiting orchestrator assignment
2. Pending specialist context creation
