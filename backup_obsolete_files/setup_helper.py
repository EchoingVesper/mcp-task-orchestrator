#!/usr/bin/env python3
"""
MCP Task Orchestrator Setup and Validation Script
"""
import json
import os
import subprocess
import sys
from pathlib import Path

def main():
    print("MCP Task Orchestrator Setup Helper")
    print("=" * 50)
    
    # Test server execution
    print("1. Testing server execution...")
    server_path = Path(__file__).parent / "src" / "main.py"
    
    try:
        process = subprocess.Popen([
            sys.executable, str(server_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           cwd=Path(__file__).parent)
        
        try:
            stdout, stderr = process.communicate(timeout=2)
            print("   ERROR: Server exited unexpectedly")
            if stderr:
                print(f"   Error details: {stderr.decode()}")
            server_ok = False
        except subprocess.TimeoutExpired:
            process.kill()
            print("   SUCCESS: Server starts and runs correctly")
            server_ok = True
            
    except Exception as e:
        print(f"   ERROR: Failed to start server: {e}")
        server_ok = False
    
    # Check configuration files
    print("\n2. Configuration files available:")
    config_dir = Path(__file__).parent
    
    configs = [
        ("claude_desktop_config_recommended.json", "Recommended config (uses 'python' command)"),
        ("claude_desktop_config_fullpath.json", "Full path config (explicit Python path)"),
    ]
    
    for config_file, description in configs:
        config_path = config_dir / config_file
        if config_path.exists():
            print(f"   FOUND: {config_file}")
            print(f"          {description}")
        else:
            print(f"   MISSING: {config_file}")
    
    # Instructions
    print("\n3. Setup Instructions:")
    print("   a) Copy one of the config files to your Claude Desktop config:")
    print("      Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("      macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("      Linux: ~/.config/Claude/claude_desktop_config.json")
    print("   b) Restart Claude Desktop completely")
    print("   c) Your server should appear as 'task-orchestrator' in Claude")
    
    # Test MCP CLI installation option
    print("\n4. Alternative: Use MCP CLI (recommended):")
    print("   Install MCP CLI: pip install 'mcp[cli]'")
    print("   Then run: mcp install src/main.py --name 'Task Orchestrator'")
    print("   This automatically configures Claude Desktop")
    
    print("\n" + "=" * 50)
    if server_ok:
        print("RESULT: Server is working! Configuration issue likely.")
        print("Follow the setup instructions above.")
    else:
        print("RESULT: Server has issues. Check error messages.")
    
    return server_ok

if __name__ == "__main__":
    success = main()
    print(f"\nStatus: {'READY' if success else 'NEEDS_FIXING'}")
    sys.exit(0 if success else 1)
