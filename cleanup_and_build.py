#!/usr/bin/env python3
"""
Final PyPI build script for MCP Task Orchestrator v1.6.0
This script will clean old artifacts and build new distribution packages
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Project configuration
PROJECT_ROOT = Path("/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator")
VERSION = "1.6.0"

def cleanup_old_builds():
    """Remove old build artifacts"""
    print("🧹 Cleaning old build artifacts...")
    
    cleanup_dirs = [
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "dist", 
        PROJECT_ROOT / "mcp_task_orchestrator.egg-info"
    ]
    
    for dir_path in cleanup_dirs:
        if dir_path.exists():
            print(f"  Removing {dir_path.name}/...")
            shutil.rmtree(dir_path)
        else:
            print(f"  {dir_path.name}/ not found (OK)")
    
    print("✅ Cleanup completed")

def verify_version():
    """Verify version is set correctly"""
    print("🔍 Verifying version...")
    
    # Check setup.py
    setup_file = PROJECT_ROOT / "setup.py"
    with open(setup_file, 'r') as f:
        content = f.read()
        if f'version="{VERSION}"' in content:
            print(f"  ✅ setup.py version: {VERSION}")
        else:
            print(f"  ❌ setup.py version incorrect")
            return False
    
    # Check __init__.py
    init_file = PROJECT_ROOT / "mcp_task_orchestrator" / "__init__.py"
    with open(init_file, 'r') as f:
        content = f.read()
        if f'__version__ = "{VERSION}"' in content:
            print(f"  ✅ __init__.py version: {VERSION}")
        else:
            print(f"  ❌ __init__.py version incorrect")
            return False
    
    print("✅ Version verification passed")
    return True

def verify_structure():
    """Verify package structure"""
    print("📂 Verifying package structure...")
    
    critical_files = [
        "setup.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "mcp_task_orchestrator/__init__.py",
        "mcp_task_orchestrator/server.py",
        "mcp_task_orchestrator_cli/__init__.py"
    ]
    
    new_features = [
        "mcp_task_orchestrator/db/auto_migration.py",
        "mcp_task_orchestrator/db/migration_manager.py", 
        "mcp_task_orchestrator/server/reboot_tools.py",
        "mcp_task_orchestrator/server/restart_manager.py"
    ]
    
    missing_files = []
    
    for file_path in critical_files + new_features:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ {len(missing_files)} files missing!")
        return False
    
    print("✅ Package structure verified")
    return True

def build_packages():
    """Build the distribution packages"""
    print("📦 Building distribution packages...")
    
    # Change to project directory
    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)
    
    try:
        # Build command
        cmd = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
        print(f"  Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("  ✅ Build completed successfully")
            return True
        else:
            print(f"  ❌ Build failed (exit code {result.returncode})")
            print(f"  Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Build timed out")
        return False
    except Exception as e:
        print(f"  ❌ Build error: {e}")
        return False
    finally:
        os.chdir(original_cwd)

def verify_build_output():
    """Verify the build output"""
    print("🔍 Verifying build output...")
    
    dist_dir = PROJECT_ROOT / "dist"
    
    if not dist_dir.exists():
        print("  ❌ No dist/ directory found")
        return False
    
    files = list(dist_dir.iterdir())
    if not files:
        print("  ❌ dist/ directory is empty")
        return False
    
    print(f"  📁 Found {len(files)} files:")
    
    source_dists = []
    wheel_dists = []
    
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"    • {file_path.name} ({size_mb:.2f} MB)")
        
        if file_path.name.endswith('.tar.gz'):
            source_dists.append(file_path)
        elif file_path.name.endswith('.whl'):
            wheel_dists.append(file_path)
    
    # Verify expected files exist
    if not source_dists:
        print("  ❌ No source distribution (.tar.gz) found")
        return False
    
    if not wheel_dists:
        print("  ❌ No wheel distribution (.whl) found") 
        return False
    
    # Verify version in filenames
    version_correct = all(VERSION in f.name for f in files)
    if not version_correct:
        print("  ⚠️  Warning: Not all files contain correct version")
    
    print("✅ Build output verified")
    return True

def generate_final_report():
    """Generate final report"""
    print("\n" + "="*60)
    print("🎉 MCP Task Orchestrator v1.6.0 - PyPI Release Ready!")
    print("="*60)
    
    dist_dir = PROJECT_ROOT / "dist"
    if dist_dir.exists():
        files = list(dist_dir.iterdir())
        print(f"\n📦 Distribution packages ({len(files)} files):")
        for file_path in sorted(files):
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  • {file_path.name} ({size_mb:.2f} MB)")
    
    print(f"\n🆕 New features in v{VERSION}:")
    print("  • Automatic Database Migration System")
    print("  • In-Context Server Reboot Capabilities")
    print("  • Enhanced Task Lifecycle Management") 
    print("  • Improved Error Handling and Recovery")
    print("  • Comprehensive Testing Infrastructure")
    
    print(f"\n📋 Next steps:")
    print("  1. Test upload to TestPyPI:")
    print("     python scripts/release/upload.py --test")
    print("  2. Production upload to PyPI:")
    print("     python scripts/release/upload.py")
    print("  3. Create and push git tag:")
    print(f"     git tag v{VERSION} && git push origin v{VERSION}")
    
    print(f"\n🌐 Package URLs after upload:")
    print(f"  • Test: https://test.pypi.org/project/mcp-task-orchestrator/{VERSION}/")
    print(f"  • Production: https://pypi.org/project/mcp-task-orchestrator/{VERSION}/")

def main():
    """Main execution function"""
    print("🚀 MCP Task Orchestrator PyPI Release Preparation")
    print(f"📦 Version: {VERSION}")
    print("=" * 60)
    
    # Execute all steps
    steps = [
        ("Cleanup old builds", cleanup_old_builds),
        ("Verify version", verify_version),
        ("Verify structure", verify_structure),
        ("Build packages", build_packages),
        ("Verify build output", verify_build_output),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            if not step_func():
                print(f"\n❌ Failed at step: {step_name}")
                return False
        except Exception as e:
            print(f"\n💥 Error in step '{step_name}': {e}")
            return False
    
    generate_final_report()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print(f"\n✨ PyPI release preparation completed successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ PyPI release preparation failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Process cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)