# MCP Task Orchestrator - Configuration Examples

## Claude Desktop Configuration

To use the MCP Task Orchestrator with Claude Desktop, add this to your Claude Desktop configuration file:

**Location:** 
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["E:/My Work/Programming/MCP Task Orchestrator/src/main.py"],
      "env": {
        "PYTHONPATH": "E:/My Work/Programming/MCP Task Orchestrator/src"
      }
    }
  }
}
```

## Windsurf Configuration

For Windsurf Cascade, configure in the MCP settings:

```json
{
  "name": "Task Orchestrator",
  "serverType": "local", 
  "command": "python",
  "args": ["E:/My Work/Programming/MCP Task Orchestrator/src/main.py"],
  "workingDirectory": "E:/My Work/Programming/MCP Task Orchestrator"
}
```

## Usage Examples

### 1. Web Scraper Development
```
User: "Build a web scraper for e-commerce product prices with error handling, data export, and monitoring capabilities"

LLM calls: orchestrator_plan_task
Server responds with breakdown:
- Architecture & Design (architect)
- Core Implementation (implementer) 
- Error Handling System (debugger)
- Data Export Module (implementer)
- Monitoring & Logging (implementer)
- Documentation (documenter)

LLM then executes each subtask with specialist context
```

### 2. Code Review and Optimization
```
User: "Review this Python codebase and suggest performance improvements"

LLM calls: orchestrator_plan_task
Server responds with:
- Initial Code Analysis (researcher)
- Quality Review (reviewer)
- Performance Analysis (debugger)
- Optimization Recommendations (implementer)
- Implementation Guide (documenter)
```

## Installation Steps

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your MCP client (Claude Desktop, Windsurf, etc.)

3. Test the connection:
```bash
python src/main.py
```

4. Start using orchestration tools in your LLM conversations!
