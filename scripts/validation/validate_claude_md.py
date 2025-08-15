#!/usr/bin/env python3
"""
CLAUDE.md Validation System

Comprehensive validation tool for the CLAUDE.md ecosystem ensuring:
- File size compliance (under 500 lines for Claude Code stability)
- Template compliance (standardized structure)
- Cross-reference accuracy (valid links)
- Status tag validation ([CURRENT], [NEEDS-UPDATE], etc.)
- Integration consistency across all CLAUDE.md files
"""

import os
import sys
import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validating a single CLAUDE.md file"""
    file_path: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    line_count: int
    status_tag: str


class CLAUDEmdValidator:
    """Validator for CLAUDE.md ecosystem compliance"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.max_lines = 500
        self.recommended_max_lines = 400
        self.required_sections = [
            "# CLAUDE.md",
            "## Status Header", 
            "## Context Analysis",
            "## Core Commands",
            "## Cross-References"
        ]
        self.valid_status_tags = ["[CURRENT]", "[NEEDS-UPDATE]", "[DEPRECATED]", "[DRAFT]", "[ARCHIVED]"]
        
    def find_claude_md_files(self) -> List[Path]:
        """Find all CLAUDE.md files in the project"""
        claude_files = []
        
        # Find all CLAUDE.md files, excluding backups and archives
        for file_path in self.project_root.rglob("CLAUDE.md"):
            # Skip backup and archive directories
            if any(part in str(file_path) for part in ["backup", "archive", "recovery_points"]):
                continue
            claude_files.append(file_path)
            
        return sorted(claude_files)
    
    def validate_file_size(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate file size compliance"""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
                
            if line_count > self.max_lines:
                errors.append(f"File exceeds maximum {self.max_lines} lines: {line_count} lines")
            elif line_count > self.recommended_max_lines:
                warnings.append(f"File exceeds recommended {self.recommended_max_lines} lines: {line_count} lines")
                
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error reading file: {str(e)}")
            return False, errors, warnings
    
    def validate_template_structure(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate template structure compliance"""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for required sections
            for section in self.required_sections:
                if section not in content:
                    errors.append(f"Missing required section: {section}")
                    
            # Check for file size compliance warning
            if "⚠️ **File Size Compliant**" not in content:
                warnings.append("Missing file size compliance statement")
                
            # Check for cross-reference section content
            if "## Cross-References" in content:
                cross_ref_section = content.split("## Cross-References")[1].split("##")[0]
                if "Related CLAUDE.md Files" not in cross_ref_section:
                    warnings.append("Cross-References section missing 'Related CLAUDE.md Files' subsection")
                    
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error validating template structure: {str(e)}")
            return False, errors, warnings
    
    def validate_status_tags(self, file_path: Path) -> Tuple[bool, List[str], List[str], str]:
        """Validate status tag presence and validity"""
        errors = []
        warnings = []
        status_tag = "UNKNOWN"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for status tags in the first 20 lines
            first_lines = content.split('\n')[:20]
            status_found = False
            
            for line in first_lines:
                for tag in self.valid_status_tags:
                    if tag in line:
                        status_tag = tag
                        status_found = True
                        break
                if status_found:
                    break
                    
            if not status_found:
                errors.append("No valid status tag found ([CURRENT], [NEEDS-UPDATE], etc.)")
                
            return len(errors) == 0, errors, warnings, status_tag
            
        except Exception as e:
            errors.append(f"Error validating status tags: {str(e)}")
            return False, errors, warnings, "ERROR"
    
    def validate_cross_references(self, file_path: Path, all_claude_files: List[Path]) -> Tuple[bool, List[str], List[str]]:
        """Validate cross-reference links"""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, link_path in links:
                # Skip external links (http/https)
                if link_path.startswith(('http://', 'https://')):
                    continue
                    
                # Check internal links
                if link_path.endswith('.md'):
                    # Resolve relative path
                    try:
                        target_path = (file_path.parent / link_path).resolve()
                        if not target_path.exists():
                            errors.append(f"Broken link: {link_text} -> {link_path}")
                    except Exception as e:
                        warnings.append(f"Could not resolve link: {link_path} ({str(e)})")
                        
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error validating cross-references: {str(e)}")
            return False, errors, warnings
    
    def validate_single_file(self, file_path: Path, all_claude_files: List[Path]) -> ValidationResult:
        """Validate a single CLAUDE.md file"""
        all_errors = []
        all_warnings = []
        line_count = 0
        status_tag = "UNKNOWN"
        
        # Validate file size
        size_valid, size_errors, size_warnings = self.validate_file_size(file_path)
        all_errors.extend(size_errors)
        all_warnings.extend(size_warnings)
        
        # Get line count for reporting
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
        except:
            line_count = 0
            
        # Validate template structure
        template_valid, template_errors, template_warnings = self.validate_template_structure(file_path)
        all_errors.extend(template_errors)
        all_warnings.extend(template_warnings)
        
        # Validate status tags
        status_valid, status_errors, status_warnings, status_tag = self.validate_status_tags(file_path)
        all_errors.extend(status_errors)
        all_warnings.extend(status_warnings)
        
        # Validate cross-references
        cross_ref_valid, cross_ref_errors, cross_ref_warnings = self.validate_cross_references(file_path, all_claude_files)
        all_errors.extend(cross_ref_errors)
        all_warnings.extend(cross_ref_warnings)
        
        is_valid = size_valid and template_valid and status_valid and cross_ref_valid
        
        return ValidationResult(
            file_path=str(file_path),
            is_valid=is_valid,
            errors=all_errors,
            warnings=all_warnings,
            line_count=line_count,
            status_tag=status_tag
        )
    
    def validate_ecosystem(self) -> Dict[str, ValidationResult]:
        """Validate the entire CLAUDE.md ecosystem"""
        claude_files = self.find_claude_md_files()
        results = {}
        
        for file_path in claude_files:
            relative_path = str(file_path.relative_to(self.project_root))
            results[relative_path] = self.validate_single_file(file_path, claude_files)
            
        return results
    
    def generate_report(self, results: Dict[str, ValidationResult], output_file: str = None) -> str:
        """Generate validation report"""
        report_lines = []
        report_lines.append("# CLAUDE.md Ecosystem Validation Report")
        report_lines.append("")
        report_lines.append(f"**Generated**: {os.environ.get('DATE', 'Unknown date')}")
        report_lines.append(f"**Files Validated**: {len(results)}")
        report_lines.append("")
        
        # Summary statistics
        valid_files = sum(1 for r in results.values() if r.is_valid)
        total_errors = sum(len(r.errors) for r in results.values())
        total_warnings = sum(len(r.warnings) for r in results.values())
        
        report_lines.append("## Summary")
        report_lines.append(f"- **Valid Files**: {valid_files}/{len(results)}")
        report_lines.append(f"- **Total Errors**: {total_errors}")
        report_lines.append(f"- **Total Warnings**: {total_warnings}")
        report_lines.append("")
        
        # File size compliance
        report_lines.append("## File Size Compliance")
        report_lines.append("| File | Lines | Status |")
        report_lines.append("|------|-------|--------|")
        
        for file_path, result in sorted(results.items()):
            status = "✅ PASS" if result.line_count <= 500 else "❌ FAIL"
            if result.line_count > 400:
                status += " (⚠️ Over recommended limit)"
            report_lines.append(f"| {file_path} | {result.line_count} | {status} |")
        report_lines.append("")
        
        # Status tags
        report_lines.append("## Status Tag Summary")
        status_counts = {}
        for result in results.values():
            status_counts[result.status_tag] = status_counts.get(result.status_tag, 0) + 1
            
        for status, count in sorted(status_counts.items()):
            report_lines.append(f"- **{status}**: {count} files")
        report_lines.append("")
        
        # Detailed results
        report_lines.append("## Detailed Validation Results")
        
        for file_path, result in sorted(results.items()):
            report_lines.append(f"### {file_path}")
            report_lines.append(f"- **Status**: {'✅ VALID' if result.is_valid else '❌ INVALID'}")
            report_lines.append(f"- **Lines**: {result.line_count}")
            report_lines.append(f"- **Status Tag**: {result.status_tag}")
            
            if result.errors:
                report_lines.append("- **Errors**:")
                for error in result.errors:
                    report_lines.append(f"  - {error}")
                    
            if result.warnings:
                report_lines.append("- **Warnings**:")
                for warning in result.warnings:
                    report_lines.append(f"  - {warning}")
                    
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
                
        return report_content


def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate CLAUDE.md ecosystem")
    parser.add_argument("--project-root", help="Project root directory", default=".")
    parser.add_argument("--output", help="Output report file", default=None)
    parser.add_argument("--quiet", action="store_true", help="Only show errors")
    
    args = parser.parse_args()
    
    validator = CLAUDEmdValidator(args.project_root)
    results = validator.validate_ecosystem()
    
    # Generate and display report
    report = validator.generate_report(results, args.output)
    
    if not args.quiet:
        print(report)
    
    # Exit with error code if any validation failed
    has_errors = any(not r.is_valid for r in results.values())
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()