# Git Worktree Strategy - Vespera Scriptorium Multi-Agent Coordination

**Meta-PRP**: Vespera Scriptorium Transition  
**Template Source**: [PRPs/templates/meta_prp_structure.md](../templates/meta_prp_structure.md)  
**Last Updated**: 2025-01-14

## Overview

This document outlines the git worktree strategy for multi-agent coordination during the Vespera Scriptorium transition, designed specifically for executive dysfunction accessibility and conflict prevention.

## Executive Dysfunction Problem Statement

**Traditional Git Challenges**:
- Merge conflicts create overwhelming decision paralysis
- Branch management adds cognitive overhead
- Context switching between features increases mental load
- Lost work due to complex git operations

**ED-Aware Solution**:
- Isolated worktrees eliminate conflicts
- Pre-defined branching strategy removes decisions
- Auto-preservation prevents work loss
- Clear coordination patterns reduce overwhelm

## Worktree Structure for Vespera Scriptorium

### Repository Layout

```directory
main-repo/                              # Main repository (coordination hub)
├── PRPs/vespera-scriptorium-transition/ # Meta-PRP structure
├── mcp_task_orchestrator/              # Source code
├── docs/                               # Documentation
└── [all other project files]

worktrees/                              # Parallel agent workspaces
├── agent-cicd-fixes/                  # Priority 1: CI/CD Pipeline Fixes
│   ├── [full repo copy]               # Branch: feature/cicd-fixes
│   └── .task_orchestrator/            # Agent-specific orchestrator session
├── agent-docs-audit/                  # Priority 2: Documentation Audit
│   ├── [full repo copy]               # Branch: feature/docs-audit
│   └── .task_orchestrator/            # Agent-specific orchestrator session
├── agent-template-system/             # Priority 3: Template System
│   ├── [full repo copy]               # Branch: feature/template-system
│   └── .task_orchestrator/            # Agent-specific orchestrator session
└── agent-feature-impl/                # Priority 4: Feature Implementation
    ├── [full repo copy]               # Branch: feature/implementation
    └── .task_orchestrator/            # Agent-specific orchestrator session
```

### Branch Strategy

**Main Branch**: `vespera-integration-prep`
- Coordination hub for all work
- Meta-PRP structure maintained here
- Final integration point for all features

**Feature Branches**: `feature/{priority-name}`
- `feature/cicd-fixes` - CI/CD pipeline fixes
- `feature/docs-audit` - Documentation audit work
- `feature/template-system` - Template system implementation
- `feature/implementation` - Feature implementation work

## Worktree Management Commands

### Initial Setup

```bash
# Navigate to main repository
cd /home/aya/dev/mcp-servers/mcp-task-orchestrator

# Create worktrees for each priority area
git worktree add ../worktrees/agent-cicd-fixes -b feature/cicd-fixes
git worktree add ../worktrees/agent-docs-audit -b feature/docs-audit
git worktree add ../worktrees/agent-template-system -b feature/template-system
git worktree add ../worktrees/agent-feature-impl -b feature/implementation

# Verify worktree creation
git worktree list
```

### Agent Work Pattern

```bash
# Agent starts work in their dedicated worktree
cd ../worktrees/agent-{priority-name}

# Executive dysfunction support: Auto-preservation every 30 minutes
git add -A && git commit -m "WIP: Auto-save $(date +%Y%m%d-%H%M%S)"

# During work: Regular progress commits
git add -A && git commit -m "WIP: {description of current progress}"

# When task/session completes
git add -A && git commit -m "feat({scope}): {detailed completion description}"
```

### Integration Workflow

```bash
# Main coordination agent merges completed work
cd /home/aya/dev/mcp-servers/mcp-task-orchestrator

# Merge priority work as it completes
git merge feature/cicd-fixes        # When Priority 1 complete
git merge feature/docs-audit        # When Priority 2 complete
git merge feature/template-system   # When Priority 3 complete
git merge feature/implementation    # When Priority 4 complete

# Clean up completed worktrees
git worktree remove ../worktrees/agent-cicd-fixes
git worktree remove ../worktrees/agent-docs-audit
git worktree remove ../worktrees/agent-template-system
git worktree remove ../worktrees/agent-feature-impl
```

## Executive Dysfunction Support Features

### 1. Decision Elimination

**Pre-Defined Strategy**:
- Worktree names follow standard pattern: `agent-{priority-name}`
- Branch names follow standard pattern: `feature/{priority-name}`
- Directory structure identical across all worktrees
- Commands documented and standardized

