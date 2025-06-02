# Quick Usage Guide

## Getting Started

After installation, restart your MCP clients and look for "task-orchestrator" in the available tools.

## Basic Usage

### New LLM-Powered Task Orchestration

The MCP Task Orchestrator now leverages the intelligence of the calling LLM to break down tasks, providing a more flexible and powerful orchestration system.

### Initialization

Always begin a task orchestration session by initializing the orchestrator:

```python
response = await call_tool("orchestrator_initialize_session", {})
```

This provides the LLM with context about its role as a Task Orchestrator and guidance on effective task breakdown.

### Task Breakdown

When you receive a complex task, analyze it and create a structured JSON representation of subtasks:

```python
subtasks_json = [
  {
    "title": "System Architecture Design",
    "description": "Design the overall system architecture for the web scraper",
    "specialist_type": "architect",
    "estimated_effort": "30-45 minutes"
  },
  {
    "title": "Core Implementation",
    "description": "Implement the web scraper core functionality",
    "specialist_type": "implementer",
    "dependencies": ["System Architecture Design"],
    "estimated_effort": "1-2 hours"
  },
  {
    "title": "Error Handling",
    "description": "Implement robust error handling and logging",
    "specialist_type": "debugger",
    "dependencies": ["Core Implementation"],
    "estimated_effort": "30-45 minutes"
  },
  {
    "title": "Documentation",
    "description": "Create comprehensive documentation",
    "specialist_type": "documenter",
    "dependencies": ["Error Handling"],
    "estimated_effort": "30-45 minutes"
  }
]

response = await call_tool("orchestrator_plan_task", {
    "description": "Build a web scraper for news articles with tests, documentation, and error handling",
    "subtasks_json": json.dumps(subtasks_json),
    "complexity_level": "moderate"
})
```

## Available Tools

- `orchestrator_initialize_session` - Initialize a new task orchestration session with guidance for effective task breakdown
- `orchestrator_plan_task` - Create a task breakdown from LLM-analyzed subtasks
- `orchestrator_execute_subtask` - Work with specialist context
- `orchestrator_complete_subtask` - Mark subtasks complete  
- `orchestrator_synthesize_results` - Combine all results
- `orchestrator_get_status` - Check progress

## Complete Workflow

1. **Initialize**: Call `orchestrator_initialize_session` to get guidance
2. **Analyze**: Break down the task into structured JSON subtasks
3. **Plan**: Call `orchestrator_plan_task` with your JSON subtasks
4. **Execute**: Work through each subtask with `orchestrator_execute_subtask`
5. **Complete**: Mark subtasks complete with `orchestrator_complete_subtask`
6. **Synthesize**: Combine results with `orchestrator_synthesize_results`

## Tips for Effective Task Breakdown

- **Be comprehensive**: Include all necessary subtasks in your breakdown
- **Assign appropriate specialists**: Match tasks to the right specialist types
- **Create clear dependencies**: Establish logical task ordering
- **Be specific**: Provide detailed task descriptions
- **Estimate effort**: Include realistic time estimates for each subtask

## Specialist Types

- **architect**: System design and architecture planning
- **implementer**: Writing code and implementing features
- **debugger**: Fixing issues and optimizing performance
- **documenter**: Creating documentation and guides
- **reviewer**: Code review and quality assurance
- **tester**: Testing and validation
- **researcher**: Research and information gathering

## JSON Format for Subtasks

Each subtask should include:

```json
{
  "title": "Clear, descriptive title",
  "description": "Detailed task description",
  "specialist_type": "One of the specialist types",
  "dependencies": ["Optional array of dependent task titles"],
  "estimated_effort": "Estimated time required (e.g., '30-45 minutes')"
}
```

## Next Steps

- Check `docs/examples/usage_examples.md` for detailed examples
- See `docs/DEVELOPER.md` for architecture details
- Read `docs/configuration.md` for configuration options

The LLM-powered orchestrator provides more flexible and intelligent task breakdown for complex, multi-step projects!
