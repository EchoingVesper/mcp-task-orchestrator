

# 📋 Filename Key and Organization System

**Document Type**: Implementation Guide & Reference  
**Version**: 1.0.0  
**Created**: 2025-06-01  
**Status**: [IN-PROGRESS] - Implementation phase  
**Priority**: HIGH - Foundation for documentation organization  
**Scope**: Complete file organization system with status tracking

---

#

# 🎯 Overview

This document defines the comprehensive filename key and organization system for the MCP Task Orchestrator project documentation. It establishes status tags, priority indicators, and maintenance procedures for systematic documentation management.

---

#

# 🏷️ Status Tag System

#

## Primary Status Tags

Status tags indicate the current phase of a document's lifecycle:

| Tag | Description | Use Cases | Color Code |
|-----|-------------|-----------|------------|
| **[RESEARCH]** | Analysis and investigation phase | Requirements gathering, feasibility studies, current state analysis | 🔵 Blue |
| **[APPROVED]** | Ready for implementation | Completed specifications, approved designs, validated requirements | 🟢 Green |
| **[IN-PROGRESS]** | Currently being worked on | Active development, ongoing documentation, implementation phase | 🟡 Yellow |
| **[TESTING]** | Implementation complete, testing phase | Verification, validation, quality assurance | 🟣 Purple |
| **[COMPLETED]** | Fully implemented and validated | well-tested, documented features, finished components | ✅ Green Check |
| **[ARCHIVED]** | Deprecated or cancelled | Obsolete features, cancelled projects, superseded documents | ⚫ Gray |
| **[BLOCKED]** | Waiting on dependencies | Pending external input, blocked by other work, resource constraints | 🔴 Red |

#

## Secondary Status Tags (Optional)

Additional context for specific situations:

| Tag | Description | Use Cases |
|-----|-------------|-----------|
| **[HIGH-PRIORITY]** | Urgent implementation needed | Critical fixes, blocking issues, time-sensitive features |
| **[LOW-PRIORITY]** | Future consideration | Nice-to-have features, optimization, long-term improvements |
| **[EXPERIMENTAL]** | Proof of concept | Research spikes, experimental features, early prototypes |
| **[DEPRECATED]** | Being phased out | Legacy systems, outdated approaches, migration targets |
| **[SECURITY]** | Security-related content | Security fixes, threat analysis, compliance requirements |
| **[BREAKING]** | Contains breaking changes | API changes, schema migrations, compatibility issues |

---

#

# 📁 File Naming Convention

#

## Standard Format

```text
[PRIMARY_STATUS]_descriptive_file_name.md
[PRIMARY_STATUS]_[SECONDARY_STATUS]_descriptive_file_name.md

```text

#

## Examples

```text

✅ Good Examples:
[RESEARCH]_enhanced_session_management_architecture.md
[APPROVED]_database_schema_enhancements.md
[IN-PROGRESS]_mcp_tools_implementation.md
[COMPLETED]_installation_guide_update.md
[BLOCKED]_[HIGH-PRIORITY]_github_integration_fix.md
[TESTING]_bidirectional_persistence_system.md
[ARCHIVED]_legacy_task_management_approach.md

❌ Bad Examples:
enhanced_session_management.md (no status tag)
[research]_session_management.md (lowercase tag)
[IN-PROGRESS][HIGH-PRIORITY]_feature.md (no separation)
very_long_descriptive_filename_that_exceeds_reasonable_length.md (too long)

```text

#

## Filename Requirements

1. **Status Tag**: Must be the first element in square brackets

2. **Descriptive Name**: Clear, concise description using underscores

3. **Length Limit**: Maximum 80 characters total filename

4. **Case Convention**: Status tags in UPPERCASE, filenames in lowercase_with_underscores

5. **Extension**: `.md` for documentation files

---

#

# 🗂️ Directory Organization Structure

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

---

#

# 🔄 File Lifecycle Management

#

## Status Progression Flow

```text

[RESEARCH] → [APPROVED] → [IN-PROGRESS] → [TESTING] → [COMPLETED]
     ↓            ↓            ↓            ↓
  [ARCHIVED]  [BLOCKED]   [BLOCKED]   [BLOCKED]

```text

#

## Lifecycle Operations

