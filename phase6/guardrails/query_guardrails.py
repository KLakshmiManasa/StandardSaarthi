"""
SIH 26108 — Phase 6 Query Guardrails Module
Provides:
1. Ambiguity & Query Sufficiency Detection: Identifies vague queries and generates structured clarification requests.
2. Out-of-Domain (OOD) Detection: Rejects non-procurement inputs (e.g., general QA, code generation, recipes).
"""

import re
from typing import Dict, Any, Tuple, Optional

# Controlled Out-Of-Domain Keywords / Intent Patterns
OOD_PATTERNS = [
    r'\bcapital\b', r'\bwho won\b', r'\bwrite a (?:python|code|script|poem|story)\b',
    r'\bhow (?:do|to) (?:bake|cook|make|code)\b', r'\bexplain (?:einstein|relativity|quantum|history)\b',
    r'\bwhat is the weather\b', r'\bmeaning of life\b'
]

# Procurement Keyword Markers
PROCUREMENT_MARKERS = [
    "procurement", "supply", "installation", "specification", "specification for",
    "cable", "wire", "conductor", "transformer", "cement", "rebar", "steel",
    "pipe", "tile", "brick", "medical", "syringe", "glove", "mask", "jacket",
    "fabric", "tire", "flange", "valve", "pump", "gearbox", "bearing", "mixer",
    "geyser", "fan", "footwear", "earthing", "electrode", "grounding", "plate",
    "chemical", "hospital", "building", "structure", "foundation", "is", "code", "qco", "bis", "grade", "mm", "kv",
    "water", "drinking water", "packaged water", "mineral water", "potable water", "carboy", "polycarbonate", "container", "bottle", "liter", "litre",
    "केबल", "तार", "वायर", "कॉपर", "तांबा", "कंडक्टर", "पीवीसी", "इंसुलेशन", "इलेक्ट्रिकल", "वायरिंग", "बिल्डिंग",
    "கேபிள்", "கம்பி", "பிவிசி", "செம்பு", "மின்சார", "வயரிங்", "காப்பர்", "கண்டக்டர்", "இன்சுலேஷன்",
    "కేబుల్స్", "వైరింగ్", "ఎలక్ట్రికల్", "కాపర్", "కండక్టర్", "ఇన్సులేషన్"
]

class QueryGuardrails:
    def evaluate_query(self, query: str, entities: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Evaluates input query for sufficiency, domain validity, and security.
        
        Returns:
            Tuple[str, dict]: (status_code, details_dict)
            status_code can be: 'VALID', 'AMBIGUOUS', 'OUT_OF_DOMAIN'
        """
        if not query or not query.strip():
            return "AMBIGUOUS", {
                "status": "AMBIGUOUS_QUERY",
                "message": "Query text is empty or whitespace.",
                "missing_fields": ["product_type", "application", "material", "technical_characteristics"]
            }

        q_lower = query.strip().lower()

        # 1. Out-of-Domain Check
        for pat in OOD_PATTERNS:
            if re.search(pat, q_lower):
                return "OUT_OF_DOMAIN", {
                    "status": "OUT_OF_DOMAIN_REJECTION",
                    "message": "Input text appears to be outside the procurement and Indian Standards domain.",
                    "recommended_action": "Please provide a valid technical procurement specification or product requirement."
                }

        has_procurement_marker = any(m in q_lower for m in PROCUREMENT_MARKERS)
        valid_prod = bool(entities and entities.get("product") and str(entities.get("product")).lower() not in ["general equipment", "general item", "general procurement item", ""])
        valid_cat = bool(entities and entities.get("category") and str(entities.get("category")).lower() not in ["general", "unknown", "none", ""])
        has_entity_match = valid_prod or valid_cat

        if not has_procurement_marker and not has_entity_match and len(q_lower.split()) > 4:
            return "OUT_OF_DOMAIN", {
                "status": "OUT_OF_DOMAIN_REJECTION",
                "message": "Non-procurement query detected. No relevant Indian Standards match non-procurement domain requests.",
                "recommended_action": "Specify product requirements, materials, or technical standards."
            }

        # 2. Ambiguity & Sufficiency Check
        words = q_lower.split()
        category = str(entities.get("category", "") if entities else "").lower()
        prod_name = str(entities.get("product", "") if entities else "").lower()

        indic_material_terms = ["कॉपर", "तांबा", "पीवीसी", "इंसुलेशन", "காப்பர்", "பிவிசி", "செம்பு", "కాపర్", "పివిసి"]
        has_material = any(w in q_lower for w in ["pvc", "copper", "aluminum", "steel", "concrete", "clay", "cotton", "rubber", "hdpe", "xlpe", "cpvc", "vitreous", "polycarbonate", "plastic", "pet", "water"] + indic_material_terms)
        has_spec = any(w in q_lower for w in ["1.1kv", "11kv", "mm", "sq mm", "grade", "3 core", "50kg", "9w", "v", "kva", "m30", "fe 500d", "opc", "amp", "liter", "litre", "20-liter", "20 litre", "20l", "drinking", "potable", "mineral", "bottled"])
        has_code = any(k in q_lower for k in ["is ", "is-", "qco", "bis"])

        if entities:
            if entities.get("materials"):
                has_material = True
            if entities.get("technical_attributes") or entities.get("volume") or entities.get("container"):
                has_spec = True

        # Check if cable/wire query
        is_cable_query = (any(w in q_lower for w in ["cable", "wire", "conductor", "केबल", "तार", "கேபிள்", "கம்பி", "వైరింగ్", "కేబుల్"]) or ("cable" in prod_name or "wire" in prod_name)) and not any(w in q_lower for w in ["electrode", "transformer", "switchgear", "earthing", "grounding", "insulator", "mcb", "fan"])
        is_specific_product = valid_prod and prod_name not in ["cable", "wire", "flexible cable", "power cable", "general equipment", "general item", "general procurement item", ""]

        is_ambiguous = False
        if not has_code:
            # Cable queries without conductor material and specs are ambiguous
            if is_cable_query and not has_material and not has_spec:
                is_ambiguous = True
            # Ultra-short query (single word or generic 2-word query without a resolved product)
            elif len(words) < 2:
                is_ambiguous = True
            # Query lacking both a specific recognized product, material, and technical specification
            elif not is_specific_product and not has_material and not has_spec:
                is_ambiguous = True

        if is_ambiguous:
            missing = []
            if is_cable_query:
                if not has_material:
                    missing.append("conductor_material")
                if not has_spec:
                    missing.append("technical_characteristics")
            else:
                if not has_material and not valid_prod:
                    missing.append("material_specification")
                if not has_spec and not valid_prod:
                    missing.append("technical_characteristics")
                if not valid_prod:
                    missing.append("product_type")
            if not missing:
                missing.append("technical_characteristics")

            return "AMBIGUOUS", {
                "status": "AMBIGUOUS_QUERY",
                "message": "Query is too brief or ambiguous for confident Indian Standards recommendation.",
                "missing_fields": missing,
                "clarification_prompt": f"Please clarify: {', '.join(missing)}."
            }

        return "VALID", {"status": "VALID_PROCUREMENT_QUERY"}


if __name__ == '__main__':
    guard = QueryGuardrails()
    print("Test 1 (Valid):", guard.evaluate_query("Procurement of 1.1kV 3 core 6 sq mm PVC insulated copper flexible cable"))
    print("Test 2 (Ambiguous):", guard.evaluate_query("hospital equipment"))
    print("Test 3 (OOD):", guard.evaluate_query("What is the capital of France?"))
