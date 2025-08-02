"""
Stage 1: Syntax & Static Analysis Validation.

This stage performs comprehensive syntax checking and static analysis including:
- Python syntax validation (AST parsing)
- Ruff linting with all rules
- MyPy type checking
- Import dependency analysis
- Code complexity metrics
- Dead code detection
"""

import ast
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Set
import time

from .base_stage import ValidationStageBase
from .models import ValidationIssue, SeverityLevel, StageMetrics


logger = logging.getLogger(__name__)


class SyntaxValidationStage(ValidationStageBase):
    """Stage 1: Syntax & Static Analysis validation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            stage_id=1,
            stage_name="Syntax & Static Analysis",
            config=config
        )
    
    async def _execute_stage(self) -> None:
        """Execute syntax and static analysis validation."""
        start_time = time.time()
        
        # Get all Python files
        python_files = self._get_python_files()
        lines_of_code = self._count_lines_of_code(python_files)
        
        logger.info(f"Analyzing {len(python_files)} Python files ({lines_of_code} LOC)")
        
        # 1. Python syntax validation
        await self._validate_python_syntax(python_files)
        
        # 2. Ruff linting
        await self._run_ruff_analysis()
        
        # 3. MyPy type checking
        await self._run_mypy_analysis()
        
        # 4. Import dependency analysis
        await self._analyze_import_dependencies(python_files)
        
        # 5. Code complexity analysis
        await self._analyze_code_complexity(python_files)
        
        # 6. Dead code detection
        await self._detect_dead_code(python_files)
        
        # Record metrics
        execution_time = timedelta(seconds=time.time() - start_time)
        metrics = StageMetrics(
            execution_time=execution_time,
            files_processed=len(python_files),
            lines_of_code=lines_of_code
        )
        self._add_metric(metrics)
        
        logger.info(f"Stage 1 completed in {execution_time.total_seconds():.2f}s")
    
    async def _validate_python_syntax(self, python_files: List[Path]) -> None:
        """Validate Python syntax using AST parsing."""
        logger.info("Validating Python syntax")
        
        syntax_errors = 0
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Try to parse the AST
                ast.parse(source_code, filename=str(file_path))
                
            except SyntaxError as e:
                syntax_errors += 1
                self._add_issue(
                    category="syntax",
                    severity=SeverityLevel.CRITICAL,
                    message=f"Syntax error: {e.msg}",
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=e.lineno,
                    column=e.offset
                )
                
            except Exception as e:
                self._add_issue(
                    category="syntax",
                    severity=SeverityLevel.HIGH,
                    message=f"Failed to parse file: {e}",
                    file_path=str(file_path.relative_to(self.project_root))
                )
        
        if syntax_errors == 0:
            logger.info("✓ No syntax errors found")
        else:
            logger.warning(f"✗ Found {syntax_errors} syntax errors")
    
    async def _run_ruff_analysis(self) -> None:
        """Run Ruff linting analysis."""
        logger.info("Running Ruff analysis")
        
        # Run Ruff with comprehensive rules
        result = await self._run_tool([
            'ruff', 'check', 
            str(self.project_root),
            '--output-format=text',
            '--show-fixes',
            '--extend-select=ALL'
        ])
        
        if result.success:
            logger.info("✓ Ruff analysis passed")
        else:
            logger.warning("✗ Ruff found issues")
            
            # Parse Ruff output into issues
            ruff_issues = self._parse_ruff_output(result.output)
            for issue in ruff_issues:
                self.result.issues.append(issue)
        
        # Store Ruff output as artifact
        self._add_artifact('ruff_output', result.output)
        self._add_artifact('ruff_error_output', result.error_output)
    
    async def _run_mypy_analysis(self) -> None:
        """Run MyPy type checking analysis."""
        logger.info("Running MyPy analysis")
        
        # Check if mypy config exists
        mypy_config_paths = [
            self.project_root / 'mypy.ini',
            self.project_root / '.mypy.ini',
            self.project_root / 'pyproject.toml'
        ]
        
        mypy_cmd = [
            'mypy',
            str(self.project_root),
            '--show-error-codes',
            '--show-column-numbers'
        ]
        
        # Add config if found
        for config_path in mypy_config_paths:
            if config_path.exists():
                if config_path.name == 'pyproject.toml':
                    # MyPy will automatically read pyproject.toml
                    break
                else:
                    mypy_cmd.extend(['--config-file', str(config_path)])
                    break
        else:
            # Use default strict settings if no config found
            mypy_cmd.extend([
                '--strict',
                '--ignore-missing-imports',
                '--show-error-context'
            ])
        
        result = await self._run_tool(mypy_cmd)
        
        if result.success:
            logger.info("✓ MyPy type checking passed")
        else:
            logger.warning("✗ MyPy found type issues")
            
            # Parse MyPy output into issues
            mypy_issues = self._parse_mypy_output(result.output)
            for issue in mypy_issues:
                self.result.issues.append(issue)
        
        # Store MyPy output as artifact
        self._add_artifact('mypy_output', result.output)
        self._add_artifact('mypy_error_output', result.error_output)
    
    async def _analyze_import_dependencies(self, python_files: List[Path]) -> None:
        """Analyze import dependencies and detect issues."""
        logger.info("Analyzing import dependencies")
        
        import_map: Dict[str, Set[str]] = {}
        unused_imports: List[ValidationIssue] = []
        circular_dependencies: List[ValidationIssue] = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code, filename=str(file_path))
                
                # Extract imports
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module)
                
                file_key = str(file_path.relative_to(self.project_root))
                import_map[file_key] = imports
                
                # Check for unused imports (simplified check)
                # This is a basic implementation - a full implementation would
                # need to check if imported names are actually used
                
            except Exception as e:
                self._add_issue(
                    category="imports",
                    severity=SeverityLevel.MEDIUM,
                    message=f"Failed to analyze imports: {e}",
                    file_path=str(file_path.relative_to(self.project_root))
                )
        
        # Detect circular dependencies (simplified)
        self._detect_circular_imports(import_map)
        
        # Store import analysis as artifact
        self._add_artifact('import_analysis', {
            'import_map': {k: list(v) for k, v in import_map.items()},
            'total_files_analyzed': len(python_files)
        })
    
    def _detect_circular_imports(self, import_map: Dict[str, Set[str]]) -> None:
        """Detect circular import dependencies."""
        # This is a simplified circular dependency detection
        # A full implementation would need more sophisticated graph analysis
        
        for file_path, imports in import_map.items():
            for imported_module in imports:
                # Convert module name to potential file path
                potential_file = imported_module.replace('.', '/') + '.py'
                
                if potential_file in import_map:
                    # Check if the imported file imports back
                    reverse_imports = import_map[potential_file]
                    module_name = file_path.replace('/', '.').replace('.py', '')
                    
                    if any(imp.startswith(module_name) for imp in reverse_imports):
                        self._add_issue(
                            category="imports",
                            severity=SeverityLevel.HIGH,
                            message=f"Potential circular import with {imported_module}",
                            file_path=file_path,
                            suggestion="Consider refactoring to remove circular dependency"
                        )
    
    async def _analyze_code_complexity(self, python_files: List[Path]) -> None:
        """Analyze code complexity metrics."""
        logger.info("Analyzing code complexity")
        
        complexity_issues = 0
        total_functions = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code, filename=str(file_path))
                
                # Analyze functions and methods
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        
                        # Calculate cyclomatic complexity (simplified)
                        complexity = self._calculate_cyclomatic_complexity(node)
                        
                        if complexity > 10:  # Threshold from config
                            complexity_issues += 1
                            severity = SeverityLevel.HIGH if complexity > 15 else SeverityLevel.MEDIUM
                            
                            self._add_issue(
                                category="complexity",
                                severity=severity,
                                message=f"Function '{node.name}' has high cyclomatic complexity: {complexity}",
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                suggestion="Consider breaking down this function into smaller parts"
                            )
                        
                        # Check function length
                        function_length = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                        if function_length > 50:  # Threshold from config
                            self._add_issue(
                                category="complexity",
                                severity=SeverityLevel.MEDIUM,
                                message=f"Function '{node.name}' is too long: {function_length} lines",
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                suggestion="Consider breaking down this function"
                            )
                
            except Exception as e:
                logger.warning(f"Could not analyze complexity for {file_path}: {e}")
        
        # Store complexity analysis as artifact
        self._add_artifact('complexity_analysis', {
            'total_functions_analyzed': total_functions,
            'high_complexity_functions': complexity_issues,
            'average_complexity': 'Not calculated'  # Would need full implementation
        })
        
        if complexity_issues == 0:
            logger.info("✓ No high complexity functions found")
        else:
            logger.warning(f"✗ Found {complexity_issues} high complexity functions")
    
    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Add complexity for control structures
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
                # Add for each except handler
                complexity += len(child.handlers)
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        
        return complexity
    
    async def _detect_dead_code(self, python_files: List[Path]) -> None:
        """Detect potentially dead/unused code."""
        logger.info("Detecting dead code")
        
        # This is a simplified dead code detection
        # A full implementation would need more sophisticated analysis
        
        defined_functions: Set[str] = set()
        called_functions: Set[str] = set()
        
        # First pass: collect all function definitions
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code, filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Skip magic methods and private methods starting with _
                        if not node.name.startswith('_'):
                            defined_functions.add(node.name)
                
            except Exception as e:
                logger.warning(f"Could not analyze {file_path} for dead code: {e}")
        
        # Second pass: collect function calls
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                tree = ast.parse(source_code, filename=str(file_path))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            called_functions.add(node.func.id)
                        elif isinstance(node.func, ast.Attribute):
                            called_functions.add(node.func.attr)
                
            except Exception as e:
                logger.warning(f"Could not analyze {file_path} for function calls: {e}")
        
        # Find potentially unused functions
        potentially_unused = defined_functions - called_functions
        
        for func_name in potentially_unused:
            # Find the file and line where this function is defined
            for file_path in python_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    tree = ast.parse(source_code, filename=str(file_path))
                    
                    for node in ast.walk(tree):
                        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                            and node.name == func_name):
                            
                            self._add_issue(
                                category="dead_code",
                                severity=SeverityLevel.LOW,
                                message=f"Function '{func_name}' appears to be unused",
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                suggestion="Consider removing if truly unused, or add to __all__ if it's a public API"
                            )
                            break
                
                except Exception:
                    continue
        
        # Store dead code analysis as artifact
        self._add_artifact('dead_code_analysis', {
            'defined_functions': len(defined_functions),
            'called_functions': len(called_functions),
            'potentially_unused': len(potentially_unused),
            'unused_function_names': list(potentially_unused)
        })
        
        if potentially_unused:
            logger.warning(f"✗ Found {len(potentially_unused)} potentially unused functions")
        else:
            logger.info("✓ No obviously unused functions found")