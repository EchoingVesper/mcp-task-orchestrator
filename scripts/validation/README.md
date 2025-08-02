
# Documentation Validation Scripts

This directory contains comprehensive validation scripts for the feature documentation standardization project. These tools ensure quality, consistency, and compliance with documentation standards.

#
# Overview

The validation system provides automated checks for:

- Template compliance and structure

- Cross-reference integrity  

- File size monitoring (Claude Code compatibility)

- Metadata validation

- Outdated pattern detection

- Modularization opportunities

#
# Quick Start

#
## Run All Validations

```bash

# Run comprehensive validation on docs directory

python scripts/validation/run_all_validations.py docs/

# Quick validation (critical checks only)

python scripts/validation/run_all_validations.py docs/ --quick

# Generate HTML report

python scripts/validation/run_all_validations.py docs/ --output validation_report.html --format html

```text

#
## Individual Validation Scripts

```text
bash

# Template compliance validation

python scripts/validation/validate_feature_template_compliance.py docs/

# File size monitoring (critical for Claude Code)

python scripts/validation/monitor_file_sizes.py docs/ --threshold critical

# Cross-reference validation

python scripts/validation/validate_cross_references.py docs/

# Metadata validation

python scripts/validation/validate_metadata.py docs/

# Outdated reference detection

python scripts/validation/check_outdated_references.py docs/

# Modularization analysis

python scripts/validation/analyze_modularization_opportunities.py docs/

```text

#
# Validation Scripts

#
## 1. Template Compliance Validator

**File:** `validate_feature_template_compliance.py`  
**Purpose:** Validates that feature documentation follows standardized template structure

**Key Features:**

- YAML frontmatter validation

- Required section checking

- File size limits (500 lines for Claude Code)

- Content quality indicators

- Deprecated pattern detection

**Usage:**
```text
bash

# Basic validation

python validate_feature_template_compliance.py docs/developers/planning/features/

# JSON output with detailed metrics

python validate_feature_template_compliance.py docs/ --format json --output compliance_report.json

# Fail on warnings (strict mode)

python validate_feature_template_compliance.py docs/ --fail-on-warnings

```text

#
## 2. Outdated Reference Checker

**File:** `check_outdated_references.py`  
**Purpose:** Identifies outdated references, patterns, and terminology

**Key Features:**

- Deprecated naming pattern detection (task_*, subtask_*)

- Outdated architecture reference checking  

- Legacy pattern identification

- Terminology consistency validation

- Broken link detection

**Usage:**
```text
bash

# Check for all outdated patterns

python check_outdated_references.py docs/

# Focus on high-severity issues only

python check_outdated_references.py docs/ --severity high

# Filter by specific pattern type

python check_outdated_references.py docs/ --type deprecated_naming

```text

#
## 3. Cross-Reference Validator

**File:** `validate_cross_references.py`  
**Purpose:** Validates cross-references and ensures link integrity

**Key Features:**

- File reference validation (@/path/to/file)

- Markdown link checking

- URL validation (optional)

- Relative path verification

- Anchor reference validation

**Usage:**
```text
bash

# Validate all references

python validate_cross_references.py docs/

# Skip URL validation for speed

python validate_cross_references.py docs/ --no-urls

# Custom timeout for URL checks

python validate_cross_references.py docs/ --timeout 30

```text

#
## 4. File Size Monitor

**File:** `monitor_file_sizes.py`  
**Purpose:** Monitors file sizes to prevent Claude Code compatibility issues

**Key Features:**

- Claude Code size limit enforcement (500 lines, 2MB)

- Size trend tracking

- Growth monitoring

- Automated recommendations

- Monitoring script generation

**Usage:**
```text
bash

# Monitor all documentation files

python monitor_file_sizes.py docs/ --pattern documentation

# Show only critical size issues

python monitor_file_sizes.py docs/ --threshold critical

# Generate detailed recommendations

python monitor_file_sizes.py docs/ --recommendations

# Generate continuous monitoring script

python monitor_file_sizes.py docs/ --generate-monitor monitor_docs.py

```text

#
## 5. Metadata Validator

**File:** `validate_metadata.py`  
**Purpose:** Validates YAML frontmatter metadata consistency

**Key Features:**

- Required field validation

- Data type checking

- Enum value validation

- Format consistency

- Terminology standards

**Usage:**
```text
bash

# Validate all metadata

python validate_metadata.py docs/

# Focus on specific field

python validate_metadata.py docs/ --field status

# Fail if any files lack metadata

python validate_metadata.py docs/ --fail-on-missing

```text

#
## 6. Modularization Analyzer

**File:** `analyze_modularization_opportunities.py`  
**Purpose:** Identifies opportunities for breaking large files into modules

**Key Features:**

- Duplicate content detection

- File complexity analysis

- Section size monitoring

- Cross-file pattern identification

- Modularization recommendations

**Usage:**
```text
bash

# Analyze modularization opportunities

python analyze_modularization_opportunities.py docs/

# Generate modularization plan

python analyze_modularization_opportunities.py docs/ --format plan

# Filter by complexity score

python analyze_modularization_opportunities.py docs/ --min-score 0.7

```text

#
## 7. Comprehensive Validation Runner

**File:** `run_all_validations.py`  
**Purpose:** Orchestrates all validation scripts and generates comprehensive reports

**Key Features:**

- Parallel validation execution

- Comprehensive reporting

