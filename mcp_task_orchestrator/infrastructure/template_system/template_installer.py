"""
Template Installation and Management System

Provides functionality to install, update, and manage the default
template library and custom user templates.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import json

from .storage_manager import TemplateStorageManager
from .json5_parser import JSON5Parser
from .security_validator import TemplateSecurityValidator
from .default_templates import get_all_default_templates, get_template_categories
from .additional_templates import get_additional_templates, get_creative_templates, get_business_templates

logger = logging.getLogger(__name__)


class TemplateInstallationError(Exception):
    """Raised when template installation fails."""
    pass


class TemplateInstaller:
    """
    Manages installation and updates of template libraries.
    
    Features:
    - Install default template library
    - Update existing templates 
    - Category-based installation
    - Version management
    - Validation and security checks
    """
    
    def __init__(self,
                 storage_manager: Optional[TemplateStorageManager] = None,
                 json5_parser: Optional[JSON5Parser] = None,
                 security_validator: Optional[TemplateSecurityValidator] = None):
        self.storage_manager = storage_manager or TemplateStorageManager()
        self.json5_parser = json5_parser or JSON5Parser()
        self.security_validator = security_validator or TemplateSecurityValidator()
    
    async def install_default_library(self, 
                                    category: str = "all",
                                    overwrite: bool = False) -> Dict[str, Any]:
        """
        Install the default template library.
        
        Args:
            category: Category to install ("all", "development", "research", etc.)
            overwrite: Whether to overwrite existing templates
            
        Returns:
            Installation results with success/failure counts
        """
        logger.info(f"Installing default template library for category: {category}")
        
        # Get templates based on category
        if category == "all":
            templates = {**get_all_default_templates(), **get_additional_templates()}
        elif category == "development":
            template_names = get_template_categories().get("development", [])
            templates = {name: get_all_default_templates()[name] for name in template_names if name in get_all_default_templates()}
        elif category == "research":
            template_names = get_template_categories().get("research", [])
            templates = {name: get_all_default_templates()[name] for name in template_names if name in get_all_default_templates()}
        elif category == "creative":
            template_names = get_creative_templates()
            additional_templates = get_additional_templates()
            templates = {name: additional_templates[name] for name in template_names if name in additional_templates}
        elif category == "business":
            template_names = get_business_templates()
            additional_templates = get_additional_templates()
            templates = {name: additional_templates[name] for name in template_names if name in additional_templates}
        elif category == "self_development":
            template_names = get_template_categories().get("self_development", [])
            templates = {name: get_all_default_templates()[name] for name in template_names if name in get_all_default_templates()}
        else:
            raise TemplateInstallationError(f"Unknown category: {category}")
        
        if not templates:
            return {
                "status": "error",
                "message": f"No templates found for category: {category}",
                "installed": [],
                "failed": [],
                "skipped": []
            }
        
        # Install templates
        results = {
            "status": "success",
            "category": category,
            "total_templates": len(templates),
            "installed": [],
            "failed": [],
            "skipped": [],
            "errors": []
        }
        
        for template_id, template_content in templates.items():
            try:
                result = await self._install_single_template(
                    template_id, template_content, "builtin", overwrite
                )
                
                if result["status"] == "installed":
                    results["installed"].append(template_id)
                elif result["status"] == "skipped":
                    results["skipped"].append(template_id)
                else:
                    results["failed"].append(template_id)
                    results["errors"].append(f"{template_id}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"Failed to install template {template_id}: {e}")
                results["failed"].append(template_id)
                results["errors"].append(f"{template_id}: {str(e)}")
        
        # Update status based on results
        if results["failed"]:
            if results["installed"]:
                results["status"] = "partial_failure"
                results["message"] = f"Installed {len(results['installed'])} templates, {len(results['failed'])} failed"
            else:
                results["status"] = "failure"
                results["message"] = f"Failed to install all {len(results['failed'])} templates"
        else:
            results["message"] = f"Successfully installed {len(results['installed'])} templates"
        
        logger.info(f"Template installation complete: {results['message']}")
        return results
    
    async def _install_single_template(self, 
                                     template_id: str,
                                     template_content: str,
                                     category: str = "user",
                                     overwrite: bool = False) -> Dict[str, Any]:
        """Install a single template with validation."""
        try:
            # Check if template already exists
            if not overwrite:
                try:
                    existing = await self.storage_manager.load_template(template_id, category)
                    if existing:
                        return {
                            "status": "skipped",
                            "message": f"Template {template_id} already exists"
                        }
                except:
                    # Template doesn't exist, continue with installation
                    pass
            
            # Parse and validate template
            try:
                parsed_template = self.json5_parser.parse(template_content)
            except Exception as e:
                return {
                    "status": "failed",
                    "error": f"JSON5 parsing failed: {str(e)}"
                }
            
            # Security validation
            try:
                self.security_validator.validate_template(parsed_template)
            except Exception as e:
                return {
                    "status": "failed", 
                    "error": f"Security validation failed: {str(e)}"
                }
            
            # Save template
            await self.storage_manager.save_template(template_id, template_content, category)
            
            return {
                "status": "installed",
                "message": f"Template {template_id} installed successfully"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def install_custom_template(self,
                                    template_id: str,
                                    template_content: str,
                                    category: str = "user",
                                    overwrite: bool = False) -> Dict[str, Any]:
        """
        Install a custom user template.
        
        Args:
            template_id: Unique identifier for the template
            template_content: JSON5 template content
            category: Template category (user, shared)
            overwrite: Whether to overwrite existing template
            
        Returns:
            Installation result
        """
        logger.info(f"Installing custom template: {template_id}")
        
        result = await self._install_single_template(
            template_id, template_content, category, overwrite
        )
        
        if result["status"] == "installed":
            logger.info(f"Custom template {template_id} installed successfully")
        else:
            logger.warning(f"Failed to install custom template {template_id}: {result.get('error')}")
        
        return result
    
    async def update_template(self,
                            template_id: str,
                            template_content: str,
                            category: str = "user") -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            template_id: Template to update
            template_content: New template content
            category: Template category
            
        Returns:
            Update result
        """
        logger.info(f"Updating template: {template_id}")
        
        # Check if template exists
        try:
            existing = await self.storage_manager.load_template(template_id, category)
            if not existing:
                return {
                    "status": "error",
                    "error": f"Template {template_id} not found in category {category}"
                }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to check existing template: {str(e)}"
            }
        
        # Install as update (with overwrite)
        result = await self._install_single_template(
            template_id, template_content, category, overwrite=True
        )
        
        if result["status"] == "installed":
            result["status"] = "updated"
            result["message"] = f"Template {template_id} updated successfully"
            logger.info(f"Template {template_id} updated successfully")
        
        return result
    
    async def uninstall_template(self,
                                template_id: str,
                                category: str = "user") -> Dict[str, Any]:
        """
        Uninstall a template.
        
        Args:
            template_id: Template to uninstall
            category: Template category
            
        Returns:
            Uninstall result
        """
        logger.info(f"Uninstalling template: {template_id}")
        
        try:
            success = await self.storage_manager.delete_template(template_id, category)
            
            if success:
                return {
                    "status": "success",
                    "message": f"Template {template_id} uninstalled successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": f"Template {template_id} not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to uninstall template {template_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_installation_status(self) -> Dict[str, Any]:
        """
        Get status of template installations.
        
        Returns:
            Installation status information
        """
        try:
            # Get installed templates by category
            installed = {}
            for category in ["builtin", "user", "shared"]:
                try:
                    templates = await self.storage_manager.list_templates(category)
                    installed[category] = templates
                except:
                    installed[category] = []
            
            # Get available default templates
            default_templates = {**get_all_default_templates(), **get_additional_templates()}
            
            # Calculate statistics
            total_installed = sum(len(templates) for templates in installed.values())
            builtin_installed = len(installed.get("builtin", []))
            user_installed = len(installed.get("user", []))
            
            return {
                "status": "success",
                "total_installed": total_installed,
                "builtin_installed": builtin_installed,
                "user_installed": user_installed,
                "available_defaults": len(default_templates),
                "installed_by_category": installed,
                "installation_coverage": {
                    "development": self._calculate_coverage("development", installed),
                    "research": self._calculate_coverage("research", installed),
                    "creative": self._calculate_coverage("creative", installed),
                    "business": self._calculate_coverage("business", installed),
                    "self_development": self._calculate_coverage("self_development", installed)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get installation status: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_coverage(self, category: str, installed: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate installation coverage for a category."""
        if category == "development":
            available = get_template_categories().get("development", [])
        elif category == "research":
            available = get_template_categories().get("research", [])
        elif category == "creative":
            available = get_creative_templates()
        elif category == "business":
            available = get_business_templates()
        elif category == "self_development":
            available = get_template_categories().get("self_development", [])
        else:
            available = []
        
        if not available:
            return {"total": 0, "installed": 0, "coverage": 0.0}
        
        # Check which are installed
        all_installed = []
        for category_templates in installed.values():
            all_installed.extend(category_templates)
        
        installed_count = sum(1 for template in available if template in all_installed)
        coverage = (installed_count / len(available)) * 100 if available else 0.0
        
        return {
            "total": len(available),
            "installed": installed_count,
            "coverage": round(coverage, 1)
        }
    
    async def validate_all_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate all installed templates.
        
        Args:
            category: Specific category to validate (optional)
            
        Returns:
            Validation results
        """
        logger.info(f"Validating templates in category: {category or 'all'}")
        
        try:
            # Get templates to validate
            if category:
                categories = [category]
            else:
                categories = ["builtin", "user", "shared"]
            
            results = {
                "status": "success",
                "validated": [],
                "failed": [],
                "errors": []
            }
            
            for cat in categories:
                try:
                    templates = await self.storage_manager.list_templates(cat)
                    
                    for template_id in templates:
                        try:
                            # Load and validate template
                            content = await self.storage_manager.load_template(template_id, cat)
                            parsed = self.json5_parser.parse(content)
                            self.security_validator.validate_template(parsed)
                            
                            results["validated"].append(f"{cat}/{template_id}")
                            
                        except Exception as e:
                            error_msg = f"{cat}/{template_id}: {str(e)}"
                            results["failed"].append(f"{cat}/{template_id}")
                            results["errors"].append(error_msg)
                            logger.warning(f"Template validation failed: {error_msg}")
                
                except Exception as e:
                    logger.error(f"Failed to list templates in category {cat}: {e}")
            
            # Update status
            if results["failed"]:
                if results["validated"]:
                    results["status"] = "partial_failure"
                else:
                    results["status"] = "failure"
            
            results["message"] = f"Validated {len(results['validated'])} templates, {len(results['failed'])} failed"
            
            return results
            
        except Exception as e:
            logger.error(f"Template validation error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global template installer instance
_global_template_installer: Optional[TemplateInstaller] = None


def get_template_installer() -> TemplateInstaller:
    """Get the global template installer instance."""
    global _global_template_installer
    if _global_template_installer is None:
        _global_template_installer = TemplateInstaller()
    return _global_template_installer