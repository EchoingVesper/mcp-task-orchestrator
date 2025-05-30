#!/usr/bin/env python3
"""
System Health Check - MCP Task Orchestrator

A simplified diagnostic tool for checking system health and project status.
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def check_database():
    """Check database health."""
    print("Database Status:")
    print("-" * 20)
    
    project_root = get_project_root()
    db_paths = [
        project_root / "task_orchestrator.db",
        project_root / "data" / "task_orchestrator.db"
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM task_breakdowns")
                task_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM subtasks") 
                subtask_count = cursor.fetchone()[0]
                conn.close()
                
                print(f"[OK] Database found: {db_path}")
                print(f"  Tasks: {task_count}")
                print(f"  Subtasks: {subtask_count}")
                return True
            except Exception as e:
                print(f"[ERROR] Database error: {e}")
                return False
    
    print("[ERROR] Database not found")
    return False

def check_structure():
    """Check project structure."""
    print("\nProject Structure:")
    print("-" * 20)
    
    project_root = get_project_root()
    required_dirs = [
        "tests/unit", "tests/integration", "tests/performance",
        "scripts/diagnostics", "scripts/maintenance",
        "docs/development", "docs/testing"
    ]
    
    missing = 0
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"[OK] {dir_name}")
        else:
            print(f"[MISSING] {dir_name}")
            missing += 1
    
    return missing == 0

def main():
    """Main health check."""
    print("MCP Task Orchestrator - System Health Check")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")
    print()
    
    db_ok = check_database()
    structure_ok = check_structure()
    
    print("\nSummary:")
    print("-" * 20)
    print(f"Database: {'OK' if db_ok else 'ERROR'}")
    print(f"Structure: {'OK' if structure_ok else 'INCOMPLETE'}")
    
    if db_ok and structure_ok:
        print("\n[SUCCESS] System health: GOOD")
        return True
    else:
        print("\n[WARNING] System health: NEEDS ATTENTION")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
