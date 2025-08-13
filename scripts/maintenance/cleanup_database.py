#!/usr/bin/env python3
"""
Database Cleanup Utility for MCP Task Orchestrator

This script provides safe database cleanup operations including:
- Removing completed tasks older than specified days
- Clearing all test/development tasks
- Archiving old tasks before deletion
- Database optimization and maintenance
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import shutil

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def find_database():
    """Find the database file in possible locations."""
    project_root = get_project_root()
    possible_paths = [
        project_root / "task_orchestrator.db",
        project_root / "data" / "task_orchestrator.db",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def backup_database(db_path):
    """Create a backup of the database before cleanup."""
    backup_dir = get_project_root() / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"task_orchestrator_backup_{timestamp}.db"
    
    print(f"Creating backup: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path

def get_database_stats(db_path):
    """Get current database statistics."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Get task counts
        cursor.execute("SELECT COUNT(*) FROM task_breakdowns")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subtasks")
        subtask_count = cursor.fetchone()[0]
        
        # Get completed tasks
        cursor.execute("SELECT COUNT(*) FROM subtasks WHERE status = 'completed'")
        completed_count = cursor.fetchone()[0]
        
        # Get pending tasks
        cursor.execute("SELECT COUNT(*) FROM subtasks WHERE status = 'pending'")
        pending_count = cursor.fetchone()[0]
        
        # Get locks
        cursor.execute("SELECT COUNT(*) FROM lock_tracking")
        lock_count = cursor.fetchone()[0]
        
        return {
            'tasks': task_count,
            'subtasks': subtask_count, 
            'completed': completed_count,
            'pending': pending_count,
            'locks': lock_count
        }
    finally:
        conn.close()

def clear_old_completed_tasks(db_path, days_old=7, dry_run=True):
    """Clear completed tasks older than specified days."""
    cutoff_date = datetime.now() - timedelta(days=days_old)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Find old completed tasks
        cursor.execute("""
            SELECT DISTINCT parent_task_id 
            FROM subtasks 
            WHERE status = 'completed' 
            AND completed_at < ?
        """, (cutoff_str,))
        
        old_tasks = cursor.fetchall()
        
        if dry_run:
            print(f"DRY RUN: Would remove {len(old_tasks)} completed tasks older than {days_old} days")
            for task in old_tasks[:5]:  # Show first 5
                print(f"  - {task[0]}")
            if len(old_tasks) > 5:
                print(f"  ... and {len(old_tasks) - 5} more")
            return len(old_tasks)
        
        # Actually delete old tasks
        for task_id_tuple in old_tasks:
            task_id = task_id_tuple[0]
            
            # Delete subtasks first
            cursor.execute("DELETE FROM subtasks WHERE parent_task_id = ?", (task_id,))
            
            # Delete parent task
            cursor.execute("DELETE FROM task_breakdowns WHERE parent_task_id = ?", (task_id,))
        
        conn.commit()
        print(f"Removed {len(old_tasks)} completed tasks older than {days_old} days")
        return len(old_tasks)
        
    finally:
        conn.close()

def clear_all_test_tasks(db_path, dry_run=True):
    """Clear all test/development tasks (tasks with 'test' in ID or description)."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Find test tasks by ID pattern or description
        cursor.execute("""
            SELECT parent_task_id, description 
            FROM task_breakdowns 
            WHERE parent_task_id LIKE '%test%' 
            OR description LIKE '%test%'
            OR description LIKE '%Test%'
            OR description LIKE '%testing%'
            OR description LIKE '%Testing%'
        """)
        
        test_tasks = cursor.fetchall()
        
        if dry_run:
            print(f"DRY RUN: Would remove {len(test_tasks)} test/development tasks")
            for task_id, desc in test_tasks[:5]:  # Show first 5
                print(f"  - {task_id}: {desc[:50]}...")
            if len(test_tasks) > 5:
                print(f"  ... and {len(test_tasks) - 5} more")
            return len(test_tasks)
        
        # Actually delete test tasks
        for task_id, _ in test_tasks:
            # Delete subtasks first
            cursor.execute("DELETE FROM subtasks WHERE parent_task_id = ?", (task_id,))
            
            # Delete parent task
            cursor.execute("DELETE FROM task_breakdowns WHERE parent_task_id = ?", (task_id,))
        
        conn.commit()
        print(f"Removed {len(test_tasks)} test/development tasks")
        return len(test_tasks)
        
    finally:
        conn.close()

def clear_all_tasks(db_path, dry_run=True):
    """Clear ALL tasks and subtasks (nuclear option)."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Get counts first
        cursor.execute("SELECT COUNT(*) FROM task_breakdowns")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM subtasks")
        subtask_count = cursor.fetchone()[0]
        
        if dry_run:
            print(f"DRY RUN: Would remove ALL {task_count} tasks and {subtask_count} subtasks")
            print("WARNING: This will completely clear the task database!")
            return task_count + subtask_count
        
        # Clear all data
        cursor.execute("DELETE FROM subtasks")
        cursor.execute("DELETE FROM task_breakdowns")
        
        conn.commit()
        print(f"CLEARED ALL: Removed {task_count} tasks and {subtask_count} subtasks")
        return task_count + subtask_count
        
    finally:
        conn.close()

