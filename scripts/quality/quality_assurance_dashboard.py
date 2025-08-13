#!/usr/bin/env python3
"""
Documentation Quality Assurance Dashboard
Part of Phase 6: Quality Assurance and Integration Testing

This dashboard provides comprehensive metrics, visual reports, and ongoing monitoring
capabilities for documentation health across the entire project.
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import subprocess

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class QualityMetrics:
    """Quality metrics for documentation"""
    timestamp: str
    health_score: float
    total_files: int
    passed_files: int
    failed_files: int
    warnings_count: int
    coverage_percentage: float
    trend_direction: str  # 'improving', 'stable', 'declining'

@dataclass
class FileQualityRecord:
    """Quality record for individual files"""
    file_path: str
    last_checked: str
    health_score: float
    issues_count: int
    warnings_count: int
    last_modified: str
    file_size: int
    check_history: List[Dict]

class QualityAssuranceDashboard:
    """Comprehensive quality assurance dashboard for documentation"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.db_path = self.project_root / '.quality_dashboard.db'
        self.setup_logging()
        self.setup_database()
        
        # Configuration
        self.config = {
            'dashboard_update_interval': 3600,  # 1 hour
            'history_retention_days': 90,
            'alert_thresholds': {
                'health_score_critical': 50.0,
                'health_score_warning': 70.0,
                'files_failing_threshold': 10,
                'trend_decline_threshold': -5.0
            },
            'report_templates': {
                'html': True,
                'json': True,
                'markdown': True
            }
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.project_root / 'quality_dashboard.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for quality metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create quality metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    health_score REAL NOT NULL,
                    total_files INTEGER NOT NULL,
                    passed_files INTEGER NOT NULL,
                    failed_files INTEGER NOT NULL,
                    warnings_count INTEGER NOT NULL,
                    coverage_percentage REAL NOT NULL,
                    trend_direction TEXT,
                    raw_data TEXT
                )
            ''')
            
            # Create file quality table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    health_score REAL NOT NULL,
                    issues_count INTEGER NOT NULL,
                    warnings_count INTEGER NOT NULL,
                    file_size INTEGER NOT NULL,
                    last_modified TEXT NOT NULL,
                    check_data TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON quality_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path ON file_quality(file_path)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_timestamp ON file_quality(timestamp)')
            
            conn.commit()
    
    def run_comprehensive_validation(self) -> Dict:
        """Run comprehensive validation and return results"""
        self.logger.info("Running comprehensive validation for dashboard...")
        
        validator_script = self.project_root / 'scripts' / 'quality' / 'comprehensive_documentation_validator.py'
        
        if not validator_script.exists():
            self.logger.error("Comprehensive validator not found")
            return {}
        
        try:
            # Run validator and capture output
            result = subprocess.run([
                sys.executable, str(validator_script),
                '--project-root', str(self.project_root),
                '--output', str(self.project_root / 'temp_validation_report.json'),
                '--quiet'
            ], capture_output=True, text=True, timeout=300)
            
            # Read the generated report
            report_file = self.project_root / 'temp_validation_report.json'
            if report_file.exists():
                with open(report_file, 'r') as f:
                    validation_data = json.load(f)
                
                # Clean up temporary file
                report_file.unlink()
                return validation_data
            else:
                self.logger.warning("Validation report not generated")
                return {}
                
        except subprocess.TimeoutExpired:
            self.logger.error("Validation timed out")
            return {}
        except Exception as e:
            self.logger.error(f"Error running validation: {str(e)}")
            return {}
    
    def store_quality_metrics(self, validation_data: Dict):
        """Store quality metrics in database"""
        if not validation_data:
            return
        
        health_metrics = validation_data.get('health_metrics', {})
        
        # Calculate trend direction
        trend_direction = self.calculate_trend_direction(health_metrics.get('health_score', 0))
        
        metrics = QualityMetrics(
            timestamp=datetime.now().isoformat(),
            health_score=health_metrics.get('health_score', 0),
            total_files=health_metrics.get('total_files', 0),
            passed_files=health_metrics.get('passed_files', 0),
            failed_files=health_metrics.get('failed_files', 0),
            warnings_count=health_metrics.get('warnings_count', 0),
            coverage_percentage=health_metrics.get('coverage_percentage', 0),
            trend_direction=trend_direction
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quality_metrics 
                (timestamp, health_score, total_files, passed_files, failed_files, 
                 warnings_count, coverage_percentage, trend_direction, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp, metrics.health_score, metrics.total_files,
                metrics.passed_files, metrics.failed_files, metrics.warnings_count,
                metrics.coverage_percentage, metrics.trend_direction,
                json.dumps(validation_data)
            ))
            conn.commit()
        
        # Store individual file metrics
        self.store_file_quality_metrics(validation_data.get('validation_results', []))
    
    def store_file_quality_metrics(self, validation_results: List[Dict]):
        """Store individual file quality metrics"""
        file_metrics = defaultdict(lambda: {'issues': 0, 'warnings': 0, 'checks': []})
        
        # Aggregate results per file
        for result in validation_results:
            file_path = result.get('file_path', '')
            if file_path and file_path != '<project-structure>':
                file_metrics[file_path]['issues'] += len(result.get('issues', []))
                file_metrics[file_path]['warnings'] += len(result.get('warnings', []))
                file_metrics[file_path]['checks'].append(result)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            
            for file_path, metrics in file_metrics.items():
                full_path = self.project_root / file_path
                
                # Get file info
                file_size = 0
                last_modified = timestamp
                if full_path.exists():
                    stat = full_path.stat()
                    file_size = stat.st_size
                    last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Calculate file health score
                total_issues = metrics['issues'] + metrics['warnings']
                health_score = max(0, 100 - (total_issues * 10))  # Reduce score by 10 per issue
                
                cursor.execute('''
                    INSERT INTO file_quality
                    (file_path, timestamp, health_score, issues_count, warnings_count,
                     file_size, last_modified, check_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_path, timestamp, health_score, metrics['issues'],
                    metrics['warnings'], file_size, last_modified,
                    json.dumps(metrics['checks'])
                ))
            
            conn.commit()
    
    def calculate_trend_direction(self, current_score: float) -> str:
        """Calculate trend direction based on recent history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT health_score FROM quality_metrics
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 5
            ''')
            recent_scores = [row[0] for row in cursor.fetchall()]
        
        if len(recent_scores) < 2:
            return 'stable'
        
        # Calculate average trend
        recent_avg = sum(recent_scores[:3]) / min(3, len(recent_scores))
        older_avg = sum(recent_scores[-2:]) / min(2, len(recent_scores[-2:]))
        
        diff = recent_avg - older_avg
        
        if diff > self.config['alert_thresholds']['trend_decline_threshold']:
            return 'improving'
        elif diff < -self.config['alert_thresholds']['trend_decline_threshold']:
            return 'declining'
        else:
            return 'stable'
    
    def get_current_metrics(self) -> Optional[QualityMetrics]:
        """Get the most recent quality metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM quality_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()
            
            if row:
                return QualityMetrics(
                    timestamp=row[1],
                    health_score=row[2],
                    total_files=row[3],
                    passed_files=row[4],
                    failed_files=row[5],
                    warnings_count=row[6],
                    coverage_percentage=row[7],
                    trend_direction=row[8] or 'stable'
                )
            return None
    
    def get_historical_metrics(self, days: int = 30) -> List[QualityMetrics]:
        """Get historical quality metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT * FROM quality_metrics
                WHERE timestamp > ?
                ORDER BY timestamp ASC
            ''', (cutoff,))
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append(QualityMetrics(
                    timestamp=row[1],
                    health_score=row[2],
                    total_files=row[3],
                    passed_files=row[4],
                    failed_files=row[5],
                    warnings_count=row[6],
                    coverage_percentage=row[7],
                    trend_direction=row[8] or 'stable'
                ))
            return metrics
    
    def get_file_quality_history(self, file_path: str, days: int = 30) -> List[FileQualityRecord]:
        """Get quality history for a specific file"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('''
                SELECT * FROM file_quality
                WHERE file_path = ? AND timestamp > ?
                ORDER BY timestamp ASC
            ''', (file_path, cutoff))
            
            records = []
            for row in cursor.fetchall():
                check_data = json.loads(row[8]) if row[8] else []
                records.append(FileQualityRecord(
                    file_path=row[1],
                    last_checked=row[2],
                    health_score=row[3],
                    issues_count=row[4],
                    warnings_count=row[5],
                    last_modified=row[7],
                    file_size=row[6],
                    check_history=check_data
                ))
            return records
    
    def generate_alerts(self) -> List[Dict]:
        """Generate alerts based on quality thresholds"""
        alerts = []
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return alerts
        
        # Health score alerts
        if current_metrics.health_score <= self.config['alert_thresholds']['health_score_critical']:
            alerts.append({
                'level': 'critical',
                'type': 'health_score',
                'message': f"Documentation health score is critical: {current_metrics.health_score:.1f}%",
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })
        elif current_metrics.health_score <= self.config['alert_thresholds']['health_score_warning']:
            alerts.append({
                'level': 'warning',
                'type': 'health_score',
                'message': f"Documentation health score needs attention: {current_metrics.health_score:.1f}%",
                'timestamp': datetime.now().isoformat(),
                'action_required': False
            })
        
        # Failed files alerts
        if current_metrics.failed_files >= self.config['alert_thresholds']['files_failing_threshold']:
            alerts.append({
                'level': 'warning',
                'type': 'failed_files',
                'message': f"High number of files failing validation: {current_metrics.failed_files}",
                'timestamp': datetime.now().isoformat(),
                'action_required': True
            })
        
        # Trend alerts
        if current_metrics.trend_direction == 'declining':
            alerts.append({
                'level': 'warning',
                'type': 'trend',
                'message': "Documentation quality is declining over time",
                'timestamp': datetime.now().isoformat(),
                'action_required': False
            })
        
        return alerts
    
    def generate_html_report(self, output_file: str = None) -> str:
        """Generate HTML quality dashboard report"""
        if not output_file:
            output_file = self.project_root / 'quality_dashboard_report.html'
        
        current_metrics = self.get_current_metrics()
        historical_metrics = self.get_historical_metrics()
        alerts = self.generate_alerts()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Quality Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ color: #666; }}
        .health-excellent {{ color: #28a745; }}
        .health-good {{ color: #ffc107; }}
        .health-poor {{ color: #dc3545; }}
        .alerts {{ margin-bottom: 30px; }}
        .alert {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
        .alert-critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
        .alert-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
        .trend-improving {{ color: #28a745; }}
        .trend-stable {{ color: #6c757d; }}
        .trend-declining {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Documentation Quality Dashboard</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
        
        if current_metrics:
            health_class = 'health-excellent' if current_metrics.health_score >= 90 else \
                          'health-good' if current_metrics.health_score >= 70 else 'health-poor'
            
            html_content += f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value {health_class}">{current_metrics.health_score:.1f}%</div>
                <div class="metric-label">Health Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{current_metrics.total_files}</div>
                <div class="metric-label">Total Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{current_metrics.passed_files}</div>
                <div class="metric-label">Passed Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{current_metrics.failed_files}</div>
                <div class="metric-label">Failed Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{current_metrics.warnings_count}</div>
                <div class="metric-label">Warnings</div>
            </div>
            <div class="metric-card">
                <div class="metric-value trend-{current_metrics.trend_direction}">{current_metrics.trend_direction.title()}</div>
                <div class="metric-label">Trend</div>
            </div>
        </div>
"""
        
        # Add alerts section
        if alerts:
            html_content += """
        <div class="alerts">
            <h2>Alerts</h2>
"""
            for alert in alerts:
                alert_class = f"alert-{alert['level']}"
                html_content += f"""
            <div class="alert {alert_class}">
                <strong>{alert['level'].upper()}:</strong> {alert['message']}
            </div>
"""
            html_content += "</div>"
        
        # Add historical data table
        if historical_metrics:
            html_content += """
        <div class="history">
            <h2>Recent History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Health Score</th>
                        <th>Total Files</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Warnings</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>
"""
            for metrics in historical_metrics[-10:]:  # Last 10 entries
                date = datetime.fromisoformat(metrics.timestamp).strftime('%Y-%m-%d %H:%M')
                html_content += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{metrics.health_score:.1f}%</td>
                        <td>{metrics.total_files}</td>
                        <td>{metrics.passed_files}</td>
                        <td>{metrics.failed_files}</td>
                        <td>{metrics.warnings_count}</td>
                        <td class="trend-{metrics.trend_direction}">{metrics.trend_direction}</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report generated: {output_file}")
        return str(output_file)
    
    def generate_markdown_summary(self, output_file: str = None) -> str:
        """Generate markdown summary report"""
        if not output_file:
            output_file = self.project_root / 'quality_summary.md'
        
        current_metrics = self.get_current_metrics()
        alerts = self.generate_alerts()
        
        content = f"""# Documentation Quality Summary

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Status
"""
        
        if current_metrics:
            status_emoji = "✅" if current_metrics.health_score >= 90 else \
                          "⚠️" if current_metrics.health_score >= 70 else "❌"
            
            content += f"""
{status_emoji} **Health Score:** {current_metrics.health_score:.1f}%
📊 **Total Files:** {current_metrics.total_files}
✅ **Passed Files:** {current_metrics.passed_files}
❌ **Failed Files:** {current_metrics.failed_files}
⚠️ **Warnings:** {current_metrics.warnings_count}
📈 **Trend:** {current_metrics.trend_direction.title()}

### Coverage
- **Pass Rate:** {(current_metrics.passed_files / current_metrics.total_files * 100):.1f}%
- **Coverage:** {current_metrics.coverage_percentage:.1f}%
"""
        
        if alerts:
            content += "\n## Active Alerts\n"
            for alert in alerts:
                emoji = "🚨" if alert['level'] == 'critical' else "⚠️"
                content += f"\n{emoji} **{alert['type'].replace('_', ' ').title()}:** {alert['message']}"
        
        content += """

## Recommendations

Based on the current metrics, here are the recommended actions:

"""
        
        if current_metrics:
            if current_metrics.health_score < 70:
                content += "- **Priority:** Address failing files immediately\n"
                content += "- Run comprehensive validation to identify specific issues\n"
                content += "- Consider updating documentation templates\n"
            elif current_metrics.failed_files > 0:
                content += "- Review and fix failing files\n"
                content += "- Update outdated documentation\n"
            
            if current_metrics.warnings_count > 10:
                content += "- Address high warning count to prevent future issues\n"
            
            if current_metrics.trend_direction == 'declining':
                content += "- **Urgent:** Quality is declining - investigate recent changes\n"
                content += "- Implement stricter validation in CI/CD\n"
        
        content += """
## Next Steps

1. Run `python scripts/quality/comprehensive_documentation_validator.py` for detailed analysis
2. Review failed files and address specific issues
3. Update documentation following current templates
4. Schedule regular quality reviews

---
*This report is automatically generated by the Documentation Quality Assurance Dashboard*
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        self.logger.info(f"Markdown summary generated: {output_file}")
        return str(output_file)
    
    def update_dashboard(self) -> Dict:
        """Update dashboard with latest validation data"""
        self.logger.info("Updating quality assurance dashboard...")
        
        # Run comprehensive validation
        validation_data = self.run_comprehensive_validation()
        
        if validation_data:
            # Store metrics
            self.store_quality_metrics(validation_data)
            
            # Generate reports
            html_report = self.generate_html_report()
            markdown_summary = self.generate_markdown_summary()
            
            # Clean up old data
            self.cleanup_old_data()
            
            return {
                'success': True,
                'html_report': html_report,
                'markdown_summary': markdown_summary,
                'metrics': validation_data.get('health_metrics', {}),
                'alerts': self.generate_alerts()
            }
        else:
            return {
                'success': False,
                'error': 'Failed to run validation'
            }
    
    def cleanup_old_data(self):
        """Clean up old data based on retention settings"""
        cutoff = (datetime.now() - timedelta(days=self.config['history_retention_days'])).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM quality_metrics WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM file_quality WHERE timestamp < ?', (cutoff,))
            conn.commit()
    
    def get_dashboard_status(self) -> Dict:
        """Get current dashboard status"""
        current_metrics = self.get_current_metrics()
        alerts = self.generate_alerts()
        
        return {
            'last_updated': current_metrics.timestamp if current_metrics else None,
            'health_score': current_metrics.health_score if current_metrics else None,
            'active_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
            'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0,
            'monitoring_active': True
        }


def main():
    """Main entry point for the quality assurance dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Quality Assurance Dashboard')
    parser.add_argument('--update', '-u', action='store_true', help='Update dashboard with latest data')
    parser.add_argument('--status', '-s', action='store_true', help='Show dashboard status')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--markdown', '-m', action='store_true', help='Generate markdown summary')
    parser.add_argument('--alerts', '-a', action='store_true', help='Show active alerts')
    parser.add_argument('--history', '-h', type=int, default=7, help='Show history for N days')
    parser.add_argument('--project-root', '-p', help='Project root directory')
    parser.add_argument('--output-dir', '-o', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = QualityAssuranceDashboard(args.project_root)
    
    if args.update:
        # Update dashboard with latest data
        result = dashboard.update_dashboard()
        if result['success']:
            print("✅ Dashboard updated successfully")
            print(f"HTML Report: {result['html_report']}")
            print(f"Markdown Summary: {result['markdown_summary']}")
            
            metrics = result['metrics']
            if metrics:
                print(f"Health Score: {metrics.get('health_score', 0):.1f}%")
        else:
            print(f"❌ Dashboard update failed: {result.get('error', 'Unknown error')}")
    
    elif args.status:
        # Show dashboard status
        status = dashboard.get_dashboard_status()
        print("Dashboard Status:")
        print(f"Last Updated: {status['last_updated']}")
        print(f"Health Score: {status['health_score']:.1f}%" if status['health_score'] else "No data")
        print(f"Active Alerts: {status['active_alerts']}")
        print(f"Critical Alerts: {status['critical_alerts']}")
        print(f"Database Size: {status['database_size']} bytes")
    
    elif args.alerts:
        # Show active alerts
        alerts = dashboard.generate_alerts()
        if alerts:
            print("Active Alerts:")
            for alert in alerts:
                emoji = "🚨" if alert['level'] == 'critical' else "⚠️"
                print(f"{emoji} {alert['message']}")
        else:
            print("✅ No active alerts")
    
    elif args.html:
        # Generate HTML report
        output_file = None
        if args.output_dir:
            output_file = Path(args.output_dir) / 'quality_dashboard.html'
        report_path = dashboard.generate_html_report(output_file)
        print(f"HTML report generated: {report_path}")
    
    elif args.markdown:
        # Generate markdown summary
        output_file = None
        if args.output_dir:
            output_file = Path(args.output_dir) / 'quality_summary.md'
        summary_path = dashboard.generate_markdown_summary(output_file)
        print(f"Markdown summary generated: {summary_path}")
    
    else:
        # Show current metrics
        current_metrics = dashboard.get_current_metrics()
        if current_metrics:
            print("Current Quality Metrics:")
            print(f"Health Score: {current_metrics.health_score:.1f}%")
            print(f"Total Files: {current_metrics.total_files}")
            print(f"Passed Files: {current_metrics.passed_files}")
            print(f"Failed Files: {current_metrics.failed_files}")
            print(f"Warnings: {current_metrics.warnings_count}")
            print(f"Trend: {current_metrics.trend_direction}")
        else:
            print("No metrics available. Run --update to collect data.")


if __name__ == "__main__":
    sys.exit(main())