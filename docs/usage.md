# MCP Task Orchestrator - Usage Guide

This guide explains how to use the MCP Task Orchestrator effectively in your LLM interactions.

## Overview

The MCP Task Orchestrator provides specialized prompting and task management capabilities through a set of tools that can be called by the LLM. These tools allow the LLM to break down complex tasks, switch between specialist roles, and track progress.

## Available Tools

The MCP Task Orchestrator provides the following tools:

1. `orchestrator_plan_task` - Break down a complex task into specialized subtasks
2. `orchestrator_execute_subtask` - Get specialist context for a specific subtask
3. `orchestrator_complete_subtask` - Mark a subtask as complete and record results
4. `orchestrator_synthesize_results` - Combine results from completed subtasks
5. `orchestrator_get_status` - Check the status of all active tasks

## Typical Workflow

A typical workflow using the MCP Task Orchestrator follows these steps:

1. **Task Planning**: The LLM calls `orchestrator_plan_task` to break down a complex task
2. **Subtask Execution**: For each subtask, the LLM calls `orchestrator_execute_subtask` to get specialist context
3. **Subtask Completion**: After completing a subtask, the LLM calls `orchestrator_complete_subtask` to record results
4. **Result Synthesis**: Once all subtasks are complete, the LLM calls `orchestrator_synthesize_results` to combine the results
5. **Status Checking**: At any point, the LLM can call `orchestrator_get_status` to check progress

## Example Usage

### Software Development Task

Let's say you want to build a web scraper for e-commerce prices. Here's how you might use the MCP Task Orchestrator:

1. **Task Planning**:
   ```
   User: "I need to build a web scraper for e-commerce product prices with error handling, data export, and monitoring capabilities."
   
   LLM: "I'll help you build a web scraper. Let me break this down into manageable subtasks."
   
   LLM calls: orchestrator_plan_task with description="Build a web scraper for e-commerce product prices with error handling, data export, and monitoring capabilities"
   
   Server responds with breakdown:
   - Architecture & Design (architect)
   - Core Implementation (implementer) 
   - Error Handling System (debugger)
   - Data Export Module (implementer)
   - Monitoring & Logging (implementer)
   - Documentation (documenter)
   ```2. **Subtask Execution**:
   ```
   LLM: "Let's start with the architecture and design. I'll switch to architect mode to design the system."
   
   LLM calls: orchestrator_execute_subtask with task_id="architecture_123"
   
   Server responds with specialist context for an architect, including:
   - Role definition
   - Expertise areas
   - Approach guidelines
   - Output format expectations
   - Task-specific instructions
   
   LLM (as Architect): "Here's my architecture design for the web scraper..."
   [Provides detailed architecture document]
   ```

3. **Subtask Completion**:
   ```
   LLM calls: orchestrator_complete_subtask with:
     - task_id="architecture_123"
     - results="Completed architecture design with component diagram and data flow"
     - artifacts=["architecture.md", "component_diagram.png"]
     - next_action="continue"
   
   Server responds with confirmation and suggests the next subtask
   ```

4. **Next Subtask**:
   ```
   LLM: "Now let's implement the core scraper functionality."
   
   LLM calls: orchestrator_execute_subtask with task_id="implementation_456"
   
   Server responds with specialist context for an implementer
   
   LLM (as Implementer): "Here's the implementation of the core scraper..."
   [Provides code implementation]
   ```

5. **Result Synthesis**:
   ```
   [After completing all subtasks]
   
   LLM calls: orchestrator_synthesize_results with parent_task_id="main_task_789"
   
   Server responds with a synthesis of all subtask results
   
   LLM: "I've completed the web scraper project. Here's a summary of what was accomplished..."
   ```

### Code Review Task

Another example for a code review task:

```
User: "Can you review my Python codebase and suggest performance improvements?"

LLM calls: orchestrator_plan_task with description="Review Python codebase and suggest performance improvements"

Server responds with breakdown:
- Initial Code Analysis (researcher)
- Quality Review (reviewer)
- Performance Analysis (debugger)
- Optimization Recommendations (implementer)

LLM executes each subtask with the appropriate specialist context
```## Best Practices

