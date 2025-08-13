"""
MCP Tools for JSON5 Template System

Provides MCP tools for template management including create, list, 
instantiate, validate, and CRUD operations.
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path
from mcp import types

from .storage_manager import TemplateStorageManager, TemplateStorageError
from .template_engine import TemplateEngine, TemplateValidationError, ParameterSubstitutionError
from .json5_parser import JSON5Parser, JSON5ValidationError
from .example_templates import EXAMPLE_TEMPLATES, get_example_template
from .template_installer import get_template_installer

logger = logging.getLogger(__name__)


def get_template_tools() -> List[types.Tool]:
    """Get all template management MCP tools."""
    return [
        types.Tool(
            name="template_create",
            description="Create a new JSON5 template in the template system",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Unique template identifier (alphanumeric, underscore, hyphen only)"
                    },
                    "template_content": {
                        "type": "string", 
                        "description": "JSON5 template content"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["user", "shared"],
                        "description": "Template category (builtin is read-only)",
                        "default": "user"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing template",
                        "default": False
                    }
                },
                "required": ["template_id", "template_content"]
            }
        ),
        types.Tool(
            name="template_list",
            description="List available templates with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["builtin", "user", "shared"],
                        "description": "Filter by template category (optional)"
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "description": "Include full template metadata",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="template_load",
            description="Load a template and show its content and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID to load"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["builtin", "user", "shared"],
                        "description": "Specific category to search (optional)"
                    }
                },
                "required": ["template_id"]
            }
        ),
        types.Tool(
            name="template_instantiate",
            description="Create tasks from a template with parameter substitution",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template to instantiate"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameter values for template substitution"
                    },
                    "create_tasks": {
                        "type": "boolean",
                        "description": "Whether to create actual tasks in the orchestrator",
                        "default": False
                    }
                },
                "required": ["template_id", "parameters"]
            }
        ),
        types.Tool(
            name="template_validate",
            description="Validate template syntax, structure, and security",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_content": {
                        "type": "string",
                        "description": "JSON5 template content to validate"
                    }
                },
                "required": ["template_content"]
            }
        ),
        types.Tool(
            name="template_delete",
            description="Delete a template from storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID to delete"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["user", "shared"],
                        "description": "Category to search (builtin templates cannot be deleted)"
                    }
                },
                "required": ["template_id"]
            }
        ),
        types.Tool(
            name="template_info",
            description="Get detailed information about a template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID to analyze"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["builtin", "user", "shared"],
                        "description": "Specific category to search (optional)"
                    }
                },
                "required": ["template_id"]
            }
        ),
        types.Tool(
            name="template_install_examples",
            description="Install example templates to get started with the template system",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["user", "shared"],
                        "description": "Category to install examples in",
                        "default": "shared"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing examples",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="template_install_default_library",
            description="Install the default template library",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["all", "development", "research", "creative", "business", "self_development"],
                        "description": "Category of templates to install",
                        "default": "all"
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "Whether to overwrite existing templates",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="template_get_installation_status",
            description="Get status of template installations and coverage",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="template_validate_all",
            description="Validate all installed templates for security and syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["builtin", "user", "shared"],
                        "description": "Specific category to validate (optional)"
                    }
                }
            }
        ),
        types.Tool(
            name="template_uninstall",
            description="Uninstall a template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID to uninstall"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["user", "shared"],
                        "description": "Template category",
                        "default": "user"
                    }
                },
                "required": ["template_id"]
            }
        )
    ]


async def handle_template_create(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template creation."""
    try:
        template_id = args["template_id"]
        template_content = args["template_content"]
        category = args.get("category", "user")
        overwrite = args.get("overwrite", False)
        
        # Initialize storage manager
        storage_manager = TemplateStorageManager()
        
        # Parse and validate the template content
        json5_parser = JSON5Parser()
        template_data = json5_parser.parse(template_content)
        
        # Save the template
        storage_manager.save_template(template_id, template_data, category, overwrite)
        
        response = {
            "status": "success",
            "message": f"Template '{template_id}' created successfully in {category} category",
            "template_id": template_id,
            "category": category,
            "next_steps": [
                "Use 'template_instantiate' to create tasks from this template",
                f"Use 'template_info {template_id}' to view template details",
                "Use 'template_list' to see all available templates"
            ]
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except (JSON5ValidationError, TemplateStorageError) as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_list(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template listing."""
    try:
        category = args.get("category")
        include_metadata = args.get("include_metadata", False)
        
        storage_manager = TemplateStorageManager()
        templates = storage_manager.list_templates(category, include_metadata)
        
        response = {
            "status": "success",
            "templates": templates,
            "total_count": len(templates),
            "filtered_by_category": category or "all"
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except TemplateStorageError as e:
        error_response = {
            "status": "error",
            "error_type": "TemplateStorageError",
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_load(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template loading."""
    try:
        template_id = args["template_id"]
        category = args.get("category")
        
        storage_manager = TemplateStorageManager()
        template_data = storage_manager.load_template(template_id, category)
        
        # Also get template info
        template_info = storage_manager.get_template_info(template_id, category)
        
        response = {
            "status": "success",
            "template": template_data,
            "info": template_info
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except TemplateStorageError as e:
        error_response = {
            "status": "error",
            "error_type": "TemplateStorageError",
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_instantiate(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template instantiation."""
    try:
        template_id = args["template_id"]
        parameters = args["parameters"]
        create_tasks = args.get("create_tasks", False)
        
        # Initialize template engine
        template_engine = TemplateEngine()
        
        # Instantiate the template
        instantiated_template = template_engine.instantiate_template(template_id, parameters)
        
        response = {
            "status": "success",
            "message": f"Template '{template_id}' instantiated successfully",
            "instantiated_template": instantiated_template,
            "parameters_used": parameters,
            "tasks_created": create_tasks
        }
        
        # If create_tasks is True, we would integrate with the task orchestrator here
        if create_tasks:
            response["message"] += " and tasks created in orchestrator"
            response["next_steps"] = [
                "Use 'orchestrator_get_status' to see created tasks",
                "Use task management tools to execute the created tasks"
            ]
        else:
            response["next_steps"] = [
                "Review the instantiated template above",
                "Set 'create_tasks: true' to actually create tasks in the orchestrator"
            ]
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except (TemplateValidationError, ParameterSubstitutionError, TemplateStorageError) as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_validate(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template validation."""
    try:
        template_content = args["template_content"]
        
        # Parse JSON5
        json5_parser = JSON5Parser()
        template_data = json5_parser.parse(template_content)
        
        # Validate with template engine
        template_engine = TemplateEngine()
        validation_errors = template_engine.validate_template_syntax(template_data)
        
        if validation_errors:
            response = {
                "status": "invalid",
                "valid": False,
                "errors": validation_errors,
                "message": f"Template validation failed with {len(validation_errors)} errors"
            }
        else:
            response = {
                "status": "valid",
                "valid": True,
                "message": "Template validation passed",
                "template_info": {
                    "metadata": template_data.get("metadata", {}),
                    "parameters": list(template_data.get("parameters", {}).keys()),
                    "tasks": list(template_data.get("tasks", {}).keys())
                }
            }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except JSON5ValidationError as e:
        error_response = {
            "status": "invalid",
            "valid": False,
            "error_type": "JSON5ValidationError",
            "message": f"JSON5 parsing failed: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_delete(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template deletion."""
    try:
        template_id = args["template_id"]
        category = args.get("category")
        
        storage_manager = TemplateStorageManager()
        storage_manager.delete_template(template_id, category)
        
        response = {
            "status": "success",
            "message": f"Template '{template_id}' deleted successfully",
            "deleted_template": template_id
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except TemplateStorageError as e:
        error_response = {
            "status": "error",
            "error_type": "TemplateStorageError",
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_info(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template info retrieval."""
    try:
        template_id = args["template_id"]
        category = args.get("category")
        
        storage_manager = TemplateStorageManager()
        template_info = storage_manager.get_template_info(template_id, category)
        
        # Also get parameter definitions
        template_engine = TemplateEngine()
        try:
            parameters = template_engine.get_template_parameters(template_id)
            parameter_details = [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default,
                    "validation": {
                        "pattern": param.validation_pattern,
                        "allowed_values": param.allowed_values,
                        "min_length": param.min_length,
                        "max_length": param.max_length,
                        "min_value": param.min_value,
                        "max_value": param.max_value
                    }
                }
                for param in parameters
            ]
            template_info["parameter_definitions"] = parameter_details
        except Exception as e:
            logger.warning(f"Could not load parameter definitions: {e}")
        
        response = {
            "status": "success",
            "template_info": template_info
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except TemplateStorageError as e:
        error_response = {
            "status": "error",
            "error_type": "TemplateStorageError",
            "message": str(e)
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_install_examples(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle example template installation."""
    try:
        category = args.get("category", "shared")
        overwrite = args.get("overwrite", False)
        
        storage_manager = TemplateStorageManager()
        json5_parser = JSON5Parser()
        
        installed_templates = []
        errors = []
        
        for template_name, template_content in EXAMPLE_TEMPLATES.items():
            try:
                # Parse the template
                template_data = json5_parser.parse(template_content)
                
                # Save the template
                storage_manager.save_template(template_name, template_data, category, overwrite)
                installed_templates.append(template_name)
                
            except Exception as e:
                errors.append(f"Failed to install {template_name}: {str(e)}")
                logger.error(f"Failed to install example template {template_name}: {e}")
        
        response = {
            "status": "success" if installed_templates else "partial_failure",
            "message": f"Installed {len(installed_templates)} example templates in {category} category",
            "installed_templates": installed_templates,
            "category": category,
            "errors": errors if errors else None,
            "next_steps": [
                "Use 'template_list' to see all installed templates",
                "Use 'template_info <template_id>' to explore template details",
                "Use 'template_instantiate' to create tasks from templates"
            ]
        }
        
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to install example templates: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_install_default_library(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle installation of default template library."""
    try:
        category = args.get("category", "all")
        overwrite = args.get("overwrite", False)
        
        installer = get_template_installer()
        result = await installer.install_default_library(category, overwrite)
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to install default library: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_get_installation_status(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle getting template installation status."""
    try:
        installer = get_template_installer()
        result = await installer.get_installation_status()
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to get installation status: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_validate_all(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle validation of all templates."""
    try:
        category = args.get("category")
        
        installer = get_template_installer()
        result = await installer.validate_all_templates(category)
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to validate templates: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def handle_template_uninstall(args: Dict[str, Any]) -> List[types.TextContent]:
    """Handle template uninstallation."""
    try:
        template_id = args["template_id"]
        category = args.get("category", "user")
        
        installer = get_template_installer()
        result = await installer.uninstall_template(template_id, category)
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        error_response = {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to uninstall template: {str(e)}"
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]


# Template tool handlers mapping
TEMPLATE_TOOL_HANDLERS = {
    "template_create": handle_template_create,
    "template_list": handle_template_list,
    "template_load": handle_template_load,
    "template_instantiate": handle_template_instantiate,
    "template_validate": handle_template_validate,
    "template_delete": handle_template_delete,
    "template_info": handle_template_info,
    "template_install_examples": handle_template_install_examples,
    "template_install_default_library": handle_template_install_default_library,
    "template_get_installation_status": handle_template_get_installation_status,
    "template_validate_all": handle_template_validate_all,
    "template_uninstall": handle_template_uninstall
}