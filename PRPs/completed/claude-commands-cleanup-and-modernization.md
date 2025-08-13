# Claude Commands Cleanup and Modernization PRP

**PRP ID**: `CLAUDE_COMMANDS_CLEANUP_2025`  
**Priority**: High  
**Status**: [PENDING]  
**Created**: 2025-08-12  
**Last Updated**: 2025-08-12  

## Overview

Comprehensive cleanup and modernization of the `.claude/commands/` directory structure, updating outdated commands with context engineering principles, removing inapplicable commands, and ensuring proper version control integration.

## Context & Background

The current `.claude/commands/` directory contains:
1. Outdated commands from the original Wirasm/PRPs-agentic-eng repository
2. Commands not applicable to this Python project (TypeScript-specific)
3. Commands that need context engineering integration
4. Misplaced files that should be in version control but aren't due to .gitignore

## Current State Analysis

### Files Currently in .claude/commands/:
```
PRPs/
├── api-contract-define.md (needs review)
├── prp-base-create.md (recently updated with context engineering)
├── prp-base-execute.md (recently updated with context engineering)
├── prp-planning-create.md (needs context engineering integration)
├── prp-spec-create.md (needs context engineering integration)
├── prp-spec-execute.md (needs context engineering integration)
├── prp-task-create.md (needs context engineering integration)
├── prp-task-execute.md (needs context engineering integration)
└── task-list-init.md (needs review)

code-quality/
├── refactor-simple.md (needs context engineering)
├── review-general.md (needs context engineering)
└── review-staged-unstaged.md (needs context engineering)

development/
├── create-pr.md (needs context engineering)
├── debug-RCA.md (needs context engineering)
├── new-dev-branch.md (needs context engineering)
├── onboarding.md (needs context engineering)
├── prime-core.md (needs context engineering)
└── smart-commit.md (needs context engineering)

git-operations/
├── conflict-resolver-general.md (needs context engineering)
├── conflict-resolver-specific.md (needs context engineering)
└── smart-resolver.md (needs context engineering)

rapid-development/experimental/ (needs full review)
└── [multiple experimental commands]
```

## Tasks

### Phase 1: Audit and Assessment

1. **Review all existing commands for applicability**
   - Assess each command's relevance to this Python MCP project
   - Identify commands that need removal vs. update
   - Document which commands are actively used

2. **Context engineering gap analysis**
   - Compare existing commands to enhanced prp-base-create.md and prp-base-execute.md
   - Identify missing context engineering principles
   - List security-first design gaps

### Phase 2: Command Updates and Integration

3. **Update PRP-related commands**
   - Integrate context engineering principles into all PRP commands
   - Add orchestrator integration checks
   - Update validation frameworks to match project structure
   - Ensure git commit enforcement

4. **Modernize development commands**
   - Update code-quality commands with project-specific tools (black, isort, pytest)
   - Integrate orchestrator health checks where relevant
   - Add security validation steps
   - Update paths and references for this project

5. **Enhance git operations commands**
   - Integrate with project-specific git workflows
   - Add orchestrator state preservation during git operations
   - Update validation commands

### Phase 3: Directory Structure Optimization

6. **Remove inapplicable commands**
   - Delete TypeScript-specific commands (already done)
   - Remove experimental commands that aren't relevant
   - Archive deprecated commands appropriately

7. **Reorganize command structure**
   - Group related commands logically
   - Create consistent naming conventions
   - Add command index/documentation

### Phase 4: Version Control Integration

8. **Update .gitignore file**
   - Remove `.claude/*` exclusion
   - Add specific exclusions for temporary files only
   - Ensure command files are version controlled
   - Add comments explaining what should/shouldn't be tracked

9. **Clean up .gitignore duplicates and inconsistencies**
   - Remove duplicate entries (multiple venv/, .db entries)
   - Organize by category with clear comments
   - Remove orphaned entries for non-existent directories

## Context Engineering Integration

All updated commands must include:

