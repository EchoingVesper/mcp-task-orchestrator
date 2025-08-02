#!/usr/bin/env python3
"""
Check for Outdated References in Documentation

This script identifies and reports outdated references, patterns, and terminology
that should be updated to align with current architecture and standards.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

class ReferenceType(Enum):
    DEPRECATED_NAMING = "deprecated_naming"
    OUTDATED_ARCHITECTURE = "outdated_architecture"
    BROKEN_LINK = "broken_link"
    LEGACY_PATTERN = "legacy_pattern"
    INCONSISTENT_TERMINOLOGY = "inconsistent_terminology"

@dataclass
class OutdatedReference:
    type: ReferenceType
    pattern: str
    line_number: int
    line_content: str
    suggestion: str
    severity: str = "medium"  # low, medium, high, critical
    context: Optional[str] = None

@dataclass
class FileReferenceReport:
    file_path: str
    references: List[OutdatedReference] = field(default_factory=list)
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0

class OutdatedReferenceChecker:
    """Checks for outdated references and patterns in documentation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.deprecated_patterns = self._load_deprecated_patterns()
        self.architecture_patterns = self._load_architecture_patterns()
        self.terminology_mappings = self._load_terminology_mappings()
        self.link_patterns = self._load_link_patterns()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load checker configuration."""
        default_config = {
            'check_deprecated_naming': True,
            'check_architecture_patterns': True,
            'check_broken_links': True,
            'check_legacy_patterns': True,
            'check_terminology': True,
            'severity_levels': {
                'deprecated_naming': 'medium',
                'outdated_architecture': 'high',
                'broken_link': 'medium',
                'legacy_pattern': 'low',
                'inconsistent_terminology': 'low'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_deprecated_patterns(self) -> List[Tuple[str, str, str]]:
        """Load deprecated naming patterns."""
        return [
            # (pattern, description, suggestion)
            (r'\btask_[a-zA-Z_]+', 'Task-based naming pattern', 'Use feature-based or component-based naming'),
            (r'\bsubtask_[a-zA-Z_]+', 'Subtask-based naming pattern', 'Use component-based naming'),
            (r'\bTask\s+[A-Z][a-zA-Z]*', 'Task class references', 'Use WorkItem, Component, or specific entity'),
            (r'\bSubtask\s+[A-Z][a-zA-Z]*', 'Subtask class references', 'Use WorkItem or Component'),
            (r'\blegacy_[a-zA-Z_]+', 'Legacy naming pattern', 'Update to current naming conventions'),
            (r'\bold_[a-zA-Z_]+', 'Old naming pattern', 'Use current naming conventions'),
            (r'\btemp_[a-zA-Z_]+', 'Temporary naming pattern', 'Use proper naming or remove if obsolete'),
            (r'\btest_[a-zA-Z_]+_old', 'Old test naming', 'Update test names to current standards'),
            (r'\bdeprecated_[a-zA-Z_]+', 'Deprecated references', 'Remove or update to current implementation'),
            (r'\bbackup_[a-zA-Z_]+', 'Backup naming pattern', 'Use proper naming or move to archives'),
        ]
    
    def _load_architecture_patterns(self) -> List[Tuple[str, str, str]]:
        """Load outdated architecture patterns."""
        return [
            # (pattern, description, suggestion)
            (r'mcp_task_orchestrator\.core', 'Old core module reference', 'Use mcp_task_orchestrator.orchestrator.task_orchestration_service'),
            (r'mcp_task_orchestrator\.specialists', 'Old specialists module', 'Use mcp_task_orchestrator.orchestrator.specialist_management_service'),
            (r'mcp_task_orchestrator\.state', 'Old state module', 'Use mcp_task_orchestrator.orchestrator.orchestration_state_manager'),
            (r'from\s+\.\s+import\s+Task', 'Old Task import', 'Use domain entities or WorkItem'),
            (r'from\s+\.\s+import\s+Subtask', 'Old Subtask import', 'Use domain entities or WorkItem'),
            (r'TaskOrchestrator\(', 'Old TaskOrchestrator class', 'Use TaskOrchestrationService'),
            (r'SpecialistManager\(', 'Old SpecialistManager class', 'Use SpecialistManagementService'),
            (r'StateManager\(', 'Old StateManager class', 'Use OrchestrationStateManager'),
            (r'simple_task_model', 'Old simple task model', 'Use generic task model'),
            (r'basic_orchestration', 'Old basic orchestration', 'Use enhanced orchestration with DI'),
            (r'legacy_database', 'Legacy database references', 'Use infrastructure.database with repositories'),
            (r'direct_sqlite', 'Direct SQLite usage', 'Use repository pattern with DI'),
            (r'manual_dependency', 'Manual dependency management', 'Use dependency injection container'),
            (r'hardcoded_config', 'Hardcoded configuration', 'Use environment-aware configuration'),
        ]
    
    def _load_terminology_mappings(self) -> Dict[str, str]:
        """Load terminology mappings for consistency."""
        return {
            'task orchestration': 'work orchestration',
            'task management': 'work management',
            'task breakdown': 'work breakdown',
            'task execution': 'work execution',
            'task lifecycle': 'work lifecycle',
            'task handler': 'work handler',
            'task processor': 'work processor',
            'task queue': 'work queue',
            'task scheduler': 'work scheduler',
            'task coordinator': 'work coordinator',
            'subtask': 'work item',
            'sub-task': 'work item',
            'task dependency': 'work dependency',
            'task state': 'work state',
            'task status': 'work status',
            'task result': 'work result',
            'task artifact': 'work artifact',
            'task output': 'work output',
            'task input': 'work input',
            'task configuration': 'work configuration',
            'task template': 'work template',
            'task pattern': 'work pattern',
            'task workflow': 'work workflow',
            'task pipeline': 'work pipeline',
        }
    
    def _load_link_patterns(self) -> List[Tuple[str, str]]:
        """Load link patterns to check for broken references."""
        return [
            (r'@([^\s]+)', 'File reference'),
            (r'\[([^\]]+)\]\(([^)]+)\)', 'Markdown link'),
            (r'\bhttps?://[^\s]+', 'URL link'),
            (r'\bfile://[^\s]+', 'File protocol link'),
            (r'\.\.?/[^\s]+', 'Relative path'),
            (r'/[^\s]+\.(md|py|json|yaml|yml)', 'Absolute file path'),
            (r'see\s+([^\s]+\.md)', 'See reference'),
            (r'refer\s+to\s+([^\s]+)', 'Refer to reference'),
        ]
    
    def check_file(self, file_path: str) -> FileReferenceReport:
        """Check a single file for outdated references."""
        report = FileReferenceReport(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            reference = OutdatedReference(
                type=ReferenceType.BROKEN_LINK,
                pattern="File read error",
                line_number=0,
                line_content="",
                suggestion=f"Fix file access issue: {e}",
                severity="critical"
            )
            report.references.append(reference)
            return report
        
        # Check deprecated naming patterns
        if self.config.get('check_deprecated_naming', True):
            self._check_deprecated_patterns(lines, report)
        
        # Check architecture patterns
        if self.config.get('check_architecture_patterns', True):
            self._check_architecture_patterns(lines, report)
        
        # Check broken links
        if self.config.get('check_broken_links', True):
            self._check_broken_links(lines, report, file_path)
        
        # Check legacy patterns
        if self.config.get('check_legacy_patterns', True):
            self._check_legacy_patterns(lines, report)
        
        # Check terminology consistency
        if self.config.get('check_terminology', True):
            self._check_terminology_consistency(lines, report)
        
        # Calculate summary statistics
        self._calculate_summary_stats(report)
        
        return report
    
    def _check_deprecated_patterns(self, lines: List[str], report: FileReferenceReport):
        """Check for deprecated naming patterns."""
        for line_num, line in enumerate(lines, 1):
            for pattern, description, suggestion in self.deprecated_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    reference = OutdatedReference(
                        type=ReferenceType.DEPRECATED_NAMING,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=suggestion,
                        severity=self.config['severity_levels']['deprecated_naming'],
                        context=description
                    )
                    report.references.append(reference)
    
    def _check_architecture_patterns(self, lines: List[str], report: FileReferenceReport):
        """Check for outdated architecture patterns."""
        for line_num, line in enumerate(lines, 1):
            for pattern, description, suggestion in self.architecture_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    reference = OutdatedReference(
                        type=ReferenceType.OUTDATED_ARCHITECTURE,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=suggestion,
                        severity=self.config['severity_levels']['outdated_architecture'],
                        context=description
                    )
                    report.references.append(reference)
    
    def _check_broken_links(self, lines: List[str], report: FileReferenceReport, file_path: str):
        """Check for broken links and references."""
        base_dir = Path(file_path).parent
        
        for line_num, line in enumerate(lines, 1):
            # Check file references (@/path/to/file)
            file_refs = re.finditer(r'@([^\\s]+)', line)
            for match in file_refs:
                ref_path = match.group(1)
                if not self._is_valid_file_reference(ref_path, base_dir):
                    reference = OutdatedReference(
                        type=ReferenceType.BROKEN_LINK,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=f"Fix broken file reference: {ref_path}",
                        severity=self.config['severity_levels']['broken_link'],
                        context="File reference"
                    )
                    report.references.append(reference)
            
            # Check markdown links
            md_links = re.finditer(r'\\[([^\\]]+)\\]\\(([^)]+)\\)', line)
            for match in md_links:
                link_text = match.group(1)
                link_url = match.group(2)
                if not self._is_valid_markdown_link(link_url, base_dir):
                    reference = OutdatedReference(
                        type=ReferenceType.BROKEN_LINK,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=f"Fix broken markdown link: {link_url}",
                        severity=self.config['severity_levels']['broken_link'],
                        context="Markdown link"
                    )
                    report.references.append(reference)
            
            # Check relative paths
            rel_paths = re.finditer(r'\\.\\.?/[^\\s]+', line)
            for match in rel_paths:
                path = match.group()
                if not self._is_valid_relative_path(path, base_dir):
                    reference = OutdatedReference(
                        type=ReferenceType.BROKEN_LINK,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=f"Fix broken relative path: {path}",
                        severity=self.config['severity_levels']['broken_link'],
                        context="Relative path"
                    )
                    report.references.append(reference)
    
    def _check_legacy_patterns(self, lines: List[str], report: FileReferenceReport):
        """Check for legacy patterns that should be updated."""
        legacy_patterns = [
            (r'\\bTODO\\b', 'TODO marker', 'Complete or remove TODO items'),
            (r'\\bFIXME\\b', 'FIXME marker', 'Fix or remove FIXME items'),
            (r'\\bXXX\\b', 'XXX marker', 'Address or remove XXX items'),
            (r'\\bHACK\\b', 'HACK marker', 'Replace hack with proper solution'),
            (r'\\bTEMP\\b', 'TEMP marker', 'Replace temporary solution'),
            (r'\\bDEBUG\\b', 'DEBUG marker', 'Remove debug code'),
            (r'print\\s*\\(', 'Print statement', 'Use proper logging'),
            (r'console\\.log\\s*\\(', 'Console.log', 'Use proper logging'),
            (r'\\btest\\b.*\\bonly\\b', 'Test only marker', 'Remove test isolation'),
            (r'\\bskip\\b.*\\btest\\b', 'Skip test marker', 'Enable or remove skipped tests'),
            (r'\\bcoming\\s+soon\\b', 'Coming soon placeholder', 'Provide actual content'),
            (r'\\bunder\\s+construction\\b', 'Under construction', 'Complete or remove'),
            (r'\\bto\\s+be\\s+determined\\b', 'TBD marker', 'Determine value or remove'),
            (r'\\bplaceholder\\b', 'Placeholder text', 'Replace with actual content'),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, description, suggestion in legacy_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    reference = OutdatedReference(
                        type=ReferenceType.LEGACY_PATTERN,
                        pattern=match.group(),
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=suggestion,
                        severity=self.config['severity_levels']['legacy_pattern'],
                        context=description
                    )
                    report.references.append(reference)
    
    def _check_terminology_consistency(self, lines: List[str], report: FileReferenceReport):
        """Check for inconsistent terminology usage."""
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            for old_term, new_term in self.terminology_mappings.items():
                if old_term in line_lower:
                    reference = OutdatedReference(
                        type=ReferenceType.INCONSISTENT_TERMINOLOGY,
                        pattern=old_term,
                        line_number=line_num,
                        line_content=line.strip(),
                        suggestion=f"Consider using '{new_term}' instead of '{old_term}'",
                        severity=self.config['severity_levels']['inconsistent_terminology'],
                        context="Terminology consistency"
                    )
                    report.references.append(reference)
    
    def _is_valid_file_reference(self, ref_path: str, base_dir: Path) -> bool:
        """Check if a file reference is valid."""
        if ref_path.startswith('@/'):
            # Absolute reference from project root
            project_root = self._find_project_root(base_dir)
            if project_root:
                full_path = project_root / ref_path[2:]
                return full_path.exists()
        elif ref_path.startswith('/'):
            # System absolute path
            return Path(ref_path).exists()
        else:
            # Relative path
            full_path = base_dir / ref_path
            return full_path.exists()
        
        return False
    
    def _is_valid_markdown_link(self, link_url: str, base_dir: Path) -> bool:
        """Check if a markdown link is valid."""
        # Skip external URLs
        if link_url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            return True
        
        # Check local file links
        if link_url.startswith('#'):
            # Anchor link within same document
            return True
        
        # Check file existence
        if '/' in link_url:
            full_path = base_dir / link_url
            return full_path.exists()
        
        return True
    
    def _is_valid_relative_path(self, path: str, base_dir: Path) -> bool:
        """Check if a relative path is valid."""
        full_path = base_dir / path
        return full_path.exists()
    
    def _find_project_root(self, start_dir: Path) -> Optional[Path]:
        """Find project root directory."""
        current = start_dir
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'pyproject.toml', 'package.json']):
                return current
            current = current.parent
        return None
    
    def _calculate_summary_stats(self, report: FileReferenceReport):
        """Calculate summary statistics for the report."""
        report.total_issues = len(report.references)
        report.critical_issues = sum(1 for ref in report.references if ref.severity == 'critical')
        report.high_issues = sum(1 for ref in report.references if ref.severity == 'high')
        report.medium_issues = sum(1 for ref in report.references if ref.severity == 'medium')
        report.low_issues = sum(1 for ref in report.references if ref.severity == 'low')
    
    def check_directory(self, directory_path: str, pattern: str = "*.md") -> List[FileReferenceReport]:
        """Check all files in a directory for outdated references."""
        reports = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                report = self.check_file(str(file_path))
                reports.append(report)
        
        return reports
    
    def generate_summary_report(self, reports: List[FileReferenceReport]) -> Dict:
        """Generate summary report from all file reports."""
        total_files = len(reports)
        files_with_issues = sum(1 for r in reports if r.total_issues > 0)
        
        summary = {
            'total_files': total_files,
            'files_with_issues': files_with_issues,
            'clean_files': total_files - files_with_issues,
            'total_issues': sum(r.total_issues for r in reports),
            'critical_issues': sum(r.critical_issues for r in reports),
            'high_issues': sum(r.high_issues for r in reports),
            'medium_issues': sum(r.medium_issues for r in reports),
            'low_issues': sum(r.low_issues for r in reports),
            'issues_by_type': {},
            'most_common_issues': {},
            'files_by_severity': {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
        }
        
        # Analyze issues by type
        type_counts = {}
        issue_counts = {}
        
        for report in reports:
            for ref in report.references:
                type_key = ref.type.value
                type_counts[type_key] = type_counts.get(type_key, 0) + 1
                
                issue_key = f"{ref.context or ref.type.value}: {ref.pattern}"
                issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
        
        summary['issues_by_type'] = type_counts
        summary['most_common_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Categorize files by highest severity
        for report in reports:
            if report.critical_issues > 0:
                summary['files_by_severity']['critical'].append(report.file_path)
            elif report.high_issues > 0:
                summary['files_by_severity']['high'].append(report.file_path)
            elif report.medium_issues > 0:
                summary['files_by_severity']['medium'].append(report.file_path)
            elif report.low_issues > 0:
                summary['files_by_severity']['low'].append(report.file_path)
        
        return summary

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check for outdated references in documentation')
    parser.add_argument('path', help='File or directory path to check')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'], 
                       help='Minimum severity level to report')
    parser.add_argument('--type', choices=[t.value for t in ReferenceType], 
                       help='Filter by reference type')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    checker = OutdatedReferenceChecker(args.config)
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run check
    if path.is_file():
        reports = [checker.check_file(str(path))]
    else:
        reports = checker.check_directory(str(path))
    
    if not reports:
        print("No files found to check")
        return 0
    
    # Apply filters
    if args.severity:
        severity_order = ['low', 'medium', 'high', 'critical']
        min_level = severity_order.index(args.severity)
        for report in reports:
            report.references = [ref for ref in report.references 
                               if severity_order.index(ref.severity) >= min_level]
    
    if args.type:
        for report in reports:
            report.references = [ref for ref in report.references 
                               if ref.type.value == args.type]
    
    # Generate summary
    summary = checker.generate_summary_report(reports)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'summary': summary,
            'reports': [
                {
                    'file_path': r.file_path,
                    'total_issues': r.total_issues,
                    'critical_issues': r.critical_issues,
                    'high_issues': r.high_issues,
                    'medium_issues': r.medium_issues,
                    'low_issues': r.low_issues,
                    'references': [
                        {
                            'type': ref.type.value,
                            'pattern': ref.pattern,
                            'line_number': ref.line_number,
                            'line_content': ref.line_content,
                            'suggestion': ref.suggestion,
                            'severity': ref.severity,
                            'context': ref.context
                        } for ref in r.references
                    ]
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
            print("Outdated References Report")
            print("=" * 50)
            print(f"Total Files: {summary['total_files']}")
            print(f"Files with Issues: {summary['files_with_issues']}")
            print(f"Clean Files: {summary['clean_files']}")
            print(f"Total Issues: {summary['total_issues']}")
            print(f"Critical: {summary['critical_issues']}, High: {summary['high_issues']}, Medium: {summary['medium_issues']}, Low: {summary['low_issues']}")
            print()
            
            # Show issues by type
            if summary['issues_by_type']:
                print("Issues by Type:")
                print("-" * 20)
                for issue_type, count in summary['issues_by_type'].items():
                    print(f"  {issue_type}: {count}")
                print()
            
            # Show files with issues
            problem_reports = [r for r in reports if r.total_issues > 0]
            if problem_reports:
                print("Files with Issues:")
                print("-" * 20)
                for report in problem_reports:
                    print(f"\\n{report.file_path} ({report.total_issues} issues):")
                    for ref in report.references:
                        print(f"  {ref.severity.upper()}: {ref.pattern} (line {ref.line_number})")
                        print(f"    Context: {ref.context or ref.type.value}")
                        print(f"    Suggestion: {ref.suggestion}")
                        if ref.line_content:
                            print(f"    Line: {ref.line_content}")
                        print()
        
        # Save text report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"Outdated References Summary: {summary['files_with_issues']}/{summary['total_files']} files have issues\\n")
                f.write(f"Total Issues: {summary['total_issues']}\\n\\n")
                for report in reports:
                    if report.total_issues > 0:
                        f.write(f"File: {report.file_path}\\n")
                        f.write(f"Issues: {report.total_issues}\\n")
                        for ref in report.references:
                            f.write(f"  {ref.severity.upper()}: {ref.pattern} (line {ref.line_number})\\n")
                            f.write(f"    {ref.suggestion}\\n")
                        f.write("\\n")
    
    # Return appropriate exit code
    if summary['critical_issues'] > 0 or summary['high_issues'] > 0:
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())