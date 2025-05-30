# Data Processing Workflow Context

*1950 char limit - ETL and analytics coordination patterns*

## Context: Data Processing Projects
Use for ETL pipelines, analytics workflows, data transformation, and reporting automation.

## Workflow Pattern

### 1. Data Research and Planning (Researcher)
- Data source analysis, schema mapping, quality assessment
- Pipeline requirements, transformation logic design

### 2. Architecture Design (Architect)
- Pipeline architecture, data flow design, error handling strategy
- Performance optimization, scalability considerations

### 3. Implementation (Implementer)
- Data extraction, transformation scripts, loading mechanisms
- Pipeline orchestration, monitoring, logging systems

### 4. Validation and Testing (Tester)
- Data quality validation, pipeline testing, performance benchmarks
- Error scenarios, data consistency checks

## Integration with Claude Code

**Research**: Orchestrator analyzes requirements, Claude Code examines data files
**Architecture**: Orchestrator designs pipeline, Claude Code validates feasibility
**Implementation**: Orchestrator coordinates stages, Claude Code handles file ops
**Testing**: Combined validation and quality assurance

## Key Coordination Points
1. **Data Dependencies**: Sequence extraction, transformation, loading
2. **Quality Gates**: Validate each stage before proceeding
3. **Error Handling**: Robust failure recovery and retry logic
4. **Performance**: Monitor processing times and resource usage
5. **Documentation**: Maintain data lineage and transformation docs

## Specialist Assignments
- **Researcher**: Data analysis, source investigation, requirements
- **Architect**: Pipeline design, technology selection, optimization
- **Implementer**: Core processing logic, automation, orchestration
- **Tester**: Quality validation, performance testing, monitoring
- **Debugger**: Issue resolution, optimization, troubleshooting

**Use for**: ETL pipelines, data migration, analytics automation, reporting