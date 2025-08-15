---
feature_id: "MODE_ROLE_SESSION_INTEGRATION"
version: "2.0.0"
status: "Planned"
priority: "High"
category: "Integration"
dependencies: ["MODE_ROLE_ENHANCEMENT_V2", "ENHANCED_SESSION_MANAGEMENT_V1"]
size_lines: 285
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/2.2-planned/mode-role-system/README.md"
  - "docs/developers/planning/features/2.2-planned/mode-role-system/mcp-tools-specification.md"
module_type: "integration"
modularized_from: "docs/developers/planning/features/2.2-planned/[PLANNED]_mode_role_system_enhancement.md"
---

# Session-Mode Integration System

This document specifies the integration between the enhanced session management system and the mode/role system.

#
# Session-Mode Binding System

```python
class SessionModeBinding:
    def __init__(self, session_manager, mode_manager):
        self.session_manager = session_manager
        self.mode_manager = mode_manager
    
    async def bind_session_to_mode(self, session_id: str, mode_file: str):
        """Bind active session to specific mode configuration."""
        
        
# Validate session is active
        active_session = await self.session_manager.get_active_session()
        if not active_session or active_session.session_id != session_id:
            raise SessionNotActiveError("Session must be active to bind mode")
        
        
# Validate mode file exists and is valid
        validation_result = await self.mode_manager.validate_mode(mode_file)
        if not validation_result.valid:
            raise InvalidModeError(f"Mode validation failed: {validation_result.errors}")
        
        
# Create binding record
        binding = SessionModeBinding(
            session_id=session_id,
            mode_file=mode_file,
            bound_at=datetime.utcnow(),
            validation_result=validation_result
        )
        
        
# Save binding to database
        await self.db.save_session_mode_binding(binding)
        
        
# Update session context with mode information
        await self.update_session_context_with_mode(session_id, mode_file)
        
        
# Cache mode configuration for performance
        await self.cache_mode_configuration(session_id, mode_file)
        
        return binding
    
    async def get_session_mode_context(self, session_id: str) -> ModeContext:
        """Get complete mode context for session."""
        
        binding = await self.db.get_session_mode_binding(session_id)
        if not binding:
            
# Use default mode
            binding = await self.create_default_mode_binding(session_id)
        
        mode_config = await self.load_mode_configuration(binding.mode_file)
        
        return ModeContext(
            session_id=session_id,
            mode_file=binding.mode_file,
            specialist_roles=mode_config.get_specialist_roles(),
            custom_roles=mode_config.get_custom_roles(),
            routing_rules=mode_config.get_routing_rules(),
            configuration=mode_config.get_mode_configuration()
        )

```text

#
# Mode Context for Task Execution

```text
python
async def execute_task_with_mode_context(self, task_id: str, session_id: str):
    """Execute task using session-specific mode context."""
    
    
# Get mode context for session
    mode_context = await self.get_session_mode_context(session_id)
    
    
# Get task details
    task = await self.db.get_task(task_id)
    
    
# Determine specialist using mode-specific routing
    specialist_type = await self.determine_specialist_with_mode(
        task, mode_context.routing_rules
    )
    
    
# Get specialist definition from mode
    specialist_config = mode_context.get_specialist_config(specialist_type)
    
    
# Execute task with mode-specific specialist context
    return await self.execute_task_with_specialist(
        task=task,
        specialist_config=specialist_config,
        mode_context=mode_context
    )

```text

#
## Mode-Aware Task Routing

```text
python
class ModeAwareTaskRouter:
    def __init__(self, mode_manager):
        self.mode_manager = mode_manager
    
    async def determine_specialist_with_mode(self, task, routing_rules):
        """Determine specialist using mode-specific routing rules."""
        
        
# Check for task-specific routing rules
        task_type = self.classify_task_type(task)
        
        if task_type in routing_rules:
            rule = routing_rules[task_type]
            return rule.get('required_specialist', self.get_default_specialist(task))
        
        
# Use default specialist selection logic
        return await self.get_default_specialist(task)
    
    def classify_task_type(self, task) -> str:
        """Classify task to apply appropriate routing rules."""
        
        task_content = task.description.lower()
        
        
# Security-related tasks
        security_keywords = ['security', 'vulnerability', 'audit', 'compliance', 'encryption']
        if any(keyword in task_content for keyword in security_keywords):
            return 'security_tasks'
        
        
# Performance-related tasks
        performance_keywords = ['performance', 'optimization', 'speed', 'bottleneck', 'profiling']
        if any(keyword in task_content for keyword in performance_keywords):
            return 'performance_tasks'
        
        
# Testing-related tasks
        testing_keywords = ['test', 'testing', 'validation', 'verification', 'qa']
        if any(keyword in task_content for keyword in testing_keywords):
            return 'testing_tasks'
        
        
# Documentation tasks
        docs_keywords = ['document', 'documentation', 'guide', 'manual', 'readme']
        if any(keyword in task_content for keyword in docs_keywords):
            return 'documentation_tasks'
        
        return 'general_tasks'

```text

#
# Session Lifecycle Integration

#
## Session Initialization

```text
python
async def initialize_session_with_mode(self, project_root: Path, mode_file: str = None):
    """Initialize new session with mode configuration."""
    
    
# Create new session
    session = await self.session_manager.create_session(project_root)
    
    
# Initialize project role management if needed
    await self.ensure_project_roles_initialized(project_root)
    
    
# Determine mode to use
    if mode_file is None:
        mode_file = await self.determine_default_mode(project_root)
    
    
# Bind session to mode
    await self.bind_session_to_mode(session.session_id, mode_file)
    
    
# Load mode context
    mode_context = await self.get_session_mode_context(session.session_id)
    
    
# Update session with mode information
    session.mode_context = mode_context
    await self.session_manager.update_session(session)
    
    return session

```text

