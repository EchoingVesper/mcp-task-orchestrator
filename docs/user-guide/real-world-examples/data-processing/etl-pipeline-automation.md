# ETL Pipeline Orchestration

*⭐ Featured Example: Multi-source data pipeline with parallel processing and quality gates*

## 🎯 Project Overview

**Scenario**: Daily processing of sales data from multiple sources (CRM, POS systems, web analytics) with data quality validation and automated reporting.

**Challenge**:
- 5 different data sources with varying formats and schedules
- Complex transformation rules requiring business logic validation
- Quality gates requiring human approval for anomalies
- Multiple output formats (database, reports, dashboards)
- Fault tolerance and recovery from partial failures

**Tools**: Task Orchestrator MCP + Claude Code MCP + Database connections + External APIs

## 🔄 Sequential Coordination Pattern in Action

### Phase 1: Pipeline Initialization and Validation

```bash
# 1. Initialize ETL orchestration session
orchestrator_initialize_session()
```

**Orchestrator Response**: ETL workflow guidance and checkpoint definitions

```bash
# 2. Create ETL task breakdown with parallel subtasks
orchestrator_plan_task({
  "description": "Execute daily sales data ETL pipeline with quality validation",
  "complexity_level": "complex",
  "subtasks_json": "[{
    \"title\": \"Data Source Validation\",
    \"description\": \"Verify all data sources are accessible and contain expected data\",
    \"specialist_type\": \"validator\"
  }, {
    \"title\": \"Parallel Data Extraction\", 
    \"description\": \"Extract data from all 5 sources simultaneously\",
    \"specialist_type\": \"extractor\"
  }, {
    \"title\": \"Data Quality Assessment\",
    \"description\": \"Validate data quality and flag anomalies for review\",
    \"specialist_type\": \"analyst\"
  }]"
})
```

**Result**: Pipeline task structure with dependency management
### Phase 2: Data Source Validation

```bash
# 3. Execute data source validation
orchestrator_execute_subtask("validator_abc123")
```

**Specialist Context**: Validator specialist with data verification expertise

**Claude Code Integration**: Source accessibility checks
```bash
# Using Claude Code for data source validation
- read_file: Check file-based sources for accessibility
- execute_command: Test database connections
- web_fetch: Validate API endpoints
- get_file_info: Verify file sizes and timestamps
```

**Validation Results**:
```yaml
data_sources:
  crm_database: ✅ accessible, 15,234 new records
  pos_files: ✅ accessible, 3 files, 45.2MB total
  web_analytics_api: ✅ accessible, rate_limit: 1000/hour
  inventory_csv: ⚠️ 2 hours delayed, but accessible
  financial_export: ❌ connection timeout - retry needed
```

**Quality Gate Decision**:
```bash
orchestrator_complete_subtask({
  "task_id": "validator_abc123",
  "results": "4/5 sources validated, financial export needs retry",
  "next_action": "continue",
  "artifacts": ["source_validation_report.json"]
})
```

### Phase 3: Parallel Data Extraction

```bash
# 4. Execute parallel extraction with graceful degradation
orchestrator_execute_subtask("extractor_def456")
```

**Coordination Pattern**: Orchestrator manages parallel execution strategy

**Claude Code Operations**: Actual data extraction and temporary storage
```bash
# Parallel extraction coordination
create_directory: /tmp/etl_staging_2025-05-30/
write_file: extraction_status.json (progress tracking)

# Source 1: CRM Database
execute_command: python extract_crm.py --date=2025-05-30
read_file: /tmp/etl_staging_2025-05-30/crm_data.json
```
## 🏆 Key Success Patterns

1. **Parallel Processing**: Multiple data sources processed simultaneously with status tracking
2. **Quality Gates**: Human review integration for anomaly approval
3. **Graceful Degradation**: Fallback strategies when sources are unavailable
4. **Error Recovery**: Retry logic and alternative data sources
5. **Progress Visibility**: Real-time status updates throughout pipeline execution

## 💡 Lessons Learned

- **Staging Strategy**: Temporary storage enables checkpoint recovery and debugging
- **Exception Handling**: Business context matters for anomaly approval decisions
- **Resource Coordination**: Clear file ownership prevents conflicts between tools
- **Performance Tracking**: Detailed metrics enable pipeline optimization
- **Human Integration**: Approval workflows require clear context and time estimates

## 🔧 Reusable Components

- **Validation Framework**: Adaptable to any data source configuration
- **Quality Assessment**: Statistical thresholds configurable per business domain  
- **Exception Handling**: Retry and fallback patterns for reliable execution
- **Output Flexibility**: Multi-format generation for diverse stakeholder needs

---
*📊 This pattern scales from simple daily reports to complex multi-source enterprise data warehouses*