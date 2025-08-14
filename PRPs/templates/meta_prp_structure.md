# Meta-PRP Hierarchical Structure Template

**Template Version**: 2.1  
**Philosophy**: Executive Dysfunction-Aware Multi-Agent Coordination with Local LLM Integration  
**Last Updated**: 2025-01-14

## Overview

This template defines the standard hierarchical structure for Meta-PRPs that coordinate complex multi-phase projects
using orchestrator-driven multi-agent workflows with git worktree isolation.

## Core Philosophy: Executive Dysfunction as Design Principle

Every Meta-PRP must be designed with these principles:
- **Momentum Preservation**: Structure survives sleep resets and interruptions
- **Lid Weight Reduction**: Pre-created directories eliminate decision paralysis
- **Pressure Delegation**: Clear structure for agent work distribution
- **Damage Prevention**: Graceful degradation paths built into structure

## Standard Directory Structure

```directory
PRPs/{project-name}-transition/
├── 00-main-coordination/           # PRIMARY ENTRY POINT
│   ├── index.md                   # Main coordination hub
│   ├── index/                     # Auto-generated indices (WORKING DIR)
│   │   ├── README.md              # Explains this folder's purpose
│   │   └── [generated files]      # Created during execution
│   ├── subtasks/                  # Coordination subtasks
│   │   ├── philosophy-integration-patterns.md  # Design patterns
│   │   ├── orchestrator-coordination-patterns.md  # Workflow patterns
│   │   └── [coordination tasks]   # Additional coordination docs
│   └── tracking/                  # Progress tracking (WORKING DIR)
│       ├── checklist.md           # Master tracking checklist
│       ├── session-logs/          # Orchestrator session records
│       └── progress-reports/      # Generated progress summaries
│
├── 01-{priority-1-name}/          # Highest priority work
│   ├── index.md                   # Priority area coordination
│   ├── index/                     # Auto-generated indices
│   ├── subtasks/                  # Atomic task breakdowns
│   └── tracking/                  # Priority-specific tracking
│
├── 02-{priority-2-name}/          # Second priority work
│   ├── index.md                   # Priority area coordination
│   ├── index/                     # Auto-generated indices
│   ├── subtasks/                  # Atomic task breakdowns
│   └── tracking/                  # Priority-specific tracking
│
├── 03-{priority-3-name}/          # Third priority work
│   └── [same structure]
│
├── 04-{priority-4-name}/          # Fourth priority work
│   └── [same structure]
│
├── README.md                      # Meta-PRP overview and navigation
├── executive-dysfunction-philosophy.md  # Optional: Project-specific ED notes
└── [archived-source-prps]/        # Optional: Source PRPs if being merged
```

## Folder Purpose Documentation

### The `index/` Folders (Working Directories)

**Purpose**: Auto-generated navigation and cross-references  
**Created By**: Orchestrator agents during execution  
**Contents**:
- File listings with descriptions
- Cross-reference maps between tasks
- Quick navigation indices
- Dependency graphs
- Progress summaries

**README.md Template**:

```markdown
# Index Directory - Auto-Generated Content

This directory contains auto-generated indices created during Meta-PRP execution.

## Purpose
- Navigation aids for complex task structures
- Cross-references between related tasks
- Quick access to frequently needed information
- Progress visualization

## Do Not Edit
Files in this directory are generated automatically. Manual edits will be overwritten.

## Generated Files
- `file-index.json` - Complete file listing with metadata
- `cross-references.md` - Links between related tasks
- `dependency-graph.dot` - Visual task dependencies
- `progress-summary.md` - Current execution status
```

### The `subtasks/` Folders

**Purpose**: Atomic task breakdowns for execution  
**Created By**: During planning phase or execution  
**Contents**:
- Individual task files (numbered for order)
- Multi-level organization with category subfolders
- Task templates ready for agent work
- Local LLM integration specifications
- Implementation specifications

**Multi-Level Organization**:

```text
subtasks/
├── 00-{category-name}/           # Task category (analysis, fixes, etc.)
│   ├── README.md                 # Category overview and structure
│   ├── 01-{first-task}.md        # First atomic task in category
│   ├── 02-{second-task}.md       # Second atomic task in category
│   └── ...
├── 01-{next-category}/           # Next task category
│   ├── README.md                 # Category overview
│   ├── 01-{task}.md              # Tasks within category
│   └── ...
└── README.md                     # Overall subtasks overview
```

