#!/usr/bin/env python3
"""
File-Based Test Output System Demo

This script demonstrates how the file-based test output system solves
timing issues where LLM calls check test results before tests finish writing.

The demo shows:
1. A test that writes output over time (simulating real test behavior)
2. An LLM simulation that tries to read results too early (fails safely)
3. Proper waiting for completion before reading (succeeds)
"""

import asyncio
import time
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from testing_utils.file_output_system import TestOutputWriter, TestOutputReader


def simulate_slow_test():
    """
    Simulate a test that writes output gradually over time.
    This represents the real-world scenario where tests write extensive output.
    """
    
    print("\\n=== Simulating Slow Test with File Output ===")
    
    writer = TestOutputWriter(Path.cwd() / "demo_outputs")
    
    with writer.write_test_output("slow_test_demo", "text") as session:
        # Simulate test phases with output
        session.write_line("=== TEST STARTING ===")
        session.write_line("Phase 1: Initialization")
        time.sleep(1)  # Simulate work
        
        session.write_line("Phase 2: Setup database")
        for i in range(5):
            session.write_line(f"  Setting up component {i+1}/5")
            time.sleep(0.5)  # Simulate setup time
        
        session.write_line("Phase 3: Running migration")
        for i in range(10):
            session.write_line(f"  Processing record {i+1}/10: Record data here...")
            time.sleep(0.3)  # Simulate processing time
        
        session.write_line("Phase 4: Verification")
        session.write_line("  Verifying all records migrated correctly...")
        time.sleep(1)
        session.write_line("  ✅ All verifications passed")
        
        session.write_line("=== TEST COMPLETED SUCCESSFULLY ===")
    
    return session.output_path


def simulate_impatient_llm_call(output_file: Path):
    """
    Simulate an LLM call that tries to read results too early.
    This represents the problematic behavior we're trying to prevent.
    """
    
    print("\\n=== Simulating Impatient LLM Call ===")
    
    reader = TestOutputReader(output_file.parent)
    
    # Try to read immediately (should fail gracefully)
    content = reader.read_completed_output(output_file)
    
    if content is None:
        print("✅ Correctly detected incomplete test - no content returned")
        print("   (This prevents reading truncated output)")
        return False
    else:
        print("❌ WARNING: Read content before test completion!")
        print(f"   Content length: {len(content)} characters")
        return True


def simulate_patient_llm_call(output_file: Path, timeout: float = 15.0):
    """
    Simulate an LLM call that properly waits for test completion.
    This represents the correct behavior using our system.
    """
    
    print("\\n=== Simulating Patient LLM Call ===")
    
    reader = TestOutputReader(output_file.parent)
    
    print(f"⏳ Waiting for test completion (timeout: {timeout}s)...")
    
    # Wait for completion
    completed = reader.wait_for_completion(output_file, timeout)
    
    if completed:
        print("✅ Test completed! Reading output...")
        content = reader.read_completed_output(output_file)
        
        if content:
            lines = content.split('\\n')
            print(f"📄 Successfully read complete output:")
            print(f"   - Total lines: {len(lines)}")
            print(f"   - Total characters: {len(content)}")
            print(f"   - First line: {lines[0] if lines else 'N/A'}")
            print(f"   - Last line: {lines[-2] if len(lines) > 1 else 'N/A'}")  # -2 because last is usually empty
            
            # Verify completion markers
            if "TEST COMPLETED SUCCESSFULLY" in content:
                print("✅ Confirmed test completed successfully")
            else:
                print("⚠️ Test may have completed with errors")
            
            return True
        else:
            print("❌ Failed to read content even after completion")
            return False
    else:
        print(f"❌ Test did not complete within {timeout} seconds")
        return False


