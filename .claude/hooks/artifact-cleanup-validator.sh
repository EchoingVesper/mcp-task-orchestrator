#!/bin/bash

# Artifact Cleanup Validator Hook
# Part of MCP Task Orchestrator Documentation Ecosystem Modernization
# 
# Purpose: Validate and enforce artifact cleanup policies
# Trigger: post-command (after Claude Code operations)
# Integration: Updates orchestrator with cleanup status and recommendations

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
HOOK_NAME="artifact-cleanup-validator"
HOOK_VERSION="1.0.0"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
DRY_RUN="${DRY_RUN:-false}"

# Project paths
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ORCHESTRATOR_DIR="${PROJECT_ROOT}/.task_orchestrator"
CLAUDE_CONFIG_DIR="${PROJECT_ROOT}/.claude"
HOOKS_DIR="${CLAUDE_CONFIG_DIR}/hooks"

# Lifecycle policies
MAX_TEMP_FILE_AGE_HOURS=24
MAX_DRAFT_FILE_AGE_DAYS=7
MAX_LOG_FILE_AGE_DAYS=30
MAX_BACKUP_FILE_AGE_DAYS=90

# Patterns for different artifact types
declare -A ARTIFACT_PATTERNS=(
    ["temp_files"]="*.tmp *~ .*.swp *.bak *.backup"
    ["log_files"]="*.log *.debug"
    ["draft_files"]="*[Dd]raft* *[Ww]ip*"
    ["test_artifacts"]="test_*.json validation_*.json *_test_report*"
    ["migration_reports"]="migration_report_* *_migration_summary*"
)

# Root directory cleanup patterns (files that shouldn't be in project root)
ROOT_PROHIBITED_PATTERNS="*.tmp *.log *.json *.bak *~ test_* migration_* validation_*"

# Logging functions
log_info() {
    [[ "$LOG_LEVEL" =~ ^(DEBUG|INFO)$ ]] && echo "[INFO] $*" >&2
}

log_warn() {
    [[ "$LOG_LEVEL" =~ ^(DEBUG|INFO|WARN)$ ]] && echo "[WARN] $*" >&2
}

log_error() {
    echo "[ERROR] $*" >&2
}

log_debug() {
    [[ "$LOG_LEVEL" = "DEBUG" ]] && echo "[DEBUG] $*" >&2
}

# Validate prerequisites
validate_prerequisites() {
    log_debug "Validating prerequisites for $HOOK_NAME"
    
    # Check required tools
    local required_tools=(find stat date)
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Required tool '$tool' not found"
            return 1
        fi
    done
    
    # Check project structure
    [[ -d "$PROJECT_ROOT" ]] || {
        log_error "Project root not found: $PROJECT_ROOT"
        return 1
    }
    
    log_debug "Prerequisites validated successfully"
    return 0
}

# Find files older than specified age
find_old_files() {
    local pattern="$1"
    local age_spec="$2"  # e.g., "+1" for older than 1 day, "+24" for older than 24 hours
    local age_unit="$3"  # "hours" or "days"
    
    local find_args=()
    if [[ "$age_unit" = "hours" ]]; then
        find_args=(-mmin "+$((age_spec * 60))")
    else
        find_args=(-mtime "+$age_spec")
    fi
    
    # Split pattern into individual patterns and find files
    for p in $pattern; do
        find "$PROJECT_ROOT" -name "$p" "${find_args[@]}" 2>/dev/null || true
    done
}

