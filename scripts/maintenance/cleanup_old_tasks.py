#!/usr/bin/env python3
"""
Direct cleanup script to archive old tasks from the database.
"""

import sqlite3
import datetime
from pathlib import Path
import json

def cleanup_old_tasks(db_path, age_days=2):
    """Archive tasks older than specified days."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calculate cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=age_days)
    
    print(f"Archiving tasks older than {age_days} days (before {cutoff_date.strftime('%Y-%m-%d')})")
    print("=" * 80)
    
    # Find old active/pending tasks
    cursor.execute("""
        SELECT task_id, title, status, specialist_type, created_at 
        FROM subtasks 
        WHERE status IN ('active', 'pending') 
        AND created_at < ?
        ORDER BY created_at
    """, (cutoff_date.isoformat(),))
    
    old_tasks = cursor.fetchall()
    
    if not old_tasks:
        print("No old tasks found to archive.")
        return
    
    print(f"\nFound {len(old_tasks)} tasks to archive:")
    
    # Create archive record
    archive_data = {
        'archived_at': datetime.datetime.now().isoformat(),
        'reason': f'Tasks older than {age_days} days',
        'tasks': []
    }
    
    for task in old_tasks:
        task_id, title, status, specialist_type, created_at = task
        print(f"\n  - {task_id}")
        print(f"    Title: {title}")
        print(f"    Status: {status}")
        print(f"    Created: {created_at}")
        
        archive_data['tasks'].append({
            'task_id': task_id,
            'title': title,
            'status': status,
            'specialist_type': specialist_type,
            'created_at': created_at
        })
    
    # Save archive
    archive_dir = Path("archives/task_cleanup")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archive_file = archive_dir / f"archived_tasks_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(archive_file, 'w') as f:
        json.dump(archive_data, f, indent=2)
    
    print(f"\n\nArchive saved to: {archive_file}")
    
    # Ask for confirmation
    response = input("\nProceed with archiving these tasks? (yes/no): ")
    
    if response.lower() == 'yes':
        # Update tasks to completed with archive note
        for task in old_tasks:
            cursor.execute("""
                UPDATE subtasks 
                SET status = 'completed',
                    results = 'Archived due to age (auto-cleanup)',
                    completed_at = ?
                WHERE task_id = ?
            """, (datetime.datetime.now().isoformat(), task[0]))
        
        conn.commit()
        print(f"\n✓ Successfully archived {len(old_tasks)} tasks")
    else:
        print("\nArchiving cancelled.")
    
    conn.close()

if __name__ == "__main__":
    db_path = Path("task_orchestrator.db")
    
    if not db_path.exists():
        print("Database not found!")
        exit(1)
    
    cleanup_old_tasks(db_path)