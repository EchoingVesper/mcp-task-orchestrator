#!/usr/bin/env python3
"""
PyPI Release Preparation Script for version 1.6.0
Handles cleanup, building, and validation of distribution packages
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
import zipfile
import tarfile
import tempfile

# Set project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

class PyPIReleasePreparation:
    """Handles PyPI release preparation tasks"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.venv_pypi = self.project_root / 'venv_pypi'
        self.python_exe = self.venv_pypi / 'bin' / 'python'
        self.pip_exe = self.venv_pypi / 'bin' / 'pip'
        
        # Fallback to system Python if venv doesn't exist
        if not self.python_exe.exists():
            self.python_exe = sys.executable
            self.pip_exe = 'pip'
            print("⚠️  PyPI venv not found, using system Python")
    
    def get_current_version(self) -> str:
        """Get version from setup.py"""
        import re
        setup_file = self.project_root / 'setup.py'
        with open(setup_file, 'r') as f:
            content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
            raise ValueError("Could not find version in setup.py")
    
    def clean_build_artifacts(self):
        """Remove old build artifacts"""
        print("🧹 Cleaning build artifacts...")
        
        dirs_to_remove = ['build', 'dist', 'mcp_task_orchestrator.egg-info']
        for dir_name in dirs_to_remove:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  ✓ Removed {dir_name}/")
            else:
                print(f"  - {dir_name}/ (not found)")
        
        print("✅ Build artifacts cleaned")
    
    def validate_package_structure(self):
        """Validate that all necessary files are present"""
        print("🔍 Validating package structure...")
        
        required_files = [
            'setup.py',
            'requirements.txt',
            'README.md',
            'LICENSE',
            'mcp_task_orchestrator/__init__.py',
            'mcp_task_orchestrator/server.py',
            'mcp_task_orchestrator_cli/__init__.py',
            'mcp_task_orchestrator_cli/cli.py',
        ]
        
        # Check for new features
        new_features = [
            'mcp_task_orchestrator/db/auto_migration.py',
            'mcp_task_orchestrator/db/migration_manager.py',
            'mcp_task_orchestrator/server/reboot_tools.py',
            'mcp_task_orchestrator/server/restart_manager.py',
        ]
        
        missing_files = []
        for file_path in required_files + new_features:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
                print(f"  ❌ Missing: {file_path}")
            else:
                print(f"  ✓ Found: {file_path}")
        
        if missing_files:
            print(f"\n❌ Missing {len(missing_files)} required files!")
            return False
        
        print("✅ Package structure validation passed")
        return True
    
    def check_dependencies(self):
        """Check that all dependencies are correctly specified"""
        print("📦 Checking dependencies...")
        
        # Install required build tools
        build_deps = ['wheel', 'twine', 'setuptools']
        for dep in build_deps:
            try:
                result = subprocess.run([str(self.pip_exe), 'show', dep], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✓ {dep} installed")
                else:
                    print(f"  📥 Installing {dep}...")
                    subprocess.run([str(self.pip_exe), 'install', dep], check=True)
                    print(f"  ✓ {dep} installed")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {dep}")
                return False
        
        print("✅ Dependencies check passed")
        return True
    
    def build_distributions(self):
        """Build source and wheel distributions"""
        print("🏗️  Building distribution packages...")
        
        try:
            # Build both source distribution and wheel
            cmd = [str(self.python_exe), 'setup.py', 'sdist', 'bdist_wheel']
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("  ✓ Source distribution (sdist) built")
            print("  ✓ Wheel distribution (bdist_wheel) built")
            print("✅ Distribution packages built successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    
    def verify_package_contents(self):
        """Verify the contents of built packages"""
        print("🔍 Verifying package contents...")
        
        dist_dir = self.project_root / 'dist'
        if not dist_dir.exists():
            print("❌ No dist/ directory found")
            return False
        
        # Check for both .tar.gz and .whl files
        tar_files = list(dist_dir.glob('*.tar.gz'))
        whl_files = list(dist_dir.glob('*.whl'))
        
        if not tar_files:
            print("❌ No source distribution (.tar.gz) found")
            return False
        
        if not whl_files:
            print("❌ No wheel distribution (.whl) found")
            return False
        
        version = self.get_current_version()
        expected_prefix = f"mcp_task_orchestrator-{version}"
        
        # Verify source distribution
        tar_file = tar_files[0]
        print(f"  📦 Source: {tar_file.name}")
        
        # Verify wheel
        whl_file = whl_files[0]
        print(f"  📦 Wheel: {whl_file.name}")
        
        # Check wheel contents
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract wheel to check contents
                with zipfile.ZipFile(whl_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                temp_path = Path(temp_dir)
                
                # Check for key files in wheel
                key_files = [
                    'mcp_task_orchestrator/__init__.py',
                    'mcp_task_orchestrator/server.py',
                    'mcp_task_orchestrator_cli/__init__.py',
                ]
                
                wheel_contents = []
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        rel_path = Path(root).relative_to(temp_path) / file
                        wheel_contents.append(str(rel_path))
                
                missing_in_wheel = []
                for key_file in key_files:
                    if not any(key_file in content for content in wheel_contents):
                        missing_in_wheel.append(key_file)
                
                if missing_in_wheel:
                    print(f"❌ Missing files in wheel: {missing_in_wheel}")
                    return False
                
                # Check for new features in wheel
                migration_files = [f for f in wheel_contents if 'auto_migration' in f or 'migration_manager' in f]
                reboot_files = [f for f in wheel_contents if 'reboot_tools' in f or 'restart_manager' in f]
                
                print(f"  ✓ Migration system files: {len(migration_files)} found")
                print(f"  ✓ Reboot system files: {len(reboot_files)} found")
                
        except Exception as e:
            print(f"❌ Error checking wheel contents: {e}")
            return False
        
        print("✅ Package contents verification passed")
        return True
    
    def check_entry_points(self):
        """Verify entry points are correctly configured"""
        print("🎯 Checking entry points...")
        
        try:
            # Parse setup.py to verify entry points
            setup_file = self.project_root / 'setup.py'
            with open(setup_file, 'r') as f:
                content = f.read()
            
            if 'mcp-task-orchestrator=' in content and 'mcp-task-orchestrator-cli=' in content:
                print("  ✓ Server entry point configured")
                print("  ✓ CLI entry point configured")
                print("✅ Entry points check passed")
                return True
            else:
                print("❌ Entry points not properly configured")
                return False
                
        except Exception as e:
            print(f"❌ Error checking entry points: {e}")
            return False
    
    def validate_with_twine(self):
        """Use twine to validate the built packages"""
        print("🔧 Validating packages with twine...")
        
        try:
            cmd = [str(self.python_exe), '-m', 'twine', 'check', 'dist/*']
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Twine validation passed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Twine validation failed: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    
    def test_installation(self):
        """Test installation in a temporary environment"""
        print("🧪 Testing package installation...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                venv_path = Path(temp_dir) / 'test_venv'
                
                # Create temporary virtual environment
                subprocess.run([sys.executable, '-m', 'venv', str(venv_path)], check=True)
                
                # Get the python executable in the test venv
                if os.name == 'nt':  # Windows
                    test_python = venv_path / 'Scripts' / 'python.exe'
                    test_pip = venv_path / 'Scripts' / 'pip.exe'
                else:  # Unix/Linux
                    test_python = venv_path / 'bin' / 'python'
                    test_pip = venv_path / 'bin' / 'pip'
                
                # Install the wheel package
                whl_files = list((self.project_root / 'dist').glob('*.whl'))
                if whl_files:
                    whl_file = whl_files[0]
                    subprocess.run([str(test_pip), 'install', str(whl_file)], check=True)
                    
                    # Test import
                    result = subprocess.run([
                        str(test_python), '-c', 
                        'import mcp_task_orchestrator; print(f"Version: {mcp_task_orchestrator.__version__}")'
                    ], capture_output=True, text=True, check=True)
                    
                    print(f"  ✓ Package imported successfully")
                    print(f"  ✓ {result.stdout.strip()}")
                    
                    # Test CLI import
                    result = subprocess.run([
                        str(test_python), '-c', 
                        'import mcp_task_orchestrator_cli; print("CLI module imported successfully")'
                    ], capture_output=True, text=True, check=True)
                    
                    print(f"  ✓ CLI module imported successfully")
                
            print("✅ Installation test passed")
            return True
            
        except Exception as e:
            print(f"❌ Installation test failed: {e}")
            return False
    
    def generate_release_summary(self):
        """Generate a summary of the release"""
        version = self.get_current_version()
        dist_dir = self.project_root / 'dist'
        
        print("\n" + "="*60)
        print(f"🎉 PyPI Release Preparation Complete - Version {version}")
        print("="*60)
        
        if dist_dir.exists():
            print("\n📦 Distribution Packages:")
            for file in sorted(dist_dir.glob('*')):
                size = file.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"  • {file.name} ({size_mb:.2f} MB)")
        
        print(f"\n🆕 New Features in {version}:")
        print("  • Automatic Database Migration System")
        print("  • In-Context Server Reboot Capabilities")
        print("  • Enhanced Task Lifecycle Management")
        print("  • Improved Error Handling and Recovery")
        print("  • Comprehensive Testing Infrastructure")
        
        print(f"\n📋 Next Steps:")
        print(f"  1. Test upload: python scripts/release/upload.py --test")
        print(f"  2. Production upload: python scripts/release/upload.py")
        print(f"  3. Git tag: git tag v{version} && git push origin v{version}")
        
        print(f"\n🌐 PyPI URLs:")
        print(f"  • Test: https://test.pypi.org/project/mcp-task-orchestrator/{version}/")
        print(f"  • Production: https://pypi.org/project/mcp-task-orchestrator/{version}/")
        
    def run_full_preparation(self):
        """Run the complete preparation process"""
        version = self.get_current_version()
        print(f"🚀 Preparing PyPI Release for version {version}")
        print("="*50)
        
        steps = [
            ("Clean build artifacts", self.clean_build_artifacts),
            ("Validate package structure", self.validate_package_structure),
            ("Check dependencies", self.check_dependencies),
            ("Build distributions", self.build_distributions),
            ("Verify package contents", self.verify_package_contents),
            ("Check entry points", self.check_entry_points),
            ("Validate with twine", self.validate_with_twine),
            ("Test installation", self.test_installation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Release preparation failed at: {step_name}")
                return False
        
        self.generate_release_summary()
        return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Prepare PyPI release for mcp-task-orchestrator')
    parser.add_argument('--quick', action='store_true', help='Skip installation test (faster)')
    args = parser.parse_args()
    
    # Create and run preparation
    prep = PyPIReleasePreparation()
    
    try:
        success = prep.run_full_preparation()
        if success:
            print("\n✨ Release preparation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Release preparation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Preparation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)