#!/usr/bin/env python3
"""
Fix Legacy Import Errors in Tests - Batch Migration Script

This script automatically fixes the 18 failing test files by updating their imports
from legacy v1.x model paths to new v2.0 Clean Architecture paths.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Maps of old imports to new imports  
IMPORT_MAPPINGS = {
    # Legacy models to Clean Architecture entities
    'from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskStatus, SpecialistType, ComplexityLevel': 
        '# Import Clean Architecture v2.0 models\nfrom mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType\nfrom mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel\nfrom mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType',
    
    'from mcp_task_orchestrator.orchestrator.models import TaskBreakdown, SubTask, TaskResult, TaskStatus, ComplexityLevel, SpecialistType':
        '# Import Clean Architecture v2.0 models\nfrom mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType\nfrom mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel\nfrom mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType\nfrom mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult',
    
    'from mcp_task_orchestrator.orchestrator.models import':
        '# Import Clean Architecture v2.0 models\nfrom mcp_task_orchestrator.domain.entities.task import Task, TaskStatus, TaskType\nfrom mcp_task_orchestrator.domain.value_objects.complexity_level import ComplexityLevel\nfrom mcp_task_orchestrator.domain.value_objects.specialist_type import SpecialistType',
        
    # Legacy installer imports
    'from installer.client_detector import ClientDetector':
        'from mcp_task_orchestrator_cli.platforms.client_detector import ClientDetector',
        
    'from installer.client_detector import':
        'from mcp_task_orchestrator_cli.platforms.client_detector import',
        
    # Legacy role loader imports
    'from mcp_task_orchestrator.orchestrator.role_loader import create_example_roles_file':
        '# create_example_roles_file moved to role management service',
        
    'from mcp_task_orchestrator.orchestrator.role_loader import':
        '# Role loader functions moved to Clean Architecture service layer',
}

# Patterns that need content replacement (not just import changes)
CONTENT_REPLACEMENTS = {
    # Old TaskBreakdown/SubTask usage to new Task hierarchy
    r'TaskBreakdown\(': 'Task(',
    r'SubTask\(': 'Task(',
    r'TaskResult\(': 'ExecutionResult(',
    r'\.parent_task_id': '.task_id',  # TaskBreakdown.parent_task_id -> Task.task_id  
    r'\.subtasks\[': '.children[',    # TaskBreakdown.subtasks -> Task.children
    r'\.subtasks': '.children',       # For general subtasks access
}

def identify_failing_test_files() -> List[Path]:
    """Identify test files that are likely to have import errors."""
    test_files = []
    test_dir = Path('tests')
    
    # Look for Python test files
    for test_file in test_dir.rglob('*.py'):
        # Skip archives and __pycache__ but include main test files  
        if 'archives' in str(test_file) or '__pycache__' in str(test_file):
            continue
            
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # Check for legacy import patterns
            legacy_patterns = [
                'from mcp_task_orchestrator.orchestrator.models import',
                'from installer.client_detector import',
                'from mcp_task_orchestrator.orchestrator.role_loader import',
                'TaskBreakdown',
                'SubTask',
                'TaskResult'
            ]
            
            for pattern in legacy_patterns:
                if pattern in content:
                    test_files.append(test_file)
                    break
                    
        except Exception as e:
            print(f"Warning: Could not read {test_file}: {e}")
            
    return test_files

def fix_imports_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix imports in a single file."""
    changes_made = []
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Apply import replacements
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made.append(f"Replaced import: {old_import[:50]}...")
        
        # Apply content replacements  
        for pattern, replacement in CONTENT_REPLACEMENTS.items():
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                changes_made.append(f"Applied pattern: {pattern}")
        
        # Write back if changes made
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            backup_path.write_text(original_content, encoding='utf-8')
            
            # Write fixed content
            file_path.write_text(content, encoding='utf-8')
            changes_made.append("File updated successfully")
            return True, changes_made
        else:
            return False, ["No changes needed"] 
            
    except Exception as e:
        return False, [f"Error processing file: {e}"]

def main():
    """Main function to fix all failing test files."""
    print("🔧 Fixing Legacy Import Errors in Tests")
    print("=" * 50)
    
    # Find files that need fixing
    failing_files = identify_failing_test_files()
    print(f"Found {len(failing_files)} files with potential legacy imports")
    
    fixed_count = 0
    total_changes = 0
    
    for file_path in failing_files:
        print(f"\n📁 Processing: {file_path}")
        
        success, changes = fix_imports_in_file(file_path)
        
        if success:
            fixed_count += 1
            total_changes += len(changes)
            print("  ✅ Fixed successfully")
            for change in changes:
                print(f"    - {change}")
        else:
            print("  ℹ️  No changes made")
            for msg in changes:
                print(f"    - {msg}")
    
    print(f"\n🎯 Summary:")
    print(f"  - Files processed: {len(failing_files)}")
    print(f"  - Files fixed: {fixed_count}")
    print(f"  - Total changes: {total_changes}")
    
    if fixed_count > 0:
        print(f"\n✨ Recommended next steps:")
        print(f"  1. Run: python -m pytest tests/ -x --tb=short")
        print(f"  2. Check for remaining import errors")
        print(f"  3. Update test logic if needed for new Task model")

if __name__ == "__main__":
    main()