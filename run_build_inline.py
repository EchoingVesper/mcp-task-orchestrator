#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Inline execution
if __name__ == "__main__":
    # Set paths
    project_root = Path("/mnt/e/My Work/Programming/MCP Servers/mcp-task-orchestrator")
    
    # Change directory
    original_cwd = os.getcwd()
    os.chdir(project_root)
    
    try:
        print("🚀 Building MCP Task Orchestrator v1.6.0")
        print(f"Working in: {os.getcwd()}")
        
        # Clean old builds
        print("\n🧹 Cleaning old builds...")
        for dirname in ['build', 'dist', 'mcp_task_orchestrator.egg-info']:
            dirpath = Path(dirname)
            if dirpath.exists():
                shutil.rmtree(dirpath)
                print(f"  Removed {dirname}/")
        
        # Execute build
        print("\n📦 Building packages...")
        cmd = [sys.executable, 'setup.py', 'sdist', 'bdist_wheel']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Build successful!")
            
            # Check results
            dist_dir = Path('dist')
            if dist_dir.exists():
                files = list(dist_dir.iterdir())
                print(f"\n📋 Built {len(files)} packages:")
                for f in files:
                    size = f.stat().st_size / (1024*1024)
                    print(f"  • {f.name} ({size:.2f} MB)")
                
                print(f"\n✨ Release packages ready!")
                print(f"📍 Location: {dist_dir.absolute()}")
                
            else:
                print("❌ No dist directory found")
                
        else:
            print(f"❌ Build failed!")
            print(f"Error: {result.stderr}")
            
    finally:
        os.chdir(original_cwd)
    
print("Done.")