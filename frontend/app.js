// Global State
let currentAnalysisResult = null;
let selectedFile = null;
let activeReviewTarget = null;
let recordedOfficerReviews = {};
let currentActiveLanguage = 'en';

// Current Authenticated User & RBAC State
let isLoggedIn = localStorage.getItem('standard_saarthi_logged_in') === 'true';
let currentUser = JSON.parse(localStorage.getItem('standard_saarthi_user')) || {
    username: 'officer@gem.gov.in',
    name: 'Er. Rajesh Kumar',
    role: 'officer',
    department: 'Procurement Cell, GeM',
    avatar: '👨‍💼'
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    updateUserUI();
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
    let rawRoute = hash.replace('#', '').trim();
    if (!rawRoute) rawRoute = '/';
    if (!rawRoute.startsWith('/')) rawRoute = '/' + rawRoute;

    // Extract base route name (e.g. /audit from /audit?foo=bar or /audit/)
    let routeName = rawRoute.split('?')[0].replace(/\/$/, '') || '/';
    let param = null;

    // Gate unauthenticated access: force login view on initial land or when not logged in
    if (!isLoggedIn && routeName !== '/login') {
        routeName = '/login';
        window.history.replaceState(null, '', '#/login');
    }

    if (rawRoute.startsWith('/standards/')) {
        routeName = '/standards/detail';
        param = decodeURIComponent(rawRoute.replace('/standards/', '').split('?')[0]);
    }

    // Hide all view panels
    document.querySelectorAll('.view-panel').forEach(panel => panel.classList.remove('active'));

    // Deactivate nav links
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    // If on login route
    if (routeName === '/login') {
        showView('view-login');
        updateUserUI();
        return;
    }

    // RBAC Security Route Protection
    if (routeName === '/admin' && (!currentUser || currentUser.role !== 'admin')) {
        showToast('Access Restricted: System Administrator privileges required for Diagnostics.', 'error');
        navigateTo('#/');
        return;
    }

    // Highlight active nav link based on current route
    const activeNav = document.querySelector(`.nav-link[data-route="${routeName}"]`) || 
                      document.querySelector(`.nav-link[data-route="/${routeName.split('/')[1]}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Handle view rendering
    if (routeName === '/' || routeName === '') {
        showView('view-home');
        loadHomeRecent();
    } else if (routeName === '/analyze') {
        showView('view-analyze');
        const urlParams = new URLSearchParams(window.location.hash.split('?')[1] || '');
        const modeParam = urlParams.get('mode');
        if (modeParam === 'c') {
            switchMode('mode-c');
        }
    } else if (routeName === '/standards') {
        showView('view-standards');
        loadCatalog();
    } else if (routeName === '/standards/detail') {
        showView('view-standard-detail');
        if (param) loadStandardDetailsPage(param);
    } else if (routeName === '/regulatory') {
        showView('view-regulatory');
        loadQCO();
    } else if (routeName === '/audit') {
        showView('view-audit');
        loadAuditTrail();
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
        loadHomeRecent();
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
        dropzone.classList.add('drag-active');
        dropzone.style.borderColor = '#2563eb';
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-active');
        dropzone.style.borderColor = '#93c5fd';
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-active');
        dropzone.style.borderColor = '#93c5fd';
        if (e.dataTransfer.files.length > 0) handleSelectedFile(e.dataTransfer.files[0]);
    });
}

function handleSelectedFile(file) {
    selectedFile = file;
    const nameLabel = document.getElementById('file-selected-name');
    const actionBox = document.getElementById('upload-action-box');
    const uploadBtn = document.getElementById('btn-upload');

    if (nameLabel) {
        nameLabel.innerHTML = `
            <div class="file-info-card">
                <div class="file-info-details">
                    <span class="file-info-icon">📄</span>
                    <div>
                        <div style="font-weight:700; color:#1e3a8a; font-size:0.95rem;">${file.name}</div>
                        <div style="font-size:0.8rem; color:#64748b;">${(file.size / 1024).toFixed(1)} KB • Ready for extraction</div>
                    </div>
                </div>
                <div>
                    <button type="button" class="btn btn-sm btn-outline" onclick="event.stopPropagation(); document.getElementById('tender-file-input').click()">Change File</button>
                </div>
            </div>
        `;
    }
    if (actionBox) actionBox.style.display = 'block';
    if (uploadBtn) uploadBtn.style.display = 'inline-block';
    showToast(`File selected: ${file.name}`, 'info');
}

// ----------------------------------------------------
// 4. MODE A: Product Description Analysis
// ----------------------------------------------------
async function runAnalysisModeA() {
    const query = document.getElementById('input-query').value.trim();
    const lang = document.getElementById('language-select').value;

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
            body: JSON.stringify({ description: query, language: lang })
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
    const specData = {
        product_name: document.getElementById('spec-name').value.trim(),
        product_category: document.getElementById('spec-category').value.trim(),
        material: document.getElementById('spec-material').value.trim(),
        voltage: document.getElementById('spec-voltage').value.trim(),
        dimensions: document.getElementById('spec-dimensions').value.trim(),
        grade: document.getElementById('spec-grade').value.trim(),
        application: document.getElementById('spec-application').value.trim(),
        safety_requirements: document.getElementById('spec-safety').value.trim()
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
        const fileInput = document.getElementById('tender-file-input');
        if (fileInput && fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
        }
    }
    if (!selectedFile) {
        showToast('Please select a PDF, DOCX, or TXT file first.', 'warning');
        return;
    }

    startLoadingProgress();
    const formData = new FormData();
    formData.append('file', selectedFile);

    const lang = document.getElementById('language-select')?.value || 'auto';

    try {
        const resp = await fetch(`/api/analyze/document?language=${encodeURIComponent(lang)}`, {
            method: 'POST',
            body: formData
        });
        const data = await resp.json();
        if (!resp.ok) {
            throw new Error(data.detail || data.error || 'Failed to parse tender document.');
        }
        renderTenderMatrix(data);
        showToast(`Document parsed into ${data.requirement_count} requirement items!`, 'success');
    } catch (err) {
        showToast(`Tender document parsing failed: ${err.message}`, 'error');
        console.error(err);
    } finally {
        stopLoadingProgress();
    }
}

// ----------------------------------------------------
// UI MULTILINGUAL DICTIONARY (10 INDIAN LANGUAGES + EN)
// ----------------------------------------------------
const UI_I18N = {
    en: {
        recommended_heading: "Recommended Primary Standards",
        candidate_heading: "Closest Matching Candidate Standards (Officer Review Required)",
        req_understanding: "Requirement Understanding",
        product: "Product",
        category: "Category",
        application: "Application",
        materials: "Materials",
        container: "Container",
        volume: "Volume",
        general_item: "General procurement item.",
        mandatory_qco: "MANDATORY QCO",
        recommended: "RECOMMENDED",
        closest_candidate: "CLOSEST CANDIDATE",
        inspect_details: "Inspect Standard Details",
        why_standard: "Why This Standard?",
        officer_review: "Officer Review & Log Decision",
        edition: "EDITION",
        relevance: "Relevance",
        no_match: "No verified Indian Standard matching query found in database.",
        download_report: "Download Official PDF Report",
        superseded_warn: "WARNING: This standard is SUPERSEDED by",
        officer_accepted: "ACCEPTED BY OFFICER",
        officer_overridden: "OVERRIDDEN TO",
        parsed_tender_file: "Parsed Tender File",
        requirements_extracted: "Requirements Extracted",
        analyze_item: "Analyze Standards for Item",
        document_language: "Document Language",
        item: "Item",
        needs_clarification: "Needs Clarification",
        confidence_gate: "CONFIDENCE GATE ACTIVATED — WRONG-CITATION RISK MITIGATION"
    },
    ta: {
        recommended_heading: "பரிந்துரைக்கப்பட்ட முதன்மை தரநிலைகள்",
        candidate_heading: "நெருங்கிய பொருத்தம் கொண்ட தரநிலைகள் (அதிகாரி மதிப்பாய்வு தேவை)",
        req_understanding: "கொள்முதல் தேவை புரிதல்",
        product: "பொருள்",
        category: "வகை",
        application: "பயன்பாடு",
        materials: "பொருட்கள்",
        container: "கொள்கலன்",
        volume: "அளவு",
        general_item: "பொது கொள்முதல் பொருள்.",
        mandatory_qco: "கட்டாய QCO",
        recommended: "பரிந்துரைக்கப்பட்டது",
        closest_candidate: "நெருங்கிய வேட்பாளர்",
        inspect_details: "விவரங்களை ஆய்வு செய்",
        why_standard: "இந்த தரநிலை ஏன்?",
        officer_review: "அதிகாரி மதிப்பாய்வு & முடிவு பதிவு",
        edition: "பதிப்பு",
        relevance: "பொருத்தம்",
        no_match: "தரவுத்தளத்தில் பொருந்தக்கூடிய சரிபார்க்கப்பட்ட இந்திய தரநிலை எதுவும் கிடைக்கவில்லை.",
        download_report: "அதிகாரப்பூர்வ PDF அறிக்கையைப் பதிவிறக்கு",
        superseded_warn: "எச்சரிக்கை: இந்த தரநிலை புதிய தரநிலையால் மாற்றப்பட்டது",
        officer_accepted: "அதிகாரியால் ஏற்றுக்கொள்ளப்பட்டது",
        officer_overridden: "மாற்றப்பட்டது",
        parsed_tender_file: "பகுப்பாய்வு செய்யப்பட்ட டெண்டர் ஆவணம்",
        requirements_extracted: "பிரித்தெடுக்கப்பட்ட தேவைகள்",
        analyze_item: "உருப்படிக்கான தரநிலைகளை பகுப்பாய்வு செய்",
        document_language: "ஆவண மொழி",
        item: "உருப்படி",
        needs_clarification: "விளக்கம் தேவை",
        confidence_gate: "நம்பகத்தன்மை வாயில் இயக்கப்பட்டது — தவறான மேற்கோள் தடுப்பு"
    },
    te: {
        recommended_heading: "సిఫార్సు చేయబడిన ప్రాథమిక ప్రమాణాలు",
        candidate_heading: "సమీప సరిపోలే ప్రమాణాలు (అధికారి సమీక్ష అవసరం)",
        req_understanding: "సేకరణ అవసరాల అవగాహన",
        product: "ఉత్పత్తి",
        category: "వర్గం",
        application: "అప్లికేషన్",
        materials: "పదార్థాలు",
        container: "కంటైనర్",
        volume: "పరిమాణం",
        general_item: "సాధారణ సేకరణ అంశం.",
        mandatory_qco: "తప్పనిసరి QCO",
        recommended: "సిఫార్సు చేయబడింది",
        closest_candidate: "సమీప అభ్యర్థి",
        inspect_details: "ప్రమాణ వివరాలను పరిశీలించండి",
        why_standard: "ఈ ప్రమాణం ఎందుకు?",
        officer_review: "అధికారి సమీక్ష & నిర్ణయం నమోదు",
        edition: "ఎడిషన్",
        relevance: "సరిపోలిక",
        no_match: "డేటాబేస్‌లో సరిపోలే ధృవీకరించబడిన భారతీయ ప్రమాణం కనుగొనబడలేదు.",
        download_report: "అధికారిక PDF నివేదికను డౌన్‌లోడ్ చేయండి",
        superseded_warn: "హెచ్చరిక: ఈ ప్రమాణం ద్వారా భర్తీ చేయబడింది",
        officer_accepted: "అధికారి ఆమోదించారు",
        officer_overridden: "ఓవర్‌రైడ్ చేయబడింది",
        parsed_tender_file: "విశ్లేషించబడిన టెండర్ ఫైల్",
        requirements_extracted: "సేకరించిన అవసరాలు",
        analyze_item: "అంశం కోసం ప్రమాణాలను విశ్లేషించండి",
        document_language: "పత్రం భాష",
        item: "అంశం",
        needs_clarification: "స్పష్టత అవసరం",
        confidence_gate: "విశ్వసనీయత గేట్ సక్రియం చేయబడింది"
    },
    hi: {
        recommended_heading: "अनुशंसित प्राथमिक मानक",
        candidate_heading: "निकटतम उम्मीदवार मानक (अधिकारी समीक्षा आवश्यक)",
        req_understanding: "खरीद आवश्यकता विश्लेषण",
        product: "उत्पाद",
        category: "श्रेणी",
        application: "अनुप्रयोग",
        materials: "सामग्री",
        container: "पात्र / कंटेनर",
        volume: "मात्रा",
        general_item: "सामान्य खरीद वस्तु।",
        mandatory_qco: "अनिवार्य QCO",
        recommended: "अनुशंसित",
        closest_candidate: "निकटतम उम्मीदवार",
        inspect_details: "मानक विवरण का निरीक्षण करें",
        why_standard: "यह मानक क्यों?",
        officer_review: "अधिकारी समीक्षा एवं निर्णय दर्ज करें",
        edition: "संस्करण",
        relevance: "प्रासंगिकता",
        no_match: "डेटाबेस में कोई सत्यापित भारतीय मानक नहीं मिला।",
        download_report: "आधिकारिक पीडीएफ रिपोर्ट डाउनलोड करें",
        superseded_warn: "चेतावनी: यह मानक प्रतिस्थापित किया गया है",
        officer_accepted: "अधिकारी द्वारा स्वीकृत",
        officer_overridden: "अधिकारी द्वारा संशोधित",
        parsed_tender_file: "पार्स की गई निविदा फाइल",
        requirements_extracted: "निकाली गई आवश्यकताएं",
        analyze_item: "मद के लिए मानक विश्लेषण करें",
        document_language: "दस्तावेज़ की भाषा",
        item: "मद",
        needs_clarification: "स्पष्टीकरण आवश्यक",
        confidence_gate: "विश्वास द्वार सक्रिय — गलत उद्धरण जोखिम न्यूनीकरण"
    },
    bn: {
        recommended_heading: "সুপারিশকৃত প্রাথমিক মানদণ্ড",
        candidate_heading: "নিকটতম প্রার্থী মানদণ্ড (কর্মকর্তা পর্যালোচনা আবশ্যক)",
        req_understanding: "ক্রয় প্রয়োজনীয়তার বিশ্লেষণ",
        product: "পণ্য",
        category: "বিভাগ",
        application: "প্রয়োগ",
        materials: "উপাদান",
        container: "পাত্র",
        volume: "আয়তন",
        general_item: "সাধারণ ক্রয় আইটেম।",
        mandatory_qco: "বাধ্যতামূলক QCO",
        recommended: "সুপারিশকৃত",
        closest_candidate: "নিকটতম প্রার্থী",
        inspect_details: "মানদণ্ডের বিবরণ দেখুন",
        why_standard: "এই মানদণ্ড কেন?",
        officer_review: "কর্মকর্তা পর্যালোচনা ও সিদ্ধান্ত সংরক্ষণ",
        edition: "সংস্করণ",
        relevance: "প্রাসঙ্গিকতা",
        no_match: "ডাটাবেসে কোনো যাচাইকৃত ভারতীয় মানদণ্ড পাওয়া যায়নি।",
        download_report: "অফিসিয়াল পিডিএফ রিপোর্ট ডাউনলোড করুন",
        superseded_warn: "সতর্কতা: এই মানদণ্ডটি প্রতিস্থাপিত হয়েছে",
        officer_accepted: "কর্মকর্তা দ্বারা গৃহীত",
        officer_overridden: "পরিবর্তিত",
        parsed_tender_file: "পার্স করা দরপত্র নথি",
        requirements_extracted: "উত্তোলিত প্রয়োজনীয়তা",
        analyze_item: "আইটেমের জন্য মানদণ্ড বিশ্লেষণ করুন",
        document_language: "নথির ভাষা",
        item: "আইটেম",
        needs_clarification: "স্পষ্টীকরণ প্রয়োজন",
        confidence_gate: "কনফিডেন্স গেট সক্রিয় — ভুল উদ্ধৃতি প্রতিরোধ"
    },
    gu: {
        recommended_heading: "ભલામણ કરેલ પ્રાથમિક ધોરણો",
        candidate_heading: "સૌથી નજીકના ઉમેદવાર ધોરણો (અધિકારી સમીક્ષા જરૂરી)",
        req_understanding: "ખરીદી જરૂરિયાતની સમજ",
        product: "ઉત્પાદન",
        category: "શ્રેણી",
        application: "ઉપયોગ",
        materials: "સામગ્રી",
        container: "કન્ટેનર",
        volume: "કદ / વોલ્યુમ",
        general_item: "સામાન્ય ખરીદી વસ્તુ.",
        mandatory_qco: "ફરજિયાત QCO",
        recommended: "ભલામણ કરેલ",
        closest_candidate: "નજીકનો ઉમેદવાર",
        inspect_details: "ધોરણની વિગતો તપાસો",
        why_standard: "આ ધોરણ શા માટે?",
        officer_review: "અધિકારી સમીક્ષા અને નિર્ણય લોગ કરો",
        edition: "આવૃત્તિ",
        relevance: "સુસંગતતા",
        no_match: "ડેટાબેઝમાં કોઈ ચકાસાયેલ ભારતીય ધોરણ મળ્યું નથી.",
        download_report: "સત્તાવાર PDF રિપોર્ટ ડાઉનલોડ કરો",
        superseded_warn: "ચેતવણી: આ ધોરણ દ્વારા બદલવામાં આવ્યું છે",
        officer_accepted: "અધિકારી દ્વારા સ્વીકૃત",
        officer_overridden: "સુધારેલ",
        parsed_tender_file: "પાર્સ કરેલ ટેન્ડર ફાઇલ",
        requirements_extracted: "તારવેલી જરૂરિયાતો",
        analyze_item: "વસ્તુ માટે ધોરણોનું વિશ્લેષણ કરો",
        document_language: "દસ્તાવેજની ભાષા",
        item: "વસ્તુ",
        needs_clarification: "સ્પષ્ટતા જરૂરી",
        confidence_gate: "વિશ્વાસ ગેટ સક્રિય — ખોટા સંદર્ભ નિવારણ"
    },
    mr: {
        recommended_heading: "शिफारस केलेले प्राथमिक मानके",
        candidate_heading: "जवळचे संभाव्य मानके (अधिकारी पुनरावलोकन आवश्यक)",
        req_understanding: "खरेदी आवश्यकतेचे आकलन",
        product: "उत्पादन",
        category: "श्रेणी",
        application: "उपयोग",
        materials: "साहित्य",
        container: "पात्र",
        volume: "प्रमाण",
        general_item: "सामान्य खरेदी वस्तू.",
        mandatory_qco: "अनिवार्य QCO",
        recommended: "शिफारस केलेले",
        closest_candidate: "जवळचा उमेदवार",
        inspect_details: "मानक तपशील तपासा",
        why_standard: "हे मानक का?",
        officer_review: "अधिकारी पुनरावलोकन आणि निर्णय नोंदवा",
        edition: "आवृत्ती",
        relevance: "सुसंगतता",
        no_match: "डेटाबेसमध्ये कोणतेही पडताळलेले भारतीय मानक आढळले नाही.",
        download_report: "अधिकृत PDF अहवाल डाउनलोड करा",
        superseded_warn: "चेतावणी: हे मानक बदलले गेले आहे",
        officer_accepted: "अधिकाऱ्याने स्वीकारले",
        officer_overridden: "बदललेले",
        parsed_tender_file: "विश्लेषित निविदा फाइल",
        requirements_extracted: "काढून घेतलेल्या आवश्यकता",
        analyze_item: "बाबीसाठी मानकांचे विश्लेषण करा",
        document_language: "दस्तऐवजाची भाषा",
        item: "बाब / आयटम",
        needs_clarification: "स्पष्टीकरण आवश्यक",
        confidence_gate: "कॉन्फिडन्स गेट सक्रिय"
    },
    kn: {
        recommended_heading: "ಶಿಫಾರಸು ಮಾಡಲಾದ ಪ್ರಾಥಮಿಕ ಮಾನದಂಡಗಳು",
        candidate_heading: "ಹತ್ತಿರದ ಅಭ್ಯರ್ಥಿ ಮಾನದಂಡಗಳು (ಅಧಿಕಾರಿ ಪರಿಶೀಲನೆ ಅಗತ್ಯವಿದೆ)",
        req_understanding: "ಖರೀದಿ ಅಗತ್ಯತೆಯ ತಿಳುವಳಿಕೆ",
        product: "ಉತ್ಪನ್ನ",
        category: "ವರ್ಗ",
        application: "ಅನ್ವಯ",
        materials: "ವಸ್ತುಗಳು",
        container: "ಪಾತ್ರೆ",
        volume: "ಗಾತ್ರ",
        general_item: "ಸಾಮಾನ್ಯ ಖರೀದಿ ವಸ್ತು.",
        mandatory_qco: "ಕಡ್ಡಾಯ QCO",
        recommended: "ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ",
        closest_candidate: "ಹತ್ತಿರದ ಅಭ್ಯರ್ಥಿ",
        inspect_details: "ಮಾನದಂಡದ ವಿವರಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ",
        why_standard: "ಈ ಮಾನದಂಡ ಏಕೆ?",
        officer_review: "ಅಧಿಕಾರಿ ಪರಿಶೀಲನೆ ಮತ್ತು ನಿರ್ಧಾರ ದಾಖಲಿಸಿ",
        edition: "ಆವೃತ್ತಿ",
        relevance: "ಹೊಂದಾಣಿಕೆ",
        no_match: "ಡೇಟಾಬೇಸ್‌ನಲ್ಲಿ ಯಾವುದೇ ಪರಿಶೀಲಿಸಿದ ಭಾರತೀಯ ಮಾನದಂಡ ಕಂಡುಬಂದಿಲ್ಲ.",
        download_report: "ಅಧಿಕೃತ PDF ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
        superseded_warn: "ಎಚ್ಚರಿಕೆ: ಈ ಮಾನದಂಡವನ್ನು ಬದಲಾಯಿಸಲಾಗಿದೆ",
        officer_accepted: "ಅಧಿಕಾರಿಯಿಂದ ಅಂಗೀಕರಿಸಲಾಗಿದೆ",
        officer_overridden: "ಬದಲಾಯಿಸಲಾಗಿದೆ",
        parsed_tender_file: "ವಿಶ್ಲೇಷಿಸಿದ ಟೆಂಡರ್ ಫೈಲ್",
        requirements_extracted: "ತೆಗೆದ ಅಗತ್ಯತೆಗಳು",
        analyze_item: "ಐಟಂಗೆ ಮಾನದಂಡಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಿ",
        document_language: "ದಾಖಲೆಯ ಭಾಷೆ",
        item: "ಐಟಂ",
        needs_clarification: "ಸ್ಪಷ್ಟೀಕರಣ ಅಗತ್ಯವಿದೆ",
        confidence_gate: "ವಿಶ್ವಾಸಾರ್ಹತೆ ಗೇಟ್ ಸಕ್ರಿಯಗೊಂಡಿದೆ"
    },
    ml: {
        recommended_heading: "ശുപാർശ ചെയ്യുന്ന പ്രാഥമിക മാനദണ്ഡങ്ങൾ",
        candidate_heading: "ഏറ്റവും അടുത്തുള്ള മാനദണ്ഡങ്ങൾ (ഉദ്യോഗസ്ഥ പരിശോധന ആവശ്യമാണ്)",
        req_understanding: "സംഭരണ ആവശ്യകത മനസ്സിലാക്കൽ",
        product: "ഉൽപ്പന്നം",
        category: "വിഭാഗം",
        application: "ഉപയോഗം",
        materials: "മെറ്റീരിയലുകൾ",
        container: "കണ്ടെയ്നർ",
        volume: "വ്യാപ്തം",
        general_item: "സാധാരണ സംഭരണ ഇനം.",
        mandatory_qco: "നിർബന്ധിത QCO",
        recommended: "ശുപാർശ ചെയ്തത്",
        closest_candidate: "ഏറ്റവും അടുത്തുള്ള കാൻഡിഡേറ്റ്",
        inspect_details: "മാനദണ്ഡ വിശദാംശങ്ങൾ പരിശോധിക്കുക",
        why_standard: "എന്തുകൊണ്ട് ഈ മാനദണ്ഡം?",
        officer_review: "ഉദ്യോഗസ്ഥ പരിശോധനയും തീരുമാനവും രേഖപ്പെടുത്തുക",
        edition: "പതിപ്പ്",
        relevance: "പൊരുത്തം",
        no_match: "ഡാറ്റാബേസിൽ പരിശോധിച്ച ഇന്ത്യൻ മാനദണ്ഡങ്ങളൊന്നും കണ്ടെത്തിയില്ല.",
        download_report: "ഔദ്യോഗിക PDF റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യുക",
        superseded_warn: "മുന്നറിയിപ്പ്: ഈ മാനദണ്ഡം മാറ്റപ്പെട്ടു",
        officer_accepted: "ഉദ്യോഗസ്ഥൻ അംഗീകരിച്ചു",
        officer_overridden: "തിരുത്തപ്പെട്ടു",
        parsed_tender_file: "പാഴ്‌സ് ചെയ്ത ടെൻഡർ ഫയൽ",
        requirements_extracted: "വേർതിരിച്ചെടുത്ത ആവശ്യകതകൾ",
        analyze_item: "ഇനത്തിനായുള്ള മാനദണ്ഡങ്ങൾ വിശകലനം ചെയ്യുക",
        document_language: "രേഖയുടെ ഭാഷ",
        item: "ഇനം",
        needs_clarification: "വ്യക്തത ആവശ്യമാണ്",
        confidence_gate: "വിശ്വാസ്യത ഗേറ്റ് സജീവമാക്കി"
    },
    pa: {
        recommended_heading: "ਸਿਫ਼ਾਰਿਸ਼ ਕੀਤੇ ਪ੍ਰਾਇਮਰੀ ਮਾਪਦੰਡ",
        candidate_heading: "ਸਭ ਤੋਂ ਨਜ਼ਦੀਕੀ ਉਮੀਦਵਾਰ ਮਾਪਦੰਡ (ਅਧਿਕਾਰੀ ਸਮੀਖਿਆ ਲੋੜੀਂਦੀ)",
        req_understanding: "ਖਰੀਦ ਲੋੜਾਂ ਦੀ ਸਮਝ",
        product: "ਉਤਪਾਦ",
        category: "ਸ਼੍ਰੇਣੀ",
        application: "ਵਰਤੋਂ",
        materials: "ਸਮੱਗਰੀ",
        container: "ਕੰਟੇਨਰ",
        volume: "ਮਾਤਰਾ",
        general_item: "ਆਮ ਖਰੀਦ ਵਸਤੂ।",
        mandatory_qco: "ਲਾਜ਼ਮੀ QCO",
        recommended: "ਸਿਫਾਰਿਸ਼ ਕੀਤੀ",
        closest_candidate: "ਨਜ਼ਦੀਕੀ ਉਮੀਦਵਾਰ",
        inspect_details: "ਮਿਆਰੀ ਵੇਰਵਿਆਂ ਦੀ ਜਾਂਚ ਕਰੋ",
        why_standard: "ਇਹ ਮਿਆਰ ਕਿਉਂ?",
        officer_review: "ਅਧਿਕਾਰੀ ਦੀ ਸਮੀਖਿਆ ਅਤੇ ਫੈਸਲਾ ਦਰਜ ਕਰੋ",
        edition: "ਐਡੀਸ਼ਨ",
        relevance: "ਸਾਰਥਕਤਾ",
        no_match: "ਡੇਟਾਬੇਸ ਵਿੱਚ ਕੋਈ ਪ੍ਰਮਾਣਿਤ ਭਾਰਤੀ ਮਿਆਰ ਨਹੀਂ ਮਿਲਿਆ।",
        download_report: "ਅਧਿਕਾਰਤ PDF ਰਿਪੋਰਟ ਡਾਊਨਲੋਡ ਕਰੋ",
        superseded_warn: "ਚੇਤਾਵਨੀ: ਇਹ ਮਿਆਰ ਬਦਲ ਦਿੱਤਾ ਗਿਆ ਹੈ",
        officer_accepted: "ਅਧਿਕਾਰੀ ਦੁਆਰਾ ਸਵੀਕਾਰ ਕੀਤਾ ਗਿਆ",
        officer_overridden: "ਸੋਧਿਆ ਗਿਆ",
        parsed_tender_file: "ਪਾਰਸ ਕੀਤੀ ਟੈਂਡਰ ਫਾਈਲ",
        requirements_extracted: "ਕੱਢੀਆਂ ਗਈਆਂ ਲੋੜਾਂ",
        analyze_item: "ਆਈਟਮ ਲਈ ਮਾਪਦੰਡਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        document_language: "ਦਸਤਾਵੇਜ਼ ਦੀ ਭਾਸ਼ਾ",
        item: "ਆਈਟਮ",
        needs_clarification: "ਸਪੱਸ਼ਟੀਕਰਨ ਦੀ ਲੋੜ ਹੈ",
        confidence_gate: "ਭਰੋਸੇਯੋਗਤਾ ਗੇਟ ਕਿਰਿਆਸ਼ੀਲ"
    },
    or: {
        recommended_heading: "ସୁପାରିଶ କରାଯାଇଥିବା ପ୍ରାଥମିକ ମାନକ",
        candidate_heading: "ନିକଟତମ ପ୍ରାର୍ଥୀ ମାନକ (ଅଧିକାରୀ ସମୀକ୍ଷା ଆବଶ୍ୟକ)",
        req_understanding: "କ୍ରୟ ଆବଶ୍ୟକତା ବିଶ୍ଳେଷଣ",
        product: "ଉତ୍ପାଦ",
        category: "ଶ୍ରେଣୀ",
        application: "ପ୍ରୟୋଗ",
        materials: "ସାମଗ୍ରୀ",
        container: "ପାତ୍ର",
        volume: "ପରିମାଣ",
        general_item: "ସାଧାରଣ କ୍ରୟ ସାମଗ୍ରୀ।",
        mandatory_qco: "ବାଧ୍ୟତାମୂଳକ QCO",
        recommended: "ସୁପାରିଶ କରାଯାଇଛି",
        closest_candidate: "ନିକଟତମ ପ୍ରାର୍ଥୀ",
        inspect_details: "ମାନକ ବିବରଣୀ ଯାଞ୍ଚ କରନ୍ତୁ",
        why_standard: "ଏହି ମାନକ କାହିଁକି?",
        officer_review: "ଅଧିକାରୀ ସମୀକ୍ଷା ଏବଂ ନିଷ୍ପତ୍ତି ଲଗ୍ କରନ୍ତୁ",
        edition: "ସଂସ୍କରଣ",
        relevance: "ପ୍ରାସଙ୍ଗିକତା",
        no_match: "ଡାଟାବେସରେ କୌଣସି ଯାଞ୍ଚ ହୋଇଥିବା ଭାରତୀୟ ମାନକ ମିଳିଲା ନାହିଁ।",
        download_report: "ସରକାରୀ PDF ରିପୋର୍ଟ ଡାଉନଲୋଡ୍ କରନ୍ତୁ",
        superseded_warn: "ଚେତାବନୀ: ଏହି ମାନକ ପ୍ରତିସ୍ଥାପିତ ହୋଇଛି",
        officer_accepted: "ଅଧିକାରୀଙ୍କ ଦ୍ୱାରା ଗ୍ରହଣ କରାଯାଇଛି",
        officer_overridden: "ପରିବର୍ତ୍ତିତ",
        parsed_tender_file: "ପାର୍ସ ହୋଇଥିବା ଟେଣ୍ଡର ଫାଇଲ୍",
        requirements_extracted: "ବାହାର କରାଯାଇଥିବା ଆବଶ୍ୟକତା",
        analyze_item: "ଆଇଟମ୍ ପାଇଁ ମାନକ ବିଶ୍ଳେଷଣ କରନ୍ତୁ",
        document_language: "ଦଲିଲ ଭାଷା",
        item: "ଆଇଟମ୍",
        needs_clarification: "ସ୍ପଷ୍ଟୀକରଣ ଆବଶ୍ୟକ",
        confidence_gate: "ବିଶ୍ୱାସ ଗେଟ୍ ସକ୍ରିୟ"
    }
};

function localizeCategory(cat, lang) {
    if (!cat) return '';
    const l = lang || 'en';
    const t = (k) => (UI_I18N[l] && UI_I18N[l][k]) || UI_I18N['en'][l] || k;
    const lower = String(cat).toLowerCase();
    if (lower.includes('food') || lower.includes('water')) return (UI_I18N[l] && UI_I18N[l].cat_food_water) || 'Food & Water';
    if (lower.includes('electric') || lower.includes('cable') || lower.includes('wire')) return (UI_I18N[l] && UI_I18N[l].cat_electrical) || 'Electrical';
    if (lower.includes('civil') || lower.includes('cement') || lower.includes('concrete') || lower.includes('construction')) return (UI_I18N[l] && UI_I18N[l].cat_civil) || 'Civil / Construction';
    return (UI_I18N[l] && UI_I18N[l].cat_general) || 'General Procurement';
}

function renderTenderMatrix(parsedDoc) {
    navigateTo('#/tenders');
    const container = document.getElementById('tender-requirements-view');

    if (parsedDoc.status !== 'success') {
        container.innerHTML = `<p class="error-text">Extraction failed: ${parsedDoc.error || 'Unknown error'}</p>`;
        return;
    }

    const docLang = parsedDoc.detected_language || 'en';
    currentActiveLanguage = docLang;
    const t = (k) => (UI_I18N[docLang] && UI_I18N[docLang][k]) || UI_I18N['en'][k] || k;

    let html = `
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:1rem; border-bottom:1px solid #e2e8f0; padding-bottom:0.75rem;">
            <div>
                <h3 style="margin:0 0 0.25rem 0;">${t('parsed_tender_file')}: ${parsedDoc.filename} (${parsedDoc.requirement_count} ${t('requirements_extracted')})</h3>
                <span class="badge-rec">✓ ${t('document_language')}: <strong>${parsedDoc.language_name || docLang.toUpperCase()}</strong></span>
            </div>
            <button class="btn btn-sm btn-outline" onclick="navigateTo('#/analyze?mode=c')">Upload Another Document</button>
        </div>
    `;

    html += `<div class="req-matrix-list" style="margin-top:1rem">`;

    parsedDoc.extracted_requirements.forEach((req, idx) => {
        const catName = localizeCategory(req.category_hint, docLang);
        html += `
            <div class="card req-item" style="margin-bottom:1rem; border-left:4px solid var(--primary-color);">
                <div class="rec-header">
                    <strong>${t('item')} ${idx + 1} (${req.req_id})</strong> <span class="chip">${catName}</span>
                </div>
                <p class="rec-scope" style="font-size:0.95rem; line-height:1.5; margin:0.6rem 0;">${req.text}</p>
                <div style="margin-top:0.6rem;">
                    <button class="btn btn-sm btn-primary" onclick="analyzeTenderItem('${encodeURIComponent(req.text)}', '${docLang}')">🔍 ${t('analyze_item')} ${idx + 1}</button>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    container.innerHTML = html;
}

function analyzeTenderItem(encodedText, docLang = 'auto') {
    const text = decodeURIComponent(encodedText);
    navigateTo('#/analyze');
    switchMode('mode-a');
    const input = document.getElementById('input-query');
    if (input) input.value = text;
    if (docLang && docLang !== 'auto') {
        const langSelect = document.getElementById('language-select');
        if (langSelect) langSelect.value = docLang;
    }
    runAnalysisModeA();
}

// ----------------------------------------------------
// 7. RENDER ANALYSIS RESULTS & DRAWERS
// ----------------------------------------------------
function renderAnalysisResults(data) {
    const container = document.getElementById('analysis-results');
    container.style.display = 'block';

    // Multilingual context: detect language from response or selector (prevent 'auto' fallback)
    let detectedLang = 'en';
    if (data.multilingual_info && data.multilingual_info.detected_language && data.multilingual_info.detected_language !== 'auto') {
        detectedLang = data.multilingual_info.detected_language;
    } else if (document.getElementById('language-select') && document.getElementById('language-select').value && document.getElementById('language-select').value !== 'auto') {
        detectedLang = document.getElementById('language-select').value;
    }
    const lang = detectedLang || 'en';
    currentActiveLanguage = lang;
    const isIndic = (lang !== 'en');
    const t = (k) => (UI_I18N[lang] && UI_I18N[lang][k]) || UI_I18N['en'][k] || k;

    // Automatically synchronize the dropdown in the UI if detected
    const langSelect = document.getElementById('language-select');
    if (langSelect && detectedLang && detectedLang !== 'auto' && detectedLang !== 'en') {
        langSelect.value = detectedLang;
    }

    // Status Banner
    const banner = document.getElementById('status-banner');
    if (data.status === 'needs_clarification') {
        banner.className = 'status-banner needs_clarification';
        banner.style.display = 'block';
        const msg = data.clarification_prompt_localized || data.message_localized || data.message;
        banner.innerHTML = `<strong>${t('needs_clarification')}:</strong> ${msg} (${(data.missing_fields || []).join(', ')})`;
    } else if (data.status === 'out_of_domain') {
        banner.className = 'status-banner out_of_domain';
        banner.style.display = 'block';
        banner.innerHTML = `<strong>Scope Restriction:</strong> ${data.message_localized || data.message}`;
    } else if (data.status === 'abstain' || data.confidence_gated) {
        banner.className = 'status-banner abstain';
        banner.style.display = 'block';
        const localizedMsg = data.message_localized
            ? `<div><strong>${data.message_localized}</strong></div><div style="font-size:0.84rem; color:#475569; margin-top:3px;">${data.message}</div>`
            : (data.message || 'System is not confident enough to force a single primary recommendation. Displaying closest candidates for procurement officer evaluation to prevent wrong-citation risk.');
        banner.innerHTML = `<strong>${t('confidence_gate')}:</strong> ${localizedMsg}`;
    } else {
        banner.style.display = 'none';
    }

    // Multilingual Notice
    const mlNotice = document.getElementById('multilingual-notice');
    if (data.multilingual_info && data.multilingual_info.is_translated) {
        mlNotice.style.display = 'block';
        mlNotice.innerHTML = `<strong>${t('document_language')}:</strong> ${data.multilingual_info.language_name} | <em>"${data.multilingual_info.original_text}"</em> → English: <em>"${data.multilingual_info.normalized_english}"</em>`;
    } else {
        mlNotice.style.display = 'none';
    }

    // Localize Section Header and Download Button
    const understandingHeading = document.getElementById('understanding-heading');
    if (understandingHeading) {
        understandingHeading.innerText = t('req_understanding');
    }

    const downloadPdfBtn = document.getElementById('btn-download-pdf');
    if (downloadPdfBtn) {
        downloadPdfBtn.innerText = t('download_report');
    }

    // Entity Chips (use localized entities if available)
    const chipContainer = document.getElementById('entity-chips');
    const rawEntities = data.entities || {};
    const locEntities = (isIndic && data.entities_localized) ? data.entities_localized : {};
    const entities = { ...rawEntities, ...locEntities };
    let chipsHtml = '';
    if (entities.product) chipsHtml += `<span class="chip">${t('product')}: ${entities.product}</span>`;
    if (entities.category) chipsHtml += `<span class="chip">${t('category')}: ${localizeCategory(entities.category, lang)}</span>`;
    if (entities.container) chipsHtml += `<span class="chip">${t('container')}: ${entities.container}</span>`;
    if (entities.materials && entities.materials.length) {
        const matStr = Array.isArray(entities.materials) ? entities.materials.join(', ') : entities.materials;
        chipsHtml += `<span class="chip">${t('materials')}: ${matStr}</span>`;
    }
    if (entities.application) chipsHtml += `<span class="chip">${t('application')}: ${entities.application}</span>`;
    if (entities.volume) chipsHtml += `<span class="chip">${t('volume')}: ${entities.volume}</span>`;
    chipContainer.innerHTML = chipsHtml || `<p class="text-muted">${t('general_item')}</p>`;

    // Dynamic Heading (Recommended vs Closest Candidates)
    const headingElem = document.getElementById('recommendations-heading');
    const isAbstained = (data.status === 'abstain' || data.confidence_gated);
    if (headingElem) {
        headingElem.innerText = isAbstained ? t('candidate_heading') : t('recommended_heading');
    }

    // Recommendations List
    const recsList = document.getElementById('recommendations-list');
    const recs = data.recommendations || [];

    if (!recs.length) {
        recsList.innerHTML = `<p class="placeholder-text">${t('no_match')}</p>`;
        return;
    }

    // Reset filter bar controls
    const searchInput = document.getElementById('results-search-input');
    const qcoFilter = document.getElementById('results-qco-filter');
    if (searchInput) searchInput.value = '';
    if (qcoFilter) qcoFilter.value = 'all';

    filterAnalysisResults();
}

function filterAnalysisResults() {
    if (!currentAnalysisResult || !currentAnalysisResult.recommendations) return;

    const searchInput = document.getElementById('results-search-input');
    const qcoFilter = document.getElementById('results-qco-filter');
    
    const queryTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const filterType = qcoFilter ? qcoFilter.value : 'all';

    const lang = currentActiveLanguage || 'en';
    const isIndic = (lang !== 'en');
    const t = (k) => (UI_I18N[lang] && UI_I18N[lang][k]) || UI_I18N['en'][k] || k;

    const allRecs = currentAnalysisResult.recommendations || [];
    const isAbstained = (currentAnalysisResult.status === 'abstain' || currentAnalysisResult.confidence_gated);

    const filteredRecs = allRecs.filter(r => {
        // Keyword Search Filter
        if (queryTerm) {
            const isCodeMatch = (r.is_code || '').toLowerCase().includes(queryTerm);
            const titleMatch = (r.title || '').toLowerCase().includes(queryTerm);
            const titleLocMatch = (r.title_localized || '').toLowerCase().includes(queryTerm);
            const scopeMatch = (r.scope || '').toLowerCase().includes(queryTerm);
            const scopeLocMatch = (r.scope_localized || '').toLowerCase().includes(queryTerm);
            if (!isCodeMatch && !titleMatch && !titleLocMatch && !scopeMatch && !scopeLocMatch) {
                return false;
            }
        }

        // Compliance / Score Dropdown Filter
        if (filterType === 'qco') {
            const isQco = r.qco_compliance && r.qco_compliance.qco_mandatory;
            if (!isQco) return false;
        } else if (filterType === 'active') {
            const isSuperseded = (r.lifecycle_status === 'SUPERSEDED' || (r.superseded_by && r.superseded_by !== 'None'));
            if (isSuperseded) return false;
        } else if (filterType === 'high_score') {
            const scorePct = (r.relevance_score || 0.5);
            if (scorePct < 0.7) return false;
        }

        return true;
    });

    const recsList = document.getElementById('recommendations-list');
    if (!recsList) return;

    if (!filteredRecs.length) {
        recsList.innerHTML = `<p class="placeholder-text" style="padding:1.5rem; text-align:center; color:#64748b;">No matching standards found for active filters.</p>`;
        return;
    }

    let recsHtml = '';
    filteredRecs.forEach((r, idx) => {
        const isQco = r.qco_compliance && r.qco_compliance.qco_mandatory;
        let badge = '';
        if (isAbstained || r.citation_status === 'CLOSEST_CANDIDATE') {
            badge = `<span class="badge-abstain">${t('closest_candidate')} #${idx + 1}</span>`;
        } else if (isQco) {
            badge = `<span class="badge-qco">${t('mandatory_qco')}</span>`;
        } else {
            badge = `<span class="badge-rec">${t('recommended')}</span>`;
        }

        const isSuperseded = (r.lifecycle_status === 'SUPERSEDED' || (r.superseded_by && r.superseded_by !== 'None'));
        const lifecycleBadge = isSuperseded
            ? `<span class="badge-qco" style="background:#b91c1c; color:#fff;">${t('superseded_warn')} ${r.superseded_by || 'NEWER REVISION'}</span>`
            : `<span class="badge-rec" style="background:#f1f5f9; color:#475569; border:1px solid #cbd5e1;">${t('edition')}: ${r.edition_year || 'CURRENT'}</span>`;

        const supersededWarningHtml = isSuperseded
            ? `<div style="margin:0.5rem 0 0.25rem 0; padding:0.45rem 0.65rem; background:#fef2f2; border:1px solid #fecaca; border-radius:4px; color:#991b1b; font-size:0.84rem; font-weight:600;">
                ${t('superseded_warn')} <u>${r.superseded_by}</u>.
               </div>`
            : '';

        const scorePct = Math.round((r.relevance_score || 0.5) * 100);

        // Check if officer determination is already recorded
        const reviewRecord = recordedOfficerReviews[r.is_code];
        let reviewBadgeHtml = '';
        if (reviewRecord) {
            if (reviewRecord.decision === 'ACCEPTED') {
                reviewBadgeHtml = `<span class="badge-officer-accepted">${t('officer_accepted')} [${reviewRecord.audit_id}]</span>`;
            } else {
                reviewBadgeHtml = `<span class="badge-officer-override">${t('officer_overridden')} ${reviewRecord.final_standard} [${reviewRecord.audit_id}]</span>`;
            }
        }

        const titleHtml = (r.title_localized && r.title_localized !== r.title)
            ? `<div class="rec-title">${r.title_localized} <div style="font-size:0.86rem; color:#64748b; font-weight:normal; margin-top:2px;">${r.title}</div></div>`
            : `<div class="rec-title">${r.title}</div>`;

        const scopeHtml = (r.scope_localized && r.scope_localized !== r.scope)
            ? `<div class="rec-scope">${r.scope_localized} <div style="font-size:0.82rem; color:#64748b; margin-top:4px;">${r.scope}</div></div>`
            : `<div class="rec-scope">${r.scope || 'Scope verified from official BIS documentation.'}</div>`;

        recsHtml += `
            <div class="rec-item">
                <div class="rec-header">
                    <span class="rec-code">#${idx + 1} ${r.is_code}</span>
                    <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;">
                        ${badge}
                        ${lifecycleBadge}
                        ${reviewBadgeHtml}
                        <span class="score-pill">${scorePct}% ${t('relevance')}</span>
                    </div>
                </div>
                ${titleHtml}
                ${supersededWarningHtml}
                ${scopeHtml}
                <div class="rec-footer">
                    <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
                        <a href="#/standards/${encodeURIComponent(r.is_code)}" class="btn btn-sm btn-outline">${t('inspect_details')}</a>
                        <button class="btn btn-sm btn-secondary" onclick="openWhyModal('${(r.is_code || '').replace(/'/g, "\\'")}')">${t('why_standard')}</button>
                        <button class="btn btn-sm btn-primary" onclick="openReviewModal('${(r.is_code || '').replace(/'/g, "\\'")}', '${(r.title || '').replace(/'/g, "\\'")}')">${t('officer_review')}</button>
                    </div>
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

    const lang = currentActiveLanguage || 'en';
    const t = (k) => (UI_I18N[lang] && UI_I18N[lang][k]) || UI_I18N['en'][k] || k;

    const overlay = document.getElementById('why-modal-overlay');
    document.getElementById('why-title').innerText = `${t('why_standard')} — ${rec.is_code} (${t('explainability') || 'Explainability & Scoring Attribution'})`;

    const reasons = rec.ranking_reasons || rec.reasons || [];
    const breakdown = rec.score_breakdown || {};
    const vecScore = Math.round((breakdown.vector_semantic || 0.45) * 100);
    const entScore = Math.round((breakdown.entity_match || 0.35) * 100);
    const appScore = Math.round((breakdown.application_match || 0.10) * 100);
    const qcoScore = (rec.qco_compliance && rec.qco_compliance.qco_mandatory) ? '100% (Mandatory Statutory Gazette Weight Applied)' : '0% (Voluntary / Unnotified)';

    let html = `
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:0.85rem; margin-bottom:1rem;">
            <h5 style="margin-bottom:0.5rem; color:#0f172a; font-size:0.92rem; text-transform:uppercase; letter-spacing:0.5px;">${t('score_attribution') || 'Multi-Factor Hybrid Score Attribution'}</h5>
            <table style="width:100%; border-collapse:collapse; font-size:0.86rem; color:#334155;">
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.35rem 0; font-weight:600;">${t('dense_semantic') || 'Dense Semantic Similarity (Weight: 45%)'}</td>
                    <td style="padding:0.35rem 0; text-align:right;">${vecScore}% match</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.35rem 0; font-weight:600;">${t('attribute_overlap') || 'Technical Attribute Overlap (Weight: 35%)'}</td>
                    <td style="padding:0.35rem 0; text-align:right;">${entScore}% match</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.35rem 0; font-weight:600;">${t('app_alignment') || 'Application & Condition Alignment (Weight: 10%)'}</td>
                    <td style="padding:0.35rem 0; text-align:right;">${appScore}% match</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:0.35rem 0; font-weight:600;">${t('qco_alignment') || 'Statutory QCO Order Alignment (Weight: 20%)'}</td>
                    <td style="padding:0.35rem 0; text-align:right; color:${rec.qco_compliance?.qco_mandatory ? '#b91c1c' : '#64748b'}; font-weight:600;">${qcoScore}</td>
                </tr>
                <tr>
                    <td style="padding:0.45rem 0; font-weight:700; color:#003366;">${t('overall_score') || 'Overall Fused Confidence Score'}</td>
                    <td style="padding:0.45rem 0; text-align:right; font-weight:700; color:#003366; font-size:1rem;">${Math.round((rec.relevance_score || 0.5) * 100)}% (${rec.confidence_level || 'MEDIUM'})</td>
                </tr>
            </table>
        </div>

        <h4>${t('matching_factors') || 'Extracted Specification Matching Factors'}</h4>
        <ul style="margin:0.75rem 0 1.25rem 1.25rem;">
    `;
    const engReasons = rec.ranking_reasons || rec.reasons || [];
    const displayReasons = (rec.ranking_reasons_localized && rec.ranking_reasons_localized.length)
        ? rec.ranking_reasons_localized
        : engReasons;

    displayReasons.forEach((r, idx) => {
        const eng = engReasons[idx];
        if (rec.ranking_reasons_localized && eng && eng !== r) {
            html += `<li style="margin-bottom:0.45rem; font-size:0.9rem;"><strong>${r}</strong><div style="font-size:0.82rem; color:#64748b; margin-top:2px;">${eng}</div></li>`;
        } else {
            html += `<li style="margin-bottom:0.35rem; font-size:0.9rem;">${r}</li>`;
        }
    });
    html += `</ul>`;

    if (rec.lifecycle_status === 'SUPERSEDED' || (rec.superseded_by && rec.superseded_by !== 'None')) {
        html += `
            <div style="background:#fef2f2; border:1px solid #f87171; padding:0.85rem; border-radius:6px; margin-bottom:1rem;">
                <strong style="color:#b91c1c;">Lifecycle Notice: Obsolete / Superseded Standard</strong>
                <p style="font-size:0.87rem; margin-top:0.3rem; color:#7f1d1d;">This standard has been superseded by <strong>${rec.superseded_by}</strong>. Using this standard in a live public tender will trigger an audit objection.</p>
            </div>
        `;
    }

    if (rec.qco_compliance && rec.qco_compliance.qco_mandatory) {
        html += `
            <div style="background:#eff6ff; border:1px solid #93c5fd; padding:0.85rem; border-radius:6px; margin-bottom:1rem">
                <strong style="color:#1d4ed8">Statutory Mandatory Quality Control Order Notice</strong>
                <p style="font-size:0.87rem; margin-top:0.3rem; color:#1e40af">Mandated under Central Ministry Gazette Order (${rec.qco_compliance.qco_name || 'Enforced Directive'}). Indenting officers must enforce BIS ISI certification under the BIS Act, 2016.</p>
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

// Standard Details Dedicated Page Route
async function loadStandardDetailsPage(isCode) {
    try {
        const resp = await fetch(`/api/standards/${encodeURIComponent(isCode)}`);
        if (!resp.ok) throw new Error('Details unavailable.');
        const details = await resp.json();

        const stdCode = details.is_code || isCode;
        const stdNum = details.standardNumber || details.isNumber || stdCode;
        document.getElementById('detail-code-title').innerText = `${stdNum} Details & Lifecycle`;

        const existingReview = recordedOfficerReviews[stdCode] || null;
        let existingAuditBadgeHtml = '';
        let currentOverrideVal = stdCode;
        let isOverridden = false;
        let existingJustification = '';
        if (existingReview) {
            isOverridden = (existingReview.decision === 'OVERRIDDEN');
            currentOverrideVal = existingReview.final_standard || stdCode;
            existingJustification = existingReview.justification || '';
            const bClass = isOverridden ? 'badge-officer-override' : 'badge-officer-accepted';
            existingAuditBadgeHtml = `<span class="${bClass}">✓ RECORDED: ${existingReview.decision} (${existingReview.audit_id})</span>`;
        }

        const srcObj = details.source || {};
        const authorityName = srcObj.authority || "Bureau of Indian Standards (BIS)";
        const kysUrl = `https://standards.bis.gov.in/website/know-your-standards?searchTerm=${encodeURIComponent(stdCode)}`;
        const specificUrl = (srcObj.specificUrl && isExternalUrl(srcObj.specificUrl) && srcObj.specificUrl !== "https://standards.bis.gov.in/") ? srcObj.specificUrl : kysUrl;
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
        const buttonText = "View Standard on BIS (KYS) ↗";
        const targetUrl = specificUrl || kysUrl;
        const sourceButtonHtml = `<a href="${targetUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-primary">${buttonText}</a>`;
        const verifiedBadgeHtml = isVerified ? `<span class="badge-rec">✓ Official BIS Source</span>` : '';
        const unavailableBadgeHtml = '';

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

        let html = `
            <div style="margin-bottom:1.25rem; padding-bottom:1rem; border-bottom:1px solid var(--border-light)">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; flex-wrap:wrap">
                    <div>
                        <h3 style="margin:0 0 0.35rem 0; font-size:1.4rem; color:var(--primary-color)">${stdNum}</h3>
                        <p style="font-weight:600; font-size:1.05rem; margin:0; color:#334155">${details.title}</p>
                    </div>
                    <div>${statusBadgeHtml}</div>
                </div>
            </div>

            <!-- VERSION & LIFECYCLE GRID -->
            <div style="margin-bottom:1.5rem">
                <h4 style="font-size:0.9rem; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; margin-bottom:0.75rem">VERSION & LIFECYCLE</h4>
                <div class="lifecycle-grid">
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">CURRENT EDITION</div>
                            <div class="version-card-value">${pubYear}</div>
                        </div>
                        <div class="version-card-subtext">The year of the published standard edition.</div>
                    </div>
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">REVISION</div>
                            <div class="version-card-value">${revLabel}</div>
                        </div>
                        <div class="version-card-subtext">The revision number of the standard.</div>
                    </div>
                    <div class="version-card">
                        <div>
                            <div class="version-card-label">LAST REVIEWED</div>
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
                <h4 style="font-size:0.95rem; font-weight:700; color:var(--primary-color); margin:0 0 0.5rem 0">AMENDMENTS & REVISION HISTORY</h4>
                <p style="margin:0 0 0.5rem 0; font-size:0.9rem"><strong>Current Published Edition:</strong> ${stdNum} — ${revLabel}</p>
                ${amendmentsDetailHtml}
            </div>

            <!-- SUPERSEDING INFORMATION -->
            <div style="margin-top:1.25rem; padding:1rem; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px">
                <h4 style="font-size:0.85rem; text-transform:uppercase; letter-spacing:0.05em; color:#64748b; margin:0 0 0.5rem 0">SUPERSEDING INFORMATION</h4>
                <div style="display:flex; gap:2rem; flex-wrap:wrap; font-size:0.9rem">
                    <div><strong>Supersedes:</strong> ${supersedes}</div>
                    <div><strong>Superseded By:</strong> ${supersededBy}</div>
                </div>
            </div>

            <!-- SCOPE & DETAILS -->
            <div style="margin-top:1.5rem">
                <p style="margin-top:0.75rem"><strong>Scope & Description:</strong> ${details.scope}</p>
                <p style="margin-top:0.5rem"><strong>Materials Specification:</strong> ${details.materials}</p>
                <p><strong>Applications:</strong> ${details.applications}</p>
                <p><strong>Technical Parameters:</strong> ${details.technical_parameters}</p>
            </div>

            <!-- SOURCE AUTHORITY -->
            <div style="margin-top:1.5rem; padding-top:1.25rem; border-top:1px solid var(--border-light)">
                <p style="margin-bottom:0.6rem"><strong>Source Authority:</strong> ${authorityName}</p>
                <div style="display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap">
                    ${sourceButtonHtml}
                    ${verifiedBadgeHtml}
                    ${unavailableBadgeHtml}
                </div>
            </div>

            <!-- STATUTORY PROCUREMENT OFFICER DETERMINATION & EDIT STANDARD NUMBER -->
            <div class="card officer-determination-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; margin-bottom:0.75rem;">
                    <div>
                        <h4 style="margin:0; color:#1e40af; font-size:1.15rem; display:flex; align-items:center; gap:0.5rem;">
                            ⚖️ Statutory Procurement Officer Determination & Standard Override
                        </h4>
                        <p style="margin:0.25rem 0 0 0; font-size:0.85rem; color:#64748b;">
                            GFR Rule 144(vii) Mandate: Review or edit/overwrite the designated standard number and record official determination into the Audit Trail.
                        </p>
                    </div>
                    <div id="inspect-audit-badge">
                        ${existingAuditBadgeHtml}
                    </div>
                </div>

                <div style="background:white; border:1px solid #cbd5e1; border-radius:8px; padding:1.25rem;">
                    <div class="form-row" style="display:grid; grid-template-columns:1fr 1fr; gap:1.25rem;">
                        <div class="form-group">
                            <label style="font-weight:600; font-size:0.88rem; color:#334155;">Original Standard Number:</label>
                            <input type="text" id="inspect-std-original" value="${stdCode}" readonly style="background:#f1f5f9; font-weight:700; color:#334155; padding:0.6rem 0.85rem; border:1px solid #cbd5e1; border-radius:6px; width:100%;">
                        </div>
                        <div class="form-group">
                            <label for="inspect-std-override-number" style="font-weight:700; font-size:0.88rem; color:#1e40af;">
                                ✏️ Designated Standard Number (Editable / Overwrite Option):
                            </label>
                            <input type="text" id="inspect-std-override-number" class="editable-std-input" value="${currentOverrideVal}" placeholder="e.g. IS 13428:2005" oninput="handleInspectOverrideInput('${stdCode.replace(/'/g, "\\'")}')">
                            <small style="color:#64748b; font-size:0.78rem;">Officer can freely edit or overwrite the IS standard number here.</small>
                        </div>
                    </div>

                    <div class="form-group" style="margin-top:1rem;">
                        <label style="font-weight:600; font-size:0.88rem;">Officer Determination Action:</label>
                        <div class="determination-options" style="display:flex; gap:1.5rem; margin-top:0.4rem;">
                            <label class="determination-option" style="cursor:pointer; display:flex; align-items:center; gap:0.4rem;">
                                <input type="radio" name="inspect-officer-decision" id="inspect-decision-accept" value="ACCEPTED" ${isOverridden ? '' : 'checked'} onchange="handleInspectDecisionChange('${stdCode.replace(/'/g, "\\'")}')">
                                <span><strong>ACCEPT</strong> Current Standard (${stdCode})</span>
                            </label>
                            <label class="determination-option" style="cursor:pointer; display:flex; align-items:center; gap:0.4rem;">
                                <input type="radio" name="inspect-officer-decision" id="inspect-decision-override" value="OVERRIDDEN" ${isOverridden ? 'checked' : ''} onchange="handleInspectDecisionChange('${stdCode.replace(/'/g, "\\'")}')">
                                <span><strong>OVERRIDE / EDIT</strong> Standard Number</span>
                            </label>
                        </div>
                    </div>

                    <div class="form-row" style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.75rem; margin-top:1rem;">
                        <div class="form-group">
                            <label style="font-size:0.82rem; font-weight:600;">Reviewing Official Name & ID:</label>
                            <input type="text" id="inspect-officer-name" value="Er. Rajesh Kumar (EMP-88412)" style="padding:0.5rem; border:1px solid #cbd5e1; border-radius:6px; width:100%;">
                        </div>
                        <div class="form-group">
                            <label style="font-size:0.82rem; font-weight:600;">Designation / Role:</label>
                            <input type="text" id="inspect-officer-desig" value="Executive Engineer (E&M)" style="padding:0.5rem; border:1px solid #cbd5e1; border-radius:6px; width:100%;">
                        </div>
                        <div class="form-group">
                            <label style="font-size:0.82rem; font-weight:600;">Department / Organization:</label>
                            <input type="text" id="inspect-officer-dept" value="GeM / Central Procurement Cell" style="padding:0.5rem; border:1px solid #cbd5e1; border-radius:6px; width:100%;">
                        </div>
                    </div>

                    <div class="form-group" style="margin-top:1rem;">
                        <label for="inspect-officer-justification" style="font-size:0.85rem; font-weight:600; color:#1e40af;">
                            Statutory Audit Justification (Mandatory under GFR Rule 144):
                        </label>
                        <textarea id="inspect-officer-justification" rows="2" placeholder="State reason for accepting or overriding the standard number (e.g. Schedule duty rating, mineral content parameters, site operating conditions under GFR 144(vii))..." style="width:100%; padding:0.6rem; border:1px solid #cbd5e1; border-radius:6px; font-family:inherit;">${existingJustification}</textarea>
                    </div>

                    <div style="margin-top:1rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem;">
                        <a href="#/audit" class="btn btn-outline btn-sm">📋 View Full Officer Audit Trail Register</a>
                        <button class="btn btn-primary" onclick="submitInspectOfficerDetermination('${encodeURIComponent(stdCode)}', '${encodeURIComponent(details.title)}')">
                            💾 Save Determination & Record in Audit Trail
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('detail-body').innerHTML = html;
        showToast(`Loaded details for ${stdCode}`, 'info');
    } catch (err) {
        document.getElementById('detail-body').innerHTML = `<p class="error-text">Standard details for '${isCode}' not available in verified database.</p>`;
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

    try {
        const resp = await fetch('/api/reports/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: currentAnalysisResult.query,
                entities: currentAnalysisResult.entities,
                recommendations: currentAnalysisResult.recommendations
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

// ----------------------------------------------------
// 10. OFFICER REVIEW MODAL & AUDIT TRAIL LOGIC
// ----------------------------------------------------
function openReviewModal(isCode, title) {
    activeReviewTarget = { isCode, title };
    const modal = document.getElementById('review-modal-overlay');
    if (!modal) return;
    
    const qText = currentAnalysisResult ? (currentAnalysisResult.user_original_query || currentAnalysisResult.query) : 'Procurement Requirement Specification';
    document.getElementById('review-query-text').innerText = qText;
    document.getElementById('review-target-std').innerText = `${isCode} — ${title || 'Indian Standard'}`;
    document.getElementById('decision-accept').checked = true;
    
    const overrideInput = document.getElementById('override-standard-code');
    if (overrideInput) {
        overrideInput.value = isCode;
    }
    document.getElementById('review-justification').value = '';
    
    modal.classList.add('active');
}

function handleOverrideInputChange() {
    const overrideInput = document.getElementById('override-standard-code');
    if (!overrideInput || !activeReviewTarget) return;
    const currentVal = overrideInput.value.trim();
    if (currentVal && currentVal !== activeReviewTarget.isCode) {
        const rad = document.getElementById('decision-override');
        if (rad) rad.checked = true;
    } else {
        const rad = document.getElementById('decision-accept');
        if (rad) rad.checked = true;
    }
}

function closeReviewModal() {
    const modal = document.getElementById('review-modal-overlay');
    if (modal) modal.classList.remove('active');
    activeReviewTarget = null;
}

function toggleOverrideField() {
    const isOverride = document.getElementById('decision-override').checked;
    const overrideInput = document.getElementById('override-standard-code');
    if (!isOverride && overrideInput && activeReviewTarget) {
        overrideInput.value = activeReviewTarget.isCode;
    } else if (isOverride && overrideInput) {
        overrideInput.focus();
    }
}

async function submitOfficerReview() {
    if (!activeReviewTarget) return;
    const isCode = activeReviewTarget.isCode;
    const decision = document.querySelector('input[name="officer-decision"]:checked')?.value || 'ACCEPTED';
    const overrideCode = document.getElementById('override-standard-code')?.value.trim();
    const finalStd = (decision === 'OVERRIDDEN' && overrideCode) ? overrideCode : isCode;
    const officerName = document.getElementById('officer-name')?.value.trim() || 'Er. Rajesh Kumar (EMP-88412)';
    const officerDesig = document.getElementById('officer-desig')?.value.trim() || 'Executive Engineer (E&M)';
    const officerDept = document.getElementById('officer-dept')?.value.trim() || 'GeM / Central Procurement Cell';
    const justification = document.getElementById('review-justification').value.trim();

    if (!justification) {
        showToast('Statutory audit justification is required to record determination.', 'warning');
        return;
    }

    if (decision === 'OVERRIDDEN' && !overrideCode) {
        showToast('Please specify the designated alternative standard code.', 'warning');
        return;
    }

    const payload = {
        analysis_id: currentAnalysisResult?.id || null,
        query: currentAnalysisResult?.query || activeReviewTarget.title || 'Procurement requirement',
        recommended_standard: isCode,
        decision: decision,
        final_standard: finalStd,
        officer_name: officerName,
        officer_designation: officerDesig,
        department: officerDept,
        justification: justification
    };

    try {
        const resp = await fetch('/api/audit/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('Failed to record review determination.');
        const auditRecord = await resp.json();
        recordedOfficerReviews[isCode] = auditRecord;

        showToast(`Determination successfully logged into Statutory Audit Trail: ${auditRecord.audit_id}`, 'success');
        closeReviewModal();
        
        // Re-render recommendations to show audit badge
        if (currentAnalysisResult) {
            renderAnalysisResults(currentAnalysisResult);
        }
    } catch (err) {
        showToast('Error recording audit review. Please verify backend connection.', 'error');
        console.error(err);
    }
}

// Inspect Page Determination Handlers
function handleInspectOverrideInput(stdCode) {
    const input = document.getElementById('inspect-std-override-number');
    if (!input) return;
    const val = input.value.trim();
    if (val && val !== stdCode) {
        const rad = document.getElementById('inspect-decision-override');
        if (rad) rad.checked = true;
    } else {
        const rad = document.getElementById('inspect-decision-accept');
        if (rad) rad.checked = true;
    }
}

function handleInspectDecisionChange(stdCode) {
    const isOverride = document.getElementById('inspect-decision-override')?.checked;
    const input = document.getElementById('inspect-std-override-number');
    if (!isOverride && input) {
        input.value = stdCode;
    } else if (isOverride && input) {
        input.focus();
    }
}

async function submitInspectOfficerDetermination(stdCodeEnc, titleEnc) {
    const isCode = decodeURIComponent(stdCodeEnc);
    const title = decodeURIComponent(titleEnc);
    
    const decision = document.querySelector('input[name="inspect-officer-decision"]:checked')?.value || 'ACCEPTED';
    const overrideCode = document.getElementById('inspect-std-override-number')?.value.trim();
    const finalStd = (decision === 'OVERRIDDEN' && overrideCode) ? overrideCode : isCode;
    const officerName = document.getElementById('inspect-officer-name')?.value.trim() || 'Er. Rajesh Kumar (EMP-88412)';
    const officerDesig = document.getElementById('inspect-officer-desig')?.value.trim() || 'Executive Engineer (E&M)';
    const officerDept = document.getElementById('inspect-officer-dept')?.value.trim() || 'GeM / Central Procurement Cell';
    const justification = document.getElementById('inspect-officer-justification')?.value.trim();

    if (!justification) {
        showToast('Statutory audit justification is required to record determination.', 'warning');
        return;
    }

    if (decision === 'OVERRIDDEN' && !overrideCode) {
        showToast('Please specify the designated alternative standard code.', 'warning');
        return;
    }

    const payload = {
        analysis_id: currentAnalysisResult?.id || null,
        query: `Inspect Determination for ${isCode} - ${title}`,
        recommended_standard: isCode,
        decision: decision,
        final_standard: finalStd,
        officer_name: officerName,
        officer_designation: officerDesig,
        department: officerDept,
        justification: justification
    };

    try {
        const resp = await fetch('/api/audit/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('Failed to record review determination.');
        const auditRecord = await resp.json();
        recordedOfficerReviews[isCode] = auditRecord;

        const bClass = (decision === 'OVERRIDDEN') ? 'badge-officer-override' : 'badge-officer-accepted';
        const badgeEl = document.getElementById('inspect-audit-badge');
        if (badgeEl) {
            badgeEl.innerHTML = `<span class="${bClass}">✓ RECORDED: ${auditRecord.decision} (${auditRecord.audit_id})</span>`;
        }

        showToast(`Determination successfully logged into Statutory Audit Trail: ${auditRecord.audit_id}`, 'success');
    } catch (err) {
        showToast('Error recording audit determination. Please verify backend connection.', 'error');
        console.error(err);
    }
}

function inspectAndEditAuditRecord(auditId, recommendedStd, finalStd, query, justification) {
    activeReviewTarget = { isCode: recommendedStd, title: finalStd };
    const modal = document.getElementById('review-modal-overlay');
    if (!modal) return;
    
    document.getElementById('review-query-text').innerText = query || 'Procurement Requirement Specification';
    document.getElementById('review-target-std').innerText = `${recommendedStd} (Audit ID: ${auditId})`;
    
    const overrideInput = document.getElementById('override-standard-code');
    if (overrideInput) {
        overrideInput.value = finalStd || recommendedStd;
    }
    
    if (finalStd && finalStd !== recommendedStd) {
        const rad = document.getElementById('decision-override');
        if (rad) rad.checked = true;
    } else {
        const rad = document.getElementById('decision-accept');
        if (rad) rad.checked = true;
    }
    
    document.getElementById('review-justification').value = justification || '';
    modal.classList.add('active');
    showToast(`Inspecting Audit Record ${auditId} - you can edit the standard number.`, 'info');
}

async function loadAuditTrail() {
    const container = document.getElementById('audit-trail-container');
    if (!container) return;
    try {
        const resp = await fetch('/api/audit/trail');
        const logs = await resp.json();
        if (!logs || !logs.length) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon-label">[No Determinations Logged]</div>
                    <h3>No Officer Determinations in Audit Trail</h3>
                    <p>Perform an analysis and click 'Officer Review & Log Decision' or inspect any standard to record formal determinations.</p>
                    <a href="#/analyze" class="btn btn-primary">Start Analysis</a>
                </div>
            `;
            return;
        }

        let html = `
            <div class="audit-table-wrapper" style="overflow-x:auto; border:1.5px solid #64748b; border-radius:6px; background:#ffffff;">
                <table class="audit-table" style="width:100%; border-collapse:collapse; border:1.5px solid #64748b; font-size:0.78rem; text-align:left;">
                    <thead>
                        <tr style="background:#e2e8f0; border-bottom:2px solid #64748b;">
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Audit ID</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Date & Time</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Procurement Requirement</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">System Citation</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Determination</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Final Standard</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Reviewing Official</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Statutory Justification</th>
                            <th style="padding:0.5rem 0.65rem; border:1px solid #94a3b8; font-weight:700; color:#0f172a; white-space:nowrap;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        logs.forEach(log => {
            const isAccept = log.decision === 'ACCEPTED';
            const badgeClass = isAccept ? 'badge-officer-accepted' : 'badge-officer-override';
            const cellStyle = "padding:0.5rem 0.65rem; border:1px solid #cbd5e1; vertical-align:top; font-size:0.78rem;";
            html += `
                <tr style="border-bottom:1px solid #cbd5e1;">
                    <td style="${cellStyle}"><span class="audit-id-badge" style="border:1px solid #cbd5e1;">${log.audit_id}</span></td>
                    <td style="${cellStyle} white-space:nowrap; font-size:0.75rem; color:#64748b;">${log.timestamp}</td>
                    <td style="${cellStyle} max-width:220px; font-weight:500;">"${log.query}"</td>
                    <td style="${cellStyle}"><strong>${log.recommended_standard}</strong></td>
                    <td style="${cellStyle}"><span class="${badgeClass}">${log.decision}</span></td>
                    <td style="${cellStyle}"><strong style="color:${isAccept ? '#065f46' : '#1e40af'}">${log.final_standard}</strong></td>
                    <td style="${cellStyle}">
                        <div style="font-weight:600; font-size:0.78rem;">${log.officer_name}</div>
                        <div style="font-size:0.75rem; color:#2563eb; font-weight:500;">${log.officer_designation || ''}</div>
                        <div style="font-size:0.72rem; color:#64748b;">${log.department}</div>
                    </td>
                    <td style="${cellStyle} max-width:220px; color:#475569;">${log.justification}</td>
                    <td style="${cellStyle} white-space:nowrap;">
                        <button class="btn btn-sm btn-outline" style="font-size:0.75rem; padding:0.25rem 0.5rem;" onclick="inspectAndEditAuditRecord('${log.audit_id}', '${(log.recommended_standard || '').replace(/'/g, "\\'")}', '${(log.final_standard || '').replace(/'/g, "\\'")}', '${(log.query || '').replace(/'/g, "\\'")}', '${(log.justification || '').replace(/'/g, "\\'")}')">
                            ✏️ Edit Standard Number
                        </button>
                    </td>
                </tr>
            `;
        });

        html += `</tbody></table></div>`;
        container.innerHTML = html;
    } catch (err) {
        container.innerHTML = `<p class="error-text">Failed to load officer audit trail register.</p>`;
    }
}

// Dynamic Output Language Selector Change Handler
async function handleOutputLanguageChange(newLang) {
    if (!currentAnalysisResult) return;

    const query = currentAnalysisResult.user_original_query || currentAnalysisResult.query;
    if (query) {
        startLoadingProgress();
        try {
            const inputLang = document.getElementById('language-select')?.value || 'auto';
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    description: query,
                    language: inputLang,
                    output_language: newLang
                })
            });
            const data = await resp.json();
            currentAnalysisResult = data;
            renderAnalysisResults(data);
            showToast(`Output language updated to ${newLang.toUpperCase()}`, 'info');
        } catch (err) {
            console.error('Failed to update output language:', err);
        } finally {
            stopLoadingProgress();
        }
    }
}

// Global Application Language Switcher
function handleGlobalLanguageChange(lang) {
    currentActiveLanguage = lang;
    
    // Sync analyze workspace dropdowns
    const outLangSelect = document.getElementById('output-language-select');
    if (outLangSelect) {
        outLangSelect.value = lang;
    }
    
    const inLangSelect = document.getElementById('language-select');
    if (inLangSelect && inLangSelect.value !== 'auto') {
        inLangSelect.value = lang;
    }

    const globalSelect = document.getElementById('global-language-select');
    if (globalSelect) {
        globalSelect.value = lang;
    }

    const langNameMap = {
        'en': 'English',
        'hi': 'Hindi (हिंदी)',
        'ta': 'Tamil (தமிழ்)',
        'te': 'Telugu (తెలుగు)',
        'mr': 'Marathi (मराठी)',
        'bn': 'Bengali (বাংলা)',
        'gu': 'Gujarati (ગુજરાતી)',
        'kn': 'Kannada (ಕನ್ನಡ)',
        'ml': 'Malayalam (മലയാളം)',
        'pa': 'Punjabi (ਪੰਜਾਬੀ)',
        'or': 'Odia (ଓଡ଼ିଆ)'
    };

    showToast(`App language set to ${langNameMap[lang] || lang.toUpperCase()}`, 'info');

    // Trigger analysis result re-localization if an active session exists
    if (currentAnalysisResult) {
        handleOutputLanguageChange(lang);
    }
}

// Global Window Bindings
window.openWhyModal = openWhyModal;
window.closeWhyModal = closeWhyModal;
window.openReviewModal = openReviewModal;
window.closeReviewModal = closeReviewModal;
window.toggleOverrideField = toggleOverrideField;
window.handleOverrideInputChange = handleOverrideInputChange;
window.submitOfficerReview = submitOfficerReview;
window.handleInspectOverrideInput = handleInspectOverrideInput;
window.handleInspectDecisionChange = handleInspectDecisionChange;
window.submitInspectOfficerDetermination = submitInspectOfficerDetermination;
window.inspectAndEditAuditRecord = inspectAndEditAuditRecord;
window.loadAuditTrail = loadAuditTrail;
window.handleOutputLanguageChange = handleOutputLanguageChange;
window.uploadTenderDocument = uploadTenderDocument;
window.filterAnalysisResults = filterAnalysisResults;
window.handleGlobalLanguageChange = handleGlobalLanguageChange;

// Auth & RBAC Window Bindings
window.updateUserUI = updateUserUI;
window.openLoginModal = openLoginModal;
window.closeLoginModal = closeLoginModal;
window.selectDemoRole = selectDemoRole;
window.syncRoleFromSelect = syncRoleFromSelect;
window.handleLoginSubmit = handleLoginSubmit;
window.logoutUser = logoutUser;

// ----------------------------------------------------
// AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC)
// ----------------------------------------------------
function updateUserUI() {
    const mainNav = document.getElementById('main-nav');
    const avatarEl = document.getElementById('user-badge-avatar');
    const nameEl = document.getElementById('user-badge-name');
    const roleEl = document.getElementById('user-badge-role');
    const navAdminLink = document.getElementById('nav-admin-link');
    const userBadge = document.getElementById('user-profile-badge');

    const isLoginView = !isLoggedIn || window.location.hash === '#/login';

    if (mainNav) {
        mainNav.style.display = isLoginView ? 'none' : 'block';
    }

    if (isLoginView && !isLoggedIn) {
        if (avatarEl) avatarEl.textContent = '🔒';
        if (nameEl) nameEl.textContent = 'Sign In';
        if (roleEl) {
            roleEl.textContent = 'PORTAL';
            roleEl.className = 'badge-role-officer';
        }
        if (navAdminLink) navAdminLink.style.display = 'none';
    } else {
        if (avatarEl) avatarEl.textContent = currentUser.avatar || (currentUser.role === 'admin' ? '🛡️' : '👨‍💼');
        if (nameEl) nameEl.textContent = currentUser.name || currentUser.username;
        if (roleEl) {
            roleEl.textContent = (currentUser.role || 'officer').toUpperCase();
            roleEl.className = currentUser.role === 'admin' ? 'badge-role-admin' : 'badge-role-officer';
        }
        if (navAdminLink) {
            navAdminLink.style.display = currentUser.role === 'admin' ? 'inline-flex' : 'none';
        }
    }
}

function openLoginModal() {
    if (!isLoggedIn || window.location.hash === '#/login') {
        navigateTo('#/login');
        return;
    }
    const modal = document.getElementById('login-modal-overlay');
    if (modal) modal.style.display = 'flex';
    syncLoginFields(currentUser.role || 'officer');
}

function closeLoginModal() {
    const modal = document.getElementById('login-modal-overlay');
    if (modal) modal.style.display = 'none';
}

function selectDemoRole(role) {
    const btnOfficerModal = document.getElementById('btn-role-officer');
    const btnAdminModal = document.getElementById('btn-role-admin');
    const btnOfficerPage = document.getElementById('btn-page-role-officer');
    const btnAdminPage = document.getElementById('btn-page-role-admin');

    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    const roleSelect = document.getElementById('login-role-select');
    const privilegesDesc = document.getElementById('role-privileges-desc');

    if (role === 'admin') {
        if (btnOfficerModal) btnOfficerModal.classList.remove('active');
        if (btnAdminModal) btnAdminModal.classList.add('active');
        if (btnOfficerPage) btnOfficerPage.classList.remove('active');
        if (btnAdminPage) btnAdminPage.classList.add('active');

        if (usernameInput) usernameInput.value = 'admin@gem.gov.in';
        if (passwordInput) passwordInput.value = 'admin123';
        if (roleSelect) roleSelect.value = 'admin';
        if (privilegesDesc) {
            privilegesDesc.innerHTML = '🛡️ <strong>System Administrator Privileges:</strong> Full administrative control, system metrics, indexing control, vector store sync, and diagnostics dashboard.';
            privilegesDesc.style.background = '#fef2f2';
            privilegesDesc.style.borderColor = '#fecaca';
            privilegesDesc.style.color = '#991b1b';
        }
    } else {
        if (btnAdminModal) btnAdminModal.classList.remove('active');
        if (btnOfficerModal) btnOfficerModal.classList.add('active');
        if (btnAdminPage) btnAdminPage.classList.remove('active');
        if (btnOfficerPage) btnOfficerPage.classList.add('active');

        if (usernameInput) usernameInput.value = 'officer@gem.gov.in';
        if (passwordInput) passwordInput.value = 'officer123';
        if (roleSelect) roleSelect.value = 'officer';
        if (privilegesDesc) {
            privilegesDesc.innerHTML = '📋 <strong>Procurement Officer Privileges:</strong> Access to Requirement Analysis workspace, BIS Catalog, QCO Notices, Statutory Audit Trail recording, and PDF Exports.';
            privilegesDesc.style.background = '#f0f9ff';
            privilegesDesc.style.borderColor = '#bae6fd';
            privilegesDesc.style.color = '#0369a1';
        }
    }
}

function syncRoleFromSelect(role) {
    selectDemoRole(role);
}

function syncLoginFields(role) {
    selectDemoRole(role);
}

async function handleLoginSubmit(event) {
    event.preventDefault();
    const username = document.getElementById('login-username')?.value.trim();
    const password = document.getElementById('login-password')?.value.trim();
    const role = document.getElementById('login-role-select')?.value;

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role })
        });
        const data = await response.json();
        if (response.ok && (data.user || data.username || data.role)) {
            currentUser = data.user || data;
            isLoggedIn = true;
            localStorage.setItem('standard_saarthi_logged_in', 'true');
            localStorage.setItem('standard_saarthi_user', JSON.stringify(currentUser));
            updateUserUI();
            closeLoginModal();
            showToast(`Welcome, ${currentUser.name}! Logged in as ${(currentUser.role || 'officer').toUpperCase()}`, 'success');
            
            // Redirect to Home Page
            navigateTo('#/');
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (err) {
        console.error('Login request failed, using local demo fallback:', err);
        const isAdminRole = role === 'admin' || username.includes('admin');
        currentUser = {
            username: username || 'user@gem.gov.in',
            name: isAdminRole ? 'System Administrator' : 'Er. Rajesh Kumar',
            role: isAdminRole ? 'admin' : 'officer',
            department: isAdminRole ? 'IT & Standards Admin' : 'Procurement Cell, GeM',
            avatar: isAdminRole ? '🛡️' : '👨‍💼'
        };
        isLoggedIn = true;
        localStorage.setItem('standard_saarthi_logged_in', 'true');
        localStorage.setItem('standard_saarthi_user', JSON.stringify(currentUser));
        updateUserUI();
        closeLoginModal();
        showToast(`Welcome, ${currentUser.name}! Logged in as ${currentUser.role.toUpperCase()}`, 'success');
        
        // Redirect to Home Page
        navigateTo('#/');
    }
}

function logoutUser() {
    isLoggedIn = false;
    localStorage.setItem('standard_saarthi_logged_in', 'false');
    currentUser = {
        username: 'officer@gem.gov.in',
        name: 'Er. Rajesh Kumar',
        role: 'officer',
        department: 'Procurement Cell, GeM',
        avatar: '👨‍💼'
    };
    localStorage.setItem('standard_saarthi_user', JSON.stringify(currentUser));
    updateUserUI();
    showToast('Logged out successfully. Switched back to Sign In page.', 'info');
    navigateTo('#/login');
}