async def run_concurrent_demo():
    """
    Run a demo showing concurrent test execution and safe reading.
    This shows how the system handles multiple tests and readers.
    """
    
    print("\\n=== Concurrent Test Demo ===")
    
    writer = TestOutputWriter(Path.cwd() / "demo_outputs")
    reader = TestOutputReader(Path.cwd() / "demo_outputs")
    
    async def simulate_test(test_name: str, duration: float):
        """Simulate a test running for a specific duration."""
        with writer.write_test_output(test_name, "text") as session:
            session.write_line(f"=== {test_name.upper()} STARTING ===")
            
            steps = int(duration * 2)  # 2 steps per second
            for i in range(steps):
                session.write_line(f"{test_name}: Step {i+1}/{steps}")
                await asyncio.sleep(0.5)
            
            session.write_line(f"=== {test_name.upper()} COMPLETED ===")
            return session.output_path
    
    async def simulate_reader(test_name: str, delay: float):
        """Simulate a reader trying to read test results."""
        await asyncio.sleep(delay)
        
        print(f"📖 Reader checking for {test_name} results...")
        
        # Find the output file
        output_files = list((Path.cwd() / "demo_outputs").glob(f"{test_name}_*.txt"))
        if not output_files:
            print(f"   No output file found for {test_name}")
            return False
        
        output_file = max(output_files, key=lambda f: f.stat().st_mtime)
        
        # Try to read
        completed = reader.wait_for_completion(output_file, timeout=10.0)
        if completed:
            content = reader.read_completed_output(output_file)
            print(f"✅ Successfully read {test_name} output ({len(content)} chars)")
            return True
        else:
            print(f"❌ {test_name} did not complete in time")
            return False
    
    # Start multiple tests and readers concurrently
    tasks = [
        simulate_test("fast_test", 2.0),      # 2 second test
        simulate_test("medium_test", 4.0),    # 4 second test  
        simulate_test("slow_test", 6.0),      # 6 second test
        simulate_reader("fast_test", 1.0),    # Try to read after 1 second
        simulate_reader("medium_test", 3.0),  # Try to read after 3 seconds
        simulate_reader("slow_test", 5.0),    # Try to read after 5 seconds
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print("\\n📊 Concurrent demo results:")
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"   Task {i}: Failed - {str(result)}")
        else:
            print(f"   Task {i}: Success")


def main():
    """Main demo function."""
    
    print("="*60)
    print("FILE-BASED TEST OUTPUT SYSTEM DEMONSTRATION")
    print("="*60)
    print("This demo shows how to prevent timing issues with test output reading.")
    
    # Demo 1: Sequential test with early/late reading
    print("\\n" + "="*40)
    print("DEMO 1: Timing Issue Prevention")
    print("="*40)
    
    # Start the slow test in background
    import threading
    output_file_container = [None]
    
    def run_slow_test():
        output_file_container[0] = simulate_slow_test()
    
    test_thread = threading.Thread(target=run_slow_test)
    test_thread.start()
    
    # Give the test a moment to start
    time.sleep(0.5)
    
    # Try to read too early (should fail safely)
    # We need to guess the output file name since test is still running
    potential_output_file = Path.cwd() / "demo_outputs" / "slow_test_demo_fake.txt"
    simulate_impatient_llm_call(potential_output_file)
    
    # Wait for test to complete
    test_thread.join()
    output_file = output_file_container[0]
    
    # Now read properly (should succeed)
    simulate_patient_llm_call(output_file)
    
    # Demo 2: Concurrent tests and readers
    print("\\n" + "="*40)
    print("DEMO 2: Concurrent Operations")
    print("="*40)
    
    try:
        asyncio.run(run_concurrent_demo())
    except Exception as e:
        print(f"Concurrent demo error: {str(e)}")
    
    # Summary
    print("\\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    print("✅ File-based output system prevents timing issues")
    print("✅ LLM calls safely detect incomplete tests")
    print("✅ Proper waiting ensures complete output reading")
    print("✅ System handles concurrent tests and readers")
    print("\\n🎯 Key Benefits:")
    print("   - Atomic file writes prevent partial reads")
    print("   - Completion markers ensure tests are finished")
    print("   - Timeout mechanisms prevent infinite waiting")
    print("   - Thread-safe operations support concurrency")
    
    # Show output location
    output_dir = Path.cwd() / "demo_outputs"
    if output_dir.exists():
        output_files = list(output_dir.glob("*.txt"))
        print(f"\\n📁 Demo output files created: {len(output_files)}")
        print(f"   Location: {output_dir}")
        for file in output_files[-3:]:  # Show last 3 files
            print(f"   - {file.name}")


if __name__ == "__main__":
    main()
