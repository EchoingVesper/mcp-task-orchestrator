# Common Workflow Patterns

*Proven templates for different types of projects*

## Development Project Patterns

### Pattern 1: Full-Stack Web Application

**Use Case**: Building complete web applications with frontend, backend, and database components.

**Template Structure:**
```python
# Initialize with comprehensive scope
initialization_command = """
Initialize orchestration and plan a full-stack web application:
- Frontend: [React/Vue/Angular] with responsive design
- Backend: [Node.js/Python/Java] REST API
- Database: [PostgreSQL/MongoDB] with proper schema
- Authentication: User management and security
- Testing: Unit, integration, and e2e testing
- Deployment: CI/CD pipeline and hosting setup
"""

# Expected task breakdown (8-12 subtasks)
typical_breakdown = [
    "architect: System architecture and technology stack decisions",
    "architect: Database schema design and API specification", 
    "implementer: Backend API development with authentication",
    "implementer: Frontend application with routing and state management",
    "implementer: Database integration and data layer",
    "implementer: User interface components and styling",
    "tester: Backend API testing and validation",
    "tester: Frontend testing and user experience validation",
    "implementer: CI/CD pipeline and deployment automation",
    "documenter: API documentation and deployment guide"
]
```

**Execution Pattern with Maintenance:**
```python
# Phase 1: Architecture and Planning (Days 1-2)
architecture_phase = [
    "Execute architect subtask for system design",
    "Execute architect subtask for database and API design",
    "Run maintenance scan after architecture phase completion"
]

# Phase 2: Backend Development (Days 3-5)
backend_phase = [
    "Execute implementer subtask for API development",
    "Execute implementer subtask for database integration",
    "Execute tester subtask for backend testing",
    "Run comprehensive maintenance scan after backend completion"
]

# Phase 3: Frontend Development (Days 6-8)
frontend_phase = [
    "Execute implementer subtask for frontend application",
    "Execute implementer subtask for UI components",
    "Execute tester subtask for frontend testing",
    "Run maintenance validation before integration"
]

# Phase 4: Integration and Deployment (Days 9-10)
integration_phase = [
    "Execute implementer subtask for CI/CD setup",
    "Execute documenter subtask for documentation",
    "Synthesize complete application",
    "Run final maintenance and prepare handover"
]
```

**Maintenance Schedule:**
```python
fullstack_maintenance = {
    "daily": "Basic cleanup after each major component",
    "phase_end": "Comprehensive scan before moving to next phase",
    "weekly": "Full project health check and optimization",
    "completion": "Archive workflow and prepare deployment handover"
}
```

### Pattern 2: API Development and Documentation

**Use Case**: Building RESTful APIs with comprehensive documentation and testing.

**Template:**
```python
api_project_template = """
Initialize orchestration and plan REST API development:
- API design: OpenAPI specification and endpoint planning
- Implementation: [Framework] with middleware and validation
- Database: Schema design and ORM integration
- Security: Authentication, authorization, and rate limiting
- Testing: Unit tests, integration tests, and load testing
- Documentation: Interactive API docs and usage guides
- Deployment: Containerization and cloud deployment
"""

# Specialized task breakdown
api_breakdown = [
    "architect: API design and OpenAPI specification",
    "architect: Database schema and data modeling",
    "implementer: Core API endpoints and business logic", 
    "implementer: Authentication and security middleware",
    "implementer: Database integration and ORM setup",
    "tester: Comprehensive API testing suite",
    "tester: Performance and load testing",
    "documenter: Interactive API documentation",
    "implementer: Containerization and deployment setup"
]
```

**API-Specific Workflow:**
```python
# Design-first approach
api_workflow = [
    # Phase 1: Design (20% of time)
    "Focus on architecture tasks first",
    "Create comprehensive API specification", 
    "Design database schema with relationships",
    "Run validation before implementation starts",
    
    # Phase 2: Core Implementation (40% of time) 
    "Implement core endpoints with business logic",
    "Add authentication and security layers",
    "Integrate database with proper error handling",
    "Continuous testing during implementation",
    
    # Phase 3: Testing and Documentation (25% of time)
    "Comprehensive test suite with edge cases",
    "Performance testing and optimization",
    "Interactive documentation with examples",
    
    # Phase 4: Deployment (15% of time)
    "Containerization and cloud setup",
    "CI/CD pipeline with automated testing",
    "Monitoring and logging implementation"
]
```

