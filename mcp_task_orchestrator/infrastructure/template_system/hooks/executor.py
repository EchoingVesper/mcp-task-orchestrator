"""
Hook execution engine with dependency management and executive dysfunction support.

Provides intelligent hook execution with automatic dependency resolution,
rollback capabilities, and executive function-friendly error handling.
"""

import asyncio
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque

from .base import Hook, HookType, HookContext, HookResult, HookExecutionError

logger = logging.getLogger(__name__)


@dataclass
class ExecutionPlan:
    """Plan for executing hooks in dependency order."""
    execution_groups: List[List[Hook]] = field(default_factory=list)
    total_estimated_time_ms: float = 0.0
    parallel_groups: Set[int] = field(default_factory=set)
    
    def add_group(self, hooks: List[Hook], is_parallel: bool = False) -> None:
        """Add a group of hooks to the execution plan."""
        group_index = len(self.execution_groups)
        self.execution_groups.append(hooks)
        
        if is_parallel:
            self.parallel_groups.add(group_index)
        
        # Estimate execution time (rough estimate)
        group_time = max(hook.average_execution_time for hook in hooks) if is_parallel else sum(hook.average_execution_time for hook in hooks)
        self.total_estimated_time_ms += group_time
    
    def get_total_hooks(self) -> int:
        """Get total number of hooks in the plan."""
        return sum(len(group) for group in self.execution_groups)
    
    def is_group_parallel(self, group_index: int) -> bool:
        """Check if a group should execute in parallel."""
        return group_index in self.parallel_groups


