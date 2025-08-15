# [Hook Name] - Claude Code Hook Template

## Overview

This template provides the structure for creating Claude Code hooks that integrate with the MCP Task Orchestrator's 
quality and lifecycle management systems. Hooks enable automated validation, enforcement, and improvement of project 
standards.

**Hook Type**: [Pre-command | Post-command | File-change | Git | Custom]
**Trigger**: [When this hook executes]
**Purpose**: [Primary purpose and value]
**Integration**: [How it integrates with orchestrator and other systems]

## Hook Specification

### Basic Information
- **Hook Name**: `[hook-name]`
- **File Location**: `.claude/hooks/[hook-name].sh`
- **Execution Trigger**: [Specific trigger condition]
- **Expected Runtime**: [Typical execution time]
- **Dependencies**: [Required tools, services, or other hooks]

### Hook Categories
| Category | Purpose | Examples |
|----------|---------|----------|
| **Quality Gates** | Enforce quality standards | Linting, format validation, documentation checks |
| **Lifecycle Management** | Manage artifact lifecycles | Cleanup, archiving, status updates |
| **Integration** | Connect with external systems | Orchestrator updates, Git operations |
| **Validation** | Verify system state | Configuration validation, dependency checks |
| **Automation** | Automate routine tasks | File organization, template application |

## Implementation Template

### Shell Script Structure
```bash
#!/bin/bash

# [Hook Name] - [Brief Description]
# Part of MCP Task Orchestrator Documentation Ecosystem Modernization
# 
# Purpose: [Detailed purpose statement]
# Trigger: [When this hook executes]
# Integration: [How it connects to orchestrator and other systems]

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
HOOK_NAME="[hook-name]"
HOOK_VERSION="1.0.0"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
DRY_RUN="${DRY_RUN:-false}"

# Project paths
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
ORCHESTRATOR_DIR="${PROJECT_ROOT}/.task_orchestrator"
CLAUDE_CONFIG_DIR="${PROJECT_ROOT}/.claude"
HOOKS_DIR="${CLAUDE_CONFIG_DIR}/hooks"

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

# Hook-specific functions
validate_prerequisites() {
    log_debug "Validating prerequisites for $HOOK_NAME"
    
    # Check required tools
    local required_tools=([tool1] [tool2] [tool3])
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_error "Required tool '$tool' not found"
            return 1
        fi
    done
    
    # Check file/directory prerequisites
    [[ -d "$PROJECT_ROOT" ]] || {
        log_error "Project root not found: $PROJECT_ROOT"
        return 1
    }
    
    # Hook-specific prerequisite checks
    # [Add specific validation logic here]
    
    log_debug "Prerequisites validated successfully"
    return 0
}

# Main hook logic
execute_hook_logic() {
    log_info "Executing $HOOK_NAME hook logic"
    
    # [Implement main hook functionality here]
    # This is where the core hook behavior goes
    
    # Example patterns:
    
    # File processing
    # while IFS= read -r -d '' file; do
    #     process_file "$file"
    # done < <(find "$PROJECT_ROOT" -type f -name "*.md" -print0)
    
    # Configuration validation
    # validate_configuration_files
    
    # Quality checks
    # run_quality_checks
    
    # Orchestrator integration
    # update_orchestrator_status
    
    log_info "Hook logic completed successfully"
}

# Integration functions
integrate_with_orchestrator() {
    log_debug "Integrating with orchestrator system"
    
    # Check if orchestrator is available
    if [[ -f "$ORCHESTRATOR_DIR/session.json" ]]; then
        log_debug "Orchestrator session found, integrating"
        
        # Example integration patterns:
        # - Update task status
        # - Log hook execution
        # - Report validation results
        # - Trigger orchestrator workflows
        
        # [Add orchestrator integration logic here]
        
    else
        log_debug "No orchestrator session found, skipping integration"
    fi
}

# Error handling and recovery
handle_error() {
    local exit_code=$1
    local line_number=$2
    
    log_error "Hook failed at line $line_number with exit code $exit_code"
    
    # Hook-specific error handling
    # [Add error recovery logic here]
    
    # Cleanup if needed
    cleanup_on_error
    
    exit "$exit_code"
}

cleanup_on_error() {
    log_debug "Performing error cleanup"
    
    # [Add cleanup logic here]
    # - Remove temporary files
    # - Reset partial changes
    # - Update status indicators
}

# Success cleanup
cleanup_on_success() {
    log_debug "Performing success cleanup"
    
    # [Add cleanup logic here]
    # - Archive temporary files
    # - Update status indicators
    # - Log success metrics
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
    if [[ "$DRY_RUN" = "true" ]]; then
        log_info "DRY_RUN mode enabled, simulating hook execution"
        # [Add dry-run simulation logic]
    else
        execute_hook_logic
    fi
    
    # Integration with orchestrator
    integrate_with_orchestrator
    
    # Success cleanup
    cleanup_on_success
    
    log_info "$HOOK_NAME hook completed successfully"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

### Python Hook Alternative
```python
#!/usr/bin/env python3

