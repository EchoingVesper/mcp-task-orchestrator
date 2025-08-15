"""
Example JSON5 Templates

Provides example templates to demonstrate the JSON5 template system
capabilities and serve as a starting point for users.
"""

# Example: Basic Project Setup Template
BASIC_PROJECT_SETUP = """// Basic Project Setup Template
// Creates a standard software project structure with initial tasks

{
  "metadata": {
    "name": "Basic Project Setup",
    "version": "1.0.0",
    "description": "Creates initial project structure and setup tasks",
    "author": "MCP Task Orchestrator",
    "category": "development",
    "tags": ["project", "setup", "development"]
  },
  
  "parameters": {
    "project_name": {
      "type": "string",
      "description": "Name of the project",
      "required": true,
      "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$",
      "min_length": 2,
      "max_length": 50
    },
    "project_type": {
      "type": "string", 
      "description": "Type of project",
      "required": true,
      "allowed_values": ["web", "api", "library", "cli", "desktop", "mobile"]
    },
    "language": {
      "type": "string",
      "description": "Primary programming language",
      "required": true,
      "allowed_values": ["python", "javascript", "typescript", "java", "rust", "go", "csharp"]
    },
    "include_tests": {
      "type": "boolean",
      "description": "Include test setup tasks",
      "required": false,
      "default": true
    },
    "include_docs": {
      "type": "boolean", 
      "description": "Include documentation setup tasks",
      "required": false,
      "default": true
    }
  },
  
  "tasks": {
    "project_initialization": {
      "title": "Initialize {{project_name}} Project",
      "description": "Set up the basic project structure for {{project_name}} ({{project_type}} in {{language}})",
      "type": "implementation",
      "specialist_type": "architect",
      "estimated_effort": "2 hours",
      "children": {
        "create_directory_structure": {
          "title": "Create Directory Structure",
          "description": "Create the standard directory layout for a {{language}} {{project_type}} project",
          "type": "implementation",
          "specialist_type": "coder",
          "estimated_effort": "30 minutes"
        },
        "setup_build_system": {
          "title": "Setup Build System", 
          "description": "Configure build tools and dependency management for {{language}}",
          "type": "implementation",
          "specialist_type": "devops",
          "estimated_effort": "1 hour"
        },
        "create_initial_files": {
          "title": "Create Initial Files",
          "description": "Generate initial project files (README, gitignore, config files)",
          "type": "implementation", 
          "specialist_type": "coder",
          "estimated_effort": "30 minutes"
        }
      }
    }
  }
}"""

# Example: Code Review Template
CODE_REVIEW_TEMPLATE = """// Code Review Process Template
// Structured approach to conducting thorough code reviews

{
  "metadata": {
    "name": "Code Review Process",
    "version": "1.1.0", 
    "description": "Comprehensive code review workflow with security and quality checks",
    "author": "MCP Task Orchestrator",
    "category": "quality-assurance",
    "tags": ["code-review", "quality", "security", "testing"]
  },
  
  "parameters": {
    "pr_number": {
      "type": "string",
      "description": "Pull request number or identifier",
      "required": true,
      "pattern": "^[a-zA-Z0-9_-]+$"
    },
    "reviewer_name": {
      "type": "string", 
      "description": "Name of the reviewer",
      "required": true,
      "min_length": 2,
      "max_length": 50
    },
    "review_type": {
      "type": "string",
      "description": "Type of review to conduct", 
      "required": true,
      "allowed_values": ["standard", "security", "performance", "architecture"]
    },
    "urgency": {
      "type": "string",
      "description": "Review urgency level",
      "required": false,
      "default": "normal",
      "allowed_values": ["low", "normal", "high", "critical"]
    }
  },
  
  "tasks": {
    "code_review_process": {
      "title": "Code Review for PR {{pr_number}}",
      "description": "{{review_type}} code review conducted by {{reviewer_name}}",
      "type": "review",
      "specialist_type": "reviewer", 
      "estimated_effort": "2 hours",
      "children": {
        "initial_assessment": {
          "title": "Initial Assessment",
          "description": "Quick overview of changes and impact analysis",
          "type": "review",
          "specialist_type": "analyst",
          "estimated_effort": "15 minutes"
        },
        "code_quality_check": {
          "title": "Code Quality Review",
          "description": "Check coding standards, best practices, and maintainability",
          "type": "review", 
          "specialist_type": "reviewer",
          "estimated_effort": "45 minutes"
        },
        "security_analysis": {
          "title": "Security Analysis",
          "description": "Review for security vulnerabilities and compliance",
          "type": "review",
          "specialist_type": "reviewer",
          "estimated_effort": "30 minutes"
        },
        "test_coverage_review": {
          "title": "Test Coverage Review", 
          "description": "Ensure adequate test coverage for new/modified code",
          "type": "review",
          "specialist_type": "tester",
          "estimated_effort": "20 minutes"
        },
        "documentation_check": {
          "title": "Documentation Review",
          "description": "Verify documentation is updated and complete",
          "type": "review",
          "specialist_type": "documenter", 
          "estimated_effort": "10 minutes"
        }
      }
    }
  }
}"""

