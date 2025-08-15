#!/bin/bash

# Documentation Quality Gate Hook
# Part of MCP Task Orchestrator Documentation Ecosystem Modernization
# 
# Purpose: Enforce documentation quality standards and Japanese development principles
# Trigger: file-change (when documentation files are modified)
# Integration: Reports quality metrics to orchestrator and blocks substandard content

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
HOOK_NAME="documentation-quality-gate"
HOOK_VERSION="1.0.0"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
DRY_RUN="${DRY_RUN:-false}"
ENFORCE_BLOCKING="${ENFORCE_BLOCKING:-true}"  # Set to false to make warnings only

# Project paths
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ORCHESTRATOR_DIR="${PROJECT_ROOT}/.task_orchestrator"
CLAUDE_CONFIG_DIR="${PROJECT_ROOT}/.claude"

# Quality standards (based on Japanese development principles)
MAX_LINE_LENGTH=120
MIN_SECTIONS_COUNT=3
REQUIRED_SECTIONS=("Overview" "Purpose")
FORBIDDEN_WORDS=("TODO" "FIXME" "HACK" "XXX")

# Status tag patterns
STATUS_TAG_PATTERN='^\[(CURRENT|IN-PROGRESS|DRAFT|NEEDS-VALIDATION|NEEDS-UPDATE|DEPRECATED|COMPLETED)\]'

# Documentation file patterns
DOC_PATTERNS="*.md *.rst *.txt"

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
    local required_tools=(find grep wc markdownlint)
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            if [[ "$tool" = "markdownlint" ]]; then
                log_warn "markdownlint not found - markdown linting will be skipped"
            else
                log_error "Required tool '$tool' not found"
                return 1
            fi
        fi
    done
    
    [[ -d "$PROJECT_ROOT" ]] || {
        log_error "Project root not found: $PROJECT_ROOT"
        return 1
    }
    
    log_debug "Prerequisites validated successfully"
    return 0
}

