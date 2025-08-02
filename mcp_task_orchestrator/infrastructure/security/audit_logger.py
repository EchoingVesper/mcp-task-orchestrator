"""
Security Audit Logging Framework for MCP Task Orchestrator

Implements comprehensive security event logging for audit trails, compliance,
and security monitoring. Follows security-first design principles.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import os

class SecurityEventType(Enum):
    """
    Types of security events that should be logged for audit trails.
    
    Each event type represents a different category of security-relevant
    activity that needs to be tracked for compliance and monitoring.
    """
    
    # Authentication Events
    AUTH_SUCCESS = "authentication_success"
    AUTH_FAILURE = "authentication_failure"
    API_KEY_GENERATED = "api_key_generated"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_EXPIRED = "api_key_expired"
    
    # Authorization Events
    AUTHZ_SUCCESS = "authorization_success"
    AUTHZ_FAILURE = "authorization_failure"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    PERMISSION_DENIED = "permission_denied"
    
    # Input Validation Events
    XSS_DETECTED = "xss_attack_detected"
    PATH_TRAVERSAL_DETECTED = "path_traversal_detected"
    INJECTION_ATTEMPT = "injection_attempt_detected"
    MALICIOUS_INPUT = "malicious_input_detected"
    VALIDATION_FAILURE = "input_validation_failure"
    
    # System Security Events
    SECURITY_VIOLATION = "security_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    UNAUTHORIZED_ACCESS = "unauthorized_access_attempt"
    
    # System Events
    SERVER_START = "server_started"
    SERVER_STOP = "server_stopped"
    MAINTENANCE_MODE = "maintenance_mode_enabled"
    SECURITY_CONFIG_CHANGE = "security_configuration_changed"


class SecurityLevel(Enum):
    """Security event severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAuditLogger:
    """
    Comprehensive security audit logging system.
    
    Provides structured logging of security events with proper formatting,
    secure storage, and integration with monitoring systems.
    """
    
    def __init__(self, log_file_path: Optional[str] = None, 
                 enable_console: bool = False,
                 enable_syslog: bool = False):
        """
        Initialize security audit logger.
        
        Args:
            log_file_path: Path to security audit log file
            enable_console: Whether to also log to console (stderr)
            enable_syslog: Whether to send events to syslog
        """
        # Set up log file path
        if log_file_path:
            self.log_file_path = Path(log_file_path)
        else:
            # Default to workspace-aware location
            workspace_dir = Path.cwd() / ".task_orchestrator"
            workspace_dir.mkdir(parents=True, exist_ok=True)
            self.log_file_path = workspace_dir / "security_audit.log"
        
        # Ensure log directory exists
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger("mcp_task_orchestrator.security.audit")
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Set up file handler with secure permissions
        file_handler = logging.FileHandler(self.log_file_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # JSON formatter for structured logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Set secure file permissions (owner read/write only)
        try:
            os.chmod(self.log_file_path, 0o600)
        except OSError:
            pass  # Best effort - may fail on some systems
        
        # Optional console logging (stderr for MCP compliance)
        if enable_console:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Optional syslog integration
        if enable_syslog:
            try:
                from logging.handlers import SysLogHandler
                syslog_handler = SysLogHandler(address='/dev/log')
                syslog_handler.setLevel(logging.INFO)
                syslog_formatter = logging.Formatter(
                    'mcp_task_orchestrator[%(process)d]: %(message)s'
                )
                syslog_handler.setFormatter(syslog_formatter)
                self.logger.addHandler(syslog_handler)
            except (ImportError, FileNotFoundError):
                # Syslog not available on this system
                pass
        
        # Log initialization
        self.log_event(
            SecurityEventType.SERVER_START,
            SecurityLevel.LOW,
            "Security audit logging initialized",
            {"log_file": str(self.log_file_path)}
        )
    
    def log_event(self, event_type: SecurityEventType, 
                  severity: SecurityLevel,
                  message: str,
                  details: Optional[Dict[str, Any]] = None,
                  user_id: Optional[str] = None,
                  source_ip: Optional[str] = None,
                  user_agent: Optional[str] = None) -> None:
        """
        Log a security event with structured data.
        
        Args:
            event_type: Type of security event
            severity: Severity level of the event
            message: Human-readable event description
            details: Additional structured data about the event
            user_id: User ID associated with the event
            source_ip: Source IP address if available
            user_agent: User agent string if available
        """
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type.value,
            "severity": severity.value,
            "message": message,
            "user_id": user_id,
            "source_ip": source_ip,
            "user_agent": user_agent,
            "process_id": os.getpid(),
            "details": details or {}
        }
        
        # Remove None values for cleaner logs
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        # Convert to JSON string for structured logging
        json_message = json.dumps(log_entry, separators=(',', ':'))
        
        # Log at appropriate level based on severity
        if severity == SecurityLevel.CRITICAL:
            self.logger.critical(json_message)
        elif severity == SecurityLevel.HIGH:
            self.logger.error(json_message)
        elif severity == SecurityLevel.MEDIUM:
            self.logger.warning(json_message)
        else:
            self.logger.info(json_message)
    
    def log_authentication_success(self, user_id: str, 
                                  details: Optional[Dict[str, Any]] = None) -> None:
        """Log successful authentication event."""
        self.log_event(
            SecurityEventType.AUTH_SUCCESS,
            SecurityLevel.LOW,
            f"User authentication successful: {user_id}",
            details,
            user_id=user_id
        )
    
    def log_authentication_failure(self, attempted_user: str,
                                  reason: str,
                                  details: Optional[Dict[str, Any]] = None) -> None:
        """Log failed authentication event."""
        self.log_event(
            SecurityEventType.AUTH_FAILURE,
            SecurityLevel.MEDIUM,
            f"Authentication failed for user: {attempted_user} - {reason}",
            details,
            user_id=attempted_user
        )
    
    def log_authorization_failure(self, user_id: str, 
                                 required_permission: str,
                                 operation: str,
                                 details: Optional[Dict[str, Any]] = None) -> None:
        """Log authorization failure event."""
        self.log_event(
            SecurityEventType.AUTHZ_FAILURE,
            SecurityLevel.MEDIUM,
            f"Authorization denied: user {user_id} lacks {required_permission} for {operation}",
            {**(details or {}), "required_permission": required_permission, "operation": operation},
            user_id=user_id
        )
    
    def log_xss_attempt(self, field_name: str, 
                       details: Optional[Dict[str, Any]] = None,
                       user_id: Optional[str] = None) -> None:
        """Log XSS attack attempt."""
        self.log_event(
            SecurityEventType.XSS_DETECTED,
            SecurityLevel.HIGH,
            f"XSS attack attempt detected in field: {field_name}",
            {**(details or {}), "field_name": field_name},
            user_id=user_id
        )
    
    def log_path_traversal_attempt(self, attempted_path: str,
                                  base_directory: str,
                                  details: Optional[Dict[str, Any]] = None,
                                  user_id: Optional[str] = None) -> None:
        """Log path traversal attack attempt."""
        self.log_event(
            SecurityEventType.PATH_TRAVERSAL_DETECTED,
            SecurityLevel.HIGH,
            f"Path traversal attempt: {attempted_path} outside {base_directory}",
            {
                **(details or {}),
                "attempted_path": attempted_path,
                "base_directory": base_directory
            },
            user_id=user_id
        )
    
    def log_api_key_generated(self, description: str,
                             expires_days: Optional[int] = None,
                             user_id: Optional[str] = None) -> None:
        """Log API key generation event."""
        self.log_event(
            SecurityEventType.API_KEY_GENERATED,
            SecurityLevel.MEDIUM,
            f"API key generated: {description}",
            {"description": description, "expires_days": expires_days},
            user_id=user_id
        )
    
    def log_api_key_revoked(self, description: str,
                           user_id: Optional[str] = None) -> None:
        """Log API key revocation event."""
        self.log_event(
            SecurityEventType.API_KEY_REVOKED,
            SecurityLevel.MEDIUM,
            f"API key revoked: {description}",
            {"description": description},
            user_id=user_id
        )
    
    def log_role_assignment(self, target_user: str, role: str,
                           assigner_user: Optional[str] = None) -> None:
        """Log role assignment event."""
        self.log_event(
            SecurityEventType.ROLE_ASSIGNED,
            SecurityLevel.MEDIUM,
            f"Role {role} assigned to user {target_user}",
            {"target_user": target_user, "role": role},
            user_id=assigner_user
        )
    
    def log_suspicious_activity(self, activity_description: str,
                               details: Optional[Dict[str, Any]] = None,
                               user_id: Optional[str] = None) -> None:
        """Log suspicious activity event."""
        self.log_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            SecurityLevel.HIGH,
            f"Suspicious activity detected: {activity_description}",
            details,
            user_id=user_id
        )
    
    def log_rate_limit_exceeded(self, limit_type: str,
                               threshold: int,
                               current_count: int,
                               user_id: Optional[str] = None) -> None:
        """Log rate limit exceeded event."""
        self.log_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            SecurityLevel.MEDIUM,
            f"Rate limit exceeded: {limit_type} ({current_count}/{threshold})",
            {
                "limit_type": limit_type,
                "threshold": threshold,
                "current_count": current_count
            },
            user_id=user_id
        )
    
    def get_recent_events(self, hours: int = 24,
                         event_types: Optional[List[SecurityEventType]] = None,
                         severity_levels: Optional[List[SecurityLevel]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve recent security events from the log file.
        
        Args:
            hours: Number of hours back to search
            event_types: Filter by specific event types
            severity_levels: Filter by severity levels
            
        Returns:
            List of matching log entries
        """
        if not self.log_file_path.exists():
            return []
        
        events = []
        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    try:
                        # Parse JSON log entry
                        parts = line.strip().split(' - ', 3)
                        if len(parts) >= 4:
                            json_part = parts[3]
                            event = json.loads(json_part)
                            
                            # Parse timestamp
                            event_time = datetime.fromisoformat(
                                event['timestamp'].replace('Z', '+00:00')
                            ).timestamp()
                            
                            # Filter by time
                            if event_time < cutoff_time:
                                continue
                            
                            # Filter by event type
                            if event_types:
                                event_type_values = [et.value for et in event_types]
                                if event.get('event_type') not in event_type_values:
                                    continue
                            
                            # Filter by severity
                            if severity_levels:
                                severity_values = [sl.value for sl in severity_levels]
                                if event.get('severity') not in severity_values:
                                    continue
                            
                            events.append(event)
                    
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Skip malformed log entries
                        continue
        
        except IOError:
            # Log file not accessible
            pass
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return events
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get a summary of recent security events.
        
        Args:
            hours: Number of hours back to analyze
            
        Returns:
            Dictionary with security event statistics
        """
        events = self.get_recent_events(hours)
        
        # Count events by type and severity
        event_type_counts = {}
        severity_counts = {}
        
        for event in events:
            event_type = event.get('event_type', 'unknown')
            severity = event.get('severity', 'unknown')
            
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "period_hours": hours,
            "total_events": len(events),
            "event_types": event_type_counts,
            "severity_levels": severity_counts,
            "recent_critical": len([e for e in events if e.get('severity') == 'critical']),
            "recent_high": len([e for e in events if e.get('severity') == 'high']),
            "auth_failures": event_type_counts.get('authentication_failure', 0),
            "authz_failures": event_type_counts.get('authorization_failure', 0),
            "attack_attempts": (
                event_type_counts.get('xss_attack_detected', 0) +
                event_type_counts.get('path_traversal_detected', 0) +
                event_type_counts.get('injection_attempt_detected', 0)
            )
        }


# Global security audit logger instance
security_audit_logger = SecurityAuditLogger(
    enable_console=False,  # Avoid stdout pollution in MCP mode
    enable_syslog=True     # Enable syslog if available
)

# Convenience functions for common logging operations
def log_auth_success(user_id: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Log authentication success - convenience function."""
    security_audit_logger.log_authentication_success(user_id, details)

def log_auth_failure(user_id: str, reason: str, 
                    details: Optional[Dict[str, Any]] = None) -> None:
    """Log authentication failure - convenience function."""
    security_audit_logger.log_authentication_failure(user_id, reason, details)

def log_authz_failure(user_id: str, permission: str, operation: str,
                     details: Optional[Dict[str, Any]] = None) -> None:
    """Log authorization failure - convenience function."""
    security_audit_logger.log_authorization_failure(user_id, permission, operation, details)

def log_xss_attempt(field_name: str, user_id: Optional[str] = None) -> None:
    """Log XSS attempt - convenience function."""
    security_audit_logger.log_xss_attempt(field_name, user_id=user_id)

def log_path_traversal(path: str, base_dir: str, user_id: Optional[str] = None) -> None:
    """Log path traversal attempt - convenience function."""
    security_audit_logger.log_path_traversal_attempt(path, base_dir, user_id=user_id)

def get_security_summary(hours: int = 24) -> Dict[str, Any]:
    """Get security event summary - convenience function."""
    return security_audit_logger.get_security_summary(hours)