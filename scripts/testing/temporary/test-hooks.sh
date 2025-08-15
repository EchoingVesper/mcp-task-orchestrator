#\!/bin/bash
echo "🧪 Testing all Claude Code hooks..."

hooks=(
    ".claude/hooks/session-context.sh"
    ".claude/hooks/git-automation-helper.sh" 
    ".claude/hooks/status-tag-validator.sh"
    ".claude/hooks/file-size-monitor.sh"
    ".claude/hooks/test-reminder.sh"
    ".claude/hooks/todo-tracker.sh"
)

for hook in "${hooks[@]}"; do
    echo "Testing $hook..."
    if bash -n "$hook" 2>/dev/null; then
        echo "✅ $hook - Syntax OK"
    else
        echo "❌ $hook - Syntax Error:"
        bash -n "$hook"
        echo ""
    fi
done
EOF < /dev/null
