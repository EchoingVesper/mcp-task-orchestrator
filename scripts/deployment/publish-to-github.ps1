# MCP Task Orchestrator - GitHub Publishing Script
# This script will complete the upload of your local project to GitHub

param(
    [string]$ProjectPath = "E:\My Work\Programming\MCP Task Orchestrator",
    [string]$GitHubUrl = "https://github.com/EchoingVesper/mcp-task-orchestrator.git"
)

# Store script path for self-deletion
$ScriptPath = $MyInvocation.MyCommand.Path

Write-Host "🚀 MCP Task Orchestrator - GitHub Publishing Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Function to handle errors
function Handle-Error {
    param([string]$ErrorMessage)
    Write-Host "❌ Error: $ErrorMessage" -ForegroundColor Red
    Write-Host ""
    Write-Host "Script failed. Please check the error above and try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Function to run git commands with error handling
function Run-GitCommand {
    param([string]$Command, [string]$Description)
    
    Write-Host "🔄 $Description..." -ForegroundColor Yellow
    
    try {
        $result = Invoke-Expression "git $Command" 2>&1
        if ($LASTEXITCODE -ne 0 -and $Command -notlike "*pull*") {
            throw "Git command failed: git $Command"
        }
        Write-Host "✅ $Description completed" -ForegroundColor Green
        return $result
    }
    catch {
        if ($Command -like "*pull*") {
            Write-Host "⚠️  Pull encountered conflicts - will continue" -ForegroundColor Yellow
        } else {
            Handle-Error "$Description failed: $_"
        }
    }
}

# Check if we're in the project directory
if (-not (Test-Path $ProjectPath)) {
    Handle-Error "Project directory not found: $ProjectPath"
}

Set-Location $ProjectPath

Write-Host "📁 Working in: $ProjectPath" -ForegroundColor Blue
Write-Host ""

# Check if git is available
try {
    git --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Git not found"
    }
    Write-Host "✅ Git is available" -ForegroundColor Green
}
catch {
    Handle-Error "Git is not installed or not in PATH. Please install Git and try again."
}

# Initialize git repository if not already done
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    Run-GitCommand "init" "Git initialization"
    Run-GitCommand "branch -M main" "Setting main branch"
} else {
    Write-Host "📦 Git repository already exists" -ForegroundColor Green
}

# Set up remote origin
Write-Host "🔗 Setting up remote origin..." -ForegroundColor Yellow
try {
    git remote remove origin 2>$null
}
catch {
    # Remote might not exist, that's okay
}
Run-GitCommand "remote add origin $GitHubUrl" "Adding remote origin"

# Fetch from remote to get the current state
Write-Host "📥 Fetching from remote repository..." -ForegroundColor Yellow
Run-GitCommand "fetch origin" "Fetching remote changes"

# Check out main branch and set up tracking
try {
    Run-GitCommand "checkout -b main origin/main" "Setting up main branch tracking"
}
catch {
    # Branch might already exist
    try {
        Run-GitCommand "checkout main" "Switching to main branch"
        Run-GitCommand "branch --set-upstream-to=origin/main main" "Setting upstream tracking"
    }
    catch {
        Write-Host "⚠️  Creating new main branch" -ForegroundColor Yellow
        Run-GitCommand "checkout -b main" "Creating main branch"
    }
}

# Handle potential merge by pulling first
Write-Host "🔄 Syncing with remote repository..." -ForegroundColor Yellow
try {
    git pull origin main --allow-unrelated-histories 2>$null
    Write-Host "✅ Synced with remote" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Will merge manually during commit" -ForegroundColor Yellow
}

# Add all files
Write-Host "📁 Adding all project files..." -ForegroundColor Yellow
Run-GitCommand "add ." "Adding all files to git"

# Check if there are changes to commit
$status = git status --porcelain
if ($status) {
    # Commit the changes
    $commitMessage = "Complete MCP Task Orchestrator implementation - Add orchestrator module with core logic, models, specialists, and state management, CLI tools, configuration, installation scripts, tests and documentation"

    Write-Host "💾 Committing changes..." -ForegroundColor Yellow
    Run-GitCommand "commit -m `"$commitMessage`"" "Committing changes"
    
    # Push to GitHub
    Write-Host "⬆️  Pushing to GitHub..." -ForegroundColor Yellow
    Run-GitCommand "push -u origin main" "Pushing to GitHub"
} else {
    Write-Host "✅ No changes to commit - repository is up to date" -ForegroundColor Green
}

# Success!
Write-Host ""
Write-Host "🎉 SUCCESS! Your MCP Task Orchestrator has been published!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Repository URL: https://github.com/EchoingVesper/mcp-task-orchestrator" -ForegroundColor Cyan
Write-Host "📚 Your first public repository is now live!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your repository on GitHub to see it live" -ForegroundColor White
Write-Host "2. Consider adding topics/tags to help people discover it" -ForegroundColor White
Write-Host "3. Share it with the MCP community!" -ForegroundColor White
Write-Host ""

# Ask user if they want to open the repository in browser
$openBrowser = Read-Host "Would you like to open the repository in your browser? (y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y" -or $openBrowser -eq "yes") {
    Start-Process "https://github.com/EchoingVesper/mcp-task-orchestrator"
}

Write-Host ""
Write-Host "🗑️  Cleaning up - deleting this script..." -ForegroundColor Yellow

# Wait a moment then delete this script
Start-Sleep -Seconds 2

try {
    Remove-Item $ScriptPath -Force
    Write-Host "✅ Script deleted successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Could not delete script automatically. You can manually delete: $ScriptPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎊 Congratulations on your first public repository!" -ForegroundColor Magenta
Read-Host "Press Enter to close"
