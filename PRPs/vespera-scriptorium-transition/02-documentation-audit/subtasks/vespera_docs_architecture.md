# Vespera Scriptorium Documentation Architecture Design

**Created**: 2025-08-14  
**Purpose**: Define the new documentation architecture for Vespera Scriptorium  
**Status**: [DRAFT] Architecture Design

## Overview

This document defines the comprehensive documentation architecture for Vespera Scriptorium, transitioning from the cluttered existing documentation to a professional, searchable, wiki-like system that reflects the "IDE for ideas" philosophy.

## Design Philosophy

### Core Principles

1. **User-Centric Navigation**: Documentation structure follows user journeys, not internal code organization
2. **Progressive Disclosure**: Information is layered from basic concepts to advanced implementation
3. **Searchable & Discoverable**: Every piece of content is findable through multiple pathways
4. **Living Documentation**: Automated generation where possible, manual curation where necessary
5. **Vespera Identity**: Consistent branding and terminology throughout

### Executive Dysfunction Awareness

- **Clear Entry Points**: Multiple ways to access the same information
- **Context Preservation**: Related information is linked and cross-referenced
- **Gentle Learning Curves**: No overwhelming technical dumps
- **Quick Wins**: Users can accomplish something meaningful quickly

## Architecture Options Analysis

### Option 1: GitHub Pages with Jekyll (RECOMMENDED)

**Advantages:**
- Native GitHub integration
- Excellent theme support (just-the-docs)
- Built-in search and navigation
- Easy deployment and maintenance
- Version control integration

**Implementation:**
```yaml
platform: GitHub Pages
theme: just-the-docs
source: docs/
deployment: Automatic on push to main
search: Built-in with lunr.js
```

### Option 2: MkDocs with Material Theme

**Advantages:**
- Excellent Material Design implementation
- Superior navigation features
- Advanced search capabilities
- Plugin ecosystem

**Considerations:**
- Requires separate hosting setup
- More complex deployment pipeline

### Option 3: GitBook (Commercial)

**Advantages:**
- Professional appearance
- Excellent user experience
- Built-in collaboration features

**Considerations:**
- Commercial platform
- Less control over customization

## Recommended Architecture: GitHub Pages + Jekyll

### Site Configuration

```yaml
# _config.yml
title: "Vespera Scriptorium"
description: "An IDE for Ideas - Document-Centric Orchestration Platform"
url: "https://vespera-scriptorium.github.io"
theme: just-the-docs

# Site structure
nav_structure:
  - Home
  - Quick Start
  - Users
  - Developers
  - Concepts
  - Reference

# Features
search_enabled: true
heading_anchors: true
color_scheme: vespera
logo: "/assets/images/vespera-logo.png"

# Plugin configuration
plugins:
  - jekyll-feed
  - jekyll-sitemap
  - jekyll-seo-tag

# Collections for organized content
collections:
  concepts:
    output: true
    permalink: /concepts/:name/
  workflows:
    output: true
    permalink: /workflows/:name/
  examples:
    output: true
    permalink: /examples/:name/
```

## Directory Structure

