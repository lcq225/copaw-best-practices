"""
MemoryCoreClaw - Working Memory Module

Implements limited-capacity temporary storage (7±2 model).
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
from dataclasses import dataclass
import json


@dataclass
class WorkingItem:
    """An item in working memory"""
    key: str
    value: Any
    priority: float
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0


class WorkingMemory:
    """
    Working Memory Engine
    
    Based on Baddeley's working memory model with capacity limit.
    
    Features:
    - Limited capacity (default 9 items, 7±2)
    - Priority-based eviction
    - TTL support
    - Access tracking
    
    Usage:
        wm = WorkingMemory()
        wm.hold("task", "processing", priority=0.9)
        task = wm.retrieve("task")
    """
    
    DEFAULT_CAPACITY = 9  # 7±2 model
    
    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        """
        Initialize working memory.
        
        Args:
            capacity: Maximum items (default 9)
        """
        self.capacity = capacity
        self.items: Dict[str, WorkingItem] = {}
        self.stats = {
            'adds': 0,
            'retrieves': 0,
            'evictions': 0,
            'expirations': 0
        }
    
    def hold(
        self,
        key: str,
        value: Any,
        priority: float = 0.5,
        ttl_seconds: int = None
    ) -> bool:
        """
        Store an item in working memory.
        
        Args:
            key: Item key
            value: Item value
            priority: Priority (0-1, higher = less likely to evict)
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if stored successfully
        """
        # Evict if at capacity
        if len(self.items) >= self.capacity and key not in self.items:
            self._evict_lowest_priority()
        
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        self.items[key] = WorkingItem(
            key=key,
            value=value,
            priority=priority,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        self.stats['adds'] += 1
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve an item from working memory.
        
        Args:
            key: Item key
            
        Returns:
            Item value or None if not found/expired
        """
        if key not in self.items:
            return None
        
        item = self.items[key]
        
        # Check expiration
        if item.expires_at and datetime.now() > item.expires_at:
            del self.items[key]
            self.stats['expirations'] += 1
            return None
        
        item.access_count += 1
        self.stats['retrieves'] += 1
        return item.value
    
    def forget(self, key: str) -> bool:
        """Remove an item"""
        if key in self.items:
            del self.items[key]
            return True
        return False
    
    def clear(self) -> int:
        """Clear all items"""
        count = len(self.items)
        self.items.clear()
        return count
    
    def _evict_lowest_priority(self):
        """Evict the lowest priority item"""
        if not self.items:
            return
        
        # Find lowest priority item
        lowest_key = min(self.items.keys(), key=lambda k: self.items[k].priority)
        del self.items[lowest_key]
        self.stats['evictions'] += 1
    
    def get_all(self) -> List[Dict]:
        """Get all items"""
        self._clean_expired()
        return [
            {
                'key': item.key,
                'value': item.value,
                'priority': item.priority,
                'created_at': item.created_at.isoformat(),
                'expires_at': item.expires_at.isoformat() if item.expires_at else None
            }
            for item in self.items.values()
        ]
    
    def _clean_expired(self):
        """Remove expired items"""
        now = datetime.now()
        expired = [
            key for key, item in self.items.items()
            if item.expires_at and now > item.expires_at
        ]
        for key in expired:
            del self.items[key]
            self.stats['expirations'] += 1
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        self._clean_expired()
        return {
            'capacity': self.capacity,
            'used': len(self.items),
            'utilization': len(self.items) / self.capacity,
            'stats': self.stats
        }