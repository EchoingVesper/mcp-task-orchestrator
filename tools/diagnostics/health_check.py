"""
Comprehensive health check tool for the MCP Task Orchestrator.

This tool provides a unified interface for running health checks,
diagnostics, and generating system reports.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_task_orchestrator.infrastructure.monitoring import (
    HealthChecker, SystemMonitor, DiagnosticRunner,
    get_metrics_collector, get_system_monitor
)
from mcp_task_orchestrator.infrastructure.di import get_container
from mcp_task_orchestrator.domain import TaskRepository, StateRepository


async def run_health_checks():
    """Run comprehensive health checks."""
    print("🏥 Running Health Checks...")
    
    # Try to get repositories from DI container
    task_repo = None
    state_repo = None
    
    try:
        container = get_container()
        if container:
            task_repo = container.get_service(TaskRepository)
            state_repo = container.get_service(StateRepository)
    except Exception as e:
        print(f"⚠️  Could not access DI container: {e}")
    
    # Create health checker
    health_checker = HealthChecker(task_repo, state_repo)
    
    # Run all health checks
    results = await health_checker.run_all_checks()
    
    # Display results
    overall_healthy = health_checker.get_overall_health(results)
    
    print(f"\n{'✅' if overall_healthy else '❌'} Overall Health: {'HEALTHY' if overall_healthy else 'UNHEALTHY'}")
    print(f"📊 Checks Run: {len(results)}")
    
    for name, result in results.items():
        status_icon = "✅" if result.healthy else "❌"
        print(f"  {status_icon} {name}: {result.message}")
        if not result.healthy and result.details:
            for key, value in result.details.items():
                print(f"    - {key}: {value}")
    
    return overall_healthy


async def run_diagnostics():
    """Run comprehensive system diagnostics."""
    print("\n🔍 Running System Diagnostics...")
    
    # Setup diagnostic runner
    diagnostic_runner = DiagnosticRunner()
    
    # Run all diagnostics
    results = await diagnostic_runner.run_all_diagnostics()
    
    # Display results
    status_counts = {"pass": 0, "warning": 0, "error": 0, "info": 0}
    for result in results.values():
        status_counts[result.status] += 1
    
    print(f"\n📋 Diagnostic Summary:")
    print(f"  ✅ Passed: {status_counts['pass']}")
    print(f"  ⚠️  Warnings: {status_counts['warning']}")
    print(f"  ❌ Errors: {status_counts['error']}")
    print(f"  ℹ️  Info: {status_counts['info']}")
    
    # Show detailed results
    for name, result in results.items():
        status_icons = {"pass": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}
        icon = status_icons[result.status]
        print(f"\n{icon} {result.name} ({result.category})")
        print(f"   {result.message}")
        
        if result.recommendations:
            print("   Recommendations:")
            for rec in result.recommendations:
                print(f"   - {rec}")
    
    return status_counts["error"] == 0


def run_system_monitoring():
    """Display current system monitoring status."""
    print("\n📊 System Monitoring Status...")
    
    # Get system monitor
    system_monitor = get_system_monitor()
    
    # Display monitoring status
    status = system_monitor.get_monitoring_status()
    print(f"  Monitoring Active: {'✅' if status['monitoring_active'] else '❌'}")
    print(f"  Collection Interval: {status['collection_interval']}s")
    print(f"  Alert Rules: {status['alert_rules_count']}")
    print(f"  Active Alerts: {status['active_alerts']}")
    
    # Get metrics summary
    metrics_collector = get_metrics_collector()
    metrics_report = metrics_collector.get_metrics_report()
    
    print(f"\n📈 Metrics Summary:")
    print(f"  Uptime: {metrics_report['uptime_seconds']:.0f}s")
    print(f"  Total Metrics: {metrics_report['total_metrics']}")
    
    if metrics_report.get('last_minute'):
        print("  Last Minute Activity:")
        for metric, data in list(metrics_report['last_minute'].items())[:5]:
            print(f"    {metric}: {data['count']} events, avg {data['avg']:.2f}")


async def generate_full_report(output_file: str = None):
    """Generate comprehensive system report."""
    print("\n📄 Generating Comprehensive Report...")
    
    report_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "report_type": "comprehensive_system_analysis"
    }
    
    # Health checks
    try:
        health_checker = HealthChecker()
        health_results = await health_checker.run_all_checks()
        report_data["health_checks"] = {
            "overall_healthy": health_checker.get_overall_health(health_results),
            "results": {name: {
                "healthy": result.healthy,
                "message": result.message,
                "duration_ms": result.duration_ms,
                "details": result.details
            } for name, result in health_results.items()}
        }
    except Exception as e:
        report_data["health_checks"] = {"error": str(e)}
    
    # Diagnostics
    try:
        diagnostic_runner = DiagnosticRunner()
        diagnostic_results = await diagnostic_runner.run_all_diagnostics()
        report_data["diagnostics"] = {name: {
            "status": result.status,
            "category": result.category,
            "message": result.message,
            "recommendations": result.recommendations,
            "details": result.details
        } for name, result in diagnostic_results.items()}
    except Exception as e:
        report_data["diagnostics"] = {"error": str(e)}
    
    # System monitoring
    try:
        system_monitor = get_system_monitor()
        monitoring_status = system_monitor.get_monitoring_status()
        metrics_report = get_metrics_collector().get_metrics_report()
        
        report_data["system_monitoring"] = {
            "status": monitoring_status,
            "metrics": metrics_report
        }
    except Exception as e:
        report_data["system_monitoring"] = {"error": str(e)}
    
    # Save or display report
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"📄 Report saved to: {output_file}")
    else:
        print("\n📄 System Report:")
        print(json.dumps(report_data, indent=2))
    
    return report_data


async def main():
    """Main entry point for the health check tool."""
    parser = argparse.ArgumentParser(description="MCP Task Orchestrator Health Check Tool")
    parser.add_argument("--health", action="store_true", help="Run health checks only")
    parser.add_argument("--diagnostics", action="store_true", help="Run diagnostics only")
    parser.add_argument("--monitoring", action="store_true", help="Show monitoring status only")
    parser.add_argument("--report", type=str, help="Generate full report (optionally save to file)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    args = parser.parse_args()
    
    print("🚀 MCP Task Orchestrator Health Check Tool")
    print("=" * 50)
    
    overall_healthy = True
    
    try:
        if args.health or (not any([args.diagnostics, args.monitoring, args.report])):
            health_result = await run_health_checks()
            overall_healthy = overall_healthy and health_result
        
        if args.diagnostics or (not any([args.health, args.monitoring, args.report])):
            diagnostic_result = await run_diagnostics()
            overall_healthy = overall_healthy and diagnostic_result
        
        if args.monitoring:
            run_system_monitoring()
        
        if args.report is not None:
            await generate_full_report(args.report if args.report else None)
        
        print(f"\n{'✅' if overall_healthy else '❌'} Overall System Status: {'HEALTHY' if overall_healthy else 'NEEDS ATTENTION'}")
        
        # Exit with appropriate code
        sys.exit(0 if overall_healthy else 1)
    
    except KeyboardInterrupt:
        print("\n🛑 Health check interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())