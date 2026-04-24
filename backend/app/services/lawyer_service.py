from pymongo.errors import PyMongoError

from app.db.mongo import lawyers_collection


CASE_TYPE_TO_QUERY = {
    "cyber law": ["Cyber Law", "Cyber & IT Law", "cyber", "cybercrime", "it law"],
    "property law": ["Property Law", "property", "civil"],
    "employment law": ["Employment Law", "Labour Law", "employment", "labour", "civil"],
    "family law": ["Family Law", "family", "divorce", "custody"],
}

CASE_TYPE_TO_AREA = {
    "cyber law": "cyber",
    "property law": "property",
    "employment law": "labour",
    "family law": "family",
}

FALLBACK_LAWYERS = [
    {
        "name": "Adv. Amit Rastogi",
        "specialization": "Cyber Law",
        "area": "cyber",
        "experience": 9,
        "court": "Cyber Appellate Tribunal",
        "rating": 4.8,
        "tags": ["Cyber Law", "IT Act", "Online Fraud", "Data Protection", "Digital IP"],
    },
    {
        "name": "Adv. Anika Kapoor",
        "specialization": "Property Law",
        "area": "property",
        "experience": 14,
        "court": "Bombay High Court",
        "rating": 4.9,
        "tags": ["Property Law", "Tenant Rights", "Civil Disputes", "Land Acquisition", "Encroachment"],
    },
    {
        "name": "Adv. Rajan Sharma",
        "specialization": "Employment Law",
        "area": "labour",
        "experience": 22,
        "court": "Supreme Court of India",
        "rating": 4.8,
        "tags": ["Labour Law", "Wrongful Termination", "Employment", "Corporate HR", "POSH Act"],
    },
    {
        "name": "Adv. Priya Mehta",
        "specialization": "Family Law",
        "area": "family",
        "experience": 8,
        "court": "Mumbai District Court",
        "rating": 4.7,
        "tags": ["Family Law", "Divorce", "Child Custody", "Succession", "Adoption"],
    },
    {
        "name": "Adv. Varun Kumar",
        "specialization": "Criminal Law",
        "area": "criminal",
        "experience": 17,
        "court": "Delhi High Court",
        "rating": 4.9,
        "tags": ["Criminal Law", "Bail Applications", "FIR Defence", "White Collar Crime", "PMLA"],
    },
]


def detect_case_type(query: str) -> str:
    q = query.lower()

    if any(word in q for word in ["photo", "leak", "blackmail", "money", "cyber", "hacked", "fraud", "phishing", "scam", "otp"]):
        return "Cyber Law"

    if any(word in q for word in ["landlord", "rent", "tenant", "property", "deposit", "evict", "eviction", "house", "room"]):
        return "Property Law"

    if any(word in q for word in ["job", "salary", "fired", "terminated", "termination", "employee", "employment", "labour"]):
        return "Employment Law"

    if any(word in q for word in ["divorce", "custody", "marriage", "family", "spouse", "children", "alimony"]):
        return "Family Law"

    return "General"


def _normalize_specializations(case_type: str) -> list[str]:
    lowered = case_type.strip().lower()

    if lowered in CASE_TYPE_TO_QUERY:
        return CASE_TYPE_TO_QUERY[lowered]

    for key, values in CASE_TYPE_TO_QUERY.items():
        if key in lowered:
            return values

    return ["Civil", "civil"]


def _case_type_to_area(case_type: str) -> str:
    return CASE_TYPE_TO_AREA.get(case_type.strip().lower(), "general")


def _extract_keywords(text: str) -> set[str]:
    tokens = []
    for part in text.lower().replace("/", " ").replace("-", " ").split():
        cleaned = "".join(ch for ch in part if ch.isalnum())
        if len(cleaned) > 2:
            tokens.append(cleaned)
    return set(tokens)


def _score_lawyer_match(query: str, case_type: str, lawyer: dict) -> int:
    query_tokens = _extract_keywords(query)
    specialization_tokens = _extract_keywords(str(lawyer.get("specialization", "")))
    area_tokens = _extract_keywords(str(lawyer.get("area", "")))
    tag_tokens = _extract_keywords(" ".join(str(tag) for tag in lawyer.get("tags", [])))

    overlap = len(query_tokens & (specialization_tokens | area_tokens | tag_tokens))
    score = overlap * 10

    expected_area = _case_type_to_area(case_type)
    if expected_area != "general" and str(lawyer.get("area", "")).lower() == expected_area:
        score += 40

    specialization = str(lawyer.get("specialization", "")).lower()
    if case_type.lower() in specialization:
        score += 20

    return score


def _normalize_lawyer(lawyer: dict) -> dict:
    specialization = lawyer.get("specialization") or lawyer.get("area") or lawyer.get("tags", ["General"])[0]
    experience = lawyer.get("experience", lawyer.get("yrs", 0))
    experience_text = f"{experience} years" if isinstance(experience, (int, float, str)) else "Experience available"

    return {
        "name": lawyer.get("name", "Recommended Lawyer"),
        "specialization": specialization,
        "experience": experience_text,
        "court": lawyer.get("court", lawyer.get("location", "Online Consultation")),
        "rating": int(round(float(lawyer.get("rating", 0)) * 20)) if float(lawyer.get("rating", 0)) <= 5 else int(float(lawyer.get("rating", 0))),
        "tags": lawyer.get("tags", []),
    }


def recommend_lawyers(query: str, issue_type: str | None = None) -> list[dict]:
    case_type = issue_type or detect_case_type(query)
    specializations = _normalize_specializations(case_type)

    try:
        regex_filters = [{"specialization": {"$regex": term, "$options": "i"}} for term in specializations]
        regex_filters.append({"specialization": {"$regex": case_type, "$options": "i"}})

        cursor = lawyers_collection.find(
            {
                "$or": regex_filters
            },
            {"_id": 0},
        )
        lawyers = list(cursor)

        if not lawyers:
            fallback = sorted(
                FALLBACK_LAWYERS,
                key=lambda lawyer: (
                    _score_lawyer_match(query, case_type, lawyer),
                    float(lawyer.get("rating", 0)),
                    int(lawyer.get("experience", 0)),
                ),
                reverse=True,
            )
            return [_normalize_lawyer(lawyer) for lawyer in fallback[:3]]

        lawyers.sort(
            key=lambda lawyer: (
                _score_lawyer_match(query, case_type, lawyer),
                float(lawyer.get("rating", 0)),
                int(lawyer.get("experience", 0)),
            ),
            reverse=True,
        )

        return [_normalize_lawyer(lawyer) for lawyer in lawyers[:3]]
    except PyMongoError as exc:
        raise RuntimeError(f"Database error while recommending lawyers: {exc}") from exc
