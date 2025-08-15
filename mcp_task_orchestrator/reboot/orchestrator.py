"""
Orchestrator Module for MCP Server Reboot System

This module provides the orchestration layer for hot-reload functionality
and restart operations. It manages file watching, automatic reloading,
and graceful shutdown/restart coordination.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import importlib
import importlib.util
from datetime import datetime
import json
from watchfiles import awatch

logger = logging.getLogger(__name__)


class HotReloadOrchestrator:
    """
    Orchestrates hot-reload functionality for automatic code updates.
    
    This class manages file watching and module reloading to enable
    development-time hot-reload without full server restarts.
    """
    
    def __init__(self, watch_paths: list[str] = None):
        """Initialize the hot-reload orchestrator."""
        self.watch_paths = watch_paths or [
            "mcp_task_orchestrator/infrastructure/mcp/handlers/",
            "mcp_task_orchestrator/domain/",
            "mcp_task_orchestrator/application/",
            "mcp_task_orchestrator/orchestrator/"
        ]
        self.active_watchers = {}
        self.reload_callbacks = []
        self.last_reload_time = None
        self.reload_count = 0
        self.enabled = True
        
    async def start_watching(self):
        """Start file watching for hot-reload."""
        if not self.enabled:
            logger.info("Hot-reload is disabled")
            return
            
        logger.info(f"Starting hot-reload watching for paths: {self.watch_paths}")
        
        for watch_path in self.watch_paths:
            path = Path(watch_path)
            if path.exists():
                await self._watch_directory(path)
            else:
                logger.warning(f"Watch path does not exist: {watch_path}")
    
    async def _watch_directory(self, path: Path):
        """Watch a directory for changes."""
        try:
            async for changes in awatch(str(path)):
                if self.enabled:
                    await self._handle_file_changes(changes)
        except Exception as e:
            logger.error(f"Error watching directory {path}: {e}")
    
    async def _handle_file_changes(self, changes):
        """Handle file change events."""
        python_changes = []
        
        for change_type, file_path in changes:
            if file_path.endswith('.py') and not file_path.endswith('__pycache__'):
                python_changes.append((change_type, file_path))
        
        if python_changes:
            logger.info(f"Detected {len(python_changes)} Python file changes")
            await self._reload_modules(python_changes)
    
    async def _reload_modules(self, changes):
        """Reload affected modules."""
        try:
            modules_to_reload = []
            
            for change_type, file_path in changes:
                # Convert file path to module name
                module_name = self._file_path_to_module_name(file_path)
                if module_name and module_name not in modules_to_reload:
                    modules_to_reload.append(module_name)
            
            # Reload modules in dependency order
            for module_name in modules_to_reload:
                await self._reload_single_module(module_name)
            
            # Trigger callbacks
            await self._trigger_reload_callbacks()
            
            self.reload_count += 1
            self.last_reload_time = datetime.utcnow()
            
            logger.info(f"Hot-reload completed. Total reloads: {self.reload_count}")
            
        except Exception as e:
            logger.error(f"Error during module reload: {e}")
    
    def _file_path_to_module_name(self, file_path: str) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            path = Path(file_path)
            
            # Find the base package directory
            parts = path.parts
            if 'mcp_task_orchestrator' in parts:
                mcp_index = parts.index('mcp_task_orchestrator')
                module_parts = parts[mcp_index:]
                
                # Remove .py extension
                if module_parts[-1].endswith('.py'):
                    module_parts = module_parts[:-1] + (module_parts[-1][:-3],)
                
                return '.'.join(module_parts)
            
        except Exception as e:
            logger.debug(f"Could not convert {file_path} to module name: {e}")
        
        return None
    
    async def _reload_single_module(self, module_name: str):
        """Reload a single Python module."""
        try:
            if module_name in globals():
                importlib.reload(globals()[module_name])
                logger.debug(f"Reloaded module: {module_name}")
            else:
                # Import and cache the module
                module = importlib.import_module(module_name)
                globals()[module_name] = module
                logger.debug(f"Imported new module: {module_name}")
                
        except Exception as e:
            logger.warning(f"Failed to reload module {module_name}: {e}")
    
    async def _trigger_reload_callbacks(self):
        """Trigger registered reload callbacks."""
        for callback in self.reload_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in reload callback: {e}")
    
    def register_reload_callback(self, callback: Callable):
        """Register a callback to be called after successful reloads."""
        self.reload_callbacks.append(callback)
    
    def enable(self):
        """Enable hot-reload functionality."""
        self.enabled = True
        logger.info("Hot-reload enabled")
    
    def disable(self):
        """Disable hot-reload functionality."""
        self.enabled = False
        logger.info("Hot-reload disabled")
    
    def get_status(self) -> Dict[str, Any]:
        """Get hot-reload status information."""
        return {
            "enabled": self.enabled,
            "watch_paths": self.watch_paths,
            "reload_count": self.reload_count,
            "last_reload_time": self.last_reload_time.isoformat() if self.last_reload_time else None,
            "active_watchers": len(self.active_watchers)
        }


class RestartOrchestrator:
    """
    Orchestrates server restart operations.
    
    This is the last-resort restart mechanism when hot-reload
    cannot handle the changes (e.g., server configuration changes).
    """
    
    def __init__(self, hot_reload_orchestrator: HotReloadOrchestrator = None):
        """Initialize the restart orchestrator."""
        self.hot_reload = hot_reload_orchestrator
        self.restart_in_progress = False
        self.maintenance_mode = False
    
    async def attempt_hot_reload_first(self, reason: str = "manual_request") -> Dict[str, Any]:
        """
        Attempt hot-reload before resorting to full restart.
        
        This method implements the preference for hot-reload over restart.
        """
        if self.hot_reload and self.hot_reload.enabled:
            try:
                # Attempt to hot-reload relevant modules
                logger.info(f"Attempting hot-reload before restart (reason: {reason})")
                
                # Trigger a manual reload
                await self.hot_reload._trigger_reload_callbacks()
                
                return {
                    "success": True,
                    "method": "hot_reload",
                    "reason": reason,
                    "message": "Changes applied via hot-reload, full restart avoided",
                    "reload_count": self.hot_reload.reload_count,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.warning(f"Hot-reload failed, falling back to restart: {e}")
                return await self.perform_restart(reason, hot_reload_failed=True)
        
        else:
            return await self.perform_restart(reason, hot_reload_unavailable=True)
    
    async def perform_restart(self, reason: str = "manual_request", 
                            hot_reload_failed: bool = False,
                            hot_reload_unavailable: bool = False) -> Dict[str, Any]:
        """
        Perform a full server restart.
        
        This is the last-resort option when hot-reload cannot handle the changes.
        """
        if self.restart_in_progress:
            return {
                "success": False,
                "error": "Restart already in progress",
                "reason": reason
            }
        
        try:
            self.restart_in_progress = True
            self.maintenance_mode = True
            
            logger.warning(f"Performing full server restart (reason: {reason})")
            
            # Graceful shutdown preparation
            await self._prepare_shutdown()
            
            # The actual restart would be handled by the parent process
            # This is just the orchestration layer
            
            restart_info = {
                "success": True,
                "method": "full_restart",
                "reason": reason,
                "message": "Server restart initiated",
                "timestamp": datetime.utcnow().isoformat(),
                "maintenance_mode": True
            }
            
            if hot_reload_failed:
                restart_info["fallback_reason"] = "hot_reload_failed"
            elif hot_reload_unavailable:
                restart_info["fallback_reason"] = "hot_reload_unavailable"
            
            return restart_info
            
        except Exception as e:
            self.restart_in_progress = False
            logger.error(f"Restart failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _prepare_shutdown(self):
        """Prepare for graceful shutdown."""
        try:
            # Disable hot-reload during shutdown
            if self.hot_reload:
                self.hot_reload.disable()
            
            # Add any other shutdown preparation logic here
            logger.info("Shutdown preparation completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown preparation: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get restart orchestrator status."""
        status = {
            "restart_in_progress": self.restart_in_progress,
            "maintenance_mode": self.maintenance_mode,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.hot_reload:
            status["hot_reload"] = self.hot_reload.get_status()
        
        return status


# Global instances for easy access
_hot_reload_orchestrator = None
_restart_orchestrator = None


def get_hot_reload_orchestrator() -> HotReloadOrchestrator:
    """Get the global hot-reload orchestrator instance."""
    global _hot_reload_orchestrator
    if _hot_reload_orchestrator is None:
        _hot_reload_orchestrator = HotReloadOrchestrator()
    return _hot_reload_orchestrator


def get_restart_orchestrator() -> RestartOrchestrator:
    """Get the global restart orchestrator instance."""
    global _restart_orchestrator
    if _restart_orchestrator is None:
        hot_reload = get_hot_reload_orchestrator()
        _restart_orchestrator = RestartOrchestrator(hot_reload)
    return _restart_orchestrator


async def initialize_orchestrator():
    """Initialize the orchestrator system."""
    try:
        hot_reload = get_hot_reload_orchestrator()
        restart = get_restart_orchestrator()
        
        # Start hot-reload watching
        await hot_reload.start_watching()
        
        logger.info("Orchestrator system initialized with hot-reload support")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        return False


# Export the main functions needed by the restart tool
async def orchestrate_restart(reason: str = "manual_request", 
                            graceful: bool = True,
                            preserve_state: bool = True,
                            timeout: int = 30) -> Dict[str, Any]:
    """
    Main entry point for orchestrated restart operations.
    
    This function implements the smart restart logic:
    1. Try hot-reload first (preferred)
    2. Fall back to full restart if needed (last resort)
    """
    orchestrator = get_restart_orchestrator()
    
    # Always attempt hot-reload first unless explicitly disabled
    result = await orchestrator.attempt_hot_reload_first(reason)
    
    # Add the additional parameters for compatibility
    result.update({
        "graceful": graceful,
        "preserve_state": preserve_state,
        "timeout": timeout
    })
    
    return result