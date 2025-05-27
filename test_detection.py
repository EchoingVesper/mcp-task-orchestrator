#!/usr/bin/env python3
"""
Test script for client detection functionality.

This script tests the client detection capabilities of the MCP Task Orchestrator
installer without making any configuration changes.
"""

import sys
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent / "installer"))

from installer.client_detector import ClientDetector

def main():
    """Test client detection and print results."""
    print("\nMCP Task Orchestrator - Client Detection Test")
    print("=" * 50)
    
    # Initialize detector
    detector = ClientDetector(Path(__file__).parent)
    
    # Get status for all clients
    status = detector.get_client_status()
    
    # Print results
    print("\nDetection Results:")
    print("-" * 30)
    
    detected_count = 0
    for client_id, client_info in status.items():
        client_name = client_info.get('name', client_id)
        detected = client_info.get('detected', False)
        status_text = "FOUND" if detected else "NOT FOUND"
        
        if detected:
            detected_count += 1
            config_path = client_info.get('config_path', 'Unknown')
            print(f"✓ {client_name}: {status_text}")
            print(f"  Config path: {config_path}")
        else:
            print(f"✗ {client_name}: {status_text}")
        
        if 'error' in client_info:
            print(f"  Error: {client_info['error']}")
        
        print()
    
    # Summary
    print("\nSummary:")
    print(f"Found {detected_count}/{len(status)} MCP clients")
    
    return 0 if detected_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
