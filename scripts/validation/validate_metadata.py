#!/usr/bin/env python3
"""
Validate Metadata in Documentation

This script validates YAML frontmatter metadata in documentation files
to ensure required fields are present and properly formatted.
"""

import os
import sys
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

@dataclass
class MetadataValidationResult:
    field_name: str
    level: ValidationLevel
    message: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    suggestion: Optional[str] = None

@dataclass
class FileMetadataReport:
    file_path: str
    has_metadata: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_results: List[MetadataValidationResult] = field(default_factory=list)
    missing_required_fields: List[str] = field(default_factory=list)
    invalid_field_values: List[str] = field(default_factory=list)
    extra_fields: List[str] = field(default_factory=list)
    is_valid: bool = False

class MetadataValidator:
    """Validates YAML frontmatter metadata in documentation files."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.required_fields = self.config['required_fields']
        self.optional_fields = self.config['optional_fields']
        self.field_validators = self._setup_field_validators()
        self.enum_values = self.config['enum_values']
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load validator configuration."""
        default_config = {
            'required_fields': {
                'title': {'type': 'string', 'min_length': 5, 'max_length': 100},
                'status': {'type': 'enum', 'values': ['DRAFT', 'REVIEW', 'APPROVED', 'IMPLEMENTED', 'COMPLETED', 'DEPRECATED']},
                'priority': {'type': 'enum', 'values': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']},
                'category': {'type': 'enum', 'values': ['CORE', 'ENHANCEMENT', 'INTEGRATION', 'PERFORMANCE', 'SECURITY', 'TESTING', 'DOCUMENTATION']},
                'version': {'type': 'version', 'pattern': r'^\\d+\\.\\d+(\\.\\d+)?$'},
                'description': {'type': 'string', 'min_length': 10, 'max_length': 500}
            },
            'optional_fields': {
                'author': {'type': 'string', 'min_length': 2, 'max_length': 50},
                'created': {'type': 'date'},
                'updated': {'type': 'date'},
                'tags': {'type': 'array', 'item_type': 'string'},
                'dependencies': {'type': 'array', 'item_type': 'string'},
                'related': {'type': 'array', 'item_type': 'string'},
                'assignee': {'type': 'string'},
                'reviewers': {'type': 'array', 'item_type': 'string'},
                'estimated_effort': {'type': 'string'},
                'complexity': {'type': 'enum', 'values': ['LOW', 'MEDIUM', 'HIGH']},
                'impact': {'type': 'enum', 'values': ['LOW', 'MEDIUM', 'HIGH']},
                'testing_required': {'type': 'boolean'},
                'breaking_change': {'type': 'boolean'},
                'documentation_required': {'type': 'boolean'}
            },
            'enum_values': {
                'status': ['DRAFT', 'REVIEW', 'APPROVED', 'IMPLEMENTED', 'COMPLETED', 'DEPRECATED'],
                'priority': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                'category': ['CORE', 'ENHANCEMENT', 'INTEGRATION', 'PERFORMANCE', 'SECURITY', 'TESTING', 'DOCUMENTATION'],
                'complexity': ['LOW', 'MEDIUM', 'HIGH'],
                'impact': ['LOW', 'MEDIUM', 'HIGH']
            },
            'validation_rules': {
                'title_case_required': True,
                'description_sentence_case': True,
                'tags_lowercase': True,
                'consistent_terminology': True,
                'no_placeholder_values': True
            },
            'terminology_standards': {
                'feature': 'enhancement',
                'bug': 'defect',
                'task': 'work item',
                'subtask': 'component'
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_field_validators(self) -> Dict:
        """Setup field-specific validators."""
        return {
            'string': self._validate_string_field,
            'enum': self._validate_enum_field,
            'version': self._validate_version_field,
            'date': self._validate_date_field,
            'array': self._validate_array_field,
            'boolean': self._validate_boolean_field,
            'number': self._validate_number_field
        }
    
    def validate_file(self, file_path: str) -> FileMetadataReport:
        """Validate metadata in a single file."""
        report = FileMetadataReport(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            report.validation_results.append(MetadataValidationResult(
                field_name="file_access",
                level=ValidationLevel.ERROR,
                message=f"Cannot read file: {e}"
            ))
            return report
        
        # Extract metadata
        metadata = self._extract_metadata(content, report)
        if metadata is None:
            return report
        
        report.has_metadata = True
        report.metadata = metadata
        
        # Validate required fields
        self._validate_required_fields(metadata, report)
        
        # Validate field values
        self._validate_field_values(metadata, report)
        
        # Check for extra fields
        self._check_extra_fields(metadata, report)
        
        # Additional validation rules
        self._apply_additional_validation_rules(metadata, report)
        
        # Determine overall validity
        report.is_valid = not any(result.level == ValidationLevel.ERROR for result in report.validation_results)
        
        return report
    
    def _extract_metadata(self, content: str, report: FileMetadataReport) -> Optional[Dict]:
        """Extract YAML frontmatter metadata."""
        if not content.strip():
            report.validation_results.append(MetadataValidationResult(
                field_name="file_content",
                level=ValidationLevel.ERROR,
                message="File is empty"
            ))
            return None
        
        if not content.startswith('---'):
            report.validation_results.append(MetadataValidationResult(
                field_name="frontmatter",
                level=ValidationLevel.ERROR,
                message="No YAML frontmatter found",
                suggestion="Add YAML frontmatter block at the beginning: ---\\n...\\n---"
            ))
            return None
        
        try:
            # Find the end of frontmatter
            lines = content.split('\\n')
            end_idx = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    end_idx = i
                    break
            
            if end_idx == -1:
                report.validation_results.append(MetadataValidationResult(
                    field_name="frontmatter",
                    level=ValidationLevel.ERROR,
                    message="Unclosed YAML frontmatter block",
                    suggestion="Add closing '---' after metadata"
                ))
                return None
            
            # Extract and parse YAML
            yaml_content = '\\n'.join(lines[1:end_idx])
            metadata = yaml.safe_load(yaml_content) or {}
            
            if not isinstance(metadata, dict):
                report.validation_results.append(MetadataValidationResult(
                    field_name="frontmatter",
                    level=ValidationLevel.ERROR,
                    message="YAML frontmatter must be a dictionary"
                ))
                return None
            
            return metadata
            
        except yaml.YAMLError as e:
            report.validation_results.append(MetadataValidationResult(
                field_name="frontmatter",
                level=ValidationLevel.ERROR,
                message=f"Invalid YAML syntax: {e}",
                suggestion="Fix YAML syntax errors"
            ))
            return None
    
    def _validate_required_fields(self, metadata: Dict, report: FileMetadataReport):
        """Validate that all required fields are present."""
        for field_name, field_config in self.required_fields.items():
            if field_name not in metadata:
                report.missing_required_fields.append(field_name)
                report.validation_results.append(MetadataValidationResult(
                    field_name=field_name,
                    level=ValidationLevel.ERROR,
                    message=f"Required field '{field_name}' is missing",
                    suggestion=f"Add '{field_name}' field to frontmatter"
                ))
            elif metadata[field_name] is None or metadata[field_name] == '':
                report.validation_results.append(MetadataValidationResult(
                    field_name=field_name,
                    level=ValidationLevel.ERROR,
                    message=f"Required field '{field_name}' is empty",
                    suggestion=f"Provide a value for '{field_name}'"
                ))
    
    def _validate_field_values(self, metadata: Dict, report: FileMetadataReport):
        """Validate field values according to their specifications."""
        all_fields = {**self.required_fields, **self.optional_fields}
        
        for field_name, value in metadata.items():
            if field_name in all_fields:
                field_config = all_fields[field_name]
                field_type = field_config['type']
                
                if field_type in self.field_validators:
                    validator = self.field_validators[field_type]
                    validator(field_name, value, field_config, report)
    
    def _validate_string_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate string field."""
        if not isinstance(value, str):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be a string",
                actual_value=str(type(value)),
                expected_value="string"
            ))
            return
        
        # Check length constraints
        if 'min_length' in config and len(value) < config['min_length']:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' is too short (minimum {config['min_length']} characters)",
                actual_value=str(len(value)),
                expected_value=f"≥{config['min_length']}"
            ))
        
        if 'max_length' in config and len(value) > config['max_length']:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.WARNING,
                message=f"Field '{field_name}' is too long (maximum {config['max_length']} characters)",
                actual_value=str(len(value)),
                expected_value=f"≤{config['max_length']}"
            ))
        
        # Check for placeholder values
        placeholder_patterns = [
            r'\\[.*\\]',  # [placeholder]
            r'TBD|To be determined',
            r'TODO|FIXME',
            r'Coming soon',
            r'Under construction',
            r'Placeholder'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                report.validation_results.append(MetadataValidationResult(
                    field_name=field_name,
                    level=ValidationLevel.WARNING,
                    message=f"Field '{field_name}' contains placeholder text",
                    actual_value=value,
                    suggestion="Replace placeholder with actual content"
                ))
                break
    
    def _validate_enum_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate enum field."""
        if not isinstance(value, str):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be a string",
                actual_value=str(type(value)),
                expected_value="string"
            ))
            return
        
        allowed_values = config.get('values', [])
        if value not in allowed_values:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Invalid value for '{field_name}'",
                actual_value=value,
                expected_value=f"One of: {', '.join(allowed_values)}",
                suggestion=f"Use one of the allowed values: {', '.join(allowed_values)}"
            ))
    
    def _validate_version_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate version field."""
        if not isinstance(value, (str, int, float)):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be a string or number",
                actual_value=str(type(value)),
                expected_value="string or number"
            ))
            return
        
        value_str = str(value)
        pattern = config.get('pattern', r'^\\d+\\.\\d+(\\.\\d+)?$')
        
        if not re.match(pattern, value_str):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Invalid version format for '{field_name}'",
                actual_value=value_str,
                expected_value="Semantic version (e.g., 1.0.0)",
                suggestion="Use semantic versioning format: MAJOR.MINOR.PATCH"
            ))
    
    def _validate_date_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate date field."""
        if isinstance(value, str):
            # Try to parse ISO date
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                # Try common date formats
                date_formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d']
                parsed = False
                for fmt in date_formats:
                    try:
                        datetime.strptime(value, fmt)
                        parsed = True
                        break
                    except ValueError:
                        continue
                
                if not parsed:
                    report.validation_results.append(MetadataValidationResult(
                        field_name=field_name,
                        level=ValidationLevel.ERROR,
                        message=f"Invalid date format for '{field_name}'",
                        actual_value=value,
                        expected_value="ISO date format (YYYY-MM-DD)",
                        suggestion="Use ISO date format: YYYY-MM-DD"
                    ))
        else:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be a date string",
                actual_value=str(type(value)),
                expected_value="date string"
            ))
    
    def _validate_array_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate array field."""
        if not isinstance(value, list):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be an array",
                actual_value=str(type(value)),
                expected_value="array"
            ))
            return
        
        # Validate array items
        item_type = config.get('item_type', 'string')
        for i, item in enumerate(value):
            if item_type == 'string' and not isinstance(item, str):
                report.validation_results.append(MetadataValidationResult(
                    field_name=f"{field_name}[{i}]",
                    level=ValidationLevel.ERROR,
                    message=f"Array item in '{field_name}' must be a string",
                    actual_value=str(type(item)),
                    expected_value="string"
                ))
        
        # Check for duplicates
        if len(value) != len(set(value)):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.WARNING,
                message=f"Array '{field_name}' contains duplicate values",
                suggestion="Remove duplicate entries"
            ))
    
    def _validate_boolean_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate boolean field."""
        if not isinstance(value, bool):
            # Accept string representations
            if isinstance(value, str) and value.lower() in ['true', 'false', 'yes', 'no']:
                # This is acceptable but warn about format
                report.validation_results.append(MetadataValidationResult(
                    field_name=field_name,
                    level=ValidationLevel.INFO,
                    message=f"Field '{field_name}' should use boolean true/false",
                    actual_value=value,
                    expected_value="true or false",
                    suggestion="Use boolean values (true/false) instead of strings"
                ))
            else:
                report.validation_results.append(MetadataValidationResult(
                    field_name=field_name,
                    level=ValidationLevel.ERROR,
                    message=f"Field '{field_name}' must be a boolean",
                    actual_value=str(type(value)),
                    expected_value="boolean (true/false)"
                ))
    
    def _validate_number_field(self, field_name: str, value: Any, config: Dict, report: FileMetadataReport):
        """Validate number field."""
        if not isinstance(value, (int, float)):
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' must be a number",
                actual_value=str(type(value)),
                expected_value="number"
            ))
            return
        
        # Check range constraints
        if 'min_value' in config and value < config['min_value']:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' is below minimum value",
                actual_value=str(value),
                expected_value=f"≥{config['min_value']}"
            ))
        
        if 'max_value' in config and value > config['max_value']:
            report.validation_results.append(MetadataValidationResult(
                field_name=field_name,
                level=ValidationLevel.ERROR,
                message=f"Field '{field_name}' is above maximum value",
                actual_value=str(value),
                expected_value=f"≤{config['max_value']}"
            ))
    
    def _check_extra_fields(self, metadata: Dict, report: FileMetadataReport):
        """Check for extra fields not in the specification."""
        all_fields = set(self.required_fields.keys()) | set(self.optional_fields.keys())
        extra_fields = set(metadata.keys()) - all_fields
        
        for field in extra_fields:
            report.extra_fields.append(field)
            report.validation_results.append(MetadataValidationResult(
                field_name=field,
                level=ValidationLevel.WARNING,
                message=f"Unexpected field '{field}' found",
                suggestion="Remove field or add to specification if needed"
            ))
    
    def _apply_additional_validation_rules(self, metadata: Dict, report: FileMetadataReport):
        """Apply additional validation rules."""
        rules = self.config.get('validation_rules', {})
        
        # Title case validation
        if rules.get('title_case_required', False) and 'title' in metadata:
            title = metadata['title']
            if isinstance(title, str) and not self._is_title_case(title):
                report.validation_results.append(MetadataValidationResult(
                    field_name='title',
                    level=ValidationLevel.WARNING,
                    message="Title should use title case",
                    actual_value=title,
                    suggestion="Capitalize first letter of each major word"
                ))
        
        # Description sentence case
        if rules.get('description_sentence_case', False) and 'description' in metadata:
            description = metadata['description']
            if isinstance(description, str) and description and not description[0].isupper():
                report.validation_results.append(MetadataValidationResult(
                    field_name='description',
                    level=ValidationLevel.WARNING,
                    message="Description should start with capital letter",
                    actual_value=description,
                    suggestion="Start description with a capital letter"
                ))
        
        # Tags lowercase
        if rules.get('tags_lowercase', False) and 'tags' in metadata:
            tags = metadata['tags']
            if isinstance(tags, list):
                for i, tag in enumerate(tags):
                    if isinstance(tag, str) and tag != tag.lower():
                        report.validation_results.append(MetadataValidationResult(
                            field_name=f'tags[{i}]',
                            level=ValidationLevel.WARNING,
                            message=f"Tag '{tag}' should be lowercase",
                            actual_value=tag,
                            expected_value=tag.lower(),
                            suggestion="Use lowercase for tags"
                        ))
        
        # Terminology consistency
        if rules.get('consistent_terminology', False):
            self._check_terminology_consistency(metadata, report)
        
        # Status progression validation
        self._validate_status_progression(metadata, report)
    
    def _is_title_case(self, title: str) -> bool:
        """Check if title uses proper title case."""
        # Simple title case check - can be enhanced
        words = title.split()
        if not words:
            return True
        
        # First word should be capitalized
        if not words[0][0].isupper():
            return False
        
        # Other major words should be capitalized (excluding articles, prepositions)
        minor_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        for word in words[1:]:
            if len(word) > 3 and word.lower() not in minor_words and not word[0].isupper():
                return False
        
        return True
    
    def _check_terminology_consistency(self, metadata: Dict, report: FileMetadataReport):
        """Check for consistent terminology usage."""
        terminology = self.config.get('terminology_standards', {})
        
        # Check text fields for deprecated terminology
        text_fields = ['title', 'description']
        for field_name in text_fields:
            if field_name in metadata and isinstance(metadata[field_name], str):
                text = metadata[field_name].lower()
                for old_term, new_term in terminology.items():
                    if old_term in text:
                        report.validation_results.append(MetadataValidationResult(
                            field_name=field_name,
                            level=ValidationLevel.INFO,
                            message=f"Consider using '{new_term}' instead of '{old_term}'",
                            suggestion="Update terminology for consistency"
                        ))
    
    def _validate_status_progression(self, metadata: Dict, report: FileMetadataReport):
        """Validate logical status progression."""
        if 'status' not in metadata:
            return
        
        status = metadata['status']
        
        # Check for logical inconsistencies
        if status == 'COMPLETED' and metadata.get('priority') == 'CRITICAL':
            report.validation_results.append(MetadataValidationResult(
                field_name='status',
                level=ValidationLevel.INFO,
                message="Completed items typically don't need critical priority",
                suggestion="Consider updating priority for completed items"
            ))
        
        if status == 'DEPRECATED' and metadata.get('version'):
            # Check if version looks current
            version = str(metadata['version'])
            if not re.search(r'0\\.[0-9]', version):  # Not a 0.x version
                report.validation_results.append(MetadataValidationResult(
                    field_name='status',
                    level=ValidationLevel.WARNING,
                    message="Deprecated item has current version number",
                    suggestion="Verify deprecation status or update version"
                ))
    
    def validate_directory(self, directory_path: str, pattern: str = "*.md") -> List[FileMetadataReport]:
        """Validate metadata in all files in a directory."""
        reports = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                report = self.validate_file(str(file_path))
                reports.append(report)
        
        return reports
    
    def generate_summary_report(self, reports: List[FileMetadataReport]) -> Dict:
        """Generate summary report from all validation results."""
        summary = {
            'total_files': len(reports),
            'files_with_metadata': sum(1 for r in reports if r.has_metadata),
            'valid_files': sum(1 for r in reports if r.is_valid),
            'files_with_errors': sum(1 for r in reports if any(res.level == ValidationLevel.ERROR for res in r.validation_results)),
            'files_with_warnings': sum(1 for r in reports if any(res.level == ValidationLevel.WARNING for res in r.validation_results)),
            'total_errors': sum(len([res for res in r.validation_results if res.level == ValidationLevel.ERROR]) for r in reports),
            'total_warnings': sum(len([res for res in r.validation_results if res.level == ValidationLevel.WARNING]) for r in reports),
            'common_missing_fields': {},
            'common_validation_issues': {},
            'metadata_coverage': 0.0,
            'validation_rate': 0.0
        }
        
        if summary['total_files'] > 0:
            summary['metadata_coverage'] = summary['files_with_metadata'] / summary['total_files']
        
        if summary['files_with_metadata'] > 0:
            summary['validation_rate'] = summary['valid_files'] / summary['files_with_metadata']
        
        # Analyze common issues
        missing_field_counts = {}
        issue_counts = {}
        
        for report in reports:
            for field in report.missing_required_fields:
                missing_field_counts[field] = missing_field_counts.get(field, 0) + 1
            
            for result in report.validation_results:
                if result.level in [ValidationLevel.ERROR, ValidationLevel.WARNING]:
                    issue_key = f"{result.level.value}: {result.message.split('.')[0]}"
                    issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
        
        summary['common_missing_fields'] = dict(sorted(missing_field_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        summary['common_validation_issues'] = dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        return summary

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate metadata in documentation files')
    parser.add_argument('path', help='File or directory path to validate')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text'], default='text', help='Output format')
    parser.add_argument('--level', choices=['error', 'warning', 'info'], default='warning', 
                       help='Minimum validation level to report')
    parser.add_argument('--field', help='Validate specific field only')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    parser.add_argument('--fail-on-missing', action='store_true', help='Fail if any files lack metadata')
    
    args = parser.parse_args()
    
    validator = MetadataValidator(args.config)
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run validation
    if path.is_file():
        reports = [validator.validate_file(str(path))]
    else:
        reports = validator.validate_directory(str(path))
    
    if not reports:
        print("No files found to validate")
        return 0
    
    # Apply filters
    level_map = {'error': [ValidationLevel.ERROR], 
                'warning': [ValidationLevel.ERROR, ValidationLevel.WARNING],
                'info': [ValidationLevel.ERROR, ValidationLevel.WARNING, ValidationLevel.INFO]}
    allowed_levels = level_map[args.level]
    
    if args.field:
        for report in reports:
            report.validation_results = [res for res in report.validation_results 
                                       if res.field_name == args.field and res.level in allowed_levels]
    else:
        for report in reports:
            report.validation_results = [res for res in report.validation_results 
                                       if res.level in allowed_levels]
    
    # Generate summary
    summary = validator.generate_summary_report(reports)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'summary': summary,
            'reports': [
                {
                    'file_path': r.file_path,
                    'has_metadata': r.has_metadata,
                    'is_valid': r.is_valid,
                    'metadata': r.metadata,
                    'missing_required_fields': r.missing_required_fields,
                    'invalid_field_values': r.invalid_field_values,
                    'extra_fields': r.extra_fields,
                    'validation_results': [
                        {
                            'field_name': res.field_name,
                            'level': res.level.value,
                            'message': res.message,
                            'expected_value': res.expected_value,
                            'actual_value': res.actual_value,
                            'suggestion': res.suggestion
                        } for res in r.validation_results
                    ]
                } for r in reports
            ]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
        else:
            print(json.dumps(output_data, indent=2))
    
    else:
        # Text output
        if not args.quiet:
            print("Metadata Validation Report")
            print("=" * 50)
            print(f"Total Files: {summary['total_files']}")
            print(f"Files with Metadata: {summary['files_with_metadata']}")
            print(f"Valid Files: {summary['valid_files']}")
            print(f"Files with Errors: {summary['files_with_errors']}")
            print(f"Files with Warnings: {summary['files_with_warnings']}")
            print(f"Metadata Coverage: {summary['metadata_coverage']:.1%}")
            print(f"Validation Rate: {summary['validation_rate']:.1%}")
            print()
            
            # Show common missing fields
            if summary['common_missing_fields']:
                print("Most Common Missing Fields:")
                print("-" * 30)
                for field, count in summary['common_missing_fields'].items():
                    print(f"  {field}: {count} files")
                print()
            
            # Show files with issues
            problem_reports = [r for r in reports if r.validation_results]
            if problem_reports:
                print("Files with Validation Issues:")
                print("-" * 35)
                for report in problem_reports[:10]:  # Limit to first 10
                    print(f"\\n{report.file_path}:")
                    if not report.has_metadata:
                        print("  No metadata found")
                    else:
                        for result in report.validation_results[:5]:  # Limit to first 5 per file
                            print(f"  {result.level.value}: {result.field_name} - {result.message}")
                            if result.suggestion:
                                print(f"    Suggestion: {result.suggestion}")
        
        # Save text report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write("Metadata Validation Summary\\n")
                f.write(f"Coverage: {summary['metadata_coverage']:.1%}, Validation Rate: {summary['validation_rate']:.1%}\\n")
                f.write(f"Errors: {summary['total_errors']}, Warnings: {summary['total_warnings']}\\n\\n")
                
                for report in reports:
                    if report.validation_results:
                        f.write(f"File: {report.file_path}\\n")
                        f.write(f"Valid: {report.is_valid}, Has Metadata: {report.has_metadata}\\n")
                        for result in report.validation_results:
                            f.write(f"  {result.level.value}: {result.field_name} - {result.message}\\n")
                        f.write("\\n")
    
    # Return appropriate exit code
    if summary['total_errors'] > 0:
        return 1
    if args.fail_on_missing and summary['files_with_metadata'] < summary['total_files']:
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())