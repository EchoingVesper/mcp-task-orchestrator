# Hooks System Patterns for MCP Task Orchestrator

## Core Principles

### 1. Event-Driven Architecture
The MCP Task Orchestrator uses an event-driven architecture with the following components:
- **Event Bus**: Central event distribution system (`infrastructure/auto_append/event_system.py`)
- **Event Listeners**: Abstract listener interface for hook implementations
- **Event Types**: Predefined lifecycle events (task_created, task_completed, etc.)

### 2. Clean Architecture Integration
Hooks must follow Clean Architecture principles:
- **Domain Layer**: Event definitions and hook interfaces
- **Application Layer**: Hook use cases and orchestration
- **Infrastructure Layer**: Hook execution and external command handling
- **Presentation Layer**: Hook configuration and management APIs

## Hook System Architecture Patterns

### 1. Event Listener Pattern
```python
# Base pattern from existing event system
class EventListener(ABC):
    @abstractmethod
    async def handle_event(self, event: TaskEvent) -> None:
        pass
    
    @abstractmethod  
    def get_supported_events(self) -> Set[EventType]:
        pass
```

### 2. Hook Manager Pattern (Recommended Implementation)
```python
class HookManager:
    def __init__(self, config_loader: ConfigLoader, security_validator: SecurityValidator):
        self.config_loader = config_loader
        self.security_validator = security_validator
        self.event_bus = EventBus()
        
    async def register_hooks(self, hooks_config: Dict[str, Any]) -> None:
        """Register hooks with security validation."""
        
    async def trigger_hook(self, event_type: str, context: Dict[str, Any]) -> None:
        """Trigger hooks for an event with deduplication."""
        
    def _should_skip_hook(self, event: str, context: Dict[str, Any]) -> bool:
        """Check Claude Code integration and deduplication."""
```

### 3. Security Validation Pattern
Based on existing security framework:
```python
@mcp_error_handler("hook_execute", require_auth=True)
@require_permission(Permission.EXECUTE_TASK)
@mcp_validation_handler(["hook_name", "command"])
async def execute_hook(args: Dict[str, Any]) -> List[types.TextContent]:
    # Security validation before execution
    validated_config = validate_hook_configuration(args)
    result = await execute_with_limits(validated_config)
    return [types.TextContent(type="text", text=result)]
```

## Error Handling Patterns

### 1. Decorator Pattern Integration
Use existing error handling decorators:
```python
@handle_errors(
    retry_policy=ExponentialBackoff(max_attempts=3),
    recovery_strategy=LogAndContinue()
)
async def execute_hook_safely(hook_config: Dict[str, Any]) -> Any:
    """Execute hook with comprehensive error handling."""
```

### 2. Security Error Sanitization
```python
def sanitize_hook_error(error: Exception) -> str:
    """Sanitize errors to prevent information disclosure."""
    if isinstance(error, SecurityError):
        return "Hook execution blocked due to security policy"
    elif isinstance(error, CommandError):
        return f"Hook execution failed: {sanitize_command_error(error)}"
    else:
        return "Hook execution failed due to unexpected error"
```

## Hook Configuration Patterns

### 1. JSON Schema Validation
```json
{
  "type": "object",
  "properties": {
    "hooks": {
      "type": "object",
      "patternProperties": {
        "^(TaskComplete|TaskCreated|SpecialistAssigned)$": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "matcher": {"type": "string"},
              "description": {"type": "string"},
              "priority": {"type": "integer", "minimum": 1, "maximum": 999},
              "hooks": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "type": {"enum": ["command", "python", "webhook"]},
                    "command": {"type": "string"},
                    "timeout": {"type": "integer", "maximum": 300},
                    "working_directory": {"type": "string"}
                  },
                  "required": ["type"]
                }
              }
            },
            "required": ["hooks"]
          }
        }
      }
    }
  }
}
```

### 2. Configuration Loading Pattern
Based on existing config loader:
```python
class HookConfigLoader:
    def __init__(self):
        self.config_loader = ConfigurationManager()
        self.path_validator = PathValidator()
        
    def load_hook_config(self, config_path: Path) -> Dict[str, Any]:
        """Load and validate hook configuration."""
        config = self.config_loader.load_from_file(config_path)
        return self.validate_hook_config(config)
        
    def validate_hook_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hook configuration against schema."""
```

## Integration Points and Context Data

### 1. Task Lifecycle Integration Points
Based on lifecycle analysis:

#### Task Creation Hook
- **File**: `mcp_task_orchestrator/orchestrator/task_orchestration_service.py`
- **Line**: 160 (after storing in state manager)
- **Context**: `{"main_task": Task, "subtasks_count": int, "complexity_level": str}`

#### Task Completion Hook  
- **File**: `mcp_task_orchestrator/orchestrator/task_orchestration_service.py`
- **Line**: 368 (after core completion logic)
- **Context**: `{"task_id": str, "status": str, "completion_time": datetime}`

