#!/usr/bin/env python3
"""
Fix malformed import statements caused by automated replacements.
Specifically fixes patterns where duplicate content appears in import lines.
"""

import re
from pathlib import Path
import sys

def fix_malformed_imports(file_path):
    """Fix malformed import statements in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Fix duplicate SpecialistType in imports
    # Example: "from ... import SpecialistType SubTask, SpecialistType, TaskResult"
    # Should become: "from ... import SpecialistType, TaskResult"
    pattern = r'from mcp_task_orchestrator\.domain\.value_objects\.specialist_type import SpecialistType\s+SubTask,\s*SpecialistType,\s*TaskResult'
    replacement = 'from mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType\nfrom mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult'
    content = re.sub(pattern, replacement, content)
    
    # Pattern 2: Fix any remaining malformed imports with missing commas
    # Example: "import A B, C" should become "import A, B, C"
    pattern = r'(from [^\n]+ import)(\s+\w+)(\s+\w+)(,.*)?'
    def fix_import(match):
        base = match.group(1)
        first = match.group(2).strip()
        second = match.group(3).strip()
        rest = match.group(4) or ''
        return f"{base} {first}, {second}{rest}"
    
    # Apply only to lines that look malformed
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if 'import' in line and re.search(r'import\s+\w+\s+\w+[,\s]', line):
            line = re.sub(pattern, fix_import, line)
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix malformed imports in test files."""
    test_files_with_errors = [
        'tests/test_artifacts_validator.py',
        'tests/security/conftest.py',
        'tests/unit/template_system/test_template_engine.py',
        'tests/unit/template_system/test_json5_parser.py',
        'tests/security/template_system/test_template_security.py',
        # Add more files as we find them
    ]
    
    fixed_count = 0
    for file_path in test_files_with_errors:
        path = Path(file_path)
        if path.exists():
            if fix_malformed_imports(path):
                print(f"Fixed malformed imports in: {file_path}")
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files with malformed imports")

if __name__ == "__main__":
    main()