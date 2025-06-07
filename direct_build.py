#!/usr/bin/env python3
"""Direct build execution for 1.6.0 release"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    # Set working directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🚀 MCP Task Orchestrator v1.6.0 - PyPI Build Process")
    print("=" * 60)
    print(f"Working directory: {project_root}")
    
    # Step 1: Clean old artifacts
    print("\n🧹 Step 1: Cleaning old build artifacts...")
    clean_dirs = ['build', 'dist', 'mcp_task_orchestrator.egg-info']
    
    for dir_name in clean_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"  ✅ Removed {dir_name}/")
            except Exception as e:
                print(f"  ❌ Failed to remove {dir_name}/: {e}")
                return False
        else:
            print(f"  ℹ️  {dir_name}/ not found (OK)")
    
    # Step 2: Verify key files exist
    print("\n🔍 Step 2: Verifying package structure...")
    key_files = [
        'setup.py',
        'requirements.txt',
        'README.md',
        'mcp_task_orchestrator/__init__.py',
        'mcp_task_orchestrator/server.py',
        'mcp_task_orchestrator/db/auto_migration.py',
        'mcp_task_orchestrator/server/reboot_tools.py'
    ]
    
    missing_files = []
    for file_path in key_files:
        if (project_root / file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ MISSING: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Cannot proceed: {len(missing_files)} critical files missing!")
        return False
    
    # Step 3: Build packages
    print("\n📦 Step 3: Building distribution packages...")
    print("  Command: python setup.py sdist bdist_wheel")
    
    try:
        # Execute the build command
        result = subprocess.run(
            [sys.executable, 'setup.py', 'sdist', 'bdist_wheel'],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("  ✅ Build command completed successfully")
        else:
            print(f"  ❌ Build command failed with return code {result.returncode}")
            print(f"  STDOUT: {result.stdout}")
            print(f"  STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Build command timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Build command failed with exception: {e}")
        return False
    
    # Step 4: Verify build output
    print("\n🔍 Step 4: Verifying build output...")
    dist_dir = project_root / 'dist'
    
    if not dist_dir.exists():
        print("  ❌ No dist/ directory created")
        return False
    
    # List all files in dist
    dist_files = list(dist_dir.iterdir())
    if not dist_files:
        print("  ❌ dist/ directory is empty")
        return False
    
    print(f"  📁 Found {len(dist_files)} files in dist/:")
    
    # Categorize files
    source_dists = []
    wheel_dists = []
    other_files = []
    
    for file_path in dist_files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"    • {file_path.name} ({size_mb:.2f} MB)")
        
        if file_path.name.endswith('.tar.gz'):
            source_dists.append(file_path)
        elif file_path.name.endswith('.whl'):
            wheel_dists.append(file_path)
        else:
            other_files.append(file_path)
    
    # Validate expected files
    if not source_dists:
        print("  ❌ No source distribution (.tar.gz) found")
        return False
    
    if not wheel_dists:
        print("  ❌ No wheel distribution (.whl) found")
        return False
    
    # Check version in filenames
    version_1_6_0_count = sum(1 for f in dist_files if '1.6.0' in f.name)
    if version_1_6_0_count != len(dist_files):
        print(f"  ⚠️  Warning: Not all files contain version 1.6.0")
        for f in dist_files:
            if '1.6.0' not in f.name:
                print(f"    ❓ {f.name}")
    
    print("  ✅ Build output verification passed")
    
    # Step 5: Summary
    print("\n🎉 PyPI Release Preparation Complete!")
    print("=" * 60)
    print(f"📦 Version: 1.6.0")
    print(f"📁 Packages: {len(dist_files)} files ready")
    print(f"📄 Source distributions: {len(source_dists)}")
    print(f"🎡 Wheel distributions: {len(wheel_dists)}")
    
    if other_files:
        print(f"❓ Other files: {len(other_files)}")
    
    print("\n🆕 New Features in v1.6.0:")
    print("  • Automatic Database Migration System")
    print("  • In-Context Server Reboot Capabilities")
    print("  • Enhanced Task Lifecycle Management")
    print("  • Improved Error Handling and Recovery")
    
    print("\n📋 Next Steps:")
    print("  1. Test upload to TestPyPI:")
    print("     python scripts/release/upload.py --test")
    print("  2. Production upload to PyPI:")
    print("     python scripts/release/upload.py")
    print("  3. Create git tag:")
    print("     git tag v1.6.0 && git push origin v1.6.0")
    
    print("\n🌐 Package URLs:")
    print("  • Test: https://test.pypi.org/project/mcp-task-orchestrator/1.6.0/")
    print("  • Production: https://pypi.org/project/mcp-task-orchestrator/1.6.0/")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n✨ All steps completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Build process failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)