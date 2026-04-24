import json

import requests

from app.config import OLLAMA_URL, LLM_MODEL


def _default_summary(issue_type: str = "general legal issue") -> dict:
    return {
        "issue_type": issue_type,
        "summary": "Unable to generate complete summary at the moment.",
        "key_points": ["Please provide more details about the legal issue."],
        "suggested_action": "Consult a qualified lawyer with the relevant specialization.",
    }


def summarize_case(query: str) -> dict:
    prompt = f"""
You are a legal case summarization assistant for lawyers.

Given a user legal issue description, return ONLY valid JSON with this exact shape:
{{
  "issue_type": "...",
  "summary": "...",
  "key_points": ["...", "..."],
  "suggested_action": "..."
}}

Instructions:
- Identify the legal category (examples: landlord dispute, cybercrime, employment, property, criminal, civil).
- Use simple professional language.
- Highlight important facts.
- Suggest a possible next legal step.
- Do not include markdown or extra text outside JSON.

User query:
{query}
""".strip()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()

        payload = response.json()
        raw_output = (payload.get("response") or "").strip()

        if not raw_output:
            return _default_summary()

        # Extract first JSON object if model adds stray text.
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return _default_summary()

        parsed = json.loads(raw_output[start : end + 1])

        issue_type = str(parsed.get("issue_type", "general legal issue")).strip() or "general legal issue"
        summary = str(parsed.get("summary", "")).strip() or "Unable to generate complete summary at the moment."
        key_points = parsed.get("key_points", [])
        if not isinstance(key_points, list) or not key_points:
            key_points = ["Please provide more details about the legal issue."]

        normalized_points = [str(point).strip() for point in key_points if str(point).strip()]
        if not normalized_points:
            normalized_points = ["Please provide more details about the legal issue."]

        suggested_action = str(parsed.get("suggested_action", "")).strip() or "Consult a qualified lawyer with the relevant specialization."

        return {
            "issue_type": issue_type,
            "summary": summary,
            "key_points": normalized_points,
            "suggested_action": suggested_action,
        }
    except (requests.RequestException, ValueError, json.JSONDecodeError):
        return _default_summary()
