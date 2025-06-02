#!/usr/bin/env python3
"""Unified MCP Task Orchestrator installer with client auto-detection."""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict

from .client_detector import ClientDetector


class UnifiedInstaller:
    """Main installer for MCP Task Orchestrator with client auto-detection."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv_mcp"
        self.python_exe = self._find_python_exe()
        self.detector = ClientDetector(self.project_root)
    
    def _find_python_exe(self):
        """Find the Python executable in the virtual environment."""
        # Check for Windows-style Scripts directory
        windows_python = self.venv_path / "Scripts" / "python.exe"
        if windows_python.exists():
            return windows_python
            
        # Check for Unix-style bin directory
        unix_python = self.venv_path / "bin" / "python"
        if unix_python.exists():
            return unix_python
            
        # Check for Unix-style with python3
        unix_python3 = self.venv_path / "bin" / "python3"
        if unix_python3.exists():
            return unix_python3
            
        # Default to Windows style if venv doesn't exist yet
        return windows_python
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, message: str):
        """Print a step message."""
        print(f"\n[{step}] {message}")
    
    def ensure_virtual_environment(self) -> bool:
        """Ensure virtual environment exists and is properly configured."""
        self.print_step("VENV", "Checking virtual environment...")
        
        if not self.venv_path.exists():
            self.print_step("VENV", "Creating virtual environment...")
            try:
                subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                              check=True, capture_output=True, text=True)
                print("[OK] Virtual environment created")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to create virtual environment: {e}")
                return False
        else:
            print("[OK] Virtual environment exists")
        
        return self.python_exe.exists()

    def install_dependencies(self) -> bool:
        """Install project dependencies in virtual environment."""
        self.print_step("PACKAGES", "Installing dependencies...")
        
        try:
            # Upgrade pip
            subprocess.run([str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"], 
                          check=True, capture_output=True, text=True)
            
            # Install requirements
            subprocess.run([str(self.python_exe), "-m", "pip", "install", "-r", "requirements.txt"], 
                          check=True, capture_output=True, text=True, cwd=str(self.project_root))
            
            # Install project in editable mode
            subprocess.run([str(self.python_exe), "-m", "pip", "install", "-e", "."], 
                          check=True, capture_output=True, text=True, cwd=str(self.project_root))
            
            print("[OK] Dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install dependencies: {e}")
            return False
    
    def detect_clients(self) -> Dict[str, bool]:
        """Detect available MCP clients."""
        self.print_step("DETECT", "Detecting MCP clients...")
        
        detected = self.detector.detect_all()
        
        for client_id, is_detected in detected.items():
            client = next(c for c in self.detector.clients if c.client_id == client_id)
            status = "FOUND" if is_detected else "NOT FOUND"
            print(f"  {client.client_name}: {status}")
        
        return detected
    
    def configure_clients(self, selected_clients: List[str] = None) -> Dict[str, bool]:
        """Configure selected MCP clients."""
        if selected_clients is None:
            # Auto-configure all detected clients
            detected = self.detector.get_detected_clients()
            selected_clients = [client.client_id for client in detected]
        
        self.print_step("CONFIG", "Configuring MCP clients...")
        
        results = {}
        for client in self.detector.clients:
            if client.client_id in selected_clients:
                try:
                    success = client.create_configuration()
                    status = "SUCCESS" if success else "FAILED"
                    print(f"  {client.client_name}: {status}")
                    results[client.client_id] = success
                except Exception as e:
                    print(f"  {client.client_name}: ERROR - {e}")
                    results[client.client_id] = False
        
        return results

    def run_installation(self, selected_clients: List[str] = None) -> bool:
        """Run the complete installation process."""
        self.print_header("MCP Task Orchestrator - Unified Installation")
        
        # Step 1: Ensure virtual environment
        if not self.ensure_virtual_environment():
            return False
        
        # Step 2: Install dependencies
        if not self.install_dependencies():
            return False
        
        # Step 3: Detect clients
        detected = self.detect_clients()
        
        # Step 4: Configure clients
        if selected_clients is None:
            # Auto-select detected clients
            selected_clients = [client_id for client_id, detected in detected.items() if detected]
        
        if not selected_clients:
            print("\n[WARNING] No MCP clients detected or selected")
            return True
        
        config_results = self.configure_clients(selected_clients)
        
        # Step 5: Summary
        self.print_header("Installation Complete!")
        
        successful = sum(1 for success in config_results.values() if success)
        total = len(config_results)
        
        print(f"\nConfigured {successful}/{total} clients successfully")
        
        if successful > 0:
            print("\nNext steps:")
            print("1. Restart your MCP client applications")
            print("2. Look for 'task-orchestrator' in the available tools/servers")
            print("3. Start using the MCP Task Orchestrator!")
        
        return successful > 0


def main():
    """Entry point for the unified installer."""
    installer = UnifiedInstaller()
    success = installer.run_installation()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
