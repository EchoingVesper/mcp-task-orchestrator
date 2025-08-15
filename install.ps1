#
# MCP Task Orchestrator Universal Installer - PowerShell Wrapper
#
# This script provides single-line installation capability for Windows systems.
# It automatically detects Python and runs the universal installer.
#
# Usage:
#   .\install.ps1 [options]
#   iex (iwr https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.ps1)
#   irm https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.ps1 | iex
#

param(
    [switch]$Dev,
    [switch]$User,  
    [switch]$System,
    [string]$Clients = "",
    [switch]$NoClients,
    [switch]$DryRun,
    [switch]$Verbose,
    [switch]$Help
)

# Configuration
$script:ProjectName = "MCP Task Orchestrator"
$script:RepoUrl = "https://github.com/EchoingVesper/mcp-task-orchestrator"
$script:InstallerUrl = "https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.py"

# Error handling
$ErrorActionPreference = "Stop"

# Utility functions
function Write-Log {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Show-Help {
    Write-Host @"

$script:ProjectName Universal Installer

USAGE:
    .\install.ps1 [OPTIONS]

OPTIONS:
    -Dev                Developer mode installation
    -User               User-scoped installation (~/.local/bin)
    -System             System-wide installation (requires admin)
    -Clients LIST       Configure specific MCP clients (claude,cursor,vscode)
    -NoClients          Skip MCP client configuration
    -DryRun             Show what would be done without making changes
    -Verbose            Enable verbose output
    -Help               Show this help message

EXAMPLES:
    .\install.ps1                   # Standard installation with auto-detection
    .\install.ps1 -Dev              # Developer mode with editable install
    .\install.ps1 -User             # User-scoped installation
    .\install.ps1 -DryRun           # Preview installation without changes

SINGLE-LINE INSTALLATION:
    iex (iwr $script:RepoUrl/install.ps1)
    irm $script:RepoUrl/install.ps1 | iex

For more options and documentation, visit: $script:RepoUrl

"@
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Find-Python {
    Write-Log "Detecting Python installation..."
    
    # List of Python commands to try in order of preference
    $pythonCommands = @(
        "python3.12", "python3.11", "python3.10", "python3.9", "python3.8",
        "python3", "python", "py"
    )
    
    foreach ($cmd in $pythonCommands) {
        try {
            $pythonPath = Get-Command $cmd -ErrorAction SilentlyContinue
            if ($pythonPath) {
                # Test if this Python version is compatible (3.8+)
                $versionCheck = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}'); exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $version = & $cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>$null
                    Write-Log "Using Python $version at $($pythonPath.Source)"
                    return $cmd
                }
            }
        }
        catch {
            continue
        }
    }
    
    Write-Error "No compatible Python interpreter found."
    Write-Error "Python 3.8 or higher is required."
    Write-Error "Please install Python from https://python.org and try again."
    exit 1
}

function Get-Installer {
    param([string]$InstallerPath)
    
    Write-Log "Downloading universal installer..."
    
    try {
        if (Get-Command Invoke-WebRequest -ErrorAction SilentlyContinue) {
            Invoke-WebRequest -Uri $script:InstallerUrl -OutFile $InstallerPath -UseBasicParsing
        }
        elseif (Get-Command Invoke-RestMethod -ErrorAction SilentlyContinue) {
            $content = Invoke-RestMethod -Uri $script:InstallerUrl
            $content | Out-File -FilePath $InstallerPath -Encoding utf8
        }
        else {
            Write-Error "Unable to download installer. PowerShell web cmdlets not available."
            exit 1
        }
        
        if (-not (Test-Path $InstallerPath)) {
            Write-Error "Failed to download installer from $script:InstallerUrl"
            exit 1
        }
        
        Write-Success "Downloaded installer successfully"
    }
    catch {
        Write-Error "Failed to download installer: $($_.Exception.Message)"
        exit 1
    }
}

