"""
Additional Default Templates

Extended collection of templates for creative workflows,
business processes, and specialized use cases.
"""

import logging

logger = logging.getLogger(__name__)


# Creative Workflow Templates

CONTENT_CREATION_WORKFLOW = """
// Content Creation Workflow Template
// Systematic approach to creating high-quality content

{
  "metadata": {
    "name": "Content Creation Workflow",
    "version": "1.0.0",
    "description": "End-to-end content creation process from ideation to publication",
    "category": "creative",
    "tags": ["content", "writing", "creative", "marketing", "publishing"],
    "author": "Task Orchestrator",
    "complexity": "moderate",
    "estimated_duration": "1-2 weeks"
  },
  
  "parameters": {
    "content_type": {
      "type": "string",
      "description": "Type of content to create",
      "required": true,
      "enum": ["blog_post", "article", "whitepaper", "case_study", "tutorial", "video_script", "podcast_episode"]
    },
    "target_audience": {
      "type": "string",
      "description": "Primary target audience",
      "required": true,
      "min_length": 5,
      "max_length": 200
    },
    "content_topic": {
      "type": "string",
      "description": "Main topic or subject of the content",
      "required": true,
      "min_length": 5,
      "max_length": 100
    },
    "content_length": {
      "type": "string",
      "description": "Expected content length",
      "required": false,
      "enum": ["short", "medium", "long", "comprehensive"],
      "default": "medium"
    },
    "publication_platform": {
      "type": "string",
      "description": "Where the content will be published",
      "required": false
    },
    "seo_focus": {
      "type": "boolean",
      "description": "Whether SEO optimization is a priority",
      "required": false,
      "default": true
    }
  },
  
  "tasks": {
    "content_strategy": {
      "title": "Develop Content Strategy",
      "description": "Define strategy and goals for {{content_type}} about {{content_topic}}",
      "type": "planning",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "2-4 hours",
      "checklist": [
        "Define content objectives and KPIs",
        "Research target audience needs and preferences",
        "Analyze competitor content and gaps",
        "Define unique value proposition",
        "Set content tone and style guidelines",
        "Plan content distribution strategy"
      ]
    },
    
    "research_and_ideation": {
      "title": "Research and Content Ideation",
      "description": "Conduct thorough research on {{content_topic}} and generate ideas",
      "type": "research",
      "specialist_type": "researcher",
      "complexity": "moderate",
      "estimated_effort": "4-6 hours",
      "dependencies": ["content_strategy"],
      "checklist": [
        "Research topic thoroughly from multiple sources",
        "Identify key themes and subtopics",
        "Gather supporting data and statistics",
        "Interview subject matter experts if needed",
        "Collect relevant examples and case studies",
        "Generate and prioritize content ideas"
      ]
    },
    
    "content_outline": {
      "title": "Create Detailed Content Outline",
      "description": "Structure the {{content_type}} with detailed outline and flow",
      "type": "planning",
      "specialist_type": "coder",
      "complexity": "simple",
      "estimated_effort": "1-2 hours",
      "dependencies": ["research_and_ideation"],
      "checklist": [
        "Create hierarchical content structure",
        "Define main sections and subsections",
        "Plan introduction and conclusion",
        "Identify key points and supporting evidence",
        "Plan visual elements and multimedia",
        "Review outline for logical flow"
      ]
    },
    
    "content_creation": {
      "title": "Write and Create Content",
      "description": "Produce the main content for {{content_type}} about {{content_topic}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "complex",
      "estimated_effort": "1-3 days",
      "dependencies": ["content_outline"],
      "checklist": [
        "Write engaging introduction",
        "Develop main content sections",
        "Add supporting evidence and examples",
        "Create compelling conclusion with call-to-action",
        "Integrate visual elements and multimedia",
        "Ensure content aligns with brand voice"
      ]
    },
    
    "seo_optimization": {
      "title": "SEO Optimization and Enhancement",
      "description": "Optimize content for search engines and discoverability",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "moderate",
      "estimated_effort": "2-4 hours",
      "dependencies": ["content_creation"],
      "checklist": [
        "Research and integrate target keywords",
        "Optimize title and meta descriptions",
        "Add proper heading structure (H1, H2, H3)",
        "Optimize images with alt text",
        "Add internal and external links",
        "Ensure mobile-friendly formatting"
      ]
    },
    
    "review_and_editing": {
      "title": "Content Review and Editing",
      "description": "Comprehensive review, editing, and proofreading of content",
      "type": "review",
      "specialist_type": "reviewer",
      "complexity": "moderate",
      "estimated_effort": "2-4 hours",
      "dependencies": ["seo_optimization"],
      "checklist": [
        "Review content for accuracy and completeness",
        "Edit for clarity, flow, and readability",
        "Proofread for grammar and spelling errors",
        "Verify all facts and sources",
        "Ensure brand compliance and consistency",
        "Get stakeholder approval if required"
      ]
    },
    
    "publication_preparation": {
      "title": "Prepare for Publication",
      "description": "Format and prepare content for publication on {{publication_platform}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "simple",
      "estimated_effort": "1-2 hours",
      "dependencies": ["review_and_editing"],
      "checklist": [
        "Format content for target platform",
        "Create and optimize featured images",
        "Set up social media promotional posts",
        "Schedule publication timing",
        "Prepare email newsletter if applicable",
        "Set up analytics tracking"
      ]
    },
    
    "promotion_and_distribution": {
      "title": "Content Promotion and Distribution",
      "description": "Execute content promotion strategy across channels",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "moderate",
      "estimated_effort": "2-3 hours",
      "dependencies": ["publication_preparation"],
      "checklist": [
        "Publish content on primary platform",
        "Share on relevant social media channels",
        "Send to email subscribers",
        "Engage with community and respond to comments",
        "Reach out to influencers or partners",
        "Monitor performance and engagement metrics"
      ]
    }
  },
  
  "milestones": {
    "strategy_and_research_complete": {
      "title": "Strategy and Research Complete",
      "description": "Content strategy defined and research completed",
      "required_tasks": ["content_strategy", "research_and_ideation", "content_outline"]
    },
    "content_ready": {
      "title": "Content Creation Complete",
      "description": "Content written, optimized, and ready for review",
      "required_tasks": ["content_creation", "seo_optimization"]
    },
    "published": {
      "title": "Content Published and Promoted",
      "description": "Content is live and promotion campaign launched",
      "required_tasks": ["review_and_editing", "publication_preparation", "promotion_and_distribution"]
    }
  }
}
"""

