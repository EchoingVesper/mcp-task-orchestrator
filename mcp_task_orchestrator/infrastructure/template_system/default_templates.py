"""
Default Template Library

Comprehensive collection of templates for common workflows:
- Software development workflows
- Research and analysis processes  
- Creative and content workflows
- Task orchestrator self-development
- Business process templates
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


# Software Development Templates

SOFTWARE_PROJECT_SETUP = """
// Software Project Setup Template
// Complete template for initializing a new software project

{
  "metadata": {
    "name": "Software Project Setup",
    "version": "1.0.0",
    "description": "Comprehensive software project initialization with modern tooling",
    "category": "development",
    "tags": ["project-setup", "initialization", "development", "tooling"],
    "author": "Task Orchestrator",
    "complexity": "moderate",
    "estimated_duration": "4-6 hours"
  },
  
  "parameters": {
    "project_name": {
      "type": "string",
      "description": "Name of the software project",
      "required": true,
      "min_length": 3,
      "max_length": 50,
      "pattern": "^[a-zA-Z][a-zA-Z0-9_-]*$"
    },
    "language": {
      "type": "string",
      "description": "Primary programming language",
      "required": true,
      "enum": ["python", "javascript", "typescript", "java", "rust", "go", "csharp"]
    },
    "framework": {
      "type": "string", 
      "description": "Framework or runtime (if applicable)",
      "required": false
    },
    "repository_url": {
      "type": "string",
      "description": "Git repository URL",
      "required": false
    },
    "target_platform": {
      "type": "string",
      "description": "Target deployment platform",
      "required": false,
      "enum": ["web", "mobile", "desktop", "server", "cloud", "embedded"]
    },
    "team_size": {
      "type": "number",
      "description": "Expected team size",
      "required": false,
      "min": 1,
      "max": 20,
      "default": 3
    }
  },
  
  "tasks": {
    "project_initialization": {
      "title": "Initialize {{project_name}} Project Structure",
      "description": "Set up basic project structure, configuration files, and initial directories for {{language}} project",
      "type": "implementation",
      "specialist_type": "architect",
      "complexity": "simple",
      "estimated_effort": "30 minutes",
      "dependencies": [],
      "checklist": [
        "Create project directory structure",
        "Initialize version control repository",
        "Set up language-specific configuration files",
        "Create initial README.md with project overview",
        "Set up gitignore for {{language}}"
      ]
    },
    
    "dependency_management": {
      "title": "Set Up Dependency Management",
      "description": "Configure package management and initial dependencies for {{project_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "simple",
      "estimated_effort": "45 minutes",
      "dependencies": ["project_initialization"],
      "checklist": [
        "Initialize package manager (pip, npm, cargo, etc.)",
        "Configure dependency versions and constraints",
        "Set up development dependencies",
        "Create lockfile for reproducible builds",
        "Document dependency management process"
      ]
    },
    
    "development_environment": {
      "title": "Configure Development Environment",
      "description": "Set up development tools, linting, formatting, and IDE configuration",
      "type": "implementation", 
      "specialist_type": "devops",
      "complexity": "moderate",
      "estimated_effort": "1 hour",
      "dependencies": ["dependency_management"],
      "checklist": [
        "Configure code formatter (black, prettier, rustfmt, etc.)",
        "Set up linter with project-specific rules",
        "Configure IDE/editor settings and extensions",
        "Set up pre-commit hooks",
        "Create development workflow documentation"
      ]
    },
    
    "testing_framework": {
      "title": "Implement Testing Framework",
      "description": "Set up comprehensive testing infrastructure for {{project_name}}",
      "type": "implementation",
      "specialist_type": "tester",
      "complexity": "moderate", 
      "estimated_effort": "1.5 hours",
      "dependencies": ["development_environment"],
      "checklist": [
        "Choose and configure testing framework",
        "Set up unit test structure and examples",
        "Configure integration test environment",
        "Set up test coverage reporting",
        "Create test data management strategy",
        "Document testing guidelines and best practices"
      ]
    },
    
    "ci_cd_pipeline": {
      "title": "Configure CI/CD Pipeline",
      "description": "Set up automated build, test, and deployment pipeline",
      "type": "implementation",
      "specialist_type": "devops",
      "complexity": "complex",
      "estimated_effort": "2 hours",
      "dependencies": ["testing_framework"],
      "checklist": [
        "Configure CI service (GitHub Actions, GitLab CI, etc.)",
        "Set up automated testing on pull requests",
        "Configure build and artifact generation",
        "Set up deployment automation",
        "Configure security scanning and dependency checks",
        "Set up monitoring and alerting"
      ]
    },
    
    "documentation_setup": {
      "title": "Create Project Documentation",
      "description": "Set up comprehensive project documentation and contribution guidelines",
      "type": "documentation",
      "specialist_type": "documenter",
      "complexity": "moderate",
      "estimated_effort": "1 hour",
      "dependencies": ["project_initialization"],
      "checklist": [
        "Create detailed README with setup instructions",
        "Write CONTRIBUTING.md with development guidelines",
        "Set up API documentation framework",
        "Create CODE_OF_CONDUCT.md",
        "Write basic user documentation",
        "Set up changelog management"
      ]
    }
  },
  
  "milestones": {
    "foundation_complete": {
      "title": "Project Foundation Complete",
      "description": "Basic project structure and tooling is ready for development",
      "required_tasks": ["project_initialization", "dependency_management", "development_environment"],
      "deliverables": ["Working development environment", "Basic project structure", "Development tooling configured"]
    },
    "production_ready": {
      "title": "Production Ready Setup",
      "description": "Project is ready for team development and deployment",
      "required_tasks": ["testing_framework", "ci_cd_pipeline", "documentation_setup"],
      "deliverables": ["Complete CI/CD pipeline", "Testing infrastructure", "Comprehensive documentation"]
    }
  },
  
  "outputs": {
    "project_structure": "Complete project directory structure with all configuration files",
    "development_guide": "Comprehensive guide for team members to start development",
    "deployment_pipeline": "Automated CI/CD pipeline for continuous integration and deployment"
  }
}
"""

FEATURE_DEVELOPMENT_WORKFLOW = """
// Feature Development Workflow Template
// Structured approach to developing new features

