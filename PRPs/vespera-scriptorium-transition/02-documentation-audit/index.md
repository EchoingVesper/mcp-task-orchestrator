# Priority 2: Comprehensive Documentation Audit & Remediation

**Parent Task ID**: `task_65480`  
**Priority**: Critical - Professional Impact  
**Status**: [IN-PROGRESS]  
**Estimated Duration**: 5-7 days with agent swarm  
**Specialist Type**: Documentation Coordinator

## Strategic Decision: Complete Documentation Reset

Given the massive clutter and corruption in the documentation, we will:

1. **Archive EVERYTHING** in `docs/` (except existing archives)
2. **Start fresh** with Vespera Scriptorium branding
3. **Implement wiki-like system** (GitHub Pages or MkDocs)
4. **Generate from code** where possible

## Documentation Wiki System Options

### Option 1: GitHub Pages with Jekyll (Recommended)

```yaml
github_pages_setup:
  repository: vespera-scriptorium.github.io
  source: docs/
  theme: just-the-docs  # Professional documentation theme
  features:
    - automatic_navigation: true
    - search: true
    - versioning: true
    - code_highlighting: true
  
  structure:
    - _config.yml  # Jekyll configuration
    - index.md     # Home page
    - users/       # User documentation
    - developers/  # Developer documentation
    - api/         # API reference (auto-generated)
```

### Option 2: MkDocs with Material Theme

```yaml
mkdocs_setup:
  config_file: mkdocs.yml
  theme: material
  features:
    - navigation.instant  # SPA-like navigation
    - navigation.tracking # URL tracking
    - search.suggest     # Search suggestions
    - content.code.copy  # Copy code buttons
  
  plugins:
    - search
    - gen-files  # Generate files from code
    - mkdocstrings  # Auto API docs from docstrings
```

## Phase 1: Complete Archive Operation

### Task 1.1: Archive Everything

```yaml
action: ARCHIVE_ALL_DOCS
location: docs/archives/pre-vespera-legacy/
specialist: organization_specialist
steps:
  - Create archive directory with timestamp
  - Move ALL non-archive content to archive
  - Preserve directory structure for reference
  - Create archive index with descriptions
```

### Task 1.2: Document Inventory

```yaml
action: CREATE_INVENTORY
output: inventory/complete_documentation_audit.json
specialist: inventory_specialist
data_collected:
  - file_path
  - file_size
  - last_modified
  - corruption_level
  - relevance_score
  - recommended_action
```

## Phase 2: Fresh Documentation Structure

### New Vespera Scriptorium Documentation

```directory
docs/
├── _config.yml                 # Jekyll/MkDocs configuration
├── index.md                    # Home: "Vespera Scriptorium"
├── quickstart.md              # 5-minute setup guide
│
├── users/
│   ├── index.md               # User guide home
│   ├── installation.md        # Installation guide
│   ├── first-task.md         # Creating your first task
│   ├── templates.md          # Using templates
│   └── workflows/            # Common workflow patterns
│
├── developers/
│   ├── index.md              # Developer guide home
│   ├── architecture.md       # Clean architecture overview
│   ├── contributing.md       # Contribution guidelines
│   ├── api/                  # API documentation (auto-generated)
│   └── extending/           # Extension guides
│
├── concepts/
│   ├── index.md             # Core concepts
│   ├── scriptorium.md       # What is a scriptorium?
│   ├── orchestration.md     # Task orchestration
│   └── agents.md           # Multi-agent coordination
│
└── reference/
    ├── cli.md              # CLI commands
    ├── configuration.md    # Configuration options
    ├── mcp-tools.md       # MCP tool reference
    └── troubleshooting.md # Common issues
```

## Phase 3: Content Generation Strategy

### Auto-Generated Documentation

```yaml
auto_generation_sources:
  api_reference:
    source: Python docstrings
    tool: mkdocstrings or sphinx
    output: docs/developers/api/
    
  cli_reference:
    source: Click commands
    tool: click-autodoc
    output: docs/reference/cli.md
    
  mcp_tools:
    source: Tool definitions
    tool: Custom generator
    output: docs/reference/mcp-tools.md
    
  configuration:
    source: Config schemas
    tool: JSON Schema doc generator
    output: docs/reference/configuration.md
```

### Manual Priority Content

1. **Quickstart Guide** - Get users running in 5 minutes
2. **Core Concepts** - Explain Vespera Scriptorium philosophy
3. **Architecture Overview** - Clean architecture with diagrams
4. **Common Workflows** - Real-world usage patterns

## Phase 4: Multi-Agent Execution Plan

### Agent Swarm Coordination

```yaml
documentation_agent_swarm:
  coordinator:
    role: "Documentation Coordinator"
    manages: 400+ file agents
    
  specialist_agents:
    archive_agent:
      count: 1
      role: "Archive all existing documentation"
      
    inventory_agent:
      count: 1
      role: "Create comprehensive inventory"
      
    content_generator_agents:
      count: 10
      role: "Generate new documentation sections"
      parallel: true
      
    api_doc_agent:
      count: 1
      role: "Generate API documentation from code"
      
    validation_agents:
      count: 5
      role: "Validate markdown and content quality"
```

### Per-File Task Pattern

For each existing documentation file:

```yaml
per_file_tasks:
  - analyze_purpose: Determine if needed in new structure
  - extract_value: Pull any valuable content
  - archive: Move to legacy archive
  - track: Record in inventory with notes
```

## Phase 5: Wiki System Implementation

### GitHub Pages Setup Tasks

```bash
# Create GitHub Pages repository
gh repo create vespera-scriptorium.github.io --public

# Configure Jekyll
bundle init
bundle add jekyll just-the-docs

# Create configuration
cat > _config.yml << EOF
title: Vespera Scriptorium
description: An IDE for Ideas - Document-Centric Orchestration Platform
theme: just-the-docs
url: https://vespera-scriptorium.github.io
EOF

# Enable GitHub Pages
gh api repos/vespera-scriptorium/vespera-scriptorium.github.io/pages \
  --method POST \
  --field source='{"branch":"main","path":"/"}'
```

## Success Criteria

- [ ] All existing docs archived with index
- [ ] Complete inventory generated
- [ ] Fresh documentation structure created
- [ ] Wiki system (GitHub Pages/MkDocs) operational
- [ ] Core documentation written
- [ ] API docs auto-generated
- [ ] Search functionality working
- [ ] Zero markdown violations
- [ ] Professional appearance
- [ ] Vespera Scriptorium branding throughout

## Tracking Files

- `tracking/checklist.md` - Task completion status
- `tracking/inventory.json` - Complete file inventory
- `tracking/archive-manifest.md` - What was archived where
- `tracking/new-docs-status.md` - New documentation progress

## Related Documents

- [Main Coordination](../00-main-coordination/index.md)
- [Template System](../03-template-system/index.md) - For documentation templates
- [Original Documentation Audit PRP](../../[IN-PROGRESS]comprehensive-documentation-audit-and-remediation-meta-prp.md)

---

*Navigate back to [Main Coordination](../00-main-coordination/index.md) or proceed to [Template System](../03-template-system/index.md)*
