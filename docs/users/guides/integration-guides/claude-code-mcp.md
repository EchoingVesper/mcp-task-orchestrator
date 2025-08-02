

# Claude Code MCP Integration Guide

*Master the art of coordinated development workflows*

#

# Overview

The Task Orchestrator + Claude Code MCP integration creates a powerful development partnership where strategic planning meets flawless execution. This guide demonstrates proven coordination patterns, real tool call sequences, and advanced workflows that showcase both systems working in perfect harmony.

**Integration Philosophy:** Task Orchestrator provides the strategic intelligence and workflow coordination, while Claude Code handles the file operations, code analysis, and implementation details.

#

# 🏗️ Core Integration Architecture

#

#

# Separation of Concerns

```text
┌─────────────────────────────┐    ┌─────────────────────────────┐
│     Task Orchestrator       │    │       Claude Code MCP       │
│                             │    │                             │
│ ✅ Strategic Planning        │    │ ✅ File Operations          │
│ ✅ Specialist Coordination   │    │ ✅ Code Analysis            │
│ ✅ Workflow State Management │    │ ✅ Implementation           │
│ ✅ Progress Tracking         │    │ ✅ Testing & Validation     │
│ ✅ Context Synthesis         │    │ ✅ Directory Operations     │
│                             │    │                             │
│ ❌ Direct File Writing       │    │ ❌ High-level Planning      │
│ ❌ Code Implementation       │    │ ❌ Workflow Coordination    │
└─────────────────────────────┘    └─────────────────────────────┘
                 │                                    │
                 └──────── Shared Context ────────────┘

```text

#

#

# Resource Coordination Principles

1. **File Operation Ownership:** Claude Code exclusively handles all file read/write operations

2. **Context Sharing:** Both tools maintain shared understanding of project goals and progress

3. **Sequential Coordination:** Orchestrator plans → Claude Code executes → Orchestrator coordinates next steps

4. **Error Handling:** Workflow-level recovery (orchestrator) + execution-level recovery (claude-code)

#

# 🎯 The Sequential Coordination Pattern (CORE)

This is the foundational pattern that drives all successful integrations:

#

#

# Step 1: Initialize Session & Context

```text

orchestrator_initialize_session()

```text
**Purpose:** Establish shared context and workflow state

#

#

# Step 2: Strategic Task Breakdown

```text

orchestrator_plan_task(
    description="Build a complete REST API with authentication",
    subtasks_json='[
        {"title": "API Architecture Design", "specialist_type": "architect"},
        {"title": "Core Endpoint Implementation", "specialist_type": "implementer"},
        {"title": "Authentication System", "specialist_type": "security_specialist"},
        {"title": "Testing Suite Creation", "specialist_type": "tester"},
        {"title": "Documentation & Examples", "specialist_type": "documenter"}
    ]'
)

```text
**Output:** Structured task breakdown with specialist assignments

#

#

# Step 3: Execute-Coordinate Loop

For each subtask:

#

#

#

# 3a. Get Specialist Context

```text

orchestrator_execute_subtask(task_id="architect_abc123")

```text
**Response:** Detailed specialist guidance and architectural decisions

#

#

#

# 3b. Implement with Claude Code

```text

# Claude Code operations (these happen in sequence):

create_directory("/project/src/api")
create_file("/project/src/api/main.py", content="...")
create_file("/project/src/api/auth.py", content="...")
create_file("/project/tests/test_api.py", content="...")

```text

**Purpose:** Transform specialist guidance into actual implementation

#

#

#

# 3c. Record Progress

```text
text
orchestrator_complete_subtask(
    task_id="architect_abc123",
    results="Created complete API architecture with auth system",
    artifacts=["main.py", "auth.py", "models.py", "test_api.py"],
    next_action="continue"
)

```text

#

#

# Step 4: Final Synthesis

```text

orchestrator_synthesize_results(parent_task_id="main_task")

```text
**Output:** Comprehensive project summary and next steps

#

# 🔄 Real Coordination Examples

#

#

# Example 1: Full-Stack Web Application

**User Request:** "Build a complete task management web app with React frontend and Node.js backend"

**Integration Sequence:**

