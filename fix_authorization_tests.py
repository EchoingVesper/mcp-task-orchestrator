#!/usr/bin/env python3
"""
Script to systematically fix authorization test API mismatches.

This script updates authorization tests to match the new API where:
- Handlers must accept **kwargs to handle _authz_metadata parameter
- Security decorators pass additional metadata through kwargs
"""

import re
import sys
from pathlib import Path


def fix_authorization_handler_signatures(file_path):
    """Fix authorization test handler signatures in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Fix handler function signatures to accept **kwargs
    patterns = [
        r'async def (\w+_handler)\(context, args\):',
        r'async def (\w+_task_handler)\(context, args\):',
        r'async def (\w+_user_handler)\(context, args\):',
        r'async def (\w+_admin_handler)\(context, args\):',
        r'async def (protected_\w+)\(context, args\):',
        r'async def (test_\w+_handler)\(context, args\):',
    ]
    
    for pattern in patterns:
        replacement = r'async def \1(context, args, **kwargs):'
        content = re.sub(pattern, replacement, content)
    
    # Fix lambda handlers too
    content = re.sub(
        r'lambda context, args:',
        r'lambda context, args, **kwargs:',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Fixed {file_path}")
        return True
    
    return False


def main():
    """Fix authorization test files."""
    test_dir = Path("tests/security")
    
    files_to_fix = [
        "test_authorization.py",
        "test_attack_vectors.py"
    ]
    
    fixed_count = 0
    for file_name in files_to_fix:
        file_path = test_dir / file_name
        if file_path.exists():
            if fix_authorization_handler_signatures(file_path):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")
    return fixed_count > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)