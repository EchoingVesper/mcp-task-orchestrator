#!/usr/bin/env python3
"""
Cross-Reference Validation for CLAUDE.md Ecosystem

Validates that all internal links in CLAUDE.md files are accurate and working.
Ensures the cross-reference network remains intact.
"""

import os
import re
import sys
from pathlib import Path
import argparse


def find_claude_md_files(directory: str) -> list:
    """Find all CLAUDE.md files in the project"""
    directory_path = Path(directory)
    claude_files = []
    
    for file_path in directory_path.rglob("CLAUDE.md"):
        # Skip backup and archive directories
        if any(part in str(file_path) for part in ["backup", "archive", "recovery_points", ".git"]):
            continue
        claude_files.append(file_path)
    
    return sorted(claude_files)


def extract_internal_links(file_path: Path) -> list:
    """Extract all internal markdown links from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []
    
    # Find all markdown links: [text](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    links = re.findall(link_pattern, content)
    
    internal_links = []
    for link_text, link_url in links:
        # Skip external links
        if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
            continue
        
        # Skip anchor links within the same file
        if link_url.startswith('#'):
            continue
            
        internal_links.append({
            'text': link_text,
            'url': link_url,
            'line_number': content[:content.find(f'[{link_text}]({link_url})')].count('\n') + 1
        })
    
    return internal_links


def validate_link(source_file: Path, link_url: str) -> dict:
    """Validate a single internal link"""
    result = {
        'valid': False,
        'target_exists': False,
        'target_path': None,
        'error': None
    }
    
    try:
        # Resolve relative path
        if link_url.startswith('/'):
            # Absolute path from project root
            project_root = source_file
            while project_root.parent != project_root and not (project_root / '.git').exists():
                project_root = project_root.parent
            target_path = project_root / link_url.lstrip('/')
        else:
            # Relative path from source file
            target_path = (source_file.parent / link_url).resolve()
        
        result['target_path'] = str(target_path)
        result['target_exists'] = target_path.exists()
        result['valid'] = target_path.exists()
        
        if not target_path.exists():
            result['error'] = f"Target file does not exist: {target_path}"
            
    except Exception as e:
        result['error'] = f"Error resolving path: {str(e)}"
    
    return result


def validate_cross_references(directory: str) -> dict:
    """Validate all cross-references in CLAUDE.md files"""
    claude_files = find_claude_md_files(directory)
    results = {
        'files_checked': len(claude_files),
        'total_links': 0,
        'valid_links': 0,
        'broken_links': 0,
        'file_results': {},
        'broken_link_details': []
    }
    
    for file_path in claude_files:
        relative_path = str(file_path.relative_to(Path(directory)))
        internal_links = extract_internal_links(file_path)
        
        file_result = {
            'file_path': relative_path,
            'total_links': len(internal_links),
            'valid_links': 0,
            'broken_links': 0,
            'links': []
        }
        
        for link in internal_links:
            validation = validate_link(file_path, link['url'])
            link_result = {
                'text': link['text'],
                'url': link['url'],
                'line_number': link['line_number'],
                'valid': validation['valid'],
                'target_exists': validation['target_exists'],
                'target_path': validation['target_path'],
                'error': validation['error']
            }
            
            file_result['links'].append(link_result)
            
            if validation['valid']:
                file_result['valid_links'] += 1
                results['valid_links'] += 1
            else:
                file_result['broken_links'] += 1
                results['broken_links'] += 1
                results['broken_link_details'].append({
                    'source_file': relative_path,
                    'line_number': link['line_number'],
                    'link_text': link['text'],
                    'link_url': link['url'],
                    'error': validation['error']
                })
        
        results['file_results'][relative_path] = file_result
        results['total_links'] += len(internal_links)
    
    return results


def generate_report(results: dict) -> str:
    """Generate a formatted validation report"""
    report_lines = []
    
    # Summary
    report_lines.append("# Cross-Reference Validation Report")
    report_lines.append("")
    report_lines.append(f"**Files Checked**: {results['files_checked']}")
    report_lines.append(f"**Total Internal Links**: {results['total_links']}")
    report_lines.append(f"**Valid Links**: {results['valid_links']}")
    report_lines.append(f"**Broken Links**: {results['broken_links']}")
    
    if results['total_links'] > 0:
        success_rate = (results['valid_links'] / results['total_links']) * 100
        report_lines.append(f"**Success Rate**: {success_rate:.1f}%")
    
    report_lines.append("")
    
    # Broken links details
    if results['broken_links'] > 0:
        report_lines.append("## ❌ Broken Links (CRITICAL)")
        report_lines.append("")
        report_lines.append("| Source File | Line | Link Text | Target URL | Error |")
        report_lines.append("|-------------|------|-----------|------------|-------|")
        
        for broken_link in results['broken_link_details']:
            report_lines.append(f"| {broken_link['source_file']} | {broken_link['line_number']} | {broken_link['link_text']} | {broken_link['link_url']} | {broken_link['error']} |")
        
        report_lines.append("")
    
    # File-by-file summary
    report_lines.append("## File-by-File Summary")
    report_lines.append("")
    report_lines.append("| File | Total Links | Valid | Broken | Status |")
    report_lines.append("|------|-------------|-------|--------|--------|")
    
    for file_path, file_result in sorted(results['file_results'].items()):
        status = "✅ PASS" if file_result['broken_links'] == 0 else "❌ FAIL"
        report_lines.append(f"| {file_path} | {file_result['total_links']} | {file_result['valid_links']} | {file_result['broken_links']} | {status} |")
    
    report_lines.append("")
    
    # Detailed results for files with broken links
    files_with_broken_links = [f for f in results['file_results'].values() if f['broken_links'] > 0]
    
    if files_with_broken_links:
        report_lines.append("## Detailed Broken Link Analysis")
        report_lines.append("")
        
        for file_result in files_with_broken_links:
            report_lines.append(f"### {file_result['file_path']}")
            report_lines.append("")
            
            broken_links = [link for link in file_result['links'] if not link['valid']]
            for link in broken_links:
                report_lines.append(f"- **Line {link['line_number']}**: [{link['text']}]({link['url']})")
                report_lines.append(f"  - Error: {link['error']}")
                report_lines.append("")
    
    return "\n".join(report_lines)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Validate cross-references in CLAUDE.md files")
    parser.add_argument("directory", help="Directory to check", default=".", nargs='?')
    parser.add_argument("--output", help="Output report to file")
    parser.add_argument("--quiet", action="store_true", help="Only show summary")
    
    args = parser.parse_args()
    
    # Validate cross-references
    print("Validating cross-references in CLAUDE.md files...")
    results = validate_cross_references(args.directory)
    
    # Generate report
    report = generate_report(results)
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    
    if not args.quiet:
        print(report)
    
    # Exit with appropriate code
    if results['broken_links'] > 0:
        print(f"\n❌ VALIDATION FAILED: {results['broken_links']} broken links found")
        sys.exit(1)
    else:
        print(f"\n✅ All {results['total_links']} cross-references are valid")
        sys.exit(0)


if __name__ == "__main__":
    main()