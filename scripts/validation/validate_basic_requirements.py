#!/usr/bin/env python3
"""
Basic Documentation Requirements Validator

This script validates basic documentation requirements without external dependencies.
It provides a simplified but functional validation system.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class BasicValidationResult:
    file_path: str
    has_frontmatter: bool = False
    has_title: bool = False
    has_sections: bool = False
    file_size_lines: int = 0
    file_size_bytes: int = 0
    is_oversized: bool = False
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class BasicDocumentationValidator:
    """Basic documentation validator without external dependencies."""
    
    def __init__(self):
        self.max_lines = 500  # Claude Code limit
        self.max_bytes = 2 * 1024 * 1024  # 2MB limit
        
    def validate_file(self, file_path: str) -> BasicValidationResult:
        """Validate a single file with basic checks."""
        result = BasicValidationResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            result.issues.append(f"Cannot read file: {e}")
            return result
        
        # Basic file size checks
        result.file_size_lines = len(lines)
        result.file_size_bytes = len(content.encode('utf-8'))
        
        if result.file_size_lines > self.max_lines:
            result.is_oversized = True
            result.issues.append(f"File exceeds {self.max_lines} lines ({result.file_size_lines} lines) - may cause Claude Code issues")
        
        if result.file_size_bytes > self.max_bytes:
            result.is_oversized = True
            result.issues.append(f"File exceeds 2MB ({result.file_size_bytes / (1024*1024):.2f}MB) - may crash Claude Code")
        
        # Check for frontmatter
        if content.startswith('---'):
            try:
                end_idx = content.find('\\n---\\n', 4)
                if end_idx > 0:
                    result.has_frontmatter = True
                else:
                    result.issues.append("Unclosed YAML frontmatter")
            except:
                result.warnings.append("Could not parse frontmatter")
        else:
            result.issues.append("Missing YAML frontmatter")
        
        # Check for title (H1 heading)
        if re.search(r'^# .+', content, re.MULTILINE):
            result.has_title = True
        else:
            result.issues.append("Missing main title (H1 heading)")
        
        # Check for sections (H2+ headings)
        if re.search(r'^## .+', content, re.MULTILINE):
            result.has_sections = True
        else:
            result.warnings.append("No sections found (H2+ headings)")
        
        # Check for deprecated patterns
        deprecated_patterns = [
            (r'\\btask_\\w+', 'task_* naming pattern (deprecated)'),
            (r'\\bsubtask_\\w+', 'subtask_* naming pattern (deprecated)'),
            (r'TODO|FIXME|XXX', 'TODO/FIXME markers'),
            (r'\\[.*\\]', 'placeholder text in brackets'),
            (r'TBD|To be determined', 'TBD placeholder text'),
        ]
        
        for pattern, description in deprecated_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                result.warnings.append(f"Found {description}")
        
        # Check for broken file references
        file_refs = re.findall(r'@([^\\s]+)', content)
        for ref in file_refs:
            if ref.startswith('/'):
                ref_path = Path(ref)
            else:
                ref_path = Path(file_path).parent / ref
            
            if not ref_path.exists():
                result.warnings.append(f"Broken file reference: {ref}")
        
        return result
    
    def validate_directory(self, directory_path: str, pattern: str = "*.md") -> List[BasicValidationResult]:
        """Validate all files in a directory."""
        results = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                result = self.validate_file(str(file_path))
                results.append(result)
        
        return results
    
    def generate_summary(self, results: List[BasicValidationResult]) -> Dict[str, Any]:
        """Generate validation summary."""
        total_files = len(results)
        files_with_issues = sum(1 for r in results if r.issues)
        files_with_warnings = sum(1 for r in results if r.warnings)
        oversized_files = sum(1 for r in results if r.is_oversized)
        files_with_frontmatter = sum(1 for r in results if r.has_frontmatter)
        files_with_title = sum(1 for r in results if r.has_title)
        files_with_sections = sum(1 for r in results if r.has_sections)
        
        return {
            'total_files': total_files,
            'files_with_issues': files_with_issues,
            'files_with_warnings': files_with_warnings,
            'oversized_files': oversized_files,
            'files_with_frontmatter': files_with_frontmatter,
            'files_with_title': files_with_title,
            'files_with_sections': files_with_sections,
            'frontmatter_coverage': files_with_frontmatter / total_files if total_files > 0 else 0,
            'title_coverage': files_with_title / total_files if total_files > 0 else 0,
            'section_coverage': files_with_sections / total_files if total_files > 0 else 0,
            'total_issues': sum(len(r.issues) for r in results),
            'total_warnings': sum(len(r.warnings) for r in results)
        }

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Basic documentation validation')
    parser.add_argument('path', help='File or directory path to validate')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    validator = BasicDocumentationValidator()
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run validation
    if path.is_file():
        results = [validator.validate_file(str(path))]
    else:
        results = validator.validate_directory(str(path))
    
    if not results:
        print("No files found to validate")
        return 0
    
    # Generate summary
    summary = validator.generate_summary(results)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'summary': summary,
            'results': [
                {
                    'file_path': r.file_path,
                    'has_frontmatter': r.has_frontmatter,
                    'has_title': r.has_title,
                    'has_sections': r.has_sections,
                    'file_size_lines': r.file_size_lines,
                    'file_size_bytes': r.file_size_bytes,
                    'is_oversized': r.is_oversized,
                    'issues': r.issues,
                    'warnings': r.warnings
                } for r in results
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
            print("Basic Documentation Validation Report")
            print("=" * 50)
            print(f"Files analyzed: {summary['total_files']}")
            print(f"Files with issues: {summary['files_with_issues']}")
            print(f"Files with warnings: {summary['files_with_warnings']}")
            print(f"Oversized files: {summary['oversized_files']}")
            print(f"Frontmatter coverage: {summary['frontmatter_coverage']:.1%}")
            print(f"Title coverage: {summary['title_coverage']:.1%}")
            print(f"Section coverage: {summary['section_coverage']:.1%}")
            
            # Show critical issues
            critical_results = [r for r in results if r.is_oversized or r.issues]
            if critical_results:
                print("\\nCritical Issues:")
                print("-" * 20)
                for result in critical_results[:5]:
                    print(f"\\n{result.file_path}:")
                    for issue in result.issues:
                        print(f"  ❌ {issue}")
                    for warning in result.warnings[:3]:  # Limit warnings
                        print(f"  ⚠️  {warning}")
        
        # Save text report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"Basic Validation Summary\\n")
                f.write(f"Files: {summary['total_files']}, Issues: {summary['total_issues']}, Warnings: {summary['total_warnings']}\\n\\n")
                for result in results:
                    if result.issues or result.warnings:
                        f.write(f"File: {result.file_path}\\n")
                        for issue in result.issues:
                            f.write(f"  Issue: {issue}\\n")
                        for warning in result.warnings:
                            f.write(f"  Warning: {warning}\\n")
                        f.write("\\n")
    
    # Return exit code
    if summary['oversized_files'] > 0:
        return 2  # Critical issues
    elif summary['files_with_issues'] > 0:
        return 1  # Issues found
    else:
        return 0  # All good

if __name__ == '__main__':
    sys.exit(main())