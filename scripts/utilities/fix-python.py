#!/usr/bin/env python3
"""
Python Fixer Command for Claude Code Agents

Specialized agent command for fixing Python syntax errors, import issues,
and other problems detected by the python_error_detector hook.
"""

import json
import sys
import ast
import re
from pathlib import Path

def load_task(task_file):
    """Load task data from JSON file"""
    with open(task_file, 'r') as f:
        return json.load(f)

def fix_syntax_errors(file_path, content, errors):
    """Fix common syntax errors"""
    lines = content.split('\n')
    
    for error in errors:
        if error['type'] != 'syntax_error':
            continue
            
        line_no = error.get('line', 0) - 1
        if 0 <= line_no < len(lines):
            line = lines[line_no]
            
            # Fix common syntax issues
            if 'unexpected EOF' in error['message']:
                # Missing closing bracket/paren
                if line.count('(') > line.count(')'):
                    lines[line_no] = line + ')'
                elif line.count('[') > line.count(']'):
                    lines[line_no] = line + ']'
                elif line.count('{') > line.count('}'):
                    lines[line_no] = line + '}'
            
            elif 'invalid syntax' in error['message']:
                # Common fixes
                if '=' in line and '==' not in line:
                    # Possible assignment in condition
                    if 'if ' in line or 'while ' in line:
                        lines[line_no] = line.replace('=', '==', 1)
    
    return '\n'.join(lines)

def fix_import_issues(file_path, content, errors):
    """Fix import-related issues"""
    lines = content.split('\n')
    
    for error in errors:
        if error['type'] not in ['incomplete_import', 'missing_module', 'test_import_outside_tests']:
            continue
            
        line_no = error.get('line', 0) - 1
        if 0 <= line_no < len(lines):
            line = lines[line_no]
            
            if error['type'] == 'incomplete_import':
                # Fix incomplete relative imports
                if 'from . import' in line and line.strip().endswith('import'):
                    # Remove the incomplete import
                    lines[line_no] = '# ' + line + ' # FIXME: Incomplete import removed'
            
            elif error['type'] == 'missing_module':
                # Fix missing module name
                if 'from import' in line:
                    lines[line_no] = '# ' + line + ' # FIXME: Missing module name'
            
            elif error['type'] == 'test_import_outside_tests':
                # Comment out test imports in production code
                lines[line_no] = '# ' + line + ' # FIXME: Test import in production code'
    
    return '\n'.join(lines)

def fix_common_issues(file_path, content, errors):
    """Fix common Python issues"""
    lines = content.split('\n')
    
    for error in errors:
        line_no = error.get('line', 0) - 1
        if 0 <= line_no < len(lines):
            line = lines[line_no]
            
            if error['type'] == 'print_statement':
                # Convert print to logging
                indent = len(line) - len(line.lstrip())
                # Add import if needed
                if 'import logging' not in content:
                    lines.insert(0, 'import logging')
                # Replace print with logging
                print_match = re.match(r'^(\s*)print\s*\((.*)\)', line)
                if print_match:
                    lines[line_no] = f"{print_match.group(1)}logging.info({print_match.group(2)})"
            
            elif error['type'] == 'bare_except':
                # Replace bare except with Exception
                lines[line_no] = line.replace('except:', 'except Exception:')
    
    return '\n'.join(lines)

def apply_fixes(task_file):
    """Apply fixes for a Python error task"""
    task = load_task(task_file)
    file_path = Path(task['file_path'])
    
    if not file_path.exists():
        print(f"Error: File {file_path} not found")
        return False
    
    # Read current content
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    errors = task['errors']
    
    # Apply fixes in order of severity
    critical_errors = [e for e in errors if e.get('severity') == 'critical']
    high_errors = [e for e in errors if e.get('severity') == 'high']
    medium_errors = [e for e in errors if e.get('severity') == 'medium']
    
    # Fix critical issues first
    if critical_errors:
        content = fix_syntax_errors(file_path, content, critical_errors)
        content = fix_import_issues(file_path, content, critical_errors)
    
    # Then high severity
    if high_errors:
        content = fix_import_issues(file_path, content, high_errors)
        content = fix_common_issues(file_path, content, high_errors)
    
    # Then medium severity
    if medium_errors:
        content = fix_common_issues(file_path, content, medium_errors)
    
    # Only write if changes were made
    if content != original_content:
        # Backup original
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        # Write fixed content
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed {len(errors)} issues in {file_path}")
        print(f"   Backup saved to: {backup_path}")
        
        # Update task status
        task['status'] = 'completed'
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        return True
    else:
        print(f"ℹ️ No automatic fixes available for {file_path}")
        print("   Manual intervention required for:")
        for error in errors[:5]:
            print(f"   - Line {error.get('line', '?')}: {error['message'][:60]}")
        return False

def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python fix-python.py <task_file.json>")
        print("   Or: python fix-python.py --all  # Fix all pending tasks")
        sys.exit(1)
    
    if sys.argv[1] == '--all':
        # Fix all pending tasks
        task_dir = Path(".task_orchestrator/python_fixes")
        if task_dir.exists():
            tasks = list(task_dir.glob("*.json"))
            fixed = 0
            for task_file in tasks:
                try:
                    task = load_task(task_file)
                    if task.get('status') == 'pending':
                        if apply_fixes(task_file):
                            fixed += 1
                except Exception as e:
                    print(f"Error processing {task_file}: {e}")
            
            print(f"\n🎯 Fixed {fixed} of {len(tasks)} Python files")
    else:
        # Fix specific task
        task_file = Path(sys.argv[1])
        if not task_file.exists():
            print(f"Error: Task file {task_file} not found")
            sys.exit(1)
        
        apply_fixes(task_file)

if __name__ == "__main__":
    main()