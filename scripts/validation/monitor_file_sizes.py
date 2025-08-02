#!/usr/bin/env python3
"""
Monitor File Sizes for Documentation

This script monitors file sizes to flag files that exceed size limits,
particularly important for Claude Code which has file size constraints.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

@dataclass
class FileSizeInfo:
    file_path: str
    size_bytes: int
    size_lines: int
    size_mb: float
    last_modified: datetime
    content_hash: str
    is_oversized: bool = False
    warning_level: str = "none"  # none, warning, critical
    suggested_action: str = ""

@dataclass
class FileSizeReport:
    scan_time: datetime
    total_files: int
    oversized_files: int
    warning_files: int
    critical_files: int
    largest_file: Optional[FileSizeInfo] = None
    files: List[FileSizeInfo] = field(default_factory=list)
    size_distribution: Dict[str, int] = field(default_factory=dict)
    trends: Dict[str, any] = field(default_factory=dict)

class FileSizeMonitor:
    """Monitors file sizes and identifies size-related issues."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.size_limits = self.config['size_limits']
        self.warning_thresholds = self.config['warning_thresholds']
        self.file_patterns = self.config['file_patterns']
        self.exclusions = self.config['exclusions']
        self.history_file = self.config.get('history_file', '.file_size_history.json')
        self.history = self._load_history()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load monitor configuration."""
        default_config = {
            'size_limits': {
                'critical_mb': 2.0,      # Claude Code crashes above 2MB
                'warning_mb': 1.0,       # Warning at 1MB
                'critical_lines': 500,   # Claude Code issues above 500 lines
                'warning_lines': 300,    # Warning at 300 lines
                'recommended_lines': 200 # Recommended max
            },
            'warning_thresholds': {
                'growth_rate': 0.5,      # 50% growth triggers warning
                'size_increase_mb': 0.1   # 100KB increase triggers warning
            },
            'file_patterns': {
                'documentation': ['*.md', '*.rst', '*.txt'],
                'code': ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c'],
                'config': ['*.json', '*.yaml', '*.yml', '*.xml'],
                'all': ['*.md', '*.py', '*.json', '*.yaml', '*.yml', '*.txt', '*.rst']
            },
            'exclusions': [
                '*/node_modules/*',
                '*/.git/*',
                '*/venv/*',
                '*/env/*',
                '*/__pycache__/*',
                '*.pyc',
                '*/build/*',
                '*/dist/*',
                '*/.pytest_cache/*'
            ],
            'history_file': '.file_size_history.json'
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_history(self) -> Dict:
        """Load historical size data."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_history(self):
        """Save historical size data."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from monitoring."""
        file_str = str(file_path)
        for pattern in self.exclusions:
            if self._matches_pattern(file_str, pattern):
                return True
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file matches exclusion pattern."""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate content hash for change detection."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _count_lines(self, file_path: str) -> int:
        """Count lines in a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _get_file_info(self, file_path: Path) -> FileSizeInfo:
        """Get comprehensive file size information."""
        stat = file_path.stat()
        size_bytes = stat.st_size
        size_mb = size_bytes / (1024 * 1024)
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        
        # Count lines for text files
        size_lines = 0
        if file_path.suffix.lower() in ['.md', '.py', '.txt', '.rst', '.json', '.yaml', '.yml']:
            size_lines = self._count_lines(str(file_path))
        
        # Calculate content hash
        content_hash = self._calculate_file_hash(str(file_path))
        
        # Determine warning level
        warning_level = "none"
        is_oversized = False
        suggested_action = ""
        
        # Check size limits
        if size_mb >= self.size_limits['critical_mb']:
            warning_level = "critical"
            is_oversized = True
            suggested_action = "CRITICAL: File exceeds 2MB - may crash Claude Code. Break into smaller files immediately."
        elif size_lines >= self.size_limits['critical_lines']:
            warning_level = "critical" 
            is_oversized = True
            suggested_action = f"CRITICAL: File exceeds {self.size_limits['critical_lines']} lines - may cause Claude Code issues. Refactor immediately."
        elif size_mb >= self.size_limits['warning_mb']:
            warning_level = "warning"
            suggested_action = "WARNING: File approaching size limit. Consider breaking into modules."
        elif size_lines >= self.size_limits['warning_lines']:
            warning_level = "warning"
            suggested_action = f"WARNING: File exceeds {self.size_limits['warning_lines']} lines. Consider refactoring."
        elif size_lines >= self.size_limits['recommended_lines']:
            warning_level = "info"
            suggested_action = f"INFO: File exceeds recommended {self.size_limits['recommended_lines']} lines. Consider optimization."
        
        return FileSizeInfo(
            file_path=str(file_path),
            size_bytes=size_bytes,
            size_lines=size_lines,
            size_mb=size_mb,
            last_modified=last_modified,
            content_hash=content_hash,
            is_oversized=is_oversized,
            warning_level=warning_level,
            suggested_action=suggested_action
        )
    
    def scan_directory(self, directory_path: str, pattern_type: str = "all") -> FileSizeReport:
        """Scan directory for file size issues."""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        scan_time = datetime.now()
        files = []
        patterns = self.file_patterns.get(pattern_type, self.file_patterns['all'])
        
        # Scan all matching files
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file() and not self._should_exclude(file_path):
                    file_info = self._get_file_info(file_path)
                    files.append(file_info)
        
        # Generate report
        report = FileSizeReport(
            scan_time=scan_time,
            total_files=len(files),
            oversized_files=sum(1 for f in files if f.is_oversized),
            warning_files=sum(1 for f in files if f.warning_level == "warning"),
            critical_files=sum(1 for f in files if f.warning_level == "critical"),
            files=files
        )
        
        # Find largest file
        if files:
            report.largest_file = max(files, key=lambda f: f.size_bytes)
        
        # Calculate size distribution
        report.size_distribution = self._calculate_size_distribution(files)
        
        # Calculate trends if history exists
        report.trends = self._calculate_trends(files)
        
        # Update history
        self._update_history(files, scan_time)
        
        return report
    
    def _calculate_size_distribution(self, files: List[FileSizeInfo]) -> Dict[str, int]:
        """Calculate size distribution statistics."""
        distribution = {
            'tiny': 0,      # < 10KB
            'small': 0,     # 10KB - 100KB
            'medium': 0,    # 100KB - 500KB
            'large': 0,     # 500KB - 1MB
            'xlarge': 0,    # 1MB - 2MB
            'oversized': 0  # > 2MB
        }
        
        for file_info in files:
            size_kb = file_info.size_bytes / 1024
            
            if size_kb < 10:
                distribution['tiny'] += 1
            elif size_kb < 100:
                distribution['small'] += 1
            elif size_kb < 500:
                distribution['medium'] += 1
            elif size_kb < 1024:
                distribution['large'] += 1
            elif size_kb < 2048:
                distribution['xlarge'] += 1
            else:
                distribution['oversized'] += 1
        
        return distribution
    
    def _calculate_trends(self, files: List[FileSizeInfo]) -> Dict:
        """Calculate size trends from historical data."""
        trends = {
            'growing_files': [],
            'shrinking_files': [],
            'new_files': [],
            'modified_files': [],
            'largest_growth': None,
            'largest_shrinkage': None
        }
        
        if not self.history:
            return trends
        
        # Get latest historical scan
        latest_scan = None
        if self.history:
            latest_scan_key = max(self.history.keys())
            latest_scan = self.history[latest_scan_key]
        
        if not latest_scan:
            return trends
        
        # Compare current files with historical data
        historical_files = {f['file_path']: f for f in latest_scan}
        
        for file_info in files:
            file_path = file_info.file_path
            
            if file_path in historical_files:
                old_size = historical_files[file_path]['size_bytes']
                new_size = file_info.size_bytes
                size_change = new_size - old_size
                
                # Check for significant changes
                if abs(size_change) > self.warning_thresholds['size_increase_mb'] * 1024 * 1024:
                    if size_change > 0:
                        trends['growing_files'].append({
                            'file_path': file_path,
                            'old_size': old_size,
                            'new_size': new_size,
                            'growth': size_change
                        })
                    else:
                        trends['shrinking_files'].append({
                            'file_path': file_path,
                            'old_size': old_size,
                            'new_size': new_size,
                            'shrinkage': abs(size_change)
                        })
                
                # Check for content changes
                old_hash = historical_files[file_path].get('content_hash', '')
                if old_hash and old_hash != file_info.content_hash:
                    trends['modified_files'].append(file_path)
            else:
                trends['new_files'].append(file_path)
        
        # Find largest changes
        if trends['growing_files']:
            trends['largest_growth'] = max(trends['growing_files'], key=lambda x: x['growth'])
        if trends['shrinking_files']:
            trends['largest_shrinkage'] = max(trends['shrinking_files'], key=lambda x: x['shrinkage'])
        
        return trends
    
    def _update_history(self, files: List[FileSizeInfo], scan_time: datetime):
        """Update historical size tracking."""
        scan_key = scan_time.isoformat()
        
        # Convert FileSizeInfo objects to dict for JSON serialization
        file_data = []
        for file_info in files:
            file_data.append({
                'file_path': file_info.file_path,
                'size_bytes': file_info.size_bytes,
                'size_lines': file_info.size_lines,
                'size_mb': file_info.size_mb,
                'last_modified': file_info.last_modified.isoformat(),
                'content_hash': file_info.content_hash,
                'warning_level': file_info.warning_level
            })
        
        self.history[scan_key] = file_data
        
        # Keep only last 10 scans to limit history size
        if len(self.history) > 10:
            old_keys = sorted(self.history.keys())[:-10]
            for key in old_keys:
                del self.history[key]
        
        self._save_history()
    
    def get_size_recommendations(self, files: List[FileSizeInfo]) -> List[Dict]:
        """Generate specific recommendations for oversized files."""
        recommendations = []
        
        # Sort by size to prioritize largest files
        sorted_files = sorted(files, key=lambda f: f.size_bytes, reverse=True)
        
        for file_info in sorted_files:
            if file_info.is_oversized or file_info.warning_level in ['warning', 'critical']:
                rec = {
                    'file_path': file_info.file_path,
                    'current_size': f"{file_info.size_mb:.2f} MB ({file_info.size_lines} lines)",
                    'warning_level': file_info.warning_level,
                    'immediate_action': file_info.suggested_action,
                    'detailed_recommendations': []
                }
                
                # Add specific recommendations based on file type
                file_ext = Path(file_info.file_path).suffix.lower()
                
                if file_ext == '.md':
                    rec['detailed_recommendations'].extend([
                        "Break into multiple topic-focused files",
                        "Move detailed examples to separate files",
                        "Use @includes for shared content",
                        "Extract large code blocks to separate files",
                        "Create index file with links to sections"
                    ])
                elif file_ext == '.py':
                    rec['detailed_recommendations'].extend([
                        "Split into multiple modules",
                        "Extract classes to separate files", 
                        "Move utility functions to utils module",
                        "Break large functions into smaller ones",
                        "Consider using composition over inheritance"
                    ])
                elif file_ext in ['.json', '.yaml', '.yml']:
                    rec['detailed_recommendations'].extend([
                        "Split configuration into multiple files",
                        "Use references/includes for shared sections",
                        "Move environment-specific configs to separate files",
                        "Extract large data arrays to separate files"
                    ])
                
                # Add file-size specific recommendations
                if file_info.size_lines > 1000:
                    rec['detailed_recommendations'].append("URGENT: File is extremely large - prioritize immediate refactoring")
                elif file_info.size_lines > 500:
                    rec['detailed_recommendations'].append("HIGH PRIORITY: File exceeds Claude Code comfort zone")
                elif file_info.size_lines > 300:
                    rec['detailed_recommendations'].append("MEDIUM PRIORITY: Consider refactoring for better maintainability")
                
                recommendations.append(rec)
        
        return recommendations
    
    def generate_monitoring_script(self, output_path: str):
        """Generate a monitoring script for continuous size tracking."""
        script_content = f'''#!/usr/bin/env python3
"""
Automated File Size Monitoring Script
Generated by FileSizeMonitor on {datetime.now().isoformat()}
"""

import sys
import json
from pathlib import Path

# Add the validation script directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitor_file_sizes import FileSizeMonitor

def main():
    """Run file size monitoring."""
    monitor = FileSizeMonitor()
    
    # Monitor current directory
    report = monitor.scan_directory(".", "all")
    
    # Print summary
    print(f"File Size Monitoring Report - {{report.scan_time}}")
    print(f"Total files: {{report.total_files}}")
    print(f"Critical files: {{report.critical_files}}")
    print(f"Warning files: {{report.warning_files}}")
    print(f"Oversized files: {{report.oversized_files}}")
    
    # Alert on critical files
    if report.critical_files > 0:
        print("\\nCRITICAL SIZE ALERTS:")
        critical_files = [f for f in report.files if f.warning_level == "critical"]
        for file_info in critical_files:
            print(f"  {{file_info.file_path}}: {{file_info.size_mb:.2f}}MB ({{file_info.size_lines}} lines)")
            print(f"    {{file_info.suggested_action}}")
        
        return 1  # Exit with error code
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(output_path, 0o755)

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor file sizes for documentation and code')
    parser.add_argument('path', help='Directory path to monitor')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text', 'summary'], default='text', help='Output format')
    parser.add_argument('--pattern', choices=['documentation', 'code', 'config', 'all'], 
                       default='all', help='File pattern to monitor')
    parser.add_argument('--threshold', choices=['critical', 'warning', 'info'], 
                       help='Minimum threshold to report')
    parser.add_argument('--recommendations', action='store_true', 
                       help='Include detailed recommendations')
    parser.add_argument('--generate-monitor', help='Generate monitoring script at specified path')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    monitor = FileSizeMonitor(args.config)
    
    # Generate monitoring script if requested
    if args.generate_monitor:
        monitor.generate_monitoring_script(args.generate_monitor)
        print(f"Generated monitoring script at: {args.generate_monitor}")
        return 0
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run scan
    try:
        report = monitor.scan_directory(str(path), args.pattern)
    except Exception as e:
        print(f"Error scanning directory: {e}")
        return 1
    
    # Apply threshold filter
    if args.threshold:
        threshold_map = {'info': ['info', 'warning', 'critical'], 
                        'warning': ['warning', 'critical'], 
                        'critical': ['critical']}
        allowed_levels = threshold_map[args.threshold]
        report.files = [f for f in report.files if f.warning_level in allowed_levels]
        
        # Recalculate counts
        report.oversized_files = sum(1 for f in report.files if f.is_oversized)
        report.warning_files = sum(1 for f in report.files if f.warning_level == "warning")
        report.critical_files = sum(1 for f in report.files if f.warning_level == "critical")
    
    # Generate recommendations if requested
    recommendations = []
    if args.recommendations:
        recommendations = monitor.get_size_recommendations(report.files)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'report': {
                'scan_time': report.scan_time.isoformat(),
                'total_files': report.total_files,
                'oversized_files': report.oversized_files,
                'warning_files': report.warning_files,
                'critical_files': report.critical_files,
                'largest_file': {
                    'file_path': report.largest_file.file_path,
                    'size_mb': report.largest_file.size_mb,
                    'size_lines': report.largest_file.size_lines
                } if report.largest_file else None,
                'size_distribution': report.size_distribution,
                'trends': report.trends
            },
            'files': [
                {
                    'file_path': f.file_path,
                    'size_bytes': f.size_bytes,
                    'size_lines': f.size_lines,
                    'size_mb': f.size_mb,
                    'last_modified': f.last_modified.isoformat(),
                    'is_oversized': f.is_oversized,
                    'warning_level': f.warning_level,
                    'suggested_action': f.suggested_action
                } for f in report.files
            ],
            'recommendations': recommendations
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
        else:
            print(json.dumps(output_data, indent=2))
    
    elif args.format == 'summary':
        # Summary format
        print(f"File Size Monitoring Summary - {report.scan_time}")
        print("=" * 50)
        print(f"Total Files: {report.total_files}")
        print(f"Critical Files: {report.critical_files}")
        print(f"Warning Files: {report.warning_files}")
        print(f"Oversized Files: {report.oversized_files}")
        
        if report.largest_file:
            print(f"Largest File: {report.largest_file.file_path} ({report.largest_file.size_mb:.2f} MB)")
        
        if report.critical_files > 0:
            print("\\n⚠️  CRITICAL SIZE ALERTS:")
            critical_files = [f for f in report.files if f.warning_level == "critical"]
            for file_info in critical_files[:5]:  # Show top 5
                print(f"   {file_info.file_path}: {file_info.size_mb:.2f}MB ({file_info.size_lines} lines)")
    
    else:
        # Text format
        if not args.quiet:
            print("File Size Monitoring Report")
            print("=" * 50)
            print(f"Scan Time: {report.scan_time}")
            print(f"Total Files: {report.total_files}")
            print(f"Critical Files: {report.critical_files}")
            print(f"Warning Files: {report.warning_files}")
            print(f"Oversized Files: {report.oversized_files}")
            print()
            
            # Size distribution
            print("Size Distribution:")
            print("-" * 20)
            for category, count in report.size_distribution.items():
                print(f"  {category.capitalize()}: {count}")
            print()
            
            # Critical and warning files
            problem_files = [f for f in report.files if f.warning_level in ['critical', 'warning']]
            if problem_files:
                print("Files Requiring Attention:")
                print("-" * 30)
                for file_info in problem_files:
                    print(f"\\n{file_info.file_path}:")
                    print(f"  Size: {file_info.size_mb:.2f} MB ({file_info.size_lines} lines)")
                    print(f"  Level: {file_info.warning_level.upper()}")
                    print(f"  Action: {file_info.suggested_action}")
            
            # Trends
            if report.trends.get('growing_files'):
                print("\\nGrowing Files:")
                print("-" * 15)
                for growth in report.trends['growing_files'][:3]:
                    change_mb = growth['growth'] / (1024 * 1024)
                    print(f"  {growth['file_path']}: +{change_mb:.2f} MB")
            
            # Recommendations
            if recommendations:
                print("\\nDetailed Recommendations:")
                print("-" * 25)
                for rec in recommendations[:3]:  # Show top 3
                    print(f"\\n{rec['file_path']}:")
                    print(f"  Current Size: {rec['current_size']}")
                    print(f"  Priority: {rec['warning_level'].upper()}")
                    print(f"  Actions:")
                    for action in rec['detailed_recommendations'][:3]:
                        print(f"    • {action}")
        
        # Save text report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(f"File Size Monitoring Report - {report.scan_time}\\n")
                f.write(f"Total: {report.total_files}, Critical: {report.critical_files}, Warning: {report.warning_files}\\n\\n")
                
                for file_info in report.files:
                    if file_info.warning_level in ['critical', 'warning']:
                        f.write(f"File: {file_info.file_path}\\n")
                        f.write(f"Size: {file_info.size_mb:.2f} MB ({file_info.size_lines} lines)\\n")
                        f.write(f"Level: {file_info.warning_level}\\n")
                        f.write(f"Action: {file_info.suggested_action}\\n\\n")
    
    # Return appropriate exit code
    if report.critical_files > 0:
        return 1
    elif report.warning_files > 0 and args.threshold == 'warning':
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())