```text
python

# Pseudo-code for file lifecycle management

class DocumentLifecycle:
    def progress_status(self, filename: str, new_status: str):
        """Move document to next status in lifecycle."""
        
        

# Validate status progression

        current_status = self.extract_status(filename)
        if not self.is_valid_progression(current_status, new_status):
            raise InvalidStatusProgression(f"Cannot move from {current_status} to {new_status}")
        
        

# Update filename and move file

        new_filename = self.update_status_tag(filename, new_status)
        new_directory = self.get_directory_for_status(new_status)
        
        self.move_file(filename, new_directory, new_filename)
        self.update_cross_references(filename, new_filename)
        self.log_status_change(filename, current_status, new_status)
    
    def is_valid_progression(self, current: str, new: str) -> bool:
        """Validate status progression according to rules."""
        valid_progressions = {
            "RESEARCH": ["APPROVED", "ARCHIVED", "BLOCKED"],
            "APPROVED": ["IN-PROGRESS", "ARCHIVED", "BLOCKED"],
            "IN-PROGRESS": ["TESTING", "COMPLETED", "BLOCKED", "ARCHIVED"],
            "TESTING": ["COMPLETED", "IN-PROGRESS", "BLOCKED"],
            "COMPLETED": ["ARCHIVED"],
            "BLOCKED": ["RESEARCH", "APPROVED", "IN-PROGRESS", "ARCHIVED"],
            "ARCHIVED": []  

# Terminal state

        }
        return new in valid_progressions.get(current, [])

```text

---

#

# 📊 Priority Matrix System

#

## Priority Levels

| Level | Description | Characteristics | Timeline |
|-------|-------------|-----------------|----------|
| **URGENT** | Critical blocking issues | Prevents other work, production impact | < 24 hours |
| **HIGH** | Important for current milestone | Core functionality, key features | 1-7 days |
| **MEDIUM** | Standard priority work | Normal feature development | 1-4 weeks |
| **LOW** | Future improvements | Nice-to-have, optimization | 1-6 months |
| **SOMEDAY** | Wishlist items | Ideas for future consideration | 6+ months |

#

## Priority Indicators in Filenames

```text

[IN-PROGRESS]_[HIGH-PRIORITY]_database_migration_fix.md
[BLOCKED]_[URGENT]_production_security_issue.md
[RESEARCH]_[LOW-PRIORITY]_ui_design_improvements.md
[APPROVED]_[MEDIUM]_session_management_implementation.md

```text

#

## Priority-Based Directory Organization

```text

features/
├── urgent/ (URGENT priority items)
├── high-priority/ (HIGH priority items)
├── current/ (MEDIUM priority - current work)
├── backlog/ (LOW priority - planned work)
└── someday/ (SOMEDAY priority - ideas)

```text

---

#

# 🔍 Automated Maintenance Tools

#

## Status Validation Script

```text
python
#!/usr/bin/env python3
"""
Documentation Status Validation Tool
Validates filename conventions and status consistency.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

class DocumentationValidator:
    VALID_STATUSES = {
        "RESEARCH", "APPROVED", "IN-PROGRESS", "TESTING", 
        "COMPLETED", "ARCHIVED", "BLOCKED"
    }
    
    VALID_PRIORITIES = {
        "URGENT", "HIGH-PRIORITY", "LOW-PRIORITY", "EXPERIMENTAL",
        "DEPRECATED", "SECURITY", "BREAKING"
    }
    
    FILENAME_PATTERN = r'^\[([A-Z-]+)\](?:_\[([A-Z-]+)\])?_([a-z0-9_]+)\.md$'
    
    def validate_directory(self, directory: Path) -> List[str]:
        """Validate all markdown files in directory."""
        errors = []
        
        for file_path in directory.rglob("*.md"):
            filename = file_path.name
            
            

# Skip special files

            if filename in ["README.md", "INDEX.md"]:
                continue
            
            

# Validate filename format

            match = re.match(self.FILENAME_PATTERN, filename)
            if not match:
                errors.append(f"Invalid filename format: {filename}")
                continue
            
            status = match.group(1)
            priority = match.group(2)
            name = match.group(3)
            
            

# Validate status

            if status not in self.VALID_STATUSES:
                errors.append(f"Invalid status '{status}' in: {filename}")
            
            

# Validate priority (if present)

            if priority and priority not in self.VALID_PRIORITIES:
                errors.append(f"Invalid priority '{priority}' in: {filename}")
            
            

# Validate filename length

            if len(filename) > 80:
                errors.append(f"Filename too long ({len(filename)} chars): {filename}")
            
            

# Validate directory placement

            expected_dir = self.get_expected_directory(status)
            if expected_dir and expected_dir not in str(file_path.parent):
                errors.append(f"File in wrong directory: {filename} (status: {status})")
        
        return errors
    
    def get_expected_directory(self, status: str) -> str:
        """Get expected directory for status."""
        directory_mapping = {
            "RESEARCH": "proposed",
            "APPROVED": "approved", 
            "IN-PROGRESS": "in-progress",
            "TESTING": "testing",
            "COMPLETED": "completed",
            "ARCHIVED": "archived"
        }
        return directory_mapping.get(status)

# Usage

if __name__ == "__main__":
    validator = DocumentationValidator()
    docs_path = Path("docs")
    
    errors = validator.validate_directory(docs_path)
    
    if errors:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ All documentation files pass validation")

```text

