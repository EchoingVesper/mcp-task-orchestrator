
# Claude Code Parallel Execution Troubleshooting

#
# Common Issues and Solutions

#
## 1. Background Process Management

#
### Issue: Processes Not Starting

**Symptoms**: No output files created, `jobs` shows no running processes
**Solutions**:

```bash

# Check if claude is in PATH

which claude

# Verify command syntax

claude -p "test" --output-format stream-json --dry-run

# Check permissions

ls -la $(which claude)
```text

#
### Issue: Zombie Processes

**Symptoms**: Processes shown in `jobs` but not producing output
**Solutions**:
```text
bash

# Kill hanging processes

jobs -p | xargs kill -9

# Clean up background jobs

disown -a

# Restart with timeout

timeout 1800 claude -p "task" --output-format stream-json > output.json &

```text

#
## 2. Output Capture Problems

#
### Issue: Malformed JSON Output

**Symptoms**: `jq` parsing errors, incomplete output files
**Solutions**:
```text
bash

# Validate JSON integrity

for file in agent_*.json; do
  if ! jq -e . "$file" >/dev/null 2>&1; then
    echo "Invalid JSON in $file"
    
# Show last few lines to diagnose
    tail -n 5 "$file"
  fi
done

# Use alternative output format if JSON fails

claude -p "task" --output-format text > output.txt &

```text

#
### Issue: Missing Output

**Symptoms**: Empty or zero-byte output files
**Solutions**:
```text
bash

# Check disk space

df -h .

# Verify write permissions

touch test_write.tmp && rm test_write.tmp

# Monitor output in real-time

tail -f agent_output.json &

```text

#
## 3. Resource Exhaustion

#
### Issue: System Overload

**Symptoms**: Slow response times, high CPU/memory usage
**Solutions**:
```text
bash

# Monitor system resources

top -p $(pgrep claude)

# Limit concurrent processes

max_concurrent=2  
# Reduce from default

# Use resource limits

ulimit -m 4194304  
# 4GB memory limit

```text

#
### Issue: Token Limit Exceeded

**Symptoms**: Truncated responses, "context window" errors
**Solutions**:
```text
bash

# Reduce max turns

--max-turns 5

# Use /clear between tasks

claude -p "task 1" && claude -p "/clear" && claude -p "task 2"

# Split large tasks into smaller chunks

```text

#
## 4. Inter-Agent Communication Issues

#
### Issue: File Conflicts

**Symptoms**: Agents overwriting each other's output
**Solutions**:

```bash

# Use unique filenames with timestamps

agent_1_$(date +%s).json

# Create separate directories

mkdir -p agent_{1..4}_workspace
cd agent_1_workspace && claude -p "task 1" > output.json &
```text

#
### Issue: Coordination Failures

**Symptoms**: Agents not reading shared files, missing updates
**Solutions**:
```text
bash

# Add explicit file synchronization

sync  
# Force file system sync

# Use file locking for critical sections

(
  flock -x 200
  echo "Agent 1 update" >> shared_file.md
) 200>shared_file.lock

# Implement simple polling

while [[ ! -f agent_1_complete.flag ]]; do
  sleep 5
done

```text

#
## 5. Git Worktree Issues

#
### Issue: Worktree Creation Failures

**Symptoms**: "fatal: cannot create worktree" errors
**Solutions**:
```text
bash

# Clean up stale worktrees

git worktree prune

# Check available disk space

df -h ../

# Use absolute paths

git worktree add /full/path/to/agent-workspace main

```text

#
### Issue: Cross-Worktree Conflicts

**Symptoms**: Git conflicts between worktrees
**Solutions**:
```text
bash

# Use different branches per worktree

git worktree add ../agent-1 -b agent-1-work
git worktree add ../agent-2 -b agent-2-work

# Ensure clean state before starting

git status --porcelain

```text

#
# Debugging Techniques

#
## 1. Verbose Logging

```text
bash

# Enable verbose output for debugging

claude -p "task" --verbose --output-format stream-json > debug_output.json 2>debug_errors.log &

# Monitor error stream

tail -f debug_errors.log

```text

