# Implemented Features vs Future Scope Roadmap (SIH 26108)

This document clearly demarcates currently implemented features from future roadmap items to ensure full transparency for SIH judges.

---

## 1. Feature Comparison Matrix

| Capability Category | Currently Implemented (Phases 0–10) | Future Research Roadmap |
|---|---|---|
| **Standards Knowledge Base** | 120 verified curated standards across Electrical and Civil sectors | Full scaling to complete 20,000+ active Bureau of Indian Standards (BIS) corpus |
| **Data Synchronization** | Off-line verified BIS catalog and gazette dataset ingest | Automated daily web scraper synchronizing newly published standards and amendments |
| **NLP Entity Extraction** | Regex & domain dictionary tokenization for products, materials, and specs | Deep learning NER (Named Entity Recognition) transformer models |
| **Vector Search** | Dense embeddings via `SentenceTransformers all-MiniLM-L6-v2` in RAM | Redis / FAISS GPU cluster vector store for sub-millisecond enterprise throughput |
| **Knowledge Graph** | Dual-store Neo4j Cypher graph with NetworkX in-memory fallback (504 nodes, 1,340 edges) | Distributed Neo4j Enterprise cluster linking international ISO/IEC cross-references |
| **QCO Verification** | Verified QCO gazette matching against database gazette orders | Direct integration with Ministry e-Gazette APIs |
| **GeM Portal Integration** | Standalone REST API & Web Dashboard | Direct API plugin for Government e-Marketplace (GeM) tender auto-filling |
| **Multilingual NLP** | English natural language procurement description parsing | Regional Indian language parsing (Hindi, Tamil, Marathi, Bengali) |
| **Containerization** | Dockerfile & Docker Compose production setup | Kubernetes (k8s) helm charts for multi-region cloud deployment |
