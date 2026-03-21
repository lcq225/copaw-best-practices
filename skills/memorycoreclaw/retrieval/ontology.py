"""
MemoryCoreClaw - Ontology Engine Module

Implements relation type definitions and inference.
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class RelationCategory(Enum):
    """Categories of relations"""
    WORK = "work"
    SOCIAL = "social"
    LOCATION = "location"
    KNOWLEDGE = "knowledge"
    USAGE = "usage"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    PREFERENCE = "preference"
    OTHER = "other"


@dataclass
class RelationType:
    """A relation type definition"""
    name: str
    category: RelationCategory
    inverse: Optional[str]
    description: str
    examples: List[str]


class OntologyEngine:
    """
    Ontology Engine for Relation Management
    
    Manages relation types and provides inference capabilities.
    
    Usage:
        ont = OntologyEngine()
        rel_type, confidence = ont.infer_relation("Alice", "TechCorp")
        print(f"Inferred: {rel_type} (confidence: {confidence})")
    """
    
    # Standard relation types
    STANDARD_RELATIONS: Dict[str, RelationType] = {
        # Work relations
        'works_at': RelationType('works_at', RelationCategory.WORK, 'employs', 
                                 'Entity works at organization', 
                                 ['Alice works at TechCorp']),
        'works_in': RelationType('works_in', RelationCategory.WORK, None,
                                 'Entity works in department/location',
                                 ['Bob works in Engineering']),
        'manages': RelationType('manages', RelationCategory.WORK, 'managed_by',
                               'Entity manages another entity',
                               ['Alice manages Bob']),
        'collaborates_with': RelationType('collaborates_with', RelationCategory.WORK, 
                                          'collaborates_with',
                                          'Entities collaborate together',
                                          ['Alice collaborates with Bob']),
        'reports_to': RelationType('reports_to', RelationCategory.WORK, 'manages',
                                   'Entity reports to another',
                                   ['Bob reports to Alice']),
        
        # Social relations
        'knows': RelationType('knows', RelationCategory.SOCIAL, 'knows',
                             'Entity knows another entity',
                             ['Alice knows Bob']),
        'friend_of': RelationType('friend_of', RelationCategory.SOCIAL, 'friend_of',
                                  'Entities are friends',
                                  ['Alice is friend of Bob']),
        'family_of': RelationType('family_of', RelationCategory.SOCIAL, 'family_of',
                                  'Entities are family',
                                  ['Alice is family of Bob']),
        
        # Location relations
        'located_in': RelationType('located_in', RelationCategory.LOCATION, 'contains',
                                   'Entity located in place',
                                   ['Office located in Building A']),
        'part_of': RelationType('part_of', RelationCategory.LOCATION, 'has_part',
                               'Entity is part of another',
                               ['Engine is part of Car']),
        
        # Knowledge relations
        'knows_about': RelationType('knows_about', RelationCategory.KNOWLEDGE, None,
                                    'Entity has knowledge about topic',
                                    ['Alice knows about Python']),
        'learned': RelationType('learned', RelationCategory.KNOWLEDGE, None,
                               'Entity learned something',
                               ['Alice learned Python']),
        
        # Usage relations
        'uses': RelationType('uses', RelationCategory.USAGE, 'used_by',
                            'Entity uses another entity',
                            ['Project uses Python']),
        'depends_on': RelationType('depends_on', RelationCategory.USAGE, 'required_by',
                                   'Entity depends on another',
                                   ['App depends on Database']),
        
        # Preference relations
        'prefers': RelationType('prefers', RelationCategory.PREFERENCE, None,
                               'Entity prefers something',
                               ['Alice prefers Python']),
        'likes': RelationType('likes', RelationCategory.PREFERENCE, None,
                             'Entity likes something',
                             ['Alice likes Coffee']),
        'dislikes': RelationType('dislikes', RelationCategory.PREFERENCE, None,
                                 'Entity dislikes something',
                                 ['Alice dislikes Bugs']),
        
        # Temporal relations
        'before': RelationType('before', RelationCategory.TEMPORAL, 'after',
                              'Event happens before another',
                              ['Meeting before Lunch']),
        'after': RelationType('after', RelationCategory.TEMPORAL, 'before',
                             'Event happens after another',
                             ['Lunch after Meeting']),
        
        # Causal relations
        'causes': RelationType('causes', RelationCategory.CAUSAL, 'caused_by',
                              'Entity causes another',
                              ['Rain causes Flood']),
        'prevents': RelationType('prevents', RelationCategory.CAUSAL, None,
                                 'Entity prevents another',
                                 ['Umbrella prevents Getting wet']),
        
        # General relations
        'related_to': RelationType('related_to', RelationCategory.OTHER, 'related_to',
                                   'Entities are related',
                                   ['A related to B']),
        'similar_to': RelationType('similar_to', RelationCategory.OTHER, 'similar_to',
                                   'Entities are similar',
                                   ['Python similar to Ruby']),
    }
    
    def __init__(self):
        """Initialize ontology engine"""
        self.relations = self.STANDARD_RELATIONS.copy()
        self.custom_relations: Dict[str, RelationType] = {}
        self.relation_patterns: Dict[str, List[str]] = {}
    
    def get_relation(self, name: str) -> Optional[RelationType]:
        """Get a relation type by name"""
        return self.relations.get(name) or self.custom_relations.get(name)
    
    def add_relation(self, relation: RelationType) -> bool:
        """Add a custom relation type"""
        if relation.name in self.relations:
            return False
        self.custom_relations[relation.name] = relation
        return True
    
    def get_inverse(self, relation: str) -> Optional[str]:
        """Get inverse relation type"""
        rel = self.get_relation(relation)
        return rel.inverse if rel else None
    
    def get_relations_by_category(self, category: RelationCategory) -> List[RelationType]:
        """Get all relations in a category"""
        return [r for r in self.relations.values() if r.category == category]
    
    def infer_relation(self, from_entity: str, to_entity: str) -> Tuple[str, float]:
        """
        Infer the most likely relation between two entities.
        
        Args:
            from_entity: Source entity
            to_entity: Target entity
            
        Returns:
            (relation_type, confidence) tuple
        """
        # Simple heuristics based on entity patterns
        from_lower = from_entity.lower()
        to_lower = to_entity.lower()
        
        # Organization patterns
        org_patterns = ['inc', 'corp', 'company', 'ltd', 'gmbh', 'llc']
        if any(p in to_lower for p in org_patterns):
            return ('works_at', 0.7)
        
        # Location patterns
        location_patterns = ['city', 'country', 'office', 'building', 'room']
        if any(p in to_lower for p in location_patterns):
            return ('located_in', 0.6)
        
        # Technology patterns
        tech_patterns = ['python', 'java', 'react', 'docker', 'kubernetes']
        if any(p in to_lower for p in tech_patterns):
            return ('uses', 0.7)
        
        # Person patterns (capitalized names)
        if from_entity[0].isupper() and to_entity[0].isupper():
            if len(to_entity.split()) <= 2:  # Likely a person name
                return ('knows', 0.5)
        
        # Default
        return ('related_to', 0.3)
    
    def validate_relation(self, relation: str) -> bool:
        """Check if a relation type is valid"""
        return relation in self.relations or relation in self.custom_relations
    
    def suggest_relations(self, entity_type: str) -> List[str]:
        """Suggest relevant relations for an entity type"""
        suggestions = {
            'person': ['works_at', 'knows', 'friend_of', 'prefers', 'uses'],
            'organization': ['employs', 'located_in', 'uses'],
            'technology': ['used_by', 'depends_on', 'similar_to'],
            'location': ['located_in', 'part_of', 'contains'],
        }
        return suggestions.get(entity_type.lower(), ['related_to'])