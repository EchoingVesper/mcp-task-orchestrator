

# MCP Task Orchestrator - Usage Examples

This document provides practical examples of using the MCP Task Orchestrator in different scenarios.

#

# LLM-Powered Task Orchestration (New Approach)

#

## Example 0: Complete Workflow with LLM-Powered Task Breakdown

#

### Task Description

Build a REST API with user authentication, data validation, and comprehensive documentation.

#

### Step 1: Initialize Session

```python

# Initialize the task orchestration session to get guidance

response = await call_tool("orchestrator_initialize_session", {})

# Server response (simplified)

{
    "session_initialized": true,
    "orchestrator_context": {
        "role": "Task Orchestrator",
        "capabilities": [
            "Breaking down complex tasks into manageable subtasks",
            "Assigning appropriate specialist roles to each subtask",
            "Managing dependencies between subtasks",
            "Tracking progress and coordinating work"
        ],
        "instructions": "As the Task Orchestrator, your role is to analyze complex tasks and break them down into a structured set of subtasks...",
        "specialist_roles": {
            "architect": "System design and architecture planning",
            "implementer": "Writing code and implementing features",
            "debugger": "Fixing issues and optimizing performance",
            "documenter": "Creating documentation and guides",
            "reviewer": "Code review and quality assurance",
            "tester": "Testing and validation",
            "researcher": "Research and information gathering"
        }
    },
    "instructions": "You are now in Task Orchestrator mode. Your role is to break down complex tasks into structured subtasks with appropriate specialist assignments..."
}

```text

#

### Step 2: Analyze Task and Create JSON-Formatted Subtasks

```text
python

# Analyze the task and create structured subtasks

subtasks_json = [
    {
        "title": "API Architecture Design",
        "description": "Design the overall API architecture, including endpoints, data models, and authentication flow",
        "specialist_type": "architect",
        "dependencies": [],
        "estimated_effort": "45-60 minutes"
    },
    {
        "title": "Database Schema Design",
        "description": "Design the database schema to support the API functionality and user authentication",
        "specialist_type": "architect",
        "dependencies": [],
        "estimated_effort": "30-45 minutes"
    },
    {
        "title": "Core API Implementation",
        "description": "Implement the core API endpoints and functionality",
        "specialist_type": "implementer",
        "dependencies": ["API Architecture Design", "Database Schema Design"],
        "estimated_effort": "1-2 hours"
    },
    {
        "title": "Authentication System",
        "description": "Implement user authentication with secure token handling and password hashing",
        "specialist_type": "implementer",
        "dependencies": ["Database Schema Design"],
        "estimated_effort": "1-1.5 hours"
    },
    {
        "title": "Data Validation",
        "description": "Implement robust data validation for all API inputs",
        "specialist_type": "implementer",
        "dependencies": ["Core API Implementation"],
        "estimated_effort": "45-60 minutes"
    },
    {
        "title": "API Testing",
        "description": "Create comprehensive tests for all API endpoints and authentication",
        "specialist_type": "tester",
        "dependencies": ["Core API Implementation", "Authentication System", "Data Validation"],
        "estimated_effort": "1-1.5 hours"
    },
    {
        "title": "API Documentation",
        "description": "Create detailed API documentation including endpoints, parameters, and examples",
        "specialist_type": "documenter",
        "dependencies": ["Core API Implementation", "Authentication System", "Data Validation"],
        "estimated_effort": "1-1.5 hours"
    }
]

```text

#

### Step 3: Plan Task with Subtasks

```text
python

# Submit the task with JSON-formatted subtasks

response = await call_tool("orchestrator_plan_task", {
    "description": "Build a REST API with user authentication, data validation, and comprehensive documentation",
    "subtasks_json": json.dumps(subtasks_json),
    "complexity_level": "complex",
    "context": "Using Node.js, Express, and MongoDB. The API will be used by a mobile application."
})

# Server response (simplified)

{
    "task_breakdown": {
        "parent_task_id": "task_a1b2c3d4",
        "total_subtasks": 7,
        "estimated_complexity": "complex",
        "subtasks": [
            {
                "task_id": "architect_e5f6g7",
                "title": "API Architecture Design",
                "specialist_type": "architect",
                "description": "Design the overall API architecture, including endpoints, data models, and authentication flow",
                "dependencies": [],
                "estimated_effort": "45-60 minutes"
            },
            

# ... other subtasks ...

        ]
    },
    "instructions": "Task breakdown complete! 7 subtasks created and stored. Use 'orchestrator_execute_subtask' with each task_id to begin working on them. Recommended order: architect_e5f6g7 → architect_h8i9j0 → implementer_k1l2m3 → implementer_n4o5p6 → implementer_q7r8s9 → tester_t0u1v2 → documenter_w3x4y5"
}

```text

