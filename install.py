#!/usr/bin/env python3
"""
MCP Task Orchestrator Universal Installer

A comprehensive installation automation script that manages the complete lifecycle
for the MCP Task Orchestrator project. Supports installation, uninstallation, 
and reinstallation for both end users and developers with comprehensive mode support.

Features:
- Multi-mode support: user, developer, system, and custom installations
- Source flexibility: PyPI, local, git, and version-specific installations  
- Virtual environment management with cross-platform compatibility
- MCP client integration with automatic detection and configuration
- Configuration preservation and backup capabilities
- Industry-standard UX matching modern Python tools

Examples:
  python install.py                          # Project install with auto-detection
  python install.py --dev                    # Developer mode installation
  python install.py --user --clients claude  # User-scoped with specific client
  python install.py --uninstall --purge      # Complete removal
  python install.py --status                 # Check installation status
"""

import sys
import argparse
import signal
from pathlib import Path

# Ensure installer module is importable
sys.path.insert(0, str(Path(__file__).parent))

try:
    from installer import (
        UniversalInstaller, 
        InstallerConfig, 
        InstallationScope,
        InstallationSource,
        OperationType
    )
except ImportError as e:
    print(f"Error: Unable to import installer modules: {e}")
    print("Please ensure you're running this script from the project root directory.")
    sys.exit(1)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="MCP Task Orchestrator Universal Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Project install with auto-detection
  %(prog)s --dev                    # Developer mode installation  
  %(prog)s --user                   # User-scoped installation (~/.local/bin)
  %(prog)s --system                 # System-wide installation (requires admin)
  %(prog)s --venv /custom/path      # Custom virtual environment location
  
  %(prog)s --source pypi            # Force PyPI even for developers
  %(prog)s --source local           # Force local/editable install
  %(prog)s --version 1.4.1          # Specific PyPI version
  %(prog)s --git https://github...  # Git repository install
  
  %(prog)s --clients all            # Configure all detected clients (default)
  %(prog)s --clients claude,cursor  # Specific clients only
  %(prog)s --no-clients             # Skip MCP configuration entirely
  
  %(prog)s --uninstall              # Remove package, preserve config/data
  %(prog)s --uninstall --purge      # Remove everything including .task_orchestrator/
  %(prog)s --uninstall --config     # Remove only configuration files
  
  %(prog)s --reinstall              # Preserve config, clean package install
  %(prog)s --reinstall --clean      # Fresh install, backup then restore config
  %(prog)s --reinstall --force      # Nuclear option, overwrite everything
  
  %(prog)s --update                 # Upgrade existing installation
  %(prog)s --verify                 # Check installation integrity
  %(prog)s --repair                 # Fix broken installations
  %(prog)s --status                 # Show current installation status
  
  %(prog)s --dry-run --verbose      # Show what would be done
  %(prog)s --backup-only            # Create config backup without installing

