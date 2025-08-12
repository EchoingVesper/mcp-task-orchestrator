# Create Pull Request with Context Engineering

Create a well-structured pull request with proper description, context engineering validation, and security considerations.

## PR Title (if provided)

$ARGUMENTS

## Pre-Execution Orchestrator Check

**MANDATORY FIRST STEP:**
```bash
# Verify orchestrator connection and health
claude mcp list | grep task-orchestrator || (echo "ORCHESTRATOR NOT CONNECTED - Fixing..." && claude mcp restart task-orchestrator)

# Check orchestrator health before proceeding
# Use orchestrator_health_check if available
```

If orchestrator fails, STOP and spawn fix agent per CLAUDE.md protocol.

## Enhanced Context References

**Load and reference project-specific documentation:**

```yaml
required_context:
  - file: CLAUDE.md
    why: "Project-specific git workflow and commit requirements"
    sections: ["Commands", "Critical Directives"]

  - file: PRPs/ai_docs/cc_github_actions.md
    why: "GitHub integration patterns and workflows"
    sections: ["PR Best Practices", "CI Integration"]

  - file: PRPs/ai_docs/security-patterns.md
    why: "Security considerations for code changes"
    sections: ["Secure Development", "Code Review Security"]
```

## Security Considerations

Before creating PR, ensure:
- **No secrets or keys** committed to repository
- **Security-sensitive changes** properly reviewed
- **Input validation** for any new endpoints
- **Dependencies** security-scanned if updated
- **Error handling** doesn't leak sensitive information

## Process

1. **Prepare Branch**

   ```bash
   # Check current branch
   git branch --show-current
   
   # Ensure we're not on main
   # If on main, create a feature branch
   ```

2. **Review Changes**

   ```bash
   # See what will be included
   git status
   git diff main...HEAD
   ```

3. **Enhanced Code Quality & Security Validation**

   ```bash
   # Project-specific code formatting and linting
   black mcp_task_orchestrator/
   isort mcp_task_orchestrator/
   
   # Security scanning
   bandit -r mcp_task_orchestrator/ || echo "Security issues found - review required"
   safety check || echo "Dependency security issues found - review required"
   
   # Run project tests
   pytest -v
   
   # Type checking if configured
   mypy mcp_task_orchestrator/ || echo "Type checking not configured or failed"
   ```

4. **Create Commits with Enhanced Messages**
   - Stage relevant files with security review
   - Create logical, atomic commits if not already done
   - **CRITICAL**: Follow CLAUDE.md commit requirements
   - Write clear commit messages following conventional commits:
     - `feat:` for new features
     - `fix:` for bug fixes  
     - `docs:` for documentation
     - `test:` for tests
     - `refactor:` for refactoring
     - Include orchestrator task ID if applicable

5. **Push to Remote**

   ```bash
   git push -u origin HEAD
   ```

6. **Create Enhanced PR**

   ```bash
   gh pr create --title "$ARGUMENTS" --body "$(cat <<'EOF'
   ## Summary
   [Brief description of what this PR does]
   
   ## Changes
   - [List key changes with security implications]
   - [Be specific about implementation details]
   - [Note any architectural changes]
   
   ## Type of Change
   - [ ] Bug fix (non-breaking change which fixes an issue)
   - [ ] New feature (non-breaking change which adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
   - [ ] Documentation update
   - [ ] Security improvement
   - [ ] Performance optimization
   
   ## Enhanced Testing & Validation
   - [ ] All tests pass locally (`pytest -v`)
   - [ ] Code formatting applied (`black`, `isort`)
   - [ ] Security scanning passed (`bandit`, `safety`)
   - [ ] Type checking passed (if configured)
   - [ ] Added new tests for changes
   - [ ] Manual testing completed
   - [ ] Integration testing with MCP protocol
   
   ## Security Review
   - [ ] No secrets or credentials committed
   - [ ] Input validation implemented where applicable
   - [ ] Error handling doesn't leak sensitive information
   - [ ] Dependencies security-scanned
   - [ ] Authentication/authorization unchanged or properly updated
   
   ## Code Quality Checklist
   - [ ] Code follows Clean Architecture principles
   - [ ] Self-reviewed with security focus
   - [ ] Updated documentation (including docstrings)
   - [ ] No debug code or console outputs
   - [ ] Follows project conventions in CLAUDE.md
   - [ ] Database migrations included if needed
   
   ## Context Engineering Integration
   - [ ] Referenced relevant PRPs/ai_docs/ documentation
   - [ ] Orchestrator integration tested if applicable
   - [ ] Context engineering principles applied
   
   ## Screenshots/Outputs (if applicable)
   [Add screenshots for UI changes or command outputs for CLI changes]
   
   ## Related Issues/Tasks
   - Closes #[issue number]
   - Related to orchestrator task: [task ID if applicable]
   
   ## Additional Context
   [Any extra information reviewers should know, including security considerations]
   
   🤖 Generated with [Claude Code](https://claude.ai/code)
   
   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

7. **Enhanced Post-Creation**
   - Add labels with security focus: `gh pr edit --add-label "feature,needs-review,security-reviewed"`
   - Request reviewers including security-focused reviewers if available
   - Link to related issues and orchestrator tasks
   - **CRITICAL**: Follow CLAUDE.md commit enforcement after PR creation

## Validation Framework

### Pre-PR Validation Checklist
- [ ] **Orchestrator health** verified
- [ ] **Security scanning** completed without critical issues
- [ ] **Code formatting** applied (`black`, `isort`)
- [ ] **Tests passing** locally
- [ ] **Enhanced context** reviewed from PRPs/ai_docs/

### Post-PR Creation
- [ ] **PR template** fully completed with security sections
- [ ] **Appropriate labels** applied
- [ ] **Related issues** linked
- [ ] **Orchestrator task ID** referenced if applicable

## Enhanced Best Practices

**Security-First PR Creation:**
- Always run security scans before creating PR
- Include security impact assessment in description
- Reference security patterns from PRPs/ai_docs/security-patterns.md
- Ensure no sensitive information in commit history

**Context Engineering Integration:**
- Reference relevant enhanced documentation
- Use orchestrator tools for complex change coordination
- Follow validation framework for consistency
- Apply context engineering principles from guide

**Project-Specific Requirements:**
- Use project tools (`black`, `isort`, `pytest`)
- Follow Clean Architecture principles
- Integrate with MCP protocol patterns
- Maintain orchestrator compatibility

Remember: Enhanced PRs with security focus and context engineering create better code reviews and safer deployments.
