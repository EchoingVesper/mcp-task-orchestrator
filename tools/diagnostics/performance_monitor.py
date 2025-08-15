"""
Performance monitoring tool for the MCP Task Orchestrator.

This tool provides real-time performance monitoring and analysis.
"""

import asyncio
import argparse
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_task_orchestrator.infrastructure.monitoring import (
    SystemMonitor, get_system_monitor, get_metrics_collector,
    track_performance, record_metric
)


class PerformanceMonitorTool:
    """Interactive performance monitoring tool."""
    
    def __init__(self):
        self.system_monitor = get_system_monitor()
        self.metrics_collector = get_metrics_collector()
        self.monitoring = False
    
    async def start_monitoring(self, interval: int = 5, duration: int = 60):
        """Start real-time performance monitoring."""
        self.monitoring = True
        end_time = time.time() + duration
        
        print(f"🚀 Starting performance monitoring for {duration}s (interval: {interval}s)")
        print("=" * 70)
        print(f"{'Time':<12} {'CPU%':<8} {'MEM%':<8} {'DISK%':<8} {'FDs':<6} {'Threads':<8}")
        print("-" * 70)
        
        try:
            while self.monitoring and time.time() < end_time:
                # Get comprehensive status
                status = await self.system_monitor.get_comprehensive_status()
                snapshot = status["system_snapshot"]
                
                # Display current metrics
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{timestamp:<12} "
                      f"{snapshot['cpu_percent']:<8.1f} "
                      f"{snapshot['memory_percent']:<8.1f} "
                      f"{snapshot['disk_usage_percent']:<8.1f} "
                      f"{snapshot['file_descriptors']:<6} "
                      f"{snapshot['thread_count']:<8}")
                
                # Check for alerts
                active_alerts = status.get("active_alerts", [])
                if active_alerts:
                    print(f"  ⚠️  Active alerts: {', '.join(active_alerts)}")
                
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        
        self.monitoring = False
    
    async def analyze_metrics(self, time_window: int = 3600):
        """Analyze performance metrics over time window."""
        print(f"📊 Analyzing metrics for the last {time_window // 60} minutes...")
        
        # Get metrics summary
        window = timedelta(seconds=time_window)
        metrics = self.metrics_collector.get_all_metrics(window)
        
        if not metrics:
            print("❌ No metrics available for analysis")
            return
        
        print(f"\n📈 Performance Analysis (last {time_window // 60} minutes):")
        print("=" * 60)
        
        # Analyze key system metrics
        system_metrics = [
            ("system.cpu_percent", "CPU Usage", "%"),
            ("system.memory_percent", "Memory Usage", "%"),
            ("system.disk_usage_percent", "Disk Usage", "%"),
            ("system.file_descriptors", "File Descriptors", "count"),
            ("system.thread_count", "Thread Count", "count")
        ]
        
        for metric_name, display_name, unit in system_metrics:
            if metric_name in metrics:
                summary = metrics[metric_name]
                print(f"\n{display_name}:")
                print(f"  Average: {summary.avg:.2f} {unit}")
                print(f"  Min/Max: {summary.min:.2f} / {summary.max:.2f} {unit}")
                print(f"  Data Points: {summary.count}")
                
                # Highlight concerning values
                if "cpu" in metric_name and summary.avg > 70:
                    print("  ⚠️  High average CPU usage")
                elif "memory" in metric_name and summary.avg > 80:
                    print("  ⚠️  High average memory usage")
                elif "disk" in metric_name and summary.avg > 85:
                    print("  ⚠️  High average disk usage")
                elif "file_descriptors" in metric_name and summary.avg > 300:
                    print("  ⚠️  High file descriptor usage")
        
        # Analyze error metrics
        error_metrics = [m for m in metrics.keys() if "error" in m or "failure" in m]
        if error_metrics:
            print("\n❌ Error Metrics:")
            for metric_name in error_metrics:
                summary = metrics[metric_name]
                print(f"  {metric_name}: {summary.sum:.0f} total, {summary.avg:.2f} avg")
        
        # Performance recommendations
        recommendations = self._generate_performance_recommendations(metrics)
        if recommendations:
            print("\n💡 Performance Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")
    
    def _generate_performance_recommendations(self, metrics: dict) -> list:
        """Generate performance recommendations based on metrics."""
        recommendations = []
        
        # CPU recommendations
        if "system.cpu_percent" in metrics:
            cpu_avg = metrics["system.cpu_percent"].avg
            if cpu_avg > 80:
                recommendations.append("High CPU usage detected - consider optimizing CPU-intensive operations")
            elif cpu_avg > 60:
                recommendations.append("Moderate CPU usage - monitor for trends")
        
        # Memory recommendations
        if "system.memory_percent" in metrics:
            mem_avg = metrics["system.memory_percent"].avg
            if mem_avg > 85:
                recommendations.append("High memory usage detected - check for memory leaks")
            elif mem_avg > 70:
                recommendations.append("Elevated memory usage - consider memory optimization")
        
        # File descriptor recommendations
        if "system.file_descriptors" in metrics:
            fd_avg = metrics["system.file_descriptors"].avg
            if fd_avg > 500:
                recommendations.append("High file descriptor usage - check for resource leaks")
            elif fd_avg > 200:
                recommendations.append("Elevated file descriptor usage - monitor resource cleanup")
        
        # Thread recommendations
        if "system.thread_count" in metrics:
            thread_avg = metrics["system.thread_count"].avg
            if thread_avg > 100:
                recommendations.append("High thread count - review concurrent operations")
        
        return recommendations
    
    async def run_performance_test(self, test_duration: int = 30):
        """Run a synthetic performance test."""
        print(f"🧪 Running performance test for {test_duration}s...")
        
        # Start system monitoring
        self.system_monitor.start_monitoring()
        
        # Record test start
        test_start = time.time()
        record_metric("performance_test.started", 1)
        
        try:
            # Simulate various operations
            print("  📝 Simulating database operations...")
            await self._simulate_database_operations()
            
            print("  🧮 Simulating CPU-intensive tasks...")
            await self._simulate_cpu_operations()
            
            print("  💾 Simulating memory operations...")
            await self._simulate_memory_operations()
            
            # Wait for test duration
            await asyncio.sleep(max(0, test_duration - (time.time() - test_start)))
            
            print("✅ Performance test completed")
            record_metric("performance_test.completed", 1)
            
            # Get results
            await asyncio.sleep(2)  # Allow metrics to be collected
            await self.analyze_metrics(test_duration + 10)
        
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            record_metric("performance_test.failed", 1)
    
    async def _simulate_database_operations(self):
        """Simulate database operations for testing."""
        for i in range(10):
            with track_performance("test.database_operation"):
                await asyncio.sleep(0.1)  # Simulate DB query
                if i % 3 == 0:
                    record_metric("test.database.query", 1)
                else:
                    record_metric("test.database.update", 1)
    
    async def _simulate_cpu_operations(self):
        """Simulate CPU-intensive operations for testing."""
        for i in range(5):
            with track_performance("test.cpu_operation"):
                # CPU-intensive calculation
                result = sum(x * x for x in range(10000))
                record_metric("test.cpu.calculation_result", result % 1000)
            await asyncio.sleep(0.1)
    
    async def _simulate_memory_operations(self):
        """Simulate memory operations for testing."""
        memory_blocks = []
        try:
            for i in range(5):
                with track_performance("test.memory_operation"):
                    # Allocate some memory
                    block = bytearray(1024 * 100)  # 100KB
                    memory_blocks.append(block)
                    record_metric("test.memory.allocated_kb", 100)
                await asyncio.sleep(0.1)
        finally:
            # Clean up memory
            del memory_blocks
            record_metric("test.memory.cleanup", 1)


