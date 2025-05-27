#!/usr/bin/env python3
"""
Test the MCP Task Orchestrator server with system Python (Claude Desktop's Python).
"""

import subprocess
import sys
import time
from pathlib import Path

def test_system_python_server():
    """Test that the server works with Claude Desktop's Python."""
    print("Testing MCP Task Orchestrator with Claude Desktop's Python...")
    print("=" * 60)
    
    # Get project directory
    project_dir = Path(__file__).parent.absolute()
    
    # Define the system Python path
    system_python = r"C:\Program Files\Python313\python.exe"
    
    try:
        # Start the server process using system Python
        print(f"Starting server with: {system_python}")
        print(f"Working directory: {project_dir}")
        print(f"Command: python -m mcp_task_orchestrator.server")
        
        process = subprocess.Popen(
            [system_python, "-m", "mcp_task_orchestrator.server"],
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        print("\nWaiting for server startup...")
        time.sleep(3)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("[SUCCESS] Server started successfully with system Python!")
            print("The server is running and ready for Claude Desktop connections.")
            
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

def main():
    """Run the test."""
    success = test_system_python_server()
    
    if success:
        print("\n" + "="*60)
        print("[READY] MCP Task Orchestrator is ready for Claude Desktop!")
        print("\nNext steps:")
        print("1. Restart Claude Desktop")
        print("2. The task-orchestrator should connect successfully")
        print("3. Check the logs for successful connection")
        return 0
    else:
        print("\n" + "="*60)
        print("[ERROR] There are still issues with the server setup.")
        print("Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
