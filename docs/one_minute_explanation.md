# 60-Second Spoken Technical Explanation — SIH 26108

**"When a procurement officer enters a tender requirement, StandardSaarthi first executes security sanitization and query guardrails to ensure input safety and identify missing technical parameters.**

**Next, our domain-specific NLP module extracts structured attributes: product types, material grades, intended applications, and technical specifications.**

**A dense semantic retriever using SentenceTransformers computes 384-dimensional embeddings to match the description against official Bureau of Indian Standards scope documentation.**

**Concurrently, our statutory QCO Engine deterministically checks candidate standards against mandatory Quality Control Orders notified by Central Ministries.**

**Our Hybrid Ranker fuses semantic similarity, exact entity overlap, and mandatory regulatory weights. Crucially, if confidence is low, margin is narrow, or required attributes are absent, the system does not force a guess—it triggers confidence-gating, abstains, and surfaces closest candidates for human review.**

**Finally, the officer review layer enables the officer to accept or override the recommendation with a logged statutory justification, creating an immutable audit trail for tender defense."**

