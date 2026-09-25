"""
Procurement Standards PDF Report Generator for SIH 26108 / Product Engine.
Generates multi-page formal PDF reports using `reportlab`.
Includes requirement specs, primary recommendations, categorized graph relationships,
lifecycle status, QCO/BIS certification scheme notices, and evidence sources.
"""

import io
import os
import time
import logging
from typing import Dict, Any, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

logger = logging.getLogger("ReportGenerator")

class ReportGenerator:
    def __init__(self):
        pass

    def generate_pdf_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """
        Builds PDF report buffer from analysis data.
        """
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
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=PRIMARY_COLOR,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=15
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=PRIMARY_COLOR,
            spaceBefore=14,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR,
            spaceAfter=6
        )

        bold_style = ParagraphStyle(
            'BodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("StandardSaarthi — Standards Intelligence Report", title_style))
        story.append(Paragraph(f"AI-Powered Procurement Intelligence • Generated on {time.strftime('%d %b %Y, %H:%M IST')} • Ref: REP-{time.strftime('%Y%m%d%H%M')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceAfter=15))

        # 2. Procurement Requirement Summary
        story.append(Paragraph("1. Procurement Requirement Overview", h2_style))
        raw_query = analysis_data.get("query", "N/A")
        story.append(Paragraph(f"<b>Query Description:</b> {raw_query}", body_style))

        entities = analysis_data.get("entities") or {}
        if entities:
            spec_data = [
                [Paragraph("<b>Attribute</b>", bold_style), Paragraph("<b>Extracted Value</b>", bold_style)],
                [Paragraph("Product Name", body_style), Paragraph(str(entities.get("product") or "Not specified"), body_style)],
                [Paragraph("Product Category", body_style), Paragraph(str(entities.get("category") or "Not specified"), body_style)],
                [Paragraph("Materials", body_style), Paragraph(", ".join(entities.get("materials", [])) if entities.get("materials") else "Not specified", body_style)],
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
        recs = analysis_data.get("recommendations") or []
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
                    story.append(Paragraph(f"• {reason}", body_style))

            # QCO Gazette Reference
            qco_eval = top_rec.get("qco_compliance") or {}
            if qco_eval.get("qco_mandatory"):
                story.append(Spacer(1, 4))
                qco_box = [
                    [Paragraph("<b>STATUTORY MANDATORY QUALITY CONTROL ORDER NOTICE</b>", ParagraphStyle('QTitle', parent=bold_style, textColor=colors.HexColor("#991b1b")))],
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
        story.append(Paragraph("<b>Notice & Decision Support Disclaimer:</b> This report is generated by an AI-assisted decision-support engine. Standard recommendations and statutory QCO compliance records are grounded in verified BIS datasets. Procurement officers should verify exact tender clauses against official BIS Gazette notifications before issuing tender specifications.", ParagraphStyle('Disc', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

report_generator = ReportGenerator()
