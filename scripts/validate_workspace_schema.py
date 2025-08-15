#!/usr/bin/env python3
"""
Simple validation script for workspace paradigm database schema.

This script validates the SQL schema files and ensures they are syntactically correct
without requiring external dependencies.
"""

import os
import sqlite3
import tempfile
from pathlib import Path


def validate_sql_file(sql_file_path):
    """Validate a SQL file by executing it against a temporary database."""
    print(f"Validating {sql_file_path.name}...")
    
    if not sql_file_path.exists():
        print(f"  ✗ File does not exist: {sql_file_path}")
        return False
    
    # Read SQL content
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False
    
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Execute the entire SQL content at once to handle complex statements like triggers
        try:
            cursor.executescript(sql_content)
        except sqlite3.Error as e:
            print(f"  ✗ SQL error: {e}")
            return False
        
        conn.commit()
        
        # Validate tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print("  ✓ SQL syntax valid")
        print(f"  ✓ Tables created: {len(tables)}")
        
        # Check for workspace-specific tables
        workspace_tables = [t for t in tables if 'workspace' in t.lower()]
        if workspace_tables:
            print(f"  ✓ Workspace tables: {', '.join(workspace_tables)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
        return False
    finally:
        conn.close()
        os.unlink(db_path)


def validate_python_file(py_file_path):
    """Validate a Python file by checking syntax."""
    print(f"Validating {py_file_path.name}...")
    
    if not py_file_path.exists():
        print(f"  ✗ File does not exist: {py_file_path}")
        return False
    
    try:
        with open(py_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check syntax
        compile(content, py_file_path, 'exec')
        print("  ✓ Python syntax valid")
        
        # Count classes and functions
        lines = content.split('\n')
        classes = [line for line in lines if line.strip().startswith('class ')]
        functions = [line for line in lines if line.strip().startswith('def ')]
        
        print(f"  ✓ Classes defined: {len(classes)}")
        print(f"  ✓ Functions defined: {len(functions)}")
        
        return True
        
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
        return False


def validate_directory_structure():
    """Validate the project directory structure for workspace paradigm."""
    print("Validating directory structure...")
    
    project_root = Path(__file__).parent.parent
    
    # Check key directories
    key_dirs = [
        'mcp_task_orchestrator',
        'mcp_task_orchestrator/db',
        'mcp_task_orchestrator/orchestrator',
        'scripts',
        'tests'
    ]
    
    missing_dirs = []
    for dir_path in key_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
        else:
            print(f"  ✓ {dir_path}")
    
    if missing_dirs:
        print(f"  ✗ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    return True


def main():
    """Main validation function."""
    print("MCP Task Orchestrator - Workspace Schema Validation")
    print("=" * 55)
    
    project_root = Path(__file__).parent.parent
    db_dir = project_root / 'mcp_task_orchestrator' / 'db'
    
    success = True
    
    # Validate directory structure
    if not validate_directory_structure():
        success = False
    
    print()
    
    # Validate SQL schema files
    sql_files = [
        db_dir / 'workspace_schema.sql',
        db_dir / 'generic_task_schema.sql'
    ]
    
    for sql_file in sql_files:
        if not validate_sql_file(sql_file):
            success = False
        print()
    
    # Validate Python files
    python_files = [
        db_dir / 'workspace_migration.py',
        db_dir / 'models.py',
        project_root / 'mcp_task_orchestrator' / 'orchestrator' / 'directory_detection.py'
    ]
    
    for py_file in python_files:
        if not validate_python_file(py_file):
            success = False
        print()
    
    # Test basic workspace detection logic (without imports)
    print("Testing workspace detection logic...")
    try:
        # Test project marker detection
        project_markers = {
            'pyproject.toml': {'confidence': 9, 'type': 'python'},
            'package.json': {'confidence': 9, 'type': 'javascript'},
            'Cargo.toml': {'confidence': 9, 'type': 'rust'},
            'go.mod': {'confidence': 9, 'type': 'go'}
        }
        
        detected_markers = []
        for marker_file in project_markers.keys():
            marker_path = project_root / marker_file
            if marker_path.exists():
                detected_markers.append(marker_file)
        
        print(f"  ✓ Project markers detected: {', '.join(detected_markers) if detected_markers else 'None'}")
        
        # Test git detection
        git_dir = project_root / '.git'
        if git_dir.exists():
            print("  ✓ Git repository detected")
        else:
            print("  - No git repository found")
        
        # Test directory writability
        test_file = project_root / '.test_write'
        try:
            test_file.write_text('test')
            test_file.unlink()
            print("  ✓ Directory is writable")
        except:
            print("  ✗ Directory is not writable")
            success = False
            
    except Exception as e:
        print(f"  ✗ Logic test error: {e}")
        success = False
    
    print()
    print("=" * 55)
    
    if success:
        print("🎉 All validations passed!")
        print("The workspace paradigm implementation is syntactically correct.")
        print("\nNext steps:")
        print("1. Install required dependencies (SQLAlchemy, pydantic)")
        print("2. Run full migration tests")
        print("3. Update orchestrator to use workspace paradigm")
    else:
        print("❌ Some validations failed.")
        print("Please fix the issues before proceeding.")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)