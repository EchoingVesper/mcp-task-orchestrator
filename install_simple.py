#!/usr/bin/env python3
"""
Simple Bundled Installation using Virtual Environment

This creates a local virtual environment for the MCP Task Orchestrator,
which is simpler and more reliable than embedded Python.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_step(step, message):
    """Print a step message."""
    print(f"\n[{step}] {message}")

def main():
    """Main installation function."""
    project_dir = Path(__file__).parent.absolute()
    venv_path = project_dir / "venv"
    scripts_path = project_dir / "launch_scripts"
    
    print_header("MCP Task Orchestrator - Virtual Environment Installation")
    print(f"Project directory: {project_dir}")
    print(f"Virtual environment: {venv_path}")
    
    # Clean up existing installation
    if venv_path.exists():
        print_step("CLEANUP", "Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    if scripts_path.exists():
        import shutil
        shutil.rmtree(scripts_path)
    
    # Create virtual environment
    print_step("VENV", "Creating virtual environment...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
            cwd=str(project_dir)
        )
        
        if result.returncode == 0:
            print("[OK] Virtual environment created successfully")
        else:
            print(f"[ERROR] Virtual environment creation failed: {result.stderr}")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Failed to create virtual environment: {e}")
        return 1
    
    # Get Python executable path
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"
    
    if not python_exe.exists():
        print(f"[ERROR] Python executable not found at {python_exe}")
        return 1
    
    print(f"[OK] Virtual environment Python: {python_exe}")
