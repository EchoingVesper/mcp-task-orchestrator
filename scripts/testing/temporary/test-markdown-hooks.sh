#!/bin/bash
# Test script to validate the markdown linting hook system

echo "🧪 Testing Markdown Lint Detection System"
echo "=========================================="

# Create a test markdown file with linting issues
cat > test-markdown-issues.md << 'EOF'
#
# Test Markdown File with Issues

This file has several markdown linting issues:

#
## Bad Heading Hierarchy

- List item 1
-List item 2 (missing space)
   - Badly indented item

2. Wrong ordered list start
1. Out of sequence

```text
python
print("Code block with wrong language tag")
```




Extra blank lines above (more than 2)

### Another heading with bad hierarchy

This line is too long and will trigger the line length rule if configured properly in the markdownlint configuration file which we have.
EOF

echo "✅ Created test file with linting issues: test-markdown-issues.md"

# Check if markdownlint is installed
if ! command -v markdownlint &> /dev/null; then
    echo "⚠️  markdownlint not found. Installing via npm..."
    if command -v npm &> /dev/null; then
        npm install -g markdownlint-cli
    else
        echo "❌ npm not found. Please install markdownlint manually:"
        echo "   npm install -g markdownlint-cli"
        exit 1
    fi
fi

echo "✅ markdownlint is available"

# Test the hook directly
echo ""
echo "🔧 Testing markdown lint detector hook..."
./.claude/hooks/markdown-lint-detector.sh

# Check if tasks were created
if [[ -d ".task_orchestrator/markdown_fixes" ]]; then
    task_count=$(find .task_orchestrator/markdown_fixes -name "*.json" | wc -l)
    echo "✅ Task directory exists"
    echo "📋 Created $task_count markdown fix task(s)"
    
    # Show task details
    if [[ $task_count -gt 0 ]]; then
        echo ""
        echo "📝 Task Details:"
        for task_file in .task_orchestrator/markdown_fixes/*.json; do
            if [[ -f "$task_file" ]]; then
                echo "   └─ $(basename "$task_file")"
                jq -r '"\(.file_path): \(.issues | length) issues"' "$task_file" 2>/dev/null || echo "   └─ Task file created"
            fi
        done
    fi
else
    echo "❌ Task directory not created"
fi

echo ""
echo "🎯 Test Commands:"
echo "   claude fix-markdown          # Fix one file at a time"  
echo "   claude fix-markdown-batch    # Process all pending fixes"
echo ""
echo "🧹 Cleanup:"
echo "   rm test-markdown-issues.md"
echo "   rm -rf .task_orchestrator/markdown_fixes"