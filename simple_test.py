#!/usr/bin/env python3
"""
Simple test script to verify MCP Task Orchestrator server functionality.
"""

import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

async def test_server_startup():
    """Test that the server can start without errors."""
    print("Testing MCP Task Orchestrator server startup...")
    
    # Get project directory
    project_dir = Path(__file__).parent.absolute()
    
    try:
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "-m", "mcp_task_orchestrator.server"],
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("[OK] Server started successfully and is running")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            return True
        else:
            # Process exited, check for errors
            stdout, stderr = process.communicate()
            print(f"[ERROR] Server exited with return code: {process.returncode}")
            if stderr:
                print(f"Error output: {stderr}")
            if stdout:
                print(f"Standard output: {stdout}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("Testing dependencies...")
    
    required_packages = [
        "mcp",
        "pydantic", 
        "jinja2",
        "yaml",
        "aiofiles"
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[MISSING] {package}")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("MCP Task Orchestrator - Server Test")
    print("=" * 50)
    
    # Test dependencies
    deps_ok = test_dependencies()
    print()
    
    if not deps_ok:
        print("[ERROR] Some dependencies are missing. Please install requirements:")
        print("pip install -r requirements.txt")
        return 1
    
    # Test server startup
    server_ok = asyncio.run(test_server_startup())
    print()
    
    if server_ok:
        print("[SUCCESS] All tests passed! The MCP Task Orchestrator is ready to use.")
        print("\nNext steps:")
        print("1. Restart Claude Desktop")
        print("2. The 'task-orchestrator' should appear in available MCP servers")
        print("3. You should see these tools available:")
        print("   - orchestrator_plan_task")
        print("   - orchestrator_execute_subtask") 
        print("   - orchestrator_complete_subtask")
        print("   - orchestrator_synthesize_results")
        print("   - orchestrator_get_status")
        return 0
    else:
        print("[ERROR] Server test failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
