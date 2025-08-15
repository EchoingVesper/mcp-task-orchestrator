# Project Cleanliness Framework

## Overview

This framework defines comprehensive cleanliness standards for project structure, providing guidelines for file 
organization, enforcement mechanisms, and automated detection and prevention of structural degradation. It ensures 
long-term maintainability and navigability of project repositories.

## Core Principles

### 1. Systematic Organization
**Principle**: Every file and directory has a logical, predictable location
**Implementation**: Hierarchical taxonomy with clear categorization rules
**Benefits**: Reduced search time, improved onboarding, consistent expectations

### 2. Purpose-Driven Structure
**Principle**: Directory structure reflects functional and conceptual relationships
**Implementation**: Domain-driven design applied to file organization
**Benefits**: Intuitive navigation, logical groupings, clear boundaries

### 3. Scalable Hierarchy
**Principle**: Structure accommodates growth without reorganization
**Implementation**: Extensible categorization with room for expansion
**Benefits**: Sustainable long-term organization, reduced restructuring overhead

### 4. Automated Enforcement
**Principle**: Standards are enforced through automation rather than manual compliance
**Implementation**: Automated validation, prevention, and correction systems
**Benefits**: Consistent compliance, reduced manual overhead, immediate feedback

## Directory Structure Standards

### Root Directory Organization

#### Allowed in Root Directory
```
├── Core Project Files
│   ├── README.md (primary project documentation)
│   ├── CHANGELOG.md (version history)
│   ├── LICENSE (legal requirements)
│   └── CONTRIBUTING.md (contribution guidelines)
├── Configuration Files
│   ├── pyproject.toml (Python project configuration)
│   ├── setup.py (legacy Python setup)
│   ├── requirements.txt (dependency specifications)
│   ├── package.json (Node.js projects)
│   └── .gitignore (version control configuration)
├── Critical Documentation
│   ├── CLAUDE.md (Claude Code integration instructions)
│   ├── QUICK_START.md (immediate getting started guide)
│   └── TESTING_INSTRUCTIONS.md (testing procedures)
├── Build Artifacts (Generated)
│   ├── build/ (build output directory)
│   ├── dist/ (distribution packages)
│   └── *.egg-info/ (Python package metadata)
└── Environment Files
    ├── .env.example (environment variable template)
    ├── .claude/ (Claude Code configuration)
    └── .github/ (GitHub-specific configuration)
```

#### Prohibited in Root Directory
- Temporary files (*.tmp, *.bak, ~*)
- Log files (*.log)
- Test artifacts (*.json reports, validation files)
- Migration reports and summaries
- Individual test files
- Backup files
- Development artifacts
- Personal configuration files

### Structured Directory Taxonomy

#### `/docs` - Documentation Hierarchy
```
docs/
├── users/              # User-facing documentation
│   ├── quick-start/    # Getting started guides
│   ├── guides/         # Comprehensive user guides
│   └── reference/      # Reference materials
├── developers/         # Developer documentation
│   ├── architecture/   # System design documents
│   ├── contributing/   # Development processes
│   ├── standards/      # Development standards (this document)
│   └── planning/       # Project planning documents
├── templates/          # Documentation templates
│   ├── user-facing/    # Templates for user documentation
│   ├── technical/      # Templates for technical documentation
│   └── internal/       # Templates for internal documentation
└── archives/           # Historical documentation
    ├── completed-implementations/
    ├── migration-reports/
    └── test-artifacts/
```

#### `/scripts` - Automation and Utilities
```
scripts/
├── diagnostics/        # Health checking and monitoring
├── maintenance/        # Routine maintenance automation
├── testing/           # Test execution and validation
├── deployment/        # Release and deployment automation
├── lifecycle/         # Document and artifact lifecycle management
└── utilities/         # General-purpose utility scripts
```

#### `/tests` - Testing Infrastructure
```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── performance/       # Performance and load tests
├── security/          # Security testing
├── archives/          # Historical test artifacts
│   ├── fixtures_archive/
│   ├── debug_scripts/
│   └── experimental/
└── validation_gates/  # Quality gate validation tests
```

## File Naming Standards

### Naming Conventions

#### Status Tag System
Use status tags in square brackets at the beginning of filenames for lifecycle tracking:

**Status Categories**:
- `[CURRENT]` - Active, up-to-date files
- `[IN-PROGRESS]` - Currently being worked on
- `[DRAFT]` - Planned but not yet started
- `[NEEDS-VALIDATION]` - Implementation complete, requires testing
- `[NEEDS-UPDATE]` - Requires updates due to system changes
- `[DEPRECATED]` - Legacy files maintained for reference
- `[COMPLETED]` - Finished work (typically in completed/ folders)

