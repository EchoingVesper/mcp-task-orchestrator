#!/usr/bin/env python3
"""Execute the build process step by step"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Set working directory
project_root = Path("/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator")
os.chdir(project_root)

print("Executing PyPI build for version 1.6.0...")
print("Working directory:", os.getcwd())

# Step 1: Clean old artifacts
print("\n1. Cleaning old build artifacts...")
dirs_to_clean = ['build', 'dist', 'mcp_task_orchestrator.egg-info']
for dirname in dirs_to_clean:
    dirpath = project_root / dirname
    if dirpath.exists():
        print(f"   Removing {dirname}/")
        shutil.rmtree(dirpath)
    else:
        print(f"   {dirname}/ not found (OK)")

# Step 2: Build packages
print("\n2. Building packages...")
try:
    print("   Running: python setup.py sdist bdist_wheel")
    result = subprocess.run([
        sys.executable, 'setup.py', 'sdist', 'bdist_wheel'
    ], cwd=project_root, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ Build successful!")
    else:
        print(f"   ❌ Build failed: {result.stderr}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Build error: {e}")
    sys.exit(1)

# Step 3: Verify results
print("\n3. Verifying build results...")
dist_dir = project_root / 'dist'
if dist_dir.exists():
    files = list(dist_dir.iterdir())
    print(f"   Found {len(files)} files in dist/:")
    for file in files:
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"   • {file.name} ({size_mb:.2f} MB)")
        
    # Check for expected files
    tar_files = [f for f in files if f.suffix == '.gz']
    whl_files = [f for f in files if f.suffix == '.whl']
    
    if tar_files and whl_files:
        print("   ✅ Both source and wheel distributions created!")
    else:
        print("   ❌ Missing expected distribution types")
        
else:
    print("   ❌ No dist/ directory found!")

print("\n🎉 Build process completed!")
print("Next: Use scripts/release/upload.py to upload to PyPI")