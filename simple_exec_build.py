exec("""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
project_path = "/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator"
os.chdir(project_path)

print("=== MCP Task Orchestrator v1.6.0 Build ===")
print(f"Working directory: {os.getcwd()}")

# Step 1: Clean
print("\\n1. Cleaning artifacts...")
for dirname in ['build', 'dist', 'mcp_task_orchestrator.egg-info']:
    path = Path(dirname)
    if path.exists():
        shutil.rmtree(path)
        print(f"   Removed {dirname}/")
    else:
        print(f"   {dirname}/ not found")

# Step 2: Build
print("\\n2. Building distribution packages...")
cmd = [sys.executable, 'setup.py', 'sdist', 'bdist_wheel']
proc = subprocess.run(cmd, capture_output=True, text=True)

if proc.returncode == 0:
    print("   ✅ Build completed successfully")
    
    # Step 3: Verify
    print("\\n3. Verification...")
    dist_path = Path('dist')
    if dist_path.exists():
        files = list(dist_path.iterdir())
        print(f"   Found {len(files)} distribution files:")
        
        for file in files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"     • {file.name} ({size_mb:.1f} MB)")
        
        # Check types
        has_source = any(f.name.endswith('.tar.gz') for f in files)
        has_wheel = any(f.name.endswith('.whl') for f in files)
        
        if has_source and has_wheel:
            print("   ✅ Both source and wheel distributions present")
            print("\\n🎉 PyPI release packages ready for v1.6.0!")
            print("\\nNext steps:")
            print("   • Test: python scripts/release/upload.py --test")
            print("   • Upload: python scripts/release/upload.py")
        else:
            print("   ❌ Missing distribution types")
    else:
        print("   ❌ No dist/ directory created")
else:
    print(f"   ❌ Build failed: {proc.stderr}")

print("\\n=== Build process complete ===")
""")