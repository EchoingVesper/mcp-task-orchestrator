#!/usr/bin/env python3
"""
Simple script to update the Claude Desktop configuration for the MCP Task Orchestrator.
"""

import json
import os
import re
from pathlib import Path
import shutil
import sys

def main():
    """Update the Claude Desktop configuration for the MCP Task Orchestrator with virtual environment."""
    print("MCP Task Orchestrator - Claude Desktop Configuration Update (Virtual Environment)")
    print("=" * 80)
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Define the virtual environment Python path
    venv_python = current_dir / "venv_mcp" / "Scripts" / "python.exe"
    print(f"Virtual environment Python: {venv_python}")
    
    # Check if the virtual environment exists
    if not venv_python.exists():
        print(f"Error: Virtual environment Python not found at {venv_python}")
        print("Please run 'install_venv_simple.py' first to create the virtual environment.")
        return 1
    
    # Find Claude Desktop config
    claude_config_path = Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
    
    if not claude_config_path.exists():
        print(f"Error: Claude Desktop configuration not found at {claude_config_path}")
        return 1
    
    print(f"Found Claude Desktop configuration at {claude_config_path}")
    
    # Create backup
    backup_path = claude_config_path.with_suffix(f".backup.{int(os.path.getmtime(claude_config_path))}.json")
    try:
        shutil.copy2(claude_config_path, backup_path)
        print(f"Created backup at {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {e}")
    
    # Read configuration file as text first to fix any JSON syntax issues
    try:
        with open(claude_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix trailing commas (common JSON syntax error)
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        
        # Parse the fixed JSON
        config = json.loads(content)
        print("Successfully parsed configuration file")
    except Exception as e:
        print(f"Error: Failed to read configuration: {e}")
        return 1    
    # Update configuration
    updated = False
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add to mcpServers with the correct virtual environment configuration
    config["mcpServers"]["task-orchestrator"] = {
        "command": str(venv_python).replace("\\", "/"),  # Use forward slashes for consistency
        "args": ["-m", "mcp_task_orchestrator.server"],
        "cwd": str(current_dir).replace("\\", "/")
    }
    updated = True
    print("Added task-orchestrator to mcpServers with virtual environment Python")
    
    # Write configuration
    if updated:
        try:
            with open(claude_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print("Successfully updated Claude Desktop configuration")
        except Exception as e:
            print(f"Error: Failed to write configuration: {e}")
            return 1
    else:
        print("No changes needed to Claude Desktop configuration")
    
    print("\nVirtual environment configuration update complete!")
    print("The configuration now points to the isolated virtual environment Python.")
    print("Please restart Claude Desktop completely to apply the changes.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())