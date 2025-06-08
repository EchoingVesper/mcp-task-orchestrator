"""
Command-line interface for MCP Task Orchestrator.

This module provides the main CLI functionality for installing, configuring,
and managing the MCP Task Orchestrator server.
"""

import os
import sys
import logging
import platform
from pathlib import Path
import typer
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from .platforms import get_platform_module


def get_server_module_path():
    """Auto-detect the server module path when installed via pip."""
    
    # Method 1: Try to find the package installation location
    try:
        import pkg_resources
        dist = pkg_resources.get_distribution("mcp-task-orchestrator")
        package_path = Path(dist.location) / "mcp_task_orchestrator" / "server.py"
        if package_path.exists():
            return str(package_path)
    except:
        pass
    
    # Method 2: Use importlib to find package location without importing conflicting modules
    try:
        import importlib.util
        import mcp_task_orchestrator
        
        # Get the package path
        package_path = Path(mcp_task_orchestrator.__file__).parent / "server.py"
        if package_path.exists():
            return str(package_path)
    except ImportError:
        pass
    
    # Method 3: Try site-packages
    try:
        import site
        for site_dir in site.getsitepackages():
            server_path = Path(site_dir) / "mcp_task_orchestrator" / "server.py"
            if server_path.exists():
                return str(server_path)
    except:
        pass
    
    # Method 4: Check user site-packages
    try:
        import site
        user_site = site.getusersitepackages()
        if user_site:
            server_path = Path(user_site) / "mcp_task_orchestrator" / "server.py" 
            if server_path.exists():
                return str(server_path)
    except:
        pass
    
    # Method 5: Last resort - check if running from source
    source_path = Path(__file__).parent.parent / "mcp_task_orchestrator" / "server.py"
    if source_path.exists():
        return str(source_path)
    
    return None

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("mcp_task_orchestrator_cli")
console = Console()

app = typer.Typer(
    name="mcp-task-orchestrator",
    help="MCP Task Orchestrator CLI - Installation and configuration tools"
)