To get the most out of the MCP Task Orchestrator, follow these best practices:

### Task Planning

1. **Be Specific**: Provide detailed descriptions when planning tasks to get better breakdowns
2. **Consider Complexity**: Specify the complexity level (simple, moderate, complex, very_complex) for more appropriate task breakdowns
3. **Include Context**: Add relevant context information to help the task planning process

Example:
```
orchestrator_plan_task with:
  description="Build a REST API for user management with authentication, authorization, and profile management"
  complexity_level="complex"
  context="Using Node.js with Express and MongoDB, following security best practices"
```

### Specialist Execution

1. **Follow the Specialist Role**: When executing a subtask, fully embrace the specialist role provided
2. **Complete One Task at a Time**: Focus on completing one subtask before moving to the next
3. **Respect Dependencies**: Follow the recommended task order to respect dependencies between subtasks

### Task Completion

1. **Provide Detailed Results**: Include comprehensive summaries when completing subtasks
2. **List All Artifacts**: Document all artifacts created during the subtask
3. **Choose the Right Next Action**:
   - `continue`: Move to the next subtask
   - `needs_revision`: The current subtask needs more work
   - `blocked`: The subtask is blocked by external factors
   - `complete`: The subtask is complete and no further action is needed

### Result Synthesis

1. **Wait for All Subtasks**: Ensure all subtasks are complete before synthesizing results
2. **Review All Contributions**: Consider the outputs from all specialist roles
3. **Provide a Cohesive Summary**: Create a unified summary that integrates all subtask results

## Advanced Usage

### Handling Revisions

If a subtask needs revision:

```
orchestrator_complete_subtask with:
  task_id="implementation_456"
  results="Initial implementation completed but needs optimization"
  artifacts=["scraper.py"]
  next_action="needs_revision"
```

Then execute the same subtask again:

```
orchestrator_execute_subtask with task_id="implementation_456"
```

### Handling Blocked Tasks

If a subtask is blocked:

```
orchestrator_complete_subtask with:
  task_id="deployment_789"
  results="Deployment preparation complete but blocked by missing credentials"
  artifacts=["deployment_guide.md"]
  next_action="blocked"
```### Checking Task Status

You can check the status of all active tasks at any time:

```
orchestrator_get_status with:
  include_completed=false
```

To include completed tasks in the status:

```
orchestrator_get_status with:
  include_completed=true
```

The status response includes:
- Active parent tasks
- Subtasks for each parent task
- Completion status
- Dependencies
- Results and artifacts

### Multi-Session Support

The MCP Task Orchestrator maintains state between sessions, allowing you to:

1. Start a complex task in one session
2. Continue working on subtasks in later sessions
3. Track progress across multiple interactions

To resume work on an existing task:

```
orchestrator_get_status with:
  include_completed=true
```

Then continue with the next pending subtask.

## Troubleshooting

### Task Planning Issues

If task planning doesn't produce the expected breakdown:

1. **Be More Specific**: Provide more details in the task description
2. **Adjust Complexity**: Try a different complexity level
3. **Add Context**: Provide relevant context information

### Specialist Context Issues

If the specialist context doesn't match your expectations:

1. **Check Specialist Type**: Verify you're using the correct specialist type for the task
2. **Customize Templates**: Modify the specialist templates in the configuration
3. **Provide Feedback**: Complete the subtask with detailed feedback

### Task Tracking Issues

If tasks aren't being tracked correctly:

1. **Check Task IDs**: Ensure you're using the correct task IDs
2. **Verify Completion**: Make sure subtasks are properly marked as complete
3. **Check Database**: Verify the database file exists and is accessible

## Conclusion

The MCP Task Orchestrator provides powerful capabilities for breaking down complex tasks, switching between specialist roles, and tracking progress. By following the workflow and best practices described in this guide, you can effectively leverage these capabilities to handle complex tasks more efficiently.

For more information, see:
- [Installation Guide](installation.md)
- [Configuration Guide](configuration.md)
- [API Reference](api.md)
- [Examples](examples/README.md)