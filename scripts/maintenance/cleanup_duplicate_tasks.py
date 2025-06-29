#!/usr/bin/env python3
"""Clean up duplicate Generic Task Model tasks, keeping only the enhanced plan."""

import sqlite3
import os
from datetime import datetime

def cleanup_duplicate_tasks():
    """Remove duplicate task plans, keeping only the enhanced version."""
    
    db_path = os.path.join(".task_orchestrator", "orchestrator_state.db")
    
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, let's see what parent tasks we have
        cursor.execute("""
            SELECT DISTINCT parent_task_id, created_at 
            FROM tasks 
            WHERE parent_task_id IS NOT NULL 
            ORDER BY created_at DESC
        """)
        parent_tasks = cursor.fetchall()
        
        print(f"Found {len(parent_tasks)} parent task groups")
        
        # Find all tasks related to Generic Task Model (older versions)
        cursor.execute("""
            SELECT task_id, title, created_at, parent_task_id
            FROM tasks
            WHERE (title LIKE '%Plugin Architecture%' 
                   OR title LIKE '%Task Type Registry%'
                   OR title LIKE '%Extensible%Attributes%'
                   OR title LIKE '%Generic Task Model%')
            AND created_at < '2025-06-03 06:36:00'
            ORDER BY created_at
        """)
        
        old_tasks = cursor.fetchall()
        print(f"\nFound {len(old_tasks)} old Generic Task Model tasks to remove")
        
        if old_tasks:
            # Get parent task IDs from old tasks
            old_parent_ids = set()
            for task in old_tasks:
                if task[3]:  # parent_task_id
                    old_parent_ids.add(task[3])
            
            # Delete old subtasks
            old_task_ids = [task[0] for task in old_tasks]
            placeholders = ','.join('?' * len(old_task_ids))
            cursor.execute(f"DELETE FROM tasks WHERE task_id IN ({placeholders})", old_task_ids)
            
            # Delete old parent tasks
            if old_parent_ids:
                placeholders = ','.join('?' * len(old_parent_ids))
                cursor.execute(f"DELETE FROM tasks WHERE task_id IN ({placeholders})", list(old_parent_ids))
                print(f"Deleted {len(old_parent_ids)} old parent tasks")
            
            print(f"Deleted {len(old_task_ids)} old subtasks")
            
        # Verify what's left
        cursor.execute("""
            SELECT COUNT(*) FROM tasks WHERE status = 'pending'
        """)
        remaining = cursor.fetchone()[0]
        print(f"\n✅ Cleanup complete. {remaining} tasks remaining (should be 24)")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    cleanup_duplicate_tasks()