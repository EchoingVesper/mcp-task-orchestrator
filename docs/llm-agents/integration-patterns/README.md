# LLM Agent Integration Patterns

*Character-optimized coordination patterns for multi-server workflows*

## Overview
Integration patterns define how to coordinate between Task Orchestrator and other MCP servers (especially Claude Code) for different execution scenarios and requirements.

## Available Patterns

### 🔄 [Sequential Coordination](sequential-coordination.md) **[CORE]**
**Use for**: File operations, complex workflows, multi-step processes
**Benefits**: No conflicts, clear dependencies, progress tracking
**Pattern**: Initialize → Plan → Execute → Complete → Synthesize

### ⚡ [Parallel Execution](parallel-execution.md)
**Use for**: Independent file operations, parallel analysis, concurrent validations
**Benefits**: Speed, resource efficiency, scalability
**Pattern**: Analyze Dependencies → Launch Parallel → Synchronize → Integrate

### 🛡️ [Graceful Degradation](graceful-degradation.md)
**Use for**: Critical deadlines, unreliable infrastructure, backup planning
**Benefits**: Continuity, fallback strategies, recovery procedures
**Pattern**: Detect Capability → Monitor Execution → Degrade Gracefully → Recover

### 🌐 [Multi-Server Coordination](multi-server-coordination.md)
**Use for**: Enterprise workflows, specialized tool requirements, complex integrations
**Benefits**: Specialized capabilities, complex data flows, enterprise scale
**Pattern**: Plan Multi-Server → Coordinate Execution → Cross-Server Synthesis

## Pattern Selection Guide
- **Single complex workflow**: Sequential Coordination
- **Independent parallel tasks**: Parallel Execution  
- **Mission-critical reliability**: Graceful Degradation
- **Multiple specialized servers**: Multi-Server Coordination

## Character Limits
Each pattern optimized for 1600-1800 characters to fit within LLM tool constraints while providing implementation details.