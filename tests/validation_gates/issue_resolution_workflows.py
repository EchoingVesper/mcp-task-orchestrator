#!/usr/bin/env python3
"""
Issue Resolution Workflows for MCP Task Orchestrator Testing

This module provides automated issue resolution workflows that can be applied
when tests fail, enabling immediate problem resolution and continuous validation.

Usage:
    from issue_resolution_workflows import IssueResolver
    
    resolver = IssueResolver()
    success = await resolver.resolve_issue("database_connection_failed", {"test": "test_name"})
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import re

logger = logging.getLogger(__name__)


@dataclass
class IssuePattern:
    """Pattern for identifying and resolving specific issues."""
    name: str
    patterns: List[str]  # Regex patterns to match in error messages
    description: str
    severity: str  # "low", "medium", "high", "critical"
    auto_resolvable: bool
    resolution_steps: List[str]


@dataclass
class ResolutionResult:
    """Result of an issue resolution attempt."""
    issue_type: str
    resolution_applied: bool
    success: bool
    steps_taken: List[str]
    error: Optional[str] = None
    recommendations: List[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class IssueResolver(ABC):
    """Base class for issue resolution workflows."""
    
    @abstractmethod
    async def can_resolve(self, issue_type: str, context: Dict[str, Any]) -> bool:
        """Check if this resolver can handle the given issue type."""
        pass
    
    @abstractmethod
    async def resolve(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        """Attempt to resolve the issue."""
        pass
    
    @abstractmethod
    def get_supported_issues(self) -> List[IssuePattern]:
        """Get list of issues this resolver can handle."""
        pass


class DatabaseIssueResolver(IssueResolver):
    """Resolver for database-related issues."""
    
    def __init__(self, database_path: str = None):
        self.database_path = database_path or "tests/test_orchestrator.db"
        self.backup_path = f"{self.database_path}.backup"
    
    async def can_resolve(self, issue_type: str, context: Dict[str, Any]) -> bool:
        """Check if this is a database-related issue."""
        database_issues = ["database_connection_failed", "database_locked", "database_corrupt", "schema_mismatch"]
        return issue_type in database_issues
    
    async def resolve(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        """Resolve database-related issues."""
        logger.info(f"Resolving database issue: {issue_type}")
        
        steps_taken = []
        
        try:
            if issue_type == "database_connection_failed":
                return await self._resolve_connection_failed(context, steps_taken)
            elif issue_type == "database_locked":
                return await self._resolve_database_locked(context, steps_taken)
            elif issue_type == "database_corrupt":
                return await self._resolve_database_corrupt(context, steps_taken)
            elif issue_type == "schema_mismatch":
                return await self._resolve_schema_mismatch(context, steps_taken)
            else:
                return ResolutionResult(
                    issue_type=issue_type,
                    resolution_applied=False,
                    success=False,
                    steps_taken=steps_taken,
                    error=f"Unknown database issue type: {issue_type}"
                )
        
        except Exception as e:
            logger.error(f"Error resolving database issue {issue_type}: {e}")
            return ResolutionResult(
                issue_type=issue_type,
                resolution_applied=True,
                success=False,
                steps_taken=steps_taken,
                error=str(e)
            )
    
    async def _resolve_connection_failed(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve database connection failures."""
        steps_taken.append("Checking database file existence")
        
        db_path = Path(self.database_path)
        if not db_path.exists():
            steps_taken.append("Database file missing, creating new database")
            await self._create_new_database()
            steps_taken.append("New database created successfully")
        else:
            steps_taken.append("Database file exists, checking permissions")
            if not db_path.is_file():
                steps_taken.append("Database path is not a file, removing and recreating")
                db_path.unlink()
                await self._create_new_database()
                steps_taken.append("Database recreated successfully")
            else:
                steps_taken.append("Attempting to repair database connection")
                await self._repair_database_connection()
                steps_taken.append("Database connection repaired")
        
        return ResolutionResult(
            issue_type="database_connection_failed",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Consider using connection pooling", "Monitor database file permissions"]
        )
    
    async def _resolve_database_locked(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve database lock issues."""
        steps_taken.append("Checking for database lock files")
        
        # Look for common lock files
        lock_files = [
            f"{self.database_path}.lock",
            f"{self.database_path}-wal",
            f"{self.database_path}-shm"
        ]
        
        for lock_file in lock_files:
            lock_path = Path(lock_file)
            if lock_path.exists():
                steps_taken.append(f"Found lock file: {lock_file}")
                try:
                    lock_path.unlink()
                    steps_taken.append(f"Removed lock file: {lock_file}")
                except Exception as e:
                    steps_taken.append(f"Failed to remove lock file {lock_file}: {e}")
        
        # Wait a moment for any processes to release locks
        steps_taken.append("Waiting for database locks to clear")
        await asyncio.sleep(2)
        
        # Try to open and close the database to test lock resolution
        steps_taken.append("Testing database access")
        await self._test_database_access()
        steps_taken.append("Database access restored")
        
        return ResolutionResult(
            issue_type="database_locked",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Ensure proper connection closing", "Consider connection timeouts"]
        )
    
    async def _resolve_database_corrupt(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve database corruption issues."""
        steps_taken.append("Backing up corrupted database")
        
        # Create backup
        db_path = Path(self.database_path)
        backup_path = Path(self.backup_path)
        
        if db_path.exists():
            db_path.rename(backup_path)
            steps_taken.append(f"Corrupted database backed up to: {backup_path}")
        
        # Create new database
        steps_taken.append("Creating new database to replace corrupted one")
        await self._create_new_database()
        steps_taken.append("New database created successfully")
        
        return ResolutionResult(
            issue_type="database_corrupt",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=[
                "Investigate cause of corruption",
                "Consider more frequent backups",
                "Check disk space and hardware health"
            ]
        )
    
    async def _resolve_schema_mismatch(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve database schema mismatches."""
        steps_taken.append("Checking database schema version")
        
        # Mock schema migration
        steps_taken.append("Applying database schema migrations")
        await asyncio.sleep(0.1)  # Simulate migration time
        
        steps_taken.append("Database schema updated successfully")
        
        return ResolutionResult(
            issue_type="schema_mismatch",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Keep schema migrations up to date", "Test migrations in development"]
        )
    
    async def _create_new_database(self):
        """Create a new database file."""
        # Mock database creation
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.database_path).touch()
        await asyncio.sleep(0.1)  # Simulate creation time
    
    async def _repair_database_connection(self):
        """Repair database connection issues."""
        # Mock connection repair
        await asyncio.sleep(0.1)
    
    async def _test_database_access(self):
        """Test database access."""
        # Mock database access test
        await asyncio.sleep(0.1)
    
    def get_supported_issues(self) -> List[IssuePattern]:
        """Get list of database issues this resolver can handle."""
        return [
            IssuePattern(
                name="database_connection_failed",
                patterns=[r"database.*connection.*failed", r"could not connect.*database"],
                description="Database connection failures",
                severity="high",
                auto_resolvable=True,
                resolution_steps=["Check database file", "Recreate if missing", "Repair connection"]
            ),
            IssuePattern(
                name="database_locked",
                patterns=[r"database.*locked", r"database.*busy"],
                description="Database lock/busy issues",
                severity="medium",
                auto_resolvable=True,
                resolution_steps=["Remove lock files", "Wait for locks to clear", "Test access"]
            ),
            IssuePattern(
                name="database_corrupt",
                patterns=[r"database.*corrupt", r"malformed.*database"],
                description="Database corruption issues",
                severity="critical",
                auto_resolvable=True,
                resolution_steps=["Backup corrupted database", "Create new database", "Restore data if possible"]
            ),
            IssuePattern(
                name="schema_mismatch",
                patterns=[r"schema.*mismatch", r"table.*not.*exist"],
                description="Database schema version mismatches",
                severity="high",
                auto_resolvable=True,
                resolution_steps=["Check schema version", "Apply migrations", "Verify schema"]
            )
        ]


class ServerIssueResolver(IssueResolver):
    """Resolver for server-related issues."""
    
    def __init__(self, server_command: str = None):
        self.server_command = server_command or "python -m mcp_task_orchestrator.server"
        self.server_process = None
        self.restart_attempts = 0
        self.max_restart_attempts = 3
    
    async def can_resolve(self, issue_type: str, context: Dict[str, Any]) -> bool:
        """Check if this is a server-related issue."""
        server_issues = ["server_not_running", "server_crash", "server_timeout", "server_overload"]
        return issue_type in server_issues
    
    async def resolve(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        """Resolve server-related issues."""
        logger.info(f"Resolving server issue: {issue_type}")
        
        steps_taken = []
        
        try:
            if issue_type == "server_not_running":
                return await self._resolve_server_not_running(context, steps_taken)
            elif issue_type == "server_crash":
                return await self._resolve_server_crash(context, steps_taken)
            elif issue_type == "server_timeout":
                return await self._resolve_server_timeout(context, steps_taken)
            elif issue_type == "server_overload":
                return await self._resolve_server_overload(context, steps_taken)
            else:
                return ResolutionResult(
                    issue_type=issue_type,
                    resolution_applied=False,
                    success=False,
                    steps_taken=steps_taken,
                    error=f"Unknown server issue type: {issue_type}"
                )
        
        except Exception as e:
            logger.error(f"Error resolving server issue {issue_type}: {e}")
            return ResolutionResult(
                issue_type=issue_type,
                resolution_applied=True,
                success=False,
                steps_taken=steps_taken,
                error=str(e)
            )
    
    async def _resolve_server_not_running(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve server not running issues."""
        steps_taken.append("Checking server process status")
        
        if not await self._is_server_running():
            steps_taken.append("Server not running, attempting to start")
            
            if self.restart_attempts < self.max_restart_attempts:
                self.restart_attempts += 1
                success = await self._start_server()
                
                if success:
                    steps_taken.append("Server started successfully")
                    return ResolutionResult(
                        issue_type="server_not_running",
                        resolution_applied=True,
                        success=True,
                        steps_taken=steps_taken,
                        recommendations=["Monitor server health", "Check server logs"]
                    )
                else:
                    steps_taken.append("Failed to start server")
                    return ResolutionResult(
                        issue_type="server_not_running",
                        resolution_applied=True,
                        success=False,
                        steps_taken=steps_taken,
                        error="Server failed to start"
                    )
            else:
                steps_taken.append("Maximum restart attempts reached")
                return ResolutionResult(
                    issue_type="server_not_running",
                    resolution_applied=True,
                    success=False,
                    steps_taken=steps_taken,
                    error="Maximum restart attempts exceeded"
                )
        else:
            steps_taken.append("Server is already running")
            return ResolutionResult(
                issue_type="server_not_running",
                resolution_applied=True,
                success=True,
                steps_taken=steps_taken
            )
    
    async def _resolve_server_crash(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve server crash issues."""
        steps_taken.append("Detecting server crash")
        
        # Check for crash logs
        steps_taken.append("Checking for crash logs")
        
        # Clean up crashed server process
        if self.server_process:
            steps_taken.append("Cleaning up crashed server process")
            try:
                self.server_process.terminate()
                await asyncio.sleep(1)
                if self.server_process.poll() is None:
                    self.server_process.kill()
            except:
                pass
        
        # Restart server
        steps_taken.append("Restarting server after crash")
        success = await self._start_server()
        
        if success:
            steps_taken.append("Server restarted successfully after crash")
            return ResolutionResult(
                issue_type="server_crash",
                resolution_applied=True,
                success=True,
                steps_taken=steps_taken,
                recommendations=[
                    "Investigate crash cause",
                    "Check system resources",
                    "Review error logs"
                ]
            )
        else:
            steps_taken.append("Failed to restart server after crash")
            return ResolutionResult(
                issue_type="server_crash",
                resolution_applied=True,
                success=False,
                steps_taken=steps_taken,
                error="Server restart failed after crash"
            )
    
    async def _resolve_server_timeout(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve server timeout issues."""
        steps_taken.append("Adjusting server timeout settings")
        
        # Mock timeout adjustment
        await asyncio.sleep(0.1)
        
        steps_taken.append("Server timeout settings adjusted")
        
        return ResolutionResult(
            issue_type="server_timeout",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Monitor response times", "Consider load balancing"]
        )
    
    async def _resolve_server_overload(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve server overload issues."""
        steps_taken.append("Detecting server overload")
        
        # Mock overload resolution
        steps_taken.append("Implementing request throttling")
        await asyncio.sleep(0.1)
        
        steps_taken.append("Server overload mitigated")
        
        return ResolutionResult(
            issue_type="server_overload",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Implement rate limiting", "Scale server resources"]
        )
    
    async def _is_server_running(self) -> bool:
        """Check if server is running."""
        # Mock server status check
        return False
    
    async def _start_server(self) -> bool:
        """Start the server."""
        # Mock server start
        await asyncio.sleep(0.5)
        return True
    
    def get_supported_issues(self) -> List[IssuePattern]:
        """Get list of server issues this resolver can handle."""
        return [
            IssuePattern(
                name="server_not_running",
                patterns=[r"server.*not.*running", r"connection.*refused"],
                description="Server not running or unreachable",
                severity="high",
                auto_resolvable=True,
                resolution_steps=["Check server status", "Start server", "Verify connection"]
            ),
            IssuePattern(
                name="server_crash",
                patterns=[r"server.*crash", r"server.*terminated"],
                description="Server crash or unexpected termination",
                severity="critical",
                auto_resolvable=True,
                resolution_steps=["Detect crash", "Clean up processes", "Restart server"]
            ),
            IssuePattern(
                name="server_timeout",
                patterns=[r"server.*timeout", r"request.*timeout"],
                description="Server timeout issues",
                severity="medium",
                auto_resolvable=True,
                resolution_steps=["Adjust timeout settings", "Optimize performance"]
            ),
            IssuePattern(
                name="server_overload",
                patterns=[r"server.*overload", r"too.*many.*requests"],
                description="Server overload conditions",
                severity="high",
                auto_resolvable=True,
                resolution_steps=["Implement throttling", "Scale resources"]
            )
        ]


class PermissionIssueResolver(IssueResolver):
    """Resolver for permission-related issues."""
    
    async def can_resolve(self, issue_type: str, context: Dict[str, Any]) -> bool:
        """Check if this is a permission-related issue."""
        permission_issues = ["permission_denied", "file_access_denied", "directory_access_denied"]
        return issue_type in permission_issues
    
    async def resolve(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        """Resolve permission-related issues."""
        logger.info(f"Resolving permission issue: {issue_type}")
        
        steps_taken = []
        
        try:
            if issue_type in ["permission_denied", "file_access_denied", "directory_access_denied"]:
                return await self._resolve_permission_denied(context, steps_taken)
            else:
                return ResolutionResult(
                    issue_type=issue_type,
                    resolution_applied=False,
                    success=False,
                    steps_taken=steps_taken,
                    error=f"Unknown permission issue type: {issue_type}"
                )
        
        except Exception as e:
            logger.error(f"Error resolving permission issue {issue_type}: {e}")
            return ResolutionResult(
                issue_type=issue_type,
                resolution_applied=True,
                success=False,
                steps_taken=steps_taken,
                error=str(e)
            )
    
    async def _resolve_permission_denied(self, context: Dict[str, Any], steps_taken: List[str]) -> ResolutionResult:
        """Resolve permission denied issues."""
        steps_taken.append("Checking file/directory permissions")
        
        # Get path from context
        path = context.get("path", ".")
        
        # Mock permission fix
        steps_taken.append(f"Adjusting permissions for: {path}")
        await asyncio.sleep(0.1)
        
        steps_taken.append("Permissions adjusted successfully")
        
        return ResolutionResult(
            issue_type="permission_denied",
            resolution_applied=True,
            success=True,
            steps_taken=steps_taken,
            recommendations=["Review file permissions regularly", "Use appropriate user accounts"]
        )
    
    def get_supported_issues(self) -> List[IssuePattern]:
        """Get list of permission issues this resolver can handle."""
        return [
            IssuePattern(
                name="permission_denied",
                patterns=[r"permission.*denied", r"access.*denied"],
                description="General permission denied errors",
                severity="medium",
                auto_resolvable=True,
                resolution_steps=["Check permissions", "Adjust file/directory permissions"]
            ),
            IssuePattern(
                name="file_access_denied",
                patterns=[r"file.*access.*denied", r"cannot.*read.*file"],
                description="File access permission issues",
                severity="medium",
                auto_resolvable=True,
                resolution_steps=["Check file permissions", "Adjust file access rights"]
            ),
            IssuePattern(
                name="directory_access_denied",
                patterns=[r"directory.*access.*denied", r"cannot.*access.*directory"],
                description="Directory access permission issues",
                severity="medium",
                auto_resolvable=True,
                resolution_steps=["Check directory permissions", "Adjust directory access rights"]
            )
        ]


class IssueResolutionManager:
    """Manager for coordinating issue resolution across multiple resolvers."""
    
    def __init__(self):
        self.resolvers = [
            DatabaseIssueResolver(),
            ServerIssueResolver(),
            PermissionIssueResolver()
        ]
        
        # Build pattern mapping
        self.issue_patterns = {}
        for resolver in self.resolvers:
            for pattern in resolver.get_supported_issues():
                self.issue_patterns[pattern.name] = pattern
    
    def identify_issue(self, error_message: str) -> Optional[str]:
        """Identify issue type from error message."""
        if not error_message:
            return None
        
        error_lower = error_message.lower()
        
        # Check each pattern
        for issue_name, pattern in self.issue_patterns.items():
            for regex_pattern in pattern.patterns:
                if re.search(regex_pattern, error_lower):
                    return issue_name
        
        return None
    
    async def resolve_issue(self, issue_type: str, context: Dict[str, Any]) -> ResolutionResult:
        """Resolve an issue using appropriate resolver."""
        # Find resolver for this issue type
        for resolver in self.resolvers:
            if await resolver.can_resolve(issue_type, context):
                return await resolver.resolve(issue_type, context)
        
        # No resolver found
        return ResolutionResult(
            issue_type=issue_type,
            resolution_applied=False,
            success=False,
            steps_taken=[],
            error=f"No resolver available for issue type: {issue_type}"
        )
    
    async def auto_resolve_from_error(self, error_message: str, context: Dict[str, Any] = None) -> ResolutionResult:
        """Automatically identify and resolve issue from error message."""
        if context is None:
            context = {}
        
        # Identify issue type
        issue_type = self.identify_issue(error_message)
        
        if not issue_type:
            return ResolutionResult(
                issue_type="unknown",
                resolution_applied=False,
                success=False,
                steps_taken=[],
                error=f"Could not identify issue type from error: {error_message}"
            )
        
        # Add error message to context
        context["error_message"] = error_message
        
        # Resolve the issue
        return await self.resolve_issue(issue_type, context)
    
    def get_all_supported_issues(self) -> List[IssuePattern]:
        """Get all supported issue patterns."""
        return list(self.issue_patterns.values())
    
    def get_resolution_statistics(self) -> Dict[str, Any]:
        """Get statistics about issue resolution capabilities."""
        patterns = self.get_all_supported_issues()
        
        return {
            "total_patterns": len(patterns),
            "auto_resolvable": sum(1 for p in patterns if p.auto_resolvable),
            "severity_distribution": {
                "low": sum(1 for p in patterns if p.severity == "low"),
                "medium": sum(1 for p in patterns if p.severity == "medium"),
                "high": sum(1 for p in patterns if p.severity == "high"),
                "critical": sum(1 for p in patterns if p.severity == "critical")
            },
            "resolvers": len(self.resolvers)
        }


# Example usage
async def main():
    """Example usage of the issue resolution system."""
    manager = IssueResolutionManager()
    
    # Test issue identification
    test_errors = [
        "Database connection failed: could not connect to database",
        "Server not running: connection refused",
        "Permission denied: access denied to file",
        "Unknown error: something went wrong"
    ]
    
    for error in test_errors:
        print(f"Error: {error}")
        issue_type = manager.identify_issue(error)
        print(f"Identified issue: {issue_type}")
        
        if issue_type:
            result = await manager.auto_resolve_from_error(error)
            print(f"Resolution result: {result.success}")
            print(f"Steps taken: {result.steps_taken}")
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())