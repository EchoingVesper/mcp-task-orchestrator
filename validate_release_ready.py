#!/usr/bin/env python3
"""
Final validation script for MCP Task Orchestrator v1.6.0 PyPI release
Performs comprehensive checks to ensure the package is ready for upload
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import List, Dict, Any

class ReleaseValidator:
    """Validates that the package is ready for PyPI release"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.expected_version = "1.6.0"
        self.issues = []
        self.warnings = []
    
    def check_version_consistency(self) -> bool:
        """Check that version is consistent across all files"""
        print("🔍 Checking version consistency...")
        
        version_files = [
            ('setup.py', r'version\s*=\s*["\']([^"\']+)["\']'),
            ('mcp_task_orchestrator/__init__.py', r'__version__\s*=\s*["\']([^"\']+)["\']'),
        ]
        
        versions_found = {}
        all_correct = True
        
        for file_path, pattern in version_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'r') as f:
                    content = f.read()
                    match = re.search(pattern, content)
                    if match:
                        version = match.group(1)
                        versions_found[file_path] = version
                        if version == self.expected_version:
                            print(f"  ✅ {file_path}: {version}")
                        else:
                            print(f"  ❌ {file_path}: {version} (expected {self.expected_version})")
                            all_correct = False
                    else:
                        print(f"  ❌ {file_path}: No version found")
                        all_correct = False
            else:
                print(f"  ❌ {file_path}: File not found")
                all_correct = False
        
        if not all_correct:
            self.issues.append("Version inconsistency or missing version information")
        
        return all_correct
    
    def check_package_structure(self) -> bool:
        """Check that all required files are present"""
        print("\n📂 Checking package structure...")
        
        required_files = [
            'setup.py',
            'pyproject.toml',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'CHANGELOG.md',
        ]
        
        package_files = [
            'mcp_task_orchestrator/__init__.py',
            'mcp_task_orchestrator/server.py',
            'mcp_task_orchestrator/persistence.py',
            'mcp_task_orchestrator_cli/__init__.py',
            'mcp_task_orchestrator_cli/cli.py',
        ]
        
        new_feature_files = [
            'mcp_task_orchestrator/db/__init__.py',
            'mcp_task_orchestrator/db/auto_migration.py',
            'mcp_task_orchestrator/db/migration_manager.py',
            'mcp_task_orchestrator/db/backup_manager.py',
            'mcp_task_orchestrator/server/__init__.py',
            'mcp_task_orchestrator/server/reboot_tools.py',
            'mcp_task_orchestrator/server/restart_manager.py',
            'mcp_task_orchestrator/server/connection_manager.py',
        ]
        
        all_files = required_files + package_files + new_feature_files
        missing_files = []
        
        for file_path in all_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                missing_files.append(file_path)
        
        if missing_files:
            self.issues.append(f"{len(missing_files)} required files missing: {', '.join(missing_files[:3])}...")
            return False
        
        print(f"  ✅ All {len(all_files)} files present")
        return True
    
    def check_setup_configuration(self) -> bool:
        """Check setup.py configuration"""
        print("\n⚙️ Checking setup.py configuration...")
        
        setup_file = self.project_root / 'setup.py'
        if not setup_file.exists():
            self.issues.append("setup.py not found")
            return False
        
        with open(setup_file, 'r') as f:
            content = f.read()
        
        # Check required fields
        required_fields = [
            ('name', 'mcp-task-orchestrator'),
            ('author', 'Echoing Vesper'),
            ('description', 'A Model Context Protocol server'),
            ('long_description_content_type', 'text/markdown'),
        ]
        
        all_good = True
        for field, expected in required_fields:
            if expected in content:
                print(f"  ✅ {field}: Found")
            else:
                print(f"  ❌ {field}: Not found or incorrect")
                all_good = False
        
        # Check entry points
        if 'mcp-task-orchestrator=' in content and 'mcp-task-orchestrator-cli=' in content:
            print("  ✅ Entry points: Configured")
        else:
            print("  ❌ Entry points: Missing or incorrect")
            all_good = False
        
        # Check classifiers
        if 'Programming Language :: Python :: 3' in content:
            print("  ✅ Python classifiers: Found")
        else:
            print("  ❌ Python classifiers: Missing")
            all_good = False
        
        if not all_good:
            self.issues.append("setup.py configuration issues")
        
        return all_good
    
    def check_dependencies(self) -> bool:
        """Check requirements.txt and setup.py dependencies"""
        print("\n📦 Checking dependencies...")
        
        # Check requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = f.read()
            
            critical_deps = ['mcp>=', 'pydantic>=', 'sqlalchemy>=', 'alembic>=']
            for dep in critical_deps:
                if dep in requirements:
                    print(f"  ✅ {dep.rstrip('>=')} dependency found")
                else:
                    print(f"  ❌ {dep.rstrip('>=')} dependency missing")
                    self.issues.append(f"Missing critical dependency: {dep}")
                    return False
        else:
            self.issues.append("requirements.txt not found")
            return False
        
        print("  ✅ All critical dependencies present")
        return True
    
    def check_build_readiness(self) -> bool:
        """Check if ready for building"""
        print("\n🔧 Checking build readiness...")
        
        # Check for old build artifacts
        old_artifacts = []
        for dirname in ['build', 'dist', 'mcp_task_orchestrator.egg-info']:
            if (self.project_root / dirname).exists():
                old_artifacts.append(dirname)
        
        if old_artifacts:
            print(f"  ⚠️  Old build artifacts present: {', '.join(old_artifacts)}")
            self.warnings.append("Old build artifacts should be cleaned before building")
        else:
            print("  ✅ No old build artifacts found")
        
        # Check pyproject.toml
        pyproject_file = self.project_root / 'pyproject.toml'
        if pyproject_file.exists():
            print("  ✅ pyproject.toml present")
        else:
            print("  ❌ pyproject.toml missing")
            self.issues.append("pyproject.toml required for modern Python packaging")
            return False
        
        return True
    
    def check_new_features(self) -> bool:
        """Check that new v1.6.0 features are present"""
        print("\n🆕 Checking new features for v1.6.0...")
        
        new_features = {
            'Auto Migration System': [
                'mcp_task_orchestrator/db/auto_migration.py',
                'mcp_task_orchestrator/db/migration_manager.py',
                'mcp_task_orchestrator/db/backup_manager.py',
            ],
            'Server Reboot System': [
                'mcp_task_orchestrator/server/reboot_tools.py',
                'mcp_task_orchestrator/server/restart_manager.py',
                'mcp_task_orchestrator/server/connection_manager.py',
            ],
            'Enhanced Repository': [
                'mcp_task_orchestrator/db/repository/__init__.py',
                'mcp_task_orchestrator/db/repository/base.py',
                'mcp_task_orchestrator/db/repository/crud_operations.py',
            ]
        }
        
        all_features_present = True
        
        for feature_name, files in new_features.items():
            missing_files = []
            for file_path in files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            if missing_files:
                print(f"  ❌ {feature_name}: {len(missing_files)} files missing")
                all_features_present = False
            else:
                print(f"  ✅ {feature_name}: All files present")
        
        if not all_features_present:
            self.issues.append("Some new features have missing files")
        
        return all_features_present
    
    def generate_report(self) -> bool:
        """Generate final validation report"""
        print("\n" + "="*60)
        print("📋 MCP Task Orchestrator v1.6.0 - Release Validation Report")
        print("="*60)
        
        if not self.issues and not self.warnings:
            print("🎉 ✅ READY FOR PYPI RELEASE!")
            print("\n📦 Package Summary:")
            print(f"  • Version: {self.expected_version}")
            print("  • Type: Production release")
            print("  • New Features: Migration System, Server Reboot, Enhanced DB")
            
            print("\n🚀 Next Steps:")
            print("  1. Clean and build:")
            print("     python execute_pypi_build.py")
            print("  2. Validate packages:")
            print("     python -m twine check dist/*")
            print("  3. Test upload (optional):")
            print("     python scripts/release/upload.py --test")
            print("  4. Production upload:")
            print("     python scripts/release/upload.py")
            
            return True
        else:
            print("❌ NOT READY FOR RELEASE")
            
            if self.issues:
                print(f"\n🚨 Critical Issues ({len(self.issues)}):")
                for i, issue in enumerate(self.issues, 1):
                    print(f"  {i}. {issue}")
            
            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"  {i}. {warning}")
            
            print("\n🔧 Resolve all critical issues before proceeding with release.")
            return False
    
    def run_full_validation(self) -> bool:
        """Run complete validation suite"""
        print("🔍 MCP Task Orchestrator v1.6.0 - Release Validation")
        print("="*60)
        
        validation_steps = [
            ("Version Consistency", self.check_version_consistency),
            ("Package Structure", self.check_package_structure),
            ("Setup Configuration", self.check_setup_configuration),
            ("Dependencies", self.check_dependencies),
            ("Build Readiness", self.check_build_readiness),
            ("New Features", self.check_new_features),
        ]
        
        all_passed = True
        
        for step_name, step_func in validation_steps:
            try:
                if not step_func():
                    all_passed = False
            except Exception as e:
                print(f"  💥 Error in {step_name}: {e}")
                self.issues.append(f"Validation error in {step_name}: {e}")
                all_passed = False
        
        return self.generate_report()

def main():
    """Main execution"""
    validator = ReleaseValidator()
    
    try:
        success = validator.run_full_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()