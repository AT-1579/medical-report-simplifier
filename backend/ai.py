import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing from .env")


def analyze_report(report_text):

    prompt = f"""
You are a medical-report explanation assistant.

Analyze the following OCR-extracted medical report.

IMPORTANT RULES:

1. Use ONLY information present in the report.
2. Dynamically identify medical tests, values, units,
   reference ranges, medical terms and notable findings.
3. Do NOT depend on a predefined medical-term dictionary.
4. Correct obvious OCR errors only when the surrounding
   context makes the correction highly reliable.
5. If an OCR value is uncertain, mark it as uncertain.
6. Compare results with the reference range provided
   in the report whenever available.
7. Explain medical terminology in simple patient-friendly
   language.
8. Do NOT diagnose a disease.
9. Do NOT prescribe medicines or dosages.
10. Precautions should be general safety/follow-up guidance.
11. If the report does not contain enough information,
    explicitly say so.
12. Do not assume that an abnormal result automatically
    means a disease.
13. Do not invent missing values.

Return ONLY valid JSON in this exact structure:

{{
    "summary": "Simple overall explanation",

    "findings": [
        "Finding 1",
        "Finding 2"
    ],

    "medical_terms": [
        {{
            "term": "Medical term",
            "explanation": "Simple explanation"
        }}
    ],

    "precautions": [
        "General precaution or follow-up suggestion"
    ],

    "follow_up": "General guidance about whether the report
    should be discussed with a qualified healthcare professional.",

    "disclaimer": "This is an AI-generated educational
    explanation and is not a medical diagnosis."
}}

MEDICAL REPORT:

{report_text}
"""

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Medical Report Simplifier"
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(
            f"OpenRouter API Error {response.status_code}: "
            f"{response.text}"
        )

    data = response.json()

    if "choices" not in data or not data["choices"]:
        raise Exception("OpenRouter returned no response.")

    content = data["choices"][0]["message"]["content"]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise Exception(
            "AI returned an invalid JSON response."
        )