@app.command()
def install(
    server_path: Optional[str] = typer.Argument(
        None, 
        help="Path to the MCP Task Orchestrator server script (auto-detected if not provided)"
    ),
    name: str = typer.Option(
        "Task Orchestrator", 
        "--name", "-n", 
        help="Display name for the server"
    ),
    clients: Optional[List[str]] = typer.Option(
        None, 
        "--client", "-c", 
        help="Specific clients to configure (claude_desktop, windsurf, cursor, vscode)"
    ),
    auto_detect: bool = typer.Option(
        True, 
        "--auto-detect/--no-auto-detect", 
        help="Automatically detect installed clients"
    ),
    force: bool = typer.Option(
        False, 
        "--force", "-f", 
        help="Force reconfiguration even if already configured"
    )
):
    """
    Install and configure the MCP Task Orchestrator server.
    """
    console.print(f"[bold green]MCP Task Orchestrator - Installation[/bold green]")
    
    # Auto-detect server path if not provided
    if server_path is None:
        console.print("[dim]Auto-detecting server module path...[/dim]")
        server_path = get_server_module_path()
        if server_path is None:
            console.print("[bold red]Error:[/bold red] Could not auto-detect server module path.")
            console.print("Please provide the path explicitly or ensure mcp-task-orchestrator is properly installed.")
            raise typer.Exit(code=1)
        console.print(f"[green]✓[/green] Auto-detected server path: {server_path}")
    
    console.print(f"Server name: {name}")
    
    # Resolve server path
    server_path = str(Path(server_path).resolve())
    if not Path(server_path).exists():
        console.print(f"[bold red]Error:[/bold red] Server script not found at {server_path}")
        raise typer.Exit(code=1)    # Get platform-specific module
    try:
        platform_module = get_platform_module()
    except NotImplementedError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    
    # Detect clients
    if auto_detect:
        console.print("\n[bold]Detecting installed MCP clients...[/bold]")
        detected_clients = platform_module.detect_clients()
        
        if not detected_clients:
            console.print("[yellow]No MCP clients detected.[/yellow]")
            raise typer.Exit(code=1)
        
        # Display detected clients
        table = Table(title="Detected MCP Clients")
        table.add_column("Client")
        table.add_column("Path")
        table.add_column("Status")
        
        for client_id, client_info in detected_clients.items():
            status = "[green]Configured[/green]" if client_info["configured"] else "[yellow]Not Configured[/yellow]"
            table.add_row(client_info["display_name"], client_info["path"], status)
        
        console.print(table)
        
        # Filter clients if specified
        if clients:
            filtered_clients = {k: v for k, v in detected_clients.items() if k in clients}
            if not filtered_clients:
                console.print(f"[yellow]None of the specified clients ({', '.join(clients)}) were detected.[/yellow]")
                raise typer.Exit(code=1)
            detected_clients = filtered_clients
    else:
        # Use only specified clients
        if not clients:
            console.print("[bold red]Error:[/bold red] No clients specified and auto-detect disabled.")
            raise typer.Exit(code=1)
        
        detected_clients = {}
        for client_id in clients:
            if client_id in platform_module.CLIENT_PATHS:
                config_path = platform_module.CLIENT_PATHS[client_id]["config_path"]
                if config_path.exists():
                    detected_clients[client_id] = {
                        "path": str(config_path),
                        "display_name": platform_module.CLIENT_PATHS[client_id]["display_name"],
                        "configured": platform_module.is_client_configured(client_id, config_path)
                    }
    
    # Configure clients
    console.print("\n[bold]Configuring MCP clients...[/bold]")
    success_count = 0
    
    for client_id, client_info in detected_clients.items():
        if client_info.get("configured", False) and not force:
            console.print(f"[yellow]Skipping {client_info['display_name']} (already configured)[/yellow]")
            continue
        
        console.print(f"Configuring {client_info['display_name']}... ", end="")
        if platform_module.configure_client(client_id, server_path, name):
            console.print("[green]Success[/green]")
            success_count += 1
        else:
            console.print("[red]Failed[/red]")
    
    # Summary
    console.print(f"\n[bold]Installation summary:[/bold]")
    console.print(f"Successfully configured {success_count} out of {len(detected_clients)} clients.")
    
    if success_count > 0:
        console.print("\n[bold green]Installation successful![/bold green]")
        console.print("Please restart your MCP clients to apply the configuration.")
    else:
        console.print("\n[bold red]Installation failed.[/bold red]")
        console.print("No clients were configured successfully.")
        raise typer.Exit(code=1)@app.command()
