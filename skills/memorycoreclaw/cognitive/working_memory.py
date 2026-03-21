"""
MemoryCoreClaw - Cognitive Module: Working Memory

Limited capacity temporary storage (7±2 items).
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
import sqlite3


@dataclass
class WorkingItem:
    """Item in working memory."""
    key: str
    value: Any
    priority: float
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0


class WorkingMemory:
    """
    Working memory with limited capacity.
    
    Features:
    - Capacity limit (default 9 items, 7±2 model)
    - Priority-based eviction
    - TTL (time-to-live) support
    - LRU eviction
    - Session isolation
    """
    
    DEFAULT_CAPACITY = 9
    
    def __init__(self, db_path: str, session_id: str = "default", 
                 capacity: int = DEFAULT_CAPACITY):
        self.db_path = db_path
        self.session_id = session_id
        self.capacity = capacity
        self._init_tables()
    
    def _init_tables(self):
        """Initialize working memory table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS working_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                priority REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_working_session 
            ON working_memory(session_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def add(self, key: str, value: Any, priority: float = 0.5,
            ttl_seconds: Optional[int] = None) -> bool:
        """
        Add item to working memory.
        
        Args:
            key: Item key
            value: Item value (will be JSON serialized)
            priority: Priority (0-1, higher = more important)
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if added, False if evicted
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check capacity
        cursor.execute('''
            SELECT COUNT(*) FROM working_memory 
            WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (self.session_id, datetime.now().isoformat()))
        
        count = cursor.fetchone()[0]
        
        # Evict if over capacity
        evicted = False
        while count >= self.capacity:
            # Evict lowest priority, oldest accessed
            cursor.execute('''
                DELETE FROM working_memory 
                WHERE id = (
                    SELECT id FROM working_memory 
                    WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY priority ASC, last_accessed ASC 
                    LIMIT 1
                )
            ''', (self.session_id, datetime.now().isoformat()))
            count -= 1
            evicted = True
        
        # Calculate expiry
        expires_at = None
        if ttl_seconds:
            expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
        
        # Add item
        cursor.execute('''
            INSERT OR REPLACE INTO working_memory 
            (session_id, key, value, priority, created_at, expires_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.session_id, key, json.dumps(value), priority, 
              datetime.now().isoformat(), expires_at, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return evicted
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from working memory.
        
        Args:
            key: Item key
            
        Returns:
            Item value or None if not found/expired
        """
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value, expires_at FROM working_memory 
            WHERE session_id = ? AND key = ?
        ''', (self.session_id, key))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        value, expires_at = result
        
        # Check expiry
        if expires_at:
            if datetime.fromisoformat(expires_at) < datetime.now():
                cursor.execute('''
                    DELETE FROM working_memory 
                    WHERE session_id = ? AND key = ?
                ''', (self.session_id, key))
                conn.commit()
                conn.close()
                return None
        
        # Update access
        cursor.execute('''
            UPDATE working_memory 
            SET last_accessed = ?, access_count = access_count + 1
            WHERE session_id = ? AND key = ?
        ''', (datetime.now().isoformat(), self.session_id, key))
        
        conn.commit()
        conn.close()
        
        return json.loads(value)
    
    def remove(self, key: str):
        """Remove item from working memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM working_memory 
            WHERE session_id = ? AND key = ?
        ''', (self.session_id, key))
        
        conn.commit()
        conn.close()
    
    def clear(self):
        """Clear all items for this session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM working_memory WHERE session_id = ?
        ''', (self.session_id,))
        
        conn.commit()
        conn.close()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items.
        
        Returns:
            Number of items removed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM working_memory 
            WHERE expires_at IS NOT NULL AND expires_at < ?
        ''', (datetime.now().isoformat(),))
        
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        
        return removed
    
    @property
    def used(self) -> int:
        """Number of items currently in working memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM working_memory 
            WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (self.session_id, datetime.now().isoformat()))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all items in working memory."""
        import json
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT key, value, priority, created_at, expires_at 
            FROM working_memory 
            WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY priority DESC
        ''', (self.session_id, datetime.now().isoformat()))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'key': row[0],
                'value': json.loads(row[1]),
                'priority': row[2],
                'created_at': row[3],
                'expires_at': row[4]
            })
        
        conn.close()
        return items