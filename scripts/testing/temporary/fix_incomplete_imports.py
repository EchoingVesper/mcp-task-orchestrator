#!/usr/bin/env python3
"""
Fix Incomplete Import Lines

This script fixes import lines that end without importing anything.
"""

import os
import re
from pathlib import Path
from typing import List

def fix_incomplete_imports_in_file(file_path: Path) -> bool:
    """Fix incomplete import lines in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check for incomplete import lines (ending with 'import' followed by nothing)
            if re.match(r'^from .+ import\s*$', line.strip()):
                # This is an incomplete import line, comment it out
                fixed_lines.append(f"# {line}  # TODO: Complete this import")
            else:
                fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Write back if changes made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix incomplete imports in test files."""
    print("🔧 Fixing Incomplete Import Lines")
    print("=" * 40)
    
    test_dir = Path('tests')
    fixed_files = []
    
    for test_file in test_dir.rglob('*.py'):
        if 'archives' in str(test_file):
            continue
            
        if fix_incomplete_imports_in_file(test_file):
            fixed_files.append(test_file)
            print(f"✅ Fixed: {test_file}")
    
    print(f"\n🎯 Summary: Fixed {len(fixed_files)} files")

if __name__ == "__main__":
    main()