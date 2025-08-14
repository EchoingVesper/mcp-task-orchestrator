# Tracking Directory - Progress and Session Management

This directory tracks Meta-PRP execution progress and orchestrator sessions.

## Contents
- `checklist.md` - Master tracking checklist (manually maintained)
- `session-logs/` - Orchestrator session records (auto-generated)
- `progress-reports/` - Periodic progress summaries (auto-generated)
- `artifacts/` - References to orchestrator artifacts
- `errors/` - Error logs and recovery information

## Session Management
Each orchestrator session creates a log file:
- `session_{id}_{timestamp}.json` - Full session record
- `session_{id}_artifacts.md` - Artifact references
- `session_{id}_status.md` - Final status report

## Executive Dysfunction Support
This tracking system provides:
- Multiple granularities of progress visibility
- Context preservation across interruptions
- Automatic progress recording
- Clear recovery points when overwhelmed