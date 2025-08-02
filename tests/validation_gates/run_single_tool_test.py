#!/usr/bin/env python3
"""
Quick test script to validate a single MCP tool
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from validation_framework import ValidationFramework


async def main():
    """Run validation for a single tool."""
    framework = ValidationFramework()
    
    # Test orchestrator_get_status as it's simple and doesn't require parameters
    tool_name = "orchestrator_get_status"
    
    print(f"Testing tool: {tool_name}")
    print("-" * 50)
    
    result = await framework.validate_tool_systematically(tool_name)
    
    print(f"\nOverall Success: {result['success']}")
    print(f"Tool: {result['tool_name']}")
    print(f"Category: {result['category']}")
    
    print("\nValidation Results:")
    for validation in result['validation_results']:
        print(f"  - {validation['level']}: {validation['status']}")
        if validation['issues']:
            print(f"    Issues: {validation['issues']}")
        if validation.get('resolution_attempted'):
            print(f"    Resolution Attempted: {validation['resolution_attempted']}")
            print(f"    Resolution Successful: {validation['resolution_successful']}")
    
    # Save result to file
    import json
    with open("single_tool_test_result.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nFull results saved to: single_tool_test_result.json")


if __name__ == "__main__":
    asyncio.run(main())