```text

1. orchestrator_initialize_session()
   → Establishes context for full-stack development

2. orchestrator_plan_task(
     description="Complete task management web application",
     subtasks=[
       {title: "Project Architecture", specialist: "architect"},
       {title: "Backend API Development", specialist: "backend_dev"},
       {title: "Database Schema & Models", specialist: "database_specialist"},
       {title: "Frontend React Components", specialist: "frontend_dev"},
       {title: "Integration & Testing", specialist: "tester"},
       {title: "Deployment Configuration", specialist: "devops"}
     ]
   )
   → Returns task breakdown with IDs

3. orchestrator_execute_subtask("architect_5a8b2c")
   → Specialist provides: "Create monorepo structure with separate client/server directories, 
      shared TypeScript types, Docker configuration, and comprehensive testing setup"

4. 

# Claude Code implements architecture:

   create_directory("/project")
   create_directory("/project/client")
   create_directory("/project/server")
   create_directory("/project/shared")
   create_file("/project/package.json", content="...")
   create_file("/project/docker-compose.yml", content="...")
   create_file("/project/client/package.json", content="...")
   create_file("/project/server/package.json", content="...")

5. orchestrator_complete_subtask(
     task_id="architect_5a8b2c",
     results="Established monorepo architecture with TypeScript, Docker support",
     artifacts=["package.json", "docker-compose.yml", "client/", "server/", "shared/"],
     next_action="continue"
   )

```text

**Result:** Complete, well-tested web application with 25+ files, proper structure, and comprehensive testing.

#

#

# Example 2: Data Processing Pipeline

**User Request:** "Create a Python pipeline that processes CSV files, cleans data, and generates reports"

**Coordination Pattern:**

```text

1. orchestrator_plan_task() → 4 subtasks created

2. For data_architect_task:

- orchestrator_execute_subtask() → "Design pandas-based pipeline with configurable stages"

- Claude Code creates: pipeline.py, config.yaml, data_models.py

- orchestrator_complete_subtask() → records architecture decisions

3. For processor_implementation:

- orchestrator_execute_subtask() → "Implement data cleaning with validation and logging"

- Claude Code creates: processors/, validation.py, logging_config.py

- orchestrator_complete_subtask() → records implementation details

4. For testing_specialist:

- orchestrator_execute_subtask() → "Create comprehensive test suite with sample data"

- Claude Code creates: tests/, sample_data/, pytest configuration

- orchestrator_complete_subtask() → records test coverage

5. orchestrator_synthesize_results() → Complete pipeline with documentation

```text

#

# 🎛️ Advanced Coordination Patterns

#

#

# Pattern 1: Iterative Refinement

When initial implementation needs improvement:

```text

1. orchestrator_execute_subtask("reviewer_xyz")
   → "Code review reveals performance bottlenecks in data processing"

2. 

# Claude Code analyzes current implementation:

   read_file("/project/src/processor.py")
   

3. orchestrator_execute_subtask("optimizer_abc") 
   → "Optimize using vectorized operations and memory management"

4. 

# Claude Code implements optimizations:

   edit_file("/project/src/processor.py", old_content="...", new_content="...")
   

5. orchestrator_complete_subtask(results="Applied vectorization, 10x performance improvement")

```text

#

#

# Pattern 2: Multi-Language Projects

Coordination across different technology stacks:

```text

1. orchestrator_plan_task() → Creates language-specific subtasks

2. python_specialist → Designs backend architecture

3. Claude Code → Implements Python backend files

4. javascript_specialist → Designs frontend architecture  

5. Claude Code → Implements React/TypeScript frontend

6. integration_specialist → Designs API contracts

7. Claude Code → Creates OpenAPI specs and integration tests

```text

#

#

# Pattern 3: Legacy System Integration

Working with existing codebases:

```text

1. orchestrator_execute_subtask("legacy_analyzer")
   → "Analyze existing codebase structure and identify integration points"

2. 

# Claude Code examines existing code:

   read_file("/legacy/src/main.py")
   search_files(pattern="*.py", directory="/legacy")

3. orchestrator_execute_subtask("integration_architect")
   → "Design adapter pattern for seamless legacy integration"

4. 

# Claude Code creates integration layer:

   create_file("/project/adapters/legacy_adapter.py")
   create_file("/project/tests/test_legacy_integration.py")

```text

#

# 🛠️ Error Handling & Recovery

#

#

# Workflow-Level Error Recovery (Orchestrator)

