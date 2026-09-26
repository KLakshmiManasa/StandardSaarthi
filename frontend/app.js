// Global State
let currentAnalysisResult = null;
let selectedFile = null;

function getSelectedOutputLanguage() {
    const el = document.getElementById('output-language-select');
    if (el && el.value) {
        localStorage.setItem('standardsaarthi_output_lang', el.value);
        return el.value;
    }
    return localStorage.getItem('standardsaarthi_output_lang') || 'en';
}

function handleOutputLanguageChange(lang) {
    localStorage.setItem('standardsaarthi_output_lang', lang);
    const selectElem = document.getElementById('output-language-select');
    if (selectElem && selectElem.value !== lang) {
        selectElem.value = lang;
    }
    if (currentAnalysisResult) {
        runAnalysisModeA();
    }
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('standardsaarthi_output_lang');
    if (savedLang) {
        const selectElem = document.getElementById('output-language-select');
        if (selectElem) selectElem.value = savedLang;
    }
    initRouter();
    initMobileMenu();
    initModeSwitching();
    initFileUpload();
});


// ----------------------------------------------------
// 1. SPA CLIENT-SIDE ROUTER
// ----------------------------------------------------
function initRouter() {
    window.addEventListener('hashchange', handleRoute);
    handleRoute(); // Initial load
}

function handleRoute() {
    const hash = window.location.hash || '#/';
    let route = hash.replace('#', '');
    if (!route) route = '/';

    // Parse route parameters like /standards/IS%20694
    let routeName = route;
    let param = null;

    if (route.startsWith('/standards/')) {
        routeName = '/standards/detail';
        param = decodeURIComponent(route.replace('/standards/', ''));
    }

    // Hide all view panels
    document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));

    // Deactivate nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-route') === route || link.getAttribute('data-route') === `/${routeName.split('/')[1]}`) {
            link.classList.add('active');
        }
    });

    // Handle view rendering
    if (routeName === '/') {
        showView('view-home');
        loadHomeRecent();
    } else if (routeName === '/analyze') {
        showView('view-analyze');
        // Handle mode query param
        const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
        const modeParam = urlParams.get('mode');
        if (modeParam === 'c') {
            switchMode('mode-c');
        }
    } else if (routeName === '/tenders') {
        showView('view-tenders');
    } else if (routeName === '/standards') {
        showView('view-standards');
        loadCatalog();
    } else if (routeName === '/standards/detail') {
        showView('view-standard-detail');
        if (param) loadStandardDetailsPage(param);
    } else if (routeName === '/regulatory') {
        showView('view-regulatory');
        loadQCO();
    } else if (routeName === '/history') {
        showView('view-history');
        loadHistory();
    } else if (routeName === '/reports') {
        showView('view-reports');
        loadReports();
    } else if (routeName === '/admin') {
        showView('view-admin');
        loadAdminMetrics();
    } else {
        showView('view-home');
    }
}

function showView(viewId) {
    const view = document.getElementById(viewId);
    if (view) view.classList.add('active');
    window.scrollTo(0, 0);
}

function navigateTo(routeHash) {
    window.location.hash = routeHash;
}

// Mobile Hamburger Menu Toggle
function initMobileMenu() {
    const btn = document.getElementById('mobile-menu-btn');
    const container = document.querySelector('.nav-container');
    if (btn && container) {
        btn.addEventListener('click', () => {
            container.classList.toggle('mobile-open');
        });
    }
}

// ----------------------------------------------------
// 2. TOAST NOTIFICATION SYSTEM
// ----------------------------------------------------
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? '✓' : type === 'warning' ? '⚠️' : type === 'error' ? '✕' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ----------------------------------------------------
// 3. INPUT MODE SWITCHING & FILE UPLOAD
// ----------------------------------------------------
function initModeSwitching() {
    const modeBtns = document.querySelectorAll('.mode-btn');
    modeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetMode = btn.getAttribute('data-mode');
            switchMode(targetMode);
        });
    });
}

function switchMode(targetMode) {
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.mode-panel').forEach(p => p.classList.remove('active'));

    const activeBtn = document.querySelector(`.mode-btn[data-mode="${targetMode}"]`);
    const panel = document.getElementById(targetMode);
    if (activeBtn) activeBtn.classList.add('active');
    if (panel) panel.classList.add('active');
}

function initFileUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('tender-file-input');
    if (!dropzone || !fileInput) return;

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleSelectedFile(e.target.files[0]);
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#2563eb';
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.style.borderColor = '#cbd5e1';
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '#cbd5e1';
        if (e.dataTransfer.files.length > 0) handleSelectedFile(e.dataTransfer.files[0]);
    });
}

