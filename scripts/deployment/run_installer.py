#!/usr/bin/env python3
"""
Simple launcher for the MCP Task Orchestrator installer.
This handles the module import issues by properly setting up the Python path.
"""

import sys
import os
from pathlib import Path

def main():
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir
    
    # Add the project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Change to the project directory
    os.chdir(project_root)
    
    try:
        # Import and run the installer
        from installer.main_installer import UnifiedInstaller
        
        print("Starting MCP Task Orchestrator installation...")
        print(f"Project root: {project_root}")
        print("")
        
        # Create and run the installer
        installer = UnifiedInstaller(project_root)
        
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='Install MCP Task Orchestrator')
        parser.add_argument('--clients', type=str, help='Specific clients to configure (space-separated)')
        args = parser.parse_args()
        
        # Run the installation
        if args.clients:
            client_list = args.clients.split()
            installer.run_installation(selected_clients=client_list)
        else:
            installer.run_installation()
            
        print("\nInstallation completed successfully!")
        print("Please restart your MCP clients (Claude Desktop, Cursor, etc.) to use the Task Orchestrator.")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all files are properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