#

## Automatic Status Migration Script

```text
python
#!/usr/bin/env python3
"""
Documentation Status Migration Tool
Automatically updates file statuses and reorganizes directories.
"""

class StatusMigrator:
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.validator = DocumentationValidator()
    
    def migrate_file_status(self, filename: str, new_status: str):
        """Migrate file to new status."""
        
        

# Find current file

        current_file = self.find_file(filename)
        if not current_file:
            raise FileNotFoundError(f"File not found: {filename}")
        
        

# Extract current status

        current_status = self.extract_status(filename)
        
        

# Validate progression

        if not self.validator.is_valid_progression(current_status, new_status):
            raise ValueError(f"Invalid progression: {current_status} → {new_status}")
        
        

# Create new filename

        new_filename = self.update_status_in_filename(filename, new_status)
        
        

# Determine target directory

        target_dir = self.get_target_directory(new_status)
        target_path = target_dir / new_filename
        
        

# Move file

        current_file.rename(target_path)
        
        

# Update cross-references

        self.update_cross_references(filename, new_filename)
        
        print(f"✅ Migrated: {filename} → {new_filename}")
        return target_path
    
    def batch_migrate(self, migrations: List[Tuple[str, str]]):
        """Perform batch status migrations."""
        
        for filename, new_status in migrations:
            try:
                self.migrate_file_status(filename, new_status)
            except Exception as e:
                print(f"❌ Failed to migrate {filename}: {e}")

# Usage example

if __name__ == "__main__":
    migrator = StatusMigrator(Path("docs"))
    
    

# Example migrations

    migrations = [
        ("automation-maintenance-enhancement.md", "APPROVED"),
        ("smart-task-routing.md", "APPROVED"),
        ("template-pattern-library.md", "APPROVED")
    ]
    
    migrator.batch_migrate(migrations)

```text

---

#

# 📋 Cross-Reference Management

#

## Reference Update System

```text
python
class CrossReferenceManager:
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.reference_cache = {}
    
    def find_all_references(self, filename: str) -> List[Tuple[Path, int, str]]:
        """Find all references to a file across documentation."""
        
        references = []
        old_name = filename.replace('.md', '')
        
        

# Search all markdown files

        for file_path in self.docs_root.rglob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                

# Look for markdown links

                if old_name in line:
                    

# Match [text](filename) or [text](path/filename)

                    if re.search(rf'\[.*?\]\([^)]*{re.escape(old_name)}[^)]*\)', line):
                        references.append((file_path, line_num, line.strip()))
                    
                    

# Match [[filename]] wiki-style links

                    if re.search(rf'\[\[.*?{re.escape(old_name)}.*?\]\]', line):
                        references.append((file_path, line_num, line.strip()))
        
        return references
    
    def update_references(self, old_filename: str, new_filename: str):
        """Update all references when file is renamed."""
        
        references = self.find_all_references(old_filename)
        old_name = old_filename.replace('.md', '')
        new_name = new_filename.replace('.md', '')
        
        for file_path, line_num, line_content in references:
            

# Read file

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            

# Update references

            content = content.replace(old_name, new_name)
            
            

# Write back

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated reference in {file_path}:{line_num}")

```text

