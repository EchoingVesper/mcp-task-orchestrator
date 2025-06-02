#!/usr/bin/env python3
"""
MCP Task Orchestrator - Unified Installation Script

Usage:
    python install.py                    # Auto-detect and configure all
    python install.py --clients claude-desktop cursor-ide  # Configure specific clients
    python install.py --list-clients     # List available clients
    python install.py --detect-only      # Only detect clients, don't configure
"""

import sys
import argparse
from pathlib import Path

# Add installer directory to path
sys.path.insert(0, str(Path(__file__).parent / "installer"))

from installer.main_installer import UnifiedInstaller


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Task Orchestrator Unified Installer")
    
    # Create mutually exclusive group for main actions
    action_group = parser.add_mutually_exclusive_group()
    
    action_group.add_argument(
        '--clients', 
        nargs='+',
        choices=['claude-desktop', 'cursor-ide', 'windsurf', 'vscode-cline'],
        help='Specific clients to configure'
    )
    
    action_group.add_argument(
        '--list-clients',
        action='store_true',
        help='List all available clients without installing'
    )
    
    action_group.add_argument(
        '--detect-only',
        action='store_true',
        help='Detect installed clients without configuring them'
    )
    
    args = parser.parse_args()
    
    # Initialize installer
    installer = UnifiedInstaller()
    
    # Handle different actions
    if args.list_clients:
        # List available clients
        print("\nAvailable MCP clients:")
        for client in installer.detector.clients:
            print(f"  - {client.client_name} (ID: {client.client_id})")
        return 0
    
    elif args.detect_only:
        # Only detect clients
        installer.print_header("MCP Task Orchestrator - Client Detection")
        detected = installer.detect_clients()
        
        print("\nDetection complete!")
        detected_count = sum(1 for status in detected.values() if status)
        print(f"Found {detected_count}/{len(detected)} MCP clients")
        return 0
    
    else:
        # Run full installation
        success = installer.run_installation(args.clients)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
