#!/usr/bin/env python3
"""
Diagnose database issues in the MCP Task Orchestrator.
"""

import sqlite3
import json
from pathlib import Path

def diagnose_database():
    """Diagnose issues in the task orchestrator database."""
    # Get project root (go up from scripts/diagnostics/ to project root)
    project_root = Path(__file__).parent.parent.parent
    
    # Try multiple possible database locations
    possible_paths = [
        project_root / "task_orchestrator.db",  # Main location
        project_root / "data" / "task_orchestrator.db",  # New organized location
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = path
            break
    
    if db_path is None:
        print("Database file not found in any expected location:")
        for path in possible_paths:
            print(f"  Checked: {path}")
        return
    
    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return
    
    print(f"Analyzing database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        
        # Check table structure
        print("\n=== TABLE STRUCTURES ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
        
        # Check artifacts column issues
        print("\n=== ARTIFACTS COLUMN ANALYSIS ===")
        cursor.execute("""
            SELECT task_id, artifacts, 
                   CASE 
                       WHEN artifacts IS NULL THEN 'NULL'
                       WHEN artifacts = '' THEN 'EMPTY_STRING'
                       WHEN artifacts LIKE '[%]' THEN 'JSON_ARRAY'
                       WHEN artifacts LIKE '{%}' THEN 'JSON_OBJECT'
                       ELSE 'STRING'
                   END as data_type
            FROM subtasks 
            WHERE artifacts IS NOT NULL
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        data_type_counts = {}
        problem_records = []
        
        for row in results:
            task_id, artifacts, data_type = row
            if data_type not in data_type_counts:
                data_type_counts[data_type] = 0
            data_type_counts[data_type] += 1
            
            if data_type == 'STRING':
                problem_records.append((task_id, artifacts))
            
            print(f"Task {task_id}: {data_type} -> {artifacts[:50]}{'...' if len(str(artifacts)) > 50 else ''}")
        
        print(f"\n=== DATA TYPE SUMMARY ===")
        for dtype, count in data_type_counts.items():
            print(f"{dtype}: {count} records")
        
        if problem_records:
            print(f"\n=== PROBLEM RECORDS (STRING ARTIFACTS) ===")
            for task_id, artifacts in problem_records:
                print(f"Task {task_id}: {artifacts}")
        
        # Check for missing cleanup_stale_locks related tables
        print("\n=== LOCK TRACKING ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%lock%'")
        lock_tables = cursor.fetchall()
        
        if lock_tables:
            print("Lock tracking tables found:")
            for table in lock_tables:
                print(f"  {table[0]}")
        else:
            print("No lock tracking tables found")
        
        # Check record counts
        print("\n=== RECORD COUNTS ===")
        cursor.execute("SELECT COUNT(*) FROM task_breakdowns")
        breakdown_count = cursor.fetchone()[0]
        print(f"Task breakdowns: {breakdown_count}")
        
        cursor.execute("SELECT COUNT(*) FROM subtasks")
        subtask_count = cursor.fetchone()[0]
        print(f"Subtasks: {subtask_count}")
        
        # Check for problematic subtasks specifically mentioned in logs
        print("\n=== CHECKING SPECIFIC PROBLEMATIC TASKS ===")
        problematic_tasks = ['task_159abae8', 'task_56e556bb']
        
        for task_id in problematic_tasks:
            cursor.execute("SELECT COUNT(*) FROM subtasks WHERE parent_task_id = ?", (task_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"\nTask {task_id} has {count} subtasks")
                cursor.execute("""
                    SELECT task_id, artifacts 
                    FROM subtasks 
                    WHERE parent_task_id = ? AND artifacts IS NOT NULL
                """, (task_id,))
                subtasks_data = cursor.fetchall()
                for st_id, artifacts in subtasks_data:
                    print(f"  Subtask {st_id}: {artifacts}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_database()
