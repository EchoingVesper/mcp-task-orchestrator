#!/bin/bash
"""
Agent Interruption Detector Hook

Claude Code hook script that detects agent interruptions during documentation
modernization operations and automatically creates checkpoints and recovery
instructions.

Key Features:
- Detection of agent interruptions and unexpected terminations
- Automatic checkpoint creation when interruptions are detected
- Recovery instruction generation for resuming operations
- Integration with Agent Recovery Manager
- Logging and reporting of interruption events

Trigger: post-command (runs after every Claude Code command)
"""

# Hook configuration
HOOK_NAME="agent-interruption-detector"
HOOK_VERSION="1.0.0"
WORKSPACE_ROOT="$(pwd)"
RECOVERY_DIR="${WORKSPACE_ROOT}/.recovery"
CHECKPOINTS_DIR="${RECOVERY_DIR}/checkpoints"
INTERRUPTION_LOG="${RECOVERY_DIR}/interruption_events.log"

# Agent tracking files
ACTIVE_AGENTS_FILE="${RECOVERY_DIR}/active_agents.json"
LAST_COMMAND_FILE="${RECOVERY_DIR}/last_command.json"

# Ensure recovery directories exist
mkdir -p "${RECOVERY_DIR}" "${CHECKPOINTS_DIR}"

# Initialize logging
log_event() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "${timestamp} [${level}] ${HOOK_NAME}: ${message}" >> "${INTERRUPTION_LOG}"
    
    # Also log to stderr for immediate visibility
    echo "${timestamp} [${level}] ${HOOK_NAME}: ${message}" >&2
}

# Check if Python is available for Agent Recovery Manager integration
check_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        log_event "WARNING" "Python not found - Agent Recovery Manager integration disabled"
        return 1
    fi
}

# Detect if we're in a documentation modernization context
is_documentation_context() {
    # Check for presence of documentation modernization files
    if [[ -f "${WORKSPACE_ROOT}/PRPs/[IN-PROGRESS]documentation-ecosystem-modernization-comprehensive.md" ]] ||
       [[ -d "${WORKSPACE_ROOT}/scripts/agents" ]] ||
       [[ -f "${WORKSPACE_ROOT}/.progress/file_progress.json" ]]; then
        return 0
    fi
    return 1
}

# Get current active agents
get_active_agents() {
    if [[ -f "${ACTIVE_AGENTS_FILE}" ]]; then
        cat "${ACTIVE_AGENTS_FILE}" 2>/dev/null || echo "[]"
    else
        echo "[]"
    fi
}

# Update active agents list
update_active_agents() {
    local agents_json="$1"
    echo "${agents_json}" > "${ACTIVE_AGENTS_FILE}"
}

# Record current command for interruption detection
record_command() {
    local command_info="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "${LAST_COMMAND_FILE}" << EOF
{
    "timestamp": "${timestamp}",
    "command": "${command_info}",
    "pid": $$,
    "workspace": "${WORKSPACE_ROOT}"
}
EOF
}

# Detect agent interruption patterns
detect_interruption() {
    local exit_code="$1"
    local command="$2"
    
    # Patterns that indicate potential interruption
    local interruption_indicators=(
        "timeout"
        "killed"
        "terminated"
        "interrupted"
        "context limit"
        "token limit"
        "memory error"
        "connection error"
    )
    
    # Check exit code
    if [[ $exit_code -ne 0 ]]; then
        log_event "WARNING" "Command exited with non-zero code: $exit_code"
        return 0
    fi
    
    # Check command output/error patterns
    for indicator in "${interruption_indicators[@]}"; do
        if echo "${command}" | grep -qi "${indicator}"; then
            log_event "WARNING" "Interruption indicator detected: ${indicator}"
            return 0
        fi
    done
    
    return 1
}

# Create emergency checkpoint
create_emergency_checkpoint() {
    local agent_id="$1"
    local reason="$2"
    local python_cmd="$3"
    
    if [[ -n "$python_cmd" ]] && [[ -f "${WORKSPACE_ROOT}/scripts/agents/agent_recovery_manager.py" ]]; then
        log_event "INFO" "Creating emergency checkpoint for agent: ${agent_id}"
        
        # Use Agent Recovery Manager to create checkpoint
        "${python_cmd}" "${WORKSPACE_ROOT}/scripts/agents/agent_recovery_manager.py" \
            --workspace "${WORKSPACE_ROOT}" \
            --agent-id "${agent_id}" \
            --checkpoint-type "interruption" \
            --reason "${reason}" \
            2>/dev/null || log_event "ERROR" "Failed to create emergency checkpoint"
    else
        # Fallback: create basic checkpoint file
        local checkpoint_id="${agent_id}_interruption_$(date +%s)"
        local checkpoint_file="${CHECKPOINTS_DIR}/${checkpoint_id}.json"
        
        cat > "${checkpoint_file}" << EOF
{
    "checkpoint_id": "${checkpoint_id}",
    "agent_id": "${agent_id}",
    "checkpoint_type": "interruption",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "reason": "${reason}",
    "workspace": "${WORKSPACE_ROOT}",
    "recovery_instructions": [
        "Review interruption reason: ${reason}",
        "Check agent progress in .recovery/progress/",
        "Resume agent operation from last successful checkpoint",
        "Verify file backups before retrying operations"
    ],
    "created_by": "agent-interruption-detector-hook"
}
EOF
        
        log_event "INFO" "Created emergency checkpoint: ${checkpoint_file}"
    fi
}

