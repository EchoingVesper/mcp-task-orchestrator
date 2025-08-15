import sqlite3
import os

# Change to project directory
import sys
from pathlib import Path
os.chdir(Path(__file__).parent)

print("🔧 Applying emergency database schema fix...")

# Connect to database
conn = sqlite3.connect("task_orchestrator.db")
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(subtasks)")
columns = cursor.fetchall()
existing_cols = [col[1] for col in columns]
print(f"Current columns: {existing_cols}")

# Add missing columns
fixes = [
    "ALTER TABLE subtasks ADD COLUMN verification_status TEXT DEFAULT 'pending';",
    "ALTER TABLE subtasks ADD COLUMN prerequisite_satisfaction_required BOOLEAN DEFAULT 0;",
    "ALTER TABLE subtasks ADD COLUMN auto_maintenance_enabled BOOLEAN DEFAULT 1;",
    "ALTER TABLE subtasks ADD COLUMN quality_gate_level TEXT DEFAULT 'standard';"
]

applied_fixes = []
for fix in fixes:
    try:
        cursor.execute(fix)
        applied_fixes.append(fix)
        print(f"✅ Applied: {fix}")
    except Exception as e:
        if "duplicate column name" in str(e):
            print(f"⚠️ Column already exists: {fix}")
        else:
            print(f"❌ Failed: {fix} - {e}")

conn.commit()
conn.close()

print(f"\n✅ Applied {len(applied_fixes)} schema fixes!")
print("\n🧪 Testing orchestrator functionality...")

try:
    from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
    persistence = DatabasePersistenceManager()
    tasks = persistence.get_all_active_tasks()
    print(f"✅ Successfully imported and got {len(tasks)} active tasks")
    persistence.dispose()
    print("✅ Database connection disposed properly")
    print("\n🎉 Emergency schema repair SUCCESSFUL!")
    print("\n📋 Next steps:")
    print("1. Restart Claude Desktop to clear any cached tool states")
    print("2. Test the orchestration tools to verify they work") 
    print("3. If working, proceed with Phase 2: orchestrated migration system")
except Exception as e:
    print(f"❌ Orchestrator still not working: {e}")
    print("Additional investigation may be needed")
