
# Universal Installer Guide

The MCP Task Orchestrator Universal Installer provides a comprehensive, industry-standard installation experience that matches the quality and user experience of modern Python tools like pipx, poetry, and uv.

#
# Overview

The universal installer is a single Python script (`install.py`) that handles the complete installation lifecycle:

- **Installation**: Multiple modes (user, developer, system, custom)

- **Source Management**: PyPI, local, git, version-specific installs  

- **Client Configuration**: Automatic MCP client detection and setup

- **Maintenance**: Updates, repairs, verification, uninstallation

- **Platform Support**: Windows, macOS, Linux, WSL

#
# Quick Start

#
## Single-Line Installation

**Unix/Linux/macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.sh | bash
```text

**Windows PowerShell:**
```text
powershell
iex (iwr https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.ps1)

```text

**Direct Python:**
```text
bash
wget https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.py
python install.py

```text

#
## Standard Installation

```text
bash

# Clone or download the repository

git clone https://github.com/EchoingVesper/mcp-task-orchestrator.git
cd mcp-task-orchestrator

# Run installer (auto-detects environment)

python install.py

```text

#
# Installation Modes

#
## Project Scope (Default for Developers)

Creates a virtual environment in the current directory:

```text
bash
python install.py --dev

# Creates: ./venv/ with editable install + dev dependencies

```text

**Features:**

- ✅ Isolated environment

- ✅ Editable/development install

- ✅ All development dependencies

- ✅ Project-specific configuration

#
## User Scope

Installs to user-local directories (no admin required):

```bash
python install.py --user

# Installs to: ~/.local/bin (Unix) or %APPDATA% (Windows)

```text

**Features:**

- ✅ No administrator privileges required

- ✅ Available across all projects

- ✅ Isolated from system Python

- ✅ PATH automatically managed

#
## System Scope

System-wide installation (requires admin):

```bash

# Unix/Linux/macOS

sudo python install.py --system

# Windows (as Administrator)

python install.py --system

```text

**Features:**

- ✅ Available to all users

- ✅ System-wide PATH integration

- ⚠️ Requires administrator privileges

- ⚠️ May conflict with system packages

#
## Custom Virtual Environment

Install to a specific location:

```text
bash
python install.py --venv /path/to/custom/venv

```text

**Features:**

- ✅ Complete control over location

- ✅ Isolated environment

- ✅ Portable installation

- ✅ Custom naming

#
# Installation Sources

#
## Auto-Detection (Default)

The installer automatically chooses the best source:

```text
bash
python install.py

# Developers: Uses local/editable install

# Users: Uses PyPI package

```text

#
## PyPI Package

Install from Python Package Index:

```text
bash
python install.py --source pypi

# Latest stable release

```text

#
## Local/Editable Install

Install from local source code:

```bash
python install.py --source local

# Editable install from current directory

```text

#
## Specific Version

Install a specific PyPI version:

```bash
python install.py --version 2.0.0

# Installs exactly version 2.0.0

```text

#
## Git Repository

Install directly from git:

```bash
python install.py --git https://github.com/EchoingVesper/mcp-task-orchestrator.git

# Installs latest from main branch

```text

#
# MCP Client Configuration

#
## Automatic Detection

The installer automatically detects and configures compatible MCP clients:

```bash
python install.py

# Detects: Claude Desktop, Claude Code, Cursor, Windsurf, VS Code

```text

#
## Specific Clients

Configure only specific clients:

```bash

# Single client

python install.py --clients claude

# Multiple clients

python install.py --clients claude,cursor,vscode

# All detected clients

python install.py --clients all

```text

#
## Skip Client Configuration

Install without configuring any clients:

```text
bash
python install.py --no-clients

# Package only, no MCP configuration

```text

#
# Maintenance Operations

#
## Check Status

View current installation status:

```bash
python install.py --status

# Shows: version, method, location, clients

# Detailed information

python install.py --status --verbose

```text

#
## Update Installation

Update to the latest version:

```text
bash
python install.py --update

# Preserves configuration and data

```text

#
## Verify Installation

Check installation integrity:

```bash
python install.py --verify

# Comprehensive health check

# Detailed verification

python install.py --verify --verbose

```text

#
## Repair Installation

Fix broken installations:

```text
bash
python install.py --repair

# Automatically detects and fixes issues

```text

#
## Uninstall

Remove the installation:

```bash

# Remove package, preserve configuration

python install.py --uninstall

# Remove everything including config/data

python install.py --uninstall --purge

# Remove only configuration files

python install.py --uninstall --config

```text

#
## Reinstall

Clean reinstall while preserving configuration:

```text
bash

# Standard reinstall

python install.py --reinstall

# Clean reinstall (backup -> fresh install -> restore)

python install.py --reinstall --clean

# Force reinstall (overwrite everything)

python install.py --reinstall --force

```text

#
# Advanced Options

#
## Preview Mode

See what would be done without making changes:

```text
bash
python install.py --dry-run --verbose

# Shows planned operations without execution

```text

#
## Backup Operations

```bash

# Create configuration backup only

python install.py --backup-only

# Skip automatic backup creation

python install.py --no-backup

