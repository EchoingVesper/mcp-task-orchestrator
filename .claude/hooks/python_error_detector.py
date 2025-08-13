#!/usr/bin/env python3
"""
Python Error Detector Hook for Claude Code

Detects Python syntax errors, import issues, and other problems
when Python files are read or edited. Creates tasks for fixing agents.
"""

import ast
import json
import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

def check_python_syntax(file_path, content):
    """Check for Python syntax errors"""
    errors = []
    
    try:
        ast.parse(content)
    except SyntaxError as e:
        errors.append({
            'type': 'syntax_error',
            'line': e.lineno,
            'message': str(e.msg),
            'severity': 'critical'
        })
    except Exception as e:
        errors.append({
            'type': 'parse_error', 
            'message': str(e),
            'severity': 'high'
        })
    
    return errors

def check_import_issues(file_path, content):
    """Check for import-related issues"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for malformed imports
        if re.match(r'^\s*from\s+\.\s*import\s*$', line):
            issues.append({
                'type': 'incomplete_import',
                'line': i,
                'message': 'Incomplete relative import statement',
                'severity': 'high'
            })
        
        # Check for missing module names
        if re.match(r'^\s*from\s+import\s+', line):
            issues.append({
                'type': 'missing_module',
                'line': i,
                'message': 'Missing module name in import',
                'severity': 'critical'
            })
        
        # Check for test API misuse
        if 'import test_' in line or 'from test_' in line:
            if '/test' not in str(file_path):
                issues.append({
                    'type': 'test_import_outside_tests',
                    'line': i,
                    'message': 'Test module imported outside test directory',
                    'severity': 'medium'
                })
    
    return issues

def check_common_issues(file_path, content):
    """Check for common Python issues"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for print statements in production code
        if re.match(r'^\s*print\s*\(', line):
            if '/test' not in str(file_path) and '/scripts' not in str(file_path):
                issues.append({
                    'type': 'print_statement',
                    'line': i,
                    'message': 'Print statement in production code (use logging instead)',
                    'severity': 'low'
                })
        
        # Check for bare except clauses
        if re.match(r'^\s*except\s*:', line):
            issues.append({
                'type': 'bare_except',
                'line': i,
                'message': 'Bare except clause (specify exception type)',
                'severity': 'medium'
            })
        
        # Check for TODO/FIXME/HACK markers
        if 'TODO' in line or 'FIXME' in line or 'HACK' in line or 'XXX' in line:
            issues.append({
                'type': 'technical_debt',
                'line': i,
                'message': f'Technical debt marker found: {line.strip()[:50]}',
                'severity': 'info'
            })
    
    return issues

def run_quick_type_check(file_path):
    """Run a quick type check if mypy is available"""
    issues = []
    
    try:
        # Quick mypy check with minimal config
        result = subprocess.run(
            ['mypy', '--no-error-summary', '--no-pretty', '--ignore-missing-imports', str(file_path)],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            for line in result.stdout.split('\n'):
                if line and ':' in line:
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        try:
                            line_no = int(parts[1])
                            issues.append({
                                'type': 'type_error',
                                'line': line_no,
                                'message': parts[3].strip(),
                                'severity': 'medium'
                            })
                        except Exception:
                            # Failed to parse mypy line - skip this line
                            pass
    except Exception:
        # mypy not available or error - not critical
        pass
    
    return issues

def create_python_fix_task(file_path, errors, severity="medium"):
    """Create a task for the Python fixing agent"""
    task_dir = Path(".task_orchestrator/python_fixes")
    task_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    task_file = task_dir / f"fix_{Path(file_path).stem}_{timestamp}.json"
    
    task_data = {
        "task_id": f"python_fix_{timestamp}",
        "file_path": str(file_path),
        "created_at": datetime.now().isoformat(),
        "severity": severity,
        "errors": errors,
        "status": "pending",
        "agent_type": "python_fixer"
    }
    
    with open(task_file, 'w') as f:
        json.dump(task_data, f, indent=2)
    
    return task_file

def main():
    """Main hook execution"""
    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        
        # Get file path from environment
        file_path = os.environ.get('CLAUDE_TOOL_RESULT_FILE', '')
        
        if not file_path or not file_path.endswith('.py'):
            sys.exit(0)
        
        # Skip test files and scripts for most checks
        is_test = '/test' in file_path
        is_script = '/script' in file_path
        
        # Read file content
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception:
            # Failed to read file - exit silently
            sys.exit(0)
        
        all_issues = []
        
        # Check syntax errors (always)
        syntax_errors = check_python_syntax(file_path, content)
        all_issues.extend(syntax_errors)
        
        # Check import issues (always)
        import_issues = check_import_issues(file_path, content)
        all_issues.extend(import_issues)
        
        # Check common issues (skip for tests)
        if not is_test:
            common_issues = check_common_issues(file_path, content)
            all_issues.extend(common_issues)
        
        # Run type check (skip for tests and scripts)
        if not is_test and not is_script:
            type_issues = run_quick_type_check(file_path)
            all_issues.extend(type_issues)
        
        # Filter out info-level issues unless there are many
        info_issues = [i for i in all_issues if i.get('severity') == 'info']
        real_issues = [i for i in all_issues if i.get('severity') != 'info']
        
        if real_issues:
            # Determine overall severity
            if any(i['severity'] == 'critical' for i in real_issues):
                severity = 'critical'
            elif any(i['severity'] == 'high' for i in real_issues):
                severity = 'high'
            else:
                severity = 'medium'
            
            # Show summary to user
            print(f"🐍 Python issues detected in {Path(file_path).name}:", file=sys.stderr)
            
            # Group by type
            by_type = {}
            for issue in real_issues:
                issue_type = issue.get('type', 'unknown')
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(issue)
            
            for issue_type, issues in by_type.items():
                print(f"   {issue_type}: {len(issues)} issue(s)", file=sys.stderr)
                # Show first few examples
                for issue in issues[:2]:
                    if 'line' in issue:
                        print(f"      Line {issue['line']}: {issue['message'][:60]}", file=sys.stderr)
            
            # Create fix task if critical or high severity
            if severity in ['critical', 'high']:
                task_file = create_python_fix_task(file_path, real_issues, severity)
                print(f"   📋 Created fix task: {task_file.name}", file=sys.stderr)
                print(f"   💡 Run: python .claude/commands/fix-python.py {task_file}", file=sys.stderr)
            
            print("", file=sys.stderr)
        
        # Show technical debt summary if many
        if len(info_issues) > 5:
            print(f"📌 {len(info_issues)} technical debt markers in {Path(file_path).name}", file=sys.stderr)
    
    except Exception as e:
        # Log error but don't fail
        print(f"Python detector error: {e}", file=sys.stderr)
    
    # Always succeed
    sys.exit(0)

if __name__ == "__main__":
    main()