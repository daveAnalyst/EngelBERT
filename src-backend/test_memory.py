# src-backend/test_memory.py
import uuid
from memory_service import MemoryService
import pandas as pd

def run_all_memory_tests():
    """
    A comprehensive and robust test suite for the entire MemoryService.
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
    
    # The new, more robust checks
    print("DEBUG: Retrieved history:")
    print(history)
    
    assert len(history) == 2, f"Episodic history should have 2 entries, but found {len(history)}."
    assert history[0][0] == "user", f"Expected first actor to be 'user', but got '{history[0][0]}'."
    assert "Hello, SQLite!" in history[0][1], "Episodic history content is missing the expected text."
    print("✅ Episodic Memory (SQLite) is working correctly.")

    # --- Test 2: Semantic Memory (LanceDB) ---
    print("\n--- Test 2: Verifying Semantic Memory (LanceDB) ---")
    sample_document_text = """
    Cognitive Augmentation is a field focused on enhancing human intellect.
    The goal is to build tools that help humans think better.
    Sovereignty is a key principle for a true thought partner.
    """
    memory.process_and_store_document(
        content=sample_document_text, 
        source_id="test_doc_1"
    )
    
    query = "How can we improve human thinking?"
    relevant_chunks = memory.find_relevant_chunks(query, top_k=1)
    
    assert len(relevant_chunks) > 0, "Semantic search should return at least one chunk."
    assert "think better" in relevant_chunks[0]['text'], "Semantic search result is not relevant."
    print("✅ Semantic Memory (LanceDB) processing and search is working.")
    
    # --- Test 3: Idempotency ---
    print("\n--- Test 3: Verifying Semantic Memory Idempotency ---")
    memory.process_and_store_document(
        content="This is a newer version with only one chunk.", 
        source_id="test_doc_1"
    )
    all_items = memory._semantic_table.search().limit(100).to_pandas()
    assert len(all_items) == 1, f"Idempotency failed. Expected 1 chunk for source_id 'test_doc_1', but found {len(all_items)}."
    print("✅ Semantic Memory (LanceDB) is idempotent.")

    # --- Cleanup ---
    memory.close_connection()
    print("\n--- ✅ All MemoryService Tests Passed Successfully ✅ ---")

if __name__ == '__main__':
    run_all_memory_tests()