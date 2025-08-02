"""
Multi-Stage Validation Pipeline

A comprehensive validation framework for the MCP Task Orchestrator that executes
5 sequential validation stages:

1. Syntax & Static Analysis
2. Unit Test Validation  
3. Integration Test Validation
4. Security & Performance Validation
5. Production Readiness Validation

Each stage must pass completely before the next stage executes, ensuring
comprehensive quality validation and production readiness.
"""

from .pipeline_orchestrator import ValidationPipelineOrchestrator
from .models import (
    ValidationStatus, SeverityLevel, ValidationIssue, StageMetrics,
    ValidationResult, PipelineResult, PipelineConfig, ToolResult
)
from .base_stage import ValidationStageBase
from .stage_1_syntax import SyntaxValidationStage
from .stage_2_unit import UnitTestStage
from .stage_3_integration import IntegrationTestStage
from .stage_4_security_performance import SecurityPerformanceStage
from .stage_5_production import ProductionReadinessStage

__version__ = '2.0.0'
__all__ = [
    # Main orchestrator
    'ValidationPipelineOrchestrator',
    
    # Data models
    'ValidationStatus',
    'SeverityLevel', 
    'ValidationIssue',
    'StageMetrics',
    'ValidationResult',
    'PipelineResult',
    'PipelineConfig',
    'ToolResult',
    
    # Base classes
    'ValidationStageBase',
    
    # Stage implementations
    'SyntaxValidationStage',
    'UnitTestStage', 
    'IntegrationTestStage',
    'SecurityPerformanceStage',
    'ProductionReadinessStage'
]