### Pattern 3: Data Processing Pipeline

**Use Case**: ETL pipelines, data analysis, and automated reporting systems.

**Template:**
```python
data_pipeline_template = """
Initialize orchestration and plan data processing pipeline:
- Data sources: API integration, file processing, database connections
- Extraction: Robust data collection with error handling
- Transformation: Data cleaning, validation, and enrichment
- Loading: Data warehouse integration and optimization
- Monitoring: Pipeline health, error tracking, and alerting
- Reporting: Automated report generation and distribution
- Scheduling: Cron jobs and workflow orchestration
"""

# Data-focused task breakdown
data_breakdown = [
    "architect: Data pipeline architecture and flow design",
    "architect: Data warehouse schema and optimization strategy",
    "implementer: Data extraction modules with error handling",
    "implementer: Data transformation and validation logic",
    "implementer: Data loading and warehouse integration",
    "implementer: Pipeline monitoring and alerting system",
    "tester: Data validation and pipeline testing",
    "documenter: Operations guide and troubleshooting manual"
]
```

**Data Pipeline Execution:**
```python
# Data pipeline workflow with validation points
pipeline_execution = [
    # Phase 1: Architecture (15% of time)
    "Design end-to-end data flow",
    "Plan data warehouse schema",
    "Run architecture validation",
    
    # Phase 2: Extraction (25% of time)
    "Build robust data extraction modules",
    "Implement error handling and retry logic",
    "Test with real data sources",
    "Validate extraction accuracy",
    
    # Phase 3: Transformation (35% of time) 
    "Implement data cleaning and validation",
    "Add data enrichment and business logic",
    "Optimize transformation performance",
    "Test with edge cases and bad data",
    
    # Phase 4: Loading and Monitoring (25% of time)
    "Implement efficient data loading",
    "Add monitoring and alerting",
    "Create operational documentation",
    "Run full pipeline testing"
]

# Pipeline-specific maintenance
pipeline_maintenance = {
    "after_extraction": "Validate data quality and source connections",
    "after_transformation": "Check performance and optimization",
    "after_loading": "Verify warehouse integration and monitoring",
    "weekly": "Full pipeline health check and optimization"
}
```

---

## Documentation Project Patterns

### Pattern 4: Comprehensive Documentation Overhaul

**Use Case**: Creating or updating documentation for existing systems.

**Template:**
```python
documentation_project = """
Initialize orchestration and plan documentation overhaul:
- Content audit: Analyze existing documentation and identify gaps
- Information architecture: Organize content structure and navigation
- User guides: Create tutorials and getting-started materials
- API documentation: Generate reference docs and interactive examples
- Visual assets: Diagrams, flowcharts, and screenshots
- Search and navigation: Implement content discovery features
- Maintenance: Establish update processes and automation
"""

# Documentation-focused breakdown
docs_breakdown = [
    "researcher: Content audit and gap analysis",
    "architect: Information architecture and site structure",
    "documenter: User guide creation and tutorial development",
    "documenter: API reference documentation",
    "implementer: Interactive examples and code samples",
    "implementer: Documentation site setup and navigation",
    "reviewer: Content quality review and consistency check"
]
```

**Documentation Workflow:**
```python
# Content-first approach
docs_workflow = [
    # Phase 1: Research and Planning (20%)
    "Analyze existing content and user needs",
    "Design information architecture",
    "Plan content creation strategy",
    
    # Phase 2: Content Creation (50%)
    "Write user guides and tutorials",
    "Create API reference documentation", 
    "Develop interactive examples",
    "Design visual assets and diagrams",
    
    # Phase 3: Implementation (20%)
    "Build documentation site",
    "Implement search and navigation",
    "Set up content management system",
    
    # Phase 4: Review and Launch (10%)
    "Quality review and editing",
    "User testing and feedback",
    "Launch and maintenance setup"
]
```

### Pattern 5: Migration Documentation

**Use Case**: Documenting system migrations, upgrades, or transitions.