#### Specialist Assignment Hook
- **File**: `mcp_task_orchestrator/orchestrator/task_orchestration_service.py`  
- **Line**: 199 (after getting specialist context)
- **Context**: `{"task_id": str, "specialist_type": str, "context_length": int}`

### 2. Environment Variable Context Pattern
```python
def prepare_hook_context(event_type: str, context: Dict[str, Any]) -> Dict[str, str]:
    """Prepare environment variables for hook execution."""
    env_vars = {
        'TASK_ORCHESTRATOR_EVENT': event_type,
        'TASK_ORCHESTRATOR_TIMESTAMP': datetime.utcnow().isoformat(),
        'TASK_ORCHESTRATOR_SESSION_ID': context.get('session_id', ''),
    }
    
    # Event-specific variables
    if 'task_id' in context:
        env_vars['TASK_ORCHESTRATOR_TASK_ID'] = context['task_id']
    if 'specialist_type' in context:
        env_vars['TASK_ORCHESTRATOR_SPECIALIST'] = context['specialist_type']
        
    return env_vars
```

## Security Patterns

### 1. Command Execution Safety
```python
def validate_hook_command(command: str) -> str:
    """Validate hook command for security."""
    # Prevent command injection
    dangerous_patterns = [';', '&&', '||', '|', '`', '$()']
    for pattern in dangerous_patterns:
        if pattern in command:
            raise SecurityError(f"Dangerous command pattern detected: {pattern}")
    
    # Validate against allowlist
    allowed_commands = get_allowed_commands()
    command_parts = shlex.split(command)
    if command_parts[0] not in allowed_commands:
        raise SecurityError(f"Command not in allowlist: {command_parts[0]}")
        
    return command
```

### 2. Resource Limits Pattern
```python
async def execute_with_limits(command: str, working_dir: Path, timeout: int = 30) -> str:
    """Execute command with resource limits."""
    import asyncio
    import resource
    
    # Set resource limits
    def preexec():
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))  # 60 second CPU limit
        resource.setrlimit(resource.RLIMIT_AS, (128*1024*1024, 128*1024*1024))  # 128MB memory limit
    
    # Execute with timeout
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=working_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        preexec_fn=preexec
    )
    
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    return stdout.decode() if stdout else stderr.decode()
```

## Claude Code Integration Patterns

### 1. Deduplication Detection
```python
class ClaudeCodeIntegration:
    def detect_claude_code_active(self) -> bool:
        """Detect if Claude Code is active to prevent hook duplication."""
        # Method 1: Environment variable
        if os.getenv('CLAUDE_CODE_ACTIVE'):
            return True
            
        # Method 2: Shared state file
        claude_state_file = Path('.claude/.active')
        if claude_state_file.exists():
            return True
            
        # Method 3: Process detection
        return self.is_claude_code_process_running()
```

### 2. Shared Hook Configuration
```python
def load_shared_hooks(self) -> Dict[str, Any]:
    """Load hooks from both Claude Code and Task Orchestrator configs."""
    configs = []
    
    # Load Claude Code hooks
    claude_hooks = Path('.claude/hooks.json')
    if claude_hooks.exists():
        configs.append(json.loads(claude_hooks.read_text()))
    
    # Load Task Orchestrator hooks  
    orchestrator_hooks = Path('.task_orchestrator/hooks.json')
    if orchestrator_hooks.exists():
        configs.append(json.loads(orchestrator_hooks.read_text()))
    
    return self.merge_hook_configs(configs)
```

## Performance Optimization Patterns

### 1. Hook Compilation (Webpack Pattern)
```python
class CompiledHookRunner:
    def __init__(self):
        self.compiled_hooks = {}
        
    def compile_hooks(self, hooks_config: Dict[str, Any]) -> None:
        """Pre-compile hooks for optimal execution."""
        for event_type, hooks in hooks_config['hooks'].items():
            compiled_runner = self.compile_hook_runner(event_type, hooks)
            self.compiled_hooks[event_type] = compiled_runner
```

### 2. Lazy Loading Pattern  
```python
class LazyHookLoader:
    def __init__(self):
        self._hooks_cache = {}
        
    def get_hooks_for_event(self, event_type: str) -> List[Hook]:
        """Lazy load hooks only when needed."""
        if event_type not in self._hooks_cache:
            self._hooks_cache[event_type] = self._load_hooks_for_event(event_type)
        return self._hooks_cache[event_type]
```

## Gotchas and Best Practices

### 1. Async Context Management
- Always use async context managers for external resources
- Properly handle asyncio task cancellation
- Use timeout wrappers for all external commands

### 2. Error Isolation
- Hook failures must not interrupt main task flow
- Use circuit breaker pattern for failing hooks
- Comprehensive logging without sensitive data exposure

### 3. Resource Cleanup
- Always clean up temporary files and processes
- Use try/finally blocks for guaranteed cleanup
- Monitor resource usage and enforce limits

### 4. Security First
- Validate all inputs before execution
- Use principle of least privilege
- Audit log all hook executions
- Never expose internal paths or configurations