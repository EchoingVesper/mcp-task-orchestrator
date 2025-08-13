#!/bin/bash

# Project Cleanliness Enforcer Hook
# Part of MCP Task Orchestrator Documentation Ecosystem Modernization
# 
# Purpose: Enforce project cleanliness framework standards and file organization
# Trigger: post-command (after Claude Code operations)
# Integration: Maintains project organization and reports to orchestrator

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
HOOK_NAME="project-cleanliness-enforcer"
HOOK_VERSION="1.0.0"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
DRY_RUN="${DRY_RUN:-false}"
AUTO_FIX="${AUTO_FIX:-true}"  # Set to false to report only, no automatic fixes

# Project paths
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ORCHESTRATOR_DIR="${PROJECT_ROOT}/.task_orchestrator"
CLAUDE_CONFIG_DIR="${PROJECT_ROOT}/.claude"

# Root directory cleanliness rules
declare -A PROHIBITED_IN_ROOT=(
    ["*.tmp"]="temporary files"
    ["*.bak"]="backup files"
    ["*.log"]="log files"
    ["*~"]="editor backup files"
    ["*.debug"]="debug files"
    ["test_*.json"]="test artifacts"
    ["validation_*.json"]="validation artifacts"
    ["migration_*.md"]="migration reports"
    ["*_migration_*"]="migration artifacts"
    ["*.swp"]="vim swap files"
    ["*.orig"]="merge conflict files"
)

# Correct locations for misplaced files
declare -A TARGET_DIRECTORIES=(
    ["*.log|*.debug"]="logs"
    ["test_*.json|*_test_*|validation_*.json"]="docs/archives/test-artifacts"
    ["migration_*|*_migration_*"]="docs/archives/migration-reports"
    ["*.tmp|*.bak|*~|*.swp|*.orig"]="tmp"
)

# Required directory structure
REQUIRED_DIRECTORIES=(
    "docs"
    "docs/users"
    "docs/developers"
    "docs/templates"
    "docs/archives"
    "docs/archives/test-artifacts"
    "docs/archives/migration-reports"
    "scripts"
    "tests"
    "logs"
    "tmp"
)

# Status tag patterns for lifecycle files
STATUS_TAG_PATTERN='^\[(CURRENT|IN-PROGRESS|DRAFT|NEEDS-VALIDATION|NEEDS-UPDATE|DEPRECATED|COMPLETED)\]'

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
    
    local required_tools=(find mkdir mv cp)
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Required tool '$tool' not found"
            return 1
        fi
    done
    
    [[ -d "$PROJECT_ROOT" ]] || {
        log_error "Project root not found: $PROJECT_ROOT"
        return 1
    }
    
    log_debug "Prerequisites validated successfully"
    return 0
}

# Ensure required directories exist
ensure_directory_structure() {
    log_debug "Ensuring required directory structure exists"
    
    local created_dirs=0
    
    for dir in "${REQUIRED_DIRECTORIES[@]}"; do
        local full_path="$PROJECT_ROOT/$dir"
        if [[ ! -d "$full_path" ]]; then
            log_info "Creating required directory: $dir"
            if [[ "$DRY_RUN" != "true" ]]; then
                mkdir -p "$full_path"
                created_dirs=$((created_dirs + 1))
            fi
        fi
    done
    
    log_debug "Directory structure check completed ($created_dirs directories created)"
    return 0
}

# Check root directory cleanliness
check_root_cleanliness() {
    log_debug "Checking root directory cleanliness"
    
    local violations=()
    
    for pattern in "${!PROHIBITED_IN_ROOT[@]}"; do
        while IFS= read -r -d '' file; do
            # Only check files directly in root (not subdirectories)
            if [[ "$(dirname "$file")" = "$PROJECT_ROOT" ]]; then
                local reason="${PROHIBITED_IN_ROOT[$pattern]}"
                violations+=("$file:$reason")
                log_warn "Root cleanliness violation: $(basename "$file") ($reason)"
            fi
        done < <(find "$PROJECT_ROOT" -maxdepth 1 -name "$pattern" -type f -print0 2>/dev/null || true)
    done
    
    echo "${#violations[@]}"  # Return violation count
    printf '%s\n' "${violations[@]}"  # Output violations
}

