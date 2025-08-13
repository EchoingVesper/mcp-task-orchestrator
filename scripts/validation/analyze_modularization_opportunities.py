#!/usr/bin/env python3
"""
Analyze Documentation Modularization Opportunities

This script analyzes documentation files to identify opportunities for modularization,
including duplicate content, large files, and logical separation points.
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from difflib import SequenceMatcher

@dataclass
class DuplicateContent:
    content: str
    files: List[str]
    line_ranges: List[Tuple[int, int]]
    similarity: float
    suggestion: str

@dataclass
class ModularizationOpportunity:
    file_path: str
    opportunity_type: str
    description: str
    suggestion: str
    priority: str
    affected_lines: Optional[Tuple[int, int]] = None
    related_files: List[str] = field(default_factory=list)
    estimated_impact: str = "medium"

@dataclass
class FileAnalysis:
    file_path: str
    total_lines: int
    section_count: int
    largest_section: Tuple[str, int]
    duplicate_content: List[DuplicateContent] = field(default_factory=list)
    opportunities: List[ModularizationOpportunity] = field(default_factory=list)
    complexity_score: float = 0.0
    modularity_score: float = 0.0

class DocumentationModularizationAnalyzer:
    """Analyzes documentation for modularization opportunities."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.min_duplicate_lines = self.config.get('min_duplicate_lines', 5)
        self.min_similarity = self.config.get('min_similarity', 0.8)
        self.max_file_lines = self.config.get('max_file_lines', 500)
        self.max_section_lines = self.config.get('max_section_lines', 100)
        self.content_hashes = defaultdict(list)
        self.section_patterns = self._compile_section_patterns()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load analyzer configuration."""
        default_config = {
            'min_duplicate_lines': 5,
            'min_similarity': 0.8,
            'max_file_lines': 500,
            'max_section_lines': 100,
            'duplicate_threshold': 0.9,
            'complexity_factors': {
                'file_size': 0.3,
                'section_count': 0.2,
                'duplicate_content': 0.3,
                'cross_references': 0.2
            },
            'priority_thresholds': {
                'high': 0.8,
                'medium': 0.5,
                'low': 0.2
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _compile_section_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for section detection."""
        return {
            'heading': re.compile(r'^(#+)\s+(.+)$', re.MULTILINE),
            'code_block': re.compile(r'```[^`]*```', re.DOTALL),
            'list_item': re.compile(r'^[-*+]\s+', re.MULTILINE),
            'numbered_list': re.compile(r'^\d+\.\s+', re.MULTILINE),
            'table': re.compile(r'^\|(.+\|)+$', re.MULTILINE),
            'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'reference': re.compile(r'@([^\s]+)'),
            'emphasis': re.compile(r'\*\*([^*]+)\*\*|\*([^*]+)\*|__([^_]+)__|_([^_]+)_')
        }
    
    def analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single file for modularization opportunities."""
        analysis = FileAnalysis(file_path=file_path, total_lines=0, section_count=0, largest_section=("", 0))
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            opportunity = ModularizationOpportunity(
                file_path=file_path,
                opportunity_type="file_error",
                description=f"Cannot read file: {e}",
                suggestion="Fix file access or encoding issues",
                priority="high"
            )
            analysis.opportunities.append(opportunity)
            return analysis
        
        analysis.total_lines = len(lines)
        
        # Analyze file structure
        self._analyze_file_structure(content, lines, analysis)
        
        # Check for size-based modularization opportunities
        self._check_file_size_opportunities(analysis)
        
        # Analyze sections
        self._analyze_sections(content, lines, analysis)
        
        # Check for duplicate content
        self._check_duplicate_content(content, analysis)
        
        # Analyze cross-references
        self._analyze_cross_references(content, analysis)
        
        # Calculate complexity and modularity scores
        self._calculate_scores(analysis)
        
        # Generate specific opportunities
        self._generate_opportunities(analysis)
        
        return analysis
    
    def _analyze_file_structure(self, content: str, lines: List[str], analysis: FileAnalysis):
        """Analyze the structural characteristics of the file."""
        # Count sections
        headings = self.section_patterns['heading'].findall(content)
        analysis.section_count = len(headings)
        
        # Find largest section
        sections = self._extract_sections(content)
        if sections:
            largest_section = max(sections, key=lambda x: x[1])
            analysis.largest_section = largest_section
        
        # Check for structural issues
        if analysis.section_count == 0:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="structure",
                description="No sections found",
                suggestion="Add section headings to improve structure",
                priority="medium"
            ))
        
        # Check for too many sections
        if analysis.section_count > 20:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="structure",
                description=f"Too many sections ({analysis.section_count})",
                suggestion="Consider breaking into multiple files or grouping related sections",
                priority="high"
            ))
    
    def _extract_sections(self, content: str) -> List[Tuple[str, int]]:
        """Extract sections with their sizes."""
        sections = []
        lines = content.splitlines()
        current_section = None
        current_lines = 0
        
        for line in lines:
            heading_match = re.match(r'^(#+)\\s+(.+)$', line)
            if heading_match:
                if current_section:
                    sections.append((current_section, current_lines))
                current_section = heading_match.group(2)
                current_lines = 0
            else:
                current_lines += 1
        
        if current_section:
            sections.append((current_section, current_lines))
        
        return sections
    
    def _check_file_size_opportunities(self, analysis: FileAnalysis):
        """Check for file size-based modularization opportunities."""
        if analysis.total_lines > self.max_file_lines:
            severity = "high" if analysis.total_lines > self.max_file_lines * 2 else "medium"
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="file_size",
                description=f"File too large ({analysis.total_lines} lines)",
                suggestion=f"Break into multiple files (recommended max: {self.max_file_lines} lines)",
                priority=severity,
                estimated_impact="high"
            ))
    
    def _analyze_sections(self, content: str, lines: List[str], analysis: FileAnalysis):
        """Analyze individual sections for modularization opportunities."""
        sections = self._extract_sections(content)
        
        for section_name, section_size in sections:
            if section_size > self.max_section_lines:
                analysis.opportunities.append(ModularizationOpportunity(
                    file_path=analysis.file_path,
                    opportunity_type="section_size",
                    description=f"Section '{section_name}' too large ({section_size} lines)",
                    suggestion="Break section into subsections or separate file",
                    priority="medium",
                    estimated_impact="medium"
                ))
        
        # Check for similar section patterns
        self._check_similar_sections(sections, analysis)
    
    def _check_similar_sections(self, sections: List[Tuple[str, int]], analysis: FileAnalysis):
        """Check for similar section patterns that could be templated."""
        section_patterns = defaultdict(list)
        
        for section_name, section_size in sections:
            # Extract pattern from section name
            pattern = re.sub(r'\\d+|[A-Z][a-z]+', 'X', section_name)
            section_patterns[pattern].append((section_name, section_size))
        
        for pattern, sections_list in section_patterns.items():
            if len(sections_list) > 2:
                analysis.opportunities.append(ModularizationOpportunity(
                    file_path=analysis.file_path,
                    opportunity_type="template_opportunity",
                    description=f"Similar sections found: {pattern}",
                    suggestion=f"Consider creating a template for {len(sections_list)} similar sections",
                    priority="low",
                    estimated_impact="low"
                ))
    
    def _check_duplicate_content(self, content: str, analysis: FileAnalysis):
        """Check for duplicate content within the file."""
        lines = content.splitlines()
        
        # Check for duplicate blocks
        for i in range(len(lines) - self.min_duplicate_lines):
            block = '\\n'.join(lines[i:i + self.min_duplicate_lines])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            
            if block_hash in self.content_hashes:
                self.content_hashes[block_hash].append((analysis.file_path, i, i + self.min_duplicate_lines))
            else:
                self.content_hashes[block_hash] = [(analysis.file_path, i, i + self.min_duplicate_lines)]
        
        # Check for repetitive patterns
        self._check_repetitive_patterns(lines, analysis)
    
    def _check_repetitive_patterns(self, lines: List[str], analysis: FileAnalysis):
        """Check for repetitive patterns that could be modularized."""
        pattern_counts = defaultdict(int)
        
        for line in lines:
            # Check for list patterns
            if re.match(r'^[-*+]\\s+', line):
                pattern_counts['list_item'] += 1
            elif re.match(r'^\\d+\\.\\s+', line):
                pattern_counts['numbered_item'] += 1
            elif re.match(r'^```', line):
                pattern_counts['code_block'] += 1
            elif re.match(r'^\\|', line):
                pattern_counts['table_row'] += 1
        
        for pattern, count in pattern_counts.items():
            if count > 50:
                analysis.opportunities.append(ModularizationOpportunity(
                    file_path=analysis.file_path,
                    opportunity_type="repetitive_pattern",
                    description=f"High repetition of {pattern} ({count} occurrences)",
                    suggestion=f"Consider using templates or includes for {pattern}",
                    priority="low",
                    estimated_impact="low"
                ))
    
    def _analyze_cross_references(self, content: str, analysis: FileAnalysis):
        """Analyze cross-references for modularization opportunities."""
        # Find all references
        references = self.section_patterns['reference'].findall(content)
        links = self.section_patterns['link'].findall(content)
        
        # Count external references
        external_refs = len([ref for ref in references if not ref.startswith('.')])
        internal_refs = len(references) - external_refs
        
        # High external reference count suggests modularization opportunity
        if external_refs > 20:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="high_coupling",
                description=f"High external references ({external_refs})",
                suggestion="Consider breaking into smaller, more focused modules",
                priority="medium",
                estimated_impact="medium"
            ))
        
        # High internal reference count suggests complex structure
        if internal_refs > 30:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="complex_structure",
                description=f"High internal references ({internal_refs})",
                suggestion="Consider simplifying structure or breaking into sections",
                priority="low",
                estimated_impact="low"
            ))
    
    def _calculate_scores(self, analysis: FileAnalysis):
        """Calculate complexity and modularity scores."""
        factors = self.config['complexity_factors']
        
        # File size factor
        size_factor = min(analysis.total_lines / self.max_file_lines, 2.0)
        
        # Section count factor
        section_factor = min(analysis.section_count / 10, 2.0)
        
        # Duplicate content factor
        duplicate_factor = len(analysis.duplicate_content) * 0.1
        
        # Cross-reference factor (estimated)
        cross_ref_factor = 0.5  # Default, could be calculated from content
        
        # Calculate weighted complexity score
        analysis.complexity_score = (
            size_factor * factors['file_size'] +
            section_factor * factors['section_count'] +
            duplicate_factor * factors['duplicate_content'] +
            cross_ref_factor * factors['cross_references']
        )
        
        # Modularity score (inverse of complexity)
        analysis.modularity_score = max(0, 1.0 - analysis.complexity_score)
    
    def _generate_opportunities(self, analysis: FileAnalysis):
        """Generate specific modularization opportunities based on analysis."""
        thresholds = self.config['priority_thresholds']
        
        # High complexity files
        if analysis.complexity_score > thresholds['high']:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="high_complexity",
                description=f"High complexity score ({analysis.complexity_score:.2f})",
                suggestion="High priority for modularization",
                priority="high",
                estimated_impact="high"
            ))
        
        # Large sections
        if analysis.largest_section[1] > self.max_section_lines:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="large_section",
                description=f"Large section: {analysis.largest_section[0]} ({analysis.largest_section[1]} lines)",
                suggestion="Extract section to separate file or break into subsections",
                priority="medium",
                estimated_impact="medium"
            ))
        
        # Many sections
        if analysis.section_count > 15:
            analysis.opportunities.append(ModularizationOpportunity(
                file_path=analysis.file_path,
                opportunity_type="many_sections",
                description=f"Many sections ({analysis.section_count})",
                suggestion="Group related sections or create index file",
                priority="medium",
                estimated_impact="medium"
            ))
    
    def analyze_directory(self, directory_path: str, pattern: str = "*.md") -> List[FileAnalysis]:
        """Analyze all files in a directory."""
        analyses = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                analysis = self.analyze_file(str(file_path))
                analyses.append(analysis)
        
        # Post-process for cross-file opportunities
        self._find_cross_file_opportunities(analyses)
        
        return analyses
    
    def _find_cross_file_opportunities(self, analyses: List[FileAnalysis]):
        """Find opportunities across multiple files."""
        # Find duplicate content across files
        for block_hash, occurrences in self.content_hashes.items():
            if len(occurrences) > 1:
                files = [occ[0] for occ in occurrences]
                duplicate = DuplicateContent(
                    content=block_hash,
                    files=files,
                    line_ranges=[(occ[1], occ[2]) for occ in occurrences],
                    similarity=1.0,
                    suggestion="Extract duplicate content to shared include file"
                )
                
                for file_path in files:
                    for analysis in analyses:
                        if analysis.file_path == file_path:
                            analysis.duplicate_content.append(duplicate)
                            analysis.opportunities.append(ModularizationOpportunity(
                                file_path=file_path,
                                opportunity_type="cross_file_duplicate",
                                description=f"Duplicate content found in {len(files)} files",
                                suggestion="Extract to shared include file",
                                priority="medium",
                                related_files=files,
                                estimated_impact="medium"
                            ))
    
    def generate_modularization_plan(self, analyses: List[FileAnalysis]) -> Dict:
        """Generate a comprehensive modularization plan."""
        plan = {
            'summary': {
                'total_files': len(analyses),
                'files_needing_modularization': 0,
                'total_opportunities': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0
            },
            'recommendations': {
                'immediate_actions': [],
                'medium_term_actions': [],
                'long_term_actions': []
            },
            'file_priorities': {
                'high': [],
                'medium': [],
                'low': []
            },
            'common_patterns': {},
            'estimated_effort': {
                'high_impact': 0,
                'medium_impact': 0,
                'low_impact': 0
            }
        }
        
        # Analyze all opportunities
        all_opportunities = []
        for analysis in analyses:
            all_opportunities.extend(analysis.opportunities)
            if analysis.opportunities:
                plan['summary']['files_needing_modularization'] += 1
        
        plan['summary']['total_opportunities'] = len(all_opportunities)
        
        # Categorize opportunities
        for opp in all_opportunities:
            if opp.priority == 'high':
                plan['summary']['high_priority'] += 1
                plan['recommendations']['immediate_actions'].append(opp)
            elif opp.priority == 'medium':
                plan['summary']['medium_priority'] += 1
                plan['recommendations']['medium_term_actions'].append(opp)
            else:
                plan['summary']['low_priority'] += 1
                plan['recommendations']['long_term_actions'].append(opp)
        
        # Prioritize files
        for analysis in analyses:
            high_priority_opps = [o for o in analysis.opportunities if o.priority == 'high']
            medium_priority_opps = [o for o in analysis.opportunities if o.priority == 'medium']
            
            if high_priority_opps:
                plan['file_priorities']['high'].append(analysis.file_path)
            elif medium_priority_opps:
                plan['file_priorities']['medium'].append(analysis.file_path)
            elif analysis.opportunities:
                plan['file_priorities']['low'].append(analysis.file_path)
        
        # Find common patterns
        pattern_counts = defaultdict(int)
        for opp in all_opportunities:
            pattern_counts[opp.opportunity_type] += 1
        
        plan['common_patterns'] = dict(sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Estimate effort
        for opp in all_opportunities:
            if opp.estimated_impact == 'high':
                plan['estimated_effort']['high_impact'] += 1
            elif opp.estimated_impact == 'medium':
                plan['estimated_effort']['medium_impact'] += 1
            else:
                plan['estimated_effort']['low_impact'] += 1
        
        return plan

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze documentation modularization opportunities')
    parser.add_argument('path', help='File or directory path to analyze')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--output', help='Output report file (JSON)')
    parser.add_argument('--format', choices=['json', 'text', 'plan'], default='text', help='Output format')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], 
                       help='Filter by priority level')
    parser.add_argument('--type', help='Filter by opportunity type')
    parser.add_argument('--min-score', type=float, help='Minimum complexity score threshold')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    analyzer = DocumentationModularizationAnalyzer(args.config)
    
    # Validate input
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {args.path}")
        return 1
    
    # Run analysis
    if path.is_file():
        analyses = [analyzer.analyze_file(str(path))]
    else:
        analyses = analyzer.analyze_directory(str(path))
    
    if not analyses:
        print("No files found to analyze")
        return 0
    
    # Apply filters
    if args.priority:
        for analysis in analyses:
            analysis.opportunities = [o for o in analysis.opportunities if o.priority == args.priority]
    
    if args.type:
        for analysis in analyses:
            analysis.opportunities = [o for o in analysis.opportunities if o.opportunity_type == args.type]
    
    if args.min_score:
        analyses = [a for a in analyses if a.complexity_score >= args.min_score]
    
    # Generate plan
    plan = analyzer.generate_modularization_plan(analyses)
    
    # Output results
    if args.format == 'json':
        output_data = {
            'plan': plan,
            'analyses': [
                {
                    'file_path': a.file_path,
                    'total_lines': a.total_lines,
                    'section_count': a.section_count,
                    'largest_section': a.largest_section,
                    'complexity_score': a.complexity_score,
                    'modularity_score': a.modularity_score,
                    'opportunities': [
                        {
                            'type': o.opportunity_type,
                            'description': o.description,
                            'suggestion': o.suggestion,
                            'priority': o.priority,
                            'estimated_impact': o.estimated_impact,
                            'affected_lines': o.affected_lines,
                            'related_files': o.related_files
                        } for o in a.opportunities
                    ]
                } for a in analyses
            ]
        }
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
        else:
            print(json.dumps(output_data, indent=2))
    
    elif args.format == 'plan':
        # Plan-focused output
        if not args.quiet:
            print("Documentation Modularization Plan")
            print("=" * 50)
            print(f"Files analyzed: {plan['summary']['total_files']}")
            print(f"Files needing modularization: {plan['summary']['files_needing_modularization']}")
            print(f"Total opportunities: {plan['summary']['total_opportunities']}")
            print(f"High priority: {plan['summary']['high_priority']}")
            print(f"Medium priority: {plan['summary']['medium_priority']}")
            print(f"Low priority: {plan['summary']['low_priority']}")
            print()
            
            # Immediate actions
            if plan['recommendations']['immediate_actions']:
                print("Immediate Actions (High Priority):")
                print("-" * 40)
                for action in plan['recommendations']['immediate_actions'][:10]:
                    print(f"• {action.description}")
                    print(f"  File: {action.file_path}")
                    print(f"  Suggestion: {action.suggestion}")
                    print()
            
            # Common patterns
            if plan['common_patterns']:
                print("Most Common Opportunities:")
                print("-" * 30)
                for pattern, count in list(plan['common_patterns'].items())[:5]:
                    print(f"• {pattern}: {count} occurrences")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(plan, f, indent=2)
    
    else:
        # Text output
        if not args.quiet:
            print("Modularization Analysis Report")
            print("=" * 50)
            print(f"Files analyzed: {len(analyses)}")
            print(f"Average complexity: {sum(a.complexity_score for a in analyses) / len(analyses):.2f}")
            print(f"Average modularity: {sum(a.modularity_score for a in analyses) / len(analyses):.2f}")
            print()
            
            # Show files with opportunities
            files_with_opps = [a for a in analyses if a.opportunities]
            if files_with_opps:
                print("Files with Modularization Opportunities:")
                print("-" * 45)
                for analysis in files_with_opps:
                    print(f"\\n{analysis.file_path}:")
                    print(f"  Lines: {analysis.total_lines}, Sections: {analysis.section_count}")
                    print(f"  Complexity: {analysis.complexity_score:.2f}, Modularity: {analysis.modularity_score:.2f}")
                    print(f"  Opportunities: {len(analysis.opportunities)}")
                    
                    for opp in analysis.opportunities:
                        print(f"    {opp.priority.upper()}: {opp.description}")
                        print(f"      Suggestion: {opp.suggestion}")
        
        # Save text report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write("Modularization Analysis Summary\\n")
                f.write(f"Files analyzed: {len(analyses)}\\n")
                f.write(f"Total opportunities: {sum(len(a.opportunities) for a in analyses)}\\n\\n")
                
                for analysis in analyses:
                    if analysis.opportunities:
                        f.write(f"File: {analysis.file_path}\\n")
                        f.write(f"Complexity: {analysis.complexity_score:.2f}\\n")
                        f.write(f"Opportunities: {len(analysis.opportunities)}\\n")
                        for opp in analysis.opportunities:
                            f.write(f"  {opp.priority.upper()}: {opp.description}\\n")
                            f.write(f"    {opp.suggestion}\\n")
                        f.write("\\n")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())