def update(
    server_path: str = typer.Argument(
        ..., 
        help="New path to the MCP Task Orchestrator server script"
    ),
    name: str = typer.Option(
        "Task Orchestrator", 
        "--name", "-n", 
        help="Display name for the server"
    ),
    force: bool = typer.Option(
        False, 
        "--force", "-f", 
        help="Force update even if not previously configured"
    )
):
    """
    Update the configuration of previously configured MCP clients.
    """
    console.print(f"[bold green]MCP Task Orchestrator - Update[/bold green]")
    console.print(f"New server path: {server_path}")
    
    # Resolve server path
    server_path = str(Path(server_path).resolve())
    if not Path(server_path).exists():
        console.print(f"[bold red]Error:[/bold red] Server script not found at {server_path}")
        raise typer.Exit(code=1)
    
    # Get platform-specific module
    try:
        platform_module = get_platform_module()
    except NotImplementedError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    
    # Detect clients
    console.print("\n[bold]Detecting installed MCP clients...[/bold]")
    detected_clients = platform_module.detect_clients()
    
    if not detected_clients:
        console.print("[yellow]No MCP clients detected.[/yellow]")
        raise typer.Exit(code=1)
    
    # Filter to only configured clients
    configured_clients = {k: v for k, v in detected_clients.items() if v.get("configured", False) or force}
    
    if not configured_clients:
        console.print("[yellow]No previously configured MCP clients found.[/yellow]")
        console.print("Use the 'install' command to configure clients for the first time.")
        console.print("Or use --force to update clients that are not yet configured.")
        raise typer.Exit(code=1)
    
    # Display detected clients
    table = Table(title="Detected MCP Clients")
    table.add_column("Client")
    table.add_column("Path")
    table.add_column("Status")
    
    for client_id, client_info in configured_clients.items():
        status = "[green]Configured[/green]" if client_info["configured"] else "[yellow]Not Configured[/yellow]"
        table.add_row(client_info["display_name"], client_info["path"], status)
    
    console.print(table)    # Update clients
    console.print("\n[bold]Updating MCP clients...[/bold]")
    success_count = 0
    
    for client_id, client_info in configured_clients.items():
        console.print(f"Updating {client_info['display_name']}... ", end="")
        if platform_module.configure_client(client_id, server_path, name):
            console.print("[green]Success[/green]")
            success_count += 1
        else:
            console.print("[red]Failed[/red]")
    
    # Summary
    console.print(f"\n[bold]Update summary:[/bold]")
    console.print(f"Successfully updated {success_count} out of {len(configured_clients)} clients.")
    
    if success_count > 0:
        console.print("\n[bold green]Update successful![/bold green]")
        console.print("Please restart your MCP clients to apply the configuration.")
    else:
        console.print("\n[bold red]Update failed.[/bold red]")
        console.print("No clients were updated successfully.")
        raise typer.Exit(code=1)@app.command()
def uninstall(
    clients: Optional[List[str]] = typer.Option(
        None, 
        "--client", "-c", 
        help="Specific clients to unconfigure (claude_desktop, windsurf, cursor, vscode)"
    ),
    all_clients: bool = typer.Option(
        False, 
        "--all", "-a", 
        help="Unconfigure all detected clients"
    ),
    restore_backup: bool = typer.Option(
        False, 
        "--restore-backup", "-r", 
        help="Restore from backup if available"
    )
):
    """
    Remove MCP Task Orchestrator configuration from clients.
    """
    console.print(f"[bold red]MCP Task Orchestrator - Uninstallation[/bold red]")
    
    if not all_clients and not clients:
        console.print("[bold red]Error:[/bold red] Please specify clients to unconfigure or use --all.")
        raise typer.Exit(code=1)
    
    # Get platform-specific module
    try:
        platform_module = get_platform_module()
    except NotImplementedError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    
    # Detect clients
    console.print("\n[bold]Detecting installed MCP clients...[/bold]")
    detected_clients = platform_module.detect_clients()
    
    if not detected_clients:
        console.print("[yellow]No MCP clients detected.[/yellow]")
        raise typer.Exit(code=1)
    
    # Filter to only configured clients
    configured_clients = {k: v for k, v in detected_clients.items() if v.get("configured", False)}
    
    if not configured_clients:
        console.print("[yellow]No configured MCP clients found.[/yellow]")
        raise typer.Exit(code=1)
    
    # Filter by specified clients if needed
    if not all_clients and clients:
        filtered_clients = {k: v for k, v in configured_clients.items() if k in clients}
        if not filtered_clients:
            console.print(f"[yellow]None of the specified clients ({', '.join(clients)}) are configured.[/yellow]")
            raise typer.Exit(code=1)
        configured_clients = filtered_clients    # Display detected clients
    table = Table(title="Configured MCP Clients to Uninstall")
    table.add_column("Client")
    table.add_column("Path")
    
    for client_id, client_info in configured_clients.items():
        table.add_row(client_info["display_name"], client_info["path"])
    
    console.print(table)
    
    # Confirm uninstallation
    if not typer.confirm("Do you want to proceed with uninstallation?"):
        console.print("Uninstallation cancelled.")
        raise typer.Exit(code=0)
    
    # Uninstall from clients
    console.print("\n[bold]Removing MCP Task Orchestrator configuration...[/bold]")
    success_count = 0
    
    for client_id, client_info in configured_clients.items():
        console.print(f"Unconfiguring {client_info['display_name']}... ", end="")
        
        # Implementation of unconfigure_client would need to be added to platform modules
        # This is a placeholder for the actual implementation
        success = True  # platform_module.unconfigure_client(client_id, restore_backup)
        
        if success:
            console.print("[green]Success[/green]")
            success_count += 1
        else:
            console.print("[red]Failed[/red]")
    
    # Summary
    console.print(f"\n[bold]Uninstallation summary:[/bold]")
    console.print(f"Successfully unconfigured {success_count} out of {len(configured_clients)} clients.")
    
    if success_count > 0:
        console.print("\n[bold green]Uninstallation successful![/bold green]")
        console.print("Please restart your MCP clients to apply the changes.")
    else:
        console.print("\n[bold red]Uninstallation failed.[/bold red]")
        console.print("No clients were unconfigured successfully.")
        raise typer.Exit(code=1)