#

### Step 4: Execute Subtasks

```text
python

# Execute the first subtask (API Architecture Design)

response = await call_tool("orchestrator_execute_subtask", {
    "task_id": "architect_e5f6g7"
})

# Server response (simplified)

"""

#

# Role

You are a System Architect focused on designing robust, scalable systems

#

# Your Expertise

• System design patterns and best practices
• Architectural trade-offs and decision-making
• Technical requirements analysis
• Component and service design
• Integration patterns and strategies
• Performance and scalability considerations
• Security architecture

#

# Current Task

**Title:** API Architecture Design
**Description:** Design the overall API architecture, including endpoints, data models, and authentication flow

#

# Instructions

You are now operating in ARCHITECT MODE. Focus entirely on this role and apply your specialized expertise to complete the task described above.
...
"""

# Complete the subtask

response = await call_tool("orchestrator_complete_subtask", {
    "task_id": "architect_e5f6g7",
    "results": "Completed API architecture design with RESTful endpoints, resource-based URL structure, and JWT-based authentication flow. Defined core resources (users, items, categories) with their relationships and operations.",
    "artifacts": ["api_architecture.md", "endpoint_definitions.json", "auth_flow_diagram.png"],
    "next_action": "continue"
})

# Server response (simplified)

{
    "task_id": "architect_e5f6g7",
    "status": "completed",
    "results_recorded": true,
    "parent_task_progress": {
        "progress": "in_progress",
        "next_steps": "Continue with dependent tasks"
    },
    "next_recommended_task": "architect_h8i9j0"
}

# Continue with remaining subtasks...

```text

#

### Step 5: Synthesize Results

```python

# After completing all subtasks, synthesize the results

response = await call_tool("orchestrator_synthesize_results", {
    "parent_task_id": "task_a1b2c3d4"
})

# Server response (simplified)

{
    "parent_task_id": "task_a1b2c3d4",
    "synthesis": "REST API successfully implemented with Node.js, Express, and MongoDB. The API includes secure user authentication using JWT, comprehensive data validation for all inputs, and detailed documentation. The architecture follows RESTful principles with clear endpoint structure. All endpoints have been tested and validated.",
    "subtasks_completed": 7,
    "total_subtasks": 7,
    "artifacts": [
        "api_architecture.md",
        "endpoint_definitions.json",
        "auth_flow_diagram.png",
        "database_schema.json",
        "api_implementation.js",
        "auth_system.js",
        "validation_middleware.js",
        "api_tests.js",
        "api_documentation.md"
    ]
}

```text

#

# Legacy Examples (Previous Pattern-Matching Approach)

#

## Example 1: Web Development Project (Legacy)

#

### Task Description (Web App)

Build a responsive web application with user authentication, data visualization, and API integration.

#

### Task Planning

```text
python

# LLM calls

response = await call_tool("orchestrator_plan_task", {
    "description": "Build a responsive web application with user authentication, data visualization, and API integration",
    "complexity_level": "complex",
    "context": "Using React, Node.js, and Express. The application should have a modern UI and follow security best practices."
})

# Server response (simplified)

{
    "task_breakdown": {
        "parent_task_id": "task_12345",
        "total_subtasks": 6,
        "estimated_complexity": "complex",
        "subtasks": [
            {
                "task_id": "architecture_1",
                "title": "System Architecture",
                "specialist_type": "architect",
                "description": "Design the overall system architecture including component structure, data flow, and API endpoints",
                "dependencies": [],
                "estimated_effort": "30-45 minutes"
            },
            {
                "task_id": "frontend_1",
                "title": "Frontend Implementation",
                "specialist_type": "implementer",
                "description": "Implement the responsive UI components using React",
                "dependencies": ["architecture_1"],
                "estimated_effort": "1-2 hours"
            },
            {
                "task_id": "backend_1",
                "title": "Backend Implementation",
                "specialist_type": "implementer",
                "description": "Implement the Node.js/Express backend with API endpoints",
                "dependencies": ["architecture_1"],
                "estimated_effort": "1-2 hours"
            },
            {
                "task_id": "auth_1",
                "title": "Authentication System",
                "specialist_type": "implementer",
                "description": "Implement secure user authentication and authorization",
                "dependencies": ["architecture_1"],
                "estimated_effort": "45-60 minutes"
            },
            {
                "task_id": "dataviz_1",
                "title": "Data Visualization",
                "specialist_type": "implementer",
                "description": "Implement data visualization components",
                "dependencies": ["frontend_1", "backend_1"],
                "estimated_effort": "45-60 minutes"
            },
            {
                "task_id": "docs_1",
                "title": "Documentation",
                "specialist_type": "documenter",
                "description": "Create comprehensive documentation for the application",
                "dependencies": ["frontend_1", "backend_1", "auth_1", "dataviz_1"],
                "estimated_effort": "30-45 minutes"
            }
        ]
    },
    "instructions": "Task breakdown complete! 6 subtasks identified. Use 'orchestrator_execute_subtask' with each task_id to begin working on them. Recommended order: architecture_1 → frontend_1 → backend_1 → auth_1 → dataviz_1 → docs_1"
}

```text

