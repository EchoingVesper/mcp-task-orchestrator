import sys
import os
import sqlite3
import json
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from scripts.migrations.migrate_artifacts import ArtifactsMigrator

def create_test_db(db_path):
    """Create a test database with sample data matching the expected schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the subtasks table expected by the migration
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subtasks (
        task_id TEXT PRIMARY KEY,
        parent_task_id TEXT,
        artifacts TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
    )
    ''')
    
    # Create tasks table for reference
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    # Insert some test tasks
    cursor.executemany(
        'INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)',
        [
            ('task1', 'Parent Task 1', 'pending'),
            ('task2', 'Parent Task 2', 'in_progress'),
            ('task3', 'Parent Task 3', 'completed')
        ]
    )
    
    # Insert test subtasks with various artifact formats
    test_subtasks = [
        # Valid JSON array (should be left as is)
        ('sub1', 'task1', json.dumps(['file1.txt', 'file2.txt'])),
        # Invalid formats that need migration
        ('sub2', 'task1', 'file3.txt'),  # Single file as string
        ('sub3', 'task2', 'file4.txt\nfile5.txt'),  # Newline-separated files
        ('sub4', 'task2', '{"path": "file6.txt"}'),  # JSON object (should be converted to string)
        ('sub5', 'task3', None),  # Null artifacts
        ('sub6', 'task3', ''),  # Empty string
        ('sub7', 'task3', '  ')  # Whitespace only
    ]
    
    cursor.executemany(
        'INSERT INTO subtasks (task_id, parent_task_id, artifacts) VALUES (?, ?, ?)',
        test_subtasks
    )
    
    conn.commit()
    conn.close()

def test_migration(tmp_path, capsys):
    """Test the artifacts migration."""
    # Create a test database
    db_path = tmp_path / "test_artifacts.db"
    create_test_db(db_path)
    
    # Print initial database state
    print("\n=== Initial Database State ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks ORDER BY task_id")
    rows = cursor.fetchall()
    print("Subtasks table:")
    for row in rows:
        print(f"  {row}")
    conn.close()
    
    # Run the migration
    print("\n=== Running Migration ===")
    migrator = ArtifactsMigrator(str(db_path))
    result = migrator.run_migration()
    
    # Verify the migration was successful
    assert result is True, "Migration failed"
    
    # Print post-migration database state with raw content
    print("\n=== Post-Migration Database State (Raw) ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT task_id, parent_task_id, LENGTH(artifacts) as len, SUBSTR(artifacts, 1, 100) as preview FROM subtasks ORDER BY task_id")
    rows = cursor.fetchall()
    print("Subtasks table (raw preview):")
    for row in rows:
        task_id, parent_id, length, preview = row
        print(f"  {task_id}: parent={parent_id}, len={length}, preview={preview!r}")
    
    # Also show the full content of each record
    print("\n=== Detailed Record Content ===")
    cursor.execute("SELECT task_id, artifacts FROM subtasks WHERE artifacts IS NOT NULL ORDER BY task_id")
    rows = cursor.fetchall()
    for task_id, artifacts_json in rows:
        print(f"\nTask ID: {task_id}")
        print(f"Raw JSON: {artifacts_json!r}")
        try:
            parsed = json.loads(artifacts_json)
            print(f"Parsed: {parsed}")
            print(f"Type: {type(parsed)}")
            if isinstance(parsed, list):
                for i, item in enumerate(parsed):
                    print(f"  Item {i}: {item!r} (type: {type(item)})")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
    
    # Check if the artifacts were properly migrated
    cursor.execute("""
        SELECT task_id, artifacts 
        FROM subtasks 
        WHERE artifacts IS NOT NULL 
        ORDER BY task_id
    """)
    rows = cursor.fetchall()
    
    print("\n=== Verifying Migrated Data ===")
    # Expected results after migration
    expected_results = {
        'sub1': ['file1.txt', 'file2.txt'],  # Should remain unchanged
        'sub2': ['file3.txt'],  # Single file should be wrapped in array
        'sub3': ['file4.txt', 'file5.txt'],  # Newline-separated should be split
        'sub4': ["{'path': 'file6.txt'}"],  # JSON object should be converted to string and wrapped in array
    }
    
    # Verify the data
    for task_id, artifacts_json in rows:
        print(f"\nVerifying task_id: {task_id}")
        print(f"Raw artifacts_json: {artifacts_json!r}")
        
        # Skip if we don't have expectations for this task
        if task_id not in expected_results:
            print(f"No expectations for {task_id}, skipping")
            continue
            
        try:
            # Try to parse the JSON
            try:
                artifacts = json.loads(artifacts_json)
                print(f"Parsed artifacts: {artifacts}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse as JSON: {e}")
                print(f"Type: {type(artifacts_json)}")
                print(f"Value: {artifacts_json!r}")
                raise
                
            # Verify against expected results
            expected = expected_results[task_id]
            print(f"Expected: {expected}")
            
            if artifacts != expected:
                print(f"Mismatch for {task_id}: expected {expected}, got {artifacts}")
                print(f"Type of artifacts: {type(artifacts)}")
                if isinstance(artifacts, list) and isinstance(expected, list) and len(artifacts) == len(expected):
                    for i, (a, e) in enumerate(zip(artifacts, expected)):
                        if a != e:
                            print(f"  Item {i} mismatch: {a!r} != {e!r}")
            
            assert artifacts == expected, f"Unexpected artifacts for {task_id}"
            
        except Exception as e:
            print(f"Error verifying {task_id}: {e}")
            raise
    
    # Verify NULL/empty cases
    print("\n=== Verifying NULL/Empty Cases ===")
    cursor.execute("""
        SELECT task_id, artifacts, 
               CASE 
                   WHEN artifacts IS NULL THEN 'NULL' 
                   WHEN TRIM(artifacts) = '' THEN 'EMPTY_STRING' 
                   ELSE 'HAS_VALUE' 
               END as status
        FROM subtasks 
        ORDER BY task_id
    """)
    all_rows = cursor.fetchall()
    
    print("\n=== All Subtasks with Artifacts Status ===")
    for task_id, artifacts, status in all_rows:
        print(f"{task_id}: {status}, value: {artifacts!r}")
    
    # Get just the NULL/empty records
    cursor.execute("""
        SELECT task_id, artifacts 
        FROM subtasks 
        WHERE artifacts IS NULL OR TRIM(COALESCE(artifacts, '')) = ''
        ORDER BY task_id
    """)
    null_rows = cursor.fetchall()
    
    print(f"\nFound {len(null_rows)} NULL/empty records: {null_rows}")
    assert len(null_rows) == 2, f"Expected 2 NULL/empty artifact records, got {len(null_rows)} (sub5 and sub7 should be NULL/empty)"
    
    conn.close()
    
    # Print captured output for debugging
    print("\n=== Test Output ===")
    captured = capsys.readouterr()
    print(captured.out)

def test_migration_nonexistent_db():
    """Test migration with non-existent database."""
    migrator = ArtifactsMigrator("/nonexistent/path/to/db.db")
    result = migrator.run_migration()
    assert result is False, "Migration should fail for non-existent database"

def test_json_object_migration(tmp_path):
    """Test migration of JSON object artifacts."""
    # Create a test database with a JSON object artifact
    db_path = tmp_path / "test_json_migration.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subtasks (
        task_id TEXT PRIMARY KEY,
        parent_task_id TEXT,
        artifacts TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
    )
    ''')
    
    # Insert test data
    cursor.execute("INSERT INTO tasks (id, title, status) VALUES (?, ?, ?)",
                  ('task1', 'Parent Task', 'pending'))
    
    # Insert a subtask with a JSON object as a string
    json_obj = '{"path": "file.txt", "type": "test"}'
    cursor.execute("""
        INSERT INTO subtasks (task_id, parent_task_id, artifacts)
        VALUES (?, ?, ?)
    """, ('sub1', 'task1', json_obj))
    
    conn.commit()
    conn.close()
    
    # Run migration
    migrator = ArtifactsMigrator(str(db_path))
    result = migrator.run_migration()
    assert result is True, "Migration failed"
    
    # Verify the migration
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT artifacts FROM subtasks WHERE task_id = 'sub1'")
    artifacts_json = cursor.fetchone()[0]
    
    # The JSON object should be wrapped in an array
    expected = [json_obj]
    assert json.loads(artifacts_json) == expected, \
        f"Expected {expected}, got {json.loads(artifacts_json)}"
    
    conn.close()