### 2. Conflict Prevention

**Isolation Benefits**:
- Each agent works in completely isolated environment
- No merge conflicts during development
- Independent progress at different speeds
- No interference between agents

### 3. Progress Preservation

**Auto-Preservation**:
- WIP commits every 30 minutes prevent work loss
- Progress maintained across sleep resets
- Recovery possible from any interruption
- Git history preserves all development stages

### 4. Context Maintenance

**Session Continuity**:
- Each worktree maintains its own `.task_orchestrator/` session
- Agent context preserved independently
- Orchestrator state specific to each priority
- No session conflicts between agents

## Agent Coordination Patterns

### Priority 1: CI/CD Pipeline Fixes

```bash
# Agent spawning with worktree context
cd ../worktrees/agent-cicd-fixes

# Agent instructions include:
WORKTREE_INTEGRATION:
  - Working in isolated environment
  - Branch: feature/cicd-fixes
  - Auto-preservation every 30 minutes
  - No conflicts with other agents
  
FOCUS_AREA:
  - CI/CD pipeline diagnosis and fixes
  - Test failure analysis and resolution
  - Build system optimization
```

### Priority 2: Documentation Audit

```bash
# Agent spawning with worktree context
cd ../worktrees/agent-docs-audit

# Agent instructions include:
WORKTREE_INTEGRATION:
  - Working in isolated environment
  - Branch: feature/docs-audit
  - Documentation changes safely isolated
  - No impact on other development work
  
FOCUS_AREA:
  - Documentation inventory and audit
  - Archival of existing docs
  - New documentation structure creation
```

## Emergency Procedures

### Overwhelm Recovery

```bash
# If agent becomes overwhelmed, preserve work immediately
cd ../worktrees/agent-{current-work}
git add -A && git commit -m "EMERGENCY SAVE: $(date) - overwhelm detected"

# Switch to main repo for coordination
cd /home/aya/dev/mcp-servers/mcp-task-orchestrator

# Document current state in tracking
echo "$(date): Overwhelm detected in {priority-area}, work preserved" >> \
  PRPs/vespera-scriptorium-transition/00-main-coordination/tracking/emergency-log.md
```

### Work Recovery

```bash
# To resume work after interruption
cd ../worktrees/agent-{priority-name}

# Check last work state
git log --oneline -5

# Resume from last WIP commit
# Work context preserved in orchestrator session
```

### Worktree Corruption Recovery

```bash
# If worktree becomes corrupted
git worktree remove ../worktrees/agent-{priority-name}
git worktree add ../worktrees/agent-{priority-name} feature/{priority-name}

# Work preserved in git history, can be recovered
cd ../worktrees/agent-{priority-name}
git log --oneline  # Find last good commit
```

## Success Metrics

### Conflict Prevention
- [ ] **Zero merge conflicts** during parallel development
- [ ] **100% agent isolation** maintained throughout
- [ ] **No work interference** between priority areas

### Progress Preservation
- [ ] **Work loss incidents**: 0
- [ ] **Recovery time** from interruption: < 30 seconds
- [ ] **Context preservation** across sleep resets: 100%

### Coordination Efficiency
- [ ] **Agent spawn time**: < 2 minutes
- [ ] **Worktree setup overhead**: < 5 minutes total
- [ ] **Integration complexity**: Low (simple merge commands)

### Executive Dysfunction Support
- [ ] **Decision points eliminated**: 90%+
- [ ] **Cognitive load reduction**: Measurable via self-report
- [ ] **Overwhelm recovery**: < 5 minutes
- [ ] **User confidence**: High (no fear of losing work)

## Future Enhancements

### Automated Worktree Management

```bash
# Future script: setup-meta-prp-worktrees.sh
#!/bin/bash
# Automatically create all worktrees for meta-PRP execution
# Include agent-specific orchestrator session initialization
# Set up auto-preservation hooks
```

### Advanced ED Features

- **Biometric Integration**: Detect stress and auto-preserve work
- **Adaptive Complexity**: Simplify git operations when overwhelmed
- **Visual Progress**: GUI showing worktree status and agent progress
- **Smart Recovery**: AI-assisted work recovery from interruptions

---

**Remember**: This git strategy exists to support executive dysfunction accessibility. Every command and procedure should reduce cognitive load and prevent work loss, not add complexity.