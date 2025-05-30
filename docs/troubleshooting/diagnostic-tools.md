# Diagnostic Tools Guide

## Overview
The MCP Task Orchestrator includes comprehensive diagnostic tools to help troubleshoot issues, monitor performance, and maintain system health.

## Available Diagnostic Scripts

### Database Diagnostics (`scripts/diagnostics/`)

#### `diagnose_db.py`
Comprehensive database analysis and health checking.

**Usage:**
```bash
# Basic database health check
python scripts/diagnostics/diagnose_db.py

# Detailed analysis with statistics
python scripts/diagnostics/diagnose_db.py --detailed

# Check for lock issues
python scripts/diagnostics/diagnose_db.py --check-locks

# Force unlock (emergency use only)
python scripts/diagnostics/diagnose_db.py --force-unlock
```

#### `check_status.py`
System status monitoring and basic health checks.

**Usage:**
```bash
# Quick status check
python scripts/diagnostics/check_status.py

# Continuous monitoring (5-second intervals)
python scripts/diagnostics/check_status.py --monitor

# Cleanup stale locks
python scripts/diagnostics/check_status.py --cleanup-locks
```

#### `verify_tools.py`
Verification that all required tools and dependencies are available.

**Usage:**
```bash
# Verify installation
python scripts/diagnostics/verify_tools.py

# Detailed dependency check
python scripts/diagnostics/verify_tools.py --detailed
```

### Server Diagnostics

#### `diagnose_server.py`
Server-specific diagnostic capabilities.
