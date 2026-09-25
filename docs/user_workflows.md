# User Workflows & Procurement Journeys

---

## 1. Free-Text Product Description Workflow (Mode A)
1. User opens `#/analyze`.
2. Selects "Mode A: Free-Text Description".
3. Enters procurement query (e.g. *"Procurement of 1.5 sq mm PVC insulated copper electrical cables for internal wiring"*).
4. Optionally selects input language (e.g. *Hindi / தமிழ் / Auto Detect*).
5. Clicks **Run Standards Analysis**.
6. Real-time progress bar displays execution stages: *Understanding requirement $\rightarrow$ Vector Search $\rightarrow$ Graph-RAG $\rightarrow$ QCO Engine*.
7. UI renders **Requirement Understanding** chips (Product, Material, Insulation, Application) and **Recommended Primary Standards** (Rank, IS Code, Match %, QCO Badge).
8. User clicks **"Why this standard?"** to inspect the matching factor breakdown in the slide-over drawer modal.
9. User clicks **Download PDF Report** to download the official multi-page PDF report.

---

## 2. Technical Specification Form Workflow (Mode B)
1. User opens `#/analyze` and switches to **Mode B: Technical Spec Form**.
2. Enters product details: Product Name (*Ready Mixed Concrete*), Grade (*M30*), Material (*Aggregate/Cement*), Application (*Structural works*).
3. Clicks **Submit Technical Specifications**.
4. Form values are normalized into internal query representation and processed through pipeline.
5. System displays primary recommendations (`IS 456`, `IS 4926`).

---

## 3. Tender Document Upload Workflow (Mode C)
1. User opens `#/analyze` and switches to **Mode C: Upload Tender File**.
2. Drags and drops or selects a PDF or DOCX tender document.
3. Clicks **Analyze Tender File**.
4. System parses text, segments document into sections, and extracts itemized procurement requirements.
5. System displays itemized requirements list on `#/tenders` tab with an `[Analyze]` button for each requirement.
6. User clicks `[Analyze]` on item 1 to run standards recommendation for that specific tender item.
