import json
import os
from importlib import import_module


LEGACY_MODEL_MAP = {
    "llama3-8b-8192": "llama-3.1-8b-instant",
}

FALLBACK_MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
]


def _default_summary(issue_type: str = "general legal issue") -> dict:
    return {
        "issue_type": issue_type,
        "summary": "Unable to generate complete summary at the moment.",
        "key_points": ["Please provide more details about the legal issue."],
        "suggested_action": "Consult a qualified lawyer with the relevant specialization.",
    }


def summarize_case(query: str) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _default_summary()

    configured_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    model_name = LEGACY_MODEL_MAP.get(configured_model, configured_model)

    try:
        Groq = import_module("groq").Groq
    except (ModuleNotFoundError, AttributeError):
        return _default_summary()

    prompt = f"""You are a legal case summarization assistant for lawyers.

Given a user legal issue description, return ONLY valid JSON with this exact shape:
{{
  "issue_type": "...",
  "summary": "...",
  "key_points": ["...", "..."],
  "suggested_action": "..."
}}

Instructions:
- Identify the legal category (e.g. landlord dispute, cybercrime, employment, property, criminal, civil).
- Use simple professional language.
- Highlight important facts.
- Suggest a possible next legal step.
- Return ONLY the JSON object, no markdown, no extra text.

User query:
{query}"""

    try:
        client = Groq(api_key=api_key)
        completion = None
        candidate_models = [model_name] + [m for m in FALLBACK_MODELS if m != model_name]
        for candidate in candidate_models:
            try:
                completion = client.chat.completions.create(
                    model=candidate,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.3,
                )
                break
            except Exception as call_error:
                err_text = str(call_error).lower()
                if "model_decommissioned" in err_text or "decommissioned" in err_text:
                    continue
                raise

        if completion is None:
            return _default_summary()

        raw_output = (completion.choices[0].message.content or "").strip()
        if not raw_output:
            return _default_summary()

        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return _default_summary()

        parsed = json.loads(raw_output[start: end + 1])

        issue_type = str(parsed.get("issue_type", "general legal issue")).strip() or "general legal issue"
        summary = str(parsed.get("summary", "")).strip() or "Unable to generate complete summary."
        key_points = parsed.get("key_points", [])
        if not isinstance(key_points, list) or not key_points:
            key_points = ["Please provide more details about the legal issue."]
        key_points = [str(p).strip() for p in key_points if str(p).strip()] or ["Please provide more details."]
        suggested_action = str(parsed.get("suggested_action", "")).strip() or "Consult a qualified lawyer."

        return {
            "issue_type": issue_type,
            "summary": summary,
            "key_points": key_points,
            "suggested_action": suggested_action,
        }

    except Exception:
        return _default_summary()