DESIGN_PROJECT_WORKFLOW = """
// Design Project Workflow Template  
// Comprehensive design process from brief to delivery

{
  "metadata": {
    "name": "Design Project Workflow",
    "version": "1.0.0",
    "description": "Complete design process workflow for digital and visual design projects",
    "category": "creative",
    "tags": ["design", "creative", "visual", "user-experience", "branding"],
    "author": "Task Orchestrator",
    "complexity": "complex",
    "estimated_duration": "2-6 weeks"
  },
  
  "parameters": {
    "project_type": {
      "type": "string",
      "description": "Type of design project",
      "required": true,
      "enum": ["web_design", "app_design", "branding", "print_design", "ui_ux", "logo_design", "marketing_materials"]
    },
    "client_name": {
      "type": "string",
      "description": "Client or project name",
      "required": true,
      "min_length": 2,
      "max_length": 100
    },
    "project_scope": {
      "type": "string",
      "description": "Scope and scale of the project",
      "required": true,
      "enum": ["small", "medium", "large", "enterprise"]
    },
    "target_deadline": {
      "type": "string",
      "description": "Project deadline (YYYY-MM-DD)",
      "required": false,
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    },
    "revision_rounds": {
      "type": "number",
      "description": "Number of revision rounds included",
      "required": false,
      "min": 1,
      "max": 5,
      "default": 3
    }
  },
  
  "tasks": {
    "project_discovery": {
      "title": "Project Discovery and Brief Analysis",
      "description": "Understand {{client_name}} requirements and project goals for {{project_type}}",
      "type": "research",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "checklist": [
        "Conduct client interview and requirements gathering",
        "Analyze project brief and objectives",
        "Define target audience and user personas",
        "Establish project scope and constraints",
        "Set design criteria and success metrics",
        "Document brand guidelines and preferences"
      ]
    },
    
    "competitive_research": {
      "title": "Competitive and Market Research",
      "description": "Research competitors and industry standards for {{project_type}}",
      "type": "research",
      "specialist_type": "researcher",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["project_discovery"],
      "checklist": [
        "Analyze direct and indirect competitors",
        "Research industry design trends and best practices",
        "Collect inspiration and reference materials",
        "Identify opportunities for differentiation",
        "Study user expectations and conventions",
        "Document findings and insights"
      ]
    },
    
    "concept_development": {
      "title": "Design Concept Development",
      "description": "Develop initial design concepts and creative direction",
      "type": "design",
      "specialist_type": "coder",
      "complexity": "complex",
      "estimated_effort": "3-5 days",
      "dependencies": ["competitive_research"],
      "checklist": [
        "Generate multiple design concepts",
        "Create mood boards and style tiles",
        "Develop color palettes and typography",
        "Create initial sketches and wireframes",
        "Define visual hierarchy and layout principles",
        "Present concepts for client feedback"
      ]
    },
    
    "design_refinement": {
      "title": "Refine and Develop Chosen Concept",
      "description": "Refine selected concept based on feedback and develop detailed designs",
      "type": "design",
      "specialist_type": "coder",
      "complexity": "complex",
      "estimated_effort": "1-2 weeks",
      "dependencies": ["concept_development"],
      "checklist": [
        "Refine chosen concept based on feedback",
        "Create detailed design mockups",
        "Develop responsive layouts if applicable",
        "Create interactive prototypes",
        "Ensure accessibility and usability standards",
        "Prepare design specifications and guidelines"
      ]
    },
    
    "client_review_cycle": {
      "title": "Client Review and Revision Cycle",
      "description": "Conduct {{revision_rounds}} rounds of client review and revisions",
      "type": "review",
      "specialist_type": "reviewer",
      "complexity": "moderate",
      "estimated_effort": "3-5 days",
      "dependencies": ["design_refinement"],
      "checklist": [
        "Present designs to client with rationale",
        "Collect and document feedback",
        "Prioritize revision requests",
        "Implement approved changes",
        "Maintain design integrity during revisions",
        "Get final approval from stakeholders"
      ]
    },
    
    "design_finalization": {
      "title": "Finalize Design Assets",
      "description": "Prepare final design assets and deliverables for {{client_name}}",
      "type": "implementation",
      "specialist_type": "coder",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["client_review_cycle"],
      "checklist": [
        "Finalize all design assets",
        "Create multiple file formats as needed",
        "Optimize assets for different use cases",
        "Create design system documentation",
        "Prepare brand guidelines if applicable",
        "Quality check all deliverables"
      ]
    },
    
    "delivery_and_handoff": {
      "title": "Project Delivery and Handoff",
      "description": "Deliver final assets and conduct project handoff",
      "type": "deployment",
      "specialist_type": "coordinator",
      "complexity": "simple",
      "estimated_effort": "1 day",
      "dependencies": ["design_finalization"],
      "checklist": [
        "Organize and package all deliverables",
        "Create delivery documentation",
        "Conduct handoff meeting with client",
        "Transfer all design files and assets",
        "Provide usage guidelines and recommendations",
        "Collect project feedback and testimonials"
      ]
    }
  },
  
  "milestones": {
    "research_complete": {
      "title": "Research and Discovery Complete",
      "description": "Project requirements understood and research completed",
      "required_tasks": ["project_discovery", "competitive_research"]
    },
    "concept_approved": {
      "title": "Design Concept Approved",
      "description": "Creative direction established and concept approved",
      "required_tasks": ["concept_development"]
    },
    "project_delivered": {
      "title": "Project Successfully Delivered",
      "description": "All deliverables completed and handed off to client",
      "required_tasks": ["design_refinement", "client_review_cycle", "design_finalization", "delivery_and_handoff"]
    }
  }
}
"""

