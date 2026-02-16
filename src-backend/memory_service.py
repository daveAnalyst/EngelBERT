# src-backend/memory_service.py
import sqlite3
import os
import lancedb
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
import pandas as pd

# --- Database Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = "wise_memory.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)
LANCEDB_DIR = os.path.join(SCRIPT_DIR, "lancedb")

class MemoryService:
    """
    The single interface for interacting with the Sovereign Second Brain's memory.
    Manages both SQLite (Episodic) and LanceDB (Semantic).
    """

    def __init__(self, db_path: str = DB_PATH, lancedb_dir: str = LANCEDB_DIR):
        # SQLite Connection
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        # LanceDB Connection
        self._lancedb_client = lancedb.connect(lancedb_dir)
        self._semantic_table = self._lancedb_client.open_table("semantic_memory")
        # Load Embedding Model
        print("🧠 MemoryService: Loading embedding model (all-MiniLM-L6-v2)...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ MemoryService is fully initialized.")

    def close_connection(self):
        if self._conn: self._conn.close()

    # --- Episodic Memory (SQLite) ---
    def add_log_entry(self, session_id: str, actor: str, content: str, active_lens: Optional[str] = None, metadata_json: Optional[str] = None):
        sql = ''' INSERT INTO conversation_log(session_id, actor, content, active_lens, metadata_json) VALUES(?,?,?,?,?) '''
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, (session_id, actor, content, active_lens, metadata_json))
            self._conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"❌ Failed to add log entry: {e}")

     # --- THE FINAL, CORRECTED VERSION ---
    def get_recent_history(self, session_id: str, limit: int = 10) -> List[Tuple]:
        """
        Retrieves the most recent turns for a given session_id,
        and returns them in the correct chronological order (oldest to newest).
        """
        if not self._conn:
            print("❌ Error: No database connection.")
            return []

        # This SQL correctly gets the N most recent messages, with the newest one first.
        sql = """ SELECT actor, content 
                  FROM conversation_log 
                  WHERE session_id = ? 
                  ORDER BY timestamp DESC 
                  LIMIT ? """
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, (session_id, limit))
            rows = cursor.fetchall()
            
            # This is the CRUCIAL FIX: we reverse the list in Python
            # so it's in the correct chronological order for the AI to read.
            return list(reversed(rows))
        
        except sqlite3.Error as e:
            print(f"❌ Failed to get history: {e}")
            return []

    # --- Semantic Memory (LanceDB) ---
    def process_and_store_document(self, content: str, source_id: str):
        print(f"🧠 Processing document from source: {source_id}...")
        try:
            existing = self._semantic_table.search().where(f"source_id = '{source_id}'").limit(1).to_pandas()
            if not existing.empty:
                self._semantic_table.delete(f"source_id = '{source_id}'")
                print(f"🧹 Cleaned up old entries for {source_id}.")
        except Exception as e:
            print(f"ℹ️ Could not clean up old entries (this is normal on first run): {e}")

        chunks = [chunk for chunk in content.split('\n') if chunk.strip() and len(chunk) > 10]
        if not chunks:
            print(f"⚠️ Document '{source_id}' is empty or has no content to process.")
            return

        print(f"Split document into {len(chunks)} chunks. Generating embeddings...")
        embeddings = self.embedding_model.encode(chunks)
        
        data_to_add = [{"vector": embeddings[i], "text": chunk_text, "source_id": source_id} for i, chunk_text in enumerate(chunks)]
        
        try:
            self._semantic_table.add(data_to_add)
            print(f"✅ Successfully added {len(chunks)} new chunks for {source_id}.")
        except Exception as e:
            print(f"❌ Failed to add data to LanceDB: {e}")

    def find_relevant_chunks(self, query_text: str, top_k: int = 3) -> List[dict]:
        print(f"🔍 Performing semantic search for: '{query_text[:30]}...'")
        try:
            query_embedding = self.embedding_model.encode(query_text)
            results = self._semantic_table.search(query_embedding).limit(top_k).to_pandas()
            return results.to_dict('records')
        except Exception as e:
            print(f"❌ Failed to perform semantic search: {e}")
            return []
    def log_insight(self, note_a: str, note_b: str, insight: str):
        """Saves a generated insight to the log for the UI to fetch."""
        # We store it in conversation_log with a special actor name "dreamer"
        self.add_log_entry(
            session_id="dream_cycle",
            actor="dreamer",
            content=insight,
            metadata_json=f"Linked: {note_a[:20]}... <-> {note_b[:20]}..."
        )
        print("   💾 Insight saved to Episodic Memory.")