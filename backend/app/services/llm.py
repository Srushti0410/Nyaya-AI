import os
import re

from groq import Groq


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

    system_prompt = (
        "You are an experienced Indian legal advisor. "
        "Answer clearly and confidently in 3-4 sentences. "
        "Do NOT mention section numbers or Act names. "
        "Do NOT ask questions. Be direct and suggest clear next steps."
    )

    user_prompt = f"""User situation:
{query}

STRICT RULES:
- Do NOT mention ANY section numbers
- Do NOT mention ANY Act names
- Do NOT say "fraud" for blackmail cases — use "blackmail" or "extortion"
- Do NOT ask questions
- Be confident and direct

Explain the issue clearly, mention rights only if relevant (e.g. Article 21 for privacy), and suggest clear next steps (police complaint, cybercrime portal, evidence preservation).

Answer in 3–4 sentences only."""

    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("[LLM ERROR] GROQ_API_KEY is not set")
            return fallback_response()

        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
            temperature=0.4,
        )

        raw = completion.choices[0].message.content.strip()

        if not raw:
            return fallback_response()

        clean = clean_output(raw)
        clean = remove_sections_and_acts(clean)
        clean = fix_articles(clean)
        clean = enforce_sentence_limit(clean)

        if len(clean) < 20:
            return fallback_response()

        return clean

    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {e}")
        return fallback_response()