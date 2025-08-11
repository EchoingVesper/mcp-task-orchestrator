"""
Authorization Security Tests

Comprehensive test suite for validating Role-Based Access Control (RBAC),
permission enforcement, privilege escalation prevention, and resource access control.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# from mcp_task_orchestrator.infrastructure.security import  # TODO: Complete this import


class TestRoleBasedAccessControl:
    """Test RBAC role and permission enforcement."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_basic_permission_enforcement(self, mock_mcp_context, test_user_basic):
        """Test basic permission enforcement works correctly."""
        # Mock the authorization validator components
        with patch('mcp_task_orchestrator.infrastructure.security.authorization.authz_validator.user_role_manager') as mock_user_role_mgr, \
             patch('mcp_task_orchestrator.infrastructure.security.authorization.authz_validator.role_manager') as mock_role_mgr:
            
            # Setup mocks for user with READ_TASK permission
            mock_user_role_mgr.get_user_role.return_value = test_user_basic["role"]
            mock_role_mgr.has_permission.return_value = True
            
            @require_permission(Permission.READ_TASK)
            async def read_task_handler(context, args, **kwargs):
                return {"success": True, "task_id": args.get("task_id")}
            
            # User with READ_TASK permission should succeed
            context = mock_mcp_context(test_user_basic)
            result = await read_task_handler(context, {"task_id": "test_123"}, _auth_metadata={"user_id": test_user_basic["user_id"]})
            assert result["success"] is True
            
            # User without permission should fail
            mock_role_mgr.has_permission.return_value = False
            limited_user = {**test_user_basic, "permissions": []}
            context = mock_mcp_context(limited_user)
            
            with pytest.raises(AuthorizationError):
                await read_task_handler(context, {"task_id": "test_123"}, _auth_metadata={"user_id": limited_user["user_id"]})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_role_hierarchy_enforcement(self, mock_mcp_context, test_user_basic, test_user_manager, test_user_admin):
        """Test role hierarchy is properly enforced."""
        @require_role(Role.MANAGER)
        async def manager_only_handler(context, args, **kwargs):
            return {"success": True, "role": context.role}
        
        # Basic user should be denied
        context = mock_mcp_context(test_user_basic)
        with pytest.raises(AuthorizationError):
            await manager_only_handler(context, {})
        
        # Manager should be allowed
        context = mock_mcp_context(test_user_manager)
        result = await manager_only_handler(context, {})
        assert result["success"] is True
        
        # Admin should be allowed (higher in hierarchy)
        context = mock_mcp_context(test_user_admin)
        result = await manager_only_handler(context, {})
        assert result["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_multiple_permission_requirements(self, mock_mcp_context, test_user_manager):
        """Test handlers requiring multiple permissions."""
        @require_permission(Permission.CREATE_TASK)
        @require_permission(Permission.UPDATE_TASK)
        async def complex_handler(context, args, **kwargs):
            return {"success": True}
        
        # User with both permissions should succeed
        context = mock_mcp_context(test_user_manager)
        result = await complex_handler(context, {})
        assert result["success"] is True
        
        # User with only one permission should fail
        partial_user = {
            **test_user_manager,
            "permissions": [Permission.CREATE_TASK]  # Missing UPDATE_TASK
        }
        context = mock_mcp_context(partial_user)
        
        with pytest.raises(AuthorizationError):
            await complex_handler(context, {})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_permission_inheritance(self, mock_mcp_context, test_user_admin):
        """Test permission inheritance through role hierarchy."""
        # Admin should have all permissions, including lower-level ones
        context = mock_mcp_context(test_user_admin)
        
        # Test various permission levels
        basic_permissions = [Permission.READ_TASK]
        manager_permissions = [Permission.CREATE_TASK, Permission.UPDATE_TASK, Permission.DELETE_TASK]
        admin_permissions = [Permission.MANAGE_USERS, Permission.SYSTEM_CONFIG]
        
        all_permissions = basic_permissions + manager_permissions + admin_permissions
        
        for permission in all_permissions:
            assert has_permission(context, permission), f"Admin should have {permission}"


class TestPrivilegeEscalationPrevention:
    """Test prevention of privilege escalation attacks."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_role_modification_prevention(self, mock_mcp_context, test_user_basic):
        """Test users cannot modify their own roles."""
        context = mock_mcp_context(test_user_basic)
        
        # Attempt to escalate privileges by modifying context
        original_role = context.role
        original_permissions = context.permissions.copy()
        
        # Simulate privilege escalation attempt
        context.role = Role.ADMIN
        context.permissions = list(Permission)
        
        @require_role(Role.ADMIN)
        async def admin_handler(ctx, args):
            return {"success": True}
        
        # Should still fail because authorization uses validated context
        with pytest.raises(AuthorizationError):
            await admin_handler(context, {})
        
        # Verify original context wasn't actually modified in validation
        assert context.role == Role.ADMIN  # Context object changed
        # But authorization should use the original validated permissions
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_permission_injection_prevention(self, mock_mcp_context, test_user_basic):
        """Test prevention of permission injection attacks."""
        @require_permission(Permission.DELETE_TASK)
        async def delete_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(test_user_basic)
        
        # Try various permission injection techniques
        malicious_permissions = [
            [Permission.DELETE_TASK],  # Direct injection
            ["DELETE_TASK"],           # String injection
            [f"{Permission.DELETE_TASK}"],  # String conversion
            [Permission.READ_TASK, Permission.DELETE_TASK],  # Permission addition
        ]
        
        for bad_permissions in malicious_permissions:
            context.permissions = bad_permissions
            
            # Should still fail because validation uses original authenticated permissions
            with pytest.raises(AuthorizationError):
                await delete_handler(context, {})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_context_tampering_prevention(self, mock_mcp_context, test_user_basic):
        """Test prevention of context tampering attacks."""
        @require_permission(Permission.SYSTEM_CONFIG)
        async def system_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(test_user_basic)
        
        # Attempt various context tampering techniques
        tampering_attempts = [
            {"user_id": "admin_user"},
            {"api_key": "admin_api_key"},
            {"is_authenticated": True, "role": Role.ADMIN},
            {"permissions": list(Permission)},
            {"__class__": "AdminContext"},
        ]
        
        for tamper_data in tampering_attempts:
            # Apply tampering
            for key, value in tamper_data.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            
            # Should still fail
            with pytest.raises(AuthorizationError):
                await system_handler(context, {})


class TestResourceAccessControl:
    """Test resource-level access control."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_task_ownership_enforcement(self, mock_mcp_context, test_user_basic, test_user_manager):
        """Test users can only access their own tasks."""
        @require_permission(Permission.READ_TASK)
        async def read_task_handler(context, args, **kwargs):
            task_id = args.get("task_id")
            # Simulate ownership check
            if task_id.startswith(f"user_{context.user_id}_"):
                return {"success": True, "task_id": task_id}
            else:
                raise AuthorizationError("Access denied: Not task owner")
        
        user1_context = mock_mcp_context(test_user_basic)
        user2_context = mock_mcp_context({
            **test_user_manager,
            "user_id": "test_user_manager_different"
        })
        
        # User should access their own task
        result = await read_task_handler(user1_context, {
            "task_id": f"user_{test_user_basic['user_id']}_task_123"
        })
        assert result["success"] is True
        
        # User should not access another user's task
        with pytest.raises(AuthorizationError):
            await read_task_handler(user1_context, {
                "task_id": f"user_{test_user_manager['user_id']}_task_456"
            })
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_cross_tenant_data_isolation(self, mock_mcp_context):
        """Test data isolation between different tenants."""
        # Simulate multi-tenant environment
        tenant1_user = {
            "user_id": "user1_tenant1",
            "tenant_id": "tenant_1",
            "role": Role.MANAGER,
            "permissions": [Permission.READ_TASK, Permission.CREATE_TASK]
        }
        
        tenant2_user = {
            "user_id": "user1_tenant2", 
            "tenant_id": "tenant_2",
            "role": Role.MANAGER,
            "permissions": [Permission.READ_TASK, Permission.CREATE_TASK]
        }
        
        @require_permission(Permission.READ_TASK)
        async def read_tenant_data(context, args):
            data_tenant_id = args.get("tenant_id")
            if context.tenant_id != data_tenant_id:
                raise AuthorizationError("Cross-tenant access denied")
            return {"success": True, "tenant": data_tenant_id}
        
        context1 = mock_mcp_context(tenant1_user)
        context1.tenant_id = tenant1_user["tenant_id"]
        
        context2 = mock_mcp_context(tenant2_user)
        context2.tenant_id = tenant2_user["tenant_id"]
        
        # User should access their tenant's data
        result = await read_tenant_data(context1, {"tenant_id": "tenant_1"})
        assert result["success"] is True
        
        # User should not access another tenant's data
        with pytest.raises(AuthorizationError):
            await read_tenant_data(context1, {"tenant_id": "tenant_2"})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_resource_permission_scoping(self, mock_mcp_context, test_user_manager):
        """Test permission scoping to specific resources."""
        # User with limited scope permissions
        scoped_user = {
            **test_user_manager,
            "resource_scope": ["project_1", "project_2"]  # Can only access these projects
        }
        
        @require_permission(Permission.UPDATE_TASK)
        async def update_project_task(context, args):
            project_id = args.get("project_id")
            if hasattr(context, 'resource_scope') and project_id not in context.resource_scope:
                raise AuthorizationError(f"Access denied to project {project_id}")
            return {"success": True, "project": project_id}
        
        context = mock_mcp_context(scoped_user)
        context.resource_scope = scoped_user["resource_scope"]
        
        # Should access allowed projects
        result = await update_project_task(context, {"project_id": "project_1"})
        assert result["success"] is True
        
        # Should not access restricted projects
        with pytest.raises(AuthorizationError):
            await update_project_task(context, {"project_id": "project_3"})


class TestSecureMCPHandler:
    """Test the combined secure MCP handler decorator."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical  
    async def test_secure_mcp_handler_success(self, mock_mcp_context, test_user_manager):
        """Test secure MCP handler with valid authentication and authorization."""
        @secure_mcp_handler(Permission.CREATE_TASK)
        async def create_task_handler(context, args, **kwargs):
            return {
                "success": True, 
                "task_id": args.get("task_id"),
                "user": context.user_id
            }
        
        context = mock_mcp_context(test_user_manager)
        result = await create_task_handler(context, {"task_id": "new_task_123"})
        
        assert result["success"] is True
        assert result["user"] == test_user_manager["user_id"]
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_secure_mcp_handler_auth_failure(self, mock_mcp_context):
        """Test secure MCP handler fails with invalid authentication."""
        @secure_mcp_handler(Permission.CREATE_TASK)
        async def create_task_handler(context, args, **kwargs):
            return {"success": True}
        
        # Unauthenticated context
        context = mock_mcp_context()
        context.is_authenticated = False
        context.api_key = None
        
        with pytest.raises(AuthorizationError):  # Should fail at authentication
            await create_task_handler(context, {})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.critical
    async def test_secure_mcp_handler_authz_failure(self, mock_mcp_context, test_user_basic):
        """Test secure MCP handler fails with insufficient permissions."""
        @secure_mcp_handler(Permission.DELETE_TASK)
        async def delete_task_handler(context, args, **kwargs):
            return {"success": True}
        
        # Authenticated but insufficient permissions
        context = mock_mcp_context(test_user_basic)  # Only has READ_TASK
        
        with pytest.raises(AuthorizationError):  # Should fail at authorization
            await delete_task_handler(context, {})


class TestAuthorizationEdgeCases:
    """Test edge cases in authorization system."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_empty_permissions_handling(self, mock_mcp_context):
        """Test handling of users with no permissions."""
        empty_user = {
            "user_id": "empty_user",
            "role": Role.USER,
            "permissions": [],  # No permissions
            "api_key": "empty_user_key"
        }
        
        @require_permission(Permission.READ_TASK)
        async def read_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(empty_user)
        
        with pytest.raises(AuthorizationError):
            await read_handler(context, {})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_invalid_permission_enum(self, mock_mcp_context, test_user_admin):
        """Test handling of invalid permission enums."""
        @require_permission("INVALID_PERMISSION")  # String instead of enum
        async def invalid_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(test_user_admin)
        
        # Should raise appropriate error for invalid permission
        with pytest.raises((ValueError, TypeError, AuthorizationError)):
            await invalid_handler(context, {})
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_none_permission_handling(self, mock_mcp_context, test_user_admin):
        """Test handling of None permissions."""
        try:
            @require_permission(None)
            async def none_handler(context, args, **kwargs):
                return {"success": True}
            
            context = mock_mcp_context(test_user_admin)
            
            with pytest.raises((ValueError, TypeError)):
                await none_handler(context, {})
        except (ValueError, TypeError):
            # Expected at decorator creation time
            pass
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    async def test_concurrent_authorization_checks(self, mock_mcp_context, test_user_manager):
        """Test concurrent authorization checks don't interfere."""
        @require_permission(Permission.CREATE_TASK)
        async def concurrent_handler(context, args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate async work
            return {"success": True, "request_id": args.get("request_id")}
        
        context = mock_mcp_context(test_user_manager)
        
        # Run 10 concurrent authorization checks
        tasks = [
            concurrent_handler(context, {"request_id": i})
            for i in range(10)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 10
        assert all(r["success"] is True for r in results)
        
        # Each should have unique request ID
        request_ids = [r["request_id"] for r in results]
        assert len(set(request_ids)) == 10  # All unique


class TestAuthorizationPerformance:
    """Test authorization system performance."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.performance
    async def test_authorization_performance_under_load(self, mock_mcp_context, test_user_admin, performance_monitor):
        """Test authorization performance under load."""
        performance_monitor.start_monitoring()
        
        @require_permission(Permission.READ_TASK)
        async def fast_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(test_user_admin)
        
        # Perform many authorization checks
        tasks = [
            fast_handler(context, {"request": i})
            for i in range(100)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify performance
        performance_monitor.assert_performance_limits(
            max_execution_time=5.0,
            max_memory_mb=20.0,
            max_cpu_percent=50.0
        )
        
        # All should succeed
        assert len(results) == 100
        assert all(r["success"] is True for r in results)
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.performance
    async def test_complex_permission_chain_performance(self, mock_mcp_context, test_user_admin, performance_monitor):
        """Test performance with complex permission chains."""
        performance_monitor.start_monitoring()
        
        # Create deeply nested permission requirements
        @require_permission(Permission.READ_TASK)
        @require_permission(Permission.CREATE_TASK)
        @require_permission(Permission.UPDATE_TASK)
        @require_permission(Permission.DELETE_TASK)
        @require_role(Role.ADMIN)
        async def complex_handler(context, args, **kwargs):
            return {"success": True}
        
        context = mock_mcp_context(test_user_admin)
        
        # Run multiple times
        for i in range(50):
            result = await complex_handler(context, {"iteration": i})
            assert result["success"] is True
        
        # Verify performance remains acceptable
        performance_monitor.assert_performance_limits(
            max_execution_time=10.0,
            max_memory_mb=15.0,
            max_cpu_percent=40.0
        )


# Integration test combining authentication and authorization
class TestAuthorizationIntegration:
    """Integration tests combining authentication and authorization."""
    
    @pytest.mark.asyncio
    @pytest.mark.authorization
    @pytest.mark.integration
    async def test_complete_security_flow(self, test_api_key_manager, admin_api_key, performance_monitor):
        """Test complete security flow from API key to resource access."""
        performance_monitor.start_monitoring()
        
        # 1. Validate API key
        auth_result = await test_api_key_manager.validate_api_key(admin_api_key)
        assert auth_result["valid"] is True
        
        # 2. Create context from authentication
        mock_context = Mock()
        mock_context.user_id = "admin_user"
        mock_context.role = Role.ADMIN
        mock_context.permissions = list(Permission)
        mock_context.api_key = admin_api_key
        mock_context.is_authenticated = True
        mock_context.has_permission = lambda perm: perm in mock_context.permissions
        
        # 3. Test authorized access
        @secure_mcp_handler(Permission.SYSTEM_CONFIG)
        async def system_config_handler(context, args, **kwargs):
            return {
                "success": True,
                "config": args.get("config_key"),
                "user": context.user_id
            }
        
        result = await system_config_handler(mock_context, {"config_key": "max_tasks"})
        assert result["success"] is True
        assert result["user"] == "admin_user"
        
        # 4. Verify performance
        performance_monitor.assert_performance_limits(
            max_execution_time=2.0,
            max_memory_mb=10.0,
            max_cpu_percent=30.0
        )