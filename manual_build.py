#!/usr/bin/env python3
"""Manual build process for PyPI release 1.6.0"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import re

# Change to project directory
project_root = Path("/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator")
os.chdir(project_root)

def step_1_clean():
    """Clean old build artifacts"""
    print("Step 1: Cleaning build artifacts...")
    
    dirs_to_remove = ['build', 'dist', 'mcp_task_orchestrator.egg-info']
    for dirname in dirs_to_remove:
        dirpath = project_root / dirname
        if dirpath.exists():
            print(f"  Removing {dirname}/...")
            shutil.rmtree(dirpath)
        else:
            print(f"  {dirname}/ not found (OK)")
    
    print("✅ Cleanup completed\n")

def step_2_verify_version():
    """Verify version is correctly set"""
    print("Step 2: Verifying version...")
    
    # Check setup.py
    with open('setup.py', 'r') as f:
        setup_content = f.read()
        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', setup_content)
        if version_match:
            setup_version = version_match.group(1)
            print(f"  setup.py version: {setup_version}")
        else:
            print("  ❌ No version found in setup.py")
            return False
    
    # Check __init__.py
    with open('mcp_task_orchestrator/__init__.py', 'r') as f:
        init_content = f.read()
        version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', init_content)
        if version_match:
            init_version = version_match.group(1)
            print(f"  __init__.py version: {init_version}")
        else:
            print("  ❌ No version found in __init__.py")
            return False
    
    if setup_version == init_version == "1.6.0":
        print("✅ Version verification passed\n")
        return True
    else:
        print("❌ Version mismatch!")
        return False

def step_3_verify_structure():
    """Verify package structure"""
    print("Step 3: Verifying package structure...")
    
    critical_files = [
        'setup.py',
        'requirements.txt', 
        'README.md',
        'LICENSE',
        'mcp_task_orchestrator/__init__.py',
        'mcp_task_orchestrator/server.py',
        'mcp_task_orchestrator_cli/__init__.py',
        'mcp_task_orchestrator_cli/cli.py',
    ]
    
    new_feature_files = [
        'mcp_task_orchestrator/db/auto_migration.py',
        'mcp_task_orchestrator/db/migration_manager.py',
        'mcp_task_orchestrator/server/reboot_tools.py',
        'mcp_task_orchestrator/server/restart_manager.py',
    ]
    
    all_files = critical_files + new_feature_files
    missing_files = []
    
    for file_path in all_files:
        if (project_root / file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ❌ MISSING: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ {len(missing_files)} files missing!")
        return False
    else:
        print("✅ Package structure verification passed\n")
        return True

def step_4_build():
    """Build the distribution packages"""
    print("Step 4: Building distribution packages...")
    
    try:
        # Build source distribution and wheel
        print("  Running: python setup.py sdist bdist_wheel")
        result = subprocess.run(
            [sys.executable, 'setup.py', 'sdist', 'bdist_wheel'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("  ✓ Build completed successfully")
            
            # List built files
            dist_dir = project_root / 'dist'
            if dist_dir.exists():
                print("  Built packages:")
                for file in dist_dir.iterdir():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"    • {file.name} ({size_mb:.2f} MB)")
            
            print("✅ Build completed\n")
            return True
        else:
            print("❌ Build failed!")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def step_5_verify_packages():
    """Verify the built packages"""
    print("Step 5: Verifying built packages...")
    
    dist_dir = project_root / 'dist'
    if not dist_dir.exists():
        print("❌ No dist/ directory found")
        return False
    
    # Check for required file types
    tar_files = list(dist_dir.glob('*.tar.gz'))
    whl_files = list(dist_dir.glob('*.whl'))
    
    if not tar_files:
        print("❌ No source distribution (.tar.gz) found")
        return False
    
    if not whl_files:
        print("❌ No wheel distribution (.whl) found")
        return False
    
    print(f"  ✓ Source distribution: {tar_files[0].name}")
    print(f"  ✓ Wheel distribution: {whl_files[0].name}")
    
    # Verify naming
    expected_prefix = "mcp_task_orchestrator-1.6.0"
    for file in tar_files + whl_files:
        if not file.name.startswith(expected_prefix):
            print(f"❌ Unexpected filename: {file.name}")
            return False
    
    print("✅ Package verification passed\n")
    return True

def step_6_entry_points():
    """Verify entry points are configured"""
    print("Step 6: Verifying entry points...")
    
    with open('setup.py', 'r') as f:
        content = f.read()
    
    if 'mcp-task-orchestrator=' in content and 'mcp-task-orchestrator-cli=' in content:
        print("  ✓ Server entry point: mcp-task-orchestrator")
        print("  ✓ CLI entry point: mcp-task-orchestrator-cli")
        print("✅ Entry points verification passed\n")
        return True
    else:
        print("❌ Entry points not found in setup.py")
        return False

def generate_summary():
    """Generate release summary"""
    print("🎉 PyPI Release 1.6.0 Preparation Complete!")
    print("=" * 50)
    
    dist_dir = project_root / 'dist'
    if dist_dir.exists():
        print("\n📦 Distribution Packages Ready:")
        for file in sorted(dist_dir.iterdir()):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  • {file.name} ({size_mb:.2f} MB)")
    
    print("\n🆕 New Features in v1.6.0:")
    print("  • Automatic Database Migration System")
    print("  • In-Context Server Reboot Capabilities") 
    print("  • Enhanced Task Lifecycle Management")
    print("  • Improved Error Handling and Recovery")
    
    print("\n📋 Next Steps:")
    print("  1. Test upload:")
    print("     python scripts/release/upload.py --test")
    print("  2. Production upload:")
    print("     python scripts/release/upload.py")
    print("  3. Create git tag:")
    print("     git tag v1.6.0 && git push origin v1.6.0")
    
    print("\n🌐 Package URLs:")
    print("  • Test: https://test.pypi.org/project/mcp-task-orchestrator/1.6.0/")
    print("  • Production: https://pypi.org/project/mcp-task-orchestrator/1.6.0/")

def main():
    """Run the complete preparation process"""
    print("🚀 MCP Task Orchestrator - PyPI Release 1.6.0 Preparation")
    print("=" * 60)
    
    steps = [
        ("Clean build artifacts", step_1_clean),
        ("Verify version", step_2_verify_version),
        ("Verify package structure", step_3_verify_structure), 
        ("Build packages", step_4_build),
        ("Verify built packages", step_5_verify_packages),
        ("Verify entry points", step_6_entry_points),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ FAILED at: {step_name}")
            print("Release preparation aborted.")
            return False
    
    generate_summary()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Preparation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)