# Subtask: Custom Documentation Specialist Roles Creation

**Task ID**: `doc-audit-03`  
**Parent**: Documentation Audit & Remediation  
**Type**: Configuration & Setup  
**Priority**: HIGH - Required for multi-agent coordination  
**Estimated Duration**: 2 hours

## Objective

Create specialized orchestrator roles for documentation audit agents in `.task_orchestrator/roles/`.

## Roles to Create

### 1. Review Specialist

```json
{
  "role_id": "review_specialist",
  "name": "Documentation Review Specialist",
  "purpose": "Examine file purpose, relevance, and appropriate placement",
  "capabilities": [
    "content_analysis",
    "purpose_identification", 
    "placement_assessment"
  ],
  "context": "Understands project structure and documentation taxonomy",
  "tools": ["Read", "Grep", "orchestrator_complete_task"],
  "decision_criteria": {
    "keep": "Essential permanent documentation",
    "archive": "Task-specific or outdated content",
    "update": "Needs modernization but relevant"
  }
}
```

### 2. Content Review Specialist

```json
{
  "role_id": "content_review_specialist",
  "name": "Code-Documentation Alignment Specialist",
  "purpose": "Verify code-documentation alignment and content accuracy",
  "capabilities": [
    "code_analysis",
    "documentation_verification",
    "accuracy_assessment"
  ],
  "context": "Deep understanding of Clean Architecture implementation",
  "tools": ["Read", "Grep", "orchestrator_execute_task"],
  "validation_checks": [
    "Code examples match current implementation",
    "API documentation matches actual APIs",
    "Architecture descriptions align with code"
  ]
}
```

### 3. Markdown Fix Specialist

```json
{
  "role_id": "markdown_fix_specialist",
  "name": "Markdown Corruption Remediation Specialist",
  "purpose": "Fix markdown corruption and markdownlint violations",
  "capabilities": [
    "markdown_parsing",
    "syntax_correction",
    "validation_testing"
  ],
  "context": "Expert in markdown standards and automated validation",
  "tools": ["Edit", "MultiEdit", "Bash:markdownlint"],
  "corruption_patterns": [
    "Extra line breaks at start",
    "Heading splits (#\\n# Heading)",
    "Code fence corruption (text\\npython)",
    "Spurious text\\n insertions"
  ]
}
```

### 4. Organization Specialist

```json
{
  "role_id": "organization_specialist",
  "name": "Documentation Organization Specialist",
  "purpose": "Restructure and organize files into appropriate locations",
  "capabilities": [
    "taxonomy_design",
    "file_organization",
    "structure_optimization"
  ],
  "context": "Information architecture and user needs expert",
  "tools": ["Bash:mv", "Write", "orchestrator_complete_task"],
  "organization_rules": [
    "Eliminate nested identical folders",
    "Separate users/ vs developers/",
    "Archive task-tracking documents",
    "Follow docs-as-code methodology"
  ]
}
```

### 5. Inventory Specialist

```json
{
  "role_id": "inventory_specialist",
  "name": "Documentation Inventory Specialist",
  "purpose": "Catalog and track all documentation files systematically",
  "capabilities": [
    "file_discovery",
    "metadata_extraction",
    "progress_tracking"
  ],
  "context": "Comprehensive project documentation scope understanding",
  "tools": ["LS", "Glob", "Write"],
  "tracking_data": [
    "file_path",
    "size",
    "last_modified",
    "corruption_score",
    "priority_rank"
  ]
}
```

## Implementation Steps

### Step 1: Create Roles Directory

```bash
mkdir -p .task_orchestrator/roles/
```

### Step 2: Generate Role Files

For each role above:
1. Save as `.task_orchestrator/roles/{role_id}.json`
2. Validate JSON structure
3. Test role loading in orchestrator

### Step 3: Integration Testing

```python
# Test role assignment
from mcp_task_orchestrator import RoleManager

role_manager = RoleManager()
for role_id in ['review_specialist', 'content_review_specialist', 
                'markdown_fix_specialist', 'organization_specialist',
                'inventory_specialist']:
    role = role_manager.load_role(role_id)
    assert role is not None
```

## Success Criteria

- [ ] All 5 specialist roles created
- [ ] JSON files valid and complete
- [ ] Roles directory properly structured
- [ ] Integration with orchestrator verified
- [ ] Role context includes external best practices

## Agent Instructions

```yaml
agent: configuration_specialist
location: .task_orchestrator/roles/
format: JSON with full specialist definitions
validation: Test each role loads successfully
```