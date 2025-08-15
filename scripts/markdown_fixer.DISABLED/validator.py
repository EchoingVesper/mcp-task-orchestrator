"""
Markdown Validator for running markdownlint and parsing results.

Provides comprehensive validation capabilities and error parsing.
"""

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class MarkdownError:
    """Represents a markdownlint error."""
    rule: str
    line: int
    column: int
    message: str
    severity: str = "error"
    file_path: Optional[Path] = None


class MarkdownValidator:
    """Validates markdown files using markdownlint."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize validator.
        
        Args:
            config_path: Path to markdownlint config file
        """
        self.config_path = config_path or Path(".markdownlint.json")
        self.markdownlint_available = self._check_markdownlint()
    
    def _check_markdownlint(self) -> bool:
        """Check if markdownlint is available."""
        try:
            result = subprocess.run(
                ['markdownlint', '--version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def validate_file(self, file_path: Path) -> List[MarkdownError]:
        """
        Validate a single markdown file.
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            List of validation errors
        """
        if not self.markdownlint_available:
            raise RuntimeError("markdownlint is not available. Install with: npm install -g markdownlint-cli")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        cmd = ['markdownlint', str(file_path)]
        if self.config_path.exists():
            cmd.extend(['--config', str(self.config_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # markdownlint outputs to stderr when there are errors
            output = result.stderr if result.stderr else result.stdout
            return self._parse_output(output, file_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"markdownlint timed out for file: {file_path}")
    
    def validate_files(self, file_paths: List[Path]) -> Dict[Path, List[MarkdownError]]:
        """
        Validate multiple markdown files.
        
        Args:
            file_paths: List of file paths to validate
            
        Returns:
            Dictionary mapping file paths to their errors
        """
        results = {}
        
        for file_path in file_paths:
            try:
                errors = self.validate_file(file_path)
                results[file_path] = errors
            except Exception as e:
                # Create an error object for processing failures
                error = MarkdownError(
                    rule="VALIDATOR_ERROR",
                    line=0,
                    column=0,
                    message=str(e),
                    severity="error",
                    file_path=file_path
                )
                results[file_path] = [error]
        
        return results
    
    def validate_directory(self, directory: Path, exclude_patterns: Optional[List[str]] = None) -> Dict[Path, List[MarkdownError]]:
        """
        Validate all markdown files in a directory.
        
        Args:
            directory: Directory to scan
            exclude_patterns: Glob patterns to exclude
            
        Returns:
            Dictionary mapping file paths to their errors
        """
        exclude_patterns = exclude_patterns or []
        
        # Find all markdown files
        md_files = []
        for pattern in ['*.md', '**/*.md']:
            md_files.extend(directory.glob(pattern))
        
        # Filter out excluded files
        filtered_files = []
        for file_path in md_files:
            excluded = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)
        
        return self.validate_files(filtered_files)
    
    def _parse_output(self, output: str, file_path: Path) -> List[MarkdownError]:
        """
        Parse markdownlint output into error objects.
        
        Args:
            output: Raw markdownlint output
            file_path: File that was validated
            
        Returns:
            List of parsed errors
        """
        errors = []
        
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
                
            # Parse markdownlint output format:
            # file:line rule/rule-alias message [context]
            # or file:line:column rule/rule-alias message [context]
            
            # Use regex to properly parse the line
            # Pattern: filename:line:column? rule message
            # Account for optional column and space after line number
            match = re.match(r'^([^:]+):(\d+)(?::(\d+))?\s+(\S+)\s+(.+)$', line.strip())
            
            if match:
                file_part, line_num, col_num, rule, message = match.groups()
                
                # Remove context information in brackets at the end
                if message.endswith(']') and '[' in message:
                    bracket_index = message.rfind('[')
                    if bracket_index > 0:
                        message = message[:bracket_index].strip()
                
                error = MarkdownError(
                    rule=rule,
                    line=int(line_num),
                    column=int(col_num) if col_num else 0,
                    message=message,
                    file_path=file_path
                )
                errors.append(error)
        
        return errors
    
    def get_error_summary(self, results: Dict[Path, List[MarkdownError]]) -> Dict[str, int]:
        """
        Get summary of error counts by rule.
        
        Args:
            results: Validation results
            
        Returns:
            Dictionary mapping rule names to error counts
        """
        summary = {}
        
        for errors in results.values():
            for error in errors:
                rule = error.rule
                summary[rule] = summary.get(rule, 0) + 1
        
        return summary
    
    def get_total_errors(self, results: Dict[Path, List[MarkdownError]]) -> int:
        """
        Get total number of errors.
        
        Args:
            results: Validation results
            
        Returns:
            Total error count
        """
        return sum(len(errors) for errors in results.values())
    
    def filter_errors_by_rule(self, results: Dict[Path, List[MarkdownError]], rules: List[str]) -> Dict[Path, List[MarkdownError]]:
        """
        Filter errors to only include specific rules.
        
        Args:
            results: Validation results
            rules: List of rule names to include
            
        Returns:
            Filtered results
        """
        filtered = {}
        
        for file_path, errors in results.items():
            filtered_errors = [error for error in errors if error.rule in rules]
            if filtered_errors:
                filtered[file_path] = filtered_errors
        
        return filtered
    
    def export_results(self, results: Dict[Path, List[MarkdownError]], output_path: Path) -> None:
        """
        Export validation results to JSON file.
        
        Args:
            results: Validation results
            output_path: Path to output file
        """
        export_data = {
            "summary": self.get_error_summary(results),
            "total_errors": self.get_total_errors(results),
            "files": {}
        }
        
        for file_path, errors in results.items():
            export_data["files"][str(file_path)] = [
                {
                    "rule": error.rule,
                    "line": error.line,
                    "column": error.column,
                    "message": error.message,
                    "severity": error.severity
                }
                for error in errors
            ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
    
    def is_markdownlint_available(self) -> bool:
        """Check if markdownlint is available."""
        return self.markdownlint_available