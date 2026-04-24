"""
Input preprocessing service to enrich raw user queries with structured context.

This module improves query quality by:
- Combining current query with previous context (history)
- Detecting issue type based on keywords
- Formatting into structured case details
"""

from typing import Optional, List

# Keyword-based issue type detection mapping
ISSUE_KEYWORDS = {
    "tenancy dispute": [
        "landlord", "tenant", "rent", "eviction", "deposit", "lease",
        "property", "room", "flat", "house", "notice", "removed",
        "locked", "belongings"
    ],
    "employment": [
        "job", "fired", "fired", "dismiss", "termination", "employee",
        "workplace", "salary", "wage", "boss", "manager", "work",
        "recruitment", "contract", "severance", "layoff"
    ],
    "cybercrime": [
        "fraud", "otp", "hacked", "phishing", "scam", "bank",
        "account", "password", "cyber", "cyber law", "cyberlaw",
        "cybercrime", "online", "digital", "identity", "forgery"
    ],
    "family law": [
        "divorce", "marriage", "child", "custody", "alimony",
        "maintenance", "separation", "spouse", "family", "children",
        "inheritance", "will"
    ],
    "contract dispute": [
        "contract", "agreement", "breach", "payment", "deliver",
        "service", "supplier", "vendor", "client", "business"
    ],
    "consumer rights": [
        "product", "defective", "return", "refund", "guarantee",
        "warranty", "quality", "consumer", "purchase", "seller"
    ],
}


def detect_issue_type(text: str) -> Optional[str]:
    """
    Detect the legal issue type based on keywords in the query.
    
    Args:
        text: User query text to analyze
    
    Returns:
        str: Detected issue type category, or None if no match found
    """
    text_lower = text.lower()
    
    # Check against each issue category
    for issue_type, keywords in ISSUE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return issue_type
    
    return None


def enrich_query(query: str, history: Optional[List[str]] = None) -> str:
    """
    Enrich a user query with structured context and case details.
    
    This function:
    - Combines current query with previous message (if history exists)
    - Detects the legal issue type based on keywords
    - Formats into structured case details for better LLM understanding
    
    Args:
        query: Current user query
        history: List of previous user messages (optional)
    
    Returns:
        str: Enriched query with structured case details
    
    Example:
        >>> query = "what should I do"
        >>> history = ["My landlord locked my room and threw my belongings out"]
        >>> result = enrich_query(query, history)
        >>> print(result)
        Case Details:
        - Issue Type: tenancy dispute
        - Situation: My landlord locked my room and threw my belongings out
        
        User Question:
        what should I do
    """
    
    # If no history, return original query
    if not history or len(history) == 0:
        return query
    
    # Take only the last message for performance
    situation = history[-1]
    
    # Detect issue type from both situation and current query
    combined_text = f"{situation} {query}"
    issue_type = detect_issue_type(combined_text)
    
    # Format enriched query
    enriched = "Case Details:\n"
    
    if issue_type:
        enriched += f"- Issue Type: {issue_type}\n"
    
    enriched += f"- Situation: {situation}\n"
    enriched += f"\nUser Question:\n{query}"
    
    return enriched


def extract_case_context(query: str, history: Optional[List[str]] = None) -> dict:
    """
    Extract structured case context from query and history.
    
    Useful for additional processing or logging.
    
    Args:
        query: Current user query
        history: List of previous user messages (optional)
    
    Returns:
        dict: Structured case context with keys:
            - "issue_type": Detected legal category
            - "situation": Previous context (if available)
            - "question": Current user question
            - "has_history": Boolean indicating if history was provided
    """
    situation = None
    if history and len(history) > 0:
        situation = history[-1]
    
    combined_text = f"{situation or ''} {query}".lower()
    issue_type = detect_issue_type(combined_text)
    
    return {
        "issue_type": issue_type,
        "situation": situation,
        "question": query,
        "has_history": history is not None and len(history) > 0,
    }
