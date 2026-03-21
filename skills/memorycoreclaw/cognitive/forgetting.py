"""
MemoryCoreClaw - Cognitive Module: Forgetting Curve

Implements Ebbinghaus forgetting curve for memory strength decay.
"""

import math
from datetime import datetime, timedelta
from typing import Optional
import sqlite3


class ForgettingCurve:
    """
    Ebbinghaus forgetting curve implementation.
    
    Formula: R = e^(-t/(S*100))
    Where:
        R = retention rate
        t = time since last access (days)
        S = memory strength (importance)
    
    Features:
    - Time-based decay
    - Importance-based strength
    - Emotion enhancement
    - Access reinforcement
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """Initialize memory strength table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_strength (
                memory_id INTEGER PRIMARY KEY,
                memory_type TEXT DEFAULT 'fact',
                base_strength REAL DEFAULT 0.5,
                current_strength REAL DEFAULT 0.5,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                decay_rate REAL DEFAULT 0.1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def calculate_retention(self, days_since_access: float, 
                           importance: float,
                           emotion: str = "neutral") -> float:
        """
        Calculate memory retention rate.
        
        Args:
            days_since_access: Days since last access
            importance: Memory importance (0-1)
            emotion: Emotional marker
            
        Returns:
            Retention rate (0-1)
        """
        # Base strength from importance
        strength = importance
        
        # Emotion enhancement
        emotion_multiplier = {
            "milestone": 1.5,
            "negative": 1.3,
            "positive": 1.2,
            "neutral": 1.0
        }
        strength *= emotion_multiplier.get(emotion, 1.0)
        
        # Ebbinghaus formula
        if days_since_access <= 0:
            return 1.0
        
        retention = math.exp(-days_since_access / (strength * 100))
        
        # Minimum retention
        return max(0.1, min(1.0, retention))
    
    def apply_forgetting_curve(self, min_importance: float = 0.3):
        """
        Apply forgetting curve to all memories.
        
        Memories below min_importance will be candidates for removal.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all facts
        cursor.execute('''
            SELECT f.id, f.importance, f.emotion, f.last_accessed, f.created_at
            FROM facts f
            WHERE f.importance >= ?
        ''', (min_importance,))
        
        facts = cursor.fetchall()
        updated = 0
        
        for fact_id, importance, emotion, last_accessed, created_at in facts:
            # Calculate days since access
            if last_accessed:
                last = datetime.fromisoformat(last_accessed)
            elif created_at:
                last = datetime.fromisoformat(created_at)
            else:
                last = datetime.now()
            
            days_since = (datetime.now() - last).days
            
            # Calculate new retention
            retention = self.calculate_retention(days_since, importance, emotion or "neutral")
            
            # Update strength
            new_strength = importance * retention
            
            # Core memories (importance >= 0.9) don't decay below 0.8
            if importance >= 0.9:
                new_strength = max(0.8, new_strength)
            
            cursor.execute('''
                INSERT OR REPLACE INTO memory_strength 
                (memory_id, memory_type, current_strength, last_accessed)
                VALUES (?, 'fact', ?, ?)
            ''', (fact_id, new_strength, datetime.now().isoformat()))
            
            updated += 1
        
        conn.commit()
        conn.close()
        
        return updated
    
    def reinforce_memory(self, memory_id: int, factor: float = 1.1):
        """
        Reinforce memory strength (called on access).
        
        Args:
            memory_id: Memory ID
            factor: Reinforcement factor (default 1.1 = 10% increase)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE memory_strength
            SET current_strength = MIN(1.0, current_strength * ?),
                access_count = access_count + 1,
                last_accessed = ?
            WHERE memory_id = ?
        ''', (factor, datetime.now().isoformat(), memory_id))
        
        conn.commit()
        conn.close()