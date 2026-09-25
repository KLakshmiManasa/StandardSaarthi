# 60-Second Spoken Technical Explanation — SIH 26108

**"When a user enters a procurement requirement, our engine first passes the query through security sanitizers and query guardrails to ensure input safety and completeness.**

**Next, our NLP module extracts product types, material compositions, intended applications, and technical specifications.**

**A dense vector retriever using SentenceTransformers computes 384-dimensional embeddings to find semantically similar standards.**

**Concurrently, our Knowledge Graph connects the extracted entities across 1-hop and 2-hop normative reference relationships in Neo4j.**

**Our QCO Engine checks whether candidate standards are subject to mandatory Quality Control Orders issued under Ministry gazettes.**

**Finally, a hybrid ranker fuses dense vector similarity, entity match scores, graph relevance, and QCO mandatory weights into an explainable relevance score, returning verifiable BIS primary source links."**
