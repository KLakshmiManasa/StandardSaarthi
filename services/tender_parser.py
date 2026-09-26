"""
Tender Document Parser & Procurement Requirement Extractor for SIH 26108 / Product Engine.
Supports PDF (pypdf/pdfplumber), DOCX (python-docx), and TXT file extraction.
Segments text into sections and extracts discrete procurement requirements.
"""

import os
import re
import io
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("TenderParser")

class TenderParser:
    def __init__(self):
        pass

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return self._extract_pdf(file_bytes)
        elif ext in ['.docx', '.doc']:
            return self._extract_docx(file_bytes)
        elif ext == '.txt':
            return file_bytes.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Unsupported file format: '{ext}'. Supported formats: .pdf, .docx, .txt")

    def _extract_pdf(self, file_bytes: bytes) -> str:
        text = ""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes), strict=False)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
        except Exception as e:
            logger.warning(f"pypdf extraction failed, trying fallback: {e}")

        if not text.strip():
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
            except Exception as e2:
                logger.debug(f"pdfplumber not available or failed: {e2}")

        if not text.strip():
            try:
                # Robust stream regex text extraction
                raw_matches = re.findall(rb'\(([^\(\)]{2,})\)\s*T[jJ]', file_bytes)
                extracted_pieces = [m.decode('utf-8', errors='ignore') for m in raw_matches if len(m) > 2]
                if extracted_pieces:
                    text = " ".join(extracted_pieces)
                else:
                    clean_str = "".join([chr(b) if 32 <= b <= 126 or b in [10, 13, 9] else " " for b in file_bytes])
                    words = [w for w in clean_str.split() if len(w) > 3 and not w.startswith(('/', '%', '<', '>'))]
                    if len(words) > 10:
                        text = " ".join(words[:500])
            except Exception as e3:
                logger.error(f"Fallback PDF stream extraction failed: {e3}")

        if not text.strip():
            raise ValueError("Could not extract legible text from PDF document. Please ensure the PDF contains selectable text or upload as TXT/DOCX.")

        return text.strip()

    def _extract_docx(self, file_bytes: bytes) -> str:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise ValueError(f"Could not extract text from DOCX document: {e}")

    def parse_tender_document(self, file_bytes: bytes, filename: str, target_lang: str = "auto") -> Dict[str, Any]:
        raw_text = self.extract_text_from_file(file_bytes, filename)
        if not raw_text or len(raw_text.strip()) < 10:
            return {
                "status": "document_extraction_failed",
                "filename": filename,
                "error": "Document contains empty or unreadable text.",
                "extracted_requirements": []
            }

        # Detect document language
        from services.multilingual import multilingual_service
        lang_info = multilingual_service.detect_language(raw_text, target_lang=target_lang)
        doc_lang = lang_info.get("code", "en")
        doc_lang_name = lang_info.get("name", "English")

        raw_lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        requirements = []
        req_id = 1

        # Multilingual procurement keywords & regexes
        item_pattern = re.compile(
            r'^(?:item\s*\d+|section\s*\d+|\d+[\.\)]|supply\s+of|procurement\s+of|technical\s+spec|'
            r'உருப்படி\s*\d+|பொருட்கள்\s*\d+|தேவை|விவரக்குறிப்பு|'
            r'मद\s*\d+|वस्तु\s*\d+|सामग्री|आवश्यकता|'
            r'అంశం\s*\d+|వస్తువు|అవసరం|'
            r'আইটেম\s*\d+|পণ্য|প্রয়োজনীয়তা|'
            r'વસ્તુ\s*\d+|જરૂરિયાત)',
            re.IGNORECASE
        )

        current_requirement = []
        for line in raw_lines:
            # Skip document header lines
            if re.match(r'^(?:tender\s+specification|tender\s+no|document\s+no|ஒப்பந்தப்புள்ளி|निविदा|టెండర్|দরপত্র)', line, re.IGNORECASE):
                continue

            # Detect numbered items or supply procurement lines
            is_new_item = bool(item_pattern.match(line))
            if is_new_item and current_requirement:
                chunk_text = " ".join(current_requirement)
                if len(chunk_text) > 15:
                    norm_en = chunk_text
                    if doc_lang != "en":
                        norm_en = multilingual_service.translate_text(chunk_text, sl=doc_lang, tl="en")

                    requirements.append({
                        "req_id": f"REQ_{req_id:03d}",
                        "text": chunk_text[:500],
                        "normalized_english": norm_en[:500],
                        "language": doc_lang,
                        "category_hint": self._infer_category(norm_en)
                    })
                    req_id += 1
                current_requirement = [line]
            else:
                current_requirement.append(line)

        if current_requirement:
            chunk_text = " ".join(current_requirement)
            if len(chunk_text) > 15:
                norm_en = chunk_text
                if doc_lang != "en":
                    norm_en = multilingual_service.translate_text(chunk_text, sl=doc_lang, tl="en")

                requirements.append({
                    "req_id": f"REQ_{req_id:03d}",
                    "text": chunk_text[:500],
                    "normalized_english": norm_en[:500],
                    "language": doc_lang,
                    "category_hint": self._infer_category(norm_en)
                })
                req_id += 1

        # Fallback paragraph or sentence segmentation so any document yields requirement items
        if not requirements and raw_lines:
            paragraphs = [p.strip() for p in raw_text.split('\n\n') if len(p.strip()) > 15]
            if not paragraphs:
                paragraphs = [line for line in raw_lines if len(line) > 15]
            for p in paragraphs[:15]:
                norm_en = p
                if doc_lang != "en":
                    norm_en = multilingual_service.translate_text(p, sl=doc_lang, tl="en")
                requirements.append({
                    "req_id": f"REQ_{req_id:03d}",
                    "text": p[:500],
                    "normalized_english": norm_en[:500],
                    "language": doc_lang,
                    "category_hint": self._infer_category(norm_en)
                })
                req_id += 1

        return {
            "status": "success",
            "filename": filename,
            "detected_language": doc_lang,
            "language_name": doc_lang_name,
            "total_character_count": len(raw_text),
            "requirement_count": len(requirements),
            "extracted_requirements": requirements,
            "raw_text_preview": raw_text[:1000]
        }

    def _infer_category(self, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ['water', 'drinking', 'beverage', 'bottle', 'mineral', 'potable', 'food']):
            return "Food & Water"
        elif any(w in lower for w in ['cable', 'wire', 'conductor', 'transformer', 'switchgear', 'voltage', 'kv', 'ampere', 'electrical', 'led']):
            return "Electrical"
        elif any(w in lower for w in ['cement', 'concrete', 'aggregate', 'bar', 'steel', 'brick', 'civil', 'pipe', 'building']):
            return "Civil / Construction"
        elif any(w in lower for w in ['medical', 'hospital', 'syringe', 'mask', 'glove', 'oxygen']):
            return "Medical"
        return "General Procurement"

tender_parser = TenderParser()
