#!/bin/bash

# Session start script for MCP Task Orchestrator development
# This runs when Claude Code starts or resumes a session

echo "🚀 MCP Task Orchestrator Development Session"
echo "============================================"

# Check Python virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment active"
    echo "   Consider running: source venv/bin/activate"
fi

# Check for required tools
command -v black >/dev/null 2>&1 && echo "✅ black installed" || echo "⚠️  black not found (auto-formatting disabled)"
command -v isort >/dev/null 2>&1 && echo "✅ isort installed" || echo "⚠️  isort not found (import sorting disabled)"
command -v markdownlint >/dev/null 2>&1 && echo "✅ markdownlint installed" || echo "⚠️  markdownlint not found"
command -v pytest >/dev/null 2>&1 && echo "✅ pytest installed" || echo "⚠️  pytest not found"

# Check database status
if [ -f ".task_orchestrator/orchestrator.db" ]; then
    echo "✅ Task orchestrator database found"
    # Could add size check or last modified time here
else
    echo "ℹ️  No task orchestrator database (will be created on first use)"
fi

# Remind about key commands
echo ""
echo "Key Commands:"
echo "  pytest -m unit                  # Run unit tests"
echo "  pytest -m integration           # Run integration tests"
echo "  python tools/diagnostics/health_check.py  # System health check"
echo "  MCP_TASK_ORCHESTRATOR_USE_DI=true python -m mcp_task_orchestrator.server  # Run server"

echo "============================================"
echo "Ready for development! Check CLAUDE.md for guidelines."