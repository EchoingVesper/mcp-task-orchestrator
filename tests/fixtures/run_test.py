import sys
import subprocess

print("Running artifacts validation test...")
result = subprocess.run([sys.executable, r"E:\My Work\Programming\MCP Task Orchestrator\test_artifacts_fix.py"], 
                       capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
