#!/usr/bin/env python3

"""
Temporary File Lifecycle Manager
Part of MCP Task Orchestrator Documentation Ecosystem Modernization

Purpose: Specialized management of temporary files and transient artifacts
Integration: Works with orchestrator and enforces Japanese cleanliness principles
"""

import os
import sys
import json
import logging
import datetime
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from enum import Enum
import argparse
import fnmatch
import stat

# Configuration
SCRIPT_NAME = "temporary_file_lifecycle"
SCRIPT_VERSION = "1.0.0"

class TempFileType(Enum):
    """Types of temporary files we manage"""
    EDITOR_BACKUP = "editor_backup"      # ~, .swp, .tmp files
    SYSTEM_TEMP = "system_temp"          # .tmp, .temp files
    BUILD_ARTIFACT = "build_artifact"    # Temporary build outputs
    DOWNLOAD_TEMP = "download_temp"      # Partial downloads, .part files
    MERGE_CONFLICT = "merge_conflict"    # .orig, .rej files from merges
    CACHE_FILE = "cache_file"            # Various cache files
    LOG_TEMP = "log_temp"                # Temporary log files
    UNKNOWN_TEMP = "unknown_temp"        # Other temporary patterns

@dataclass
class TempFileInfo:
    """Information about a temporary file"""
    path: Path
    temp_type: TempFileType
    size_bytes: int
    created_time: datetime.datetime
    modified_time: datetime.datetime
    accessed_time: datetime.datetime
    is_locked: bool = False
    process_name: Optional[str] = None
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH
    
