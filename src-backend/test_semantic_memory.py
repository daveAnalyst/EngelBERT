# src-backend/test_semantic_memory.py
import sys
import os

# This allows the script to find and import our MemoryService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from memory_service import MemoryService

def run_semantic_test():
    """
    A dedicated test script for our new LanceDB semantic memory functions.
    """
    print("--- Starting Semantic Memory Test ---")
    
    # Initialize the full MemoryService. This will load the embedding model.
    # This might take a moment the first time you run it.
    memory = MemoryService()

    # --- Test 1: Add a "document" to our semantic memory ---
    print("\n--- Test 1: Processing and storing a document ---")
    
    # This is a sample document. In a real scenario, this would be read from a PDF or text file.
    sample_document_text = """
    Cognitive Augmentation is a field of research focused on enhancing human intellect.
    Unlike traditional AI, which often aims for automation, augmentation seeks to create a partnership.
    The goal is to build tools that help humans think better, reason more clearly, and be more creative.
    A key challenge in this field is the signal-to-noise ratio of AI-generated insights.
    Sovereignty and privacy are also paramount for a true thought partner.
    """
    
    memory.process_and_store_document(
        content=sample_document_text, 
        source_id="test_document_v1.txt"
    )

    # --- Test 2: Perform a semantic search ---
    print("\n--- Test 2: Performing a semantic search for a related concept ---")
    
    query = "How can we improve human thinking and creativity?"
    
    # This query doesn't use the exact words, but it's semantically similar.
    relevant_chunks = memory.find_relevant_chunks(query, top_k=2)
    
    if relevant_chunks:
        print("\n✅ Successfully found relevant chunks:")
        for i, chunk in enumerate(relevant_chunks):
            print(f"  Result {i+1}:")
            print(f"    Text: '{chunk['text']}'")
            print(f"    Source: {chunk['source_id']}")
            # LanceDB also returns a distance score. Lower is better.
            print(f"    Similarity Score (_distance): {chunk['_distance']:.4f}")
    else:
        print("\n❌ Failed to find any relevant chunks.")

    # Clean up the connection
    memory.close_connection()
    print("\n--- Semantic Memory Test Finished ---")

if __name__ == '__main__':
    run_semantic_test()

