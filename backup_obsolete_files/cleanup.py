#!/usr/bin/env python3
"""
Cleanup script for the MCP Task Orchestrator project.

This script removes obsolete files that are no longer needed in the restructured project.
"""

import os
import shutil
from pathlib import Path
import sys

def main():
    """Clean up obsolete files from the project directory."""
    print("MCP Task Orchestrator - Project Cleanup")
    print("=" * 50)
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    print(f"Project directory: {current_dir}")
    
    # Files to remove
    files_to_remove = [
        # Old configuration files
        "claude_desktop_config.json",
        "claude_desktop_config_fullpath.json",
        "claude_desktop_config_no_spaces.json",
        "claude_desktop_config_recommended.json",
        "test_config.json",
        "test_config_fullpath.json",
        
        # Old test scripts
        "simple_test.py",
        "test_import.py",
        "test_imports.bat",
        "test_mcp_imports.py",
        "test_server.py",
        "test_server_import.py",
        "test_server_simple.py",
        "setup_helper.py",
        "validate_claude_config.py",
        
        # Old implementation files
        "IMPLEMENTATION_SUMMARY.md",
        
        # Database file (should be regenerated)
        "task_orchestrator.db"
    ]
    
    # Directories to remove
    dirs_to_remove = [
        # Old source directory
        "src",
        
        # Generated directory
        "mcp_task_orchestrator.egg-info"
    ]
    
    # Create a backup directory
    backup_dir = current_dir / "backup_obsolete_files"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")
    
    # Move files to backup directory
    for file_name in files_to_remove:
        file_path = current_dir / file_name
        if file_path.exists():
            try:
                shutil.copy2(file_path, backup_dir / file_name)
                os.remove(file_path)
                print(f"Removed file: {file_name}")
            except Exception as e:
                print(f"Error removing file {file_name}: {e}")
    
    # Move directories to backup directory
    for dir_name in dirs_to_remove:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            try:
                shutil.copytree(dir_path, backup_dir / dir_name)
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_name}")
            except Exception as e:
                print(f"Error removing directory {dir_name}: {e}")
    
    print("\nCleanup complete!")
    print(f"Obsolete files have been backed up to: {backup_dir}")
    print("You can safely delete the backup directory if everything works correctly.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())