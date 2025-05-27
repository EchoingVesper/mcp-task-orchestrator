#!/usr/bin/env python3
"""Validate MCP client configurations."""

import sys
import json
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent / "installer"))

from installer.clients import get_all_clients

def main():
    """Validate client configurations."""
    print("Validating MCP Client Configurations...")
    print("=" * 45)
    
    project_root = Path(__file__).parent
    clients = get_all_clients(project_root)
    
    all_valid = True
    
    for client in clients:
        print(f"\n{client.client_name}:")
        print(f"  Config Path: {client.get_config_path()}")
        
        config_path = client.get_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Check if our server is configured
                if "mcpServers" in config and "task-orchestrator" in config["mcpServers"]:
                    server_config = config["mcpServers"]["task-orchestrator"]
                    print(f"  Status: CONFIGURED [OK]")
                    print(f"  Command: {server_config.get('command', 'N/A')}")
                    
                    # Validate Python path exists
                    python_path = Path(server_config.get('command', ''))
                    if python_path.exists():
                        print(f"  Python Valid: YES")
                    else:
                        print(f"  Python Valid: NO [ERROR]")
                        all_valid = False
                else:
                    print(f"  Status: NOT CONFIGURED [ERROR]")
                    all_valid = False
                    
            except json.JSONDecodeError:
                print(f"  Status: INVALID JSON [ERROR]")
                all_valid = False
            except Exception as e:
                print(f"  Status: ERROR - {e}")
                all_valid = False
        else:
            print(f"  Status: CONFIG FILE MISSING [ERROR]")
            all_valid = False
    
    print(f"\nOverall Status: {'ALL VALID' if all_valid else 'ISSUES FOUND'}")
    return all_valid

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
