"""
SIH 26108 — Phase 5 Vector Retrieval Module
Provides semantic vector search over Indian Standards, clause descriptions, product scopes, and QCO texts.
"""

from typing import Dict, Any, List, Optional
from phase2.retrieval.semantic_search import SemanticSearchEngine

class Phase5VectorRetriever:
    def __init__(self):
        self.engine = SemanticSearchEngine()

    def retrieve_candidates(self, query: str, top_k: int = 10, sector: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves top-K candidate standards using dense vector embeddings.
        """
        res = self.engine.search(query, top_k=top_k, sector_filter=sector)
        return res.get("results", [])


if __name__ == '__main__':
    retriever = Phase5VectorRetriever()
    results = retriever.retrieve_candidates("PVC insulated copper wire for control panels", top_k=5)
    print(f"[OK] Vector Retriever found {len(results)} candidate standards.")
    for r in results:
        print(f"  - {r['is_code']} (Similarity: {r['similarity']:.4f}): {r['title']}")
