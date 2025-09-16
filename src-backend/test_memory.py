# src-backend/database/test_memory.py
import sys
import os
import uuid

# This is a bit of a hack to allow this script to import the MemoryService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory_service import MemoryService

def run_test():
    print("--- Starting MemoryService Test ---")
    memory = MemoryService()
    
    # Generate a unique session ID for this test run
    test_session_id = str(uuid.uuid4())
    print(f"Using test session ID: {test_session_id}")

    # Test 1: Add some data
    print("\n--- Test 1: Adding log entries ---")
    memory.add_log_entry(test_session_id, "user", "Hello, Wise!")
    memory.add_log_entry(test_session_id, "ai", "Hello! How can I help you think today?", "Scholar")
    memory.add_log_entry(test_session_id, "user", "What is cognitive augmentation?")

    # Test 2: Retrieve the data
    print("\n--- Test 2: Retrieving recent history ---")
    history = memory.get_recent_history(test_session_id, limit=5)
    
    if history:
        print("Successfully retrieved history:")
        for actor, content in history:
            print(f"  [{actor}]: {content}")
    else:
        print("Failed to retrieve history.")

    # Clean up
    memory.close_connection()
    print("\n--- MemoryService Test Finished ---")

if __name__ == '__main__':
    run_test()