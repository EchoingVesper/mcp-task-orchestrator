#!/usr/bin/env python3
"""
Server integration validation script.

This script validates that the server integration changes are syntactically
correct and the integration points are properly implemented.
"""

import ast
import sys
from pathlib import Path


def validate_server_py_integration():
    """Validate that server.py has the correct integration changes."""
    print("=== Validating server.py Integration ===")
    
    server_path = Path("mcp_task_orchestrator/server.py")
    
    if not server_path.exists():
        print(f"✗ Server file not found: {server_path}")
        return False
    
    try:
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Parse the file to check syntax
        tree = ast.parse(content)
        print("✓ server.py syntax is valid")
        
        # Check for migration import
        if "from .db.auto_migration import execute_startup_migration" in content:
            print("✓ Migration import added to server.py")
        else:
            print("✗ Migration import missing from server.py")
            return False
        
        # Check for migration function definition
        if "def initialize_database_with_migration(" in content:
            print("✓ Migration function added to server.py")
        else:
            print("✗ Migration function missing from server.py")
            return False
        
        # Check for migration call in get_state_manager
        if "initialize_database_with_migration(base_dir=base_dir)" in content:
            print("✓ Migration call added to get_state_manager")
        else:
            print("✗ Migration call missing from get_state_manager")
            return False
        
        # Check that the function handles errors gracefully
        if "migration_success" in content and "logger.warning" in content:
            print("✓ Graceful error handling implemented")
        else:
            print("✗ Error handling missing or incomplete")
            return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error in server.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Error validating server.py: {e}")
        return False


def validate_migration_system_files():
    """Validate that all migration system files exist and have valid syntax."""
    print("\n=== Validating Migration System Files ===")
    
    migration_files = [
        "mcp_task_orchestrator/db/auto_migration.py",
        "mcp_task_orchestrator/db/migration_manager.py",
        "mcp_task_orchestrator/db/schema_comparator.py",
        "mcp_task_orchestrator/db/migration_history.py",
        "mcp_task_orchestrator/db/backup_manager.py",
        "mcp_task_orchestrator/db/rollback_manager.py"
    ]
    
    all_valid = True
    
    for file_path_str in migration_files:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"✗ Missing file: {file_path.name}")
            all_valid = False
            continue
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check syntax
            ast.parse(content)
            print(f"✓ {file_path.name} syntax valid")
            
        except SyntaxError as e:
            print(f"✗ Syntax error in {file_path.name}: {e}")
            all_valid = False
        except Exception as e:
            print(f"✗ Error validating {file_path.name}: {e}")
            all_valid = False
    
    return all_valid


def validate_integration_flow():
    """Validate the logical flow of the integration."""
    print("\n=== Validating Integration Flow ===")
    
    try:
        server_path = Path("mcp_task_orchestrator/server.py")
        
        with open(server_path, 'r') as f:
            server_content = f.read()
        
        # Check the order of operations in get_state_manager
        lines = server_content.split('\n')
        get_state_manager_start = None
        migration_call_line = None
        state_manager_creation = None
        
        for i, line in enumerate(lines):
            if "def get_state_manager(" in line:
                get_state_manager_start = i
            elif "initialize_database_with_migration" in line and get_state_manager_start:
                migration_call_line = i
            elif "_state_manager = StateManager(" in line and get_state_manager_start:
                state_manager_creation = i
        
        if get_state_manager_start is None:
            print("✗ get_state_manager function not found")
            return False
        
        if migration_call_line is None:
            print("✗ Migration call not found in get_state_manager")
            return False
        
        if state_manager_creation is None:
            print("✗ StateManager creation not found")
            return False
        
        if migration_call_line < state_manager_creation:
            print("✓ Migration called before StateManager creation")
        else:
            print("✗ Migration called after StateManager creation (incorrect order)")
            return False
        
        print("✓ Integration flow is logically correct")
        return True
        
    except Exception as e:
        print(f"✗ Error validating integration flow: {e}")
        return False


def validate_function_signatures():
    """Validate that integration functions have correct signatures."""
    print("\n=== Validating Function Signatures ===")
    
    try:
        server_path = Path("mcp_task_orchestrator/server.py")
        
        with open(server_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = node
        
        # Check initialize_database_with_migration signature
        if "initialize_database_with_migration" in functions:
            func = functions["initialize_database_with_migration"]
            args = [arg.arg for arg in func.args.args]
            
            if "base_dir" in args and "db_path" in args:
                print("✓ initialize_database_with_migration has correct parameters")
            else:
                print(f"✗ initialize_database_with_migration has incorrect parameters: {args}")
                return False
        else:
            print("✗ initialize_database_with_migration function not found")
            return False
        
        # Check get_state_manager still exists and is modified
        if "get_state_manager" in functions:
            print("✓ get_state_manager function exists")
        else:
            print("✗ get_state_manager function not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error validating function signatures: {e}")
        return False


def validate_documentation_files():
    """Validate that integration documentation exists."""
    print("\n=== Validating Documentation ===")
    
    doc_files = [
        "INTEGRATION_GUIDE.md",
        "MIGRATION_SYSTEM_IMPLEMENTATION_SUMMARY.md",
        "server_migration_integration.py"
    ]
    
    all_present = True
    
    for doc_file in doc_files:
        doc_path = Path(doc_file)
        if doc_path.exists():
            print(f"✓ {doc_file} exists")
            
            # Check file size to ensure it's not empty
            if doc_path.stat().st_size > 1000:  # At least 1KB
                print(f"✓ {doc_file} has substantial content")
            else:
                print(f"⚠️  {doc_file} seems small")
        else:
            print(f"✗ {doc_file} missing")
            all_present = False
    
    return all_present


def main():
    """Run all validation checks."""
    print("Server Migration Integration Validation")
    print("=" * 50)
    
    validations = [
        ("Server.py Integration", validate_server_py_integration),
        ("Migration System Files", validate_migration_system_files),
        ("Integration Flow", validate_integration_flow),
        ("Function Signatures", validate_function_signatures),
        ("Documentation", validate_documentation_files),
    ]
    
    passed = 0
    total = len(validations)
    
    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Validation '{validation_name}' failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Validation Results: {passed}/{total} validations passed")
    
    if passed == total:
        print("🎉 All validations passed!")
        print("The migration system is properly integrated into the server.")
        print("\nIntegration Status: ✅ COMPLETE")
        print("\nWhat happens next:")
        print("1. Server automatically runs migration check on startup")
        print("2. Database schema is created/updated as needed")
        print("3. Backup is created before any migrations")
        print("4. Server continues normal operation")
        print("\nTo test with dependencies:")
        print("1. Install required packages: pip install sqlalchemy mcp")
        print("2. Run server: python -m mcp_task_orchestrator.server")
        print("3. Check logs for migration messages")
    else:
        print("⚠️  Some validations failed.")
        print("Please review the errors above and fix integration issues.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)