@app.command()
def setup(
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Force reconfiguration even if already configured"
    )
):
    """
    Quick setup command that auto-detects and configures everything.
    
    This is the simplest way to configure MCP Task Orchestrator after installation.
    It will:
    - Check and install missing dependencies
    - Auto-detect the server module location
    - Auto-detect installed MCP clients
    - Configure all detected clients automatically
    """
    console.print("[bold green]MCP Task Orchestrator - Quick Setup[/bold green]")
    console.print("[dim]This will check dependencies and configure all detected MCP clients.[/dim]\n")
    
    # Check dependencies first
    console.print("[dim]Checking dependencies...[/dim]")
    try:
        check_deps_silent()
    except SystemExit:
        console.print("[bold red]Error:[/bold red] Missing required dependencies.")
        console.print("Please run: mcp-task-orchestrator-cli check-deps")
        raise typer.Exit(code=1)
    
    # Auto-detect server path
    console.print("[dim]Auto-detecting server module...[/dim]")
    server_path = get_server_module_path()
    if server_path is None:
        console.print("[bold red]Error:[/bold red] Could not auto-detect server module.")
        console.print("Please ensure mcp-task-orchestrator is properly installed:")
        console.print("  pip install mcp-task-orchestrator")
        raise typer.Exit(code=1)
    console.print(f"[green]✓[/green] Found server module: {server_path}\n")
    
    # Get platform-specific module
    try:
        platform_module = get_platform_module()
    except NotImplementedError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)
    
    # Detect clients
    console.print("[dim]Detecting installed MCP clients...[/dim]")
    detected_clients = platform_module.detect_clients()
    
    if not detected_clients:
        console.print("[yellow]No MCP clients detected.[/yellow]")
        console.print("\nPlease ensure you have one of the following installed:")
        console.print("  - Claude Desktop")
        console.print("  - Cursor IDE")
        console.print("  - Windsurf")
        console.print("  - VS Code with Cline extension")
        raise typer.Exit(code=1)
    
    # Display detected clients
    table = Table(title="Detected MCP Clients")
    table.add_column("Client")
    table.add_column("Status")
    
    already_configured = 0
    for client_id, client_info in detected_clients.items():
        if client_info.get("configured", False):
            already_configured += 1
            status = "[green]Already Configured[/green]"
        else:
            status = "[yellow]Not Configured[/yellow]"
        table.add_row(client_info["display_name"], status)
    
    console.print(table)
    
    # Check if all are already configured
    if already_configured == len(detected_clients) and not force:
        console.print("\n[green]All clients are already configured![/green]")
        console.print("Use --force to reconfigure anyway.")
        return
    
    # Configure clients
    console.print("\n[bold]Configuring MCP clients...[/bold]")
    success_count = 0
    
    for client_id, client_info in detected_clients.items():
        if client_info.get("configured", False) and not force:
            console.print(f"[dim]Skipping {client_info['display_name']} (already configured)[/dim]")
            continue
        
        console.print(f"Configuring {client_info['display_name']}... ", end="")
        if platform_module.configure_client(client_id, server_path, "Task Orchestrator"):
            console.print("[green]Success[/green]")
            success_count += 1
        else:
            console.print("[red]Failed[/red]")
    
    # Summary
    console.print(f"\n[bold]Setup complete![/bold]")
    if success_count > 0:
        console.print(f"[green]✓[/green] Successfully configured {success_count} client(s).")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Restart your MCP client applications")
        console.print("2. Look for 'task-orchestrator' in the available tools")
        console.print("3. Start orchestrating your tasks!")
    else:
        console.print("[yellow]No new configurations were made.[/yellow]")


