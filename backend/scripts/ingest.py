import fitz
import re
import chromadb
from sentence_transformers import SentenceTransformer

# -------- Extract --------
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# -------- Clean --------
def clean_text(text):
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
    text = re.sub(r"\s+", " ", text)

    return text


# -------- Chunk --------
def chunk_by_articles(text):
    pattern = r"(\d+\.\s+[A-Z][^0-9]+)"
    matches = re.finditer(pattern, text)

    chunks = []
    positions = []

    for match in matches:
        positions.append((match.start(), match.group()))

    for i in range(len(positions)):
        start = positions[i][0]
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)

        article_title = positions[i][1].strip()
        article_number = article_title.split(".")[0]

        chunk_text = text[start:end].strip()

        chunks.append({
            "article": f"Article {article_number}",
            "text": chunk_text
        })

    return chunks


# -------- Embeddings --------
model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):
    texts = [chunk["text"] for chunk in chunks]
    return model.encode(texts)


# -------- Store (Persistent Chroma) --------
def store_chroma(embeddings, chunks):
    client = chromadb.PersistentClient(path="data/vectordb")

    # Clean old collection
    try:
        client.delete_collection("constitution")
    except:
        pass

    collection = client.get_or_create_collection(name="constitution")

    for i, chunk in enumerate(chunks):
        collection.add(
            embeddings=[embeddings[i].tolist()],
            documents=[chunk["text"]],
            metadatas=[{"article": chunk["article"]}],
            ids=[str(i)]
        )

    print("✅ Chroma DB saved")


# -------- MAIN --------
if __name__ == "__main__":
    print("🚀 Starting ingest...")

    raw = extract_text("data/raw/constitution.pdf")
    print("✅ Extracted")

    clean = clean_text(raw)
    print("✅ Cleaned")

    chunks = chunk_by_articles(clean)
    print(f"✅ {len(chunks)} chunks created")

    embeddings = create_embeddings(chunks)
    print("✅ Embeddings created")

    store_chroma(embeddings, chunks)

    print("🎉 DONE")