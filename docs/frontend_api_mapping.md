# Frontend-Backend API & Interaction Mapping Audit

**Project:** Indian Standards Recommendation Engine & Procurement Intelligence Platform  
**Phase:** Phase 12 — Dynamic UI & Integration  
**Date:** 23 September 2026  

---

## 1. UI Action to Backend Endpoint Mapping Table

| UI Component / Button | User Action | Frontend Event Handler | Backend REST Endpoint | HTTP Method | Response Payload / Behavior | Working Status |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: |
| **Home -> Primary CTA 1** | Click "Analyze Requirement" | `navigateTo('#/analyze')` | Client SPA Route | `N/A` | Navigates to `/analyze` view | `CONNECTED` |
| **Home -> Primary CTA 2** | Click "Upload Tender Document" | `navigateTo('#/analyze')` | Client SPA Route | `N/A` | Navigates to Mode C upload tab | `CONNECTED` |
| **Home -> Browse Catalog** | Click "Browse Catalog" | `navigateTo('#/standards')` | Client SPA Route | `N/A` | Navigates to `/standards` view | `CONNECTED` |
| **Mode A -> Submit** | Click "Run Standards Analysis" | `runAnalysisModeA()` | `/api/analyze` | `POST` | Structured JSON recommendations + entities + QCO | `CONNECTED` |
| **Mode B -> Submit** | Click "Submit Specifications" | `runAnalysisModeB()` | `/api/analyze/specification` | `POST` | Spec query normalization + recommendations | `CONNECTED` |
| **Mode C -> Dropzone** | Select PDF / DOCX file | `handleSelectedFile(file)` | Client FileReader | `N/A` | Displays filename & enables Upload button | `CONNECTED` |
| **Mode C -> Upload** | Click "Analyze Tender File" | `uploadTenderDocument()` | `/api/analyze/document` | `POST` | Itemized requirement items list | `CONNECTED` |
| **Tender Item -> Analyze** | Click "Analyze Item X" | `analyzeTenderItem(text)` | `/api/analyze` | `POST` | Runs Mode A analysis on item text | `CONNECTED` |
| **Rec Card -> View Details** | Click "Inspect Standard Details" | `loadStandardDetails(code)` | `/api/standards/{code}` | `GET` | Full standard details, scope, lifecycle | `CONNECTED` |
| **Rec Card -> Why Standard** | Click "Why This Standard?" | `openWhyModal(code)` | Client Result Data | `N/A` | Opens slide-over drawer modal with score breakdown | `CONNECTED` |
| **Rec Card -> Download PDF** | Click "Download PDF Report" | `downloadPdfReport()` | `/api/reports/generate` | `POST` | Multi-page PDF binary stream attachment | `CONNECTED` |
| **Standards Search Bar** | Type in search input | `filterCatalog()` | `/api/standards?q=...` | `GET` | Filtered list of verified standards | `CONNECTED` |
| **Regulatory Portal** | View / Search QCOs | `loadQCO()` | `/api/regulatory` | `GET` | List of mandatory QCO gazette notices | `CONNECTED` |
| **History Tab** | View search history | `loadHistory()` | `/api/history` | `GET` | List of past queries & saved projects | `CONNECTED` |
| **Admin Tab** | View system status | `loadAdminMetrics()` | `/api/admin/metrics` | `GET` | Isolated benchmark & diagnostic metrics | `CONNECTED` |

---

## 2. Toast Notification Signals

| Trigger Condition | Toast Type | Message Content |
| :--- | :---: | :--- |
| Analysis Completed | `SUCCESS` | *"Procurement requirement analyzed successfully!"* |
| Document Parsed | `SUCCESS` | *"{filename} parsed successfully into {count} items!"* |
| PDF Report Downloaded | `SUCCESS` | *"PDF Procurement Standards Report generated successfully!"* |
| Standard Detail Loaded | `INFO` | *"Loaded standard details for {is_code}."* |
| Ambiguity Detected | `WARNING` | *"Insufficient specification. Please clarify product type or grade."* |
| Out-of-Domain Query | `ERROR` | *"Query restricted to Indian Standards procurement domain."* |
| File Upload Error | `ERROR` | *"Failed to process document file. Please select PDF, DOCX, or TXT."* |