**Benefits of Multi-Level Structure**:
- **Executive Dysfunction Support**: Clearer task organization reduces overwhelm
- **Local LLM Integration**: Category-based organization supports automated task distribution
- **Agent Specialization**: Categories align with specialist agent types
- **Progressive Disclosure**: Complexity revealed gradually by category

### The `tracking/` Folders (Working Directories)

**Purpose**: Progress tracking and session management  
**Created By**: Orchestrator and agents during execution  
**Contents**:
- Checklists (manually created and updated)
- Session logs from orchestrator
- Progress reports (auto-generated)
- Artifact manifests
- Error logs and recovery points

**README.md Template**:

```markdown
# Tracking Directory - Progress and Session Management

This directory tracks Meta-PRP execution progress and orchestrator sessions.

## Contents
- `checklist.md` - Master tracking checklist (manually maintained)
- `session-logs/` - Orchestrator session records (auto-generated)
- `progress-reports/` - Periodic progress summaries (auto-generated)
- `artifacts/` - References to orchestrator artifacts
- `errors/` - Error logs and recovery information

## Session Management
Each orchestrator session creates a log file:
- `session_{id}_{timestamp}.json` - Full session record
- `session_{id}_artifacts.md` - Artifact references
- `session_{id}_status.md` - Final status report
```

## Git Worktree Strategy Integration

### Worktree Structure for Multi-Agent Work

```directory
main-repo/                         # Main repository
├── PRPs/{project-name}-transition/  # Meta-PRP structure
│
worktrees/                         # Parallel agent workspaces
├── agent-{task-01}/              # Worktree for task 01
│   └── [full repo copy on feature branch]
├── agent-{task-02}/              # Worktree for task 02
│   └── [full repo copy on feature branch]
└── agent-{task-03}/              # Worktree for task 03
    └── [full repo copy on feature branch]
```

### Worktree Management Commands

```bash
# Create worktree for agent task
git worktree add ../worktrees/agent-{task-id} -b feature/{task-name}

# Agent works in isolated worktree
cd ../worktrees/agent-{task-id}
# Implementation happens here

# Auto-preserve work (executive dysfunction support)
git add -A && git commit -m "WIP: Auto-save $(date +%Y%m%d-%H%M%S)"

# When task completes
git add -A && git commit -m "feat({scope}): {task description}"

# Merge back to main
cd ../../main-repo
git merge feature/{task-name}

# Clean up worktree
git worktree remove ../worktrees/agent-{task-id}
```

## Local LLM Integration Patterns

### Pattern 1: Task Readiness Classification

**Objective**: Classify tasks by local LLM automation readiness  
**Implementation**: Use consistent readiness indicators in task metadata

**Readiness Levels**:
- **✅ High**: Structured input/output, clear prompts, deterministic validation
- **🟡 Medium**: Some ambiguity, requires human verification
- **❌ Low**: Complex reasoning, creative decisions, multi-step coordination

### Pattern 2: Structured Prompt Templates

**Objective**: Standardize prompts for consistent local LLM execution  
**Implementation**: Include prompt templates in every high-readiness task

**Template Structure**:
```text
CONTEXT: {Background information}
TASK: {Specific objective}
INPUT: {Structured input data}
REQUIREMENTS: {Specific constraints and requirements}
OUTPUT_FORMAT: {Expected output structure}
VALIDATION: {How to verify success}
```

### Pattern 3: Category-Based Task Distribution

**Objective**: Align task categories with LLM capabilities and agent specialization  
**Implementation**: Organize subtasks into categories that match:
- Analysis tasks → Research/data processing LLMs
- Fix implementation → Code-focused LLMs
- Design tasks → Architecture/planning LLMs

### Pattern 4: Progressive Automation

**Objective**: Enable gradual transition from manual to automated execution  
**Implementation**: Structure tasks so they can be:
1. **Manual**: Human agent execution with clear instructions
2. **Semi-Automated**: Local LLM generates, human verifies
3. **Fully Automated**: Local LLM executes with validation checks

## Executive Dysfunction Design Patterns

### Pattern 1: Pre-Created Structure

**Problem**: Creating directories requires decisions (heavy lid)  
**Solution**: All directories pre-created, ready for content  
**Implementation**: Use this template to create full structure upfront

### Pattern 2: Clear Naming Convention

