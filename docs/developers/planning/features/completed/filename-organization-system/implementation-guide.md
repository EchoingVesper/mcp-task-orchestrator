---
feature_id: "IMPLEMENTATION_GUIDE"
version: "1.0.0"
status: "Completed"
priority: "Medium"
category: "Documentation"
dependencies: ["STATUS_TAG_SYSTEM", "PRIORITY_MATRIX", "MAINTENANCE_PROCEDURES"]
size_lines: 185
last_updated: "2025-07-08"
validation_status: "pending"
cross_references:
  - "docs/developers/planning/features/completed/filename-organization-system/README.md"
  - "docs/developers/planning/features/completed/filename-organization-system/status-tag-system.md"
module_type: "guide"
modularized_from: "docs/developers/planning/features/completed/[COMPLETED]_filename_key_and_organization_system.md"
---

# 🛠️ Implementation Guide

Practical guide for implementing and using the filename organization system.

#
# Directory Organization Structure

#
## Enhanced Features Directory

```text
docs/prompts/features/
├── README.md
├── [COMPLETED]_filename_key_and_organization_system.md (this document)
├── proposed/
│   ├── [RESEARCH]_enhanced_session_management_architecture.md
│   ├── [RESEARCH]_mode_role_system_enhancement.md
│   ├── [RESEARCH]_mcp_tools_suite_expansion.md
│   ├── [RESEARCH]_bidirectional_persistence_system.md
│   ├── [APPROVED]_automation_maintenance_enhancement.md
│   ├── [APPROVED]_smart_task_routing.md
│   ├── [APPROVED]_template_pattern_library.md
│   ├── [APPROVED]_integration_health_monitoring.md
│   ├── [APPROVED]_git_integration_issue_management.md
│   └── [APPROVED]_orchestrator_intelligence_suite_bundle.md
├── approved/ (move files here when ready for implementation)
├── in-progress/ (move files here during active development)
├── testing/ (move files here during validation)
├── completed/ (move files here when finished)
├── archived/ (move files here when deprecated)
└── templates/
    ├── [COMPLETED]_feature_specification_template.md
    └── [COMPLETED]_implementation_plan_template.md

```text

#
## Root Documentation Structure

```text
text
docs/
├── [COMPLETED]_INDEX.md
├── [COMPLETED]_installation.md
├── [COMPLETED]_configuration.md
├── [COMPLETED]_usage.md
├── [IN-PROGRESS]_DEVELOPER.md
├── [COMPLETED]_MIGRATION.md
├── architecture/
│   ├── [COMPLETED]_a2a_framework_integration.md
│   ├── [COMPLETED]_decision_documentation_framework.md
│   ├── [COMPLETED]_file_change_tracking_system.md
│   ├── [COMPLETED]_nested_task_architecture.md
│   └── [RESEARCH]_enhanced_session_management_architecture.md
└── prompts/
    ├── [COMPLETED]_handover_prompt.md
    ├── [RESEARCH]_documentation_analysis_and_plan.md
    └── features/ (structured as above)

```text

#
# File Lifecycle Management

#
## Status Progression Flow

```text
mermaid
flowchart TD
    A["Create: [RESEARCH]"] --> B["Research Complete"]
    B --> C["Update: [APPROVED]"]
    C --> D["Implementation Start"]
    D --> E["Update: [IN-PROGRESS]"]
    E --> F["Implementation Complete"]
    F --> G["Update: [TESTING]"]
    G --> H["Testing Complete"]
    H --> I["Update: [COMPLETED]"]
    
    A --> J["Cancelled"]
    C --> J
    E --> J
    G --> J
    J --> K["Update: [ARCHIVED]"]
    
    E --> L["Blocked"]
    G --> L
    L --> M["Update: [BLOCKED]"]
    M --> N["Issue Resolved"]
    N --> E
    N --> G

```text

#
## File Movement Procedures

**Directory Movement Rules**:

1. Files can stay in current directory with status tag updates

