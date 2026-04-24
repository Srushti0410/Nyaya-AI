"""
Lightweight JSON-based retrieval replacing ChromaDB + sentence-transformers.
Loads constitution chunks from data/processed/chunks.json at startup.
Falls back to an empty list if the file is missing.
"""
import json
import os
import re

_CHUNKS: list[dict] = []  # [{article, text}, ...]

def _load_chunks() -> list[dict]:
    base = os.path.dirname(os.path.abspath(__file__))
    # Walk up to backend root, then into data/processed/chunks.json
    chunks_path = os.path.join(base, "..", "..", "..", "data", "processed", "chunks.json")
    chunks_path = os.path.normpath(chunks_path)
    if not os.path.exists(chunks_path):
        return []
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


_CHUNKS = _load_chunks()


def keyword_search(query: str, k: int = 3) -> list[dict]:
    """
    Simple keyword overlap search over constitution chunks.
    Returns up to k chunks sorted by overlap score.
    """
    if not _CHUNKS:
        return []

    tokens = set(re.findall(r"[a-z]+", query.lower()))
    stopwords = {"the", "and", "for", "with", "this", "that", "from", "have",
                 "what", "when", "where", "which", "would", "could", "should",
                 "about", "there", "their", "them", "your", "you", "are",
                 "was", "were", "can", "help", "need", "want", "does", "did"}
    tokens = {t for t in tokens if t not in stopwords and len(t) > 2}

    scored = []
    for chunk in _CHUNKS:
        chunk_tokens = set(re.findall(r"[a-z]+", chunk.get("text", "").lower()))
        score = len(tokens & chunk_tokens)
        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]


def get_collection():
    """Kept for backward compatibility — returns None (not used in new flow)."""
    return None
