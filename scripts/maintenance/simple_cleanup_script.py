#!/usr/bin/env python3
"""
Simple cleanup script to archive stale tasks when the database might be locked.
Works by reading the current state and suggesting cleanup actions.
"""

import json
import datetime
from pathlib import Path

def analyze_stale_tasks():
    """Analyze tasks and identify which ones should be archived."""
    
    # Define what constitutes a stale task
    stale_threshold_days = 2  # Tasks older than 2 days
    current_time = datetime.datetime.now()
    
    print("Task Age Analysis")
    print("=" * 80)
    
    # These are the active/pending tasks from the orchestrator
    active_tasks = [
        ("reviewer_195ccb", "2025-06-01T19:44:06", "pending"),
        ("tester_10b158", "2025-06-01T19:44:06", "pending"),
        ("documenter_a3790a", "2025-06-01T17:24:27", "pending"),
        ("tester_a1cd46", "2025-06-01T17:24:27", "pending"),
        ("implementer_7fb268", "2025-06-01T17:24:27", "pending"),
        ("implementer_ddbec5", "2025-06-01T17:24:27", "pending"),
        ("architect_553b67", "2025-06-01T10:21:13", "pending"),
        ("implementer_3a3e34", "2025-06-01T09:27:12", "pending"),
        ("tester_cde7b0", "2025-06-01T09:27:12", "pending"),
        ("implementer_a86b37", "2025-06-01T09:27:12", "pending"),
        ("implementer_5d4aea", "2025-06-01T08:23:13", "pending"),
        ("documenter_bb9bee", "2025-06-01T08:23:13", "active"),
        ("reviewer_1d0d7d", "2025-06-01T05:49:22", "active"),
        ("implementer_849522", "2025-06-01T05:49:22", "pending"),
        ("tester_fda6a3", "2025-06-01T05:49:22", "active"),
        ("implementer_704e8f", "2025-06-01T05:49:22", "pending"),
        ("documenter_de327a", "2025-06-01T05:49:22", "pending"),
        ("implementer_4ee506", "2025-05-30T09:07:58", "active"),
        ("reviewer_398e44", "2025-05-30T09:07:58", "active"),
        ("implementer_e0fbc4", "2025-05-30T09:07:58", "active"),
        ("implementer_ce7374", "2025-05-30T09:07:58", "active"),
        ("documenter_ffbc88", "2025-05-30T09:07:58", "active"),
        ("reviewer_74f538", "2025-05-30T06:26:03", "active"),
        ("tester_0519bf", "2025-05-30T06:26:03", "pending"),
        ("tester_aa7599", "2025-05-30T06:26:03", "pending"),
        ("researcher_f77035", "2025-05-30T06:26:03", "active"),
    ]
    
    stale_tasks = []
    
    for task_id, created_at, status in active_tasks:
        # Parse the creation time
        created = datetime.datetime.fromisoformat(created_at.replace('T', ' '))
        age = current_time - created
        
        print(f"\nTask: {task_id}")
        print(f"  Status: {status}")
        print(f"  Created: {created_at}")
        print(f"  Age: {age.days} days, {age.seconds // 3600} hours")
        
        if age.days >= stale_threshold_days:
            stale_tasks.append({
                'task_id': task_id,
                'status': status,
                'created': created_at,
                'age_days': age.days
            })
            print(f"  → STALE (older than {stale_threshold_days} days)")
    
    print(f"\n\nSummary: Found {len(stale_tasks)} stale tasks out of {len(active_tasks)} total")
    
    # Save recommendations
    recommendations_file = Path("stale_task_recommendations.json")
    with open(recommendations_file, 'w') as f:
        json.dump({
            'analyzed_at': current_time.isoformat(),
            'total_active_pending': len(active_tasks),
            'stale_count': len(stale_tasks),
            'stale_tasks': stale_tasks,
            'recommendation': 'Archive or complete these tasks to clean up the system'
        }, f, indent=2)
    
    print(f"\nRecommendations saved to: {recommendations_file}")
    
    return stale_tasks

if __name__ == "__main__":
    print("MCP Task Orchestrator - Stale Task Analysis")
    print("=" * 80)
    print("Note: This script analyzes tasks without modifying the database.")
    print("      It's safe to run even when the orchestrator is active.\n")
    
    stale_tasks = analyze_stale_tasks()
    
    if stale_tasks:
        print("\n\nRecommended Actions:")
        print("-" * 80)
        print("Since the database is currently locked, you can:")
        print("1. Stop the orchestrator server temporarily to release the lock")
        print("2. Use the orchestrator's task completion tools to mark tasks as done")
        print("3. Wait for the current session to complete before running cleanup")