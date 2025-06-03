#!/usr/bin/env python3
"""Verify database schema fix and orchestrator status"""
import sqlite3
import os
import sys

def check_database():
    """Check if database has correct schema"""
    db_path = '.task_orchestrator/task_orchestrator.db'
    
    if not os.path.exists(db_path):
        print("❌ Database not found at", db_path)
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get column info
    cursor.execute("PRAGMA table_info(subtasks)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    # Required columns
    required = {
        'verification_status': 'TEXT',
        'prerequisite_satisfaction_required': 'BOOLEAN', 
        'auto_maintenance_enabled': 'BOOLEAN',
        'quality_gate_level': 'TEXT'
    }
    
    print("\n📊 Database Schema Check:")
    print(f"Database: {db_path}")
    print(f"Total columns: {len(columns)}")
    
    all_present = True
    for col_name, col_type in required.items():
        if col_name in columns:
            print(f"  ✅ {col_name} ({col_type})")
        else:
            print(f"  ❌ {col_name} ({col_type}) - MISSING")
            all_present = False
    
    conn.close()
    return all_present

def check_orchestrator():
    """Check if orchestrator can be imported"""
    print("\n🔧 Orchestrator Import Check:")
    try:
        from mcp_task_orchestrator.server import serve
        print("  ✅ Can import server module")
        return True
    except ImportError as e:
        print(f"  ❌ Cannot import server: {e}")
        print("\n💡 To fix: Activate the virtual environment:")
        print("   Windows: venv_mcp\\Scripts\\activate")
        print("   Linux/WSL: python -m venv venv_linux && source venv_linux/bin/activate")
        return False

if __name__ == "__main__":
    print("🚀 MCP Task Orchestrator Verification")
    print("=" * 40)
    
    db_ok = check_database()
    import_ok = check_orchestrator()
    
    print("\n📋 Summary:")
    print(f"  Database schema: {'✅ Fixed' if db_ok else '❌ Needs fix'}")
    print(f"  Orchestrator import: {'✅ Ready' if import_ok else '❌ Need venv'}")
    
    if db_ok and import_ok:
        print("\n✅ Task orchestrator is ready to use!")
        sys.exit(0)
    else:
        print("\n⚠️  Issues detected. See above for details.")
        sys.exit(1)