### Mandatory Context References
```yaml
- file: PRPs/ai_docs/mcp-protocol-patterns.md
  why: "MCP server implementation patterns"
  sections: ["Core Principles", "Error Handling"]

- file: PRPs/protocols/orchestrator-fix-protocol.md
  why: "Orchestrator failure recovery procedures"
  sections: ["Diagnosis", "Recovery", "Validation"]

- file: CLAUDE.md
  why: "Project-specific guidance and critical directives"
  sections: ["Critical Directives", "Commands", "Architecture"]
```

### Orchestrator Integration
All development commands must:
- Check orchestrator health before proceeding
- Use orchestrator tools for complex multi-step tasks
- Follow failure protocol if orchestrator fails
- Commit changes after successful completion

### Security-First Design
All commands must:
- Include input validation requirements
- Specify error sanitization procedures
- Reference security patterns from PRPs/ai_docs/security-patterns.md
- Include security testing steps

## Validation Framework

### Stage 1: Command Syntax Validation
```bash
# Validate all markdown files
markdownlint .claude/commands/**/*.md

# Check for broken links
find .claude/commands -name "*.md" -exec grep -l "PRPs/" {} \; | xargs -I {} sh -c 'echo "Checking {}" && grep -o "PRPs/[^)]*" "{}"'
```

### Stage 2: Context Engineering Validation
```bash
# Verify context engineering integration
python scripts/validate_command_context.py .claude/commands/

# Check orchestrator integration
grep -r "orchestrator_" .claude/commands/ || echo "Missing orchestrator integration"
```

### Stage 3: Functional Testing
```bash
# Test sample commands (non-destructive)
echo "Testing command structure and references"
python scripts/test_command_structure.py
```

## Implementation Strategy

### Priority Order:
1. **High Priority**: PRP commands (prp-planning-create.md, prp-spec-*.md, prp-task-*.md)
2. **Medium Priority**: Development workflow commands (create-pr.md, debug-RCA.md, etc.)
3. **Low Priority**: Experimental commands review and cleanup

### Context Engineering Template for Updates:

Each command should follow this structure:
```markdown
# [Command Name] with Context Engineering

## Pre-Execution Checks
- Orchestrator health check
- Required context validation

## Enhanced Context References
[List of required PRPs/ai_docs files]

## Security Considerations
[Security requirements and validation]

## Implementation
[Enhanced implementation with context engineering]

## Validation
[Multi-stage validation specific to command]

## Git Integration
[Commit requirements and procedures]
```

## Success Criteria

- [ ] All commands updated with context engineering principles
- [ ] Orchestrator integration in all development commands
- [ ] Security-first design in all commands
- [ ] .gitignore properly configured for version control
- [ ] All commands tested and validated
- [ ] Command documentation updated
- [ ] Inapplicable commands removed
- [ ] No broken references or missing dependencies

## Files to be Modified

### Direct Updates:
- `.claude/commands/PRPs/prp-planning-create.md`
- `.claude/commands/PRPs/prp-spec-create.md`
- `.claude/commands/PRPs/prp-spec-execute.md`
- `.claude/commands/PRPs/prp-task-create.md`
- `.claude/commands/PRPs/prp-task-execute.md`
- `.claude/commands/code-quality/*.md`
- `.claude/commands/development/*.md`
- `.claude/commands/git-operations/*.md`
- `.gitignore`

### Supporting Scripts to Create:
- `scripts/validate_command_context.py`
- `scripts/test_command_structure.py`
- `scripts/command_updater.py`

## Risk Mitigation

- **Backup existing commands** before modifications
- **Test commands incrementally** rather than batch updates
- **Maintain backward compatibility** where possible
- **Document all changes** for easy rollback if needed

## Context Engineering Score Target: 9/10
## Security Integration Score Target: 9/10
## Overall Success Confidence: 8/10

This comprehensive cleanup will modernize the command structure, integrate context engineering principles, and ensure proper version control of the development workflow tools.