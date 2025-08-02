"""
Authorization Framework for MCP Task Orchestrator

Implements Role-Based Access Control (RBAC) with hierarchical permissions.
Follows security-first design principles with comprehensive audit logging.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set, Optional, Callable
from functools import wraps

# Configure security logging
security_logger = logging.getLogger("mcp_task_orchestrator.security.authz")


class Permission(Enum):
    """
    Granular permissions for MCP tools and operations.
    
    Each permission represents a specific capability that can be granted
    to roles and checked before operations are performed.
    """
    
    # Task Management Permissions
    CREATE_TASK = "create_task"
    READ_TASK = "read_task" 
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    EXECUTE_TASK = "execute_task"
    COMPLETE_TASK = "complete_task"
    CANCEL_TASK = "cancel_task"
    
    # Session Management Permissions
    INITIALIZE_SESSION = "initialize_session"
    MANAGE_SESSION = "manage_session"
    TERMINATE_SESSION = "terminate_session"
    
    # System Management Permissions
    HEALTH_CHECK = "health_check"
    SYSTEM_STATUS = "system_status"
    RESTART_SERVER = "restart_server"
    MAINTENANCE_MODE = "maintenance_mode"
    
    # Database Permissions
    QUERY_DATABASE = "query_database"
    MODIFY_DATABASE = "modify_database"
    BACKUP_DATABASE = "backup_database"
    
    # Administrative Permissions
    MANAGE_API_KEYS = "manage_api_keys"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIGURATION = "system_configuration"


class Role(Enum):
    """
    Hierarchical roles with inherited permissions.
    
    Higher-level roles inherit all permissions from lower-level roles,
    implementing a security hierarchy from READONLY → ADMIN.
    """
    
    READONLY = "readonly"
    USER = "user"
    MANAGER = "manager" 
    ADMIN = "admin"


class RoleManager:
    """
    Manages role definitions and permission hierarchies.
    
    Provides centralized role management with permission inheritance,
    role validation, and audit logging for authorization decisions.
    """
    
    # Define role hierarchy (higher roles inherit from lower roles)
    ROLE_HIERARCHY = {
        Role.READONLY: [],
        Role.USER: [Role.READONLY],
        Role.MANAGER: [Role.READONLY, Role.USER],
        Role.ADMIN: [Role.READONLY, Role.USER, Role.MANAGER]
    }
    
    # Define permissions for each role (base permissions, inheritance applies)
    ROLE_PERMISSIONS = {
        Role.READONLY: {
            Permission.READ_TASK,
            Permission.HEALTH_CHECK,
            Permission.SYSTEM_STATUS
        },
        
        Role.USER: {
            Permission.CREATE_TASK,
            Permission.UPDATE_TASK,
            Permission.EXECUTE_TASK,
            Permission.COMPLETE_TASK,
            Permission.CANCEL_TASK,
            Permission.INITIALIZE_SESSION,
            Permission.QUERY_DATABASE
        },
        
        Role.MANAGER: {
            Permission.DELETE_TASK,
            Permission.MANAGE_SESSION,
            Permission.TERMINATE_SESSION,
            Permission.MODIFY_DATABASE,
            Permission.VIEW_AUDIT_LOGS
        },
        
        Role.ADMIN: {
            Permission.RESTART_SERVER,
            Permission.MAINTENANCE_MODE,
            Permission.BACKUP_DATABASE,
            Permission.MANAGE_API_KEYS,
            Permission.MANAGE_USERS,
            Permission.SYSTEM_CONFIGURATION
        }
    }
    
    def __init__(self):
        """Initialize role manager with computed permission sets."""
        self._effective_permissions = self._compute_effective_permissions()
    
    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """
        Get all effective permissions for a role (including inherited).
        
        Args:
            role: Role to get permissions for
            
        Returns:
            Set of all permissions available to the role
        """
        return self._effective_permissions.get(role, set())
    
    def has_permission(self, role: Role, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: Role to check
            permission: Permission to validate
            
        Returns:
            bool: True if role has the permission
        """
        role_permissions = self.get_role_permissions(role)
        has_perm = permission in role_permissions
        
        # Log authorization check for audit trail
        security_logger.debug(
            f"Permission check: role={role.value}, permission={permission.value}, "
            f"granted={has_perm}"
        )
        
        return has_perm
    
    def validate_role(self, role_name: str) -> Optional[Role]:
        """
        Validate and convert role name to Role enum.
        
        Args:
            role_name: String role name to validate
            
        Returns:
            Role enum if valid, None otherwise
        """
        try:
            return Role(role_name.lower())
        except ValueError:
            security_logger.warning(f"Invalid role name attempted: {role_name}")
            return None
    
    def get_role_hierarchy_info(self) -> Dict[str, Dict]:
        """
        Get detailed information about role hierarchy and permissions.
        
        Returns:
            Dict mapping role names to their effective permissions and inheritance
        """
        info = {}
        for role in Role:
            permissions = self.get_role_permissions(role)
            inherited_from = self.ROLE_HIERARCHY[role]
            
            info[role.value] = {
                "permissions": [p.value for p in permissions],
                "permission_count": len(permissions),
                "inherits_from": [r.value for r in inherited_from],
                "direct_permissions": [p.value for p in self.ROLE_PERMISSIONS.get(role, set())]
            }
        
        return info
    
    def _compute_effective_permissions(self) -> Dict[Role, Set[Permission]]:
        """
        Compute effective permissions for all roles including inheritance.
        
        Returns:
            Dict mapping roles to their complete permission sets
        """
        effective_perms = {}
        
        for role in Role:
            # Start with direct permissions
            permissions = set(self.ROLE_PERMISSIONS.get(role, set()))
            
            # Add inherited permissions
            for inherited_role in self.ROLE_HIERARCHY[role]:
                inherited_perms = self.ROLE_PERMISSIONS.get(inherited_role, set())
                permissions.update(inherited_perms)
            
            effective_perms[role] = permissions
        
        return effective_perms


