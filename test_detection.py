#!/usr/bin/env python3
"""Test client detection functionality."""

import sys
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent / "installer"))

from installer.client_detector import ClientDetector

def main():
    """Test client detection."""
    print("Testing MCP Client Detection...")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    detector = ClientDetector(project_root)
    
    # Test detection
    detected = detector.detect_all()
    
    print("Detection Results:")
    for client_id, is_detected in detected.items():
        client = next(c for c in detector.clients if c.client_id == client_id)
        status = "FOUND" if is_detected else "NOT FOUND"
        print(f"  {client.client_name}: {status}")
    
    # Test detailed status
    print("\nDetailed Status:")
    status = detector.get_client_status()
    for client_id, info in status.items():
        print(f"  {client_id}:")
        print(f"    Name: {info['name']}")
        print(f"    Detected: {info['detected']}")
        print(f"    Config Path: {info.get('config_path', 'N/A')}")
        if 'error' in info:
            print(f"    Error: {info['error']}")

if __name__ == "__main__":
    main()
