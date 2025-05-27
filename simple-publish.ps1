# MCP Task Orchestrator GitHub Publisher
# Simple script to upload your project to GitHub

Write-Host "MCP Task Orchestrator - GitHub Publisher" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$ProjectPath = "E:\My Work\Programming\MCP Task Orchestrator"
$GitHubUrl = "https://github.com/EchoingVesper/mcp-task-orchestrator.git"

# Change to project directory
Set-Location $ProjectPath
Write-Host "Working in: $ProjectPath" -ForegroundColor Green

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
}

# Set up remote
Write-Host "Setting up GitHub remote..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $GitHubUrl

# Fetch and merge
Write-Host "Fetching from GitHub..." -ForegroundColor Yellow
git fetch origin
git checkout -b main origin/main 2>$null
if ($LASTEXITCODE -ne 0) {
    git checkout main 2>$null
    git branch --set-upstream-to=origin/main main 2>$null
}

# Pull any changes
Write-Host "Syncing with remote..." -ForegroundColor Yellow
git pull origin main --allow-unrelated-histories 2>$null

# Add all files
Write-Host "Adding project files..." -ForegroundColor Yellow
git add .

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Complete MCP Task Orchestrator implementation with all modules and documentation"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

# Success message
Write-Host ""
Write-Host "SUCCESS! Repository published!" -ForegroundColor Green
Write-Host "Visit: https://github.com/EchoingVesper/mcp-task-orchestrator" -ForegroundColor Cyan
Write-Host ""

# Open browser
$open = Read-Host "Open repository in browser? (y/n)"
if ($open -eq "y") {
    Start-Process "https://github.com/EchoingVesper/mcp-task-orchestrator"
}

Write-Host "Congratulations on your first public repository!" -ForegroundColor Magenta