- Multiple output formats (JSON, HTML, Markdown)

- Priority-based recommendations

- Performance metrics

**Usage:**
```text
bash

# Run all validations

python run_all_validations.py docs/

# Quick critical-only validation

python run_all_validations.py docs/ --quick

# Generate comprehensive HTML report

python run_all_validations.py docs/ --output report.html --format html

```text

#
# Configuration

#
## Markdown Linting Configuration

**File:** `feature_docs_markdownlint.json`  
Custom markdownlint rules for feature documentation:

```text
json
{
  "MD013": false,
  "MD025": {"front_matter_title": ""},
  "MD033": {"allowed_elements": ["details", "summary", "br"]},
  "MD041": true,
  "feature-docs-metadata": {
    "required_fields": ["title", "status", "priority", "category"]
  }
}

```text

#
## Validation Configuration

Each script accepts configuration files to customize validation rules:

```text
json
{
  "required_fields": ["title", "status", "priority"],
  "size_limits": {
    "critical_lines": 500,
    "warning_lines": 300
  },
  "enum_values": {
    "status": ["DRAFT", "REVIEW", "APPROVED"]
  }
}

```text

#
# Integration with CI/CD

#
## GitHub Actions Integration

```text
yaml
name: Documentation Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install pyyaml requests
          npm install -g markdownlint-cli
      - name: Run validation
        run: |
          python scripts/validation/run_all_validations.py docs/ --quick

```text

#
## Pre-commit Hook

```text
bash
#!/bin/bash

# Pre-commit hook for documentation validation

python scripts/validation/run_all_validations.py docs/ --quick --format text
exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "Documentation validation failed. Please fix issues before committing."
    exit 1
fi

```text

#
# Output Formats

#
## JSON Output

Structured data for integration with other tools:
```text
json
{
  "summary": {
    "total_files": 45,
    "passed_files": 42,
    "failed_files": 3
  },
  "reports": [...]
}

```text

#
## HTML Reports

Comprehensive web-based reports with:

- Visual status indicators

- Interactive sections

- Detailed issue breakdown

- Actionable recommendations

#
## Markdown Reports

Documentation-friendly format for inclusion in project docs:
```text
markdown

# Validation Report

**Status:** ✅ PASSED
**Files:** 45 total, 42 passed, 3 failed

```text

#
# Best Practices

#
## Regular Validation

1. **Run before commits:**
   ```
bash
   python scripts/validation/run_all_validations.py docs/ --quick
   
```text

2. **Weekly comprehensive check:**
   ```
bash
   python scripts/validation/run_all_validations.py docs/ --output weekly_report.html --format html
   
```text

3. **Monitor file sizes continuously:**
   ```
bash
   python scripts/validation/monitor_file_sizes.py docs/ --generate-monitor daily_size_check.py
   
```text

#
## Addressing Issues

1. **Critical Issues (Exit Code 2):**
- File size violations (>500 lines)
- Missing required metadata
- Template compliance failures

2. **Warning Issues (Exit Code 1):**
- Outdated references
- Broken links
- Style guideline violations

3. **Info Issues (Exit Code 0):**
- Optimization opportunities
- Consistency suggestions
- Best practice recommendations

#
## Performance Optimization

- Use `--quick` for fast critical-only validation

- Run validations in parallel with `--parallel`

- Skip URL validation with `--no-urls` for speed

- Use appropriate timeouts for network checks

#
# Troubleshooting

#
## Common Issues

1. **Script Not Found:**
   ```
bash
   
# Ensure you're running from project root
   python scripts/validation/validate_metadata.py docs/
   
```text

2. **Permission Errors:**
   ```
bash
   
# Make scripts executable
   chmod +x scripts/validation/*.py
   
```text

3. **Missing Dependencies:**
   ```
bash
   pip install pyyaml requests
   npm install -g markdownlint-cli
   
```text

4. **Timeout Issues:**
   ```
bash
   
# Increase timeout for slow systems
   python scripts/validation/run_all_validations.py docs/ --timeout 600
   
```text

#
## Debug Mode

Enable verbose output for troubleshooting:
```text
bash
python scripts/validation/run_all_validations.py docs/ --verbose

```text

#
# Contributing

When adding new validation scripts:

1. Follow the established naming pattern

2. Support JSON output format

3. Include comprehensive error handling

4. Add configuration support

5. Update this README

6. Include in `run_all_validations.py`

#
## Script Template

```text
python
#!/usr/bin/env python3
"""
New Validation Script

Description of what this script validates.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    
# Define result structure
    pass

class NewValidator:
    """Validates specific documentation aspect."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
    
    def validate_file(self, file_path: str) -> ValidationResult:
        
# Implement validation logic
        pass
    
    def validate_directory(self, directory_path: str) -> List[ValidationResult]:
        
# Implement directory scanning
        pass

def main():
    """Main execution function."""
    
# Implement CLI interface
    pass

if __name__ == '__main__':
    sys.exit(main())
```text

#
# Support

For issues or questions about the validation system:

1. Check this README for common solutions

2. Review script documentation and help text

3. Examine example outputs in the repository

4. Create an issue with detailed error information

#
# Changelog

#
## Version 1.0.0 (2025-01-08)

- Initial release of comprehensive validation system

- Six core validation scripts

- Comprehensive runner with parallel execution

- Multiple output formats (JSON, HTML, Markdown)

- CI/CD integration support

- Configuration system for customization