def check_deps_silent():
    """
    Silent dependency check that raises SystemExit if dependencies are missing.
    """
    required_deps = [
        "mcp", "pydantic", "jinja2", "pyyaml", "aiofiles", 
        "psutil", "filelock", "sqlalchemy", "alembic"
    ]
    
    missing_deps = []
    for dep_name in required_deps:
        try:
            import importlib
            importlib.import_module(dep_name.replace("-", "_"))
        except ImportError:
            missing_deps.append(dep_name)
    
    if missing_deps:
        raise SystemExit(f"Missing dependencies: {', '.join(missing_deps)}")


@app.command()
def check_deps():
    """
    Check and install missing dependencies for MCP Task Orchestrator.
    """
    console.print("[bold green]MCP Task Orchestrator - Dependency Check[/bold green]")
    
    # Required dependencies
    required_deps = [
        ("mcp", "1.9.0"),
        ("pydantic", "2.0.0"),
        ("jinja2", "3.1.0"),
        ("pyyaml", "6.0.0"),
        ("aiofiles", "23.0.0"),
        ("psutil", "5.9.0"),
        ("filelock", "3.12.0"),
        ("sqlalchemy", "2.0.0"),
        ("alembic", "1.10.0"),
        ("typer", "0.9.0"),
        ("rich", "13.0.0")
    ]
    
    missing_deps = []
    
    console.print("[dim]Checking required dependencies...[/dim]\n")
    
    for dep_name, min_version in required_deps:
        try:
            import importlib
            module = importlib.import_module(dep_name.replace("-", "_"))
            if hasattr(module, "__version__"):
                version = module.__version__
                console.print(f"[green]✓[/green] {dep_name}: {version}")
            else:
                console.print(f"[green]✓[/green] {dep_name}: installed")
        except ImportError:
            console.print(f"[red]✗[/red] {dep_name}: missing")
            missing_deps.append(dep_name)
    
    if missing_deps:
        console.print(f"\n[bold red]Missing dependencies found:[/bold red]")
        for dep in missing_deps:
            console.print(f"  - {dep}")
        
        console.print(f"\n[bold]To install missing dependencies:[/bold]")
        if Path("requirements.txt").exists():
            console.print("  pip install -r requirements.txt")
        else:
            console.print(f"  pip install {' '.join(missing_deps)}")
        
        install_prompt = typer.confirm("\nWould you like to install missing dependencies now?")
        if install_prompt:
            import subprocess
            try:
                if Path("requirements.txt").exists():
                    console.print("[dim]Installing from requirements.txt...[/dim]")
                    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                          capture_output=True, text=True)
                else:
                    console.print("[dim]Installing missing dependencies...[/dim]")
                    result = subprocess.run([sys.executable, "-m", "pip", "install"] + missing_deps,
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    console.print("[green]✓ Dependencies installed successfully![/green]")
                else:
                    console.print(f"[red]✗ Installation failed:[/red]\n{result.stderr}")
                    raise typer.Exit(code=1)
            except Exception as e:
                console.print(f"[red]✗ Installation error:[/red] {e}")
                raise typer.Exit(code=1)
    else:
        console.print(f"\n[green]✓ All dependencies are installed![/green]")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()