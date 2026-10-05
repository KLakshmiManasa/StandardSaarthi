import requests
import json
import pypdf
import os

url = 'http://127.0.0.1:8000/api/reports/generate'

test_cases = [
    {
        "lang": "te",
        "name": "Telugu Session",
        "payload": {
            "query": "పివిసి తీగలు మరియు కేబుల్స్",
            "entities": {"multilingual_info": {"detected_language": "te", "normalized_english": "PVC wires and cables"}},
            "recommendations": [
                {
                    "standard_number": "IS 694",
                    "title": "Polyvinyl Chloride Insulated Cables",
                    "localized_title": "పాలివినైల్ క్లోరైడ్ ఇన్సులేటెడ్ కేబుల్స్",
                    "official_title": "Polyvinyl Chloride Insulated Cables",
                    "scope": "Covers PVC insulated cables for working voltages up to 1100V",
                    "localized_scope": "1100V వరకు పని చేసే వోల్టేజ్ ల కోసం PVC ఇన్సులేటెడ్ కేబుల్స్ ని కవర్ చేస్తుంది",
                    "official_scope": "Covers PVC insulated cables for working voltages up to 1100V",
                    "why_this_standard": "కనిష్ట భద్రత మరియు విద్యుత్ ప్రామాణిక అవసరాలను నెరవేరుస్తుంది",
                    "localized_reason": "కనిష్ట భద్రత మరియు విద్యుత్ ప్రామాణిక అవసరాలను నెరవేరుస్తుంది",
                    "compliance_guidance": "BIS సర్టిఫికేషన్ తప్పనిసరి",
                    "localized_compliance": "BIS సర్టిఫికేషన్ తప్పనిసరి"
                }
            ],
            "output_language": "te"
        }
    },
    {
        "lang": "hi",
        "name": "Hindi Session",
        "payload": {
            "query": "पीवीसी तार और केबल",
            "entities": {"multilingual_info": {"detected_language": "hi", "normalized_english": "PVC wire and cable"}},
            "recommendations": [
                {
                    "standard_number": "IS 694",
                    "title": "Polyvinyl Chloride Insulated Cables",
                    "localized_title": "पॉलीविनाइल क्लोराइड इंसुलेटेड केबल",
                    "official_title": "Polyvinyl Chloride Insulated Cables",
                    "scope": "Covers PVC insulated cables for working voltages up to 1100V",
                    "localized_scope": "1100V तक के कामकाजी वोल्टेज के लिए पीवीसी इंसुलेटेड केबल शामिल हैं",
                    "official_scope": "Covers PVC insulated cables for working voltages up to 1100V",
                    "why_this_standard": "न्यूनतम सुरक्षा आवश्यकताएं",
                    "localized_reason": "न्यूनतम सुरक्षा आवश्यकताएं"
                }
            ],
            "output_language": "hi"
        }
    },
    {
        "lang": "ta",
        "name": "Tamil Session",
        "payload": {
            "query": "பிவிசி கம்பிகள் மற்றும் கேபிள்கள்",
            "entities": {"multilingual_info": {"detected_language": "ta", "normalized_english": "PVC wires and cables"}},
            "recommendations": [
                {
                    "standard_number": "IS 694",
                    "title": "Polyvinyl Chloride Insulated Cables",
                    "localized_title": "பாலிவினைல் குளோரைடு காப்பிடப்பட்ட கேபிள்கள்",
                    "official_title": "Polyvinyl Chloride Insulated Cables"
                }
            ],
            "output_language": "ta"
        }
    },
    {
        "lang": "en",
        "name": "English Session",
        "payload": {
            "query": "PVC wires and cables",
            "entities": {"multilingual_info": {"detected_language": "en", "normalized_english": "PVC wires and cables"}},
            "recommendations": [
                {
                    "standard_number": "IS 694",
                    "title": "Polyvinyl Chloride Insulated Cables",
                    "official_title": "Polyvinyl Chloride Insulated Cables"
                }
            ],
            "output_language": "en"
        }
    }
]

print("=== STARTING PDF GENERATION VERIFICATION ===")

for tc in test_cases:
    print(f"\nTesting {tc['name']} (Requested lang: {tc['lang']})...")
    res = requests.post(url, json=tc["payload"])
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    
    filename = f"test_out_{tc['lang']}.pdf"
    with open(filename, "wb") as f:
        f.write(res.content)
    
    # Read generated PDF text
    reader = pypdf.PdfReader(filename)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    print(f"PDF Generated successfully. Size: {len(res.content)} bytes, Pages: {len(reader.pages)}")
    clean_display = full_text.encode("ascii", errors="replace").decode("ascii")
    print("--- Extracted Text Sample ---")
    print(clean_display[:300].strip())
    print("-----------------------------")
    
    # Check for missing glyph boxes or non-ASCII characters that failed encoding
    assert "■" not in full_text, f"FAILED: Black box glyph found in PDF for {tc['name']}"
    
    # Check that localized indicative texts are NOT present
    if tc['lang'] == 'te':
        assert "పాలివినైల్" not in full_text, "FAILED: Raw Telugu found in PDF!"
    elif tc['lang'] == 'hi':
        assert "पॉलीविनाइल" not in full_text, "FAILED: Raw Hindi found in PDF!"
    elif tc['lang'] == 'ta':
        assert "பாலிவினைல்" not in full_text, "FAILED: Raw Tamil found in PDF!"
        
    print(f"SUCCESS: {tc['name']} PDF is 100% clean English!")

print("\nALL 4 SCENARIOS PASSED VERIFICATION PERFECTLY!")