**Problem**: Naming decisions cause paralysis  
**Solution**: Strict numbering (00-99) and descriptive suffixes  
**Implementation**: Priority-based numbering, task-based naming

### Pattern 3: Working Directory Markers

**Problem**: Confusion about what's manual vs generated  
**Solution**: Clear README files explaining each directory's purpose  
**Implementation**: Include README templates in structure creation

### Pattern 4: Progress Visibility

**Problem**: Loss of momentum when progress unclear  
**Solution**: Multiple tracking mechanisms at different granularities  
**Implementation**: Checklists, session logs, progress reports

## Meta-PRP File Templates

### Main Coordination Index (`00-main-coordination/index.md`)

```markdown
# {Project Name} Meta-PRP - Main Coordination

**Meta-PRP ID**: `{PROJECT}_TRANSITION_{YEAR}`  
**Type**: Multi-Agent Coordination with Full Orchestrator Integration  
**Priority**: {Priority Level}  
**Estimated Total Effort**: {Timeline}  
**Status**: [IN-PROGRESS]  
**Orchestrator Session**: `{session_id}`  
**Parent Task ID**: `{task_id}`

## Foundational Philosophy: Executive Dysfunction as Design Principle

{Project-specific ED considerations}

## Executive Summary

{High-level overview of the meta-PRP goals}

## Priority Structure

### Priority 1: {Name} ({Timeline})
**Location**: [01-{name}/](../01-{name}/index.md)  
**Status**: {Status}  
**Orchestrator Tasks**: `{task_range}`  
**Issue**: {What problem this solves}

{Additional priorities...}

## Multi-Agent Coordination Structure

{Agent hierarchy and workflow}

## Success Metrics

{Measurable success criteria}

## Navigation

- Priority 1: [01-{name}/index.md](../01-{name}/index.md)
- Priority 2: [02-{name}/index.md](../02-{name}/index.md)
- Tracking: [tracking/checklist.md](tracking/checklist.md)
```

### Priority Area Index (`0X-{priority-name}/index.md`)

```markdown
# Priority {X}: {Full Name}

**Parent Task ID**: `{parent_task_id}`  
**Priority**: {Priority Level}  
**Status**: [{STATUS}]  
**Estimated Duration**: {Timeline}  
**Specialist Type**: {Primary Specialist}

## Problem Statement

{What problem this priority area solves}

## Executive Dysfunction Design Focus

**Lid Weight Impact**: {How this reduces task initiation barriers}
**Momentum Preservation**: {How this maintains progress}
**Pressure Delegation**: {What can be delegated to agents}

## Subtasks

{List of atomic subtasks with links}

## Success Criteria

{Measurable completion criteria}

## Tracking

- Checklist: [tracking/checklist.md](tracking/checklist.md)
- Sessions: [tracking/session-logs/](tracking/session-logs/)
```

### Subtask Template (`subtasks/XX-{category}/YY-{task-name}.md`)

```markdown
# {Task Title}

**Task ID**: `{category}-{task-type}-{number}`  
**Type**: {Analysis|Fix Implementation|Design|etc.}  
**Local LLM Ready**: ✅ High | 🟡 Medium | ❌ Low  
**Estimated Duration**: {Timeline}  
**Priority**: 🔴 Critical | 🟡 Medium | 🟢 Low

## Objective

{Clear, single objective}

## Inputs

{Specific files, commands, or data to analyze}

## Expected Outputs

{Precise deliverables - JSON files, code changes, documentation}

## Success Criteria

- [ ] {Measurable completion criteria}
- [ ] {Validation commands pass}
- [ ] {Expected outputs generated}

## Local LLM Prompt Template

```
{Structured prompt for local LLM execution}

INPUT_DATA: {input_specification}
REQUIREMENTS: {specific_requirements}

Expected output: {format_specification}
```

## Agent Instructions

{Specific instructions for executing agent}

## Validation

{Commands to verify task completion}

## Git Worktree Strategy

{Worktree approach for this task if applicable}
```

### Category README Template (`subtasks/XX-{category}/README.md`)

```markdown
# {Category Name} Subtasks

**Purpose**: {High-level purpose of this task category}  
**Local LLM Ready**: {Overall readiness level for automation}  
**Executive Dysfunction Support**: {How this category reduces cognitive load}

## Task Structure

{Explanation of how tasks in this category are organized}

## Benefits

- **{Benefit 1}**: {Description}
- **{Benefit 2}**: {Description}
- **Local LLM Integration**: {How tasks support automation}
```

