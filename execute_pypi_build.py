#!/usr/bin/env python3
"""
Execute PyPI build for MCP Task Orchestrator v1.6.0
Run this script to build the distribution packages
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    # Set working directory to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 MCP Task Orchestrator v1.6.0 - PyPI Build Execution")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    
    # Step 1: Clean old build artifacts
    print("\n🧹 Step 1: Cleaning old build artifacts...")
    
    cleanup_dirs = ['build', 'dist', 'mcp_task_orchestrator.egg-info']
    for dirname in cleanup_dirs:
        dirpath = Path(dirname)
        if dirpath.exists():
            print(f"  Removing {dirname}/...")
            shutil.rmtree(dirpath)
        else:
            print(f"  {dirname}/ not found (OK)")
    
    print("  ✅ Cleanup completed")
    
    # Step 2: Execute build
    print("\n📦 Step 2: Building distribution packages...")
    print("  Command: python setup.py sdist bdist_wheel")
    
    try:
        result = subprocess.run(
            [sys.executable, 'setup.py', 'sdist', 'bdist_wheel'],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("  ✅ Build successful!")
            
            # Show build output (last few lines)
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                if len(stdout_lines) > 5:
                    print("  Build output (last 5 lines):")
                    for line in stdout_lines[-5:]:
                        if line.strip():
                            print(f"    {line}")
            
        else:
            print(f"  ❌ Build failed (exit code: {result.returncode})")
            if result.stderr:
                print(f"  Error output:")
                for line in result.stderr.split('\n')[:10]:  # First 10 lines
                    if line.strip():
                        print(f"    {line}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Build timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Build error: {e}")
        return False
    
    # Step 3: Verify build results
    print("\n🔍 Step 3: Verifying build results...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("  ❌ No dist/ directory created")
        return False
    
    files = list(dist_dir.iterdir())
    if not files:
        print("  ❌ dist/ directory is empty")
        return False
    
    print(f"  📁 Found {len(files)} distribution files:")
    
    source_dists = []
    wheel_dists = []
    
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"    • {file_path.name} ({size_mb:.2f} MB)")
        
        if file_path.name.endswith('.tar.gz'):
            source_dists.append(file_path)
        elif file_path.name.endswith('.whl'):
            wheel_dists.append(file_path)
    
    # Validation
    if not source_dists:
        print("  ❌ No source distribution (.tar.gz) found")
        return False
    
    if not wheel_dists:
        print("  ❌ No wheel distribution (.whl) found")
        return False
    
    # Check version in filenames
    version_1_6_0_files = [f for f in files if '1.6.0' in f.name]
    if len(version_1_6_0_files) != len(files):
        print("  ⚠️  Warning: Not all files contain version 1.6.0")
        for f in files:
            if '1.6.0' not in f.name:
                print(f"    ❓ {f.name}")
    
    print("  ✅ Build verification passed")
    
    # Step 4: Final summary
    print("\n🎉 PyPI Build Complete for v1.6.0!")
    print("=" * 40)
    print(f"📦 Packages built: {len(files)}")
    print(f"📄 Source distributions: {len(source_dists)}")
    print(f"🎡 Wheel distributions: {len(wheel_dists)}")
    
    print("\n🆕 New Features in v1.6.0:")
    print("  • Automatic Database Migration System")
    print("  • In-Context Server Reboot Capabilities")
    print("  • Enhanced Task Lifecycle Management")
    print("  • Improved Error Handling and Recovery")
    
    print("\n📋 Next Steps:")
    print("  1. Validate packages:")
    print("     python -m twine check dist/*")
    print("  2. Test upload (optional):")
    print("     python scripts/release/upload.py --test")
    print("  3. Production upload:")
    print("     python scripts/release/upload.py")
    print("  4. Create git tag:")
    print("     git tag v1.6.0 && git push origin v1.6.0")
    
    print(f"\n✨ Ready for PyPI upload!")
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            print("\n🎊 All done! Packages are ready for PyPI upload.")
            sys.exit(0)
        else:
            print("\n❌ Build failed. Please check the errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)