#!/usr/bin/env python3
"""
PyPI Release Automation Script
Handles version bumping, building, and uploading to PyPI
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import re
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / '.env')


class ReleaseManager:
    """Manages the release process for PyPI packages"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.setup_file = self.project_root / 'setup.py'
        self.token = os.getenv('PYPI_API_TOKEN')
        self.test_token = os.getenv('PYPI_TEST_TOKEN')
        self.auto_tag = os.getenv('AUTO_GIT_TAG', 'true').lower() == 'true'
        self.run_tests = os.getenv('RUN_TESTS_BEFORE_UPLOAD', 'true').lower() == 'true'
        self.clean_artifacts = os.getenv('CLEAN_BUILD_ARTIFACTS', 'true').lower() == 'true'
        
    def get_current_version(self) -> str:
        """Extract current version from setup.py"""
        with open(self.setup_file, 'r') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
            raise ValueError("Could not find version in setup.py")
    
    def bump_version(self, bump_type: str) -> str:
        """Bump version based on type (patch, minor, major)"""
        current = self.get_current_version()
        parts = current.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if bump_type == 'patch':
            patch += 1
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        return f"{major}.{minor}.{patch}"
    
    def update_version_files(self, new_version: str):
        """Update version in all relevant files"""
        files_to_update = [
            ('setup.py', r'version\s*=\s*["\'][^"\']+["\']', f'version="{new_version}"'),
            ('mcp_task_orchestrator/__init__.py', r'__version__\s*=\s*["\'][^"\']+["\']', f'__version__ = "{new_version}"'),
            ('README.md', r'Version \d+\.\d+\.\d+', f'Version {new_version}'),
            ('README.md', r'version-\d+\.\d+\.\d+-green', f'version-{new_version}-green'),
        ]
        
        for filepath, pattern, replacement in files_to_update:
            full_path = self.project_root / filepath
            if full_path.exists():
                with open(full_path, 'r') as f:
                    content = f.read()
                
                updated_content = re.sub(pattern, replacement, content)
                
                with open(full_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"✓ Updated version in {filepath}")
    
    def run_tests(self):
        """Run test suite"""
        print("\n🧪 Running tests...")
        try:
            subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                         check=True, cwd=self.project_root)
            print("✓ All tests passed")
        except subprocess.CalledProcessError:
            print("✗ Tests failed! Aborting release.")
            sys.exit(1)
    
    def clean_build_artifacts(self):
        """Remove build artifacts"""
        print("\n🧹 Cleaning build artifacts...")
        dirs_to_remove = ['dist', 'build', 'mcp_task_orchestrator.egg-info']
        for dir_name in dirs_to_remove:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
                print(f"✓ Removed {dir_name}/")
    
    def build_package(self):
        """Build distribution packages"""
        print("\n📦 Building packages...")
        self.clean_build_artifacts()
        
        subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'], 
                      check=True, cwd=self.project_root)
        print("✓ Packages built successfully")
    
    def validate_package(self):
        """Validate package with twine check"""
        print("\n🔍 Validating packages...")
        subprocess.run([sys.executable, '-m', 'twine', 'check', 'dist/*'], 
                      check=True, cwd=self.project_root)
        print("✓ Package validation passed")
    
    def upload_to_pypi(self, test: bool = False):
        """Upload package to PyPI or TestPyPI"""
        token = self.test_token if test else self.token
        if not token:
            print(f"✗ {'Test' if test else ''}PyPI token not found in environment!")
            print("  Set PYPI_API_TOKEN in your .env file")
            sys.exit(1)
        
        repo_name = "TestPyPI" if test else "PyPI"
        print(f"\n📤 Uploading to {repo_name}...")
        
        cmd = [sys.executable, '-m', 'twine', 'upload']
        if test:
            cmd.extend(['--repository-url', os.getenv('TEST_PYPI_REPOSITORY_URL')])
        
        cmd.extend(['-u', '__token__', '-p', token, 'dist/*'])
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print(f"✓ Successfully uploaded to {repo_name}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to upload to {repo_name}")
            sys.exit(1)
    
    def create_git_tag(self, version: str):
        """Create and push git tag"""
        if not self.auto_tag:
            return
        
        print(f"\n🏷️  Creating git tag v{version}...")
        try:
            subprocess.run(['git', 'add', '-A'], check=True, cwd=self.project_root)
            subprocess.run(['git', 'commit', '-m', f'Release version {version}'], 
                         check=True, cwd=self.project_root)
            subprocess.run(['git', 'tag', f'v{version}'], check=True, cwd=self.project_root)
            print(f"✓ Created tag v{version}")
            print("  To push: git push origin main --tags")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git operations failed: {e}")
    
    def release(self, bump_type: str, test: bool = False):
        """Execute the full release process"""
        print(f"🚀 Starting {'test ' if test else ''}release process...")
        
        # Get current and new versions
        current_version = self.get_current_version()
        new_version = self.bump_version(bump_type)
        
        print(f"\n📊 Version: {current_version} → {new_version}")
        
        # Confirm with user
        response = input(f"\nProceed with release? [y/N]: ")
        if response.lower() != 'y':
            print("❌ Release cancelled")
            return
        
        # Update version files
        self.update_version_files(new_version)
        
        # Run tests if enabled
        if self.run_tests:
            self.run_tests()
        
        # Build package
        self.build_package()
        
        # Validate package
        self.validate_package()
        
        # Upload to PyPI
        self.upload_to_pypi(test=test)
        
        # Create git tag
        self.create_git_tag(new_version)
        
        # Clean up if enabled
        if self.clean_artifacts and not test:
            self.clean_build_artifacts()
        
        print(f"\n✨ Release {new_version} completed successfully!")
        if test:
            print(f"   Test package: https://test.pypi.org/project/mcp-task-orchestrator/{new_version}/")
        else:
            print(f"   Package: https://pypi.org/project/mcp-task-orchestrator/{new_version}/")


def main():
    parser = argparse.ArgumentParser(description='Release package to PyPI')
    parser.add_argument('--patch', action='store_true', help='Bump patch version (x.x.N)')
    parser.add_argument('--minor', action='store_true', help='Bump minor version (x.N.0)')
    parser.add_argument('--major', action='store_true', help='Bump major version (N.0.0)')
    parser.add_argument('--test', action='store_true', help='Upload to TestPyPI instead')
    
    args = parser.parse_args()
    
    # Determine bump type
    if args.patch:
        bump_type = 'patch'
    elif args.minor:
        bump_type = 'minor'
    elif args.major:
        bump_type = 'major'
    else:
        parser.error('Must specify --patch, --minor, or --major')
    
    # Create release manager and execute
    manager = ReleaseManager()
    
    try:
        manager.release(bump_type, test=args.test)
    except KeyboardInterrupt:
        print("\n❌ Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Release failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()