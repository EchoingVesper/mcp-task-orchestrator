#!/usr/bin/env python3
"""Client detection utilities for MCP Task Orchestrator."""

from pathlib import Path
from typing import List, Dict
from .clients import get_all_clients


class ClientDetector:
    """Utility class for detecting installed MCP clients."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.clients = get_all_clients(project_root)
    
    def detect_all(self) -> Dict[str, bool]:
        """Detect all available MCP clients."""
        results = {}
        for client in self.clients:
            try:
                results[client.client_id] = client.detect_installation()
            except Exception:
                results[client.client_id] = False
        return results
    
    def get_detected_clients(self) -> List:
        """Get list of detected client instances."""
        detected = []
        for client in self.clients:
            try:
                if client.detect_installation():
                    detected.append(client)
            except Exception:
                continue
        return detected
    
    def get_client_status(self) -> Dict[str, Dict]:
        """Get detailed status for all clients."""
        status = {}
        for client in self.clients:
            try:
                status[client.client_id] = {
                    'name': client.client_name,
                    'detected': client.detect_installation(),
                    'config_path': str(client.get_config_path())
                }
            except Exception as e:
                status[client.client_id] = {'name': client.client_name, 'error': str(e)}
        return status