```text
python

# When a subtask fails:

orchestrator_complete_subtask(
    task_id="failed_task",
    results="Implementation failed due to dependency conflicts",
    next_action="needs_revision"
)

# Orchestrator creates recovery subtask:

orchestrator_execute_subtask("troubleshooter_123")

# → Provides debugging guidance and alternative approaches

```text

#

#

# Execution-Level Error Recovery (Claude Code)

```python

# When file operations fail:

try:
    create_file("/project/src/app.py", content="...")
except FileExistsError:
    

# Claude Code handles gracefully:

    edit_file("/project/src/app.py", old_content="...", new_content="...")
    

# When code analysis reveals issues:

lint_results = analyze_code("/project/src/")
if lint_results.has_errors:
    fix_code_issues("/project/src/", issues=lint_results.errors)

```text

#

# 📊 Performance Optimization Patterns

#

#

# Parallel Subtask Execution

For independent subtasks that can run simultaneously:

```text

1. orchestrator_plan_task() → Identifies parallel opportunities

2. Execute independent subtasks:

- orchestrator_execute_subtask("frontend_dev") | Claude Code: UI components

- orchestrator_execute_subtask("backend_dev") | Claude Code: API endpoints  

- orchestrator_execute_subtask("database_dev") | Claude Code: Schema & migrations

3. orchestrator_execute_subtask("integrator") → Combines all components

```text

#

#

# Incremental Implementation

For large projects, break into meaningful chunks:

```text

Week 1: Core architecture + basic functionality
Week 2: Advanced features + integrations
Week 3: Testing + performance optimization
Week 4: Documentation + deployment

Each week follows full orchestrator → claude-code → synthesis cycle

```text

#

# 🔍 Integration Debugging

#

#

# Common Issues & Solutions

**Issue:** Orchestrator plans don't align with Claude Code capabilities
**Solution:** Use Claude Code file analysis before planning:

```text

1. 

# Claude Code analyzes constraints:

   list_directory("/project")
   read_file("/project/package.json")
   

2. orchestrator_plan_task() → Plans with full context of existing setup

```text
text

**Issue:** Context loss between subtasks
**Solution:** Use comprehensive completion records:

```text

orchestrator_complete_subtask(
    results="Detailed description of what was implemented",
    artifacts=["complete list of created/modified files"],
    next_action="continue_with_specific_guidance"
)
```text
text

**Issue:** File conflicts between tools
**Solution:** Clear ownership boundaries:

- Orchestrator NEVER writes files directly

- Claude Code ALWAYS handles file operations

- Use Claude Code to verify file states before planning

#

# 🚀 Best Practices

#

#

# 1. Start Small, Scale Up

Begin with simple 2-3 subtask workflows before attempting complex orchestrations.

#

#

# 2. Maintain Clear Ownership

- **Orchestrator:** Planning, coordination, specialist expertise, progress tracking

- **Claude Code:** File operations, code implementation, testing, directory management

#

#

# 3. Use Specific Specialist Types

Instead of generic "developer", use "backend_specialist", "frontend_architect", "security_expert" for focused expertise.

#

#

# 4. Complete Subtasks Fully

Don't move to the next subtask until the current one is completely implemented and recorded.

#

#

# 5. Leverage File Analysis

Use Claude Code's file reading capabilities to inform orchestrator planning decisions.

#

#

# 6. Document Integration Points

When Claude Code creates files, have the orchestrator document architectural decisions and integration patterns.

#

# 🎯 Success Metrics

A successful integration should demonstrate:

✅ **Strategic Planning:** Orchestrator provides expert-level guidance for each domain
✅ **Flawless Execution:** Claude Code implements exactly what was planned
✅ **Seamless Coordination:** Natural flow between planning and implementation phases
✅ **Professional Results:** well-tested code with proper structure and testing
✅ **Knowledge Transfer:** Clear documentation of decisions and patterns used

#

# 📚 Next Steps

- **Explore More Patterns:** [MCP Aggregators Guide](mcp-aggregators.md)

- **Complex Workflows:** [Multi-Server Patterns](multi-server-patterns.md)

- **Real Examples:** [Documentation Projects](../real-world-examples/documentation-projects/)

- **Advanced Techniques:** [Parallel Orchestration](../advanced-techniques/parallel-workflows.md)

---

*Master these patterns and you'll unlock development workflows that combine the best of strategic thinking with precise execution.*
