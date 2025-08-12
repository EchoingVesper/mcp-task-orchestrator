#!/usr/bin/env python3
"""
Pre-read linting hook for Claude Code

Runs linting checks before reading files and adds errors to context,
making Claude aware of issues that need fixing.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def run_markdownlint(file_path):
    """Run markdownlint and return issues"""
    try:
        result = subprocess.run(
            ['markdownlint', '--json', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            # Parse JSON output
            issues = json.loads(result.stdout)
            return issues
        else:
            return []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []

def run_python_checks(file_path):
    """Run Python checks and return issues"""
    issues = []
    
    try:
        # Quick syntax check
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            issues.append({
                'tool': 'python-syntax',
                'line': e.lineno,
                'message': str(e.msg),
                'severity': 'error'
            })
        
        # Quick ruff check if available
        try:
            result = subprocess.run(
                ['ruff', 'check', '--output-format=json', str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                for issue in ruff_issues:
                    issues.append({
                        'tool': 'ruff',
                        'line': issue.get('location', {}).get('row', 0),
                        'code': issue.get('code', ''),
                        'message': issue.get('message', ''),
                        'severity': 'warning'
                    })
        except:
            pass
            
    except Exception:
        pass
    
    return issues

def format_linting_context(file_path, issues):
    """Format linting issues for Claude's context"""
    if not issues:
        return ""
    
    context_parts = [
        f"\n<!-- LINTING CONTEXT for {Path(file_path).name} -->",
        f"<!-- {len(issues)} linting issue(s) detected: -->"
    ]
    
    # Group by tool
    by_tool = {}
    for issue in issues:
        tool = issue.get('tool', 'markdownlint')
        if tool not in by_tool:
            by_tool[tool] = []
        by_tool[tool].append(issue)
    
    for tool, tool_issues in by_tool.items():
        context_parts.append(f"<!-- {tool.upper()}: {len(tool_issues)} issue(s) -->")
        
        # Show first few issues with line numbers
        for issue in tool_issues[:5]:
            line = issue.get('line') or issue.get('lineNumber', '?')
            code = issue.get('code') or issue.get('ruleNames', [''])[0] if issue.get('ruleNames') else ''
            message = issue.get('message', '')
            
            if code:
                context_parts.append(f"<!--   Line {line} ({code}): {message[:80]} -->")
            else:
                context_parts.append(f"<!--   Line {line}: {message[:80]} -->")
        
        if len(tool_issues) > 5:
            context_parts.append(f"<!--   ... and {len(tool_issues) - 5} more {tool} issues -->")
    
    context_parts.append("<!-- END LINTING CONTEXT -->\n")
    
    return "\n".join(context_parts)

def main():
    """Main hook execution"""
    try:
        # Get file path from command line argument (PostToolUse mode)
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
        else:
            # Fallback to environment variable
            file_path = os.environ.get('CLAUDE_TOOL_RESULT_FILE', '')
        
        if not file_path:
            sys.exit(0)
        
        if not file_path or not os.path.exists(file_path):
            sys.exit(0)
        
        file_ext = Path(file_path).suffix.lower()
        all_issues = []
        
        # Run appropriate linters based on file type
        if file_ext == '.md':
            markdown_issues = run_markdownlint(file_path)
            for issue in markdown_issues:
                # Convert markdownlint format to standard format
                all_issues.append({
                    'tool': 'markdownlint',
                    'line': issue.get('lineNumber', 0),
                    'code': ', '.join(issue.get('ruleNames', [])),
                    'message': issue.get('ruleDescription', ''),
                    'severity': 'warning'
                })
        
        elif file_ext == '.py':
            python_issues = run_python_checks(file_path)
            all_issues.extend(python_issues)
        
        # Add linting context to stderr so Claude sees it
        if all_issues:
            context = format_linting_context(file_path, all_issues)
            print(context, file=sys.stderr)
            
            # Also add brief summary
            error_count = sum(1 for i in all_issues if i.get('severity') == 'error')
            warning_count = sum(1 for i in all_issues if i.get('severity') == 'warning')
            
            if error_count > 0:
                print(f"🚨 {error_count} error(s) and {warning_count} warning(s) in {Path(file_path).name}", file=sys.stderr)
            elif warning_count > 0:
                print(f"⚠️ {warning_count} linting warning(s) in {Path(file_path).name}", file=sys.stderr)
    
    except Exception as e:
        # Don't fail the hook
        print(f"Pre-read linter error: {e}", file=sys.stderr)
    
    # Always succeed
    sys.exit(0)

if __name__ == "__main__":
    main()