# Quick Usage Guide

## Getting Started

After installation, restart your MCP clients and look for "task-orchestrator" in the available tools.

## Basic Usage

### Simple Task

```ascii
"Create a Python script to calculate fibonacci numbers"
```

→ Single implementer specialist handles this

### Complex Task  

```ascii
"Build a web scraper for news articles with tests, documentation, and error handling"
```

→ Orchestrator breaks this down:

1. 🏗️ Architect: Plans system design
2. 💻 Implementer: Writes scraper code  
3. 🐛 Debugger: Creates and runs tests
4. 📝 Documenter: Writes documentation

## Available Tools

- `orchestrator_plan_task` - Break down complex tasks
- `orchestrator_execute_subtask` - Work with specialist context
- `orchestrator_complete_subtask` - Mark subtasks complete  
- `orchestrator_synthesize_results` - Combine all results
- `orchestrator_get_status` - Check progress

## Example Workflow

1. **You ask**: "Create a REST API with authentication"
2. **Orchestrator plans**: Breaks into architecture, implementation, testing, docs
3. **Specialists execute**: Each brings focused expertise
4. **Results synthesized**: Combined into final deliverable

## Tips

- **Be specific** about requirements and technologies
- **Ask for explanations** of the orchestration process
- **Use follow-up questions** to refine specialist work
- **Request status updates** for long-running tasks

## Next Steps

- Check `docs/EXAMPLES.md` for detailed examples
- See `CONTRIBUTING.md` to add new specialist types
- Read `docs/DEVELOPER.md` for architecture details

The orchestrator works best with complex, multi-step projects that benefit from specialized expertise!
