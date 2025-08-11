#!/usr/bin/env python3
"""
Fix missing import statements for classes used in test files.
"""

import re
from pathlib import Path

def fix_missing_imports(file_path):
    """Add missing import statements for classes used in the file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Dictionary of class names to their proper import statements
    missing_imports = {
        'TemplateEngine': 'from mcp_task_orchestrator.infrastructure.template_system.template_engine import TemplateEngine',
        'TemplateSecurityValidator': 'from mcp_task_orchestrator.infrastructure.template_system.security_validator import TemplateSecurityValidator',
        'JSON5Parser': 'from mcp_task_orchestrator.infrastructure.template_system.json5_parser import JSON5Parser',
        'ParameterSubstitutionError': 'from mcp_task_orchestrator.infrastructure.template_system.exceptions import ParameterSubstitutionError',
        'TemplateValidationError': 'from mcp_task_orchestrator.infrastructure.template_system.exceptions import TemplateValidationError',
        'SecurityValidationError': 'from mcp_task_orchestrator.infrastructure.template_system.exceptions import SecurityValidationError',
        'JSON5ValidationError': 'from mcp_task_orchestrator.infrastructure.template_system.exceptions import JSON5ValidationError',
        'ExecutionResult': 'from mcp_task_orchestrator.domain.value_objects.execution_result import ExecutionResult',
        'APIKeyManager': 'from mcp_task_orchestrator.infrastructure.security.authentication import APIKeyManager',
        'Role': 'from mcp_task_orchestrator.domain.value_objects.role import Role',
        'Permission': 'from mcp_task_orchestrator.domain.value_objects.permission import Permission'
    }
    
    # Find classes that are used but not imported
    used_classes = set()
    for class_name in missing_imports.keys():
        if class_name in content and not re.search(rf'import.*{class_name}', content):
            used_classes.add(class_name)
    
    if used_classes:
        # Find the end of existing imports
        lines = content.split('\n')
        import_end_index = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                import_end_index = i
            elif line.strip() == '' and import_end_index > 0:
                continue
            elif line.strip().startswith('#') and 'TODO: Complete this import' in line:
                # Replace TODO comment with actual imports
                import_lines = []
                for class_name in sorted(used_classes):
                    import_lines.append(missing_imports[class_name])
                lines[i] = '\n'.join(import_lines)
                content = '\n'.join(lines)
                break
            elif line.strip() and not line.strip().startswith('#') and import_end_index > 0:
                # Insert imports after the last import
                import_lines = []
                for class_name in sorted(used_classes):
                    import_lines.append(missing_imports[class_name])
                
                # Insert the imports
                lines.insert(import_end_index + 1, '')
                for j, import_line in enumerate(import_lines):
                    lines.insert(import_end_index + 2 + j, import_line)
                
                content = '\n'.join(lines)
                break
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, used_classes
    return False, set()

def main():
    """Fix missing imports in test files."""
    test_files_with_missing_imports = [
        'tests/security/conftest.py',
        'tests/unit/template_system/test_template_engine.py',
        'tests/unit/template_system/test_json5_parser.py',
        'tests/security/template_system/test_template_security.py'
    ]
    
    fixed_count = 0
    for file_path in test_files_with_missing_imports:
        path = Path(file_path)
        if path.exists():
            fixed, imported_classes = fix_missing_imports(path)
            if fixed:
                print(f"Added imports for {imported_classes} in: {file_path}")
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()