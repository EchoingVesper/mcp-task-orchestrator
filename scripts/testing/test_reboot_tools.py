#!/usr/bin/env python3
"""
Test script for server reboot tools integration.

This script validates that the reboot tools are properly integrated
into the MCP server and can be invoked successfully.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_task_orchestrator.server.reboot_tools import REBOOT_TOOL_HANDLERS, REBOOT_TOOLS
from mcp_task_orchestrator.server.reboot_integration import get_reboot_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_reboot_tools")


async def test_tool_registration():
    """Test that all reboot tools are properly registered."""
    logger.info("Testing tool registration...")
    
    expected_tools = [
        "orchestrator_restart_server",
        "orchestrator_health_check", 
        "orchestrator_shutdown_prepare",
        "orchestrator_reconnect_test",
        "orchestrator_restart_status"
    ]
    
    # Check that all tools are defined
    tool_names = [tool.name for tool in REBOOT_TOOLS]
    logger.info(f"Registered tools: {tool_names}")
    
    for expected_tool in expected_tools:
        if expected_tool not in tool_names:
            logger.error(f"Missing tool: {expected_tool}")
            return False
        
        if expected_tool not in REBOOT_TOOL_HANDLERS:
            logger.error(f"Missing handler for tool: {expected_tool}")
            return False
    
    logger.info("✓ All tools properly registered")
    return True


async def test_health_check():
    """Test the health check tool."""
    logger.info("Testing health check tool...")
    
    try:
        handler = REBOOT_TOOL_HANDLERS["orchestrator_health_check"]
        result = await handler({})
        
        # Parse the response
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        logger.info(f"Health check result: {response_data}")
        
        if "healthy" not in response_data:
            logger.error("Health check response missing 'healthy' field")
            return False
        
        logger.info("✓ Health check tool working")
        return True
        
    except Exception as e:
        logger.error(f"Health check tool failed: {e}")
        return False


async def test_shutdown_prepare():
    """Test the shutdown prepare tool."""
    logger.info("Testing shutdown prepare tool...")
    
    try:
        handler = REBOOT_TOOL_HANDLERS["orchestrator_shutdown_prepare"]
        result = await handler({})
        
        # Parse the response
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        logger.info(f"Shutdown prepare result: {response_data}")
        
        if "ready_for_shutdown" not in response_data:
            logger.error("Shutdown prepare response missing 'ready_for_shutdown' field")
            return False
        
        logger.info("✓ Shutdown prepare tool working")
        return True
        
    except Exception as e:
        logger.error(f"Shutdown prepare tool failed: {e}")
        return False


async def test_restart_status():
    """Test the restart status tool."""
    logger.info("Testing restart status tool...")
    
    try:
        handler = REBOOT_TOOL_HANDLERS["orchestrator_restart_status"]
        result = await handler({})
        
        # Parse the response
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        logger.info(f"Restart status result: {response_data}")
        
        if "current_status" not in response_data:
            logger.error("Restart status response missing 'current_status' field")
            return False
        
        logger.info("✓ Restart status tool working")
        return True
        
    except Exception as e:
        logger.error(f"Restart status tool failed: {e}")
        return False


async def test_reconnect_test():
    """Test the reconnect test tool."""
    logger.info("Testing reconnect test tool...")
    
    try:
        handler = REBOOT_TOOL_HANDLERS["orchestrator_reconnect_test"]
        result = await handler({})
        
        # Parse the response
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        logger.info(f"Reconnect test result: {response_data}")
        
        if "test_completed" not in response_data:
            logger.error("Reconnect test response missing 'test_completed' field")
            return False
        
        logger.info("✓ Reconnect test tool working")
        return True
        
    except Exception as e:
        logger.error(f"Reconnect test tool failed: {e}")
        return False


async def test_reboot_manager_integration():
    """Test the reboot manager integration."""
    logger.info("Testing reboot manager integration...")
    
    try:
        reboot_manager = get_reboot_manager()
        
        # Test getting restart readiness
        readiness = await reboot_manager.get_restart_readiness()
        logger.info(f"Restart readiness: {readiness}")
        
        if "ready" not in readiness:
            logger.error("Restart readiness missing 'ready' field")
            return False
        
        # Test getting shutdown status
        status = await reboot_manager.get_shutdown_status()
        logger.info(f"Shutdown status: {status}")
        
        if "phase" not in status:
            logger.error("Shutdown status missing 'phase' field")
            return False
        
        logger.info("✓ Reboot manager integration working")
        return True
        
    except Exception as e:
        logger.error(f"Reboot manager integration failed: {e}")
        return False


async def run_all_tests():
    """Run all tests and report results."""
    logger.info("Starting reboot tools integration tests...")
    
    tests = [
        ("Tool Registration", test_tool_registration),
        ("Health Check", test_health_check),
        ("Shutdown Prepare", test_shutdown_prepare),
        ("Restart Status", test_restart_status),
        ("Reconnect Test", test_reconnect_test),
        ("Reboot Manager Integration", test_reboot_manager_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            success = await test_func()
            if success:
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                failed += 1
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            failed += 1
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    logger.info("\n--- Test Results ---")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed!")
        return True
    else:
        logger.error(f"❌ {failed} tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)