For detailed documentation, visit:
https://github.com/EchoingVesper/mcp-task-orchestrator
        """.strip()
    )
    
    # Operation modes (mutually exclusive)
    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument(
        "--install", 
        action="store_true", 
        default=True,
        help="Install the package (default operation)"
    )
    operation_group.add_argument(
        "--uninstall", 
        action="store_true",
        help="Uninstall the package"
    )
    operation_group.add_argument(
        "--reinstall", 
        action="store_true",
        help="Reinstall the package (preserves configuration by default)"
    )
    operation_group.add_argument(
        "--update", 
        action="store_true",
        help="Update existing installation to latest version"
    )
    operation_group.add_argument(
        "--verify", 
        action="store_true",
        help="Verify installation integrity and configuration"
    )
    operation_group.add_argument(
        "--repair", 
        action="store_true",
        help="Repair broken installation"
    )
    operation_group.add_argument(
        "--status", 
        action="store_true",
        help="Show current installation status"
    )
    
    # Installation scope (mutually exclusive)
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument(
        "--user", 
        action="store_true",
        help="Install in user-scoped location (~/.local/bin)"
    )
    scope_group.add_argument(
        "--system", 
        action="store_true",
        help="Install system-wide (requires administrator privileges)"
    )
    scope_group.add_argument(
        "--venv", 
        type=Path, 
        metavar="PATH",
        help="Install in custom virtual environment at specified path"
    )
    
    # Installation source options
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        "--source",
        choices=['auto', 'pypi', 'local', 'git'],
        default='auto',
        help="Installation source (default: auto-detect based on environment)"
    )
    source_group.add_argument(
        "--version",
        metavar="VERSION",
        help="Install specific version from PyPI (e.g., '2.0.0')"
    )
    source_group.add_argument(
        "--git",
        metavar="URL", 
        help="Install from git repository URL"
    )
    
    # Development and build options
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Developer mode: editable install + dev dependencies + build tools"
    )
    
    # MCP client configuration
    parser.add_argument(
        "--clients",
        metavar="LIST",
        default="all",
        help="MCP clients to configure: 'all', 'none', or comma-separated list (e.g., 'claude,cursor')"
    )
    parser.add_argument(
        "--no-clients",
        action="store_true", 
        help="Skip MCP client configuration entirely"
    )
    
    # Uninstall options (used with --uninstall)
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Remove all data including configuration and user data (.task_orchestrator/)"
    )
    parser.add_argument(
        "--config",
        action="store_true", 
        help="Remove only configuration files (use with --uninstall)"
    )
    
    # Reinstall options (used with --reinstall)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean install: backup config, fresh install, restore config"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force operation, overwrite existing installations without confirmation"
    )
    
    # Behavior modifiers
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output with detailed progress information"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimize output, show only essential information"
    )
    
    # Backup options
    parser.add_argument(
        "--backup-only",
        action="store_true", 
        help="Create configuration backup without installing"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip automatic backup creation"
    )
    
    # Version information
    parser.add_argument(
        "--version-info",
        action="store_true",
        help="Show installer version and exit"
    )
    
    return parser


def handle_interrupt(signum, frame):
    """Handle keyboard interrupt gracefully."""
    print("\n[yellow]Installation cancelled by user[/yellow]")
    sys.exit(130)


def validate_arguments(args) -> None:
    """Validate command-line arguments for logical consistency."""
    
    # Check conflicting options
    if args.config and not args.uninstall:
        raise ValueError("--config can only be used with --uninstall")
    
    if args.purge and not args.uninstall:
        raise ValueError("--purge can only be used with --uninstall")
    
    if args.clean and not args.reinstall:
        raise ValueError("--clean can only be used with --reinstall")
    
    # Validate scope combinations
    if args.system and args.dev:
        raise ValueError("--system and --dev cannot be used together (use --user for development)")
    
    # Validate client options
    if args.no_clients and args.clients != "all":
        raise ValueError("--no-clients and --clients cannot be used together")
    
    # Validate dry-run combinations
    if args.dry_run and args.backup_only:
        raise ValueError("--dry-run and --backup-only cannot be used together")
    
    # Validate output options
    if args.verbose and args.quiet:
        raise ValueError("--verbose and --quiet cannot be used together")


def setup_console_output(args):
    """Setup console output based on user preferences."""
    try:
        from rich.console import Console
        from rich.logging import RichHandler
        import logging
        
        # Configure console
        console = Console(quiet=args.quiet)
        
        # Configure logging
        log_level = logging.DEBUG if args.verbose else logging.INFO
        if args.quiet:
            log_level = logging.WARNING
            
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, show_path=False)]
        )
        
        return console
    except ImportError:
        # Fallback to basic print if rich is not available
        class BasicConsole:
            def print(self, *args, **kwargs):
                print(*args)
        return BasicConsole()


def main() -> int:
    """Main entry point for the universal installer."""
    
    # Setup signal handling
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        # Parse command-line arguments
        parser = create_argument_parser()
        args = parser.parse_args()
        
        # Handle version information
        if args.version_info:
            print("MCP Task Orchestrator Universal Installer v2.0.0")
            print("https://github.com/EchoingVesper/mcp-task-orchestrator")
            return 0
        
        # Validate arguments
        validate_arguments(args)
        
        # Setup console output
        console = setup_console_output(args)
        
        # Create installer configuration
        config = InstallerConfig.from_args(args)
        
        # Auto-detect optimal settings if not explicitly specified
        config.auto_detect_optimal_settings()
        
        if args.verbose:
            console.print(f"[blue]Configuration:[/blue] {config}")
        
        # Create and execute installer
        installer = UniversalInstaller(config, console)
        return installer.execute()
        
    except KeyboardInterrupt:
        print("\n[yellow]Installation cancelled by user[/yellow]")
        return 130
    except ValueError as e:
        print(f"[red]Error: {e}[/red]")
        return 2
    except Exception as e:
        print(f"[red]Installation failed: {e}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())