# Check for files that shouldn't be in project root
check_root_cleanliness() {
    log_debug "Checking project root cleanliness"
    
    local violations=()
    
    for pattern in $ROOT_PROHIBITED_PATTERNS; do
        while IFS= read -r -d '' file; do
            # Only check files directly in root (not subdirectories)
            if [[ "$(dirname "$file")" = "$PROJECT_ROOT" ]]; then
                violations+=("$file")
                log_warn "Prohibited file in project root: $(basename "$file")"
            fi
        done < <(find "$PROJECT_ROOT" -maxdepth 1 -name "$pattern" -type f -print0 2>/dev/null || true)
    done
    
    if [[ ${#violations[@]} -gt 0 ]]; then
        log_warn "Found ${#violations[@]} file(s) violating root directory cleanliness"
        return 1
    fi
    
    log_info "Project root cleanliness: PASSED"
    return 0
}

# Validate artifact lifecycle compliance
validate_artifact_lifecycle() {
    log_debug "Validating artifact lifecycle compliance"
    
    local violations=0
    local recommendations=()
    
    # Check temporary files
    log_debug "Checking temporary files (max age: ${MAX_TEMP_FILE_AGE_HOURS}h)"
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            violations=$((violations + 1))
            recommendations+=("Remove stale temporary file: $file")
            log_warn "Stale temporary file found: $file"
        fi
    done < <(find_old_files "${ARTIFACT_PATTERNS[temp_files]}" "$MAX_TEMP_FILE_AGE_HOURS" "hours")
    
    # Check draft files
    log_debug "Checking draft files (max age: ${MAX_DRAFT_FILE_AGE_DAYS}d)"
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            violations=$((violations + 1))
            recommendations+=("Review or archive old draft: $file")
            log_warn "Old draft file found: $file"
        fi
    done < <(find_old_files "${ARTIFACT_PATTERNS[draft_files]}" "$MAX_DRAFT_FILE_AGE_DAYS" "days")
    
    # Check log files
    log_debug "Checking log files (max age: ${MAX_LOG_FILE_AGE_DAYS}d)"
    while IFS= read -r file; do
        if [[ -n "$file" ]]; then
            violations=$((violations + 1))
            recommendations+=("Archive or remove old log: $file")
            log_warn "Old log file found: $file"
        fi
    done < <(find_old_files "${ARTIFACT_PATTERNS[log_files]}" "$MAX_LOG_FILE_AGE_DAYS" "days")
    
    # Check test artifacts in wrong locations
    log_debug "Checking for misplaced test artifacts"
    for pattern in ${ARTIFACT_PATTERNS[test_artifacts]}; do
        while IFS= read -r -d '' file; do
            # Check if test artifact is in root or docs directories (should be in archives)
            local file_dir="$(dirname "$file")"
            if [[ "$file_dir" = "$PROJECT_ROOT" ]] || [[ "$file_dir" = "$PROJECT_ROOT/docs" ]]; then
                violations=$((violations + 1))
                recommendations+=("Move test artifact to appropriate archive: $file")
                log_warn "Misplaced test artifact: $file"
            fi
        done < <(find "$PROJECT_ROOT" -name "$pattern" -type f -print0 2>/dev/null || true)
    done
    
    return "$violations"
}

# Generate artifact cleanup report
generate_cleanup_report() {
    local violations="$1"
    shift
    local recommendations=("$@")
    
    local report_file="/tmp/artifact_cleanup_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
  "hook": "$HOOK_NAME",
  "version": "$HOOK_VERSION",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT",
  "validation_status": $([ "$violations" -eq 0 ] && echo '"PASSED"' || echo '"FAILED"'),
  "violations_count": $violations,
  "recommendations": [
$(printf '    "%s"' "${recommendations[@]}" | paste -sd, -)
  ],
  "policies": {
    "max_temp_file_age_hours": $MAX_TEMP_FILE_AGE_HOURS,
    "max_draft_file_age_days": $MAX_DRAFT_FILE_AGE_DAYS,
    "max_log_file_age_days": $MAX_LOG_FILE_AGE_DAYS,
    "max_backup_file_age_days": $MAX_BACKUP_FILE_AGE_DAYS
  }
}
EOF
    
    echo "$report_file"
}

# Auto-cleanup (if enabled and not in dry-run mode)
perform_auto_cleanup() {
    local violations="$1"
    
    if [[ "$violations" -eq 0 ]]; then
        log_info "No cleanup needed - all artifacts within policy compliance"
        return 0
    fi
    
    if [[ "$DRY_RUN" = "true" ]]; then
        log_info "DRY_RUN mode: Would perform cleanup for $violations violations"
        return 0
    fi
    
    # Only perform safe, automated cleanup
    log_info "Performing safe automated cleanup"
    
    # Clean up temporary files older than policy
    local cleaned=0
    while IFS= read -r file; do
        if [[ -n "$file" && -f "$file" ]]; then
            log_debug "Removing stale temporary file: $file"
            rm -f "$file" && cleaned=$((cleaned + 1))
        fi
    done < <(find_old_files "${ARTIFACT_PATTERNS[temp_files]}" "$MAX_TEMP_FILE_AGE_HOURS" "hours")
    
    # Move misplaced files to appropriate locations
    for pattern in $ROOT_PROHIBITED_PATTERNS; do
        while IFS= read -r -d '' file; do
            if [[ "$(dirname "$file")" = "$PROJECT_ROOT" ]]; then
                local target_dir=""
                local filename="$(basename "$file")"
                
                # Determine appropriate target directory
                case "$filename" in
                    *.log|*.debug) target_dir="$PROJECT_ROOT/logs" ;;
                    test_*.json|*_test_report*|validation_*.json) target_dir="$PROJECT_ROOT/docs/archives/test-artifacts" ;;
                    migration_*|*_migration_*) target_dir="$PROJECT_ROOT/docs/archives/migration-reports" ;;
                    *) continue ;; # Skip files we're not sure about
                esac
                
                if [[ -n "$target_dir" ]]; then
                    mkdir -p "$target_dir"
                    log_debug "Moving $file to $target_dir/"
                    mv "$file" "$target_dir/" && cleaned=$((cleaned + 1))
                fi
            fi
        done < <(find "$PROJECT_ROOT" -maxdepth 1 -name "$pattern" -type f -print0 2>/dev/null || true)
    done
    
    log_info "Automated cleanup completed: $cleaned items processed"
    return 0
}

