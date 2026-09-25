"""
SIH 26108 — BM25 Lexical Search Engine
Implements Okapi BM25 sparse keyword retrieval over Indian Standards search documents.
"""

import os
import math
from typing import List, Dict, Any, Optional
from phase2.retrieval.dataset_loader import load_standards_dataset
from phase2.retrieval.preprocess import preprocess_query

# Try importing rank_bm25, fallback to pure Python Okapi BM25 implementation if unavailable
try:
    from rank_bm25 import BM25Okapi
    HAS_RANK_BM25 = True
except ImportError:
    HAS_RANK_BM25 = False


class PureBM25Okapi:
    """Pure Python implementation of Okapi BM25 algorithm."""
    def __init__(self, corpus_tokens: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus_tokens)
        self.doc_lengths = [len(doc) for doc in corpus_tokens]
        self.avg_doc_len = sum(self.doc_lengths) / self.corpus_size if self.corpus_size > 0 else 1.0
        self.doc_freqs = []
        self.idf = {}
        
        # Calculate Term Frequencies & Document Frequencies
        df_count = {}
        for doc in corpus_tokens:
            frequencies = {}
            for token in doc:
                frequencies[token] = frequencies.get(token, 0) + 1
            self.doc_freqs.append(frequencies)
            for token in frequencies.keys():
                df_count[token] = df_count.get(token, 0) + 1
                
        # Calculate IDF values
        for token, freq in df_count.items():
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)

    def get_scores(self, query_tokens: List[str]) -> List[float]:
        scores = [0.0] * self.corpus_size
        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for idx, doc_freq in enumerate(self.doc_freqs):
                if token in doc_freq:
                    tf = doc_freq[token]
                    doc_len = self.doc_lengths[idx]
                    num = tf * (self.k1 + 1)
                    den = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    scores[idx] += idf_val * (num / den)
        return scores


class BM25SearchEngine:
    def __init__(self, standards_dataset: Optional[List[Dict[str, Any]]] = None):
        if standards_dataset is None:
            standards_dataset = load_standards_dataset()
            
        self.standards = standards_dataset
        self.corpus_tokens = []
        
        for std in self.standards:
            doc_text = std.get('search_doc', '')
            tokens = preprocess_query(doc_text)['tokens']
            self.corpus_tokens.append(tokens)
            
        if HAS_RANK_BM25:
            self.bm25 = BM25Okapi(self.corpus_tokens)
        else:
            self.bm25 = PureBM25Okapi(self.corpus_tokens)

    def search(self, query: str, top_k: int = 10, sector_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes BM25 keyword search.
        
        Args:
            query (str): Natural language procurement query.
            top_k (int): Number of top candidate results to retrieve.
            sector_filter (str, optional): Sector filter ('Electrical' or 'Civil').
            
        Returns:
            dict: Structured BM25 search results.
        """
        if not query or not query.strip():
            return {
                "method": "bm25",
                "query": query,
                "results": []
            }
            
        prep = preprocess_query(query)
        query_tokens = prep['tokens']
        
        if not query_tokens:
            return {
                "method": "bm25",
                "query": query,
                "results": []
            }
            
        scores = self.bm25.get_scores(query_tokens)
        
        # Rank document indices by score descending
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        
        results = []
        rank = 1
        for idx in ranked_indices:
            std = self.standards[idx]
            
            # Apply sector filter if specified
            if sector_filter and std.get('sector') != sector_filter:
                continue
                
            raw_score = float(scores[idx])
            
            # Compute matched tokens for explainability
            doc_tokens_set = set(self.corpus_tokens[idx])
            matched_terms = [t for t in query_tokens if t in doc_tokens_set]
            
            results.append({
                "rank": rank,
                "is_code": std['is_code'],
                "title": std['title'],
                "sector": std.get('sector', ''),
                "product_category": std.get('product_category', ''),
                "raw_score": round(raw_score, 4),
                "matched_terms": matched_terms
            })
            
            rank += 1
            if len(results) >= top_k:
                break
                
        return {
            "method": "bm25",
            "query": query,
            "results": results
        }


if __name__ == '__main__':
    engine = BM25SearchEngine()
    test_query = "Supply of PVC insulated copper electrical cables suitable for internal wiring of a government hospital."
    res = engine.search(test_query, top_k=5)
    print("[OK] BM25 Search Results:")
    for r in res['results']:
        print(f"Rank {r['rank']}: {r['is_code']} | Score: {r['raw_score']} | Title: {r['title'][:60]}... | Matched: {r['matched_terms']}")
