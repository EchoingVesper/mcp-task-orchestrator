

# Single Task Execution

#

# Overview

Single task execution is the simplest workflow in MCP Task Orchestrator. Use this pattern when you have a well-defined task that can be completed by one or two specialists working together.

#

# When to Use Single Task Execution

#

## Ideal Scenarios

- Code reviews or debugging sessions

- Writing documentation for a specific feature  

- Creating simple scripts or utilities

- Research on specific technical topics

- Quick prototyping or proof-of-concept work

#

## Not Suitable For

- Complex multi-component projects

- Tasks requiring multiple phases or stages

- Work that needs significant planning or architecture

- Projects with unknown scope or requirements

#

# Basic Workflow

#

## Step 1: Initialize Simple Task

```plaintext
Use orchestrator_initialize with:

- task_description: Clear, specific description

- complexity: "basic" 

- specialist_count: 1-2

```text

#

## Step 2: Direct Execution

For simple tasks, you can often skip separate planning:

```text
plaintext
Use orchestrator_execute immediately after initialization

```text

#

## Step 3: Quick Review

```text
plaintext
Use orchestrator_synthesize to get final results

```text

#

# Example: Code Review Task

#

## Task Setup

```text
plaintext
Task: "Review the user authentication module for security issues"
Complexity: basic
Expected Output: Security analysis with recommendations

```text

#

## Execution Flow

1. **Reviewer specialist** analyzes the code

2. **Debugger specialist** identifies specific issues  

3. **Results synthesized** into actionable report

#

## Expected Timeline

- Simple tasks: 5-15 minutes

- Code reviews: 10-30 minutes

- Documentation: 15-45 minutes

#

# Best Practices

#

## Task Description Tips

- Be specific about scope and requirements

- Include context about existing codebase or constraints

- Specify desired output format

- Mention any coding standards or preferences

#

## Example Good Descriptions

```text
plaintext
✅ "Review authentication.py for SQL injection vulnerabilities and suggest fixes"
✅ "Write API documentation for the user management endpoints"  
✅ "Debug the connection timeout issue in database.py"

```text

#

## Example Poor Descriptions

```text
plaintext
❌ "Fix the code" (too vague)
❌ "Make the app better" (no specific goal)
❌ "Build a complete user system" (too complex for single task)
```text

#

# Troubleshooting Single Tasks

#

## Task Fails to Start

- Check task description specificity

- Verify workspace permissions

- Ensure MCP client is properly configured

#

## Incomplete Results

- Task may be more complex than expected

- Consider breaking into smaller subtasks

- Try with different specialist assignments

#

## Quality Issues

- Add more context in task description

- Specify coding standards or style preferences

- Use explicit requirements for output format

#

# Next Steps

- Try [multi-step workflows](../intermediate/project-planning.md)

- Learn about [specialist coordination](../intermediate/specialist-coordination.md)

- Explore [configuration options](configuration.md)