# Check if file should have status tag
should_have_status_tag() {
    local file="$1"
    local rel_path="${file#$PROJECT_ROOT/}"
    
    # Files that should have status tags
    case "$rel_path" in
        PRPs/*.md|docs/developers/planning/*.md|docs/templates/*.md) return 0 ;;
        docs/archives/*|docs/completed/*) return 1 ;;  # Archive files exempt
        *) return 1 ;;
    esac
}

# Validate status tag
validate_status_tag() {
    local file="$1"
    local filename=$(basename "$file")
    
    if should_have_status_tag "$file"; then
        if [[ ! "$filename" =~ $STATUS_TAG_PATTERN ]]; then
            log_warn "Missing status tag: $file"
            return 1
        else
            log_debug "Valid status tag found: $filename"
        fi
    fi
    
    return 0
}

# Check markdown lint compliance
check_markdownlint() {
    local file="$1"
    
    if ! command -v markdownlint >/dev/null 2>&1; then
        log_debug "Skipping markdownlint check (not installed)"
        return 0
    fi
    
    log_debug "Running markdownlint on $file"
    
    # Create temporary config to match our standards
    local config_file="/tmp/markdownlint_config_$$.json"
    cat > "$config_file" <<EOF
{
  "MD013": { "line_length": $MAX_LINE_LENGTH },
  "MD001": true,
  "MD003": { "style": "atx" },
  "MD004": { "style": "dash" },
  "MD007": { "indent": 2 },
  "MD012": { "maximum": 1 },
  "MD022": true,
  "MD025": true,
  "MD026": true,
  "MD032": true,
  "MD036": true,
  "MD041": true
}
EOF
    
    local lint_output
    if lint_output=$(markdownlint -c "$config_file" "$file" 2>&1); then
        log_debug "Markdownlint passed for $file"
        rm -f "$config_file"
        return 0
    else
        log_warn "Markdownlint violations in $file:"
        echo "$lint_output" | while read -r line; do
            log_warn "  $line"
        done
        rm -f "$config_file"
        return 1
    fi
}

# Check content quality
check_content_quality() {
    local file="$1"
    local issues=0
    
    log_debug "Checking content quality for $file"
    
    # Check for required sections
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -q "^## $section" "$file"; then
            log_warn "Missing required section '$section' in $file"
            issues=$((issues + 1))
        fi
    done
    
    # Check minimum section count
    local section_count
    section_count=$(grep -c "^## " "$file" || true)
    if [[ "$section_count" -lt "$MIN_SECTIONS_COUNT" ]]; then
        log_warn "Insufficient sections ($section_count) in $file (minimum: $MIN_SECTIONS_COUNT)"
        issues=$((issues + 1))
    fi
    
    # Check for forbidden words (indicating incomplete work)
    for word in "${FORBIDDEN_WORDS[@]}"; do
        if grep -q "$word" "$file"; then
            log_warn "Found forbidden word '$word' in $file (indicates incomplete work)"
            issues=$((issues + 1))
        fi
    done
    
    # Check for placeholder content
    if grep -q "{.*}" "$file"; then
        log_warn "Found placeholder content (curly braces) in $file"
        issues=$((issues + 1))
    fi
    
    # Check for excessive line length
    local long_lines
    long_lines=$(awk "length > $MAX_LINE_LENGTH {count++} END {print count+0}" "$file")
    if [[ "$long_lines" -gt 0 ]]; then
        log_warn "Found $long_lines lines exceeding $MAX_LINE_LENGTH characters in $file"
        issues=$((issues + 1))
    fi
    
    return "$issues"
}

# Check Japanese development principles compliance
check_japanese_principles() {
    local file="$1"
    local issues=0
    
    log_debug "Checking Japanese development principles compliance for $file"
    
    # 1. Cleanliness (Seiso) - No empty sections
    if grep -q "^## .*$" "$file" && grep -A1 "^## " "$file" | grep -q "^--$"; then
        log_warn "Found empty sections in $file (violates Seiso principle)"
        issues=$((issues + 1))
    fi
    
    # 2. Standardization (Seiketsu) - Consistent formatting
    local inconsistent_lists=0
    inconsistent_lists=$(grep -c "^[*+]" "$file" || true)
    local dash_lists=0
    dash_lists=$(grep -c "^-" "$file" || true)
    
    if [[ "$inconsistent_lists" -gt 0 ]] && [[ "$dash_lists" -gt 0 ]]; then
        log_warn "Inconsistent list formatting in $file (use either - or * consistently)"
        issues=$((issues + 1))
    fi
    
    # 3. Systematic organization - Logical heading hierarchy
    local heading_hierarchy_issues=0
    local prev_level=1
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^#+\ ]]; then
            local current_level=${#line}
            current_level=$((current_level - ${#line%#*}))
            
            if [[ "$current_level" -gt $((prev_level + 1)) ]]; then
                heading_hierarchy_issues=$((heading_hierarchy_issues + 1))
            fi
            prev_level=$current_level
        fi
    done < "$file"
    
    if [[ "$heading_hierarchy_issues" -gt 0 ]]; then
        log_warn "Heading hierarchy issues in $file (don't skip levels: H1→H2→H3)"
        issues=$((issues + 1))
    fi
    
    # 4. Completeness - File should end with newline
    if [[ -n "$(tail -c1 "$file")" ]]; then
        log_warn "File $file doesn't end with newline (completeness principle)"
        issues=$((issues + 1))
    fi
    
    return "$issues"
}

# Generate quality report for a file
generate_file_quality_report() {
    local file="$1"
    local total_issues="$2"
    shift 2
    local specific_issues=("$@")
    
    local rel_path="${file#$PROJECT_ROOT/}"
    
    cat <<EOF
    {
      "file": "$rel_path",
      "status": $([ "$total_issues" -eq 0 ] && echo '"PASSED"' || echo '"FAILED"'),
      "issues_count": $total_issues,
      "issues": [
$(printf '        "%s"' "${specific_issues[@]}" | paste -sd, -)
      ],
      "checks": {
        "status_tag": $(validate_status_tag "$file" >/dev/null 2>&1 && echo 'true' || echo 'false'),
        "markdownlint": $(check_markdownlint "$file" >/dev/null 2>&1 && echo 'true' || echo 'false'),
        "content_quality": $(check_content_quality "$file" >/dev/null 2>&1 && echo 'true' || echo 'false'),
        "japanese_principles": $(check_japanese_principles "$file" >/dev/null 2>&1 && echo 'true' || echo 'false')
      }
    }
EOF
}

# Process a documentation file through quality gates
process_documentation_file() {
    local file="$1"
    
    log_debug "Processing documentation file: $file"
    
    local total_issues=0
    local file_issues=()
    
    # Capture issues from each check
    local temp_log="/tmp/quality_check_$$.log"
    
    # Status tag validation
    if ! validate_status_tag "$file" 2>"$temp_log"; then
        local issue_count=0
        while IFS= read -r line; do
            file_issues+=("Status: $line")
            issue_count=$((issue_count + 1))
        done < <(grep "Missing status tag" "$temp_log" | sed 's/.*: //')
        total_issues=$((total_issues + issue_count))
    fi
    
    # Markdownlint validation
    if [[ "$file" == *.md ]]; then
        check_markdownlint "$file" 2>"$temp_log" || {
            while IFS= read -r line; do
                [[ -n "$line" ]] && file_issues+=("Lint: $line")
                total_issues=$((total_issues + 1))
            done < <(grep -v "^\[" "$temp_log" || true)
        }
    fi
    
    # Content quality validation
    local content_issues=0
    check_content_quality "$file" 2>"$temp_log" || content_issues=$?
    if [[ "$content_issues" -gt 0 ]]; then
        while IFS= read -r line; do
            [[ -n "$line" ]] && file_issues+=("Content: $line")
        done < <(grep "Missing\|Insufficient\|Found\|exceeding" "$temp_log" | sed 's/.*: //')
        total_issues=$((total_issues + content_issues))
    fi
    
    # Japanese principles validation
    local principle_issues=0
    check_japanese_principles "$file" 2>"$temp_log" || principle_issues=$?
    if [[ "$principle_issues" -gt 0 ]]; then
        while IFS= read -r line; do
            [[ -n "$line" ]] && file_issues+=("Principles: $line")
        done < <(grep "Found\|violates\|issues\|doesn't" "$temp_log" | sed 's/.*: //')
        total_issues=$((total_issues + principle_issues))
    fi
    
    rm -f "$temp_log"
    
    # Generate file report
    generate_file_quality_report "$file" "$total_issues" "${file_issues[@]}"
    
    return "$total_issues"
}

# Main hook logic
execute_hook_logic() {
    log_info "Executing $HOOK_NAME hook logic"
    
    # Find all documentation files to check
    local doc_files=()
    for pattern in $DOC_PATTERNS; do
        while IFS= read -r -d '' file; do
            doc_files+=("$file")
        done < <(find "$PROJECT_ROOT" -name "$pattern" -type f -print0 2>/dev/null || true)
    done
    
    if [[ ${#doc_files[@]} -eq 0 ]]; then
        log_info "No documentation files found to validate"
        return 0
    fi
    
    log_info "Validating ${#doc_files[@]} documentation files"
    
    # Process each file and collect results
    local total_violations=0
    local failed_files=0
    local reports=()
    
    for file in "${doc_files[@]}"; do
        log_debug "Validating: $file"
        
        local file_issues=0
        local file_report
        file_report=$(process_documentation_file "$file")
        process_documentation_file "$file" >/dev/null 2>&1 || file_issues=$?
        
        if [[ "$file_issues" -gt 0 ]]; then
            failed_files=$((failed_files + 1))
            total_violations=$((total_violations + file_issues))
            log_warn "Quality gate FAILED for $file ($file_issues issues)"
        else
            log_debug "Quality gate PASSED for $file"
        fi
        
        reports+=("$file_report")
    done
    
    # Generate comprehensive report
    local report_file="/tmp/documentation_quality_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
  "hook": "$HOOK_NAME",
  "version": "$HOOK_VERSION",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_root": "$PROJECT_ROOT",
  "summary": {
    "total_files": ${#doc_files[@]},
    "failed_files": $failed_files,
    "total_violations": $total_violations,
    "quality_status": $([ "$total_violations" -eq 0 ] && echo '"PASSED"' || echo '"FAILED"')
  },
  "standards": {
    "max_line_length": $MAX_LINE_LENGTH,
    "min_sections_count": $MIN_SECTIONS_COUNT,
    "required_sections": [$(printf '"%s"' "${REQUIRED_SECTIONS[@]}" | paste -sd, -)],
    "enforce_status_tags": true,
    "japanese_principles": true
  },
  "files": [
$(printf '%s' "${reports[@]}" | paste -sd, -)
  ]
}
EOF
    
    # Integration with orchestrator
    integrate_with_orchestrator "$report_file" "$total_violations" "$failed_files"
    
    # Handle blocking vs warning behavior
    if [[ "$total_violations" -gt 0 ]]; then
        if [[ "$ENFORCE_BLOCKING" = "true" ]] && [[ "$DRY_RUN" != "true" ]]; then
            log_error "❌ Documentation quality gate BLOCKED: $total_violations violations in $failed_files files"
            log_error "📋 Full report: $report_file"
            log_error "Fix quality issues or set ENFORCE_BLOCKING=false to allow warnings only"
            return 1
        else
            log_warn "⚠ Documentation quality gate WARNING: $total_violations violations in $failed_files files"
            log_warn "📋 Full report: $report_file"
        fi
    else
        log_info "✓ Documentation quality gate PASSED: All files meet quality standards"
    fi
    
    log_info "Hook logic completed successfully"
    return 0
}

# Integration with orchestrator
integrate_with_orchestrator() {
    local report_file="$1"
    local violations="$2"
    local failed_files="$3"
    
    log_debug "Integrating with orchestrator system"
    
    local session_file="$ORCHESTRATOR_DIR/session.json"
    if [[ -f "$session_file" ]]; then
        log_debug "Orchestrator session found, reporting quality status"
        
        local quality_update=$(cat <<EOF
{
  "quality_gate": {
    "hook_name": "$HOOK_NAME",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "status": $([ "$violations" -eq 0 ] && echo '"success"' || echo '"failure"'),
    "violations": $violations,
    "failed_files": $failed_files,
    "report_file": "$report_file",
    "enforced": $([[ "$ENFORCE_BLOCKING" = "true" ]] && echo 'true' || echo 'false'),
    "message": "Documentation quality validation completed"
  }
}
EOF
)
        
        # Store update for orchestrator
        echo "$quality_update" > "$ORCHESTRATOR_DIR/documentation_quality_status.json"
        
        # Try to post to orchestrator API if available
        if command -v curl >/dev/null 2>&1; then
            curl -s -X POST "http://localhost:3001/api/hooks/documentation-quality" \
                 -H "Content-Type: application/json" \
                 -d "$quality_update" >/dev/null 2>&1 || true
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
    
    # Create error report
    local error_report="/tmp/documentation_quality_error_$(date +%Y%m%d_%H%M%S).json"
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