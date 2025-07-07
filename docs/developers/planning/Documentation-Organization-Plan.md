

# Documentation Organization Plan for v2.0.0

**Document Type**: Organization Strategy  
**Version**: 2.0.0  
**Created**: 2025-01-28  
**Status**: Active Planning

#

# Current State Analysis

#

## Major Issues Identified

1. **docs/prompts/ Overgrowth**: 60+ files with mixed planning/archive content

2. **Root Directory Clutter**: 20+ loose files in docs/ that should be organized

3. **Planning Underutilization**: docs/planning/ only has 2 files but should contain strategic content

4. **Archive Accumulation**: Many completed/obsolete files scattered throughout

5. **Duplicate Content**: Similar content in multiple locations

6. **Test File Pollution**: Random test files in docs/ that should be in tests/ or removed

#

# Reorganization Strategy

#

## Phase 1: Archive Historical Content

**Move to docs/archives/historical/**:

```text
FROM docs/prompts/archives/ → docs/archives/historical/handover-prompts/
FROM docs/prompts/fix-statemanager-parent-task-id*.md → docs/archives/completed-fixes/
FROM docs/prompts/release-1.3.0-*.md → docs/archives/historical/releases/
FROM docs/prompts/investigate-*.md → docs/archives/completed-investigations/
FROM docs/prompts/installer_*.md → docs/archives/completed-implementations/
FROM docs/prompts/testing_suite_implementation.md → docs/archives/completed-implementations/

```text

**Create archive structure**:

```text

docs/archives/
├── completed-fixes/           

# Resolved technical issues

├── completed-implementations/ 

# Finished feature work  

├── historical/               

# Legacy documents

│   ├── handover-prompts/
│   ├── releases/
│   └── investigations/
└── README.md                 

# Archive index and retention policy

```text

#

## Phase 2: Reorganize Planning Content

**Move to docs/planning/**:

```text

FROM docs/prompts/features/ → docs/planning/features/
FROM docs/prompts/improvement_areas.md → docs/planning/improvement-areas.md
FROM docs/prompts/final_implementation.md → docs/planning/legacy-plans/
FROM docs/architecture/ (selected files) → docs/planning/architecture/

```text

**Enhanced planning structure**:

```text

docs/planning/
├── MCP_TASK_ORCHESTRATOR_2.0_IMPLEMENTATION_PLAN.md  

# New master plan

├── version-progression-plan.md                       

# Move from root planning/

├── feature-specifications.md                         

# Move from root planning/

├── features/                                         

# From prompts/features/

│   ├── approved/
│   ├── proposed/  
│   ├── completed/
│   └── templates/
├── architecture/                                     

# Strategic architecture docs

│   ├── clean-architecture-decisions.md
│   ├── generic-task-model-design.md
│   └── future-roadmap.md
├── improvement-areas.md                              

# From prompts/

└── legacy-plans/                                     

# Archive old planning docs

```text

#

## Phase 3: Consolidate User Documentation

**Reorganize docs/ root files**:

```text

MOVE TO user-guide/:

- INSTALLATION_IMPROVEMENTS.md → user-guide/installation/

- MIGRATION.md → user-guide/migration/

- WORKSPACE_PARADIGM_FINDINGS_SUMMARY.md → user-guide/workspace-paradigm/

MOVE TO reference/:

- API_REFERENCE.md → reference/api/

- MCP_CONFIGURATION_REFERENCE.md → reference/configuration/

- TOOL_NAMING_MIGRATION.md → reference/migration/

- UNIVERSAL_INSTALLER.md → reference/installation/

MOVE TO development/:

- DEVELOPER.md → development/contributing/

- TESTING_BEST_PRACTICES.md → development/testing/

- TESTING_IMPROVEMENTS.md → development/testing/

- CLAUDE_CODE_RULES_STRUCTURE.md → development/

```text

#

## Phase 4: Consolidate Implementation Guides

**Merge scattered implementation content**:

```text

docs/implementation/ MERGE INTO docs/development/implementation/
docs/database_persistence*.md → development/implementation/database/
docs/file_based_test_output_system.md → development/testing/

```text

#

## Phase 5: Clean Root Directory

**Final docs/ root structure** (only essential top-level files):

```text

docs/
├── README.md                           

# Main documentation index

├── INDEX.md                           

# Navigation hub

├── CLAUDE.md                          

# Development guidance (keep in root)

├── CLEAN_ARCHITECTURE_GUIDE.md        

# Architecture reference (keep in root)

├── QUICK_COMMANDS.md                  

# Quick reference (keep in root)

└── installation.md                    

# Main installation guide

```text

#

# Detailed Reorganization Actions

#

## Immediate Actions (Week 1)

#

### 1. Create Archive Structure

```text
bash
mkdir -p docs/archives/{completed-fixes,completed-implementations,historical/{handover-prompts,releases,investigations}}

```text

#

### 2. Archive Completed Work

```text
bash

# Move completed fixes

mv docs/prompts/fix-statemanager-parent-task-id*.md docs/archives/completed-fixes/
mv docs/prompts/remaining-synchronization-fixes.md docs/archives/completed-fixes/

# Move completed implementations  

mv docs/prompts/installer_*.md docs/archives/completed-implementations/
mv docs/prompts/testing_suite_implementation.md docs/archives/completed-implementations/
mv docs/prompts/maintenance_coordinator_implementation.md docs/archives/completed-implementations/

# Move historical handover prompts

mv docs/prompts/archives/* docs/archives/historical/handover-prompts/

# Move old releases

mv docs/prompts/release-1.3.0-*.md docs/archives/historical/releases/

```text

#

### 3. Enhance Planning Directory

```text
bash

# Move strategic planning content

mv docs/prompts/features/ docs/planning/
mv docs/prompts/improvement_areas.md docs/planning/
mv planning/* docs/planning/  

# Merge root planning/

# Move strategic architecture docs

mkdir -p docs/planning/architecture
mv docs/architecture/generic-task-implementation-guide.md docs/planning/architecture/
mv docs/architecture/nested-task-architecture.md docs/planning/architecture/

```text

#

## Secondary Actions (Week 2)

#

### 4. Reorganize User Documentation

```text
bash

# Enhance user-guide structure

mkdir -p docs/user-guide/{installation,migration,workspace-paradigm}
mv docs/INSTALLATION_IMPROVEMENTS.md docs/user-guide/installation/
mv docs/MIGRATION.md docs/user-guide/migration/
mv docs/WORKSPACE_PARADIGM_FINDINGS_SUMMARY.md docs/user-guide/workspace-paradigm/

# Enhance reference structure  

mkdir -p docs/reference/{api,configuration,migration,installation}
mv docs/API_REFERENCE.md docs/reference/api/
mv docs/MCP_CONFIGURATION_REFERENCE.md docs/reference/configuration/
mv docs/TOOL_NAMING_MIGRATION.md docs/reference/migration/
mv docs/UNIVERSAL_INSTALLER.md docs/reference/installation/

```text

#

### 5. Consolidate Development Documentation

```text
bash

# Merge implementation guides

mv docs/implementation/* docs/development/implementation/
rmdir docs/implementation

# Organize database documentation

mkdir -p docs/development/implementation/database
mv docs/database_persistence*.md docs/development/implementation/database/

# Consolidate testing documentation

mv docs/TESTING_*.md docs/development/testing/
mv docs/file_based_test_output_system.md docs/development/testing/

```text

#

# Content Audit and Cleanup

#

## Files for Deletion

**Criteria**: Outdated, superseded, or no longer relevant

```text
bash

# Remove outdated prompt files

rm docs/prompts/directory-cleanup.md  

# Superseded by this plan

rm docs/prompts/project-organization-cleanup-task.md  

# Completed

rm docs/prompts/documentation_reorganization_and_installer_docs.md  

# Completed

# Remove test artifacts that aren't proper tests

rm docs/development/documentation_reorganization_verification.py  

# Should be in tests/

rm docs/hanging_points_analysis.md  

# Outdated analysis

rm docs/timeout_investigation_complete.md  

# Completed investigation

```text

#

## Files for Consolidation

**Merge similar content to eliminate duplication**:

1. **Testing Documentation**: Merge multiple testing guides into comprehensive docs/development/testing/ structure

2. **Installation Guides**: Consolidate various installation documents

3. **Migration Documentation**: Unify migration guides and references

4. **Architecture Documentation**: Merge scattered architecture decisions

#

# New Documentation Structure

#

## Final Target Structure

```text

docs/
├── README.md                           

# Main entry point

├── INDEX.md                           

# Navigation hub  

├── CLAUDE.md                          

# Development guidance

├── CLEAN_ARCHITECTURE_GUIDE.md        

# Architecture reference

├── QUICK_COMMANDS.md                  

# Quick reference

├── installation.md                    

# Main installation guide

├── planning/                          

# Strategic planning (enhanced)

│   ├── MCP_TASK_ORCHESTRATOR_2.0_IMPLEMENTATION_PLAN.md
│   ├── version-progression-plan.md
│   ├── feature-specifications.md
│   ├── features/                      

# Feature lifecycle management

│   ├── architecture/                  

# Strategic architecture decisions

│   └── improvement-areas.md
├── user-guide/                        

# User documentation (enhanced)

│   ├── installation/
│   ├── migration/
│   ├── workspace-paradigm/
│   └── [existing user-guide structure]
├── reference/                         

# Reference materials (enhanced)

│   ├── api/
│   ├── configuration/
│   ├── migration/
│   └── installation/
├── development/                       

# Developer documentation (enhanced)

│   ├── implementation/
│   │   ├── database/
│   │   ├── generic-tasks/
│   │   └── templates/
│   ├── testing/
│   ├── contributing/
│   └── [existing development structure]
├── architecture/                      

# Technical architecture (focused)

│   ├── a2a-framework-integration.md
│   ├── workspace-paradigm-implementation-guide.md
│   └── [core technical architecture only]
├── archives/                          

# Historical content (new)

│   ├── completed-fixes/
│   ├── completed-implementations/
│   ├── historical/
│   └── README.md
└── [existing well-organized directories: examples/, testing/, etc.]
```text

#

# Quality Improvements

#

## 1. Consistent Naming Conventions

- Use kebab-case for all markdown files

- Prefix archive files with dates when relevant

- Use descriptive, scannable filenames

#

## 2. Cross-Reference Updates

- Update all internal links after reorganization

- Create redirect documentation for moved content

- Update CLAUDE.md with new structure guidance

#

## 3. Index and Navigation

- Update INDEX.md with new structure

- Create comprehensive README.md files in each major directory

- Add navigation breadcrumbs to key documents

#

# Success Criteria

#

## Quantitative Metrics

- [ ] Reduce docs/prompts/ from 60+ files to <10 essential files

- [ ] Reduce docs/ root from 20+ files to <10 essential files

- [ ] Increase docs/planning/ from 2 files to comprehensive planning structure

- [ ] Archive 40+ historical/completed documents

#

## Qualitative Improvements

- [ ] Clear separation between user, developer, and planning documentation

- [ ] Logical information architecture for 2.0.0 development

- [ ] Reduced cognitive load when navigating documentation

- [ ] Historical content preserved but not cluttering active development

#

# Maintenance Plan

#

## Ongoing Practices

1. **Archive Quickly**: Move completed work to archives within 1 week

2. **Planning First**: New strategic content goes in planning/ not prompts/

3. **User Focus**: Keep user-facing docs in user-guide/ hierarchy

4. **Developer Focus**: Technical implementation content in development/

#

## Quarterly Reviews

- Audit docs/ root for new clutter

- Review archives for content that can be removed (>1 year old)

- Update navigation and cross-references

- Consolidate any new documentation silos

This organization plan will create a clean, logical documentation structure ready for 2.0.0 development and beyond.
