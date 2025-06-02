#!/usr/bin/env python3
"""
Simple Stale Task Cleanup using Orchestrator API

This script uses the task orchestrator's get_status function to identify and clean up stale tasks.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

def parse_timestamp(timestamp_str):
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
        print(f"⚠️ Failed to parse timestamp '{timestamp_str}': {e}")
        return None

def analyze_stale_tasks(tasks_data, dry_run=True):
    """Analyze tasks from the orchestrator status API"""
    
    # Define specialist thresholds (in hours)
    specialist_thresholds = {
        'researcher': 24,      # Research tasks should complete within 24 hours
        'architect': 48,       # Architecture tasks may take longer
        'implementer': 72,     # Implementation can be complex
        'documenter': 36,      # Documentation should be timely
        'tester': 24,          # Testing should be quick
        'reviewer': 12,        # Reviews should be fast
        'debugger': 6,         # Debugging should be immediate
        'default': 48          # Default threshold for unknown specialists
    }
    
    print("🔍 Analyzing Task Staleness")
    print("=" * 50)
    
    all_tasks = tasks_data.get('tasks', [])
    
    stale_tasks = []
    current_time = datetime.now()
    
    print(f"📊 Total tasks found: {len(all_tasks)}")
    print(f"📊 Active tasks: {tasks_data.get('active_tasks', 0)}")
    print(f"📊 Pending tasks: {tasks_data.get('pending_tasks', 0)}")
    print(f"📊 Completed tasks: {tasks_data.get('completed_tasks', 0)}")
    
    # Analyze each task
    for task in all_tasks:
        task_id = task.get('task_id', 'unknown')
        status = task.get('status', 'unknown')
        specialist_type = task.get('specialist_type', 'default')
        created_at = task.get('created_at')
        title = task.get('title', 'No title')
        
        if not created_at:
            continue
            
        created_time = parse_timestamp(created_at)
        if not created_time:
            continue
            
        age_hours = (current_time - created_time).total_seconds() / 3600
        threshold = specialist_thresholds.get(specialist_type, specialist_thresholds['default'])
        
        # Determine if task is stale
        stale_reasons = []
        
        if status == 'pending' and age_hours > (7 * 24):  # Pending for more than 7 days
            stale_reasons.append(f"pending for {age_hours:.1f} hours (>7 days)")
        elif status == 'active' and age_hours > threshold:
            stale_reasons.append(f"active for {age_hours:.1f} hours (>{threshold}h threshold)")
        elif status == 'pending' and age_hours > threshold:
            stale_reasons.append(f"pending for {age_hours:.1f} hours (>{threshold}h threshold)")
        
        if stale_reasons:
            stale_task = {
                'task_id': task_id,
                'title': title,
                'status': status,
                'specialist_type': specialist_type,
                'created_at': created_at,
                'age_hours': age_hours,
                'threshold_hours': threshold,
                'stale_reasons': stale_reasons
            }
            stale_tasks.append(stale_task)
    
    print(f"\n🕰️ Found {len(stale_tasks)} stale tasks")
    
    # Group by status and specialist
    stale_by_status = {}
    stale_by_specialist = {}
    
    for task in stale_tasks:
        status = task['status']
        specialist = task['specialist_type']
        
        stale_by_status[status] = stale_by_status.get(status, 0) + 1
        stale_by_specialist[specialist] = stale_by_specialist.get(specialist, 0) + 1
    
    print(f"📊 Stale tasks by status: {dict(stale_by_status)}")
    print(f"👥 Stale tasks by specialist: {dict(stale_by_specialist)}")
    
    # Display detailed stale task information
    if stale_tasks:
        print(f"\n📋 Detailed Stale Task Report:")
        print("=" * 80)
        
        for i, task in enumerate(stale_tasks, 1):
            print(f"\n{i}. Task ID: {task['task_id']}")
            print(f"   Title: {task['title']}")
            print(f"   Status: {task['status']}")
            print(f"   Specialist: {task['specialist_type']}")
            print(f"   Created: {task['created_at']}")
            print(f"   Age: {task['age_hours']:.1f} hours")
            print(f"   Threshold: {task['threshold_hours']} hours")
            print(f"   Reasons: {', '.join(task['stale_reasons'])}")
    
    # Create recommendations
    recommendations = []
    
    if stale_tasks:
        # Group recommendations by type
        long_pending = [t for t in stale_tasks if t['status'] == 'pending' and t['age_hours'] > 7*24]
        long_active = [t for t in stale_tasks if t['status'] == 'active' and t['age_hours'] > t['threshold_hours']]
        
        if long_pending:
            recommendations.append(f"Archive {len(long_pending)} long-pending tasks (>7 days old)")
        
        if long_active:
            recommendations.append(f"Review {len(long_active)} long-active tasks")
        
        # Specific specialist recommendations
        if 'debugger' in stale_by_specialist:
            recommendations.append(f"Prioritize {stale_by_specialist['debugger']} stale debugger tasks (should be fast)")
        
        if 'reviewer' in stale_by_specialist:
            recommendations.append(f"Complete {stale_by_specialist['reviewer']} stale reviewer tasks")
    
    # Create cleanup report
    report = {
        "analysis_timestamp": current_time.isoformat(),
        "summary": {
            "total_tasks": len(all_tasks),
            "stale_tasks": len(stale_tasks),
            "stale_by_status": stale_by_status,
            "stale_by_specialist": stale_by_specialist,
            "specialist_thresholds": specialist_thresholds
        },
        "stale_tasks": stale_tasks,
        "recommendations": recommendations
    }
    
    # Save report
    report_path = Path(__file__).parent / "stale_task_analysis_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Analysis report saved to: {report_path}")
    except Exception as e:
        print(f"⚠️ Failed to save analysis report: {e}")
    
    # Display recommendations
    if recommendations:
        print(f"\n💡 Cleanup Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print(f"\n✅ No cleanup recommendations - system looks healthy!")
    
    return stale_tasks, recommendations

def main():
    # This would normally get data from the orchestrator API
    # For now, we'll create a sample analysis
    print("📊 Simple Stale Task Analysis")
    print("=" * 50)
    print("Note: This script analyzes task staleness based on age and specialist thresholds")
    print("To get live data, this should be integrated with the orchestrator API")
    
    # Sample tasks data structure (would come from API)
    sample_tasks = {
        "active_tasks": 11,
        "pending_tasks": 18,
        "completed_tasks": 104,
        "tasks": []  # Would be populated from API
    }
    
    print("\n⚠️ This script needs to be integrated with live orchestrator data")
    print("Please run this script through the orchestrator's maintenance coordinator")
    
    return True

if __name__ == "__main__":
    main()