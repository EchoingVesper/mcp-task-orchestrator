#!/usr/bin/env python3
"""
Database Schema Fix and Validation
Fixes the schema mismatch and validates orchestrator functionality
"""
import sqlite3
import os
import sys
from pathlib import Path

def main():
    # Ensure we're in the project directory
    project_dir = Path(r"E:\My Work\Programming\MCP Servers\mcp-task-orchestrator")
    os.chdir(project_dir)
    
    print("🔧 Emergency Database Schema Repair")
    print("=" * 50)
    
    # Connect to database
    db_path = "task_orchestrator.db"
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(subtasks)")
        columns = cursor.fetchall()
        existing_cols = [col[1] for col in columns]
        print(f"📊 Current columns: {len(existing_cols)} found")
        
        # Define missing columns to add
        missing_columns = [
            ("verification_status", "TEXT DEFAULT 'pending'"),
            ("prerequisite_satisfaction_required", "BOOLEAN DEFAULT 0"),
            ("auto_maintenance_enabled", "BOOLEAN DEFAULT 1"), 
            ("quality_gate_level", "TEXT DEFAULT 'standard'")
        ]
        
        fixes_applied = 0
        for col_name, col_def in missing_columns:
            if col_name not in existing_cols:
                try:
                    sql = f"ALTER TABLE subtasks ADD COLUMN {col_name} {col_def};"
                    cursor.execute(sql)
                    fixes_applied += 1
                    print(f"✅ Added column: {col_name}")
                except Exception as e:
                    print(f"❌ Failed to add {col_name}: {e}")
            else:
                print(f"⚠️ Column already exists: {col_name}")
        
        if fixes_applied > 0:
            conn.commit()
            print(f"\n✅ Applied {fixes_applied} schema fixes successfully!")
        else:
            print(f"\n✅ No schema fixes needed - all columns present!")
        
        # Test the fixed schema
        print(f"\n🧪 Testing orchestrator functionality...")
        
        # Import and test the persistence manager
        sys.path.insert(0, str(project_dir))
        from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
        
        # Test creating persistence manager
        persistence = DatabasePersistenceManager()
        active_tasks = persistence.get_all_active_tasks()
        print(f"✅ Persistence manager works - found {len(active_tasks)} active tasks")
        
        # Test the core orchestrator
        from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
        orchestrator = TaskOrchestrator()
        print(f"✅ Task orchestrator initialized successfully")
        
        # Clean up
        persistence.dispose()
        
        print(f"\n🎉 EMERGENCY REPAIR SUCCESSFUL!")
        print(f"\n📋 Next Steps:")
        print(f"1. Restart Claude Desktop to clear any cached tool states")
        print(f"2. Test the orchestration tools: orchestrator_initialize_session")
        print(f"3. If working, proceed with Phase 2: orchestrated migration system")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during repair: {e}")
        print(f"Additional troubleshooting may be needed")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
