

# LLM Agent Documentation

*Optimized for AI assistants with context limits*

#

# 🎯 Purpose

This documentation tree is specifically designed for LLM agents and AI assistants working with the Task Orchestrator MCP server. Each file is optimized for:

- **Character limits** (1200-2000 chars per file)

- **Quick access** to specific information

- **Context-aware** organization

- **Integration patterns** with other MCP servers

#

# 📁 Directory Structure

#

## Quick Reference (1200-1600 chars)

- `core-commands.md` - All orchestrator tools with signatures

- `integration-cheatsheet.md` - Integration patterns with Claude Code MCP

- `troubleshooting-guide.md` - Common issues and quick solutions

- `specialist-contexts.md` - Available specialist role descriptions

#

## Workflow Contexts (1800-2000 chars)

- `documentation-context.md` - Documentation generation workflows

- `data-processing-context.md` - ETL and analytics workflows  

- `modernization-context.md` - Legacy system migration patterns

- `multi-team-context.md` - Enterprise coordination workflows

#

## Integration Patterns (1600-1800 chars)

- `sequential-coordination.md` - Step-by-step cross-server patterns

- `parallel-execution.md` - Concurrent execution coordination

- `graceful-degradation.md` - Fallback strategies when servers fail

- `multi-server-coordination.md` - Complex multi-server workflows

#

## Troubleshooting (1400-1600 chars)

- `connection-issues.md` - Server connectivity problems

- `permission-problems.md` - File access and security issues

- `workflow-failures.md` - Process recovery strategies

#

# 🔗 Cross-References

**For detailed explanations:** See `/docs/user-guide/`
**For visual aids:** See `/docs/user-guide/visual-guides/`
**For examples:** See `/docs/user-guide/real-world-examples/`

#

# ⚡ Quick Start for LLM Agents

1. **Initialize**: Always start with `orchestrator_initialize_session`

2. **Plan**: Use `orchestrator_plan_task` with JSON subtasks

3. **Execute**: Run subtasks with `orchestrator_execute_subtask`

4. **Coordinate**: Use Claude Code tools for file operations

5. **Complete**: Use `orchestrator_complete_subtask` for each step

---
*Last updated: Documentation restructure - Task Orchestrator v1.4.0*
