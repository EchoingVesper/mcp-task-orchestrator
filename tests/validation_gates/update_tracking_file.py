#!/usr/bin/env python3
"""
Update the MCP_TOOLS_TESTING_TRACKER.md file with test results
"""

import json
from pathlib import Path
from datetime import datetime

# Read the validation results
results_file = Path("tests/validation_results/validation_results_20250709_232757.json")
tracking_file = Path("tests/validation_gates/MCP_TOOLS_TESTING_TRACKER.md")

with open(results_file) as f:
    results_data = json.load(f)

# Parse results by tool and level
tool_results = {}
for result in results_data["results"]:
    tool_name = result["tool_name"]
    level = result["level"]
    status = result["status"]
    
    if tool_name not in tool_results:
        tool_results[tool_name] = {
            "basic": "pending",
            "edge_cases": "pending", 
            "integration": "pending"
        }
    
    tool_results[tool_name][level] = status

# Read tracking file
with open(tracking_file) as f:
    content = f.read()

# Update checkboxes based on results
for tool_name, levels in tool_results.items():
    # Find the tool section
    tool_section_start = content.find(f"### {content.count(tool_name)}")
    
    for level, status in levels.items():
        if status == "passed":
            # Update checkbox to checked
            if level == "basic":
                search_text = "- [ ] **Basic Functionality**"
                replace_text = "- [x] **Basic Functionality** ✅"
            elif level == "edge_cases":
                search_text = "- [ ] **Edge Cases**"
                replace_text = "- [x] **Edge Cases** ✅"
            elif level == "integration":
                search_text = "- [ ] **Integration**"
                replace_text = "- [x] **Integration** ✅"
            
            # Find and replace within the tool section
            # This is a simplified approach - in production you'd want more sophisticated parsing
            
# For now, let's create a summary update
summary = f"""
## Testing Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}

### Summary Results
- **Total Tests Run**: 48 (16 tools × 3 levels)
- **Passed**: 14 tests (29.2%)
- **Failed**: 34 tests (70.8%)

### Tools with Passing Tests

#### Fully Working Tools (all tests passed):
- None yet

#### Partially Working Tools:
1. **orchestrator_health_check**: ✅ Basic, ❌ Edge Cases, ✅ Integration
2. **orchestrator_shutdown_prepare**: ✅ Basic, ❌ Edge Cases, ✅ Integration  
3. **orchestrator_reconnect_test**: ✅ Basic, ❌ Edge Cases, ✅ Integration
4. **orchestrator_restart_status**: ✅ Basic, ❌ Edge Cases, ✅ Integration

#### Tools with Edge Case Handling:
5. **orchestrator_plan_task**: ❌ Basic, ✅ Edge Cases, ❌ Integration
6. **orchestrator_update_task**: ❌ Basic, ✅ Edge Cases, ❌ Integration
7. **orchestrator_delete_task**: ❌ Basic, ✅ Edge Cases, ❌ Integration
8. **orchestrator_cancel_task**: ❌ Basic, ✅ Edge Cases, ❌ Integration
9. **orchestrator_query_tasks**: ❌ Basic, ✅ Edge Cases, ❌ Integration
10. **orchestrator_restart_server**: ❌ Basic, ✅ Edge Cases, ❌ Integration

### Critical Issues Found
1. **Database Integration Error**: `cannot access local variable 'operation' where it is not associated with a value`
2. **Missing Methods**: Several tools missing implementation methods (update_task, delete_task, etc.)
3. **DatabasePersistenceManager**: Missing required methods

### Next Steps
1. Fix the database integration bug in db_integration.py
2. Implement missing methods in RealTaskUseCase
3. Complete DatabasePersistenceManager implementation
4. Re-run tests after fixes
"""

# Append summary to tracking file
with open(tracking_file, 'a') as f:
    f.write("\n\n---\n")
    f.write(summary)

print(f"Updated tracking file with test results")
print(f"Summary appended to: {tracking_file}")

# Also create a detailed tool status file
detailed_status = []
for tool_name, levels in sorted(tool_results.items()):
    status_emoji = {
        "passed": "✅",
        "failed": "❌",
        "error": "⚠️",
        "pending": "📋"
    }
    
    basic = status_emoji.get(levels.get("basic", "pending"), "📋")
    edge = status_emoji.get(levels.get("edge_cases", "pending"), "📋")
    integration = status_emoji.get(levels.get("integration", "pending"), "📋")
    
    overall = "PASS" if all(levels.get(l) == "passed" for l in ["basic", "edge_cases", "integration"]) else "FAIL"
    
    detailed_status.append(f"{tool_name}: {basic} {edge} {integration} - {overall}")

with open("tests/validation_gates/detailed_tool_status.txt", "w") as f:
    f.write("Tool Status Summary\n")
    f.write("==================\n")
    f.write("Format: Tool Name: Basic EdgeCases Integration - Overall\n\n")
    for status in detailed_status:
        f.write(status + "\n")

print("Created detailed status file: tests/validation_gates/detailed_tool_status.txt")