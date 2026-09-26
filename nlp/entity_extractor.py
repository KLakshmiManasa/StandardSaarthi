"""
SIH 26108 — NLP Requirement & Entity Extraction Module
Extracts domain-specific entities (product, category, materials, application, industry, technical parameters, regulatory terms)
from natural language procurement descriptions.
"""

import re
from typing import Dict, Any, List

ELECTRICAL_PRODUCTS = [
    "pvc insulated cable", "pvc cable", "heavy duty cable", "armored cable", "unarmored cable",
    "xlpe cable", "power cable", "control cable", "copper cable", "aluminum cable", "flexible cable",
    "conductor", "copper conductor", "aluminum conductor", "distribution transformer", "power transformer",
    "switchgear", "circuit breaker", "mcb", "mccb", "porcelain insulator", "insulator", "wiring",
    "flexible cord", "cable joint", "cable termination", "busbar", "earth electrode"
]

CIVIL_PRODUCTS = [
    "ordinary portland cement", "opc 53", "opc 43", "opc 33", "ppc", "portland cement", "cement",
    "tmt rebar", "tmt bar", "steel rebar", "high strength deformed steel bars", "structural steel",
    "ready mix concrete", "concrete", "coarse aggregate", "fine aggregate", "aggregates", "sand",
    "fly ash bricks", "clay bricks", "bricks", "concrete block", "paving blocks", "bitumen", "asphalt",
    "shuttering plywood", "flush door", "plywood", "hdpe pipe", "cpvc pipe", "upvc pipe", "pvc pipe", "di pipe", "pipes"
]

FOOD_WATER_PRODUCTS = [
    "packaged drinking water", "packaged natural mineral water", "packaged water",
    "drinking water", "bottled drinking water", "bottled water", "mineral water",
    "potable water", "purified water"
]

CONTAINERS = [
    "reusable polycarbonate carboy", "polycarbonate carboy", "reusable carboy",
    "water carboy", "carboy", "reusable container", "plastic container", "bottle"
]

MATERIALS = [
    "annealed copper", "copper", "aluminum", "polyvinyl chloride", "pvc", "xlpe", "galvanized steel",
    "tmt steel", "tmt", "steel", "ordinary portland cement", "opc", "fly ash", "aggregate", "sand",
    "bitumen", "hdpe", "ductile iron", "lead", "brass", "porcelain", "epoxy",
    "polycarbonate", "plastic container", "pet", "glass"
]

APPLICATIONS = [
    "underground power distribution", "power distribution", "internal building wiring", "control panel wiring",
    "control panel", "industrial plants", "mains cabling", "high voltage transmission", "substation", "residential wiring",
    "reinforced concrete", "rcc structure", "foundation", "bridge deck", "road pavement", "water supply", "sewerage", "drainage",
    "human consumption", "direct human consumption", "potable water supply"
]

INDUSTRIES = [
    "electrical", "power sector", "civil engineering", "construction", "infrastructure",
    "utilities", "water supply", "renewable energy", "railways", "industrial manufacturing",
    "food and water safety", "food & water"
]

REGULATORY_TERMS = [
    "quality control order", "qco", "bureau of indian standards", "bis", "is code", "isi mark",
    "mandatory certification", "mandatory", "scheme-i", "gazette notification", "statutory requirement"
]


INDIC_TERM_MAPPINGS = [
    (r'\b(?:केबल|केबल्स|கேபிள்|கேபிள்கள்|கேபில்கள்|కేబుల్స్|కేబుల్)\b', 'cable'),
    (r'\b(?:तार|तारों|वायर|கம்பி|வயரிங்|వైరింగ్|वायरिंग)\b', 'wire wiring'),
    (r'\b(?:कॉपर|तांबा|तांबे|காப்பர்|தாமிரம்|செம்பு|కాపర్)\b', 'copper'),
    (r'\b(?:कंडक्टर|கண்டக்டர்|కండక్టర్)\b', 'conductor'),
    (r'\b(?:पीवीसी|பிவிசி|పివిసి)\b', 'pvc'),
    (r'\b(?:इंसुलेशन|इंसुलेटेड|இன்சுலேஷன்|ఇన్సులేషన్)\b', 'insulation insulated'),
    (r'\b(?:इलेक्ट्रिकल|बिजली|மின்சார|மின்|ఎలక్ట్రికల్)\b', 'electrical'),
    (r'\b(?:बिल्डिंग|கட்டிட|భవనం)\b', 'building'),
    (r'\b(?:अंदर|உள்ளே|లోపల)\b', 'indoor'),
    (r'(?:அடைக்கப்பட்ட\s*குடிநீர்|குடிநீர்|பாட்டில்\s*தண்ணீர்|தண்ணீர்)', 'packaged drinking water'),
    (r'(?:पैकेज्ड\s*पेयजल|पेयजल|पीने\s*का\s*पानी|पानी)', 'packaged drinking water')
]

