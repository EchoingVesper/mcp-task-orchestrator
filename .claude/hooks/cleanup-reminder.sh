#!/bin/bash
# Claude Code Hook: Cleanup Reminder
# Part of Phase 4 - Documentation Ecosystem Modernization
# 
# This hook reminds about cleanup tasks and lifecycle management
# Runs after Claude Code commands to check for temporary file accumulation

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMP_DIR="$PROJECT_ROOT/scripts/testing/temporary"

# Function to check for temporary files in root
check_root_temp_files() {
    local temp_files=0
    
    # Count temporary files in root
    if ls "$PROJECT_ROOT"/fix_*.py >/dev/null 2>&1; then
        temp_files=$((temp_files + $(ls "$PROJECT_ROOT"/fix_*.py 2>/dev/null | wc -l)))
    fi
    
    if ls "$PROJECT_ROOT"/system_health*.json >/dev/null 2>&1; then
        temp_files=$((temp_files + $(ls "$PROJECT_ROOT"/system_health*.json 2>/dev/null | wc -l)))
    fi
    
    if ls "$PROJECT_ROOT"/test-*hooks*.sh >/dev/null 2>&1; then
        temp_files=$((temp_files + $(ls "$PROJECT_ROOT"/test-*hooks*.sh 2>/dev/null | wc -l)))
    fi
    
    if ls "$PROJECT_ROOT"/test_mcp_compatibility.py >/dev/null 2>&1; then
        temp_files=$((temp_files + 1))
    fi
    
    echo "$temp_files"
}

# Function to check temporary directory size
check_temp_directory() {
    if [ -d "$TEMP_DIR" ]; then
        find "$TEMP_DIR" -name "*.py" -o -name "*.sh" -o -name "*.json" | wc -l
    else
        echo "0"
    fi
}

# Function to get age of oldest temp file
get_oldest_temp_age() {
    local oldest_age=0
    local now=$(date +%s)
    
    # Check root directory
    for pattern in "fix_*.py" "system_health*.json" "test-*hooks*.sh"; do
        for file in "$PROJECT_ROOT"/$pattern; do
            if [ -f "$file" ]; then
                local file_time=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
                local age=$(( (now - file_time) / 86400 ))
                if [ "$age" -gt "$oldest_age" ]; then
                    oldest_age=$age
                fi
            fi
        done
    done
    
    # Check temp directory
    if [ -d "$TEMP_DIR" ]; then
        for file in "$TEMP_DIR"/*.py "$TEMP_DIR"/*.sh "$TEMP_DIR"/*.json; do
            if [ -f "$file" ]; then
                local file_time=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
                local age=$(( (now - file_time) / 86400 ))
                if [ "$age" -gt "$oldest_age" ]; then
                    oldest_age=$age
                fi
            fi
        done
    fi
    
    echo "$oldest_age"
}

# Main logic
main() {
    local root_temp_count=$(check_root_temp_files)
    local temp_dir_count=$(check_temp_directory)
    local oldest_age=$(get_oldest_temp_age)
    local total_temp=$((root_temp_count + temp_dir_count))
    
    # Skip if no temporary files
    if [ "$total_temp" -eq 0 ]; then
        exit 0
    fi
    
    # Trigger reminders based on conditions
    local should_remind=0
    local urgency="INFO"
    local message=""
    
    if [ "$total_temp" -gt 15 ]; then
        should_remind=1
        urgency="WARN"
        message="High temporary file count: $total_temp files"
    elif [ "$oldest_age" -gt 14 ]; then
        should_remind=1
        urgency="WARN" 
        message="Old temporary files detected: oldest is $oldest_age days"
    elif [ "$total_temp" -gt 8 ] && [ "$oldest_age" -gt 7 ]; then
        should_remind=1
        urgency="INFO"
        message="Consider cleanup: $total_temp files, oldest $oldest_age days"
    fi
    
    if [ "$should_remind" -eq 1 ]; then
        echo ""
        echo "🧹 CLEANUP REMINDER [$urgency]"
        echo "   $message"
        echo ""
        echo "   Root directory: $root_temp_count temporary files"
        echo "   Temp directory: $temp_dir_count files" 
        echo ""
        echo "   Quick cleanup options:"
        echo "   • Run: python scripts/lifecycle/automated_cleanup_manager.py --dry-run"
        echo "   • Manual: mv fix_*.py system_health*.json scripts/testing/temporary/"
        echo ""
    fi
}

# Only run if this is actually a hook invocation
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi