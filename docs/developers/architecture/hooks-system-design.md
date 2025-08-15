# Hooks System Design for MCP Task Orchestrator

## Overview

This document outlines the design for a hooks system in the MCP Task Orchestrator that is compatible with Claude Code's hooks format, enabling shared hook configurations and intelligent deduplication.

## Architecture Goals

1. **Format Compatibility**: Use the same JSON structure as Claude Code hooks
2. **Event Parity**: Support similar event types where applicable
3. **Deduplication**: Intelligent detection when running alongside Claude Code
4. **Extensibility**: Support orchestrator-specific events

## Hook Events Mapping

### Direct Equivalents to Claude Code

| Claude Code Event | Task Orchestrator Event | Description |
|------------------|------------------------|-------------|
| SessionStart | OrchestratorInitialize | New orchestration session starts |
| Stop | TaskComplete | Task or subtask completes |
| SubagentStop | SpecialistComplete | Specialist finishes their role |
| PreToolUse | PreTaskExecute | Before executing a subtask |
| PostToolUse | PostTaskExecute | After executing a subtask |
| UserPromptSubmit | TaskPlan | When user submits task for planning |

### Orchestrator-Specific Events

| Event | Trigger | Use Case |
|-------|---------|----------|
| SpecialistAssign | Specialist role assigned | Add role-specific context |
| TaskBreakdown | Task decomposed into subtasks | Validate task structure |
| ArtifactSave | Artifact written to disk | Trigger documentation updates |
| MaintenanceRun | Maintenance coordinator runs | Clean up resources |
| ContextSwitch | Switching between specialists | Save/load context |
| DependencyResolve | Task dependencies calculated | Optimize execution order |

## Configuration Structure

```json
{
  "hooks": {
    "TaskComplete": [
      {
        "matcher": "type:implementation",
        "description": "Auto-format code after implementation tasks",
        "hooks": [
          {
            "type": "command",
            "command": "black $TASK_OUTPUT_DIR && isort $TASK_OUTPUT_DIR"
          }
        ]
      }
    ],
    "SpecialistComplete": [
      {
        "matcher": "role:tester",
        "description": "Run tests after tester specialist completes",
        "hooks": [
          {
            "type": "command",
            "command": "pytest $TASK_WORKSPACE -m unit"
          }
        ]
      }
    ]
  },
  "integration": {
    "claude_code_aware": true,
    "deduplication_strategy": "orchestrator_priority",
    "shared_hooks_path": ".claude/hooks.json"
  }
}
```

## Implementation Plan

### Phase 1: Core Hook System
```python
# mcp_task_orchestrator/infrastructure/hooks/

class HookManager:
    """Manages hook execution for orchestrator events."""
    
    def __init__(self, config_path: Path = None):
        self.config = self._load_config(config_path)
        self.claude_code_detected = self._detect_claude_code()
        
    def trigger(self, event: str, context: Dict[str, Any]):
        """Trigger hooks for an event with deduplication."""
        if self._should_skip_hook(event, context):
            return
            
        for hook in self._get_hooks_for_event(event, context):
            self._execute_hook(hook, context)
    
    def _should_skip_hook(self, event: str, context: Dict[str, Any]) -> bool:
        """Check if hook should be skipped due to Claude Code."""
        if not self.claude_code_detected:
            return False
            
        # Skip if Claude Code is handling this
        if context.get('triggered_by') == 'claude_code':
            return True
            
        # Check deduplication strategy
        strategy = self.config.get('integration', {}).get('deduplication_strategy')
        if strategy == 'claude_code_priority':
            return event in CLAUDE_CODE_HANDLED_EVENTS
        
        return False
```

### Phase 2: Event Integration
```python
# mcp_task_orchestrator/orchestrator/task_lifecycle.py

class TaskLifecycleManager:
    def __init__(self, hook_manager: HookManager):
        self.hook_manager = hook_manager
    
    async def complete_subtask(self, task_id: str, result: str):
        # Existing logic...
        
        # Trigger hook
        self.hook_manager.trigger('TaskComplete', {
            'task_id': task_id,
            'task_type': task.type,
            'specialist': task.specialist,
            'output_dir': task.output_directory,
            'TASK_OUTPUT_DIR': str(task.output_directory),  # Environment variable
            'TASK_WORKSPACE': str(self.workspace_dir)
        })
```

### Phase 3: Deduplication Protocol

```python
# Shared state file: .task_orchestrator/.hooks_state.json
{
  "active_processor": "claude_code|task_orchestrator",
  "last_event": {
    "type": "TaskComplete",
    "timestamp": "2024-01-11T10:30:00Z",
    "processor": "task_orchestrator"
  },
  "shared_hooks": [
    "auto_format_python",
    "validate_markdown"
  ]
}
```

## Integration Strategy

### Detection Methods

1. **Environment Variable**: Check `CLAUDE_CODE_ACTIVE`
2. **Process Detection**: Look for Claude Code process
3. **Shared State File**: Check `.claude/.active` file
4. **MCP Protocol**: Query active MCP servers

### Deduplication Strategies

1. **orchestrator_priority**: Task Orchestrator handles its own events
2. **claude_code_priority**: Claude Code handles when both could
3. **first_wins**: First to acquire lock handles the hook
4. **both**: Both run (for non-interfering hooks)

### Configuration Sharing

```python
class SharedHooksConfig:
    """Load hooks from both Claude Code and Task Orchestrator configs."""
    
    def load_merged_config(self):
        configs = []
        
        # Load Claude Code hooks
        claude_hooks = Path('.claude/hooks.json')
        if claude_hooks.exists():
            configs.append(json.loads(claude_hooks.read_text()))
        
        # Load Task Orchestrator hooks
        orchestrator_hooks = Path('.task_orchestrator/hooks.json')
        if orchestrator_hooks.exists():
            configs.append(json.loads(orchestrator_hooks.read_text()))
        
        return self._merge_configs(configs)
```

## Benefits

1. **Unified Experience**: Same hooks work in both tools
2. **No Duplication**: Intelligent deduplication prevents double processing
3. **Migration Path**: Easy to move hooks between tools
4. **Ecosystem Growth**: Hooks can be shared in the community

## Next Steps

1. Implement core hook manager in Task Orchestrator
2. Add hook triggers to key lifecycle points
3. Create configuration UI/CLI for managing hooks
4. Document hook development for users
5. Build hook marketplace/registry for sharing

## Example Use Cases

### Development Workflow Hook
```json
{
  "hooks": {
    "SpecialistComplete": [
      {
        "matcher": "role:implementer",
        "hooks": [
          {
            "type": "command",
            "command": "black . && isort . && pytest -x"
          }
        ]
      }
    ]
  }
}
```

### Documentation Generation Hook
```json
{
  "hooks": {
    "TaskComplete": [
      {
        "matcher": "type:feature",
        "hooks": [
          {
            "type": "command", 
            "command": "python scripts/generate_docs.py --task-id $TASK_ID"
          }
        ]
      }
    ]
  }
}
```