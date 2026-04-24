import requests
import re

from app.config import LLM_MODEL, OLLAMA_URL


# ---------------- CLEANING ---------------- #

def clean_output(text: str) -> str:
    if not text:
        return text

    forbidden = [
        "puzzle", "scenario", "rules", "follow-up",
        "you are an ai", "as an ai", "teacher", "trainer"
    ]

    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        if not any(f in line.lower() for f in forbidden):
            clean_lines.append(line)

    cleaned = " ".join(clean_lines)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned


def enforce_sentence_limit(text: str, max_sentences: int = 4) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return " ".join(sentences[:max_sentences])


def remove_sections_and_acts(text: str) -> str:
    """
    Remove ANY section numbers or Act references completely
    """

    # Remove "Section 123", "section 66E", etc.
    text = re.sub(r'\b[Ss]ection\s*\d+[A-Za-z]*\b', '', text)

    # Remove "Act 2000", "Act of 1970"
    text = re.sub(r'\b[A-Z][A-Za-z\s]+Act\s*(of)?\s*\d{4}\b', '', text)

    # Remove incomplete "section 4(1) of"
    text = re.sub(r'\b[Ss]ection\s*\d+\(\d+\)[^.,]*', '', text)

    return text.strip()


def fix_articles(text: str) -> str:
    """
    Allow ONLY safe Article usage
    """

    # Remove wrong Article references like 22 misuse
    text = re.sub(r'Article\s+22[^.]*\.', '', text)

    allowed = ["Article 21", "Article 14", "Article 300A"]

    sentences = re.split(r'(?<=[.!?])\s+', text)
    filtered = []

    for sent in sentences:
        if "Article" in sent:
            if any(a in sent for a in allowed):
                filtered.append(sent)
        else:
            filtered.append(sent)

    return " ".join(filtered)


# ---------------- FALLBACK ---------------- #

def fallback_response():
    return (
        "This is a serious legal issue. You should immediately preserve all evidence such as messages or screenshots "
        "and avoid paying any money. You can file a complaint with the cybercrime authorities or your nearest police station. "
        "It is advisable to consult a lawyer for further guidance."
    )


# ---------------- MAIN FUNCTION ---------------- #

def generate_answer(context_chunks, query, history=None):
    context = "\n\n".join(context_chunks) if context_chunks else ""

    prompt = f"""
You are an experienced Indian legal advisor.

User situation:
{query}

IMPORTANT:
- This is an ongoing conversation. Do NOT ask for details again.
- Always answer based on the situation already given.

INSTRUCTIONS:

1. Identify the issue type:
   - criminal (blackmail, photo leak, harassment)
   - civil/property
   - rights issue

2. If the user asks about rights:
   - For privacy/photo leak → mention Article 21 (privacy, dignity, liberty)

STRICT RULES:
- Do NOT mention ANY section numbers
- Do NOT mention ANY Act names
- Do NOT invent laws
- Do NOT say "fraud" for blackmail cases
- Use "blackmail" or "extortion"
- Do NOT ask questions
- Do NOT reset conversation
- Be confident and direct

TASK:
- Explain the issue clearly
- Mention rights only if relevant
- Suggest clear next steps (police complaint, cybercrime portal, evidence)

Answer in 3–4 sentences only.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 140
                }
            },
            timeout=90,
        )

        response.raise_for_status()
        data = response.json()

        raw = data.get("response", "").strip()

        if not raw:
            return fallback_response()

        # 🔥 CLEAN PIPELINE
        clean = clean_output(raw)
        clean = remove_sections_and_acts(clean)
        clean = fix_articles(clean)
        clean = enforce_sentence_limit(clean)

        if len(clean) < 20:
            return fallback_response()

        return clean

    except Exception:
        return fallback_response()