#!/usr/bin/env python3
"""
Fix test files to use the correct Clean Architecture v2.0 API.
Updates Task constructor calls and ExecutionResult usage.
"""

import re
from pathlib import Path

def fix_task_constructor_calls(content):
    """Fix Task constructor calls to include required fields."""
    # Pattern for Task constructor calls
    pattern = r'Task\(\s*([^)]+)\s*\)'
    
    def fix_task_call(match):
        args_str = match.group(1)
        
        # Parse existing arguments
        args = {}
        for arg in args_str.split(','):
            arg = arg.strip()
            if '=' in arg:
                key, value = arg.split('=', 1)
                args[key.strip()] = value.strip()
        
        # Ensure required fields are present
        if 'hierarchy_path' not in args:
            task_id = args.get('task_id', '"test_task"').strip('"\'')
            args['hierarchy_path'] = f'"{task_id}"'
        
        if 'artifacts' in args and isinstance(args['artifacts'], str):
            # Convert string artifacts to list format
            artifact_value = args['artifacts']
            if not artifact_value.startswith('['):
                args['artifacts'] = f'[{artifact_value}]'
        
        # Reconstruct the call
        formatted_args = []
        for key, value in args.items():
            formatted_args.append(f'{key}={value}')
        
        return f'Task(\n        {",\n        ".join(formatted_args)}\n    )'
    
    return re.sub(pattern, fix_task_call, content, flags=re.DOTALL)

def fix_execution_result_calls(content):
    """Fix ExecutionResult constructor calls."""
    # Replace TaskResult with ExecutionResult
    content = re.sub(r'\bTaskResult\b', 'ExecutionResult', content)
    
    # Fix ExecutionResult constructor calls
    pattern = r'ExecutionResult\(\s*([^)]+)\s*\)'
    
    def fix_result_call(match):
        args_str = match.group(1)
        
        # Parse existing arguments
        args = {}
        for arg in args_str.split(','):
            arg = arg.strip()
            if '=' in arg:
                key, value = arg.split('=', 1)
                args[key.strip()] = value.strip()
        
        # Ensure required fields are present for ExecutionResult
        if 'task_id' not in args:
            args['task_id'] = '"test_result"'
        if 'content' not in args:
            args['content'] = '"Test result content"'
        
        if 'artifacts' in args and isinstance(args['artifacts'], str):
            # Convert string artifacts to list format
            artifact_value = args['artifacts']
            if not artifact_value.startswith('['):
                args['artifacts'] = f'[{artifact_value}]'
        
        # Reconstruct the call
        formatted_args = []
        for key, value in args.items():
            formatted_args.append(f'{key}={value}')
        
        return f'ExecutionResult(\n        {",\n        ".join(formatted_args)}\n    )'
    
    return re.sub(pattern, fix_result_call, content, flags=re.DOTALL)

def fix_test_api_usage(file_path):
    """Fix API usage in test files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix Task constructor calls
    content = fix_task_constructor_calls(content)
    
    # Fix ExecutionResult calls
    content = fix_execution_result_calls(content)
    
    # Fix references to old model names
    content = re.sub(r'\bSubTask\b', 'Task', content)
    content = re.sub(r'\bTaskResult\b', 'ExecutionResult', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix API usage in test files."""
    test_files_to_fix = [
        'tests/test_artifacts_validator.py'
    ]
    
    fixed_count = 0
    for file_path in test_files_to_fix:
        path = Path(file_path)
        if path.exists():
            if fix_test_api_usage(path):
                print(f"Fixed API usage in: {file_path}")
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed API usage in {fixed_count} files")

if __name__ == "__main__":
    main()