"""
Command-line interface for MCP Task Orchestrator.

This module provides CLI commands for managing the orchestrator,
checking status, and performing administrative tasks.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from ..infrastructure.config import ConfigurationManager
from ..infrastructure.monitoring import HealthChecker
from ..infrastructure.di import ServiceContainer, get_container
from ..infrastructure.di.service_configuration import configure_all_services
from ..domain import TaskRepository, StateRepository
from .mcp_server import MCPServerEntryPoint

logger = logging.getLogger(__name__)


class CLIInterface:
    """
    Command-line interface for the MCP Task Orchestrator.
    
    Provides commands for:
    - Starting the server
    - Checking system health
    - Managing configuration
    - Administrative tasks
    """
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.container: Optional[ServiceContainer] = None
    
    def setup_container(self) -> bool:
        """Set up dependency injection container for CLI operations."""
        try:
            settings = self.config_manager.load_configuration()
            self.container = ServiceContainer()
            configure_all_services(self.container, settings.__dict__)
            return True
        except Exception as e:
            logger.error(f"Failed to setup DI container: {e}")
            return False
    
    async def health_check(self) -> int:
        """
        Run system health checks and return status code.
        
        Returns:
            0 if healthy, 1 if unhealthy
        """
        print("Running MCP Task Orchestrator health checks...")
        
        if not self.setup_container():
            print("❌ Failed to initialize system")
            return 1
        
        try:
            # Get repositories for health checking
            task_repo = self.container.get_service(TaskRepository)
            state_repo = self.container.get_service(StateRepository)
            
            # Create health checker
            health_checker = HealthChecker(task_repo, state_repo)
            
            # Run all health checks
            results = await health_checker.run_all_checks()
            
            # Display results
            overall_healthy = True
            for check_name, result in results.items():
                status = "✅" if result.healthy else "❌"
                print(f"{status} {check_name}: {result.message}")
                if not result.healthy:
                    overall_healthy = False
                    if result.details:
                        for key, value in result.details.items():
                            print(f"   {key}: {value}")
            
            if overall_healthy:
                print("\n🎉 All health checks passed!")
                return 0
            else:
                print("\n⚠️  Some health checks failed!")
                return 1
        
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return 1
        finally:
            if self.container:
                self.container.dispose()
    
    async def start_server(self, config_file: Optional[Path] = None) -> int:
        """
        Start the MCP server.
        
        Args:
            config_file: Optional configuration file path
            
        Returns:
            Exit code
        """
        try:
            server_entry = MCPServerEntryPoint(config_file)
            
            if server_entry.initialize():
                await server_entry.run()
                return 0
            else:
                print("❌ Failed to initialize server")
                return 1
        
        except KeyboardInterrupt:
            print("\n🛑 Server shutdown requested")
            return 0
        except Exception as e:
            print(f"❌ Server error: {e}")
            return 1
    
    def show_config(self) -> int:
        """
        Display current configuration.
        
        Returns:
            Exit code
        """
        try:
            settings = self.config_manager.load_configuration()
            
            print("📋 MCP Task Orchestrator Configuration:")
            print(f"  Database Path: {self.config_manager.get_database_url()}")
            print(f"  Workspace Dir: {self.config_manager.get_workspace_directory()}")
            print(f"  Artifacts Dir: {self.config_manager.get_artifacts_directory()}")
            print(f"  DI Enabled: {self.config_manager.is_dependency_injection_enabled()}")
            print(f"  Log Level: {settings.log_level}")
            print(f"  Max Concurrent Tasks: {settings.max_concurrent_tasks}")
            print(f"  Default Task Timeout: {settings.default_task_timeout}s")
            
            return 0
        
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return 1
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="MCP Task Orchestrator CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '--config', '-c',
            type=Path,
            help='Configuration file path'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose logging'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Server command
        server_parser = subparsers.add_parser('server', help='Start the MCP server')
        server_parser.add_argument(
            '--config-file',
            type=Path,
            help='Server configuration file'
        )
        
        # Health command
        subparsers.add_parser('health', help='Run health checks')
        
        # Config command
        subparsers.add_parser('config', help='Show current configuration')
        
        return parser
    
    async def run_cli(self, args: Optional[list] = None) -> int:
        """
        Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Update config manager if config file provided
        if parsed_args.config:
            self.config_manager = ConfigurationManager(parsed_args.config)
        
        # Route to appropriate command
        if parsed_args.command == 'server':
            return await self.start_server(parsed_args.config_file)
        elif parsed_args.command == 'health':
            return await self.health_check()
        elif parsed_args.command == 'config':
            return self.show_config()
        else:
            parser.print_help()
            return 1


def main_cli():
    """Main CLI entry point."""
    cli = CLIInterface()
    exit_code = asyncio.run(cli.run_cli())
    sys.exit(exit_code)


if __name__ == "__main__":
    main_cli()