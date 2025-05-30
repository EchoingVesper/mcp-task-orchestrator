import sys
sys.path.insert(0, r"E:\My Work\Programming\MCP Task Orchestrator")

from migrate_artifacts import main
print("Starting migration...")
result = main()
print(f"Migration result: {result}")