# Determine correct target directory for a file
determine_target_directory() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Check against target directory patterns
    for pattern_set in "${!TARGET_DIRECTORIES[@]}"; do
        local target_dir="${TARGET_DIRECTORIES[$pattern_set]}"
        
        # Split pattern set by | and check each pattern
        IFS='|' read -ra patterns <<< "$pattern_set"
        for pattern in "${patterns[@]}"; do
            if [[ "$filename" = $pattern ]]; then
                echo "$target_dir"
                return 0
            fi
        done
    done
    
    # Default fallback
    echo "tmp"
}

# Fix root directory violations
fix_root_violations() {
    local violation_count="$1"
    shift
    local violations=("$@")
    
    if [[ "$violation_count" -eq 0 ]]; then
        log_debug "No root directory violations to fix"
        return 0
    fi
    
    if [[ "$AUTO_FIX" != "true" ]]; then
        log_info "AUTO_FIX disabled - would fix $violation_count root violations"
        return 0
    fi
    
    if [[ "$DRY_RUN" = "true" ]]; then
        log_info "DRY_RUN mode - would fix $violation_count root violations"
        return 0
    fi
    
    log_info "Fixing $violation_count root directory violations"
    local fixed_count=0
    
    for violation in "${violations[@]}"; do
        local file="${violation%%:*}"
        local reason="${violation##*:}"
        
        if [[ -f "$file" ]]; then
            local target_dir
            target_dir=$(determine_target_directory "$file")
            local target_path="$PROJECT_ROOT/$target_dir"
            
            # Ensure target directory exists
            mkdir -p "$target_path"
            
            # Move file to correct location
            local filename=$(basename "$file")
            local new_path="$target_path/$filename"
            
            # Handle file name conflicts
            if [[ -f "$new_path" ]]; then
                local timestamp=$(date +%Y%m%d_%H%M%S)
                new_path="$target_path/${filename%.*}_${timestamp}.${filename##*.}"
            fi
            
            log_info "Moving $filename to $target_dir/ ($reason)"
            mv "$file" "$new_path"
            fixed_count=$((fixed_count + 1))
        fi
    done
    
    log_info "Fixed $fixed_count root directory violations"
    return 0
}

