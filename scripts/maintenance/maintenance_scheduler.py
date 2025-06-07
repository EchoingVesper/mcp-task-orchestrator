#!/usr/bin/env python3
"""
Project Maintenance Scheduler
Automated scheduling and execution of maintenance tasks.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class MaintenanceScheduler:
    """Automated maintenance task scheduler."""
    
    def __init__(self):
        self.schedule_file = ".maintenance_schedule.json"
        self.last_run_file = ".last_maintenance_run.json"
        self.load_schedule()
        
    def load_schedule(self):
        """Load maintenance schedule configuration."""
        default_schedule = {
            "tasks": {
                "health_check": {
                    "script": "scripts/diagnostics/health_monitor.py",
                    "frequency_hours": 24,
                    "enabled": True,
                    "description": "Monitor project health metrics"
                },
                "automated_cleanup": {
                    "script": "scripts/maintenance/automated_cleanup.py",
                    "frequency_hours": 168,  # Weekly
                    "enabled": True,
                    "description": "Clean build artifacts and cache files"
                },
                "structure_validation": {
                    "script": "scripts/diagnostics/check-project-structure.py",
                    "frequency_hours": 72,  # Every 3 days
                    "enabled": True,
                    "description": "Validate project organization structure"
                },
                "script_verification": {
                    "script": "scripts/testing/verify_script_reorganization.py",
                    "frequency_hours": 168,  # Weekly
                    "enabled": True,
                    "description": "Verify script organization integrity"
                },
                "documentation_verification": {
                    "script": "docs/development/documentation_reorganization_verification.py",
                    "frequency_hours": 168,  # Weekly
                    "enabled": True,
                    "description": "Verify documentation organization"
                }
            },
            "notifications": {
                "console_output": True,
                "log_to_file": True,
                "log_file": "maintenance.log"
            },
            "thresholds": {
                "health_score_alert": 85,
                "consecutive_failures_alert": 3
            }
        }
        
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r') as f:
                    user_schedule = json.load(f)
                    # Merge with defaults
                    for category in default_schedule:
                        if category in user_schedule:
                            if isinstance(default_schedule[category], dict):
                                default_schedule[category].update(user_schedule[category])
                            else:
                                default_schedule[category] = user_schedule[category]
            except Exception as e:
                print(f"Warning: Could not load schedule: {e}")
        
        self.schedule = default_schedule
        
    def save_schedule(self):
        """Save current schedule configuration."""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(self.schedule, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save schedule: {e}")
    
    def load_last_run_data(self) -> Dict:
        """Load last run timestamps."""
        if not os.path.exists(self.last_run_file):
            return {}
            
        try:
            with open(self.last_run_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load last run data: {e}")
            return {}
    
    def save_last_run_data(self, data: Dict):
        """Save last run timestamps."""
        try:
            with open(self.last_run_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save last run data: {e}")
    
    def is_task_due(self, task_name: str, task_config: Dict) -> bool:
        """Check if a maintenance task is due to run."""
        if not task_config.get("enabled", True):
            return False
            
        last_run_data = self.load_last_run_data()
        last_run_str = last_run_data.get(task_name)
        
        if not last_run_str:
            return True  # Never run before
            
        try:
            last_run = datetime.fromisoformat(last_run_str)
            frequency_hours = task_config.get("frequency_hours", 24)
            next_run = last_run + timedelta(hours=frequency_hours)
            return datetime.now() >= next_run
        except Exception:
            return True  # Error parsing, assume due
    
    def run_task(self, task_name: str, task_config: Dict) -> Dict[str, Any]:
        """Run a maintenance task."""
        script_path = task_config["script"]
        result = {
            "task_name": task_name,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "error": ""
        }
        
        try:
            if not os.path.exists(script_path):
                result["error"] = f"Script not found: {script_path}"
                return result
            
            # Run the script
            process = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result["success"] = process.returncode == 0
            result["output"] = process.stdout
            result["error"] = process.stderr
            result["return_code"] = process.returncode
            
        except subprocess.TimeoutExpired:
            result["error"] = "Task timed out after 5 minutes"
        except Exception as e:
            result["error"] = str(e)
        
        result["end_time"] = datetime.now().isoformat()
        return result
    
    def log_result(self, result: Dict[str, Any]):
        """Log task execution result."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        
        log_entry = f"[{timestamp}] {status}: {result['task_name']}"
        
        if self.schedule["notifications"]["console_output"]:
            print(log_entry)
            if result["error"]:
                print(f"   Error: {result['error']}")
        
        if self.schedule["notifications"]["log_to_file"]:
            log_file = self.schedule["notifications"]["log_file"]
            try:
                with open(log_file, 'a') as f:
                    f.write(log_entry + "\\n")
                    if result["error"]:
                        f.write(f"   Error: {result['error']}\\n")
            except Exception as e:
                print(f"Warning: Could not write to log file: {e}")
    
    def run_due_tasks(self) -> List[Dict[str, Any]]:
        """Run all due maintenance tasks."""
        results = []
        last_run_data = self.load_last_run_data()
        
        for task_name, task_config in self.schedule["tasks"].items():
            if self.is_task_due(task_name, task_config):
                print(f"🔧 Running maintenance task: {task_name}")
                result = self.run_task(task_name, task_config)
                results.append(result)
                self.log_result(result)
                
                # Update last run time if successful
                if result["success"]:
                    last_run_data[task_name] = result["start_time"]
        
        # Save updated last run data
        self.save_last_run_data(last_run_data)
        return results
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get status of all maintenance tasks."""
        last_run_data = self.load_last_run_data()
        status = {}
        
        for task_name, task_config in self.schedule["tasks"].items():
            last_run_str = last_run_data.get(task_name)
            last_run = None
            next_run = None
            
            if last_run_str:
                try:
                    last_run = datetime.fromisoformat(last_run_str)
                    frequency_hours = task_config.get("frequency_hours", 24)
                    next_run = last_run + timedelta(hours=frequency_hours)
                except Exception:
                    pass
            
            status[task_name] = {
                "enabled": task_config.get("enabled", True),
                "description": task_config.get("description", ""),
                "frequency_hours": task_config.get("frequency_hours", 24),
                "last_run": last_run.isoformat() if last_run else "Never",
                "next_run": next_run.isoformat() if next_run else "Now",
                "is_due": self.is_task_due(task_name, task_config)
            }
        
        return status
    
    def generate_status_report(self) -> str:
        """Generate maintenance status report."""
        status = self.get_task_status()
        
        report = []
        report.append("📅 MAINTENANCE SCHEDULE STATUS")
        report.append("=" * 40)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for task_name, task_status in status.items():
            emoji = "✅" if not task_status["is_due"] else "⏰"
            status_text = "Due Now" if task_status["is_due"] else "Up to Date"
            
            report.append(f"{emoji} {task_name.replace('_', ' ').title()}")
            report.append(f"   Description: {task_status['description']}")
            report.append(f"   Status: {status_text}")
            report.append(f"   Last Run: {task_status['last_run']}")
            report.append(f"   Next Run: {task_status['next_run']}")
            report.append(f"   Frequency: Every {task_status['frequency_hours']} hours")
            report.append("")
        
        return "\\n".join(report)

def main():
    """Main scheduler function."""
    scheduler = MaintenanceScheduler()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            print(scheduler.generate_status_report())
        elif command == "run":
            print("🔧 Running due maintenance tasks...")
            results = scheduler.run_due_tasks()
            if not results:
                print("✅ No maintenance tasks due at this time")
            else:
                success_count = sum(1 for r in results if r["success"])
                print(f"\\n📊 Maintenance Summary: {success_count}/{len(results)} tasks succeeded")
        elif command == "force":
            print("🔧 Force running all maintenance tasks...")
            # Temporarily mark all tasks as due
            for task_name in scheduler.schedule["tasks"]:
                result = scheduler.run_task(task_name, scheduler.schedule["tasks"][task_name])
                scheduler.log_result(result)
        else:
            print("Usage: maintenance_scheduler.py [status|run|force]")
            print("  status - Show maintenance schedule status")
            print("  run    - Run due maintenance tasks")
            print("  force  - Force run all maintenance tasks")
    else:
        # Default: show status
        print(scheduler.generate_status_report())

if __name__ == "__main__":
    main()