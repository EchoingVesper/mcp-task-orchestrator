

# Integration Patterns Visual Guide

*ASCII diagrams for all coordination patterns*

#

# 🔄 Sequential Coordination Pattern

```text
Time ───────────────────────────────────────────►

Phase 1:
[Orchestrator] ──► Initialize ──► Plan Task ──► Create Breakdown

Phase 2:
[Orchestrator] ──► Execute Subtask 1 ──► Get Context
[Claude Code]  ──────────────────────► Implement ──► Complete

Phase 3:
[Orchestrator] ──► Execute Subtask 2 ──► Get Context
[Claude Code]  ──────────────────────► Implement ──► Complete

Phase 4:
[Orchestrator] ──► Synthesize Results ──► Final Output

```text

#

# ⚡ Parallel Execution Pattern

```text

Time ───────────────────────────────────────────►

Planning:
[Orchestrator] ──► Identify Independent Tasks ──► Create Parallel Groups

Execution:
                   ┌─ [Claude Code A] ──► Task 1 ──► Complete
[Orchestrator] ────┼─ [Claude Code B] ──► Task 2 ──► Complete
                   └─ [Claude Code C] ──► Task 3 ──► Complete
                   │
                   └─► Synchronization Point ──► Continue

Synthesis:
[Orchestrator] ──► Combine Results ──► Final Output

```text

#

# 🛡️ Graceful Degradation Pattern

```text

Normal Operation:
[Orchestrator] ◄──► [Claude Code] ──► Full Functionality

Server Unavailable:
[Orchestrator] ──X─ [Claude Code]
       │
       └──► Fallback Mode:
            • Manual file operations
            • Alternative tools
            • Reduced functionality
            • Clear user notification

Recovery:
[Orchestrator] ◄──► [Claude Code] ──► Resume Normal Operation

```text

#

# 🌐 Multi-Server Coordination Pattern

```text

               ┌─── Task Orchestrator ───┐
               │    (Central Command)    │
               └───────────┬─────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ Claude Code │ │ Database    │ │ API Gateway │
    │    MCP      │ │    MCP      │ │    MCP      │
    └─────────────┘ └─────────────┘ └─────────────┘
            │              │              │
            └─────── Coordinated ─────────┘
                    Operations

```text

#

# 🔗 Aggregator Integration Pattern

```text

Direct Access (Complex):
[User] ──► [Tool A] ──► [Tool B] ──► [Tool C] ──► [Tool D]

Aggregated Access (Simple):
[User] ──► [Aggregator MCP] ────┐
                                ├──► [Tool A]
                                ├──► [Tool B]  
                                ├──► [Tool C]
                                └──► [Tool D]

Benefits: Unified interface, simplified workflows, coordinated operations

```text

#

# 📊 Pattern Selection Guide

```text

Choose Pattern Based On:

Simple Task        ──► Sequential Coordination
Independent Tasks  ──► Parallel Execution  
High Availability  ──► Graceful Degradation
Complex Ecosystem  ──► Multi-Server Coordination
Unified Interface  ──► Aggregator Integration
```text

Each pattern addresses specific coordination challenges while maintaining clean separation of concerns.
