# MCP Error Codes Unit Tests
"""
Comprehensive unit tests for MCP JSON-RPC error code implementation.

Tests ensure proper error code mapping, response formatting, and integration
with the existing error sanitization framework.
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime
from typing import Dict, Any

# from mcp_task_orchestrator.infrastructure.mcp.error_codes import  # TODO: Complete this import

# from mcp_task_orchestrator.infrastructure.mcp.error_handling import  # TODO: Complete this import

# from mcp_task_orchestrator.infrastructure.security.error_sanitization import  # TODO: Complete this import

# from mcp_task_orchestrator.domain.exceptions import  # TODO: Complete this import


class TestMCPErrorCodes:
    """Test MCP error code constants and mappings."""
    
    def test_error_code_values(self):
        """Test that error codes have correct JSON-RPC values."""
        assert MCPErrorCode.PARSE_ERROR.value == -32700
        assert MCPErrorCode.INVALID_REQUEST.value == -32600
        assert MCPErrorCode.METHOD_NOT_FOUND.value == -32601
        assert MCPErrorCode.INVALID_PARAMS.value == -32602
        assert MCPErrorCode.INTERNAL_ERROR.value == -32603
        
        # MCP-specific error codes in server range
        assert MCPErrorCode.TASK_NOT_FOUND.value == -32000
        assert MCPErrorCode.PERMISSION_DENIED.value == -32001
        assert MCPErrorCode.VALIDATION_FAILED.value == -32002
        assert MCPErrorCode.AUTHENTICATION_REQUIRED.value == -32003
    
    def test_error_code_properties(self):
        """Test error code classification properties."""
        # Client errors
        assert MCPErrorCode.INVALID_PARAMS.is_client_error
        assert MCPErrorCode.AUTHENTICATION_REQUIRED.is_client_error
        assert not MCPErrorCode.INVALID_PARAMS.is_server_error
        
        # Server errors
        assert MCPErrorCode.INTERNAL_ERROR.is_server_error
        assert MCPErrorCode.DATABASE_ERROR.is_server_error
        assert not MCPErrorCode.INTERNAL_ERROR.is_client_error
    
    def test_error_code_messages(self):
        """Test standard error messages."""
        assert MCPErrorCode.INVALID_PARAMS.message == "Invalid params"
        assert MCPErrorCode.TASK_NOT_FOUND.message == "Task not found"
        assert MCPErrorCode.PERMISSION_DENIED.message == "Permission denied"


class TestMCPErrorResponse:
    """Test MCP error response formatting."""
    
    def test_basic_error_response(self):
        """Test basic error response creation."""
        response = MCPErrorResponse(
            code=MCPErrorCode.INVALID_PARAMS,
            message="Test error message",
            data={"field": "test_field"},
            request_id="test_123"
        )
        
        assert response.code == MCPErrorCode.INVALID_PARAMS
        assert response.message == "Test error message"
        assert response.data["field"] == "test_field"
        assert response.request_id == "test_123"
        assert response.error_id is not None
    
    def test_error_response_to_dict(self):
        """Test error response dictionary conversion."""
        response = MCPErrorResponse(
            code=MCPErrorCode.VALIDATION_FAILED,
            message="Validation error",
            data={"details": "Field required"},
            request_id=42
        )
        
        result = response.to_dict()
        
        assert result["jsonrpc"] == "2.0"
        assert result["error"]["code"] == -32002  # VALIDATION_FAILED
        assert result["error"]["message"] == "Validation error"
        assert result["error"]["data"]["details"] == "Field required"
        assert result["error"]["data"]["error_id"] == response.error_id
        assert result["error"]["data"]["error_type"] == "validation_failed"
        assert result["id"] == 42
    
    def test_error_response_to_json(self):
        """Test JSON serialization of error response."""
        response = MCPErrorResponse(
            code=MCPErrorCode.TASK_NOT_FOUND,
            message="Task not found",
            request_id=None
        )
        
        json_str = response.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["error"]["code"] == -32000
        assert parsed["error"]["message"] == "Task not found"
        assert parsed["id"] is None


class TestErrorCodeMapping:
    """Test mapping from exceptions to MCP error codes."""
    
    def test_category_to_mcp_code_mapping(self):
        """Test category to MCP code mapping."""
        assert ERROR_CATEGORY_TO_MCP_CODE[ErrorCategory.VALIDATION_ERROR] == MCPErrorCode.INVALID_PARAMS
        assert ERROR_CATEGORY_TO_MCP_CODE[ErrorCategory.AUTHENTICATION_ERROR] == MCPErrorCode.AUTHENTICATION_REQUIRED
        assert ERROR_CATEGORY_TO_MCP_CODE[ErrorCategory.NOT_FOUND_ERROR] == MCPErrorCode.TASK_NOT_FOUND
        assert ERROR_CATEGORY_TO_MCP_CODE[ErrorCategory.DATABASE_ERROR] == MCPErrorCode.DATABASE_ERROR
    
    def test_exception_type_to_mcp_code_mapping(self):
        """Test exception type to MCP code mapping."""
        assert EXCEPTION_TYPE_TO_MCP_CODE["ValidationError"] == MCPErrorCode.VALIDATION_FAILED
        assert EXCEPTION_TYPE_TO_MCP_CODE["ValueError"] == MCPErrorCode.INVALID_PARAMS
        assert EXCEPTION_TYPE_TO_MCP_CODE["FileNotFoundError"] == MCPErrorCode.TASK_NOT_FOUND
        assert EXCEPTION_TYPE_TO_MCP_CODE["PermissionError"] == MCPErrorCode.PERMISSION_DENIED
    
    def test_get_mcp_error_code_by_exception_type(self):
        """Test getting MCP error code by exception type."""
        assert get_mcp_error_code(ValueError("test")) == MCPErrorCode.INVALID_PARAMS
        assert get_mcp_error_code(FileNotFoundError("test")) == MCPErrorCode.TASK_NOT_FOUND
        assert get_mcp_error_code(PermissionError("test")) == MCPErrorCode.PERMISSION_DENIED
    
    def test_get_mcp_error_code_by_category(self):
        """Test getting MCP error code by category override."""
        exception = ValueError("test")
        assert get_mcp_error_code(exception, ErrorCategory.AUTHENTICATION_ERROR) == MCPErrorCode.AUTHENTICATION_REQUIRED
        assert get_mcp_error_code(exception, ErrorCategory.DATABASE_ERROR) == MCPErrorCode.DATABASE_ERROR
    
    def test_get_mcp_error_code_unknown_exception(self):
        """Test getting MCP error code for unknown exception types."""
        class UnknownError(Exception):
            pass
        
        assert get_mcp_error_code(UnknownError("test")) == MCPErrorCode.INTERNAL_ERROR


class TestMCPErrorCreation:
    """Test MCP error creation utilities."""
    
    def test_create_mcp_error_response(self):
        """Test creating MCP error response from exception."""
        exception = ValueError("Invalid input value")
        context = {"field": "title", "operation": "create_task"}
        
        response = create_mcp_error_response(exception, context, request_id="test_123")
        
        assert response.code == MCPErrorCode.INVALID_PARAMS
        assert response.request_id == "test_123"
        assert response.data["exception_type"] == "ValueError"
        assert response.data["field"] == "title"
        assert response.data["operation"] == "create_task"
    
    def test_create_validation_error(self):
        """Test creating validation error response."""
        response = create_validation_error(
            field="title",
            value="",
            message="Title cannot be empty",
            request_id="val_123"
        )
        
        assert response.code == MCPErrorCode.INVALID_PARAMS
        assert "title" in response.message
        assert response.data["field"] == "title"
        assert response.data["validation_message"] == "Title cannot be empty"
        assert response.request_id == "val_123"
    
    def test_create_not_found_error(self):
        """Test creating not found error response."""
        response = create_not_found_error(
            resource_type="task",
            resource_id="task_123",
            request_id="nf_123"
        )
        
        assert response.code == MCPErrorCode.TASK_NOT_FOUND
        assert "Task not found" in response.message
        assert response.data["resource_type"] == "task"
        assert response.data["resource_id"] == "task_123"
        assert response.request_id == "nf_123"
    
    def test_create_authentication_error(self):
        """Test creating authentication error response."""
        response = create_authentication_error(
            reason="Invalid API key",
            request_id="auth_123"
        )
        
        assert response.code == MCPErrorCode.AUTHENTICATION_REQUIRED
        assert response.message == "Invalid API key"
        assert response.data["auth_required"] is True
        assert response.request_id == "auth_123"
    
    def test_create_permission_error(self):
        """Test creating permission error response."""
        response = create_permission_error(
            action="delete",
            resource="task_123",
            request_id="perm_123"
        )
        
        assert response.code == MCPErrorCode.PERMISSION_DENIED
        assert "delete" in response.message
        assert "task_123" in response.message
        assert response.data["action"] == "delete"
        assert response.data["resource"] == "task_123"
        assert response.request_id == "perm_123"


class TestErrorSanitizationIntegration:
    """Test integration with error sanitization framework."""
    
    def test_safe_error_response_mcp_conversion(self):
        """Test converting SafeErrorResponse to MCP format."""
        exception = ValueError("Test validation error")
        
        # Test with our error sanitization system
        safe_response = sanitize_error(exception)
        mcp_dict = safe_response.to_mcp_error()
        
        assert "jsonrpc" in mcp_dict
        assert mcp_dict["jsonrpc"] == "2.0"
        assert "error" in mcp_dict
        assert "code" in mcp_dict["error"]
        assert "message" in mcp_dict["error"]
        assert "data" in mcp_dict["error"]
        assert mcp_dict["id"] is None
    
    def test_error_sanitization_with_mcp_codes(self):
        """Test that error sanitization properly maps to MCP codes."""
        # Test different error types
        test_cases = [
            (ValueError("test"), MCPErrorCode.INVALID_PARAMS),
            (FileNotFoundError("test"), MCPErrorCode.TASK_NOT_FOUND),
            (PermissionError("test"), MCPErrorCode.PERMISSION_DENIED),
            (ConnectionError("test"), MCPErrorCode.DATABASE_ERROR),
        ]
        
        for exception, expected_code in test_cases:
            safe_response = sanitize_error(exception)
            mcp_dict = safe_response.to_mcp_error()
            assert mcp_dict["error"]["code"] == expected_code.value


class TestMCPErrorHandling:
    """Test MCP error handling decorators and utilities."""
    
    def test_validate_task_id_valid(self):
        """Test task ID validation with valid inputs."""
        assert validate_task_id("task_123") == "task_123"
        assert validate_task_id("12345") == "12345"
        assert validate_task_id("  uuid-string  ") == "uuid-string"
    
    def test_validate_task_id_invalid(self):
        """Test task ID validation with invalid inputs."""
        with pytest.raises(ValueError, match="Task ID is required"):
            validate_task_id(None)
        
        with pytest.raises(ValueError, match="Task ID is required"):
            validate_task_id("")
        
        with pytest.raises(ValueError, match="Task ID cannot be empty"):
            validate_task_id("   ")
        
        with pytest.raises(ValueError, match="Task ID too long"):
            validate_task_id("x" * 101)
    
    def test_validate_tool_arguments_valid(self):
        """Test tool arguments validation with valid inputs."""
        args = {"title": "Test Task", "description": "Test Description", "optional": "value"}
        required = ["title", "description"]
        optional = ["optional", "extra"]
        
        result = validate_tool_arguments(args, required, optional)
        
        assert result["title"] == "Test Task"
        assert result["description"] == "Test Description"
        assert result["optional"] == "value"
    
    def test_validate_tool_arguments_missing_required(self):
        """Test tool arguments validation with missing required fields."""
        args = {"description": "Test Description"}
        required = ["title", "description"]
        
        with pytest.raises(ValueError, match="Missing required fields: title"):
            validate_tool_arguments(args, required)
    
    def test_validate_tool_arguments_unknown_fields(self):
        """Test tool arguments validation with unknown fields."""
        args = {"title": "Test", "description": "Test", "unknown": "value"}
        required = ["title", "description"]
        optional = ["optional"]
        
        with pytest.raises(ValueError, match="Unknown fields: unknown"):
            validate_tool_arguments(args, required, optional)
    
    def test_validate_tool_arguments_not_dict(self):
        """Test tool arguments validation with non-dictionary input."""
        with pytest.raises(ValueError, match="Tool arguments must be a dictionary"):
            validate_tool_arguments("not a dict", ["title"])
    
    def test_format_mcp_success_response(self):
        """Test formatting MCP success response."""
        data = {"task_id": "123", "status": "created"}
        message = "Task created successfully"
        
        result = format_mcp_success_response(data, message)
        
        assert len(result) == 1
        content = json.loads(result[0].text)
        assert content["status"] == "success"
        assert content["message"] == message
        assert content["data"] == data
        assert "timestamp" in content
    
    def test_format_mcp_error_response_with_exception(self):
        """Test formatting MCP error response with exception."""
        exception = ValueError("Test error")
        context = {"handler": "test_handler"}
        
        result = format_mcp_error_response(exception, context)
        
        assert len(result) == 1
        content = json.loads(result[0].text)
        assert content["jsonrpc"] == "2.0"
        assert "error" in content
        assert content["error"]["code"] == MCPErrorCode.INVALID_PARAMS.value
        assert "Test error" in str(content["error"])
    
    def test_format_mcp_error_response_with_string(self):
        """Test formatting MCP error response with string message."""
        error_message = "Something went wrong"
        
        result = format_mcp_error_response(error_message)
        
        assert len(result) == 1
        content = json.loads(result[0].text)
        assert content["jsonrpc"] == "2.0"
        assert "error" in content
        assert "Something went wrong" in str(content["error"])


class TestMCPErrorHandlerDecorator:
    """Test MCP error handler decorator functionality."""
    
    @pytest.mark.asyncio
    async def test_mcp_error_handler_success(self):
        """Test MCP error handler with successful execution."""
        from mcp import types
        
        @mcp_error_handler(tool_name="test_tool")
        async def test_handler(args):
            return [types.TextContent(type="text", text="success")]
        
        result = await test_handler({"test": "data"})
        assert len(result) == 1
        assert result[0].text == "success"
    
    @pytest.mark.asyncio
    async def test_mcp_error_handler_with_exception(self):
        """Test MCP error handler with exception."""
        from mcp import types
        
        @mcp_error_handler(tool_name="test_tool")
        async def test_handler(args):
            raise ValueError("Test error message")
        
        result = await test_handler({"test": "data"})
        assert len(result) == 1
        
        content = json.loads(result[0].text)
        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == MCPErrorCode.INVALID_PARAMS.value
        assert "error_id" in content["error"]["data"]
        assert content["error"]["data"]["handler"] == "test_tool"
    
    @pytest.mark.asyncio
    async def test_mcp_validation_handler_success(self):
        """Test MCP validation handler with valid arguments."""
        from mcp import types
        
        @mcp_validation_handler(["title", "description"])
        async def test_handler(args):
            return [types.TextContent(type="text", text="validated")]
        
        valid_args = {"title": "Test Title", "description": "Test Description"}
        result = await test_handler(valid_args)
        assert len(result) == 1
        assert result[0].text == "validated"
    
    @pytest.mark.asyncio
    async def test_mcp_validation_handler_missing_fields(self):
        """Test MCP validation handler with missing fields."""
        @mcp_validation_handler(["title", "description"])
        async def test_handler(args):
            return [types.TextContent(type="text", text="should not reach here")]
        
        invalid_args = {"title": "Test Title"}  # missing description
        result = await test_handler(invalid_args)
        assert len(result) == 1
        
        content = json.loads(result[0].text)
        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == MCPErrorCode.INVALID_PARAMS.value
        assert "description" in content["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_mcp_validation_handler_empty_fields(self):
        """Test MCP validation handler with empty fields."""
        @mcp_validation_handler(["title"])
        async def test_handler(args):
            return [types.TextContent(type="text", text="should not reach here")]
        
        invalid_args = {"title": ""}  # empty title
        result = await test_handler(invalid_args)
        assert len(result) == 1
        
        content = json.loads(result[0].text)
        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == MCPErrorCode.INVALID_PARAMS.value
        assert "Empty or invalid fields" in content["error"]["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])