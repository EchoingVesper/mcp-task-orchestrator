#!/usr/bin/env python3
"""
File Size Validation for Claude Code Compatibility

Checks all files in specified directories for Claude Code's 500-line limit.
Particularly important for CLAUDE.md files and documentation.
"""

import os
import sys
from pathlib import Path
import argparse


def check_file_sizes(directory: str, max_lines: int = 500, extensions: list = None) -> dict:
    """
    Check file sizes in directory and subdirectories
    
    Args:
        directory: Directory to check
        max_lines: Maximum allowed lines (default 500 for Claude Code)
        extensions: List of file extensions to check (default: .md, .py, .txt)
    
    Returns:
        Dictionary with results
    """
    if extensions is None:
        extensions = ['.md', '.py', '.txt']
    
    results = {
        'compliant': [],
        'over_limit': [],
        'warnings': [],
        'errors': []
    }
    
    directory_path = Path(directory)
    
    if not directory_path.exists():
        results['errors'].append(f"Directory does not exist: {directory}")
        return results
    
    # Find all files with specified extensions
    for ext in extensions:
        for file_path in directory_path.rglob(f"*{ext}"):
            # Skip backup and archive directories
            if any(part in str(file_path) for part in ["backup", "archive", "recovery_points", ".git"]):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
                
                relative_path = file_path.relative_to(directory_path)
                
                if line_count > max_lines:
                    results['over_limit'].append({
                        'file': str(relative_path),
                        'lines': line_count,
                        'excess': line_count - max_lines
                    })
                elif line_count > max_lines * 0.8:  # Warning at 80% of limit
                    results['warnings'].append({
                        'file': str(relative_path),
                        'lines': line_count,
                        'percentage': (line_count / max_lines) * 100
                    })
                else:
                    results['compliant'].append({
                        'file': str(relative_path),
                        'lines': line_count
                    })
                    
            except Exception as e:
                results['errors'].append(f"Error reading {file_path}: {str(e)}")
    
    return results


def generate_report(results: dict, max_lines: int) -> str:
    """Generate a formatted report"""
    report_lines = []
    
    # Summary
    total_files = len(results['compliant']) + len(results['over_limit']) + len(results['warnings'])
    report_lines.append("# File Size Validation Report")
    report_lines.append("")
    report_lines.append(f"**Maximum Lines**: {max_lines}")
    report_lines.append(f"**Total Files Checked**: {total_files}")
    report_lines.append(f"**Files Over Limit**: {len(results['over_limit'])}")
    report_lines.append(f"**Files with Warnings**: {len(results['warnings'])}")
    report_lines.append(f"**Compliant Files**: {len(results['compliant'])}")
    report_lines.append("")
    
    # Files over limit (critical issues)
    if results['over_limit']:
        report_lines.append("## ❌ Files Exceeding Line Limit (CRITICAL)")
        report_lines.append("")
        report_lines.append("| File | Lines | Excess | Action Required |")
        report_lines.append("|------|-------|--------|-----------------|")
        
        for file_info in sorted(results['over_limit'], key=lambda x: x['lines'], reverse=True):
            report_lines.append(f"| {file_info['file']} | {file_info['lines']} | +{file_info['excess']} | Split or refactor |")
        report_lines.append("")
    
    # Files with warnings
    if results['warnings']:
        report_lines.append("## ⚠️ Files Approaching Line Limit (WARNING)")
        report_lines.append("")
        report_lines.append("| File | Lines | Usage | Recommendation |")
        report_lines.append("|------|-------|-------|----------------|")
        
        for file_info in sorted(results['warnings'], key=lambda x: x['lines'], reverse=True):
            report_lines.append(f"| {file_info['file']} | {file_info['lines']} | {file_info['percentage']:.1f}% | Monitor growth |")
        report_lines.append("")
    
    # Compliant files summary
    if results['compliant']:
        report_lines.append("## ✅ Compliant Files Summary")
        report_lines.append("")
        avg_lines = sum(f['lines'] for f in results['compliant']) / len(results['compliant'])
        max_compliant = max(f['lines'] for f in results['compliant'])
        report_lines.append(f"**Compliant Files**: {len(results['compliant'])}")
        report_lines.append(f"**Average Lines**: {avg_lines:.1f}")
        report_lines.append(f"**Largest Compliant File**: {max_compliant} lines")
        report_lines.append("")
    
    # Errors
    if results['errors']:
        report_lines.append("## 🚨 Errors")
        report_lines.append("")
        for error in results['errors']:
            report_lines.append(f"- {error}")
        report_lines.append("")
    
    return "\n".join(report_lines)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Check file sizes for Claude Code compatibility")
    parser.add_argument("directory", help="Directory to check", default=".", nargs='?')
    parser.add_argument("--max-lines", type=int, default=500, help="Maximum allowed lines (default: 500)")
    parser.add_argument("--extensions", nargs='+', default=['.md', '.py', '.txt'], 
                       help="File extensions to check (default: .md .py .txt)")
    parser.add_argument("--output", help="Output report to file")
    parser.add_argument("--claude-md-only", action="store_true", help="Check only CLAUDE.md files")
    parser.add_argument("--quiet", action="store_true", help="Only show summary")
    
    args = parser.parse_args()
    
    # Special mode for CLAUDE.md files only
    if args.claude_md_only:
        args.extensions = ['.md']
        # We'll filter to only CLAUDE.md files in the results
    
    # Check file sizes
    results = check_file_sizes(args.directory, args.max_lines, args.extensions)
    
    # Filter for CLAUDE.md files if requested
    if args.claude_md_only:
        for category in ['compliant', 'over_limit', 'warnings']:
            results[category] = [f for f in results[category] if f['file'].endswith('CLAUDE.md')]
    
    # Generate report
    report = generate_report(results, args.max_lines)
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    
    if not args.quiet:
        print(report)
    
    # Exit with error if there are files over the limit
    if results['over_limit']:
        print(f"\n❌ VALIDATION FAILED: {len(results['over_limit'])} files exceed the {args.max_lines}-line limit")
        sys.exit(1)
    elif results['warnings']:
        print(f"\n⚠️ WARNING: {len(results['warnings'])} files are approaching the limit")
        sys.exit(0)
    else:
        print(f"\n✅ All files are within the {args.max_lines}-line limit")
        sys.exit(0)


if __name__ == "__main__":
    main()