#

### Subtask Execution - Architecture

```text
python

# LLM calls

response = await call_tool("orchestrator_execute_subtask", {
    "task_id": "architecture_1"
})

# Server response (simplified)

"""

#

# Role

You are a System Architect focused on designing robust, scalable systems

#

# Your Expertise

• System design patterns and best practices
• Architectural trade-offs and decision-making
• Technical requirements analysis
• Component and service design
• Integration patterns and strategies
• Performance and scalability considerations
• Security architecture

#

# Your Approach

• Start with a high-level overview of the system
• Break down complex systems into manageable components
• Consider scalability, reliability, and maintainability
• Document design decisions and their rationales
• Provide clear diagrams and visual representations
• Consider both functional and non-functional requirements
• Evaluate trade-offs between different approaches

#

# Expected Output Format

Comprehensive architectural documents with diagrams, component descriptions, and implementation guidance

#

# Current Task

**Title:** System Architecture
**Description:** Design the overall system architecture including component structure, data flow, and API endpoints

#

# Instructions

You are now operating in ARCHITECT MODE. Focus entirely on this role and apply your specialized expertise to complete the task described above.

When you have completed this task, be sure to:

1. Provide a clear summary of what was accomplished

2. List any artifacts or deliverables created

3. Mention any recommendations for next steps

Remember: You are the architect specialist for this task. Apply your expertise accordingly.
"""

```text

#

### Subtask Completion

```text
python

# LLM calls

response = await call_tool("orchestrator_complete_subtask", {
    "task_id": "architecture_1",
    "results": "Completed system architecture design with component diagram, data flow diagram, and API endpoint specifications. The architecture follows a modern React frontend with Redux state management, Node.js/Express RESTful API backend, and MongoDB database. Authentication uses JWT with refresh tokens.",
    "artifacts": ["architecture_diagram.png", "api_endpoints.md", "data_model.md"],
    "next_action": "continue"
})

# Server response (simplified)

{
    "task_id": "architecture_1",
    "status": "completed",
    "results_recorded": true,
    "parent_task_progress": {
        "progress": "in_progress",
        "next_steps": "Continue with dependent tasks: frontend_1, backend_1, auth_1"
    },
    "next_recommended_task": "frontend_1"
}

```text

#

### Result Synthesis

After completing all subtasks, the results can be synthesized:

```text
python

# LLM calls

response = await call_tool("orchestrator_synthesize_results", {
    "parent_task_id": "task_12345"
})

# Server response (simplified)

{
    "parent_task_id": "task_12345",
    "synthesis": "Web application successfully implemented with React frontend, Node.js/Express backend, JWT authentication, and data visualization components. The application follows the designed architecture with proper separation of concerns. All components are documented and tested.",
    "subtasks_completed": 6,
    "total_subtasks": 6,
    "artifacts": [
        "architecture_diagram.png",
        "api_endpoints.md",
        "data_model.md",
        "frontend_components.js",
        "backend_api.js",
        "auth_service.js",
        "data_visualization.js",
        "user_documentation.md",
        "developer_documentation.md"
    ]
}

```text

#

## Example 2: Code Review and Optimization

#

### Task Description (Code Review)

Review a Python codebase and suggest performance improvements.

#

### Task Planning (Code Review)

