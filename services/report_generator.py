"""
Procurement Standards PDF Report Generator for SIH 26108 / Product Engine.
Generates formal multi-page PDF reports using `reportlab`.
PDF reports are strictly generated in ENGLISH to ensure consistent font rendering across all environments.
"""

import io
import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

logger = logging.getLogger("ReportGenerator")

def _clean_str_to_ascii(text: Any, fallback: str = "") -> str:
    """Safely converts input string to clean ASCII text, stripping non-ASCII characters."""
    if not isinstance(text, str):
        text = str(text) if text is not None else ""
    if not text.isascii():
        cleaned = text.encode("ascii", errors="ignore").decode("ascii").strip()
        return cleaned if cleaned else fallback
    return text

def _sanitize_data_for_english_pdf(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes analysis data payload to ensure ONLY English fields and ASCII values are used.
    Strips localized/translated fields (localized_title, localized_scope, etc.) and
    replaces raw Indic query text with normalized English.
    """
    clean_data = dict(analysis_data)

    # 1. Extract multilingual info from wherever it might be nested
    ml_info = (
        clean_data.get("multilingual_info") or
        (clean_data.get("entities") or {}).get("multilingual_info") or
        (clean_data.get("query_analysis") or {}).get("multilingual_info") or
        {}
    )
    norm_eng = (
        ml_info.get("normalized_english") or
        clean_data.get("normalized_query") or
        (clean_data.get("query_analysis") or {}).get("detected_product")
    )

    raw_query = clean_data.get("query", "")
    if norm_eng and isinstance(norm_eng, str) and norm_eng.isascii() and norm_eng.strip():
        clean_data["query"] = norm_eng.strip()
    elif isinstance(raw_query, str) and raw_query.isascii() and raw_query.strip():
        clean_data["query"] = raw_query.strip()
    else:
        clean_data["query"] = "Procurement Requirement Specification"

    # 2. Entities sanitization
    entities = clean_data.get("entities") or {}
    clean_entities = {}
    if isinstance(entities, dict):
        for k, v in entities.items():
            if k == "multilingual_info":
                continue
            if isinstance(v, list):
                clean_entities[k] = [_clean_str_to_ascii(item) for item in v if isinstance(item, (str, int, float)) and _clean_str_to_ascii(item)]
            elif isinstance(v, (str, int, float)):
                clean_entities[k] = _clean_str_to_ascii(v, "Not specified")
    clean_data["entities"] = clean_entities

    # 3. Recommendations sanitization
    recs = clean_data.get("recommendations") or []
    clean_recs = []
    localized_keys = {
        "localized_title", "localized_scope", "localized_reason", "localized_compliance",
        "localized_why_this_standard", "localized_applications", "localized_materials",
        "localized_notice", "localized_qco"
    }

    for r in recs:
        if not isinstance(r, dict):
            continue
        r_clean = dict(r)

        # Strip localized fields
        for lk in localized_keys:
            r_clean.pop(lk, None)
        
        # Use official / English title
        title = r_clean.get("official_title") or r_clean.get("title") or ""
        r_clean["title"] = _clean_str_to_ascii(title, "Indian Standard Specification")

        # Use official / English scope
        scope = r_clean.get("official_scope") or r_clean.get("scope") or ""
        r_clean["scope"] = _clean_str_to_ascii(scope, "Scope details available in BIS official document.")

        # Handle ranking reasons / why_this_standard
        reasons = r_clean.get("official_ranking_reasons") or r_clean.get("ranking_reasons") or []
        clean_reasons = []
        if isinstance(reasons, list):
            clean_reasons = [_clean_str_to_ascii(reason) for reason in reasons if _clean_str_to_ascii(reason)]
        
        why_std = r_clean.get("why_this_standard")
        if why_std and isinstance(why_std, str):
            cleaned_why = _clean_str_to_ascii(why_std)
            if cleaned_why and cleaned_why not in clean_reasons:
                clean_reasons.append(cleaned_why)

        if not clean_reasons:
            clean_reasons = ["Satisfies statutory BIS quality & technical criteria for product category."]

        r_clean["ranking_reasons"] = clean_reasons
        r_clean.pop("why_this_standard", None)

        # Handle compliance guidance
        if "compliance_guidance" in r_clean:
            r_clean["compliance_guidance"] = _clean_str_to_ascii(r_clean["compliance_guidance"], "BIS Certification Recommended")

        # Clean remaining string fields in r_clean
        for k, v in list(r_clean.items()):
            if isinstance(v, str):
                r_clean[k] = _clean_str_to_ascii(v)

        # Ensure qco_compliance uses English values
        if "qco_compliance" in r_clean and isinstance(r_clean["qco_compliance"], dict):
            qco = dict(r_clean["qco_compliance"])
            for lk in localized_keys:
                qco.pop(lk, None)
            for qk, qv in qco.items():
                if isinstance(qv, str):
                    qco[qk] = _clean_str_to_ascii(qv)
            r_clean["qco_compliance"] = qco

        clean_recs.append(r_clean)

    clean_data["recommendations"] = clean_recs
    return clean_data

class ReportGenerator:
    def __init__(self):
        pass

    def generate_pdf_report(self, analysis_data: Dict[str, Any], output_language: str = "en") -> bytes:
        """
        Builds PDF report buffer from analysis data.
        Enforces English output for all generated PDF reports.
        """
        # Force English sanitization on input data
        clean_data = _sanitize_data_for_english_pdf(analysis_data)
        
        font_regular = "Helvetica"
        font_bold = "Helvetica-Bold"

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Palette
        PRIMARY_COLOR = colors.HexColor("#1e3a8a") # Deep Navy
        SECONDARY_COLOR = colors.HexColor("#0f766e") # Teal
        TEXT_COLOR = colors.HexColor("#1f2937")
        LIGHT_BG = colors.HexColor("#f8fafc")
        ALERT_BG = colors.HexColor("#fef2f2")
        ACCENT_COLOR = colors.HexColor("#2563eb")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName=font_bold,
            fontSize=20,
            leading=24,
            textColor=PRIMARY_COLOR,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName=font_regular,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=15
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName=font_bold,
            fontSize=14,
            leading=18,
            textColor=PRIMARY_COLOR,
            spaceBefore=14,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName=font_regular,
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR,
            spaceAfter=6
        )

        bold_style = ParagraphStyle(
            'BodyBold',
            parent=body_style,
            fontName=font_bold
        )

        qco_title_style = ParagraphStyle(
            'QTitle',
            parent=bold_style,
            fontName=font_bold,
            textColor=colors.HexColor("#991b1b")
        )

        disc_style = ParagraphStyle(
            'Disc',
            parent=body_style,
            fontName=font_regular,
            fontSize=8,
            textColor=colors.HexColor("#64748b")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("StandardSaarthi - Standards Intelligence Report", title_style))
        story.append(Paragraph(f"AI-Powered Procurement Intelligence | Generated on {time.strftime('%d %b %Y, %H:%M IST')} | Ref: REP-{time.strftime('%Y%m%d%H%M')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceAfter=15))

        # 2. Procurement Requirement Summary
        story.append(Paragraph("1. Procurement Requirement Overview", h2_style))
        raw_query = clean_data.get("query", "N/A")
        story.append(Paragraph(f"<b>Query Description:</b> {raw_query}", body_style))

        entities = clean_data.get("entities") or {}
        if entities:
            spec_data = [
                [Paragraph("<b>Attribute</b>", bold_style), Paragraph("<b>Extracted Value</b>", bold_style)],
                [Paragraph("Product Name", body_style), Paragraph(str(entities.get("product") or "Not specified"), body_style)],
                [Paragraph("Product Category", body_style), Paragraph(str(entities.get("category") or "Not specified"), body_style)],
                [Paragraph("Materials", body_style), Paragraph(", ".join(entities.get("materials", [])) if isinstance(entities.get("materials"), list) else str(entities.get("materials") or "Not specified"), body_style)],
                [Paragraph("Intended Application", body_style), Paragraph(str(entities.get("application") or "Not specified"), body_style)],
                [Paragraph("Industry Sector", body_style), Paragraph(str(entities.get("industry") or "Not specified"), body_style)],
            ]
            t_spec = Table(spec_data, colWidths=[2.2*inch, 4.8*inch])
            t_spec.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), LIGHT_BG),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t_spec)
        story.append(Spacer(1, 10))

        # 3. Recommended Indian Standards
        story.append(Paragraph("2. Recommended Primary Indian Standards", h2_style))
        recs = clean_data.get("recommendations") or []
        if not recs:
            story.append(Paragraph("No verified Indian Standard matching your query was found in the database.", body_style))
        else:
            rec_rows = [[
                Paragraph("<b>Rank / IS Code</b>", bold_style),
                Paragraph("<b>Standard Title</b>", bold_style),
                Paragraph("<b>Match Score</b>", bold_style),
                Paragraph("<b>Regulatory Status</b>", bold_style)
            ]]
            for idx, r in enumerate(recs[:5], 1):
                is_code = r.get("is_code", "")
                title = r.get("title", "")
                score = r.get("relevance_score", 0.0)
                score_pct = f"{score*100:.1f}%"
                
                qco_info = r.get("qco_compliance") or {}
                is_qco = qco_info.get("qco_mandatory", False)
                qco_badge = "MANDATORY QCO" if is_qco else "RECOMMENDED"
                badge_color = colors.HexColor("#dc2626") if is_qco else colors.HexColor("#16a34a")

                rec_rows.append([
                    Paragraph(f"<b>#{idx} {is_code}</b>", body_style),
                    Paragraph(title, body_style),
                    Paragraph(score_pct, bold_style),
                    Paragraph(f"<font color='{badge_color}'><b>{qco_badge}</b></font>", body_style)
                ])

            t_recs = Table(rec_rows, colWidths=[1.8*inch, 3.2*inch, 1.0*inch, 1.0*inch])
            t_recs.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t_recs)

        story.append(Spacer(1, 10))

        # 4. Standard Detail & Why Recommended (Top Result)
        if recs:
            top_rec = recs[0]
            story.append(Paragraph(f"3. Detailed Recommendation Breakdown ({top_rec.get('is_code')})", h2_style))
            story.append(Paragraph(f"<b>Scope:</b> {top_rec.get('scope', 'Scope details available in BIS official document.')}", body_style))
            
            # Why Recommended
            reasons = top_rec.get("ranking_reasons") or []
            if reasons:
                story.append(Paragraph("<b>Why this standard was recommended:</b>", bold_style))
                for reason in reasons:
                    story.append(Paragraph(f"- {reason}", body_style))

            # QCO Gazette Reference
            qco_eval = top_rec.get("qco_compliance") or {}
            if qco_eval.get("qco_mandatory"):
                story.append(Spacer(1, 4))
                qco_box = [
                    [Paragraph("<b>STATUTORY MANDATORY QUALITY CONTROL ORDER NOTICE</b>", qco_title_style)],
                    [Paragraph(f"<b>Order Name:</b> {qco_eval.get('qco_name', 'Ministry Quality Control Order')}", body_style)],
                    [Paragraph(f"<b>Ministry / Authority:</b> {qco_eval.get('issuing_authority', 'Government of India')}", body_style)],
                    [Paragraph(f"<b>Gazette Reference:</b> {qco_eval.get('gazette_notification', 'Official Gazette Notification')}", body_style)],
                    [Paragraph(f"<b>Effective Date:</b> {qco_eval.get('effective_date', 'Currently Effective')}", body_style)]
                ]
                t_qco = Table(qco_box, colWidths=[7.0*inch])
                t_qco.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), ALERT_BG),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#fca5a5")),
                    ('PADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(t_qco)

        story.append(Spacer(1, 10))

        # 5. Evidence & Provenance
        story.append(Paragraph("4. Evidence & Provenance Verification", h2_style))
        ev_items = (recs[0].get("evidence") if recs else []) or []
        if ev_items:
            for ev in ev_items:
                story.append(Paragraph(f"<b>Source Authority:</b> {ev.get('organization', 'Bureau of Indian Standards (BIS)')}", body_style))
                story.append(Paragraph(f"<b>Source Document:</b> {ev.get('document', 'BIS Standards Portal')}", body_style))
                story.append(Paragraph(f"<b>Source URL:</b> <font color='{ACCENT_COLOR}'>{ev.get('url', 'https://standards.bis.gov.in/')}</font>", body_style))

        # 6. Disclaimer
        story.append(Spacer(1, 15))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
        story.append(Paragraph("<b>Notice & Decision Support Disclaimer:</b> This report is generated by an AI-assisted decision-support engine. Standard recommendations and statutory QCO compliance records are grounded in verified BIS datasets. Procurement officers should verify exact tender clauses against official BIS Gazette notifications before issuing tender specifications.", disc_style))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

report_generator = ReportGenerator()
