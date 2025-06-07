#!/usr/bin/env python3
"""
Enhanced Health Monitoring System
Advanced project health monitoring with trend analysis and automated alerts.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any

class HealthMonitor:
    """Enhanced health monitoring with trend analysis and automation."""
    
    def __init__(self, config_path: str = ".health_monitor_config.json"):
        self.config_path = config_path
        self.history_file = ".health_history.json"
        self.load_config()
        
    def load_config(self):
        """Load monitoring configuration."""
        default_config = {
            "thresholds": {
                "health_score_minimum": 95,
                "root_files_maximum": 15,
                "virtual_envs_maximum": 1,
                "warning_threshold": 85
            },
            "monitoring": {
                "enabled": True,
                "check_interval_hours": 24,
                "history_retention_days": 30
            },
            "alerts": {
                "email_enabled": False,
                "console_alerts": True,
                "log_alerts": True
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
        
        self.config = default_config
        
    def save_config(self):
        """Save current configuration."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current project health metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "root_files": len([f for f in os.listdir('.') if os.path.isfile(f)]),
            "documentation_files": len(list(Path("docs").glob("**/*.md"))),
            "script_files": len(list(Path("scripts").glob("**/*.py"))),
            "test_files": len(list(Path("tests").glob("**/*.py"))),
            "virtual_environments": len([d for d in os.listdir('.') if d.startswith('venv')]),
            "build_artifacts": self._count_build_artifacts(),
            "health_score": self._calculate_health_score()
        }
        
        return metrics
    
    def _count_build_artifacts(self) -> int:
        """Count build artifacts that should be cleaned."""
        artifacts = 0
        
        # Check for build directories
        for artifact_dir in ['build', 'dist']:
            if os.path.exists(artifact_dir):
                artifacts += 1
                
        # Check for egg-info directories
        for item in os.listdir('.'):
            if item.endswith('.egg-info') and os.path.isdir(item):
                artifacts += 1
                
        return artifacts
    
    def _calculate_health_score(self) -> int:
        """Calculate comprehensive health score."""
        score = 100
        
        # Root files penalty (target: ≤15)
        root_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
        if root_files > 15:
            score -= min(20, (root_files - 15) * 2)
            
        # Virtual environments penalty (target: 1)
        venvs = len([d for d in os.listdir('.') if d.startswith('venv')])
        if venvs > 1:
            score -= min(15, (venvs - 1) * 5)
            
        # Build artifacts penalty
        artifacts = self._count_build_artifacts()
        if artifacts > 0:
            score -= min(10, artifacts * 5)
            
        # Documentation organization bonus
        if os.path.exists("docs") and len(list(Path("docs").glob("**/*.md"))) > 50:
            score += 5  # Bonus for good documentation
            
        # Script organization bonus
        if (os.path.exists("scripts/build") and 
            os.path.exists("scripts/testing") and 
            os.path.exists("scripts/diagnostics")):
            score += 5  # Bonus for good script organization
            
        return max(0, min(100, score))
    
    def load_history(self) -> List[Dict]:
        """Load health monitoring history."""
        if not os.path.exists(self.history_file):
            return []
            
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            return []
    
    def save_history(self, history: List[Dict]):
        """Save health monitoring history."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def add_health_record(self, metrics: Dict[str, Any]):
        """Add new health record to history."""
        history = self.load_history()
        history.append(metrics)
        
        # Clean old records
        cutoff_date = datetime.now() - timedelta(days=self.config["monitoring"]["history_retention_days"])
        history = [
            record for record in history 
            if datetime.fromisoformat(record["timestamp"]) > cutoff_date
        ]
        
        self.save_history(history)
    
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze health trends over time."""
        history = self.load_history()
        if len(history) < 2:
            return {"trend_analysis": "Insufficient data for trend analysis"}
            
        latest = history[-1]
        previous = history[-2]
        
        trends = {}
        for key in ["health_score", "root_files", "virtual_environments", "build_artifacts"]:
            if key in latest and key in previous:
                change = latest[key] - previous[key]
                trends[f"{key}_trend"] = "improving" if change < 0 else "stable" if change == 0 else "degrading"
                trends[f"{key}_change"] = change
                
        return trends
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """Check metrics against configured thresholds."""
        alerts = []
        thresholds = self.config["thresholds"]
        
        if metrics["health_score"] < thresholds["health_score_minimum"]:
            alerts.append(f"CRITICAL: Health score {metrics['health_score']} below minimum {thresholds['health_score_minimum']}")
            
        if metrics["health_score"] < thresholds["warning_threshold"]:
            alerts.append(f"WARNING: Health score {metrics['health_score']} below warning threshold {thresholds['warning_threshold']}")
            
        if metrics["root_files"] > thresholds["root_files_maximum"]:
            alerts.append(f"WARNING: Root files {metrics['root_files']} exceeds maximum {thresholds['root_files_maximum']}")
            
        if metrics["virtual_environments"] > thresholds["virtual_envs_maximum"]:
            alerts.append(f"WARNING: Virtual environments {metrics['virtual_environments']} exceeds maximum {thresholds['virtual_envs_maximum']}")
            
        if metrics["build_artifacts"] > 0:
            alerts.append(f"NOTICE: Build artifacts present ({metrics['build_artifacts']} items)")
            
        return alerts
    
    def generate_report(self) -> str:
        """Generate comprehensive health report."""
        metrics = self.get_current_metrics()
        trends = self.analyze_trends()
        alerts = self.check_thresholds(metrics)
        
        report = []
        report.append("🏥 PROJECT HEALTH MONITORING REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Current metrics
        report.append("📊 CURRENT METRICS:")
        report.append(f"   Health Score: {metrics['health_score']}/100")
        report.append(f"   Root Files: {metrics['root_files']} (target: ≤15)")
        report.append(f"   Documentation Files: {metrics['documentation_files']}")
        report.append(f"   Script Files: {metrics['script_files']}")
        report.append(f"   Test Files: {metrics['test_files']}")
        report.append(f"   Virtual Environments: {metrics['virtual_environments']} (target: 1)")
        report.append(f"   Build Artifacts: {metrics['build_artifacts']} (target: 0)")
        report.append("")
        
        # Trend analysis
        if trends and "trend_analysis" not in trends:
            report.append("📈 TREND ANALYSIS:")
            for key, value in trends.items():
                if key.endswith("_trend"):
                    metric_name = key.replace("_trend", "").replace("_", " ").title()
                    change_key = key.replace("_trend", "_change")
                    change = trends.get(change_key, 0)
                    emoji = "✅" if value == "improving" else "⚠️" if value == "degrading" else "📊"
                    report.append(f"   {emoji} {metric_name}: {value} (change: {change:+d})")
            report.append("")
        
        # Alerts
        if alerts:
            report.append("🚨 ALERTS:")
            for alert in alerts:
                report.append(f"   {alert}")
            report.append("")
        else:
            report.append("✅ NO ALERTS: All metrics within acceptable ranges")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        if metrics["health_score"] >= 95:
            report.append("   🎯 Excellent! Maintain current organization standards")
        elif metrics["health_score"] >= 85:
            report.append("   📈 Good health score. Minor improvements recommended")
        else:
            report.append("   🔧 Health score needs attention. Review organization")
            
        if metrics["root_files"] > 15:
            report.append("   📁 Consider moving additional files to appropriate subdirectories")
            
        if metrics["build_artifacts"] > 0:
            report.append("   🧹 Clean build artifacts: rm -rf build/ dist/ *.egg-info/")
            
        return "\\n".join(report)
    
    def run_monitoring_check(self) -> bool:
        """Run complete monitoring check and return success status."""
        try:
            metrics = self.get_current_metrics()
            self.add_health_record(metrics)
            
            alerts = self.check_thresholds(metrics)
            
            if self.config["alerts"]["console_alerts"] and alerts:
                print("🚨 HEALTH MONITORING ALERTS:")
                for alert in alerts:
                    print(f"   {alert}")
                    
            return metrics["health_score"] >= self.config["thresholds"]["health_score_minimum"]
            
        except Exception as e:
            print(f"Error during monitoring check: {e}")
            return False

def main():
    """Main monitoring function."""
    monitor = HealthMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        print(monitor.generate_report())
    elif len(sys.argv) > 1 and sys.argv[1] == "--check":
        success = monitor.run_monitoring_check()
        sys.exit(0 if success else 1)
    else:
        # Default: generate report
        print(monitor.generate_report())

if __name__ == "__main__":
    main()