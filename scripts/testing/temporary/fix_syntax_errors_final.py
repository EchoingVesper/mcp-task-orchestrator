#!/usr/bin/env python3
"""
Fix remaining syntax errors in test files.
"""

import ast
import re
from pathlib import Path

def check_syntax_errors(file_path):
    """Check if a file has syntax errors."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return False, None
    except SyntaxError as e:
        return True, e
    except Exception as e:
        return True, e

def fix_common_syntax_errors(file_path):
    """Fix common syntax errors in test files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix malformed f-strings
    # Pattern: f"text} more text"
    content = re.sub(r'f"([^"]*)}([^"]*)"', r'f"\1}\2"', content)
    
    # Fix import SpecialistType ( patterns
    content = re.sub(r'import SpecialistType \(', 'import SpecialistType', content)
    
    # Fix incomplete imports ending with just "import"
    content = re.sub(r'\nimport$', '\n# import', content)
    
    # Fix lines ending with "import SubTask, SpecialistType"
    content = re.sub(r'import SubTask, SpecialistType', 'from mcp_task_orchestrator.domain.entities.task import Task\nfrom mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Find and fix syntax errors in test files."""
    test_dir = Path('tests')
    syntax_error_files = []
    fixed_files = []
    
    # Find all Python files in tests directory
    for py_file in test_dir.rglob('*.py'):
        if 'archives' in str(py_file):
            continue
            
        has_error, error = check_syntax_errors(py_file)
        if has_error:
            syntax_error_files.append((py_file, error))
    
    print(f"Found {len(syntax_error_files)} files with syntax errors")
    
    # Try to fix each file
    for file_path, error in syntax_error_files:
        print(f"\nFixing {file_path}:")
        print(f"  Error: {error}")
        
        if fix_common_syntax_errors(file_path):
            # Check if fix worked
            has_error_after, _ = check_syntax_errors(file_path)
            if not has_error_after:
                print(f"  ✓ Fixed!")
                fixed_files.append(file_path)
            else:
                print(f"  ✗ Still has errors")
        else:
            print(f"  - No automatic fix available")
    
    print(f"\nSummary:")
    print(f"  Total files with errors: {len(syntax_error_files)}")
    print(f"  Files fixed: {len(fixed_files)}")
    print(f"  Files still with errors: {len(syntax_error_files) - len(fixed_files)}")

if __name__ == "__main__":
    main()