def clear_stale_locks(db_path, dry_run=True):
    """Clear stale locks older than 1 hour."""
    cutoff_date = datetime.now() - timedelta(hours=1)
    cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Find stale locks
        cursor.execute("""
            SELECT resource_name, locked_at 
            FROM lock_tracking 
            WHERE locked_at < ?
        """, (cutoff_str,))
        
        stale_locks = cursor.fetchall()
        
        if dry_run:
            print(f"DRY RUN: Would remove {len(stale_locks)} stale locks")
            for resource, locked_at in stale_locks:
                print(f"  - {resource} (locked: {locked_at})")
            return len(stale_locks)
        
        # Clear stale locks
        cursor.execute("DELETE FROM lock_tracking WHERE locked_at < ?", (cutoff_str,))
        
        conn.commit()
        print(f"Removed {len(stale_locks)} stale locks")
        return len(stale_locks)
        
    finally:
        conn.close()

def optimize_database(db_path):
    """Optimize database performance."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("Optimizing database...")
        
        # VACUUM to reclaim space
        cursor.execute("VACUUM")
        
        # ANALYZE to update statistics
        cursor.execute("ANALYZE")
        
        print("Database optimization complete")
        
    finally:
        conn.close()

def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(description="MCP Task Orchestrator Database Cleanup")
    parser.add_argument("--old-completed", type=int, metavar="DAYS", 
                       help="Remove completed tasks older than DAYS (default: 7)")
    parser.add_argument("--test-tasks", action="store_true",
                       help="Remove all test/development tasks")
    parser.add_argument("--all-tasks", action="store_true",
                       help="Remove ALL tasks (DANGER: complete wipe)")
    parser.add_argument("--stale-locks", action="store_true",
                       help="Remove stale locks older than 1 hour")
    parser.add_argument("--optimize", action="store_true",
                       help="Optimize database (VACUUM and ANALYZE)")
    parser.add_argument("--execute", action="store_true",
                       help="Actually perform operations (default is dry-run)")
    parser.add_argument("--backup", action="store_true",
                       help="Create backup before any operations")
    
    args = parser.parse_args()
    
    # Find database
    db_path = find_database()
    if not db_path:
        print("[ERROR] Database not found!")
        return 1
    
    print(f"[DATABASE] {db_path}")
    
    # Show current stats
    stats = get_database_stats(db_path)
    print("\n[STATS] Current Stats:")
    print(f"   Tasks: {stats['tasks']}")
    print(f"   Subtasks: {stats['subtasks']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Locks: {stats['locks']}")
    print()
    
    # Create backup if requested
    if args.backup or not args.execute:
        backup_path = backup_database(db_path)
        print()
    
    dry_run = not args.execute
    if dry_run:
        print("[DRY RUN] No changes will be made")
        print("Use --execute to perform actual cleanup")
        print()
    
    total_removed = 0
    
    # Perform requested operations
    if args.old_completed is not None:
        days = args.old_completed if args.old_completed > 0 else 7
        removed = clear_old_completed_tasks(db_path, days, dry_run)
        total_removed += removed
        print()
    
    if args.test_tasks:
        removed = clear_all_test_tasks(db_path, dry_run)
        total_removed += removed
        print()
    
    if args.all_tasks:
        if not dry_run:
            confirm = input("[WARNING] Are you sure you want to delete ALL tasks? (type 'YES' to confirm): ")
            if confirm != 'YES':
                print("Aborted.")
                return 0
        removed = clear_all_tasks(db_path, dry_run)
        total_removed += removed
        print()
    
    if args.stale_locks:
        removed = clear_stale_locks(db_path, dry_run)
        total_removed += removed
        print()
    
    if args.optimize and not dry_run:
        optimize_database(db_path)
        print()
    
    # Show final stats
    if not dry_run and total_removed > 0:
        final_stats = get_database_stats(db_path)
        print("[STATS] Final Stats:")
        print(f"   Tasks: {final_stats['tasks']} (was {stats['tasks']})")
        print(f"   Subtasks: {final_stats['subtasks']} (was {stats['subtasks']})")
        print(f"   Completed: {final_stats['completed']} (was {stats['completed']})")
        print(f"   Pending: {final_stats['pending']} (was {stats['pending']})")
        print(f"   Locks: {final_stats['locks']} (was {stats['locks']})")
        print(f"\n[SUCCESS] Cleanup complete! Removed {total_removed} items")
    elif dry_run:
        print(f"[INFO] Would remove {total_removed} items total")
        print("Run with --execute to perform actual cleanup")
    
    return 0

if __name__ == "__main__":
    exit(main())