class DependencyGraph:
    """
    Manages hook dependencies and resolves execution order.
    
    Uses topological sorting to ensure hooks execute in correct dependency order
    while supporting parallel execution where possible.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Hook] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_hook(self, hook: Hook) -> None:
        """Add a hook to the dependency graph."""
        self.nodes[hook.hook_id] = hook
        
        # Add dependencies
        for dep_id in hook.get_dependencies():
            self.add_edge(dep_id, hook.hook_id)
    
    def add_edge(self, from_hook_id: str, to_hook_id: str) -> None:
        """Add a dependency edge (from_hook must execute before to_hook)."""
        self.edges[from_hook_id].add(to_hook_id)
        self.reverse_edges[to_hook_id].add(from_hook_id)
    
    def resolve_execution_order(self) -> ExecutionPlan:
        """
        Resolve execution order using topological sort with parallelization.
        
        Returns:
            ExecutionPlan with hooks grouped by execution order and parallelization
            
        Raises:
            HookExecutionError: If circular dependencies are detected
        """
        # Detect circular dependencies
        if self._has_circular_dependencies():
            cycles = self._find_cycles()
            raise HookExecutionError(
                f"Circular dependencies detected: {cycles}",
                "dependency_resolver",
                None,  # No context available
                error_type="circular_dependency"
            )
        
        plan = ExecutionPlan()
        remaining_hooks = set(self.nodes.keys())
        in_degree = self._calculate_in_degrees()
        
        while remaining_hooks:
            # Find all hooks with no remaining dependencies
            ready_hooks = [
                hook_id for hook_id in remaining_hooks
                if in_degree[hook_id] == 0
            ]
            
            if not ready_hooks:
                # This shouldn't happen if no cycles exist
                raise HookExecutionError(
                    "No hooks ready for execution but hooks remain - possible circular dependency",
                    "dependency_resolver",
                    None,
                    error_type="dependency_deadlock"
                )
            
            # Create execution group
            group_hooks = [self.nodes[hook_id] for hook_id in ready_hooks]
            is_parallel = len(ready_hooks) > 1 and self._can_execute_in_parallel(ready_hooks)
            
            plan.add_group(group_hooks, is_parallel)
            
            # Remove executed hooks and update in-degrees
            for hook_id in ready_hooks:
                remaining_hooks.remove(hook_id)
                
                for dependent_id in self.edges[hook_id]:
                    in_degree[dependent_id] -= 1
        
        return plan
    
    def _calculate_in_degrees(self) -> Dict[str, int]:
        """Calculate in-degree (number of dependencies) for each hook."""
        in_degree = {hook_id: 0 for hook_id in self.nodes.keys()}
        
        for hook_id in self.nodes.keys():
            in_degree[hook_id] = len(self.reverse_edges[hook_id])
        
        return in_degree
    
    def _has_circular_dependencies(self) -> bool:
        """Check if the graph has circular dependencies using DFS."""
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {hook_id: WHITE for hook_id in self.nodes.keys()}
        
        def dfs(node_id: str) -> bool:
            if colors[node_id] == GRAY:
                return True  # Back edge found (cycle)
            if colors[node_id] == BLACK:
                return False  # Already processed
            
            colors[node_id] = GRAY
            
            for neighbor in self.edges[node_id]:
                if dfs(neighbor):
                    return True
            
            colors[node_id] = BLACK
            return False
        
        for hook_id in self.nodes.keys():
            if colors[hook_id] == WHITE:
                if dfs(hook_id):
                    return True
        
        return False
    
    def _find_cycles(self) -> List[List[str]]:
        """Find all cycles in the dependency graph."""
        cycles = []
        WHITE, GRAY, BLACK = 0, 1, 2
        colors = {hook_id: WHITE for hook_id in self.nodes.keys()}
        path = []
        
        def dfs(node_id: str) -> None:
            colors[node_id] = GRAY
            path.append(node_id)
            
            for neighbor in self.edges[node_id]:
                if colors[neighbor] == GRAY:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                elif colors[neighbor] == WHITE:
                    dfs(neighbor)
            
            colors[node_id] = BLACK
            path.pop()
        
        for hook_id in self.nodes.keys():
            if colors[hook_id] == WHITE:
                dfs(hook_id)
        
        return cycles
    
    def _can_execute_in_parallel(self, hook_ids: List[str]) -> bool:
        """
        Determine if hooks can be safely executed in parallel.
        
        Currently uses simple heuristics, but could be enhanced with
        resource conflict detection and hook-specific parallelization hints.
        """
        # Check if hooks have any mutual dependencies
        for i, hook_id1 in enumerate(hook_ids):
            for hook_id2 in hook_ids[i+1:]:
                # Check if hook1 depends on hook2 or vice versa
                if hook_id2 in self.edges[hook_id1] or hook_id1 in self.edges[hook_id2]:
                    return False
        
        # Additional heuristics could be added here:
        # - Resource conflict detection
        # - Hook-specific parallelization hints
        # - Performance characteristics
        
        return True


class HookExecutor:
    """
    Orchestrates hook execution with dependency management and ED support.
    
    Features:
    - Automatic dependency resolution
    - Parallel execution where safe
    - Executive dysfunction-aware error handling
    - Automatic rollback on failures
    - Progress tracking and checkpointing
    - Interruption handling
    """
    
    def __init__(self, max_parallel_hooks: int = 3, enable_rollback: bool = True):
        self.max_parallel_hooks = max_parallel_hooks
        self.enable_rollback = enable_rollback
        self.execution_history: List[Dict[str, Any]] = []
        self.current_execution: Optional[str] = None
        
        # Executive dysfunction support
        self.checkpoint_interval = timedelta(minutes=2)  # Checkpoint every 2 minutes
        self.overwhelm_threshold = 5  # Max hooks before suggesting break
        self.last_checkpoint = None
    
    async def execute_hooks(
        self,
        hook_type: HookType,
        hooks: List[Hook],
        context: HookContext
    ) -> List[HookResult]:
        """
        Execute hooks of given type with dependency resolution.
        
        Args:
            hook_type: Type of hooks being executed
            hooks: List of hooks to execute
            context: Execution context
            
        Returns:
            List of hook results in execution order
            
        Raises:
            HookExecutionError: If execution fails and cannot be recovered
        """
        execution_id = f"{hook_type.value}_{datetime.now().timestamp()}"
        self.current_execution = execution_id
        
        logger.info(f"Starting hook execution: {execution_id} with {len(hooks)} hooks")
        
        try:
            # Build dependency graph
            graph = DependencyGraph()
            for hook in hooks:
                graph.add_hook(hook)
            
            # Resolve execution plan
            plan = self._resolve_execution_plan(graph, context)
            
            # Execute hooks according to plan
            results = await self._execute_plan(plan, context, hook_type)
            
            # Record successful execution
            self._record_execution_success(execution_id, hook_type, len(hooks), results)
            
            return results
            
        except Exception as e:
            # Record failed execution
            self._record_execution_failure(execution_id, hook_type, e)
            
            # Attempt rollback if enabled
            if self.enable_rollback:
                await self._attempt_rollback(hooks, context)
            
            # Re-raise with context
            if isinstance(e, HookExecutionError):
                raise
            else:
                raise HookExecutionError(
                    f"Hook execution failed: {e}",
                    execution_id,
                    context,
                    error_type="execution_failure"
                ) from e
        
        finally:
            self.current_execution = None
    
    def _resolve_execution_plan(self, graph: DependencyGraph, context: HookContext) -> ExecutionPlan:
        """Resolve execution plan with ED-aware optimizations."""
        base_plan = graph.resolve_execution_order()
        
        # Apply executive dysfunction optimizations
        optimized_plan = self._optimize_for_ed(base_plan, context)
        
        # Log execution plan
        logger.info(f"Resolved execution plan: {optimized_plan.get_total_hooks()} hooks in {len(optimized_plan.execution_groups)} groups")
        
        return optimized_plan
    
    def _optimize_for_ed(self, plan: ExecutionPlan, context: HookContext) -> ExecutionPlan:
        """Apply executive dysfunction-aware optimizations to execution plan."""
        optimized = ExecutionPlan()
        
        for group_idx, group in enumerate(plan.execution_groups):
            is_parallel = plan.is_group_parallel(group_idx)
            
            # Check if group size exceeds overwhelm threshold
            if len(group) > self.overwhelm_threshold:
                logger.warning(f"Hook group size ({len(group)}) exceeds overwhelm threshold ({self.overwhelm_threshold})")
                
                # Split large groups into smaller chunks
                for i in range(0, len(group), self.overwhelm_threshold):
                    chunk = group[i:i + self.overwhelm_threshold]
                    chunk_parallel = is_parallel and len(chunk) > 1
                    optimized.add_group(chunk, chunk_parallel)
            else:
                optimized.add_group(group, is_parallel)
        
        return optimized
    
    async def _execute_plan(
        self,
        plan: ExecutionPlan,
        context: HookContext,
        hook_type: HookType
    ) -> List[HookResult]:
        """Execute the resolved execution plan."""
        all_results = []
        executed_hooks = []
        
        try:
            for group_idx, group in enumerate(plan.execution_groups):
                is_parallel = plan.is_group_parallel(group_idx)
                
                logger.info(f"Executing hook group {group_idx + 1}/{len(plan.execution_groups)}: {len(group)} hooks {'in parallel' if is_parallel else 'sequentially'}")
                
                # Check if checkpoint is needed
                await self._check_checkpoint_needed(context)
                
                # Execute group
                if is_parallel:
                    group_results = await self._execute_hooks_parallel(group, context)
                else:
                    group_results = await self._execute_hooks_sequential(group, context)
                
                # Update context with group results
                self._update_context_with_results(context, group_results)
                
                all_results.extend(group_results)
                executed_hooks.extend(group)
                
                # Check for execution errors
                failed_results = [r for r in group_results if not r.success]
                if failed_results:
                    raise HookExecutionError(
                        f"Hook group execution failed: {len(failed_results)} hooks failed",
                        f"group_{group_idx}",
                        context,
                        error_type="group_execution_failure"
                    )
        
        except Exception as e:
            # Store executed hooks for potential rollback
            context.metadata["executed_hooks"] = [h.hook_id for h in executed_hooks]
            raise
        
        return all_results
    
    async def _execute_hooks_parallel(self, hooks: List[Hook], context: HookContext) -> List[HookResult]:
        """Execute hooks in parallel with concurrency limiting."""
        semaphore = asyncio.Semaphore(min(self.max_parallel_hooks, len(hooks)))
        
        async def execute_with_semaphore(hook: Hook) -> HookResult:
            async with semaphore:
                return await self._execute_single_hook(hook, context)
        
        # Execute all hooks concurrently
        tasks = [execute_with_semaphore(hook) for hook in hooks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for hook, result in zip(hooks, results):
            if isinstance(result, Exception):
                processed_results.append(HookResult(
                    success=False,
                    hook_id=hook.hook_id,
                    execution_time_ms=0.0,
                    message=f"Parallel execution failed: {result}",
                    error_type="parallel_execution_error",
                    rollback_required=True
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_hooks_sequential(self, hooks: List[Hook], context: HookContext) -> List[HookResult]:
        """Execute hooks sequentially."""
        results = []
        
        for hook in hooks:
            result = await self._execute_single_hook(hook, context)
            results.append(result)
            
            # Stop on first failure
            if not result.success:
                break
        
        return results
    
    async def _execute_single_hook(self, hook: Hook, context: HookContext) -> HookResult:
        """Execute a single hook with error handling and metrics."""
        start_time = datetime.now()
        
        try:
            # Validate context
            validation_errors = hook.validate_context(context)
            if validation_errors:
                return HookResult(
                    success=False,
                    hook_id=hook.hook_id,
                    execution_time_ms=0.0,
                    message=f"Context validation failed: {validation_errors}",
                    error_type="context_validation_error"
                )
            
            # Execute hook
            logger.debug(f"Executing hook: {hook.hook_id}")
            result = await hook.execute(context)
            
            # Record metrics
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            hook._record_execution_metrics(execution_time, result.success)
            
            # Update result with actual execution time
            result.execution_time_ms = execution_time
            
            logger.debug(f"Hook {hook.hook_id} completed: {result.success} ({execution_time:.1f}ms)")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            hook._record_execution_metrics(execution_time, False)
            
            logger.error(f"Hook {hook.hook_id} failed: {e}")
            
            return HookResult(
                success=False,
                hook_id=hook.hook_id,
                execution_time_ms=execution_time,
                message=f"Hook execution failed: {e}",
                error_type="hook_execution_error",
                error_details={"exception": str(e), "exception_type": type(e).__name__},
                rollback_required=hook.supports_rollback()
            )
    
    def _update_context_with_results(self, context: HookContext, results: List[HookResult]) -> None:
        """Update context with results from executed hooks."""
        for result in results:
            # Update metadata
            context.metadata.update(result.metadata)
            
            # Add artifacts
            context.artifacts.extend(result.artifacts)
            
            # Add spawned agents
            for agent_id in result.spawned_agents:
                if agent_id not in context.spawned_agents:
                    context.spawned_agents.append(agent_id)
                    context.active_agents.add(agent_id)
            
            # Create checkpoint if requested
            if result.checkpoint_created:
                context.checkpoint_data[result.checkpoint_created] = result.recovery_data
        
        # Update last activity timestamp
        context.last_activity_at = datetime.now()
    
    async def _check_checkpoint_needed(self, context: HookContext) -> None:
        """Check if automatic checkpoint is needed for ED support."""
        now = datetime.now()
        
        if (self.last_checkpoint is None or 
            now - self.last_checkpoint > self.checkpoint_interval):
            
            checkpoint_name = f"auto_checkpoint_{now.timestamp()}"
            context.create_checkpoint(checkpoint_name)
            self.last_checkpoint = now
            
            logger.debug(f"Created automatic checkpoint: {checkpoint_name}")
    
    async def _attempt_rollback(self, hooks: List[Hook], context: HookContext) -> None:
        """Attempt to rollback executed hooks on failure."""
        executed_hook_ids = context.metadata.get("executed_hooks", [])
        rollback_hooks = [h for h in hooks if h.hook_id in executed_hook_ids and h.supports_rollback()]
        
        if not rollback_hooks:
            logger.warning("No hooks support rollback - execution state may be inconsistent")
            return
        
        logger.info(f"Attempting rollback of {len(rollback_hooks)} hooks")
        
        # Execute rollbacks in reverse order
        for hook in reversed(rollback_hooks):
            try:
                await hook.rollback(context)
                logger.debug(f"Rolled back hook: {hook.hook_id}")
            except Exception as e:
                logger.error(f"Failed to rollback hook {hook.hook_id}: {e}")
    
    def _record_execution_success(
        self,
        execution_id: str,
        hook_type: HookType,
        hook_count: int,
        results: List[HookResult]
    ) -> None:
        """Record successful execution for monitoring."""
        total_time = sum(r.execution_time_ms for r in results)
        
        record = {
            "execution_id": execution_id,
            "hook_type": hook_type.value,
            "hook_count": hook_count,
            "total_execution_time_ms": total_time,
            "success": True,
            "completed_at": datetime.now().isoformat()
        }
        
        self.execution_history.append(record)
        logger.info(f"Execution {execution_id} completed successfully in {total_time:.1f}ms")
    
    def _record_execution_failure(
        self,
        execution_id: str,
        hook_type: HookType,
        error: Exception
    ) -> None:
        """Record failed execution for monitoring."""
        record = {
            "execution_id": execution_id,
            "hook_type": hook_type.value,
            "error": str(error),
            "error_type": type(error).__name__,
            "success": False,
            "failed_at": datetime.now().isoformat()
        }
        
        self.execution_history.append(record)
        logger.error(f"Execution {execution_id} failed: {error}")
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get execution statistics for monitoring."""
        if not self.execution_history:
            return {"total_executions": 0}
        
        successful = [r for r in self.execution_history if r["success"]]
        failed = [r for r in self.execution_history if not r["success"]]
        
        stats = {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": len(successful) / len(self.execution_history),
        }
        
        if successful:
            execution_times = [r["total_execution_time_ms"] for r in successful]
            stats.update({
                "average_execution_time_ms": sum(execution_times) / len(execution_times),
                "max_execution_time_ms": max(execution_times),
                "min_execution_time_ms": min(execution_times)
            })
        
        return stats