class NLPEntityExtractor:
    def __init__(self):
        self.products_db = ELECTRICAL_PRODUCTS + CIVIL_PRODUCTS + FOOD_WATER_PRODUCTS
        self.containers_db = CONTAINERS
        self.materials_db = MATERIALS
        self.apps_db = APPLICATIONS
        self.industries_db = INDUSTRIES
        self.regulatory_db = REGULATORY_TERMS

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Parses natural language procurement text into structured domain entities.
        Supports English and Indic language queries.
        """
        if not text or not text.strip():
            return {
                "product": "",
                "category": "",
                "materials": [],
                "application": "",
                "container": "",
                "volume": "",
                "industry": "",
                "technical_attributes": [],
                "regulatory_terms": [],
                "raw_query": text
            }

        raw_lower = text.lower()
        norm_text = raw_lower

        # Substitute Indic terms into English equivalents for robust multilingual entity extraction
        for pat, eng_rep in INDIC_TERM_MAPPINGS:
            norm_text = re.sub(pat, eng_rep, norm_text, flags=re.IGNORECASE)

        indic_kws = [
            ("कॉपर", "copper"), ("तांबा", "copper"), ("तांबे", "copper"), ("காப்பர்", "copper"), ("தாமிரம்", "copper"), ("செம்பு", "copper"), ("కాపర్", "copper"),
            ("कंडक्टर", "conductor"), ("கண்டக்டர்", "conductor"), ("కండక్టర్", "conductor"),
            ("पीवीसी", "pvc"), ("பிவிसी", "pvc"), ("பிவிசி", "pvc"), ("పివిసి", "pvc"),
            ("इंसुलेशन", "insulation"), ("इंसुलेटेड", "insulation"), ("இன்சுலேஷன்", "insulation"), ("ఇన్సులేషన్", "insulation"),
            ("इलेक्ट्रिकल", "electrical"), ("बिजली", "electrical"), ("மின்சார", "electrical"), ("மின்", "electrical"), ("ఎలక్ట్రికల్", "electrical"),
            ("केबल", "cable"), ("केबल्स", "cables"), ("கேபிள்", "cable"), ("கேபிள்கள்", "cables"), ("కేబుల్స్", "cables"), ("కేబుల్", "cable"),
            ("वायरिंग", "wiring"), ("வயரிங்", "wiring"), ("వైరింగ్", "wiring"),
            ("बिल्डिंग", "building"), ("கட்டிட", "building"), ("భవனம்", "building"),
            ("अंदर", "indoor"), ("உள்ளே", "indoor"), ("లోపల", "indoor")
        ]
        for ikw, erep in indic_kws:
            if ikw.lower() in raw_lower:
                norm_text += f" {erep}"

        text_lower = f"{raw_lower} {norm_text}"

        # 1. Product Extraction & Normalization
        matched_products = []
        for p in self.products_db:
            p_words = p.lower().split()
            if p.lower() in text_lower or all(w in text_lower for w in p_words):
                matched_products.append(p)
        
        matched_products.sort(key=lambda x: len(x), reverse=True)
        raw_product = matched_products[0] if matched_products else ""

        # Normalize product title for food & water and electrical cables
        if any(kw in text_lower for kw in ["drinking water", "packaged water", "bottled water"]):
            primary_product = "Packaged Drinking Water"
        elif any(kw in text_lower for kw in ["pvc cable", "pvc insulated cable", "copper cable", "insulated cable", "cable", "wire"]) and any(kw in text_lower for kw in ["pvc", "copper", "insulated", "wiring", "conductor", "electrical"]):
            primary_product = "PVC Insulated Cable"
        elif raw_product:
            primary_product = raw_product.title()
        else:
            primary_product = ""

        # Category determination
        category = ""
        if any(kw in text_lower for kw in ["cable", "wire", "conductor", "transformer", "switchgear", "voltage", "current", "mcb", "earthing", "copper", "pvc", "insulation", "electrical", "wiring"]):
            category = "Electrical"
        elif any(kw in text_lower for kw in ["cement", "concrete", "rebar", "steel", "aggregate", "brick", "pave", "pipe", "plumbing"]):
            category = "Civil"
        elif any(kw in text_lower for kw in ["drinking water", "packaged water", "mineral water", "bottled water", "potable water", "carboy"]):
            category = "Food & Water"

        # 2. Materials Extraction
        matched_materials = []
        for m in self.materials_db:
            if m.lower() in text_lower:
                matched_materials.append(m.title())

        # Ensure copper and PVC are captured if present
        if "copper" in text_lower and "Copper" not in matched_materials:
            matched_materials.append("Copper")
        if "pvc" in text_lower and "PVC" not in matched_materials:
            matched_materials.append("PVC")
        matched_materials = list(dict.fromkeys(matched_materials))

        # 3. Container Extraction & Normalization
        matched_containers = []
        for c in self.containers_db:
            if c.lower() in text_lower:
                matched_containers.append(c)
        matched_containers.sort(key=lambda x: len(x), reverse=True)
        primary_container = matched_containers[0].title() if matched_containers else ""

        # 4. Volume / Capacity Extraction & Normalization (e.g. 20-liter, 20 litre, 20L)
        vol_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:-|l|liter|litre|liters|litres)\b', text_lower)
        primary_volume = f"{vol_match.group(1)} litre" if vol_match else ""

        # 5. Application Extraction
        matched_apps = []
        for a in self.apps_db:
            if a.lower() in text_lower:
                matched_apps.append(a)
        matched_apps.sort(key=lambda x: len(x), reverse=True)
        if matched_apps:
            primary_app = matched_apps[0].title()
        elif any(kw in text_lower for kw in ["building", "wiring", "indoor", "internal"]):
            primary_app = "Internal Building Wiring"
        elif category == "Food & Water":
            primary_app = "Human Consumption"
        else:
            primary_app = "Electrical Distribution" if category == "Electrical" else "General Engineering Application"

        # 6. Industry Extraction
        matched_ind = [i for i in self.industries_db if i.lower() in text_lower]
        primary_ind = matched_ind[0].title() if matched_ind else (category if category else "General Engineering")

        # 7. Technical Attributes Extraction (Regex patterns)
        tech_patterns = [
            r'\b\d+(?:\.\d+)?\s*(?:kv|v|volts)\b',
            r'\b\d+(?:\.\d+)?\s*(?:sq\s*mm|sqmm|mm2)\b',
            r'\b\d+(?:\.\d+)?\s*(?:mm|cm|m)\b',
            r'\b\d+\s*grade\b|\bgrade\s*\d+\b',
            r'\b\d+(?:\.\d+)?\s*(?:n/mm2|mpa|bar)\b',
            r'\b\d+(?:\.\d+)?\s*°c\b|\b\d+\s*deg\s*c\b',
            r'\b\d+\s*core\b',
            r'\b\d+(?:\.\d+)?\s*(?:liter|litre|l)\b'
        ]

        tech_attrs = []
        for pat in tech_patterns:
            matches = re.findall(pat, text_lower)
            tech_attrs.extend(matches)
        tech_attrs = list(dict.fromkeys(tech_attrs))

        # 8. Regulatory Terms Extraction
        matched_reg = [r for r in self.regulatory_db if r.lower() in text_lower]
        matched_reg = list(dict.fromkeys(matched_reg))

        return {
            "product": primary_product if primary_product else "General Equipment",
            "category": category if category else "General",
            "materials": [m.title() for m in matched_materials],
            "container": primary_container,
            "volume": primary_volume,
            "application": primary_app if primary_app else "General Engineering Application",
            "industry": primary_ind,
            "technical_attributes": tech_attrs,
            "regulatory_terms": [r.upper() for r in matched_reg],
            "raw_query": text
        }


if __name__ == '__main__':
    extractor = NLPEntityExtractor()
    sample_q = "Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable for control panel wiring with QCO compliance."
    res = extractor.extract_entities(sample_q)
    print("[OK] Enhanced NLP Entity Extraction Test:")
    for k, v in res.items():
        print(f"  {k}: {v}")
