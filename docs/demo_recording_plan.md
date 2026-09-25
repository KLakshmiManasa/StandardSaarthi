# SIH 26108 — 3.5-Minute Video Demonstration Recording Sequence

If a recorded video demonstration is requested by SIH organizers, use this structured sequence:

---

## 🎬 Video Recording Timeline

| Timestamp | Section | Visual Content | Audio Narrative / Voiceover |
|---|---|---|---|
| **00:00 – 00:25** | **Problem Statement** | Title Slide & Web Search Dashboard | "Public procurement officers write specifications in natural language, but must map them to official Indian Standards (IS codes) and mandatory Quality Control Orders." |
| **00:25 – 00:50** | **Scenario 1 (Cable)** | Click preset button: `1. Electrical Cable` -> Click `Analyze Requirement` | "Notice how selecting Scenario 1 populates our text requirement. In under 20ms, the engine extracts entities and recommends IS 694." |
| **00:50 – 01:15** | **QCO & Evidence** | Highlight QCO Badge -> Click `View Evidence` modal | "The QCO Engine automatically flags that IS 694 requires mandatory certification under Ministry gazette directives, opening official BIS links." |
| **01:15 – 01:45** | **Scenario 3 (Graph-RAG)** | Click `3. Multi-Attribute` -> Click `Analyze` | "In Scenario 3, for ready mixed concrete, our Knowledge Graph recommends IS 4926 while exposing linked standards IS 456, IS 8112, and IS 383." |
| **01:45 – 02:15** | **Guardrails (Ambiguity)** | Click `2. Ambiguous Query` -> Click `Analyze` | "For vague queries like 'cable for office', the system triggers Needs Clarification, requesting missing voltage and material specifications." |
| **02:15 – 02:40** | **Guardrails (OOD)** | Click `5. Out of Domain` -> Click `Analyze` | "Out-of-domain queries like smartphone searches return Out of Domain, preventing arbitrary AI hallucinations." |
| **02:40 – 03:10** | **Evaluation & Benchmark** | Show `reports/phase8_evaluation_report.md` | "We benchmarked our engine across 195 multi-sector queries with P50 latency of 17.6ms and 100% guardrail accuracy." |
| **03:10 – 03:30** | **Conclusion** | Architecture Diagram Slide & Closing | "Our solution provides an evidence-grounded, transparent decision support platform for public procurement. Thank you!" |
