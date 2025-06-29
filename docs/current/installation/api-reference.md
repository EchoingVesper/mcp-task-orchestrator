# Installer & Uninstaller API Reference

## Overview

This document provides comprehensive API reference for the MCP Task Orchestrator installer and uninstaller systems. The installation system provides both command-line interfaces and programmatic APIs for automated deployment scenarios.

## Core Installation Classes

### SecureInstaller

Primary installation class with comprehensive security and cross-platform compatibility.

```python
from mcp_task_orchestrator_cli.secure_installer import SecureInstaller

class SecureInstaller:
    """Secure installer with zero-vulnerability design"""
    
    def __init__(self, config_path: Optional[str] = None, 
                 security_mode: str = "enhanced"):
        """
        Initialize secure installer
        
        Args:
            config_path: Path to custom configuration file
            security_mode: Security level ('standard' or 'enhanced')
        """
```

#### Installation Methods

```python
async def install_single_client(self, client_name: str, 
                               force_backup: bool = True,
                               validate_after: bool = True) -> Dict[str, Any]:
    """
    Install to a single MCP client
    
    Args:
        client_name: Name of MCP client ('claude-desktop', 'cursor', etc.)
        force_backup: Create configuration backup before installation
        validate_after: Validate installation after completion
        
    Returns:
        Installation result with status, paths, and validation info
        
    Raises:
        InstallationError: If installation fails
        ValidationError: If post-installation validation fails
        SecurityError: If security checks fail
    """

async def install_multi_client(self, client_list: List[str],
                              concurrent: bool = True,
                              fail_fast: bool = False) -> Dict[str, Any]:
    """
    Install to multiple MCP clients
    
    Args:
        client_list: List of client names to install to
        concurrent: Install to clients concurrently
        fail_fast: Stop on first failure
        
    Returns:
        Installation results for each client
    """

async def auto_detect_and_install(self, exclude_clients: List[str] = None) -> Dict[str, Any]:
    """
    Auto-detect supported clients and install to all found
    
    Args:
        exclude_clients: List of clients to skip
        
    Returns:
        Installation results for all detected clients
    """
```

#### Security & Validation Methods

```python
def validate_system_requirements(self) -> Dict[str, bool]:
    """Validate system meets installation requirements"""

def check_security_compliance(self) -> Dict[str, Any]:
    """Perform comprehensive security validation"""

def create_installation_backup(self, client_name: str) -> str:
    """Create backup of existing configuration"""

def validate_installation(self, client_name: str) -> Dict[str, Any]:
    """Validate completed installation"""
```

### UniversalInstaller

Batch installation system for enterprise deployments.

```python
from mcp_task_orchestrator_cli.universal_installer import UniversalInstaller

class UniversalInstaller:
    """Universal installer for batch deployments"""
    
    def __init__(self, deployment_config: Optional[Dict] = None):
        """Initialize universal installer with deployment configuration"""

async def batch_install(self, 
                       clients: List[str] = None,
                       deployment_type: str = "standard",
                       rollback_on_failure: bool = True) -> Dict[str, Any]:
    """
    Perform batch installation across multiple clients
    
    Args:
        clients: Specific clients to install (auto-detect if None)
        deployment_type: 'standard', 'enterprise', or 'development'
        rollback_on_failure: Rollback all installations if any fail
        
    Returns:
        Comprehensive deployment results
    """
```

### SecureUninstaller

Surgical precision uninstaller with automatic backups.

```python
from mcp_task_orchestrator_cli.secure_uninstaller import SecureUninstaller

class SecureUninstaller:
    """Secure uninstaller with surgical precision removal"""
    
    def __init__(self, preserve_data: bool = True):
        """Initialize uninstaller with data preservation settings"""

async def uninstall_single_client(self, client_name: str,
                                 create_backup: bool = True,
                                 force_remove: bool = False) -> Dict[str, Any]:
    """
    Remove installation from single client
    
    Args:
        client_name: Target client name
        create_backup: Create backup before removal
        force_remove: Force removal even if validation fails
        
    Returns:
        Uninstallation results and backup information
    """

async def uninstall_all_clients(self, 
                               preserve_backups: bool = True) -> Dict[str, Any]:
    """Remove installation from all detected clients"""

def restore_from_backup(self, backup_path: str, 
                       client_name: str) -> Dict[str, Any]:
    """Restore configuration from backup"""
```

## Cross-Tool Compatibility

### ClientDetector

Client detection and compatibility validation.

