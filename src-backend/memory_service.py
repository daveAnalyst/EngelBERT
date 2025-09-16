# src-backend/memory_service.py
import sqlite3
import os
from typing import List, Tuple, Optional

# This robust pathing ensures the database is always created next to this file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = "wise_memory.db"
DB_PATH = os.path.join(SCRIPT_DIR, DB_FILE)

class MemoryService:
    """
    The single interface for interacting with the Sovereign Second Brain's memory.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        # This flag tells Python to allow the connection to be used by different parts of our app
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        print("MemoryService initialized and connected to SQLite.")

    def close_connection(self):
        """Closes the SQLite database connection."""
        if self._conn:
            self._conn.close()
            print("SQLite connection closed.")

    def add_log_entry(self, session_id: str, actor: str, content: str, active_lens: str = None, metadata_json: str = None):
        """Adds a new turn from a conversation to the conversation_log table."""
        sql = ''' INSERT INTO conversation_log(session_id, actor, content, active_lens, metadata_json)
                  VALUES(?,?,?,?,?) '''
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, (session_id, actor, content, active_lens, metadata_json))
            self._conn.commit()
            print(f"Added log entry: {actor} - '{content[:20]}...'")
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Failed to add log entry: {e}")
            return None

    def get_recent_history(self, session_id: str, limit: int = 10) -> List[Tuple]:
        """Retrieves the most recent turns for a given session_id."""
        sql = """ SELECT actor, content 
                  FROM conversation_log 
                  WHERE session_id = ? 
                  ORDER BY timestamp DESC 
                  LIMIT ? """
        try:
            cursor = self._conn.cursor()
            cursor.execute(sql, (session_id, limit))
            rows = cursor.fetchall()
            return list(reversed(rows))
        except sqlite3.Error as e:
            print(f"Failed to get history: {e}")
            return []