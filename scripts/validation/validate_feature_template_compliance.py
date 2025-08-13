#!/usr/bin/env python3
"""
Validate Feature Documentation Template Compliance

This script validates that feature documentation files follow the standardized template
structure and contain all required elements.
"""

import os
import sys
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass
class ValidationResult:
    level: ValidationLevel
    message: str
    line_number: Optional[int] = None
    section: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class FileValidationReport:
    file_path: str
    passed: bool = True
    results: List[ValidationResult] = field(default_factory=list)
    metrics: Dict[str, int] = field(default_factory=dict)

class FeatureDocumentationValidator:
    """Validates feature documentation against standardized template requirements."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.required_metadata = self.config.get('required_metadata', [])
        self.required_sections = self.config.get('required_sections', [])
        self.status_values = self.config.get('status_values', [])
        self.priority_values = self.config.get('priority_values', [])
        self.category_values = self.config.get('category_values', [])
        self.max_file_size = self.config.get('max_file_size', 500)
        self.max_section_size = self.config.get('max_section_size', 100)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validation configuration."""
        default_config = {
            'required_metadata': ['title', 'status', 'priority', 'category', 'version', 'description'],
            'required_sections': ['Overview', 'Requirements', 'Implementation', 'Testing', 'Dependencies'],
            'status_values': ['DRAFT', 'REVIEW', 'APPROVED', 'IMPLEMENTED', 'COMPLETED', 'DEPRECATED'],
            'priority_values': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            'category_values': ['CORE', 'ENHANCEMENT', 'INTEGRATION', 'PERFORMANCE', 'SECURITY', 'TESTING', 'DOCUMENTATION'],
            'max_file_size': 500,
            'max_section_size': 100
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def validate_file(self, file_path: str) -> FileValidationReport:
        """Validate a single feature documentation file."""
        report = FileValidationReport(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Failed to read file: {e}"
            ))
            report.passed = False
            return report
        
        # Basic file metrics
        report.metrics['total_lines'] = len(lines)
        report.metrics['total_characters'] = len(content)
        
        # Validate file size
        if len(lines) > self.max_file_size:
            report.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"File exceeds recommended size limit ({len(lines)} > {self.max_file_size} lines)",
                suggestion="Consider breaking into smaller files or modules"
            ))
        
        # Extract and validate metadata
        metadata = self._extract_metadata(content, lines, report)
        if metadata:
            self._validate_metadata(metadata, report)
        
        # Validate document structure
        self._validate_structure(content, lines, report)
        
        # Validate sections
        self._validate_sections(content, lines, report)
        
        # Validate content quality
        self._validate_content_quality(content, lines, report)
        
        # Check for deprecated patterns
        self._check_deprecated_patterns(content, lines, report)
        
        # Final pass/fail determination
        report.passed = not any(r.level == ValidationLevel.ERROR for r in report.results)
        
        return report
    
    def _extract_metadata(self, content: str, lines: List[str], report: FileValidationReport) -> Optional[Dict]:
        """Extract YAML frontmatter metadata."""
        if not content.startswith('---'):
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="Missing YAML frontmatter metadata",
                line_number=1,
                suggestion="Add metadata block at the beginning of the file"
            ))
            return None
        
        # Find end of frontmatter
        try:
            end_idx = content.index('\\n---\\n', 4)
            frontmatter = content[4:end_idx]
            metadata = yaml.safe_load(frontmatter)
            return metadata
        except (ValueError, yaml.YAMLError) as e:
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Invalid YAML frontmatter: {e}",
                line_number=1,
                suggestion="Fix YAML syntax in frontmatter"
            ))
            return None
    
    def _validate_metadata(self, metadata: Dict, report: FileValidationReport):
        """Validate metadata fields and values."""
        # Check required fields
        for field in self.required_metadata:
            if field not in metadata:
                report.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Missing required metadata field: {field}",
                    suggestion=f"Add '{field}' to frontmatter"
                ))
            elif not metadata[field]:
                report.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Empty metadata field: {field}",
                    suggestion=f"Provide value for '{field}'"
                ))
        
        # Validate enum values
        if 'status' in metadata and metadata['status'] not in self.status_values:
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Invalid status value: {metadata['status']}",
                suggestion=f"Use one of: {', '.join(self.status_values)}"
            ))
        
        if 'priority' in metadata and metadata['priority'] not in self.priority_values:
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Invalid priority value: {metadata['priority']}",
                suggestion=f"Use one of: {', '.join(self.priority_values)}"
            ))
        
        if 'category' in metadata and metadata['category'] not in self.category_values:
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Invalid category value: {metadata['category']}",
                suggestion=f"Use one of: {', '.join(self.category_values)}"
            ))
        
        # Validate version format
        if 'version' in metadata:
            version_pattern = r'^\\d+\\.\\d+(\\.\\d+)?$'
            if not re.match(version_pattern, str(metadata['version'])):
                report.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Invalid version format: {metadata['version']}",
                    suggestion="Use semantic versioning (e.g., 1.0.0)"
                ))
    
    def _validate_structure(self, content: str, lines: List[str], report: FileValidationReport):
        """Validate document structure."""
        # Check for main title (H1)
        if not re.search(r'^# .+', content, re.MULTILINE):
            report.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="Missing main title (H1 heading)",
                suggestion="Add main title with '# Title' format"
            ))
        
        # Check for multiple H1 headings
        h1_matches = re.findall(r'^# .+', content, re.MULTILINE)
        if len(h1_matches) > 1:
            report.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Multiple H1 headings found ({len(h1_matches)})",
                suggestion="Use only one H1 heading for the main title"
            ))
        
        # Check heading hierarchy
        headings = re.findall(r'^(#+) (.+)', content, re.MULTILINE)
        for i, (level, text) in enumerate(headings):
            if i > 0:
                prev_level = len(headings[i-1][0])
                curr_level = len(level)
                if curr_level > prev_level + 1:
                    line_num = self._find_line_number(content, f"{level} {text}")
                    report.results.append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        message=f"Heading hierarchy skip: {level} {text}",
                        line_number=line_num,
                        suggestion="Don't skip heading levels"
                    ))
    
    def _validate_sections(self, content: str, lines: List[str], report: FileValidationReport):
        """Validate required sections."""
        found_sections = []
        section_sizes = {}
        
        # Extract sections
        sections = re.findall(r'^## (.+)', content, re.MULTILINE)
        for section in sections:
            found_sections.append(section)
            # Calculate section size
            section_start = content.find(f"## {section}")
            next_section = content.find("## ", section_start + 1)
            if next_section == -1:
                next_section = len(content)
            section_content = content[section_start:next_section]
            section_lines = len(section_content.splitlines())
            section_sizes[section] = section_lines
        
        # Check for required sections
        for required_section in self.required_sections:
            if required_section not in found_sections:
                report.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Missing required section: {required_section}",
                    suggestion=f"Add '## {required_section}' section"
                ))
        
        # Check section sizes
        for section, size in section_sizes.items():
            if size > self.max_section_size:
                report.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Section '{section}' is too large ({size} > {self.max_section_size} lines)",
                    suggestion=f"Consider breaking '{section}' into subsections"
                ))
        
        report.metrics['sections_found'] = len(found_sections)
        report.metrics['sections_required'] = len(self.required_sections)
    
    def _validate_content_quality(self, content: str, lines: List[str], report: FileValidationReport):
        """Validate content quality indicators."""
        # Check for empty sections
        empty_sections = re.findall(r'^## (.+)\\n\\n## ', content, re.MULTILINE)
        for section in empty_sections:
            report.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"Empty section: {section}",
                suggestion=f"Add content to '{section}' section or remove it"
            ))
        
        # Check for TODO markers
        todo_matches = re.finditer(r'TODO|FIXME|XXX', content, re.IGNORECASE)
        for match in todo_matches:
            line_num = content[:match.start()].count('\\n') + 1
            report.results.append(ValidationResult(
                level=ValidationLevel.INFO,
                message=f"TODO marker found: {match.group()}",
                line_number=line_num,
                suggestion="Complete or remove TODO items before approval"
            ))
        
        # Check for placeholder text
        placeholder_patterns = [
            r'\\[.*\\]',  # [placeholder]
            r'TBD|To be determined',
            r'Coming soon',
            r'Under construction'
        ]
        
        for pattern in placeholder_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\\n') + 1
                report.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Placeholder text found: {match.group()}",
                    line_number=line_num,
                    suggestion="Replace placeholder with actual content"
                ))
    
    def _check_deprecated_patterns(self, content: str, lines: List[str], report: FileValidationReport):
        """Check for deprecated patterns that should be updated."""
        deprecated_patterns = [
            (r'\\btask_', 'task_* naming pattern', 'Use feature-based naming'),
            (r'\\bsubtask_', 'subtask_* naming pattern', 'Use component-based naming'),
            (r'\\bTask\\b(?!\\s*:)', 'Task class references', 'Use WorkItem or specific entity'),
            (r'\\bSubtask\\b', 'Subtask references', 'Use WorkItem or Component'),
            (r'legacy_', 'legacy_* references', 'Update to current architecture'),
            (r'old_', 'old_* references', 'Remove or update references')
        ]
        
        for pattern, description, suggestion in deprecated_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\\n') + 1
                report.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Deprecated pattern found: {description}",
                    line_number=line_num,
                    suggestion=suggestion
                ))
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """Find line number for given text."""
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if search_text in line:
                return i + 1
        return 0
    
    def validate_directory(self, directory_path: str, pattern: str = "*.md") -> List[FileValidationReport]:
        """Validate all feature documentation files in a directory."""
        reports = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                report = self.validate_file(str(file_path))
                reports.append(report)
        
        return reports
    
    def generate_summary_report(self, reports: List[FileValidationReport]) -> Dict:
        """Generate summary report from validation results."""
        summary = {
            'total_files': len(reports),
            'passed_files': sum(1 for r in reports if r.passed),
            'failed_files': sum(1 for r in reports if not r.passed),
            'total_errors': sum(len([res for res in r.results if res.level == ValidationLevel.ERROR]) for r in reports),
            'total_warnings': sum(len([res for res in r.results if res.level == ValidationLevel.WARNING]) for r in reports),
            'total_info': sum(len([res for res in r.results if res.level == ValidationLevel.INFO]) for r in reports),
            'files_by_status': {},
            'common_issues': {},
            'metrics': {
                'average_file_size': sum(r.metrics.get('total_lines', 0) for r in reports) / len(reports) if reports else 0,
                'largest_file': max((r.metrics.get('total_lines', 0) for r in reports), default=0),
                'total_sections': sum(r.metrics.get('sections_found', 0) for r in reports)
            }
        }
        
        # Analyze common issues
        issue_counts = {}
        for report in reports:
            for result in report.results:
                key = f"{result.level.value}: {result.message.split(':')[0]}"
                issue_counts[key] = issue_counts.get(key, 0) + 1
        
        summary['common_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return summary

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate feature documentation template compliance')
    parser.add_argument('path', help='File or directory path to validate')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    parser.add_argument('--fail-on-warnings', action='store_true', help='Fail on warnings')
    
    args = parser.parse_args()
    
    validator = FeatureDocumentationValidator(args.config)
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run validation
    if path.is_file():
        reports = [validator.validate_file(str(path))]
    else:
        reports = validator.validate_directory(str(path))
    
    if not reports:
        print("No files found to validate")
        return 0
    
    # Generate summary
    summary = validator.generate_summary_report(reports)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'summary': summary,
            'reports': [
                {
                    'file_path': r.file_path,
                    'passed': r.passed,
                    'results': [
                        {
                            'level': res.level.value,
                            'message': res.message,
                            'line_number': res.line_number,
                            'section': res.section,
                            'suggestion': res.suggestion
                        } for res in r.results
                    ],
                    'metrics': r.metrics
                } for r in reports
            ]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
        else:
            print(json.dumps(output_data, indent=2))
    else:
        # Text output
        if not args.quiet:
            print("Feature Documentation Validation Report")
            print("=" * 50)
            print(f"Total Files: {summary['total_files']}")
            print(f"Passed: {summary['passed_files']}")
            print(f"Failed: {summary['failed_files']}")
            print(f"Errors: {summary['total_errors']}")
            print(f"Warnings: {summary['total_warnings']}")
            print(f"Info: {summary['total_info']}")
            print()
            
            # Show failed files
            failed_reports = [r for r in reports if not r.passed]
            if failed_reports:
                print("Failed Files:")
                print("-" * 20)
                for report in failed_reports:
                    print(f"\\n{report.file_path}:")
                    for result in report.results:
                        if result.level == ValidationLevel.ERROR:
                            line_info = f" (line {result.line_number})" if result.line_number else ""
                            print(f"  ERROR: {result.message}{line_info}")
                            if result.suggestion:
                                print(f"    Suggestion: {result.suggestion}")
            
            # Show warnings if requested
            if not args.fail_on_warnings:
                warning_reports = [r for r in reports if any(res.level == ValidationLevel.WARNING for res in r.results)]
                if warning_reports:
                    print("\\nWarnings:")
                    print("-" * 20)
                    for report in warning_reports:
                        warnings = [res for res in report.results if res.level == ValidationLevel.WARNING]
                        if warnings:
                            print(f"\\n{report.file_path}:")
                            for result in warnings:
                                line_info = f" (line {result.line_number})" if result.line_number else ""
                                print(f"  WARNING: {result.message}{line_info}")
        
        # Save text report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"Validation Summary: {summary['passed_files']}/{summary['total_files']} passed\\n")
                f.write(f"Errors: {summary['total_errors']}, Warnings: {summary['total_warnings']}\\n\\n")
                for report in reports:
                    f.write(f"File: {report.file_path}\\n")
                    f.write(f"Status: {'PASSED' if report.passed else 'FAILED'}\\n")
                    for result in report.results:
                        f.write(f"  {result.level.value}: {result.message}\\n")
                    f.write("\\n")
    
    # Return appropriate exit code
    if summary['total_errors'] > 0:
        return 1
    if args.fail_on_warnings and summary['total_warnings'] > 0:
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())