# Check file naming conventions
check_naming_conventions() {
    log_debug "Checking file naming conventions"
    
    local naming_violations=()
    
    # Check for improper naming patterns
    while IFS= read -r -d '' file; do
        local filename=$(basename "$file")
        local dir_path="${file%/*}"
        
        # Skip certain directories
        case "$dir_path" in
            */node_modules/*|*/.git/*|*/venv/*|*/build/*|*/dist/*) continue ;;
        esac
        
        # Check for spaces in filenames (should use hyphens or underscores)
        if [[ "$filename" =~ [[:space:]] ]]; then
            naming_violations+=("$file:spaces_in_filename")
            log_warn "Naming violation: spaces in filename: $filename"
        fi
        
        # Check for mixed case in documentation files (prefer lowercase)
        if [[ "$filename" =~ \.md$ ]] && [[ "$filename" =~ [A-Z] ]]; then
            # Allow certain patterns
            case "$filename" in
                README.md|CHANGELOG.md|LICENSE.md|CONTRIBUTING.md|CLAUDE*.md) ;;
                *) 
                    naming_violations+=("$file:mixed_case_documentation")
                    log_warn "Naming violation: mixed case in doc file: $filename"
                    ;;
            esac
        fi
        
    done < <(find "$PROJECT_ROOT" -type f -print0 2>/dev/null || true)
    
    echo "${#naming_violations[@]}"  # Return violation count
    printf '%s\n' "${naming_violations[@]}"  # Output violations
}

# Check status tag compliance
check_status_tag_compliance() {
    log_debug "Checking status tag compliance"
    
    local tag_violations=()
    
    # Files that should have status tags
    local lifecycle_dirs=("PRPs" "docs/developers/planning" "docs/templates")
    
    for dir in "${lifecycle_dirs[@]}"; do
        local full_dir="$PROJECT_ROOT/$dir"
        if [[ -d "$full_dir" ]]; then
            while IFS= read -r -d '' file; do
                if [[ "$file" =~ \.md$ ]]; then
                    local filename=$(basename "$file")
                    
                    # Skip files in archives or completed directories
                    case "$file" in
                        */archives/*|*/completed/*) continue ;;
                    esac
                    
                    # Check for status tag
                    if [[ ! "$filename" =~ $STATUS_TAG_PATTERN ]]; then
                        tag_violations+=("$file:missing_status_tag")
                        log_warn "Status tag violation: missing tag in $filename"
                    fi
                fi
            done < <(find "$full_dir" -name "*.md" -type f -print0 2>/dev/null || true)
        fi
    done
    
    echo "${#tag_violations[@]}"  # Return violation count
    printf '%s\n' "${tag_violations[@]}"  # Output violations
}

# Check directory organization
check_directory_organization() {
    log_debug "Checking directory organization"
    
    local org_violations=()
    
    # Check for files in wrong directories
    local checks=(
        "tests/test_*.py:unit tests should be in tests/unit/"
        "scripts/*.py:scripts should be organized by purpose in subdirectories"
        "docs/*.json:JSON artifacts should be in docs/archives/"
    )
    
    for check in "${checks[@]}"; do
        local pattern="${check%%:*}"
        local message="${check##*:}"
        
        # Convert pattern to find command
        local dir_part="${pattern%/*}"
        local file_part="${pattern##*/}"
        
        if [[ -d "$PROJECT_ROOT/$dir_part" ]]; then
            while IFS= read -r -d '' file; do
                org_violations+=("$file:$message")
                log_warn "Organization violation: $file ($message)"
            done < <(find "$PROJECT_ROOT/$dir_part" -maxdepth 1 -name "$file_part" -type f -print0 2>/dev/null || true)
        fi
    done
    
    echo "${#org_violations[@]}"  # Return violation count
    printf '%s\n' "${org_violations[@]}"  # Output violations
}

# Generate cleanliness report
generate_cleanliness_report() {
    local root_violations="$1"
    local naming_violations="$2"
    local tag_violations="$3"
    local org_violations="$4"
    local total_violations=$((root_violations + naming_violations + tag_violations + org_violations))
    
    local report_file="/tmp/project_cleanliness_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
  "hook": "$HOOK_NAME",
  "version": "$HOOK_VERSION",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT",
  "cleanliness_status": $([ "$total_violations" -eq 0 ] && echo '"CLEAN"' || echo '"VIOLATIONS"'),
  "summary": {
    "total_violations": $total_violations,
    "root_violations": $root_violations,
    "naming_violations": $naming_violations,
    "status_tag_violations": $tag_violations,
    "organization_violations": $org_violations
  },
  "policies": {
    "auto_fix_enabled": $([[ "$AUTO_FIX" = "true" ]] && echo 'true' || echo 'false'),
    "required_directories": [$(printf '"%s"' "${REQUIRED_DIRECTORIES[@]}" | paste -sd, -)],
    "status_tag_enforcement": true,
    "root_cleanliness_enforcement": true
  },
  "directory_structure_validated": true
}
EOF
    
    echo "$report_file"
}

