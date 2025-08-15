"""
Hook registry for managing and discovering available hooks.

Provides centralized hook registration, discovery, and configuration
with support for executive dysfunction-aware hook selection.
"""

from typing import Dict, List, Optional, Set, Type, Any
from dataclasses import dataclass
import logging

from .base import Hook, HookType, ExecutiveDysfunctionHook

logger = logging.getLogger(__name__)


@dataclass
class HookRegistration:
    """Information about a registered hook."""
    hook_class: Type[Hook]
    hook_id: str
    description: str
    hook_types: List[HookType]
    ed_features: Dict[str, bool]
    dependencies: List[str]
    tags: List[str]
    priority: int = 100  # Lower numbers = higher priority


class HookRegistry:
    """
    Central registry for template hooks.
    
    Provides hook discovery, instantiation, and configuration
    with executive dysfunction-aware selection and filtering.
    """
    
    def __init__(self):
        self._hooks: Dict[str, HookRegistration] = {}
        self._hooks_by_type: Dict[HookType, List[str]] = {}
        self._hooks_by_tag: Dict[str, List[str]] = {}
        self._ed_hooks: Set[str] = set()
        
        # Initialize with built-in hooks
        self._register_builtin_hooks()
    
    def register_hook(
        self,
        hook_class: Type[Hook],
        hook_types: List[HookType],
        tags: Optional[List[str]] = None,
        priority: int = 100
    ) -> None:
        """
        Register a hook class with the registry.
        
        Args:
            hook_class: Hook class to register
            hook_types: List of hook types this hook supports
            tags: Optional tags for categorization
            priority: Priority for execution ordering (lower = higher priority)
        """
        # Create temporary instance to get metadata
        temp_instance = hook_class()
        
        registration = HookRegistration(
            hook_class=hook_class,
            hook_id=temp_instance.hook_id,
            description=temp_instance.description,
            hook_types=hook_types,
            ed_features=temp_instance.get_ed_support_features(),
            dependencies=temp_instance.get_dependencies(),
            tags=tags or [],
            priority=priority
        )
        
        # Store registration
        self._hooks[temp_instance.hook_id] = registration
        
        # Index by type
        for hook_type in hook_types:
            if hook_type not in self._hooks_by_type:
                self._hooks_by_type[hook_type] = []
            self._hooks_by_type[hook_type].append(temp_instance.hook_id)
        
        # Index by tags
        for tag in registration.tags:
            if tag not in self._hooks_by_tag:
                self._hooks_by_tag[tag] = []
            self._hooks_by_tag[tag].append(temp_instance.hook_id)
        
        # Track ED-aware hooks
        if isinstance(temp_instance, ExecutiveDysfunctionHook):
            self._ed_hooks.add(temp_instance.hook_id)
        
        logger.info(f"Registered hook: {temp_instance.hook_id} ({hook_class.__name__})")
    
    def get_hook(self, hook_id: str) -> Optional[Hook]:
        """
        Get hook instance by ID.
        
        Args:
            hook_id: Hook identifier
            
        Returns:
            Hook instance or None if not found
        """
        registration = self._hooks.get(hook_id)
        if not registration:
            return None
        
        return registration.hook_class()
    
    def get_hooks_for_type(
        self,
        hook_type: HookType,
        ed_only: bool = False,
        tags: Optional[List[str]] = None
    ) -> List[Hook]:
        """
        Get all hooks for a specific type.
        
        Args:
            hook_type: Type of hooks to retrieve
            ed_only: If True, only return executive dysfunction-aware hooks
            tags: Optional tags to filter by
            
        Returns:
            List of hook instances matching criteria
        """
        hook_ids = self._hooks_by_type.get(hook_type, [])
        
        # Filter by ED requirement
        if ed_only:
            hook_ids = [hid for hid in hook_ids if hid in self._ed_hooks]
        
        # Filter by tags
        if tags:
            tag_filtered = set()
            for tag in tags:
                tag_filtered.update(self._hooks_by_tag.get(tag, []))
            hook_ids = [hid for hid in hook_ids if hid in tag_filtered]
        
        # Get hook instances
        hooks = []
        for hook_id in hook_ids:
            hook = self.get_hook(hook_id)
            if hook:
                hooks.append(hook)
        
        # Sort by priority
        hooks.sort(key=lambda h: self._hooks[h.hook_id].priority)
        
        return hooks
    
    def list_hooks(self, include_details: bool = False) -> List[Dict[str, Any]]:
        """
        List all registered hooks.
        
        Args:
            include_details: If True, include detailed hook information
            
        Returns:
            List of hook information dictionaries
        """
        hooks_info = []
        
        for hook_id, registration in self._hooks.items():
            hook_info = {
                "hook_id": hook_id,
                "description": registration.description,
                "hook_types": [ht.value for ht in registration.hook_types],
                "is_ed_aware": hook_id in self._ed_hooks,
                "priority": registration.priority
            }
            
            if include_details:
                hook_info.update({
                    "ed_features": registration.ed_features,
                    "dependencies": registration.dependencies,
                    "tags": registration.tags,
                    "class_name": registration.hook_class.__name__
                })
            
            hooks_info.append(hook_info)
        
        return hooks_info
    
    def find_hooks_by_features(
        self,
        required_features: List[str],
        hook_type: Optional[HookType] = None
    ) -> List[Hook]:
        """
        Find hooks that provide specific ED features.
        
        Args:
            required_features: List of required ED features
            hook_type: Optional hook type filter
            
        Returns:
            List of hooks providing all required features
        """
        matching_hooks = []
        
        for hook_id, registration in self._hooks.items():
            # Check hook type filter
            if hook_type and hook_type not in registration.hook_types:
                continue
            
            # Check if hook provides all required features
            if all(registration.ed_features.get(feature, False) for feature in required_features):
                hook = self.get_hook(hook_id)
                if hook:
                    matching_hooks.append(hook)
        
        return matching_hooks
    
    def get_recommended_hooks_for_template(
        self,
        template_metadata: Dict[str, Any],
        hook_type: HookType
    ) -> List[Hook]:
        """
        Get recommended hooks for a specific template.
        
        Uses template metadata to recommend most suitable hooks
        with executive dysfunction considerations.
        
        Args:
            template_metadata: Template metadata for analysis
            hook_type: Type of hooks to recommend
            
        Returns:
            List of recommended hooks in priority order
        """
        all_hooks = self.get_hooks_for_type(hook_type)
        
        # Score hooks based on template characteristics
        scored_hooks = []
        for hook in all_hooks:
            score = self._calculate_hook_score(hook, template_metadata)
            scored_hooks.append((hook, score))
        
        # Sort by score (highest first) and return hooks
        scored_hooks.sort(key=lambda x: x[1], reverse=True)
        return [hook for hook, _ in scored_hooks]
    
    def validate_hook_configuration(
        self,
        hook_ids: List[str]
    ) -> Dict[str, List[str]]:
        """
        Validate a hook configuration for dependency and compatibility issues.
        
        Args:
            hook_ids: List of hook IDs to validate
            
        Returns:
            Dictionary with validation results:
            - "errors": List of error messages
            - "warnings": List of warning messages
            - "missing_dependencies": List of missing dependencies
        """
        errors = []
        warnings = []
        missing_dependencies = []
        
        # Check if all hooks exist
        for hook_id in hook_ids:
            if hook_id not in self._hooks:
                errors.append(f"Unknown hook: {hook_id}")
        
        # Check dependencies
        all_hook_ids = set(hook_ids)
        for hook_id in hook_ids:
            if hook_id not in self._hooks:
                continue
                
            registration = self._hooks[hook_id]
            for dep in registration.dependencies:
                if dep not in all_hook_ids:
                    missing_dependencies.append(f"{hook_id} requires {dep}")
        
        # Check for potential conflicts
        ed_hook_count = sum(1 for hid in hook_ids if hid in self._ed_hooks)
        non_ed_hook_count = len(hook_ids) - ed_hook_count
        
        if ed_hook_count > 0 and non_ed_hook_count > ed_hook_count:
            warnings.append(
                f"Mixed ED-aware ({ed_hook_count}) and non-ED hooks ({non_ed_hook_count}) - "
                "consider using ED-aware hooks for consistency"
            )
        
        return {
            "errors": errors,
            "warnings": warnings,
            "missing_dependencies": missing_dependencies
        }
    
    def _register_builtin_hooks(self) -> None:
        """Register built-in hooks."""
        from .builtin_hooks import (
            GitBranchHook,
            WorkspaceSetupHook,
            AgentSpawningHook,
            DocumentAssociationHook,
            CheckpointHook,
            ValidationHook,
            CommitHook,
            NotificationHook
        )
        
        # Register git operations
        self.register_hook(
            GitBranchHook,
            [HookType.PRE_EXECUTION],
            tags=["git", "automation", "ed-aware"],
            priority=10
        )
        
        # Register workspace setup
        self.register_hook(
            WorkspaceSetupHook,
            [HookType.PRE_EXECUTION],
            tags=["workspace", "setup", "ed-aware"],
            priority=5
        )
        
        # Register agent spawning
        self.register_hook(
            AgentSpawningHook,
            [HookType.PHASE_INIT],
            tags=["agents", "spawning", "ed-aware"],
            priority=20
        )
        
        # Register document association
        self.register_hook(
            DocumentAssociationHook,
            [HookType.PRE_EXECUTION, HookType.PHASE_INIT],
            tags=["documents", "context", "ed-aware"],
            priority=15
        )
        
        # Register checkpointing
        self.register_hook(
            CheckpointHook,
            [HookType.PHASE_TRANSITION, HookType.CONTEXT_RECOVERY],
            tags=["checkpoints", "recovery", "ed-aware"],
            priority=25
        )
        
        # Register validation
        self.register_hook(
            ValidationHook,
            [HookType.PHASE_TRANSITION, HookType.POST_EXECUTION],
            tags=["validation", "quality"],
            priority=30
        )
        
        # Register commits
        self.register_hook(
            CommitHook,
            [HookType.PHASE_TRANSITION, HookType.POST_EXECUTION],
            tags=["git", "commits", "ed-aware"],
            priority=35
        )
        
        # Register notifications
        self.register_hook(
            NotificationHook,
            [HookType.PHASE_TRANSITION, HookType.POST_EXECUTION],
            tags=["notifications", "progress"],
            priority=50
        )
    
    def _calculate_hook_score(
        self,
        hook: Hook,
        template_metadata: Dict[str, Any]
    ) -> float:
        """Calculate compatibility score between hook and template."""
        score = 0.0
        registration = self._hooks[hook.hook_id]
        
        # Base score from priority (lower priority = higher score)
        score += max(0, 100 - registration.priority) / 100
        
        # Boost for ED-aware hooks if template benefits from ED features
        if hook.hook_id in self._ed_hooks:
            template_complexity = template_metadata.get("complexity", "medium")
            if template_complexity in ["high", "very_high"]:
                score += 0.5
            elif template_complexity == "medium":
                score += 0.3
        
        # Boost for hooks with relevant tags
        template_tags = template_metadata.get("tags", [])
        common_tags = set(registration.tags) & set(template_tags)
        score += len(common_tags) * 0.2
        
        # Consider template-specific preferences
        preferred_hooks = template_metadata.get("preferred_hooks", [])
        if hook.hook_id in preferred_hooks:
            score += 1.0
        
        excluded_hooks = template_metadata.get("excluded_hooks", [])
        if hook.hook_id in excluded_hooks:
            score = 0.0
        
        return min(score, 2.0)  # Cap at 2.0


# Global registry instance
_global_registry = HookRegistry()


def register_hook(
    hook_class: Type[Hook],
    hook_types: List[HookType],
    tags: Optional[List[str]] = None,
    priority: int = 100
) -> None:
    """Register a hook with the global registry."""
    _global_registry.register_hook(hook_class, hook_types, tags, priority)


def get_hook(hook_id: str) -> Optional[Hook]:
    """Get hook from global registry."""
    return _global_registry.get_hook(hook_id)


def get_hooks_for_type(
    hook_type: HookType,
    ed_only: bool = False,
    tags: Optional[List[str]] = None
) -> List[Hook]:
    """Get hooks for type from global registry."""
    return _global_registry.get_hooks_for_type(hook_type, ed_only, tags)


def list_hooks(include_details: bool = False) -> List[Dict[str, Any]]:
    """List all hooks from global registry."""
    return _global_registry.list_hooks(include_details)


def find_hooks_by_features(
    required_features: List[str],
    hook_type: Optional[HookType] = None
) -> List[Hook]:
    """Find hooks by ED features from global registry."""
    return _global_registry.find_hooks_by_features(required_features, hook_type)


def get_registry() -> HookRegistry:
    """Get global hook registry instance."""
    return _global_registry