```python
from mcp_task_orchestrator_cli.cross_tool_compatibility import ClientDetector

class ClientDetector:
    """Advanced client detection with compatibility validation"""
    
    def detect_all_clients(self) -> Dict[str, Dict[str, Any]]:
        """
        Detect all supported MCP clients
        
        Returns:
            Dict mapping client names to detection results:
            {
                'claude-desktop': {
                    'detected': True,
                    'version': '0.4.1',
                    'config_path': '/path/to/config',
                    'compatible': True,
                    'install_method': 'json_config'
                },
                ...
            }
        """

    def validate_client_compatibility(self, client_name: str) -> Dict[str, Any]:
        """Validate specific client compatibility"""

    def get_client_config_path(self, client_name: str) -> Optional[str]:
        """Get configuration file path for client"""

    def check_client_version(self, client_name: str) -> Optional[str]:
        """Check installed client version"""
```

### CompatibilityValidator

Cross-platform compatibility validation.

```python
from mcp_task_orchestrator_cli.cross_tool_compatibility import CompatibilityValidator

class CompatibilityValidator:
    """Comprehensive compatibility validation"""
    
    def validate_python_environment(self) -> Dict[str, Any]:
        """Validate Python version and environment"""

    def validate_platform_support(self) -> Dict[str, Any]:
        """Validate operating system and platform support"""

    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required and optional dependencies"""

    def generate_compatibility_report(self) -> Dict[str, Any]:
        """Generate comprehensive compatibility report"""
```

## Validation & Backup System

### ValidationBackupSystem

Comprehensive validation and backup management.

```python
from mcp_task_orchestrator_cli.validation_backup_system import ValidationBackupSystem

class ValidationBackupSystem:
    """Advanced validation and backup management"""
    
    def __init__(self, backup_retention: int = 10):
        """Initialize with backup retention policy"""

    def create_comprehensive_backup(self, client_name: str) -> Dict[str, Any]:
        """
        Create comprehensive configuration backup
        
        Returns:
            {
                'backup_id': 'unique_backup_identifier',
                'backup_path': '/path/to/backup',
                'timestamp': '2025-06-13T12:00:00Z',
                'client_name': 'claude-desktop',
                'config_files': ['/path/to/config.json'],
                'validation_hash': 'sha256_hash',
                'backup_size': 1024
            }
        """

    def validate_configuration(self, client_name: str) -> Dict[str, Any]:
        """Validate client configuration integrity"""

    def restore_from_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore configuration from specific backup"""

    def list_available_backups(self, client_name: str = None) -> List[Dict[str, Any]]:
        """List all available backups"""

    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Clean up old backups according to retention policy"""
```

## Command Line Interface

### SecureInstallerCLI

Command-line interface for interactive installation.

```python
from mcp_task_orchestrator_cli.secure_installer_cli import SecureInstallerCLI

class SecureInstallerCLI:
    """Interactive command-line installer"""
    
    def run_interactive_installation(self) -> None:
        """Run interactive installation wizard"""

    def run_batch_installation(self, args: argparse.Namespace) -> None:
        """Run batch installation from command line arguments"""
```

#### CLI Arguments

```bash
# Interactive mode (default)
python -m mcp_task_orchestrator_cli.secure_installer_cli

# Batch mode with specific clients
python -m mcp_task_orchestrator_cli.secure_installer_cli \
    --batch \
    --clients claude-desktop,cursor \
    --force-backup \
    --validate

# Development mode
python -m mcp_task_orchestrator_cli.secure_installer_cli \
    --dev \
    --enhanced-security \
    --verbose

# Enterprise deployment
python -m mcp_task_orchestrator_cli.secure_installer_cli \
    --deployment-type enterprise \
    --config-file /path/to/enterprise.json \
    --audit-log /path/to/audit.log
```

#### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--batch` | Non-interactive batch mode | Interactive |
| `--clients` | Comma-separated client list | Auto-detect |
| `--force-backup` | Force backup creation | True |
| `--validate` | Validate after installation | True |
| `--dev` | Development mode with debug logging | False |
| `--enhanced-security` | Enhanced security mode | Standard |
| `--verbose` | Verbose output | False |
| `--config-file` | Custom configuration file | Default |
| `--deployment-type` | Deployment type (standard/enterprise) | Standard |
| `--audit-log` | Audit log file path | None |

## Configuration Schema

### Installation Configuration

```json
{
  "installation": {
    "security_mode": "enhanced",
    "backup_retention": 10,
    "validation_level": "comprehensive",
    "deployment_type": "enterprise",
    "concurrent_installs": true,
    "fail_fast": false
  },
  "clients": {
    "claude-desktop": {
      "enabled": true,
      "auto_detect": true,
      "config_path": "/custom/path/config.json",
      "backup_before_install": true,
      "validate_after_install": true
    },
    "cursor": {
      "enabled": true,
      "auto_detect": true
    }
  },
  "security": {
    "input_validation": true,
    "permission_checks": true,
    "audit_logging": true,
    "backup_encryption": false
  },
  "performance": {
    "max_concurrent_installs": 6,
    "install_timeout": 300,
    "validation_timeout": 60
  }
}
```

