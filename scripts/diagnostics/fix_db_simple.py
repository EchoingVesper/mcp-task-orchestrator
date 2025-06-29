import sqlite3
import os

# Change to project directory
os.chdir(r"E:\dev\mcp-servers\mcp-task-orchestrator")

print("Checking database schema...")

# Connect to database
conn = sqlite3.connect("task_orchestrator.db")
cursor = conn.cursor()

# Check subtasks table schema
cursor.execute("PRAGMA table_info(subtasks)")
columns = cursor.fetchall()
print("Current subtasks table schema:")
actual_columns = {}
for col in columns:
    actual_columns[col[1]] = col[2]
    print(f"  - {col[1]}: {col[2]}")

# Missing columns to add
missing_columns = []
expected_columns = {
    'file_operations_count': 'INTEGER DEFAULT 0',
    'verification_status': 'TEXT DEFAULT \'pending\'',
    'prerequisite_satisfaction_required': 'BOOLEAN DEFAULT 0',
    'auto_maintenance_enabled': 'BOOLEAN DEFAULT 1', 
    'quality_gate_level': 'TEXT DEFAULT \'standard\''
}

for col_name, col_def in expected_columns.items():
    if col_name not in actual_columns:
        missing_columns.append((col_name, col_def))

if missing_columns:
    print(f"Missing columns: {[col[0] for col in missing_columns]}")
    print("Fixing schema...")
    
    for col_name, col_def in missing_columns:
        try:
            sql = f"ALTER TABLE subtasks ADD COLUMN {col_name} {col_def};"
            cursor.execute(sql)
            print(f"Added: {col_name}")
        except Exception as e:
            if "duplicate column name" in str(e):
                print(f"Column already exists: {col_name}")
            else:
                print(f"Failed to add {col_name}: {e}")
    
    conn.commit()
    print("Schema fix completed!")
else:
    print("All columns present!")

conn.close()

# Test import
print("Testing orchestrator import...")
try:
    from mcp_task_orchestrator.db.persistence import DatabasePersistenceManager
    persistence = DatabasePersistenceManager()
    tasks = persistence.get_all_active_tasks()
    print(f"Successfully imported and got {len(tasks)} active tasks")
    persistence.dispose()
    print("Orchestrator is working!")
except Exception as e:
    print(f"Import failed: {e}")