2. Optional: Move to status-specific directories for better organization

3. Always move to `archived/` when status becomes [ARCHIVED]

4. Consider moving [COMPLETED] items to `completed/` for clarity

**Movement Script Example**:
```text
bash
#!/bin/bash

# move_by_status.sh - Organize files by status

organize_files() {
    local source_dir="$1"
    
    
# Create status directories if they don't exist
    mkdir -p research approved in-progress testing completed archived
    
    
# Move files based on status tags
    for file in "$source_dir"/[*.md; do
        if [[ -f "$file" ]]; then
            local filename=$(basename "$file")
            
            case "$filename" in
                \[RESEARCH\]*) mv "$file" research/ ;;
                \[APPROVED\]*) mv "$file" approved/ ;;
                \[IN-PROGRESS\]*) mv "$file" in-progress/ ;;
                \[TESTING\]*) mv "$file" testing/ ;;
                \[COMPLETED\]*) mv "$file" completed/ ;;
                \[ARCHIVED\]*) mv "$file" archived/ ;;
                *) echo "Unknown status for: $filename" ;;
            esac
        fi
    done
}

```text

#
# Automated Maintenance Tools

#
## Status Validation Script

```text
python
#!/usr/bin/env python3

# validate_documentation.py

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

VALID_STATUS_TAGS = {
    'RESEARCH', 'APPROVED', 'IN-PROGRESS', 'TESTING', 
    'COMPLETED', 'ARCHIVED', 'BLOCKED'
}

VALID_PRIORITY_TAGS = {
    'CRITICAL', 'HIGH-PRIORITY', 'LOW-PRIORITY', 
    'EXPERIMENTAL', 'DEPRECATED', 'SECURITY', 'BREAKING'
}

def validate_filename(filename: str) -> Tuple[bool, List[str]]:
    """Validate filename against organization standards."""
    
    errors = []
    
    
# Check for status tag
    if not filename.startswith('['):
        errors.append("Missing status tag")
        return False, errors
    
    
# Extract status tag
    tag_match = re.match(r'\[([^\]]+)\]', filename)
    if not tag_match:
        errors.append("Malformed status tag")
        return False, errors
    
    status_tag = tag_match.group(1)
    
    
# Check for secondary tags
    remaining = filename[len(tag_match.group(0)):]
    secondary_tag = None
    
    if remaining.startswith('_['):
        secondary_match = re.match(r'_\[([^\]]+)\]', remaining)
        if secondary_match:
            secondary_tag = secondary_match.group(1)
            remaining = remaining[len(secondary_match.group(0)):]
    
    
# Validate status tag
    if status_tag not in VALID_STATUS_TAGS:
        errors.append(f"Invalid status tag: {status_tag}")
    
    
# Validate secondary tag if present
    if secondary_tag and secondary_tag not in VALID_PRIORITY_TAGS:
        errors.append(f"Invalid secondary tag: {secondary_tag}")
    
    
# Check descriptive name
    if not remaining.startswith('_'):
        errors.append("Missing underscore after status tag")
    
    
# Check file extension
    if not filename.endswith('.md'):
        errors.append("Must be .md file")
    
    
# Check length
    if len(filename) > 80:
        errors.append(f"Filename too long: {len(filename)} chars (max 80)")
    
    return len(errors) == 0, errors

def validate_directory(directory: Path) -> Dict[str, List[str]]:
    """Validate all markdown files in directory."""
    
    results = {}
    
    for md_file in directory.glob('**/*.md'):
        is_valid, errors = validate_filename(md_file.name)
        if not is_valid:
            results[str(md_file)] = errors
    
    return results

def main():
    """Main validation function."""
    
    if len(sys.argv) < 2:
        print("Usage: python validate_documentation.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    
    if not directory.exists():
        print(f"Directory does not exist: {directory}")
        sys.exit(1)
    
    results = validate_directory(directory)
    
    if not results:
        print("✅ All documentation files are properly organized!")
        sys.exit(0)
    
    print(f"❌ Found {len(results)} files with issues:")
    print()
    
    for file_path, errors in results.items():
        print(f"File: {file_path}")
        for error in errors:
            print(f"  - {error}")
        print()
    
    sys.exit(1)

if __name__ == '__main__':
    main()

```text