**Examples**:
```
[IN-PROGRESS]foundation-stabilization.md
[DRAFT]feature-roadmap.md
[NEEDS-UPDATE]installation-guide.md
[COMPLETED]v1-to-v2-migration.md
[CURRENT]clean-architecture-guide.md
```

#### Descriptive Naming
- Use kebab-case for multi-word filenames
- Include primary purpose in filename
- Avoid abbreviations unless universally understood
- Include version numbers when appropriate

**Examples**:
```
Good: user-authentication-guide.md
Bad: auth.md

Good: api-reference-v2.md
Bad: api_ref_2.md

Good: database-migration-script.py
Bad: db_mig.py
```

### File Type Organization

#### Documentation Files (.md)
- Use descriptive names indicating content purpose
- Include status tags for lifecycle management
- Group related documents in appropriate subdirectories
- Maintain consistent formatting and structure

#### Script Files (.py, .sh, .ps1)
- Use verb-noun naming pattern
- Include purpose-specific directory placement
- Maintain executable permissions where appropriate
- Include proper shebang lines and documentation

#### Configuration Files
- Use standard names when possible (requirements.txt, setup.py)
- Include environment or purpose indicators when needed
- Place in appropriate configuration directories
- Maintain version control for all configuration files

## Quality Gates and Enforcement

### Tier 1: Automated Prevention
**Purpose**: Prevent structural violations before they occur
**Implementation**: Pre-commit hooks, CI/CD pipeline checks
**Scope**: File placement, naming conventions, prohibited files

#### File Placement Validation
```bash
#!/bin/bash
# Check for prohibited files in root directory
prohibited_patterns=("*.tmp" "*.bak" "*.log" "*~" "test_*.json")
for pattern in "${prohibited_patterns[@]}"; do
    if ls ${pattern} 2>/dev/null; then
        echo "ERROR: Prohibited file pattern ${pattern} found in root"
        exit 1
    fi
done
```

#### Naming Convention Validation
```bash
#!/bin/bash
# Validate status tag usage for PRPs and planning documents
find PRPs/ -name "*.md" | while read file; do
    if [[ ! "$file" =~ \[(CURRENT|IN-PROGRESS|DRAFT|NEEDS-VALIDATION|NEEDS-UPDATE|DEPRECATED|COMPLETED)\] ]]; then
        echo "WARNING: Missing status tag in $file"
    fi
done
```

### Tier 2: Automated Detection
**Purpose**: Identify structural issues for remediation
**Implementation**: Regular scanning and reporting
**Scope**: Orphaned files, incorrect placement, missing metadata

#### Orphaned File Detection
```python
import os
import re
from pathlib import Path

def detect_orphaned_files(root_dir):
    """Detect files that don't follow organizational standards"""
    orphaned = []
    
    for file_path in Path(root_dir).rglob('*'):
        if file_path.is_file():
            if not follows_placement_rules(file_path):
                orphaned.append(file_path)
    
    return orphaned

def follows_placement_rules(file_path):
    """Check if file follows placement rules"""
    # Implementation of placement rule validation
    pass
```

#### Structure Health Monitoring
```python
def analyze_structure_health(project_root):
    """Analyze overall project structure health"""
    metrics = {
        'root_cleanliness': check_root_cleanliness(),
        'naming_compliance': check_naming_compliance(),
        'directory_structure': validate_directory_structure(),
        'orphaned_files': count_orphaned_files(),
        'missing_status_tags': count_missing_status_tags()
    }
    return metrics
```

### Tier 3: Automated Correction
**Purpose**: Automatically fix detected structural issues
**Implementation**: Automated cleanup and reorganization
**Scope**: Moveable files, correctable naming issues, automated cleanup

#### Automated File Movement
```python
def reorganize_misplaced_files():
    """Automatically move files to correct locations"""
    movement_rules = {
        '*.json': 'test-artifacts/',  # Test artifacts
        'migration_*.md': 'docs/archives/migration-reports/',
        'test_*.py': 'tests/',
        '*.log': 'logs/'  # Move to logs directory
    }
    
    for pattern, destination in movement_rules.items():
        move_files_matching_pattern(pattern, destination)
```

## Implementation Roadmap

### Phase 1: Assessment and Baseline (Week 1-2)
1. **Current State Analysis**
   - Audit existing project structure
   - Identify violations of cleanliness standards
   - Document current organizational patterns

2. **Priority Classification**
   - Classify issues by severity and impact
   - Identify quick wins for immediate improvement
   - Plan phased approach for complex reorganization

