#!/usr/bin/env python3
"""
Simple script to update the Windsurf configuration for the MCP Task Orchestrator.
"""

import json
import os
import re
from pathlib import Path
import shutil
import sys

def main():
    """Update the Windsurf configuration for the MCP Task Orchestrator."""
    print("MCP Task Orchestrator - Windsurf Configuration Update")
    print("=" * 60)
    
    # Get the current directory
    current_dir = Path(__file__).parent.absolute()
    
    # Define the new server path
    new_server_path = str(current_dir / "mcp_task_orchestrator" / "server.py")
    print(f"New server path: {new_server_path}")
    
    # Check if the new server path exists
    if not Path(new_server_path).exists():
        print(f"Error: Server script not found at {new_server_path}")
        return 1
    
    # Find Windsurf config - using the correct path
    windsurf_config_path = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"
    
    if not windsurf_config_path.exists():
        print(f"Error: Windsurf configuration not found at {windsurf_config_path}")
        return 1
    
    print(f"Found Windsurf configuration at {windsurf_config_path}")
    
    # Create backup
    backup_path = windsurf_config_path.with_suffix(f".backup.{int(os.path.getmtime(windsurf_config_path))}.json")
    try:
        shutil.copy2(windsurf_config_path, backup_path)
        print(f"Created backup at {backup_path}")
    except Exception as e:
        print(f"Warning: Failed to create backup: {e}")
    
    # Read configuration file as text first to fix any JSON syntax issues
    try:
        with open(windsurf_config_path, 'r', encoding='utf-8') as f:
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
    
    # Remove from servers array if it exists (wrong format)
    if "servers" in config and isinstance(config["servers"], list):
        config["servers"] = [s for s in config["servers"] if not (isinstance(s, dict) and s.get("name") == "task-orchestrator")]
        print("Removed task-orchestrator from servers array (wrong format)")
    
    # Add to mcpServers with the correct format
    config["mcpServers"]["task-orchestrator"] = {
        "command": "python",
        "args": [new_server_path.replace("\\", "/")],  # Use forward slashes for consistency
        "cwd": str(current_dir).replace("\\", "/"),    # Use forward slashes for consistency
        "env": {}
    }
    updated = True
    print("Added task-orchestrator to mcpServers with correct format")
    
    # Write configuration
    if updated:
        try:
            with open(windsurf_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print("Successfully updated Windsurf configuration")
        except Exception as e:
            print(f"Error: Failed to write configuration: {e}")
            return 1
    else:
        print("No changes needed to Windsurf configuration")
    
    print("\nConfiguration update complete!")
    print("Please restart Windsurf to apply the changes.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())