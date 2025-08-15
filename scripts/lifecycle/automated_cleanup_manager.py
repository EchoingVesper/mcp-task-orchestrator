#!/usr/bin/env python3
"""
Automated Cleanup Manager for Documentation Ecosystem
Part of Phase 4 - Documentation Ecosystem Modernization

This script implements automated lifecycle management and cleanup 
prevention for the mcp-task-orchestrator project.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedCleanupManager:
    """Manages automated cleanup and lifecycle operations"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.archives_path = self.project_root / "docs" / "archives"
        self.scripts_temp = self.project_root / "scripts" / "testing" / "temporary"
        
        # Patterns for temporary files that should be cleaned
        self.temp_patterns = {
            "fix_scripts": ["fix_*.py"],
            "test_reports": ["*_test_report_*.json", "system_health*.json"],
            "security_reports": ["security_test_suite*.*"],
            "temp_logs": ["*.log"],
            "validation_reports": ["validation_*.json"],
            "hook_test_scripts": ["test-*hooks*.sh"]
        }
        
        # Retention policies (days)
        self.retention_policies = {
            "test_artifacts": 90,  # 3 months
            "system_health": 30,   # Keep latest 5, but clean after 30 days  
            "security_reports": 60, # 2 months
            "temp_scripts": 7,     # 1 week
            "validation_reports": 180  # 6 months
        }
        
    def scan_root_directory(self) -> Dict[str, List[Path]]:
        """Scan root directory for temporary files that need cleanup"""
        found_files = {category: [] for category in self.temp_patterns.keys()}
        
        for category, patterns in self.temp_patterns.items():
            for pattern in patterns:
                matches = list(self.project_root.glob(pattern))
                found_files[category].extend(matches)
                
        return found_files
        
    def cleanup_root_temporary_files(self, dry_run: bool = True) -> Dict[str, int]:
        """Clean up temporary files from root directory"""
        found_files = self.scan_root_directory()
        cleanup_stats = {"moved": 0, "archived": 0, "errors": 0}
        
        for category, files in found_files.items():
            if not files:
                continue
                
            logger.info(f"Processing {len(files)} files in category: {category}")
            
            for file_path in files:
                try:
                    if self._should_cleanup_file(file_path, category):
                        target_path = self._get_target_path(file_path, category)
                        
                        if not dry_run:
                            self._move_file_safely(file_path, target_path)
                            cleanup_stats["moved"] += 1
                        else:
                            logger.info(f"Would move: {file_path} -> {target_path}")
                            
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    cleanup_stats["errors"] += 1
                    
        return cleanup_stats
        
    def _should_cleanup_file(self, file_path: Path, category: str) -> bool:
        """Determine if a file should be cleaned up based on age and category"""
        if not file_path.exists():
            return False
            
        # Get file age
        file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
        max_age = timedelta(days=self.retention_policies.get(category, 7))
        
        # Always cleanup temp_scripts, others based on age
        if category == "temp_scripts":
            return True
        elif category in ["test_reports", "security_reports"]:
            return file_age > max_age or file_path.name.startswith(("fix_", "test_", "system_health"))
        else:
            return file_age > max_age
            
    def _get_target_path(self, file_path: Path, category: str) -> Path:
        """Get target path for file based on category"""
        if category in ["fix_scripts", "temp_scripts", "hook_test_scripts"]:
            return self.scripts_temp / file_path.name
        elif category in ["test_reports", "security_reports", "validation_reports"]:
            return self.archives_path / "test-artifacts" / file_path.name
        else:
            return self.archives_path / "historical" / "development-scripts" / file_path.name
            
    def _move_file_safely(self, source: Path, target: Path) -> None:
        """Move file safely, creating directories and avoiding conflicts"""
        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle name conflicts
        if target.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = target.stem
            suffix = target.suffix
            target = target.parent / f"{stem}_{timestamp}{suffix}"
            
        # Move file
        shutil.move(str(source), str(target))
        logger.info(f"Moved: {source} -> {target}")
        
    def apply_retention_policies(self, dry_run: bool = True) -> Dict[str, int]:
        """Apply retention policies to archived files"""
        stats = {"removed": 0, "kept": 0, "errors": 0}
        
        # Clean old test artifacts
        test_artifacts_path = self.archives_path / "test-artifacts"
        if test_artifacts_path.exists():
            for file_path in test_artifacts_path.rglob("*"):
                if file_path.is_file():
                    try:
                        age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        # Keep system health reports (latest 5)
                        if "system_health" in file_path.name:
                            health_files = sorted(
                                [f for f in test_artifacts_path.glob("system_health*.json")],
                                key=lambda x: x.stat().st_mtime,
                                reverse=True
                            )
                            if file_path not in health_files[:5]:
                                if not dry_run:
                                    file_path.unlink()
                                    stats["removed"] += 1
                                else:
                                    logger.info(f"Would remove old health report: {file_path}")
                            else:
                                stats["kept"] += 1
                                
                        # Apply general retention policies
                        elif age.days > self.retention_policies.get("test_artifacts", 90):
                            if not dry_run:
                                file_path.unlink()
                                stats["removed"] += 1
                            else:
                                logger.info(f"Would remove old artifact: {file_path}")
                        else:
                            stats["kept"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        stats["errors"] += 1
                        
        return stats
        
    def update_gitignore(self) -> None:
        """Update .gitignore to prevent temporary files from being committed"""
        gitignore_path = self.project_root / ".gitignore"
        
        temp_file_patterns = [
            "# Temporary files from development",
            "fix_*.py",
            "system_health*.json",
            "security_test_suite*.*",
            "test-*hooks*.sh",
            "*.log",
            "validation_*.json",
            "",
            "# Testing artifacts",
            "test_mcp_compatibility.py",
            "*_test_report_*.json",
            "",
        ]
        
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                current_content = f.read()
                
            # Add patterns if not already present
            patterns_to_add = []
            for pattern in temp_file_patterns:
                if pattern and pattern not in current_content:
                    patterns_to_add.append(pattern)
                    
            if patterns_to_add:
                with open(gitignore_path, "a") as f:
                    f.write("\n" + "\n".join(patterns_to_add) + "\n")
                logger.info(f"Added {len(patterns_to_add)} patterns to .gitignore")
                
    def generate_cleanup_report(self, cleanup_stats: Dict, retention_stats: Dict) -> str:
        """Generate cleanup report"""
        timestamp = datetime.now().isoformat()
        
        report = {
            "timestamp": timestamp,
            "cleanup_operation": {
                "root_directory_cleanup": cleanup_stats,
                "retention_policy_application": retention_stats
            },
            "summary": {
                "total_files_moved": cleanup_stats.get("moved", 0),
                "total_files_removed": retention_stats.get("removed", 0),
                "total_errors": cleanup_stats.get("errors", 0) + retention_stats.get("errors", 0)
            },
            "next_recommended_cleanup": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        return json.dumps(report, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Automated Cleanup Manager")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--apply-retention", action="store_true", help="Apply retention policies to archives")
    parser.add_argument("--update-gitignore", action="store_true", help="Update .gitignore with temp file patterns")
    parser.add_argument("--report", help="Generate cleanup report to specified file")
    
    args = parser.parse_args()
    
    manager = AutomatedCleanupManager(Path(args.project_root))
    
    logger.info("Starting automated cleanup manager...")
    
    # Cleanup root directory
    cleanup_stats = manager.cleanup_root_temporary_files(dry_run=args.dry_run)
    logger.info(f"Root cleanup stats: {cleanup_stats}")
    
    # Apply retention policies if requested
    retention_stats = {}
    if args.apply_retention:
        retention_stats = manager.apply_retention_policies(dry_run=args.dry_run)
        logger.info(f"Retention policy stats: {retention_stats}")
        
    # Update gitignore if requested
    if args.update_gitignore:
        manager.update_gitignore()
        
    # Generate report if requested
    if args.report:
        report = manager.generate_cleanup_report(cleanup_stats, retention_stats)
        with open(args.report, "w") as f:
            f.write(report)
        logger.info(f"Cleanup report saved to: {args.report}")
        
    logger.info("Automated cleanup manager completed")

if __name__ == "__main__":
    main()