# Business Process Templates

PROJECT_PLANNING_TEMPLATE = """
// Project Planning Template
// Comprehensive project planning and management workflow

{
  "metadata": {
    "name": "Project Planning and Management",
    "version": "1.0.0",
    "description": "Complete project planning workflow from initiation to closure",
    "category": "business",
    "tags": ["project-management", "planning", "business", "coordination"],
    "author": "Task Orchestrator",
    "complexity": "complex",
    "estimated_duration": "2-8 weeks"
  },
  
  "parameters": {
    "project_name": {
      "type": "string",
      "description": "Name of the project",
      "required": true,
      "min_length": 3,
      "max_length": 100
    },
    "project_type": {
      "type": "string",
      "description": "Type of project",
      "required": true,
      "enum": ["software", "marketing", "research", "product", "process_improvement", "infrastructure"]
    },
    "project_duration": {
      "type": "string",
      "description": "Expected project duration",
      "required": true,
      "enum": ["short", "medium", "long", "ongoing"]
    },
    "team_size": {
      "type": "number",
      "description": "Number of team members",
      "required": false,
      "min": 1,
      "max": 50,
      "default": 5
    },
    "budget_available": {
      "type": "boolean",
      "description": "Whether budget information is available",
      "required": false,
      "default": true
    },
    "stakeholder_count": {
      "type": "number",
      "description": "Number of key stakeholders",
      "required": false,
      "min": 1,
      "max": 20,
      "default": 3
    }
  },
  
  "tasks": {
    "project_initiation": {
      "title": "Project Initiation and Charter",
      "description": "Define {{project_name}} scope, objectives, and create project charter",
      "type": "planning",
      "specialist_type": "coordinator",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "checklist": [
        "Define project scope and objectives",
        "Identify key stakeholders and sponsors",
        "Create project charter document",
        "Establish success criteria and KPIs",
        "Define project constraints and assumptions",
        "Get formal project approval"
      ]
    },
    
    "stakeholder_analysis": {
      "title": "Stakeholder Analysis and Engagement Plan",
      "description": "Analyze stakeholders and create engagement strategy",
      "type": "planning",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "dependencies": ["project_initiation"],
      "checklist": [
        "Identify all project stakeholders",
        "Analyze stakeholder influence and interest",
        "Create stakeholder engagement matrix",
        "Define communication preferences",
        "Plan stakeholder management approach",
        "Schedule regular stakeholder meetings"
      ]
    },
    
    "work_breakdown": {
      "title": "Work Breakdown Structure",
      "description": "Break down {{project_name}} into manageable work packages",
      "type": "planning",
      "specialist_type": "coordinator",
      "complexity": "complex",
      "estimated_effort": "2-3 days",
      "dependencies": ["stakeholder_analysis"],
      "checklist": [
        "Decompose project into work packages",
        "Define deliverables for each package",
        "Estimate effort and duration",
        "Identify task dependencies",
        "Assign responsibility matrix (RACI)",
        "Validate WBS with team and stakeholders"
      ]
    },
    
    "schedule_development": {
      "title": "Project Schedule Development",
      "description": "Create detailed project schedule with critical path analysis",
      "type": "planning",
      "specialist_type": "coordinator",
      "complexity": "complex",
      "estimated_effort": "2-3 days",
      "dependencies": ["work_breakdown"],
      "checklist": [
        "Create detailed project timeline",
        "Identify critical path and dependencies",
        "Allocate resources to tasks",
        "Define milestones and checkpoints",
        "Build in buffer time for risks",
        "Create baseline schedule"
      ]
    },
    
    "risk_management": {
      "title": "Risk Management Planning",
      "description": "Identify, analyze, and plan responses to project risks",
      "type": "planning",
      "specialist_type": "analyst",
      "complexity": "moderate",
      "estimated_effort": "1-2 days",
      "dependencies": ["schedule_development"],
      "checklist": [
        "Identify potential project risks",
        "Analyze risk probability and impact",
        "Develop risk response strategies",
        "Create risk register and monitoring plan",
        "Define escalation procedures",
        "Plan contingency measures"
      ]
    },
    
    "communication_plan": {
      "title": "Communication and Reporting Plan",
      "description": "Establish communication protocols and reporting structure",
      "type": "planning",
      "specialist_type": "coordinator",
      "complexity": "simple",
      "estimated_effort": "1 day",
      "dependencies": ["risk_management"],
      "checklist": [
        "Define communication channels and protocols",
        "Set up regular reporting schedule",
        "Create meeting cadence and agendas",
        "Establish documentation standards",
        "Set up project tracking tools",
        "Define escalation procedures"
      ]
    },
    
    "project_execution": {
      "title": "Project Execution and Monitoring",
      "description": "Execute project plan while monitoring progress and performance",
      "type": "implementation",
      "specialist_type": "coordinator",
      "complexity": "complex",
      "estimated_effort": "Ongoing",
      "dependencies": ["communication_plan"],
      "checklist": [
        "Kick off project with team and stakeholders",
        "Monitor task progress and deliverables",
        "Track budget and resource utilization",
        "Manage scope changes and issues",
        "Conduct regular team meetings",
        "Provide regular status reports"
      ]
    },
    
    "quality_assurance": {
      "title": "Quality Assurance and Control",
      "description": "Ensure deliverables meet quality standards and requirements",
      "type": "review",
      "specialist_type": "reviewer",
      "complexity": "moderate",
      "estimated_effort": "Ongoing",
      "dependencies": ["project_execution"],
      "checklist": [
        "Define quality standards and criteria",
        "Conduct regular quality reviews",
        "Implement quality control processes",
        "Track and resolve quality issues",
        "Conduct stakeholder reviews and approvals",
        "Document lessons learned"
      ]
    },
    
    "project_closure": {
      "title": "Project Closure and Handoff",
      "description": "Complete project closure activities and knowledge transfer",
      "type": "deployment",
      "specialist_type": "coordinator",
      "complexity": "moderate",
      "estimated_effort": "2-3 days",
      "dependencies": ["quality_assurance"],
      "checklist": [
        "Finalize all project deliverables",
        "Conduct project retrospective",
        "Document lessons learned",
        "Release project resources",
        "Conduct knowledge transfer",
        "Archive project documentation"
      ]
    }
  },
  
  "milestones": {
    "planning_complete": {
      "title": "Project Planning Complete",
      "description": "All planning activities completed and approved",
      "required_tasks": ["project_initiation", "stakeholder_analysis", "work_breakdown", "schedule_development", "risk_management", "communication_plan"]
    },
    "execution_phase": {
      "title": "Project Execution Phase",
      "description": "Project execution underway with monitoring and control",
      "required_tasks": ["project_execution", "quality_assurance"]
    },
    "project_complete": {
      "title": "Project Successfully Completed",
      "description": "All deliverables completed and project closed",
      "required_tasks": ["project_closure"]
    }
  }
}
"""


def get_additional_templates() -> Dict[str, str]:
    """Get additional default templates."""
    return {
        "content_creation_workflow": CONTENT_CREATION_WORKFLOW,
        "design_project_workflow": DESIGN_PROJECT_WORKFLOW,
        "project_planning_template": PROJECT_PLANNING_TEMPLATE
    }


def get_creative_templates() -> List[str]:
    """Get list of creative workflow templates."""
    return [
        "content_creation_workflow",
        "design_project_workflow"
    ]


def get_business_templates() -> List[str]:
    """Get list of business process templates."""
    return [
        "project_planning_template"
    ]