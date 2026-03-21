"""
MemoryCoreClaw - Database Manager Module

Handles database connections and operations.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """
    Database Manager for MemoryCoreClaw
    
    Handles database connection, initialization, and basic operations.
    """
    
    def __init__(self, db_path: str = None, encrypt: bool = False):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to database file
            encrypt: Whether to use encryption (requires sqlcipher)
        """
        if db_path is None:
            db_dir = Path.home() / ".memorycoreclaw"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "memory.db")
        
        self.db_path = db_path
        self.encrypt = encrypt
        self._conn = None
    
    def connect(self) -> sqlite3.Connection:
        """Get database connection"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def execute(self, sql: str, params: tuple = None):
        """Execute SQL statement"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor
    
    def query(self, sql: str, params: tuple = None) -> list:
        """Execute query and return results"""
        conn = self.connect()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        return cursor.fetchall()
    
    def backup(self, backup_path: str):
        """Create database backup"""
        conn = self.connect()
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
    
    def get_size(self) -> int:
        """Get database file size in bytes"""
        return Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0