async def main():
    """Main entry point for the performance monitoring tool."""
    parser = argparse.ArgumentParser(description="MCP Task Orchestrator Performance Monitor")
    parser.add_argument("--monitor", action="store_true", help="Start real-time monitoring")
    parser.add_argument("--analyze", action="store_true", help="Analyze recent metrics")
    parser.add_argument("--test", action="store_true", help="Run performance test")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds")
    parser.add_argument("--duration", type=int, default=60, help="Monitoring/test duration in seconds")
    parser.add_argument("--window", type=int, default=3600, help="Analysis time window in seconds")
    
    args = parser.parse_args()
    
    tool = PerformanceMonitorTool()
    
    print("📊 MCP Task Orchestrator Performance Monitor")
    print("=" * 50)
    
    try:
        if args.monitor:
            await tool.start_monitoring(args.interval, args.duration)
        elif args.analyze:
            await tool.analyze_metrics(args.window)
        elif args.test:
            await tool.run_performance_test(args.duration)
        else:
            # Default: show current status and analyze recent metrics
            print("📈 Current Performance Status:")
            system_monitor = get_system_monitor()
            status = await system_monitor.get_comprehensive_status()
            
            snapshot = status["system_snapshot"]
            print(f"  CPU: {snapshot['cpu_percent']:.1f}%")
            print(f"  Memory: {snapshot['memory_percent']:.1f}%")
            print(f"  Disk: {snapshot['disk_usage_percent']:.1f}%")
            print(f"  File Descriptors: {snapshot['file_descriptors']}")
            print(f"  Threads: {snapshot['thread_count']}")
            
            # Show recent metrics analysis
            await tool.analyze_metrics(1800)  # Last 30 minutes
    
    except KeyboardInterrupt:
        print("\n🛑 Performance monitoring interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Performance monitoring failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())