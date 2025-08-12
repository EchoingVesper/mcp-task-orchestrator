# Fix Markdown in v2.0-release-meta-prp Files

Fix all markdown linting errors in the v2.0-release-meta-prp directory files.

## Task

Apply surgical fixes to markdown formatting issues in v2.0-release-meta-prp files:

1. Fix heading splits (`#\n#` → `##`)
2. Fix code block closings (`\`\`\`text` → `\`\`\``)
3. Fix code block languages (`\`\`\`text\nyaml` → `\`\`\`yaml`)
4. Add proper spacing around headings
5. Fix list numbering

## Files to Process

```bash
# Main coordinator
PRPs/v2.0-release-meta-prp/meta-coordination-orchestrator.md

# Phase 1-4 files (01-12)
PRPs/v2.0-release-meta-prp/01-documentation-automation-spec-orchestrator.md
PRPs/v2.0-release-meta-prp/02-git-integration-task-orchestrator.md
PRPs/v2.0-release-meta-prp/03-health-monitoring-spec-orchestrator.md
PRPs/v2.0-release-meta-prp/04-smart-routing-task-orchestrator.md
PRPs/v2.0-release-meta-prp/05-template-library-spec-orchestrator.md
PRPs/v2.0-release-meta-prp/06-testing-automation-spec-orchestrator.md
PRPs/v2.0-release-meta-prp/07-integration-testing-task-orchestrator.md
PRPs/v2.0-release-meta-prp/09-documentation-update-task-orchestrator.md
PRPs/v2.0-release-meta-prp/10-repository-cleanup-task-orchestrator.md
PRPs/v2.0-release-meta-prp/11-git-commit-organization-task-orchestrator.md
PRPs/v2.0-release-meta-prp/12-release-preparation-task-orchestrator.md
```

## Common Patterns to Fix

```python
# Pattern fixes
patterns = [
    # Fix heading splits
    (r'#\n#', '##'),
    (r'#\n\n#', '##'),
    
    # Fix code block endings
    (r'```text\n', '```\n'),
    (r'```bash\n', '```\n'),
    
    # Fix malformed code blocks
    (r'```text\nyaml', '```yaml'),
    (r'```text\nmermaid', '```mermaid'),
    
    # Add spacing around headings (if missing)
    (r'([^\n])\n#', r'\1\n\n#'),
    (r'#([^\n]+)\n([^\n#])', r'#\1\n\n\2'),
]
```

## Preserve Content

CRITICAL: Only fix formatting, never change actual content or meaning!