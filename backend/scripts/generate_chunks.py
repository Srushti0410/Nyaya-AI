"""
Generates data/processed/chunks.json from data/raw/constitution.pdf.
Only requires pymupdf (fitz). No sentence-transformers needed.
Run from the backend/ directory:
    python scripts/generate_chunks.py
"""
import json
import re
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    print("ERROR: pymupdf not installed. Run: pip install pymupdf")
    sys.exit(1)

PDF_PATH = Path("data/raw/constitution.pdf")
OUT_PATH = Path("data/processed/chunks.json")


def extract_text(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def clean_text(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "THE CONSTITUTION OF INDIA" in line:
            continue
        if line.startswith("(") and "Part" in line:
            continue
        if line.isdigit():
            continue
        cleaned.append(line)
    text = " ".join(cleaned)
    return re.sub(r"\s+", " ", text)


def chunk_by_articles(text: str) -> list[dict]:
    pattern = r"(\d+\.\s+[A-Z][^0-9]+)"
    matches = list(re.finditer(pattern, text))
    chunks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        article_title = match.group().strip()
        article_number = article_title.split(".")[0]
        chunk_text = text[start:end].strip()
        chunks.append({
            "article": f"Article {article_number}",
            "text": chunk_text
        })
    return chunks


if __name__ == "__main__":
    if not PDF_PATH.exists():
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    print("Extracting text...")
    raw = extract_text(PDF_PATH)
    print("Cleaning...")
    clean = clean_text(raw)
    print("Chunking by articles...")
    chunks = chunk_by_articles(clean)
    print(f"Created {len(chunks)} chunks")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Saved to {OUT_PATH}")
