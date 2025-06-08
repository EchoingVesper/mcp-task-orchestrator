#!/usr/bin/env python3
"""
Comprehensive uninstall script for MCP Task Orchestrator.

This script safely removes MCP Task Orchestrator from all MCP client configurations
without affecting other MCP servers or user configurations.
"""

import os
import sys
import json
import shutil
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
import argparse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("uninstall_orchestrator.log")
    ]
)
logger = logging.getLogger(__name__)


class MCPClientManager:
    """Manages MCP client configurations across different platforms."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.backup_dir = Path.cwd() / "mcp_config_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Define client configuration paths
        self.client_configs = self._get_client_config_paths()
    
    def _get_client_config_paths(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration paths for all supported MCP clients."""
        if self.platform == "windows":
            home = Path.home()
            appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
            localappdata = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
            
            return {
                "claude_desktop": {
                    "name": "Claude Desktop",
                    "config_path": appdata / "Claude" / "claude_desktop_config.json",
                    "backup_name": "claude_desktop_config_backup.json"
                },
                "windsurf": {
                    "name": "Windsurf",
                    "config_path": appdata / "Windsurf" / "User" / "globalStorage" / "windsurf-ai.windsurf" / "config.json",
                    "backup_name": "windsurf_config_backup.json"
                },
                "cursor": {
                    "name": "Cursor",
                    "config_path": appdata / "Cursor" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "cursor_config_backup.json"
                },
                "vscode": {
                    "name": "VS Code",
                    "config_path": appdata / "Code" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "vscode_config_backup.json"
                }
            }
        
        elif self.platform == "darwin":  # macOS
            home = Path.home()
            
            return {
                "claude_desktop": {
                    "name": "Claude Desktop",
                    "config_path": home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
                    "backup_name": "claude_desktop_config_backup.json"
                },
                "windsurf": {
                    "name": "Windsurf", 
                    "config_path": home / "Library" / "Application Support" / "Windsurf" / "User" / "globalStorage" / "windsurf-ai.windsurf" / "config.json",
                    "backup_name": "windsurf_config_backup.json"
                },
                "cursor": {
                    "name": "Cursor",
                    "config_path": home / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "cursor_config_backup.json"
                },
                "vscode": {
                    "name": "VS Code",
                    "config_path": home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "vscode_config_backup.json"
                }
            }
        
        else:  # Linux and other Unix-like systems
            home = Path.home()
            
            return {
                "claude_desktop": {
                    "name": "Claude Desktop",
                    "config_path": home / ".config" / "Claude" / "claude_desktop_config.json",
                    "backup_name": "claude_desktop_config_backup.json"
                },
                "windsurf": {
                    "name": "Windsurf",
                    "config_path": home / ".config" / "Windsurf" / "User" / "globalStorage" / "windsurf-ai.windsurf" / "config.json",
                    "backup_name": "windsurf_config_backup.json"
                },
                "cursor": {
                    "name": "Cursor",
                    "config_path": home / ".config" / "Cursor" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "cursor_config_backup.json"
                },
                "vscode": {
                    "name": "VS Code",
                    "config_path": home / ".config" / "Code" / "User" / "globalStorage" / "mcp-config.json",
                    "backup_name": "vscode_config_backup.json"
                }
            }
    
    def backup_config(self, client_id: str, config_path: Path) -> bool:
        """Create a backup of the client configuration."""
        try:
            if not config_path.exists():
                logger.info(f"No configuration file found for {client_id}: {config_path}")
                return True
            
            backup_path = self.backup_dir / self.client_configs[client_id]["backup_name"]
            shutil.copy2(config_path, backup_path)
            logger.info(f"Backed up {client_id} config to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup {client_id} config: {e}")
            return False
    
    def remove_orchestrator_from_config(self, client_id: str, config_path: Path, dry_run: bool = False) -> Tuple[bool, List[str]]:
        """Remove MCP Task Orchestrator from a client configuration."""
        removed_entries = []
        
        try:
            if not config_path.exists():
                logger.info(f"No configuration file found for {client_id}: {config_path}")
                return True, removed_entries
            
            # Read current configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Track original state for comparison
            original_config = json.dumps(config, sort_keys=True)
            
            # Remove orchestrator entries from mcpServers
            if "mcpServers" in config:
                servers_to_remove = []
                
                for server_name, server_config in config["mcpServers"].items():
                    # Check if this is a task orchestrator server
                    if self._is_orchestrator_server(server_name, server_config):
                        servers_to_remove.append(server_name)
                        removed_entries.append(f"mcpServers.{server_name}")
                
                # Remove identified servers
                for server_name in servers_to_remove:
                    if not dry_run:
                        del config["mcpServers"][server_name]
                    logger.info(f"{'Would remove' if dry_run else 'Removed'} server: {server_name}")
            
            # Check if configuration actually changed
            new_config = json.dumps(config, sort_keys=True)
            if original_config == new_config:
                logger.info(f"No orchestrator entries found in {client_id} configuration")
                return True, removed_entries
            
            # Write updated configuration (if not dry run)
            if not dry_run:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                logger.info(f"Updated {client_id} configuration: {config_path}")
            else:
                logger.info(f"Would update {client_id} configuration: {config_path}")
            
            return True, removed_entries
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {client_id} config file {config_path}: {e}")
            return False, removed_entries
            
        except Exception as e:
            logger.error(f"Failed to process {client_id} config: {e}")
            return False, removed_entries
    
    def _is_orchestrator_server(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Check if a server configuration is for MCP Task Orchestrator."""
        # Check server name patterns
        orchestrator_name_patterns = [
            "task-orchestrator",
            "task_orchestrator", 
            "mcp-task-orchestrator",
            "mcp_task_orchestrator",
            "orchestrator"
        ]
        
        name_lower = server_name.lower()
        if any(pattern in name_lower for pattern in orchestrator_name_patterns):
            return True
        
        # Check command patterns
        if "command" in server_config:
            command = server_config["command"]
            if isinstance(command, str):
                command_lower = command.lower()
                if any(pattern in command_lower for pattern in orchestrator_name_patterns):
                    return True
                if "mcp-task-orchestrator" in command_lower or "task_orchestrator" in command_lower:
                    return True
            elif isinstance(command, list) and command:
                first_arg = command[0].lower()
                if any(pattern in first_arg for pattern in orchestrator_name_patterns):
                    return True
        
        # Check arguments for orchestrator-specific paths
        if "args" in server_config:
            args = server_config.get("args", [])
            if isinstance(args, list):
                args_str = " ".join(str(arg) for arg in args).lower()
                if any(pattern in args_str for pattern in orchestrator_name_patterns):
                    return True
        
        return False
    
    def detect_configured_clients(self) -> Dict[str, Dict[str, Any]]:
        """Detect which MCP clients have configurations."""
        configured_clients = {}
        
        for client_id, client_info in self.client_configs.items():
            config_path = client_info["config_path"]
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # Check if orchestrator is configured
                    has_orchestrator = False
                    orchestrator_servers = []
                    
                    if "mcpServers" in config:
                        for server_name, server_config in config["mcpServers"].items():
                            if self._is_orchestrator_server(server_name, server_config):
                                has_orchestrator = True
                                orchestrator_servers.append(server_name)
                    
                    configured_clients[client_id] = {
                        **client_info,
                        "has_orchestrator": has_orchestrator,
                        "orchestrator_servers": orchestrator_servers,
                        "config_exists": True
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not read {client_id} config: {e}")
                    configured_clients[client_id] = {
                        **client_info,
                        "has_orchestrator": False,
                        "orchestrator_servers": [],
                        "config_exists": True,
                        "error": str(e)
                    }
            else:
                configured_clients[client_id] = {
                    **client_info,
                    "has_orchestrator": False,
                    "orchestrator_servers": [],
                    "config_exists": False
                }
        
        return configured_clients


class OrchestatorUninstaller:
    """Main uninstaller class for MCP Task Orchestrator."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client_manager = MCPClientManager()
        self.uninstall_log = []
    
    def run_uninstall(self, clients_to_process: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run the complete uninstall process."""
        logger.info("=" * 60)
        logger.info("MCP Task Orchestrator - Comprehensive Uninstall")
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No changes will be made")
        
        results = {
            "success": True,
            "clients_processed": 0,
            "clients_modified": 0,
            "entries_removed": 0,
            "errors": [],
            "summary": [],
            "backup_location": str(self.client_manager.backup_dir)
        }
        
        # Detect configured clients
        logger.info("\n📋 Detecting MCP client configurations...")
        configured_clients = self.client_manager.detect_configured_clients()
        
        # Filter clients if specified
        if clients_to_process:
            configured_clients = {
                k: v for k, v in configured_clients.items() 
                if k in clients_to_process
            }
        
        # Display detection results
        self._display_detection_results(configured_clients)
        
        # Process each client
        logger.info(f"\n🔧 {'Would process' if self.dry_run else 'Processing'} MCP client configurations...")
        
        for client_id, client_info in configured_clients.items():
            if not client_info["config_exists"]:
                continue
            
            results["clients_processed"] += 1
            
            # Create backup
            if not self.dry_run:
                backup_success = self.client_manager.backup_config(
                    client_id, client_info["config_path"]
                )
                if not backup_success:
                    results["errors"].append(f"Failed to backup {client_id} configuration")
                    continue
            
            # Remove orchestrator from configuration
            success, removed_entries = self.client_manager.remove_orchestrator_from_config(
                client_id, client_info["config_path"], self.dry_run
            )
            
            if success:
                if removed_entries:
                    results["clients_modified"] += 1
                    results["entries_removed"] += len(removed_entries)
                    results["summary"].append(f"{client_info['name']}: Removed {len(removed_entries)} entries")
                else:
                    results["summary"].append(f"{client_info['name']}: No orchestrator entries found")
            else:
                results["success"] = False
                results["errors"].append(f"Failed to process {client_id}")
        
        # Package uninstallation
        logger.info(f"\n📦 {'Would check' if self.dry_run else 'Checking'} package installation...")
        package_results = self._handle_package_uninstall()
        results.update(package_results)
        
        # Generate final report
        self._generate_final_report(results)
        
        return results
    
    def _display_detection_results(self, configured_clients: Dict[str, Dict[str, Any]]):
        """Display the results of client detection."""
        logger.info("\n📍 MCP Client Detection Results:")
        
        for client_id, client_info in configured_clients.items():
            status_icon = "✅" if client_info["config_exists"] else "❌"
            orch_icon = "🎯" if client_info["has_orchestrator"] else "➖"
            
            logger.info(f"  {status_icon} {client_info['name']}")
            logger.info(f"    Config: {client_info['config_path']}")
            
            if client_info["config_exists"]:
                if client_info["has_orchestrator"]:
                    logger.info(f"    {orch_icon} Orchestrator servers: {', '.join(client_info['orchestrator_servers'])}")
                else:
                    logger.info(f"    {orch_icon} No orchestrator configuration found")
            else:
                logger.info(f"    {orch_icon} No configuration file found")
    
    def _handle_package_uninstall(self) -> Dict[str, Any]:
        """Handle the Python package uninstallation."""
        package_results = {
            "package_installed": False,
            "package_uninstall_recommended": False
        }
        
        try:
            import subprocess
            
            # Check if package is installed
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "mcp-task-orchestrator"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                package_results["package_installed"] = True
                package_results["package_uninstall_recommended"] = True
                
                if not self.dry_run:
                    logger.info("📦 Package 'mcp-task-orchestrator' is installed")
                    logger.info("   Recommendation: Uninstall with 'pip uninstall mcp-task-orchestrator'")
                else:
                    logger.info("📦 Would check package installation status")
            else:
                logger.info("📦 Package 'mcp-task-orchestrator' is not installed")
                
        except Exception as e:
            logger.warning(f"Could not check package installation: {e}")
        
        return package_results
    
    def _generate_final_report(self, results: Dict[str, Any]):
        """Generate and display the final uninstall report."""
        logger.info("\n" + "=" * 60)
        logger.info("🏁 UNINSTALL SUMMARY")
        logger.info("=" * 60)
        
        if self.dry_run:
            logger.info("🔍 DRY RUN COMPLETED - No actual changes were made")
        
        logger.info(f"📊 Clients processed: {results['clients_processed']}")
        logger.info(f"📝 Clients modified: {results['clients_modified']}")
        logger.info(f"🗑️  Entries removed: {results['entries_removed']}")
        
        if results["errors"]:
            logger.error(f"❌ Errors encountered: {len(results['errors'])}")
            for error in results["errors"]:
                logger.error(f"   - {error}")
        
        if results["summary"]:
            logger.info("\n📋 Client Summary:")
            for summary_item in results["summary"]:
                logger.info(f"   • {summary_item}")
        
        if not self.dry_run and results["clients_modified"] > 0:
            logger.info(f"\n💾 Configuration backups saved to: {results['backup_location']}")
        
        if results["package_uninstall_recommended"]:
            logger.info("\n📦 NEXT STEPS:")
            logger.info("   1. Exit Claude Code and restart your MCP clients")
            logger.info("   2. Uninstall the Python package: pip uninstall mcp-task-orchestrator")
        
        success_emoji = "✅" if results["success"] else "❌"
        logger.info(f"\n{success_emoji} Uninstall {'would complete' if self.dry_run else 'completed'} {'successfully' if results['success'] else 'with errors'}")


def main():
    """Main entry point for the uninstall script."""
    parser = argparse.ArgumentParser(
        description="Comprehensive uninstaller for MCP Task Orchestrator"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--clients",
        nargs="+",
        choices=["claude_desktop", "windsurf", "cursor", "vscode"],
        help="Specific clients to process (default: all detected)"
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        help="Custom backup directory path"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimize output (errors only)"
    )
    
    args = parser.parse_args()
    
    # Adjust logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    try:
        # Create uninstaller
        uninstaller = OrchestatorUninstaller(dry_run=args.dry_run)
        
        # Set custom backup directory if specified
        if args.backup_dir:
            uninstaller.client_manager.backup_dir = Path(args.backup_dir)
            uninstaller.client_manager.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Run uninstall
        results = uninstaller.run_uninstall(clients_to_process=args.clients)
        
        # Exit with appropriate code
        sys.exit(0 if results["success"] else 1)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Uninstall cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()