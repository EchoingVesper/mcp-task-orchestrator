# Sales Analytics Pipeline
*Real-time business intelligence with automated insights generation*

## 🎯 Project Overview
**Scenario**: Transform raw sales CSV files into executive dashboards with automated trend analysis.
**Challenge**: Multiple CSV formats, statistical analysis, automated chart generation, mobile delivery
**Tools**: Task Orchestrator MCP + Claude Code MCP + Python analytics stack

## 🔄 Workflow Coordination
```bash
orchestrator_plan_task({
  "description": "Process daily sales data into executive analytics dashboard",
  "subtasks_json": "[{
    \"title\": \"CSV Format Detection and Standardization\",
    \"specialist_type\": \"analyst\"
  }, {
    \"title\": \"Statistical Analysis and Trend Detection\", 
    \"specialist_type\": \"data_scientist\"
  }, {
    \"title\": \"Interactive Dashboard Generation\",
    \"specialist_type\": \"implementer\"
  }]"
})
```

## 🔄 Key Coordination Patterns
**Orchestrator Role**: Data science specialist context for complex analytics
**Claude Code Role**: File operations, Python script execution, chart generation

```bash
# Data analysis coordination
read_multiple_files: [sales_region_a.csv, sales_region_b.csv, sales_online.csv]
execute_command: python sales_analyzer.py --detect-anomalies --confidence=95%
write_file: insights_report.json

# Generate executive summary
execute_command: python generate_insights.py --executive-level
write_file: dashboard/sales_dashboard.html
```

## 🏆 Success Metrics
- **Processing Time**: 3-minute end-to-end pipeline
- **Automation Level**: 95% automated with intelligent exception handling
- **Insight Accuracy**: Statistical significance testing for all trend claims

---
*📈 Demonstrates sophisticated analytics automation with orchestration*