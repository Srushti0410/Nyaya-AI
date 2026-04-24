import re

from app.db.vector_store import get_collection
from app.services.embeddings import embed_text

collection = get_collection()

LEGAL_KEYWORDS = {
    "tenancy": [
        "landlord", "tenant", "tenancy", "evict", "eviction", "rent",
        "property", "room", "house", "deposit", "notice", "locked",
        "possession", "belongings", "lease",
    ],
    "employment": [
        "job", "fired", "dismiss", "termination", "employee", "workplace",
        "salary", "wage", "boss", "manager", "recruitment", "contract",
        "severance", "layoff",
    ],
    "cybercrime": [
        "fraud", "otp", "hacked", "phishing", "scam", "bank", "account",
        "password", "cyber", "online", "digital", "identity", "forgery",
    ],
    "family": [
        "divorce", "marriage", "child", "custody", "alimony", "maintenance",
        "separation", "spouse", "children", "inheritance", "will",
    ],
    "contract": [
        "contract", "agreement", "breach", "payment", "deliver", "service",
        "supplier", "vendor", "client", "business",
    ],
    "consumer": [
        "product", "defective", "return", "refund", "guarantee", "warranty",
        "quality", "consumer", "purchase", "seller",
    ],
}

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "have", "been",
    "what", "when", "where", "which", "would", "could", "should", "about",
    "there", "their", "them", "your", "you", "are", "was", "were", "can",
    "help", "need", "want", "does", "did", "done", "into", "over", "under",
    "after", "before", "while", "case", "issue", "legal",
}


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\b[a-z]+\b", text.lower())
        if token not in STOPWORDS and len(token) > 2
    }


def _extract_query_keywords(query: str) -> list[str]:
    query_lower = query.lower()
    keywords: set[str] = set()

    for keyword_group in LEGAL_KEYWORDS.values():
        for keyword in keyword_group:
            if keyword in query_lower:
                keywords.add(keyword)

    if keywords:
        return sorted(keywords)

    tokens = re.findall(r"[a-z]+", query_lower)
    return sorted(
        token for token in tokens
        if len(token) > 4 and token not in STOPWORDS
    )


def is_context_relevant(query: str, context_chunks: list[str]) -> bool:
    if not context_chunks:
        return False

    query_keywords = set(_extract_query_keywords(query))
    if not query_keywords:
        return False

    context_tokens = _tokenize(" ".join(context_chunks))
    overlap = query_keywords.intersection(context_tokens)

    if overlap:
        return True

    # Fall back to phrase matching for obvious legal-situation terms.
    context_text = " ".join(context_chunks).lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", context_text) for keyword in query_keywords)


def filter_relevant_context(query: str, context_chunks: list[str], sources: list[str]) -> tuple[list[str], list[str], bool]:
    relevant = is_context_relevant(query, context_chunks)
    if not relevant:
        return [], [], False
    return context_chunks, sources, True

def retrieve_context(query, k=1):
    """
    Retrieve relevant context from the vector database.
    
    Args:
        query: User query to retrieve context for
        k: Number of top results to retrieve (default: 1 for strict relevance)
    
    Returns:
        tuple: (documents: list of relevant text chunks, sources: list of article references)
               Returns empty lists if no valid context found
    """
    try:
        query_embedding = embed_text(query)[0].tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # Filter results: only include chunks that contain BOTH "article" AND "constitution"
        valid_documents = []
        valid_sources = []
        
        for doc, meta in zip(documents, metadatas):
            # Check if metadata contains article reference and is from constitution
            if ("article" in meta and meta.get("article")) and \
               ("constitution" in str(meta).lower() or "constitution" in str(doc).lower()):
                valid_documents.append(doc)
                valid_sources.append(meta["article"])
        
        # Return empty context if no valid chunks found
        return valid_documents, valid_sources
    
    except Exception as exc:
        # Return empty context on error to trigger safe fallback
        return [], []