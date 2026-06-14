"""
Purpose: Connection Manager for SQLite database.
Inputs:
    - db_path: Optional[str] (absolute path to the sqlite file)
Outputs:
    - SQLiteManager (Singleton class representing the connection manager)
Complexity: O(1) connection setup.
Production Concerns: Concurrent database access; enabling WAL mode to allow readers to proceed while writers write; thread safety.
Future Improvements: Support full connection pooling if database write traffic scales heavily.
"""
import sqlite3
import threading
import os
from typing import Optional

class SQLiteManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SQLiteManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db_path: Optional[str] = None):
        if getattr(self, "_initialized", False):
            return
            
        self.db_path = db_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/argus_ai.db")
        )
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Establish connection. check_same_thread=False allows sharing across FastAPI worker threads.
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0  # Avoid database locked errors under concurrency
        )
        self.conn.row_factory = sqlite3.Row
        
        # Configure PRAGMA parameters
        # WAL (Write-Ahead Logging) allows concurrent reads while writes are active
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.commit()
        
        self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Returns the raw connection object."""
        return self.conn

    def execute_write(self, sql: str, params: tuple = ()) -> int:
        """Executes a single write query inside a thread lock."""
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor.rowcount

    def execute_read(self, sql: str, params: tuple = ()) -> list:
        """Executes a read query and returns rows."""
        # Row reads can run concurrently if connection check_same_thread is False
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def close(self):
        """Closes connection safely."""
        with self._lock:
            if getattr(self, "conn", None):
                self.conn.close()
                self.conn = None
