-- Emergency Database Schema Fix
-- Adds missing columns to subtasks table

-- Add verification_status column
ALTER TABLE subtasks ADD COLUMN verification_status TEXT DEFAULT 'pending';

-- Add prerequisite_satisfaction_required column  
ALTER TABLE subtasks ADD COLUMN prerequisite_satisfaction_required BOOLEAN DEFAULT 0;

-- Add auto_maintenance_enabled column
ALTER TABLE subtasks ADD COLUMN auto_maintenance_enabled BOOLEAN DEFAULT 1;

-- Add quality_gate_level column
ALTER TABLE subtasks ADD COLUMN quality_gate_level TEXT DEFAULT 'standard';

-- Verify the fix by checking table structure
.schema subtasks
