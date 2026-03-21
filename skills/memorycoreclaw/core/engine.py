"""
MemoryCoreClaw - Core Memory Engine

A human-brain-inspired memory system with:
- Layered memory (core/important/normal)
- Forgetting curve (Ebbinghaus model)
- Contextual memory triggers
- Working memory (limited capacity)
- Relation learning
"""

import sqlite3
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class MemoryLayer(Enum):
    """Memory importance layers"""
    CORE = 0.9       # Permanent, injected into context
    IMPORTANT = 0.7  # Long-term retention
    NORMAL = 0.5     # Periodic consolidation
    MINOR = 0.3      # May decay over time


class Emotion(Enum):
    """Emotional markers for memories"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MILESTONE = "milestone"


# Standard relation types
STANDARD_RELATIONS = {
    # Work relations
    'works_at', 'works_in', 'manages', 'collaborates_with', 'reports_to',
    # Location relations
    'located_in', 'part_of', 'connected_to',
    # Knowledge relations
    'knows', 'learned', 'teaches', 'studies',
    # Usage relations
    'uses', 'depends_on', 'implements', 'produces',
    # Preference relations
    'prefers', 'likes', 'dislikes', 'avoids',
    # Social relations
    'friend_of', 'family_of', 'partner_of', 'colleague_of',
    # Temporal relations
    'before', 'after', 'during', 'since',
    # Causal relations
    'causes', 'prevents', 'enables', 'hinders',
    # General relations
    'related_to', 'belongs_to', 'associated_with', 'similar_to',
}


@dataclass
class Fact:
    """A fact memory"""
    id: Optional[int] = None
    content: str = ""
    importance: float = 0.5
    category: str = "general"
    emotion: str = "neutral"
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0


@dataclass
class Lesson:
    """A learned lesson from experience"""
    id: Optional[int] = None
    action: str = ""
    context: str = ""
    outcome: str = "neutral"
    insight: str = ""
    importance: float = 0.5
    created_at: Optional[datetime] = None


@dataclass
class Context:
    """Memory context for contextual recall"""
    location: Optional[str] = None
    people: List[str] = field(default_factory=list)
    emotion: Optional[str] = None
    activity: Optional[str] = None
    channel: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class MemoryEngine:
    """
    Core Memory Engine
    
    Usage:
        engine = MemoryEngine()
        fact_id = engine.remember("Important info", importance=0.8)
        results = engine.recall("info")
    """
    
    # Standard relation types
    STANDARD_RELATIONS = {
        # Work relations
        'works_at', 'works_in', 'manages', 'collaborates_with', 'reports_to',
        # Location relations
        'located_in', 'part_of', 'connected_to',
        # Knowledge relations
        'knows', 'learned', 'teaches', 'studies',
        # Usage relations
        'uses', 'depends_on', 'implements', 'produces',
        # Preference relations
        'prefers', 'likes', 'dislikes', 'avoids',
        # Social relations
        'friend_of', 'family_of', 'partner_of', 'colleague_of',
        # Temporal relations
        'before', 'after', 'during', 'since',
        # Causal relations
        'causes', 'prevents', 'enables', 'hinders',
        # Other
        'related_to', 'belongs_to', 'associated_with', 'similar_to'
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize memory engine.
        
        Args:
            db_path: Path to SQLite database. Default: ~/.memorycoreclaw/memory.db
        """
        if db_path is None:
            db_dir = Path.home() / ".memorycoreclaw"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / "memory.db")
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Facts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                category TEXT DEFAULT 'general',
                emotion TEXT DEFAULT 'neutral',
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Experiences (lessons) table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                context TEXT,
                outcome TEXT CHECK(outcome IN ('positive', 'negative', 'neutral')),
                insight TEXT,
                importance REAL DEFAULT 0.5,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # Entities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Relations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entity TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                to_entity TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                evidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_entity, relation_type, to_entity)
            )
        ''')
        
        # Memory strength table (for forgetting curve)
        # Note: Using base_strength (matching actual DB schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_strength (
                memory_type TEXT NOT NULL,
                memory_id INTEGER NOT NULL,
                base_strength REAL DEFAULT 0.5,
                current_strength REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_decay TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                retention_rate REAL DEFAULT 1.0,
                PRIMARY KEY (memory_type, memory_id)
            )
        ''')
        
        # Contexts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT,
                people TEXT,
                emotion TEXT,
                activity TEXT,
                channel TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Memory-context bindings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_context_bindings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT NOT NULL,
                memory_id INTEGER NOT NULL,
                context_id INTEGER NOT NULL,
                match_score REAL DEFAULT 1.0,
                FOREIGN KEY (context_id) REFERENCES contexts(id)
            )
        ''')
        
        # Working memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS working_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT DEFAULT 'default',
                key TEXT NOT NULL,
                value TEXT,
                priority REAL DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                UNIQUE(session_id, key)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_content ON facts(content)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_from ON relations(from_entity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relations_to ON relations(to_entity)')
        
        conn.commit()
        conn.close()
    
    # ==================== Fact Operations ====================
    
    def remember(
        self,
        content: str,
        importance: float = 0.5,
        category: str = "general",
        emotion: str = "neutral",
        tags: List[str] = None
    ) -> int:
        """
        Store a fact in memory.
        
        Args:
            content: The fact content
            importance: Importance score (0-1)
            category: Category label
            emotion: Emotional marker
            tags: List of tags
            
        Returns:
            Fact ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else "[]"
        
        cursor.execute('''
            INSERT INTO facts (content, importance, category, emotion, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (content, importance, category, emotion, tags_json))
        
        fact_id = cursor.lastrowid
        
        # Initialize memory strength
        cursor.execute('''
            INSERT INTO memory_strength (memory_type, memory_id, base_strength, current_strength, last_decay)
            VALUES ('fact', ?, ?, ?, datetime('now'))
        ''', (fact_id, importance, importance))
        
        conn.commit()
        conn.close()
        
        return fact_id
    
    def recall(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for facts matching query.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching facts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, importance, category, emotion, tags, created_at
            FROM facts
            WHERE content LIKE ?
            ORDER BY importance DESC
            LIMIT ?
        ''', (f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'importance': row[2],
                'category': row[3],
                'emotion': row[4],
                'tags': json.loads(row[5]) if row[5] else [],
                'created_at': row[6]
            })
            
            # Record access (for forgetting curve)
            self._record_access('fact', row[0])
        
        conn.close()
        return results
    
    def get_fact(self, fact_id: int) -> Optional[Dict]:
        """Get a specific fact by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, content, importance, category, emotion, tags, created_at
            FROM facts WHERE id = ?
        ''', (fact_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'content': row[1],
                'importance': row[2],
                'category': row[3],
                'emotion': row[4],
                'tags': json.loads(row[5]) if row[5] else [],
                'created_at': row[6]
            }
        return None
    
    def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM facts WHERE id = ?', (fact_id,))
        cursor.execute('DELETE FROM memory_strength WHERE memory_type = ? AND memory_id = ?', 
                       ('fact', fact_id))
        cursor.execute('DELETE FROM memory_context_bindings WHERE memory_type = ? AND memory_id = ?',
                       ('fact', fact_id))
        
        conn.commit()
        conn.close()
        return True
    
    # ==================== Lesson Operations ====================
    
    def learn(
        self,
        action: str,
        context: str,
        outcome: str,
        insight: str,
        importance: float = 0.5
    ) -> int:
        """
        Learn a lesson from experience.
        
        Args:
            action: What was done
            context: The situation
            outcome: Result (positive/negative/neutral)
            insight: What was learned
            importance: Importance score
            
        Returns:
            Lesson ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO experiences (action, context, outcome, insight, importance)
            VALUES (?, ?, ?, ?, ?)
        ''', (action, context, outcome, insight, importance))
        
        lesson_id = cursor.lastrowid
        
        # Initialize strength
        cursor.execute('''
            INSERT INTO memory_strength (memory_type, memory_id, base_strength, current_strength, last_decay)
            VALUES ('experience', ?, ?, ?, datetime('now'))
        ''', (lesson_id, importance, importance))
        
        conn.commit()
        conn.close()
        
        return lesson_id
    
    def get_lessons(self, limit: int = 20) -> List[Dict]:
        """Get all learned lessons"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, action, context, outcome, insight, importance
            FROM experiences
            ORDER BY importance DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'action': row[1],
                'context': row[2],
                'outcome': row[3],
                'insight': row[4],
                'importance': row[5]
            })
        
        conn.close()
        return results
    
    # ==================== Relation Operations ====================
    
    def relate(
        self,
        from_entity: str,
        relation_type: str,
        to_entity: str,
        evidence: str = ""
    ) -> int:
        """
        Create a relation between entities.
        
        Args:
            from_entity: Source entity
            relation_type: Relation type
            to_entity: Target entity
            evidence: Evidence or source
            
        Returns:
            Relation ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ensure entities exist
        for entity in [from_entity, to_entity]:
            cursor.execute('''
                INSERT OR IGNORE INTO entities (name) VALUES (?)
            ''', (entity,))
        
        cursor.execute('''
            INSERT OR REPLACE INTO relations (from_entity, relation_type, to_entity, evidence)
            VALUES (?, ?, ?, ?)
        ''', (from_entity, relation_type, to_entity, evidence))
        
        relation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return relation_id
    
    def get_relations(self, entity: str) -> List[Dict]:
        """Get all relations for an entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT from_entity, relation_type, to_entity, weight, evidence
            FROM relations
            WHERE from_entity = ? OR to_entity = ?
        ''', (entity, entity))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'from_entity': row[0],
                'relation_type': row[1],
                'to_entity': row[2],
                'weight': row[3],
                'evidence': row[4]
            })
        
        conn.close()
        return results
    
    def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM facts WHERE id = ?', (fact_id,))
        cursor.execute('DELETE FROM memory_strength WHERE memory_type = ? AND memory_id = ?',
                       ('fact', fact_id))
        cursor.execute('DELETE FROM memory_context_bindings WHERE memory_type = ? AND memory_id = ?',
                       ('fact', fact_id))
        conn.commit()
        conn.close()
        return True
    
    def update_fact(self, fact_id: int, **kwargs) -> bool:
        """Update a fact"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query
        updates = []
        values = []
        for key, value in kwargs.items():
            if key == 'tags':
                updates.append(f'{key} = ?')
                values.append(json.dumps(value))
            else:
                updates.append(f'{key} = ?')
                values.append(value)
        
        if not updates:
            conn.close()
            return False
        
        values.append(fact_id)
        query = f"UPDATE facts SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        return True
    
    def associate(self, entity: str, depth: int = 2) -> Dict:
        """
        Get association network for an entity.
        
        Args:
            entity: Starting entity
            depth: Maximum depth to traverse
            
        Returns:
            Network with center and associations
        """
        associations = []
        visited = set()
        queue = [(entity, 0)]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        while queue:
            current, level = queue.pop(0)
            
            if current in visited or level > depth:
                continue
            
            visited.add(current)
            
            cursor.execute('''
                SELECT from_entity, relation_type, to_entity
                FROM relations
                WHERE from_entity = ? OR to_entity = ?
            ''', (current, current))
            
            for row in cursor.fetchall():
                from_e, rel, to_e = row
                
                # Determine direction
                if from_e == current:
                    other, direction = to_e, 'out'
                else:
                    other, direction = from_e, 'in'
                
                if other not in visited:
                    associations.append({
                        'from_entity': from_e,
                        'relation_type': rel,
                        'to_entity': to_e,
                        'level': level + 1,
                        'direction': direction
                    })
                    queue.append((other, level + 1))
        
        conn.close()
        
        return {
            'center': entity,
            'associations': associations
        }
    
    # ==================== Contextual Memory ====================
    
    def bind_context(self, memory_type: str, memory_id: int, context: Context) -> int:
        """Bind a memory to a context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create context
        cursor.execute('''
            INSERT INTO contexts (location, people, emotion, activity, channel)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            context.location,
            json.dumps(context.people),
            context.emotion,
            context.activity,
            context.channel
        ))
        
        context_id = cursor.lastrowid
        
        # Create binding
        cursor.execute('''
            INSERT INTO memory_context_bindings (memory_type, memory_id, context_id)
            VALUES (?, ?, ?)
        ''', (memory_type, memory_id, context_id))
        
        conn.commit()
        conn.close()
        
        return context_id
    
    def recall_by_context(
        self,
        location: str = None,
        people: List[str] = None,
        emotion: str = None,
        activity: str = None
    ) -> List[Dict]:
        """
        Recall memories by context.
        
        Args:
            location: Location filter
            people: People filter
            emotion: Emotion filter
            activity: Activity filter
            
        Returns:
            List of matching memories
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        conditions = []
        params = []
        
        if location:
            conditions.append("c.location = ?")
            params.append(location)
        
        if emotion:
            conditions.append("c.emotion = ?")
            params.append(emotion)
        
        if activity:
            conditions.append("c.activity = ?")
            params.append(activity)
        
        if people:
            # Check if any person in the list is in the context
            people_conditions = []
            for person in people:
                people_conditions.append("c.people LIKE ?")
                params.append(f'%{person}%')
            conditions.append(f"({' OR '.join(people_conditions)})")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f'''
            SELECT DISTINCT mcb.memory_type, mcb.memory_id, c.location, c.people, c.emotion
            FROM memory_context_bindings mcb
            JOIN contexts c ON mcb.context_id = c.id
            WHERE {where_clause}
        '''
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            memory_type, memory_id = row[0], row[1]
            
            # Get the actual memory
            if memory_type == 'fact':
                memory = self.get_fact(memory_id)
            else:
                memory = {'id': memory_id, 'type': memory_type}
            
            if memory:
                memory['match_reason'] = f"Context: {row[2]}, {row[3]}"
                results.append(memory)
        
        conn.close()
        return results
    
    # ==================== Working Memory ====================
    
    def hold(self, key: str, value: Any, priority: float = 0.5, ttl_seconds: int = None) -> bool:
        """
        Store in working memory.
        
        Args:
            key: Key
            value: Value (will be JSON serialized)
            priority: Priority (used for eviction)
            ttl_seconds: Time to live in seconds
            
        Returns:
            Success
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check capacity
        cursor.execute('SELECT COUNT(*) FROM working_memory')
        count = cursor.fetchone()[0]
        
        CAPACITY = 9  # 7±2 model
        
        if count >= CAPACITY:
            # Evict lowest priority
            cursor.execute('''
                SELECT key FROM working_memory
                ORDER BY priority ASC
                LIMIT 1
            ''')
            to_evict = cursor.fetchone()
            if to_evict:
                cursor.execute('DELETE FROM working_memory WHERE key = ?', (to_evict[0],))
        
        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now().timestamp() + ttl_seconds
        
        cursor.execute('''
            INSERT OR REPLACE INTO working_memory (key, value, priority, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (key, json.dumps(value), priority, expires_at))
        
        conn.commit()
        conn.close()
        return True
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from working memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value, expires_at FROM working_memory WHERE key = ?
        ''', (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            value, expires_at = row
            
            # Check expiration
            if expires_at and datetime.now().timestamp() > expires_at:
                self.forget(key)
                return None
            
            return json.loads(value)
        
        return None
    
    def forget(self, key: str) -> bool:
        """Remove from working memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM working_memory WHERE key = ?', (key,))
        conn.commit()
        conn.close()
        return True
    
    def clear_working_memory(self) -> int:
        """Clear all working memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM working_memory')
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
    
    # ==================== Forgetting Curve ====================
    
    def calculate_retention(self, days: float, strength: float) -> float:
        """
        Calculate memory retention using Ebbinghaus model.
        
        R = e^(-t/S)
        
        Args:
            days: Days since last access
            strength: Memory strength
            
        Returns:
            Retention ratio (0-1)
        """
        return math.exp(-days / max(strength, 0.1))
    
    def _record_access(self, memory_type: str, memory_id: int) -> float:
        """Record access to strengthen memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT base_strength, current_strength
            FROM memory_strength
            WHERE memory_type = ? AND memory_id = ?
        ''', (memory_type, memory_id))
        
        row = cursor.fetchone()
        
        if row:
            base_strength, current = row
            # Strengthen by 10%, capped at base_strength
            new_strength = min(current * 1.1, base_strength)
            
            cursor.execute('''
                UPDATE memory_strength
                SET current_strength = ?,
                    last_accessed = ?,
                    access_count = access_count + 1
                WHERE memory_type = ? AND memory_id = ?
            ''', (new_strength, datetime.now().isoformat(), memory_type, memory_id))
            
            conn.commit()
            conn.close()
            return new_strength
        
        conn.close()
        return 0.5
    
    # ==================== Statistics ====================
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM facts')
        facts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM experiences')
        experiences = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM relations')
        relations = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM entities')
        entities = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM working_memory')
        working = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'facts': facts,
            'experiences': experiences,
            'relations': relations,
            'entities': entities,
            'working_memory': working
        }
    
    # ==================== Export ====================
    
    def export_json(self) -> Dict:
        """Export all memory to JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {
            'export_time': datetime.now().isoformat(),
            'facts': [],
            'experiences': [],
            'relations': [],
            'entities': []
        }
        
        cursor.execute('SELECT * FROM facts')
        cols = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            data['facts'].append(dict(zip(cols, row)))
        
        cursor.execute('SELECT * FROM experiences')
        cols = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            data['experiences'].append(dict(zip(cols, row)))
        
        cursor.execute('SELECT * FROM relations')
        cols = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            data['relations'].append(dict(zip(cols, row)))
        
        cursor.execute('SELECT * FROM entities')
        cols = [d[0] for d in cursor.description]
        for row in cursor.fetchall():
            data['entities'].append(dict(zip(cols, row)))
        
        conn.close()
        return data