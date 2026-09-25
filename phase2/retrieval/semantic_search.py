"""
SIH 26108 — Dense Semantic Search Engine
Executes vector similarity search using cached SentenceTransformer embeddings.
"""

from typing import Dict, Any, Optional
from phase2.embeddings.embedding_store import EmbeddingStore

class SemanticSearchEngine:
    def __init__(self):
        self.store = EmbeddingStore()

    def search(self, query: str, top_k: int = 10, sector_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes semantic vector search over standard embeddings.
        
        Args:
            query (str): Input query text.
            top_k (int): Number of top candidates.
            sector_filter (str, optional): Sector filter.
            
        Returns:
            dict: Structured semantic search results.
        """
        if not query or not query.strip():
            return {
                "method": "semantic",
                "query": query,
                "results": []
            }

        vector_results = self.store.search_vector(query, top_k=top_k, sector_filter=sector_filter)
        
        return {
            "method": "semantic",
            "query": query,
            "results": vector_results
        }

if __name__ == '__main__':
    engine = SemanticSearchEngine()
    res = engine.search("HDPE pipes for rural drinking water supply lines", top_k=5)
    print("[OK] Semantic Search Results:")
    for r in res['results']:
        print(f"Rank {r['rank']}: {r['is_code']} | Similarity: {r['similarity']} | {r['title'][:60]}...")