# Generate recovery instructions
generate_recovery_instructions() {
    local agent_id="$1"
    local interruption_reason="$2"
    
    local instructions_file="${RECOVERY_DIR}/recovery_instructions_${agent_id}.md"
    
    cat > "${instructions_file}" << EOF
# Agent Recovery Instructions

**Agent ID:** ${agent_id}
**Interruption Time:** $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Reason:** ${interruption_reason}
**Workspace:** ${WORKSPACE_ROOT}

## Immediate Actions Required

1. **Check Agent Status:**
   - Review progress in \`.recovery/progress/${agent_id}_progress.json\`
   - Examine latest checkpoint in \`.recovery/checkpoints/\`
   - Verify which files were being processed

2. **Assess File State:**
   - Check for any corrupted or partially modified files
   - Restore from backups if necessary (located in \`.recovery/backups/\`)
   - Verify file integrity before resuming

3. **Resume Operations:**
   - Use Agent Recovery Manager to resume: \`python3 scripts/agents/agent_recovery_manager.py --workspace . --agent-id ${agent_id} --resume\`
   - Or start fresh if corruption detected
   - Monitor for repeated interruptions

4. **Prevention Measures:**
   - Check available system resources (memory, disk space)
   - Monitor token usage to prevent context limits
   - Ensure stable network connection
   - Consider splitting large batches into smaller chunks

## Recovery Commands

\`\`\`bash
# Check recovery status
python3 scripts/agents/agent_recovery_manager.py --workspace . --report --agent-id ${agent_id}

# Resume agent from checkpoint
python3 scripts/agents/agent_recovery_manager.py --workspace . --agent-id ${agent_id} --resume

# Check progress tracking
python3 scripts/agents/documentation_progress_tracker.py --workspace . --summary
\`\`\`

## Contact Information

If recovery fails repeatedly, escalate to:
- Check orchestrator health: Run orchestrator health check
- Review system resources and constraints
- Consider manual intervention for specific files

---
*Generated by agent-interruption-detector hook at $(date)*
EOF

    log_event "INFO" "Generated recovery instructions: ${instructions_file}"
}

# Check for stale agent processes
check_stale_agents() {
    local python_cmd="$1"
    
    if [[ ! -f "${ACTIVE_AGENTS_FILE}" ]]; then
        return
    fi
    
    # Read active agents and check if they're still running
    local active_agents=$(get_active_agents)
    
    # This would require more sophisticated process tracking
    # For now, just log the check
    log_event "DEBUG" "Checking for stale agent processes"
}

# Main hook execution
main() {
    # Only run if we're in a documentation modernization context
    if ! is_documentation_context; then
        exit 0
    fi
    
    log_event "DEBUG" "Agent interruption detector hook triggered"
    
    # Get command information from environment or arguments
    local command_info="${1:-${CLAUDE_LAST_COMMAND:-'unknown command'}}"
    local exit_code="${2:-${CLAUDE_LAST_EXIT_CODE:-0}}"
    
    # Record the command for tracking
    record_command "${command_info}"
    
    # Check for Python availability
    local python_cmd
    python_cmd=$(check_python) || python_cmd=""
    
    # Detect potential interruptions
    if detect_interruption "${exit_code}" "${command_info}"; then
        log_event "WARNING" "Potential agent interruption detected"
        
        # Get current active agents
        local active_agents=$(get_active_agents)
        
        # Create emergency checkpoints for all active agents
        if [[ "${active_agents}" != "[]" ]] && [[ -n "${python_cmd}" ]]; then
            # Parse JSON and create checkpoints (simplified)
            log_event "INFO" "Creating emergency checkpoints for active agents"
            
            # For demonstration, create a generic checkpoint
            create_emergency_checkpoint "documentation_agent" "interruption_detected" "${python_cmd}"
            
            # Generate recovery instructions
            generate_recovery_instructions "documentation_agent" "Agent interruption detected by hook"
        fi
    fi
    
    # Check for stale agents periodically
    if [[ $(($(date +%s) % 300)) -eq 0 ]]; then  # Every 5 minutes
        check_stale_agents "${python_cmd}"
    fi
    
    # Clean up old logs (keep last 1000 lines)
    if [[ -f "${INTERRUPTION_LOG}" ]] && [[ $(wc -l < "${INTERRUPTION_LOG}") -gt 1000 ]]; then
        tail -1000 "${INTERRUPTION_LOG}" > "${INTERRUPTION_LOG}.tmp" && 
        mv "${INTERRUPTION_LOG}.tmp" "${INTERRUPTION_LOG}"
    fi
    
    log_event "DEBUG" "Agent interruption detector hook completed"
}

# Handle different invocation methods
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Direct execution
    main "$@"
elif [[ -n "${CLAUDE_HOOK_CONTEXT}" ]]; then
    # Called as Claude Code hook
    main "${CLAUDE_LAST_COMMAND}" "${CLAUDE_LAST_EXIT_CODE}"
else
    # Called from other script
    main "$@"
fi