{
  "metadata": {
    "name": "Feature Development Workflow",
    "version": "1.0.0",
    "description": "End-to-end workflow for developing and deploying new features",
    "category": "development",
    "tags": ["feature", "development", "workflow", "agile"],
    "author": "Task Orchestrator",
    "complexity": "moderate",
    "estimated_duration": "1-3 weeks"
  },
  
  "parameters": {
    "feature_name": {
      "type": "string",
      "description": "Name of the feature to develop",
      "required": true,
      "min_length": 3,
      "max_length": 100
    },
    "feature_description": {
      "type": "string",
      "description": "Detailed description of the feature",
      "required": true,
      "min_length": 20,
      "max_length": 1000
    },
    "priority": {
      "type": "string",
      "description": "Feature priority level",
      "required": true,
      "enum": ["low", "medium", "high", "critical"]
    },
    "target_users": {
      "type": "string",
      "description": "Target user group for this feature",
      "required": false
    },
    "estimated_complexity": {
      "type": "string",
      "description": "Development complexity estimate",
      "required": false,
      "enum": ["simple", "moderate", "complex", "very_complex"],
      "default": "moderate"
    }
  },
  
  "tasks": {
    "requirements_analysis": {
      "title": "Analyze Requirements for {{feature_name}}",
      "description": "Gather and analyze detailed requirements for {{feature_name}} feature",
      "type": "research",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "4-8 hours",
      "checklist": [
        "Define user stories and acceptance criteria",
        "Identify functional requirements",
        "Identify non-functional requirements",
        "Analyze dependencies and constraints",
        "Create user journey mapping",
        "Document edge cases and error scenarios"
      ]
    },
    
    "technical_design": {
      "title": "Design Technical Architecture",
      "description": "Create technical design and architecture for {{feature_name}}",
      "type": "design",
      "specialist_type": "architect",
      "complexity": "complex",
      "estimated_effort": "8-12 hours",
      "dependencies": ["requirements_analysis"],
      "checklist": [
        "Design system architecture and components",
        "Define API contracts and data models",
        "Plan database schema changes",
        "Identify integration points",
        "Design error handling and recovery",
        "Create security considerations document"
      ]
    },
    
    "implementation_planning": {
      "title": "Plan Implementation Strategy",
      "description": "Break down implementation into manageable tasks and sprints",
      "type": "planning",
      "specialist_type": "coordinator",
      "complexity": "moderate",
      "estimated_effort": "2-4 hours",
      "dependencies": ["technical_design"],
      "checklist": [
        "Break feature into development tasks",
        "Estimate effort for each task",
        "Plan implementation phases",
        "Identify critical path and dependencies",
        "Assign tasks to team members",
        "Set up project tracking and milestones"
      ]
    },
    
    "core_implementation": {
      "title": "Implement Core {{feature_name}} Functionality",
      "description": "Develop the main functionality of {{feature_name}} feature",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "{{estimated_complexity}}",
      "estimated_effort": "1-2 weeks",
      "dependencies": ["implementation_planning"],
      "checklist": [
        "Implement core business logic",
        "Create API endpoints and handlers",
        "Implement data access layer",
        "Add input validation and sanitization",
        "Implement error handling",
        "Add logging and monitoring"
      ]
    },
    
    "user_interface": {
      "title": "Develop User Interface",
      "description": "Create user interface components for {{feature_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "moderate",
      "estimated_effort": "3-5 days",
      "dependencies": ["core_implementation"],
      "checklist": [
        "Design UI/UX wireframes",
        "Implement frontend components",
        "Add responsive design support",
        "Implement client-side validation",
        "Add accessibility features",
        "Test across different browsers/devices"
      ]
    },
    
    "testing_implementation": {
      "title": "Implement Comprehensive Testing",
      "description": "Create thorough test suite for {{feature_name}}",
      "type": "testing",
      "specialist_type": "tester",
      "complexity": "moderate",
      "estimated_effort": "4-6 days",
      "dependencies": ["user_interface"],
      "checklist": [
        "Write unit tests for core logic",
        "Create integration tests",
        "Implement end-to-end tests",
        "Add performance tests",
        "Create test data and fixtures",
        "Set up automated test execution"
      ]
    },
    
    "documentation": {
      "title": "Create Feature Documentation",
      "description": "Document {{feature_name}} for users and developers",
      "type": "documentation",
      "specialist_type": "documenter",
      "complexity": "simple",
      "estimated_effort": "1-2 days",
      "dependencies": ["testing_implementation"],
      "checklist": [
        "Write user documentation and guides",
        "Create API documentation",
        "Document configuration options",
        "Create troubleshooting guide",
        "Update system documentation",
        "Create video tutorials or demos"
      ]
    },
    
    "deployment_preparation": {
      "title": "Prepare for Deployment",
      "description": "Prepare {{feature_name}} for production deployment",
      "type": "deployment",
      "specialist_type": "devops",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "dependencies": ["documentation"],
      "checklist": [
        "Configure feature flags and toggles",
        "Set up monitoring and alerting",
        "Prepare rollback procedures",
        "Configure security settings",
        "Set up performance monitoring",
        "Create deployment checklist"
      ]
    }
  },
  
  "milestones": {
    "design_complete": {
      "title": "Design Phase Complete",
      "description": "Requirements and technical design are finalized",
      "required_tasks": ["requirements_analysis", "technical_design", "implementation_planning"]
    },
    "development_complete": {
      "title": "Development Phase Complete", 
      "description": "Feature implementation and testing are complete",
      "required_tasks": ["core_implementation", "user_interface", "testing_implementation"]
    },
    "ready_for_deployment": {
      "title": "Ready for Production Deployment",
      "description": "Feature is fully ready for production release",
      "required_tasks": ["documentation", "deployment_preparation"]
    }
  }
}
"""

# Research and Analysis Templates

MARKET_RESEARCH_TEMPLATE = """
// Market Research Template
// Comprehensive market analysis and competitive research

