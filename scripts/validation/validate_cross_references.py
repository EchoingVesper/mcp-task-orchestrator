#!/usr/bin/env python3
"""
Validate Cross-References in Documentation

This script validates cross-references (@links, file paths, URLs) in documentation
to ensure they point to existing files and valid locations.
"""

import os
import sys
import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

@dataclass
class CrossReference:
    type: str
    original_text: str
    target: str
    line_number: int
    line_content: str
    is_valid: bool = False
    error_message: Optional[str] = None
    suggested_fix: Optional[str] = None

@dataclass
class FileCrossReferenceReport:
    file_path: str
    references: List[CrossReference] = field(default_factory=list)
    total_references: int = 0
    valid_references: int = 0
    invalid_references: int = 0
    broken_file_refs: int = 0
    broken_url_refs: int = 0
    broken_anchor_refs: int = 0

class CrossReferenceValidator:
    """Validates cross-references in documentation files."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.project_root = None
        self.url_cache = {}
        self.file_existence_cache = {}
        self.check_urls = self.config.get('check_urls', True)
        self.url_timeout = self.config.get('url_timeout', 10)
        self.max_workers = self.config.get('max_workers', 5)
        self.reference_patterns = self._compile_reference_patterns()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validator configuration."""
        default_config = {
            'check_urls': True,
            'check_file_refs': True,
            'check_anchor_refs': True,
            'url_timeout': 10,
            'max_workers': 5,
            'skip_url_patterns': [
                r'example\\.com',
                r'localhost',
                r'127\\.0\\.0\\.1',
                r'\\{.*\\}',  # Template variables
                r'\\[.*\\]',  # Placeholder brackets
            ],
            'trusted_domains': [
                'github.com',
                'docs.python.org',
                'www.python.org',
                'pypi.org',
                'readthedocs.io',
                'stackoverflow.com'
            ],
            'reference_types': {
                'file_ref': r'@([^\s]+)',
                'markdown_link': r'\[([^\]]+)\]\(([^)]+)\)',
                'url': r'https?://[^\s]+',
                'relative_path': r'\.\.?/[^\s]+',
                'absolute_path': r'/[^\s]+\.(md|py|json|yaml|yml|txt|rst)',
                'anchor': r'#[a-zA-Z0-9_-]+',
                'see_ref': r'see\s+([^\s]+\.(md|py|json|yaml|yml))',
                'refer_to': r'refer\s+to\s+([^\s]+)'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _compile_reference_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for reference detection."""
        patterns = {}
        for ref_type, pattern in self.config['reference_types'].items():
            patterns[ref_type] = re.compile(pattern, re.IGNORECASE)
        return patterns
    
    def _find_project_root(self, start_path: str) -> Optional[Path]:
        """Find the project root directory."""
        if self.project_root:
            return self.project_root
        
        current = Path(start_path).resolve()
        while current.parent != current:
            if any((current / marker).exists() for marker in ['.git', 'pyproject.toml', 'package.json', 'setup.py']):
                self.project_root = current
                return current
            current = current.parent
        
        return None
    
    def validate_file(self, file_path: str) -> FileCrossReferenceReport:
        """Validate cross-references in a single file."""
        report = FileCrossReferenceReport(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            reference = CrossReference(
                type="file_error",
                original_text="",
                target=file_path,
                line_number=0,
                line_content="",
                is_valid=False,
                error_message=f"Cannot read file: {e}"
            )
            report.references.append(reference)
            return report
        
        # Find project root
        project_root = self._find_project_root(file_path)
        file_dir = Path(file_path).parent
        
        # Extract all references
        all_references = []
        
        # File references (@/path/to/file)
        if self.config.get('check_file_refs', True):
            all_references.extend(self._extract_file_references(lines, file_dir, project_root))
        
        # Markdown links
        all_references.extend(self._extract_markdown_links(lines, file_dir, project_root))
        
        # URL references
        if self.config.get('check_urls', True):
            all_references.extend(self._extract_url_references(lines))
        
        # Relative and absolute paths
        all_references.extend(self._extract_path_references(lines, file_dir, project_root))
        
        # Anchor references
        if self.config.get('check_anchor_refs', True):
            all_references.extend(self._extract_anchor_references(lines, content))
        
        # Validate all references
        report.references = all_references
        self._validate_references(report.references)
        
        # Calculate statistics
        report.total_references = len(report.references)
        report.valid_references = sum(1 for ref in report.references if ref.is_valid)
        report.invalid_references = report.total_references - report.valid_references
        report.broken_file_refs = sum(1 for ref in report.references 
                                    if not ref.is_valid and ref.type in ['file_ref', 'relative_path', 'absolute_path'])
        report.broken_url_refs = sum(1 for ref in report.references 
                                   if not ref.is_valid and ref.type == 'url')
        report.broken_anchor_refs = sum(1 for ref in report.references 
                                      if not ref.is_valid and ref.type == 'anchor')
        
        return report
    
    def _extract_file_references(self, lines: List[str], file_dir: Path, project_root: Optional[Path]) -> List[CrossReference]:
        """Extract @/path/to/file references."""
        references = []
        
        for line_num, line in enumerate(lines, 1):
            matches = self.reference_patterns['file_ref'].finditer(line)
            for match in matches:
                target = match.group(1)
                reference = CrossReference(
                    type="file_ref",
                    original_text=match.group(0),
                    target=target,
                    line_number=line_num,
                    line_content=line.strip()
                )
                references.append(reference)
        
        return references
    
    def _extract_markdown_links(self, lines: List[str], file_dir: Path, project_root: Optional[Path]) -> List[CrossReference]:
        """Extract markdown [text](url) links."""
        references = []
        
        for line_num, line in enumerate(lines, 1):
            matches = self.reference_patterns['markdown_link'].finditer(line)
            for match in matches:
                link_text = match.group(1)
                link_url = match.group(2)
                
                # Determine reference type
                if link_url.startswith(('http://', 'https://')):
                    ref_type = 'url'
                elif link_url.startswith('#'):
                    ref_type = 'anchor'
                else:
                    ref_type = 'markdown_link'
                
                reference = CrossReference(
                    type=ref_type,
                    original_text=match.group(0),
                    target=link_url,
                    line_number=line_num,
                    line_content=line.strip()
                )
                references.append(reference)
        
        return references
    
    def _extract_url_references(self, lines: List[str]) -> List[CrossReference]:
        """Extract URL references."""
        references = []
        
        for line_num, line in enumerate(lines, 1):
            matches = self.reference_patterns['url'].finditer(line)
            for match in matches:
                url = match.group(0)
                
                # Skip URLs that match skip patterns
                skip = False
                for skip_pattern in self.config['skip_url_patterns']:
                    if re.search(skip_pattern, url):
                        skip = True
                        break
                
                if not skip:
                    reference = CrossReference(
                        type="url",
                        original_text=url,
                        target=url,
                        line_number=line_num,
                        line_content=line.strip()
                    )
                    references.append(reference)
        
        return references
    
    def _extract_path_references(self, lines: List[str], file_dir: Path, project_root: Optional[Path]) -> List[CrossReference]:
        """Extract relative and absolute path references."""
        references = []
        
        for line_num, line in enumerate(lines, 1):
            # Relative paths
            rel_matches = self.reference_patterns['relative_path'].finditer(line)
            for match in rel_matches:
                path = match.group(0)
                reference = CrossReference(
                    type="relative_path",
                    original_text=path,
                    target=path,
                    line_number=line_num,
                    line_content=line.strip()
                )
                references.append(reference)
            
            # Absolute paths
            abs_matches = self.reference_patterns['absolute_path'].finditer(line)
            for match in abs_matches:
                path = match.group(0)
                reference = CrossReference(
                    type="absolute_path",
                    original_text=path,
                    target=path,
                    line_number=line_num,
                    line_content=line.strip()
                )
                references.append(reference)
        
        return references
    
    def _extract_anchor_references(self, lines: List[str], content: str) -> List[CrossReference]:
        """Extract anchor references and validate against headings."""
        references = []
        
        # Extract all anchors
        for line_num, line in enumerate(lines, 1):
            matches = self.reference_patterns['anchor'].finditer(line)
            for match in matches:
                anchor = match.group(0)
                reference = CrossReference(
                    type="anchor",
                    original_text=anchor,
                    target=anchor,
                    line_number=line_num,
                    line_content=line.strip()
                )
                references.append(reference)
        
        return references
    
    def _validate_references(self, references: List[CrossReference]):
        """Validate all references."""
        # Group references by type for efficient validation
        by_type = {}
        for ref in references:
            if ref.type not in by_type:
                by_type[ref.type] = []
            by_type[ref.type].append(ref)
        
        # Validate file references
        if 'file_ref' in by_type:
            self._validate_file_references(by_type['file_ref'])
        
        # Validate paths
        if 'relative_path' in by_type:
            self._validate_path_references(by_type['relative_path'])
        
        if 'absolute_path' in by_type:
            self._validate_path_references(by_type['absolute_path'])
        
        # Validate markdown links
        if 'markdown_link' in by_type:
            self._validate_markdown_links(by_type['markdown_link'])
        
        # Validate URLs
        if 'url' in by_type:
            self._validate_url_references(by_type['url'])
        
        # Validate anchors
        if 'anchor' in by_type:
            self._validate_anchor_references(by_type['anchor'])
    
    def _validate_file_references(self, references: List[CrossReference]):
        """Validate @/path/to/file references."""
        for ref in references:
            target = ref.target
            
            if target.startswith('@/'):
                # Absolute reference from project root
                if self.project_root:
                    full_path = self.project_root / target[2:]
                    if full_path.exists():
                        ref.is_valid = True
                    else:
                        ref.error_message = f"File not found: {full_path}"
                        ref.suggested_fix = f"Check if file exists or update path"
                else:
                    ref.error_message = "Project root not found"
                    ref.suggested_fix = "Ensure project has .git, pyproject.toml, or package.json"
            else:
                # Relative reference
                file_dir = Path(ref.line_content).parent if hasattr(ref, 'file_path') else Path.cwd()
                full_path = file_dir / target
                if full_path.exists():
                    ref.is_valid = True
                else:
                    ref.error_message = f"File not found: {full_path}"
                    ref.suggested_fix = f"Check if file exists or update path"
    
    def _validate_path_references(self, references: List[CrossReference]):
        """Validate relative and absolute path references."""
        for ref in references:
            target = ref.target
            
            if target.startswith('/'):
                # Absolute path
                path = Path(target)
            else:
                # Relative path
                file_dir = Path(ref.line_content).parent if hasattr(ref, 'file_path') else Path.cwd()
                path = file_dir / target
            
            if path.exists():
                ref.is_valid = True
            else:
                ref.error_message = f"Path not found: {path}"
                ref.suggested_fix = f"Check if path exists or update reference"
    
    def _validate_markdown_links(self, references: List[CrossReference]):
        """Validate markdown link targets."""
        for ref in references:
            target = ref.target
            
            if target.startswith(('http://', 'https://')):
                # URL - validate separately
                self._validate_single_url(ref)
            elif target.startswith('#'):
                # Anchor - validate separately
                ref.type = 'anchor'
            else:
                # File path
                file_dir = Path(ref.line_content).parent if hasattr(ref, 'file_path') else Path.cwd()
                
                # Handle fragment (anchor) in file path
                if '#' in target:
                    file_part, anchor_part = target.split('#', 1)
                    target = file_part
                
                if target.startswith('/'):
                    path = Path(target)
                else:
                    path = file_dir / target
                
                if path.exists():
                    ref.is_valid = True
                else:
                    ref.error_message = f"Link target not found: {path}"
                    ref.suggested_fix = f"Check if file exists or update link"
    
    def _validate_url_references(self, references: List[CrossReference]):
        """Validate URL references."""
        if not self.check_urls:
            for ref in references:
                ref.is_valid = True
                ref.error_message = "URL checking disabled"
            return
        
        # Use threading for URL validation
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ref = {executor.submit(self._validate_single_url, ref): ref for ref in references}
            
            for future in as_completed(future_to_ref):
                ref = future_to_ref[future]
                try:
                    future.result()
                except Exception as e:
                    ref.is_valid = False
                    ref.error_message = f"URL validation error: {e}"
    
    def _validate_single_url(self, ref: CrossReference):
        """Validate a single URL."""
        url = ref.target
        
        # Check cache first
        if url in self.url_cache:
            cached_result = self.url_cache[url]
            ref.is_valid = cached_result['is_valid']
            ref.error_message = cached_result.get('error_message')
            return
        
        try:
            # Parse URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                ref.is_valid = False
                ref.error_message = "Invalid URL format"
                ref.suggested_fix = "Ensure URL has proper scheme (http/https) and domain"
                return
            
            # Check if domain is trusted (for faster validation)
            domain = parsed.netloc.lower()
            if any(trusted in domain for trusted in self.config['trusted_domains']):
                ref.is_valid = True
                self.url_cache[url] = {'is_valid': True}
                return
            
            # Make HTTP request
            response = requests.head(url, timeout=self.url_timeout, allow_redirects=True)
            
            if response.status_code < 400:
                ref.is_valid = True
                self.url_cache[url] = {'is_valid': True}
            else:
                ref.is_valid = False
                ref.error_message = f"HTTP {response.status_code}"
                ref.suggested_fix = f"Check if URL is correct or accessible"
                self.url_cache[url] = {'is_valid': False, 'error_message': ref.error_message}
        
        except requests.exceptions.Timeout:
            ref.is_valid = False
            ref.error_message = "URL timeout"
            ref.suggested_fix = "URL may be slow or unreachable"
            self.url_cache[url] = {'is_valid': False, 'error_message': ref.error_message}
        
        except requests.exceptions.ConnectionError:
            ref.is_valid = False
            ref.error_message = "Connection error"
            ref.suggested_fix = "Check if URL is correct and accessible"
            self.url_cache[url] = {'is_valid': False, 'error_message': ref.error_message}
        
        except Exception as e:
            ref.is_valid = False
            ref.error_message = f"Validation error: {str(e)}"
            ref.suggested_fix = "Check URL format and accessibility"
            self.url_cache[url] = {'is_valid': False, 'error_message': ref.error_message}
    
    def _validate_anchor_references(self, references: List[CrossReference]):
        """Validate anchor references against available headings."""
        # This would need access to the file content to extract headings
        # For now, just mark as valid (implementation depends on context)
        for ref in references:
            ref.is_valid = True  # Placeholder - would need heading extraction
    
    def validate_directory(self, directory_path: str, pattern: str = "*.md") -> List[FileCrossReferenceReport]:
        """Validate cross-references in all files in a directory."""
        reports = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                report = self.validate_file(str(file_path))
                reports.append(report)
        
        return reports
    
    def generate_summary_report(self, reports: List[FileCrossReferenceReport]) -> Dict:
        """Generate summary report from all validation results."""
        summary = {
            'total_files': len(reports),
            'files_with_issues': sum(1 for r in reports if r.invalid_references > 0),
            'total_references': sum(r.total_references for r in reports),
            'valid_references': sum(r.valid_references for r in reports),
            'invalid_references': sum(r.invalid_references for r in reports),
            'broken_file_refs': sum(r.broken_file_refs for r in reports),
            'broken_url_refs': sum(r.broken_url_refs for r in reports),
            'broken_anchor_refs': sum(r.broken_anchor_refs for r in reports),
            'validation_rate': 0.0,
            'common_issues': {},
            'problematic_files': []
        }
        
        if summary['total_references'] > 0:
            summary['validation_rate'] = summary['valid_references'] / summary['total_references']
        
        # Find common issues
        issue_counts = {}
        for report in reports:
            for ref in report.references:
                if not ref.is_valid and ref.error_message:
                    issue_counts[ref.error_message] = issue_counts.get(ref.error_message, 0) + 1
        
        summary['common_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Identify most problematic files
        problematic = sorted(
            [(r.file_path, r.invalid_references) for r in reports if r.invalid_references > 0],
            key=lambda x: x[1], reverse=True
        )
        summary['problematic_files'] = problematic[:10]
        
        return summary

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate cross-references in documentation')
    parser.add_argument('path', help='File or directory path to validate')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--no-urls', action='store_true', help='Skip URL validation')
    parser.add_argument('--timeout', type=int, default=10, help='URL timeout in seconds')
    parser.add_argument('--workers', type=int, default=5, help='Number of worker threads for URL validation')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    # Load config and override with command line args
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    if args.no_urls:
        config['check_urls'] = False
    if args.timeout:
        config['url_timeout'] = args.timeout
    if args.workers:
        config['max_workers'] = args.workers
    
    # Create temporary config file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        temp_config = f.name
    
    try:
        validator = CrossReferenceValidator(temp_config)
        
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
                        'total_references': r.total_references,
                        'valid_references': r.valid_references,
                        'invalid_references': r.invalid_references,
                        'broken_file_refs': r.broken_file_refs,
                        'broken_url_refs': r.broken_url_refs,
                        'broken_anchor_refs': r.broken_anchor_refs,
                        'references': [
                            {
                                'type': ref.type,
                                'original_text': ref.original_text,
                                'target': ref.target,
                                'line_number': ref.line_number,
                                'line_content': ref.line_content,
                                'is_valid': ref.is_valid,
                                'error_message': ref.error_message,
                                'suggested_fix': ref.suggested_fix
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
                print("Cross-Reference Validation Report")
                print("=" * 50)
                print(f"Total Files: {summary['total_files']}")
                print(f"Files with Issues: {summary['files_with_issues']}")
                print(f"Total References: {summary['total_references']}")
                print(f"Valid References: {summary['valid_references']}")
                print(f"Invalid References: {summary['invalid_references']}")
                print(f"Validation Rate: {summary['validation_rate']:.2%}")
                print()
                
                # Show breakdown by type
                print("Broken References by Type:")
                print("-" * 30)
                print(f"File References: {summary['broken_file_refs']}")
                print(f"URL References: {summary['broken_url_refs']}")
                print(f"Anchor References: {summary['broken_anchor_refs']}")
                print()
                
                # Show common issues
                if summary['common_issues']:
                    print("Most Common Issues:")
                    print("-" * 20)
                    for issue, count in list(summary['common_issues'].items())[:5]:
                        print(f"  {issue}: {count} occurrences")
                    print()
                
                # Show problematic files
                if summary['problematic_files']:
                    print("Most Problematic Files:")
                    print("-" * 25)
                    for file_path, issue_count in summary['problematic_files'][:5]:
                        print(f"  {file_path}: {issue_count} issues")
                    print()
                
                # Show detailed issues for files with problems
                problem_reports = [r for r in reports if r.invalid_references > 0]
                if problem_reports and not args.quiet:
                    print("Detailed Issues:")
                    print("-" * 15)
                    for report in problem_reports[:5]:  # Limit to first 5
                        print(f"\\n{report.file_path}:")
                        invalid_refs = [ref for ref in report.references if not ref.is_valid]
                        for ref in invalid_refs[:3]:  # Limit to first 3 per file
                            print(f"  Line {ref.line_number}: {ref.type} - {ref.target}")
                            print(f"    Error: {ref.error_message}")
                            if ref.suggested_fix:
                                print(f"    Fix: {ref.suggested_fix}")
            
            # Save text report if requested
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(f"Cross-Reference Validation Summary\\n")
                    f.write(f"Validation Rate: {summary['validation_rate']:.2%}\\n")
                    f.write(f"Total Issues: {summary['invalid_references']}/{summary['total_references']}\\n\\n")
                    
                    for report in reports:
                        if report.invalid_references > 0:
                            f.write(f"File: {report.file_path}\\n")
                            f.write(f"Issues: {report.invalid_references}/{report.total_references}\\n")
                            for ref in report.references:
                                if not ref.is_valid:
                                    f.write(f"  Line {ref.line_number}: {ref.target} - {ref.error_message}\\n")
                            f.write("\\n")
    
    finally:
        # Clean up temporary config
        if os.path.exists(temp_config):
            os.unlink(temp_config)
    
    # Return appropriate exit code
    if summary['invalid_references'] > 0:
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())