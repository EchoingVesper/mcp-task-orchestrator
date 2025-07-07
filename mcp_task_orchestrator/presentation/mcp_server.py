"""
MCP Server entry point using clean architecture.

This module provides the main entry point for the MCP Task Orchestrator server
using the new clean architecture with dependency injection.
"""

import asyncio
import os
import logging
from typing import Optional
from pathlib import Path

from mcp.server.stdio import stdio_server

from ..infrastructure.config import ConfigurationManager
from ..infrastructure.di import ServiceContainer, get_container, set_container
from ..infrastructure.di.service_configuration import configure_all_services
from ..infrastructure.mcp import MCPServerAdapter
from ..application import (
    OrchestrateTaskUseCase,
    ManageSpecialistsUseCase,
    TrackProgressUseCase
)

logger = logging.getLogger(__name__)


class MCPServerEntryPoint:
    """
    Clean architecture entry point for the MCP Task Orchestrator server.
    
    This class sets up the entire application stack including:
    - Configuration management
    - Dependency injection container
    - Application use cases
    - MCP server adapter
    """
    
    def __init__(self, config_file_path: Optional[Path] = None):
        self.config_manager = ConfigurationManager(config_file_path)
        self.container: Optional[ServiceContainer] = None
        self.mcp_adapter: Optional[MCPServerAdapter] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging based on configuration."""
        try:
            log_config = self.config_manager.get_log_configuration()
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(log_config['level'])
            
            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Create console handler
            handler = logging.StreamHandler()
            handler.setLevel(log_config['level'])
            
            # Create formatter
            formatter = logging.Formatter(log_config['format'])
            handler.setFormatter(formatter)
            
            root_logger.addHandler(handler)
            
        except Exception as e:
            # Fallback to basic logging
            logging.basicConfig(level=logging.INFO)
            logger.warning(f"Failed to configure logging from config: {e}")
    
    def initialize(self) -> bool:
        """
        Initialize the application using dependency injection.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Check if DI should be enabled
            if not self.config_manager.is_dependency_injection_enabled():
                logger.info("Dependency injection disabled by configuration")
                return False
            
            # Load configuration
            settings = self.config_manager.load_configuration()
            logger.info("Configuration loaded successfully")
            
            # Create and configure DI container
            self.container = ServiceContainer()
            configure_all_services(self.container, settings.__dict__)
            set_container(self.container)
            
            # Get application use cases from container
            orchestrate_use_case = self.container.get_service(OrchestrateTaskUseCase)
            specialist_use_case = self.container.get_service(ManageSpecialistsUseCase)
            progress_use_case = self.container.get_service(TrackProgressUseCase)
            
            # Create MCP server adapter
            self.mcp_adapter = MCPServerAdapter(
                orchestrate_use_case=orchestrate_use_case,
                specialist_use_case=specialist_use_case,
                progress_use_case=progress_use_case
            )
            
            logger.info("Clean architecture initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize clean architecture: {e}")
            return False
    
    async def run(self) -> None:
        """
        Run the MCP server.
        
        This method starts the server and handles the main event loop.
        """
        if not self.mcp_adapter:
            raise RuntimeError("Server not initialized. Call initialize() first.")
        
        try:
            logger.info("Starting MCP Task Orchestrator server...")
            
            # Get the configured MCP server
            server = self.mcp_adapter.get_server()
            
            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                await server.run(
                    read_stream,
                    write_stream,
                    server.create_initialization_options()
                )
            
            logger.info("MCP Task Orchestrator server shutdown gracefully")
            
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        if self.container:
            try:
                self.container.dispose()
                logger.info("DI container disposed successfully")
            except Exception as e:
                logger.error(f"Error disposing DI container: {e}")


async def main_clean_architecture():
    """
    Main entry point using clean architecture.
    
    This function sets up and runs the MCP server using the new
    clean architecture with dependency injection.
    """
    server_entry = MCPServerEntryPoint()
    
    # Try to initialize with clean architecture
    if server_entry.initialize():
        logger.info("Using clean architecture mode")
        await server_entry.run()
    else:
        logger.error("Clean architecture initialization failed")
        raise RuntimeError("Failed to start server with clean architecture")


def main_sync_clean():
    """Synchronous wrapper for clean architecture entry point."""
    asyncio.run(main_clean_architecture())


if __name__ == "__main__":
    main_sync_clean()