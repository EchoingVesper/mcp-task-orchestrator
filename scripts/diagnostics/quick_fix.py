import sqlite3
import sys
from pathlib import Path

# Change to project directory
import os
os.chdir(r"E:\dev\mcp-servers\mcp-task-orchestrator")

print("🔍 Checking database schema...")

# Connect to database
conn = sqlite3.connect("task_orchestrator.db")
cursor = conn.cursor()

# Check if subtasks table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"📋 Found tables: {tables}")

if 'subtasks' in tables:
    # Check subtasks table schema
    cursor.execute("PRAGMA table_info(subtasks)")
    columns = cursor.fetchall()
    print(f"\n📊 Current subtasks table schema:")
    actual_columns = {}
    for col in columns:
        actual_columns[col[1]] = col[2]
        print(f"  - {col[1]}: {col[2]}")
    
    # Expected columns
    expected = ['task_id', 'parent_task_id', 'title', 'description', 'specialist_type', 
                'dependencies', 'estimated_effort', 'status', 'results', 'artifacts', 
                'file_operations_count', 'verification_status', 'created_at', 'completed_at',
                'prerequisite_satisfaction_required', 'auto_maintenance_enabled', 'quality_gate_level']
    
    missing = [col for col in expected if col not in actual_columns]
    
    if missing:
        print(f"\n❌ Missing columns: {missing}")
        print("\n🔧 Fixing schema...")
        
        # Add missing columns
        fixes = [
            "ALTER TABLE subtasks ADD COLUMN file_operations_count INTEGER DEFAULT 0;",
            "ALTER TABLE subtasks ADD COLUMN verification_status TEXT DEFAULT 'pending';", 
            "ALTER TABLE subtasks ADD COLUMN prerequisite_satisfaction_required BOOLEAN DEFAULT 0;",
            "ALTER TABLE subtasks ADD COLUMN auto_maintenance_enabled BOOLEAN DEFAULT 1;",
            "ALTER TABLE subtasks ADD COLUMN quality_gate_level TEXT DEFAULT 'standard';"
        ]
        
        for fix in fixes:
            try:
                cursor.execute(fix)
                print(f"✅ Applied: {fix}")
            except Exception as e:
                if "duplicate column name" in str(e):
                    print(f"⚠️ Column already exists: {fix}")
                else:
                    print(f"❌ Failed: {fix} - {e}")
        
        conn.commit()
        print("\n✅ Schema fix completed!")
    else:
        print("\n✅ All columns present!")
else:
    print("❌ subtasks table not found!")

conn.close()
print("\n🧪 Testing orchestrator import...")

try:
    from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
    persistence = DatabasePersistenceManager()
    tasks = persistence.get_all_active_tasks()
    print(f"✅ Successfully imported and got {len(tasks)} active tasks")
    persistence.dispose()
except Exception as e:
    print(f"❌ Import failed: {e}")

print("\n✅ Emergency repair completed!")
