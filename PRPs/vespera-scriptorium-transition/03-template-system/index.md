# Priority 3: Template System with Agent Hooks

**Parent Task ID**: `task_65480`  
**Priority**: Foundation for Automation  
**Status**: [PLANNED]  
**Estimated Duration**: 7 days  
**Specialist Type**: Template Architect

## Vision: Templates as Automation Blueprints

Templates in Vespera Scriptorium are not just task structures - they're complete automation blueprints with:
- **Pre-hooks**: Actions before task execution (branch creation, environment setup)
- **Phase hooks**: Actions during each phase (validation, testing)
- **Post-hooks**: Actions after completion (commit, push, deploy)
- **Agent spawning**: Automatic specialist agent assignment
- **Context loading**: Automatic document association

## Core Template Features

### 1. Hook System Architecture

```yaml
template_hook_system:
  hook_types:
    pre_execution:
      - name: "github_branch"
      - trigger: "before_task_start"
      - agent: "git_integration_agent"
      - actions: ["create_branch", "setup_pr_draft"]
      
    phase_transition:
      - name: "validation"
      - trigger: "after_phase_complete"
      - agent: "validation_agent"
      - actions: ["run_tests", "check_quality"]
      
    post_execution:
      - name: "git_commit"
      - trigger: "after_task_complete"
      - agent: "git_integration_agent"
      - actions: ["commit_changes", "push_branch", "create_pr"]
      
    error_handling:
      - name: "rollback"
      - trigger: "on_error"
      - agent: "recovery_agent"
      - actions: ["restore_state", "notify_user"]
```

### 2. Document Association System

```yaml
document_context_system:
  automatic_loading:
    on_task_start:
      - load_associated_documents: true
      - inject_into_context: true
      - track_modifications: true
      
  document_types:
    specifications:
      - pattern: "PRPs/*.md"
      - role: "requirements"
      
    architecture:
      - pattern: "docs/architecture/*.md"
      - role: "design_guidance"
      
    tests:
      - pattern: "tests/*_test.py"
      - role: "validation_reference"
      
    examples:
      - pattern: "examples/*.py"
      - role: "implementation_patterns"
```

## Template Categories

### 1. Feature Implementation Template

```json5
{
  "template_id": "feature_implementation",
  "name": "Feature Implementation with Full Automation",
  "description": "Complete feature development from research to deployment",
  
  "hooks": {
    "pre": [
      {
        "id": "create_feature_branch",
        "agent": "github_workflow_agent",
        "action": "create_branch",
        "params": {
          "branch_name": "feature/${task_name}",
          "from": "main"
        }
      }
    ],
    
    "post": [
      {
        "id": "commit_and_pr",
        "agent": "git_integration_agent",
        "action": "complete_pr_workflow",
        "params": {
          "commit_message": "feat: ${task_name}",
          "pr_template": "feature_pr",
          "auto_merge": false
        }
      }
    ]
  },
  
  "phases": [
    {
      "name": "research",
      "agent": "research_specialist",
      "duration": "2h",
      "context": ["existing_code", "similar_features"],
      "deliverables": ["research_summary", "implementation_plan"]
    },
    {
      "name": "implementation",
      "agent": "implementation_specialist",
      "duration": "4h",
      "context": ["architecture_docs", "api_specs"],
      "deliverables": ["code", "unit_tests"],
      "hooks": {
        "post": [
          {
            "id": "run_tests",
            "agent": "test_runner",
            "action": "pytest",
            "fail_on_error": true
          }
        ]
      }
    },
    {
      "name": "documentation",
      "parallel_agents": [
        {
          "agent": "dev_doc_specialist",
          "task": "Update developer documentation",
          "context": ["code_changes", "api_changes"]
        },
        {
          "agent": "user_doc_specialist",
          "task": "Update user documentation",
          "context": ["feature_description", "usage_examples"]
        }
      ],
      "auto_commit": true
    }
  ],
  
  "associated_documents": [
    "docs/architecture/clean-architecture.md",
    "PRPs/coding-standards.md",
    "docs/api/guidelines.md"
  ]
}
```

### 2. Bug Fix Template

```json5
{
  "template_id": "bug_fix",
  "name": "Bug Fix with Regression Prevention",
  
  "hooks": {
    "pre": [
      {
        "id": "create_bugfix_branch",
        "agent": "github_workflow_agent",
        "action": "create_branch",
        "params": {
          "branch_name": "fix/${issue_number}",
          "link_issue": true
        }
      }
    ]
  },
  
  "phases": [
    {
      "name": "reproduce",
      "agent": "test_specialist",
      "task": "Create failing test that reproduces the bug",
      "deliverables": ["failing_test"]
    },
    {
      "name": "fix",
      "agent": "bug_fix_specialist",
      "task": "Implement minimal fix",
      "validation": "failing_test_passes"
    },
    {
      "name": "regression_prevention",
      "agent": "test_specialist",
      "task": "Add comprehensive test coverage",
      "deliverables": ["regression_tests"]
    }
  ]
}
```

