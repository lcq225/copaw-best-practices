"""
MemoryCoreClaw - Heuristic Engine Module

Implements cognitive schema recognition and thought patterns.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import re


@dataclass
class Schema:
    """A cognitive schema pattern"""
    name: str
    description: str
    patterns: List[str]
    triggers: List[str]


class HeuristicEngine:
    """
    Cognitive Heuristic Engine
    
    Recognizes thought patterns and cognitive schemas.
    
    Usage:
        he = HeuristicEngine()
        schemas = he.recognize("Why did this happen? How can I fix it?")
        for s in schemas:
            print(f"Detected: {s.name}")
    """
    
    # Predefined cognitive schemas
    DEFAULT_SCHEMAS = [
        Schema(
            name="problem_solving",
            description="Identifying problem and seeking solution",
            patterns=[
                r"why\s+did",
                r"how\s+can\s+i\s+fix",
                r"what\s+caused",
                r"how\s+to\s+solve"
            ],
            triggers=["why", "how", "fix", "solve", "problem"]
        ),
        Schema(
            name="planning",
            description="Planning future actions",
            patterns=[
                r"i\s+will",
                r"we\s+plan\s+to",
                r"scheduled\s+for",
                r"next\s+step"
            ],
            triggers=["plan", "will", "schedule", "next", "tomorrow"]
        ),
        Schema(
            name="learning",
            description="Learning from experience",
            patterns=[
                r"i\s+learned",
                r"the\s+lesson\s+is",
                r"i\s+realized",
                r"now\s+i\s+know"
            ],
            triggers=["learned", "lesson", "realized", "know", "understand"]
        ),
        Schema(
            name="inquiry",
            description="Asking questions to understand",
            patterns=[
                r"who\s+is",
                r"what\s+is",
                r"where\s+is",
                r"when\s+did",
                r"\?$"
            ],
            triggers=["who", "what", "where", "when", "?"]
        ),
        Schema(
            name="reflection",
            description="Reflecting on past events",
            patterns=[
                r"i\s+remember",
                r"looking\s+back",
                r"in\s+the\s+past",
                r"previously"
            ],
            triggers=["remember", "past", "before", "previously"]
        ),
        Schema(
            name="decision",
            description="Making a decision",
            patterns=[
                r"i\s+decided",
                r"i\s+chose",
                r"the\s+best\s+option",
                r"i\s+prefer"
            ],
            triggers=["decided", "chose", "option", "prefer", "better"]
        ),
        Schema(
            name="emotion_expression",
            description="Expressing emotions",
            patterns=[
                r"i\s+feel",
                r"i\s+am\s+(happy|sad|angry|worried|excited)",
                r"makes\s+me\s+feel"
            ],
            triggers=["feel", "happy", "sad", "angry", "worried", "excited"]
        )
    ]
    
    def __init__(self, custom_schemas: List[Schema] = None):
        """
        Initialize heuristic engine.
        
        Args:
            custom_schemas: Additional schemas to include
        """
        self.schemas = self.DEFAULT_SCHEMAS.copy()
        if custom_schemas:
            self.schemas.extend(custom_schemas)
    
    def recognize(self, text: str) -> List[Schema]:
        """
        Recognize cognitive schemas in text.
        
        Args:
            text: Input text
            
        Returns:
            List of matched schemas (sorted by relevance)
        """
        text_lower = text.lower()
        matches = []
        
        for schema in self.schemas:
            score = 0
            
            # Check patterns
            for pattern in schema.patterns:
                if re.search(pattern, text_lower):
                    score += 2
            
            # Check triggers
            for trigger in schema.triggers:
                if trigger in text_lower:
                    score += 1
            
            if score > 0:
                matches.append((schema, score))
        
        # Sort by score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [m[0] for m in matches]
    
    def get_schema(self, name: str) -> Optional[Schema]:
        """Get a schema by name"""
        for schema in self.schemas:
            if schema.name == name:
                return schema
        return None
    
    def add_schema(self, schema: Schema) -> bool:
        """Add a custom schema"""
        if self.get_schema(schema.name):
            return False
        self.schemas.append(schema)
        return True
    
    def suggest_followup(self, schema_name: str) -> List[str]:
        """
        Suggest follow-up questions/actions for a schema.
        
        Args:
            schema_name: Name of detected schema
            
        Returns:
            List of suggestions
        """
        suggestions = {
            "problem_solving": [
                "What is the root cause?",
                "What solutions have been tried?",
                "What resources are available?"
            ],
            "planning": [
                "What is the timeline?",
                "Who is responsible?",
                "What could go wrong?"
            ],
            "learning": [
                "How can this be applied elsewhere?",
                "What would you do differently?",
                "Who else should know this?"
            ],
            "inquiry": [
                "What do you already know?",
                "Where can you find more information?",
                "Who might have the answer?"
            ],
            "reflection": [
                "What changed since then?",
                "What did you learn?",
                "How does this affect the future?"
            ],
            "decision": [
                "What alternatives were considered?",
                "What are the trade-offs?",
                "When will you reevaluate?"
            ]
        }
        
        return suggestions.get(schema_name, [])