**Template:**
```python
migration_docs_template = """
Initialize orchestration and plan migration documentation:
- Current state analysis: Document existing system architecture
- Migration strategy: Plan transition approach and timeline
- Step-by-step guides: Create detailed migration procedures
- Risk assessment: Document potential issues and mitigation
- Testing procedures: Create validation and rollback plans
- Communication materials: User notifications and training
- Post-migration support: Troubleshooting and maintenance guides
"""
```

---

## DevOps and Infrastructure Patterns

### Pattern 6: CI/CD Pipeline Implementation

**Use Case**: Setting up automated testing, building, and deployment.

**Template:**
```python
cicd_pipeline_template = """
Initialize orchestration and plan CI/CD pipeline implementation:
- Repository setup: Branch strategy and workflow configuration
- Automated testing: Unit, integration, and deployment testing
- Build automation: Code compilation and artifact creation
- Deployment automation: Staging and production deployment
- Monitoring integration: Health checks and performance tracking
- Security scanning: Vulnerability assessment and compliance
- Documentation: Operations runbooks and troubleshooting guides
"""

# DevOps-focused breakdown
cicd_breakdown = [
    "architect: CI/CD pipeline design and tool selection",
    "implementer: Repository and branch workflow setup",
    "implementer: Automated testing pipeline configuration",
    "implementer: Build and artifact management automation",
    "implementer: Deployment automation and environment management",
    "implementer: Monitoring and alerting integration",
    "tester: Pipeline testing and validation procedures",
    "documenter: Operations documentation and runbooks"
]
```

**CI/CD Execution Pattern:**
```python
# Infrastructure-as-code approach
cicd_execution = [
    # Phase 1: Planning and Design (15%)
    "Design pipeline architecture",
    "Select tools and integration points",
    "Plan security and compliance measures",
    
    # Phase 2: Core Pipeline (40%)
    "Implement automated testing",
    "Set up build automation",
    "Configure deployment processes",
    
    # Phase 3: Integration and Security (30%)
    "Add monitoring and alerting",
    "Implement security scanning",
    "Set up environment management",
    
    # Phase 4: Documentation and Training (15%)
    "Create operations runbooks",
    "Document troubleshooting procedures",
    "Train team on new processes"
]
```

### Pattern 7: Infrastructure Modernization

**Use Case**: Migrating legacy infrastructure to modern platforms.

**Template:**
```python
infrastructure_modernization = """
Initialize orchestration and plan infrastructure modernization:
- Current state assessment: Inventory existing infrastructure
- Target architecture design: Plan modern infrastructure setup
- Migration strategy: Phased approach with minimal downtime
- Containerization: Application containerization and orchestration
- Cloud migration: Cloud platform setup and configuration
- Security enhancement: Modern security practices and compliance
- Monitoring and observability: Comprehensive system monitoring
- Documentation and training: Knowledge transfer and procedures
"""
```

---

## Research and Analysis Patterns

### Pattern 8: Technology Evaluation and Selection

**Use Case**: Researching and selecting technologies for new projects.

**Template:**
```python
tech_evaluation_template = """
Initialize orchestration and plan technology evaluation:
- Requirements analysis: Define technical and business requirements
- Market research: Survey available technologies and solutions
- Proof of concept: Build prototypes with candidate technologies
- Performance testing: Benchmark and compare alternatives
- Risk assessment: Evaluate adoption risks and mitigation strategies
- Cost analysis: Calculate total cost of ownership and ROI
- Recommendation report: Provide decision framework and guidance
"""

# Research-focused breakdown
research_breakdown = [
    "researcher: Requirements gathering and analysis",
    "researcher: Market research and technology survey",
    "architect: Evaluation criteria and testing framework",
    "implementer: Proof of concept development",
    "tester: Performance testing and benchmarking",
    "researcher: Risk assessment and cost analysis",
    "documenter: Recommendation report and decision framework"
]
```

### Pattern 9: Competitive Analysis

**Use Case**: Analyzing competitors and market positioning.

**Template:**
```python
competitive_analysis_template = """
Initialize orchestration and plan competitive analysis:
- Market landscape: Identify key competitors and market segments
- Feature comparison: Analyze competing products and capabilities
- Pricing analysis: Compare pricing models and value propositions
- User experience evaluation: Assess competitor UX and design
- Technology assessment: Evaluate competitor technology stacks
- Market positioning: Analyze messaging and brand positioning
- Opportunity identification: Find market gaps and opportunities
"""
```

