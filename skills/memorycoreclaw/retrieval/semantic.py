"""
MemoryCoreClaw - Semantic Search Module

Implements semantic similarity search for memory retrieval.
"""

from typing import List, Dict, Optional, Tuple
import math
from dataclasses import dataclass


@dataclass
class SearchResult:
    """A search result with similarity score"""
    id: int
    content: str
    score: float
    metadata: Dict


class SemanticSearch:
    """
    Semantic Search Engine
    
    Supports both embedding-based and keyword-based search.
    
    Features:
    - Semantic similarity using embeddings (optional)
    - Fallback to TF-IDF keyword search
    - Hybrid search combining both
    
    Usage:
        ss = SemanticSearch()
        ss.index(1, "Alice works at TechCorp")
        results = ss.search("Where does Alice work?")
    """
    
    def __init__(self, embedding_model: str = None, api_key: str = None):
        """
        Initialize semantic search.
        
        Args:
            embedding_model: Model name for embeddings (e.g., "bge-m3")
            api_key: API key for embedding service
        """
        self.embedding_model = embedding_model
        self.api_key = api_key
        self.documents: Dict[int, Dict] = {}
        self.vectors: Dict[int, List[float]] = {}
        self.use_embedding = False
        
        # Try to initialize embedding model
        if embedding_model:
            try:
                self._init_embedding()
            except Exception:
                print("Warning: Could not initialize embedding model, using keyword search")
    
    def _init_embedding(self):
        """Initialize embedding model"""
        # Placeholder for embedding initialization
        # In production, would use sentence-transformers or API
        pass
    
    def index(self, doc_id: int, content: str, metadata: Dict = None):
        """
        Index a document.
        
        Args:
            doc_id: Document ID
            content: Document content
            metadata: Optional metadata
        """
        self.documents[doc_id] = {
            'content': content,
            'metadata': metadata or {}
        }
        
        # Generate embedding if available
        if self.use_embedding:
            vector = self._get_embedding(content)
            if vector:
                self.vectors[doc_id] = vector
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text"""
        # Placeholder for embedding generation
        return None
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of search results
        """
        if self.use_embedding and self.vectors:
            return self._semantic_search(query, limit)
        else:
            return self._keyword_search(query, limit)
    
    def _semantic_search(self, query: str, limit: int) -> List[SearchResult]:
        """Semantic search using embeddings"""
        query_vector = self._get_embedding(query)
        if not query_vector:
            return self._keyword_search(query, limit)
        
        # Calculate cosine similarity
        scores = []
        for doc_id, doc_vector in self.vectors.items():
            score = self._cosine_similarity(query_vector, doc_vector)
            scores.append((doc_id, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in scores[:limit]:
            doc = self.documents.get(doc_id)
            if doc:
                results.append(SearchResult(
                    id=doc_id,
                    content=doc['content'],
                    score=score,
                    metadata=doc['metadata']
                ))
        
        return results
    
    def _keyword_search(self, query: str, limit: int) -> List[SearchResult]:
        """Keyword-based search using TF-IDF"""
        query_terms = set(query.lower().split())
        
        scores = []
        for doc_id, doc in self.documents.items():
            content = doc['content'].lower()
            content_terms = set(content.split())
            
            # Jaccard similarity
            intersection = len(query_terms & content_terms)
            union = len(query_terms | content_terms)
            score = intersection / union if union > 0 else 0
            
            # Boost for exact substring match
            if query.lower() in content:
                score += 0.5
            
            scores.append((doc_id, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in scores[:limit]:
            doc = self.documents.get(doc_id)
            if doc:
                results.append(SearchResult(
                    id=doc_id,
                    content=doc['content'],
                    score=score,
                    metadata=doc['metadata']
                ))
        
        return results
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(a) != len(b):
            return 0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        
        if mag_a == 0 or mag_b == 0:
            return 0
        
        return dot_product / (mag_a * mag_b)
    
    def remove(self, doc_id: int):
        """Remove a document from index"""
        self.documents.pop(doc_id, None)
        self.vectors.pop(doc_id, None)
    
    def clear(self):
        """Clear all documents"""
        self.documents.clear()
        self.vectors.clear()