# Example: Bug Investigation Template  
BUG_INVESTIGATION_TEMPLATE = """// Bug Investigation Template
// Systematic approach to investigating and resolving bugs

{
  "metadata": {
    "name": "Bug Investigation Process",
    "version": "1.0.0",
    "description": "Structured workflow for investigating and fixing bugs",
    "author": "MCP Task Orchestrator", 
    "category": "debugging",
    "tags": ["bug", "investigation", "debugging", "resolution"]
  },
  
  "parameters": {
    "bug_id": {
      "type": "string",
      "description": "Bug tracking ID or reference",
      "required": true
    },
    "severity": {
      "type": "string",
      "description": "Bug severity level", 
      "required": true,
      "allowed_values": ["critical", "high", "medium", "low"]
    },
    "component": {
      "type": "string",
      "description": "Affected system component or module",
      "required": true,
      "min_length": 2,
      "max_length": 100
    },
    "reporter": {
      "type": "string",
      "description": "Person who reported the bug",
      "required": false,
      "default": "unknown"
    }
  },
  
  "tasks": {
    "bug_investigation": {
      "title": "Investigate Bug {{bug_id}}",
      "description": "{{severity}} severity bug in {{component}} reported by {{reporter}}",
      "type": "research",
      "specialist_type": "analyst",
      "estimated_effort": "4 hours",
      "children": {
        "reproduce_issue": {
          "title": "Reproduce the Issue",
          "description": "Create minimal reproduction case for bug {{bug_id}}",
          "type": "research", 
          "specialist_type": "tester",
          "estimated_effort": "1 hour"
        },
        "analyze_root_cause": {
          "title": "Root Cause Analysis",
          "description": "Identify the underlying cause of the bug",
          "type": "research",
          "specialist_type": "analyst", 
          "estimated_effort": "1.5 hours"
        },
        "design_fix": {
          "title": "Design Fix Strategy",
          "description": "Plan the approach to fix the bug without breaking other functionality",
          "type": "implementation",
          "specialist_type": "architect",
          "estimated_effort": "45 minutes"
        },
        "implement_fix": {
          "title": "Implement Bug Fix", 
          "description": "Code the solution for bug {{bug_id}}",
          "type": "implementation",
          "specialist_type": "coder",
          "estimated_effort": "2 hours"
        },
        "test_fix": {
          "title": "Test the Fix",
          "description": "Verify the fix resolves the issue and does not introduce regressions", 
          "type": "testing",
          "specialist_type": "tester",
          "estimated_effort": "1 hour"
        }
      }
    }
  }
}"""

