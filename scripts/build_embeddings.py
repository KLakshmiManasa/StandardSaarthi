"""
SIH 26108 — Phase 8 Vector Embedding Builder
Rebuilds SentenceTransformer dense vector index for standards dataset.
"""

import os
from phase2.retrieval.semantic_search import SemanticSearchEngine

def build_vector_index():
    print("[*] Rebuilding vector index for current standards dataset...")
    engine = SemanticSearchEngine()
    print(f"[OK] Vector index successfully built with {len(engine.standards)} standards.")

if __name__ == '__main__':
    build_vector_index()
