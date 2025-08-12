#!/usr/bin/env python3
"""
Auto-reload system for MCP Task Orchestrator.

Detects code changes and automatically reloads the server when modifications are made.
This helps maintain continuous operation during development.
"""

import asyncio
import hashlib
import logging
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class OrchestratorAutoReload:
    """Monitors orchestrator code and auto-reloads on changes."""
    
    def __init__(self, watch_dir: Path = None):
        """Initialize auto-reload monitor.
        
        Args:
            watch_dir: Directory to watch for changes (defaults to orchestrator package)
        """
        self.watch_dir = watch_dir or Path(__file__).parent.parent
        self.file_hashes: Dict[Path, str] = {}
        self.last_reload = None
        self.reload_count = 0
        self.max_reload_frequency = timedelta(seconds=5)  # Prevent reload loops
        self.ignore_patterns = {
            '__pycache__', '.pyc', '.pyo', '.pyd', 
            '.egg-info', '.git', '.pytest_cache'
        }
        
    def _should_watch_file(self, path: Path) -> bool:
        """Check if file should be watched for changes."""
        # Skip ignored patterns
        for pattern in self.ignore_patterns:
            if pattern in str(path):
                return False
                
        # Only watch Python files
        return path.suffix == '.py'
        
    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate hash of file contents."""
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.debug(f"Could not hash {path}: {e}")
            return ""
            
    def _get_watched_files(self) -> Set[Path]:
        """Get all files to watch."""
        watched = set()
        
        for path in self.watch_dir.rglob('*'):
            if path.is_file() and self._should_watch_file(path):
                watched.add(path)
                
        return watched
        
    def detect_changes(self) -> Set[Path]:
        """Detect which files have changed.
        
        Returns:
            Set of paths that have changed
        """
        changed_files = set()
        current_files = self._get_watched_files()
        
        # Check for new or modified files
        for path in current_files:
            current_hash = self._calculate_file_hash(path)
            
            if path not in self.file_hashes:
                # New file
                self.file_hashes[path] = current_hash
                if self.reload_count > 0:  # Don't trigger on initial scan
                    changed_files.add(path)
                    logger.info(f"New file detected: {path}")
            elif self.file_hashes[path] != current_hash:
                # Modified file
                self.file_hashes[path] = current_hash
                changed_files.add(path)
                logger.info(f"File modified: {path}")
                
        # Check for deleted files
        deleted_files = set(self.file_hashes.keys()) - current_files
        for path in deleted_files:
            del self.file_hashes[path]
            changed_files.add(path)
            logger.info(f"File deleted: {path}")
            
        return changed_files
        
    async def reload_server(self) -> bool:
        """Reload the MCP server.
        
        Returns:
            True if reload successful, False otherwise
        """
        # Check reload frequency
        if self.last_reload:
            time_since_reload = datetime.now() - self.last_reload
            if time_since_reload < self.max_reload_frequency:
                logger.warning(
                    f"Skipping reload - too frequent "
                    f"(last reload {time_since_reload.seconds}s ago)"
                )
                return False
                
        try:
            logger.info("Reloading MCP Task Orchestrator...")
            
            # Reinstall package if in development mode
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                capture_output=True,
                text=True,
                cwd=self.watch_dir.parent
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to reinstall package: {result.stderr}")
                return False
                
            # Restart MCP server
            result = subprocess.run(
                ["claude", "mcp", "restart", "task-orchestrator"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to restart MCP server: {result.stderr}")
                return False
                
            self.last_reload = datetime.now()
            self.reload_count += 1
            logger.info(f"Server reloaded successfully (reload #{self.reload_count})")
            return True
            
        except Exception as e:
            logger.error(f"Error during reload: {e}")
            return False
            
    async def monitor(self, check_interval: int = 5):
        """Monitor for changes and auto-reload.
        
        Args:
            check_interval: Seconds between change checks
        """
        logger.info(f"Starting auto-reload monitor for {self.watch_dir}")
        logger.info(f"Watching {len(self._get_watched_files())} files")
        
        # Initial scan to populate hashes
        self.detect_changes()
        
        while True:
            try:
                await asyncio.sleep(check_interval)
                
                changed_files = self.detect_changes()
                
                if changed_files:
                    logger.info(f"Detected {len(changed_files)} file changes")
                    
                    # Only reload for substantive changes
                    if any(not path.name.startswith('test_') for path in changed_files):
                        success = await self.reload_server()
                        
                        if not success:
                            logger.error(
                                "Auto-reload failed - manual intervention may be required"
                            )
                            
            except KeyboardInterrupt:
                logger.info("Auto-reload monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(check_interval)
                

class IntegratedAutoReload:
    """Integrated auto-reload that works with the MCP server."""
    
    @staticmethod
    async def start_monitoring():
        """Start monitoring in background task."""
        monitor = OrchestratorAutoReload()
        
        # Create background task
        asyncio.create_task(monitor.monitor())
        
        logger.info("Auto-reload monitoring started in background")
        
    @staticmethod
    def check_restart_needed() -> bool:
        """Quick check if restart is needed based on git status."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "mcp_task_orchestrator/"],
                capture_output=True,
                text=True
            )
            
            changed_files = result.stdout.strip().split('\n') if result.stdout else []
            python_changes = [f for f in changed_files if f.endswith('.py')]
            
            return len(python_changes) > 0
            
        except Exception:
            return False


# Convenience function for integration
async def enable_auto_reload():
    """Enable auto-reload monitoring for the orchestrator."""
    await IntegratedAutoReload.start_monitoring()


if __name__ == "__main__":
    # Run standalone monitor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    monitor = OrchestratorAutoReload()
    
    try:
        asyncio.run(monitor.monitor())
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")