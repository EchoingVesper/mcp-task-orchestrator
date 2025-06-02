# Architecture Overview

*Visual guide to Task Orchestrator + Claude Code MCP integration*

## 🏗️ High-Level System Architecture

```
                    ┌─── User Instructions ───┐
                    │                         │
                    ▼                         ▼
    ┌─────────────────────────────┐  ┌─────────────────────────────┐
    │    Task Orchestrator MCP    │  │     Claude Code MCP         │
    │                             │  │                             │
    │  ┌─────────────────────┐    │  │  ┌─────────────────────┐    │
    │  │   Session Manager   │    │  │  │   File Operations   │    │
    │  │                     │    │  │  │                     │    │
    │  │ • Context Tracking  │    │  │  │ • Read/Write Files  │    │
    │  │ • Task State        │    │  │  │ • Directory Ops     │    │
    │  │ • Progress Monitor  │    │  │  │ • Search & Analysis │    │
    │  └─────────────────────┘    │  │  └─────────────────────┘    │
    │                             │  │                             │
    │  ┌─────────────────────┐    │  │  ┌─────────────────────┐    │
    │  │  Task Planner       │    │  │  │  Code Generator     │    │
    │  │                     │    │  │  │                     │    │
    │  │ • Break Down Tasks  │◄───┼──┼──► • Implementation    │    │
    │  │ • Assign Specialists│    │  │  │ • Testing          │    │
    │  │ • Manage Dependencies│   │  │  │ • Validation       │    │
    │  └─────────────────────┘    │  │  └─────────────────────┘    │
    │                             │  │                             │
    │  ┌─────────────────────┐    │  │  ┌─────────────────────┐    │
    │  │ Specialist Contexts │    │  │  │   Tool Integration  │    │
    │  │                     │    │  │  │                     │    │
    │  │ • Architect         │    │  │  │ • Shell Commands    │    │
    │  │ • Implementer       │    │  │  │ • Process Control   │    │
    │  │ • Documenter        │    │  │  │ • Environment Setup │    │
    │  │ • Debugger          │    │  │  │ • Dependency Mgmt   │    │
    │  └─────────────────────┘    │  │  └─────────────────────┘    │
    └─────────────────────────────┘  └─────────────────────────────┘
                    │                             │
                    └──────── Shared Project ─────┘
                               Context & State
```

## 🔄 Coordination Flow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   User Request   │────▶│  Orchestrator    │────▶│  Claude Code     │
│                  │     │  Strategic Plan  │     │  Implementation  │
│ "Build a web     │     │                  │     │                  │
│  scraper with    │     │ 1. Analyze req   │     │ 4. Write files   │
│  authentication"│     │ 2. Create tasks  │     │ 5. Execute code  │
│                  │     │ 3. Assign roles  │     │ 6. Test & debug  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
         ▲                         │                         │
         │                         ▼                         │
         │               ┌──────────────────┐                │
         │               │   Progress       │                │
         └───────────────│   Tracking &     │◄───────────────┘
                         │   Synthesis      │
                         └──────────────────┘
```

## 📊 Responsibility Matrix

| Function                  | Task Orchestrator | Claude Code | Shared |
|---------------------------|:----------------:|:-----------:|:------:|
| **Strategic Planning**    |        ✅        |      ❌     |   ❌   |
| **Task Breakdown**        |        ✅        |      ❌     |   ❌   |
| **Specialist Coordination**|       ✅        |      ❌     |   ❌   |
| **File Operations**       |        ❌        |      ✅     |   ❌   |
| **Code Implementation**   |        ❌        |      ✅     |   ❌   |
| **Testing & Validation**  |        ❌        |      ✅     |   ❌   |
| **Progress Tracking**     |        ✅        |      ❌     |   ❌   |
| **Context Maintenance**   |        ❌        |      ❌     |   ✅   |
| **Error Recovery**        |        ✅        |      ✅     |   ❌   |
| **Final Synthesis**       |        ✅        |      ❌     |   ❌   |

## 🎯 Key Design Principles

### 1. Single Responsibility
```
Task Orchestrator ────┐
                      ├─── NO OVERLAP ─── Clean Separation
Claude Code     ──────┘
```

### 2. Sequential Coordination
```
Plan ──▶ Execute ──▶ Track ──▶ Synthesize
  ▲                                │
  └────── Feedback Loop ───────────┘
```

### 3. Context Preservation
```
┌─── Session Context ───┐
│                       │
│ • Project Goals       │
│ • Current Progress    │
│ • Specialist States   │
│ • File Locations      │
│ • Dependencies        │
│                       │
└───────────────────────┘
```

This architecture ensures clean separation of concerns while maintaining powerful coordination capabilities.
