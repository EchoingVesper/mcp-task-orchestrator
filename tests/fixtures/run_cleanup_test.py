import sys
import subprocess

print("Running cleanup_stale_locks test...")
result = subprocess.run([sys.executable, r"E:\My Work\Programming\MCP Task Orchestrator\test_cleanup_locks.py"], 
                       capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