```
docs/
├── _config.yml                    # Jekyll configuration
├── _layouts/                      # Custom page layouts
│   ├── default.html
│   ├── concept.html
│   └── example.html
├── _includes/                     # Reusable components
│   ├── navigation.html
│   ├── code-block.html
│   └── concept-link.html
├── assets/
│   ├── css/
│   │   └── vespera-theme.scss     # Custom Vespera styling
│   ├── js/
│   │   └── enhanced-search.js     # Enhanced search functionality
│   └── images/
│       └── vespera-logo.png       # Vespera branding
│
├── index.md                       # Home page: "Welcome to Vespera Scriptorium"
├── quick-start.md                 # 5-minute getting started
│
├── users/
│   ├── index.md                   # User documentation home
│   ├── installation/
│   │   ├── index.md              # Installation overview
│   │   ├── claude-desktop.md     # Claude Desktop setup
│   │   ├── cursor.md             # Cursor IDE setup
│   │   ├── vs-code.md            # VS Code setup
│   │   └── troubleshooting.md    # Installation issues
│   ├── first-steps/
│   │   ├── creating-tasks.md     # Your first task
│   │   ├── using-templates.md    # Working with templates
│   │   └── understanding-output.md # Reading results
│   ├── guides/
│   │   ├── task-orchestration.md # Core orchestration guide
│   │   ├── multi-agent-workflows.md # Advanced coordination
│   │   ├── integration-patterns.md # Common integration patterns
│   │   └── troubleshooting.md    # User troubleshooting
│   └── examples/
│       ├── documentation-projects/ # Real-world examples
│       ├── development-workflows/
│       └── creative-writing/
│
├── developers/
│   ├── index.md                   # Developer documentation home
│   ├── architecture/
│   │   ├── overview.md           # System architecture
│   │   ├── clean-architecture.md # Clean architecture implementation
│   │   ├── domain-driven-design.md # DDD principles
│   │   └── mcp-protocol.md       # MCP protocol integration
│   ├── api/
│   │   ├── index.md              # API overview
│   │   ├── orchestrator.md       # Orchestrator API (auto-generated)
│   │   ├── templates.md          # Template API (auto-generated)
│   │   └── maintenance.md        # Maintenance API (auto-generated)
│   ├── contributing/
│   │   ├── getting-started.md    # Setup for contributors
│   │   ├── code-standards.md     # Coding standards
│   │   ├── testing.md           # Testing guidelines
│   │   └── pull-requests.md     # PR process
│   └── extending/
│       ├── custom-specialists.md # Creating specialist types
│       ├── plugins.md           # Plugin system
│       └── integrations.md      # External integrations
│
├── concepts/
│   ├── index.md                   # Core concepts overview
│   ├── scriptorium.md            # What is a scriptorium?
│   ├── orchestration.md          # Task orchestration explained
│   ├── specialists.md            # Specialist system
│   ├── templates.md              # Template system
│   ├── artifacts.md              # Artifact management
│   └── workflows.md              # Workflow patterns
│
└── reference/
    ├── index.md                   # Reference overview
    ├── cli/
    │   ├── orchestrator.md        # CLI commands reference
    │   └── templates.md          # Template CLI
    ├── configuration/
    │   ├── mcp-settings.md       # MCP configuration
    │   ├── server-config.md      # Server configuration
    │   └── client-setup.md       # Client setup options
    ├── tools/
    │   ├── orchestrator-tools.md # Orchestrator MCP tools
    │   ├── template-tools.md     # Template MCP tools
    │   └── maintenance-tools.md  # Maintenance tools
    └── troubleshooting/
        ├── common-issues.md      # Common problems
        ├── error-codes.md        # Error code reference
        └── diagnostics.md        # Diagnostic tools
```

## Content Strategy

### Automated Content Generation

1. **API Reference**: Generated from Python docstrings using sphinx or mkdocstrings
2. **CLI Reference**: Generated from Click command definitions
3. **MCP Tools Reference**: Generated from tool definitions
4. **Configuration Reference**: Generated from configuration schemas

### Manual Content Priority

1. **Core Concepts**: Explain Vespera Scriptorium philosophy and approach
2. **Quick Start Guide**: Get users productive in under 5 minutes
3. **Integration Guides**: Real-world setup and usage patterns
4. **Architecture Documentation**: Clean architecture with visual diagrams

### Content Guidelines

#### Voice and Tone
- **Professional but Approachable**: Technical accuracy with human warmth
- **Empowering**: Focus on what users can accomplish
- **Clear and Concise**: Respect users' time and cognitive load
- **Vespera-Centric**: Use Vespera Scriptorium terminology consistently