### Client Configuration Schema

```json
{
  "client_name": "claude-desktop",
  "detection_result": {
    "detected": true,
    "version": "0.4.1",
    "config_path": "/Users/user/.config/claude/config.json",
    "compatible": true,
    "install_method": "json_config"
  },
  "installation_result": {
    "success": true,
    "installed_at": "2025-06-13T12:00:00Z",
    "backup_created": true,
    "backup_path": "/path/to/backup",
    "validation_passed": true,
    "config_changes": {
      "added_servers": 1,
      "modified_settings": []
    }
  }
}
```

## Error Handling

### Exception Classes

```python
class InstallationError(Exception):
    """Base installation error"""
    
class SecurityError(InstallationError):
    """Security validation failed"""
    
class ValidationError(InstallationError):
    """Post-installation validation failed"""
    
class CompatibilityError(InstallationError):
    """Client compatibility issue"""
    
class BackupError(InstallationError):
    """Backup operation failed"""
    
class ConfigurationError(InstallationError):
    """Configuration file error"""
```

### Error Response Format

```python
{
    "success": False,
    "error": {
        "code": "INSTALLATION_FAILED",
        "message": "Failed to install to claude-desktop",
        "details": {
            "client": "claude-desktop",
            "phase": "configuration_update",
            "underlying_error": "Permission denied accessing config file"
        },
        "recovery_suggestions": [
            "Check file permissions",
            "Run with elevated privileges",
            "Verify client installation"
        ]
    },
    "partial_results": {
        "backup_created": True,
        "backup_path": "/path/to/backup"
    }
}
```

## Testing API

### Installation Testing

```python
from mcp_task_orchestrator_cli.testing import InstallationTester

class InstallationTester:
    """Comprehensive installation testing"""
    
    def test_client_detection(self) -> Dict[str, Any]:
        """Test client detection accuracy"""

    def test_security_validation(self) -> Dict[str, Any]:
        """Test security compliance"""

    def test_backup_restore_cycle(self, client_name: str) -> Dict[str, Any]:
        """Test backup creation and restoration"""

    def test_installation_rollback(self, client_name: str) -> Dict[str, Any]:
        """Test installation rollback on failure"""

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete installation test suite"""
```

## Performance Monitoring

### Installation Metrics

```python
from mcp_task_orchestrator_cli.monitoring import InstallationMetrics

class InstallationMetrics:
    """Performance monitoring and metrics collection"""
    
    def measure_installation_time(self, client_name: str) -> float:
        """Measure installation duration"""

    def measure_memory_usage(self) -> Dict[str, int]:
        """Measure memory usage during installation"""

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
```

### Benchmark Results

| Operation | Single Client | Multi-Client (6) | Memory Usage |
|-----------|--------------|------------------|--------------|
| Client Detection | < 1 second | < 2 seconds | < 10 MB |
| Security Validation | < 2 seconds | < 5 seconds | < 20 MB |
| Configuration Update | < 2 seconds | < 8 seconds | < 30 MB |
| Backup Creation | < 1 second | < 3 seconds | < 15 MB |
| Full Installation | < 5 seconds | < 15 seconds | < 50 MB |

## Integration Examples

### Programmatic Installation

```python
async def automated_deployment():
    """Example automated deployment script"""
    
    # Initialize installer
    installer = SecureInstaller(security_mode="enhanced")
    
    # Validate system requirements
    requirements = installer.validate_system_requirements()
    if not all(requirements.values()):
        raise Exception("System requirements not met")
    
    # Auto-detect clients
    result = await installer.auto_detect_and_install()
    
    # Validate all installations
    for client, status in result['clients'].items():
        if not status['success']:
            print(f"Installation failed for {client}: {status['error']}")
        else:
            print(f"Successfully installed to {client}")
    
    return result

# Run deployment
import asyncio
result = asyncio.run(automated_deployment())
```

### Custom Client Integration

```python
async def custom_client_install():
    """Example custom client installation"""
    
    detector = ClientDetector()
    installer = SecureInstaller()
    
    # Custom client detection logic
    clients = detector.detect_all_clients()
    priority_clients = ['claude-desktop', 'cursor']
    
    # Install to priority clients first
    for client in priority_clients:
        if client in clients and clients[client]['detected']:
            result = await installer.install_single_client(
                client_name=client,
                force_backup=True,
                validate_after=True
            )
            
            if not result['success']:
                # Handle failure
                print(f"Priority installation failed: {client}")
            else:
                print(f"Priority installation complete: {client}")

# Run custom installation
asyncio.run(custom_client_install())
```

---

**API Version**: 1.0  
**Compatibility**: Python 3.9+, All supported platforms  
**Security**: Zero-vulnerability design with comprehensive validation