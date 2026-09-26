"""
SIH 26108 — Generate Dense Embeddings Script
Computes dense vector representations for all verified Indian Standards search documents.
Model: SentenceTransformers ('all-MiniLM-L6-v2') or TF-IDF + TruncatedSVD dense fallback.
"""

import os
import json
import numpy as np
from phase2.retrieval.dataset_loader import load_standards_dataset

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_INDEX_DIR = os.path.join(BASE_DIR, 'indexes', 'vector')
VECTORS_FILE = os.path.join(VECTOR_INDEX_DIR, 'standard_vectors.npy')
METADATA_FILE = os.path.join(VECTOR_INDEX_DIR, 'metadata.json')

MODEL_NAME = 'all-MiniLM-L6-v2'

def get_embedder():
    """
    Attempts to load SentenceTransformer model, falls back to scikit-learn TF-IDF + SVD.
    """
    try:
        from sentence_transformers import SentenceTransformer
        print(f"[*] Loading SentenceTransformer model '{MODEL_NAME}'...")
        try:
            model = SentenceTransformer(MODEL_NAME, local_files_only=True)
        except Exception:
            model = SentenceTransformer(MODEL_NAME)
        
        def embed_fn(texts: list[str]) -> np.ndarray:
            embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
            return np.array(embeddings, dtype=np.float32)
            
        return embed_fn, "sentence_transformers/all-MiniLM-L6-v2"
    except Exception as e:
        print(f"[!] SentenceTransformer load notice ({e}). Using scikit-learn TF-IDF + SVD Dense Fallback...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        
        def fallback_embed_fn(texts: list[str]) -> np.ndarray:
            vec = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
            tfidf = vec.fit_transform(texts)
            n_comp = min(128, tfidf.shape[1] - 1) if tfidf.shape[1] > 1 else 1
            svd = TruncatedSVD(n_components=n_comp, random_state=42)
            dense = svd.fit_transform(tfidf)
            # Normalize L2
            norms = np.linalg.norm(dense, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            return (dense / norms).astype(np.float32)
            
        return fallback_embed_fn, "scikit-learn/TFIDF-SVD-Dense"


def generate_embeddings(force_rebuild: bool = False):
    os.makedirs(VECTOR_INDEX_DIR, exist_ok=True)
    
    if not force_rebuild and os.path.exists(VECTORS_FILE) and os.path.exists(METADATA_FILE):
        print(f"[OK] Vector index already exists at {VECTORS_FILE}. Skipping generation.")
        return VECTORS_FILE, METADATA_FILE

    standards = load_standards_dataset()
    if not standards:
        raise ValueError("No verified standards found to generate embeddings.")

    search_docs = [std['search_doc'] for std in standards]
    metadata = []
    
    for idx, std in enumerate(standards):
        metadata.append({
            "doc_id": idx,
            "is_code": std['is_code'],
            "title": std['title'],
            "sector": std.get('sector', ''),
            "product_category": std.get('product_category', '')
        })

    embed_fn, model_info = get_embedder()
    print(f"[*] Computing embeddings for {len(search_docs)} standards using {model_info}...")
    vectors = embed_fn(search_docs)

    np.save(VECTORS_FILE, vectors)
    
    meta_payload = {
        "model_name": model_info,
        "vector_dim": vectors.shape[1],
        "num_records": len(metadata),
        "standards": metadata
    }
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(meta_payload, f, indent=2)

    print(f"[OK] Saved {vectors.shape[0]} dense vector embeddings (dim={vectors.shape[1]}) -> {VECTORS_FILE}")
    return VECTORS_FILE, METADATA_FILE


if __name__ == '__main__':
    generate_embeddings(force_rebuild=True)
