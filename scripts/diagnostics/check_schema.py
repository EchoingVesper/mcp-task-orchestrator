import sqlite3

conn = sqlite3.connect('task_orchestrator.db')
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(subtasks)")
columns = cursor.fetchall()

print("Subtasks table schema:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

conn.close()