#!/bin/bash
# Worktree Development Environment Setup Script
# Usage: ./scripts/setup_worktree.sh <worktree_name>

set -e

WORKTREE_NAME="$1"
if [ -z "$WORKTREE_NAME" ]; then
    echo "Usage: $0 <worktree_name>"
    echo "Available worktrees:"
    git worktree list
    exit 1
fi

WORKTREE_PATH="worktrees/$WORKTREE_NAME"

if [ ! -d "$WORKTREE_PATH" ]; then
    echo "Error: Worktree '$WORKTREE_PATH' does not exist"
    echo "Available worktrees:"
    git worktree list
    exit 1
fi

echo "Setting up development environment for worktree: $WORKTREE_NAME"
echo "Path: $WORKTREE_PATH"

# Navigate to worktree
cd "$WORKTREE_PATH"

echo "✅ Current directory: $(pwd)"
echo "✅ Current branch: $(git branch --show-current)"

# Check Python environment
if command -v python3 &> /dev/null; then
    echo "🐍 Python version: $(python3 --version)"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    echo "🐍 Python version: $(python --version)"
    PYTHON_CMD="python"
else
    echo "⚠️  Python not found in PATH"
    PYTHON_CMD="python3"
fi

# Check if virtual environment should be activated
if [ -f "../../venv/bin/activate" ]; then
    echo "🔧 Virtual environment available at ../../venv/"
    echo "   Run: source ../../venv/bin/activate"
elif [ -f "../../venv_test/bin/activate" ]; then
    echo "🔧 Test virtual environment available at ../../venv_test/"
    echo "   Run: source ../../venv_test/bin/activate"
fi

# Verify orchestrator functionality
echo "🔍 Testing orchestrator import..."
$PYTHON_CMD -c "
import sys
sys.path.append('.')
try:
    from mcp_task_orchestrator.server import app
    print('✅ Orchestrator import successful')
except Exception as e:
    print(f'❌ Orchestrator import failed: {e}')
"

# Check task status
echo "📋 Checking orchestrator task status..."
$PYTHON_CMD -c "
import sys, json
sys.path.append('.')
try:
    import asyncio
    from mcp_task_orchestrator.orchestrator.core import TaskOrchestrator
    from mcp_task_orchestrator.orchestrator.state import StateManager
    
    # This is a simplified check - full status requires async context
    print('✅ Core orchestrator components accessible')
    print('💡 Use MCP tools for full task status check')
except Exception as e:
    print(f'⚠️  Task status check limited: {e}')
"

echo ""
echo "🚀 Worktree '$WORKTREE_NAME' is ready for development!"
echo ""
echo "Next steps:"
echo "1. cd $WORKTREE_PATH"
echo "2. claude"
echo "3. Use MCP tools to execute orchestrator tasks"
echo ""
echo "Available orchestrator tasks for this worktree:"
case "$WORKTREE_NAME" in
    "db-migration")
        echo "   - architect_f74a18: Design migration detection engine"
        echo "   - implementer_8cf1b2: Implement migration execution"
        echo "   - implementer_ade9c3: Server startup integration"
        ;;
    "server-reboot")
        echo "   - architect_9e06a9: Design state serialization"
        echo "   - implementer_a8b5f3: Graceful shutdown implementation"
        echo "   - implementer_dd2297: Restart mechanism"
        ;;
    *)
        echo "   - Check CLAUDE.md for specific task details"
        ;;
esac

echo ""
echo "📖 See CLAUDE.md in the worktree for detailed guidance"