# src-backend/create_db.py
import sqlite3
import os
import lancedb
from sentence_transformers import SentenceTransformer

# --- Database Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = "wise_memory.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)
LANCEDB_DIR = os.path.join(SCRIPT_DIR, "lancedb")

def create_sqlite_tables():
    """Create the SQLite database file and the necessary tables."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Successfully connected to/created SQLite DB at {DB_PATH}")
        cursor = conn.cursor()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS conversation_log (
            turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            actor TEXT NOT NULL,
            content TEXT NOT NULL,
            active_lens TEXT,
            metadata_json TEXT
        );
        """
        cursor.execute(create_table_sql)
        print("✅ Table 'conversation_log' is ready.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if conn:
            conn.close()

def create_lancedb_table():
    """Create the LanceDB vector store and the semantic_memory table."""
    print("\n🧠 Initializing Semantic Memory (LanceDB)...")
    try:
        db = lancedb.connect(LANCEDB_DIR)
        
        # We need a small piece of text to infer the schema from the embedding model
        # This is a standard pattern for creating a LanceDB table
        print("Creating embedding for schema inference...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode("This is a test sentence.")
        
        schema_data = [{
            "vector": embedding,
            "text": "test",
            "source_id": "test"
        }]

        # Create the table if it doesn't exist
        if "semantic_memory" not in db.table_names():
            db.create_table("semantic_memory", data=schema_data)
            print("✅ Table 'semantic_memory' created in LanceDB.")
        else:
            print("✅ Table 'semantic_memory' already exists.")
            
    except Exception as e:
        print(f"❌ LanceDB error: {e}")

if __name__ == '__main__':
    print("--- Architecting the Sovereign Second Brain ---")
    create_sqlite_tables()
    create_lancedb_table()
    print("\n🎉 Brain architecture is complete.")