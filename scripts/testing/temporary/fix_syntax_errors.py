#!/usr/bin/env python3
"""
Fix Syntax Errors from Import Replacement Script

This script fixes syntax errors that may have been introduced during 
automated import replacements.
"""

import os
import re
from pathlib import Path
from typing import List

def fix_syntax_errors_in_file(file_path: Path) -> bool:
    """Fix common syntax errors in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Fix malformed import lines with duplicate content
        # Pattern: import SpecialistType ( <old imports> )
        pattern = r'from (.+) import (.+) \(\s*\n*\s*(.*?)\s*\n*\s*\)'
        def fix_import(match):
            module = match.group(1)
            new_import = match.group(2)
            old_imports = match.group(3)
            return f'from {module} import {new_import}'
        
        content = re.sub(pattern, fix_import, content, flags=re.MULTILINE | re.DOTALL)
        
        # Fix malformed imports with duplicate SpecialistType, TaskStatus etc.
        content = re.sub(r'SpecialistType TaskStatus, SpecialistType', 'SpecialistType', content)
        content = re.sub(r'import SpecialistType, TaskStatus, SpecialistType', 'import SpecialistType', content)
        
        # Fix orphaned opening parentheses
        content = re.sub(r'import SpecialistType \($', 'import SpecialistType', content)
        
        # Fix lines that end with ( followed by old imports
        lines = content.split('\n')
        cleaned_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for import lines ending with (
            if 'import' in line and line.strip().endswith('('):
                # Keep only the import line, skip the old import block
                cleaned_line = line.rstrip(' (')
                cleaned_lines.append(cleaned_line)
                # Skip until we find the closing )
                i += 1
                while i < len(lines) and not lines[i].strip().endswith(')'):
                    i += 1
                # Skip the closing ) line too
                if i < len(lines):
                    i += 1
            else:
                cleaned_lines.append(line)
                i += 1
        
        content = '\n'.join(cleaned_lines)
        
        # Write back if changes made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix syntax errors in test files."""
    print("🔧 Fixing Syntax Errors from Import Replacements")
    print("=" * 50)
    
    test_dir = Path('tests')
    fixed_files = []
    
    for test_file in test_dir.rglob('*.py'):
        if 'archives' in str(test_file):
            continue
            
        if fix_syntax_errors_in_file(test_file):
            fixed_files.append(test_file)
            print(f"✅ Fixed: {test_file}")
    
    print(f"\n🎯 Summary: Fixed {len(fixed_files)} files")
    
    if fixed_files:
        print("\nRecommended next step:")
        print("python -m pytest tests/ -x --tb=short --disable-warnings --ignore=tests/archives")

if __name__ == "__main__":
    main()