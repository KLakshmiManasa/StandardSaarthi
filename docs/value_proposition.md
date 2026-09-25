# "Why Not Just Google?" — Value Proposition (SIH 26108)

## 1. Executive Summary

Traditional web search engines and basic vector search engines cannot effectively handle public procurement standards mapping due to fragmented terminology, missing regulatory context, and lack of verifiable provenance.

The **AI-Powered Indian Standards Recommendation Engine** addresses this challenge by combining dense vector retrieval with a structured Knowledge Graph, Quality Control Order (QCO) gazette matching, and evidence grounding.

---

## 2. Capability Comparison Matrix

| Search Dimension | Traditional Keyword Search (e.g. Google / BM25) | Basic Vector Search (Dense RAG) | Proposed Graph-RAG + QCO Engine (SIH 26108) |
|---|---|---|---|
| **Query Understanding** | Matches raw text tokens | Matches semantic embedding similarity | Extracts product, category, material, application, and technical attributes |
| **Handling Trade Jargon vs Official Title** | Fails if keywords differ ("PVC wire" vs "Polyvinyl chloride cable") | Partial match based on embedding proximity | Resolves synonyms using domain NLP entity dictionary |
| **Relationship Traversal** | Cannot link related testing or material standards | Returns isolated document chunks | Traverses 1-hop and 2-hop normative references (`IS 694 -> IS 8130`) |
| **Mandatory QCO Regulatory Compliance** | No regulatory awareness | No gazette integration | Flags statutory Quality Control Orders from official Gazette notifications |
| **Ambiguity Handling** | Returns irrelevant web links | Guesses top vector neighbor | Triggers `NEEDS_CLARIFICATION` requesting missing technical parameters |
| **Hallucination Prevention** | High risk of arbitrary SEO pages | Risk of embedding hallucination | Grounded in verified database, explicit citations, and source URLs |
| **Explainability** | Shows snippet matches | Shows abstract cosine similarity percentage | Provides structured breakdown ("Product match", "Material match", "QCO mandatory") |

---

## 3. Core Technical Differentiators

1. **Structured Entity Grounding:** Combines dense semantic search with explicit rule-based entity matching across materials, applications, and voltage/rating parameters.
2. **Statutory Regulatory Integration:** Directly links candidate standards to Quality Control Orders (QCOs), helping procurement officers comply with mandatory certification directives.
3. **Graph-RAG Multi-Hop Context:** Exposes linked testing standards, raw material specifications, and replacement history via Knowledge Graph traversals.
4. **Verifiable Evidence Provenance:** Every recommendation includes an explicit primary source citation and official BIS catalog URL.