```text

#
## Force Operations

Override safety checks and confirmations:

```text
bash
python install.py --force

# Skips confirmations, overwrites existing installations

```text

#
## Verbose Output

Enable detailed logging:

```bash
python install.py --verbose

# Shows detailed progress and diagnostic information

```text

#
# Platform-Specific Notes

#
## Windows

**PowerShell (Recommended):**

```powershell

# Download and run

iwr https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.ps1 | iex

# Or locally

python install.py --user
```text

**Command Prompt:**
```text
cmd
python install.py --user

```text

**System Installation:**

- Requires "Run as Administrator"

- Automatically handles Windows paths and registry

#
## macOS

**Homebrew Python (Recommended):**
```text
bash

# Install with Homebrew Python

python3 install.py --user

```text

**System Python:**
```text
bash

# Use system Python

python install.py --user

```text

**Notes:**

- M1/M2 Macs fully supported

- Automatically handles Application Support directories

- Homebrew integration when available

#
## Linux

**Modern Distributions:**
```text
bash

# Handles externally-managed environments

python install.py --user

```text

**Development Environment:**
```text
bash

# Project-specific installation

python install.py --dev

```text

**Notes:**

- Supports all major distributions

- Handles externally-managed Python environments (Ubuntu 23.04+)

- Automatic XDG directory compliance

#
## WSL (Windows Subsystem for Linux)

```text
bash

# Full WSL support

python install.py --dev

```text

**Features:**

- Automatically detects WSL environment

- Proper path handling between Windows/Linux

- Client detection works correctly

#
# Troubleshooting

#
## Common Issues

**Python Not Found:**
```text
bash

# Install Python 3.8+ from python.org

# Or use package manager
sudo apt install python3.8  
# Ubuntu/Debian
brew install python@3.8     
# macOS

```text

**Permission Errors:**
```text
bash

# Use user installation instead of system

python install.py --user

# Or run as administrator (Windows)

# Or use sudo (Unix)

```text

**Virtual Environment Corruption:**
```text
bash

# Force recreation

python install.py --force

# Or repair

python install.py --repair

```text

**Network Issues:**
```text
bash

# Use local source if available

python install.py --source local

# Or check network connectivity

```text

#
## Diagnostic Commands

```bash

# Check installation health

python install.py --status --verbose

# Verify all components

python install.py --verify --verbose

# Preview operations

python install.py --dry-run --verbose

# Test client detection

python install.py --dry-run --clients all --verbose

```text

#
## Recovery Procedures

**Corrupted Installation:**
```text
bash

# Step 1: Verify the issue

python install.py --verify

# Step 2: Attempt repair

python install.py --repair

# Step 3: Force reinstall if needed

python install.py --reinstall --force

```text

**Lost Configuration:**
```text
bash

# Check for backups

ls ~/.task_orchestrator.backup.*

# Reinstall with clean configuration

python install.py --reinstall --clean

```text

#
# Integration Examples

#
## Development Workflow

```text
bash

# 1. Clone repository

git clone https://github.com/your-org/your-project.git
cd your-project

# 2. Install MCP Task Orchestrator for development

python /path/to/install.py --dev --clients claude

# 3. Start development

# Task orchestrator is now available in Claude Desktop

```text

#
## CI/CD Pipeline

```text
bash

# Automated installation in CI

curl -fsSL https://raw.githubusercontent.com/EchoingVesper/mcp-task-orchestrator/main/install.py | python - --user --no-clients --force

```text

#
## Production Deployment

```text
bash

# Production server installation

python install.py --system --source pypi --version 2.0.0 --no-clients
```text

#
# Architecture

The universal installer follows clean architecture principles:

- **Presentation Layer**: CLI interface with argparse

- **Application Layer**: Installation orchestration logic  

- **Infrastructure Layer**: Platform-specific implementations

- **Domain Layer**: Core models and business logic

#
## Key Components

- **`install.py`**: Main CLI entry point

- **`installer/core.py`**: Core installation orchestration

- **`installer/environments.py`**: Virtual environment management

- **`installer/sources.py`**: Package source management

- **`installer/clients.py`**: MCP client configuration

- **`installer/validation.py`**: Health checks and verification

#
# Security Considerations

- ✅ **Input Validation**: All user inputs sanitized

- ✅ **Path Safety**: No shell injection vulnerabilities  

- ✅ **Backup Creation**: Automatic configuration backups

- ✅ **Rollback Capability**: Failed installations are rolled back

- ✅ **Permission Checks**: Admin privileges validated before system installs

- ✅ **Network Security**: HTTPS-only downloads with verification

#
# Performance

- **Installation Time**: < 60 seconds for most installations

- **Resource Usage**: < 100MB memory during installation

- **Network Usage**: Minimal, only downloads necessary packages

- **Disk Usage**: Varies by scope (50MB - 200MB typical)

#
# Support

For issues, questions, or feature requests:

- **GitHub Issues**: [Report problems](https://github.com/EchoingVesper/mcp-task-orchestrator/issues)

- **Documentation**: [Full documentation](../README.md)

- **Repository**: [Source code](https://github.com/EchoingVesper/mcp-task-orchestrator)