function Test-Requirements {
    Write-Log "Checking system requirements..."
    
    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        Write-Warning "PowerShell 5.0+ recommended. Current version: $psVersion"
    }
    
    # Check for package managers
    $hasPackageManager = $false
    
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        $hasPackageManager = $true
    }
    elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
        $hasPackageManager = $true
    }
    
    if (-not $hasPackageManager) {
        Write-Error "No Python package manager (pip) found."
        Write-Error "Please ensure Python is properly installed with pip."
        exit 1
    }
    
    # Check for admin privileges if system install requested
    if ($System -and -not (Test-AdminPrivileges)) {
        Write-Error "System-wide installation requires administrator privileges."
        Write-Error "Please run PowerShell as Administrator or use -User instead."
        exit 1
    }
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -lt 10) {
        Write-Warning "Windows 10+ recommended. Current version: $osVersion"
    }
}

function Invoke-Installer {
    param(
        [string]$PythonCmd,
        [string]$InstallerPath,
        [string[]]$Arguments
    )
    
    Write-Log "Running $script:ProjectName installer..."
    
    try {
        # Execute the installer with all provided arguments
        $process = Start-Process -FilePath $PythonCmd -ArgumentList @($InstallerPath) + $Arguments -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Success "Installation completed successfully!"
        }
        else {
            Write-Error "Installation failed with exit code $($process.ExitCode)"
            exit $process.ExitCode
        }
    }
    catch {
        Write-Error "Failed to run installer: $($_.Exception.Message)"
        exit 1
    }
}

function Remove-TempFile {
    param([string]$FilePath)
    
    if ($FilePath -and (Test-Path $FilePath) -and $FilePath.StartsWith($env:TEMP)) {
        try {
            Remove-Item $FilePath -Force -ErrorAction SilentlyContinue
        }
        catch {
            # Ignore cleanup errors
        }
    }
}

function Main {
    # Show help if requested
    if ($Help) {
        Show-Help
        exit 0
    }
    
    # Show banner
    Write-Host ""
    Write-Host "================================" -ForegroundColor Blue
    Write-Host " $script:ProjectName" -ForegroundColor Blue
    Write-Host " Universal Installer" -ForegroundColor Blue
    Write-Host "================================" -ForegroundColor Blue
    Write-Host ""
    
    # Check if we're in the project directory
    $needDownload = $false
    $installerPath = ""
    
    if ((Test-Path ".\install.py") -and (Test-Path ".\pyproject.toml")) {
        Write-Log "Using local installer from project directory"
        $installerPath = ".\install.py"
    }
    else {
        Write-Log "Downloading installer from repository"
        $installerPath = Join-Path $env:TEMP "install.py"
        $needDownload = $true
    }
    
    try {
        # Perform pre-installation checks
        Test-Requirements
        
        # Detect Python
        $pythonCmd = Find-Python
        
        # Download installer if needed
        if ($needDownload) {
            Get-Installer -InstallerPath $installerPath
        }
        
        # Build arguments for the installer
        $installerArgs = @()
        
        if ($Dev) { $installerArgs += "--dev" }
        if ($User) { $installerArgs += "--user" }
        if ($System) { $installerArgs += "--system" }
        if ($Clients) { $installerArgs += "--clients"; $installerArgs += $Clients }
        if ($NoClients) { $installerArgs += "--no-clients" }
        if ($DryRun) { $installerArgs += "--dry-run" }
        if ($Verbose) { $installerArgs += "--verbose" }
        
        # Run the installer
        Invoke-Installer -PythonCmd $pythonCmd -InstallerPath $installerPath -Arguments $installerArgs
        
        Write-Host ""
        Write-Success "Installation process completed!"
        Write-Log "For more information, visit: $script:RepoUrl"
    }
    finally {
        # Cleanup
        if ($needDownload) {
            Remove-TempFile -FilePath $installerPath
        }
    }
}

# Only run main if script is executed directly (not dot-sourced)
if ($MyInvocation.InvocationName -ne ".") {
    Main
}