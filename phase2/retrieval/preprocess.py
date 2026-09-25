"""
SIH 26108 — Query Preprocessing Pipeline
Normalizes, tokenizes, and preserves technical domain terms in procurement queries.
"""

import re

# Stop words list (preserving technical and domain terms)
DEFAULT_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will',
    'with', 'the', 'this', 'but', 'or', 'so', 'if', 'about', 'than', 'into', 'over'
}

# Protected technical domain terms to prevent aggressive stemming/scrubbing
DOMAIN_TERMS = {
    'pvc', 'frls', 'fr', 'copper', 'cu', 'aluminum', 'al', 'xlpe', '1100v', '11kv', '33kv',
    '415v', 'mcb', 'rccb', 'elcb', 'mccb', 'led', 'ups', 'tmt', 'opc', 'ppc', 'rcc', 'hdpe',
    'upvc', 'fe500', 'fe500d', 'fe550', 'm20', 'm25', 'm30', 'm40', 'pn10', 'pn16', 'pe100'
}

def preprocess_query(query: str) -> dict:
    """
    Preprocesses a natural language procurement query.
    
    Args:
        query (str): Input query text.
        
    Returns:
        dict: Preprocessed query metadata including original query, normalized query string, and tokens.
    """
    if not query or not isinstance(query, str):
        return {
            "original_query": "" if query is None else str(query),
            "normalized_query": "",
            "tokens": []
        }

    original_query = query.strip()
    
    # 1. Lowercase conversion
    normalized = original_query.lower()
    
    # 2. Punctuation handling (keep hyphens and alphanumeric characters)
    normalized = re.sub(r'[^a-z0-9\s\-\.]', ' ', normalized)
    
    # 3. Whitespace normalization
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # 4. Tokenization & domain term preservation
    raw_tokens = normalized.split()
    tokens = []
    
    for token in raw_tokens:
        clean_token = token.strip('.-')
        if not clean_token:
            continue
        # Retain token if it is a domain term, or if it is not in generic stop words
        if clean_token in DOMAIN_TERMS or clean_token not in DEFAULT_STOP_WORDS:
            tokens.append(clean_token)
            
    return {
        "original_query": original_query,
        "normalized_query": normalized,
        "tokens": tokens
    }

if __name__ == '__main__':
    sample_query = "Supply of 1.5 sq mm PVC insulated copper electrical cables suitable for internal wiring of a government hospital."
    result = preprocess_query(sample_query)
    print("[OK] Preprocessed Query Result:")
    print(result)
