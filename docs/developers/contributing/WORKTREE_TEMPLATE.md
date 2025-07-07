

# Git Worktree Setup Template

This template provides a step-by-step guide for creating and managing new git worktrees for parallel development.

#

# 🌳 Creating a New Worktree

#

## Step 1: Create the Worktree

```bash

# From the main repository directory

cd /mnt/e/My\ Work/Programming/MCP\ Servers/mcp-task-orchestrator

# Create new worktree with feature branch

git worktree add worktrees/[FEATURE-NAME] -b feature/[FEATURE-NAME]

# Examples:

git worktree add worktrees/server-reboot -b feature/in-context-server-reboot
git worktree add worktrees/api-enhancement -b feature/api-enhancement
git worktree add worktrees/performance-optimization -b feature/performance-optimization

```text

#

## Step 2: Initialize Development Environment

```text
bash

# Enter the new worktree

cd worktrees/[FEATURE-NAME]

# Start Claude Code in the worktree

claude

# Verify worktree status

git worktree list
git status

```text

#

## Step 3: Set Up Worktree Documentation

Create or update the worktree-specific CLAUDE.md:

```text
markdown

# [Feature Name] - Claude Code Development Guide

<worktree_context>
**Worktree Purpose**: [Brief description of the feature]
**Branch**: feature/[FEATURE-NAME]
**Task ID**: [If applicable]
**Priority**: [HIGH/MEDIUM/LOW]
**Timeline**: [Estimated completion time]
</worktree_context>

<worktree_focus>

- [Key objective 1]

- [Key objective 2] 

- [Key objective 3]

- [Key objective 4]
</worktree_focus>

#

# Quick Start Commands

```bash

# [Primary commands for this feature]

# Example: Test the feature

python test_[feature].py

# Example: Run specific diagnostics

python scripts/diagnostics/check_[feature].py

```text

[Include main CLAUDE.md content here with worktree-specific modifications]

```text

#

# 🔄 Worktree Development Workflow

#

## Daily Development

```text
text
bash

# Start development session

cd worktrees/[FEATURE-NAME]
claude

# Regular git operations (work exactly the same)

git status
git add .
git commit -m "feat: implement [specific change]"
git push -u origin feature/[FEATURE-NAME]

```text

#

## Creating Pull Requests

```text
bash

# From the worktree directory

gh pr create --title "feat: [Feature Name]" --body "

#
# Summary

[Feature description]

#

# Key Changes

- [Change 1]

- [Change 2]

- [Change 3]

#

# Test Plan

- [x] [Test 1]

- [x] [Test 2]

- [ ] [Test 3]

🤖 Generated with [Claude Code](https://claude.ai/code)"

```text

#

## Staying Updated

```text
bash

# Pull latest changes from main (if needed)

git fetch origin
git merge origin/main

# Or rebase if preferred

git rebase origin/main

```text

#

# 📋 Worktree Management

#

## Viewing All Worktrees

```text
bash

# From anywhere in the repository

git worktree list

# View branches across all worktrees

git branch -a

# See commits from all worktrees

git log --oneline --all --graph

```text

#

## Working with Multiple Worktrees

```text
bash

# Terminal 1: Database migration work

cd worktrees/db-migration && claude

# Terminal 2: Server reboot work (simultaneously!)

cd worktrees/server-reboot && claude

# Terminal 3: API enhancement work

cd worktrees/api-enhancement && claude

```text

#

## Communication Between Worktrees

- **File Changes**: Each worktree has independent file states

- **Git History**: All worktrees share the same git repository

- **Branches**: Each worktree typically works on a different branch

- **Integration**: Merge conflicts resolved when PRs are merged to main

#

# 🧹 Cleanup After Feature Completion

#

## After PR is Merged

```text
bash

# From main repository

cd /mnt/e/My\ Work/Programming/MCP\ Servers/mcp-task-orchestrator

# Update main branch

git checkout main
git pull origin main

# Remove the completed worktree

git worktree remove worktrees/[FEATURE-NAME]

# Delete the local feature branch

git branch -d feature/[FEATURE-NAME]

# Clean up remote tracking branches

git remote prune origin

```text

#

## Verification

```text
bash

# Verify worktree is removed

git worktree list

# Verify branch cleanup

git branch -a

```text

#

# 🎯 Best Practices for Worktrees

#

## Naming Conventions

- **Worktree Directory**: `worktrees/[feature-name]`

- **Branch Name**: `feature/[feature-name]`

- **Use kebab-case**: `db-migration`, `server-reboot`, `api-enhancement`

#

## File Organization

```text

worktrees/
├── db-migration/           

# Database migration feature

├── server-reboot/          

# Server reboot feature

├── api-enhancement/        

# API enhancement feature

└── performance-opt/        

# Performance optimization feature

```text

#

## Documentation Standards

- Each worktree should have clear purpose documentation

- Update CLAUDE.md with worktree-specific context

- Document feature progress and status

- Include quick start commands for the feature

#

## Git Workflow

- Commit early and often within each worktree

- Use descriptive commit messages with conventional commit format

- Push feature branches regularly for backup

- Create PRs when features are ready for review

#

## Communication

- Document active worktrees in team communications

- Include worktree status in status updates

- Coordinate integration testing across features

- Share worktree creation/removal in team channels

#

# 🔧 Troubleshooting

#

## Common Issues

#

### Worktree Won't Remove

```text
bash

# If worktree has uncommitted changes

cd worktrees/[FEATURE-NAME]
git status
git stash  

# or commit changes

# Then remove

cd ..
git worktree remove worktrees/[FEATURE-NAME]

```text

#

### Branch Conflicts

```text
bash

# If branch already exists

git worktree add worktrees/[FEATURE-NAME] -b feature/[FEATURE-NAME]-v2

# Or checkout existing branch

git worktree add worktrees/[FEATURE-NAME] feature/existing-branch

```text

#

### Viewing Worktree Status

```text
bash

# Check all worktree health

git worktree list
git worktree prune  

# Clean up stale references

```text

---

#

# 📝 Template Checklist

When creating a new worktree:

- [ ] Create worktree with descriptive name

- [ ] Create feature branch with matching name  

- [ ] Set up worktree-specific CLAUDE.md

- [ ] Document feature purpose and objectives

- [ ] Test basic git operations in worktree

- [ ] Add worktree to active development documentation

- [ ] Plan integration and testing approach

- [ ] Set up appropriate development environment

This template ensures consistent worktree creation and management across the project.
