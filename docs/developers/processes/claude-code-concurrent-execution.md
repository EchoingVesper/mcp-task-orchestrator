
# Claude Code Concurrent Execution Patterns

#
# Overview

This document provides comprehensive guidance for executing multiple Claude Code instances in parallel to maximize research efficiency and enable complex multi-agent workflows.

#
# Core Concepts

#
## Headless Mode Execution

Claude Code's headless mode (`-p` flag) enables non-interactive, programmatic execution suitable for automation and parallel workflows.

**Basic Syntax:**

```bash
claude -p "your prompt here" \
  --output-format stream-json \
  --max-turns 10 \
  --allowedTools "Read,Write,Bash" \
  > output.json &
```text

#
## Key Configuration Options

| Flag | Purpose | Example |
|------|---------|---------|
| `-p, --print` | Enable headless mode | `claude -p "analyze files"` |
| `--output-format` | Output format (text, json, stream-json) | `--output-format stream-json` |
| `--max-turns` | Limit agentic iterations | `--max-turns 15` |
| `--allowedTools` | Restrict tool access | `--allowedTools "Read,Grep,Write"` |
| `--append-system-prompt` | Add instructions to system prompt | `--append-system-prompt "Focus on research only"` |

#
## Output Formats

#
### Stream JSON (Recommended for Parallel Execution)

```text
bash
claude -p "task" --output-format stream-json > agent_output.json &

```text

**Processing Stream JSON:**
```text
bash

# Extract assistant messages

jq -r 'select(.type == "assistant") | .content // empty' agent_output.json

# Extract final result

jq -r 'select(.type == "result") | .stats' agent_output.json

```text

#
# Parallel Execution Patterns

#
## Pattern 1: Background Process Coordination

```text
bash

# Launch multiple agents in background

claude -p "Research task A" --output-format stream-json > agent_a.json &
claude -p "Research task B" --output-format stream-json > agent_b.json &
claude -p "Research task C" --output-format stream-json > agent_c.json &

# Monitor progress

while jobs | grep -q Running; do
  echo "$(date): Agents still running ($(jobs | grep Running | wc -l) active)"
  sleep 30
done

# Process results when complete

wait
for output in agent_*.json; do
  echo "=== Processing $output ==="
  jq -r 'select(.type == "assistant") | .content // empty' "$output"
done

```text

#
## Pattern 2: Git Worktrees for Isolation

```text
bash

# Create isolated workspaces

git worktree add ../project-agent-1 main
git worktree add ../project-agent-2 main
git worktree add ../project-agent-3 main

# Launch in separate terminals (manual)

cd ../project-agent-1 && claude  
# Terminal 1
cd ../project-agent-2 && claude  
# Terminal 2 
cd ../project-agent-3 && claude  
# Terminal 3

# Cleanup when complete

git worktree remove ../project-agent-1
git worktree remove ../project-agent-2
git worktree remove ../project-agent-3

```text

#
## Pattern 3: Session Management for Complex Workflows

```text
bash

# Start session and capture ID

session_id=$(claude -p "Begin complex analysis" --output-format json | jq -r '.session_id')

# Resume and continue work

claude --resume "$session_id" -p "Continue with deeper analysis..."

# Or continue most recent session

claude --continue -p "Add this additional requirement..."

```text

#
# Inter-Agent Communication

#
## Shared Workspace Pattern

```text
bash

# Create coordination directory

mkdir -p .agent_coordination
touch .agent_coordination/agent_1_findings.md
touch .agent_coordination/agent_2_findings.md
touch .agent_coordination/shared_workspace.md

# Agents write to shared files

claude -p "Research X, write findings to .agent_coordination/agent_1_findings.md" \
  --allowedTools "Read,Write,WebSearch" &

claude -p "Research Y, write findings to .agent_coordination/agent_2_findings.md" \
  --allowedTools "Read,Write,Grep" &

```text

#
## Progress Coordination

```text
bash

# Status tracking

echo "Agent 1: Starting documentation analysis..." >> .agent_coordination/progress.log
echo "Agent 2: Industry research in progress..." >> .agent_coordination/progress.log

# Real-time monitoring

tail -f .agent_coordination/progress.log

```text

#
# Error Handling and Recovery

#
## Failed Agent Detection

```text
bash

# Check for JSON validity

for agent in {1..4}; do
  if ! jq -e . agent_${agent}_output.json >/dev/null 2>&1; then
    echo "Agent $agent failed - restarting..."
    claude -p "Resume task for Agent $agent" --output-format stream-json > agent_${agent}_output.json &
  fi
done

```text

#
## Timeout Handling

```text
bash

# Set timeout for background processes

timeout 1800 claude -p "long running task" --output-format stream-json > agent_output.json &

# Check completion status

if wait $!; then
  echo "Agent completed successfully"
else
  echo "Agent timed out or failed"
fi

```text

#
# Best Practices

#
## Tool Restriction Strategy

- **Research agents**: `--allowedTools "Read,Grep,WebSearch,WebFetch"`

- **Analysis agents**: `--allowedTools "Read,Write,Glob"`

- **Implementation agents**: `--allowedTools "Edit,Write,Bash"`

#
## System Prompt Guidelines

```text
bash

# Research-focused agents

--append-system-prompt "RESEARCH ONLY - Do not modify files. Focus on gathering information."

# Analysis-focused agents  

--append-system-prompt "ANALYSIS ONLY - Read files and generate insights. Write findings to designated output files."

# Implementation-focused agents

--append-system-prompt "IMPLEMENTATION FOCUS - Make changes based on provided analysis and requirements."

```text

#
## Resource Management

```text
bash

# Limit concurrent agents to avoid resource exhaustion

max_agents=4
current_agents=0

for task in "${tasks[@]}"; do
  if [[ $current_agents -ge $max_agents ]]; then
    wait -n  
# Wait for any job to complete
    ((current_agents--))
  fi
  
  claude -p "$task" --output-format stream-json > "agent_${current_agents}.json" &
  ((current_agents++))
done

wait  
# Wait for all remaining jobs

```text

#
# Common Pitfalls and Solutions

#
## Issue: Agents Interfering with Each Other

**Solution**: Use git worktrees or separate checkouts for file modification tasks

#
## Issue: Lost Agent Output

**Solution**: Always use output redirection and verify JSON validity

#
## Issue: Resource Exhaustion

**Solution**: Limit concurrent agents and use appropriate `--max-turns` values

#
## Issue: Context Window Overflow

**Solution**: Use `/clear` command or restart sessions periodically

#
# Advanced Patterns

#
## Synthesis Agent Pattern

```text
bash

# Launch research agents

claude -p "Research A" --output-format stream-json > research_a.json &
claude -p "Research B" --output-format stream-json > research_b.json &
wait

# Synthesis agent combines results

claude -p "Synthesize findings from research_a.json and research_b.json into comprehensive report" \
  --allowedTools "Read,Write" \
  --output-format stream-json > synthesis.json

```text

#
## Validation Pipeline Pattern

```text
bash

# Implementation agent

claude -p "Implement feature X" --output-format stream-json > implementation.json &
wait

# Validation agent

claude -p "Review and validate implementation.json results" \
  --output-format stream-json > validation.json &
wait

# Approval agent

claude -p "Final approval based on validation.json findings" \
  --output-format stream-json > approval.json
```text

#
# Related Documentation

- [Claude Code SDK Documentation](https://docs.anthropic.com/en/docs/claude-code/sdk)

- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

- [Multi-Agent PRP Templates](../../.claude/commands/rapid-development/experimental/)
