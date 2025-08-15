

# Decision Documentation Database Schema

*Database design for architectural decision tracking*

#

# Core Tables

#

#

# Architectural Decisions

```sql
CREATE TABLE architectural_decisions (
    decision_id VARCHAR(36) PRIMARY KEY,
    decision_number INTEGER NOT NULL,
    subtask_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    specialist_type VARCHAR(50) NOT NULL,
    
    -- Decision Content
    title TEXT NOT NULL,
    category VARCHAR(30) NOT NULL,
    impact_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'proposed',
    problem_statement TEXT,
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT NOT NULL,
    implementation_approach TEXT,
    
    -- Relationships
    supersedes JSON, -- Array of decision IDs this replaces
    dependencies JSON, -- Array of decision IDs this depends on
    affected_files JSON,
    affected_components JSON,
    
    -- Quality Aspects
    alternatives_considered JSON,
    trade_offs JSON,
    risks JSON,
    mitigation_strategies JSON,
    success_criteria JSON,
    
    -- Implementation Tracking
    implementation_status VARCHAR(20) DEFAULT 'planned',
    outcome_assessment TEXT,
    lessons_learned TEXT,
    review_schedule DATETIME,
    
    -- Timestamps
    timestamp DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (subtask_id) REFERENCES subtasks(task_id)
);

```text

#

#

# Decision Evolution Tracking

```text
sql
CREATE TABLE decision_evolution (
    evolution_id VARCHAR(36) PRIMARY KEY,
    original_decision_id VARCHAR(36) NOT NULL,
    new_decision_id VARCHAR(36) NOT NULL,
    evolution_type VARCHAR(30) NOT NULL,
    evolution_reason TEXT,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (original_decision_id) REFERENCES architectural_decisions(decision_id),
    FOREIGN KEY (new_decision_id) REFERENCES architectural_decisions(decision_id)
);
```text