{
  "metadata": {
    "name": "Market Research Analysis",
    "version": "1.0.0", 
    "description": "Systematic approach to market research and competitive analysis",
    "category": "research",
    "tags": ["market-research", "competitive-analysis", "business-intelligence"],
    "author": "Task Orchestrator",
    "complexity": "moderate",
    "estimated_duration": "2-4 weeks"
  },
  
  "parameters": {
    "market_segment": {
      "type": "string",
      "description": "Target market segment or industry",
      "required": true,
      "min_length": 3,
      "max_length": 100
    },
    "geographic_scope": {
      "type": "string",
      "description": "Geographic scope of research",
      "required": true,
      "enum": ["local", "regional", "national", "international", "global"]
    },
    "research_objectives": {
      "type": "array",
      "description": "Primary research objectives",
      "required": true,
      "items": {"type": "string"}
    },
    "budget_range": {
      "type": "string",
      "description": "Research budget range",
      "required": false,
      "enum": ["low", "medium", "high", "enterprise"]
    },
    "timeline_weeks": {
      "type": "number",
      "description": "Research timeline in weeks",
      "required": false,
      "min": 1,
      "max": 52,
      "default": 4
    }
  },
  
  "tasks": {
    "market_definition": {
      "title": "Define Market Scope and Boundaries",
      "description": "Clearly define the {{market_segment}} market scope and research boundaries",
      "type": "research",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "checklist": [
        "Define target market segments",
        "Identify market boundaries and scope",
        "Define key research questions",
        "Set success metrics and KPIs",
        "Identify stakeholders and decision makers"
      ]
    },
    
    "secondary_research": {
      "title": "Conduct Secondary Market Research",
      "description": "Gather existing market data and industry reports for {{market_segment}}",
      "type": "research",
      "specialist_type": "researcher",
      "complexity": "moderate",
      "estimated_effort": "3-5 days",
      "dependencies": ["market_definition"],
      "checklist": [
        "Collect industry reports and market studies", 
        "Analyze government and regulatory data",
        "Review academic research and publications",
        "Gather demographic and psychographic data",
        "Compile economic indicators and trends",
        "Document data sources and reliability"
      ]
    },
    
    "competitive_analysis": {
      "title": "Analyze Competitive Landscape",
      "description": "Comprehensive analysis of competitors in {{market_segment}}",
      "type": "research", 
      "specialist_type": "analyst",
      "complexity": "complex",
      "estimated_effort": "1 week",
      "dependencies": ["secondary_research"],
      "checklist": [
        "Identify direct and indirect competitors",
        "Analyze competitor products and services",
        "Research competitor pricing strategies",
        "Evaluate competitor marketing approaches",
        "Assess competitor strengths and weaknesses",
        "Map competitor market positioning"
      ]
    },
    
    "primary_research_design": {
      "title": "Design Primary Research Methodology",
      "description": "Design surveys, interviews, and other primary research methods",
      "type": "planning",
      "specialist_type": "researcher",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["competitive_analysis"],
      "checklist": [
        "Design survey questionnaires",
        "Plan interview guides and protocols",
        "Define target participant criteria",
        "Calculate required sample sizes",
        "Plan data collection methods",
        "Set up research ethics and privacy protocols"
      ]
    },
    
    "primary_data_collection": {
      "title": "Collect Primary Market Data",
      "description": "Execute primary research plan to gather firsthand market insights",
      "type": "research",
      "specialist_type": "researcher", 
      "complexity": "complex",
      "estimated_effort": "1-2 weeks",
      "dependencies": ["primary_research_design"],
      "checklist": [
        "Conduct customer surveys and interviews",
        "Perform focus groups or user sessions",
        "Gather expert interviews and opinions",
        "Collect observational and behavioral data",
        "Document research process and challenges",
        "Ensure data quality and completeness"
      ]
    },
    
    "data_analysis": {
      "title": "Analyze and Synthesize Research Data",
      "description": "Comprehensive analysis of all collected market research data",
      "type": "research",
      "specialist_type": "analyst",
      "complexity": "complex",
      "estimated_effort": "1 week",
      "dependencies": ["primary_data_collection"],
      "checklist": [
        "Clean and validate research data",
        "Perform statistical analysis",
        "Identify patterns and trends",
        "Cross-reference primary and secondary data",
        "Generate insights and implications",
        "Validate findings with additional sources"
      ]
    },
    
    "report_creation": {
      "title": "Create Market Research Report",
      "description": "Compile comprehensive market research report with findings and recommendations",
      "type": "documentation",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "3-5 days",
      "dependencies": ["data_analysis"],
      "checklist": [
        "Write executive summary",
        "Document methodology and limitations",
        "Present key findings and insights",
        "Provide actionable recommendations",
        "Create data visualizations and charts",
        "Include appendices with detailed data"
      ]
    }
  },
  
  "milestones": {
    "research_design_complete": {
      "title": "Research Design Finalized",
      "description": "Market scope defined and research methodology established",
      "required_tasks": ["market_definition", "secondary_research", "primary_research_design"]
    },
    "data_collection_complete": {
      "title": "Data Collection Finished",
      "description": "All primary and secondary research data collected",
      "required_tasks": ["competitive_analysis", "primary_data_collection"]
    },
    "final_report_ready": {
      "title": "Final Report Delivered",
      "description": "Complete market research report with actionable insights",
      "required_tasks": ["data_analysis", "report_creation"]
    }
  }
}
"""

# Task Orchestrator Self-Development Templates

ORCHESTRATOR_FEATURE_DEVELOPMENT = """
// Task Orchestrator Feature Development Template
// Specialized template for developing new orchestrator features