# Main hook logic
execute_hook_logic() {
    log_info "Executing $HOOK_NAME hook logic"
    
    # Ensure required directory structure
    ensure_directory_structure
    
    # Check various cleanliness aspects
    log_debug "Performing cleanliness checks"
    
    # Root directory cleanliness
    local root_check_output
    root_check_output=$(check_root_cleanliness)
    local root_violations
    root_violations=$(echo "$root_check_output" | head -n 1)
    local root_violation_details=()
    if [[ "$root_violations" -gt 0 ]]; then
        while IFS= read -r line; do
            [[ -n "$line" ]] && root_violation_details+=("$line")
        done < <(echo "$root_check_output" | tail -n +2)
    fi
    
    # Naming conventions
    local naming_check_output
    naming_check_output=$(check_naming_conventions)
    local naming_violations
    naming_violations=$(echo "$naming_check_output" | head -n 1)
    
    # Status tag compliance
    local tag_check_output
    tag_check_output=$(check_status_tag_compliance)
    local tag_violations
    tag_violations=$(echo "$tag_check_output" | head -n 1)
    
    # Directory organization
    local org_check_output
    org_check_output=$(check_directory_organization)
    local org_violations
    org_violations=$(echo "$org_check_output" | head -n 1)
    
    local total_violations=$((root_violations + naming_violations + tag_violations + org_violations))
    
    # Fix violations if enabled
    if [[ "$root_violations" -gt 0 ]]; then
        fix_root_violations "$root_violations" "${root_violation_details[@]}"
    fi
    
    # Generate comprehensive report
    local report_file
    report_file=$(generate_cleanliness_report "$root_violations" "$naming_violations" "$tag_violations" "$org_violations")
    
    # Integration with orchestrator
    integrate_with_orchestrator "$report_file" "$total_violations"
    
    # Output summary
    if [[ "$total_violations" -eq 0 ]]; then
        log_info "✓ Project cleanliness enforcement PASSED - project structure is clean"
    else
        log_warn "⚠ Project cleanliness enforcement found $total_violations violations"
        log_warn "  Root violations: $root_violations"
        log_warn "  Naming violations: $naming_violations"  
        log_warn "  Status tag violations: $tag_violations"
        log_warn "  Organization violations: $org_violations"
        log_warn "📋 Full report: $report_file"
    fi
    
    log_info "Hook logic completed successfully"
    return 0
}

# Integration with orchestrator
integrate_with_orchestrator() {
    local report_file="$1"
    local violations="$2"
    
    log_debug "Integrating with orchestrator system"
    
    local session_file="$ORCHESTRATOR_DIR/session.json"
    if [[ -f "$session_file" ]]; then
        log_debug "Orchestrator session found, reporting cleanliness status"
        
        local cleanliness_update=$(cat <<EOF
{
  "cleanliness_enforcement": {
    "hook_name": "$HOOK_NAME",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": $([ "$violations" -eq 0 ] && echo '"clean"' || echo '"violations"'),
    "violations": $violations,
    "report_file": "$report_file",
    "auto_fix_enabled": $([[ "$AUTO_FIX" = "true" ]] && echo 'true' || echo 'false'),
    "message": "Project cleanliness enforcement completed"
  }
}
EOF
)
        
        # Store update for orchestrator
        echo "$cleanliness_update" > "$ORCHESTRATOR_DIR/project_cleanliness_status.json"
        
        # Try to post to orchestrator API if available
        if command -v curl >/dev/null 2>&1; then
            curl -s -X POST "http://localhost:3001/api/hooks/project-cleanliness" \
                 -H "Content-Type: application/json" \
                 -d "$cleanliness_update" >/dev/null 2>&1 || true
        fi
    else
        log_debug "No orchestrator session found, skipping integration"
    fi
}

# Error handling
handle_error() {
    local exit_code=$1
    local line_number=$2
    
    log_error "Hook failed at line $line_number with exit code $exit_code"
    
    local error_report="/tmp/project_cleanliness_error_$(date +%Y%m%d_%H%M%S).json"
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