#
## 2. Step-by-Step Validation

```text
bash

# Test basic functionality first

claude -p "echo hello" --output-format json

# Verify tool access

claude -p "list current directory" --allowedTools "LS" --output-format json

# Test specific tool combinations

claude -p "read a file" --allowedTools "Read" --output-format json

```text

#
## 3. Output Inspection

```text
bash

# Check message structure

jq 'keys' agent_output.json | head -20

# Inspect specific message types

jq 'select(.type == "assistant")' agent_output.json

# Extract error messages

jq 'select(.type == "error") | .content' agent_output.json

```text

#
# Monitoring and Health Checks

#
## Process Health Monitoring

```text
bash
#!/bin/bash

# agent_health_monitor.sh

check_agent_health() {
  local agent_id=$1
  local output_file="agent_${agent_id}_output.json"
  
  
# Check if process is running
  if pgrep -f "claude.*agent.*${agent_id}" >/dev/null; then
    echo "Agent $agent_id: RUNNING"
  else
    echo "Agent $agent_id: STOPPED"
  fi
  
  
# Check output file size
  if [[ -f "$output_file" ]]; then
    local size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
    echo "Agent $agent_id: Output size: $size bytes"
  fi
  
  
# Check JSON validity
  if jq -e . "$output_file" >/dev/null 2>&1; then
    echo "Agent $agent_id: Valid JSON output"
  else
    echo "Agent $agent_id: WARNING - Invalid JSON"
  fi
}

# Monitor all agents

for i in {1..4}; do
  check_agent_health $i
done

```text

#
## Progress Tracking

```text
bash

# Simple progress indicator

progress_file=".agent_coordination/progress.log"

monitor_progress() {
  while jobs | grep -q Running; do
    running_count=$(jobs | grep Running | wc -l)
    echo "$(date '+%H:%M:%S'): $running_count agents still running"
    
    
# Check for new progress updates
    if [[ -f "$progress_file" ]]; then
      tail -n 1 "$progress_file"
    fi
    
    sleep 30
  done
  
  echo "$(date '+%H:%M:%S'): All agents completed"
}

```text

#
# Performance Optimization

#
## Resource-Aware Execution

```text
bash

# Detect system capabilities

cpu_cores=$(nproc)
available_memory=$(free -m | awk '/^Mem:/{print $7}')

# Calculate optimal agent count

if [[ $available_memory -gt 8000 ]]; then
  max_agents=$((cpu_cores - 1))
elif [[ $available_memory -gt 4000 ]]; then
  max_agents=$((cpu_cores / 2))
else
  max_agents=2
fi

echo "Running with $max_agents concurrent agents based on system resources"

```text

#
## Efficient Output Processing

```text
bash

# Stream processing for large outputs

process_agent_output() {
  local output_file=$1
  
  
# Process output as it's generated
  tail -f "$output_file" | while IFS= read -r line; do
    if echo "$line" | jq -e '.type == "assistant"' >/dev/null 2>&1; then
      echo "$line" | jq -r '.content' >> processed_output.md
    fi
  done &
}

```text

#
# Emergency Recovery

#
## Kill All Claude Processes

```text
bash
#!/bin/bash

# emergency_stop.sh

echo "Stopping all Claude Code processes..."
pkill -f claude

echo "Cleaning up background jobs..."
jobs -p | xargs kill -9 2>/dev/null

echo "Removing temporary files..."
rm -f agent_*.json debug_*.log

echo "Emergency stop completed"

```text

#
## Session Recovery

```text
bash

# List recent sessions

claude --list-sessions

# Resume specific session

claude --resume <session-id> -p "Continue previous work"

# Recover from session logs

tail -n 100 ~/.claude/session.log
```text

#
# Related Documentation

- [Claude Code Concurrent Execution Patterns](./claude-code-concurrent-execution.md)

- [Multi-Agent Workflow Templates](../../.claude/commands/rapid-development/experimental/)

- [PRP Creation Best Practices](../planning/)