class TemporaryFileLifecycleManager:
    """Manager for temporary file lifecycle operations"""
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.orchestrator_dir = project_root / ".task_orchestrator"
        
        # Set up logging
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='[%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(SCRIPT_NAME)
        
        # Temporary file patterns by type
        self.temp_patterns = {
            TempFileType.EDITOR_BACKUP: [
                "*~", ".*~", ".*.swp", ".*.swo", "#*#", ".#*"
            ],
            TempFileType.SYSTEM_TEMP: [
                "*.tmp", "*.temp", "*.TMP", "*.TEMP", "tmp_*", "temp_*"
            ],
            TempFileType.BUILD_ARTIFACT: [
                "*.pyc", "*.pyo", "__pycache__", ".DS_Store", "Thumbs.db",
                "*.o", "*.obj", "*.exe", "*.dll"
            ],
            TempFileType.DOWNLOAD_TEMP: [
                "*.part", "*.partial", "*.crdownload", "*.tmp.download"
            ],
            TempFileType.MERGE_CONFLICT: [
                "*.orig", "*.rej", "*.bak", "*.backup"
            ],
            TempFileType.CACHE_FILE: [
                ".cache", "*.cache", "cache_*", "*_cache", ".pytest_cache"
            ],
            TempFileType.LOG_TEMP: [
                "*.log.tmp", "*.debug.tmp", "log_*", "*_log_*"
            ]
        }
        
        # Age thresholds (in hours)
        self.age_thresholds = {
            TempFileType.EDITOR_BACKUP: 1,      # Very short - likely orphaned
            TempFileType.SYSTEM_TEMP: 24,       # 1 day
            TempFileType.BUILD_ARTIFACT: 72,    # 3 days (might be reused)
            TempFileType.DOWNLOAD_TEMP: 2,      # 2 hours (likely failed)
            TempFileType.MERGE_CONFLICT: 168,   # 1 week (user might need)
            TempFileType.CACHE_FILE: 168,       # 1 week
            TempFileType.LOG_TEMP: 48,          # 2 days
            TempFileType.UNKNOWN_TEMP: 24       # Conservative for unknown
        }
        
        # Directories to skip during scanning
        self.skip_dirs = {
            ".git", "node_modules", "venv", "__pycache__", "build", "dist",
            ".pytest_cache", ".mypy_cache", ".tox", ".coverage",
            "target", "bin", "obj", ".gradle"
        }
        
    def discover_temp_files(self) -> List[TempFileInfo]:
        """Discover all temporary files in the project"""
        self.logger.info("Discovering temporary files in project")
        temp_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Filter out directories we should skip
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Classify temporary file
                temp_type = self._classify_temp_file(file_path)
                if temp_type is None:
                    continue
                
                try:
                    file_stat = file_path.stat()
                    
                    # Check if file is locked (in use)
                    is_locked = self._is_file_locked(file_path)
                    process_name = self._get_locking_process(file_path) if is_locked else None
                    
                    temp_info = TempFileInfo(
                        path=file_path,
                        temp_type=temp_type,
                        size_bytes=file_stat.st_size,
                        created_time=datetime.datetime.fromtimestamp(file_stat.st_ctime),
                        modified_time=datetime.datetime.fromtimestamp(file_stat.st_mtime),
                        accessed_time=datetime.datetime.fromtimestamp(file_stat.st_atime),
                        is_locked=is_locked,
                        process_name=process_name,
                        risk_level=self._assess_risk_level(file_path, temp_type, file_stat)
                    )
                    
                    temp_files.append(temp_info)
                    
                except (OSError, IOError) as e:
                    self.logger.warning(f"Could not process {file_path}: {e}")
                    continue
        
        self.logger.info(f"Discovered {len(temp_files)} temporary files")
        return temp_files
    
    def _classify_temp_file(self, file_path: Path) -> Optional[TempFileType]:
        """Classify a file as a specific type of temporary file"""
        filename = file_path.name
        
        # Check against known patterns
        for temp_type, patterns in self.temp_patterns.items():
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(str(file_path), f"*/{pattern}"):
                    return temp_type
        
        # Additional heuristics
        if filename.startswith('.') and ('tmp' in filename.lower() or 'temp' in filename.lower()):
            return TempFileType.SYSTEM_TEMP
        
        # Check if it's in a temp directory
        path_str = str(file_path).lower()
        if any(temp_word in path_str for temp_word in ['tmp', 'temp', 'cache']):
            return TempFileType.UNKNOWN_TEMP
        
        return None
    
    def _is_file_locked(self, file_path: Path) -> bool:
        """Check if a file is currently locked/in use"""
        try:
            # Try to open the file in write mode
            with open(file_path, 'r+b'):
                return False
        except (IOError, PermissionError):
            return True
        except IsADirectoryError:
            return False
    
    def _get_locking_process(self, file_path: Path) -> Optional[str]:
        """Get the name of the process locking a file (Linux/Unix only)"""
        try:
            # Use lsof to find processes using the file
            import subprocess
            result = subprocess.run(
                ['lsof', str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                if lines:
                    # Extract process name from first line
                    parts = lines[0].split()
                    if len(parts) > 0:
                        return parts[0]
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return None
    
    def _assess_risk_level(self, file_path: Path, temp_type: TempFileType, file_stat: os.stat_result) -> str:
        """Assess the risk level of removing this temporary file"""
        # Start with low risk
        risk = "LOW"
        
        # Check if file was recently accessed (higher risk)
        hours_since_access = (datetime.datetime.now() - datetime.datetime.fromtimestamp(file_stat.st_atime)).total_seconds() / 3600
        if hours_since_access < 1:
            risk = "MEDIUM"
        
        # Large files are higher risk
        if file_stat.st_size > 100 * 1024 * 1024:  # 100MB
            risk = "MEDIUM"
        
        # Files in critical directories
        path_str = str(file_path)
        if any(critical in path_str for critical in ['/etc/', '/usr/', '/bin/', '/sbin/']):
            risk = "HIGH"
        
        # Editor backup files in recently modified directories are higher risk
        if temp_type == TempFileType.EDITOR_BACKUP:
            parent_dir = file_path.parent
            try:
                parent_stat = parent_dir.stat()
                hours_since_parent_modified = (datetime.datetime.now() - datetime.datetime.fromtimestamp(parent_stat.st_mtime)).total_seconds() / 3600
                if hours_since_parent_modified < 2:
                    risk = "MEDIUM"
            except OSError:
                pass
        
        return risk
    
    def analyze_temp_files(self, temp_files: List[TempFileInfo]) -> Dict[str, Any]:
        """Analyze temporary files and generate cleanup recommendations"""
        self.logger.info("Analyzing temporary files")
        
        analysis = {
            "total_temp_files": len(temp_files),
            "by_type": {},
            "by_risk_level": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
            "cleanup_candidates": [],
            "locked_files": [],
            "large_files": [],
            "old_files": [],
            "total_size_bytes": 0,
            "potential_cleanup_bytes": 0,
            "safety_analysis": {
                "safe_to_clean": 0,
                "needs_review": 0,
                "do_not_clean": 0
            }
        }
        
        # Initialize type counters
        for temp_type in TempFileType:
            analysis["by_type"][temp_type.value] = {
                "count": 0,
                "total_size": 0,
                "avg_age_hours": 0,
                "oldest_file": None,
                "largest_file": None
            }
        
        now = datetime.datetime.now()
        
        for temp_file in temp_files:
            type_key = temp_file.temp_type.value
            
            # Update type statistics
            analysis["by_type"][type_key]["count"] += 1
            analysis["by_type"][type_key]["total_size"] += temp_file.size_bytes
            analysis["total_size_bytes"] += temp_file.size_bytes
            
            # Update risk level counters
            analysis["by_risk_level"][temp_file.risk_level] += 1
            
            # Calculate age in hours
            age_hours = (now - temp_file.modified_time).total_seconds() / 3600
            
            # Update oldest file tracking
            if (analysis["by_type"][type_key]["oldest_file"] is None or 
                age_hours > analysis["by_type"][type_key]["oldest_file"]["age_hours"]):
                analysis["by_type"][type_key]["oldest_file"] = {
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "age_hours": age_hours
                }
            
            # Update largest file tracking
            if (analysis["by_type"][type_key]["largest_file"] is None or
                temp_file.size_bytes > analysis["by_type"][type_key]["largest_file"]["size_bytes"]):
                analysis["by_type"][type_key]["largest_file"] = {
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "size_bytes": temp_file.size_bytes
                }
            
            # Check if file is a cleanup candidate
            threshold_hours = self.age_thresholds.get(temp_file.temp_type, 24)
            is_cleanup_candidate = (
                age_hours > threshold_hours and
                not temp_file.is_locked and
                temp_file.risk_level in ["LOW", "MEDIUM"]
            )
            
            if is_cleanup_candidate:
                analysis["cleanup_candidates"].append({
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "type": type_key,
                    "size_bytes": temp_file.size_bytes,
                    "age_hours": age_hours,
                    "risk_level": temp_file.risk_level,
                    "reason": f"Older than {threshold_hours}h threshold"
                })
                analysis["potential_cleanup_bytes"] += temp_file.size_bytes
                
                # Safety analysis
                if temp_file.risk_level == "LOW":
                    analysis["safety_analysis"]["safe_to_clean"] += 1
                else:
                    analysis["safety_analysis"]["needs_review"] += 1
            else:
                if temp_file.is_locked:
                    analysis["locked_files"].append({
                        "path": str(temp_file.path.relative_to(self.project_root)),
                        "process": temp_file.process_name,
                        "type": type_key
                    })
                
                if temp_file.risk_level == "HIGH":
                    analysis["safety_analysis"]["do_not_clean"] += 1
                elif age_hours <= threshold_hours:
                    analysis["safety_analysis"]["needs_review"] += 1
            
            # Track large files (>10MB)
            if temp_file.size_bytes > 10 * 1024 * 1024:
                analysis["large_files"].append({
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "size_bytes": temp_file.size_bytes,
                    "type": type_key
                })
            
            # Track old files (>7 days)
            if age_hours > 168:  # 7 days
                analysis["old_files"].append({
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "age_hours": age_hours,
                    "type": type_key
                })
        
        # Calculate average ages
        for type_key, type_info in analysis["by_type"].items():
            if type_info["count"] > 0:
                # Calculate average age from all files of this type
                total_age_hours = sum(
                    (now - tf.modified_time).total_seconds() / 3600
                    for tf in temp_files if tf.temp_type.value == type_key
                )
                type_info["avg_age_hours"] = total_age_hours / type_info["count"]
        
        return analysis
    
    def perform_cleanup(self, temp_files: List[TempFileInfo]) -> Dict[str, Any]:
        """Perform automated cleanup of temporary files"""
        self.logger.info(f"Performing temporary file cleanup ({'DRY RUN' if self.dry_run else 'LIVE'})")
        
        cleanup_results = {
            "processed": 0,
            "cleaned": 0,
            "skipped": 0,
            "errors": 0,
            "bytes_freed": 0,
            "actions": []
        }
        
        now = datetime.datetime.now()
        
        for temp_file in temp_files:
            cleanup_results["processed"] += 1
            
            # Skip locked files
            if temp_file.is_locked:
                cleanup_results["skipped"] += 1
                cleanup_results["actions"].append({
                    "type": "skipped",
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "reason": f"File locked by {temp_file.process_name or 'unknown process'}"
                })
                continue
            
            # Skip high-risk files
            if temp_file.risk_level == "HIGH":
                cleanup_results["skipped"] += 1
                cleanup_results["actions"].append({
                    "type": "skipped",
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "reason": "High risk file - manual review required"
                })
                continue
            
            # Check age threshold
            age_hours = (now - temp_file.modified_time).total_seconds() / 3600
            threshold_hours = self.age_thresholds.get(temp_file.temp_type, 24)
            
            if age_hours <= threshold_hours:
                cleanup_results["skipped"] += 1
                cleanup_results["actions"].append({
                    "type": "skipped",
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "reason": f"Too recent ({age_hours:.1f}h < {threshold_hours}h threshold)"
                })
                continue
            
            # Perform cleanup
            try:
                rel_path = str(temp_file.path.relative_to(self.project_root))
                self.logger.info(f"Cleaning up temp file: {rel_path}")
                
                if not self.dry_run:
                    temp_file.path.unlink()
                
                cleanup_results["cleaned"] += 1
                cleanup_results["bytes_freed"] += temp_file.size_bytes
                cleanup_results["actions"].append({
                    "type": "cleaned",
                    "path": rel_path,
                    "temp_type": temp_file.temp_type.value,
                    "size_bytes": temp_file.size_bytes,
                    "age_hours": age_hours,
                    "dry_run": self.dry_run
                })
                
            except Exception as e:
                self.logger.error(f"Failed to clean {temp_file.path}: {e}")
                cleanup_results["errors"] += 1
                cleanup_results["actions"].append({
                    "type": "error",
                    "path": str(temp_file.path.relative_to(self.project_root)),
                    "error": str(e)
                })
        
        return cleanup_results
    
    def generate_report(self, analysis: Dict[str, Any], cleanup_results: Dict[str, Any]) -> str:
        """Generate comprehensive temporary file lifecycle report"""
        timestamp = datetime.datetime.now().isoformat()
        
        report = {
            "script": SCRIPT_NAME,
            "version": SCRIPT_VERSION,
            "timestamp": timestamp,
            "project_root": str(self.project_root),
            "dry_run": self.dry_run,
            "analysis": analysis,
            "cleanup_results": cleanup_results,
            "thresholds": {
                temp_type.value: hours
                for temp_type, hours in self.age_thresholds.items()
            },
            "patterns": {
                temp_type.value: patterns
                for temp_type, patterns in self.temp_patterns.items()
            }
        }
        
        # Create report file
        report_dir = self.project_root / "tmp"
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"temp_file_lifecycle_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Report generated: {report_file}")
        return str(report_file)
    
    def integrate_with_orchestrator(self, report_file: str, analysis: Dict[str, Any]) -> None:
        """Integrate with orchestrator system"""
        self.logger.debug("Integrating with orchestrator system")
        
        if not self.orchestrator_dir.exists():
            self.logger.debug("No orchestrator session found")
            return
        
        # Create orchestrator update
        orchestrator_update = {
            "temp_file_lifecycle": {
                "script_name": SCRIPT_NAME,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "completed",
                "total_temp_files": analysis["total_temp_files"],
                "cleanup_candidates": len(analysis["cleanup_candidates"]),
                "locked_files": len(analysis["locked_files"]),
                "total_size_bytes": analysis["total_size_bytes"],
                "potential_cleanup_bytes": analysis["potential_cleanup_bytes"],
                "safety_summary": analysis["safety_analysis"],
                "report_file": report_file,
                "dry_run": self.dry_run
            }
        }
        
        # Store update for orchestrator
        status_file = self.orchestrator_dir / "temp_file_lifecycle_status.json"
        with open(status_file, 'w') as f:
            json.dump(orchestrator_update, f, indent=2)
        
        self.logger.debug(f"Orchestrator update saved: {status_file}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage temporary file lifecycle and cleanup"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without making changes"
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report without performing cleanup"
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Use more aggressive cleanup thresholds"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize manager
        manager = TemporaryFileLifecycleManager(args.project_root, args.dry_run)
        
        # Adjust thresholds if aggressive mode
        if args.aggressive:
            for temp_type in manager.age_thresholds:
                manager.age_thresholds[temp_type] = max(1, manager.age_thresholds[temp_type] // 2)
            logging.info("Aggressive mode: using shorter age thresholds")
        
        # Discover and analyze temporary files
        temp_files = manager.discover_temp_files()
        analysis = manager.analyze_temp_files(temp_files)
        
        # Perform cleanup if not report-only
        if args.report_only:
            cleanup_results = {
                "processed": 0,
                "cleaned": 0,
                "skipped": 0,
                "errors": 0,
                "bytes_freed": 0,
                "actions": []
            }
            logging.info("Report-only mode: skipping cleanup operations")
        else:
            cleanup_results = manager.perform_cleanup(temp_files)
        
        # Generate report and integrate with orchestrator
        report_file = manager.generate_report(analysis, cleanup_results)
        manager.integrate_with_orchestrator(report_file, analysis)
        
        # Output summary
        print("\nTemporary File Lifecycle Summary:")
        print(f"  Total temp files: {analysis['total_temp_files']}")
        print(f"  Cleanup candidates: {len(analysis['cleanup_candidates'])}")
        print(f"  Locked files: {len(analysis['locked_files'])}")
        print(f"  Total size: {analysis['total_size_bytes']:,} bytes")
        print(f"  Potential savings: {analysis['potential_cleanup_bytes']:,} bytes")
        
        if not args.report_only:
            print(f"  Files cleaned: {cleanup_results['cleaned']}")
            print(f"  Files skipped: {cleanup_results['skipped']}")
            print(f"  Space freed: {cleanup_results['bytes_freed']:,} bytes")
            
        print("  Safety analysis:")
        print(f"    Safe to clean: {analysis['safety_analysis']['safe_to_clean']}")
        print(f"    Needs review: {analysis['safety_analysis']['needs_review']}")
        print(f"    Do not clean: {analysis['safety_analysis']['do_not_clean']}")
        print(f"  Report: {report_file}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Temporary file lifecycle management failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())