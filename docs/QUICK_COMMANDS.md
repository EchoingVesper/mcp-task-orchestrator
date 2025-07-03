# Quick Commands Reference

*Copy-paste commands for common orchestrator tasks*

## Essential Workflow Commands

### Start a New Project

```
"Initialize a new orchestration session and plan a project to [describe your project]"
```

### Get Current Status

```
"Check the status of all active tasks and show progress"
```

### Resume Work

```
"Initialize session and show me any interrupted tasks I can resume"
```

### Finish and Handoff

```
"Synthesize all results and prepare handover documentation"
```

## Maintenance Commands

### Daily Cleanup

```
"Use the maintenance coordinator to scan and cleanup the current session"
```

### Performance Optimization

```
"Run a comprehensive maintenance scan on the full project to optimize performance"
```

### Before Handoffs

```
"Prepare handover documentation with comprehensive validation"
```

### System Health Check

```
"Validate the structure of the full project with full audit level"
```

## Specialist Task Commands

### For Architecture Work

```
"Execute the architect subtask [task_id] and provide system design guidance"
```

### For Implementation

```
"Execute the implementer subtask [task_id] and provide coding guidance"
```

### For Documentation

```
"Execute the documenter subtask [task_id] and provide documentation guidance"
```

### For Testing

```
"Execute the tester subtask [task_id] and provide testing guidance"
```

## Task Completion Commands

### Complete with Files Created

```
"Complete subtask [task_id] with summary: [brief summary], files created: [file1.py, file2.md], artifact type: code, next action: continue"
```

### Complete Documentation Task

```
"Complete subtask [task_id] with summary: [doc summary], artifact type: documentation, next action: continue"
```

### Complete with Issue

```
"Complete subtask [task_id] with summary: [issue description], next action: needs_revision"
```

## Complex Project Examples

### Web Development Project

```
"Initialize orchestration and plan a full-stack web application with React frontend, Node.js backend, PostgreSQL database, including testing, documentation, and deployment setup"
```

### Data Processing Pipeline

```
"Initialize orchestration and create a data processing pipeline that extracts data from APIs, transforms it using Python, stores in a database, and generates automated reports"
```

### Documentation Project

```
"Initialize orchestration and plan a comprehensive documentation project including API documentation, user guides, tutorials, and migration documentation"
```

### Legacy System Migration

```
"Initialize orchestration and plan migration of a legacy PHP application to modern Python Django, including database migration, API compatibility, and user training"
```

## Troubleshooting Commands

### Check for Issues

```
"Check status and run maintenance validation to identify any system issues"
```

### Fix Stale Tasks

```
"Run maintenance coordinator with comprehensive cleanup to fix any stale or orphaned tasks"
```

### Reset Database

```
"If you're experiencing database issues, restart your MCP client and delete the .task_orchestrator folder"
```

### Get Diagnostic Info

```
"Show system status, active tasks, and any maintenance recommendations"
```

## Advanced Commands

### Custom Specialist Roles

```
"Initialize session and plan a project using custom roles including security_auditor and performance_engineer"
```

### Large Project Management

```
"Initialize session and create a multi-phase project plan with 15+ subtasks for [complex project description]"
```

### Cross-Project Synthesis

```
"Synthesize results from multiple completed task breakdowns into a unified project deliverable"
```

## Maintenance Schedule Commands

### Daily (5 minutes)

```
"Run basic maintenance cleanup on current session"
```

### Weekly (10 minutes)

```
"Run comprehensive maintenance scan on current session and review recommendations"
```

### Monthly (20 minutes)

```
"Run full project comprehensive maintenance scan and prepare optimization recommendations"
```

### Before Major Milestones

```
"Run full audit validation on entire project and prepare comprehensive handover documentation"
```

## Integration Commands

### With Git Workflows

```
"Initialize session, plan code review process, and prepare branch management documentation"
```

### With CI/CD Pipelines

```
"Plan deployment automation including testing, building, and release documentation"
```

### With Team Handoffs

```
"Prepare comprehensive handover including status summary, artifact organization, and next steps documentation"
```

## Command Variations by MCP Client

### For Claude Desktop

```
"Use orchestrator_initialize_session to begin workflow coordination"
```

### For Cursor/VS Code

```
"Initialize task orchestration for this project and create development plan"
```

### For General Usage

```
"Start the task orchestrator and help me break down this complex project into manageable steps"
```

## Tips for Better Results

### Be Specific

```
❌ "Create a website"
✅ "Create a responsive e-commerce website with user authentication, product catalog, shopping cart, and payment integration using React and Node.js"
```

### Include Context

```
❌ "Plan testing"
✅ "Plan comprehensive testing strategy for a financial API including unit tests, integration tests, security testing, and performance testing"
```

### Specify Requirements

```
❌ "Build an app"
✅ "Build a mobile-first web application for task management with offline capabilities, real-time sync, and team collaboration features"
```

### Use Action Words

```
❌ "Something with databases"
✅ "Design and implement a database migration strategy from MySQL to PostgreSQL with zero downtime"
```

## Quick Reference Card

| Task | Command Pattern |
|------|----------------|
| **Start** | "Initialize orchestration and plan..." |
| **Status** | "Check status of..." |
| **Maintain** | "Run maintenance coordinator..." |
| **Complete** | "Complete subtask [id] with..." |
| **Synthesize** | "Synthesize results from..." |
| **Resume** | "Initialize session and show interrupted..." |
| **Handoff** | "Prepare handover with..." |
| **Debug** | "Check status and run validation..." |

---

*For detailed documentation, see [API Reference](./API_REFERENCE.md) and [User Guide](./docs/user-guide/).*