```text
python

# LLM calls

response = await call_tool("orchestrator_plan_task", {
    "description": "Review a Python codebase and suggest performance improvements",
    "complexity_level": "moderate",
    "context": "The codebase is a data processing pipeline with potential bottlenecks in file I/O and data transformation."
})

# Server response (simplified)

{
    "task_breakdown": {
        "parent_task_id": "task_67890",
        "total_subtasks": 4,
        "estimated_complexity": "moderate",
        "subtasks": [
            {
                "task_id": "analysis_1",
                "title": "Code Analysis",
                "specialist_type": "researcher",
                "description": "Analyze the codebase structure, dependencies, and overall architecture",
                "dependencies": [],
                "estimated_effort": "30-45 minutes"
            },
            {
                "task_id": "review_1",
                "title": "Code Quality Review",
                "specialist_type": "reviewer",
                "description": "Review code quality, patterns, and potential issues",
                "dependencies": ["analysis_1"],
                "estimated_effort": "45-60 minutes"
            },
            {
                "task_id": "performance_1",
                "title": "Performance Analysis",
                "specialist_type": "debugger",
                "description": "Identify performance bottlenecks and optimization opportunities",
                "dependencies": ["analysis_1", "review_1"],
                "estimated_effort": "45-60 minutes"
            },
            {
                "task_id": "recommendations_1",
                "title": "Optimization Recommendations",
                "specialist_type": "implementer",
                "description": "Provide specific optimization recommendations and code improvements",
                "dependencies": ["performance_1"],
                "estimated_effort": "45-60 minutes"
            }
        ]
    },
    "instructions": "Task breakdown complete! 4 subtasks identified. Use 'orchestrator_execute_subtask' with each task_id to begin working on them. Recommended order: analysis_1 → review_1 → performance_1 → recommendations_1"
}

```text

#

## Example 3: Research Project

#

### Task Description (Research)

Research the latest advancements in quantum computing and prepare a comprehensive report.

#

### Task Planning (Research)

```text
python

# LLM calls

response = await call_tool("orchestrator_plan_task", {
    "description": "Research the latest advancements in quantum computing and prepare a comprehensive report",
    "complexity_level": "moderate",
    "context": "The report should cover recent breakthroughs, practical applications, and future prospects."
})

# Server response (simplified)

{
    "task_breakdown": {
        "parent_task_id": "task_24680",
        "total_subtasks": 4,
        "estimated_complexity": "moderate",
        "subtasks": [
            {
                "task_id": "research_1",
                "title": "Initial Research",
                "specialist_type": "researcher",
                "description": "Research recent advancements in quantum computing technology",
                "dependencies": [],
                "estimated_effort": "45-60 minutes"
            },
            {
                "task_id": "applications_1",
                "title": "Practical Applications",
                "specialist_type": "researcher",
                "description": "Research practical applications of quantum computing in various fields",
                "dependencies": ["research_1"],
                "estimated_effort": "30-45 minutes"
            },
            {
                "task_id": "future_1",
                "title": "Future Prospects",
                "specialist_type": "researcher",
                "description": "Analyze future prospects and potential developments in quantum computing",
                "dependencies": ["research_1"],
                "estimated_effort": "30-45 minutes"
            },
            {
                "task_id": "report_1",
                "title": "Report Compilation",
                "specialist_type": "documenter",
                "description": "Compile a comprehensive report on quantum computing advancements",
                "dependencies": ["research_1", "applications_1", "future_1"],
                "estimated_effort": "45-60 minutes"
            }
        ]
    },
    "instructions": "Task breakdown complete! 4 subtasks identified. Use 'orchestrator_execute_subtask' with each task_id to begin working on them. Recommended order: research_1 → applications_1 → future_1 → report_1"
}
```text

#

# Best Practices

Based on these examples, here are some best practices for using the MCP Task Orchestrator:

1. **Provide Detailed Task Descriptions**: The more specific your task description, the better the task breakdown will be.

2. **Include Relevant Context**: Adding context helps the orchestrator understand the specific requirements and constraints.

3. **Follow the Recommended Task Order**: The orchestrator suggests a task order that respects dependencies between subtasks.

4. **Embrace Specialist Roles**: When executing a subtask, fully embrace the specialist role provided by the orchestrator.

5. **Provide Comprehensive Results**: When completing a subtask, include detailed results and list all artifacts created.

6. **Track Progress**: Use the `orchestrator_get_status` tool to track progress and identify the next steps.

7. **Synthesize Results Properly**: After completing all subtasks, use the synthesis tool to create a cohesive summary.

For more detailed information, see the [Usage Guide](../usage.md) and [Configuration Guide](../configuration.md).
