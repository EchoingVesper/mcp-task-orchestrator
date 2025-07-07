import sqlite3
import os

# Change to project directory
os.chdir(r"E:\dev\mcp-servers\mcp-task-orchestrator")

print("🔧 Applying emergency database schema fix...")

# Connect to database
conn = sqlite3.connect("task_orchestrator.db")
cursor = conn.cursor()

# Add missing columns (ignore if they already exist)
fixes = [
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
            print(f"⚠️ Already exists: {fix}")
        else:
            print(f"❌ Error: {fix} - {e}")

conn.commit()
conn.close()
print("✅ Schema fix completed!")