{
  "metadata": {
    "name": "Orchestrator Feature Development",
    "version": "1.0.0",
    "description": "Template for developing new features in the Task Orchestrator system",
    "category": "self-development",
    "tags": ["orchestrator", "feature", "development", "clean-architecture"],
    "author": "Task Orchestrator",
    "complexity": "complex",
    "estimated_duration": "1-4 weeks"
  },
  
  "parameters": {
    "feature_name": {
      "type": "string", 
      "description": "Name of the orchestrator feature",
      "required": true,
      "min_length": 3,
      "max_length": 100
    },
    "feature_type": {
      "type": "string",
      "description": "Type of feature being developed",
      "required": true,
      "enum": ["domain-entity", "use-case", "infrastructure", "mcp-tool", "integration", "optimization"]
    },
    "architecture_layer": {
      "type": "string",
      "description": "Primary architecture layer for this feature",
      "required": true, 
      "enum": ["domain", "application", "infrastructure", "presentation"]
    },
    "breaking_change": {
      "type": "boolean",
      "description": "Whether this feature introduces breaking changes",
      "required": false,
      "default": false
    }
  },
  
  "tasks": {
    "architecture_analysis": {
      "title": "Analyze Clean Architecture Impact",
      "description": "Analyze how {{feature_name}} fits into the clean architecture design",
      "type": "design",
      "specialist_type": "architect",
      "complexity": "complex",
      "estimated_effort": "4-8 hours",
      "checklist": [
        "Review current architecture and identify integration points",
        "Design domain entities and value objects",
        "Define use cases and business logic",
        "Plan infrastructure implementations",
        "Identify dependency injection requirements",
        "Design interface contracts and abstractions"
      ]
    },
    
    "domain_implementation": {
      "title": "Implement Domain Layer Components",
      "description": "Implement domain entities, value objects, and business logic for {{feature_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "complex",
      "estimated_effort": "1-2 weeks",
      "dependencies": ["architecture_analysis"],
      "checklist": [
        "Create domain entities with business invariants",
        "Implement value objects and domain services",
        "Define repository interfaces",
        "Implement domain exceptions with recovery strategies",
        "Add domain events for integration",
        "Create domain validation logic"
      ]
    },
    
    "application_layer": {
      "title": "Implement Application Use Cases",
      "description": "Create application layer use cases and DTOs for {{feature_name}}",
      "type": "implementation",
      "specialist_type": "coder", 
      "complexity": "moderate",
      "estimated_effort": "3-5 days",
      "dependencies": ["domain_implementation"],
      "checklist": [
        "Implement use case classes with business workflows",
        "Create request/response DTOs",
        "Add application service interfaces",
        "Implement cross-cutting concerns (logging, validation)",
        "Add error handling and transaction management",
        "Create integration event publishers"
      ]
    },
    
    "infrastructure_implementation": {
      "title": "Implement Infrastructure Layer",
      "description": "Create infrastructure implementations for {{feature_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "complex", 
      "estimated_effort": "1 week",
      "dependencies": ["application_layer"],
      "checklist": [
        "Implement repository patterns with SQLite",
        "Create database migrations and schema updates",
        "Add configuration management", 
        "Implement external service adapters",
        "Add monitoring and health checks",
        "Create dependency injection bindings"
      ]
    },
    
    "mcp_integration": {
      "title": "Create MCP Tool Integration",
      "description": "Implement MCP tools and server integration for {{feature_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["infrastructure_implementation"],
      "checklist": [
        "Design MCP tool interfaces and schemas",
        "Implement MCP request handlers",
        "Add error handling and validation",
        "Create tool documentation and examples",
        "Integrate with existing MCP server",
        "Add security controls and rate limiting"
      ]
    },
    
    "testing_suite": {
      "title": "Implement Comprehensive Test Suite",
      "description": "Create thorough tests for all layers of {{feature_name}}",
      "type": "testing",
      "specialist_type": "tester",
      "complexity": "complex",
      "estimated_effort": "1 week",
      "dependencies": ["mcp_integration"],
      "checklist": [
        "Write unit tests for domain logic",
        "Create application layer integration tests",
        "Implement infrastructure tests with test doubles",
        "Add MCP tool integration tests",
        "Create end-to-end workflow tests",
        "Add performance and load tests"
      ]
    },
    
    "documentation_update": {
      "title": "Update System Documentation",
      "description": "Update architecture and user documentation for {{feature_name}}",
      "type": "documentation",
      "specialist_type": "documenter",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["testing_suite"],
      "checklist": [
        "Update CLAUDE.md with new features",
        "Document MCP tool usage and examples",
        "Update architecture documentation",
        "Create migration guides if needed",
        "Update API reference documentation",
        "Create user guides and tutorials"
      ]
    }
  },
  
  "milestones": {
    "architecture_complete": {
      "title": "Architecture Design Complete",
      "description": "Clean architecture design finalized and domain layer implemented",
      "required_tasks": ["architecture_analysis", "domain_implementation"]
    },
    "core_implementation_complete": {
      "title": "Core Implementation Complete", 
      "description": "Application and infrastructure layers fully implemented",
      "required_tasks": ["application_layer", "infrastructure_implementation"]
    },
    "feature_ready": {
      "title": "Feature Ready for Production",
      "description": "Feature is fully tested, documented, and ready for deployment",
      "required_tasks": ["mcp_integration", "testing_suite", "documentation_update"]
    }
  }
}
"""


def get_all_default_templates() -> Dict[str, str]:
    """Get all default templates as a dictionary."""
    return {
        "software_project_setup": SOFTWARE_PROJECT_SETUP,
        "feature_development_workflow": FEATURE_DEVELOPMENT_WORKFLOW,
        "market_research_analysis": MARKET_RESEARCH_TEMPLATE,
        "orchestrator_feature_development": ORCHESTRATOR_FEATURE_DEVELOPMENT
    }


def get_template_categories() -> Dict[str, List[str]]:
    """Get templates organized by category."""
    return {
        "development": [
            "software_project_setup",
            "feature_development_workflow"
        ],
        "research": [
            "market_research_analysis"
        ],
        "self_development": [
            "orchestrator_feature_development"
        ]
    }


def get_template_metadata(template_id: str) -> Dict[str, Any]:
    """Get metadata for a specific template."""
    templates = get_all_default_templates()
    if template_id not in templates:
        return {}
    
    # Parse the JSON5 content to extract metadata
    # This is a simplified extraction - in practice, you'd use the JSON5 parser
    template_content = templates[template_id]
    
    # Extract basic metadata (simplified)
    metadata = {}
    if "metadata" in template_content:
        # This would use the actual JSON5 parser in practice
        pass
    
    return metadata