#### Structure Standards
- **Scannable**: Use headers, lists, and callouts
- **Progressive**: Start simple, add complexity gradually
- **Linked**: Cross-reference related concepts
- **Searchable**: Use consistent terminology and keywords

## Branding and Visual Design

### Vespera Scriptorium Identity

```scss
// Vespera color palette
$vespera-primary: #2c3e50;      // Deep blue-gray
$vespera-secondary: #3498db;    // Bright blue
$vespera-accent: #e67e22;       // Warm orange
$vespera-text: #2c3e50;         // Dark text
$vespera-background: #ecf0f1;   // Light background

// Typography
$vespera-font-primary: 'Inter', sans-serif;
$vespera-font-mono: 'JetBrains Mono', monospace;
```

### Visual Elements
- **Logo**: Scriptorium-inspired design with modern tech elements
- **Icons**: Consistent icon set for navigation and concepts
- **Diagrams**: Professional system architecture visualizations
- **Screenshots**: Standardized formatting for UI examples

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create GitHub Pages repository
- [ ] Set up Jekyll with just-the-docs theme
- [ ] Implement Vespera branding
- [ ] Create core page structure
- [ ] Write essential content (home, quick start, concepts)

### Phase 2: Content Migration (Week 2)
- [ ] Set up automated API documentation generation
- [ ] Migrate high-priority content from archive
- [ ] Create user guides and examples
- [ ] Implement search optimization

### Phase 3: Polish and Enhancement (Week 3)
- [ ] Advanced navigation features
- [ ] Visual enhancements
- [ ] Content review and editing
- [ ] Performance optimization

### Phase 4: Launch and Iteration (Week 4)
- [ ] Final content review
- [ ] Launch documentation site
- [ ] Gather feedback
- [ ] Iterate based on user needs

## Technical Implementation

### Build Pipeline

```yaml
# .github/workflows/docs.yml
name: Build and Deploy Documentation
on:
  push:
    branches: [ main ]
    paths: [ 'docs/**' ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.0
      - name: Install dependencies
        run: |
          cd docs
          bundle install
      - name: Build site
        run: |
          cd docs
          bundle exec jekyll build
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/_site
```

### Search Enhancement

```javascript
// Enhanced search functionality
document.addEventListener('DOMContentLoaded', function() {
  // Add concept-aware search
  // Add "did you mean" functionality
  // Add category filtering
  // Add keyboard shortcuts
});
```

## Success Metrics

### Quantitative Metrics
- **Search Success Rate**: Users find what they're looking for
- **Page Views**: Most accessed documentation sections
- **Time on Page**: Users engage with content
- **Bounce Rate**: Users stay and explore

### Qualitative Metrics
- **User Feedback**: Surveys and GitHub issues
- **Content Completeness**: No major gaps in documentation
- **Consistency**: Uniform voice and structure throughout
- **Maintainability**: Easy to update and extend

## Migration Strategy

### Content Prioritization
1. **Core User Paths**: Installation → First Task → Common Workflows
2. **Developer Essentials**: Architecture → API → Contributing
3. **Reference Materials**: CLI → Configuration → Troubleshooting
4. **Advanced Topics**: Extensions → Integrations → Complex Workflows

### Quality Assurance
- [ ] Markdown lint compliance
- [ ] Link validation (internal and external)
- [ ] Search functionality testing
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] Accessibility compliance

## Maintenance Strategy

### Automated Maintenance
- **Link Checking**: Daily automated link validation
- **Content Freshness**: Alerts for outdated content
- **API Sync**: Automatic API documentation updates
- **Performance Monitoring**: Site speed and availability

### Manual Maintenance
- **Quarterly Content Review**: Update examples and best practices
- **User Feedback Integration**: Address common questions and issues
- **Version Updates**: Maintain compatibility with system updates
- **SEO Optimization**: Keep content discoverable

---

This architecture provides a solid foundation for professional, user-centric documentation that truly embodies the Vespera Scriptorium vision while being practical to implement and maintain.