# Example: Research Template with Inheritance
RESEARCH_BASE_TEMPLATE = """// Base Research Template
// Foundation template for research tasks

{
  "metadata": {
    "name": "Research Base Template",
    "version": "1.0.0",
    "description": "Base template for research and analysis tasks",
    "author": "MCP Task Orchestrator",
    "category": "research",
    "tags": ["research", "analysis", "base"]
  },
  
  "parameters": {
    "research_topic": {
      "type": "string",
      "description": "Main topic of research",
      "required": true,
      "min_length": 5,
      "max_length": 200
    },
    "deadline": {
      "type": "string", 
      "description": "Research deadline (YYYY-MM-DD)",
      "required": false,
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    }
  },
  
  "tasks": {
    "research_project": {
      "title": "Research: {{research_topic}}",
      "description": "Comprehensive research on {{research_topic}}",
      "type": "research",
      "specialist_type": "researcher",
      "estimated_effort": "8 hours",
      "children": {
        "literature_review": {
          "title": "Literature Review",
          "description": "Review existing literature and sources on {{research_topic}}",
          "type": "research",
          "specialist_type": "researcher", 
          "estimated_effort": "3 hours"
        },
        "data_collection": {
          "title": "Data Collection",
          "description": "Gather relevant data and evidence for {{research_topic}}",
          "type": "research",
          "specialist_type": "analyst",
          "estimated_effort": "2 hours"
        },
        "analysis": {
          "title": "Analysis and Synthesis",
          "description": "Analyze collected data and synthesize findings",
          "type": "research",
          "specialist_type": "analyst", 
          "estimated_effort": "2 hours"
        },
        "documentation": {
          "title": "Document Findings",
          "description": "Create comprehensive research documentation",
          "type": "documentation",
          "specialist_type": "documenter",
          "estimated_effort": "1 hour"
        }
      }
    }
  }
}"""

# Example: Extended Research Template (inherits from base)
MARKET_RESEARCH_TEMPLATE = """// Market Research Template
// Extends base research template for market analysis

{
  "metadata": {
    "name": "Market Research Analysis", 
    "version": "1.0.0",
    "description": "Comprehensive market research and competitive analysis",
    "author": "MCP Task Orchestrator",
    "category": "business",
    "tags": ["market", "research", "competitive-analysis", "business"],
    "extends": "research_base"
  },
  
  "parameters": {
    "market_segment": {
      "type": "string",
      "description": "Target market segment to analyze",
      "required": true,
      "min_length": 3,
      "max_length": 100
    },
    "geographic_scope": {
      "type": "string",
      "description": "Geographic scope of research",
      "required": true,
      "allowed_values": ["local", "regional", "national", "international", "global"]
    },
    "budget_range": {
      "type": "string",
      "description": "Budget range for research",
      "required": false,
      "allowed_values": ["under-1k", "1k-5k", "5k-10k", "10k-50k", "50k-plus"]
    }
  },
  
  "tasks": {
    "market_analysis": {
      "title": "Market Analysis for {{market_segment}}",
      "description": "{{geographic_scope}} market research focusing on {{market_segment}}",
      "type": "research",
      "specialist_type": "analyst",
      "estimated_effort": "12 hours",
      "children": {
        "competitor_analysis": {
          "title": "Competitive Analysis",
          "description": "Analyze competitors in the {{market_segment}} space",
          "type": "research",
          "specialist_type": "analyst",
          "estimated_effort": "3 hours"
        },
        "market_sizing": {
          "title": "Market Sizing", 
          "description": "Determine market size and growth potential for {{market_segment}}",
          "type": "research",
          "specialist_type": "analyst",
          "estimated_effort": "2 hours"
        },
        "customer_analysis": {
          "title": "Customer Analysis",
          "description": "Analyze target customer demographics and behavior",
          "type": "research",
          "specialist_type": "researcher",
          "estimated_effort": "3 hours"
        },
        "trend_analysis": {
          "title": "Trend Analysis",
          "description": "Identify market trends and future opportunities",
          "type": "research", 
          "specialist_type": "analyst",
          "estimated_effort": "2 hours"
        },
        "financial_analysis": {
          "title": "Financial Analysis",
          "description": "Analyze financial aspects and investment requirements",
          "type": "research",
          "specialist_type": "analyst",
          "estimated_effort": "2 hours"
        }
      }
    }
  }
}"""

EXAMPLE_TEMPLATES = {
    "basic_project_setup": BASIC_PROJECT_SETUP,
    "code_review_process": CODE_REVIEW_TEMPLATE,
    "bug_investigation": BUG_INVESTIGATION_TEMPLATE,
    "research_base": RESEARCH_BASE_TEMPLATE,
    "market_research": MARKET_RESEARCH_TEMPLATE
}


def get_example_template(template_name: str) -> str:
    """Get example template by name."""
    return EXAMPLE_TEMPLATES.get(template_name, "")


def get_all_example_templates() -> dict:
    """Get all example templates."""
    return EXAMPLE_TEMPLATES.copy()


def list_example_template_names() -> list:
    """Get list of available example template names."""
    return list(EXAMPLE_TEMPLATES.keys())