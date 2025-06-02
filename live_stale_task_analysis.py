#!/usr/bin/env python3
"""
Live Stale Task Analysis

Analyzes the live task data from the orchestrator and provides cleanup recommendations.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Live task data from orchestrator status (June 1, 2025)
LIVE_TASK_DATA = {
  "active_tasks": 11,
  "pending_tasks": 18,
  "completed_tasks": 104,
  "tasks": [
    {
      "task_id": "tester_836147",
      "title": "Integration Testing and Stale Task Cleanup Validation",
      "status": "active",
      "specialist_type": "tester",
      "created_at": "2025-06-01T17:52:05.666567"
    },
    {
      "task_id": "documenter_4576d1",
      "title": "Update Documentation and Tool Naming",
      "status": "pending",
      "specialist_type": "documenter",
      "created_at": "2025-06-01T17:52:05.666561"
    },
    {
      "task_id": "documenter_a3790a",
      "title": "Document Resilient File Operations System",
      "status": "pending",
      "specialist_type": "documenter",
      "created_at": "2025-06-01T17:24:27.219557"
    },
    {
      "task_id": "tester_a1cd46",
      "title": "Create Comprehensive Testing Suite",
      "status": "pending",
      "specialist_type": "tester",
      "created_at": "2025-06-01T17:24:27.219551"
    },
    {
      "task_id": "implementer_7fb268",
      "title": "Update Complete Subtask Implementation",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T17:24:27.219545"
    },
    {
      "task_id": "implementer_ddbec5",
      "title": "Add Resume Capability for Interrupted Writes",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T17:24:27.219539"
    },
    {
      "task_id": "architect_553b67",
      "title": "Release Strategy and Deployment Recommendations",
      "status": "pending",
      "specialist_type": "architect",
      "created_at": "2025-06-01T10:21:13.352959"
    },
    {
      "task_id": "implementer_3a3e34",
      "title": "Update Error Handling and User Feedback",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T09:27:12.806516"
    },
    {
      "task_id": "tester_cde7b0",
      "title": "Test and Validate the Fixed Artifact System",
      "status": "pending",
      "specialist_type": "tester",
      "created_at": "2025-06-01T09:27:12.806510"
    },
    {
      "task_id": "implementer_a86b37",
      "title": "Fix Path Resolution and Directory Creation Logic",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T09:27:12.806504"
    },
    {
      "task_id": "debugger_cf0ecc",
      "title": "Analyze Database Operations and Persistence Issues",
      "status": "pending",
      "specialist_type": "debugger",
      "created_at": "2025-06-01T09:27:12.806497"
    },
    {
      "task_id": "debugger_ebb70f",
      "title": "Trace Artifact Creation Process and Identify Failure Points",
      "status": "pending",
      "specialist_type": "debugger",
      "created_at": "2025-06-01T09:27:12.806488"
    },
    {
      "task_id": "implementer_5d4aea",
      "title": "Archive Processed Stale Tasks",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T08:23:13.797933"
    },
    {
      "task_id": "documenter_bb9bee",
      "title": "Update Template and Visual Assets Feature Planning",
      "status": "active",
      "specialist_type": "documenter",
      "created_at": "2025-06-01T08:23:13.797926"
    },
    {
      "task_id": "reviewer_1d0d7d",
      "title": "Visual Assets and Documentation Quality Review",
      "status": "active",
      "specialist_type": "reviewer",
      "created_at": "2025-06-01T05:49:22.539038"
    },
    {
      "task_id": "implementer_849522",
      "title": "Documentation Organization and Publishing (implementer_4ee506)",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T05:49:22.539032"
    },
    {
      "task_id": "tester_fda6a3",
      "title": "Testing Work Stream Coordination and Execution",
      "status": "active",
      "specialist_type": "tester",
      "created_at": "2025-06-01T05:49:22.539026"
    },
    {
      "task_id": "implementer_704e8f",
      "title": "Interactive Examples and Code Samples (implementer_e0fbc4)",
      "status": "pending",
      "specialist_type": "implementer",
      "created_at": "2025-06-01T05:49:22.539020"
    },
    {
      "task_id": "documenter_de327a",
      "title": "LLM-Optimized Reference Documentation (documenter_ffbc88)",
      "status": "pending",
      "specialist_type": "documenter",
      "created_at": "2025-06-01T05:49:22.539013"
    },
    {
      "task_id": "debugger_7694e7",
      "title": "Critical Debugging Task - Orchestrator Issue Resolution",
      "status": "pending",
      "specialist_type": "debugger",
      "created_at": "2025-06-01T05:49:22.538986"
    },
    {
      "task_id": "implementer_4ee506",
      "title": "Documentation Organization and Publishing",
      "status": "active",
      "specialist_type": "implementer",
      "created_at": "2025-05-30T09:07:58.557565"
    },
    {
      "task_id": "reviewer_398e44",
      "title": "Documentation Quality Review and Testing",
      "status": "active",
      "specialist_type": "reviewer",
      "created_at": "2025-05-30T09:07:58.557559"
    },
    {
      "task_id": "implementer_e0fbc4",
      "title": "Interactive Examples and Code Samples",
      "status": "active",
      "specialist_type": "implementer",
      "created_at": "2025-05-30T09:07:58.557553"
    },
    {
      "task_id": "implementer_ce7374",
      "title": "Visual Assets and Diagrams Creation",
      "status": "active",
      "specialist_type": "implementer",
      "created_at": "2025-05-30T09:07:58.557547"
    },
    {
      "task_id": "documenter_ffbc88",
      "title": "LLM-Optimized Reference Documentation",
      "status": "active",
      "specialist_type": "documenter",
      "created_at": "2025-05-30T09:07:58.557541"
    },
    {
      "task_id": "reviewer_74f538",
      "title": "Analyze Test Results",
      "status": "active",
      "specialist_type": "reviewer",
      "created_at": "2025-05-30T06:26:03.273508"
    },
    {
      "task_id": "tester_0519bf",
      "title": "Run All Tests",
      "status": "pending",
      "specialist_type": "tester",
      "created_at": "2025-05-30T06:26:03.273502"
    },
    {
      "task_id": "tester_aa7599",
      "title": "Run Migration Test",
      "status": "pending",
      "specialist_type": "tester",
      "created_at": "2025-05-30T06:26:03.273494"
    },
    {
      "task_id": "researcher_f77035",
      "title": "Examine Migration Test Structure",
      "status": "active",
      "specialist_type": "researcher",
      "created_at": "2025-05-30T06:26:03.273486"
    }
  ]
}

def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except Exception as e:
        print(f"⚠️ Failed to parse timestamp '{timestamp_str}': {e}")
        return None

def analyze_live_tasks():
    """Analyze the live task data for staleness"""
    
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
    
    print("🔍 Live Stale Task Analysis")
    print("=" * 50)
    print("Analysis Date: June 1, 2025")
    
    tasks = LIVE_TASK_DATA['tasks']
    current_time = datetime.now()
    
    print(f"📊 Total tasks analyzed: {len(tasks)}")
    print(f"📊 Active tasks: {LIVE_TASK_DATA['active_tasks']}")
    print(f"📊 Pending tasks: {LIVE_TASK_DATA['pending_tasks']}")
    print(f"📊 Completed tasks: {LIVE_TASK_DATA['completed_tasks']}")
    
    stale_tasks = []
    priority_stale = []
    
    # Analyze each task
    for task in tasks:
        if task['status'] in ['completed']:
            continue
            
        task_id = task['task_id']
        status = task['status']
        specialist_type = task['specialist_type']
        created_at = task['created_at']
        title = task['title']
        
        created_time = parse_timestamp(created_at)
        if not created_time:
            continue
            
        age_hours = (current_time - created_time).total_seconds() / 3600
        threshold = specialist_thresholds.get(specialist_type, specialist_thresholds['default'])
        
        # Determine if task is stale
        stale_reasons = []
        is_priority = False
        
        if status == 'pending' and age_hours > (7 * 24):  # Pending for more than 7 days
            stale_reasons.append(f"pending for {age_hours:.1f} hours (>7 days)")
            is_priority = True
        elif status == 'active' and age_hours > (3 * 24):  # Active for more than 3 days
            stale_reasons.append(f"active for {age_hours:.1f} hours (>3 days)")
            is_priority = True
        elif age_hours > threshold:
            stale_reasons.append(f"{status} for {age_hours:.1f} hours (>{threshold}h threshold)")
            
        # Special priority for debugger tasks
        if specialist_type == 'debugger' and age_hours > 6:
            is_priority = True
            if not stale_reasons:
                stale_reasons.append(f"debugger task pending for {age_hours:.1f} hours (>6h)")
        
        if stale_reasons:
            stale_task = {
                'task_id': task_id,
                'title': title,
                'status': status,
                'specialist_type': specialist_type,
                'created_at': created_at,
                'age_hours': age_hours,
                'threshold_hours': threshold,
                'stale_reasons': stale_reasons,
                'is_priority': is_priority
            }
            stale_tasks.append(stale_task)
            
            if is_priority:
                priority_stale.append(stale_task)
    
    print(f"\n🕰️ Found {len(stale_tasks)} stale tasks ({len(priority_stale)} high priority)")
    
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
    
    # Display priority stale tasks first
    if priority_stale:
        print(f"\n🚨 HIGH PRIORITY Stale Tasks ({len(priority_stale)} tasks):")
        print("=" * 80)
        
        for i, task in enumerate(priority_stale, 1):
            print(f"\n{i}. 🔥 Task ID: {task['task_id']}")
            print(f"   Title: {task['title']}")
            print(f"   Status: {task['status']}")
            print(f"   Specialist: {task['specialist_type']}")
            print(f"   Age: {task['age_hours']:.1f} hours ({task['age_hours']/24:.1f} days)")
            print(f"   Reasons: {', '.join(task['stale_reasons'])}")
    
    # Display all stale tasks
    if stale_tasks:
        print(f"\n📋 All Stale Tasks ({len(stale_tasks)} tasks):")
        print("=" * 80)
        
        for i, task in enumerate(stale_tasks, 1):
            priority_marker = "🔥 " if task['is_priority'] else "   "
            print(f"\n{i}. {priority_marker}Task ID: {task['task_id']}")
            print(f"   Title: {task['title']}")
            print(f"   Status: {task['status']}")
            print(f"   Specialist: {task['specialist_type']}")
            print(f"   Created: {task['created_at']}")
            print(f"   Age: {task['age_hours']:.1f} hours ({task['age_hours']/24:.1f} days)")
            print(f"   Reasons: {', '.join(task['stale_reasons'])}")
    
    # Create specific cleanup recommendations
    recommendations = []
    
    # Priority recommendations
    old_pending = [t for t in stale_tasks if t['status'] == 'pending' and t['age_hours'] > 7*24]
    old_active = [t for t in stale_tasks if t['status'] == 'active' and t['age_hours'] > 3*24]
    debugger_tasks = [t for t in stale_tasks if t['specialist_type'] == 'debugger']
    reviewer_tasks = [t for t in stale_tasks if t['specialist_type'] == 'reviewer']
    
    if old_pending:
        recommendations.append({
            "priority": "HIGH",
            "action": f"Archive {len(old_pending)} very old pending tasks (>7 days)",
            "task_ids": [t['task_id'] for t in old_pending]
        })
    
    if old_active:
        recommendations.append({
            "priority": "HIGH", 
            "action": f"Review and complete {len(old_active)} long-running active tasks (>3 days)",
            "task_ids": [t['task_id'] for t in old_active]
        })
    
    if debugger_tasks:
        recommendations.append({
            "priority": "CRITICAL",
            "action": f"Immediately address {len(debugger_tasks)} stale debugger tasks",
            "task_ids": [t['task_id'] for t in debugger_tasks]
        })
    
    if reviewer_tasks:
        recommendations.append({
            "priority": "MEDIUM",
            "action": f"Complete {len(reviewer_tasks)} stale reviewer tasks",
            "task_ids": [t['task_id'] for t in reviewer_tasks]
        })
    
    # Additional pattern-based recommendations
    duplicate_docs = []
    for task in stale_tasks:
        if 'Documentation' in task['title'] and task['status'] == 'pending':
            duplicate_docs.append(task)
    
    if len(duplicate_docs) > 1:
        recommendations.append({
            "priority": "MEDIUM",
            "action": f"Consolidate {len(duplicate_docs)} duplicate documentation tasks",
            "task_ids": [t['task_id'] for t in duplicate_docs]
        })
    
    # Create comprehensive report
    report = {
        "analysis_timestamp": current_time.isoformat(),
        "summary": {
            "total_tasks_analyzed": len(tasks),
            "stale_tasks_found": len(stale_tasks),
            "priority_stale_tasks": len(priority_stale),
            "stale_by_status": stale_by_status,
            "stale_by_specialist": stale_by_specialist,
            "specialist_thresholds": specialist_thresholds
        },
        "stale_tasks": stale_tasks,
        "priority_stale_tasks": priority_stale,
        "recommendations": recommendations
    }
    
    # Save detailed report
    report_path = Path(__file__).parent / "live_stale_task_analysis_report.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Detailed analysis report saved to: {report_path}")
    except Exception as e:
        print(f"⚠️ Failed to save analysis report: {e}")
    
    # Display recommendations
    if recommendations:
        print(f"\n💡 Cleanup Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {"CRITICAL": "🚨", "HIGH": "🔥", "MEDIUM": "⚠️", "LOW": "💡"}
            icon = priority_icon.get(rec['priority'], "📝")
            print(f"   {i}. {icon} [{rec['priority']}] {rec['action']}")
            print(f"      Task IDs: {', '.join(rec['task_ids'][:5])}{'...' if len(rec['task_ids']) > 5 else ''}")
    else:
        print(f"\n✅ No cleanup recommendations - system looks healthy!")
    
    return stale_tasks, recommendations, report

def create_cleanup_script(stale_tasks, recommendations):
    """Create executable cleanup commands"""
    
    cleanup_script = []
    cleanup_script.append("#!/bin/bash")
    cleanup_script.append("# Stale Task Cleanup Script")
    cleanup_script.append("# Generated on: " + datetime.now().isoformat())
    cleanup_script.append("")
    
    # Add manual steps for different categories
    old_pending = [t for t in stale_tasks if t['status'] == 'pending' and t['age_hours'] > 7*24]
    debugger_tasks = [t for t in stale_tasks if t['specialist_type'] == 'debugger']
    
    if old_pending:
        cleanup_script.append("# Step 1: Archive very old pending tasks (>7 days)")
        cleanup_script.append("echo 'Archiving very old pending tasks...'")
        for task in old_pending:
            cleanup_script.append(f"# Archive task: {task['task_id']} - {task['title']}")
        cleanup_script.append("")
    
    if debugger_tasks:
        cleanup_script.append("# Step 2: Prioritize debugger tasks")
        cleanup_script.append("echo 'Addressing critical debugger tasks...'")
        for task in debugger_tasks:
            cleanup_script.append(f"# Complete task: {task['task_id']} - {task['title']}")
        cleanup_script.append("")
    
    cleanup_script.append("echo 'Manual cleanup complete!'")
    
    # Save cleanup script
    script_path = Path(__file__).parent / "cleanup_commands.sh"
    try:
        with open(script_path, 'w') as f:
            f.write('\n'.join(cleanup_script))
        print(f"📜 Cleanup script saved to: {script_path}")
    except Exception as e:
        print(f"⚠️ Failed to save cleanup script: {e}")

def main():
    print("📊 Live Stale Task Analysis and Cleanup")
    print("=" * 60)
    
    stale_tasks, recommendations, report = analyze_live_tasks()
    
    # Create cleanup script
    create_cleanup_script(stale_tasks, recommendations)
    
    print(f"\n" + "=" * 60)
    print(f"✅ Analysis Complete!")
    print(f"   • {len(stale_tasks)} stale tasks identified")
    print(f"   • {len(recommendations)} cleanup recommendations")
    print(f"   • Reports and scripts generated")
    
    return True

if __name__ == "__main__":
    main()