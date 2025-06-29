"""
Template Operations Module - Task template management for Generic Tasks

This module provides template operations including:
- Saving and retrieving task templates
- Template versioning and validation
- Template usage tracking
- Template schema management
"""

import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.sql import text

from ...orchestrator.generic_models import TaskTemplate
from .converters import row_to_template

logger = logging.getLogger(__name__)


async def save_template(repo_instance, template: TaskTemplate) -> TaskTemplate:
    """Save a task template.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        template: The template to save
        
    Returns:
        The saved template
    """
    async with repo_instance.get_session() as session:
        stmt = text("""
            INSERT OR REPLACE INTO task_templates (
                template_id, template_name, template_category, template_version,
                description, template_schema, default_values, task_structure,
                is_active, is_public, created_by, tags,
                usage_count, last_used_at, created_at, updated_at
            ) VALUES (
                :template_id, :template_name, :template_category, :template_version,
                :description, :template_schema, :default_values, :task_structure,
                :is_active, :is_public, :created_by, :tags,
                :usage_count, :last_used_at, :created_at, :updated_at
            )
        """)
        
        # Convert template to storage format
        params = {
            "template_id": template.template_id,
            "template_name": template.template_name,
            "template_category": template.template_category,
            "template_version": template.template_version,
            "description": template.description,
            "template_schema": json.dumps([p.dict() for p in template.parameters]),
            "default_values": json.dumps({
                p.name: p.default for p in template.parameters if p.default is not None
            }),
            "task_structure": json.dumps(template.task_structure),
            "is_active": template.is_active,
            "is_public": template.is_public,
            "created_by": template.created_by,
            "tags": json.dumps(template.tags),
            "usage_count": template.usage_count,
            "last_used_at": template.last_used_at.isoformat() if template.last_used_at else None,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
        
        await session.execute(stmt, params)
        logger.info(f"Saved template {template.template_id}")
        return template


async def get_template(repo_instance, template_id: str) -> Optional[TaskTemplate]:
    """Get a template by ID.
    
    Args:
        repo_instance: Repository instance for accessing session and helper methods
        template_id: The template ID
        
    Returns:
        The template if found
    """
    async with repo_instance.get_session() as session:
        stmt = text("SELECT * FROM task_templates WHERE template_id = :template_id")
        result = await session.execute(stmt, {"template_id": template_id})
        row = result.fetchone()
        
        if row:
            return row_to_template(dict(row))
        return None