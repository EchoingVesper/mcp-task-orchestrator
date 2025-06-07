#!/usr/bin/env python3
"""
Automated Maintenance and Cleanup System
Maintains project organization and health automatically.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class AutomatedMaintenance:
    """Automated project maintenance and cleanup system."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.actions_taken = []
        self.issues_found = []
        
    def log_action(self, action: str, details: str = ""):
        """Log maintenance action."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_action = f"[{timestamp}] {action}"
        if details:
            full_action += f": {details}"
        self.actions_taken.append(full_action)
        if not self.dry_run:
            print(f"✅ {full_action}")
        else:
            print(f"🔍 DRY RUN: {full_action}")
    
    def log_issue(self, issue: str, severity: str = "INFO"):
        """Log maintenance issue."""
        self.issues_found.append(f"[{severity}] {issue}")
        emoji = "🚨" if severity == "CRITICAL" else "⚠️" if severity == "WARNING" else "ℹ️"
        print(f"{emoji} {issue}")
    
    def clean_build_artifacts(self) -> bool:
        """Clean build artifacts and temporary files."""
        artifacts_cleaned = False
        
        # Remove build directories
        for build_dir in ['build', 'dist']:
            if os.path.exists(build_dir):
                if not self.dry_run:
                    shutil.rmtree(build_dir)
                self.log_action(f"Removed build directory", build_dir)
                artifacts_cleaned = True
        
        # Remove egg-info directories
        for item in os.listdir('.'):
            if item.endswith('.egg-info') and os.path.isdir(item):
                if not self.dry_run:
                    shutil.rmtree(item)
                self.log_action(f"Removed egg-info directory", item)
                artifacts_cleaned = True
        
        # Clean Python cache files
        cache_dirs = list(Path('.').glob('**/__pycache__'))
        for cache_dir in cache_dirs:
            if 'venv' not in str(cache_dir):  # Preserve venv cache
                if not self.dry_run:
                    shutil.rmtree(cache_dir)
                self.log_action(f"Removed cache directory", str(cache_dir))
                artifacts_cleaned = True
        
        # Clean pytest cache
        pytest_caches = list(Path('.').glob('**/.pytest_cache'))
        for cache_dir in pytest_caches:
            if 'venv' not in str(cache_dir):
                if not self.dry_run:
                    shutil.rmtree(cache_dir)
                self.log_action(f"Removed pytest cache", str(cache_dir))
                artifacts_cleaned = True
        
        if not artifacts_cleaned:
            self.log_action("No build artifacts found to clean")
            
        return artifacts_cleaned
    
    def validate_file_organization(self) -> List[str]:
        """Validate and suggest file organization improvements."""
        suggestions = []
        
        # Check for misplaced scripts in root
        root_files = [f for f in os.listdir('.') if os.path.isfile(f)]
        misplaced_scripts = [f for f in root_files if f.endswith('.py') and f not in [
            'setup.py', 'launch_cli.py', 'launch_orchestrator.py'
        ]]
        
        if misplaced_scripts:
            suggestions.append(f"Consider moving scripts to scripts/: {', '.join(misplaced_scripts)}")
            
        # Check for misplaced documentation
        misplaced_docs = [f for f in root_files if f.endswith('.md') and f not in [
            'README.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'CLAUDE.md', 'QUICK_START.md'
        ]]
        
        if misplaced_docs:
            suggestions.append(f"Consider moving documentation to docs/: {', '.join(misplaced_docs)}")
            
        # Check script organization
        if os.path.exists('scripts'):
            script_subdirs = ['build', 'testing', 'diagnostics', 'deployment']
            missing_dirs = [d for d in script_subdirs if not os.path.exists(f'scripts/{d}')]
            if missing_dirs:
                suggestions.append(f"Consider creating script directories: {', '.join(missing_dirs)}")
        
        return suggestions
    
    def optimize_gitignore(self) -> bool:
        """Optimize .gitignore patterns."""
        if not os.path.exists('.gitignore'):
            self.log_issue("No .gitignore file found", "WARNING")
            return False
            
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        # Essential patterns that should be present
        essential_patterns = [
            '__pycache__/',
            '*.pyc',
            '.pytest_cache/',
            'build/',
            'dist/',
            '*.egg-info/',
            'venv*/',
            '.env',
            'temp/',
            '*-session.md'
        ]
        
        missing_patterns = []
        for pattern in essential_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            self.log_issue(f"Missing .gitignore patterns: {', '.join(missing_patterns)}", "INFO")
            return False
        else:
            self.log_action("✅ .gitignore contains all essential patterns")
            return True
    
    def validate_directory_structure(self) -> bool:
        """Validate expected directory structure."""
        expected_dirs = [
            'docs',
            'docs/releases', 
            'docs/testing',
            'docs/development',
            'docs/user-guide',
            'docs/troubleshooting',
            'scripts',
            'scripts/build',
            'scripts/testing', 
            'scripts/diagnostics',
            'scripts/deployment',
            'tests',
            'mcp_task_orchestrator',
            'mcp_task_orchestrator_cli'
        ]
        
        all_present = True
        for directory in expected_dirs:
            if not os.path.exists(directory):
                self.log_issue(f"Missing expected directory: {directory}", "WARNING")
                all_present = False
        
        if all_present:
            self.log_action("✅ All expected directories present")
            
        return all_present
    
    def run_maintenance_cycle(self) -> Dict[str, any]:
        """Run complete maintenance cycle."""
        self.log_action("Starting automated maintenance cycle")
        
        results = {
            "start_time": datetime.now().isoformat(),
            "artifacts_cleaned": False,
            "organization_validated": False,
            "directory_structure_valid": False,
            "gitignore_optimized": False,
            "suggestions": [],
            "actions_taken": [],
            "issues_found": []
        }
        
        # Clean build artifacts
        results["artifacts_cleaned"] = self.clean_build_artifacts()
        
        # Validate file organization
        suggestions = self.validate_file_organization()
        results["suggestions"] = suggestions
        if suggestions:
            for suggestion in suggestions:
                self.log_issue(suggestion, "INFO")
        else:
            self.log_action("✅ File organization looks good")
            results["organization_validated"] = True
        
        # Validate directory structure
        results["directory_structure_valid"] = self.validate_directory_structure()
        
        # Optimize .gitignore
        results["gitignore_optimized"] = self.optimize_gitignore()
        
        # Final summary
        results["end_time"] = datetime.now().isoformat()
        results["actions_taken"] = self.actions_taken
        results["issues_found"] = self.issues_found
        
        self.log_action("Maintenance cycle completed")
        
        return results
    
    def generate_maintenance_report(self, results: Dict) -> str:
        """Generate maintenance report."""
        report = []
        report.append("🔧 AUTOMATED MAINTENANCE REPORT")
        report.append("=" * 40)
        report.append(f"Execution Time: {results['start_time']} to {results['end_time']}")
        report.append(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        report.append("")
        
        # Summary
        report.append("📊 MAINTENANCE SUMMARY:")
        report.append(f"   Artifacts Cleaned: {'✅' if results['artifacts_cleaned'] else '❌'}")
        report.append(f"   Organization Valid: {'✅' if results['organization_validated'] else '⚠️'}")
        report.append(f"   Directory Structure: {'✅' if results['directory_structure_valid'] else '⚠️'}")
        report.append(f"   GitIgnore Optimized: {'✅' if results['gitignore_optimized'] else '⚠️'}")
        report.append("")
        
        # Actions taken
        if results["actions_taken"]:
            report.append("🔨 ACTIONS TAKEN:")
            for action in results["actions_taken"]:
                report.append(f"   {action}")
            report.append("")
        
        # Issues found
        if results["issues_found"]:
            report.append("⚠️ ISSUES IDENTIFIED:")
            for issue in results["issues_found"]:
                report.append(f"   {issue}")
            report.append("")
        
        # Suggestions
        if results["suggestions"]:
            report.append("💡 IMPROVEMENT SUGGESTIONS:")
            for suggestion in results["suggestions"]:
                report.append(f"   • {suggestion}")
            report.append("")
        
        return "\\n".join(report)

def main():
    """Main maintenance function."""
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    maintenance = AutomatedMaintenance(dry_run=dry_run)
    
    print("🔧 MCP Task Orchestrator - Automated Maintenance")
    print("=" * 50)
    
    if dry_run:
        print("🔍 DRY RUN MODE: No changes will be made")
        print("")
    
    results = maintenance.run_maintenance_cycle()
    
    if verbose or dry_run:
        print("")
        print(maintenance.generate_maintenance_report(results))
    
    # Exit with appropriate code
    has_critical_issues = any("CRITICAL" in issue for issue in results["issues_found"])
    sys.exit(1 if has_critical_issues else 0)

if __name__ == "__main__":
    main()