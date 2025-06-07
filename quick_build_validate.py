#!/usr/bin/env python3
"""Quick build and validation script for PyPI release"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Set working directory
project_root = Path("/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator")
os.chdir(project_root)

def clean_artifacts():
    """Clean old build artifacts"""
    print("Cleaning build artifacts...")
    for dirname in ['build', 'dist', 'mcp_task_orchestrator.egg-info']:
        dirpath = project_root / dirname
        if dirpath.exists():
            shutil.rmtree(dirpath)
            print(f"Removed {dirname}/")

def get_version():
    """Get version from setup.py"""
    import re
    with open('setup.py', 'r') as f:
        content = f.read()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
    return "unknown"

def build_packages():
    """Build the packages"""
    print("Building packages...")
    try:
        result = subprocess.run([sys.executable, 'setup.py', 'sdist', 'bdist_wheel'], 
                              capture_output=True, text=True, check=True)
        print("Build successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

def validate_packages():
    """Basic validation of built packages"""
    dist_dir = project_root / 'dist'
    if not dist_dir.exists():
        print("No dist directory found")
        return False
    
    files = list(dist_dir.glob('*'))
    tar_files = [f for f in files if f.suffix == '.gz']
    whl_files = [f for f in files if f.suffix == '.whl']
    
    print(f"Found {len(tar_files)} source distributions")
    print(f"Found {len(whl_files)} wheel distributions")
    
    for f in files:
        print(f"  {f.name}")
    
    return len(tar_files) > 0 and len(whl_files) > 0

def main():
    version = get_version()
    print(f"Preparing PyPI release for version {version}")
    print("=" * 50)
    
    clean_artifacts()
    
    if build_packages():
        if validate_packages():
            print("\n✅ Release preparation successful!")
            print(f"\nNext steps:")
            print(f"1. Test upload: python scripts/release/upload.py --test")
            print(f"2. Production upload: python scripts/release/upload.py")
        else:
            print("❌ Package validation failed")
    else:
        print("❌ Build failed")

if __name__ == '__main__':
    main()