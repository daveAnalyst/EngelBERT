# src-backend/create_db.py
import sqlite3
import os

# This ensures we create the database in the same directory as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = "wise_memory.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)

def create_db_and_tables():
    """Create a database file and the necessary tables."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Successfully connected to/created SQLite DB at {DB_PATH}")
        
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
        print("Table 'conversation_log' created or already exists.")
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
            print("SQLite connection closed.")

if __name__ == '__main__':
    create_db_and_tables()