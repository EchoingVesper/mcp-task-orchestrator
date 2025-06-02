# Multi-Server Coordination Pattern

*1700 char limit - Complex workflows across specialized MCP servers*

## Pattern Overview
Coordinate workflows across multiple specialized MCP servers (orchestrator, claude-code, database, web-fetch, etc.) for complex enterprise scenarios.

## Implementation Steps

### Phase 1: Multi-Server Planning
```
1. orchestrator_plan_task() - Identify required server capabilities
2. Map subtasks to appropriate specialized servers
3. Plan cross-server data flow and dependencies
```

### Phase 2: Coordinated Execution
```
4. orchestrator_execute_subtask() - Establish context
5. [Primary Server Operations] - Core functionality
6. [Secondary Server Operations] - Supporting capabilities
7. Data synchronization and validation between servers
```

### Phase 3: Cross-Server Synthesis
```
8. Aggregate results from multiple server operations
9. orchestrator_synthesize_results() - Unified final output
10. Validate cross-server consistency and completeness
```

## Server Specialization Examples

### Database + File Operations
- **Database Server**: Query data, manage schemas, transactions
- **Claude Code**: File operations, code generation, analysis
- **Orchestrator**: Coordinate data-driven file generation

### Web Research + Documentation
- **Web Fetch**: Research current information, API documentation
- **Claude Code**: File creation, content organization
- **Orchestrator**: Coordinate research-driven documentation

## Best Practices
- Clear server responsibility boundaries
- Explicit data handoff protocols
- Error isolation per server
- Consistent state management

**Use When**: Enterprise workflows, specialized tool requirements, complex integrations