#
## Cross-Reference Checker

```text
python
#!/usr/bin/env python3

# check_cross_references.py

import os
import re
from pathlib import Path
from typing import List, Set

def extract_markdown_links(content: str) -> List[Tuple[str, str]]:
    """Extract markdown links from content."""
    
    
# Pattern for [text](url) format
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, content)

def check_internal_links(file_path: Path, project_root: Path) -> List[str]:
    """Check internal links in a markdown file."""
    
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    links = extract_markdown_links(content)
    
    for link_text, link_url in links:
        
# Check internal links (starting with docs/ or relative paths)
        if link_url.startswith('docs/') or link_url.startswith('../'):
            
# Resolve relative path
            if link_url.startswith('../'):
                target_path = (file_path.parent / link_url).resolve()
            else:
                target_path = project_root / link_url
            
            if not target_path.exists():
                errors.append(f"Broken link: {link_url}")
    
    return errors

def main():
    """Check all cross-references in documentation."""
    
    project_root = Path.cwd()
    docs_dir = project_root / 'docs'
    
    if not docs_dir.exists():
        print("No docs directory found")
        return
    
    total_errors = 0
    
    for md_file in docs_dir.glob('**/*.md'):
        errors = check_internal_links(md_file, project_root)
        
        if errors:
            print(f"\nFile: {md_file.relative_to(project_root)}")
            for error in errors:
                print(f"  ❌ {error}")
            total_errors += len(errors)
    
    if total_errors == 0:
        print("✅ All cross-references are valid!")
    else:
        print(f"\n❌ Found {total_errors} broken links")

if __name__ == '__main__':
    main()

```text

#
# Best Practices and Examples

#
## Filename Construction Patterns

```text
text

# Basic pattern

[STATUS]_descriptive_name.md

# With priority

[STATUS]_[PRIORITY]_descriptive_name.md

# Good examples

[RESEARCH]_user_authentication_analysis.md
[APPROVED]_[HIGH-PRIORITY]_database_migration.md
[IN-PROGRESS]_api_documentation_update.md
[TESTING]_performance_optimization.md
[COMPLETED]_installation_guide.md
[ARCHIVED]_legacy_deployment_process.md

# Avoid these patterns

user_auth.md                           
# No status tag
[research]_user_auth.md                
# Lowercase status
[RESEARCH][HIGH]_user_auth.md          
# No separation
[RESEARCH]_very_long_descriptive_name_that_exceeds_length_limits.md  
# Too long

```text

#
## Content Structure Templates

**Research Document Template**:
```text
markdown

# [RESEARCH] Feature Investigation: [Feature Name]

**Status**: Research Phase
**Priority**: [HIGH/MEDIUM/LOW]
**Estimated Effort**: [Time estimate]
**Dependencies**: [List dependencies]

#
# Problem Statement

[Describe the problem or opportunity]

#
# Current State Analysis

[Analyze existing situation]

#
# Proposed Solutions

[List and evaluate options]

#
# Recommendations

[Recommended approach and next steps]

#
# Risk Assessment

[Identify potential risks and mitigations]

```text

**Implementation Document Template**:
```text
markdown

# [IN-PROGRESS] Implementation: [Feature Name]

**Status**: In Development
**Assigned**: [Developer name]
**Started**: [Date]
**Target Completion**: [Date]

#
# Implementation Plan

[Detailed implementation approach]

#
# Progress Updates

#
## [Date]
[Progress description]

#
# Blockers and Issues

[Current challenges]

#
# Testing Plan

[How feature will be validated]
```text

This implementation guide provides practical tools and procedures for effectively using the filename organization system in daily development workflows.
