

# Quick Usage Guide

#

# Getting Started

After installation, restart your MCP clients and look for "task-orchestrator" in the available tools.

#

# Workspace Paradigm (v1.8.0)

#

#

# Automatic Workspace Detection

The MCP Task Orchestrator v1.8.0 introduces **workspace-aware task management**. Instead of manual session setup, the orchestrator automatically:

- **Detects your project workspace** by finding Git repositories, package.json, pyproject.toml, and other project markers

- **Associates tasks with workspaces** so each project maintains its own task history

- **Saves artifacts in appropriate locations** relative to your project root

#

#

# Initialization (Optional but Recommended)

You can initialize a workspace to get guidance, but it's no longer required:

```python
response = await call_tool("orchestrator_initialize_session", {})

```text

This provides the LLM with context about its role as a Task Orchestrator and confirms the detected workspace.

#

#

#

# Manual Workspace Override

In rare cases where automatic detection fails, you can specify a workspace explicitly:

```text
python
response = await call_tool("orchestrator_initialize_session", {
    "working_directory": "/path/to/your/project"
})

```text

The response will include:

- `working_directory`: The workspace directory being used  

- `orchestrator_path`: Full path to the `.task_orchestrator` folder

- `detection_method`: How the workspace was detected (git_root, project_marker, etc.)

#

#

# Task Breakdown

When you receive a complex task, analyze it and create a structured JSON representation of subtasks:

```text
python
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

```text

#

# Available Tools

- `orchestrator_initialize_session` - Initialize workspace and get guidance for effective task breakdown (optional: specify working_directory)

- `orchestrator_plan_task` - Create a task breakdown from LLM-analyzed subtasks

- `orchestrator_execute_subtask` - Work with specialist context

- `orchestrator_complete_subtask` - Mark subtasks complete  

- `orchestrator_synthesize_results` - Combine all results

- `orchestrator_get_status` - Check progress

#

# Complete Workflow

1. **Workspace Detection**: Orchestrator automatically detects your project workspace

2. **Initialize** (Optional): Call `orchestrator_initialize_session` to confirm workspace and get guidance

3. **Analyze**: Break down the task into structured JSON subtasks

4. **Plan**: Call `orchestrator_plan_task` with your JSON subtasks (automatically uses detected workspace)

5. **Execute**: Work through each subtask with `orchestrator_execute_subtask`

6. **Complete**: Mark subtasks complete with `orchestrator_complete_subtask`

7. **Synthesize**: Combine results with `orchestrator_synthesize_results`

All artifacts will be saved in your detected workspace directory, maintaining project organization.

#

# Tips for Effective Task Breakdown

- **Be comprehensive**: Include all necessary subtasks in your breakdown

- **Assign appropriate specialists**: Match tasks to the right specialist types

- **Create clear dependencies**: Establish logical task ordering

- **Be specific**: Provide detailed task descriptions

- **Estimate effort**: Include realistic time estimates for each subtask

#

# Specialist Types

- **architect**: System design and architecture planning

- **implementer**: Writing code and implementing features

- **debugger**: Fixing issues and optimizing performance

- **documenter**: Creating documentation and guides

- **reviewer**: Code review and quality assurance

- **tester**: Testing and validation

- **researcher**: Research and information gathering

#

# JSON Format for Subtasks

Each subtask should include:

```text
json
{
  "title": "Clear, descriptive title",
  "description": "Detailed task description",
  "specialist_type": "One of the specialist types",
  "dependencies": ["Optional array of dependent task titles"],
  "estimated_effort": "Estimated time required (e.g., '30-45 minutes')"
}
```text

#

# Next Steps

- Check `docs/examples/usage_examples.md` for detailed examples

- See `docs/DEVELOPER.md` for architecture details

- Read `docs/configuration.md` for configuration options

The LLM-powered orchestrator provides more flexible and intelligent task breakdown for complex, multi-step projects!
