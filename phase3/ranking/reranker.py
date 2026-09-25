"""
SIH 26108 — Cross-Encoder Reranker Engine
Reranks top candidate standards using a pretrained Cross-Encoder model ('cross-encoder/ms-marco-MiniLM-L-6-v2').
"""

import math
from typing import List, Dict, Any, Optional
from phase2.retrieval.dataset_loader import load_standards_dataset

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class CrossEncoderReranker:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.standards_map = {s['is_code']: s for s in load_standards_dataset()}
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import CrossEncoder
            print(f"[*] Loading CrossEncoder model '{self.model_name}'...")
            self.model = CrossEncoder(self.model_name)
        except Exception as e:
            print(f"[!] CrossEncoder load notice ({e}). Cross-encoder will fallback to lexical-semantic similarity estimation.")
            self.model = None

    def rerank(self, query: str, candidate_list: List[Dict[str, Any]], rerank_top_n: int = 30) -> List[Dict[str, Any]]:
        """
        Reranks top N candidate standards using Cross-Encoder model.
        
        Args:
            query (str): Input procurement query.
            candidate_list (list): Candidates from RRF / candidate generator.
            rerank_top_n (int): Number of top candidates to pass to cross-encoder.
            
        Returns:
            list: Reranked candidates with cross-encoder relevance scores.
        """
        if not candidate_list or not query or not query.strip():
            return candidate_list

        top_candidates = candidate_list[:rerank_top_n]
        remaining_candidates = candidate_list[rerank_top_n:]

        pairs = []
        for cand in top_candidates:
            code = cand['is_code']
            std = self.standards_map.get(code, {})
            title = std.get('title', '')
            scope = std.get('scope_text', '')[:300]
            
            doc_str = f"IS CODE: {code} | TITLE: {title} | SCOPE: {scope}"
            pairs.append((query, doc_str))

        if self.model is not None and pairs:
            try:
                raw_scores = self.model.predict(pairs, show_progress_bar=False)
                
                # Apply Sigmoid activation to map logits to [0.0, 1.0] relevance range
                for idx, cand in enumerate(top_candidates):
                    logit = float(raw_scores[idx])
                    sigmoid_score = 1.0 / (1.0 + math.exp(-logit))
                    cand['reranker_score'] = round(sigmoid_score, 4)
            except Exception as ex:
                print(f"[!] CrossEncoder prediction fallback: {ex}")
                for cand in top_candidates:
                    cand['reranker_score'] = round(cand.get('rrf_score', 0.5), 4)
        else:
            # Fallback score if model is not available
            for cand in top_candidates:
                cand['reranker_score'] = round(cand.get('rrf_score', 0.5), 4)

        # Sort top candidates by reranker_score descending
        top_candidates.sort(key=lambda x: x.get('reranker_score', 0.0), reverse=True)
        
        # Combine reranked top candidates with remaining pool
        final_list = top_candidates + remaining_candidates
        for idx, item in enumerate(final_list):
            item['rerank_position'] = idx + 1

        return final_list


if __name__ == '__main__':
    from phase3.ranking.rrf import RRFEngine
    rrf_engine = RRFEngine()
    test_query = "Supply of PVC insulated copper electrical cables for hospital internal wiring"
    candidates = rrf_engine.search(test_query, top_k=20)['results']
    
    reranker = CrossEncoderReranker()
    reranked = reranker.rerank(test_query, candidates, rerank_top_n=10)
    
    print("[OK] Reranker Test Results:")
    for r in reranked[:5]:
        print(f"Rerank Position {r['rerank_position']}: {r['is_code']} | Reranker Score: {r.get('reranker_score')} | Title: {r['title'][:50]}...")
