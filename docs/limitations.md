# System Limitations & Future Research Roadmap — SIH 26108

## 1. Current System Limitations

1. **Pilot Knowledge Base Size:** Current verified dataset contains 120 curated standards across Electrical and Civil sectors. Full production deployment requires scaling to 20,000+ active BIS standards.
2. **Local CPU Embedding Latency:** Dense vector embedding generation on CPU adds ~12-18ms per request queue under heavy concurrency. GPU acceleration or pre-indexed FAISS search is recommended for enterprise scale.
3. **QCO Gazette Verification Scope:** Quality Control Orders are strictly verified against gazette records present in the database. Unverified orders are intentionally not hallucinated.
4. **Complex Compound Procurement Parsing:** Procurement descriptions containing multiple unrelated equipment items simultaneously (e.g. "Cables, Transformers, and Office Furniture") require multi-item splitting pre-processors.

---

## 2. Future System Roadmap

1. **Automated BIS Portal Scraper:** Development of automated scrapers for real-time synchronization with the Bureau of Indian Standards (BIS) portal for newly published standards and amendments.
2. **GeM Portal Integration:** Direct API connector for Government e-Marketplace (GeM) tender description auto-filling and compliance validation.
3. **Multilingual NLP Support:** NLP entity extraction support for regional Indian languages (Hindi, Tamil, Marathi, Bengali) in procurement descriptions.