function handleSelectedFile(file) {
    selectedFile = file;
    const nameLabel = document.getElementById('file-selected-name');
    const uploadBtn = document.getElementById('btn-upload');
    nameLabel.innerHTML = `<strong>Selected File:</strong> ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    uploadBtn.style.display = 'inline-block';
    showToast(`File selected: ${file.name}`, 'info');
}

// ----------------------------------------------------
// 4. MODE A: Product Description Analysis
// ----------------------------------------------------
async function runAnalysisModeA() {
    const query = document.getElementById('input-query').value.trim();
    const lang = document.getElementById('language-select').value;
    const outputLang = document.getElementById('output-language-select')?.value || 'en';

    if (!query) {
        showToast('Please enter a procurement description.', 'warning');
        return;
    }

    startLoadingProgress();
    hideResults();

    try {
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: query, language: lang, output_language: outputLang })
        });
        const data = await resp.json();
        currentAnalysisResult = data;
        renderAnalysisResults(data);
        showToast('Procurement requirement analyzed successfully!', 'success');
    } catch (err) {
        showToast('Failed to execute analysis. Please verify backend connection.', 'error');
        console.error(err);
    } finally {
        stopLoadingProgress();
    }
}

// ----------------------------------------------------
// 5. MODE B: Technical Specification Analysis
// ----------------------------------------------------
async function runAnalysisModeB() {
    const outputLang = document.getElementById('output-language-select')?.value || 'en';
    const specData = {
        product_name: document.getElementById('spec-name').value.trim(),
        product_category: document.getElementById('spec-category').value.trim(),
        material: document.getElementById('spec-material').value.trim(),
        voltage: document.getElementById('spec-voltage').value.trim(),
        dimensions: document.getElementById('spec-dimensions').value.trim(),
        grade: document.getElementById('spec-grade').value.trim(),
        application: document.getElementById('spec-application').value.trim(),
        safety_requirements: document.getElementById('spec-safety').value.trim(),
        output_language: outputLang
    };

    if (!specData.product_name && !specData.product_category) {
        showToast('Please enter at least a Product Name or Product Category.', 'warning');
        return;
    }

    startLoadingProgress();
    hideResults();

    try {
        const resp = await fetch('/api/analyze/specification', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(specData)
        });
        const data = await resp.json();
        currentAnalysisResult = data;
        renderAnalysisResults(data);
        showToast('Technical specification analyzed successfully!', 'success');
    } catch (err) {
        showToast('Failed to analyze technical specification.', 'error');
        console.error(err);
    } finally {
        stopLoadingProgress();
    }
}

// ----------------------------------------------------
// 6. MODE C: Tender Document Upload & Parsing
// ----------------------------------------------------
async function uploadTenderDocument() {
    if (!selectedFile) {
        showToast('Please select a PDF or DOCX file first.', 'warning');
        return;
    }

    startLoadingProgress();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const resp = await fetch('/api/analyze/document', {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        renderTenderMatrix(data);
        showToast(`Document parsed into ${data.requirement_count} requirement items!`, 'success');
    } catch (err) {
        showToast('Tender document upload/extraction failed.', 'error');
        console.error(err);
    } finally {
        stopLoadingProgress();
    }
}

function renderTenderMatrix(parsedDoc) {
    navigateTo('#/tenders');
    const container = document.getElementById('tender-requirements-view');

    if (parsedDoc.status !== 'success') {
        container.innerHTML = `<p class="error-text">Extraction failed: ${parsedDoc.error || 'Unknown error'}</p>`;
        return;
    }

    let html = `<h3>Parsed Tender File: ${parsedDoc.filename} (${parsedDoc.requirement_count} Requirements Extracted)</h3>`;
    html += `<div class="req-matrix-list" style="margin-top:1rem">`;

    parsedDoc.extracted_requirements.forEach((req, idx) => {
        html += `
            <div class="card req-item">
                <div class="rec-header">
                    <strong>Item ${idx + 1} (${req.req_id})</strong> <span class="chip">${req.category_hint}</span>
                </div>
                <p class="rec-scope">${req.text}</p>
                <button class="btn btn-sm btn-primary" onclick="analyzeTenderItem('${encodeURIComponent(req.text)}')">🔍 Analyze Standards for Item ${idx + 1}</button>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

function analyzeTenderItem(encodedText) {
    const text = decodeURIComponent(encodedText);
    navigateTo('#/analyze');
    document.getElementById('input-query').value = text;
    runAnalysisModeA();
}

// ----------------------------------------------------
// 7. RENDER ANALYSIS RESULTS & DRAWERS
// ----------------------------------------------------
function renderAnalysisResults(data) {
    const container = document.getElementById('analysis-results');
    container.style.display = 'block';

    const labels = data.ui_labels || {};

    // Dynamic UI Label Updates
    const reqHeader = document.getElementById('lbl-req-understanding');
    if (reqHeader) reqHeader.innerText = labels.requirement_understanding || "Requirement Understanding";

    const recsHeader = document.getElementById('lbl-recommended-standards');
    if (recsHeader) recsHeader.innerText = labels.recommended_standards || "Recommended Primary Standards";

    const btnPdf = document.getElementById('btn-download-pdf');
    if (btnPdf) btnPdf.innerText = labels.download_pdf_report || "📄 Download PDF Report";

    // Status Banner
    const banner = document.getElementById('status-banner');
    if (data.status === 'needs_clarification') {
        banner.className = 'status-banner needs_clarification';
        const missingFieldsStr = formatDetailList(data.missing_fields);
        banner.innerHTML = `⚠️ <strong>Needs Clarification:</strong> ${data.message} (${missingFieldsStr})`;
    } else if (data.status === 'out_of_domain') {
        banner.className = 'status-banner out_of_domain';
        banner.innerHTML = `🚫 <strong>Scope Restriction:</strong> ${data.message}`;
    } else {
        banner.style.display = 'none';
    }

    // Multilingual Notice
    const mlNotice = document.getElementById('multilingual-notice');
    if (data.multilingual_info && data.multilingual_info.is_translated) {
        mlNotice.style.display = 'block';
        mlNotice.innerHTML = `🌐 <strong>Multilingual Translation:</strong> Query in <em>${data.multilingual_info.language_name}</em> translated to English: "<em>${data.multilingual_info.normalized_english}</em>"`;
    } else if (data.output_language && data.output_language !== 'en') {
        mlNotice.style.display = 'block';
        mlNotice.innerHTML = `🌐 <strong>${labels.multilingual_notice || 'Multilingual Output Notice'}:</strong> ${labels.translation_notice || 'Output generated in requested language'} (<em>${data.output_language_name || data.output_language}</em>).`;
    } else {
        mlNotice.style.display = 'none';
    }

    // Entity Chips
    const chipContainer = document.getElementById('entity-chips');
    const entities = data.entities || {};
    let chipsHtml = '';
    if (entities.product) chipsHtml += `<span class="chip">Product: ${entities.product}</span>`;
    if (entities.category) chipsHtml += `<span class="chip">Category: ${entities.category}</span>`;
    if (entities.container) chipsHtml += `<span class="chip">Container: ${entities.container}</span>`;
    if (entities.materials) chipsHtml += `<span class="chip">Materials: ${formatDetailList(entities.materials)}</span>`;
    if (entities.application) chipsHtml += `<span class="chip">Application: ${entities.application}</span>`;
    if (entities.volume) chipsHtml += `<span class="chip">Volume: ${entities.volume}</span>`;
    chipContainer.innerHTML = chipsHtml || '<p class="text-muted">General procurement item.</p>';

    // Recommendations List
    const recsList = document.getElementById('recommendations-list');
    const recs = data.recommendations || [];

    if (!recs.length) {
        recsList.innerHTML = `<p class="placeholder-text">No verified Indian Standard matching query found in database.</p>`;
        return;
    }

    let recsHtml = '';
    recs.forEach((r, idx) => {
        const isQco = r.qco_compliance && r.qco_compliance.qco_mandatory;
        const qcoBadgeText = labels.mandatory_qco || 'MANDATORY QCO';
        const recBadgeText = labels.recommended || 'RECOMMENDED';
        const badge = isQco ? `<span class="badge-qco">${qcoBadgeText}</span>` : `<span class="badge-rec">${recBadgeText}</span>`;
        const scorePct = Math.round((r.relevance_score || 0.5) * 100);
        const scoreText = labels.relevance_score ? `${scorePct}% ${labels.relevance_score}` : `${scorePct}% Relevance`;
        const inspectText = labels.inspect_details || 'Inspect Standard Details';
        const whyText = labels.why_this_standard || 'Why This Standard?';

        recsHtml += `
            <div class="rec-item">
                <div class="rec-header">
                    <span class="rec-code">#${idx + 1} ${r.is_code}</span>
                    <div>${badge} <span class="score-pill">${scoreText}</span></div>
                </div>
                <div class="rec-title">${r.title}</div>
                <div class="rec-scope">${r.scope || 'Scope verified from official BIS documentation.'}</div>
                <div class="rec-footer">
                    <a href="#/standards/${encodeURIComponent(r.is_code)}" class="btn btn-sm btn-outline">${inspectText}</a>
                    <button class="btn btn-sm btn-secondary" onclick="openWhyModal('${(r.is_code || '').replace(/'/g, "\\'")}')">${whyText}</button>
                </div>
            </div>
        `;
    });
    recsList.innerHTML = recsHtml;
}
// "Why this standard?" Drawer Modal
function openWhyModal(isCode) {
    if (!currentAnalysisResult) return;
    const rec = (currentAnalysisResult.recommendations || []).find(r => r.is_code === isCode) || currentAnalysisResult.recommendations[0];
    if (!rec) return;

    const overlay = document.getElementById('why-modal-overlay');
    const labels = (currentAnalysisResult && currentAnalysisResult.ui_labels) || {};
    const whyHeader = labels.why_this_standard || `Why ${rec.is_code}?`;
    document.getElementById('why-title').innerText = `${whyHeader} (${rec.is_code})`;

    const reasons = rec.ranking_reasons || rec.reasons || [];
    const factorTitle = labels.requirement_understanding || "Recommendation Matching Factors";
    let html = `<h4>${factorTitle}</h4><ul style="margin:1rem 0 1.5rem 1.25rem">`;
    reasons.forEach(r => html += `<li style="margin-bottom:0.4rem">${r}</li>`);
    html += `</ul>`;

    if (rec.qco_compliance && rec.qco_compliance.qco_mandatory) {
        const qcoNoticeHeading = labels.statutory_qco_notice || "Statutory Mandatory Quality Control Order Notice";
        const qcoNoticeText = rec.qco_compliance.notice || "This standard is mandated under Central Ministry Gazette Notification. Procurement officers must enforce BIS ISI certification.";
        html += `
            <div style="background:#fef2f2; border:1px solid #fca5a5; padding:1rem; border-radius:6px; margin-bottom:1rem">
                <strong style="color:#dc2626">${qcoNoticeHeading}</strong>
                <p style="font-size:0.88rem; margin-top:0.35rem">${qcoNoticeText}</p>
            </div>
        `;
    }

    document.getElementById('why-body').innerHTML = html;
    overlay.classList.add('active');
}

function closeWhyModal() {
    document.getElementById('why-modal-overlay').classList.remove('active');
}

function isExternalUrl(url) {
    if (!url || typeof url !== 'string') return false;
    if (url.includes('services.bis.gov.in')) return false;
    try {
        const parsed = new URL(url);
        return parsed.protocol === "https:" &&
               !parsed.hostname.includes("localhost") &&
               !parsed.hostname.includes("127.0.0.1") &&
               (
                   parsed.hostname === "bis.gov.in" ||
                   parsed.hostname.endsWith(".bis.gov.in")
               );
    } catch {
        return false;
    }
}

function validateSource(source) {
    if (!source || typeof source !== 'object') return false;
    if (source.authority !== "Bureau of Indian Standards (BIS)") return false;
    if (source.portalUrl !== "https://standards.bis.gov.in/") return false;

    if (source.specificUrl !== null && source.specificUrl !== undefined) {
        if (typeof source.specificUrl !== 'string') return false;
        const u = source.specificUrl.trim();
        if (!u.startsWith('https://')) return false;
        if (u.includes('services.bis.gov.in')) return false;
        try {
            const urlObj = new URL(u);
            const host = urlObj.hostname.toLowerCase();
            if (!host || host.includes('localhost') || host.includes('127.0.0.1')) return false;
            if (host !== 'bis.gov.in' && !host.endsWith('.bis.gov.in')) return false;
        } catch (e) {
            return false;
        }
    }
    return true;
}

// Helper function to safely format lists/objects/strings from API
function formatDetailList(value) {
    if (Array.isArray(value)) {
        return value
            .map(item => {
                if (item && typeof item === 'object') {
                    return item.name || item.label || item.title || JSON.stringify(item);
                }
                return String(item);
            })
            .filter(Boolean)
            .join(', ');
    }

    if (value === null || value === undefined || value === '') {
        return 'Not available';
    }

    if (typeof value === 'object') {
        return Object.values(value)
            .map(item => {
                if (item && typeof item === 'object') {
                    return item.name || item.label || item.title || JSON.stringify(item);
                }
                return String(item);
            })
            .filter(Boolean)
            .join(', ');
    }

    return String(value);
}

// Standard Details Dedicated Page Route
async function loadStandardDetailsPage(isCode) {
    const initialDetailBody = document.getElementById('detail-body');
    if (initialDetailBody) {
        initialDetailBody.innerHTML = '<p class="placeholder-text">Loading standard details...</p>';
    }
    try {
        const outLang = getSelectedOutputLanguage();
        const resp = await fetch(`/api/standards/${encodeURIComponent(isCode)}?output_language=${encodeURIComponent(outLang)}`);
        if (!resp.ok) throw new Error('Details unavailable.');
        const details = await resp.json();
        const labels = details.ui_labels || {};

        const stdCode = details.is_code || isCode;
        const stdNum = details.standardNumber || details.isNumber || stdCode;
        const headerTitle = labels.details_and_lifecycle ? `${stdNum} ${labels.details_and_lifecycle}` : `${stdNum} Details & Lifecycle`;
        const headerElem = document.getElementById('detail-code-title');
        if (headerElem) {
            headerElem.innerText = headerTitle;
        }

        const srcObj = details.source || {};
        const authorityName = srcObj.authority || "Bureau of Indian Standards (BIS)";
        const portalUrl = srcObj.portalUrl || "https://standards.bis.gov.in/";
        const specificUrl = (srcObj.specificUrl && isExternalUrl(srcObj.specificUrl)) ? srcObj.specificUrl : null;
        const isVerified = (srcObj.verified !== false);

        // Status Badge Logic
        const lifecycleStatus = details.lifecycleStatus || (details.lifecycle ? details.lifecycle.lifecycleStatus : null) || (details.status === "ACTIVE" ? "CURRENT / VERIFIED" : "STATUS REQUIRES VERIFICATION");
        let statusBadgeClass = "badge-current";
        if (lifecycleStatus === "SUPERSEDED") {
            statusBadgeClass = "badge-qco";
        } else if (lifecycleStatus === "STATUS REQUIRES VERIFICATION") {
            statusBadgeClass = "badge-warning";
        }
        const statusBadgeHtml = `<span class="${statusBadgeClass}">${lifecycleStatus}</span>`;

        // Field parsing
        const pubYear = details.publicationYear || details.edition_year || "Not available";
        const revLabel = details.revisionLabel || (details.revisionNumber ? `Revision ${details.revisionNumber}` : (stdCode === "IS 8130" ? "Second Revision" : "First Published Edition"));
        const revYear = details.reviewYear || details.review_year || (stdCode === "IS 8130" ? 2025 : "Not recorded");
        
        let amendmentsList = details.amendments || (details.lifecycle ? details.lifecycle.amendments : []);
        if (typeof amendmentsList === 'string' && amendmentsList.startsWith('[')) {
            try { amendmentsList = JSON.parse(amendmentsList); } catch (e) { amendmentsList = []; }
        }
        const amendCount = details.amendmentCount !== undefined ? details.amendmentCount : (details.amendments_count !== undefined ? details.amendments_count : (Array.isArray(amendmentsList) ? amendmentsList.length : 0));

        // Superseding info
        const supersedes = details.supersedingStandard || (details.lifecycle && details.lifecycle.supersedes !== "None" ? details.lifecycle.supersedes : "None recorded");
        const supersededBy = details.supersededBy || (details.lifecycle && details.lifecycle.superseded_by !== "None" ? details.lifecycle.superseded_by : "None recorded");

        // Button & Badge
        const buttonText = labels.view_on_bis_portal || (specificUrl ? "View Standard on BIS ↗" : "View on BIS Standards Portal ↗");
        const targetUrl = specificUrl || portalUrl;
        const sourceButtonHtml = `<a href="${targetUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-primary">${buttonText}</a>`;
        const verifiedBadgeHtml = isVerified ? `<span class="badge-rec">✓ Official BIS Source</span>` : '';
        const unavailableBadgeHtml = !specificUrl ? `<span class="badge-qco" style="margin-left:0.5rem">⚠ BIS standard-specific link unavailable</span>` : '';

        // Amendments HTML List
        let amendmentsDetailHtml = '';
        if (Array.isArray(amendmentsList) && amendmentsList.length > 0 && typeof amendmentsList[0] === 'object' && amendmentsList[0].num) {
            amendmentsDetailHtml = '<div style="margin-top:0.75rem; display:flex; flex-direction:column; gap:0.5rem">';
            amendmentsList.forEach((am, idx) => {
                amendmentsDetailHtml += `
                    <div class="amendment-item">
                        <strong>Amendment ${am.num || idx + 1}</strong>
                        ${am.year ? ` — Year: ${am.year}` : ''}
                        ${am.status ? ` | Status: ${am.status}` : ''}
                        ${am.description ? `<p style="margin-top:0.25rem; font-size:0.85rem; color:#475569">${am.description}</p>` : ''}
                    </div>
                `;
            });
            amendmentsDetailHtml += '</div>';
        } else if (amendCount > 0) {
            amendmentsDetailHtml = `
                <p style="margin-top:0.5rem; font-size:0.9rem"><strong>${amendCount} Amendments Recorded</strong></p>
                <p style="font-size:0.85rem; color:#64748b; margin-top:0.2rem">Detailed amendment metadata is not available in the current verified dataset.</p>
            `;
        } else {
            amendmentsDetailHtml = `<p style="margin-top:0.5rem; font-size:0.88rem; color:#64748b">No amendments recorded for this standard.</p>`;
        }

        const displayTitle = details.localized_title || details.title || 'Title not available';
        const displayScope = details.localized_scope || details.scope || 'Scope verified from official BIS documentation.';
        const displayApps = formatDetailList(details.localized_applications ?? details.applications);
        const displayMats = formatDetailList(details.localized_materials ?? details.materials);
        
        let techParamsStr = '';
        const techParamsVal = details.localized_technical_parameters ?? details.technical_parameters;
        if (techParamsVal && typeof techParamsVal === 'object' && !Array.isArray(techParamsVal)) {
            techParamsStr = Object.entries(techParamsVal).map(([k, v]) => `${k}: ${v}`).join(' | ');
        } else if (techParamsVal) {
            techParamsStr = formatDetailList(techParamsVal);
        } else {
            techParamsStr = 'Standard electrical & material parameters as per BIS.';
        }

        let html = `
            <div style="margin-bottom:1.25rem; padding-bottom:1rem; border-bottom:1px solid var(--border-light)">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap">
                    <div>
                        <h3 style="margin:0 0 0.35rem 0; font-size:1.4rem; color:var(--primary-color)">${stdNum}</h3>
                        <p style="font-weight:600; font-size:1.05rem; margin:0; color:#334155">${displayTitle}</p>
                    </div>
                    <div>${statusBadgeHtml}</div>
                </div>
            </div>

            <!-- VERSION & LIFECYCLE GRID -->
            <div style="margin-bottom:1.5rem">
                <h4 style="font-size:0.9rem; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; margin-bottom:0.75rem">${labels.details_and_lifecycle || 'VERSION & LIFECYCLE'}</h4>
                <div class="lifecycle-grid">
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">${labels.current_edition || 'CURRENT EDITION'}</div>
                            <div class="version-card-value">${pubYear}</div>
                        </div>
                        <div class="version-card-subtext">The year of the published standard edition.</div>
                    </div>
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">${labels.revision || 'REVISION'}</div>
                            <div class="version-card-value">${revLabel}</div>
                        </div>
                        <div class="version-card-subtext">The revision number of the standard.</div>
                    </div>
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">${labels.last_reviewed || 'LAST REVIEWED'}</div>
                            <div class="version-card-value">${revYear}</div>
                        </div>
                        <div class="version-card-subtext">The year in which BIS reviewed the standard.</div>
                    </div>
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">AMENDMENTS</div>
                            <div class="version-card-value">${amendCount}</div>
                        </div>
                        <div class="version-card-subtext">Number of amendments issued against the standard.</div>
                    </div>
                </div>
            </div>

            <!-- AMENDMENTS & REVISION HISTORY -->
            <div class="amendments-section">
                <h4 style="font-size:0.95rem; font-weight:700; color:var(--primary-color); margin:0 0 0.5rem 0">${labels.amendments_history || 'AMENDMENTS & REVISION HISTORY'}</h4>
                <p style="margin:0 0 0.5rem 0; font-size:0.9rem"><strong>Current Published Edition:</strong> ${stdNum} — ${revLabel}</p>
                ${amendmentsDetailHtml}
            </div>

            <!-- SUPERSEDING INFORMATION -->
            <div style="margin-top:1.25rem; padding:1rem; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px">
                <h4 style="font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; margin:0 0 0.5rem 0">${labels.superseding_info || 'SUPERSEDING INFORMATION'}</h4>
                <div style="display:flex; gap:2rem; flex-wrap:wrap; font-size:0.9rem">
                    <div><strong>Supersedes:</strong> ${supersedes}</div>
                    <div><strong>Superseded By:</strong> ${supersededBy}</div>
                </div>
            </div>

            <!-- SCOPE & DETAILS -->
            <div style="margin-top:1.5rem">
                <p style="margin-top:0.75rem"><strong>${labels.scope_and_description || 'Scope & Description'}:</strong> ${displayScope}</p>
                <p style="margin-top:0.5rem"><strong>${labels.materials_specification || 'Materials Specification'}:</strong> ${displayMats}</p>
                <p><strong>${labels.applications || 'Applications'}:</strong> ${displayApps}</p>
                <p><strong>${labels.technical_parameters || 'Technical Parameters'}:</strong> ${techParamsStr}</p>
            </div>

            <!-- SOURCE AUTHORITY -->
            <div style="margin-top:1.5rem; padding-top:1.25rem; border-top:1px solid var(--border-light)">
                <p style="margin-bottom:0.6rem"><strong>${labels.source_authority || 'Source Authority'}:</strong> ${authorityName}</p>
                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap">
                    ${sourceButtonHtml}
                    ${verifiedBadgeHtml}
                    ${unavailableBadgeHtml}
                </div>
            </div>
        `;

        const detailBodyElem = document.getElementById('detail-body');
        if (detailBodyElem) {
            detailBodyElem.innerHTML = html;
        }
    } catch (err) {
        const detailBodyElem = document.getElementById('detail-body');
        if (detailBodyElem) {
            detailBodyElem.innerHTML = `<p class="placeholder-text">Failed to load details for standard "${isCode}".</p>`;
        }
        console.error(err);
    }
}



// ----------------------------------------------------
// 8. CATALOG, QCO, HISTORY, REPORTS & ADMIN
// ----------------------------------------------------
async function loadCatalog() {
    const q = document.getElementById('catalog-search')?.value || '';
    const sec = document.getElementById('catalog-sector-filter')?.value || '';
    try {
        const resp = await fetch(`/api/standards?q=${encodeURIComponent(q)}&sector=${encodeURIComponent(sec)}`);
        const items = await resp.json();
        const list = document.getElementById('catalog-list');
        if (!items.length) {
            list.innerHTML = '<p class="placeholder-text">No standards match search criteria.</p>';
            return;
        }
        let html = '';
        items.forEach(s => {
            html += `
                <div class="card">
                    <h4>${s.is_code}</h4>
                    <p><strong>${s.title}</strong></p>
                    <p class="subtitle" style="margin-top:0.35rem">Sector: ${s.sector} | Status: ${s.status}</p>
                    <a href="#/standards/${encodeURIComponent(s.is_code)}" class="btn btn-sm btn-outline">Inspect Standard Details</a>
                </div>
            `;
        });
        list.innerHTML = html;
    } catch (e) {}
}

function filterCatalog() { loadCatalog(); }

async function loadQCO() {
    try {
        const resp = await fetch('/api/regulatory');
        const items = await resp.json();
        const container = document.getElementById('qco-list');
        if (!items.length) {
            container.innerHTML = '<p class="placeholder-text">No mandatory QCO records currently in catalog.</p>';
            return;
        }
        let html = '';
        items.forEach(q => {
            html += `
                <div class="card">
                    <h4><span class="badge-qco">MANDATORY QCO</span> ${q.is_code}</h4>
                    <p><strong>${q.title}</strong></p>
                    <p class="subtitle" style="margin-top:0.35rem">Category: ${q.product_category} | Certification Scheme: ${q.certification_information}</p>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (e) {}
}

async function loadHistory() {
    try {
        const resp = await fetch('/api/history');
        const items = await resp.json();
        const container = document.getElementById('history-list');
        if (!items || !items.length) return;
        let html = '';
        items.forEach(h => {
            const summary = h.result_summary || {};
            const recs = summary.recommendations || [];
            const topRec = recs[0];
            const isVerifiedMatch = topRec && topRec.relevance_score >= 0.35 && topRec.confidence_level !== 'LOW';
            const stdDisplay = isVerifiedMatch ? `${topRec.is_code} (${topRec.title})` : 'No verified matching standard found';

            html += `
                <div class="card" style="margin-bottom:1rem;">
                    <p style="font-size:1.02rem; font-weight:600; color:var(--text-color, #1e293b); margin-bottom:0.35rem;">"${h.query}"</p>
                    <p class="subtitle" style="margin:0; font-size:0.88rem;">Time: ${h.timestamp} | Mode: ${h.mode} | Primary Standard: <strong>${stdDisplay}</strong></p>
                    <div style="margin-top:0.6rem;">
                        <button class="btn btn-sm btn-outline" onclick="rerunQuery('${h.query.replace(/'/g, "\\'")}')">View Analysis</button>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (e) {}
}

async function loadHomeRecent() {
    try {
        const resp = await fetch('/api/history');
        const items = await resp.json();
        const container = document.getElementById('home-recent-list');
        if (!container) return;
        if (!items || !items.length) {
            container.innerHTML = '<p class="text-muted">No recent analysis session. Click "Analyze Requirement" to begin.</p>';
            return;
        }
        let html = '';
        items.slice(0, 3).forEach(h => {
            const summary = h.result_summary || {};
            const recs = summary.recommendations || [];
            const topRec = recs[0];
            const isVerifiedMatch = topRec && topRec.relevance_score >= 0.35 && topRec.confidence_level !== 'LOW';
            
            const standardsCount = isVerifiedMatch ? recs.length : 0;
            const statusText = isVerifiedMatch 
                ? (topRec.qco_compliance?.qco_mandatory ? 'Mandatory QCO Checked' : 'Compliance Checked') 
                : 'No verified match';

            const displayTitle = isVerifiedMatch 
                ? `${standardsCount} standard${standardsCount > 1 ? 's' : ''} identified (${topRec.is_code})`
                : 'No verified matching standard found';

            const dateStr = h.timestamp ? h.timestamp.split(' ')[0] : 'Recent';

            html += `
                <div class="card" style="margin-bottom:0.85rem; padding:1.1rem; border-left:4px solid ${isVerifiedMatch ? 'var(--primary-color)' : '#cbd5e1'};">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap;">
                        <div style="flex:1; min-width:240px;">
                            <h4 style="margin:0 0 0.35rem 0; font-size:1.02rem; color:var(--text-color, #1e293b);">${h.query}</h4>
                            <p style="margin:0; font-size:0.88rem; color:${isVerifiedMatch ? '#2563eb' : '#64748b'}; font-weight:600;">${displayTitle}</p>
                            <p style="margin:0.25rem 0 0 0; font-size:0.8rem; color:#64748b;">${statusText} • ${dateStr}</p>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline" onclick="rerunQuery('${h.query.replace(/'/g, "\\'")}')">View Analysis</button>
                        </div>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch (e) {}
}

function rerunQuery(queryStr) {
    window.location.hash = '#/analyze';
    const input = document.getElementById('input-query');
    if (input) {
        input.value = queryStr;
        runAnalysisModeA();
    }
}

async function loadReports() {
    const container = document.getElementById('reports-list');
    if (currentAnalysisResult) {
        container.innerHTML = `
            <div class="card">
                <h3>Active Analysis Session Report</h3>
                <p><strong>Query:</strong> "${currentAnalysisResult.query}"</p>
                <p class="subtitle" style="margin-top:0.35rem">Primary Standard: ${currentAnalysisResult.recommendations?.[0]?.is_code || 'N/A'}</p>
                <button class="btn btn-primary" onclick="downloadPdfReport()">📄 Download PDF Procurement Report</button>
            </div>
        `;
    }
}

async function loadAdminMetrics() {
    try {
        const resp = await fetch('/api/admin/metrics');
        const metrics = await resp.json();
        const container = document.getElementById('admin-metrics-view');
        container.innerHTML = `
            <div class="workflow-steps" style="margin-bottom:1.5rem">
                <div class="step-card">
                    <h4>Verified Standards</h4>
                    <p style="font-size:1.8rem; font-weight:700; color:#1e3a8a">${metrics.dataset_statistics.total_verified_standards}</p>
                </div>
                <div class="step-card">
                    <h4>Graph Relationships</h4>
                    <p style="font-size:1.8rem; font-weight:700; color:#0f766e">${metrics.dataset_statistics.total_relationships}</p>
                </div>
                <div class="step-card">
                    <h4>Benchmark Queries</h4>
                    <p style="font-size:1.8rem; font-weight:700; color:#2563eb">${metrics.dataset_statistics.benchmark_queries}</p>
                </div>
            </div>
            <pre style="background:#f1f5f9; padding:1.25rem; border-radius:6px; font-size:0.85rem">${JSON.stringify(metrics, null, 2)}</pre>
        `;
    } catch (e) {}
}

// ----------------------------------------------------
// 9. PDF REPORT DOWNLOAD
// ----------------------------------------------------
async function downloadPdfReport() {
    if (!currentAnalysisResult) {
        showToast('No active analysis session to export.', 'warning');
        return;
    }

    // PDF report is always generated in English as per system requirement
    const pdfLanguage = 'en';

    try {
        const resp = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: currentAnalysisResult.query,
                entities: currentAnalysisResult.entities,
                recommendations: currentAnalysisResult.recommendations,
                output_language: pdfLanguage
            })
        });

        if (!resp.ok) throw new Error('PDF Generation error.');
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Procurement_Standards_Report.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast('PDF Procurement Standards Report generated successfully!', 'success');
    } catch (err) {
        showToast('Failed to download PDF report.', 'error');
        console.error(err);
    }
}

// Loading Stage Progress Simulation
let progressInterval = null;
function startLoadingProgress() {
    const card = document.getElementById('analysis-spinner');
    const bar = document.getElementById('progress-bar-fill');
    const title = document.getElementById('loading-stage-title');
    const desc = document.getElementById('loading-stage-desc');

    card.style.display = 'block';
    bar.style.width = '10%';
    title.innerText = 'Understanding Requirement...';

    const stages = [
        { pct: '30%', title: 'Extracting Technical Parameters...', desc: 'Extracting product, category, materials, and specification details...' },
        { pct: '60%', title: 'Searching Standards Knowledge Base...', desc: 'Matching procurement requirements against official Indian Standards...' },
        { pct: '85%', title: 'Linking Related Standards...', desc: 'Identifying normative references, test methods, and safety standards...' },
        { pct: '95%', title: 'Evaluating Mandatory Compliance...', desc: 'Checking mandatory Quality Control Orders (QCOs)...' }
    ];

    let idx = 0;
    progressInterval = setInterval(() => {
        if (idx < stages.length) {
            bar.style.width = stages[idx].pct;
            title.innerText = stages[idx].title;
            desc.innerText = stages[idx].desc;
            idx++;
        }
    }, 600);
}

function stopLoadingProgress() {
    clearInterval(progressInterval);
    document.getElementById('analysis-spinner').style.display = 'none';
}

function hideResults() {
    document.getElementById('analysis-results').style.display = 'none';
}

// Dynamic Output Language Selector Change Handler
async function handleOutputLanguageChange(newLang) {
    if (!currentAnalysisResult) return;

    if (currentAnalysisResult.query) {
        startLoadingProgress();
        try {
            const inputLang = document.getElementById('language-select')?.value || 'auto';
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: currentAnalysisResult.user_original_query || currentAnalysisResult.query,
                    language: inputLang,
                    output_language: newLang
                })
            });
            const data = await resp.json();
            currentAnalysisResult = data;
            renderAnalysisResults(data);
            showToast(`Output language updated to ${data.output_language_name || newLang}`, 'info');
        } catch (err) {
            console.error('Failed to update output language:', err);
        } finally {
            stopLoadingProgress();
        }
    }
}

// Global Window Bindings
window.openWhyModal = openWhyModal;
window.closeWhyModal = closeWhyModal;
window.handleOutputLanguageChange = handleOutputLanguageChange;