---

#

# 🎯 Implementation Guidelines

#

## Initial Setup Process

1. **Create directory structure** for status-based organization

2. **Run validation script** on existing documentation

3. **Add status tags** to existing files

4. **Reorganize files** into appropriate directories

5. **Update cross-references** to reflect new names

6. **Establish maintenance schedule** for regular validation

#

## Maintenance Procedures

- **Weekly**: Run validation script to check compliance

- **Monthly**: Review status progressions and update outdated tags

- **Quarterly**: Archive completed items and clean up deprecated content

- **Annually**: Review and update the organization system itself

#

## Quality Gates

- All new documentation must include status tags

- Status progressions must be validated before file moves

- Cross-references must be updated when files are renamed

- Directory structure must match status classifications

---

#

# 📊 Metrics and Monitoring

#

## Documentation Health Metrics

```text
python
class DocumentationMetrics:
    def generate_status_report(self, docs_path: Path) -> dict:
        """Generate comprehensive status report."""
        
        status_counts = {}
        priority_counts = {}
        total_files = 0
        
        for file_path in docs_path.rglob("*.md"):
            if file_path.name in ["README.md", "INDEX.md"]:
                continue
            
            total_files += 1
            status = self.extract_status(file_path.name)
            priority = self.extract_priority(file_path.name)
            
            status_counts[status] = status_counts.get(status, 0) + 1
            if priority:
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "total_files": total_files,
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "completion_percentage": (status_counts.get("COMPLETED", 0) / total_files) * 100,
            "active_work": status_counts.get("IN-PROGRESS", 0) + status_counts.get("TESTING", 0)
        }

```text

---

#

# 🔄 Migration Plan for Existing Files

#

## Phase 1: Assessment (Week 1)

1. **Inventory existing files** without status tags

2. **Categorize by current state** (research, approved, etc.)

3. **Identify cross-references** that need updating

4. **Plan migration schedule** to minimize disruption

#

## Phase 2: Core System Files (Week 1)

```text

Current → New Status
installation.md → [COMPLETED]_installation.md
configuration.md → [COMPLETED]_configuration.md
usage.md → [COMPLETED]_usage.md
DEVELOPER.md → [IN-PROGRESS]_DEVELOPER.md
INDEX.md → [COMPLETED]_INDEX.md

```text

#

## Phase 3: Feature Files (Week 2)

```text

Current → New Status
automation-maintenance-enhancement.md → [APPROVED]_automation_maintenance_enhancement.md
smart-task-routing.md → [APPROVED]_smart_task_routing.md
template-pattern-library.md → [APPROVED]_template_pattern_library.md
integration-health-monitoring.md → [APPROVED]_integration_health_monitoring.md
git-integration-issue-management.md → [APPROVED]_git_integration_issue_management.md

```text

#

## Phase 4: Architecture Files (Week 2)

```text

Current → New Status
a2a-framework-integration.md → [COMPLETED]_a2a_framework_integration.md
decision-documentation-framework.md → [COMPLETED]_decision_documentation_framework.md
nested-task-architecture.md → [COMPLETED]_nested_task_architecture.md
```text

#

## Phase 5: Cross-Reference Updates (Week 3)

1. **Update all internal links** to use new filenames

2. **Update INDEX.md** with new structure

3. **Update README references** across the project

4. **Validate all links** work correctly

---

#

# ✅ Success Criteria

#

## System Implementation

- ✅ All documentation files follow naming convention

- ✅ Directory structure reflects status organization  

- ✅ Validation tools successfully identify violations

- ✅ Migration tools can move files between statuses

- ✅ Cross-references remain functional after moves

#

## Operational Success

- ✅ Development team adopts new naming convention

- ✅ Status progressions tracked accurately

- ✅ Outdated documentation identified and archived

- ✅ New features follow established lifecycle

- ✅ Documentation quality improves measurably

---

**Implementation Status**: SYSTEM DESIGNED ✅  
**Next Steps**: Apply to existing files and establish maintenance procedures  
**Success Metrics**: 100% compliance with naming convention, automated validation  
**Maintenance**: Weekly validation, monthly review, quarterly cleanup
