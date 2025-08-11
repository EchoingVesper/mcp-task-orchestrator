#!/usr/bin/env python3
"""
Validation script for MCP Task Orchestrator configurations.

This script validates that all detected MCP client configurations
are properly formatted and contain valid paths.
"""

import sys
import json
import os
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent / "installer"))

from mcp_task_orchestrator_cli.platforms.client_detector import ClientDetector

def validate_config(client_id, config_path):
    """Validate a client configuration file."""
    try:
        # Check if file exists
        if not os.path.exists(config_path):
            return False, f"Configuration file does not exist: {config_path}"
        
        # Read and parse JSON
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check for task-orchestrator in mcpServers
        if 'mcpServers' not in config:
            return False, "Missing 'mcpServers' section"
        
        if 'task-orchestrator' not in config['mcpServers']:
            return False, "Missing 'task-orchestrator' server configuration"
        
        server_config = config['mcpServers']['task-orchestrator']
        
        # Check for required fields
        if 'command' not in server_config:
            return False, "Missing 'command' in server configuration"
        
        if 'args' not in server_config:
            return False, "Missing 'args' in server configuration"
        
        # Validate Python path
        python_path = server_config['command']
        if not os.path.exists(python_path):
            return False, f"Python path does not exist: {python_path}"
        
        # All checks passed
        return True, "Configuration is valid"
    
    except json.JSONDecodeError:
        return False, "Invalid JSON format"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def main():
    """Validate all detected client configurations."""
    print("\nMCP Task Orchestrator - Configuration Validation")
    print("=" * 50)
    
    # Initialize detector
    detector = ClientDetector(Path(__file__).parent)
    
    # Get status for all clients
    status = detector.get_client_status()
    
    # Print results
    print("\nValidation Results:")
    print("-" * 30)
    
    valid_count = 0
    detected_count = 0
    
    for client_id, client_info in status.items():
        client_name = client_info.get('name', client_id)
        detected = client_info.get('detected', False)
        
        if detected:
            detected_count += 1
            config_path = client_info.get('config_path', None)
            
            if config_path:
                is_valid, message = validate_config(client_id, config_path)
                status_text = "VALID" if is_valid else "INVALID"
                
                if is_valid:
                    valid_count += 1
                    print(f"✓ {client_name}: {status_text}")
                else:
                    print(f"✗ {client_name}: {status_text}")
                    print(f"  Error: {message}")
            else:
                print(f"✗ {client_name}: MISSING CONFIG PATH")
        
        print()
    
    # Summary
    print("\nSummary:")
    print(f"Valid configurations: {valid_count}/{detected_count} detected clients")
    
    return 0 if valid_count == detected_count and detected_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
