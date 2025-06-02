#!/usr/bin/env python3
"""
Universal launcher for MCP Task Orchestrator CLI.
Automatically detects OS and activates the appropriate virtual environment.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def find_venv_python():
    """Find the Python executable in the virtual environment."""
    project_root = Path(__file__).parent.absolute()
    
    # Possible virtual environment names
    venv_names = ['venv_mcp', 'venv', '.venv']
    
    for venv_name in venv_names:
        venv_path = project_root / venv_name
        
        if not venv_path.exists():
            continue
            
        # Check for Windows-style Scripts directory
        windows_python = venv_path / 'Scripts' / 'python.exe'
        if windows_python.exists():
            return str(windows_python)
            
        # Check for Unix-style bin directory
        unix_python = venv_path / 'bin' / 'python'
        if unix_python.exists():
            return str(unix_python)
            
        # Check for Unix-style with python3
        unix_python3 = venv_path / 'bin' / 'python3'
        if unix_python3.exists():
            return str(unix_python3)
    
    return None

def main():
    """Launch the MCP Task Orchestrator CLI with the appropriate Python."""
    # Find the virtual environment Python
    venv_python = find_venv_python()
    
    if not venv_python:
        print("Error: Virtual environment not found!")
        print("Please run 'python run_installer.py' or create a virtual environment first.")
        sys.exit(1)
    
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Prepare the command
    cmd = [venv_python, '-m', 'mcp_task_orchestrator_cli.cli']
    
    # Add any additional arguments passed to this launcher
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # Set the working directory
    os.chdir(str(project_root))
    
    # Launch the CLI
    try:
        # Use subprocess.run for better cross-platform compatibility
        result = subprocess.run(cmd, cwd=str(project_root))
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\nCLI stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching CLI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()