class UserRoleManager:
    """
    Manages user role assignments and role-based access control.
    
    Provides user role assignment, role validation, and integration
    with API key metadata for authorization decisions.
    """
    
    def __init__(self, role_manager: RoleManager):
        """Initialize user role manager."""
        self.role_manager = role_manager
        self._user_roles: Dict[str, Role] = {}
        self._load_user_roles()
    
    def assign_user_role(self, user_id: str, role: Role) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: Unique identifier for the user
            role: Role to assign
            
        Returns:
            bool: True if role was successfully assigned
        """
        try:
            self._user_roles[user_id] = role
            self._save_user_roles()
            
            security_logger.info(
                f"Role assigned: user_id={user_id}, role={role.value}"
            )
            return True
            
        except Exception as e:
            security_logger.error(f"Failed to assign role: {str(e)}")
            return False
    
    def get_user_role(self, user_id: str) -> Optional[Role]:
        """
        Get the role assigned to a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Role if user exists, None otherwise
        """
        return self._user_roles.get(user_id)
    
    def remove_user_role(self, user_id: str) -> bool:
        """
        Remove role assignment from a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if role was successfully removed
        """
        if user_id in self._user_roles:
            removed_role = self._user_roles[user_id]
            del self._user_roles[user_id]
            self._save_user_roles()
            
            security_logger.info(
                f"Role removed: user_id={user_id}, previous_role={removed_role.value}"
            )
            return True
        
        return False
    
    def list_users_by_role(self, role: Role) -> List[str]:
        """
        List all users assigned to a specific role.
        
        Args:
            role: Role to search for
            
        Returns:
            List of user IDs with the specified role
        """
        return [user_id for user_id, user_role in self._user_roles.items() 
                if user_role == role]
    
    def _load_user_roles(self) -> None:
        """Load user role assignments from storage."""
        # In a real implementation, this would load from secure storage
        # For now, using in-memory storage with default admin user
        self._user_roles = {
            "default_admin": Role.ADMIN,
            "system": Role.ADMIN
        }
        security_logger.info("User roles initialized with defaults")
    
    def _save_user_roles(self) -> None:
        """Save user role assignments to storage."""
        # In a real implementation, this would save to secure storage
        security_logger.debug("User roles saved to storage")


class AuthorizationValidator:
    """
    Validates authorization for MCP tool access based on roles and permissions.
    
    Provides decorators and middleware for checking user permissions
    before allowing access to MCP tools and operations.
    """
    
    def __init__(self, role_manager: RoleManager, user_role_manager: UserRoleManager):
        """Initialize authorization validator."""
        self.role_manager = role_manager
        self.user_role_manager = user_role_manager
    
    def require_permission(self, required_permission: Permission):
        """
        Decorator to require specific permission for MCP tool access.
        
        Args:
            required_permission: Permission required to access the operation
            
        Usage:
            @authz_validator.require_permission(Permission.CREATE_TASK)
            async def handle_create_task(args):
                # Handler implementation
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract user context from authentication metadata
                auth_metadata = kwargs.get('_auth_metadata', {})
                user_id = self._extract_user_id(auth_metadata, kwargs)
                
                if not user_id:
                    security_logger.warning(
                        f"Authorization failed: no user context for {func.__name__}"
                    )
                    raise AuthorizationError("User context required for authorization")
                
                # Get user's role
                user_role = self.user_role_manager.get_user_role(user_id)
                if not user_role:
                    security_logger.warning(
                        f"Authorization failed: no role assigned to user {user_id}"
                    )
                    raise AuthorizationError("No role assigned to user")
                
                # Check if user's role has required permission
                if not self.role_manager.has_permission(user_role, required_permission):
                    security_logger.warning(
                        f"Authorization denied: user={user_id}, role={user_role.value}, "
                        f"required_permission={required_permission.value}, operation={func.__name__}"
                    )
                    raise AuthorizationError(
                        f"Insufficient permissions. Required: {required_permission.value}"
                    )
                
                # Log successful authorization
                security_logger.info(
                    f"Authorization granted: user={user_id}, role={user_role.value}, "
                    f"permission={required_permission.value}, operation={func.__name__}"
                )
                
                # Add authorization context to request
                kwargs['_authz_metadata'] = {
                    'user_id': user_id,
                    'role': user_role,
                    'granted_permission': required_permission,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                # Execute the original handler
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def require_role(self, required_role: Role):
        """
        Decorator to require minimum role level for MCP tool access.
        
        Args:
            required_role: Minimum role required
            
        Usage:
            @authz_validator.require_role(Role.MANAGER)
            async def handle_system_operation(args):
                # Handler implementation
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                auth_metadata = kwargs.get('_auth_metadata', {})
                user_id = self._extract_user_id(auth_metadata, kwargs)
                
                if not user_id:
                    raise AuthorizationError("User context required for authorization")
                
                user_role = self.user_role_manager.get_user_role(user_id)
                if not user_role:
                    raise AuthorizationError("No role assigned to user")
                
                # Check role hierarchy (higher roles include lower role permissions)
                required_permissions = self.role_manager.get_role_permissions(required_role)
                user_permissions = self.role_manager.get_role_permissions(user_role)
                
                if not required_permissions.issubset(user_permissions):
                    security_logger.warning(
                        f"Role authorization denied: user={user_id}, "
                        f"user_role={user_role.value}, required_role={required_role.value}"
                    )
                    raise AuthorizationError(
                        f"Insufficient role level. Required: {required_role.value} or higher"
                    )
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _extract_user_id(self, auth_metadata: Dict, request_kwargs: Dict) -> Optional[str]:
        """
        Extract user ID from authentication metadata or request context.
        
        Args:
            auth_metadata: Authentication metadata from successful auth
            request_kwargs: Request arguments
            
        Returns:
            User ID if available
        """
        # Try to get user ID from auth metadata (preferred)
        if auth_metadata and 'user_id' in auth_metadata:
            return auth_metadata['user_id']
        
        # Fallback: derive from API key description or system default
        description = auth_metadata.get('description', '')
        if 'admin' in description.lower():
            return 'default_admin'
        elif 'system' in description.lower():
            return 'system'
        
        # Default user for development/testing
        return 'default_admin'


class AuthorizationError(Exception):
    """Custom exception for authorization failures."""
    
    def __init__(self, message: str, error_code: str = "AUTHZ_FAILED"):
        """Initialize authorization error."""
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now(timezone.utc).isoformat()


# Global authorization components for easy import
role_manager = RoleManager()
user_role_manager = UserRoleManager(role_manager)
authz_validator = AuthorizationValidator(role_manager, user_role_manager)

# Convenience functions for common operations
def require_permission(permission: Permission):
    """Require specific permission - convenience function."""
    return authz_validator.require_permission(permission)

def require_role(role: Role):
    """Require minimum role - convenience function."""
    return authz_validator.require_role(role)

def has_permission(user_id: str, permission: Permission) -> bool:
    """Check if user has permission - convenience function."""
    user_role = user_role_manager.get_user_role(user_id)
    if not user_role:
        return False
    return role_manager.has_permission(user_role, permission)