## Automation Opportunities

### Structure Creation Script

```python
#!/usr/bin/env python3
"""Create Meta-PRP structure from template"""

import os
from pathlib import Path

def create_meta_prp_structure(project_name, priorities):
    """Create full Meta-PRP directory structure"""
    
    base_path = Path(f"PRPs/{project_name}-transition")
    
    # Create main coordination
    create_priority_structure(base_path / "00-main-coordination", 
                            "Main Coordination", is_main=True)
    
    # Create priority areas
    for i, priority in enumerate(priorities, 1):
        create_priority_structure(base_path / f"{i:02d}-{priority['slug']}", 
                                 priority['name'])
    
    # Create README
    create_readme(base_path, project_name, priorities)
    
    print(f"✅ Created Meta-PRP structure at {base_path}")

def create_priority_structure(path, name, is_main=False, subtask_categories=None):
    """Create structure for a priority area"""
    
    # Create directories
    (path / "index").mkdir(parents=True, exist_ok=True)
    (path / "subtasks").mkdir(parents=True, exist_ok=True)
    (path / "tracking").mkdir(parents=True, exist_ok=True)
    
    # Create multi-level subtask structure if categories provided
    if subtask_categories:
        create_subtask_categories(path / "subtasks", subtask_categories)
    
    # Create index.md
    create_index_file(path, name, is_main)
    
    # Create README files for working directories
    create_working_dir_readme(path / "index", "Index")
    create_working_dir_readme(path / "tracking", "Tracking")
    
    # Create checklist
    create_checklist(path / "tracking", name)

def create_subtask_categories(subtasks_path, categories):
    """Create multi-level subtask category structure"""
    
    # Create main subtasks README
    create_subtasks_overview_readme(subtasks_path, categories)
    
    # Create each category
    for i, category in enumerate(categories):
        category_path = subtasks_path / f"{i:02d}-{category['slug']}"
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Create category README
        create_category_readme(category_path, category)
        
        # Create placeholder task files if specified
        if 'tasks' in category:
            for j, task in enumerate(category['tasks'], 1):
                task_file = category_path / f"{j:02d}-{task['slug']}.md"
                create_task_template(task_file, task, category)
```

## Success Patterns

### Pattern 1: Incremental Population

Start with structure, populate incrementally as work progresses

### Pattern 2: Agent Isolation

Each agent works in own worktree, prevents conflicts

### Pattern 3: Artifact-Centric

All detailed work in orchestrator artifacts, structure holds references

### Pattern 4: Progressive Disclosure

Structure reveals complexity gradually, not all at once

## Common Pitfalls to Avoid

1. **Over-Population**: Don't pre-create every possible file
2. **Under-Structure**: Don't skip the working directories
3. **Mixed Content**: Keep generated and manual content separate
4. **Lost Context**: Always link back to main coordination
5. **Forgotten Philosophy**: Every decision should consider ED impact

## Validation Checklist

### Structure Validation
- [ ] All priority areas have consistent structure
- [ ] Working directories have README files
- [ ] Main coordination links to all priorities
- [ ] Each priority has index.md
- [ ] Tracking checklists created

### Multi-Level Subtask Validation
- [ ] Subtask categories organized logically
- [ ] Category README files explain purpose and structure
- [ ] Tasks classified by Local LLM readiness (✅🟡❌)
- [ ] Task templates include structured prompt sections
- [ ] Validation commands specified for each task

### Local LLM Integration Validation
- [ ] High-readiness tasks have complete prompt templates
- [ ] Input/output specifications are structured
- [ ] Task categories align with LLM capabilities
- [ ] Progressive automation paths documented

### Executive Dysfunction Design Validation
- [ ] Executive dysfunction philosophy documented
- [ ] Lid weight reduction strategies implemented
- [ ] Momentum preservation mechanisms in place
- [ ] Pressure delegation patterns documented
- [ ] Damage prevention procedures specified

### Git and Coordination Validation
- [ ] Git worktree strategy documented
- [ ] Success metrics defined
- [ ] Navigation paths clear
- [ ] Agent coordination patterns specified

---

*This template ensures Meta-PRPs are structured for executive dysfunction accessibility while supporting complex multi-
agent orchestration workflows.*