"""
[Hook Name] - [Brief Description]
Part of MCP Task Orchestrator Documentation Ecosystem Modernization

Purpose: [Detailed purpose statement]
Trigger: [When this hook executes]  
Integration: [How it connects to orchestrator and other systems]
"""

import sys
import os
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configuration
HOOK_NAME = "[hook-name]"
HOOK_VERSION = "1.0.0"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

# Project paths
PROJECT_ROOT = Path(subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], 
    capture_output=True, text=True, check=False
).stdout.strip() or os.getcwd())

ORCHESTRATOR_DIR = PROJECT_ROOT / ".task_orchestrator"
CLAUDE_CONFIG_DIR = PROJECT_ROOT / ".claude"
HOOKS_DIR = CLAUDE_CONFIG_DIR / "hooks"

# Logging setup
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(HOOK_NAME)

class HookExecutionError(Exception):
    """Custom exception for hook execution failures"""
    pass

class [HookName]Hook:
    """Main hook implementation class"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.orchestrator_dir = ORCHESTRATOR_DIR
        self.dry_run = DRY_RUN
        
    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for hook execution"""
        logger.debug(f"Validating prerequisites for {HOOK_NAME}")
        
        # Check required tools
        required_tools = ["[tool1]", "[tool2]", "[tool3]"]
        for tool in required_tools:
            if not self._command_exists(tool):
                logger.error(f"Required tool '{tool}' not found")
                return False
        
        # Check file/directory prerequisites
        if not self.project_root.exists():
            logger.error(f"Project root not found: {self.project_root}")
            return False
        
        # Hook-specific prerequisite checks
        # [Add specific validation logic here]
        
        logger.debug("Prerequisites validated successfully")
        return True
    
    def execute_hook_logic(self) -> Dict[str, Any]:
        """Main hook logic implementation"""
        logger.info(f"Executing {HOOK_NAME} hook logic")
        
        results = {
            "status": "success",
            "processed_files": [],
            "issues_found": [],
            "actions_taken": []
        }
        
        # [Implement main hook functionality here]
        # This is where the core hook behavior goes
        
        # Example patterns:
        
        # File processing
        # for file_path in self._find_target_files():
        #     result = self._process_file(file_path)
        #     results["processed_files"].append(str(file_path))
        
        # Configuration validation  
        # validation_result = self._validate_configuration()
        # results["issues_found"].extend(validation_result.get("issues", []))
        
        # Quality checks
        # quality_result = self._run_quality_checks()
        # results["actions_taken"].extend(quality_result.get("actions", []))
        
        logger.info("Hook logic completed successfully")
        return results
    
    def integrate_with_orchestrator(self, results: Dict[str, Any]) -> None:
        """Integration with orchestrator system"""
        logger.debug("Integrating with orchestrator system")
        
        session_file = self.orchestrator_dir / "session.json"
        if session_file.exists():
            logger.debug("Orchestrator session found, integrating")
            
            # Example integration patterns:
            # - Update task status
            # - Log hook execution
            # - Report validation results
            # - Trigger orchestrator workflows
            
            # [Add orchestrator integration logic here]
            
        else:
            logger.debug("No orchestrator session found, skipping integration")
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        return subprocess.run(
            ["which", command], 
            capture_output=True
        ).returncode == 0
    
    def _find_target_files(self) -> List[Path]:
        """Find files to process based on hook criteria"""
        # [Implement file discovery logic]
        pass
    
    def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process individual file"""
        # [Implement file processing logic]
        pass
    
    def run(self) -> int:
        """Main execution method"""
        try:
            logger.info(f"Starting {HOOK_NAME} hook (version {HOOK_VERSION})")
            
            # Validate prerequisites
            if not self.validate_prerequisites():
                logger.error("Prerequisites validation failed")
                return 1
            
            # Execute main hook logic
            if self.dry_run:
                logger.info("DRY_RUN mode enabled, simulating hook execution")
                # [Add dry-run simulation logic]
                results = {"status": "simulated", "message": "Dry run completed"}
            else:
                results = self.execute_hook_logic()
            
            # Integration with orchestrator
            self.integrate_with_orchestrator(results)
            
            logger.info(f"{HOOK_NAME} hook completed successfully")
            return 0
            
        except Exception as e:
            logger.error(f"Hook execution failed: {e}")
            return 1

def main() -> int:
    """Main entry point"""
    hook = [HookName]Hook()
    return hook.run()

if __name__ == "__main__":
    sys.exit(main())
```

## Hook Configuration

### Claude Code Hook Configuration
Add to `.claude/config.json`:

```json
{
  "hooks": {
    "[trigger-type]": [
      ".claude/hooks/[hook-name].sh"
    ]
  },
  "hookSettings": {
    "[hook-name]": {
      "enabled": true,
      "logLevel": "INFO",
      "dryRun": false,
      "[hook-specific-setting]": "[value]"
    }
  }
}
```

### Available Triggers
| Trigger Type | When Executed | Use Cases |
|--------------|---------------|-----------|
| `pre-command` | Before Claude Code commands | Validation, preparation |
| `post-command` | After Claude Code commands | Cleanup, reporting |
| `file-change` | When files are modified | Quality gates, formatting |
| `git-pre-commit` | Before Git commits | Code quality, compliance |
| `git-post-commit` | After Git commits | Status updates, notifications |

## Integration Patterns

### Orchestrator Integration
```bash
# Check if orchestrator is running
if curl -s "http://localhost:3001/health" >/dev/null 2>&1; then
    # Update orchestrator with hook results
    curl -X POST "http://localhost:3001/api/hooks/report" \
        -H "Content-Type: application/json" \
        -d "{
            \"hook\": \"$HOOK_NAME\",
            \"status\": \"success\",
            \"results\": $results_json
        }"
fi
```

### Status Tag Management
```bash
# Update file status tags based on hook results
update_status_tag() {
    local file="$1"
    local new_status="$2"
    
    # Extract current status tag
    local current_tag=$(basename "$file" | grep -o '^\[.*\]' || echo "")
    
    # Update with new status
    if [[ -n "$current_tag" ]]; then
        # Replace existing tag
        local new_name=$(basename "$file" | sed "s/^\[.*\]/[$new_status]/")
        mv "$file" "$(dirname "$file")/$new_name"
    else
        # Add new tag
        local new_name="[$new_status]$(basename "$file")"
        mv "$file" "$(dirname "$file")/$new_name"
    fi
}
```

### Quality Gate Enforcement
```bash
# Quality gate pattern
enforce_quality_gate() {
    local check_name="$1"
    local files=("${@:2}")
    
    log_info "Enforcing quality gate: $check_name"
    
    local failed_files=()
    for file in "${files[@]}"; do
        if ! validate_file_quality "$file"; then
            failed_files+=("$file")
        fi
    done
    
    if [[ ${#failed_files[@]} -gt 0 ]]; then
        log_error "Quality gate failed for ${#failed_files[@]} files"
        for failed_file in "${failed_files[@]}"; do
            log_error "  - $failed_file"
        done
        return 1
    fi
    
    log_info "Quality gate passed: $check_name"
    return 0
}
```

## Testing Strategy

### Unit Testing
```bash
# Test individual hook functions
test_validate_prerequisites() {
    local test_dir="/tmp/hook_test_$$"
    mkdir -p "$test_dir"
    cd "$test_dir"
    
    # Test with missing prerequisites
    if validate_prerequisites 2>/dev/null; then
        echo "FAIL: Should fail with missing prerequisites"
        return 1
    fi
    
    # Test with valid prerequisites
    # [Set up valid environment]
    if ! validate_prerequisites; then
        echo "FAIL: Should pass with valid prerequisites"
        return 1
    fi
    
    echo "PASS: Prerequisites validation works correctly"
    cleanup_test_dir "$test_dir"
}
```

### Integration Testing
```bash
# Test hook integration with orchestrator
test_orchestrator_integration() {
    local test_results='{"status": "test", "message": "Test execution"}'
    
    # Mock orchestrator session
    mkdir -p "$ORCHESTRATOR_DIR"
    echo '{"session_id": "test"}' > "$ORCHESTRATOR_DIR/session.json"
    
    # Test integration
    integrate_with_orchestrator
    
    # Verify integration worked
    # [Add verification logic]
    
    echo "PASS: Orchestrator integration works correctly"
}
```

### End-to-End Testing
```bash
# Full hook execution test
test_full_execution() {
    export DRY_RUN=true
    export LOG_LEVEL=DEBUG
    
    # Run full hook
    if ! main; then
        echo "FAIL: Full hook execution failed"
        return 1
    fi
    
    # Verify expected outcomes
    # [Add verification logic]
    
    echo "PASS: Full hook execution works correctly"
}
```

## Best Practices

### Performance Optimization
- **Early Exit**: Return early when conditions aren't met
- **Batch Processing**: Process multiple files together when possible
- **Caching**: Cache expensive operations between runs
- **Parallel Processing**: Use parallel processing for independent tasks

### Error Handling
- **Graceful Degradation**: Continue operation when possible
- **Clear Error Messages**: Provide actionable error messages
- **State Recovery**: Clean up partial changes on failure
- **Logging**: Log all important operations and errors

### Security Considerations
- **Input Validation**: Validate all inputs and file paths
- **Path Traversal Prevention**: Use absolute paths and validate directories
- **Command Injection Prevention**: Properly escape shell commands
- **Permissions**: Run with minimal required permissions

### Maintainability
- **Modular Design**: Break complex logic into functions
- **Configuration**: Make behavior configurable
- **Documentation**: Document complex logic and decisions
- **Version Management**: Track hook versions and changes

## Common Hook Types

### Documentation Quality Hook
```bash
# Validate markdown files for quality standards
validate_markdown_quality() {
    local file="$1"
    
    # Check markdownlint compliance
    if ! markdownlint "$file"; then
        return 1
    fi
    
    # Check for required sections
    if ! grep -q "^## Overview" "$file"; then
        log_warn "Missing Overview section in $file"
    fi
    
    # Check status tags for lifecycle management
    if [[ $(basename "$file") =~ ^\[.*\] ]]; then
        validate_status_tag "$file"
    fi
    
    return 0
}
```

### File Organization Hook
```bash
# Ensure files are in correct locations
enforce_file_organization() {
    # Check for misplaced files
    find "$PROJECT_ROOT" -maxdepth 1 -name "*.tmp" -o -name "*.log" -o -name "*~" | while read -r misplaced_file; do
        log_warn "Misplaced file in root: $misplaced_file"
        
        if [[ "$DRY_RUN" != "true" ]]; then
            # Move to appropriate location
            move_to_appropriate_location "$misplaced_file"
        fi
    done
}
```

### Status Tag Validation Hook
```bash
# Validate and update status tags
validate_status_tags() {
    find "$PROJECT_ROOT" -name "*.md" | while read -r file; do
        local filename=$(basename "$file")
        
        # Check if file should have status tag
        if should_have_status_tag "$file"; then
            if [[ ! "$filename" =~ ^\[.*\] ]]; then
                log_warn "Missing status tag: $file"
                
                if [[ "$DRY_RUN" != "true" ]]; then
                    add_default_status_tag "$file"
                fi
            fi
        fi
    done
}
```

## Troubleshooting

### Common Issues

#### Hook Not Executing
**Symptoms**: Hook doesn't run when expected
**Causes**:
- Hook not registered in `.claude/config.json`
- Permission issues with hook script
- Invalid hook script syntax

**Solutions**:
1. Verify hook registration in configuration
2. Check script permissions: `chmod +x .claude/hooks/[hook-name].sh`
3. Test script syntax: `bash -n .claude/hooks/[hook-name].sh`

#### Hook Execution Failures  
**Symptoms**: Hook executes but fails with errors
**Causes**:
- Missing dependencies
- Invalid file paths
- Permission issues

**Solutions**:
1. Check prerequisites with `LOG_LEVEL=DEBUG`
2. Verify all file paths exist and are accessible
3. Test with `DRY_RUN=true` first

#### Performance Issues
**Symptoms**: Hook takes too long to execute
**Causes**:
- Processing too many files
- Inefficient algorithms
- External tool bottlenecks

**Solutions**:
1. Add file filtering to reduce scope
2. Implement parallel processing
3. Cache expensive operations

## Documentation Standards

### Hook Documentation Requirements
- Purpose and trigger clearly stated
- Prerequisites and dependencies listed
- Configuration options documented
- Integration points explained
- Testing instructions provided

### Code Documentation
- Functions have clear purpose comments
- Complex logic explained
- Error handling documented
- Integration patterns demonstrated

---

## Template Usage Notes

### For Hook Developers
- Start with the appropriate script template (Bash or Python)
- Customize the placeholder content for specific hook purpose
- Test thoroughly in development environment
- Follow security best practices
- Document integration requirements

### Quality Requirements
- All hooks must pass testing requirements
- Error handling must be comprehensive
- Integration with orchestrator must be optional
- Performance impact must be minimal
- Security considerations must be addressed

This template enables creation of robust, well-integrated hooks that enhance the MCP Task Orchestrator's automation capabilities while maintaining consistency with project standards.