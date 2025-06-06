# Getting Started

*Your first successful workflow in 15 minutes + Claude Code integration*

Welcome! Let's get you from zero to orchestrating complex workflows with both Task Orchestrator and Claude Code MCP servers working in perfect harmony. By the end of this guide, you'll have completed your first multi-step project using intelligent task breakdown **and** seamless file operations.

## What You'll Accomplish

In the next 20 minutes, you'll:
- Set up the Task Orchestrator + Claude Code integration ([Visual Setup Flow](./visual-guides/setup-flow.md))
- Run your first coordinated workflow (building a complete web scraper project)
- See how specialist roles work together with file operations ([Architecture Overview](./visual-guides/architecture-overview.md))
- Master the art of letting each tool do what it does best ([Sequential Coordination](./visual-guides/sequential-coordination-flow.md))

**Perfect for:** Developers, technical writers, consultants, anyone who works on complex projects that involve both planning and implementation

**Visual Learner?** Check out our [Visual Guides](./visual-guides/) for diagrams and flowcharts that explain the integration patterns.

## Prerequisites Check

You'll need one of these MCP clients:
- ✅ Claude Desktop 
- ✅ Cursor IDE
- ✅ VS Code with Cline extension
- ✅ Windsurf

*Don't have one yet? Claude Desktop is the quickest to set up - grab it from [claude.ai](https://claude.ai).*

## 🔧 Step 1: Installation (5 minutes)

### Task Orchestrator Setup

#### Option 1: From PyPI (Recommended)
```bash
pip install mcp-task-orchestrator
mcp-task-orchestrator-cli install
```

#### Option 2: From Source
```bash
git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator
python run_installer.py
```

### Claude Code MCP Setup

Add Claude Code to your MCP configuration. In your MCP client config:
```json
{
  "mcpServers": {
    "task-orchestrator": {
      "command": "python",
      "args": ["-m", "mcp_task_orchestrator"],
      "env": {}
    },
    "claude-code": {
      "command": "npx",
      "args": ["@anthropic-ai/claude-code-mcp-server"],
      "env": {}
    }
  }
}
```

**What's happening:** Both servers get configured. You'll see:

```
✅ Detected Claude Desktop
✅ Task Orchestrator configured
✅ Claude Code MCP configured
⚙️  Testing integration...
✅ Integration complete! Restart your MCP clients.
```

**Restart your MCP client** and look for both "task-orchestrator" and "claude-code" tools.

## 🎯 Integration Architecture

Here's how these two powerhouses work together:

```
     Your Request
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│ Task            │◄──►│ Claude Code      │
│ Orchestrator    │    │ MCP Server       │
│                 │    │                  │
│ 🧠 Planning     │    │ ⚡ File Ops      │
│ 📋 Coordination │    │ 🔍 Code Analysis │
│ 📊 Progress     │    │ 🛠️ Execution     │
└─────────────────┘    └──────────────────┘
         │                       │
         └──── Shared Context ────┘
```

**The Secret Sauce:** Task Orchestrator plans the "what" and "when", Claude Code handles the "how" and "where".

## 🚀 Step 2: Your First Integrated Workflow (12 minutes)

Let's build a complete web scraper project that demonstrates both planning and implementation working together.

### 2.1 Initialize the Orchestration

In your MCP client:

```
Initialize a new orchestration session and help me build a complete Python web scraper project for news articles. I want to create actual files, include proper error handling, and have comprehensive documentation.
```

### 2.2 Watch the Magic - Automatic Task Breakdown

The orchestrator creates structured subtasks:

```
Created 6 subtasks:
1. 📐 Project Architecture (architect) - File structure, dependencies, design patterns
2. 🏗️ Core Implementation (implementer) - Main scraper logic with error handling
3. 🧪 Testing Framework (tester) - Unit tests and integration tests
4. 📝 Documentation (documenter) - README, API docs, usage examples
5. 🔧 Configuration Setup (implementer) - Config files, environment setup
6. 🎯 Integration Testing (reviewer) - End-to-end validation
```

### 2.3 Execute With File Operations

Now here's where the magic happens. As you execute each subtask:

```
Execute the project architecture subtask
```

**Task Orchestrator Response:** Provides architectural expertise and planning
**Your Next Action:** Use Claude Code to actually create the project structure:

```
Create the project directory structure and initial files as planned by the architect
```

**Claude Code Response:** Creates actual files, directories, and initial code structure

### 2.4 The Integration Dance 💃

Watch this beautiful coordination:

1. **Orchestrator Plans** → "Create a modular scraper with separate concerns"
2. **Claude Code Implements** → Actually creates the files and writes the code
3. **Orchestrator Coordinates** → "Now add error handling to the scraper module" 
4. **Claude Code Executes** → Edits files, adds robust error handling
5. **Orchestrator Reviews** → "Let's add comprehensive tests for edge cases"
6. **Claude Code Delivers** → Creates test files with thorough coverage

## 🎉 Step 3: See Your Results (3 minutes)

After completing all subtasks:

```
Synthesize the results for this web scraper project
```

**What you get:** A complete project directory with:
- ✅ Professional file structure (`src/`, `tests/`, `docs/`, `config/`)
- ✅ Working Python scraper with robust error handling
- ✅ Comprehensive test suite with high coverage
- ✅ Detailed documentation and usage examples
- ✅ Configuration files and environment setup
- ✅ Integration tests that actually work

**File count:** Typically 12-15 files in a well-organized project structure
**Code quality:** Production-ready with best practices throughout

## 🎭 What Just Happened? The Power of Separation

**Task Orchestrator:** The brilliant project manager who thinks strategically
**Claude Code:** The skilled developer who executes flawlessly  
**You:** The conductor bringing both together for symphony-level results

### Before vs. After Integration

**Single Tool Approach:**
- ❌ Basic planning OR basic implementation
- ❌ Missing components or poor coordination
- ❌ Inconsistent file structure
- ❌ Minimal error handling and testing

**Integrated Approach:**
- ✅ Expert-level planning AND flawless execution
- ✅ All components included and coordinated
- ✅ Professional file organization
- ✅ Comprehensive error handling and testing
- ✅ Production-ready from day one

## 🚀 Next Steps

Ready to level up? Try these progressions:

- **Master the Patterns:** [Integration Patterns Guide](integration-guides/claude-code-mcp.md)
- **Explore Workflows:** [Real-World Examples](real-world-examples/) 
- **Go Deep:** [Advanced Techniques](advanced-techniques/)
- **Visual Learning:** [Architecture Diagrams](visual-guides/)

**Pro Tips for Integration Success:**
1. Always let the orchestrator plan before using Claude Code
2. Use specific specialist types for focused work
3. Complete subtasks fully before moving to the next
4. Let each tool do what it does best - planning vs. execution

---

*Congratulations! You've experienced the future of coordinated development. Two AI systems, one powerful workflow, infinite possibilities.*

## 🔗 Quick References

**For LLM Agents:** See `/docs/llm-agents/quick-reference/` for context-optimized guides
**For Troubleshooting:** Check [Common Issues](troubleshooting/) if anything goes wrong
**For Visual Learners:** Browse [Workflow Diagrams](visual-guides/workflow-flowcharts.md)