### 3. Documentation Update Template

```json5
{
  "template_id": "documentation_update",
  "name": "Documentation Update with Auto-Generation",
  
  "phases": [
    {
      "name": "analyze",
      "agent": "doc_analysis_specialist",
      "task": "Analyze code changes and identify doc impacts"
    },
    {
      "name": "generate",
      "parallel_agents": [
        {
          "agent": "api_doc_generator",
          "task": "Generate API docs from docstrings",
          "tool": "mkdocstrings"
        },
        {
          "agent": "cli_doc_generator",
          "task": "Generate CLI docs from commands",
          "tool": "click-autodoc"
        }
      ]
    },
    {
      "name": "review",
      "agent": "doc_review_specialist",
      "task": "Review and enhance generated docs"
    }
  ],
  
  "hooks": {
    "post": [
      {
        "id": "deploy_docs",
        "agent": "deployment_agent",
        "action": "update_github_pages"
      }
    ]
  }
}
```

## Implementation Plan

### Phase 1: Core Hook System (Days 1-2)

```yaml
tasks:
  - design_hook_interface:
      description: "Define hook contract and lifecycle"
      deliverables: ["hook_interface.py", "hook_lifecycle.md"]
      
  - implement_hook_executor:
      description: "Build hook execution engine"
      deliverables: ["hook_executor.py", "tests/test_hooks.py"]
      
  - create_agent_spawner:
      description: "Agent spawning from hooks"
      deliverables: ["agent_spawner.py", "agent_context.py"]
```

### Phase 2: Document Association (Days 3-4)

```yaml
tasks:
  - design_association_schema:
      description: "Schema for task-document relationships"
      deliverables: ["document_schema.sql", "association_model.py"]
      
  - implement_auto_loader:
      description: "Automatic document loading system"
      deliverables: ["document_loader.py", "context_injector.py"]
      
  - create_tracking_system:
      description: "Track document modifications"
      deliverables: ["document_tracker.py", "modification_log.py"]
```

### Phase 3: Template Engine (Days 5-6)

```yaml
tasks:
  - build_template_parser:
      description: "JSON5 template parsing and validation"
      deliverables: ["template_parser.py", "template_validator.py"]
      
  - implement_template_executor:
      description: "Execute templates with hooks"
      deliverables: ["template_executor.py", "execution_context.py"]
      
  - create_template_library:
      description: "Built-in template library"
      deliverables: ["templates/*.json5", "template_catalog.md"]
```

### Phase 4: Integration & Testing (Day 7)

```yaml
tasks:
  - integrate_with_orchestrator:
      description: "Full orchestrator integration"
      deliverables: ["orchestrator_integration.py"]
      
  - comprehensive_testing:
      description: "End-to-end template execution tests"
      deliverables: ["tests/test_templates_e2e.py"]
      
  - documentation:
      description: "Template system documentation"
      deliverables: ["docs/templates/guide.md", "docs/templates/api.md"]
```

## Template Library Structure

```directory
.task_orchestrator/
├── templates/
│   ├── builtin/           # Built-in templates
│   │   ├── feature.json5
│   │   ├── bugfix.json5
│   │   ├── documentation.json5
│   │   ├── refactor.json5
│   │   └── release.json5
│   │
│   ├── project/          # Project-specific templates
│   │   └── custom.json5
│   │
│   └── shared/           # Shared team templates
│       └── team.json5
│
├── hooks/               # Hook implementations
│   ├── git_hooks.py
│   ├── test_hooks.py
│   └── doc_hooks.py
│
└── contexts/           # Document contexts
    ├── associations.db
    └── tracked_docs.json
```

## Success Criteria

- [ ] Hook system fully functional
- [ ] 10+ built-in templates created
- [ ] Document auto-loading working
- [ ] Agent spawning from templates
- [ ] GitHub integration via hooks
- [ ] Test automation via hooks
- [ ] Documentation auto-update
- [ ] Template validation system
- [ ] Template catalog/browser
- [ ] Performance < 100ms overhead

## Example Usage

```python
# Using a template programmatically
from mcp_task_orchestrator import TemplateExecutor

executor = TemplateExecutor()

# Execute feature template
result = await executor.execute_template(
    template_id="feature_implementation",
    parameters={
        "task_name": "user-authentication",
        "description": "Implement OAuth2 authentication",
        "priority": "high"
    },
    context={
        "issue_number": "123",
        "assigned_to": "team-auth"
    }
)

# The template will:
# 1. Create feature branch
# 2. Spawn research agent
# 3. Spawn implementation agent
# 4. Run tests automatically
# 5. Update documentation
# 6. Commit and create PR
```

## Related Documents

- [Main Coordination](../00-main-coordination/index.md)
- [Feature Implementation](../04-feature-implementation/index.md)
- [Template Library Spec](../../v2.0-release-meta-prp/05-[PENDING]-template-library-spec-orchestrator.md)

---

*Navigate back to [Main Coordination](../00-main-coordination/index.md) or proceed to [Feature Implementation](../04-feature-implementation/index.md)*
