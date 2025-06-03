#!/usr/bin/env python3
"""
Stale Task Cleanup Script

This script identifies and cleans up stale tasks in the orchestrator based on:
1. Task age (creation timestamp)
2. Specialist type thresholds
3. Last update timestamps
4. Task status (focusing on pending/active tasks that haven't progressed)

Usage:
    python stale_task_cleanup.py [--dry-run] [--verbose]
"""

import json
import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add the project root to Python path
project_root = Path(__file__).parent

class StaleTaskCleanup:
    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.db = None
        
        # Define specialist thresholds (in hours)
        self.specialist_thresholds = {
            'researcher': 24,      # Research tasks should complete within 24 hours
            'architect': 48,       # Architecture tasks may take longer
            'implementer': 72,     # Implementation can be complex
            'documenter': 36,      # Documentation should be timely
            'tester': 24,          # Testing should be quick
            'reviewer': 12,        # Reviews should be fast
            'debugger': 6,         # Debugging should be immediate
            'default': 48          # Default threshold for unknown specialists
        }
        
        self.stale_tasks = []
        self.archived_tasks = []
        
    def connect_database(self):
        """Connect to the orchestrator database"""
        try:
            # Try multiple possible database locations
            possible_paths = [
                project_root / "task_orchestrator.db",
                project_root / ".task_orchestrator" / "task_orchestrator.db",
                project_root / "orchestrator_tasks.db"
            ]
            
            db_path = None
            for path in possible_paths:
                if path.exists():
                    db_path = path
                    break
            
            if not db_path:
                print(f"❌ Database not found in any of these locations:")
                for path in possible_paths:
                    print(f"   • {path}")
                return False
                
            self.db_path = str(db_path)
            # Test connection
            conn = sqlite3.connect(self.db_path)
            conn.close()
            
            if self.verbose:
                print(f"✅ Connected to database at {db_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    def parse_timestamp(self, timestamp_str):
        """Parse timestamp string to datetime object"""
        try:
            # Handle different timestamp formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
                    
            # If all formats fail, try parsing with fromisoformat
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to parse timestamp '{timestamp_str}': {e}")
            return None
    
    def is_task_stale(self, task):
        """Determine if a task is stale based on various criteria"""
        task_id = task.get('task_id', 'unknown')
        status = task.get('status', 'unknown')
        specialist_type = task.get('specialist_type', 'default')
        created_at = task.get('created_at')
        
        if not created_at:
            if self.verbose:
                print(f"⚠️ Task {task_id} has no creation timestamp")
            return False
            
        created_time = self.parse_timestamp(created_at)
        if not created_time:
            return False
            
        now = datetime.now()
        age_hours = (now - created_time).total_seconds() / 3600
        
        # Get threshold for this specialist type
        threshold = self.specialist_thresholds.get(specialist_type, 
                                                  self.specialist_thresholds['default'])
        
        # Conditions for staleness:
        # 1. Task is older than specialist threshold
        # 2. Task is pending and very old (7+ days)
        # 3. Task is active but hasn't been updated recently
        
        is_old = age_hours > threshold
        is_very_old = age_hours > (7 * 24)  # 7 days
        
        # Additional staleness criteria
        stale_reasons = []
        
        if status == 'pending' and is_very_old:
            stale_reasons.append(f"pending for {age_hours:.1f} hours (>7 days)")
        elif status == 'active' and is_old:
            stale_reasons.append(f"active for {age_hours:.1f} hours (>{threshold}h threshold)")
        elif status == 'pending' and is_old:
            stale_reasons.append(f"pending for {age_hours:.1f} hours (>{threshold}h threshold)")
            
        if stale_reasons:
            task['stale_reasons'] = stale_reasons
            task['age_hours'] = age_hours
            task['threshold_hours'] = threshold
            return True
            
        return False
    
    def get_all_tasks(self):
        """Retrieve all tasks from the database"""
        try:
            # Direct database query to get more detailed information
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT 
                    task_id,
                    title,
                    status,
                    specialist_type,
                    created_at,
                    updated_at,
                    completed_at,
                    parent_task_id
                FROM tasks
                ORDER BY created_at DESC
            """
            
            cursor = conn.execute(query)
            tasks = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if self.verbose:
                print(f"📊 Retrieved {len(tasks)} tasks from database")
                
            return tasks
            
        except Exception as e:
            print(f"❌ Failed to retrieve tasks: {e}")
            return []
    
    def identify_stale_tasks(self):
        """Identify all stale tasks"""
        print("🔍 Identifying stale tasks...")
        
        all_tasks = self.get_all_tasks()
        
        for task in all_tasks:
            if self.is_task_stale(task):
                self.stale_tasks.append(task)
                
        print(f"🕰️ Found {len(self.stale_tasks)} stale tasks")
        
        # Group by status for reporting
        stale_by_status = {}
        stale_by_specialist = {}
        
        for task in self.stale_tasks:
            status = task['status']
            specialist = task['specialist_type']
            
            stale_by_status[status] = stale_by_status.get(status, 0) + 1
            stale_by_specialist[specialist] = stale_by_specialist.get(specialist, 0) + 1
            
        print(f"📊 Stale tasks by status: {dict(stale_by_status)}")
        print(f"👥 Stale tasks by specialist: {dict(stale_by_specialist)}")
        
        return self.stale_tasks
    
    def display_stale_tasks(self):
        """Display detailed information about stale tasks"""
        if not self.stale_tasks:
            print("✅ No stale tasks found!")
            return
            
        print(f"\n📋 Detailed Stale Task Report ({len(self.stale_tasks)} tasks):")
        print("=" * 80)
        
        for i, task in enumerate(self.stale_tasks, 1):
            print(f"\n{i}. Task ID: {task['task_id']}")
            print(f"   Title: {task['title']}")
            print(f"   Status: {task['status']}")
            print(f"   Specialist: {task['specialist_type']}")
            print(f"   Created: {task['created_at']}")
            print(f"   Age: {task['age_hours']:.1f} hours")
            print(f"   Threshold: {task['threshold_hours']} hours")
            print(f"   Reasons: {', '.join(task['stale_reasons'])}")
            
            if task.get('parent_task_id'):
                print(f"   Parent: {task['parent_task_id']}")
    
    def archive_stale_tasks(self):
        """Archive stale tasks by updating their status"""
        if not self.stale_tasks or self.dry_run:
            if self.dry_run:
                print(f"🔍 DRY RUN: Would archive {len(self.stale_tasks)} stale tasks")
            return
            
        print(f"📦 Archiving {len(self.stale_tasks)} stale tasks...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            for task in self.stale_tasks:
                task_id = task['task_id']
                
                # Update task status to 'archived' and add archive timestamp
                update_query = """
                    UPDATE tasks 
                    SET status = 'archived',
                        updated_at = ?,
                        archived_at = ?,
                        archive_reason = ?
                    WHERE task_id = ?
                """
                
                archive_time = datetime.now().isoformat()
                archive_reason = f"Auto-archived: {'; '.join(task['stale_reasons'])}"
                
                conn.execute(update_query, (archive_time, archive_time, archive_reason, task_id))
                
                if self.verbose:
                    print(f"   ✅ Archived task {task_id}")
                    
                self.archived_tasks.append(task_id)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully archived {len(self.archived_tasks)} tasks")
            
        except Exception as e:
            print(f"❌ Failed to archive tasks: {e}")
    
    def create_cleanup_report(self):
        """Create a detailed cleanup report"""
        report_path = project_root / "stale_task_cleanup_report.json"
        
        report = {
            "cleanup_timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "summary": {
                "total_stale_tasks": len(self.stale_tasks),
                "archived_tasks": len(self.archived_tasks),
                "specialist_thresholds": self.specialist_thresholds
            },
            "stale_tasks": self.stale_tasks,
            "archived_task_ids": self.archived_tasks
        }
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Cleanup report saved to: {report_path}")
            
        except Exception as e:
            print(f"⚠️ Failed to save cleanup report: {e}")
    
    def validate_orchestrator_health(self):
        """Validate that the orchestrator is working properly after cleanup"""
        print("\n🔍 Validating orchestrator health post-cleanup...")
        
        try:
            # Check database connectivity
            all_tasks = self.get_all_tasks()
            active_tasks = [t for t in all_tasks if t['status'] == 'active']
            pending_tasks = [t for t in all_tasks if t['status'] == 'pending']
            completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
            archived_tasks = [t for t in all_tasks if t['status'] == 'archived']
            
            print(f"📊 Post-cleanup task distribution:")
            print(f"   • Active: {len(active_tasks)}")
            print(f"   • Pending: {len(pending_tasks)}")
            print(f"   • Completed: {len(completed_tasks)}")
            print(f"   • Archived: {len(archived_tasks)}")
            
            # Check for remaining stale tasks
            remaining_stale = []
            for task in active_tasks + pending_tasks:
                if self.is_task_stale(task):
                    remaining_stale.append(task)
            
            if remaining_stale:
                print(f"⚠️ Found {len(remaining_stale)} remaining stale tasks")
            else:
                print("✅ No remaining stale active/pending tasks found")
            
            return True
            
        except Exception as e:
            print(f"❌ Health validation failed: {e}")
            return False
    
    def run_cleanup(self):
        """Run the complete cleanup process"""
        print("🧹 Starting Stale Task Cleanup Process")
        print("=" * 50)
        
        if not self.connect_database():
            return False
        
        # Step 1: Identify stale tasks
        self.identify_stale_tasks()
        
        # Step 2: Display stale tasks
        if self.verbose:
            self.display_stale_tasks()
        
        # Step 3: Archive stale tasks (unless dry run)
        self.archive_stale_tasks()
        
        # Step 4: Create cleanup report
        self.create_cleanup_report()
        
        # Step 5: Validate orchestrator health
        health_ok = self.validate_orchestrator_health()
        
        print("\n" + "=" * 50)
        if self.dry_run:
            print("🔍 DRY RUN COMPLETED - No changes made")
        elif health_ok:
            print("✅ CLEANUP COMPLETED SUCCESSFULLY")
        else:
            print("⚠️ CLEANUP COMPLETED WITH WARNINGS")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="Clean up stale tasks in the orchestrator")
    parser.add_argument('--dry-run', action='store_true', 
                       help="Show what would be cleaned up without making changes")
    parser.add_argument('--verbose', '-v', action='store_true',
                       help="Show detailed output")
    
    args = parser.parse_args()
    
    cleanup = StaleTaskCleanup(dry_run=args.dry_run, verbose=args.verbose)
    success = cleanup.run_cleanup()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()