3. **Tool Development**
   - Create initial validation scripts
   - Develop detection algorithms
   - Set up basic reporting infrastructure

### Phase 2: Automated Detection (Week 3-4)
1. **Detection System Deployment**
   - Implement comprehensive scanning tools
   - Set up regular monitoring schedules
   - Create issue tracking and reporting

2. **Baseline Cleanup**
   - Address critical structural violations
   - Implement immediate improvements
   - Establish clean baseline for future enforcement

3. **Documentation Updates**
   - Update existing documentation for new standards
   - Create user guides for structural requirements
   - Establish change management procedures

### Phase 3: Prevention Implementation (Week 5-6)
1. **Automated Prevention Systems**
   - Implement pre-commit hooks
   - Set up CI/CD pipeline validation
   - Create real-time feedback systems

2. **Developer Tool Integration**
   - Integrate with IDE and editor workflows
   - Provide real-time structural validation
   - Create templates and scaffolding tools

3. **Training and Adoption**
   - Train team on new structural standards
   - Create quick reference guides
   - Establish support and feedback channels

### Phase 4: Automated Correction (Week 7-8)
1. **Correction System Development**
   - Implement safe automated correction
   - Create rollback and recovery procedures
   - Test correction algorithms thoroughly

2. **Full Automation Integration**
   - Connect detection, prevention, and correction systems
   - Implement comprehensive monitoring dashboards
   - Create automated reporting and notifications

3. **Continuous Improvement**
   - Establish metrics and KPIs for structural health
   - Create feedback loops for standard refinement
   - Implement ongoing optimization processes

## Monitoring and Metrics

### Structural Health Metrics
- **Root Directory Cleanliness**: Percentage compliance with root directory standards
- **Naming Convention Adherence**: Percentage of files following naming standards
- **Directory Structure Compliance**: Adherence to prescribed directory taxonomy
- **Orphaned File Count**: Number of files in incorrect locations

### Process Metrics
- **Prevention Effectiveness**: Percentage of violations prevented by automation
- **Detection Speed**: Time from violation to detection
- **Correction Accuracy**: Success rate of automated corrections
- **Manual Intervention Rate**: Frequency of required manual intervention

### User Experience Metrics
- **Navigation Efficiency**: Time to locate specific files or documentation
- **Onboarding Speed**: Time for new team members to understand project structure
- **Search Success Rate**: Percentage of successful file/information searches
- **User Satisfaction**: Team satisfaction with project organization

### Maintenance Metrics
- **Maintenance Overhead**: Time spent on structural maintenance tasks
- **Automation Coverage**: Percentage of maintenance tasks automated
- **Standard Compliance Trend**: Improvement or degradation over time
- **Issue Resolution Time**: Time from detection to resolution

## Success Criteria

### Short-term Success (Month 1)
- Root directory meets cleanliness standards
- Automated detection system operational
- Initial cleanup of major structural violations completed
- Team trained on new standards

### Medium-term Success (Month 3)
- Comprehensive prevention system deployed
- Naming conventions consistently applied
- Directory structure fully compliant
- Automated correction system operational

### Long-term Success (Month 6)
- Self-maintaining project structure
- Cultural adoption of cleanliness principles
- Continuous improvement processes mature
- Industry-leading project organization practices

## Tools and Automation

### Validation Scripts
- `project-structure-validator.sh` - Comprehensive structure validation
- `naming-convention-checker.py` - Automated naming standard enforcement
- `root-directory-cleanliness.py` - Root directory compliance checking
- `status-tag-validator.sh` - Status tag presence and correctness validation

### Correction Scripts
- `automated-file-organizer.py` - Move files to correct locations
- `naming-standard-corrector.py` - Fix naming convention violations
- `duplicate-file-merger.py` - Identify and merge duplicate content
- `orphan-file-processor.py` - Handle orphaned and abandoned files

### Monitoring Tools
- `structure-health-monitor.py` - Continuous structure health monitoring
- `cleanliness-dashboard.py` - Real-time cleanliness metrics dashboard
- `compliance-reporter.py` - Generate compliance reports
- `trend-analyzer.py` - Analyze structural health trends over time

## Conclusion

A clean, well-organized project structure is fundamental to long-term maintainability and team productivity. 
This framework provides comprehensive standards, automated enforcement, and continuous improvement mechanisms 
to ensure project structure remains optimal throughout the project lifecycle.

Success depends on consistent application of standards, effective automation, and team commitment to 
maintaining structural excellence. The investment in clean project organization pays dividends in reduced 
maintenance overhead, improved team productivity, and enhanced project sustainability.