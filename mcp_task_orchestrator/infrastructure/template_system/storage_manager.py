"""
Template Storage Manager

Manages template storage in the .task_orchestrator/templates/ directory
with CRUD operations, metadata management, and workspace isolation.
"""

import json
import logging
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import uuid

from .json5_parser import JSON5Parser, JSON5ValidationError
from .security_validator import TemplateSecurityValidator, SecurityValidationError

logger = logging.getLogger(__name__)


class TemplateStorageError(Exception):
    """Raised when template storage operations fail."""
    pass


class TemplateStorageManager:
    """
    Manages template storage with workspace isolation and metadata tracking.
    
    Storage structure:
    .task_orchestrator/
    ├── templates/
    │   ├── builtin/           # Built-in templates (read-only)
    │   ├── user/              # User templates
    │   ├── shared/            # Shared templates
    │   └── metadata.json      # Template registry metadata
    """
    
    def __init__(self, workspace_dir: Optional[Path] = None, create_dirs: bool = True):
        self.workspace_dir = workspace_dir or Path.cwd()
        self.orchestrator_dir = self.workspace_dir / ".task_orchestrator"
        self.templates_dir = self.orchestrator_dir / "templates"
        
        # Template category directories
        self.builtin_dir = self.templates_dir / "builtin"
        self.user_dir = self.templates_dir / "user"
        self.shared_dir = self.templates_dir / "shared"
        
        # Metadata file
        self.metadata_file = self.templates_dir / "metadata.json"
        
        # Components
        self.json5_parser = JSON5Parser()
        self.security_validator = TemplateSecurityValidator()
        
        if create_dirs:
            self._ensure_directories()
    
    def save_template(self, template_id: str, template_data: Dict[str, Any], 
                     category: str = "user", overwrite: bool = False) -> None:
        """
        Save a template to storage.
        
        Args:
            template_id: Unique template identifier
            template_data: Template content
            category: Template category (builtin, user, shared)
            overwrite: Whether to overwrite existing template
            
        Raises:
            TemplateStorageError: If save operation fails
        """
        if not self._validate_template_id(template_id):
            raise TemplateStorageError(f"Invalid template ID: {template_id}")
        
        if category not in ["builtin", "user", "shared"]:
            raise TemplateStorageError(f"Invalid category: {category}")
        
        # Security validation
        try:
            self.security_validator.validate_template(template_data)
        except SecurityValidationError as e:
            raise TemplateStorageError(f"Security validation failed: {e}")
        
        # Determine storage directory
        storage_dir = self._get_category_dir(category)
        template_file = storage_dir / f"{template_id}.json5"
        
        # Check if template exists
        if template_file.exists() and not overwrite:
            raise TemplateStorageError(f"Template already exists: {template_id}")
        
        # Read-only check for builtin templates
        if category == "builtin" and template_file.exists():
            raise TemplateStorageError("Built-in templates are read-only")
        
        try:
            # Add metadata to template
            template_with_metadata = self._add_storage_metadata(template_data, template_id, category)
            
            # Save template file
            self._save_template_file(template_file, template_with_metadata)
            
            # Update metadata registry
            self._update_metadata_registry(template_id, template_with_metadata, category)
            
            logger.info(f"Template saved: {template_id} in {category}")
            
        except Exception as e:
            raise TemplateStorageError(f"Failed to save template {template_id}: {e}")
    
    def load_template(self, template_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a template from storage.
        
        Args:
            template_id: Template to load
            category: Specific category to search (None for all)
            
        Returns:
            Template data
            
        Raises:
            TemplateStorageError: If template not found or cannot be loaded
        """
        template_file = self._find_template_file(template_id, category)
        
        if not template_file:
            raise TemplateStorageError(f"Template not found: {template_id}")
        
        try:
            template_data = self.json5_parser.parse_file(template_file)
            
            # Security validation on load
            self.security_validator.validate_template(template_data)
            
            return template_data
            
        except JSON5ValidationError as e:
            raise TemplateStorageError(f"Failed to parse template {template_id}: {e}")
        except SecurityValidationError as e:
            raise TemplateStorageError(f"Security validation failed for template {template_id}: {e}")
    
    def list_templates(self, category: Optional[str] = None, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """
        List available templates.
        
        Args:
            category: Filter by category (None for all)
            include_metadata: Whether to include full metadata
            
        Returns:
            List of template information
        """
        templates = []
        
        # Determine directories to search
        search_dirs = []
        if category:
            if category in ["builtin", "user", "shared"]:
                search_dirs.append((self._get_category_dir(category), category))
        else:
            search_dirs = [
                (self.builtin_dir, "builtin"),
                (self.user_dir, "user"),
                (self.shared_dir, "shared")
            ]
        
        for template_dir, cat in search_dirs:
            if not template_dir.exists():
                continue
                
            for template_file in template_dir.glob("*.json5"):
                template_id = template_file.stem
                
                try:
                    if include_metadata:
                        template_data = self.json5_parser.parse_file(template_file)
                        templates.append({
                            "id": template_id,
                            "category": cat,
                            "file_path": str(template_file),
                            "metadata": template_data.get("metadata", {}),
                            "storage_metadata": template_data.get("_storage", {})
                        })
                    else:
                        # Just extract basic info
                        stat = template_file.stat()
                        templates.append({
                            "id": template_id,
                            "category": cat,
                            "file_path": str(template_file),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to read template {template_id}: {e}")
                    continue
        
        return sorted(templates, key=lambda x: x["id"])
    
    def delete_template(self, template_id: str, category: Optional[str] = None) -> None:
        """
        Delete a template from storage.
        
        Args:
            template_id: Template to delete
            category: Specific category (None to search all)
            
        Raises:
            TemplateStorageError: If template cannot be deleted
        """
        template_file = self._find_template_file(template_id, category)
        
        if not template_file:
            raise TemplateStorageError(f"Template not found: {template_id}")
        
        # Check if it's a builtin template
        if self.builtin_dir in template_file.parents:
            raise TemplateStorageError("Cannot delete built-in templates")
        
        try:
            # Remove template file
            template_file.unlink()
            
            # Remove from metadata registry
            self._remove_from_metadata_registry(template_id)
            
            logger.info(f"Template deleted: {template_id}")
            
        except Exception as e:
            raise TemplateStorageError(f"Failed to delete template {template_id}: {e}")
    
    def backup_templates(self, backup_dir: Optional[Path] = None) -> Path:
        """
        Create a backup of all templates.
        
        Args:
            backup_dir: Directory for backup (default: workspace/backups)
            
        Returns:
            Path to backup directory
        """
        if not backup_dir:
            backup_dir = self.workspace_dir / "backups" / f"templates_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy templates directory
            if self.templates_dir.exists():
                shutil.copytree(self.templates_dir, backup_dir / "templates")
            
            # Create backup metadata
            backup_metadata = {
                "created": datetime.now().isoformat(),
                "workspace": str(self.workspace_dir),
                "template_count": len(self.list_templates())
            }
            
            with open(backup_dir / "backup_info.json", 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            logger.info(f"Templates backed up to: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            raise TemplateStorageError(f"Backup failed: {e}")
    
    def restore_templates(self, backup_dir: Path, overwrite: bool = False) -> None:
        """
        Restore templates from backup.
        
        Args:
            backup_dir: Backup directory
            overwrite: Whether to overwrite existing templates
            
        Raises:
            TemplateStorageError: If restore fails
        """
        backup_templates_dir = backup_dir / "templates"
        
        if not backup_templates_dir.exists():
            raise TemplateStorageError(f"Backup templates directory not found: {backup_templates_dir}")
        
        try:
            if overwrite and self.templates_dir.exists():
                shutil.rmtree(self.templates_dir)
            
            shutil.copytree(backup_templates_dir, self.templates_dir, dirs_exist_ok=not overwrite)
            
            logger.info(f"Templates restored from: {backup_dir}")
            
        except Exception as e:
            raise TemplateStorageError(f"Restore failed: {e}")
    
    def get_template_info(self, template_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a template.
        
        Args:
            template_id: Template to analyze
            category: Specific category to search
            
        Returns:
            Template information dictionary
        """
        template_file = self._find_template_file(template_id, category)
        
        if not template_file:
            raise TemplateStorageError(f"Template not found: {template_id}")
        
        try:
            template_data = self.json5_parser.parse_file(template_file)
            stat = template_file.stat()
            
            # Determine category
            file_category = "unknown"
            for cat, cat_dir in [("builtin", self.builtin_dir), ("user", self.user_dir), ("shared", self.shared_dir)]:
                if cat_dir in template_file.parents:
                    file_category = cat
                    break
            
            return {
                "id": template_id,
                "category": file_category,
                "file_path": str(template_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "metadata": template_data.get("metadata", {}),
                "storage_metadata": template_data.get("_storage", {}),
                "parameters": list(template_data.get("parameters", {}).keys()),
                "tasks": list(template_data.get("tasks", {}).keys()),
                "content_hash": self.security_validator.generate_content_hash(template_data)
            }
            
        except Exception as e:
            raise TemplateStorageError(f"Failed to get template info for {template_id}: {e}")
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for directory in [self.orchestrator_dir, self.templates_dir, self.builtin_dir, self.user_dir, self.shared_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _validate_template_id(self, template_id: str) -> bool:
        """Validate template ID format."""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', template_id)) and len(template_id) <= 100
    
    def _get_category_dir(self, category: str) -> Path:
        """Get directory for template category."""
        return {
            "builtin": self.builtin_dir,
            "user": self.user_dir,
            "shared": self.shared_dir
        }[category]
    
    def _find_template_file(self, template_id: str, category: Optional[str] = None) -> Optional[Path]:
        """Find template file across categories."""
        search_dirs = []
        
        if category:
            search_dirs.append(self._get_category_dir(category))
        else:
            # Search in order: user, shared, builtin
            search_dirs = [self.user_dir, self.shared_dir, self.builtin_dir]
        
        for directory in search_dirs:
            template_file = directory / f"{template_id}.json5"
            if template_file.exists():
                return template_file
        
        return None
    
    def _add_storage_metadata(self, template_data: Dict[str, Any], template_id: str, category: str) -> Dict[str, Any]:
        """Add storage metadata to template."""
        template_with_metadata = template_data.copy()
        
        storage_metadata = {
            "template_id": template_id,
            "category": category,
            "stored_at": datetime.now().isoformat(),
            "storage_version": "1.0",
            "storage_uuid": str(uuid.uuid4())
        }
        
        template_with_metadata["_storage"] = storage_metadata
        return template_with_metadata
    
    def _save_template_file(self, template_file: Path, template_data: Dict[str, Any]) -> None:
        """Save template to file in JSON5 format."""
        # Convert to JSON5 format with pretty printing
        json_content = json.dumps(template_data, indent=2, ensure_ascii=False)
        
        # Add JSON5 comment header
        json5_content = f"""// JSON5 Template File
// Generated by MCP Task Orchestrator
// Template ID: {template_data.get('_storage', {}).get('template_id', 'unknown')}
// Created: {template_data.get('_storage', {}).get('stored_at', 'unknown')}

{json_content}
"""
        
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(json5_content)
    
    def _update_metadata_registry(self, template_id: str, template_data: Dict[str, Any], category: str) -> None:
        """Update the metadata registry."""
        try:
            # Load existing metadata
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    registry = json.load(f)
            else:
                registry = {"templates": {}, "last_updated": None}
            
            # Update template entry
            registry["templates"][template_id] = {
                "category": category,
                "metadata": template_data.get("metadata", {}),
                "storage": template_data.get("_storage", {}),
                "last_updated": datetime.now().isoformat()
            }
            
            registry["last_updated"] = datetime.now().isoformat()
            
            # Save updated registry
            with open(self.metadata_file, 'w') as f:
                json.dump(registry, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to update metadata registry: {e}")
    
    def _remove_from_metadata_registry(self, template_id: str) -> None:
        """Remove template from metadata registry."""
        try:
            if not self.metadata_file.exists():
                return
            
            with open(self.metadata_file, 'r') as f:
                registry = json.load(f)
            
            if template_id in registry.get("templates", {}):
                del registry["templates"][template_id]
                registry["last_updated"] = datetime.now().isoformat()
                
                with open(self.metadata_file, 'w') as f:
                    json.dump(registry, f, indent=2)
                    
        except Exception as e:
            logger.warning(f"Failed to remove from metadata registry: {e}")