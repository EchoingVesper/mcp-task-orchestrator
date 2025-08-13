#!/usr/bin/env python3

"""
Artifact Cleanup Manager
Part of MCP Task Orchestrator Documentation Ecosystem Modernization

Purpose: Manage artifact lifecycle policies and automated cleanup operations
Integration: Works with orchestrator system and Japanese development principles
"""

import os
import sys
import json
import logging
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import argparse
import subprocess
import fnmatch

# Configuration
SCRIPT_NAME = "artifact_cleanup_manager"
SCRIPT_VERSION = "1.0.0"

class LifecycleStage(Enum):
    """Artifact lifecycle stages"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    ARCHIVE = "archive"
    DISPOSAL = "disposal"

class ArtifactType(Enum):
    """Types of artifacts we manage"""
    DOCUMENTATION = "documentation"
    TEST_ARTIFACTS = "test_artifacts"
    MIGRATION_REPORTS = "migration_reports"
    LOG_FILES = "log_files"
    TEMPORARY_FILES = "temporary_files"
    BACKUP_FILES = "backup_files"
    DRAFT_FILES = "draft_files"

@dataclass
class LifecyclePolicy:
    """Lifecycle policy for artifact types"""
    artifact_type: ArtifactType
    active_retention_days: int
    maintenance_retention_days: int
    archive_retention_days: int
    disposal_after_days: int
    auto_cleanup_enabled: bool = True
    
@dataclass
class ArtifactInfo:
    """Information about an artifact"""
    path: Path
    artifact_type: ArtifactType
    size_bytes: int
    created_time: datetime.datetime
    modified_time: datetime.datetime
    accessed_time: datetime.datetime
    current_stage: LifecycleStage
    next_stage_date: Optional[datetime.datetime] = None

class ArtifactCleanupManager:
    """Main class for managing artifact cleanup and lifecycle"""
    
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.orchestrator_dir = project_root / ".task_orchestrator"
        self.claude_config_dir = project_root / ".claude"
        
        # Set up logging
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='[%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(SCRIPT_NAME)
        
        # Initialize policies
        self.policies = self._initialize_policies()
        
        # Artifact patterns
        self.artifact_patterns = {
            ArtifactType.TEMPORARY_FILES: [
                "*.tmp", "*~", ".*.swp", "*.bak", "*.backup"
            ],
            ArtifactType.LOG_FILES: [
                "*.log", "*.debug", "*.error", "error.log", "debug.log"
            ],
            ArtifactType.TEST_ARTIFACTS: [
                "test_*.json", "validation_*.json", "*_test_report*", 
                "test_results_*", "*_validation_*"
            ],
            ArtifactType.MIGRATION_REPORTS: [
                "migration_report_*", "*_migration_summary*", "migration_*.md",
                "*_migration_*"
            ],
            ArtifactType.DRAFT_FILES: [
                "*[Dd]raft*", "*[Ww]ip*", "*.draft", "draft_*"
            ],
            ArtifactType.BACKUP_FILES: [
                "*.backup", "*_backup_*", "backup_*", "*.orig", "*.bak"
            ]
        }
        
    def _initialize_policies(self) -> Dict[ArtifactType, LifecyclePolicy]:
        """Initialize lifecycle policies for different artifact types"""
        return {
            ArtifactType.TEMPORARY_FILES: LifecyclePolicy(
                ArtifactType.TEMPORARY_FILES,
                active_retention_days=1,
                maintenance_retention_days=7,
                archive_retention_days=30,
                disposal_after_days=30,
                auto_cleanup_enabled=True
            ),
            ArtifactType.LOG_FILES: LifecyclePolicy(
                ArtifactType.LOG_FILES,
                active_retention_days=30,
                maintenance_retention_days=90,
                archive_retention_days=365,
                disposal_after_days=365,
                auto_cleanup_enabled=True
            ),
            ArtifactType.TEST_ARTIFACTS: LifecyclePolicy(
                ArtifactType.TEST_ARTIFACTS,
                active_retention_days=7,
                maintenance_retention_days=30,
                archive_retention_days=90,
                disposal_after_days=180,
                auto_cleanup_enabled=True
            ),
            ArtifactType.MIGRATION_REPORTS: LifecyclePolicy(
                ArtifactType.MIGRATION_REPORTS,
                active_retention_days=30,
                maintenance_retention_days=90,
                archive_retention_days=730,  # 2 years
                disposal_after_days=1095,   # 3 years
                auto_cleanup_enabled=False  # Keep for compliance
            ),
            ArtifactType.DRAFT_FILES: LifecyclePolicy(
                ArtifactType.DRAFT_FILES,
                active_retention_days=7,
                maintenance_retention_days=30,
                archive_retention_days=90,
                disposal_after_days=180,
                auto_cleanup_enabled=True
            ),
            ArtifactType.BACKUP_FILES: LifecyclePolicy(
                ArtifactType.BACKUP_FILES,
                active_retention_days=30,
                maintenance_retention_days=90,
                archive_retention_days=365,
                disposal_after_days=730,  # 2 years
                auto_cleanup_enabled=True
            )
        }
    
    def discover_artifacts(self) -> List[ArtifactInfo]:
        """Discover all artifacts in the project"""
        self.logger.info("Discovering artifacts in project")
        artifacts = []
        
        # Skip certain directories
        skip_dirs = {".git", "node_modules", "venv", "__pycache__", "build", "dist"}
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove skip directories from traversal
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Classify artifact
                artifact_type = self._classify_artifact(file_path)
                if artifact_type is None:
                    continue
                
                # Get file information
                try:
                    stat = file_path.stat()
                    artifact_info = ArtifactInfo(
                        path=file_path,
                        artifact_type=artifact_type,
                        size_bytes=stat.st_size,
                        created_time=datetime.datetime.fromtimestamp(stat.st_ctime),
                        modified_time=datetime.datetime.fromtimestamp(stat.st_mtime),
                        accessed_time=datetime.datetime.fromtimestamp(stat.st_atime),
                        current_stage=self._determine_lifecycle_stage(artifact_type, stat)
                    )
                    artifacts.append(artifact_info)
                    
                except (OSError, IOError) as e:
                    self.logger.warning(f"Could not process {file_path}: {e}")
                    continue
        
        self.logger.info(f"Discovered {len(artifacts)} artifacts")
        return artifacts
    
    def _classify_artifact(self, file_path: Path) -> Optional[ArtifactType]:
        """Classify a file as a specific artifact type"""
        filename = file_path.name
        parent_dir = file_path.parent.name
        
        # Check patterns for each artifact type
        for artifact_type, patterns in self.artifact_patterns.items():
            for pattern in patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return artifact_type
        
        # Special classification based on location
        relative_path = str(file_path.relative_to(self.project_root))
        
        if "test" in relative_path.lower() and filename.endswith(('.json', '.xml', '.html')):
            return ArtifactType.TEST_ARTIFACTS
        
        if "migration" in relative_path.lower() and filename.endswith('.md'):
            return ArtifactType.MIGRATION_REPORTS
        
        if filename.endswith('.md') and any(word in filename.lower() for word in ['draft', 'wip']):
            return ArtifactType.DRAFT_FILES
        
        return None
    
    def _determine_lifecycle_stage(self, artifact_type: ArtifactType, stat: os.stat_result) -> LifecycleStage:
        """Determine current lifecycle stage based on age"""
        policy = self.policies[artifact_type]
        age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(stat.st_mtime)).days
        
        if age_days <= policy.active_retention_days:
            return LifecycleStage.ACTIVE
        elif age_days <= policy.maintenance_retention_days:
            return LifecycleStage.MAINTENANCE
        elif age_days <= policy.archive_retention_days:
            return LifecycleStage.ARCHIVE
        else:
            return LifecycleStage.DISPOSAL
    
    def analyze_artifacts(self, artifacts: List[ArtifactInfo]) -> Dict[str, Any]:
        """Analyze discovered artifacts and generate recommendations"""
        self.logger.info("Analyzing artifacts for lifecycle compliance")
        
        analysis = {
            "total_artifacts": len(artifacts),
            "by_type": {},
            "by_stage": {},
            "cleanup_candidates": [],
            "archive_candidates": [],
            "policy_violations": [],
            "storage_usage": 0,
            "potential_savings": 0
        }
        
        # Initialize counters
        for artifact_type in ArtifactType:
            analysis["by_type"][artifact_type.value] = {
                "count": 0,
                "total_size": 0,
                "stages": {stage.value: 0 for stage in LifecycleStage}
            }
        
        for stage in LifecycleStage:
            analysis["by_stage"][stage.value] = {"count": 0, "total_size": 0}
        
        # Analyze each artifact
        for artifact in artifacts:
            type_key = artifact.artifact_type.value
            stage_key = artifact.current_stage.value
            
            # Update counters
            analysis["by_type"][type_key]["count"] += 1
            analysis["by_type"][type_key]["total_size"] += artifact.size_bytes
            analysis["by_type"][type_key]["stages"][stage_key] += 1
            analysis["by_stage"][stage_key]["count"] += 1
            analysis["by_stage"][stage_key]["total_size"] += artifact.size_bytes
            analysis["storage_usage"] += artifact.size_bytes
            
            # Check for cleanup candidates
            policy = self.policies[artifact.artifact_type]
            
            if artifact.current_stage == LifecycleStage.DISPOSAL:
                analysis["cleanup_candidates"].append({
                    "path": str(artifact.path.relative_to(self.project_root)),
                    "type": type_key,
                    "size": artifact.size_bytes,
                    "age_days": (datetime.datetime.now() - artifact.modified_time).days,
                    "reason": "Past disposal date"
                })
                analysis["potential_savings"] += artifact.size_bytes
                
            elif artifact.current_stage == LifecycleStage.ARCHIVE:
                # Check if should be archived to proper location
                if not self._is_properly_archived(artifact):
                    analysis["archive_candidates"].append({
                        "path": str(artifact.path.relative_to(self.project_root)),
                        "type": type_key,
                        "size": artifact.size_bytes,
                        "suggested_location": self._get_archive_location(artifact)
                    })
        
        return analysis
    
    def _is_properly_archived(self, artifact: ArtifactInfo) -> bool:
        """Check if artifact is in appropriate archive location"""
        relative_path = str(artifact.path.relative_to(self.project_root))
        
        # Define proper archive locations
        archive_paths = {
            ArtifactType.TEST_ARTIFACTS: "docs/archives/test-artifacts",
            ArtifactType.MIGRATION_REPORTS: "docs/archives/migration-reports",
            ArtifactType.LOG_FILES: "logs/archive",
            ArtifactType.BACKUP_FILES: "backups/archive"
        }
        
        expected_path = archive_paths.get(artifact.artifact_type)
        if expected_path:
            return relative_path.startswith(expected_path)
        
        return True  # No specific archive requirement
    
    def _get_archive_location(self, artifact: ArtifactInfo) -> str:
        """Get suggested archive location for artifact"""
        archive_locations = {
            ArtifactType.TEST_ARTIFACTS: "docs/archives/test-artifacts",
            ArtifactType.MIGRATION_REPORTS: "docs/archives/migration-reports",
            ArtifactType.LOG_FILES: "logs/archive",
            ArtifactType.BACKUP_FILES: "backups/archive",
            ArtifactType.DRAFT_FILES: "docs/archives/drafts",
            ArtifactType.TEMPORARY_FILES: "tmp/archive"
        }
        
        return archive_locations.get(artifact.artifact_type, "archives")
    
    def perform_cleanup(self, artifacts: List[ArtifactInfo]) -> Dict[str, Any]:
        """Perform automated cleanup based on policies"""
        self.logger.info(f"Performing cleanup ({'DRY RUN' if self.dry_run else 'LIVE'})")
        
        cleanup_results = {
            "processed": 0,
            "cleaned": 0,
            "archived": 0,
            "errors": 0,
            "bytes_cleaned": 0,
            "bytes_archived": 0,
            "actions": []
        }
        
        for artifact in artifacts:
            cleanup_results["processed"] += 1
            policy = self.policies[artifact.artifact_type]
            
            if not policy.auto_cleanup_enabled:
                continue
            
            try:
                if artifact.current_stage == LifecycleStage.DISPOSAL:
                    # Clean up files past disposal date
                    action = self._cleanup_artifact(artifact)
                    if action:
                        cleanup_results["actions"].append(action)
                        cleanup_results["cleaned"] += 1
                        cleanup_results["bytes_cleaned"] += artifact.size_bytes
                        
                elif artifact.current_stage == LifecycleStage.ARCHIVE:
                    # Archive files that need archiving
                    if not self._is_properly_archived(artifact):
                        action = self._archive_artifact(artifact)
                        if action:
                            cleanup_results["actions"].append(action)
                            cleanup_results["archived"] += 1
                            cleanup_results["bytes_archived"] += artifact.size_bytes
                            
            except Exception as e:
                self.logger.error(f"Error processing {artifact.path}: {e}")
                cleanup_results["errors"] += 1
                cleanup_results["actions"].append({
                    "type": "error",
                    "path": str(artifact.path.relative_to(self.project_root)),
                    "error": str(e)
                })
        
        return cleanup_results
    
    def _cleanup_artifact(self, artifact: ArtifactInfo) -> Optional[Dict[str, Any]]:
        """Remove artifact (disposal stage)"""
        rel_path = str(artifact.path.relative_to(self.project_root))
        
        self.logger.info(f"Cleaning up: {rel_path}")
        
        if not self.dry_run:
            try:
                artifact.path.unlink()
            except OSError as e:
                self.logger.error(f"Failed to delete {rel_path}: {e}")
                return None
        
        return {
            "type": "cleanup",
            "path": rel_path,
            "artifact_type": artifact.artifact_type.value,
            "size": artifact.size_bytes,
            "dry_run": self.dry_run
        }
    
    def _archive_artifact(self, artifact: ArtifactInfo) -> Optional[Dict[str, Any]]:
        """Move artifact to archive location"""
        rel_path = str(artifact.path.relative_to(self.project_root))
        archive_location = self._get_archive_location(artifact)
        archive_dir = self.project_root / archive_location
        
        # Ensure archive directory exists
        if not self.dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Handle filename conflicts
        target_path = archive_dir / artifact.path.name
        if target_path.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = artifact.path.stem
            suffix = artifact.path.suffix
            target_path = archive_dir / f"{stem}_{timestamp}{suffix}"
        
        self.logger.info(f"Archiving: {rel_path} -> {archive_location}/{target_path.name}")
        
        if not self.dry_run:
            try:
                shutil.move(str(artifact.path), str(target_path))
            except (OSError, IOError) as e:
                self.logger.error(f"Failed to archive {rel_path}: {e}")
                return None
        
        return {
            "type": "archive",
            "source_path": rel_path,
            "target_path": f"{archive_location}/{target_path.name}",
            "artifact_type": artifact.artifact_type.value,
            "size": artifact.size_bytes,
            "dry_run": self.dry_run
        }
    
    def generate_report(self, analysis: Dict[str, Any], cleanup_results: Dict[str, Any]) -> str:
        """Generate comprehensive cleanup report"""
        timestamp = datetime.datetime.now().isoformat()
        
        report = {
            "script": SCRIPT_NAME,
            "version": SCRIPT_VERSION,
            "timestamp": timestamp,
            "project_root": str(self.project_root),
            "dry_run": self.dry_run,
            "analysis": analysis,
            "cleanup_results": cleanup_results,
            "policies": {
                atype.value: {
                    "active_retention_days": policy.active_retention_days,
                    "maintenance_retention_days": policy.maintenance_retention_days,
                    "archive_retention_days": policy.archive_retention_days,
                    "disposal_after_days": policy.disposal_after_days,
                    "auto_cleanup_enabled": policy.auto_cleanup_enabled
                }
                for atype, policy in self.policies.items()
            }
        }
        
        # Write report to file
        report_dir = self.project_root / "tmp"
        report_dir.mkdir(exist_ok=True)
        report_file = report_dir / f"artifact_cleanup_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
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
            "artifact_cleanup": {
                "script_name": SCRIPT_NAME,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "completed",
                "total_artifacts": analysis["total_artifacts"],
                "cleanup_candidates": len(analysis["cleanup_candidates"]),
                "archive_candidates": len(analysis["archive_candidates"]),
                "potential_savings_bytes": analysis["potential_savings"],
                "report_file": report_file,
                "dry_run": self.dry_run
            }
        }
        
        # Store update for orchestrator
        status_file = self.orchestrator_dir / "artifact_cleanup_status.json"
        with open(status_file, 'w') as f:
            json.dump(orchestrator_update, f, indent=2)
        
        self.logger.debug(f"Orchestrator update saved: {status_file}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Manage artifact lifecycle and automated cleanup"
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
    
    args = parser.parse_args()
    
    try:
        # Initialize manager
        manager = ArtifactCleanupManager(args.project_root, args.dry_run)
        
        # Discover and analyze artifacts
        artifacts = manager.discover_artifacts()
        analysis = manager.analyze_artifacts(artifacts)
        
        # Perform cleanup if not report-only
        if args.report_only:
            cleanup_results = {
                "processed": 0,
                "cleaned": 0,
                "archived": 0,
                "errors": 0,
                "bytes_cleaned": 0,
                "bytes_archived": 0,
                "actions": []
            }
            logging.info("Report-only mode: skipping cleanup operations")
        else:
            cleanup_results = manager.perform_cleanup(artifacts)
        
        # Generate report and integrate with orchestrator
        report_file = manager.generate_report(analysis, cleanup_results)
        manager.integrate_with_orchestrator(report_file, analysis)
        
        # Output summary
        print("\nArtifact Cleanup Summary:")
        print(f"  Total artifacts: {analysis['total_artifacts']}")
        print(f"  Cleanup candidates: {len(analysis['cleanup_candidates'])}")
        print(f"  Archive candidates: {len(analysis['archive_candidates'])}")
        if not args.report_only:
            print(f"  Files cleaned: {cleanup_results['cleaned']}")
            print(f"  Files archived: {cleanup_results['archived']}")
            print(f"  Storage freed: {cleanup_results['bytes_cleaned']:,} bytes")
        print(f"  Report: {report_file}")
        
        return 0
        
    except Exception as e:
        logging.error(f"Artifact cleanup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())