#
## Session Resumption

```text
python
async def resume_session_with_mode(self, session_id: str):
    """Resume existing session with its bound mode."""
    
    
# Resume session
    session = await self.session_manager.resume_session(session_id)
    
    
# Get existing mode binding
    binding = await self.db.get_session_mode_binding(session_id)
    
    if binding:
        
# Validate mode file still exists and is valid
        validation_result = await self.mode_manager.validate_mode(binding.mode_file)
        
        if validation_result.valid:
            
# Load mode context
            mode_context = await self.get_session_mode_context(session_id)
            session.mode_context = mode_context
        else:
            
# Handle invalid mode file
            await self.handle_invalid_mode_on_resume(session_id, binding.mode_file)
    else:
        
# Create default mode binding for legacy session
        await self.create_default_mode_binding(session_id)
        mode_context = await self.get_session_mode_context(session_id)
        session.mode_context = mode_context
    
    return session

```text

#
## Session Termination

```text
python
async def terminate_session_with_mode(self, session_id: str):
    """Terminate session and clean up mode resources."""
    
    
# Create mode backup before termination
    await self.create_session_mode_backup(session_id)
    
    
# Clear mode cache
    await self.clear_mode_cache(session_id)
    
    
# Update mode history
    await self.record_session_termination(session_id)
    
    
# Terminate session
    await self.session_manager.terminate_session(session_id)

```text

#
# Mode Context Management

#
## Context Caching

```text
python
class ModeContextCache:
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_ttl = timedelta(minutes=30)
    
    async def get_cached_context(self, session_id: str) -> ModeContext:
        """Get cached mode context if still valid."""
        
        if session_id not in self.cache:
            return None
        
        timestamp = self.cache_timestamps.get(session_id)
        if timestamp and datetime.utcnow() - timestamp > self.cache_ttl:
            
# Cache expired
            del self.cache[session_id]
            del self.cache_timestamps[session_id]
            return None
        
        return self.cache[session_id]
    
    async def cache_context(self, session_id: str, context: ModeContext):
        """Cache mode context for session."""
        
        self.cache[session_id] = context
        self.cache_timestamps[session_id] = datetime.utcnow()
    
    async def invalidate_cache(self, session_id: str):
        """Invalidate cached context for session."""
        
        if session_id in self.cache:
            del self.cache[session_id]
            del self.cache_timestamps[session_id]

```text

#
## Context Updates

```text
python
async def update_session_context_with_mode(self, session_id: str, mode_file: str):
    """Update session context when mode changes."""
    
    
# Load new mode configuration
    mode_config = await self.load_mode_configuration(mode_file)
    
    
# Create updated context
    updated_context = ModeContext(
        session_id=session_id,
        mode_file=mode_file,
        specialist_roles=mode_config.get_specialist_roles(),
        custom_roles=mode_config.get_custom_roles(),
        routing_rules=mode_config.get_routing_rules(),
        configuration=mode_config.get_mode_configuration()
    )
    
    
# Update cache
    await self.context_cache.cache_context(session_id, updated_context)
    
    
# Notify session manager of context change
    await self.session_manager.notify_context_change(session_id, updated_context)
    
    
# Update any active tasks with new context
    await self.update_active_tasks_context(session_id, updated_context)

```text

#
# Integration Points

#
## Database Schema Integration

```text
sql
-- Session-mode binding table
CREATE TABLE session_mode_bindings (
    session_id TEXT PRIMARY KEY,
    mode_file TEXT NOT NULL,
    bound_at TIMESTAMP NOT NULL,
    validation_status TEXT NOT NULL,
    mode_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- Mode usage history
CREATE TABLE mode_usage_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    mode_file TEXT NOT NULL,
    action_type TEXT NOT NULL, -- 'bind', 'switch', 'validate', 'unbind'
    timestamp TIMESTAMP NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

```text

#
## MCP Tool Integration

Mode management tools integrate seamlessly with session operations:

```text
python

# Enhanced session tools include mode context

async def orchestrator_get_status():
    """Get orchestrator status including mode information."""
    
    status = await base_get_status()
    
    
# Add mode information for active sessions
    for session in status['active_sessions']:
        mode_context = await get_session_mode_context(session['session_id'])
        session['mode_info'] = {
            'mode_file': mode_context.mode_file,
            'specialist_count': len(mode_context.specialist_roles),
            'custom_roles': len(mode_context.custom_roles),
            'routing_rules': len(mode_context.routing_rules)
        }
    
    return status

```text

#
## Error Handling Integration

```text
python
class ModeSessionErrorHandler:
    async def handle_mode_error_during_task_execution(self, session_id: str, error: Exception):
        """Handle mode-related errors during task execution."""
        
        if isinstance(error, InvalidModeError):
            
# Attempt mode recovery
            recovery_success = await self.attempt_mode_recovery(session_id)
            if recovery_success:
                
# Retry task execution with recovered mode
                return await self.retry_task_execution(session_id)
            else:
                
# Fall back to default mode
                await self.fallback_to_default_mode(session_id)
                return await self.retry_task_execution(session_id)
        
        elif isinstance(error, ModeFileNotFoundError):
            
# Handle missing mode file
            await self.handle_missing_mode_file(session_id, error.mode_file)
        
        else:
            
# Standard error handling
            raise error
```text

This session-mode integration provides seamless coordination between session lifecycle and mode management, ensuring that each session operates with appropriate specialist configurations while maintaining reliability and performance.