---

## Advanced Project Patterns

### Pattern 10: Multi-Phase Enterprise Project

**Use Case**: Large-scale projects spanning multiple months with multiple teams.

**Template Structure:**
```python
enterprise_project_template = """
Initialize orchestration and plan enterprise-scale project:
- Phase 1: Discovery and planning (Month 1)
- Phase 2: Foundation and architecture (Months 2-3)
- Phase 3: Core implementation (Months 4-6)
- Phase 4: Integration and testing (Months 7-8)
- Phase 5: Deployment and launch (Month 9)
- Phase 6: Post-launch optimization (Month 10+)
"""

# Enterprise workflow management
enterprise_workflow = [
    # Monthly planning cycles
    "Plan each phase as separate orchestration workflow",
    "Use comprehensive handovers between phases",
    "Maintain artifact organization across phases",
    "Regular architecture reviews and validation",
    
    # Cross-phase coordination
    "Establish consistent naming conventions",
    "Use shared artifact repositories",
    "Maintain project-wide documentation",
    "Regular system health checks and optimization"
]

# Enterprise maintenance schedule
enterprise_maintenance = {
    "daily": "Basic cleanup within active phase",
    "weekly": "Comprehensive phase health check",
    "monthly": "Cross-phase validation and optimization",
    "phase_transition": "Complete handover and archive preparation",
    "quarterly": "Full project audit and performance review"
}
```

### Pattern 11: Open Source Project Development

**Use Case**: Developing open source projects with community considerations.

**Template:**
```python
opensource_template = """
Initialize orchestration and plan open source project:
- Project foundation: Repository setup and community guidelines
- Core functionality: Implement essential features and APIs
- Documentation: Comprehensive docs for contributors and users
- Testing and quality: Automated testing and code quality tools
- Community building: Contribution guidelines and issue templates
- Release management: Versioning, packaging, and distribution
- Governance: Maintainer guidelines and decision processes
"""

# Community-focused breakdown
opensource_breakdown = [
    "architect: Project architecture and contribution framework",
    "implementer: Core functionality and API development",
    "documenter: User documentation and contributor guides",
    "documenter: Code documentation and API references",
    "implementer: Testing framework and CI/CD setup",
    "implementer: Packaging and distribution automation",
    "reviewer: Code review processes and quality standards"
]
```

---

## Pattern Selection Guide

### Choosing the Right Pattern

**Project Complexity Assessment:**
```python
complexity_factors = {
    "simple": "Single developer, <2 weeks, well-defined scope",
    "moderate": "Small team, 2-8 weeks, some unknowns",
    "complex": "Multiple developers, 2-6 months, significant integration",
    "enterprise": "Multiple teams, 6+ months, high coordination needs"
}
```

**Pattern Matching:**
```python
pattern_selection = {
    "web_application": "Use full-stack pattern for complete applications",
    "api_only": "Use API pattern for backend-focused projects", 
    "data_heavy": "Use data pipeline pattern for ETL/analytics",
    "docs_focus": "Use documentation patterns for content projects",
    "infrastructure": "Use DevOps patterns for deployment/operations",
    "research": "Use analysis patterns for evaluation projects",
    "enterprise": "Use multi-phase patterns for large initiatives"
}
```

### Customizing Patterns

**Adaptation Guidelines:**
```python
customization_approach = [
    "Start with closest matching pattern",
    "Modify specialist assignments based on project needs",
    "Adjust phase timing based on team size and complexity",
    "Add project-specific validation and maintenance points",
    "Customize artifact types and organization for domain"
]
```

**Pattern Combination:**
```python
# Many projects benefit from combining patterns
combined_patterns = {
    "api_with_docs": "Combine API and documentation patterns",
    "research_to_implementation": "Research pattern followed by development pattern",
    "infrastructure_with_migration": "Combine DevOps and migration patterns",
    "enterprise_multi_component": "Multiple development patterns within enterprise framework"
}
```

---

*These workflow patterns provide proven templates for common project types. Start with the pattern that most closely matches your project, then customize the specialist assignments and phase timing based on your specific needs and constraints.*