# Integration with orchestrator
integrate_with_orchestrator() {
    local report_file="$1"
    local violations="$2"
    
    log_debug "Integrating with orchestrator system"
    
    local session_file="$ORCHESTRATOR_DIR/session.json"
    if [[ -f "$session_file" ]]; then
        log_debug "Orchestrator session found, reporting cleanup status"
        
        # Create orchestrator update
        local status_update=$(cat <<EOF
{
  "hook_execution": {
    "hook_name": "$HOOK_NAME",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": $([ "$violations" -eq 0 ] && echo '"success"' || echo '"warning"'),
    "violations": $violations,
    "report_file": "$report_file",
    "message": "Artifact cleanup validation completed with $violations policy violations"
  }
}
EOF
)
        
        # Store update for orchestrator (if orchestrator MCP tools are available)
        if command -v curl >/dev/null 2>&1; then
            # Try to post to orchestrator if it's running
            if curl -s -X POST "http://localhost:3001/api/hooks/artifact-cleanup" \
                    -H "Content-Type: application/json" \
                    -d "$status_update" >/dev/null 2>&1; then
                log_debug "Successfully reported to orchestrator API"
            else
                log_debug "Orchestrator API not available, storing update locally"
                echo "$status_update" > "$ORCHESTRATOR_DIR/artifact_cleanup_status.json"
            fi
        fi
    else
        log_debug "No orchestrator session found, skipping integration"
    fi
}

# Main hook logic
execute_hook_logic() {
    log_info "Executing $HOOK_NAME hook logic"
    
    # Check root directory cleanliness
    local root_clean=0
    check_root_cleanliness || root_clean=1
    
    # Validate artifact lifecycles
    local violations=0
    local recommendations=()
    
    # Capture recommendations in an array
    while IFS= read -r rec; do
        recommendations+=("$rec")
    done < <(
        # Run validation and capture recommendations
        validate_artifact_lifecycle 2>&1 | grep "Remove\|Review\|Archive\|Move" | sed 's/.*: //' || true
    )
    
    # Get violation count
    validate_artifact_lifecycle >/dev/null 2>&1 || violations=$?
    
    # Add root cleanliness violations
    violations=$((violations + root_clean))
    
    # Generate report
    local report_file
    report_file=$(generate_cleanup_report "$violations" "${recommendations[@]}")
    
    # Perform auto-cleanup if configured
    perform_auto_cleanup "$violations"
    
    # Integration with orchestrator
    integrate_with_orchestrator "$report_file" "$violations"
    
    # Output summary
    if [[ "$violations" -eq 0 ]]; then
        log_info "✓ Artifact lifecycle validation PASSED - all policies compliant"
    else
        log_warn "⚠ Artifact lifecycle validation found $violations policy violations"
        log_warn "📋 Full report: $report_file"
        
        # Show top recommendations
        if [[ ${#recommendations[@]} -gt 0 ]]; then
            log_warn "Top recommendations:"
            for i in "${!recommendations[@]}"; do
                [[ $i -lt 3 ]] && log_warn "  - ${recommendations[$i]}"
            done
        fi
    fi
    
    log_info "Hook logic completed successfully"
    return 0
}

# Error handling and recovery
handle_error() {
    local exit_code=$1
    local line_number=$2
    
    log_error "Hook failed at line $line_number with exit code $exit_code"
    
    # Create error report
    local error_report="/tmp/artifact_cleanup_error_$(date +%Y%m%d_%H%M%S).json"
    cat > "$error_report" <<EOF
{
  "hook": "$HOOK_NAME",
  "status": "error",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "error_code": $exit_code,
  "error_line": $line_number,
  "project_root": "$PROJECT_ROOT"
}
EOF
    
    log_error "Error report: $error_report"
    exit "$exit_code"
}

# Main execution flow
main() {
    log_info "Starting $HOOK_NAME hook (version $HOOK_VERSION)"
    
    # Set up error handling
    trap 'handle_error $? $LINENO' ERR
    
    # Validate prerequisites
    validate_prerequisites || {
        log_error "Prerequisites validation failed"
        exit 1
    }
    
    # Execute main hook logic
    execute_hook_logic
    
    log_info "$HOOK_NAME hook completed successfully"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi