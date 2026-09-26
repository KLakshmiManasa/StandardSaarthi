"""
SIH 26108 — Embedding Store & Vector Index
Manages cached vector embeddings, handles similarity queries using NumPy / FAISS.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from phase2.embeddings.generate_embeddings import generate_embeddings, VECTORS_FILE, METADATA_FILE, get_embedder

class EmbeddingStore:
    def __init__(self):
        if not os.path.exists(VECTORS_FILE) or not os.path.exists(METADATA_FILE):
            generate_embeddings(force_rebuild=False)
            
        self.vectors = np.load(VECTORS_FILE)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
            
        self.embed_fn, self.model_name = get_embedder()
        self.standards_meta = self.metadata['standards']

    def search_vector(self, query_text: str, top_k: int = 10, sector_filter: str = None) -> List[Dict[str, Any]]:
        """
        Computes query vector embedding and calculates cosine similarity against standard vectors.
        
        Returns ranked list of candidate records with similarity scores.
        """
        if not query_text or not query_text.strip():
            return []
            
        query_vec = self.embed_fn([query_text])[0]
        
        # Ensure dimension alignment with precomputed vector store
        target_dim = self.vectors.shape[1]
        if query_vec.shape[0] != target_dim:
            if query_vec.shape[0] < target_dim:
                padded = np.zeros(target_dim, dtype=np.float32)
                padded[:query_vec.shape[0]] = query_vec
                query_vec = padded
            else:
                query_vec = query_vec[:target_dim]
            norm = np.linalg.norm(query_vec)
            if norm > 0:
                query_vec = query_vec / norm

        # Calculate cosine similarity (vectors are L2-normalized)
        sim_scores = np.dot(self.vectors, query_vec)
        
        ranked_indices = np.argsort(sim_scores)[::-1]
        
        # Normalize sector filter: ignore if General, Unknown, empty, or None
        if sector_filter and str(sector_filter).lower() in ["general", "unknown", "none", ""]:
            sector_filter = None

        results = []
        rank = 1
        for idx in ranked_indices:
            meta = self.standards_meta[idx]
            if sector_filter and meta.get('sector') != sector_filter:
                continue
                
            sim_val = float(sim_scores[idx])
            results.append({
                "rank": rank,
                "is_code": meta['is_code'],
                "title": meta['title'],
                "sector": meta.get('sector', ''),
                "product_category": meta.get('product_category', ''),
                "similarity": round(sim_val, 4)
            })
            rank += 1
            if len(results) >= top_k:
                break
                
        return results

if __name__ == '__main__':
    store = EmbeddingStore()
    res = store.search_vector("Supply of PVC insulated copper electrical cables for hospital internal wiring", top_k=5)
    print("[OK] Vector Search Test Results:")
    for r in res:
        print(f"Rank {r['rank']}: {r['is_code']} | Similarity: {r['similarity']} | {r['title'][:60]}...")
