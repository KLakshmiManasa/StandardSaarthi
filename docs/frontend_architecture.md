# Frontend Architecture & SPA Design Document

**Project:** Indian Standards Recommendation Engine & Procurement Intelligence Platform  
**Phase:** Phase 12 — Dynamic UI & Integration  

---

## 1. Overview

The frontend is built as a responsive Single Page Application (SPA) using vanilla HTML5, CSS3, and ES6 JavaScript. It communicates asynchronously with the FastAPI REST API backend via standard `fetch` APIs.

---

## 2. Component Structure & Hierarchy

```text
frontend/
├── index.html          # Main SPA shell & template layout
├── styles.css          # Design tokens, SaaS color palette & responsive styles
└── app.js              # SPA Hash Router, State Manager, API Client & Controllers
```

---

## 3. Router Architecture

The SPA uses hash-based client-side routing (`window.location.hash`).

### Supported Hash Routes:
- `#/`: Clean Homepage with CTAs, Recent Analyses, and 4-step "How it Works" guide.
- `#/analyze`: Primary Recommendation Workspace (Mode A, Mode B, Mode C tabs).
- `#/tenders`: Uploaded Tender Document Requirements Matrix.
- `#/standards`: Verified Indian Standards Catalog Search & Sector Filter.
- `#/standards/:code`: Standard Detail Page with Lifecycle & Categorized Graph Relationships.
- `#/regulatory`: Statutory QCO & BIS Certification Scheme Finder.
- `#/history`: Search History & Saved Procurement Projects.
- `#/reports`: Procurement PDF Reports Manager.
- `#/admin`: System Diagnostics & Performance Benchmarks (Isolated).

---

## 4. Toast Notification & Modal Drawer System

- **Toast Container (`#toast-container`):** Displays floating non-intrusive notification popups at the bottom-right corner.
- **Slide-over Drawer Modal (`#why-modal-overlay`):** Displays detailed matching breakdown for *"Why this standard?"*.
- **Standard Detail Modal (`#standard-detail-view`):** Renders scope, amendments, lifecycle status, and normative references.
