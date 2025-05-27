# MCP Task Orchestrator Release Notes

## Version 1.1 (May 27, 2025)

### Major Enhancements

#### LLM-Powered Task Orchestration
- Introduced a new approach that leverages the calling LLM's intelligence for task breakdown
- Added `initialize_session` method to provide guidance to the LLM
- Modified `plan_task` method to accept JSON-formatted subtasks directly from the LLM
- Removed pattern-matching approach in favor of more flexible LLM-driven task analysis

#### Documentation Updates
- Updated README.md to reflect the new LLM-powered approach
- Enhanced usage.md with comprehensive instructions for the new workflow
- Updated DEVELOPER.md with architecture documentation for the new system
- Updated usage_examples.md with examples of the new workflow
- Fixed markdown linting issues across documentation files

### API Changes
- Added new tool: `orchestrator_initialize_session` - Provides context and guidance to the LLM
- Modified `orchestrator_plan_task` tool to accept JSON-formatted subtasks

### Compatibility
- Maintains backward compatibility with existing task orchestration features
- All existing specialist types and state management remain functional

## Version 1.0 (Initial Release)

### Features
- Unified installation system for all supported MCP clients
- Auto-detection of installed clients
- Task decomposition with pattern matching
- Specialist modes (Architect, Implementer, Debugger, Documenter)
- State management for tracking task progress
- Support for Claude Desktop, Cursor IDE, Windsurf, and VS Code with Cline
