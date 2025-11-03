# In src-backend/test_memory.py

import uuid
from memory_service import MemoryService  # Make sure this import path matches your project structure

def run_all_memory_tests():
    """
    A comprehensive test suite for the entire MemoryService.
    """
    print("--- 🧠 Starting Full MemoryService Test Suite 🧠 ---")
    
    memory = MemoryService()
    
    # --- Test 1: Episodic Memory (SQLite) ---
    print("\n--- Test 1: Verifying Episodic Memory (SQLite) ---")
    test_session_id = str(uuid.uuid4())
    print(f"Using test session ID: {test_session_id}")
    
    # Add entries
    memory.add_log_entry(test_session_id, "user", "Hello, SQLite!")
    memory.add_log_entry(test_session_id, "ai", "Hello! I am storing this conversation.")
    
    # Get history
    history = memory.get_recent_history(test_session_id)
    
    # --- NEW, MORE ROBUST CHECKS ---
    print("DEBUG: Retrieved history:")
    print(history)
    
    assert len(history) == 2, f"Episodic history should have 2 entries, but found {len(history)}."
    assert history[0][0] == "user", f"Expected first actor to be 'user', but got '{history[0][0]}'."
    assert "Hello, SQLite!" in history[0][1], "Episodic history content is missing the expected text."
    print("✅ Episodic Memory (SQLite) is working correctly.")

    # ... (The rest of the test script remains exactly the same) ...

    print("\n--- ✅ All MemoryService Tests Passed Successfully ✅ ---")

if __name__ == '__main__':
    run_all_memory_tests()