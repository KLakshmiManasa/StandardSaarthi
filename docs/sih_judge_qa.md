# Smart India Hackathon (SIH 26108) — 15 Judge Questions & Answers

### Q1. Why is this system needed?
**Answer:** Procurement officials write requirements in natural language trade jargon, while Indian Standards are published under formal technical nomenclature. Identifying the correct IS code and mandatory Quality Control Orders (QCOs) manually leads to tender errors, audit objections, and non-compliant equipment delivery.

### Q2. Why can't traditional keyword search solve this problem?
**Answer:** Keyword search relies on exact token matching. Trade terms like "PVC wire" fail to match official titles like "Polyvinyl chloride insulated cables". Furthermore, keyword search has no understanding of material relationships or statutory QCO gazette notifications.

### Q3. Why do you use a Knowledge Graph?
**Answer:** Standards do not exist in isolation. A Knowledge Graph represents inter-standard relationships (`NORMATIVE_REFERENCE`, `SUPERSEDES`, `COMPLEMENTS`), interlinking product categories, materials, and testing standards.

### Q4. What is Graph-RAG and how does it differ from basic RAG?
**Answer:** Basic vector RAG retrieves isolated document text chunks based on semantic similarity alone. Graph-RAG traverses connected entities in the graph (e.g. concrete standard -> cement standard -> coarse aggregate standard), enriching the context with domain relationships.

### Q5. Why is the QCO Engine important?
**Answer:** Finding a relevant standard is not the same as verifying legal compliance. The QCO Engine checks whether candidate standards are governed by mandatory Quality Control Orders issued by Ministry gazettes.

### Q6. Where does your data come from?
**Answer:** The dataset is built from official Bureau of Indian Standards (BIS) catalogs, published standards documents, and Ministry Quality Control Order gazette notifications.

### Q7. How do you prevent AI hallucinations?
**Answer:** The system uses strict evidence grounding. Recommendations are generated from structured database records with primary source citations and official BIS URLs. If no verified match exists, the system returns `NO_RESULTS` rather than inventing an IS code.

### Q8. How did you evaluate the system?
**Answer:** We built a 195-query multi-sector evaluation benchmark across 13 product sectors measuring Mean Reciprocal Rank (MRR), Precision@K, Recall@K, NDCG@K, P50/P95 latency, and QCO accuracy.

### Q9. How does the system handle ambiguous procurement descriptions?
**Answer:** The query guardrail module checks if essential attributes (product type, application, material) are missing. If underspecified (e.g., "cable for office"), it returns `NEEDS_CLARIFICATION` and prompts the user for missing fields.

### Q10. How does the system scale to thousands of standards?
**Answer:** The pipeline uses a dual-store architecture: FAISS vector indices for fast dense retrieval and Neo4j for scalable graph traversals. Automated batch ingestion scripts handle data normalization and indexing.

### Q11. What happens if a requested standard is not in the dataset?
**Answer:** The system explicitly returns `NO_RESULTS` with a clear message: *"No verified Indian Standard was found in the current knowledge base matching your query."*

### Q12. Is this a legal compliance certification tool?
**Answer:** No. It is an evidence-grounded decision support tool designed to assist procurement officers. Statutory compliance flags apply strictly to verified database gazette records.

### Q13. How is your approach different from basic LLM prompts?
**Answer:** Direct LLM prompting suffers from hallucinations, lack of deterministic gazette verification, and outdated training data. Our system combines deterministic knowledge graph lookups and vector embeddings.

### Q14. What happens if QCO information is unavailable for a standard?
**Answer:** The system explicitly flags QCO status as *"No verified mandatory QCO order found in current database"* rather than assuming compliance.

### Q15. What is the biggest current limitation of your system?
**Answer:** The current pilot dataset indexes 120 verified standards across Electrical and Civil sectors. Scaling to the complete 20,000+ BIS standards corpus represents the primary future work roadmap item.
