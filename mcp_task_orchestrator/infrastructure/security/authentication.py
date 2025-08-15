"""
Authentication Framework for MCP Task Orchestrator

Implements API key management with secure hashing, key generation, and validation.
Follows security-first design principles with comprehensive audit logging.
"""

import hashlib
import logging
import secrets
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

# Configure security logging
security_logger = logging.getLogger("mcp_task_orchestrator.security.auth")


class APIKeyManager:
    """
    Manages API keys with secure hashing and validation.
    
    Security Features:
    - SHA256 hashing for key storage
    - Cryptographically secure key generation
    - Key expiration support
    - Rate limiting integration points
    - Comprehensive audit logging
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize API key manager with secure storage."""
        self.storage_path = Path(storage_path or ".task_orchestrator/api_keys.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._keys: Dict[str, Dict] = {}
        self._load_keys()
    
    def generate_api_key(self, description: str = "Generated API Key", 
                        expires_days: Optional[int] = None) -> str:
        """
        Generate a new API key with secure random generation.
        
        Args:
            description: Human-readable description of the key
            expires_days: Optional expiration in days
            
        Returns:
            str: New API key (unhashed, only returned once)
        """
        # Generate cryptographically secure API key
        api_key = f"mcp_task_{secrets.token_urlsafe(32)}"
        
        # Calculate expiration if specified
        expires_at = None
        if expires_days:
            expires_at = datetime.now(timezone.utc).timestamp() + (expires_days * 24 * 3600)
        
        # Hash the key for storage (never store raw keys)
        key_hash = self._hash_key(api_key)
        
        # Store key metadata
        key_data = {
            "description": description,
            "created_at": datetime.now(timezone.utc).timestamp(),
            "expires_at": expires_at,
            "last_used": None,
            "usage_count": 0,
            "is_active": True
        }
        
        self._keys[key_hash] = key_data
        self._save_keys()
        
        # Log key generation for security audit
        security_logger.info(
            f"API key generated: description='{description}', "
            f"expires_days={expires_days}, key_hash={key_hash[:16]}..."
        )
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, Optional[Dict]]:
        """
        Validate an API key and return validation result with metadata.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, key_metadata)
        """
        if not api_key or not api_key.startswith("mcp_task_"):
            security_logger.warning("Invalid API key format attempted")
            return False, None
        
        key_hash = self._hash_key(api_key)
        key_data = self._keys.get(key_hash)
        
        if not key_data:
            security_logger.warning("API key validation failed: key not found")
            return False, None
        
        # Check if key is active
        if not key_data.get("is_active", False):
            security_logger.warning("API key validation failed: key inactive")
            return False, None
        
        # Check expiration
        expires_at = key_data.get("expires_at")
        if expires_at and datetime.now(timezone.utc).timestamp() > expires_at:
            security_logger.warning("API key validation failed: key expired")
            return False, None
        
        # Update usage statistics
        key_data["last_used"] = datetime.now(timezone.utc).timestamp()
        key_data["usage_count"] = key_data.get("usage_count", 0) + 1
        self._save_keys()
        
        security_logger.info(f"API key validated successfully: {key_hash[:16]}...")
        return True, key_data.copy()
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key by marking it as inactive.
        
        Args:
            api_key: The API key to revoke
            
        Returns:
            bool: True if key was successfully revoked
        """
        key_hash = self._hash_key(api_key)
        key_data = self._keys.get(key_hash)
        
        if not key_data:
            security_logger.warning("Attempted to revoke non-existent key")
            return False
        
        key_data["is_active"] = False
        key_data["revoked_at"] = datetime.now(timezone.utc).timestamp()
        self._save_keys()
        
        security_logger.info(f"API key revoked: {key_hash[:16]}...")
        return True
    
    def list_active_keys(self) -> List[Dict]:
        """
        List all active API keys with metadata (excluding hashes).
        
        Returns:
            List of key metadata dictionaries
        """
        active_keys = []
        for key_hash, key_data in self._keys.items():
            if key_data.get("is_active", False):
                # Return safe metadata without the hash
                safe_data = key_data.copy()
                safe_data["key_id"] = key_hash[:16] + "..."  # Partial hash for identification
                active_keys.append(safe_data)
        
        return active_keys
    
    def cleanup_expired_keys(self) -> int:
        """
        Remove expired keys from storage.
        
        Returns:
            int: Number of keys cleaned up
        """
        current_time = datetime.now(timezone.utc).timestamp()
        expired_keys = []
        
        for key_hash, key_data in self._keys.items():
            expires_at = key_data.get("expires_at")
            if expires_at and current_time > expires_at:
                expired_keys.append(key_hash)
        
        for key_hash in expired_keys:
            del self._keys[key_hash]
        
        if expired_keys:
            self._save_keys()
            security_logger.info(f"Cleaned up {len(expired_keys)} expired API keys")
        
        return len(expired_keys)
    
    def _hash_key(self, api_key: str) -> str:
        """
        Hash an API key using SHA256 for secure storage.
        
        Args:
            api_key: Raw API key to hash
            
        Returns:
            str: SHA256 hash of the key
        """
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    
    def _load_keys(self) -> None:
        """Load API keys from secure storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    self._keys = json.load(f)
                security_logger.info(f"Loaded {len(self._keys)} API keys from storage")
            else:
                self._keys = {}
                security_logger.info("No existing API keys found, starting fresh")
        except Exception as e:
            security_logger.error(f"Failed to load API keys: {str(e)}")
            self._keys = {}
    
    def _save_keys(self) -> None:
        """Save API keys to secure storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self._keys, f, indent=2)
            # Set restrictive permissions (owner read/write only)
            self.storage_path.chmod(0o600)
        except Exception as e:
            security_logger.error(f"Failed to save API keys: {str(e)}")


class AuthenticationValidator:
    """
    Validates authentication for MCP tool access.
    
    Integrates with APIKeyManager to provide authentication decorators
    and middleware for MCP handlers.
    """
    
    def __init__(self, api_key_manager: APIKeyManager):
        """Initialize authentication validator."""
        self.api_key_manager = api_key_manager
    
    def require_authentication(self, func):
        """
        Decorator to require valid API key authentication for MCP tools.
        
        Usage:
            @auth_validator.require_authentication
            async def handle_create_task(args):
                # Handler implementation
        """
        async def wrapper(*args, **kwargs):
            # Extract API key from request context
            api_key = self._extract_api_key(kwargs)
            
            if not api_key:
                security_logger.warning("Authentication required but no API key provided")
                raise AuthenticationError("API key required for this operation")
            
            # Validate the API key
            is_valid, key_metadata = self.api_key_manager.validate_api_key(api_key)
            
            if not is_valid:
                security_logger.warning(f"Authentication failed for operation: {func.__name__}")
                raise AuthenticationError("Invalid or expired API key")
            
            # Add key metadata to request context
            kwargs['_auth_metadata'] = key_metadata
            
            # Execute the original handler
            return await func(*args, **kwargs)
        
        return wrapper
    
    def _extract_api_key(self, request_kwargs: Dict) -> Optional[str]:
        """
        Extract API key from request context.
        
        Checks multiple possible locations:
        1. 'api_key' in request arguments
        2. 'x-api-key' header simulation
        3. Environment variable fallback for development
        """
        # Check direct parameter
        if 'api_key' in request_kwargs:
            return request_kwargs['api_key']
        
        # Check arguments dict if present
        args = request_kwargs.get('arguments', {})
        if isinstance(args, dict) and 'api_key' in args:
            return args['api_key']
        
        # Development fallback (should be removed in production)
        import os
        dev_key = os.environ.get('MCP_TASK_ORCHESTRATOR_DEV_API_KEY')
        if dev_key:
            security_logger.warning("Using development API key from environment")
            return dev_key
        
        return None


class AuthenticationError(Exception):
    """Custom exception for authentication failures."""
    
    def __init__(self, message: str, error_code: str = "AUTH_FAILED"):
        """Initialize authentication error."""
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now(timezone.utc).isoformat()


# Global authentication components for easy import
api_key_manager = APIKeyManager()
auth_validator = AuthenticationValidator(api_key_manager)

# Convenience functions for common operations
def generate_api_key(description: str = "Generated API Key", 
                    expires_days: Optional[int] = None) -> str:
    """Generate a new API key - convenience function."""
    return api_key_manager.generate_api_key(description, expires_days)

def validate_api_key(api_key: str) -> bool:
    """Validate an API key - convenience function."""
    is_valid, _ = api_key_manager.validate_api_key(api_key)
    return is_valid

def require_auth(func):
    """Authentication decorator - convenience function."""
    return auth_validator.require_authentication(func)