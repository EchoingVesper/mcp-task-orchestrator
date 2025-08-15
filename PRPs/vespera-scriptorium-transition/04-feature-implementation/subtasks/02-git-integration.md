# Subtask: Git Integration & Issue Management

**Task ID**: `feature-02`  
**Parent**: Feature Implementation  
**Source PRP**: `02-[PENDING]-git-integration-task-orchestrator.md`  
**Type**: Feature Implementation  
**Priority**: HIGH - Momentum preservation critical  
**Estimated Duration**: 3-4 days

## Executive Dysfunction Design Focus

**Lid Weight Impact**: Git operations often create heavy lids due to complexity
**Momentum Preservation**: Automatic context preservation across git operations  
**Pressure Delegation**: Agents handle branching, commits, and PR creation
**Damage Prevention**: Prevents git-related frustration that damages projects

## Feature Overview

Comprehensive Git platform integration designed to eliminate git as a barrier to progress, with special focus on preserving work during low-capacity periods.

## Core Components

### 1. Issue Tracking Integration
```yaml
purpose: "Seamlessly link tasks to issues"
lid_reduction: "No manual issue lookup needed"
features:
  - Auto-link commits to issues
  - Create issues from tasks
  - Update issue status automatically
  - Generate release notes from issues
```

### 2. Smart Commit Organization
```yaml
purpose: "Intelligent commit management"
lid_reduction: "No commit message paralysis"
features:
  - Auto-generate semantic commits
  - Group related changes
  - Preserve work-in-progress automatically
  - Recover from interrupted commits
```

### 3. Branch Management Automation
```yaml
purpose: "Effortless branch workflows"
lid_reduction: "No branch confusion"
features:
  - Auto-create feature branches
  - Smart branch naming
  - Automatic cleanup
  - Worktree integration for agents
```

### 4. PR/MR Workflow Automation
```yaml
purpose: "Streamlined pull request process"
lid_reduction: "No PR preparation overhead"
features:
  - Auto-generate PR descriptions
  - Link related issues
  - Add reviewers automatically
  - Create draft PRs for WIP
```

## Git Worktree Integration

**CRITICAL**: Leverage git worktrees for multi-agent coordination

```python
class GitWorktreeManager:
    """Manages worktrees for agent isolation"""
    
    def create_agent_worktree(self, agent_id, feature_name):
        """Create isolated worktree for agent"""
        worktree_path = f"../worktrees/{agent_id}-{feature_name}"
        branch_name = f"feature/{feature_name}"
        
        # Create worktree with new branch
        self.execute(f"git worktree add {worktree_path} -b {branch_name}")
        
        return WorktreeContext(worktree_path, branch_name)
    
    def preserve_agent_work(self, agent_id):
        """Auto-commit WIP to prevent work loss"""
        # Critical for executive dysfunction support
        self.auto_commit_wip(agent_id)
        
    def merge_agent_work(self, agent_id):
        """Merge completed work back to main"""
        # Handles complexity transparently
```

## Implementation Architecture

### Database Schema
```sql
-- Track git operations for momentum preservation
CREATE TABLE git_sessions (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    branch_name TEXT,
    worktree_path TEXT,
    last_commit_sha TEXT,
    wip_preserved BOOLEAN,
    created_at TIMESTAMP,
    UNIQUE(session_id)
);

CREATE TABLE issue_links (
    id INTEGER PRIMARY KEY,
    task_id TEXT NOT NULL,
    issue_number INTEGER,
    platform TEXT, -- github, gitlab, etc
    auto_updated BOOLEAN
);
```

### Core Modules

Located in `mcp_task_orchestrator/features/git/`:
- `worktree_manager.py` - Worktree orchestration
- `issue_tracker.py` - Issue integration
- `commit_organizer.py` - Smart commits
- `branch_automation.py` - Branch workflows
- `pr_automation.py` - PR/MR management

## Executive Dysfunction Optimizations

### Auto-Preservation System
```python
class AutoPreservation:
    """Prevents work loss during low-capacity periods"""
    
    def monitor_uncommitted_changes(self):
        """Watch for uncommitted work"""
        # Run every 5 minutes
        if self.has_uncommitted_changes():
            self.create_wip_commit()
    
    def create_wip_commit(self):
        """Auto-commit with WIP message"""
        # Preserves work without user intervention
        message = f"WIP: Auto-save {datetime.now()}"
        self.commit_all(message)
    
    def recover_from_interruption(self):
        """Restore context after interruption"""
        # Combats sleep reset problem
        return self.restore_last_session()
```

### Semantic Commit Generation
```python
def generate_commit_message(changes):
    """Generate meaningful commit without user input"""
    # Analyzes changes to create semantic commit
    # Reduces decision fatigue
    
    file_groups = group_by_feature(changes)
    commit_type = detect_change_type(file_groups)
    scope = identify_scope(file_groups)
    description = summarize_changes(file_groups)
    
    return f"{commit_type}({scope}): {description}"
```

## Accessibility Features

### One-Command Operations
```bash
# Complete git workflow in one command
vespera git ship  # Commits, pushes, creates PR

# Auto-recover from any state
vespera git recover  # Finds WIP, resumes work

# Smart context switch
vespera git switch <task>  # Handles all complexity
```

### Visual Feedback
- Progress indicators for long operations
- Clear status messages
- Undo capabilities for all operations
- Recovery suggestions on errors

## Success Criteria

### Accessibility Metrics
- [ ] Git operations require single command
- [ ] Zero work loss from interruptions
- [ ] Automatic context preservation
- [ ] No git expertise required

### Technical Metrics
- [ ] Worktree management implemented
- [ ] Issue tracking integrated
- [ ] Commit automation working
- [ ] PR workflow automated

### User Experience
- [ ] Reduces git overhead by 90%
- [ ] Prevents git-related frustration
- [ ] Preserves momentum across sessions
- [ ] Works during low-capacity periods

## Testing Scenarios

### Executive Dysfunction Tests
1. **Sudden Exit**: Verify work preservation
2. **Context Switch**: Test worktree isolation
3. **Low Energy**: Validate one-command operations
4. **Confusion Recovery**: Test state recovery

### Integration Tests
- With orchestrator sessions
- With documentation automation
- With template system hooks
- Cross-platform compatibility

## Related Documents

- [Feature Implementation Index](../index.md)
- [Git Commit Organization](11-git-commit-organization.md)
- [Release Preparation](12-release-preparation.md)
- [Executive Dysfunction Philosophy](../../executive_dysfunction_design_prp.md)